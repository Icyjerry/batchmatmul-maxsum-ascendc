#!/usr/bin/env python3
"""Extracted FF producer + actual AIV row ownership/store and finalizer.

Integer/FIFO CPU evidence. Synthetic Vector maxima isolate row ownership;
unchanged reduction body is byte checked. Not native timing/TQue proof.
"""
from pathlib import Path
import hashlib,re,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_c10_ff_b_packages import model as ff_model
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 old=source('af886e1');e=span(s,'// The basic-API path owns','// Resident A and larger B packages');p=span(old,'// The basic-API path owns','// Resident A and larger B packages')
 helper=span(s,'// Partition actual M rows','// The basic-API path owns')
 host=span(s,'// Keep complete-N maxima','struct Case9PackagePlan')
 launch=span(s,'    if(UseBalancedMShards(s,p)) {','    if(p.schedule.dual==20 && s.dtype==1')
 assert s.replace(helper,'',1).replace(e,p,1).replace(host,'',1).replace(launch,'',1)==old
 v=e[e.index('#else\n    AscendC::TQue'):];pv=p[p.index('#else\n    AscendC::TQue'):]
 a=span(v,'    const auto range=','        const uint32_t rowLimit=');b=span(pv,'    const auto range=','        const uint32_t rowLimit=')
 store=span(v,'            if constexpr(M_BALANCE) {','        }\n        mq.FreeTensor(maxima);')
 prev=span(pv,'            AscendC::DataCopy(partials[(batch*s.nSplit','        }\n        mq.FreeTensor(maxima);')
 assert v.replace(a,b,1).replace(store,prev,1)==pv,'Vector arithmetic/sync changed'
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e,helper

def cube(s,e,helper):
 f=ff_model(s,e).split('// Test extracted C9 producer')[0]
 f=f.replace(' constexpr bool TX1=false,TX2=false,RESIDENT_PAD=true,FULL_A=false,RESIDENT_B=false;',
  ' constexpr bool TX1=false,TX2=false,RESIDENT_PAD=true,FULL_A=false,RESIDENT_B=false,M_BALANCE=B_PACKAGE!=0;')
 f=f.replace(' const int64_t tasks=s.b*s.mTiles*s.nSplit;uint32_t sequence=0;',
  ' const auto mShard=M_BALANCE?ManualBalancedMShard(s,worker):ManualMShard{0,s.m};\n const int64_t ownedRows=mShard.end-mShard.begin;\n const int64_t tasks=M_BALANCE?(ownedRows+s.baseM-1)/s.baseM:s.b*s.mTiles*s.nSplit;uint32_t sequence=0;')
 f=f.replace('template<class T,bool PAD_MN,uint32_t B_PACKAGE>',helper+'template<class T,bool PAD_MN,uint32_t B_PACKAGE>',1)
 f+=(ROOT/'tests/cpu/c10_balanced_m_cube.cpp.in').read_text()
 return f

def ownership(s,e,helper):
 v=e[e.index('#else\n    AscendC::TQue'):]
 projection=span(v,'        const uint32_t ns=M_BALANCE','        const uint32_t begin=ns*s.nTiles')
 store=span(v,'            if constexpr(M_BALANCE) {','        }\n        mq.FreeTensor(maxima);')
 final=span(s,'__aicore__ inline void FinalizeRows(GM_ADDR partial, GM_ADDR output, Schedule s, AscendC::TPipe &pipe)\n{','__aicore__ inline void FinalizeSplitK(')
 f=(ROOT/'tests/cpu/c10_balanced_m_ownership.cpp.in').read_text()
 return f.replace('// SHARD_HELPER',helper).replace('// PROJECTION',projection).replace('// STORE',store).replace('// FINALIZER',final)

def host(s):
 headers='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in ['C7KernelShape','WideNKernelShape','TTFrameShape','C13ResidentFrame'])
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 return stub+span(s,'struct Shape {','template <AscendC::HardEvent')+headers+span(s,'struct Plan {','using CacheKey =')+r'''
int main(){auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();unsigned n=0,hits=0;
 for(int cores:{1,3,8,20,24,32})for(int m:{4096,4112,6144,8176})for(int dt:{1,2})for(int x:{0,1})for(int y:{0,1}){
  hw->aic=cores;hw->aiv=2*cores;Shape s{1,m,1280,1152,dt,x,y};auto p=MakePlan(s,cores);bool hit=UseBalancedMShards(s,p);
  if(hit){assert(dt==2&&!x&&!y&&p.schedule.nSplit==1);assert(Ceil(m/16,p.schedule.workers)*16*10<=Ceil(p.schedule.mTiles,p.schedule.workers)*128*9);}++n;hits+=hit;
 }
 Shape s{1,4096,1280,1152,2,0,0};hw->aic=20;hw->aiv=40;auto p=MakePlan(s,20);assert(UseBalancedMShards(s,p));
 for(auto field:{&s.b,&s.m,&s.n,&s.k}){++*field;assert(!UseBalancedMShards(s,p));--*field;}
 for(auto field:{&p.schedule.baseM,&p.schedule.baseN,&p.schedule.kChunk,&p.schedule.tree,&p.schedule.nSplit,&p.schedule.kSplit,&p.schedule.window}){++*field;assert(!UseBalancedMShards(s,p));--*field;}
 p.totalBytes=p.systemBytes+16384+uint64_t(p.schedule.workers)*262144;assert(UseBalancedMShards(s,p));--p.totalBytes;assert(!UseBalancedMShards(s,p));
#ifdef BMMMS_TUNING
 for(auto field:{&Tune().group,&Tune().rows,&Tune().dual,&Tune().early,&Tune().tree,&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,&Tune().workers}){Tune()=TuneConfig{};*field=1;assert(!UseBalancedMShards(s,p));}Tune()=TuneConfig{};
#endif
 assert(hits);std::cout<<n<<" actual host plans/"<<hits<<" hits, complete N/resource-derived arena/pins PASS\n";
}
'''

def main():
 s=(ROOT/'kernel.asc').read_text();e,h=scope(s);c=cube(s,e,h);v=ownership(s,e,h);p=host(s)
 print('kernel SHA256',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c10-m-shards-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=180)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  run('cube',c);run('ownership-finalizer',v);run('host',p);run('host-tuning',p,flags=['-DBMMMS_TUNING'])
  proxy=c.replace('Run<true>({1,4096,1280,1152,128,256,0,0,1,20,0,0},false);','')
  for name,a,b in [('shard-bound','const int64_t remaining=(M_BALANCE?mShard.end:s.m)-m0;','const int64_t remaining=s.m-m0;'),
   ('C-ready','Fence<AscendC::HardEvent::M_FIX>();',''),('L0-ready','AscendC::WaitFlag<AscendC::HardEvent::MTE1_M>(loadReady[ks]);','')]:
   assert a in proxy;run('bad-'+name,proxy.replace(a,b,1),True)
  for name,a,b in [('padded-store','if(rows)AscendC::DataCopy(partials[m0+rowStart],maxima,rows);','AscendC::DataCopy(partials[m0+rowStart],maxima,s.baseM/2);'),
   ('writer-start','mShard.begin+task*s.baseM','task*s.baseM'),('writer-bound','(M_BALANCE?mShard.end:s.m)-m0-rowStart','s.m-m0-rowStart')]:
   assert a in v;run('bad-'+name,v.replace(a,b,1),True)
  print('Six ownership/readiness fault controls rejected PASS')
 print('Native CANN9/TQue/precision/performance PENDING; no inferred route hit.')
if __name__=='__main__':main()
