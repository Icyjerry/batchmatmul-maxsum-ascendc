#!/usr/bin/env python3
"""Execute contiguous producer and host control with bounded CPU models.

MTE2 is deferred. MTE1/MMAD/Fixpipe are synchronous, not NPU hardware timing.
"""
from pathlib import Path
import shutil, subprocess, tempfile, hashlib
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'kernel.asc').read_text()
parent_src=subprocess.check_output(['git','show','a05035e:kernel.asc'],cwd=ROOT,text=True)
zero=src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
helpers=src[src.index('// One full-M accumulator:'):src.index('// All N-tile partials are ready')]
def vector_body(s):
 a=s.index('void bmmms_manual(');a=s.index('\n#else\n    AscendC::TQue',a)
 return s[a:s.index('\n#endif\n}',a)]
v=vector_body(src).replace('    const auto range=ManualFullMTasks(s,worker,TILE_STREAM);\n    for(int64_t task=range.begin;task<range.end;task+=range.step) {',
 '    for(int64_t task=worker;task<tasks;task+=s.workers) {')
v=v.replace('    if constexpr(TILE_STREAM) {\n        FinalizeFullMTiles(partial,output,s,pipe);\n    } else if(s.earlySum && s.nSplit==1) {',
 '    if(s.earlySum && s.nSplit==1) {')
