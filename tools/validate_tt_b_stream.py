#!/usr/bin/env python3
"""Actual TT package-stream producer with independent NZ/live operand models.

Delayed MTE2, MTE1 and M queues enforce explicit B1 buffer reuse credits.
Native A1 TQue completion is abstracted; no hardware timing/FP16 precision.
"""
from pathlib import Path
import subprocess, tempfile, shutil, hashlib

ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'tools/validate_tt_contiguous.py').read_text().split('def main():')[0]
text=text.replace("'a05035e:kernel.asc'", "'4ac80c9:kernel.asc'")
a=text.index('v=vector_body(src)');b=text.index('legacy_model=',a)
text=text[:a]+"assert vector_body(src)==vector_body(parent_src), 'Vector unchanged from passing C9+TT'\n"+text[b:]
ns={'__file__':str(ROOT/'tools/validate_tt_contiguous.py')}
exec(text,ns)
src=ns['src'];parent_src=ns['parent_src']
model=ns['model']
model=model.replace('negativeInput=neg;s.window=1;', '''negativeInput=neg;s.window=1;
 const uint32_t bk=s.baseN==256?64:128;
 const uint32_t kp=(s.k+15)/16*16;
 const uint64_t available=(512*1024-2ULL*s.baseM*kp)/(4ULL*s.baseN);
 s.kChunk=std::min<uint64_t>((s.k+bk-1)/bk*bk,available/bk*bk);assert(s.kChunk>=bk);''')
model=model.replace('st.bCopies==st.mmads', 'st.bCopies==uint64_t(end-first)*((s.k+s.kChunk-1)/s.kChunk)')
model=model.replace('std::map<std::pair<int,int>,int> events;', 'uint64_t bAhead=0;std::map<std::pair<int,int>,int> events;')
model=model.replace('    ++(src.isA?st.aCopies:st.bCopies);', '''    ++(src.isA?st.aCopies:st.bCopies);
    if(!src.isA&&st.fixes<st.expected.size()){
      auto e=st.expected[st.fixes];int64_t batch=src.offset/(st.s.n*st.s.k),n0=src.offset%(st.s.n*st.s.k)/st.s.k;
      if(batch!=e.b||n0!=e.n)++st.bAhead;
    }''')
model=model.replace('assert(AscendC::dma.empty()&&st.fixes', 'if(end-first>=2)assert(st.bAhead>0);assert(AscendC::dma.empty()&&st.fixes')
model=model.replace('balanced unique full tile cover, delayed NZ input, cached A release/refresh,',
 'cross-tile B prefetch, balanced unique full tile cover, adaptive B packages, cached A release/refresh,')

def events(code):
    # Manual B1's two non-overlapping slots share one TBuf. Track DMA spans,
    # rather than incorrectly treating the whole allocation as one busy slot.
    code=code.replace('bool pending=false;', 'unsigned pending=0;std::map<size_t,size_t> writes;')
    code=code.replace('x.mem->pending=false;', '--x.mem->pending;')
    code=code.replace('    assert(!dst.mem->pending);dst.mem->pending=true;', '''
    const size_t bytes=size_t((p.dValue+15)/16*16)*p.dstNzC0Stride*sizeof(T);
    for(auto w:dst.mem->writes)assert(dst.offset+bytes<=w.first||w.first+w.second<=dst.offset);
    dst.mem->writes[dst.offset]=bytes;++dst.mem->pending;''')
    code=code.replace('    }});', '    dst.mem->writes.erase(dst.offset);}});')
    code=code.replace('    assert(!src.mem->pending);', '''
    for(uint32_t r=0;r<p.repeatTimes;++r)for(auto w:src.mem->writes){
      size_t first=src.offset+size_t(r)*p.srcStride*256*sizeof(T),bytes=256*sizeof(T);
      assert(first+bytes<=w.first||w.first+w.second<=first);
    }''')
    code=code.replace('panelL1K=0,window=1;', 'panelL1K=0,window=1,kChunk=0;')
    code=code.replace('MTE2_MTE1};','MTE2_MTE1,MTE1_MTE2};').replace('next[5]', 'next[6]')
    # Immediate-model ready waits complete every preceding MTE2 instruction.
    code=code.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);',
      '    if(E==HardEvent::MTE2_MTE1)while(!dma.empty())Flush(dma.front().mem);\n    assert(st.events[std::make_pair(int(E),i)]--==1);')
    return code

model=model.replace(' const uint64_t bk=s.baseN==256?64:128;','')
model=events(model)
legacy_model=events(ns['legacy_model'])
hostmain=ns['hostmain'].replace('(x.dual==1||x.dual==29)', 'x.dual==33')
hostmain=hostmain.replace('halfM+=y.baseM<x.baseM;', 'halfM+=y.kChunk>(y.baseN==256?64u:128u);')
hostmain=hostmain.replace('uint64_t bm=y.baseM,bn=y.baseN,bk=bn==256?64:128,kp=Ceil(k,16)*16,chunks=Ceil(m,bm/2);',
 '''uint64_t bm=y.baseM,bn=y.baseN,bk=bn==256?64:128,kp=Ceil(k,16)*16,chunks=Ceil(m,bm/2);
   assert(y.kChunk>=bk&&y.kChunk%bk==0&&y.kChunk<=Ceil(k,bk)*bk);
   assert(2*bm*kp+4*bn*y.kChunk<=std::min<uint64_t>(hw->l1,512*1024));''')
hostmain=hostmain.replace('y.dual=x.dual;', 'y.kChunk=x.kChunk;y.dual=x.dual;')
hostmain=hostmain.replace(' contiguous selected, ', ' package streams selected, ').replace(' half-M for actual L1 capacity:', ' enlarged B packages:')
stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
shapes=ns['shapes'];host=ns['host'];parent=ns['parent']
hostmodel='#include <cstring>\n'+stub+shapes+'namespace Parent{'+parent+'}\nnamespace Candidate{'+host+'}\n'+hostmain

