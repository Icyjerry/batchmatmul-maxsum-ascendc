#!/usr/bin/env python3
"""Teammate tiny coverage, exact source scope and bounds-checked CPU execution.

This model does not emulate FP16/BF16 encoding or native event timing.
"""
from pathlib import Path
import hashlib, subprocess, shutil, tempfile, sys
ROOT=Path(__file__).resolve().parents[1]
PARENT='d5cd4af'
def git_source(rev):
    return subprocess.check_output(['git','show',rev+':kernel.asc'],cwd=ROOT,text=True)
def region(s,a,b):
    return s[s.index(a):s.index(b,s.index(a))]
def replace_once(s,a,b):
    assert s.count(a)==1, a[:100]
    return s.replace(a,b,1)
def candidate(parent):
    teammate=git_source('9ab2312')
    s=parent
    header='template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>\n__global__ __vector__ void bmmms_tiny_direct'
    s=replace_once(s,header,header.replace('__global__ __vector__ void bmmms_tiny_direct','__aicore__ inline void TinyCompute'))
    s=replace_once(s,'// At most three tiny matrices share input conversion and batched reductions.', '// Capacity-validated tiny groups share input conversion and batched reductions.')
    wrappers='''template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>
__global__ __vector__ void bmmms_tiny_direct(GM_ADDR x1,GM_ADDR x2,GM_ADDR output,TinyKernelShape s)
{
    TinyCompute<T,TX1,TX2,KCONST>(x1,x2,output,s);
}

// Each AIV owns complete batch pairs; only the last group can be shorter.
template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>
__global__ __vector__ void bmmms_tiny_grouped(GM_ADDR x1,GM_ADDR x2,GM_ADDR output,
    TinyKernelShape s,uint32_t batchGroup)
{
    const uint32_t k=KCONST?KCONST:s.k;
    const int64_t b0=int64_t(AscendC::GetBlockIdx())*batchGroup;
    const int64_t remaining=int64_t(s.b)-b0;
    if(remaining<=0)return;
    s.b=remaining<batchGroup?remaining:batchGroup;
    x1=(GM_ADDR)(reinterpret_cast<__gm__ T*>(x1)+b0*s.m*k);
    x2=(GM_ADDR)(reinterpret_cast<__gm__ T*>(x2)+b0*s.n*k);
    output=(GM_ADDR)(reinterpret_cast<__gm__ float*>(output)+b0);
    TinyCompute<T,TX1,TX2,KCONST>(x1,x2,output,s);
}

'''
    marker='template<typename T>\n__aicore__ inline void DotGroupCopy('
    s=replace_once(s,marker,wrappers+marker)
    fits=region(teammate,'// The short vector algorithm has real mask','inline bool SmallFullTileFits')
    fits=replace_once(fits,'s.n>64 || s.k>64','s.n>64 || s.k<32 || s.k>64 || s.k%8!=0')
    fits+='''// Vector-only plan; it uses no Cube session or GM scratch.
inline Plan TinyGroupPlan(const Shape& s,uint64_t ub,uint32_t aiv,uint32_t group=0)
{
    if(!group)group=TinyVectorBatchGroup(s,ub);
    Shape frame=s;frame.b=std::min<int64_t>(s.b,group);
    if(!group || group>8 || !TinyVectorFits(frame,ub))
        throw std::invalid_argument("invalid grouped tiny UB/mask plan");
    Plan p;auto& d=p.schedule;
    d.b=s.b;d.m=s.m;d.n=s.n;d.k=s.k;d.dual=24;d.kSplit=1;d.kChunk=s.k;
    d.batchGroup=group;d.balance=1;d.workers=Ceil(s.b,group);p.finalBlocks=d.workers;
    if(p.finalBlocks>aiv)throw std::runtime_error("insufficient AIV cores for tiny groups");
    return p;
}

'''
    s=replace_once(s,'inline CaseProfile ClassifyCase(',fits+'inline CaseProfile ClassifyCase(')
    s=replace_once(s,'if (s.b >= 1 && s.b <= 3 && s.m <= 8 && s.n <= 16) { c.dual = FORCED_TINY; return c; }',
                     'if (TinyVectorFits(s,ub)) { c.dual = FORCED_TINY; return c; }')
    measured=region(teammate,'    // Keep a full tiny frame on its original entry.','    // Preserve the existing TN')
    s=replace_once(s,'    const bool small4=',measured+'    const bool small4=')
    needle='    if (caseProfile.dual == FORCED_DOT || caseProfile.dual == FORCED_TINY) {'
    early='''#ifdef BMMMS_TUNING
    if(Tune().dual==24)
        return TinyGroupPlan(s,ub,aiv,Tune().group>0?Tune().group:0);
#endif
    if(caseProfile.dual==24)return TinyGroupPlan(s,ub,aiv);
'''
    s=replace_once(s,needle,early+needle)
    needle='''            // bmmms_tiny_direct is single-core and needs no GM scratch.
            p.schedule.workers = 1;'''
    s=replace_once(s,needle,'''            // Independent batch pairs can occupy separate AIVs without GM scratch.
            if(s.b>1 && s.b<=aiv)return TinyGroupPlan(s,ub,aiv,1);
            p.schedule.workers = 1;''')
    s=replace_once(s,'p.schedule.dual==16 && (s.b>3 || s.m>8 || s.n>16 || s.k>64)',
                     'p.schedule.dual==16 && !TinyVectorFits(s,ub)')
    s=replace_once(s,'if(s.b>3 || s.m>8 || s.n>16 || s.k>64)','if(!TinyVectorFits(s,ub))')
    oldhelpers=region(s,'template<typename T,bool TX1,bool TX2,uint32_t KCONST>\ninline void LaunchTinyK',
                         'template <typename T>\ninline void Launch(')
    newhelpers=region(teammate,'template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>\ninline void LaunchTinyK',
                          'template <typename T>\ninline void Launch(')
    s=replace_once(s,oldhelpers,newhelpers)
    launch=region(s,'    if(p.schedule.dual==16) {\n        if(s.tx1', '    if (s.m == 1 && s.n == 1) {\n        if(p.schedule.dual==15)')
    newlaunch=region(teammate,'    if(p.schedule.dual==16) {\n        if(s.tx1', '    if (s.m == 1 && s.n == 1) {\n        if(p.schedule.dual==15)')
    s=replace_once(s,launch,newlaunch)
    return s

