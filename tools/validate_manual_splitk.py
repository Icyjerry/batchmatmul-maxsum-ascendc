#!/usr/bin/env python3
"""Check the long-K manual split routing and independent TT arithmetic oracle."""
from pathlib import Path
import math
import random
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
    for(int n: {64,96,127}) for(int m: {64,65}) {
        Shape s{1,m,n,8192,1,1,1};
        auto p=MakePlan(s,20);const auto& d=p.schedule;
        assert(d.dual==25 && d.kSplit==8 && d.kChunk==1024);
        assert(d.baseM==Ceil(m,16)*16 && d.baseN==Ceil(n,16)*16);
        assert(d.workers==8 && p.cubeBlocks==8);
        uint64_t required=p.systemBytes+Ceil(uint64_t(8)*d.baseM*d.baseN*4,512)*512;
        assert(p.totalBytes>=required);
    }
    for(Shape s: {Shape{1,64,127,8192,2,1,1},
                  Shape{1,64,127,8192,1,1,0},
                  Shape{2,64,127,8192,1,1,1},
                  Shape{1,64,129,8192,1,1,1},
                  Shape{1,64,127,4104,1,1,1}})
        assert(MakePlan(s,20).schedule.dual!=25);
    hw->l0a=16384;
    assert(MakePlan({1,64,127,8192,1,1,1},20).schedule.dual!=25);
    std::cout << "manual split-K host route and resource fallback passed\n";
}
'''
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-manual-split-') as directory:
    cpp, exe = Path(directory) / 'model.cpp', Path(directory) / 'model'
    cpp.write_text(model)
    subprocess.run([compiler, '-std=c++14', '-O2', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)


def check_math(m, n, negative, workers):
    rng = random.Random(100000 * m + 100 * n + 10 * negative + workers)
    k, splits, panel = 128, 8, 16
    x1 = [[rng.randint(1, 3) if negative else rng.randint(-3, 3)
           for _ in range(m)] for _ in range(k)]  # physical TT [K,M]
    x2 = [[rng.randint(-3, -1) if negative else rng.randint(-3, 3)
           for _ in range(k)] for _ in range(n)]  # physical TT [N,K]
    bm, bn = math.ceil(m / 16) * 16, math.ceil(n / 16) * 16
    partial = [None] * (splits * bm * bn)
    seen = set()
    for worker in range(workers):
        for split in range(worker, splits, workers):
            assert split not in seen
            seen.add(split)
            start, end = split * (k // splits), (split + 1) * (k // splits)
            for row in range(bm):
                for col in range(bn):
                    value = 0
                    if row < m and col < n:
                        for k0 in range(start, end, panel):
                            value += sum(x1[kk][row] * x2[col][kk]
                                         for kk in range(k0, k0 + panel))
                    offset = split * bm * bn + row * bn + col
                    assert partial[offset] is None
                    partial[offset] = value
    assert len(seen) == splits and all(value is not None for value in partial)
    got = sum(max(sum(partial[split * bm * bn + row * bn + col]
                      for split in range(splits)) for col in range(n)) for row in range(m))
    expected = sum(max(sum(x1[kk][row] * x2[col][kk] for kk in range(k))
                       for col in range(n)) for row in range(m))
    assert got == expected, (m, n, negative, workers, got, expected)


cases = 0
for m, n in [(16, 16), (17, 31), (31, 17), (64, 64),
             (65, 96), (64, 127), (127, 64), (127, 127)]:
    for negative in (False, True):
        for workers in (1, 4, 8):
            check_math(m, n, negative, workers)
            cases += 1
print(f"manual TT split-K numeric/padding/task model: {cases} cases passed")