# Delayed engine commands read live L1/L0/C memory, never snapshot operands.
delayed_model=model
delayed_model=delayed_model.replace('namespace AscendC {',
 'std::deque<std::function<void()>> mte1,mac;\nnamespace AscendC {',1)
delayed_model=delayed_model.replace('--x.mem->pending;', 'if(x.mem)--x.mem->pending;')
delayed_model=delayed_model.replace('template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}', '''
template<HardEvent E>void SetFlag(int i){
 auto f=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};
 if(E==HardEvent::M_MTE1)mac.push_back(f);
 else if(E==HardEvent::MTE1_M||E==HardEvent::MTE1_MTE2)mte1.push_back(f);
 else if(E==HardEvent::MTE2_MTE1)dma.push_back({nullptr,f});
 else f();
}''')
delayed_model=delayed_model.replace('    if(E==HardEvent::MTE2_MTE1)while(!dma.empty())Flush(dma.front().mem);', '''
    while(st.events[std::make_pair(int(E),i)]==0){
     if(E==HardEvent::MTE2_MTE1){assert(!dma.empty());auto x=dma.front();dma.pop_front();x.op();if(x.mem)--x.mem->pending;}
     else if(E==HardEvent::MTE1_M||E==HardEvent::MTE1_MTE2){assert(!mte1.empty());auto f=mte1.front();mte1.pop_front();f();}
     else if(E==HardEvent::M_MTE1){assert(!mac.empty());auto f=mac.front();mac.pop_front();f();}
     else assert(false);
    }''')
delayed_model=delayed_model.replace('for(auto x:dma)if(x.mem->pos', 'for(auto x:dma)if(x.mem&&x.mem->pos')
def defer(code,start,end,loop):
    a=code.index(start);b=code.index(end,a);part=code[a:b]
    part=part.replace(loop,'    mte1.push_back([=]{\n'+loop,1)
    part=part.rsplit('}\n',1)[0]+'    });\n}\n'
    return code[:a]+part+code[b:]
delayed_model=defer(delayed_model,'template<class T>void LoadData(', 'template<class T>struct LoadData3DParamsV2',
 '    for(uint32_t r=0;r<p.repeatTimes;++r)')
delayed_model=defer(delayed_model,'void LoadData(LocalTensor<half>', 'struct MmadParams',
 '    for(uint32_t m=0;m<rows;++m)')
a=delayed_model.index('template<class T>void Mmad(');b=delayed_model.index('struct FixpipeParamsV220',a)
mm=delayed_model[a:b].replace('    for(uint32_t m=0;m<p.m;++m)', '    mac.push_back([=]{\n    for(uint32_t m=0;m<p.m;++m)',1)
mm=mm.rsplit('}\n',1)[0]+'    });\n}\n'
delayed_model=delayed_model[:a]+mm+delayed_model[b:]
delayed_model=delayed_model.replace('template<AscendC::HardEvent E>void Fence(){}', '''
template<AscendC::HardEvent E>void Fence(){
 if(E==AscendC::HardEvent::M_FIX)while(!mac.empty()){auto f=mac.front();mac.pop_front();f();}
}''')
delayed_model=delayed_model.replace('assert(AscendC::dma.empty()&&st.fixes', 'assert(mac.empty()&&mte1.empty());assert(AscendC::dma.empty()&&st.fixes')

# The passed C9 implementation and every Vector producer/consumer are preserved.
for begin,end in [('template<typename T,bool TX1,bool PAD_MN>\n__aicore__ inline void Case9CopyAPackage','// Isolated case12'),
                  ('struct Case9PackagePlan','using CacheKey ='),('template <typename T>\ninline void Launch(', 'extern "C"')]:
    assert begin in src and end in src[src.index(begin):], 'missing region'
    a=src.index(begin);b=src.index(end,a);x=parent_src.index(begin);y=parent_src.index(end,x)
    assert src[a:b]==parent_src[x:y], 'changes outside TT stream'

# Alternate schedule: MTE2 completes immediately at issue, while MTE1 stays
# deferred. This exposes overwrites that a lazy DMA schedule could conceal.
eager_model=delayed_model.replace('    ++(src.isA?st.aCopies:st.bCopies);', '''
    ++(src.isA?st.aCopies:st.bCopies);
    while(!dma.empty()){auto x=dma.front();dma.pop_front();x.op();if(x.mem)--x.mem->pending;}
''')
guard='    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(free);'
assert eager_model.count(guard)==1
unsafe_model=eager_model.replace(guard, '// Negative control: illegally omit last-reader credit.')

def main():
    compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
    print('Kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
    with tempfile.TemporaryDirectory(prefix='bmmms-tt-stream-') as d:
        for name,code,flags in [('cube',model,[]),('delayed-mte1-mmad',delayed_model,[]),('eager-mte2',eager_model,[]),
                                ('legacy',legacy_model,[]),('host',hostmodel,[]),('host-tuning',hostmodel,['-DBMMMS_TUNING'])]:
            cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name;cpp.write_text(code)
            subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
        cpp,exe=Path(d)/'missing-credit.cpp',Path(d)/'missing-credit'
        cpp.write_text(unsafe_model)
        subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        result=subprocess.run([str(exe)],capture_output=True,text=True)
        assert result.returncode!=0 and 'Assertion failed' in result.stderr, 'negative control must reject missing B1 last-reader credit'
        print('Missing B1 last-reader wait correctly rejected by adversarial schedule PASS')
    print('CPU model only; CANN9 compilation/NPU accuracy/latency PENDING.')

if __name__=='__main__':main()
