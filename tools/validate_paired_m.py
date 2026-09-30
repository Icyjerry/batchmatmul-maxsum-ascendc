#!/usr/bin/env python3
"""Execute paired-M source in CPU block model; no CANN or real event timing."""
from pathlib import Path
import shutil, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
src=(root/'kernel.asc').read_text()
zero=src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
helpers=src[src.index('// TT products in one M pair'):src.index('__aicore__ inline void ManualCopyC(')]
model=(root/'tests/cpu/paired_m_model.cpp.in').read_text().replace('// INSERT_HELPERS',zero+helpers)
shapes=src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host=src[src.index('struct Plan {'):src.index('using CacheKey =')]
hostmodel=(root/'tests/cpu/planner_stub.hpp').read_text()+shapes+host+r'''
int main() {
    auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
    unsigned paired=0;
    for(int cores:{1,4,8,20,24})for(int m:{1024,1025,1536,1537})
    for(int n:{1536,2048,3072})for(int k:{2048,2056,3072})for(int dtype:{1,2}) {
        Shape s{1,m,n,k,dtype,1,1};auto p=MakePlan(s,cores);const auto& d=p.schedule;
        if(d.dual!=28)continue;
        assert((d.baseM==128 || d.baseM==256) && d.baseN==128 && d.window==1 && d.kSplit==1);
        assert(d.mTiles==Ceil(m,d.baseM) && d.nTiles==Ceil(n,128));
        assert(d.workers>0 && d.workers<=cores && d.workers<=d.mTiles*d.nSplit);
        assert(p.cubeBlocks==d.workers && p.systemBytes==Ceil(hw->system,512)*512 && !d.earlySum);
        const auto parts=uint64_t(d.nSplit)*d.mTiles*d.baseM*4;
        assert(p.totalBytes==p.systemBytes+Ceil(parts,512)*512+uint64_t(d.workers)*2*d.baseM*d.baseN*4);
        ++paired;
    }
    assert(paired>0);
    Shape hit{1,1536,3072,3072,1,1,1};assert(MakePlan(hit,20).schedule.dual==28);
    for(auto member:{&hw->l0a,&hw->l0b,&hw->l0,&hw->l1,&hw->ub}) {
        auto old=*member;*member=4096;
        try {assert(MakePlan(hit,20).schedule.dual!=28);}catch(const std::runtime_error&){}
        *member=old;
    }
    for(Shape s:{Shape{1,1536,3072,1536,1,1,1},Shape{2,1536,3072,3072,1,1,1},
            Shape{1,1536,3072,3072,1,0,1},Shape{1,1536,3072,3072,1,1,0},
            Shape{1,64,127,8192,1,1,1}})assert(MakePlan(s,20).schedule.dual!=28);
#ifdef BMMMS_TUNING
    for(auto pin:{&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,
            &Tune().workers,&Tune().tree,&Tune().dual,&Tune().early}) {
        Tune()=TuneConfig{};*pin=1;
        try {assert(MakePlan(hit,20).schedule.dual!=28);}catch(const std::invalid_argument&){}
    }
#endif
    std::cout<<paired<<" paired-M host resource/routing/workspace/pins checks PASS\n";
}
'''
compiler=shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-paired-m-') as d:
    for name,code,flags in [('producer',model,[]),('host',hostmodel,[]),('host-pins',hostmodel,['-DBMMMS_TUNING'])]:
        cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name
        cpp.write_text(code)
        subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
