#!/usr/bin/env python3
"""Execute extracted producer with source tags, delayed DMA/MMAD/Fix and full math."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text();parent=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],cwd=R,text=True)
a=s.index('template<typename T>\n__schedmode__(1)__global__ __mix__(1,1)void bmmms_manual_split_tt_two_mmad(');b=s.index('inline void CheckAcl(',a);body=s[a:b]
x=body.index('#ifdef __DAV_CUBE__\n')+len('#ifdef __DAV_CUBE__\n');y=body.index('#else',x);cube=body[x:y]
assert cube.index('AscendC::Fixpipe(')<cube.index('AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(0);')<cube.index('AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);')
vector=body[y:];assert vector.index('CrossCoreWaitFlag<2>(0)')<vector.index('SyncAll<true>()')<vector.index('FinalizeSplitKND<true>')
assert 'const Schedule s{1,64,64,8192,64,64,1,1,1,8,1024,1,8,1024,64,8,25,0,0,1};' in vector
inv=s[:a]+s[b:];a=inv.index('inline bool UseSplitTTTwoMmad(');b=inv.index('using CacheKey=',a);inv=inv[:a]+inv[b:]
hook='''if(UseSplitTTTwoMmad(s,p,x1,x2)){
bmmms_manual_split_tt_two_mmad<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y);return;}
'''
assert hook in inv;inv=inv.replace(hook,'',1);assert inv==parent,'unrelated source changed'
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=R)
PRE=r'''
#include <cassert>
#include <cstdint>
#include <vector>
#include <deque>
#include <functional>
#include <map>
#include <memory>
#include <numeric>
#include <algorithm>
#include <iostream>
#include <cmath>
#include <type_traits>
#define __gm__
#define PIPE_FIX 0
using T=uint32_t;using GM_ADDR=void*;
unsigned currentWorker,seed;bool negative;uint64_t checked=0;bool notified[8];
float aval(unsigned k,unsigned m){return negative?float(1+(k*3+m*7+seed)%3):float(int((k*3+m*7+seed)%5)-2);}
float bval(unsigned n,unsigned k){return negative?-float(1+(n*5+k*7+seed)%3):float(int((n*5+k*7+seed)%7)-3);}
namespace AscendC{
enum class TPosition{A1,B1,A2,B2,CO1};enum class HardEvent{MTE2_MTE1,MTE1_M,M_MTE1,M_FIX,FIX_M};
struct Store{TPosition pos;std::vector<uint32_t>tag;std::vector<float>f;std::vector<bool>defined;bool busy=false;Store(TPosition p,unsigned count):pos(p),tag(count),f(count),defined(count,false){}};
std::vector<std::unique_ptr<Store>>memory;
template<class U>struct LocalTensor{Store*p;unsigned off=0;LocalTensor(TPosition pos,unsigned address,unsigned count){
 assert((pos==TPosition::A1&&address==0&&count==65536)||(pos==TPosition::B1&&address==131072&&count==65536)||(pos==TPosition::A2&&address==0&&count==32768)||(pos==TPosition::B2&&address==0&&count==32768)||(pos==TPosition::CO1&&address==0&&count==4096));memory.emplace_back(new Store(pos,count));p=memory.back().get();}
 LocalTensor(Store*q,unsigned o):p(q),off(o){}LocalTensor operator[](unsigned n)const{return{p,off+n};}
 U get(unsigned n)const{assert(off+n<p->defined.size()&&p->defined[off+n]);if constexpr(std::is_same<U,float>::value)return p->f[off+n];else return p->tag[off+n];}
 void set(unsigned n,U v)const{assert(off+n<p->defined.size());if constexpr(std::is_same<U,float>::value)p->f[off+n]=v;else p->tag[off+n]=v;p->defined[off+n]=true;}};
template<class U>struct GlobalTensor{U*p;unsigned off=0,size=0;void SetGlobalBuffer(U*q,unsigned count){p=q;size=count;}GlobalTensor operator[](unsigned n)const{return{p,off+n,size};}};
struct Nd2NzParams{unsigned ndNum=0,nValue=0,dValue=0,srcDValue=0,srcNdMatrixStride=0,dstNzC0Stride=0,dstNzNStride=0,dstNzMatrixStride=0;};
struct LoadData2DParams{bool ifTranspose=false;unsigned repeatTimes=0,srcStride=0;};
struct MmadParams{unsigned m=0,n=0,k=0;bool cmatrixInitVal=false;};
struct FixpipeParamsV220{unsigned nSize=0,mSize=0,srcStride=0,dstStride=0;};
std::deque<std::function<void()>>dma,math,fix;unsigned dIssue=0,dDone=0,mIssue=0,mDone=0,fIssue=0,fDone=0,loads=0;bool loadReady=false,mathReady=false;
std::map<std::pair<HardEvent,unsigned>,unsigned>flags;
void SetAtomicNone(){}void SetMMColumnMajor(){}void SetLoadDataBoundary(uint64_t){}void SetLoadDataPaddingValue(uint64_t){}unsigned GetBlockIdx(){return currentWorker;}
void DataCopy(LocalTensor<T>dst,GlobalTensor<T>src,Nd2NzParams p){++dIssue;dma.push_back([=]{assert(p.ndNum&&p.nValue%16==0&&p.dValue%16==0);for(unsigned q=0;q<p.ndNum;++q)for(unsigned row=0;row<p.nValue;++row)for(unsigned col=0;col<p.dValue;++col){unsigned from=src.off+q*p.srcNdMatrixStride+row*p.srcDValue+col;assert(from<src.size);unsigned to=q*p.dstNzMatrixStride+(col/16)*p.dstNzC0Stride*16+row*p.dstNzNStride*16+col%16;dst.set(to,src.p[from]);}});}
void flush(std::deque<std::function<void()>>&q,unsigned&done,unsigned target){while(done<target){assert(!q.empty());auto f=q.front();q.pop_front();f();++done;}}
template<HardEvent E>void SetFlag(unsigned i){auto key=std::make_pair(E,i);assert(!flags.count(key));if constexpr(E==HardEvent::MTE2_MTE1)flags[key]=dIssue;else if constexpr(E==HardEvent::FIX_M)flags[key]=fIssue;else if constexpr(E==HardEvent::MTE1_M)flags[key]=loads;else flags[key]=mIssue;}
template<HardEvent E>void WaitFlag(unsigned i){auto key=std::make_pair(E,i);assert(flags.count(key));auto count=flags[key];flags.erase(key);if constexpr(E==HardEvent::MTE2_MTE1)flush(dma,dDone,count);else if constexpr(E==HardEvent::MTE1_M){assert(count==loads);loadReady=true;}else if constexpr(E==HardEvent::FIX_M)flush(fix,fDone,count);else{flush(math,mDone,count);if constexpr(E==HardEvent::M_FIX)mathReady=true;}}
void LoadData(LocalTensor<T>dst,LocalTensor<T>src,LoadData2DParams p){assert(!dst.p->busy&&p.repeatTimes==128&&p.srcStride==1);for(unsigned r=0;r<p.repeatTimes;++r)for(unsigned x=0;x<16;++x)for(unsigned y=0;y<16;++y)dst.set(r*256+x*16+y,src.get(r*256+(p.ifTranspose?y*16+x:x*16+y)));++loads;loadReady=false;}
void Mmad(LocalTensor<float>c,LocalTensor<T>a,LocalTensor<T>b,MmadParams mp){assert(loadReady&&mp.m==64&&mp.n==64&&mp.k==512);loadReady=false;assert(!a.p->busy&&!b.p->busy);a.p->busy=b.p->busy=true;unsigned pass=mIssue++;mathReady=false;
 math.push_back([=]{assert(mp.cmatrixInitVal==(pass==0));unsigned k0=currentWorker*1024+pass*512;
 for(unsigned m=0;m<64;++m)for(unsigned k=0;k<512;++k){assert(a.get((m/16*32+k/16)*256+m%16*16+k%16)==(k0+k)*64+m);++checked;}
 for(unsigned n=0;n<64;++n)for(unsigned k=0;k<512;++k){assert(b.get((k/16*4+n/16)*256+n%16*16+k%16)==524288+n*8192+k0+k);++checked;}
 for(unsigned m=0;m<64;++m)for(unsigned n=0;n<64;++n){float sum=mp.cmatrixInitVal?0:c.get(m*64+n);for(unsigned k=0;k<512;++k){auto at=a.get((m/16*32+k/16)*256+m%16*16+k%16);auto bt=b.get((k/16*4+n/16)*256+n%16*16+k%16)-524288;sum+=aval(at/64,at%64)*bval(bt/8192,bt%8192);}c.set(m*64+n,sum);}a.p->busy=b.p->busy=false;});}
void Fixpipe(GlobalTensor<float>dst,LocalTensor<float>src,FixpipeParamsV220 p){assert(mathReady&&mDone==2&&p.nSize==64&&p.mSize==64&&p.srcStride==64&&p.dstStride==64&&dst.off==currentWorker*4096);++fIssue;fix.push_back([=]{for(unsigned i=0;i<4096;++i){assert(dst.off+i<dst.size);dst.p[dst.off+i]=src.get(i);}});}
template<int Mode,int Pipe>void CrossCoreSetFlag(unsigned i){assert(Mode==2&&Pipe==PIPE_FIX&&i==0);assert(dDone==2&&mDone==2&&fDone==1&&loads==4&&dma.empty()&&math.empty()&&fix.empty()&&flags.empty());notified[currentWorker]=true;}
void reset(){memory.clear();flags.clear();dma.clear();math.clear();fix.clear();dIssue=dDone=mIssue=mDone=fIssue=fDone=loads=0;loadReady=mathReady=false;}
}
void producer(GM_ADDR x1,GM_ADDR x2,GM_ADDR partial){
'''
END=r'''
}
int main(){std::vector<T>a(524288),b(524288);std::iota(a.begin(),a.end(),0);std::iota(b.begin(),b.end(),524288);std::vector<float>parts(32768+8,9876543);
for(seed=0;seed<2;++seed)for(bool neg:{false,true}){negative=neg;for(currentWorker=0;currentWorker<8;++currentWorker){AscendC::reset();notified[currentWorker]=false;producer(a.data(),b.data(),parts.data());assert(notified[currentWorker]);}
float score=0;double golden=0;for(unsigned m=0;m<64;++m){float row=-INFINITY;double ref=-INFINITY;for(unsigned n=0;n<64;++n){float dot=0;for(unsigned ks=0;ks<8;++ks)dot+=parts[ks*4096+m*64+n];double direct=0;for(unsigned k=0;k<8192;++k)direct+=double(aval(k,m))*bval(n,k);assert(dot==direct);row=std::max(row,dot);ref=std::max(ref,direct);}score+=row;golden+=ref;}assert(score==golden);if(negative)assert(score<0);for(unsigned i=32768;i<32776;++i)assert(parts[i]==9876543);
}for(unsigned i=0;i<524288;++i)assert(a[i]==i&&b[i]==524288+i);assert(checked==4194304);std::cout<<"Actual producer:4194304 source-address checks,32 split tasks/two K512 MMAD each, delayed DMA/L0 readers/Fix completion,4 full M64N64K8192 golden reductions PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c15-two-mmad-') as tmp:
 d=Path(tmp)
 def run(code,name):
  src=d/(name+'.cpp');exe=d/name;src.write_text(PRE+code+END);subprocess.run(['c++','-std=c++17','-O2',str(src),'-o',str(exe)],check=True);return subprocess.run([str(exe)],capture_output=True)
 result=run(cube,'good');assert result.returncode==0,result.stderr.decode();print(result.stdout.decode(),end='')
 for name,code in [('wrong_A_panel_stride',cube.replace('ap.dstNzMatrixStride=512*64','ap.dstNzMatrixStride=512*64+16')),('wrong_B_gm_stride',cube.replace('bp.srcDValue=8192','bp.srcDValue=1024')),('missing_B_ready',cube.replace('if(pass==0)AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(1);','')),('early_L0_overwrite',cube.replace('AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(0);','')),('missing_load_ready',cube.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE1_M>(0);','')),('wrong_accumulator_init',cube.replace('mp.cmatrixInitVal=pass==0','mp.cmatrixInitVal=true')),('missing_fix_ready',cube.replace('AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(0);',''))]:
  assert code!=cube;assert run(code,name).returncode!=0,name
print('Whole-source inverse/protected7/literal plan/producer-ready and seven fault controls PASS; tags and integer math do not prove native FP16 or hardware layout/speed')
