#!/usr/bin/env python3
"""Execute extracted scalar kernel with public-API mocks and independent bit/golden data."""
from pathlib import Path
import subprocess,tempfile,struct,random,math
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text();old=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],cwd=R,text=True)
a=s.index('template<bool BF16>__aicore__ inline float ScalarDotDecode');b=s.index('struct TinyKernelShape',a);device=s[a:b]
g=s.index('inline bool UseScalarDot32(');h=s.index('inline bool UseSmallC5Direct',g);guard=s[g:h]
call='''if(UseScalarDot32(s,p,x1,x2)){
if(s.dtype==2)bmmms_scalar_cache_dot32<true><<<1,nullptr,stream>>>(x1,x2,y);
else bmmms_scalar_cache_dot32<false><<<1,nullptr,stream>>>(x1,x2,y);
return;}
'''
inv=s[:a]+s[b:];inv=inv.replace(guard,'',1).replace(call,'',1);assert inv==old
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=R)
PRE=r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#define __aicore__
#define __global__
#define __vector__
#define __ubuf__
#define __gm__
#define PIPE_ALL 0
using GM_ADDR=uint8_t*;
namespace AscendC {
enum class TPosition{VECCALC};enum class CacheLine{SINGLE_CACHE_LINE};enum class DcciDst{CACHELINE_OUT,CACHELINE_UB};enum class HardEvent{S_MTE3};
uint32_t*ga,*gb;uint32_t ca[16],cb[16];bool ia,ib,ubclean,ready,pending;float sumValue,cleanSum;
template<class T>struct GlobalTensor{T*p;void SetGlobalBuffer(T*q,unsigned){p=q;}T GetValue(unsigned i){assert(i<16);if((void*)p==(void*)ga){if(ia){memcpy(ca,ga,64);ia=false;}return ca[i];}assert((void*)p==(void*)gb);if(ib){memcpy(cb,gb,64);ib=false;}return cb[i];}};
template<class T>struct LocalTensor{LocalTensor(TPosition,unsigned offset,unsigned count){assert(offset==0&&count==8);}uintptr_t GetPhyAddr()const{return 0;}void SetValue(unsigned i,T v){assert(i==0);sumValue=v;ubclean=false;}};
template<class T,CacheLine,DcciDst dst>void DataCacheCleanAndInvalid(GlobalTensor<T>x){assert(dst==DcciDst::CACHELINE_OUT);if((void*)x.p==(void*)ga)ia=true;else{assert((void*)x.p==(void*)gb);ib=true;}}
template<class T,CacheLine,DcciDst dst>void DataCacheCleanAndInvalid(LocalTensor<T>){assert(dst==DcciDst::CACHELINE_UB);cleanSum=sumValue;ubclean=true;}
template<HardEvent>void SetFlag(unsigned n){assert(n==0);}template<HardEvent>void WaitFlag(unsigned n){assert(n==0);ready=true;}
struct DataCopyExtParams{unsigned count,len,src,dst,unused;};
void DataCopyPad(GlobalTensor<float>out,LocalTensor<float>,DataCopyExtParams p){assert(ready&&p.count==1&&p.len==4);out.p[0]=ubclean?cleanSum:0;pending=true;}
template<int>void PipeBarrier(){pending=false;}
}
void dcci(void*p,uint64_t,uint64_t){assert(p==nullptr);AscendC::cleanSum=AscendC::sumValue;AscendC::ubclean=true;}
'''
MAIN=r'''
int main(int argc,char**argv){assert(argc==3);unsigned n=0;std::ifstream bits(argv[1],std::ios::binary);uint32_t dt,h,wanted;
while(bits.read((char*)&dt,4)){bits.read((char*)&h,4);bits.read((char*)&wanted,4);float got=dt?ScalarDotDecode<true>(h):ScalarDotDecode<false>(h);uint32_t raw;memcpy(&raw,&got,4);assert(raw==wanted);++n;}assert(n==128768);
std::ifstream data(argv[2],std::ios::binary);unsigned cases=0;while(data.read((char*)&dt,4)){alignas(64)uint32_t a[16],b[16];data.read((char*)a,64);data.read((char*)b,64);double expected;data.read((char*)&expected,8);float y[17];for(float&v:y)v=9876543;
using namespace AscendC;ga=a;gb=b;for(unsigned i=0;i<16;++i)ca[i]=cb[i]=0;ia=ib=ubclean=ready=pending=false;
uint32_t beforea[16],beforeb[16];memcpy(beforea,a,64);memcpy(beforeb,b,64);
if(dt)bmmms_scalar_cache_dot32<true>((GM_ADDR)a,(GM_ADDR)b,(GM_ADDR)y);else bmmms_scalar_cache_dot32<false>((GM_ADDR)a,(GM_ADDR)b,(GM_ADDR)y);
assert(!pending);assert(std::isfinite(y[0]));assert(std::abs(double(y[0])-expected)<=1e-4+1e-4*std::abs(expected));for(unsigned i=1;i<17;++i)assert(y[i]==9876543);assert(!memcmp(beforea,a,64)&&!memcmp(beforeb,b,64));++cases;
}assert(cases==256);std::cout<<n<<" finite FP16/BF16 bit patterns and "<<cases<<" encoded full-K32 mixed/negative/subnormal/zero/cancellation cases PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c1-scalar-') as tmp:
 d=Path(tmp);raw=bytearray()
 for dt in (0,1):
  for h in range(65536):
   if (dt and h&0x7f80==0x7f80) or (not dt and h&0x7c00==0x7c00):continue
   wanted=h<<16 if dt else struct.unpack('<I',struct.pack('<f',struct.unpack('<e',struct.pack('<H',h))[0]))[0]
   raw+=struct.pack('<III',dt,h,wanted)
 (d/'bits').write_bytes(raw);raw=bytearray();rng=random.Random(1746)
 for dt in (0,1):
  def encode(x):
   if not dt:return struct.unpack('<H',struct.pack('<e',x))[0]
   bits=struct.unpack('<I',struct.pack('<f',x))[0];return ((bits+0x7fff+((bits>>16)&1))>>16)&65535
  def decode(h):return struct.unpack('<f',struct.pack('<I',h<<16))[0] if dt else struct.unpack('<e',struct.pack('<H',h))[0]
  for seed in range(128):
   a=[rng.uniform(-.5,.5) for _ in range(32)];b=[rng.uniform(-.5,.5) for _ in range(32)]
   if seed%4==1:a=list(map(abs,a));b=[-abs(x) for x in b]
   if seed%4==2:a=[(-1 if i%2 else 1)*2**-24 for i in range(32)];b=[.5]*32
   if seed%4==3:a=[0.0]*32
   ah=list(map(encode,a));bh=list(map(encode,b));gold=math.fsum(decode(x)*decode(y) for x,y in zip(ah,bh));raw+=struct.pack('<I32H32Hd',dt,*ah,*bh,gold)
 (d/'cases').write_bytes(raw)
 def run(code,name):
  f=d/(name+'.cpp');exe=d/name;f.write_text(PRE+code+MAIN);subprocess.run(['c++','-std=c++17','-O2',str(f),'-o',str(exe)],check=True);return subprocess.run([str(exe),str(d/'bits'),str(d/'cases')],capture_output=True)
 r=run(device,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,code in [('no_a_invalidation',device.replace('AscendC::DcciDst::CACHELINE_OUT>(a);','AscendC::DcciDst::CACHELINE_OUT>(b);',1)),('no_ub_flush',device.replace(next(line for line in device.splitlines(True) if line.startswith('dcci(')),'',1)),('missing_output_dependency',device.replace('AscendC::WaitFlag<AscendC::HardEvent::S_MTE3>(0);','')),('overwide_y',device.replace('cp{1,sizeof(float),','cp{1,8,')),('incomplete_K',device.replace('i<16','i<15')),('no_terminal',device.replace('AscendC::PipeBarrier<PIPE_ALL>();',''))]:
  assert code!=device;assert run(code,name).returncode!=0,name
print('Actual kernel extraction/default inverse/protected7/six negative controls PASS; mocked cache/events are not native hardware timing/coherence proof')
