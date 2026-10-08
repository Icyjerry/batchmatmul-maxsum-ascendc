#!/usr/bin/env python3
"""Actual resident-B/A frame models; integer arithmetic, not native timing/BF16.

Cross-core companions are synthetic; does not simulate a joint Cube/AIV device.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_tt_manual_frame import cube,vector
ROOT=Path(__file__).resolve().parents[1]
def scope(s):
 e=span(s,'// Same TT tile/package stream','// All N-tile partials are ready')
 old=span(source('7492776'),'// Same TT tile/package stream','// All N-tile partials are ready')
 host=span(s,'// Exact C8: same symmetric tile/package allocation','// Exact supplied C13 geometry')
 call='''            if(C8ResidentBStreamFits(s,p,frame))
                bmmms_tt_manual_frame<T,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);
            else bmmms_tt_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);'''
 oldcall='''            bmmms_tt_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);'''
 assert s.count(call)==1 and s.replace(e,old,1).replace(host,'',1).replace(call,oldcall,1)==source('7492776')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e,host

def producer(s,e):
 f=cube(s,e).split('void Run(uint32_t M,uint32_t N,uint32_t K,')[0]
 # Model the physical independence of the two A1 packages, retaining the single
 # full resident B1. This is the same bank/byte/offset accounting as the parent.
 f=f.replace('uint32_t block=0;', 'bool residentB=false;uint32_t block=0;')
 f=f.replace('if(p==TPosition::B1){mem=', 'if((p==TPosition::B1&&!residentB)||(p==TPosition::A1&&residentB)){mem=')
 return f+(ROOT/'tests/cpu/c8_resident_b_cube.cpp.in').read_text()

def consumer(s,e):
 # Existing extraction expects its original template token; restore only during
 # extraction, then insert the new ownership helpers and actual bool template.
 token='template<typename T,bool RESIDENT_B=false>\n__schedmode__(1)'
 assert e.count(token)==1
 f=vector(s,e.replace(token,'template<typename T>\n__schedmode__(1)',1))
 helpers=span(e,'// N-major full-B residence','template<typename T>\n__aicore__ inline void TTFramePrefetchA')
 f=f.replace('template<typename T>\n__schedmode__(1)',helpers+token,1)
 f=f.replace('thread_local State st;', 'bool residentB=false;thread_local State st;')
 assert 'bool residentB=false;' in f
 # Independent reference mapping inside the synthetic producer/DMA/store oracle.
 f=f.replace('(task/s.nt)', '(residentB?task%(s.mp/s.bm):task/s.nt)')
 f=f.replace('(task%s.nt)', '(residentB?task/(s.mp/s.bm):task%s.nt)')
 f=f.replace('ns=task%s.nt', 'ns=(residentB?task/(s.mp/s.bm):task%s.nt)')
 f=f.replace('mt=task/s.nt', 'mt=(residentB?task%(s.mp/s.bm):task/s.nt)')
 f=f[:f.index('void Run(uint32_t M,uint32_t N,uint32_t BM,')]
 driver=(ROOT/'tests/cpu/tt_manual_frame_vector.cpp.in').read_text()
 driver=driver.replace('uint32_t mode){', 'uint32_t mode,bool resident){',1)
 driver=driver.replace(' uint32_t MP=', ' residentB=resident;uint32_t MP=',1)
 driver=driver.replace('  bmmms_tt_manual_frame<int16_t>(nullptr,nullptr,data.scratch.data(),data.output.data(),s);',
  '  if(resident)bmmms_tt_manual_frame<int16_t,true>(nullptr,nullptr,data.scratch.data(),data.output.data(),s);\n  else bmmms_tt_manual_frame<int16_t>(nullptr,nullptr,data.scratch.data(),data.output.data(),s);')
 driver=driver.replace('(t/nt)*BM','(resident?t%(MP/BM):t/nt)*BM')
 driver=driver[:driver.index('int main()')]+'''int main(){unsigned count=0;
 for(auto v:std::vector<std::vector<uint32_t>>{{129,257,3},{129,129,20},{1025,1031,20},
   {1025,1031,8},{1025,1031,32}})for(bool resident:{false,true})for(bool neg:{false,true})for(uint32_t mode=0;mode<3;++mode){
  Run(v[0],v[1],128,128,v[2],neg,mode,resident);++count;
 }
 std::cout<<count<<" threaded actual AIV groups: independent ownership, N/M tails, three FIFO priorities, destructive ring release, unique original partial/y writers, MaxN then SumM PASS\\n";
}
'''
 return f+driver

def main():
 s=(ROOT/'kernel.asc').read_text();e,host=scope(s)
 print('Whole retained-parent inverse and protected7 PASS; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c8-resident-b-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=240)
   if bad:assert r.returncode!=0,'missed negative control '+name
   else:r.check_returncode()
  c=producer(s,e);run('cube',c)
  for name,line in [('package-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),
   ('resident-reader','            AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(2);'),
   ('package-ready','                AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(ps);'),
   ('resident-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2);cachedOuter=outer;'),
   ('L0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(bs);'),
   ('C-reader','            if(k0==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);'),
   ('full-K-fix','        AscendC::WaitFlag<AscendC::HardEvent::M_FIX>(cs);')]:
   replacement='            cachedOuter=outer;' if name=='resident-ready' else ''
   unsafe=c.replace(line,replacement);assert unsafe!=c;run('no-'+name,unsafe,True,['-DNEGATIVE_CONTROL'])
  # Probe an earlier B release without claiming independent last-reader coverage.
  # The retained MTE1_M readiness wait completes that read before the next task.
  release='''            if(RESIDENT_B && k0+bk>=s.k && (task+1==end || TTFrameTaskN<true>(task+1,s)!=outer))
                AscendC::SetFlag<AscendC::HardEvent::MTE1_MTE2>(2);
'''
  assert c.count(release)==1
  unsafe=c.replace(release,'').replace('            AscendC::LoadData2DParams lp;',release+'            AscendC::LoadData2DParams lp;',1)
  run('early-B-release',unsafe,False,['-DNEGATIVE_CONTROL'])
  print('Seven Cube controls rejected; early B release is NOT detected because the retained MTE1_M wait drains its last read. Keep conservative device release placement; no independent race-detection claim.',flush=True)
  v=consumer(s,e);run('vector',v)
  for name,line in [('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);'),
   ('row-reader','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(slot);'),
   ('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);'),
   ('partial-ready','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(slot);'),
   ('barrier','    AscendC::SyncAll<true>();'),
   ('final-copy-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();'),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();')]:
   unsafe=v.replace(line,'');assert unsafe!=v;run('no-'+name,unsafe,True)
  print('Seven live AIV handoff/barrier/completion controls rejected PASS',flush=True)
 print('Integer/synthetic pipeline evidence only; native CANN/BF16 precision/latency PENDING.')
if __name__=='__main__':main()
