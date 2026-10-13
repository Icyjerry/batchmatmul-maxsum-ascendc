#!/usr/bin/env python3
"""Execute actual proposed raw-read/load helpers under explicit CPU Load3D model."""
from pathlib import Path
import subprocess,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
START='template<typename T>__aicore__ inline void SingleTileRawRowRead('
END='template<bool DIRECT_BATCH>\nstruct SingleTileDirectContext'
PRE=r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <deque>
#include <functional>
#include <vector>
#include <map>
#include <iostream>
#define __aicore__
#define __gm__
using half=uint16_t;
namespace AscendC {
using TEventID=unsigned;
enum class HardEvent{MTE2_MTE1};enum class TPosition{A1,B1,A2,B2};
struct Storage{std::vector<uint16_t>v;std::vector<bool>valid;TPosition pos;Storage(size_t n,TPosition p):v(n,0xfbad),valid(n,false),pos(p){}};
template<class T>struct LocalTensor{
 Storage* owner;size_t off=0;
 LocalTensor operator[](size_t i)const{return {owner,off+i};}
 template<class U>LocalTensor<U> ReinterpretCast()const{static_assert(sizeof(T)==sizeof(U));return {owner,off};}
 T read(size_t i)const{assert(off+i<owner->v.size()&&owner->valid[off+i]);return owner->v[off+i];}
 void write(size_t i,T x)const{assert(off+i<owner->v.size());owner->v[off+i]=x;owner->valid[off+i]=true;}
};
std::map<uintptr_t,const std::vector<uint16_t>*> gm;
template<class T>struct GlobalTensor{
 const std::vector<T>*v=nullptr;size_t off=0;
 void SetGlobalBuffer(T*ptr){assert(gm.count(reinterpret_cast<uintptr_t>(ptr)));v=gm.at(reinterpret_cast<uintptr_t>(ptr));}
 GlobalTensor operator[](size_t i)const{return {v,off+i};}
};
std::deque<std::function<void()>> dma;size_t issued=0,done=0;std::map<unsigned,size_t> ready;
template<class T>struct InitConstValueParams{uint16_t repeats,len,gap;T value;};
template<class T>void InitConstValue(LocalTensor<T>dst,InitConstValueParams<T>p){++issued;dma.push_back([=]{
 for(unsigned r=0;r<p.repeats;++r)for(unsigned i=0;i<p.len*16;++i)dst.write(r*(p.len+p.gap)*16+i,p.value);});}
template<class T>void DataCopy(LocalTensor<T>dst,GlobalTensor<T>src,unsigned count){
 assert(count*sizeof(T)%32==0&&src.off*sizeof(T)%32==0&&src.off+count<=src.v->size());++issued;
 dma.push_back([=]{for(unsigned i=0;i<count;++i)dst.write(i,src.v->at(src.off+i));});
}
template<HardEvent>void SetFlag(unsigned id){assert(!ready.count(id));ready[id]=issued;}
template<HardEvent>void WaitFlag(unsigned id){assert(ready.count(id));while(done<ready[id]){assert(!dma.empty());auto f=dma.front();dma.pop_front();f();++done;}ready.erase(id);}
template<class T>struct LoadData3DParamsV2{
 unsigned l1H=1,l1W=0,channelSize=0,strideH=1,strideW=1,filterH=1,filterW=1,dilationFilterH=1,dilationFilterW=1;
 unsigned mStartPt=0,kStartPt=0,mExtension=0,kExtension=0;
 bool filterSizeH=false,filterSizeW=false,enTranspose=false,fMatrixCtrl=false;
};
template<class T>void LoadData(LocalTensor<T>dst,LocalTensor<T>src,LoadData3DParamsV2<T>p){
 assert(p.l1H==1&&p.channelSize==16&&p.filterH==1&&p.filterW==12&&p.strideH==1&&p.strideW==12);
 assert(p.dilationFilterH==1&&p.dilationFilterW==1&&!p.filterSizeH&&!p.filterSizeW&&!p.enTranspose);
 assert(!p.mStartPt&&!p.kStartPt&&p.kExtension==192&&p.mExtension%16==0&&p.l1W==p.mExtension*12);
 bool right=dst.owner->pos==TPosition::B2;assert(p.fMatrixCtrl==right);
 assert(issued==4);if(!right)assert(done==2&&ready.count(1));else assert(done==4&&ready.empty());
 assert(src.owner->pos==(right?TPosition::B1:TPosition::A1));
 assert(src.off+p.l1W*16<=src.owner->v.size());
 for(unsigned m=0;m<p.mExtension;++m)for(unsigned k=0;k<192;++k){
  unsigned feature=m*p.strideW+k/16,channel=k%16;
  unsigned index=(right?(k/16*(p.mExtension/16)+m/16)*256+(m%16)*16+k%16:
                   (m/16*12+k/16)*256+(m%16)*16+k%16);
  dst.write(index,src.read(feature*16+channel));
 }
}
}
'''
POST=r'''
int main(){
 constexpr unsigned B=13,M=23,N=73,K=192,MP=32,NP=80;
 for(unsigned seed=0;seed<3;++seed)for(unsigned neg=0;neg<2;++neg){
  std::vector<half>a(B*M*K),b(B*N*K);
  for(unsigned z=0;z<B;++z)for(unsigned k=0;k<K;++k){
   for(unsigned m=0;m<M;++m)a[z*M*K+m*K+k]=1+(seed+z*7+m*3+k)%11;
   for(unsigned n=0;n<N;++n)b[z*N*K+n*K+k]=uint16_t(neg?-int(1+(seed+z*3+n*5+k)%13):int((seed+z*3+n*5+k)%17)-8);
  }
  auto aa=a,bb=b;
  for(unsigned z=0;z<B;++z){
   using namespace AscendC;assert(dma.empty()&&ready.empty());issued=done=0;
   Storage as(MP*K,TPosition::A1),bs(NP*K,TPosition::B1),ad(MP*K,TPosition::A2),bd(NP*K,TPosition::B2);
   LocalTensor<half>a1{&as},b1{&bs},a2{&ad},b2{&bd};
   gm.clear();gm[reinterpret_cast<uintptr_t>(a.data())]=&a;gm[reinterpret_cast<uintptr_t>(b.data())]=&b;
   RunActual(a.data(),b.data(),z,a1,b1,a2,b2);
   assert(dma.empty()&&ready.empty());
   for(unsigned m=0;m<MP;++m)for(unsigned k=0;k<K;++k){unsigned p=(m/16*12+k/16)*256+(m%16)*16+k%16;
    assert(a2.read(p)==(m<M?a[z*M*K+m*K+k]:0));}
   for(unsigned n=0;n<NP;++n)for(unsigned k=0;k<K;++k){unsigned p=(k/16*5+n/16)*256+(n%16)*16+k%16;
    assert(b2.read(p)==(n<N?b[z*N*K+n*K+k]:0));}
   int64_t score=0,reference=0;
   for(unsigned m=0;m<M;++m){int64_t max1=INT64_MIN,max2=INT64_MIN;
    for(unsigned n=0;n<N;++n){int64_t dot=0,ref=0;
     for(unsigned k=0;k<K;++k){unsigned ap=(m/16*12+k/16)*256+(m%16)*16+k%16,bp=(k/16*5+n/16)*256+(n%16)*16+k%16;
      dot+=int64_t(int16_t(a2.read(ap)))*int16_t(b2.read(bp));ref+=int64_t(int16_t(a[z*M*K+m*K+k]))*int16_t(b[z*N*K+n*K+k]);}
     assert(dot==ref);max1=std::max(max1,dot);max2=std::max(max2,ref);}
    if(neg)assert(max1<0);score+=max1;reference+=max2;}
   assert(score==reference&&aa==a&&bb==b);
  }
 }
 std::cout<<"Actual producer input branch/helpers PASS:78 batch pairs/fullK/normal+negative/native-tag-ZZ-ZN/explicit zero tails/input bounds/ready ordering\n";
}
'''
def main():
 s=(ROOT/'kernel.asc').read_text();old=subprocess.check_output(['git','show','e2f1b63:kernel.asc'],cwd=ROOT,text=True)
 a=s.index(START);b=s.index(END,a);helper=s[a:b]
 inv=s[:a]+s[b:]
 inv=inv.replace('bool DIRECT_BATCH=false,bool SINGLE_AIV=false,bool RAW_ROWS=false>', 'bool DIRECT_BATCH=false,bool SINGLE_AIV=false>',1)
 # Source wording is retained below; only remove the actual static-assert block.
 actual=inv[inv.index('static_assert(!RAW_ROWS'):inv.index('SingleTileDirectContext<DIRECT_BATCH>context;')]
 inv=inv.replace(actual,'',1)
 start=inv.index('if constexpr(RAW_ROWS){');else_at=inv.index('}else{',start);stop=inv.index('}SingleTileDirectFence<DIRECT_BATCH,AscendC::HardEvent::MTE1_M>();',else_at)
 caller=inv[start+len('if constexpr(RAW_ROWS){'):else_at]
 inv=inv[:start]+inv[else_at+len('}else{'):stop]+inv[stop+1:]
 inv=inv.replace('bool DIRECT_BATCH=false,bool RAW_ROWS=false>','bool DIRECT_BATCH=false>',1).replace('MP,NP,KP,DIRECT_BATCH,true,RAW_ROWS>','MP,NP,KP,DIRECT_BATCH,true>',1)
 start=inv.index('inline bool UseSmallC6RawRows(');stop=inv.index('inline bool UseSmallC5Direct(',start);inv=inv[:start]+inv[stop:]
 call='''
