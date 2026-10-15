#!/usr/bin/env python3
"""Execute actual row finalizer concurrently with deferred DMA and workspace guards."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('__aicore__ inline void FinalizeSplitTTRows(');b=s.index('template<typename T,bool PACKED_FINAL=false,bool ROW_FINAL=false>',a)
body=s[a:b]
old=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
inv=s[:a]+s[b:];inv=inv.replace('bool PACKED_FINAL=false,bool ROW_FINAL=false','bool PACKED_FINAL=false',1)
inv=inv.replace('if constexpr(ROW_FINAL)FinalizeSplitTTRows(partial,output,pipe);\nelse FinalizeSplitKND<PACKED_FINAL>','FinalizeSplitKND<PACKED_FINAL>',1)
a=inv.index('inline bool UseSplitTTRowFinalize(');b=inv.index('using CacheKey=',a);inv=inv[:a]+inv[b:]
hook='''
if(UseSplitTTRowFinalize(s,p,x1,x2)){
bmmms_manual_split_tt<T,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);return;}
'''
assert hook in inv;inv=inv.replace(hook,'',1);assert inv==old,'unrelated changes'
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name])
PRE=r'''
#include <vector>
#include <memory>
#include <functional>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <cassert>
#include <cmath>
#include <iostream>
#include <algorithm>
#include <cstdint>
#define __aicore__
#define __gm__
#define PIPE_V 0
using GM_ADDR=void*;
thread_local unsigned worker,readCount=0;thread_local bool published=false;
std::mutex mu;std::condition_variable cv;unsigned arrived=0;
namespace AscendC{
enum class TPosition{VECCALC};enum class HardEvent{MTE2_V,V_MTE3,MTE3_S};enum class ReduceOrder{ORDER_ONLY_VALUE};
struct TPipe{};thread_local std::vector<std::function<void()>> reads,writes;
struct Mem{std::vector<float>v;std::vector<bool>defined;Mem(unsigned n):v(n),defined(n,false){}};
template<class T>struct LocalTensor{std::shared_ptr<Mem>p;unsigned off=0;LocalTensor operator[](unsigned n)const{return{p,off+n};}float get(unsigned n)const{assert(off+n<p->v.size()&&p->defined[off+n]);return p->v[off+n];}void put(unsigned n,float f)const{assert(off+n<p->v.size());p->v[off+n]=f;p->defined[off+n]=true;}};
template<TPosition P>struct TBuf{std::shared_ptr<Mem>p;template<class T>LocalTensor<T>Get(){return{p,0};}};
struct TPipeMock:TPipe{};
template<class T>struct GlobalTensor{T*p;unsigned off=0,size=0;void SetGlobalBuffer(T*q,unsigned n){p=q;size=n;}GlobalTensor operator[](unsigned n)const{return{p,off+n,size};}};
struct DataCopyParams{unsigned blockCount,blockLen,srcStride,dstStride;};struct DataCopyExtParams{unsigned count,len,a,b,c;};struct BinaryRepeatParams{unsigned a,b,c,d,e,f;};
unsigned GetBlockIdx(){return worker;}
void DataCopy(LocalTensor<float>dst,GlobalTensor<float>src,DataCopyParams cp){
 if(cp.blockLen==64){assert(src.off==worker*512&&cp.blockCount==8&&cp.srcStride==448&&cp.dstStride==0);}
 else {std::lock_guard<std::mutex>lock(mu);assert(worker==0&&arrived==8&&cp.blockCount==8&&cp.blockLen==1&&cp.srcStride==63&&cp.dstStride==0);}
 reads.push_back([=]{for(unsigned b=0;b<cp.blockCount;++b)for(unsigned x=0;x<cp.blockLen*8;++x){unsigned from=src.off+b*(cp.blockLen+cp.srcStride)*8+x;assert(from<src.size);dst.put(b*(cp.blockLen+cp.dstStride)*8+x,src.p[from]);}++readCount;});}
void DataCopy(GlobalTensor<float>dst,LocalTensor<float>src,unsigned count){assert(count==8&&dst.off==worker*512&&readCount==1);writes.push_back([=]{for(unsigned i=0;i<count;++i){assert(dst.off+i<dst.size);dst.p[dst.off+i]=src.get(i);}published=true;});}
void Add(LocalTensor<float>d,LocalTensor<float>a,LocalTensor<float>b,uint64_t mask,unsigned repeats,BinaryRepeatParams p){assert(mask==64&&repeats==8&&p.a==1&&p.b==1&&p.c==1&&p.d==8&&p.e==8&&p.f==8);for(unsigned i=0;i<512;++i)d.put(i,a.get(i)+b.get(i));}
void WholeReduceMax(LocalTensor<float>d,LocalTensor<float>a,uint64_t mask,unsigned repeats,unsigned dr,unsigned bs,unsigned rs,ReduceOrder){assert(mask==64&&repeats==8&&dr==1&&bs==1&&rs==8);for(unsigned r=0;r<8;++r){float x=-INFINITY;for(unsigned n=0;n<64;++n)x=std::max(x,a.get(r*64+n));d.put(r,x);}}
void Duplicate(LocalTensor<float>d,float v,unsigned n){for(unsigned i=0;i<n;++i)d.put(i,v);}
template<class T,bool B>void ReduceSum(LocalTensor<float>d,LocalTensor<float>a,LocalTensor<float>,unsigned n){float x=0;for(unsigned i=0;i<n;++i)x+=a.get(i);d.put(0,x);}
template<int>void PipeBarrier(){}
template<bool>void SyncAll(){assert(published&&reads.empty()&&writes.empty());std::unique_lock<std::mutex>lock(mu);++arrived;cv.notify_all();cv.wait(lock,[]{return arrived==8;});}
void DataCopyPad(GlobalTensor<float>d,LocalTensor<float>a,DataCopyExtParams cp){assert(worker==0&&cp.count==1&&cp.len==4&&cp.a==0&&cp.b==0&&cp.c==0&&d.size==1);d.p[0]=a.get(0);}
}
struct Pipe:AscendC::TPipe{template<AscendC::TPosition P>void InitBuffer(AscendC::TBuf<P>&b,unsigned bytes){assert(bytes%4==0);b.p=std::make_shared<AscendC::Mem>(bytes/4);}};
// Preserve the extracted function's TPipe signature and its real allocation calls.
'''
PRE=PRE.replace('struct TPipe{};', 'template<TPosition P>struct TBuf; struct TPipe{template<TPosition P>void InitBuffer(TBuf<P>&b,unsigned bytes);};')
PRE+=r'''
template<AscendC::TPosition P>void AscendC::TPipe::InitBuffer(AscendC::TBuf<P>&b,unsigned bytes){assert(bytes%4==0);b.p=std::make_shared<AscendC::Mem>(bytes/4);}
template<AscendC::HardEvent E>void Fence(){if constexpr(E==AscendC::HardEvent::MTE2_V){for(auto&f:AscendC::reads)f();AscendC::reads.clear();}else if constexpr(E==AscendC::HardEvent::MTE3_S){for(auto&f:AscendC::writes)f();AscendC::writes.clear();}}
'''
END=r'''
int main(){for(unsigned seed=0;seed<4;++seed){arrived=0;std::vector<float>part(32768+16,1234567),saved;float out[17];std::fill(out,out+17,987654);
for(unsigned k=0;k<8;++k)for(unsigned m=0;m<64;++m)for(unsigned n=0;n<64;++n)part[k*4096+m*64+n]=seed==0?-float(1+(k*3+m*5+n*7)%19):float(int((k*13+m*7+n*11+seed)%37)-18);
saved=part;double ref=0;for(unsigned m=0;m<64;++m){double mx=-INFINITY;for(unsigned n=0;n<64;++n){double x=0;for(unsigned k=0;k<8;++k)x+=saved[k*4096+m*64+n];mx=std::max(mx,x);}ref+=mx;}
std::vector<std::thread>threads;for(unsigned w=0;w<8;++w)threads.emplace_back([&,w]{worker=w;readCount=0;published=false;AscendC::TPipe p;FinalizeSplitTTRows(part.data(),out,p);assert(readCount==(w==0?2:1)&&published);});for(auto&t:threads)t.join();assert(out[0]==ref);if(seed==0)assert(out[0]<0);for(unsigned i=1;i<17;++i)assert(out[i]==987654);for(unsigned i=0;i<part.size();++i)if(i>=4096||i%512>=8)assert(part[i]==saved[i]);
}std::cout<<"Actual concurrent 8-AIV row finalizer: all 32768 partials, four complete signed tensors, delayed read/publish, sole row ownership, final visibility, workspace/y guards PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c15-rows-') as tmp:
 d=Path(tmp)
 def run(code,name):
  src=d/(name+'.cpp');exe=d/name;src.write_text(PRE+code+END)
  subprocess.run(['c++','-std=c++17','-O2','-pthread',str(src),'-o',str(exe)],check=True)
  return subprocess.run([str(exe)],capture_output=True)
 r=run(body,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,bad in [('wrong_read_stride',body.replace('{8,64,448,0}','{8,64,0,0}')),('wrong_row_owner',body.replace('in[worker*8*64]','in[0]')),('missing_load_ready',body.replace('Fence<AscendC::HardEvent::MTE2_V>();','')),('missing_publish_ready',body.replace('Fence<AscendC::HardEvent::MTE3_S>();','')),('missing_final_barrier',body.replace('AscendC::SyncAll<true>();','')),('wrong_score_stride',body.replace('{8,1,63,0}','{8,1,0,0}'))]:
  assert bad!=body;assert run(bad,name).returncode!=0,name
print('Six fault controls and whole-source inverse/protected7 PASS; CPU partials are not native timing or FP16 layout proof')
