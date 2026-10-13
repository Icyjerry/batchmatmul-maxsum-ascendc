#!/usr/bin/env python3
"""Execute extracted production Bprep with CPU byte-copy/transpose semantics."""
from pathlib import Path
import subprocess,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
START='template<typename T,bool STRIDED_STORE=false>__aicore__ inline void ManualCase12PhasedPrepB('
END='template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool RESIDENT_PAD'
PRE=r'''
#include <cassert>
#include <cstdint>
#include <vector>
#include <memory>
#include <cstring>
#include <iostream>
#define __aicore__
using half=uint16_t;
struct Schedule{int64_t b,k,n;uint32_t workers,nTiles,baseN;};
namespace AscendC {
enum class TPosition{VECIN,VECOUT};
static uint32_t block;static size_t stores;
template<class T>struct LocalTensor{
 std::shared_ptr<std::vector<T>> owner;T* p;
 LocalTensor operator[](size_t i)const{return {owner,p+i};}
 T* GetPhyAddr()const{return p;}
};
template<class T>struct GlobalTensor{T* p;T* operator[](size_t i)const{return p+i;}};
template<TPosition P,int Depth>struct TQue{
 LocalTensor<half> current;
 template<class T>LocalTensor<T> AllocTensor(){auto p=std::make_shared<std::vector<T>>(16384);return {p,p->data()};}
 void EnQue(LocalTensor<half> t){current=t;}
 template<class T>LocalTensor<T> DeQue(){return current;}
 void FreeTensor(LocalTensor<half>){}void FreeAllEvent(){}
};
struct DataCopyExtParams{uint16_t count;uint32_t len,srcGap,dstGap,reserved;};
template<class T>struct DataCopyPadExtParams{bool enabled;uint8_t left,right;T value;};
struct DataCopyParams{uint16_t count,len,srcGap,dstGap;};
struct TransDataTo5HDParams{uint32_t repeatTimes,srcRepStride,dstRepStride;bool srcHighHalf,dstHighHalf;};
uint32_t GetBlockIdx(){return block;}
template<class T>void DataCopyPad(LocalTensor<T> dst,T* src,DataCopyExtParams cp,DataCopyPadExtParams<T>){
 for(unsigned r=0;r<cp.count;++r)std::memcpy(reinterpret_cast<char*>(dst.p)+r*(cp.len+cp.dstGap*32),reinterpret_cast<char*>(src)+r*(cp.len+cp.srcGap),cp.len);
}
template<class T>void TransDataTo5HD(uint64_t dst[16],uint64_t src[16],TransDataTo5HDParams p){
 for(unsigned r=0;r<p.repeatTimes;++r)for(unsigned i=0;i<16;++i)for(unsigned j=0;j<16;++j)
  *(reinterpret_cast<T*>(dst[j]+r*p.dstRepStride*32)+i)=*(reinterpret_cast<T*>(src[i]+r*p.srcRepStride*32)+j);
}
template<class T>void DataCopy(T* dst,LocalTensor<T> src,unsigned count){++stores;std::memcpy(dst,src.p,count*sizeof(T));}
template<class T>void DataCopy(T* dst,LocalTensor<T> src,DataCopyParams cp){
 ++stores;for(unsigned i=0;i<cp.count;++i)std::memcpy(reinterpret_cast<char*>(dst)+i*(cp.len+cp.dstGap)*32,reinterpret_cast<char*>(src.p)+i*(cp.len+cp.srcGap)*32,cp.len*32);
}
}
'''
POST=r'''
int main(){
 Schedule s{1,1536,4096,20,32,128};size_t total=s.b*s.n*s.k;
 std::vector<half> input(total),old(total+32,0xa7a7),got(total+32,0xa7a7);
 for(size_t i=0;i<total;++i)input[i]=static_cast<half>((i*3571+(i/4096)*101)^0xbeef);
 AscendC::GlobalTensor<half>b{input.data()},op{old.data()+16},np{got.data()+16};
 size_t counts[2]={};
 for(unsigned mode=0;mode<2;++mode){AscendC::stores=0;
  for(unsigned phase=0;phase<2;++phase)for(AscendC::block=0;AscendC::block<2*s.workers;++AscendC::block){
   AscendC::TQue<AscendC::TPosition::VECIN,2>cq;AscendC::TQue<AscendC::TPosition::VECOUT,2>znq;
   if(mode)ManualCase12PhasedPrepB<half,true>(cq,znq,b,np,s,phase);else ManualCase12PhasedPrepB<half,false>(cq,znq,b,op,s,phase);
  }counts[mode]=AscendC::stores;
 }
 assert(old==got);assert(counts[0]==3072&&counts[1]==384);
 for(size_t i=0;i<16;++i)assert(got[i]==0xa7a7&&got[total+16+i]==0xa7a7);
 for(unsigned k=0;k<s.k;++k)for(unsigned n=0;n<s.n;++n){
  size_t offset=(n/128)*s.k*128+(k/16)*16*128+((n%128)/16)*256+(n%16)*16+k%16;
  assert(np.p[offset]==input[k*s.n+n]);
 }
 std::cout<<"Actual helper old/new full byte identity; native Zn independent coordinate coverage; guards; stores3072->384 PASS\n";
}
'''
def main():
 s=(ROOT/'kernel.asc').read_text();old=subprocess.check_output(['git','show','e2f1b63:kernel.asc'],cwd=ROOT,text=True)
 a=s.index(START);b=s.index(END,a);oa=old.index('template<typename T>__aicore__ inline void ManualCase12PhasedPrepB(');ob=old.index(END,oa)
 inverse=s[:a]+old[oa:ob]+s[b:];inverse=inverse.replace('ManualCase12PhasedPrepB<T,true>(cq,znq,b,packed,s,','ManualCase12PhasedPrepB(cq,znq,b,packed,s,')
 assert inverse==old,'change escaped helper and two phased call sites'
 for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=ROOT)
 helper=s[a:b]
 with tempfile.TemporaryDirectory(prefix='bmmms-c12-store-') as temp:
  p=Path(temp);(p/'model.cpp').write_text(PRE+helper+POST)
  subprocess.run(['c++','-std=c++17','-O2',str(p/'model.cpp'),'-o',str(p/'model')],check=True)
  subprocess.run([str(p/'model')],check=True)
  # Negative control for 32-byte gap semantics, preserving the same total storage.
  broken=helper.replace('(s.k-16)*s.baseN*sizeof(T)/32','(s.k-32)*s.baseN*sizeof(T)/32')
  assert broken!=helper;(p/'fault.cpp').write_text(PRE+broken+POST)
  subprocess.run(['c++','-std=c++17','-O2',str(p/'fault.cpp'),'-o',str(p/'fault')],check=True)
  r=subprocess.run([str(p/'fault')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  assert r.returncode!=0,'faulty destination stride escaped oracle'
 print('Scope/protected7/fault control PASS',hashlib.sha256(s.encode()).hexdigest())
 print('CPU model is not native event/precision/performance evidence.')
if __name__=='__main__':main()
