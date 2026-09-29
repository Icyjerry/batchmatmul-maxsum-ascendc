#!/usr/bin/env python3
"""Compile the real host planner with a permissive tiler and inspect TT routing."""
from pathlib import Path
import shutil
import subprocess
import tempfile


root = Path(__file__).resolve().parents[1]
source = (root / 'kernel.asc').read_text()
shapes = source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
host = source[source.index('struct Plan {'):source.index('using CacheKey =')]
model = (root / 'tests/cpu/planner_stub.hpp').read_text() + shapes + host + r'''
int main() {
    auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
    for(Shape s: {Shape{1,1536,1536,1536,2,1,1},
                  Shape{1,1536,3072,3072,1,1,1}}) {
        auto p=MakePlan(s,20);const auto& d=p.schedule;
        std::cerr << s.m << "," << s.n << "," << s.k << " dual=" << d.dual
                  << " bm=" << d.baseM << " bn=" << d.baseN << " ns=" << d.nSplit
                  << " ksplit=" << d.kSplit << "\n";
        assert(d.dual==24 && d.panelK==128 && d.panelGroup==2);
        assert(d.baseM==128 && d.baseN==128 && d.nTiles>=2*d.nSplit);
        assert(d.workers==p.cubeBlocks && p.cubeBlocks<=20);
        const uint64_t parts=uint64_t(s.b)*d.nSplit*d.mTiles*d.baseM*4;
        assert(p.totalBytes>=p.systemBytes+Ceil(parts,512)*512+
            uint64_t(d.workers)*2*d.baseM*d.baseN*4);
    }
    for(Shape s: {Shape{1,1536,1536,1536,2,0,1},
                  Shape{1,513,511,2048,1,1,1},
                  Shape{2,1536,1536,1536,2,1,1},
                  Shape{1,1024,2048,2048,1,1,1}})
        assert(MakePlan(s,20).schedule.dual!=24);
    hw->l0=65536;
    assert(MakePlan({1,1536,1536,1536,2,1,1},20).schedule.dual!=24);
    hw->l0=131072;hw->l0a=32768;
    assert(MakePlan({1,1536,1536,1536,2,1,1},20).schedule.dual!=24);
    std::cout << "TT panel routing and scratch gates passed\n";
}
'''
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-tt-panel-plan-') as directory:
    cpp = Path(directory) / 'model.cpp'
    exe = Path(directory) / 'model'
    cpp.write_text(model)
    subprocess.run([compiler, '-std=c++14', '-O2', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
