#!/usr/bin/env python3
"""Audit parent Norm full-K L1 caching with fixed public source.

Unmodified public 8.3 tiler, extracted actual cache methods, explicit queue/index
metadata model. Not installed CANN9, full scheduler simulation or NPU profiling.
Use --source /path/to/fixed/ascendc-api-adv.
"""
from pathlib import Path
import subprocess,shutil,hashlib
root=Path(__file__).resolve().parents[1]
bootstrap=(root/'tools/inspect_public_matmul_tiling.py').read_text()
env={};exec(bootstrap[:bootstrap.index("put('probe.cpp',")],env)
put,src,out=env['put'],env['src'],env['out']
put('tiling/platform/platform_ascendc.h','#pragma once\n#include <cstdint>\nnamespace platform_ascendc {\nenum class SocVersion{ASCEND910,ASCEND310P,ASCEND910B,ASCEND310B,ASCEND910_95};\nenum class CoreMemType{L1,L0_C,UB,L0_A,L0_B};\nstruct PlatformAscendC {\nint aic=20,aiv=40;uint64_t l1=524288,l0c=131072,ub=196608,l0a=65536,l0b=65536;\nstatic PlatformAscendC* GetInstance(){static PlatformAscendC p;return &p;}\nSocVersion GetSocVersion() const{return SocVersion::ASCEND910B;}\nint GetCoreNumAic(){return aic;}int GetCoreNumAiv(){return aiv;}\nuint64_t GetLibApiWorkSpaceSize(){return 16*1024*1024;}\nvoid GetCoreMemSize(CoreMemType t,uint64_t& n) const{\nn=t==CoreMemType::L1?l1:t==CoreMemType::L0_C?l0c:t==CoreMemType::UB?ub:t==CoreMemType::L0_A?l0a:l0b;}\n};using PlatformAscendCManager=PlatformAscendC;\n}\n')
put('kernel_tiling/kernel_tiling.h','#pragma once\n#include <cstdint>\n'+env['raw']+'namespace AscendC{namespace tiling{using TCubeTiling=::TCubeTiling;}}\n')
baseline=subprocess.check_output(['git','show','968e957:kernel.asc'],cwd=root,text=True)
shapes=baseline[baseline.index('struct Shape {'):baseline.index('template <AscendC::HardEvent')]
host=baseline[baseline.index('struct Plan {'):baseline.index('using CacheKey =')]
cache_source=src/'impl/matmul/resource/cube_in_buffer/cube_in_buffer_normal.h'
raw=cache_source.read_text()
methods=raw[raw.index('    __aicore__ inline LocalTensor<TransT> AllocTensor('):raw.index('    __aicore__ inline void EnQue(')]
code=r'''#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>
#include "lib/matmul/matmul_tiling.h"
inline int64_t Ceil(int64_t n,int64_t d){return (n+d-1)/d;}
#define __aicore__
#define ASCENDC_ASSERT(cond,body) assert(cond)
template<class T>struct LocalTensor{int offset=0;LocalTensor operator[](int n)const{return {offset+n};}};
template<class T>constexpr LocalTensor<T> NULL_TENSOR{};
struct Queue {
 int allocations=0,releases=0;bool live=false;
 template<class T>LocalTensor<T> AllocTensor(){assert(!live);live=true;++allocations;return {};}
 template<class T>void FreeTensor(LocalTensor<T>){assert(live);live=false;++releases;}
};
class Cache {
 using TransT=float;int baseBlockSize_=256,cacheSize_,cacheProc_=0;bool cacheAlloc_=false;
 Queue qid_,qidCache_;LocalTensor<float> cacheHead_;
 public:explicit Cache(int depth):cacheSize_(depth){}
'''+methods+r'''
 void CheckEmpty(){assert(cacheProc_==0 && !qidCache_.live && !qid_.live && qidCache_.allocations==qidCache_.releases);}
};
'''+shapes+'namespace Parent{'+host+'}\n'+r'''
int main(){
 unsigned configs=0,fullCache=0,oneWindow=0,repeats=0,misses=0;
 uint64_t parentReads=0,residentReads=0;
 for(int cores:{4,8,20,32})for(int m:{1024,1025,1408,1536,2048})for(int n:{1024,1025,1408,1536,2048})
 for(int k:{1024,1032,1408,1536,1544,2048,3072})for(int dt:{1,2}){
  Shape s{1,m,n,k,dt,1,1};auto p=Parent::MakePlan(s,cores);auto d=p.schedule;auto t=p.cube;++configs;
  if(d.dual!=1)continue;
  int kt=Ceil(k,t.baseK);
  assert(t.stepM==1 && t.stepN==1 && t.iterateOrder==1 && t.depthA1>=uint32_t(kt));++fullCache;
  unsigned perConfigMiss=0,perConfigRepeat=0;
  for(unsigned ns=0;ns<d.nSplit;++ns){
   unsigned begin=ns*d.nTiles/d.nSplit,end=(ns+1)*d.nTiles/d.nSplit;
   Cache cache(t.depthA1);
   // Actual ORDER_N A index for one M basic block is k; SetTensorA resets
   // each IterateAll window in parent kernel. Queue EnQue/DeQue are metadata.
   for(unsigned nt=begin;nt<end;nt+=d.window){
    unsigned tiles=std::min(d.window,end-nt);
    ++perConfigRepeat;
    for(unsigned tile=0;tile<tiles;++tile)for(int ki=0;ki<kt;++ki){
     LocalTensor<float> a;
     if(cache.Hit(ki))a=cache.GetBuffer(ki);
     else{a=cache.AllocTensor(ki);++perConfigMiss;}
     assert(a.offset==ki*256);cache.FreeTensor(ki,a);
    }
    cache.Reset();cache.CheckEmpty();
   }
  }
  assert(perConfigMiss==perConfigRepeat*kt);
  misses+=perConfigMiss;repeats+=perConfigRepeat;
  bool single=perConfigRepeat==d.nSplit;if(single)++oneWindow;
  parentReads+=uint64_t(s.m*s.k)*perConfigRepeat;
  residentReads+=uint64_t(s.m*s.k)*d.nSplit;
 }
 assert(configs==1400 && fullCache==1000 && oneWindow>0);
 std::cout<<configs<<" fixed public tiler configurations; "<<fullCache<<" dual1 plans have full-K A cache, "<<oneWindow<<" have only one window per N shard\n";
 std::cout<<"Extracted cache methods: "<<repeats<<" window lifecycles, "<<misses<<" K-panel misses; subsequent N tiles hit; Reset/Free ownership PASS\n";
 std::cout<<"Illustrative logical A elements summed across grid: parent="<<parentReads<<" manual-resident="<<residentReads<<" (not measured bandwidth or speedup)\n";
 for(Shape s:{Shape{1,1024,1024,1024,2,1,1},Shape{1,1025,1025,1032,2,1,1},Shape{1,1536,1536,1536,2,1,1}}){
  auto p=Parent::MakePlan(s,20);auto d=p.schedule;auto t=p.cube;
  std::cout<<"Example "<<s.m<<","<<s.n<<","<<s.k<<" W="<<d.window<<" NS="<<d.nSplit<<" baseK="<<t.baseK<<" stepKa="<<t.stepKa<<" depthA1="<<t.depthA1<<" ORDER_N\n";
 }
}
'''
put('probe.cpp',code)
files=['matmul_tiling.cpp','matmul_tiling_base.cpp','matmul_tiling_algorithm.cpp','math_util.cpp']
compiler=shutil.which('clang++') or shutil.which('c++')
cmd=[compiler,'-std=c++17','-O2','-include','map','-I'+str(out),'-I'+str(src),str(out/'probe.cpp')]+[str(src/'impl/matmul/tiling'/f) for f in files]+['-o',str(out/'cache-audit')]
subprocess.run(cmd,check=True);subprocess.run([str(out/'cache-audit')],check=True)
print('Actual cache source SHA256:',hashlib.sha256(cache_source.read_bytes()).hexdigest())
print('Installed CANN9 cache behavior and NPU traffic/latency are not established.')
env['tmp'].cleanup()
