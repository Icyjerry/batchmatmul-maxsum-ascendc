#!/usr/bin/env python3
"""Run real host planning branches with an explicitly permissive fake tiler."""
import hashlib
import csv
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    raw = (ROOT / 'kernel.asc').read_bytes()
    source = raw.decode()
    shapes = source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
    host = source[source.index('struct Plan {'):source.index('using CacheKey =')]
    code = (ROOT / 'tests/cpu/planner_stub.hpp').read_text() + shapes + host + r'''
uint64_t panelPlans=0,residentPlans=0;
void Check(Shape s,int cores){
    Plan p=MakePlan(s,cores);const auto& d=p.schedule;
    assert(p.finalBlocks>0 && p.finalBlocks<=40);
    if(d.dual==15 || d.dual==16){assert(p.totalBytes==0);return;}
    if(s.m==1 && s.n==1 || p.small)return;
    if(p.micro){assert(d.workers>0);return;}
    if(d.dual==9 || d.dual==11){
        assert(d.workers>0 && d.workers<=uint32_t(2*cores));
        assert(p.totalBytes>=s.b*Ceil(std::max(s.m,s.n),8)*8*4);return;
    }
    assert(p.cubeBlocks>0 && p.cubeBlocks<=uint32_t(cores));
    assert(d.workers==p.cubeBlocks*(d.dual?1:2));
    assert(d.baseM%16==0 && d.baseN%16==0);
    assert(d.mTiles==Ceil(s.m,d.baseM) && d.nTiles==Ceil(s.n,d.baseN));
    assert(d.nSplit>0 && d.nSplit<=d.nTiles && d.window>0);
    if(d.panelK){
        ++panelPlans;residentPlans+=d.panelResident;
        auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
        assert(d.dual==14 && d.kSplit==1 && d.window==1 && d.panelGroup==std::min(2,BMMMS_CUBE_PANEL));
        assert(d.panelK>=64 && d.panelK%16==0 && d.nTiles>=2*d.nSplit);
        assert(4ULL*d.baseM*d.panelK<=hw->l0a && 4ULL*d.baseN*d.panelK<=hw->l0b);
        assert(4ULL*(d.baseM+d.baseN)*d.panelK+1024<=hw->l1);
        assert(8ULL*d.baseM*d.baseN<=hw->l0);
        assert(d.panelResident==(BMMMS_CUBE_PANEL>=3 && 2ULL*d.baseM*Ceil(s.k,16)*16+4ULL*d.baseN*d.panelK+1024<=hw->l1));
    }
    uint64_t partial;
    if(d.kSplit>1){
        assert(d.baseM>=s.m && d.baseN>=s.n);
        assert(d.kSplit==Ceil(s.k,d.kChunk) && d.kChunk%32==0);
        assert(SplitKNDLiveBytes(d.baseM,d.baseN,s.n)<192*1024);
        partial=s.b*d.kSplit*d.baseM*d.baseN*4;
    }else partial=s.b*d.nSplit*d.mTiles*d.baseM*4;
    bool manual=d.dual==3||d.dual==4||d.dual==6||d.dual==7||d.dual==14;
    assert((p.systemBytes==0)==manual);
    uint64_t required=p.systemBytes+Ceil(partial,512)*512;
    if(d.kSplit==1)required+=uint64_t(d.workers)*d.baseM*d.baseN*d.window*4*(d.dual?2:1);
    assert(p.totalBytes>=required);
    if(manual)assert(p.totalBytes<16*1024*1024);
}
int main(){
    int count=0;
    for(int b:{1,2,8,64})for(int m:{1,2,8,16,32,64,65,68,80,112,128,129,513,1024,1536,8192})
    for(int n:{1,2,8,16,32,64,96,127,128,192,256,513,1024,1536,4096,8192})
    for(int k:{32,40,64,128,248,512,1032,2048,4104,8192})
    for(int layout=0;layout<4;++layout)for(int dtype:{1,2}){
        if(std::max(int64_t(b)*m*k,int64_t(b)*n*k)>(1LL<<26))continue;
        Shape s{b,m,n,k,dtype,layout/2,layout%2};
        Check(s,count%3==0?1:count%3==1?8:20);++count;
    }
    // INSERT_UNIFIED_CASES
    // Reject first candidate: generic plans must continue the host fallback loop.
    matmul_tiling::MatmulApiTiling::rejectFirst=true;
    Check({1,1536,1536,1536,1,1,1},20);
    assert(!matmul_tiling::MatmulApiTiling::rejectFirst);
    auto* platform=platform_ascendc::PlatformAscendCManager::GetInstance();
    bool needsSystem=MakePlan({1,1536,1536,1536,1,1,1},20).systemBytes!=0;
    platform->system=0;
    Check({1,8192,127,248,1,0,0},20); // manual does not require library scratch
    bool rejected=false;
    try{MakePlan({1,1536,1536,1536,1,1,1},20);}catch(const std::runtime_error&){rejected=true;}
    assert(rejected==needsSystem);
    for(uint64_t bytes:{0ULL,8192ULL,16384ULL,32768ULL,65536ULL}){
        platform->l0a=bytes;platform->l0b=bytes;platform->system=16*1024*1024;
        Check({1,1536,1536,1536,1,1,1},20);
    }
    platform->l0a=platform->l0b=65536;
    std::cout<<"panel="<<BMMMS_CUBE_PANEL<<", selected="<<panelPlans<<", resident="<<residentPlans<<"\n";
#ifdef BMMMS_TUNING
    platform->system=16*1024*1024;
    Tune().dual=10;
    auto dot=MakePlan({64,1,1,512,1,0,0},1);
    assert(dot.schedule.kSplit==1 && dot.finalBlocks==8 && dot.totalBytes==256);
    Tune()=TuneConfig{};
#endif
    std::cout<<count<<" real-host plans checked with permissive tiler; CANN tiling PENDING\n";
}
'''
    unified = list(csv.DictReader((ROOT / 'docs/known_issues_cases.csv').open()))
    literals = ','.join('{' + ','.join(r[d] for d in 'BMNK') + ',1,0,0}' for r in unified)
    code = code.replace('// INSERT_UNIFIED_CASES',
                        'Shape unified[]={' + literals + '};\n'
                        'for(auto s:unified)for(int dtype:{1,2})for(int layout=0;layout<4;++layout){'
                        's.dtype=dtype;s.tx1=layout/2;s.tx2=layout%2;Check(s,20);++count;}')
    print('Host control-flow model only; fake tiler accepts requested tiles.', flush=True)
    print('kernel SHA256:', hashlib.sha256(raw).hexdigest(), flush=True)
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler
    with tempfile.TemporaryDirectory(prefix='bmmms-hostplan-') as tmp:
        cpp, exe = Path(tmp) / 'model.cpp', Path(tmp) / 'model'
        cpp.write_text(code)
        for mode in (0, 1, 2, 3):
            for flags in [[], ['-DBMMMS_TUNING']]:
                print('TUNING' if flags else 'production planner', flush=True)
                subprocess.run([compiler, '-std=c++14', '-O2', '-DBMMMS_ADAPTIVE_SPLITK=1',
                                '-DBMMMS_BALANCED_NSPLIT=1', f'-DBMMMS_CUBE_PANEL={mode}',
                                *flags, str(cpp), '-o', str(exe)], check=True, timeout=60)
                subprocess.run([str(exe)], check=True, timeout=60)


if __name__ == '__main__':
    main()
