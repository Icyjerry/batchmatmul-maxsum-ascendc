#!/usr/bin/env python3
"""Actual phased-A producer with per-byte ND2NZ readiness and live operands.

Integer CPU arithmetic and synthetic consumer credits, not CANN/BF16/timing.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_tt_manual_frame import cube
ROOT=Path(__file__).resolve().parents[1]
OLD_CALL='''        if(frame.workers) {
            bmmms_tt_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);
            return;
        }'''
NEW_CALL='''        if(frame.workers) {
            if(s.m==1025 && s.n==1031 && s.k==1032 && frame.bm==128 && frame.bn==128 &&
               frame.packageK==384 && frame.nTiles==9)
                bmmms_tt_manual_frame<T,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);
            else bmmms_tt_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);
            return;
        }'''
def scope(s):
 e=span(s,'// Same TT tile/package stream','// All N-tile partials are ready')
 old=span(source('7492776'),'// Same TT tile/package stream','// All N-tile partials are ready')
 assert s.count(NEW_CALL)==1 and s.replace(e,old,1).replace(NEW_CALL,OLD_CALL,1)==source('7492776')
 assert e[e.index('#else\n    const uint32_t halfM='):]==old[old.index('#else\n    const uint32_t halfM='):]
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e

def producer(s,e):
 f=cube(s,e).split('void Run(uint32_t M,uint32_t N,uint32_t K,')[0]
 # One A1 tensor has three non-overlapping pending regions. A whole-buffer
 # pending boolean would either serialize them or wrongly publish all at once.
 f=f.replace('bool pending=false;Storage(size_t n,TPosition p):bytes(n,0x77),pos(p){}',
  'bool pending=false;uint32_t pendingCopies=0;std::vector<uint8_t> busy;Storage(size_t n,TPosition p):bytes(n,0x77),pos(p),busy(n,0){}')
 assert 'pendingCopies=0' in f
 a=f.index('template<HardEvent E>void SetFlag');b=f.index('struct Nd2NzParams',a)
 f=f[:a]+'''template<HardEvent E>void SetFlag(int i){
 auto flag=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};
 if(E==HardEvent::MTE2_MTE1)dma.push_back({nullptr,flag});
 else if(E==HardEvent::MTE1_MTE2||E==HardEvent::MTE1_M)mte1.push_back(flag);
 else if(E==HardEvent::M_MTE1||E==HardEvent::M_FIX)mac.push_back(flag);
 else if(E==HardEvent::FIX_M)fix.push_back(flag);else assert(false);
}
void FlushOneDMA(){assert(!dma.empty());auto x=dma.front();dma.pop_front();x.op();}
template<HardEvent E>void WaitFlag(int i){
 while(!st.events[std::make_pair(int(E),i)]){
  if(E==HardEvent::MTE2_MTE1)FlushOneDMA();
  else if(E==HardEvent::MTE1_MTE2||E==HardEvent::MTE1_M)FlushCommands(mte1);
  else if(E==HardEvent::M_MTE1||E==HardEvent::M_FIX)FlushCommands(mac);
  else if(E==HardEvent::FIX_M)FlushCommands(fix);else assert(false);
 }
 assert(st.events[std::make_pair(int(E),i)]--==1);
 if(E==HardEvent::FIX_M)st.lastCWait=i;
}
template<int P>void PipeBarrier(){
 if(P==PIPE_ALL)assert(dma.empty()&&mte1.empty()&&mac.empty()&&fix.empty());
 else if(P==PIPE_M)while(!mac.empty())FlushCommands(mac);
}
template<int Mode>void CrossCoreWaitFlag(int id){
 assert(Mode==2&&id>=4&&id<6);while(st.cross[id-4]==0)FlushCommands(fix);assert(st.cross[id-4]--==1);
}
template<int Mode,int P>void CrossCoreSetFlag(int id){
 assert(Mode==2&&P==PIPE_FIX&&id>=0&&id<2);
 fix.push_back([=]{assert(st.cross[id]++==0);});
 if(eagerFix)while(!fix.empty())FlushCommands(fix);
}
'''+f[b:]
 a=f.index('template<class T>void DataCopy(LocalTensor<T>');b=f.index('struct LoadData2DParams',a)
 f=f[:a]+'''template<class T>T Read(LocalTensor<T> src,size_t i){
 size_t start=src.offset+i*sizeof(T);assert(start+sizeof(T)<=src.mem->busy.size());
 for(size_t j=0;j<sizeof(T);++j)assert(!src.mem->busy[start+j]&&"read before this A/B region ready");
 return src.at(i);
}
template<class T>void DataCopy(LocalTensor<T> dst,GlobalTensor<T> src,Nd2NzParams p){
 assert(p.ndNum==1&&p.dstNzNStride==1&&p.dstNzC0Stride%16==0);
 uint32_t dp=(p.dValue+15)/16*16;
 for(uint32_t r=0;r<p.nValue;++r)for(uint32_t c=0;c<dp;++c){
  size_t i=(c/16)*p.dstNzC0Stride*16+r*16+c%16,start=dst.offset+i*sizeof(T);
  assert(start+sizeof(T)<=dst.mem->busy.size());
  for(size_t j=0;j<sizeof(T);++j){assert(!dst.mem->busy[start+j]&&"overlapping DMA regions");dst.mem->busy[start+j]=1;}
 }
 ++dst.mem->pendingCopies;dst.mem->pending=true;
 dma.push_back({dst.mem,[=]{
  for(uint32_t r=0;r<p.nValue;++r)for(uint32_t c=0;c<dp;++c){
   size_t i=(c/16)*p.dstNzC0Stride*16+r*16+c%16;dst.at(i)=c<p.dValue?src.at(r*p.srcDValue+c):0;
   for(size_t j=0;j<sizeof(T);++j){auto& busy=dst.mem->busy[dst.offset+i*sizeof(T)+j];assert(busy==1);busy=0;}
  }
  assert(dst.mem->pendingCopies);dst.mem->pending=--dst.mem->pendingCopies!=0;
 }});
 (src.isA?st.aReads:st.bReads)+=p.nValue*p.dValue;++(src.isA?st.aCopies:st.bCopies);
}
'''+f[b:]
 # Load2D/Load3D inspect exactly the source bytes read, including padded values;
 # unrelated pending A regions must not implicitly block a ready K region.
 a=f.index('template<class T>void LoadData(');b=f.index('struct MmadParams',a)
 l=f[a:b].replace('    assert(!src.mem->pending);','').replace('&&!src.mem->pending','')
 l=l.replace('src.at(', 'Read(src,')
 f=f[:a]+l+f[b:]
 f=f.replace('if(x.mem->pos==TPosition::A1)', 'if(x.mem&&x.mem->pos==TPosition::A1)')
 return f+(ROOT/'tests/cpu/c8_phased_a_cube.cpp.in').read_text()

def main():
 s=(ROOT/'kernel.asc').read_text();e=scope(s)
 print('Whole retained-parent inverse, unchanged AIV/plan/GM/protected7 PASS; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plan=span(s,'struct Plan {','// Select only an already complete TF batch')
 fits=span(s,'// Reuse UB only after','// Exact supplied C13 geometry')
 header=e[:e.index('template<typename T>')]
 condition=NEW_CALL[NEW_CALL.index('            if(')+15:NEW_CALL.index(')\n                bmmms')]
 select='bool SelectPhased(const Shape& s,const Plan& p){const auto frame=MakeTTManualFrame(s,p);if(!frame.workers)return false;return '+condition+';}'
 h='#include <cstring>\n'+stub+shapes+header+plan+fits+select+(ROOT/'tests/cpu/c8_phased_a_host.cpp.in').read_text()
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c8-phased-a-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=240)
   if bad:assert r.returncode!=0,'missed control '+name
   else:r.check_returncode()
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
  c=producer(s,e);run('cube',c)
  for name,line,replacement in [
   ('A-first-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2);cachedM=mt;','            cachedM=mt;'),
   ('A-later-ready','                AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2+aReadyPhase);',''),
   ('B-ready','                AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(ps);',''),
   ('A-reader','            AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(2);',''),
   ('B-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);',''),
   ('L0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(bs);',''),
   ('C-reader','            if(k0==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);',''),
   ('full-K','        AscendC::WaitFlag<AscendC::HardEvent::M_FIX>(cs);',''),
   ('NZ-pitch','cp.dstNzC0Stride=(s.k+15)/16*16;cp.dstNzNStride=1;','cp.dstNzC0Stride=(count+15)/16*16;cp.dstNzNStride=1;')]:
   unsafe=c.replace(line,replacement);assert unsafe!=c;run('no-'+name,unsafe,True,['-DNEGATIVE_CONTROL'])
  print('Nine per-region ready/pitch and live operand/final-K controls rejected PASS',flush=True)
 print('CPU integers/synthetic consumer only; phased ordering permits overlap, not measured device time. Native CANN/BF16 precision/latency PENDING.')
if __name__=='__main__':main()
