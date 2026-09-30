#!/usr/bin/env python3
"""Execute extracted streaming producer/control and ND consumer in CPU mocks."""
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
src = (root / 'kernel.asc').read_text()
shapes = src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host = src[src.index('struct Plan {'):src.index('using CacheKey =')]
stream_dual = 27 if 'if(p.schedule.dual==27)' in src else 26
stub = (root / 'tests/cpu/planner_stub.hpp').read_text()
stub = stub.replace('uint32_t m=0,n=0; static bool rejectFirst;',
    'uint32_t m=0,n=0; static bool rejectFirst,rejectStream; static unsigned tilerCalls;')
stub = stub.replace('if(rejectFirst){', 'if(rejectStream && ++tilerCalls>1)return -1;\n        if(rejectFirst){')
stub += '\nbool matmul_tiling::MatmulApiTiling::rejectStream=false;\nunsigned matmul_tiling::MatmulApiTiling::tilerCalls=0;\n'
checks = r'''
int main() {
    unsigned routes=0;
    for(int m: {1024,1025,1537,2047})for(int n: {1024,1025,2049,4095})
    for(int k: {1024,1032,1536})for(int dtype: {1,2}) {
        auto p=MakePlan({1,m,n,k,dtype,1,1},20);auto d=p.schedule;
        assert(d.dual==26 && d.window==1 && d.kSplit==1);++routes;
        assert(d.baseM==p.cube.baseM && d.baseN==p.cube.baseN);
        assert(p.cube.usedCoreNum==d.workers && d.nTiles>=2*d.nSplit);
        auto partial=uint64_t(d.nSplit)*d.mTiles*d.baseM*4;
        assert(p.totalBytes==p.systemBytes+Ceil(partial,512)*512+
            uint64_t(d.workers)*2*d.baseM*d.baseN*4);
    }
    for(Shape s: {Shape{2,1025,1537,1032,2,1,1},Shape{1,1025,1537,1032,2,0,1},
        Shape{1,1025,1537,1032,2,1,0},Shape{1,65,127,8192,1,1,1}})
        assert(MakePlan(s,20).schedule.dual!=26);
    assert(MakePlan({1,1025,1537,1032,2,1,1},20).schedule.dual==26);
    matmul_tiling::MatmulApiTiling::rejectStream=true;
    assert(MakePlan({1,1025,1537,1032,2,1,1},20).schedule.dual==1);
    matmul_tiling::MatmulApiTiling::rejectStream=false;
#ifdef BMMMS_TUNING
    for(auto pin: {&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,
                  &Tune().workers,&Tune().tree,&Tune().dual,&Tune().early}) {
        Tune()=TuneConfig{};*pin=1;
        assert(MakePlan({1,1025,1537,1032,2,1,1},20).schedule.dual!=26);
    }
#endif
    std::cout << "cube stream host routing/workspace: " << routes << " configurations\n";
}
'''
host_model = stub + shapes + host + checks.replace('26', str(stream_dual))

start = src.index('    for(int64_t task=worker;', src.index('void bmmms_dual('))
producer = src[start:src.index('        } else {\n        for(uint32_t nt=begin;', start)]
producer = producer + '        }\n    }\n'
consumer_start = src.index('            for(uint32_t p=0;rows && p<tiles;', src.index('void bmmms_dual('))
consumer = src[consumer_start:src.index('            AscendC::CrossCoreSetFlag', consumer_start)]
assert 'sourceWidth=STREAM?cols:width' in consumer

model = (root / 'tests/cpu/cube_stream_model.cpp.in').read_text()
model = model.replace('// INSERT_SHAPES', shapes).replace('// INSERT_PRODUCER', producer).replace('// INSERT_CONSUMER', consumer)
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-cube-stream-') as tmp:
    for name, code, flags in [('host', host_model, []), ('host-pins', host_model, ['-DBMMMS_TUNING']),
                              ('producer-consumer-nd', model, ['-DTEST_NZ=0']),
                              ('producer-consumer-nz', model, ['-DTEST_NZ=1'])]:
        cpp, exe = Path(tmp) / (name + '.cpp'), Path(tmp) / name
        cpp.write_text(code)
        subprocess.run([compiler, '-std=c++17', '-O2', *flags, str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
