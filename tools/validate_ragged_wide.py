#!/usr/bin/env python3
"""Check ragged wide-N routing and the padded TT/NT arithmetic boundaries."""
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
    for(int m: {65,68,127}) for(int n: {4097,8191,8192})
        for(int k: {128,136,248}) {
            Shape s{1,m,n,k,2,0,1};
            auto p=MakePlan(s,20);const auto& d=p.schedule;
            assert(d.dual==26 && d.baseM==Ceil(m,32)*32 && d.baseN==128);
            assert(d.mTiles==1 && d.nTiles==Ceil(n,128));
            assert(d.workers>0 && d.workers<=20 && p.cubeBlocks==d.workers);
            const uint64_t partial=uint64_t(d.nSplit)*d.baseM*4;
            const uint64_t ring=uint64_t(d.workers)*2*d.baseM*d.baseN*4;
            assert(p.totalBytes>=p.systemBytes+Ceil(partial,512)*512+ring);
        }
    assert(MakePlan({1,64,8192,128,2,0,1},20).schedule.dual==21);
    for(Shape s: {Shape{1,65,8191,248,1,0,1},
                  Shape{1,65,8191,248,2,1,1},
                  Shape{1,65,4095,248,2,0,1},
                  Shape{1,129,8191,248,2,0,1}})
        assert(MakePlan(s,20).schedule.dual!=26);
    auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
    hw->l0b=32768;
    assert(MakePlan({1,65,8191,248,2,0,1},20).schedule.dual!=26);
    std::cout << "ragged wide-N host route and capacity fallback passed\n";
}
'''
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-ragged-wide-') as directory:
    cpp, exe = Path(directory) / 'model.cpp', Path(directory) / 'model'
    cpp.write_text(model)
    subprocess.run([compiler, '-std=c++14', '-O2', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)


def check_math(m, n, k, negative):
    rng = random.Random(m * 100000 + n * 100 + k + negative)
    # Physical layouts of TX1=false and TX2=true.
    a = [[rng.randint(1, 3) if negative else rng.randint(-3, 3)
          for _ in range(k)] for _ in range(m)]
    b = [[rng.randint(-3, -1) if negative else rng.randint(-3, 3)
          for _ in range(k)] for _ in range(n)]
    bm, bk = math.ceil(m / 32) * 32, math.ceil(k / 16) * 16
    maxima = [-math.inf] * m
    for n0 in range(0, n, 128):
        cols = min(128, n - n0)
        # ND2NZ pads both the row and K tail; only valid N columns enter Max.
        a_panel = [[a[row][kk] if row < m and kk < k else 0
                    for kk in range(bk)] for row in range(bm)]
        b_panel = [[b[n0 + col][kk] if col < cols and kk < k else 0
                    for kk in range(bk)] for col in range(128)]
        for row in range(m):
            for col in range(cols):
                value = sum(a_panel[row][kk] * b_panel[col][kk]
                            for kk in range(bk))
                maxima[row] = max(maxima[row], value)
    got = sum(maxima)
    expected = sum(max(sum(a[row][kk] * b[col][kk] for kk in range(k))
                       for col in range(n)) for row in range(m))
    assert got == expected, (m, n, k, negative, got, expected)


cases = 0
for m, n, k in [(17, 129, 40), (33, 255, 72), (65, 129, 40),
                (68, 257, 72), (127, 255, 40)]:
    for negative in (False, True):
        check_math(m, n, k, negative)
        cases += 1
print(f"ragged wide-N numeric/padding model: {cases} cases passed")
