#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
a=s.index('inline bool UseSmallC5Direct(');b=s.index('using CacheKey=',a);guard=s[a:b]
main=r'''
int main(){Shape s{8,16,32,128,1,0,0};Plan p{};p.schedule={8,16,32,128,16,32,1,1,1,8,1024,1,1,128,16,0,19,0,0,1};p.cubeBlocks=8;p.finalBlocks=1;p.systemBytes=16777216;p.totalBytes=p.systemBytes+33280;auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aiv=48;hw->ub=196352;
void*a=(void*)uintptr_t(0x10000),*b=(void*)uintptr_t(0x20000);auto ok=[&](Shape x,Plan q){return UseC5HalfVector(x,q,a,b);};unsigned good=0,reject=0;
for(int dt:{1})for(int t1:{0,1})for(int t2:{0,1}){auto x=s;x.dtype=dt;x.tx1=t1;x.tx2=t2;assert(ok(x,p));++good;}
for(auto field:{&Shape::b,&Shape::m,&Shape::n,&Shape::k}){auto x=s;x.*field+=1;assert(!ok(x,p));++reject;}
for(int dt:{0,2,3}){auto x=s;x.dtype=dt;assert(!ok(x,p));++reject;}

for(unsigned d:{1u,2u,4u,8u,16u}){assert(!UseC5HalfVector(s,p,(void*)(uintptr_t(a)+d),b));assert(!UseC5HalfVector(s,p,a,(void*)(uintptr_t(b)+d)));reject+=2;}
for(auto f:{&Plan::small,&Plan::micro}){auto q=p;q.*f=true;assert(!ok(s,q));++reject;}
{auto q=p;q.cubeBlocks=1;assert(!ok(s,q));++reject;q=p;q.totalBytes=512;assert(!ok(s,q));++reject;}
assert(UseC5HalfVector(s,p,(void*)(uintptr_t(a)+32),b));hw->aiv=0;assert(!ok(s,p));++reject;hw->aiv=8;assert(ok(s,p));hw->ub=160351;assert(!ok(s,p));++reject;hw->ub=160352;assert(ok(s,p));
#ifdef BMMMS_TUNING
for(auto field:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){auto v=Tune();Tune().*field=1;assert(!ok(s,p));Tune()=v;assert(ok(s,p));++reject;}
#endif
for(auto f:{&Schedule::b,&Schedule::m,&Schedule::n,&Schedule::k}){auto q=p;q.schedule.*f+=1;assert(!ok(s,q));++reject;}
for(auto f:{&Schedule::kSplit,&Schedule::kChunk}){auto q=p;q.schedule.*f+=1;assert(!ok(s,q));++reject;}
for(auto f:{&Schedule::baseM,&Schedule::baseN,&Schedule::mTiles,&Schedule::nTiles,&Schedule::nSplit,&Schedule::workers,&Schedule::earlySum,&Schedule::tree}){auto q=p;q.schedule.*f+=1;assert(!ok(s,q));++reject;}
{auto v=hw->aic;hw->aic=7;assert(!ok(s,p));++reject;hw->aic=v;hw->aiv=7;assert(!ok(s,p));++reject;hw->aiv=8;}
{auto q=p;--q.totalBytes;assert(!ok(s,q));++reject;q=p;q.systemBytes=0;assert(!ok(s,q));++reject;}
std::cout<<"Actual C5 half Vector guard accepted "<<good<<" dtype/layout cases; rejected "<<reject<<" shape/alignment/plan/resource/tuning cases PASS\n";}
'''
code=(R/'tests/cpu/planner_stub.hpp').read_text()+'\nusing GM_ADDR=void*;\n'+types+plans+guard+main
with tempfile.TemporaryDirectory(prefix='bmmms-c5-half-guard-') as tmp:
 d=Path(tmp);(d/'test.cpp').write_text(code)
 for tuning in (False,True):
  subprocess.run(['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(d/'test.cpp'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
