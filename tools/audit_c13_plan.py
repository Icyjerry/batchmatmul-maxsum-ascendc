#!/usr/bin/env python3
"""Execute extracted host plans on the explicit CPU tiler stub; no NPU timing."""
from collections import Counter
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
from validate_c7_manual_frame import span

ROOT = Path(__file__).resolve().parents[1]

def main():
    s = (ROOT / 'kernel.asc').read_text()
    stub = (ROOT / 'tests/cpu/planner_stub.hpp').read_text()
    stub = stub.replace('struct TCubeTiling {', 'struct TCubeTiling {int stepKa=1,stepKb=1;')
    shape = span(s, 'struct Shape {', 'template <AscendC::HardEvent')
    plan = span(s, 'struct Plan {', 'struct Case9PackagePlan ')
    driver = r'''
int main(){
 auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 std::cout<<"cores,n,k,dual,bm,bn,workers,mTiles,nTiles,nSplit,kSplit,earlySum,residentB\n";
 for(int cores:{1,8,20,32})for(int n=64;n<128;++n)for(int k=128;k<256;k+=8){
  hw->aic=cores;hw->aiv=2*cores;
  Shape s{1,8192,n,k,1,0,0};auto p=MakePlan(s,cores);const auto& d=p.schedule;
  assert(d.baseM==128 && d.baseN==Ceil(n,16)*16 && d.mTiles==64 &&
         d.nTiles==1 && d.nSplit==1 && d.kSplit==1 && d.window==1);
  assert(d.workers>0 && d.workers<=unsigned(cores) && p.cubeBlocks==d.workers);
  assert(d.dual==3 || d.dual==14);
  std::cout<<cores<<","<<n<<","<<k<<","<<d.dual<<","<<d.baseM<<","<<d.baseN
   <<","<<d.workers<<","<<d.mTiles<<","<<d.nTiles<<","<<d.nSplit<<","<<d.kSplit
   <<","<<d.earlySum<<","<<bool(d.tree&16)<<"\n";
 }
}
'''
    compiler = shutil.which('clang++') or shutil.which('c++')
    with tempfile.TemporaryDirectory(prefix='bmmms-c13-plan-') as tmp:
        cpp, exe = Path(tmp) / 'audit.cpp', Path(tmp) / 'audit'
        cpp.write_text(stub + shape + plan + driver)
        subprocess.run([compiler, '-std=c++17', '-O2', str(cpp), '-o', str(exe)], check=True)
        rows = subprocess.check_output([str(exe)], text=True).splitlines()[1:]
    print('Source SHA', hashlib.sha256(s.encode()).hexdigest())
    for cores in [1, 8, 20, 32]:
        selected = [list(map(int, row.split(','))) for row in rows if row.split(',')[0] == str(cores)]
        counts = Counter((row[3], row[11], row[12]) for row in selected)
        workers = sorted({row[6] for row in selected})
        print(f'{cores} explicit cores: {len(selected)} plans; (dual,earlySum,residentB)={dict(counts)}; workers={workers}')
        assert len(selected) == 1024
        assert counts == {(3, 1, 1): 32, (14, 1, 0): 992}
    print('4096 actual host executions on CPU tiler stub PASS; not installed CANN9/native plans, route hits or performance.')

if __name__ == '__main__':
    main()
