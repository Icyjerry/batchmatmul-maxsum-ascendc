#!/usr/bin/env python3
"""Execute actual mixed-half/FP32 entry with deferred engines and encoded full-K data."""
from pathlib import Path
import subprocess,tempfile,struct,random,math
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('__global__ __vector__ void bmmms_dot_short_mixed32(');b=s.index('struct TinyKernelShape',a);entry=s[a:b]
g=s.index('inline bool UseMixedDot32(');h=s.index('using CacheKey=',g);guard=s[g:h]
hook='''if(UseMixedDot32(s,p,x1,x2)){
bmmms_dot_short_mixed32<<<1,nullptr,stream>>>(x1,x2,y);return;}
'''
inv=s[:a]+s[b:];inv=inv.replace(guard,'',1).replace(hook,'',1)
assert inv==subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name])
PRE=r'''
#include <cstdint>
#include <cstring>
#include <cassert>
#include <cmath>
#include <functional>
#include <vector>
#include <fstream>
#include <iostream>
#define __global__
#define __vector__
#define __gm__
#define PIPE_V 0
#define PIPE_ALL 1
struct half{uint16_t bits;};using GM_ADDR=void*;
float fp(half h){unsigned e=(h.bits>>10)&31,m=h.bits&1023;assert(e!=31);float x=e?std::ldexp(float(1024+m),int(e)-25):std::ldexp(float(m),-24);return h.bits&32768?-x:x;}
namespace AscendC{
enum class TPosition{VECCALC};enum class HardEvent{MTE2_V,V_MTE3};
alignas(32)uint8_t ub[288+32];bool defined[288];bool inputReady,productReady,outputReady;
std::vector<std::function<void()>>dma,vec,output;
void flush(std::vector<std::function<void()>>&v){for(auto&f:v)f();v.clear();}
template<class T>struct LocalTensor{unsigned off,count;LocalTensor(TPosition,unsigned o,unsigned n):off(o),count(n){assert(o%32==0&&o+n*sizeof(T)<=288);}T get(unsigned i)const{assert(i<count);for(unsigned j=0;j<sizeof(T);++j)assert(defined[off+i*sizeof(T)+j]);T x;memcpy(&x,ub+off+i*sizeof(T),sizeof(T));return x;}void put(unsigned i,T v)const{assert(i<count);memcpy(ub+off+i*sizeof(T),&v,sizeof(T));for(unsigned j=0;j<sizeof(T);++j)defined[off+i*sizeof(T)+j]=true;}};
template<class T>struct GlobalTensor{T*p;unsigned count;void SetGlobalBuffer(T*q,unsigned n){p=q;count=n;}};
struct BinaryRepeatParams{unsigned a,b,c,d,e,f;};struct DataCopyExtParams{unsigned n,bytes,a,b,c;};
void DataCopy(LocalTensor<half>d,GlobalTensor<half>a,unsigned n){assert(n==32&&n==a.count&&n==d.count);dma.push_back([=]{for(unsigned i=0;i<n;++i)d.put(i,a.p[i]);});}
void Duplicate(LocalTensor<float>d,float x,uint64_t mask,uint8_t reps,uint16_t block,uint8_t stride){assert(mask==32&&reps==1&&block==1&&stride==8);vec.push_back([=]{for(unsigned i=0;i<32;++i)d.put(i,x);});}
template<class T,class U>void MulAddDst(LocalTensor<T>d,LocalTensor<U>a,LocalTensor<U>b,uint64_t mask,uint8_t reps,BinaryRepeatParams p){assert(inputReady&&mask==32&&reps==1&&p.a==1&&p.b==1&&p.c==1);std::vector<float>v;for(unsigned i=0;i<32;++i)v.push_back(std::fma(fp(a.get(i)),fp(b.get(i)),d.get(i)));productReady=false;vec.push_back([=]{for(unsigned i=0;i<32;++i)d.put(i,v[i]);productReady=true;});}
void WholeReduceSum(LocalTensor<float>d,LocalTensor<float>a,uint64_t mask,unsigned repeats,unsigned dst,unsigned blk,unsigned rep){assert(productReady&&mask==32&&repeats==1&&dst==1&&blk==1&&rep==4);float x=0;for(unsigned i=0;i<32;++i)x+=a.get(i);vec.push_back([=]{d.put(0,x);});}
template<HardEvent E>void SetFlag(unsigned i){assert(i==0);}template<HardEvent E>void WaitFlag(unsigned i){assert(i==0);if constexpr(E==HardEvent::MTE2_V){flush(dma);inputReady=true;}else{flush(vec);outputReady=true;}}
void DataCopyPad(GlobalTensor<float>d,LocalTensor<float>a,DataCopyExtParams p){assert(outputReady&&p.n==1&&p.bytes==4&&p.a==0&&p.b==0&&p.c==0&&d.count==1);output.push_back([=]{d.p[0]=a.get(0);});}
template<int P>void PipeBarrier(){if constexpr(P==PIPE_V)flush(vec);else{flush(dma);flush(vec);flush(output);}}
}
'''
END=r'''
int main(int argc,char**argv){assert(argc==2);std::ifstream in(argv[1],std::ios::binary);unsigned exact,count=0;while(in.read((char*)&exact,4)){alignas(32)half a[32],b[32];in.read((char*)a,64);in.read((char*)b,64);float expected;in.read((char*)&expected,4);auto copyA=std::vector<half>(a,a+32),copyB=std::vector<half>(b,b+32);float out[17];for(auto&x:out)x=1234567;
using namespace AscendC;memset(ub,0xab,sizeof ub);memset(defined,0,sizeof defined);inputReady=productReady=outputReady=false;dma.clear();vec.clear();output.clear();bmmms_dot_short_mixed32(a,b,out);assert(dma.empty()&&vec.empty()&&output.empty());assert(std::isfinite(out[0]));if(exact)assert(!memcmp(out,&expected,4));else assert(std::abs(double(out[0])-expected)<=1e-4+1e-4*std::abs(expected));for(unsigned i=1;i<17;++i)assert(out[i]==1234567);for(unsigned i=288;i<sizeof ub;++i)assert(ub[i]==0xab);assert(!memcmp(a,copyA.data(),64)&&!memcmp(b,copyB.data(),64));++count;
}assert(count==2115);std::cout<<"Actual entry:2115 encoded full-K32 fixtures, all63488 finite FP16 encodings, mixed/negative/large-product/small-product exact controls, deferred DMA/vector/output and UB/y/input guards PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c1-mixed-') as tmp:
 d=Path(tmp);cases=[];finite=[x for x in range(65536) if x&0x7c00!=0x7c00]
 for i in range(0,len(finite),32):cases.append((finite[i:i+32],[0x3c00]*32,1))
 rng=random.Random(1746);enc=lambda x:struct.unpack('<H',struct.pack('<e',x))[0];dec=lambda x:struct.unpack('<e',struct.pack('<H',x))[0]
 for i in range(128):cases.append(([enc(rng.uniform(-1,1)) for _ in range(32)],[enc(rng.uniform(-1,1)) for _ in range(32)],0))
 cases.extend([([0x7bff]+[0]*31,[0x7bff]+[0]*31,1),([0x400]*32,[0x400]*32,1),([0x3c00]*32,[0xbc00]*32,1)])
 data=bytearray()
 for a,b,exact in cases:
  golden=struct.unpack('<f',struct.pack('<f',math.fsum(dec(x)*dec(y) for x,y in zip(a,b))))[0]
  data+=struct.pack('<I32H32Hf',exact,*a,*b,golden)
 (d/'inputs').write_bytes(data)
 def run(code,name):
  p=d/(name+'.cpp');e=d/name;p.write_text(PRE+code+END);subprocess.run(['c++','-std=c++17','-O2',str(p),'-o',str(e)],check=True);return subprocess.run([str(e),str(d/'inputs')],capture_output=True)
 r=run(entry,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,bad in [('missing_input_ready',entry.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);','')),('missing_zero_init',entry.replace('AscendC::Duplicate(prod,0.0f,uint64_t(32),uint8_t(1),uint16_t(1),uint8_t(8));','')),('wrong_K',entry.replace('(prod,ra,rb,uint64_t(32)','(prod,ra,rb,uint64_t(16)')),('missing_output_ready',entry.replace('AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(0);','')),('missing_terminal',entry.replace('AscendC::PipeBarrier<PIPE_ALL>();',''))]:
  assert bad!=entry;assert run(bad,name).returncode!=0,name
print('Five fault controls, full-source inverse/protected7 PASS; software mixed MAC is an assumption requiring native overflow/underflow exact checks')
