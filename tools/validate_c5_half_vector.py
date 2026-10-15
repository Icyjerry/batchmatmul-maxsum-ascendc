#!/usr/bin/env python3
"""Execute the actual C5 mixed-half Vector entry, full K128 before MaxN/SumM."""
from pathlib import Path
import math,random,struct,subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('template<bool TX1,bool TX2>\n__global__ __vector__ void bmmms_c5_half_vector(');b=s.index('struct SmallVectorManualShape{',a);entry=s[a:b]
g=s.index('inline bool UseC5HalfVector(');h=s.index('using CacheKey=',g);guard=s[g:h]
a=s.index('if(UseC5HalfVector(s,p,x1,x2)){');b=s.index('if(UseSmallC5Direct(s,p)){',a);hook=s[a:b]
assert s.replace(entry,'',1).replace(guard,'',1).replace(hook,'',1)==subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
for n in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/n).read_bytes()==subprocess.check_output(['git','show','1734f16:'+n])
a=s.index('__aicore__ inline void SmallVectorManualIndex(');b=s.index('template<bool TX1,bool TX2>',a);helpers=s[a:b]
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
END = r"""
template<bool X,bool Y>void Check(half*a,half*b,float*expected){using namespace AscendC;float out[24];for(auto&x:out)x=1234567;
std::vector<half>ac(a,a+8*2048),bc(b,b+8*4096);writes.clear();
for(unsigned bi=0;bi<8;++bi){block=bi;ub=std::make_shared<std::vector<uint8_t>>(159328+32,0xab);defined.assign(159328+32,0);dma.clear();vec.clear();outDma.clear();flags.clear();inputReady=outputReady=false;
bmmms_c5_half_vector<X,Y>(a,b,out);assert(dma.empty()&&vec.empty()&&outDma.empty());
assert(std::isfinite(out[bi])&&std::abs(double(out[bi])-expected[bi])<=1e-4+1e-4*std::abs(expected[bi]));
for(unsigned i=bi+1;i<24;++i)assert(out[i]==1234567);
for(unsigned i=159328;i<159360;++i)assert(ub->at(i)==0xab);for(auto f:flags)assert(f.second==0);
}assert(writes.size()==8);for(auto w:writes)assert(w.second==1);assert(!memcmp(a,ac.data(),ac.size()*2)&&!memcmp(b,bc.data(),bc.size()*2));
}
int main(int argc,char**argv){assert(argc==2);std::ifstream in(argv[1],std::ios::binary);unsigned flags,count=0;
while(in.read((char*)&flags,4)){std::vector<half>as(8*2048+16),bs(8*4096+16);auto*a=(half*)(((uintptr_t)as.data()+31)&~uintptr_t(31));auto*b=(half*)(((uintptr_t)bs.data()+31)&~uintptr_t(31));float y[8];in.read((char*)a,8*4096);in.read((char*)b,8*8192);in.read((char*)y,32);assert(in.good());
switch(flags){case 0:Check<false,false>(a,b,y);break;case 1:Check<false,true>(a,b,y);break;case 2:Check<true,false>(a,b,y);break;case 3:Check<true,true>(a,b,y);break;default:assert(false);}++count;}
assert(count==40);std::cout<<"320 actual C5 batch entries/full M16N32K128/all layouts, FP16/FP64 oracle/defined UB/input-y guards PASS\n";}
"""
enc=lambda x:struct.unpack('<H',struct.pack('<e',x))[0]
dec=lambda x:struct.unpack('<e',struct.pack('<H',x))[0]
rng=random.Random(1746);cases=[]
for seed in range(4):cases.append(([enc(rng.uniform(-1,1)) for _ in range(8*2048)],[enc(rng.uniform(-1,1)) for _ in range(8*4096)]))
cases += [([enc(1)]*(8*2048),[enc(-1 if n==31 else -2) for bi in range(8) for n in range(32) for k in range(128)]),
 ([enc(k>=64) for bi in range(8) for m in range(16) for k in range(128)],[enc(1 if n==31 else -1) for bi in range(8) for n in range(32) for k in range(128)]),
 ([enc(k<64) for bi in range(8) for m in range(16) for k in range(128)],[enc(1 if n==0 else -1) for bi in range(8) for n in range(32) for k in range(128)]),
 ([enc(1+bi) for bi in range(8) for m in range(16) for k in range(128)],[enc(1)]*(8*4096)),
 ([0x7bff]*(8*2048),[0x7bff]*(8*4096)),([1]*(8*2048),[0x7bff]*(8*4096))]
data=bytearray()
for x,z in cases:
 fx=list(map(dec,x));fz=list(map(dec,z))
 golden=[math.fsum(max(math.fsum(fx[bi*2048+m*128+k]*fz[bi*4096+n*128+k] for k in range(128)) for n in range(32)) for m in range(16)) for bi in range(8)]
 for tx1 in (0,1):
  for tx2 in (0,1):
   a=[x[bi*2048+m*128+k] for bi in range(8) for k in range(128) for m in range(16)] if tx1 else x
   b=z if tx2 else [z[bi*4096+n*128+k] for bi in range(8) for k in range(128) for n in range(32)]
   data+=struct.pack('<I16384H32768H8f',tx1*2+tx2,*a,*b,*golden)
with tempfile.TemporaryDirectory(prefix='bmmms-c5-half-') as tmp:
 d=Path(tmp);(d/'inputs').write_bytes(data)
 def run(code,name):
  cpp=d/(name+'.cpp');exe=d/name;cpp.write_text(model.replace('// INSERT_KERNELS',helpers+code)+END)
  subprocess.run(['c++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True);return subprocess.run([str(exe),str(d/'inputs')],capture_output=True)
 r=run(entry,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,old,new in [
  ('input_ready','AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);',''),
  ('output_ready','AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(0);',''),
  ('completion','AscendC::PipeBarrier<PIPE_ALL>();',''),
  ('zero_init','AscendC::Duplicate(prod,0.0f,32768);',''),
  ('half_offset','int32_t(64),128','int32_t(128),128'),
  ('half_stride','rp{1,1,1,8,0,8}','rp{1,1,1,8,0,4}'),
  ('high_K','ca[m*128+64],cb[64]','ca[m*128],cb'),
  ('batch_pair','+batch*4096,4096','+0,4096'),
  ('full_N','uint64_t(32),16,1','uint64_t(31),16,1')]:
  bad=entry.replace(old,new);assert bad!=entry,name;assert run(bad,name).returncode!=0,name
print('Nine fault controls/whole-source inverse/protected7 PASS; one Vector FIFO/software FMA is not hardware evidence.')
