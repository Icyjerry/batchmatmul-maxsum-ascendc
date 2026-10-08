#!/usr/bin/env python3
"""Exact C11 routing over unchanged TT entry: CPU integer/synthetic event models.

Not native FP16, real CANN tiling, performance or whole-hardware co-simulation.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_tt_manual_frame import cube,vector
from validate_teammate_single_tile import source,span
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 h=span(s,'// Exact supplied C11 boundary:','using CacheKey =')
 c='''    const auto c11=MakeC11TTFrame(s,p);
    if(c11.workers) {
        bmmms_tt_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,c11);
        return;
    }
'''
 assert s.count(c)==1 and s.replace(h,'',1).replace(c,'',1)==source('7492776')
 return span(s,'// Same TT tile/package stream','// All N-tile partials are ready'),h

def main():
 s=(ROOT/'kernel.asc').read_text();entry,h=scope(s)
 print('Two host additions restore entire retained C13 source; device entry byte-identical; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 header=entry[:entry.index('template<typename T>')]
 host='#include <cstring>\n'+stub+span(s,'struct Shape {','template <AscendC::HardEvent')+span(s,'struct Plan {','struct Case9PackagePlan ')+header+h+(ROOT/'tests/cpu/c11_exact_frame_host.cpp.in').read_text()
 # Keep actual producer and oracle. Full K/N packages on a reduced-M proxy;
 # full supplied M/N is covered by actual host and threaded consumer below.
 c=cube(s,entry).split('int main(){')[0]+'''int main(){unsigned count=0;
 for(bool neg:{false,true})for(bool eager:{false,true}){
  AscendC::eagerFix=eager;Run(129,513,136,64,256,256,20,neg);++count;
 }
 AscendC::eagerFix=false;Run(128,2048,2048,64,256,256,20,false);++count;
 AscendC::eagerFix=true;Run(192,512,2048,64,256,256,8,true);++count;
 std::cout<<count<<" actual TT Cube groups: full K2048/BN256/BK64/PK256 physical layouts, delayed operands, A M-boundary reuse, N8 stream, idle workers, ring/event/input guards PASS\\n";
}
'''
 v=vector(s,entry).split('int main(){')[0].replace('Shape q{M,N,136,','Shape q{M,N,2048,').replace('TTFrameShape s{M,N,136,','TTFrameShape s{M,N,2048,')+'''int main(){unsigned count=0;
 for(uint32_t workers:{1u,8u,20u,32u,64u})for(bool neg:{false,true})for(uint32_t mode=0;mode<3;++mode){
  Run(1536,2048,64,256,workers,neg,mode);++count;
  Run(129,513,64,256,workers,neg,mode);++count;
 }
 std::cout<<count<<" threaded actual TT AIV groups: full supplied M/N, immutable N8 partials, C/row reuse, three engine priorities, padded/idle rows, barrier, valid MaxN/SumM/exact4B y PASS\\n";
}
'''
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c11-frame-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=240)
   if bad:assert r.returncode!=0,'missed control:'+name
   else:r.check_returncode()
  run('host',host);run('host-tuning',host,flags=['-DBMMMS_TUNING'])
  run('cube',c)
  for name,line in [('B1-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),
   ('A1-reader','            AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(2);'),
   ('L0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(bs);'),
   ('C-reader','            if(k0==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);'),
   ('A-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2);'),
   ('M-fix','        AscendC::WaitFlag<AscendC::HardEvent::M_FIX>(cs);')]:
   unsafe=c.replace(line,'');assert unsafe!=c;run('no-'+name,unsafe,True)
  print('Six Cube readiness/last-reader/full-K handoff negative controls rejected PASS',flush=True)
  run('vector',v)
  for name,line in [('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);'),
   ('row-reader','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(slot);'),
   ('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);'),
   ('partial-ready','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(slot);'),
   ('barrier','    AscendC::SyncAll<true>();'),
   ('final-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();'),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();')]:
   unsafe=v.replace(line,'');assert unsafe!=v;run('no-'+name,unsafe,True)
  print('Seven queued Vector readiness/store/barrier/completion controls rejected PASS',flush=True)
 print('Native CANN9/FP16 precision/latency PENDING. Cube reduced-M full-K proxy; full M/N consumer with synthetic producers.')
if __name__=='__main__':main()
