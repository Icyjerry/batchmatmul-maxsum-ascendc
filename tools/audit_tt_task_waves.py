#!/usr/bin/env python3
"""Audit task/wave geometry of historical C8 bucket, without guessing timing.

Requires --source fixed official checkout, version 8.3.T9.0.B066. Platform,
logging and tiling storage are shims; not installed CANN9 or NPU evidence.
"""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
ns={'__file__':str(root/'tools/validate_narrow_fullk.py')}
ns['__name__']='narrow_model_import'
exec((root/'tools/validate_narrow_fullk.py').read_text(),ns)
env={}
bootstrap=(root/'tools/inspect_public_matmul_tiling.py').read_text()
exec(bootstrap[:bootstrap.index("put('probe.cpp',")],env)
put,src,out=env['put'],env['src'],env['out']
put('tiling/platform/platform_ascendc.h','#pragma once\n#include <cstdint>\nnamespace platform_ascendc {\nenum class SocVersion{ASCEND910,ASCEND310P,ASCEND910B,ASCEND310B,ASCEND910_95};\nenum class CoreMemType{L1,L0_C,UB,L0_A,L0_B};\nstruct PlatformAscendC {\nint aic=20,aiv=40;uint64_t l1=524288,l0c=131072,ub=196608,l0a=65536,l0b=65536;\nstatic PlatformAscendC* GetInstance(){static PlatformAscendC p;return &p;}\nSocVersion GetSocVersion() const{return SocVersion::ASCEND910B;}\nint GetCoreNumAic(){return aic;}int GetCoreNumAiv(){return aiv;}\nuint64_t GetLibApiWorkSpaceSize(){return 16*1024*1024;}\nvoid GetCoreMemSize(CoreMemType t,uint64_t& n) const{\nn=t==CoreMemType::L1?l1:t==CoreMemType::L0_C?l0c:t==CoreMemType::UB?ub:t==CoreMemType::L0_A?l0a:l0b;}\n};using PlatformAscendCManager=PlatformAscendC;\n}\n')
put('kernel_tiling/kernel_tiling.h','#pragma once\n#include <cstdint>\n'+env['raw']+'namespace AscendC{namespace tiling{using TCubeTiling=::TCubeTiling;}}\n')
code="""#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>
#include "lib/matmul/matmul_tiling.h"
inline int64_t Ceil(int64_t n,int64_t d){return (n+d-1)/d;}
"""+ns['shapes']+ns['host']+r'''
int main(){
 std::cout<<"cores,M,N,K,dual,BM,BN,W,NS,workers,tasks,min_tiles,max_tiles,nonempty,ideal_max_tiles,max_windows,full_A_bytes,L1_need\n";
 auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 unsigned checked=0,under=0,native=0;
 for(int cores:{8,20,24,32})for(int m:{1024,1025,1408,1536,1537,2047})
 for(int n:{1024,1025,1408,1536,1537,2047})for(int k:{1024,1032,1536,1776,2040}){
  hw->aic=cores;hw->aiv=2*cores;
  Shape s{1,m,n,k,2,1,1};auto p=MakePlan(s,cores);auto d=p.schedule;++checked;
  uint64_t maxTiles=0,minTiles=~0ULL,maxWindows=0,totalTiles=0;unsigned nonempty=0;
  for(unsigned worker=0;worker<d.workers;++worker){uint64_t tiles=0,windows=0;
   for(uint64_t task=worker;task<uint64_t(d.mTiles)*d.nSplit;task+=d.workers){
    unsigned ns=task%d.nSplit,begin=ns*d.nTiles/d.nSplit,end=(ns+1)*d.nTiles/d.nSplit;
    tiles+=end-begin;windows+=Ceil(end-begin,d.window);
   }
   totalTiles+=tiles;maxTiles=std::max(maxTiles,tiles);minTiles=std::min(minTiles,tiles);maxWindows=std::max(maxWindows,windows);nonempty+=tiles>0;
  }
  assert(totalTiles==uint64_t(d.mTiles)*d.nTiles);under+=d.workers<unsigned(cores);native+=d.dual==29;
  const auto aBytes=2ULL*d.baseM*Ceil(k,16)*16;
  const auto l1Need=aBytes+4ULL*d.baseN*(d.baseN==256?64:128)+4096;
  std::cout<<cores<<","<<m<<","<<n<<","<<k<<","<<d.dual<<","<<d.baseM<<","<<d.baseN<<","<<d.window<<","<<d.nSplit<<","<<d.workers<<","<<d.mTiles*d.nSplit<<","<<minTiles<<","<<maxTiles<<","<<nonempty<<","<<Ceil(totalTiles,d.workers)<<","<<maxWindows<<","<<aBytes<<","<<l1Need<<"\n";
 }
 std::cerr<<checked<<" public-tiler synthetic TT plans; native="<<native<<" fewer workers than physical cores="<<under<<"; counts are not timings or hidden route proof\n";
}
'''
put('probe.cpp',code)
files=['matmul_tiling.cpp','matmul_tiling_base.cpp','matmul_tiling_algorithm.cpp','math_util.cpp']
for flags in ([],):
 exe=out/('tuning' if flags else 'prod')
 subprocess.run(['clang++','-std=c++17','-O2','-include','map',*flags,'-I'+str(out),'-I'+str(src),str(out/'probe.cpp')]+[str(src/'impl/matmul/tiling'/f) for f in files]+['-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
env['tmp'].cleanup()