assert v==vector_body(parent_src), 'vector changes outside task order/finalizer dispatch'
legacy_model=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().replace('// INSERT_HELPERS',zero+helpers)
model=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
model=model.replace('// INSERT_HELPERS',zero+helpers)
model+=r'''
void Run(Schedule s,bool neg){
 negativeInput=neg;s.window=1;s.mTiles=(s.m+s.baseM-1)/s.baseM;s.nTiles=(s.n+s.baseN-1)/s.baseN;s.nSplit=s.nTiles;
 std::vector<int16_t> a(s.b*s.m*s.k),b(s.b*s.n*s.k);
 for(int64_t z=0;z<s.b;++z)for(int64_t m=0;m<s.m;++m)for(int64_t k=0;k<s.k;++k)a[z*s.m*s.k+k*s.m+m]=A(z,m,k);
 for(int64_t z=0;z<s.b;++z)for(int64_t k=0;k<s.k;++k)for(int64_t n=0;n<s.n;++n)b[z*s.n*s.k+n*s.k+k]=B(z,k,n);
 const auto oldA=a,oldB=b;std::map<int64_t,int> seen;uint64_t sumA=0,sumB=0,sumMM=0,sumTasks=0;
 std::vector<float> final(s.b*s.m,-std::numeric_limits<float>::infinity());
 unsigned minTiles=~0u,maxTiles=0;
 for(uint32_t worker=0;worker<s.workers;++worker){
  st=State{};st.s=s;st.tx1=st.tx2=true;uint32_t seq=0;uint64_t expectedA=0,expectedCopies=0,expectedALoads=0;int64_t lastM=-1;
  const int64_t total=int64_t(s.b)*s.mTiles*s.nTiles;
  // Independent integer partition oracle, not the extracted helper.
  int64_t first=total*worker/s.workers,end=total*(worker+1)/s.workers;
  minTiles=std::min(minTiles,unsigned(end-first));maxTiles=std::max(maxTiles,unsigned(end-first));
  auto range=ManualFullMTasks(s,worker,true);assert(range.begin==first&&range.end==end&&range.step==1);
  for(int64_t task=first;task<end;++task,++seq){
   assert(++seen[task]==1);int64_t mt=(task/s.nTiles)%s.mTiles,z=task/(s.nTiles*s.mTiles),nt=task%s.nTiles;
   uint32_t rows=std::min<int64_t>(s.baseM,s.m-mt*s.baseM),cols=std::min<int64_t>(s.baseN,s.n-nt*s.baseN);
   if(lastM!=task/s.nTiles){expectedA+=uint64_t(rows)*s.k;++expectedCopies;lastM=task/s.nTiles;}
   st.expected.push_back({z,mt*s.baseM,nt*s.baseN,rows,cols,uint32_t(nt),size_t((seq&1)*s.baseM*s.baseN)});
  }
  for(int64_t t=first;t<end;){
   ++expectedALoads;t+=(t+1<end&&t%s.nTiles+1<s.nTiles)?2:1;
  }
  expectedALoads*=(s.k+(s.baseN==256?64:128)-1)/(s.baseN==256?64:128);
  std::vector<float> ring(2*s.baseM*s.baseN+16,1e30f);AscendC::TPipe pipe;
  RunManualFullMCube<int16_t,true>(pipe,{&a,0,true},{&b,0,false},{&ring},s,worker);
  assert(AscendC::dma.empty()&&st.fixes==unsigned(end-first));
  assert(st.aCopies==expectedCopies&&st.aDeques==expectedCopies&&st.aReads==expectedA);
  assert(st.aLoads==expectedALoads&&st.bLoads==st.mmads&&st.bCopies==st.mmads);
  assert(!st.cross[0]&&!st.cross[1]);for(auto e:st.events)assert(e.second==0);
  for(size_t i=2*s.baseM*s.baseN;i<ring.size();++i)assert(ring[i]==1e30f);
  for(auto x:st.maxima){auto z=std::get<0>(x.first),m=std::get<1>(x.first);auto nt=std::get<2>(x.first);
   float gold=-std::numeric_limits<float>::infinity();
   for(int64_t n=int64_t(nt)*s.baseN;n<std::min<int64_t>(s.n,int64_t(nt+1)*s.baseN);++n){
    float v=0;for(int64_t k=0;k<s.k;++k)v+=float(A(z,m,k))*float(B(z,k,n));gold=std::max(gold,v);
   }
   assert(x.second==gold);final[z*s.m+m]=std::max(final[z*s.m+m],x.second);
  }
  sumA+=st.aReads;sumB+=st.bReads;sumMM+=st.mmads;sumTasks+=st.fixes;
 }
 assert(a==oldA&&b==oldB&&seen.size()==uint64_t(s.b)*s.mTiles*s.nTiles&&maxTiles-minTiles<=1);
 assert(sumB==uint64_t(s.b)*s.mTiles*s.n*s.k);
 const uint64_t bk=s.baseN==256?64:128;
 assert(sumMM==uint64_t(s.b)*s.mTiles*s.nTiles*((s.k+bk-1)/bk));
 assert(sumTasks==uint64_t(s.b)*s.mTiles*s.nTiles);
 assert(sumA<=uint64_t(s.b)*s.m*s.k*s.nTiles);
 for(int64_t z=0;z<s.b;++z){float sum=0,gold=0;
  for(int64_t m=0;m<s.m;++m){float mx=-std::numeric_limits<float>::infinity();
   for(int64_t n=0;n<s.n;++n){float v=0;for(int64_t k=0;k<s.k;++k)v+=float(A(z,m,k))*float(B(z,k,n));mx=std::max(mx,v);}
   assert(final[z*s.m+m]==mx);if(neg)assert(mx<0);sum+=final[z*s.m+m];gold+=mx;
  }assert(sum==gold);
 }
}
int main(){unsigned count=0;
 for(uint32_t bm:{32u,64u,128u})for(uint32_t tail:{1u,bm/2,bm-1,bm})
 for(uint32_t n:{33u,65u,129u})for(uint32_t k:{40u,136u})for(uint32_t workers:{1u,3u,8u})for(bool neg:{false,true}){
  Run({2,2*bm+tail,n,k,bm,32,0,0,0,workers,0,0},neg);++count;
 }
 for(auto s:std::vector<Schedule>{{1,129,257,1032,128,128,0,0,0,3,0,0},
  {1,193,1297,1544,64,128,0,0,0,20,0,0},{1,129,513,1032,64,256,0,0,0,8,0,0},
  {1,257,129,2040,64,128,0,0,0,20,0,0}})for(bool neg:{false,true}){Run(s,neg);++count;}
 std::cout<<count<<" extracted contiguous Cube executions: balanced unique full tile cover, delayed NZ input, cached A release/refresh, paired/unpaired A2 reuse, both C slots, full-K C/padding/ring/event counts, paired batches, negative Max then Sum PASS\n";
}
'''
# Execute MMAD when its ordered M-pipe flag is awaited, not at issue time.
# The callback reads live A2/B2/C storage, exposing early operand reuse.
delayed_model=model.replace('namespace AscendC {',
 'std::deque<std::function<void()>> mac;\nnamespace AscendC {',1)
delayed_model=delayed_model.replace(
 'template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}',
 'template<HardEvent E>void SetFlag(int i){auto f=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};if(E==HardEvent::M_MTE1)mac.push_back(f);else f();}')
delayed_model=delayed_model.replace(
 '    assert(st.events[std::make_pair(int(E),i)]--==1);',
 '    if(E==HardEvent::M_MTE1)while(st.events[std::make_pair(int(E),i)]==0){assert(!mac.empty());auto f=mac.front();mac.pop_front();f();}\n    assert(st.events[std::make_pair(int(E),i)]--==1);')
