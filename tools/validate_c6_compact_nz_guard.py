#!/usr/bin/env python3
"""Exercise extracted host resource/fallback guard; not an SDK tiler model."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
a=s.index('inline bool MakeSmallFullKBatch(');b=s.index('inline bool UseSmallC5Direct(',a);guard=s[a:b]
main=r'''
int main(){Shape s{13,23,73,192,2,0,1};Plan p{};auto&d=p.schedule;
d.b=s.b;d.m=s.m;d.n=s.n;d.k=s.k;d.baseM=32;d.baseN=80;d.mTiles=d.nTiles=d.nSplit=d.kSplit=d.window=d.balance=1;
d.kChunk=192;d.workers=13;d.dual=19;p.cubeBlocks=13;
auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=24;hw->aiv=48;hw->ub=196352;hw->l1=524032;
p.systemBytes=hw->system;p.totalBytes=p.systemBytes+Ceil(13*32*4,512)*512+8ULL*13*32*80;
auto ok=[&](const Shape&x,const Plan&q){return UseSmallC6CompactNZ(x,q);};assert(ok(s,p));unsigned rejects=0;
for(auto field:{&Shape::b,&Shape::m,&Shape::n,&Shape::k}){auto bad=s;bad.*field+=1;assert(!ok(bad,p));++rejects;}
for(auto field:{&Shape::dtype,&Shape::tx1,&Shape::tx2}){auto bad=s;bad.*field^=1;assert(!ok(bad,p));++rejects;}
for(auto field:{&Schedule::baseM,&Schedule::baseN,&Schedule::mTiles,&Schedule::nTiles,&Schedule::nSplit,&Schedule::kSplit,&Schedule::kChunk,&Schedule::workers,&Schedule::dual,&Schedule::earlySum,&Schedule::tree,&Schedule::window,&Schedule::balance}){auto q=p;q.schedule.*field+=1;assert(!ok(s,q));++rejects;}
for(auto field:{&Schedule::b,&Schedule::m,&Schedule::n,&Schedule::k}){auto q=p;q.schedule.*field+=1;assert(!ok(s,q));++rejects;}
for(auto field:{&Plan::small,&Plan::micro,&Plan::case12PackedA}){auto q=p;q.*field=true;assert(!ok(s,q));++rejects;}
{auto q=p;q.cubeBlocks=12;assert(!ok(s,q));++rejects;}{auto q=p;--q.totalBytes;assert(!ok(s,q));++rejects;}
for(auto field:{&platform_ascendc::PlatformAscendCManager::aic,&platform_ascendc::PlatformAscendCManager::aiv}){int v=hw->*field;hw->*field=12;assert(!ok(s,p));hw->*field=v;assert(ok(s,p));++rejects;}
for(auto item:std::vector<std::pair<uint64_t*,uint64_t>>{{&hw->l1,(32+80)*192*2+4096},{&hw->l0a,32*192*2},{&hw->l0b,80*192*2},{&hw->l0,32*80*4},{&hw->ub,32*80*4+32*8+64+1024}}){auto v=*item.first;*item.first=item.second;assert(ok(s,p));--*item.first;assert(!ok(s,p));*item.first=v;assert(ok(s,p));++rejects;}
#ifdef BMMMS_TUNING
for(auto field:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){auto v=Tune();Tune().*field=1;assert(!ok(s,p));Tune()=v;assert(ok(s,p));++rejects;}
#endif
std::cout<<"Actual compact guard: "<<rejects<<" rejected shape/layout/plan/UB/L1/L0/workspace/core/tuning counterexamples PASS\n";}
'''
code=(R/'tests/cpu/planner_stub.hpp').read_text()+'\n'+types+plans+guard+main
with tempfile.TemporaryDirectory(prefix='bmmms-c6-nz-guard-') as tmp:
 d=Path(tmp);(d/'test.cpp').write_text(code)
 for tuning in (False,True):
  subprocess.run(['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(d/'test.cpp'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
