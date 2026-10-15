#!/usr/bin/env python3
"""Extract the exact row-finalizer host guard and exercise resource boundaries."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
a=s.index('inline bool UseSplitTTRowFinalize(');b=s.index('using CacheKey=',a);guard=s[a:b]
main=r'''
int main(){Shape s{1,64,64,8192,1,1,1};Plan p{};p.schedule={1,64,64,8192,64,64,1,1,1,8,1024,1,8,1024,64,8,25,0,0,1};p.cubeBlocks=8;p.finalBlocks=1;p.cube.usedCoreNum=8;
auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=24;hw->aiv=48;hw->ub=196352;hw->l1=524032;p.systemBytes=hw->system;p.totalBytes=p.systemBytes+131072;
void*a=(void*)uintptr_t(0x10000),*b=(void*)uintptr_t(0x20000);auto ok=[&](Shape x,Plan q){return UseSplitTTRowFinalize(x,q,a,b);};assert(ok(s,p));unsigned rejected=0;
for(auto field:{&Shape::b,&Shape::m,&Shape::n,&Shape::k}){auto bad=s;bad.*field+=1;assert(!ok(bad,p));++rejected;}
for(auto field:{&Shape::dtype,&Shape::tx1,&Shape::tx2}){auto bad=s;bad.*field^=1;assert(!ok(bad,p));++rejected;}
for(auto field:{&Schedule::b,&Schedule::m,&Schedule::n,&Schedule::k}){auto bad=p;bad.schedule.*field+=1;assert(!ok(s,bad));++rejected;}
for(auto field:{&Schedule::baseM,&Schedule::baseN,&Schedule::mTiles,&Schedule::nTiles,&Schedule::nSplit,&Schedule::workers,&Schedule::vectorTile,&Schedule::window,&Schedule::kSplit,&Schedule::kChunk,&Schedule::microRows,&Schedule::batchGroup,&Schedule::dual,&Schedule::earlySum,&Schedule::tree,&Schedule::balance}){auto bad=p;bad.schedule.*field+=1;assert(!ok(s,bad));++rejected;}
for(auto field:{&Plan::small,&Plan::micro,&Plan::case12PackedA}){auto bad=p;bad.*field=true;assert(!ok(s,bad));++rejected;}
{auto bad=p;bad.cubeBlocks=7;assert(!ok(s,bad));++rejected;}{auto bad=p;bad.finalBlocks=2;assert(!ok(s,bad));++rejected;}{auto bad=p;bad.cube.usedCoreNum=9;assert(!ok(s,bad));++rejected;}
for(unsigned delta:{1u,2u,4u,8u,16u}){assert(!UseSplitTTRowFinalize(s,p,(void*)(uintptr_t(a)+delta),b));assert(!UseSplitTTRowFinalize(s,p,a,(void*)(uintptr_t(b)+delta)));rejected+=2;}
for(auto item:std::vector<std::pair<uint64_t*,uint64_t>>{{&hw->l1,65536+4096},{&hw->l0a,32768},{&hw->l0b,32768},{&hw->l0,16384},{&hw->ub,16928+1024}}){auto original=*item.first;*item.first=item.second;assert(ok(s,p));--*item.first;assert(!ok(s,p));*item.first=original;assert(ok(s,p));++rejected;}
for(auto field:{&platform_ascendc::PlatformAscendCManager::aic,&platform_ascendc::PlatformAscendCManager::aiv}){auto v=hw->*field;hw->*field=7;assert(!ok(s,p));hw->*field=8;assert(ok(s,p));hw->*field=v;++rejected;}
{auto bad=p;--bad.totalBytes;assert(!ok(s,bad));++rejected;bad=p;bad.totalBytes+=512;assert(!ok(s,bad));++rejected;bad=p;bad.systemBytes=0;assert(!ok(s,bad));++rejected;bad=p;bad.systemBytes+=512;bad.totalBytes+=512;assert(!ok(s,bad));++rejected;}
#ifdef BMMMS_TUNING
for(auto field:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){auto v=Tune();Tune().*field=1;assert(!ok(s,p));Tune()=v;assert(ok(s,p));++rejected;}
#endif
std::cout<<"Actual row-finalizer frame guard: "<<rejected<<" rejected shape/dtype/layout/plan/alignment/core/capacity/workspace/pin cases, exact producer/vector capacities accepted PASS\n";}
'''
code=(R/'tests/cpu/planner_stub.hpp').read_text()+'\nusing GM_ADDR=void*;\n'+types+plans+guard+main
with tempfile.TemporaryDirectory(prefix='bmmms-c15-two-guard-') as tmp:
 d=Path(tmp);(d/'test.cpp').write_text(code)
 for tuning in (False,True):
  subprocess.run(['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(d/'test.cpp'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