def main():
    parent=git_source(PARENT); expected=candidate(parent)
    if '--apply' in sys.argv:
        assert (ROOT/'kernel.asc').read_text()==parent
        (ROOT/'kernel.asc').write_text(expected);return
    src=(ROOT/'kernel.asc').read_text();assert src==expected,'unexpected source change outside precise teammate tiny coverage'
    print('Full source scope: exact candidate transformation of passed '+PARENT+' PASS',flush=True)
    run_models(src,parent)

def run_models(src,parent):
    tiny=region(src,'struct TinyKernelShape', 'template<typename T>\n__aicore__ inline void DotGroupCopy(')
    reference=region(parent,'template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>\n__global__ __vector__ void bmmms_tiny_direct',
                     'template<typename T>\n__aicore__ inline void DotGroupCopy(').replace('bmmms_tiny_direct(','ReferenceTiny(')
    shape=region(src,'struct Shape {','struct Schedule {')
    fits=region(src,'inline bool TinyVectorFits(', '// Vector-only plan;')
    fixture=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
    stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling { int stepKa=1,stepKb=1;')
    code=stub+shape+fixture.replace('// INSERT_KERNELS',tiny+reference+fits)
    code+=(ROOT/'tests/cpu/tiny_batch_coverage_model.cpp.in').read_text()
    shapes=region(src,'struct Shape {','template <AscendC::HardEvent')
    host=stub+shapes+region(src,'struct Plan {','using CacheKey =')
    host+=(ROOT/'tests/cpu/tiny_batch_coverage_host.cpp.in').read_text()
    compiler=shutil.which('clang++') or shutil.which('c++')
    with tempfile.TemporaryDirectory(prefix='bmmms-tiny-coverage-') as tmp:
        def run(text,name,flags=(),negative=False):
            cpp=Path(tmp)/(name+'.cpp');exe=Path(tmp)/name;cpp.write_text(text)
            subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
            r=subprocess.run([str(exe)],capture_output=negative)
            if negative:assert r.returncode!=0, 'negative control not rejected: '+name
            else:r.check_returncode()
        run(code,'vector')
        run(host,'host');run(host,'host-tuning',['-DBMMMS_TUNING'])
        bad=code.replace('output=(GM_ADDR)(reinterpret_cast<__gm__ float*>(output)+b0);', '')
        assert bad!=code;run(bad,'duplicate-output',negative=True)
        bad=code.replace('s.b=remaining<batchGroup?remaining:batchGroup;', 's.b=batchGroup;')
        assert bad!=code;run(bad,'batch-tail',negative=True)
        print('Missing output offset and unclamped batch tail controls rejected PASS')
    print('CANN9 compilation / native precision / NPU timing PENDING',flush=True)
if __name__=='__main__':main()
