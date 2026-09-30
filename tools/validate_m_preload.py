#!/usr/bin/env python3
"""Run current/baseline host against fixed public tiler and actual preload predicates.

Public 8.3.T9.0.B066 source evidence only; not installed CANN9, instruction
emulation, hardware precision or performance. --source is an official checkout.
"""
from pathlib import Path
import subprocess
import shutil
import hashlib

root=Path(__file__).resolve().parents[1]
bootstrap=(root/'tools/inspect_public_matmul_tiling.py').read_text()
env={}
exec(bootstrap[:bootstrap.index("put('probe.cpp',")],env)
put,src,out=env['put'],env['src'],env['out']
platform='''#pragma once
#include <cstdint>
namespace platform_ascendc {
enum class SocVersion{ASCEND910,ASCEND310P,ASCEND910B,ASCEND310B,ASCEND910_95};
enum class CoreMemType{L1,L0_C,UB,L0_A,L0_B};
struct PlatformAscendC {
int aic=20,aiv=40;uint64_t l1=524288,l0c=131072,ub=196608,l0a=65536,l0b=65536;
static PlatformAscendC* GetInstance(){static PlatformAscendC p;return &p;}
SocVersion GetSocVersion() const{return SocVersion::ASCEND910B;}
int GetCoreNumAic(){return aic;}int GetCoreNumAiv(){return aiv;}
uint64_t GetLibApiWorkSpaceSize(){return 16*1024*1024;}
void GetCoreMemSize(CoreMemType t,uint64_t& n) const{
n=t==CoreMemType::L1?l1:t==CoreMemType::L0_C?l0c:t==CoreMemType::UB?ub:t==CoreMemType::L0_A?l0a:l0b;}
};using PlatformAscendCManager=PlatformAscendC;
}
'''
put('tiling/platform/platform_ascendc.h',platform)
put('kernel_tiling/kernel_tiling.h','#pragma once\n#include <cstdint>\n'+env['raw']+
    'namespace AscendC{namespace tiling{using TCubeTiling=::TCubeTiling;}}\n')
source=(root/'kernel.asc').read_text()
baseline=subprocess.check_output(['git','show','4f39f98:kernel.asc'],cwd=root,text=True)
def host(s):return s[s.index('struct Plan {'):s.index('using CacheKey =')]
def dual(s):
    a=s.index('__schedmode__(1) __global__ __mix__(1, 2) void bmmms_dual(')
    b=s.index('\n#endif\n}',a)+len('\n#endif\n}')
    return s[a:b]