if(UseSmallC6RawRows(s,p,x1,x2)){
bmmms_single_tile_direct_batch_mix11<T,false,true,32,80,192,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);
return;
}'''
 assert call in inv;inv=inv.replace(call,'',1);assert inv==old,'change escaped two helpers/producer branch/MIX11 template/guard and early launch'
 for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=ROOT)
 with tempfile.TemporaryDirectory(prefix='bmmms-c6-raw-') as temp:
  p=Path(temp)
  def run(body,name,call=caller):
   frame="struct Frame{unsigned m=23,n=73,k=192;};\nvoid RunActual(void*x1,void*x2,unsigned worker,AscendC::LocalTensor<half>a1,AscendC::LocalTensor<half>b1,AscendC::LocalTensor<half>a2,AscendC::LocalTensor<half>b2){using T=half;Frame s;constexpr unsigned mp=32,np=80,kp=192;\n"+call+"}\n"
   (p/(name+'.cpp')).write_text(PRE+body+frame+POST);subprocess.run(['c++','-std=c++17','-O2',str(p/(name+'.cpp')),'-o',str(p/name)],check=True)
   return subprocess.run([str(p/name)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  r=run(helper,'model');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
  for label,bad in [('tail_fill',helper.replace('if(rows<paddedRows){','if(false){')),('row_stride',helper.replace('panel.strideW=12','panel.strideW=1')),('right_matrix',helper.replace('panel.fMatrixCtrl=RIGHT','panel.fMatrixCtrl=false')),('read_offset',helper.replace('src[offset],rows*k','src[offset+16],rows*k'))]:
   assert bad!=helper;result=run(bad,label);assert result.returncode!=0,label
  for label,bad in [('A_ready',caller.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(0);','')),('B_ready',caller.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(1);','')),('batch_stride',caller.replace('int64_t(worker)*s.n*s.k','int64_t(worker)*s.m*s.k'))]:
   assert bad!=caller;result=run(helper,label,bad);assert result.returncode!=0,label
 print('Scope/protected7/seven negative controls PASS',hashlib.sha256(s.encode()).hexdigest())
 print('CPU im2col instruction semantics are an explicit hypothesis. Native Load3D support/layout/float accuracy/performance PENDING.')
if __name__=='__main__':main()
