#!/usr/bin/env python3
"""Run the actual C2 entry on encoded FP16 data; CPU semantics, not CANN emulation."""
from pathlib import Path
import math, random, struct, subprocess, tempfile

R = Path(__file__).resolve().parents[1]
s = (R/'kernel.asc').read_text()
a = s.index('template<bool TX1,bool TX2>\n__global__ __vector__ void bmmms_tiny_direct_half_mla40(')
b = s.index('template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>\n__global__ __vector__ void bmmms_tiny_direct(', a)
entry = s[a:b]
g = s.index('inline bool UseTinyHalfMla40('); h = s.index('using CacheKey=', g)
hook = s[s.index('if(UseTinyHalfMla40(s,p,x1,x2)){'):s.index('const uint32_t vectorRows=SmallVectorK256Rows(s);')]
assert s.replace(entry,'',1).replace(s[g:h],'',1).replace(hook,'',1) == subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
    assert (R/name).read_bytes() == subprocess.check_output(['git','show','1734f16:'+name])
helpers = s[s.index('__aicore__ inline void TinyManualIndex64('):s.index('__aicore__ inline void TinyZeroProductPadding(')]
model = (R/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
model = model.replace('using GM_ADDR = void*;', '''using GM_ADDR = void*; using half=int16_t;
#include <fstream>
float Decode(half v){uint16_t u=uint16_t(v);unsigned e=(u>>10)&31,m=u&1023;assert(e!=31);
float x=e?std::ldexp(float(1024+m),int(e)-25):std::ldexp(float(m),-24);return u&32768?-x:x;}
''')
model = model.replace('dma,outDma;', 'dma,outDma,vec;')
model = model.replace('size_t manualBytes=0;', 'size_t manualBytes=0;std::vector<uint8_t> defined;bool inputReady=false,outputReady=false;')
model = model.replace('std::memcpy(&v,mem->data()+offset+i*sizeof(T),sizeof(T));return v;',
    'for(size_t j=0;j<sizeof(T);++j)assert(defined.at(offset+i*sizeof(T)+j));\nstd::memcpy(&v,mem->data()+offset+i*sizeof(T),sizeof(T));return v;')
model = model.replace('std::memcpy(mem->data()+offset+i*sizeof(T),&v,sizeof(T));}',
    'std::memcpy(mem->data()+offset+i*sizeof(T),&v,sizeof(T));for(size_t j=0;j<sizeof(T);++j)defined.at(offset+i*sizeof(T)+j)=1;}')
a = model.index('template<HardEvent E>void SetFlag'); b = model.index('\nuint32_t block', a)
model = model[:a]+'''template<HardEvent E>void SetFlag(int id){assert(id==0);auto mark=[] {assert(flags[E]++==0);};
if(E==HardEvent::V_MTE3)vec.push_back(mark);else {if(E==HardEvent::MTE2_V)Flush(dma);mark();}}
template<HardEvent E>void WaitFlag(int id){if(E==HardEvent::V_MTE3){Flush(vec);outputReady=true;}assert(id==0&&flags[E]--==1);if(E==HardEvent::MTE2_V)inputReady=true;}
'''+model[b:]
model = model.replace('template<int P> void PipeBarrier(){if(P==PIPE_ALL){Flush(dma);Flush(outDma);}}',
    'template<int P> void PipeBarrier(){if(P==PIPE_ALL){Flush(outDma);Flush(vec);Flush(dma);}else Flush(vec);}')
model = model.replace('void Gather(LocalTensor<float> dst,LocalTensor<float> src,', 'template<class T>void Gather(LocalTensor<T> dst,LocalTensor<T> src,')
model = model.replace('assert(bytes%4==0);dst.write(i,src.read(bytes/4));', 'assert(bytes%sizeof(T)==0);dst.write(i,src.read(bytes/sizeof(T)));')
model = model.replace('assert(p.blockCount==1 && p.srcStride==0', 'assert(outputReady);assert(p.blockCount==1 && p.srcStride==0')
model = model.replace('assert(dst.offset%32==0 && src.offset%32==0 && idx.offset%32==0);', 'assert(inputReady);assert(dst.offset%32==0 && src.offset%32==0 && idx.offset%32==0);')
mixed = '''template<class T,class U>void MulAddDst(LocalTensor<T>d,LocalTensor<U>a,LocalTensor<U>b,uint64_t mask,uint8_t reps,BinaryRepeatParams p){
assert(inputReady&&sizeof(T)==4&&sizeof(U)==2&&mask>0&&mask<=64&&reps<=255);
assert(d.offset%32==0&&a.offset%32==0&&b.offset%32==0&&p.dstBlk==1&&p.src0Blk==1&&p.src1Blk==1);
for(unsigned r=0;r<reps;++r)for(unsigned i=0;i<mask;++i){unsigned z=r*p.dstRep*8+i;
d.write(z,std::fma(Decode(a.read(r*p.src0Rep*16+i)),Decode(b.read(r*p.src1Rep*16+i)),d.read(z)));}}
'''
model = model.replace('float tree_sum(', mixed+'float tree_sum(')
# One deferred Vector FIFO; cross-instruction sub-pipeline timing is not modeled.
for token in ['void Gather(', 'void Adds(', 'void Muls(', 'void Duplicate(', 'void MulAddDst(', 'void WholeReduceSum(', 'void WholeReduceMax(']:
    pos = 0
    while True:
        a = model.find(token,pos)
        if a < 0: break
        a = model.index('{',a); depth=1; b=a+1
        while depth:
            depth += (model[b]=='{')-(model[b]=='}'); b+=1
        body=model[a+1:b-1]; replacement='{vec.push_back([=]{'+body+'});}'
        model=model[:a]+replacement+model[b:]; pos=a+len(replacement)
END = r'''
template<bool X,bool Y>void Check(half*a,half*b,float expected){using namespace AscendC;
ub=std::make_shared<std::vector<uint8_t>>(6848+32,0xab);defined.assign(6848+32,0);dma.clear();vec.clear();outDma.clear();flags.clear();writes.clear();inputReady=outputReady=false;
half ac[120],bc[200];memcpy(ac,a,sizeof ac);memcpy(bc,b,sizeof bc);float out[17];for(auto&x:out)x=1234567;
bmmms_tiny_direct_half_mla40<X,Y>(a,b,out);assert(dma.empty()&&vec.empty()&&outDma.empty());
assert(std::isfinite(out[0])&&std::abs(double(out[0])-expected)<=1e-4+1e-4*std::abs(expected));
for(unsigned i=1;i<17;++i)assert(out[i]==1234567);assert(writes.size()==1&&writes.begin()->second==1);
assert(!memcmp(a,ac,sizeof ac)&&!memcmp(b,bc,sizeof bc));for(unsigned i=6848;i<6880;++i)assert(ub->at(i)==0xab);
for(auto f:flags)assert(f.second==0);
}
int main(int argc,char**argv){assert(argc==2);std::ifstream in(argv[1],std::ios::binary);unsigned flags,count=0;
while(in.read((char*)&flags,4)){alignas(32)half a[120],b[200];float y;in.read((char*)a,sizeof a);in.read((char*)b,sizeof b);in.read((char*)&y,4);assert(in.good());
switch(flags){case 0:Check<false,false>(a,b,y);break;case 1:Check<false,true>(a,b,y);break;case 2:Check<true,false>(a,b,y);break;case 3:Check<true,true>(a,b,y);break;default:assert(false);}++count;}
assert(count==536);std::cout<<"536 full-K40 FP16 fixtures/all four layouts/defined UB/DMA-Vector-output/input and y guards PASS\n";}
'''
enc = lambda x: struct.unpack('<H',struct.pack('<e',x))[0]
dec = lambda x: struct.unpack('<e',struct.pack('<H',x))[0]
rng = random.Random(1746)
cases = []
for seed in range(128):
    cases.append(([enc(rng.uniform(-1,1)) for _ in range(120)], [enc(rng.uniform(-1,1)) for _ in range(200)]))
# Nonzero last K8, all-negative rows, last document only winner, cancellation,
# FP32-only range and FP16 input denormals. Golden always uses every actual value.
cases += [([enc(1)]*120,[enc(-1)]*200),
          ([enc(1 if k>=32 else 0) for m in range(3) for k in range(40)],
           [enc(n-5 if k>=32 else 0) for n in range(5) for k in range(40)]),
          ([enc(1)]*120,[enc(-1 if n<4 else 1) for n in range(5) for k in range(40)]),
          ([enc((-1)**k) for m in range(3) for k in range(40)], [enc(1)]*200),
          ([0x7bff]*120,[0x7bff]*200),
          ([1]*120,[0x7bff]*200)]
data=bytearray()
for x,z in cases:
    y=math.fsum(max(math.fsum(dec(x[m*40+k])*dec(z[n*40+k]) for k in range(40)) for n in range(5)) for m in range(3))
    for tx1 in (0,1):
        for tx2 in (0,1):
            a=[x[m*40+k] for k in range(40) for m in range(3)] if tx1 else x
            b=z if tx2 else [z[n*40+k] for k in range(40) for n in range(5)]
            data+=struct.pack('<I120H200Hf',tx1*2+tx2,*a,*b,y)
with tempfile.TemporaryDirectory(prefix='bmmms-c2-half-') as tmp:
    d=Path(tmp);(d/'inputs').write_bytes(data)
    def run(code,name):
        cpp=d/(name+'.cpp');exe=d/name;cpp.write_text(model.replace('// INSERT_KERNELS',helpers+code)+END)
        subprocess.run(['c++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        return subprocess.run([str(exe),str(d/'inputs')],capture_output=True)
    r=run(entry,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
    for name,old,new in [
        ('input_ready','AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);',''),
        ('output_ready','AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(0);',''),
        ('completion','AscendC::PipeBarrier<PIPE_ALL>();',''),
        ('zero_init','AscendC::Duplicate(prod,0.0f,1152);',''),
        ('half_offset','int32_t(6),40','int32_t(12),40'),
        ('mixed_stride','rp{1,1,1,6,0,3}','rp{1,1,1,6,0,6}'),
        ('full_K','uint64_t(40),uint8_t(5)','uint64_t(32),uint8_t(5)'),
        ('valid_N','uint64_t(5),3,8','uint64_t(8),3,8')]:
        bad=entry.replace(old,new);assert bad!=entry,name;assert run(bad,name).returncode!=0,name
print('Eight semantic fault controls, whole-source inverse and protected7 PASS; CANN/native/perf separate.')
