#!/usr/bin/env python3
"""Actual C9 AIV and finalizer + old consumer under FIFO CPU engines.

Synthetic complete-K Cube, software float semantics and fake host tiler.
Unchanged Cube byte proof; not CANN/FP16 accuracy or hardware timing.
"""
from pathlib import Path
import hashlib,re,shutil,subprocess,tempfile
from validate_c7_manual_frame import source,span
ROOT=Path(__file__).resolve().parents[1]
START='template <typename T, bool PAD_MN'
END='// Isolated case12 packed-B'
def scope(s):
 old=source('a2e6763')
 a=s.index(START,s.index('inline void Case9CopyBPackage'));b=s.index(END,a);e=s[a:b]
 a=old.index(START,old.index('inline void Case9CopyBPackage'));b=old.index(END,a);oe=old[a:b]
 h=span(s,'// Only the retained exact C9 package route','// Select only an already complete TF batch')
 launch=span(s,'            if(UseC9StreamMax(s,p)) {','            const bool pad=s.m%16 || s.n%16 || s.k%16;')
 assert s.replace(e,oe,1).replace(h,'',1).replace(launch,'',1)==old
 assert span(e,'#ifdef __DAV_CUBE__\n    AscendC::SetAtomicNone();','\n#else\n    AscendC::TQue')==span(oe,'#ifdef __DAV_CUBE__\n    AscendC::SetAtomicNone();','\n#else\n    AscendC::TQue')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e

def model(s,e):
 intro=span(e,'    AscendC::TPipe pipe;','\n#ifdef __DAV_CUBE__\n    const uint32_t worker')
 vars=span(e,'    ring.SetGlobalBuffer','\n#ifdef __DAV_CUBE__\n    AscendC::SetAtomicNone();')
 body=span(e,'#else\n    AscendC::TQue','\n#endif\n}')[len('#else\n'):]
 wrapper='''template<class T,bool PAD_MN,bool STREAM_MAX>void RunC9AIV(
 GM_ADDR x1,GM_ADDR x2,GM_ADDR partial,GM_ADDR output,Schedule s,uint32_t aPackK,uint32_t bPackK){
'''+intro+'''\n    const uint32_t worker=AscendC::GetBlockIdx()/2,sub=AscendC::GetBlockIdx()%2;
    const uint32_t rowStart=sub*(s.baseM/2);
'''+vars+'\n'+body+'\n}\n'
 fence=span(s,'template <AscendC::HardEvent E>\n__aicore__ inline void Fence()','template <typename T, bool TX1, bool TX2>')
 final=span(s,'__aicore__ inline void FinalizeRows(GM_ADDR partial, GM_ADDR output, Schedule s, AscendC::TPipe &pipe)\n{','__aicore__ inline void FinalizeSplitK(')
 f=(ROOT/'tests/cpu/c9_stream_max_aiv.cpp.in').read_text()
 return f.replace('// INSERT_ACTUAL_FENCE',fence).replace('// INSERT_ACTUAL_FINALIZER',final).replace('// INSERT_ACTUAL_CONSUMER',wrapper)

