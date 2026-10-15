#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
a=s.index('struct TinyKernelShape{');b=s.index('};',a)+2;tiny=s[a:b]
a=s.index('inline bool TinyVectorFits(');b=s.index('inline uint32_t TinyVectorBatchGroup(',a);fits=s[a:b]
a=s.index('template<bool TX1,bool TX2>\ninline bool UseTinyFlatGather48(');b=s.index('template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>',a);guard=s[a:b]
main=r'''
bool accept(bool t1,bool t2,TinyKernelShape s,unsigned g,unsigned b){if(t1)return t2?UseTinyFlatGather48<true,true>(s,g,b):UseTinyFlatGather48<true,false>(s,g,b);return t2?UseTinyFlatGather48<false,true>(s,g,b):UseTinyFlatGather48<false,false>(s,g,b);}
int main(){TinyKernelShape s{2,7,13,48};auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->ub=196352;hw->aiv=48;unsigned good=0,reject=0;
for(bool t1:{false,true})for(bool t2:{false,true}){if(!t1&&t2){assert(!accept(t1,t2,s,1,2));++reject;continue;}assert(accept(t1,t2,s,1,2));++good;
for(auto field:{&TinyKernelShape::b,&TinyKernelShape::m,&TinyKernelShape::n,&TinyKernelShape::k}){auto bad=s;bad.*field+=1;assert(!accept(t1,t2,bad,1,2));++reject;}
for(unsigned g:{0u,2u}){assert(!accept(t1,t2,s,g,2));++reject;}for(unsigned b:{1u,3u}){assert(!accept(t1,t2,s,1,b));++reject;}
hw->aiv=1;assert(!accept(t1,t2,s,1,2));++reject;hw->aiv=2;assert(accept(t1,t2,s,1,2));hw->aiv=48;
unsigned minimum=t1?(t2?34144:36608):35296;hw->ub=minimum;assert(accept(t1,t2,s,1,2));--hw->ub;assert(!accept(t1,t2,s,1,2));++reject;hw->ub=196352;
#ifdef BMMMS_TUNING
for(auto field:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){auto old=Tune();Tune().*field=1;assert(!accept(t1,t2,s,1,2));Tune()=old;assert(accept(t1,t2,s,1,2));++reject;}
#endif
}std::cout<<"Actual flat-gather guard: "<<good<<" accepted layouts; "<<reject<<" shape/group/grid/AIV/UB/pin rejections and exact capacity boundaries PASS\n";}
'''
code=(R/'tests/cpu/planner_stub.hpp').read_text()+'\n'+types+plans+tiny+fits+guard+main
with tempfile.TemporaryDirectory(prefix='bmmms-c3-guard-') as tmp:
 d=Path(tmp);(d/'test.cpp').write_text(code)
 for tuning in (False,True):
  subprocess.run(['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(d/'test.cpp'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
