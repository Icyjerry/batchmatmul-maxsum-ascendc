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
helpers=src[src.index('// One full-M accumulator:'):src.index('// Consume wide GM windows')]
consumer=src[src.index('// Consume wide GM windows'):src.index('__aicore__ inline void ManualCopyC(')]
consumer_model=(root/'tests/cpu/fullk_window_consumer_model.cpp.in').read_text().replace('// INSERT_CONSUMER',consumer)
model=(root/'tests/cpu/fullm_storage_model.cpp.in').read_text().replace('// INSERT_HELPERS',zero+helpers)
shapes=src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host=src[src.index('struct Plan {'):src.index('using CacheKey =')]
baseline=subprocess.check_output(['git','show','968e957:kernel.asc'],cwd=root,text=True)
parent=baseline[baseline.index('struct Plan {'):baseline.index('using CacheKey =')]
# Vector body and old producer/launch paths outside the full-M helper remain
# byte-identical to the passed wide-window parent.
passed=subprocess.check_output(['git','show','1c2f5b9:kernel.asc'],cwd=root,text=True)
def vector(s):
    a=s.index('void bmmms_manual(');a=s.index('\n#else\n    AscendC::TQue',a);b=s.index('\n#endif\n}',a)
    return s[a:b]
assert vector(src)==vector(passed)
hostmodel=(root/'tests/cpu/planner_stub.hpp').read_text()+shapes+'namespace Parent{'+parent+'}\nnamespace Candidate{'+host+'}\n'+r'''
int main(){unsigned checked=0,selected=0;
 auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{4,8,20,32})for(int m:{1024,1025,1408,1536,2048,4096,8191})for(int n:{1024,1025,1536,2048,4096,8191})
 for(int k:{1024,1032,1536,1544,2048,3072})for(int dt:{1,2})for(int tx1:{0,1})for(int tx2:{0,1}){
  Shape s{1,m,n,k,dt,tx1,tx2};auto a=Parent::MakePlan(s,cores);auto b=Candidate::MakePlan(s,cores);++checked;
  auto x=a.schedule,y=b.schedule;
  if(y.dual==29||y.dual==30){++selected;assert(x.dual==1||x.dual==20||x.dual==6);
   const int buffers=y.dual==30?1:2;y.dual=x.dual;
   uint64_t bm=y.baseM,bn=y.baseN,bk=bn==256?64:128;
   assert(2*bm*Ceil(k,16)*16+4*bn*bk+4096<=hw->l1);
   assert(4*bm*bk<=hw->l0a && 4*bn*bk<=hw->l0b && 4*buffers*bm*bn<=hw->l0);
   assert(y.window<=8 && !y.earlySum);
   assert(uint64_t(y.baseM)*bn*4+20*y.baseM+3*y.vectorTile*4+64+4096<hw->ub);
  }
  assert(a.cubeBlocks==b.cubeBlocks && a.finalBlocks==b.finalBlocks && a.systemBytes==b.systemBytes && a.totalBytes==b.totalBytes);
  assert(std::tie(x.b,x.m,x.n,x.k,x.baseM,x.baseN,x.mTiles,x.nTiles,x.nSplit,x.workers,x.vectorTile,x.window,x.kSplit,x.kChunk,x.microRows,x.batchGroup,x.dual,x.earlySum,x.tree,x.balance)==
         std::tie(y.b,y.m,y.n,y.k,y.baseM,y.baseN,y.mTiles,y.nTiles,y.nSplit,y.workers,y.vectorTile,y.window,y.kSplit,y.kChunk,y.microRows,y.batchGroup,y.dual,y.earlySum,y.tree,y.balance));
 }
 for(auto s:{Shape{1,3072,1536,1536,1,0,1},Shape{1,6144,1536,1536,2,0,0},Shape{1,1536,6144,1536,2,1,0}}){
  auto p=Parent::MakePlan(s,20);auto q=Candidate::MakePlan(s,20);
  assert(q.schedule.dual==29||q.schedule.dual==30);
  std::cout<<"parent dual "<<p.schedule.dual<<" -> "<<q.schedule.dual<<" BM"<<q.schedule.baseM<<" BN"<<q.schedule.baseN<<" W"<<q.schedule.window<<" storage "<<s.tx1<<s.tx2<<"\n";
 }
 assert(selected>16);Shape wide{1,1025,1025,1032,2,1,1};assert(Candidate::MakePlan(wide,20).schedule.dual==29);
 Shape edge{1,1025,1025,1776,2,1,1};assert(Candidate::MakePlan(edge,20).schedule.dual==29);
 edge.k=1784;assert(Candidate::MakePlan(edge,20).schedule.dual!=29);
 Shape hit{1,1536,1536,1536,2,1,1};assert(Candidate::MakePlan(hit,20).schedule.dual==29);
 for(auto member:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){
  auto old=*member;*member=4096;
  try{auto d=Candidate::MakePlan(hit,20).schedule.dual;assert(d!=29&&d!=30);}catch(const std::runtime_error&){}
  *member=old;
 }
 for(Shape s:{Shape{2,1536,1536,1536,2,1,1},Shape{1,513,511,2048,1,1,1},
              Shape{1,1536,1536,8192,2,1,1}}){auto d=Candidate::MakePlan(s,20).schedule.dual;assert(d!=29&&d!=30);}
#ifdef BMMMS_TUNING
 for(auto pin:{&Candidate::Tune().bm,&Candidate::Tune().bn,&Candidate::Tune().window,&Candidate::Tune().ns,
    &Candidate::Tune().ks,&Candidate::Tune().workers,&Candidate::Tune().tree,&Candidate::Tune().dual,&Candidate::Tune().early}){
  Candidate::Tune()=Candidate::TuneConfig{};*pin=1;
  try{auto d=Candidate::MakePlan(hit,20).schedule.dual;assert(d!=29&&d!=30);}catch(const std::invalid_argument&){}
 }
 Candidate::Tune()=Candidate::TuneConfig{};
#endif
 std::cout<<checked<<" actual host-control configurations with permissive fake tiler, "<<selected<<" selected; resource fallbacks/pins and unchanged schedule/workspace PASS\n";
}
'''
compiler=shutil.which('clang++') or shutil.which('c++')
assert compiler
print('CPU model only, all-storage full-M; kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
with tempfile.TemporaryDirectory(prefix='bmmms-manual-fullk-m-') as d:
    for name,code,flags in [('producer',model,[]),('consumer',consumer_model,[]),('host',hostmodel,[]),('host-tuning',hostmodel,['-DBMMMS_TUNING'])]:
        cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name
        cpp.write_text(code)
        subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
print('CANN9 compile, NPU accuracy and latency PENDING.')
