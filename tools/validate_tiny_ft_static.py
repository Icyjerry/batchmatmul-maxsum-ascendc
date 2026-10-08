#!/usr/bin/env python3
"""Actual constant FT entry: typed bounds, queued engines, FP64 golden and host guards."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=(ROOT/'kernel.asc').read_text();parent=source('1734f16')
 entry=span(s,'// Small FT: static UB addresses','// Each AIV owns complete batch pairs; only the last group can be shorter.')
 host=span(s,'// Constant FT frame only replaces','template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>\ninline void LaunchTinyK')
 call='''    if(TinyFTStaticFits(s,p)) {
        if(s.n==8)LaunchTinyFTStaticM<T,8>(x1,x2,y,s,stream);
        else LaunchTinyFTStaticM<T,16>(x1,x2,y,s,stream);
        return;
    }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==parent
 assert 'TPipe' not in entry
 for m in range(4,8):assert f'case {m}:LaunchTinyFTStaticK<T,{m},NP>' in host
 for k in [32,40,48,56]:assert f'case {k}:bmmms_tiny_ft_static<T,M,NP,{k}>' in host
 f=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
 f=f.replace('std::deque<std::function<void()>> dma,outDma;','std::deque<std::function<void()>> dma,outDma,vec;')
 f=f.replace('size_t manualBytes=0;','size_t manualBytes=0;std::vector<uint8_t> defined;')
 f=f.replace('std::memcpy(&v,mem->data()+offset+i*sizeof(T),sizeof(T));return v;',
 '''if(mem==ub)for(size_t j=0;j<sizeof(T);++j)assert(defined.at(offset+i*sizeof(T)+j));
        std::memcpy(&v,mem->data()+offset+i*sizeof(T),sizeof(T));return v;''')
 f=f.replace('std::memcpy(mem->data()+offset+i*sizeof(T),&v,sizeof(T));}',
 '''std::memcpy(mem->data()+offset+i*sizeof(T),&v,sizeof(T));
        if(mem==ub)for(size_t j=0;j<sizeof(T);++j)defined.at(offset+i*sizeof(T)+j)=1;}''')
 a=f.index('template<HardEvent E>void SetFlag');b=f.index('\nuint32_t block',a)
 f=f[:a]+'''template<HardEvent E>void SetFlag(int id){
 assert(id==0);auto mark=[] {assert(flags[E]++==0);};
 if(E==HardEvent::V_MTE3)vec.push_back(mark);else {if(E==HardEvent::MTE2_V)Flush(dma);mark();}
}
template<HardEvent E>void WaitFlag(int id){if(E==HardEvent::V_MTE3)Flush(vec);assert(id==0&&flags[E]--==1);}
int encoding=0;
float Decode(int16_t v){
 if(!encoding)return float(v);uint16_t u=uint16_t(v);
 uint32_t e=(u>>10)&31,m=u&1023;assert(e!=31);
 float x=e?std::ldexp(float(1024+m),int(e)-25):std::ldexp(float(m),-24);
 return u&32768?-x:x;
}
'''+f[b:]
 f=f.replace('float(src.read(i))','Decode(int16_t(src.read(i)))')
 f=f.replace('template<int P> void PipeBarrier(){if(P==PIPE_ALL){Flush(dma);Flush(outDma);}}',
 'template<int P> void PipeBarrier(){if(P==PIPE_ALL){Flush(outDma);Flush(vec);Flush(dma);}else Flush(vec);}')
 for token in ['void Cast(', 'void Duplicate(', 'void Mul(', 'void WholeReduceSum(', 'void WholeReduceMax(']:
  pos=0
  while True:
   a=f.find(token,pos)
   if a<0:break
   a=f.index('{',a);depth=1;b=a+1
   while depth:
    depth+=(f[b]=='{')-(f[b]=='}');b+=1
   body=f[a+1:b-1];new='{vec.push_back([=]{'+body+'});}'
   f=f[:a]+new+f[b:];pos=a+len(new)
 buf=span(s,'__aicore__ inline AscendC::LocalTensor<uint8_t> TinyUbBuffer','// Match DAV2201 CreateVecIndex')
 f=f.replace('// INSERT_KERNELS',buf+entry)+(ROOT/'tests/cpu/tiny_ft_static.cpp.in').read_text()
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plans=span(s,'struct Plan {','// Select only an already complete TF batch')
 guard=host[:host.index('template<typename T,uint32_t M,uint32_t NP>')]
 h='#include <cstring>\n'+stub+shapes+plans+guard+(ROOT/'tests/cpu/tiny_ft_static_host.cpp.in').read_text()
 print('Three additions restore whole parent1734f16; SHA',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tiny-ft-static-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed:'+name
   else:r.check_returncode()
  run('entry',f)
  changes=[
   ('input-ready','    AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(0);\n    AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);',''),
   ('output-ready','    AscendC::SetFlag<AscendC::HardEvent::V_MTE3>(0);\n    AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(0);',''),
   ('completion','    AscendC::PipeBarrier<PIPE_ALL>();',''),
   ('K-complete','uint64_t(K),s.n,1','uint64_t(K-8),s.n,1'),
   ('dot-repeat','uint64_t(K),s.n,1','uint64_t(K),NP,1'),
   ('N-mask','uint64_t(s.n),M,1','uint64_t(NP),M,1'),
   ('M-compact','uint64_t(M),1,1,1,8','uint64_t(M+1),1,1,1,8'),
   ('batch-offset','+int64_t(batch)*s.n*K','+int64_t(0)*s.n*K')]
  for name,old,new in changes:
   unsafe=f.replace(old,new);assert unsafe!=f;run('no-'+name,unsafe,True)
  print('Eight queued readiness/completion/defined-dot/fullK/validN/compactM/batch controls rejected PASS',flush=True)
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CPU typed/FP32/queued-engine model only; CANN9 compile/native precision/latency PENDING.')
if __name__=='__main__':main()
