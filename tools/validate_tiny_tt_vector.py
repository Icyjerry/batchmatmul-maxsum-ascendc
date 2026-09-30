#!/usr/bin/env python3
"""Execute extracted tiny TT source and host routing; CPU evidence only."""
from pathlib import Path
import math
import random
import shutil
import struct
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'kernel.asc').read_text()
shapes = source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
start = source.index('template<typename T>\n__schedmode__(1) __global__ __vector__ void bmmms_tiny_tt_vector(')
end = source.index('\n// Small GEMMs', start)
kernel = source[start:end]
model = (root / 'tests/cpu/tiny_tt_model.cpp.in').read_text().replace('// @SHAPES@', shapes).replace('// @KERNEL@', kernel)
host = source[source.index('struct Plan {'):source.index('using CacheKey =')]
host_model = (root / 'tests/cpu/planner_stub.hpp').read_text() + shapes + host + r'''
int main(){
    auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();unsigned selected=0;
    for(int cores:{4,8,20,32})for(int b:{4,5,7})for(int m:{8,11,15})
    for(int n:{16,23,31})for(int k:{128,136,192,248}){
        Shape s{b,m,n,k,2,1,1};auto p=MakePlan(s,cores);
        if(b<=cores){assert(p.schedule.dual==28);assert(p.finalBlocks==b && p.cubeBlocks==0);++selected;}
        else assert(p.schedule.dual!=28);
    }
    hw->ub=32*1024;
    assert(MakePlan({5,15,31,248,2,1,1},20).schedule.dual==19);
    hw->ub=192*1024;
    for(Shape s:{Shape{5,15,31,248,2,1,0},Shape{5,15,31,248,2,0,1},
                 Shape{5,15,31,248,2,0,0},Shape{5,15,31,248,1,1,1},
                 Shape{5,15,31,264,2,1,1},Shape{5,17,31,248,2,1,1},
                 Shape{8,17,64,192,2,0,1}})assert(MakePlan(s,20).schedule.dual!=28);
#ifdef BMMMS_TUNING
    for(int pin:{19,1}){Tune().dual=pin;assert(MakePlan({5,15,31,248,2,1,1},20).schedule.dual!=28);}
    Tune().dual=-1;
#endif
    std::cout<<"Host production/TUNING: "<<selected<<" selected, resource/layout/geometry fallbacks PASS\n";
}
'''
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-tiny-tt-') as directory:
    for name, code, flags in [('producer', model, []), ('host', host_model, []),
                              ('host_tuning', host_model, ['-DBMMMS_TUNING'])]:
        cpp, exe = Path(directory) / f'{name}.cpp', Path(directory) / name
        cpp.write_text(code)
        subprocess.run([compiler, '-std=c++14', '-O2', *flags, str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


def f32(x):
    return struct.unpack('f', struct.pack('f', x))[0]


def quantize(x, dtype):
    if dtype == 'fp16':
        return struct.unpack('e', struct.pack('e', x))[0]
    bits = struct.unpack('I', struct.pack('f', x))[0]
    bits = (bits + 0x7fff + ((bits >> 16) & 1)) & 0xffff0000
    return struct.unpack('f', struct.pack('I', bits))[0]


def tree_sum(values):
    values = values + [0.0] * ((1 << (len(values) - 1).bit_length()) - len(values))
    while len(values) > 1:
        values = [f32(values[i] + values[i + 1]) for i in range(0, len(values), 2)]
    return values[0]


cases = 0
worst_abs = worst_rel = 0.0
for dtype in ('fp16', 'bf16'):
    for m, n, k in ((8, 16, 128), (11, 23, 136), (15, 31, 184), (15, 31, 248), (16, 32, 256)):
        for pattern in ('mixed', 'negative', 'cancellation'):
            rng = random.Random(991 + m + n + k)
            def row(sign):
                v = [(rng.random() if pattern == 'negative' else rng.uniform(-1, 1)) * sign for _ in range(k)]
                norm = math.sqrt(sum(x*x for x in v))
                return [quantize(x / norm, dtype) for x in v]
            a = [row(1) for _ in range(m)]
            b = [row(-1 if pattern == 'negative' else 1) for _ in range(n)]
            if pattern == 'cancellation':
                # The same maxima cancel across pairs of query rows.
                b = [b[0]] * n
                a = [a[0] if i % 2 == 0 else [-x for x in a[0]] for i in range(m)]
            got, expected = [], []
            for ar in a:
                dots, oracle = [], []
                for br in b:
                    prod = [f32(x*y) for x, y in zip(ar, br)]
                    lanes = prod[:64]
                    for start in range(64, k, 64):
                        lanes = [f32(x + (prod[start+i] if start+i < k else 0.0)) for i, x in enumerate(lanes)]
                    dots.append(tree_sum(lanes))
                    oracle.append(sum(float(x)*y for x, y in zip(ar, br)))
                got += [max(dots), 0.0]
                expected.append(max(oracle))
            actual, golden = tree_sum(got), f32(sum(expected))
            absolute = abs(actual - golden)
            relative = absolute / max(abs(golden), 1e-30)
            assert absolute < 1e-4 and (relative < 1e-4 or abs(golden) < 1e-4), (dtype, pattern, actual, golden)
            worst_abs = max(worst_abs, absolute)
            if abs(golden) >= 1e-4:
                worst_rel = max(worst_rel, relative)
            cases += 1
print(f'Independent quantized FP64 oracle: {cases} cases PASS, max abs={worst_abs:.3g}, max nonzero rel={worst_rel:.3g}')
print('CANN compile, asynchronous events, hardware precision and performance: PENDING')
