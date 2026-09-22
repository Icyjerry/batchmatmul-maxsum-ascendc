#!/usr/bin/env python3
"""Print real planner decisions using a permissive CPU tiler, never NPU timings."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'kernel.asc').read_text()
code=(r/'tests/cpu/planner_stub.hpp').read_text()+s[s.index('struct Shape {'):s.index('template <AscendC::HardEvent')]+s[s.index('struct Plan {'):s.index('using CacheKey =')]+r'''
void Dump(Shape s){auto p=MakePlan(s,20);auto d=p.schedule;
std::cout<<s.b<<","<<s.m<<","<<s.n<<","<<s.k<<" tx"<<s.tx1<<s.tx2<<" family="<<d.dual<<" tile="<<d.baseM<<"x"<<d.baseN<<" window="<<d.window<<" ns="<<d.nSplit<<" blocks="<<p.cubeBlocks<<" panel="<<d.panelK<<" l1="<<d.panelL1K<<" resident="<<d.panelResident<<"\n";}
int main(){
for(Shape s: {Shape{1,64,8192,128,2,0,1},Shape{1,1536,1536,1536,1,1,1},Shape{16,128,256,128,1,1,0},Shape{16,128,256,128,1,0,0},Shape{1,513,511,2048,1,0,1}})Dump(s);
#ifdef BMMMS_TUNING
Tune().bm=32;Tune().bn=64;Tune().ns=2;Tune().window=1;
std::cout<<"explicit bm32/bn64/ns2/window1: ";Dump({1,64,8192,128,2,0,1});
#endif
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'a.cpp').write_text(code)
 for mode in (0,2,3):
  subprocess.run(['clang++','-std=c++14','-O2','-DBMMMS_TUNING','-DBMMMS_ADAPTIVE_SPLITK=1','-DBMMMS_BALANCED_NSPLIT=1',f'-DBMMMS_CUBE_PANEL={mode}','-DBMMMS_L1_K_PANELS=1',str(p/'a.cpp'),'-o',str(p/'a')],check=True)
  print('CPU permissive tiler only, panel mode',mode,flush=True);subprocess.run([str(p/'a')],check=True)