assert dual(source).replace('DUAL_SELECTED_CONFIG<M_PRELOAD>','DUAL_CONFIG')==dual(baseline)
shapes=source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
code='''#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>
#include "lib/matmul/matmul_tiling.h"
inline int64_t Ceil(int64_t n,int64_t d){return (n+d-1)/d;}
'''+shapes+'namespace Parent{'+host(baseline)+'}\nnamespace Candidate{'+host(source)+'}\n'+r'''
unsigned checked=0,selected=0;
void check(Shape s,int cores){
 auto a=Parent::MakePlan(s,cores);auto b=Candidate::MakePlan(s,cores);++checked;
 auto x=a.schedule,y=b.schedule;
 if(y.dual==29){
  ++selected;assert(x.dual==1);y.dual=1;
  auto t=b.cube;auto* hw=platform_ascendc::PlatformAscendC::GetInstance();
  assert(t.baseM*2==y.baseM && t.baseN==y.baseN*y.window && t.baseK==(t.baseN==256?64:128));
  assert(t.stepM==1 && t.stepN==1 && t.stepKa==Ceil(s.k,t.baseK) && t.stepKb==1);
  assert(t.depthA1==2*t.stepKa && t.depthB1==2 && t.dbL0A==2 && t.dbL0B==2);
  assert(t.singleCoreM==y.baseM && t.singleCoreN==y.baseN*y.window && t.singleCoreK==s.k);
  uint64_t A=uint64_t(t.depthA1)*t.baseM*t.baseK*2;
  uint64_t B=uint64_t(t.depthB1)*t.baseN*t.baseK*2;
  assert(A+B==uint64_t(t.shareL1Size) && A+B+4096<=hw->l1);
  assert(uint64_t(t.dbL0A)*t.baseM*t.baseK*2<=hw->l0a);
  assert(uint64_t(t.dbL0B)*t.baseN*t.baseK*2<=hw->l0b);
  assert(uint64_t(t.dbL0C)*t.baseM*t.baseN*4<=hw->l0c);
  assert(t.shareL0CSize>=int64_t(t.dbL0C)*t.baseM*t.baseN*4 && uint64_t(t.shareL0CSize)<=hw->l0c);
 }
 assert(a.cubeBlocks==b.cubeBlocks && a.finalBlocks==b.finalBlocks && a.systemBytes==b.systemBytes && a.totalBytes==b.totalBytes);
 assert(a.small==b.small && a.micro==b.micro);
 assert(std::tie(x.b,x.m,x.n,x.k,x.baseM,x.baseN,x.mTiles,x.nTiles,x.nSplit,x.workers,x.vectorTile,x.window,x.kSplit,x.kChunk,x.microRows,x.batchGroup,x.dual,x.earlySum,x.tree,x.balance)==
        std::tie(y.b,y.m,y.n,y.k,y.baseM,y.baseN,y.mTiles,y.nTiles,y.nSplit,y.workers,y.vectorTile,y.window,y.kSplit,y.kChunk,y.microRows,y.batchGroup,y.dual,y.earlySum,y.tree,y.balance));
}
int main(){
 auto* hw=platform_ascendc::PlatformAscendC::GetInstance();
 for(int cores:{4,8,20,32})for(int m:{1024,1281,1408,1440,1488,1536,2048})for(int n:{1024,1281,1408,1440,1488,1536,2048})for(int k:{1024,1032,1408,1440,1488,1536,1544,1792,2048})check({1,m,n,k,2,1,1},cores);
 assert(selected>0);
 auto p=Candidate::MakePlan({1,1536,1536,1536,2,1,1},20);assert(p.schedule.dual==29);
 for(int dt:{1,2})for(int tx=0;tx<4;++tx)if(dt!=2 || tx!=3)check({1,1536,1536,1536,dt,tx/2,tx%2},20);
 for(uint64_t cap:{65536ULL,131072ULL,262144ULL}){hw->l1=cap;check({1,1536,1536,1536,2,1,1},20);assert(Candidate::MakePlan({1,1536,1536,1536,2,1,1},20).schedule.dual!=29);}
 hw->l1=524288;hw->l0b=32768;check({1,1536,1536,1536,2,1,1},20);assert(Candidate::MakePlan({1,1536,1536,1536,2,1,1},20).schedule.dual!=29);hw->l0b=65536;
#ifdef BMMMS_TUNING
 for(int pin:{0,1,2}){Candidate::Tune().dual=Parent::Tune().dual=pin;check({1,1536,1536,1536,2,1,1},20);assert(Candidate::MakePlan({1,1536,1536,1536,2,1,1},20).schedule.dual!=29);}
 Candidate::Tune()=Candidate::TuneConfig{};Parent::Tune()=Parent::TuneConfig{};
 Candidate::Tune().ns=Parent::Tune().ns=3;check({1,1536,1536,1536,2,1,1},20);assert(Candidate::MakePlan({1,1536,1536,1536,2,1,1},20).schedule.dual!=29);
#endif
 std::cout<<"Actual public tiler + extracted production/TUNING host: "<<checked<<" configurations, "<<selected<<" selected; unchanged schedule/workspace/resource fallbacks PASS\n";
}
'''
put('probe.cpp',code)
files=['matmul_tiling.cpp','matmul_tiling_base.cpp','matmul_tiling_algorithm.cpp','math_util.cpp']
compiler=shutil.which('clang++') or shutil.which('c++')
for mode in ([],['-DBMMMS_TUNING']):
    exe=out/('host-tuning' if mode else 'host')
    cmd=[compiler,'-std=c++17','-O2','-include','map',*mode,'-I'+str(out),'-I'+str(src),str(out/'probe.cpp')]+[str(src/'impl/matmul/tiling'/f) for f in files]+['-o',str(exe)]
    subprocess.run(cmd,check=True)
    subprocess.run([str(exe)],check=True)
