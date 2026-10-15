#!/usr/bin/env python3
"""Actual static MDL guard/config and whole-source scope; no SDK/kernel emulator."""
from pathlib import Path
import subprocess, tempfile

R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
parent=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
a=s.index('template<bool STATIC_C11>constexpr auto DualMdlEntryConfig()')
b=s.index('template<typename T,bool TX1,bool TX2,bool STATIC_C11=false>',a)
config=s[a:b]
a=s.index('inline bool UseStaticMdlC11(');b=s.index('using CacheKey=',a);guard=s[a:b]
hook='''if(UseStaticMdlC11(s,p)){
bmmms_dual_mdl<T,true,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,workspace,p.cube,p.schedule);
return;
}
'''
assert s.count(hook)==1
inv=s.replace(config,'',1).replace(guard,'',1).replace(hook,'',1)
inv=inv.replace('template<typename T,bool TX1,bool TX2,bool STATIC_C11=false>', 'template<typename T,bool TX1,bool TX2>',1)
inv=inv.replace('matmul::Matmul<A,B,C,Bias,DUAL_MDL_ENTRY_CONFIG<STATIC_C11>>mm;', 'matmul::Matmul<A,B,C,Bias,DUAL_MDL_CONFIG>mm;',1)
assert inv==parent,'Algorithm/task/allocator/default body escaped intended scope'
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
    assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name])
