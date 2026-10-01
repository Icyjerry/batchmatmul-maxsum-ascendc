#!/usr/bin/env python3
"""Actual one-barrier finalizer; integer CPU, not Ascend timing/rounding/TPipe."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=(ROOT/'kernel.asc').read_text()
 entry=span(s,'// The first all-AIV barrier','// All N-tile partials are ready')
 host=span(s,'// Reuse UB only after','using CacheKey =')
 call='''        if(FullMTilesBatchFits(s,p))
            bmmms_manual<T,true,true,true,false,false,false,false,true,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);
        else bmmms_manual<T,true,true,true,false,false,false,false,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);
'''
 old='        bmmms_manual<T,true,true,true,false,false,false,false,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);\n'
 body='''        if constexpr(BATCH_FINAL)FinalizeFullMTilesBatch(partial,output,s);
        else FinalizeFullMTiles(partial,output,s,pipe);'''
 assert s.count(call)==1 and s.count(body)==1 and s.count(', bool BATCH_FINAL=false>')==1
 restored=s.replace(entry,'',1).replace(host,'',1).replace(call,old,1)
 restored=restored.replace(', bool BATCH_FINAL=false>','>',1).replace(body,'        FinalizeFullMTiles(partial,output,s,pipe);',1)
 assert restored==source('cf16501'),'outside finalizer/guard/dispatch scope'
 finish=span(s,'    AscendC::SyncAll<true>();\n    if constexpr(TILE_STREAM)', '    } else if(s.earlySum && s.nSplit==1)')+'    }\n'
 merge=span(s,'// Fold disjoint split halves','template<typename T>\n__schedmode__(1) __global__ __mix__(1,2) void bmmms_wide_n_manual_frame')
 model=(ROOT/'tests/cpu/tt_batch_finalize_model.cpp.in').read_text().replace('// INSERT_FINALIZER',merge+entry).replace('// INSERT_BARRIER_CALL',finish)
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plan=span(s,'struct Plan {','// Select only an already complete TF batch')
 h='#include <cstring>\n'+stub+shapes+plan+host+(ROOT/'tests/cpu/tt_batch_finalize_host.cpp.in').read_text()
 print('Exact parent scope: Cube/plan/GM/old consumer/C7/C14 unchanged; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tt-batch-final-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   result=subprocess.run([str(exe)],capture_output=bad,timeout=120)
   if bad:assert result.returncode!=0,'negative control missed: '+name
   else:result.check_returncode()
  run('vector',model)
  for name,old,new in [('first-barrier','    AscendC::SyncAll<true>();',''),
   ('DMA-ready','    Fence<AscendC::HardEvent::MTE2_V>();',''),
   ('output-ready','    Fence<AscendC::HardEvent::V_MTE3>();',''),
   ('terminal-drain','    AscendC::PipeBarrier<PIPE_ALL>();',''),
   ('N-merge','    WideNMergeRows(all,paddedM,s.nSplit);',''),
   ('M-tail','full=s.m/64,tail=s.m%64','full=(s.m+63)/64,tail=0')]:
   unsafe=model.replace(old,new);assert unsafe!=model;run('no-'+name,unsafe,True)
  print('Six actual alias/barrier/DMA/output/completion/N-merge/M-tail negative controls rejected PASS',flush=True)
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CANN9/native precision/latency PENDING. Original consumer/Cube and TPipe internals are not simulated.')
if __name__=='__main__':main()
