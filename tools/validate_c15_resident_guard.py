#!/usr/bin/env python3
"""Extract actual admission guard; synthetic host frame, not native MakePlan."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
MAIN=r'''
int main(){
 Shape s{1,64,64,8192,1,1,1};Plan p{};auto&d=p.schedule;
 d.b=s.b;d.m=s.m;d.n=s.n;d.k=s.k;d.baseM=64;d.baseN=64;d.mTiles=d.nTiles=d.nSplit=1;d.kSplit=8;d.window=1;
 d.kChunk=1024;d.workers=8;d.dual=25;p.cubeBlocks=8;
 auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=24;hw->aiv=48;hw->ub=196352;hw->l1=524032;
 p.systemBytes=hw->system;p.totalBytes=p.systemBytes+8ULL*64*64*4;
 void*a=reinterpret_cast<void*>(uintptr_t(0x10000)),*b=reinterpret_cast<void*>(uintptr_t(0x20000));
 auto accepts=[&](const Shape&x,const Plan&q){return UseSplitTTResidentInput(x,q,a,b);};assert(accepts(s,p));unsigned rejects=0;
 for(auto field:{&Shape::b,&Shape::m,&Shape::n,&Shape::k}){Shape bad=s;bad.*field+=1;assert(!accepts(bad,p));++rejects;}
 for(auto field:{&Shape::dtype,&Shape::tx1,&Shape::tx2}){Shape bad=s;bad.*field^=1;assert(!accepts(bad,p));++rejects;}
 for(auto field:{&Schedule::baseM,&Schedule::baseN,&Schedule::window,&Schedule::mTiles,&Schedule::nTiles,&Schedule::nSplit,&Schedule::kSplit,&Schedule::kChunk,&Schedule::workers,&Schedule::dual,&Schedule::earlySum,&Schedule::tree}){
  Plan q=p;q.schedule.*field+=1;assert(!accepts(s,q));++rejects;}
 for(auto field:{&Schedule::b,&Schedule::m,&Schedule::n,&Schedule::k}){Plan q=p;q.schedule.*field+=1;assert(!accepts(s,q));++rejects;}
 for(unsigned delta:{1u,2u,4u,8u,16u}){
  assert(!UseSplitTTResidentInput(s,p,reinterpret_cast<void*>(uintptr_t(0x10000+delta)),b));
  assert(!UseSplitTTResidentInput(s,p,a,reinterpret_cast<void*>(uintptr_t(0x20000+delta))));rejects+=2;}
 for(auto field:{&Plan::small,&Plan::micro,&Plan::case12PackedA}){Plan q=p;q.*field=true;assert(!accepts(s,q));++rejects;}
 {Plan q=p;q.cubeBlocks=7;assert(!accepts(s,q));++rejects;}
 {Plan q=p;--q.totalBytes;assert(!accepts(s,q));++rejects;}
 {Plan q=p;q.systemBytes=0;assert(!accepts(s,q));q=p;q.systemBytes+=512;q.totalBytes+=512;assert(!accepts(s,q));rejects+=2;}
 for(auto field:{&platform_ascendc::PlatformAscendCManager::aic,&platform_ascendc::PlatformAscendCManager::aiv}){
  int save=hw->*field;hw->*field=7;assert(!accepts(s,p));hw->*field=save;assert(accepts(s,p));++rejects;}
 for(auto item:std::vector<std::pair<uint64_t*,uint64_t>>{{&hw->l1,2*(64+64)*1024+4096},{&hw->l0a,4*64*128},{&hw->l0b,4*64*128},{&hw->l0,4*64*64},{&hw->ub,131904+1024}}){
  uint64_t save=*item.first;*item.first=item.second;assert(accepts(s,p));--*item.first;assert(!accepts(s,p));*item.first=save;assert(accepts(s,p));++rejects;}
#ifdef BMMMS_TUNING
 for(auto field:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){
  TuneConfig save=Tune();Tune().*field=1;assert(!accepts(s,p));Tune()=save;assert(accepts(s,p));++rejects;}
#endif
 std::cout<<"Actual admission guard accepted exact synthetic frame; rejected "<<rejects<<" shape/layout/dtype/plan/alignment/capacity/workspace/tuning counterexamples\n";
}
'''
def main():
 s=(ROOT/'kernel.asc').read_text();a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
 a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
 a=s.index('inline bool UseSplitTTResidentInput(');b=s.index('using CacheKey=',a);guard=s[a:b]
 code=(ROOT/'tests/cpu/planner_stub.hpp').read_text()+'\nusing GM_ADDR=void*;\n'+types+plans+guard+MAIN
 with tempfile.TemporaryDirectory(prefix='bmmms-c15-guard-') as temp:
  p=Path(temp);(p/'guard.cpp').write_text(code)
  for tuning in [False,True]:
   cmd=['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(p/'guard.cpp'),'-o',str(p/'guard')]
   subprocess.run(cmd,check=True);subprocess.run([str(p/'guard')],check=True)
 print('Actual normalPlan was independently read; this test checks guard control flow and synthetic boundary fallbacks, not hardware precision or speed.')
if __name__=='__main__':main()