a=delayed_model.index('template<class T>void Mmad(')
b=delayed_model.index('struct FixpipeParamsV220',a)
mm=delayed_model[a:b]
mm=mm.replace('    for(uint32_t m=0;m<p.m;++m)', '    mac.push_back([=]{\n    for(uint32_t m=0;m<p.m;++m)',1)
mm=mm.rsplit('}\n',1)[0]+'    });\n}\n'
delayed_model=delayed_model[:a]+mm+delayed_model[b:]
delayed_model=delayed_model.replace('template<AscendC::HardEvent E>void Fence(){}',
 'template<AscendC::HardEvent E>void Fence(){if(E==AscendC::HardEvent::M_FIX)while(!mac.empty()){auto f=mac.front();mac.pop_front();f();}}')
delayed_model=delayed_model.replace('assert(AscendC::dma.empty()&&st.fixes', 'assert(mac.empty());assert(AscendC::dma.empty()&&st.fixes')
shapes=src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host=src[src.index('struct Plan {'):src.index('using CacheKey =')]
parent=parent_src[parent_src.index('struct Plan {'):parent_src.index('using CacheKey =')]
hostmain=r'''
int main(){unsigned checked=0,selected=0,halfM=0;
 auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{8,20,24,32})for(int m:{1024,1025,1408,1536,1537,2048})for(int n:{1024,1025,1408,1536,1537,2048})
 for(int k:{1024,1032,1536,1776,2040,2048})for(int dtype:{1,2})for(int layout=0;layout<4;++layout){
  hw->aic=cores;hw->aiv=2*cores;Shape s{1,m,n,k,dtype,layout/2,layout%2};
  auto a=Parent::MakePlan(s,cores);auto b=Candidate::MakePlan(s,cores);++checked;
  auto x=a.schedule,y=b.schedule;
  if(y.dual==33){++selected;assert(dtype==2&&s.tx1&&s.tx2&&(x.dual==1||x.dual==29));
   assert(y.window==1&&y.nSplit==y.nTiles&&y.workers==unsigned(cores));halfM+=y.baseM<x.baseM;
   uint64_t bm=y.baseM,bn=y.baseN,bk=bn==256?64:128,kp=Ceil(k,16)*16,chunks=Ceil(m,bm/2);
   assert(2*bm*kp+4*bn*bk+4096<=hw->l1&&4*bm*bk<=hw->l0a&&4*bn*bk<=hw->l0b&&8*bm*bn<=hw->l0);
   assert(4*bm*bn+20*bm+8*bm+64+chunks*32+Ceil(chunks,8)*32+4096<hw->ub);
   assert(b.cubeBlocks==y.workers&&b.cube.usedCoreNum==y.workers&&b.systemBytes==a.systemBytes);
   assert(b.totalBytes==b.systemBytes+Ceil(4ULL*y.mTiles*bm*y.nSplit,512)*512+8ULL*y.workers*bm*bn);
   y.dual=x.dual;y.baseM=x.baseM;y.mTiles=x.mTiles;y.nSplit=x.nSplit;y.window=x.window;y.workers=x.workers;
  }else assert(a.totalBytes==b.totalBytes&&a.cubeBlocks==b.cubeBlocks);
  assert(!std::memcmp(&x,&y,sizeof(x)));
 }
 assert(selected>0&&halfM>0);Shape hit{1,1536,1536,1536,2,1,1};
 for(auto member:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){
  auto old=*member;*member=4096;try{assert(Candidate::MakePlan(hit,20).schedule.dual!=33);}catch(const std::runtime_error&){}*member=old;
 }
#ifdef BMMMS_TUNING
 for(auto pin:{&Candidate::Tune().bm,&Candidate::Tune().bn,&Candidate::Tune().window,&Candidate::Tune().ns,
  &Candidate::Tune().ks,&Candidate::Tune().workers,&Candidate::Tune().tree,&Candidate::Tune().dual,&Candidate::Tune().early}){
  Candidate::Tune()=Candidate::TuneConfig{};*pin=1;try{assert(Candidate::MakePlan(hit,20).schedule.dual!=33);}catch(const std::exception&){}
 }Candidate::Tune()=Candidate::TuneConfig{};
#endif
 std::cout<<checked<<" host cases, "<<selected<<" contiguous selected, "<<halfM<<" half-M for actual L1 capacity: workspace/grid/budget/pins/other layouts PASS\n";
}
'''
hostmodel='#include <cstring>\n'+(ROOT/'tests/cpu/planner_stub.hpp').read_text()+shapes+'namespace Parent{'+parent+'}\nnamespace Candidate{'+host+'}\n'+hostmain

def main():
 compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
 print('Kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
 with tempfile.TemporaryDirectory(prefix='bmmms-tt-contig-') as d:
  for name,code,flags in [('cube',model,[]),('delayed-mmad',delayed_model,[]),('legacy-producer',legacy_model,[]),('host',hostmodel,[]),('host-tuning',hostmodel,['-DBMMMS_TUNING'])]:
   cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
 print('CANN9/NPU accuracy/latency PENDING; not a timing model.')
if __name__=='__main__':main()
