#!/usr/bin/env python3
"""Execute extracted Cube-ready collective and paired AIV wait under skewed arrivals."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
row=subprocess.check_output(['git','show','81f49ff:kernel.asc'],text=True)
a=s.index('if constexpr(CUBE_READY){\nAscendC::CrossCoreSetFlag<0,PIPE_FIX>(8);')
b=s.index('\n}else AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);',a)
cube=s[a+len('if constexpr(CUBE_READY){\n'):b]
vector='AscendC::CrossCoreWaitFlag<2>(9);'
assert 'if constexpr(CUBE_READY)'+vector in s
old='''AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);
#else
AscendC::CrossCoreWaitFlag<2>(0);
AscendC::SyncAll<true>();
if constexpr(ROW_FINAL)FinalizeSplitTTRows(partial,output,pipe);'''
x=s.index('if constexpr(CUBE_READY){',s.index('void bmmms_manual_split_tt('));y=s.index('else FinalizeSplitKND<PACKED_FINAL>',x)
inv=s[:x]+old+'\n'+s[y:];inv=inv.replace('bool CUBE_READY=false','bool ROW_FINAL=false',1).replace('UseSplitTTCubeCollective','UseSplitTTRowFinalize')
assert inv==row,'arithmetic, guard, producer or workspace changed outside ready protocol'
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name])
PRE=r'''
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <array>
#include <cassert>
#include <chrono>
#include <iostream>
#define PIPE_FIX 0
thread_local unsigned worker;unsigned roundNo;
std::mutex mu;std::condition_variable cv;
std::array<bool,8>ready,issued,collected,paired,consumed;unsigned total=0;
namespace AscendC {
template<int Mode,int Pipe>void CrossCoreSetFlag(unsigned id){std::lock_guard<std::mutex>l(mu);assert(Pipe==PIPE_FIX);
 if constexpr(Mode==0){assert(id==8&&!issued[worker]);ready[worker]=true;issued[worker]=true;++total;cv.notify_all();}
 else{assert(Mode==2&&id==9&&!paired[worker]&&collected[worker]);paired[worker]=true;cv.notify_all();}}
template<int Mode>void CrossCoreWaitFlag(unsigned id){std::unique_lock<std::mutex>l(mu);
 if constexpr(Mode==0){assert(id==8&&issued[worker]&&!collected[worker]);cv.wait(l,[]{return total==8;});collected[worker]=true;}
 else{assert(Mode==2&&id==9);cv.wait(l,[]{return paired[worker];});for(bool r:ready)assert(r);assert(!consumed[worker]);consumed[worker]=true;}}
}
void producer(){
'''
MID='\n}\nvoid consumer(){\n'
END=r'''
}
int main(){for(roundNo=0;roundNo<8;++roundNo){ready.fill(false);issued.fill(false);collected.fill(false);paired.fill(false);consumed.fill(false);total=0;std::vector<std::thread>t;
for(unsigned w=0;w<8;++w)t.emplace_back([=]{worker=w;consumer();});
for(unsigned w=0;w<8;++w)t.emplace_back([=]{worker=w;if(w==roundNo)std::this_thread::sleep_for(std::chrono::milliseconds(20));producer();});
for(auto&x:t)x.join();assert(total==8);for(bool r:consumed)assert(r);for(bool r:collected)assert(r);}
std::cout<<"Actual Cube collective and paired AIV entry: eight skewed producers, all partials before all row owners, all flags consumed across eight arrival orders PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c15-collective-') as tmp:
 d=Path(tmp)
 def run(c,v,name):
  p=d/(name+'.cpp');e=d/name;p.write_text(PRE+c+MID+v+END)
  subprocess.run(['c++','-std=c++17','-O2','-pthread',str(p),'-o',str(e)],check=True)
  return subprocess.run([str(e)],capture_output=True,timeout=10)
 r=run(cube,vector,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,bad in [('missing_collective_wait',cube.replace('AscendC::CrossCoreWaitFlag<0>(8);','')),('missing_collective_publish',cube.replace('AscendC::CrossCoreSetFlag<0,PIPE_FIX>(8);','')),('wrong_collective_id',cube.replace('Flag<0,PIPE_FIX>(8)','Flag<0,PIPE_FIX>(7)')),('wrong_pair_id',cube.replace('Flag<2,PIPE_FIX>(9)','Flag<2,PIPE_FIX>(8)'))]:
  assert bad!=cube;assert run(bad,vector,name).returncode!=0,name
print('Four readiness/ID fault controls, exact row-finalizer/arithmetic/producer inverse, protected7 PASS; CPU flag semantics follow SDK pattern, native protocol remains mandatory')