static_fields={'baseM':256,'baseN':128,'baseK':64,'stepM':1,'stepN':1,'stepKa':4,'stepKb':4,'depthA1':8,'depthB1':8,'dbL0A':2,'dbL0B':2,'dbL0C':1,'shareL1Size':393216}
runtime_fields=['usedCoreNum','M','N','Ka','Kb','singleCoreM','singleCoreN','singleCoreK','isBias','transLength','iterateOrder','shareMode','shareL0CSize','shareUbSize','depthAL1CacheUB','depthBL1CacheUB']
static_stub='struct MatmulApiStaticTiling{int cfg=-1;'+''.join('int '+f+'=-1;' for f in [*static_fields,*runtime_fields])+'};\nconstexpr int DUAL_MDL_CONFIG=73;\n'
checks=''.join(f'static_assert(c.{f}=={v},"constant {f}");\n' for f,v in static_fields.items())
checks+=''.join(f'static_assert(c.{f}==-1,"runtime {f}");\n' for f in runtime_fields)
checks+='static_assert(c.cfg==DUAL_MDL_CONFIG && DUAL_MDL_ENTRY_CONFIG<false> == DUAL_MDL_CONFIG,"default config");\n'
stub=(R/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {uint32_t stepKa=0,stepKb=0,depthA1=0,depthB1=0,dbL0A=0,dbL0B=0,dbL0C=0,shareL1Size=0;')
a=s.index('struct Shape{');b=s.index('template<AscendC::HardEvent E>',a);types=s[a:b]
a=s.index('struct Plan{');b=s.index('inline bool Case12K16GroupZn(',a);plans=s[a:b]
main=r'''
int main(){Shape s{1,1536,2048,2048,2,1,1};Plan p{};
p.schedule={1,1536,2048,2048,256,128,6,16,16,20,1024,1,1,2048,1536,8,2,0,0,1};
p.cubeBlocks=20;p.finalBlocks=1;p.systemBytes=16777216;
p.cube.usedCoreNum=20;p.cube.baseM=256;p.cube.baseN=128;p.cube.baseK=64;
p.cube.stepM=p.cube.stepN=1;p.cube.stepKa=p.cube.stepKb=4;p.cube.depthA1=p.cube.depthB1=8;
p.cube.dbL0A=p.cube.dbL0B=2;p.cube.dbL0C=1;p.cube.shareL1Size=393216;
auto total=[](Plan&q){q.totalBytes=q.systemBytes+98304+262144ULL*q.schedule.workers;};total(p);
auto*hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=24;hw->aiv=48;hw->ub=196352;hw->l1=524032;
auto ok=[&](Shape x,Plan q){return UseStaticMdlC11(x,q);};unsigned accepts=0,rejects=0;
assert(ok(s,p));++accepts;{auto x=s;x.dtype=1;assert(ok(x,p));++accepts;}
for(auto f:{&Shape::b,&Shape::m,&Shape::n,&Shape::k}){auto x=s;++(x.*f);assert(!ok(x,p));++rejects;}
for(int dt:{0,3}){auto x=s;x.dtype=dt;assert(!ok(x,p));++rejects;}
for(auto f:{&Shape::tx1,&Shape::tx2}){auto x=s;x.*f=0;assert(!ok(x,p));++rejects;}
for(auto f:{&Schedule::b,&Schedule::m,&Schedule::n,&Schedule::k}){auto q=p;++(q.schedule.*f);assert(!ok(s,q));++rejects;}
for(auto f:{&Schedule::baseM,&Schedule::baseN,&Schedule::mTiles,&Schedule::nTiles,&Schedule::nSplit,&Schedule::kSplit,&Schedule::kChunk,&Schedule::window,&Schedule::dual,&Schedule::earlySum,&Schedule::tree,&Schedule::workers}){auto q=p;++(q.schedule.*f);assert(!ok(s,q));++rejects;}
for(auto f:{&Plan::small,&Plan::micro,&Plan::case12PackedA}){auto q=p;q.*f=true;assert(!ok(s,q));++rejects;}
for(auto f:{&Plan::cubeBlocks,&Plan::finalBlocks}){auto q=p;++(q.*f);assert(!ok(s,q));++rejects;}
for(auto f:{&AscendC::tiling::TCubeTiling::usedCoreNum,&AscendC::tiling::TCubeTiling::baseM,&AscendC::tiling::TCubeTiling::baseN,&AscendC::tiling::TCubeTiling::baseK,&AscendC::tiling::TCubeTiling::stepM,&AscendC::tiling::TCubeTiling::stepN,&AscendC::tiling::TCubeTiling::stepKa,&AscendC::tiling::TCubeTiling::stepKb,&AscendC::tiling::TCubeTiling::depthA1,&AscendC::tiling::TCubeTiling::depthB1,&AscendC::tiling::TCubeTiling::dbL0A,&AscendC::tiling::TCubeTiling::dbL0B,&AscendC::tiling::TCubeTiling::dbL0C,&AscendC::tiling::TCubeTiling::shareL1Size}){auto q=p;++(q.cube.*f);assert(!ok(s,q));++rejects;}
{auto q=p;q.systemBytes=0;assert(!ok(s,q));++rejects;q=p;q.systemBytes+=512;total(q);assert(!ok(s,q));++rejects;q=p;--q.totalBytes;assert(!ok(s,q));++rejects;q=p;q.schedule.workers=q.cubeBlocks=q.cube.usedCoreNum=0;assert(!ok(s,q));++rejects;}
for(auto item:std::vector<std::pair<uint64_t*,uint64_t>>{{&hw->l1,393216},{&hw->l0a,65536},{&hw->l0b,32768},{&hw->l0,131072},{&hw->ub,138272}}){auto v=*item.first;*item.first=item.second;assert(ok(s,p));++accepts;--*item.first;assert(!ok(s,p));++rejects;*item.first=v;}
for(unsigned w:{1u,8u,20u,24u,32u}){auto q=p;q.schedule.workers=q.cubeBlocks=q.cube.usedCoreNum=w;hw->aic=w;hw->aiv=2*w;total(q);assert(ok(s,q));++accepts;--hw->aic;assert(!ok(s,q));++rejects;++hw->aic;--hw->aiv;assert(!ok(s,q));++rejects;}hw->aic=24;hw->aiv=48;
#ifdef BMMMS_TUNING
for(auto f:{&TuneConfig::group,&TuneConfig::rows,&TuneConfig::dual,&TuneConfig::early,&TuneConfig::tree,&TuneConfig::bm,&TuneConfig::bn,&TuneConfig::window,&TuneConfig::ns,&TuneConfig::ks,&TuneConfig::workers}){auto v=Tune();Tune().*f=1;assert(!ok(s,p));++rejects;Tune()=v;assert(ok(s,p));}
#endif
std::cout<<"Actual static C11 guard "<<accepts<<" accepts/"<<rejects<<" rejects, dtype/core/resource/workspace/tiling/tuning boundaries PASS\n";}
'''
code=stub+types+plans+static_stub+config+'constexpr auto c=DUAL_MDL_ENTRY_CONFIG<true>;\n'+checks+guard+main
with tempfile.TemporaryDirectory(prefix='bmmms-c11-static-') as tmp:
    p=Path(tmp)/'test.cpp';exe=Path(tmp)/'test';p.write_text(code)
    for tuning in (False,True):
        subprocess.run(['c++','-std=c++17','-O2']+(['-DBMMMS_TUNING'] if tuning else [])+[str(p),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
print('13 frozen values/16 runtime defaults, original config/default MDL body, entire-source inverse and protected7 PASS. Not SDK/native evidence.')