# Execute the real public preload predicates with deferred, bounds-checked
# transfer metadata. One basic N block prevents duplicate A preload waits.
scheduler=(src/'impl/matmul/scheduler/base/scheduler_mdl_base.h').read_text()
a=scheduler.index('    __aicore__ inline void DoPreloadLoad()')
b=scheduler.index('\nprotected:',a)
methods=scheduler[a:b].replace('__aicore__','')
predicates=r'''#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>
constexpr int PRELOAD_M=1,PRELOAD_N=2,PRELOAD_K=3;
struct Config{int doMTE2Preload;};constexpr Config ToMatmulConfig(Config c){return c;}
struct Module{
 int idx=0,total=1,rows=0,bm=0,k=0,stepKa=0,reads=0,waits=0;
 bool pending=false;int transferredRows=0;
 bool FirstOuterIter(){return idx==0;}bool IsBKL1FullLoad(){return false;}
 bool IsLastInnerIter(){return idx==total-1;}
 int GetInnerIdx(){return idx;}int GetOuterIdx(){return idx;}
 int GetTotalIter(){return total;}int GetInnerIter(){return 1;}int GetInnerStartIdx(){return idx;}
 int GetStepM(){return 1;}int GetStepN(){return 1;}int GetStepKb(){return 1;}
 int GetStepKa(){return stepKa;}Module& GetTiling(){return *this;}
 int GetTileShapeOf(int tile){assert(tile<total);return std::min(bm,rows-tile*bm);}
 int GetTileShapeA(){return k;}int GetTileShapeB(){return 64;}int GetTileShapeBOf(int){return 64;}
 void AsyncLoadData(int m,int ko,int count,int width){
  assert(!pending && m==1 && ko==0 && count>0 && count<=bm && width==k);
  pending=true;transferredRows=count;++reads;
 }
 void AwaitLoadData(){assert(pending);pending=false;++waits;}
};
#define MATMUL_MODULE(name) (&name)
template<int MODE>struct Predicates{
 static constexpr Config MM_CFG{MODE};
 int cacheA1Factor_=1,cacheB1Factor_=1;
 Module KLoop,MLoop,NLoop,CopyCubeInA,CopyCubeInB,MatmulShapeTiling;
'''+methods+r'''
};
int main(){unsigned checks=0;
 for(int bm:{32,64})for(int rows=1;rows<=2*bm;++rows)for(int k:{1024,1032,1536,1544,2048,3072})for(int bk:{64,128}){
  Predicates<1> s;s.MLoop.rows=rows;s.MLoop.bm=bm;s.MLoop.total=(rows+bm-1)/bm;
  s.KLoop.total=(k+bk-1)/bk;s.KLoop.k=k;
  s.CopyCubeInA.bm=bm;s.CopyCubeInA.k=k;
  for(int m=0;m<s.MLoop.total;++m){
   s.MLoop.idx=m;
   for(int ko=0;ko<s.KLoop.total;++ko){s.KLoop.idx=ko;s.DoPreloadLoad();}
   s.DoPreloadAWait();
  }
  int expected=rows>bm?1:0;
  assert(s.CopyCubeInA.reads==expected && s.CopyCubeInA.waits==expected && !s.CopyCubeInA.pending);
  assert(s.CopyCubeInA.transferredRows==(expected?rows-bm:0));
  assert(!s.CopyCubeInB.reads && !s.CopyCubeInB.waits);++checks;
 }
 std::cout<<"Actual public M-preload predicates: "<<checks<<" full-K/tail/deferred-transfer executions PASS\n";
}
'''
put('predicates.cpp',predicates)
exe=out/'predicates'
subprocess.run([compiler,'-std=c++17','-O2',str(out/'predicates.cpp'),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
print('Kernel SHA256:',hashlib.sha256(source.encode()).hexdigest())
print('Public tiler revision:',env['revision'])
print('Existing Cube/Vector source unchanged except config selection. CANN9/NPU validation PENDING.')
env['tmp'].cleanup()
