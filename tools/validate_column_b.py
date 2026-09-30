#!/usr/bin/env python3
"""Execute actual column-B source; synchronous CPU model, not NPU evidence."""
from pathlib import Path
import shutil
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
source=(root/'kernel.asc').read_text()
zero=source[source.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):
            source.index('// One Cube owns one complete small batch.')]
copy=source[source.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>'):
            source.index('// A TT N panel remains')]
producer=source[source.index('// A TT N panel remains'):source.index('template<typename T>\n__schedmode__(1) __global__ __mix__(1,2) void bmmms_column_b')]
start=source.index('void bmmms_column_b(')
vector=source[source.index('#else\n    const uint32_t ns=',start)+6:source.index('    AscendC::SyncAll<true>();',start)]
vector='void RunVector(AscendC::TPipe& pipe,AscendC::GlobalTensor<float> ring,AscendC::GlobalTensor<float> partials,const Schedule& s,uint32_t worker,uint32_t sub){\nconst uint32_t slotSize=s.baseM*s.baseN;\n'+vector+'}\n'
model=(root/'tests/cpu/column_b_model.cpp.in').read_text().replace('// INSERT_HELPERS',zero+copy+producer).replace('// INSERT_VECTOR',vector)
assert '// INSERT_' not in model
shapes=source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
host=source[source.index('struct Plan {'):source.index('using CacheKey =')]
hostmodel=(root/'tests/cpu/planner_stub.hpp').read_text()+shapes+host+r'''
int main(){
    auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();unsigned chosen=0;
    for(int cores:{1,4,8,20,24,32})for(int m:{1024,1025,1536,1537})
    for(int n:{1024,1535,1536,2048})for(int k:{1024,1032,1536,1544,2048}){
        Shape s{1,m,n,k,2,1,1};auto p=MakePlan(s,cores);auto& d=p.schedule;
        if(d.dual!=29)continue;
        assert(d.baseM==128 && d.baseN==128 && d.window==1 && d.kSplit==1);
        assert(d.workers==p.cubeBlocks && d.workers<=cores && d.workers%d.nSplit==0);
        unsigned mg=d.workers/d.nSplit;assert(d.mTiles>=2*mg);
        auto parts=uint64_t(d.nSplit)*d.mTiles*d.baseM*4;
        assert(p.totalBytes==p.systemBytes+Ceil(parts,512)*512+uint64_t(d.workers)*2*d.baseM*d.baseN*4);
        ++chosen;
    }
    Shape hit{1,1536,1536,1536,2,1,1};auto p=MakePlan(hit,20);assert(p.schedule.dual==29);
    assert(p.schedule.nSplit==6 && p.schedule.workers==18);
    for(auto member:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){
        auto before=*member;*member=4096;
        try{assert(MakePlan(hit,20).schedule.dual!=29);}catch(const std::runtime_error&){}
        *member=before;
    }
    for(Shape s:{Shape{1,1536,1536,2048,2,1,1},Shape{1,1536,1536,1536,1,1,1},
        Shape{2,1536,1536,1536,2,1,1},Shape{1,1536,1536,1536,2,0,1},
        Shape{1,1536,1536,1536,2,1,0},Shape{1,1536,1536,1536,2,0,0}})
        assert(MakePlan(s,20).schedule.dual!=29);
#ifdef BMMMS_TUNING
    for(auto member:{&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,
        &Tune().workers,&Tune().tree,&Tune().dual,&Tune().early}){
        Tune()=TuneConfig{};*member=1;
        try{assert(MakePlan(hit,20).schedule.dual!=29);}catch(const std::invalid_argument&){}
    }
#endif
    std::cout<<chosen<<" host column-B routing/resource/grid/workspace checks PASS\n";
}
'''
compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-column-b-') as directory:
    for name,code,flags in [('blocks',model,[]),('host',hostmodel,[]),('pins',hostmodel,['-DBMMMS_TUNING'])]:
        cpp,exe=Path(directory)/(name+'.cpp'),Path(directory)/name
        cpp.write_text(code)
        subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
