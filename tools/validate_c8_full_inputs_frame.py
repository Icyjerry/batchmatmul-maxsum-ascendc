#!/usr/bin/env python3
"""Full-input C8 actual-source models: CPU integers and synthetic pipelines only."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_tt_manual_frame import cube,vector
ROOT=Path(__file__).resolve().parents[1]
def scope(s):
 e=span(s,'// Same TT tile/package stream','// All N-tile partials are ready')
 old=span(source('7492776'),'// Same TT tile/package stream','// All N-tile partials are ready')
 host=span(s,'// C8 full-A/full-B L1 frame','// Exact supplied C13 geometry')
 call='''        const auto fullInputs=MakeC8FullInputsFrame(s,p);
        if(fullInputs.workers) {
            bmmms_tt_manual_frame<T,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,fullInputs);
            return;
        }
'''
 assert s.count(call)==1 and s.replace(e,old,1).replace(host,'',1).replace(call,'',1)==source('7492776')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e,host

def producer(s,e):
 f=cube(s,e).split('void Run(uint32_t M,uint32_t N,uint32_t K,')[0]
 f=f.replace('uint32_t block=0;', 'bool fullB=false;uint32_t block=0;')
 f=f.replace('if(p==TPosition::B1){mem=', 'if(p==TPosition::B1&&!fullB){mem=')
 return f+(ROOT/'tests/cpu/c8_full_inputs_cube.cpp.in').read_text()

def consumer(s,e):
 token='template<typename T,bool FULL_B=false>\n__schedmode__(1)'
 f=vector(s,e.replace(token,'template<typename T>\n__schedmode__(1)',1))
 f=f.replace('template<typename T>\n__schedmode__(1)',token,1)
 f=f[:f.index('void Run(uint32_t M,uint32_t N,uint32_t BM,')]
 driver=(ROOT/'tests/cpu/tt_manual_frame_vector.cpp.in').read_text()
 driver=driver.replace('uint32_t mode){', 'uint32_t mode,bool full){',1)
 driver=driver.replace('  bmmms_tt_manual_frame<int16_t>(nullptr,nullptr,data.scratch.data(),data.output.data(),s);',
  '  if(full)bmmms_tt_manual_frame<int16_t,true>(nullptr,nullptr,data.scratch.data(),data.output.data(),s);\n  else bmmms_tt_manual_frame<int16_t>(nullptr,nullptr,data.scratch.data(),data.output.data(),s);')
 driver=driver[:driver.index('int main()')]+'''int main(){unsigned count=0;
 for(auto v:std::vector<std::vector<uint32_t>>{{129,257,3},{129,129,20},{1025,1031,20},
   {1025,1031,8},{1025,1031,32}})for(bool full:{false,true})for(bool neg:{false,true})for(uint32_t mode=0;mode<3;++mode){
  Run(v[0],v[1],128,full?112:128,v[2],neg,mode,full);++count;
 }
 std::cout<<count<<" threaded actual AIV groups: N112 full/tail DMA, three FIFO priorities, destructive ring release, unique original partial/y writers, MaxN then SumM PASS\\n";
}
'''
 return f+driver

def main():
 s=(ROOT/'kernel.asc').read_text();e,host=scope(s)
 print('Whole retained-parent inverse/protected7 PASS; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plan=span(s,'struct Plan {','// Select only an already complete TF batch')
 fits=span(s,'// Reuse UB only after','// C8 full-A/full-B L1 frame')
 header=e[:e.index('template<typename T>')]
 h='#include <cstring>\n'+stub+shapes+header+plan+fits+host+(ROOT/'tests/cpu/c8_full_inputs_host.cpp.in').read_text()
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c8-full-inputs-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=240)
   if bad:assert r.returncode!=0,'missed negative control '+name
   else:r.check_returncode()
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
  c=producer(s,e);run('cube',c)
  for name,line in [('B1-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),
   ('A1-reader','            AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(2);'),
   ('B-ready','                AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(ps);'),
   ('A-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2);cachedM=mt;'),
   ('L0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(bs);'),
   ('C-reader','            if(k0==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);'),
   ('full-K-fix','        AscendC::WaitFlag<AscendC::HardEvent::M_FIX>(cs);')]:
   replacement='            cachedM=mt;' if name=='A-ready' else ''
   unsafe=c.replace(line,replacement);assert unsafe!=c;run('no-'+name,unsafe,True,['-DNEGATIVE_CONTROL'])
  print('Seven live Cube readiness/last-reader/full-K controls rejected PASS',flush=True)
  v=consumer(s,e);run('vector',v)
  for name,line in [('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);'),
   ('row-reader','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(slot);'),
   ('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);'),
   ('partial-ready','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(slot);'),
   ('barrier','    AscendC::SyncAll<true>();'),
   ('final-copy-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();'),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();')]:
   unsafe=v.replace(line,'');assert unsafe!=v;run('no-'+name,unsafe,True)
  unsafe=v.replace('uint64_t(n-64),rows,rp','uint64_t(64),rows,rp');assert unsafe!=v;run('no-N-mask',unsafe,True)
  print('Eight live AIV handoff/barrier/completion/N-mask controls rejected PASS',flush=True)
 print('CPU integers/synthetic companions only; native CANN/BF16 precision/latency PENDING.')
if __name__=='__main__':main()