def host(s):
 headers='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in ['C7KernelShape','WideNKernelShape','TTFrameShape','C13ResidentFrame'])
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 return '#include <cstring>\n'+stub+span(s,'struct Shape {','template <AscendC::HardEvent')+headers+span(s,'struct Plan {','using CacheKey =')+r'''
int main(){auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();unsigned n=0,hits=0;
 for(int cores:{1,3,8,20,24,32})for(int B:{1,2})for(int M:{2047,2048,2049})for(int N:{1535,1536,1537})
 for(int K:{1272,1280,1288})for(int dt:{1,2})for(int lay=0;lay<4;++lay){
  hw->aic=cores;hw->aiv=2*cores;Shape s{B,M,N,K,dt,lay/2,lay%2};auto p=MakePlan(s,cores),old=p;
  bool hit=UseC9StreamMax(s,p);++n;
  assert(!memcmp(&p.schedule,&old.schedule,sizeof(Schedule))&&p.totalBytes==old.totalBytes&&p.cubeBlocks==old.cubeBlocks);
  if(hit){++hits;assert(B==1&&M==2048&&N==1536&&K==1280&&dt==1&&lay==1);}
 }
 assert(hits==6);hw->aic=20;hw->aiv=40;Shape s{1,2048,1536,1280,1,0,1};auto p=MakePlan(s,20);assert(UseC9StreamMax(s,p));
 auto d=p.schedule;uint64_t minimum=uint64_t(d.baseM)*d.baseN*4+20ULL*d.baseM+3ULL*d.vectorTile*4+64+uint64_t(d.baseM/2)*64*4+4096;
 auto saved=hw->ub;hw->ub=minimum;assert(UseC9StreamMax(s,p));--hw->ub;assert(!UseC9StreamMax(s,p));hw->ub=saved;
 for(auto cap:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0}){auto old=*cap;*cap=4096;assert(!UseC9StreamMax(s,p));*cap=old;}
 auto bytes=p.totalBytes;p.totalBytes=p.systemBytes;assert(!UseC9StreamMax(s,p));p.totalBytes=bytes;
 for(auto field:{&p.schedule.b,&p.schedule.m,&p.schedule.n,&p.schedule.k}){++*field;assert(!UseC9StreamMax(s,p));--*field;}
 for(auto field:{&p.schedule.baseM,&p.schedule.baseN,&p.schedule.kChunk,&p.schedule.kSplit,&p.schedule.earlySum,&p.schedule.workers}){++*field;assert(!UseC9StreamMax(s,p));--*field;}
 hw->aic=d.workers-1;assert(!UseC9StreamMax(s,p));hw->aic=20;hw->aiv=2*(d.workers-1);assert(!UseC9StreamMax(s,p));hw->aiv=40;
#ifdef BMMMS_TUNING
 for(auto field:{&Tune().group,&Tune().rows,&Tune().dual,&Tune().early,&Tune().tree,&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,&Tune().workers}){Tune()=TuneConfig{};*field=1;assert(!UseC9StreamMax(s,p));}Tune()=TuneConfig{};
#endif
 std::cout<<n<<" actual host plans/"<<hits<<" exact C9 hits; UB one-byte/core/capacity/arena/pin boundaries, original Plan unchanged PASS\n";
}
'''

def main():
 s=(ROOT/'kernel.asc').read_text();e=scope(s);v=model(s,e);p=host(s)
 print('Whole parent inverse + Cube byte identity + protected7 PASS; SHA',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or 'c++'
 with tempfile.TemporaryDirectory(prefix='bmmms-c9-stream-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=240)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  run('host',p);run('host-tuning',p,flags=['-DBMMMS_TUNING']);run('aiv',v)
  for name,a,b in [
   ('negative-init','if(rows)AscendC::Duplicate(lanes,-__builtin_inff(),rows*64)','if(rows)AscendC::Duplicate(lanes,0.0f,rows*64)'),
   ('N-mask','AscendC::Max(lanes,lanes,c[col],uint64_t(n),rows,rp);','AscendC::Max(lanes,lanes,c[col],uint64_t(64),rows,rp);'),
   ('C-pitch','8,8,static_cast<uint8_t>(s.baseN/8)','8,8,uint8_t(8)'),
   ('final-fold','            AscendC::WholeReduceMax(maxima,lanes,uint64_t(64),rows,1,1,8,\n                AscendC::ReduceOrder::ORDER_ONLY_VALUE);',''),
   ('task-reset','if(rows)AscendC::Duplicate(lanes,-__builtin_inff(),rows*64)','if(rows&&task==worker)AscendC::Duplicate(lanes,-__builtin_inff(),rows*64)'),
   ('C-ready','                cq.EnQue(c);c=cq.DeQue<float>();','                c=cq.DeQue<float>();'),
   ('ring-release','            AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(2+slot);',''),
   ('final-barrier','    AscendC::SyncAll<true>();','')]:
   assert a in v,name;run('bad-'+name,v.replace(a,b),True,['-DNEGATIVE_CONTROL'])
  early=v.replace('                cq.FreeTensor(c);','').replace('                for(uint32_t col=0;col<cols;col+=64) {','                cq.FreeTensor(c);\n                for(uint32_t col=0;col<cols;col+=64) {')
  assert early!=v;run('bad-early-C-free',early,True,['-DNEGATIVE_CONTROL'])
  print('Nine initialization/tail/pitch/task/C queue/ring/fold/barrier fault controls rejected PASS',flush=True)
 print('FIFO models include no instruction-internal Vector pipeline; fake tiler/synthetic complete-K Cube/native FP16/CANN timing remain limitations.')
if __name__=='__main__':main()
