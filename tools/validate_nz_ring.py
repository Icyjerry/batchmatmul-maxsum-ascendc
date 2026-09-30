#!/usr/bin/env python3
"""Model the dual NZ ring addresses and check its host routing."""
from pathlib import Path
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
    for (Shape s : {Shape{1,1536,1536,1536,2,1,1}}) {
        auto p=MakePlan(s,20);
        assert(p.schedule.dual==1 && p.schedule.kSplit==1);
        assert((p.schedule.tree&32)!=0);
        assert(p.totalBytes>=p.systemBytes+
               uint64_t(p.schedule.workers)*2*p.schedule.baseM*
               p.schedule.baseN*p.schedule.window*4);
    }
    for (Shape s : {Shape{1,1536,1536,1536,2,0,1},
                    Shape{1,1536,1536,1536,2,1,0},
                    Shape{2,1536,1536,1536,2,1,1}})
        assert((MakePlan(s,20).schedule.tree&32)==0);
    std::cout << "NZ dual host route and ring capacity passed\n";
}
'''
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-nz-ring-') as directory:
    cpp, exe = Path(directory) / 'model.cpp', Path(directory) / 'model'
    cpp.write_text(model)
    subprocess.run([compiler, '-std=c++14', '-O2', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)

callback = source[source.index('template<uint32_t BASE_N>\n__aicore__ inline void CompactNZCopyOut('):
                  source.index('template <typename T, bool TX1, bool TX2, bool NZ = false,')]
callback_model = r'''
#include <cassert>
#include <cstdint>
#include <vector>
#include <iostream>
#define __aicore__
#define __gm__
#define __DAV_CUBE__
namespace AscendC {
struct DataCopyOutParams {uint16_t burstLen,cBurstNum;int curN;};
struct FixpipeParamsV220 {uint32_t nSize=0,mSize=0,srcStride=0,dstStride=0;};
constexpr int CFG_NZ=0;
template<typename T> struct LocalTensor {
    T* data;
    template<typename U> LocalTensor<U> ReinterpretCast() const {
        return {reinterpret_cast<U*>(data)};
    }
};
template<typename T> struct GlobalTensor {
    T* data;void SetGlobalBuffer(T* p){data=p;}
};
float* mockEnd;
template<typename D,typename S,int C> void Fixpipe(GlobalTensor<D> dst,
    LocalTensor<S> src,FixpipeParamsV220 fp) {
    for(uint32_t g=0;g<fp.nSize/16;++g) {
        assert(dst.data+g*fp.dstStride*8+fp.mSize*16<=mockEnd);
        for(uint32_t i=0;i<fp.mSize*16;++i)
            dst.data[g*fp.dstStride*8+i]=src.data[g*fp.srcStride*16+i];
    }
}
}
''' + callback + r'''
int main() {
    for(int rows: {1,15,16,31,32,63,64,65,127,128})
    for(int bn: {64,128,256}) for(int tiles: {1,2,4}) {
        const int mp=(rows+15)/16*16;
        std::vector<float> ring(128*bn*tiles,-999);
        AscendC::mockEnd=ring.data()+ring.size();
        for(int p=0;p<tiles;++p) {
            std::vector<float> cube(mp*bn,-777);
            for(int g=0;g<bn/16;++g) for(int r=0;r<rows;++r) for(int lane=0;lane<16;++lane)
                cube[g*mp*16+r*16+lane]=p*100000+g*1000+r*16+lane;
            AscendC::DataCopyOutParams cp{uint16_t(rows*2),uint16_t(bn/16),p};
            if(bn==64) CompactNZCopyOut<64>(ring.data(),{reinterpret_cast<int8_t*>(cube.data())},&cp,0,0);
            if(bn==128) CompactNZCopyOut<128>(ring.data(),{reinterpret_cast<int8_t*>(cube.data())},&cp,0,0);
            if(bn==256) CompactNZCopyOut<256>(ring.data(),{reinterpret_cast<int8_t*>(cube.data())},&cp,0,0);
        }
        for(int p=0;p<tiles;++p) for(int g=0;g<bn/16;++g)
        for(int r=0;r<rows;++r) for(int lane=0;lane<16;++lane)
            assert(ring[p*bn*mp+g*mp*16+r*16+lane]==p*100000+g*1000+r*16+lane);
    }
    std::cout << "extracted NZ output callback: 90 tile-window/unit cases passed\n";
}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-nz-callback-') as directory:
    cpp, exe = Path(directory) / 'callback.cpp', Path(directory) / 'callback'
    cpp.write_text(callback_model)
    subprocess.run([compiler, '-std=c++14', '-O2', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)


def check_tile(base_m, base_n, full_rows, total_cols, window, negative):
    rng = random.Random(base_m*100000 + base_n*1000 + full_rows*100 +
                        total_cols*10 + window*2 + negative)
    row_pad = (full_rows + 15) // 16 * 16
    groups = (total_cols + 15) // 16
    slot = [1e8] * (row_pad * groups * 16)
    values = [[rng.uniform(-10, -1 if negative else 10)
               for _ in range(total_cols)] for _ in range(full_rows)]
    for row in range(full_rows):
        for col in range(total_cols):
            slot[(col // 16) * row_pad * 16 + row * 16 + col % 16] = values[row][col]
    for sub in (0, 1):
        row_start = sub * (base_m // 2)
        rows = max(0, min(base_m // 2, full_rows - row_start))
        for p in range(window):
            col_start = p * base_n
            cols = max(0, min(base_n, total_cols - col_start))
            if not rows or not cols:
                continue
            copied = []
            src_start = (col_start // 16) * row_pad * 16 + row_start * 16
            for group in range((cols + 15) // 16):
                block = src_start + group * row_pad * 16
                copied.extend(slot[block:block + rows * 16])
            stride = rows * 16
            got = [max(copied[group * stride + row * 16 + lane]
                       for group in range((cols + 15) // 16)
                       for lane in range(min(16, cols - group * 16)))
                   for row in range(rows)]
            expected = [max(values[row_start + row][col_start:col_start + cols])
                        for row in range(rows)]
            assert got == expected, (base_m, base_n, full_rows, total_cols, window, sub, p)


count = 0
for base_m in (64, 128):
    for base_n in (64, 128, 256):
        for full_rows in (1, 15, 16, 31, base_m // 2, base_m // 2 + 1, base_m - 1, base_m):
            for window in (1, 2):
                for total_cols in (1, 15, 16, base_n - 1, base_n,
                                   min(window * base_n, base_n + 1), window * base_n):
                    for negative in (False, True):
                        check_tile(base_m, base_n, full_rows, total_cols, window, negative)
                        count += 1
print(f'NZ ring row/N-tail address and all-negative model: {count} cases passed')
