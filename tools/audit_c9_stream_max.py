#!/usr/bin/env python3
"""Actual host/source arithmetic assessment; no kernel or NPU timing change."""
from pathlib import Path
import re,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=(ROOT/'kernel.asc').read_text();assert s==source('a2e6763')
 e=span(s,'template <typename T, bool PAD_MN>\n__schedmode__(1) __global__ __mix__(1, 2) void bmmms_case9_packages','// Isolated case12 packed-B');
 v=e[e.index('#else\n    AscendC::TQue'):]
 assert 'for(uint32_t col=0;col<cols;col+=64)' in v
 assert 'AscendC::WholeReduceMax(row,c[col]' in v
 assert 'AscendC::Max(maxima,maxima,row' in v
 # The C6 queue-removal idea is already implemented in the selected direct path.
 c6=span(s,'// Isolated case6 fast path','template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>')
 assert 'SingleTileDirectContext<DIRECT_BATCH> context;' in c6
 assert 'if constexpr(DIRECT_BATCH)' in c6 and 'AscendC::LocalTensor<T>(AscendC::TPosition::A1' in c6
 assert 'mm.m=mp;mm.n=np;mm.k=kp;mm.cmatrixInitVal=true;' in c6
 headers='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in ['C7KernelShape','WideNKernelShape','TTFrameShape','C13ResidentFrame'])
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 code=stub+span(s,'struct Shape {','template <AscendC::HardEvent')+headers+span(s,'struct Plan {','using CacheKey =')+r'''
int main(){auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{8,20,24,32}){
  hw->aic=cores;hw->aiv=2*cores;Shape s{1,2048,1536,1280,1,0,1};auto p=MakePlan(s,cores);auto d=p.schedule;auto pack=MakeCase9PackagePlan(s,p);
  assert(d.dual==20&&pack.safe&&pack.resident&&pack.bK>d.kChunk);
  uint64_t oldHorizontal=0,newHorizontal=0,lanewise=0,maxLaneBytes=0,oldUb=0;
  // Enumerate the exact selected producer/AIV loop geometry, both companions.
  for(uint32_t w=0;w<d.workers;++w)for(uint32_t sub=0;sub<2;++sub)
  for(int64_t task=w;task<s.b*d.mTiles*d.nSplit;task+=d.workers){
   uint32_t ns=task%d.nSplit,mt=(task/d.nSplit)%d.mTiles;
   int64_t rem=s.m-mt*d.baseM-sub*d.baseM/2;uint32_t rows=rem<=0?0:std::min<int64_t>(rem,d.baseM/2);
   if(!rows)continue;++newHorizontal;
   uint32_t begin=ns*d.nTiles/d.nSplit,end=(ns+1)*d.nTiles/d.nSplit;
   for(uint32_t nt=begin;nt<end;nt+=d.window){uint32_t tiles=std::min(d.window,end-nt);
    for(uint32_t tile=0;tile<tiles;++tile){uint32_t cols=std::min<int64_t>(s.n-(nt+tile)*d.baseN,d.baseN);
     oldHorizontal+=Ceil(cols,64);lanewise+=Ceil(cols,64);
    }
   }
   maxLaneBytes=std::max<uint64_t>(maxLaneBytes,rows*64*4);
  }
  oldUb=2ULL*(d.baseM/2)*d.baseN*4+3ULL*d.baseM*4+32;
  assert(oldUb+maxLaneBytes+4096<=hw->ub&&oldHorizontal>newHorizontal);
  std::cout<<"cores="<<cores<<" BM/BN/BK="<<d.baseM<<"/"<<d.baseN<<"/"<<d.kChunk<<" Nsplit="<<d.nSplit<<" workers="<<d.workers<<" Bpackage="<<pack.bK
   <<" old/new horizontal APIs="<<oldHorizontal<<"/"<<newHorizontal<<" existing row-Max/new lane-Max APIs="<<lanewise<<"/"<<lanewise
   <<" old UB bytes="<<oldUb<<" extra lane bytes="<<maxLaneBytes<<" PASS\n";
 }
}
'''
 with tempfile.TemporaryDirectory(prefix='bmmms-c9-stream-audit-') as tmp:
  cpp,exe=Path(tmp)/'audit.cpp',Path(tmp)/'audit';cpp.write_text(code)
  subprocess.run([shutil.which('clang++') or 'c++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True)
 print('Actual current C6 source already no TPipe in DIRECT_BATCH; reject duplicate queue/frame hypothesis.')
 print('C9 selected host/source arithmetic only. Extra Max lanes process more elements; native route/latency/precision unknown. No kernel candidate/submission.')
if __name__=='__main__':main()
