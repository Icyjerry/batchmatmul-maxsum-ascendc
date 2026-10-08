#!/usr/bin/env python3
"""C10 supplied dimensions under all dtype/layouts; CPU host control only.

No metadata inference from timing; historical BF16/FF and FP16/TT conflict stays.
"""
from pathlib import Path
import hashlib,re,shutil,subprocess,tempfile
from validate_c7_manual_frame import span
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=(ROOT/'kernel.asc').read_text()
 headers='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in
  ['C7KernelShape','WideNKernelShape','TTFrameShape','C13ResidentFrame'])
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 h=stub+span(s,'struct Shape {','template <AscendC::HardEvent')+headers+span(s,'struct Plan {','using CacheKey =')
 h+='''
int main(){
 std::cout<<"cores,dtype,tx1,tx2,dual,bm,bn,kchunk,nt,mt,ns,ks,workers,window,tree,tt_frame,parts_bytes,plan_ring_bytes\\n";
 for(int cores:{1,8,20,32})for(int dt:{1,2})for(int x:{0,1})for(int y:{0,1}){
  auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=cores;hw->aiv=2*cores;
  Shape s{1,4096,1280,1152,dt,x,y};auto p=MakePlan(s,cores);auto d=p.schedule;auto tt=MakeTTManualFrame(s,p);
  uint64_t parts=Ceil(d.nSplit*d.mTiles*d.baseM*4,512)*512;
  std::cout<<cores<<","<<dt<<","<<x<<","<<y<<","<<d.dual<<","<<d.baseM<<","<<d.baseN<<","<<d.kChunk
   <<","<<d.nTiles<<","<<d.mTiles<<","<<d.nSplit<<","<<d.kSplit<<","<<d.workers<<","<<d.window<<","<<d.tree
   <<","<<tt.workers<<","<<parts<<","<<(p.totalBytes-p.systemBytes-parts)<<"\\n";
 }
}
'''
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c10-audit-') as t:
  cpp,exe=Path(t)/'audit.cpp',Path(t)/'audit';cpp.write_text(h)
  subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
  print(subprocess.check_output([str(exe)],text=True),end='')
if __name__=='__main__':main()
