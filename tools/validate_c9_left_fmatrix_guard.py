#!/usr/bin/env python3
"""Exercise actual C9 FMatrix guard; do not infer a hidden plan from this stub."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
a=s.index('inline bool UseC9LeftFmatrix(');b=s.index('using CacheKey=',a);guard=s[a:b]
main=r'''
int main(){Shape s{1,2048,1536,1280,1,0,1};Plan p{};p.schedule={1,2048,1536,1280,128,128,16,12,5,20,1024,3,1,256,2048,8,36,0,0,1};p.cubeBlocks=20;p.finalBlocks=1;p.cube.usedCoreNum=20;p.cube.baseK=128;
auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=24;hw->aiv=48;hw->ub=196352;hw->l1=524032;p.systemBytes=16777216;
auto total=[](Plan&q){auto&d=q.schedule;q.totalBytes=q.systemBytes+((4ULL*d.nSplit*16*128+511)/512*512)+8ULL*d.workers*128*128*d.window;};total(p);
auto ok=[&](Shape x,Plan q){return UseC9LeftFmatrix(x,q);};assert(ok(s,p));unsigned rejected=0;
for(auto f:{&Shape::b,&Shape::m,&Shape::n,&Shape::k}){auto t=s;t.*f+=1;assert(!ok(t,p));++rejected;}
for(auto f:{&Shape::dtype,&Shape::tx1,&Shape::tx2}){auto t=s;t.*f^=1;assert(!ok(t,p));++rejected;}
for(auto f:{&Schedule::b,&Schedule::m,&Schedule::n,&Schedule::k}){auto q=p;q.schedule.*f+=1;assert(!ok(s,q));++rejected;}
for(auto f:{&Schedule::baseM,&Schedule::baseN,&Schedule::mTiles,&Schedule::nTiles,&Schedule::kSplit,&Schedule::dual,&Schedule::earlySum,&Schedule::tree}){auto q=p;q.schedule.*f+=1;assert(!ok(s,q));++rejected;}
for(auto f:{&Plan::small,&Plan::micro,&Plan::case12PackedA}){auto q=p;q.*f=true;assert(!ok(s,q));++rejected;}
for(unsigned ns:{0u,13u}){auto q=p;q.schedule.nSplit=ns;total(q);assert(!ok(s,q));++rejected;}
for(unsigned w:{0u,5u}){auto q=p;q.schedule.window=w;total(q);assert(!ok(s,q));++rejected;}
for(unsigned k:{128u,257u}){auto q=p;q.schedule.kChunk=k;assert(!ok(s,q));++rejected;}
for(auto f:{&Plan::cubeBlocks,&Plan::finalBlocks}){auto q=p;q.*f+=1;assert(!ok(s,q));++rejected;}
{auto q=p;++q.cube.usedCoreNum;assert(!ok(s,q));++rejected;q=p;q.cube.baseK=64;assert(!ok(s,q));++rejected;q=p;q.schedule.workers=0;assert(!ok(s,q));++rejected;q=p;++q.totalBytes;assert(!ok(s,q));++rejected;q=p;q.systemBytes=0;total(q);assert(!ok(s,q));++rejected;}
for(auto item:std::vector<std::pair<uint64_t*,uint64_t>>{{&hw->l1,327680+4*128*256+4096},{&hw->l0a,65536},{&hw->l0b,65536},{&hw->l0,131072},{&hw->ub,131072}}){auto v=*item.first;*item.first=item.second;assert(ok(s,p));--*item.first;assert(!ok(s,p));*item.first=v;++rejected;}
for(unsigned w:{8u,20u,24u,32u}){auto q=p;q.schedule.workers=w;q.cubeBlocks=w;q.cube.usedCoreNum=w;hw->aic=w;hw->aiv=2*w;total(q);assert(ok(s,q));--hw->aic;assert(!ok(s,q));++hw->aic;--hw->aiv;assert(!ok(s,q));rejected+=2;}hw->aic=24;hw->aiv=48;
#ifdef BMMMS_TUNING
for(auto f:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){auto t=Tune();Tune().*f=1;assert(!ok(s,p));Tune()=t;assert(ok(s,p));++rejected;}
#endif
std::cout<<"Actual C9 FMatrix guard: "<<rejected<<" negative controls,8/20/24/32 budgets and exact capacity boundaries PASS\n";}
'''
code=(R/'tests/cpu/planner_stub.hpp').read_text()+'\nusing GM_ADDR=void*;\n'+types+plans+guard+main
with tempfile.TemporaryDirectory(prefix='bmmms-c9-left-guard-') as tmp:
 d=Path(tmp);(d/'test.cpp').write_text(code)
 for tuning in (False,True):
  subprocess.run(['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(d/'test.cpp'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
