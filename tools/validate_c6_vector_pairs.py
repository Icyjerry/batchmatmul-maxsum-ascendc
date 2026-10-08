#!/usr/bin/env python3
"""Actual C6 Vector pairs CPU model: not native BF16/real CANN tiling/timing."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_teammate_single_tile import source,span
ROOT=Path(__file__).resolve().parents[1]
def scope(s):
 e=span(s,'// Exact small FT geometry:','// Isolated case6 fast path copied')
 h=span(s,'inline bool C6VectorPairsFits','using CacheKey =')
 c='''    if(C6VectorPairsFits(s,p)) {
        bmmms_c6_vector_pairs<T><<<2*p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,uint32_t(s.b));
        return;
    }
'''
 assert s.count(c)==1 and s.replace(e,'',1).replace(h,'',1).replace(c,'',1)==source('7492776')
 return e,h
def main():
 s=(ROOT/'kernel.asc').read_text();e,h=scope(s)
 print('Three additions restore whole retained C13 source; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 fold=span(s,'__aicore__ inline void SmallRowMaxLaneFold','// One Cube owns one complete small batch.')
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Exact small FT geometry:')
 model=(ROOT/'tests/cpu/c6_vector_pairs.cpp.in').read_text().replace('// INSERT_KERNEL',fold+fence+e)
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 host='#include <cstring>\n'+stub+span(s,'struct Shape {','template <AscendC::HardEvent')+span(s,'struct Plan {','struct Case9PackagePlan ')+h+(ROOT/'tests/cpu/c6_vector_pairs_host.cpp.in').read_text()
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c6-vector-pairs-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'missed control:'+name
   else:r.check_returncode()
  run('host',host);run('host-tuning',host,flags=['-DBMMMS_TUNING']);run('vector',model)
  for name,line in [('input-ready','    SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();'),
   ('partial-ready','    SingleTileDirectFence<true,AscendC::HardEvent::V_MTE3>();'),
   ('barrier','    AscendC::SyncAll<true>();'),('terminal','    AscendC::PipeBarrier<PIPE_ALL>();')]:
   unsafe=model.replace(line,'');assert unsafe!=model;run('no-'+name,unsafe,True)
  unsafe=model.replace('kc<3','kc<2');assert unsafe!=model;run('no-complete-K',unsafe,True)
  unsafe=model.replace('SmallRowMaxLaneFold(dots,row[r],count,n,np);','SmallRowMaxLaneFold(dots,row[r],count,np,np);')
  assert unsafe!=model;run('no-N-mask',unsafe,True)
  print('Six input/store/barrier/terminal/full-K/invalid-N negative controls rejected PASS',flush=True)
 print('Integer FIFO model only; Vector internal pipeline hazards not modeled. Native CANN9/BF16 precision/performance PENDING.')
if __name__=='__main__':main()
