#!/usr/bin/env python3
"""Actual small TT packed frame: typed bounds, delayed DMA/store and FP64 oracle."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=(ROOT/'kernel.asc').read_text();parent=source('1734f16')
 entry=span(s,'// Small TT: one shared Cast','// Small GEMMs avoid the Cube server/client protocol.')
 host=span(s,'// Specialize the front small Vector route','template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>\ninline void LaunchTinyK')
 call='''    const auto packedTT=MakeTinyTTPackedFrame(s,p);
    if(packedTT.workers) {
        bmmms_tiny_tt_packed_frame<T><<<packedTT.workers,nullptr,stream>>>(x1,x2,y,packedTT);
        return;
    }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==parent
 launch=span(s,'inline void Launch(GM_ADDR','    if(p.schedule.dual==28)')
 assert launch.index(call)<launch.index('const uint32_t vectorRows=SmallVectorK256Rows(s);')
 buf=span(s,'__aicore__ inline AscendC::LocalTensor<uint8_t> TinyUbBuffer','// Match DAV2201 CreateVecIndex')
 index=span(s,'__aicore__ inline void SmallVectorManualIndex','struct SmallVectorManualShape')
 f=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
 f=f.replace('MTE2_V,V_MTE3,S_V','MTE2_V,V_MTE3,S_V,V_MTE2,MTE3_V')
 a=f.index('template<HardEvent E>void SetFlag');b=f.index('\nuint32_t block',a)
 f=f[:a]+'''template<HardEvent E>void SetFlag(int id){
 assert(id==0);
 if(E==HardEvent::MTE3_V){outDma.push_back([]{assert(flags[E]++==0);});return;}
 if(E==HardEvent::MTE2_V)Flush(dma);assert(flags[E]++==0);
}
template<HardEvent E>void WaitFlag(int id){
 if(E==HardEvent::MTE3_V)Flush(outDma);
 assert(id==0&&flags[E]--==1);
}
void SetAtomicNone(){}void SetMaskNorm(){}void ResetMask(){}
int encoding=0;
float Decode(int16_t v){
 uint16_t u=uint16_t(v);
 if(encoding==0)return float(v);
 if(encoding==2){uint32_t bits=uint32_t(u)<<16;float f;std::memcpy(&f,&bits,4);return f;}
 uint32_t e=(u>>10)&31,m=u&1023;assert(e!=31);
 float f=e?std::ldexp(float(1024+m),int(e)-25):std::ldexp(float(m),-24);
 return u&32768?-f:f;
}
'''+f[b:]
 f=f.replace('float(src.read(i))','Decode(int16_t(src.read(i)))')
 f=f.replace('// INSERT_KERNELS',buf+index+entry)
 f+=(ROOT/'tests/cpu/tiny_tt_packed_frame.cpp.in').read_text()
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plans=span(s,'struct Plan {','// Select only an already complete TF batch')
 header=entry[:entry.index('template<typename T>')]
 front=span(s,'inline uint32_t SmallVectorK256Rows','// Specialize the front small Vector route')
 h=stub+'\n#include <cstring>\n'+shapes+header+plans+front+host+(ROOT/'tests/cpu/tiny_tt_packed_host.cpp.in').read_text()
 print('Three additions restore whole passed parent; SHA',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tiny-tt-packed-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed: '+name
   else:r.check_returncode()
  run('frame',f)
  controls=[
   ('input-ready','        AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(0);\n        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);',''),
   ('output-retirement','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(0);',''),
   ('K-padding','        AscendC::Duplicate(prod,0.0f,products);',''),
   ('K-complete','for(uint32_t g=1;g<groups;++g)','for(uint32_t g=1;g<1;++g)'),
   ('N-tail','uint64_t(s.n),countM,2','uint64_t(np),countM,2'),
   ('query-offset','index.ReinterpretCast<uint32_t>(),m*4,s.k','index.ReinterpretCast<uint32_t>(),0,s.k'),
   ('terminal','    AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(0);AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(0);\n    AscendC::PipeBarrier<PIPE_ALL>();','')]
  for name,old,new in controls:
   unsafe=f.replace(old,new);assert unsafe!=f;run('no-'+name,unsafe,True)
  print('Seven readiness/retirement/padding/K/N/layout/completion controls rejected PASS',flush=True)
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CPU Vector arithmetic synchronous; input/output delayed. CANN9/NPU precision/latency PENDING.')
if __name__=='__main__':main()
