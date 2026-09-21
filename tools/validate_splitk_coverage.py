#!/usr/bin/env python3
"""Host-only coverage of real classifiers and explicit live UB allocation sites."""
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def function(source, name):
    start = source.index('void ' + name + '(')
    end = source.index('\n}\n', start) + 3
    return source[start:end]


def main():
    raw = (ROOT / 'kernel.asc').read_bytes()
    source = raw.decode()
    baseline = subprocess.check_output(['git', 'show', 'user-best-20260921:kernel.asc'], cwd=ROOT).decode()
    current = source[source.index('inline uint64_t SplitKNDLiveBytes('):source.index('inline Plan MakePlan(')]
    original = baseline[baseline.index('enum ForcedKind'):baseline.index('inline Plan MakePlan(')]
    shape = source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
    final = function(source, 'FinalizeSplitKND')
    allocations = re.findall(r'pipe.InitBuffer\([^;]+;', final)
    zero = re.findall(r'pipe.InitBuffer\(zerosBuf,[^;]+;', function(source, 'bmmms_dual_split'))
    assert len(allocations) == 6 and len(zero) == 1
    assert 'std::max(vectorBytes, SplitKNDLiveBytes(bm, bn, s.n))' in source
    code = '''#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
inline int64_t Ceil(int64_t v,int64_t d){return (v+d-1)/d;}
''' + shape + '\nnamespace old {\n' + original + '\n}\nnamespace now {\n' + current + '''
}
struct BudgetPipe {
    uint64_t bytes=0;
    void InitBuffer(int,int size){bytes+=(uint64_t(size)+31)/32*32;}
    void InitBuffer(int,int depth,int size){bytes+=depth*((uint64_t(size)+31)/32*32);}
};
uint64_t Actual(Schedule s) {
    BudgetPipe pipe;
    int iq=0,oq=0,accumBuf=0,tmpBuf=0,groupBuf=0,lanesBuf=0,zerosBuf=0;
    const uint32_t elements=s.baseM*s.baseN;
    const uint32_t groups=(static_cast<uint32_t>(s.n)+63)/64;
''' + '\n'.join(zero + allocations) + '''
    return pipe.bytes;
}
int main() {
    uint64_t checked=0,unsafe=0;
    for(uint64_t ub:{128ULL*1024,192ULL*1024,256ULL*1024})
    for(int m=16;m<=128;++m) for(int n=1;n<=256;++n) {
        Shape x{1,m,n,8192,1,0,0};
        Schedule s{}; s.baseM=Ceil(m,16)*16; s.baseN=Ceil(n,16)*16;s.n=n;
        auto actual=Actual(s);
        assert(now::SplitKNDLiveBytes(s.baseM,s.baseN,n)==actual);
        auto before=old::ClassifyCase(x,ub);
        auto corrected=now::ClassifyCase(x,ub);
        if(before.ks>1 && actual>=ub) {++unsafe; assert(corrected.ks==0);}
        if(corrected.ks>1) assert(actual<ub);
        ++checked;
    }
    Schedule bad{}; bad.baseM=112;bad.baseN=192;bad.n=192;
    assert(Actual(bad)==217120);
    Shape x{1,112,192,8192,1,0,0};
    assert(old::ClassifyCase(x,192*1024).ks==4 && now::ClassifyCase(x,192*1024).ks==0);
    std::cout<<"UB/classifier: "<<checked<<" boundary configurations; "<<unsafe
             <<" formerly accepted over-budget selections rejected. (112,192): live=217120 bytes PASS\\n";
}
'''
    print('CPU host/allocation model only; actual CANN tiling and NPU correctness PENDING.', flush=True)
    print('kernel SHA256:', hashlib.sha256(raw).hexdigest(), flush=True)
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler
    with tempfile.TemporaryDirectory(prefix='bmmms-coverage-') as tmp:
        cpp = Path(tmp) / 'model.cpp'; exe = Path(tmp) / 'model'
        cpp.write_text(code)
        subprocess.run([compiler, '-std=c++14', '-O2', str(cpp), '-o', str(exe)], check=True, timeout=60)
        subprocess.run([str(exe)], check=True, timeout=60)


if __name__ == '__main__':
    main()
