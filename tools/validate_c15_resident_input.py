#!/usr/bin/env python3
"""Execute extracted proposed DMA/Load2D blocks as source-address tags, not floats."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1]
s=(R/'kernel.asc').read_text();old=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True,cwd=R)
a=s.index('if constexpr(RESIDENT_INPUT){\nauto fullA=');b=s.index('}else{\nManualCopyK',a);read=s[a+len('if constexpr(RESIDENT_INPUT){\n'):b]
a=s.index('if constexpr(RESIDENT_INPUT){\nif(k0==kBegin)');b=s.index('}else{a1=aq.DeQue',a);select=s[a+len('if constexpr(RESIDENT_INPUT){\n'):b]
a=s.index('auto a2=aAll[slot*s.baseM*bk]',b);b=s.index('if constexpr(!RESIDENT_INPUT){',a);load=s[a:b]
# Every operation from MMAD to Fixpipe, completion notification and Vector finalizer is unchanged.
a=s.index('template<typename T,bool PACKED_FINAL=false,bool RESIDENT_INPUT=false>');b=s.index('inline void CheckAcl(',a);body=s[a:b]
oa=old.index('template<typename T,bool PACKED_FINAL=false>');ob=old.index('inline void CheckAcl(',oa);parent=old[oa:ob]
marker='AscendC::SetFlag<AscendC::HardEvent::MTE1_M>(loadReady[slot]);'
assert body[body.index(marker):body.index('if constexpr(RESIDENT_INPUT)for(uint32_t i=0;i<2;++i)\npipe.ReleaseEventID')]==parent[parent.index(marker):parent.index('AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);')]
assert body[body.index('AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);'):]==parent[parent.index('AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);'):]
inv=s[:a]+parent+s[b:]
g=inv.index('inline bool UseSplitTTResidentInput(');h=inv.index('using CacheKey=',g);inv=inv[:g]+inv[h:]
call='''if(packedBytes+otherBytes+1024<=ub){
if(UseSplitTTResidentInput(s,p,x1,x2))
bmmms_manual_split_tt<T,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,d);
else
bmmms_manual_split_tt<T,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,d);
}'''
assert call in inv;inv=inv.replace(call,'''if(packedBytes+otherBytes+1024<=ub)
bmmms_manual_split_tt<T,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,d);''',1);assert inv==old
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=R)
PRE=r'''
#include <cassert>
#include <cstdint>
#include <vector>
#include <deque>
#include <functional>
#include <map>
#include <iostream>
using T=uint32_t;using event_t=unsigned;
namespace AscendC {
enum class HardEvent{MTE2_MTE1,M_MTE1};
struct Store{std::vector<T>v;std::vector<bool>ok;Store(unsigned n):v(n),ok(n,false){}};
template<class U>struct LocalTensor{Store*p;unsigned off=0;LocalTensor operator[](unsigned n)const{return{p,off+n};}
 U get(unsigned i)const{assert(off+i<p->v.size()&&p->ok[off+i]);return p->v[off+i];}
 void set(unsigned i,U x)const{assert(off+i<p->v.size());p->v[off+i]=x;p->ok[off+i]=true;}};
struct Buf{Store*p;template<class U>LocalTensor<U>Get(){return{p};}};
struct Global{const std::vector<T>*p;unsigned off=0;Global operator[](unsigned n)const{return{p,off+n};}};
struct Nd2NzParams{unsigned ndNum=0,nValue=0,dValue=0,srcDValue=0,srcNdMatrixStride=0,dstNzC0Stride=0,dstNzNStride=0,dstNzMatrixStride=0;};
struct LoadData2DParams{bool ifTranspose=false;unsigned repeatTimes=0,srcStride=0;};
std::deque<std::function<void()>>dma;unsigned issued=0,done=0;std::map<unsigned,unsigned>flags;
void DataCopy(LocalTensor<T>dst,Global src,Nd2NzParams p){assert(p.ndNum&&p.nValue%16==0&&p.dValue%16==0);++issued;
 dma.push_back([=]{for(unsigned q=0;q<p.ndNum;++q)for(unsigned row=0;row<p.nValue;++row)for(unsigned col=0;col<p.dValue;++col){
 unsigned from=src.off+q*p.srcNdMatrixStride+row*p.srcDValue+col;assert(from<src.p->size());
 unsigned to=q*p.dstNzMatrixStride+col/16*p.dstNzC0Stride*16+row*p.dstNzNStride*16+col%16;dst.set(to,src.p->at(from));}});}
template<HardEvent E>void SetFlag(unsigned i){static_assert(E==HardEvent::MTE2_MTE1);assert(!flags.count(i));flags[i]=issued;}
template<HardEvent E>void WaitFlag(unsigned i){if constexpr(E==HardEvent::MTE2_MTE1){assert(flags.count(i));while(done<flags[i]){auto f=dma.front();dma.pop_front();f();++done;}flags.erase(i);}}
void LoadData(LocalTensor<T>dst,LocalTensor<T>src,LoadData2DParams p){assert(p.srcStride==1&&p.repeatTimes==32);
 for(unsigned r=0;r<p.repeatTimes;++r)for(unsigned x=0;x<16;++x)for(unsigned y=0;y<16;++y)
 dst.set(r*256+x*16+y,src.get(r*p.srcStride*256+(p.ifTranspose?y*16+x:x*16+y)));}
}
struct Schedule{unsigned m=64,n=64,k=8192,baseM=64,baseN=64,kChunk=1024;};
'''
POST=r'''
 for(unsigned row=0;row<64;++row)for(unsigned k=0;k<128;++k){
 unsigned index=(row/16*8+k/16)*256+row%16*16+k%16;
 assert(a2.get(index)==(k0+k)*64+row);
 unsigned bi=(k/16*4+row/16)*256+row%16*16+k%16;
 assert(b2.get(bi)==524288+row*8192+k0+k);}
 }
 assert(issued==2&&done==2&&AscendC::dma.empty()&&AscendC::flags.empty());
 }
 std::cout<<"Actual DMA/select/Load2D blocks: all8 K1024 splits, 1048576 L0 element source-address tags match parent panels; ready/read/bounds PASS\n";
}
'''
def run(read_code,select_code,load_code,p,name):
 frame='''int main(){using namespace AscendC;std::vector<T>av(524288),bv(524288);for(unsigned i=0;i<av.size();++i){av[i]=i;bv[i]=524288+i;}Global a{&av},b{&bv};Schedule s;constexpr unsigned bk=128;constexpr bool RESIDENT_INPUT=true;event_t inputReady[2]={0,1},loadFree[2]={0,1};
 for(unsigned split=0;split<8;++split){unsigned batch=0,kBegin=split*1024;Store aa(65536),bb(65536),la(16384),lb(16384);Buf residentABuf{&aa},residentBBuf{&bb};LocalTensor<T>aAll{&la},bAll{&lb};issued=done=0;\n'''+read_code+'''\nfor(unsigned k0=kBegin;k0<kBegin+1024;k0+=128){unsigned slot=(k0/128)%2;LocalTensor<T>a1,b1;\n'''+select_code+load_code+POST
 src=p/(name+'.cpp');exe=p/name;src.write_text(PRE+frame);subprocess.run(['c++','-std=c++17','-O2',str(src),'-o',str(exe)],check=True)
 return subprocess.run([str(exe)],capture_output=True)
with tempfile.TemporaryDirectory(prefix='bmmms-c15-resident-') as temp:
 p=Path(temp);r=run(read,select,load,p,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for label,r1,r2,r3 in [('A_matrix_stride',read.replace('ap.dstNzMatrixStride=bk*s.baseM','ap.dstNzMatrixStride=bk*s.baseM+16'),select,load),('B_gm_stride',read.replace('bp.srcDValue=s.k','bp.srcDValue=s.kChunk'),select,load),('A_ready',read,select.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(inputReady[0]);',''),load),('B_ready',read,select,load.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(inputReady[1]);','')),('B_panel_offset',read,select.replace('(k0-kBegin)*s.baseN','(k0-kBegin)*s.kChunk'),load)]:
  assert (r1,r2,r3)!=(read,select,load);assert run(r1,r2,r3,p,label).returncode!=0,label
print('Scope/unchanged math and finalizer/protected7/five negative controls PASS; hardware DMA semantics and native precision/performance PENDING')
