#!/usr/bin/env python3
"""Execute real run_kernel/cache/release code with CPU allocation/runtime doubles."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = (ROOT / 'kernel.asc').read_text()
    shapes = source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
    planner = source[source.index('struct Plan {'):source.index('using CacheKey =')]
    cache = source[source.index('using CacheKey ='):source.index('template <typename T>\ninline void Launch')]
    entry = source[source.index('extern "C" void run_kernel('):]
    runtime = r'''
#include <cstdlib>
using GM_ADDR=char*;using aclrtStream=void*;using aclrtContext=void*;
using aclError=int;constexpr int ACL_SUCCESS=0,ACL_MEM_MALLOC_HUGE_FIRST=0;
struct half{};struct bfloat16_t{};
void* context=reinterpret_cast<void*>(1);
std::map<void*,uint64_t> live;
int fail=0,allocations=0,synchronizations=0;
int aclrtGetCurrentContext(void** c){*c=context;return 0;}
int aclrtSynchronizeStream(void*){++synchronizations;return fail==4?1:0;}
int aclrtMalloc(void** p,uint64_t n,int){if(fail==1)return 1;*p=std::malloc(1);live[*p]=n;++allocations;return 0;}
int aclrtMemset(void* p,uint64_t n,int,uint64_t count){assert(live.at(p)>=n && n>=count);return fail==2?1:0;}
int aclrtFree(void* p){if(fail==3){fail=0;return 1;}assert(live.erase(p)==1);std::free(p);return 0;}
'''
    code = (ROOT / 'tests/cpu/planner_stub.hpp').read_text() + runtime
    code += '\nnamespace bmmms_opt4 {\n' + shapes + '\n}\n'
    code += 'struct TensorGroupInfo {bmmms_opt4::Shape shape;};\nnamespace bmmms_opt4 {\n'
    code += planner + r'''
inline void CheckAcl(int error,const char* msg){if(error)throw std::runtime_error(msg);}
inline Shape Validate(const TensorGroupInfo& a,const TensorGroupInfo&,const TensorGroupInfo&,bool,bool){return a.shape;}
''' + cache + r'''
Plan launched;int launches=0;
template<class T>void Launch(GM_ADDR,GM_ADDR,GM_ADDR,const Shape&,const Plan& p,void* mem,aclrtStream){
    if(p.totalBytes)assert(mem && live.at(mem)>=p.totalBytes);
    launched=p;++launches;
}
}
''' + entry + r'''
void Run(void* stream){
    char x;TensorGroupInfo info{{1,1536,1536,1536,1,1,1}};
    run_kernel(&x,info,&x,info,&x,info,20,stream,true,true);
}
int main(){
    using namespace bmmms_opt4;
    // All 11 tune fields participate in plan-cache equality.
    int TuneConfig::*fields[]={&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,
        &TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,
        &TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers};
    for(auto field:fields){TuneConfig a,b;++(b.*field);assert(!(a==b));assert(a==a);}
    auto s=reinterpret_cast<void*>(2);
    Tune().ns=3;Run(s);assert(launched.schedule.nSplit==3);
    int once=allocations,sync=synchronizations;
    Run(s);assert(allocations==once && synchronizations==sync);
    Tune().ns=1;Run(s);assert(launched.schedule.nSplit==1);
    Tune().ns=3;Run(s);assert(launched.schedule.nSplit==3);
    auto oldkey=CurrentKey(s);
    context=reinterpret_cast<void*>(3);Run(s);
    assert(Cache().size()==2 && CurrentKey(s)!=oldkey);
    release_kernel_resources(s);context=reinterpret_cast<void*>(1);
    release_kernel_resources(s);release_kernel_resources(s);
    assert(live.empty() && Cache().empty());
    // Failures must not publish a valid plan or leak the newly allocated block.
    for(int error:{1,2,4}){
        fail=error;bool threw=false;
        try{Run(s);}catch(const std::runtime_error&){threw=true;}
        assert(threw && live.empty() && !Cache().at(CurrentKey(s)).hasPlan);
        fail=0;Run(s);release_kernel_resources(s);assert(live.empty());
    }
    // Failure freeing the old allocation during growth preserves it for retry.
    Tune().ns=3;Run(s);auto original=Cache().at(CurrentKey(s));
    Tune().ns=1;assert(MakePlan({1,1536,1536,1536,1,1,1},20).totalBytes>original.capacity);
    fail=3;bool threw=false;
    try{Run(s);}catch(const std::runtime_error&){threw=true;}
    assert(threw && live.size()==1 && Cache().at(CurrentKey(s)).memory==original.memory);
    assert(Cache().at(CurrentKey(s)).tuning.ns==3);
    Run(s);assert(launched.schedule.nSplit==1);release_kernel_resources(s);
    assert(live.empty() && Cache().empty());
    std::cout<<"Cache: 11 tune fields, same-shape retuning, context isolation, reuse, release and 4 failure modes PASS\n";
}
'''
    print('CPU runtime doubles; no ACL/NPU lifecycle claim.', flush=True)
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler
    with tempfile.TemporaryDirectory(prefix='bmmms-cache-') as tmp:
        cpp, exe = Path(tmp) / 'model.cpp', Path(tmp) / 'model'
        cpp.write_text(code)
        subprocess.run([compiler, '-std=c++14', '-O2', '-DBMMMS_TUNING',
                        '-DBMMMS_ADAPTIVE_SPLITK=1', '-DBMMMS_BALANCED_NSPLIT=1',
                        str(cpp), '-o', str(exe)], check=True, timeout=60)
        subprocess.run([str(exe)], check=True, timeout=60)


if __name__ == '__main__':
    main()
