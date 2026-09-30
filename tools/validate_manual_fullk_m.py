#!/usr/bin/env python3
"""Execute real full-K M producer in bounded NZ/event/queue CPU model.

MTE2 reads are deferred until queue completion; MTE1/MMAD/Fixpipe remain
synchronous. This is not CANN compilation, hardware event timing, BF16
instruction precision, or performance evidence.
"""
from pathlib import Path
import shutil, subprocess, tempfile, hashlib
root=Path(__file__).resolve().parents[1]
src=(root/'kernel.asc').read_text()
zero=src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
copy=src[src.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>'):src.index('// TT: retain two half-M')]
helpers=src[src.index('// TT: retain two half-M'):src.index('__aicore__ inline void ManualCopyC(')]
model=(root/'tests/cpu/manual_fullk_m_model.cpp.in').read_text().replace('// INSERT_HELPERS',zero+copy+helpers)
shapes=src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host=src[src.index('struct Plan {'):src.index('using CacheKey =')]
baseline=subprocess.check_output(['git','show','968e957:kernel.asc'],cwd=root,text=True)
parent=baseline[baseline.index('struct Plan {'):baseline.index('using CacheKey =')]
# The Vector body is reused without modifications; span changes to the same
# existing 1/2-tile layout. The producer model checks every C/ring coordinate.
def vector_body(s):
    a=s.index('void bmmms_manual(')
    a=s.index('\n#else\n    AscendC::TQue',a)
    b=s.index('\n#endif\n}',a)
    return s[a:b]
assert vector_body(src)==vector_body(baseline)
hostmodel=(root/'tests/cpu/planner_stub.hpp').read_text()+shapes+'namespace Parent{'+parent+'}\nnamespace Candidate{'+host+'}\n'+r'''
int main(){unsigned checked=0,selected=0;
 auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{4,8,20,32})for(int m:{1024,1025,1408,1536,2048})for(int n:{1024,1025,1408,1536,2048})
 for(int k:{1024,1032,1408,1536,1544,2048,3072})for(int dt:{1,2}){
  Shape s{1,m,n,k,dt,1,1};auto a=Parent::MakePlan(s,cores);auto b=Candidate::MakePlan(s,cores);++checked;
  auto x=a.schedule,y=b.schedule;
  if(y.dual==29){++selected;assert(x.dual==1);y.dual=1;
   uint64_t bm=y.baseM/2,bn=y.baseN,bk=bn==256?64:128;
   assert(4*bm*Ceil(k,16)*16+4*bn*bk+4096<=hw->l1);
   assert(4*bm*bk<=hw->l0a && 4*bn*bk<=hw->l0b && 16*bm*bn<=hw->l0);
   assert(y.window<=2 && y.baseN*y.window<=256 && !y.earlySum);
  }
  assert(a.cubeBlocks==b.cubeBlocks && a.finalBlocks==b.finalBlocks && a.systemBytes==b.systemBytes && a.totalBytes==b.totalBytes);
  assert(std::tie(x.b,x.m,x.n,x.k,x.baseM,x.baseN,x.mTiles,x.nTiles,x.nSplit,x.workers,x.vectorTile,x.window,x.kSplit,x.kChunk,x.microRows,x.batchGroup,x.dual,x.earlySum,x.tree,x.balance)==
         std::tie(y.b,y.m,y.n,y.k,y.baseM,y.baseN,y.mTiles,y.nTiles,y.nSplit,y.workers,y.vectorTile,y.window,y.kSplit,y.kChunk,y.microRows,y.batchGroup,y.dual,y.earlySum,y.tree,y.balance));
 }
 assert(selected>0);Shape hit{1,1536,1536,1536,2,1,1};assert(Candidate::MakePlan(hit,20).schedule.dual==29);
 for(auto member:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){
  auto old=*member;*member=4096;
  try{assert(Candidate::MakePlan(hit,20).schedule.dual!=29);}catch(const std::runtime_error&){}
  *member=old;
 }
 for(Shape s:{Shape{2,1536,1536,1536,2,1,1},Shape{1,1536,1536,1536,2,0,1},
              Shape{1,1536,1536,1536,2,1,0},Shape{1,513,511,2048,1,1,1},
              Shape{1,1536,1536,8192,2,1,1}})assert(Candidate::MakePlan(s,20).schedule.dual!=29);
#ifdef BMMMS_TUNING
 for(auto pin:{&Candidate::Tune().bm,&Candidate::Tune().bn,&Candidate::Tune().window,&Candidate::Tune().ns,
    &Candidate::Tune().ks,&Candidate::Tune().workers,&Candidate::Tune().tree,&Candidate::Tune().dual,&Candidate::Tune().early}){
  Candidate::Tune()=Candidate::TuneConfig{};*pin=1;
  try{assert(Candidate::MakePlan(hit,20).schedule.dual!=29);}catch(const std::invalid_argument&){}
 }
 Candidate::Tune()=Candidate::TuneConfig{};
#endif
 std::cout<<checked<<" actual host-control configurations with permissive fake tiler, "<<selected<<" selected; resource fallbacks/pins and unchanged schedule/workspace PASS\n";
}
'''
compiler=shutil.which('clang++') or shutil.which('c++')
assert compiler
print('CPU model only; kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
with tempfile.TemporaryDirectory(prefix='bmmms-manual-fullk-m-') as d:
    for name,code,flags in [('producer',model,[]),('host',hostmodel,[]),('host-tuning',hostmodel,['-DBMMMS_TUNING'])]:
        cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name
        cpp.write_text(code)
        subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
print('CANN9 compile, NPU accuracy and latency PENDING.')
