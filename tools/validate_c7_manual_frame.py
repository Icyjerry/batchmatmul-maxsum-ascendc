#!/usr/bin/env python3
"""Extract the actual manual frame. Integer CPU models, not CANN/NPU timing.

Cube operands use physical NZ/ZZ/ZN and deferred live MMAD reads; Vector has
three queued engines and destructive GM credit reuse. Load3D and Fixpipe remain
synchronous; native FP16 rounding and hardware configuration are not modeled.
"""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
def span(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
def source(rev):return subprocess.check_output(['git','show',rev+':kernel.asc'],cwd=ROOT,text=True)
def scope(s):
 parent=source('0fe38f0')
 entry=span(s,'// Full small TF inputs use one physical frame','template<typename T>\n__aicore__ inline void ManualFullMReadB')
 host=span(s,'// Select only an already complete TF batch','using CacheKey =')
 call='''    const auto c7=MakeC7ManualFrame(s,p);
    if(c7.workers) {
        bmmms_c7_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,c7);
        return;
    }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==parent
 assert 'TPipe' not in entry[entry.index('struct C7KernelShape'):]
 return entry,host

def vector(s,entry):
 f=(ROOT/'tests/cpu/c7_lean_vector_model.cpp.in').read_text()
 f=f.replace('#define __gm__','#define __global__\n#define __schedmode__(x)\n#define __mix__(...)\n#define __gm__')
 f=f.replace('constexpr int PIPE_MTE2=0,PIPE_V=1,PIPE_MTE3=2;','constexpr int PIPE_MTE2=0,PIPE_V=1,PIPE_MTE3=2,PIPE_ALL=3;')
 f=f.replace('size_t allocated=0;', 'size_t ringBase=0,allocated=0;std::vector<std::pair<size_t,size_t>> ranges;')
 f=f.replace(' LocalTensor operator[]', ''' LocalTensor()=default;
 LocalTensor(std::shared_ptr<Storage> p,size_t o):mem(p),offset(o){}
 LocalTensor(TPosition p,size_t bytes,size_t elems){
  assert(bytes%32==0 && bytes+elems*4<=192*1024);
  for(auto r:st.ranges)assert(bytes+elems*4<=r.first||bytes>=r.second);
  st.ranges.push_back({bytes,bytes+elems*4});++st.allocs;st.allocated+=elems*4;
  mem=std::make_shared<Storage>(elems,p);
 }
 LocalTensor operator[]''')
 f=f.replace('assert(ptr==st.output->data()+8);mem=st.output;offset=8;', '''if(ptr==st.output->data()+8){mem=st.output;offset=8;}
  else {assert(ptr==st.ring->data()+st.ringBase);mem=st.ring;offset=st.ringBase;}''')
 f=f.replace('st.ring->begin()+slot*','st.ring->begin()+st.ringBase+slot*')
 f=f.replace('src.offset==((st.issued-1)&1)*','src.offset==st.ringBase+((st.issued-1)&1)*')
 f=f.replace('template<int P>void PipeBarrier(){assert(P==PIPE_V);}', 'template<int P>void PipeBarrier(){if(P==PIPE_ALL)st.Drain();else assert(P==PIPE_V);}')
 a=f.index('template<AscendC::HardEvent E>void Fence()');b=f.index('// INSERT_CONSUMER',a)
 f=f[:a]+'''namespace AscendC {
uint32_t GetBlockIdx(){return st.worker*2+st.sub;}
void SetAtomicNone(){}void SetMaskNorm(){}void ResetMask(){}
template<HardEvent E>void SetFlag(int id){
 assert(id==0);const int event=int(E);
 const int from=E==HardEvent::V_MTE2||E==HardEvent::V_MTE3?PIPE_V:E==HardEvent::MTE2_V?PIPE_MTE2:PIPE_MTE3;
 st.Push(from,[=]{assert(st.events[event]++==0);});
}
template<HardEvent E>void WaitFlag(int id){
 assert(id==0);const int event=int(E);
 const int to=E==HardEvent::V_MTE2?PIPE_MTE2:E==HardEvent::V_MTE3?PIPE_MTE3:PIPE_V;
 st.queues[to].push_back({[=]{return st.events[event]>0;},[=]{--st.events[event];}});
}
}
template<AscendC::HardEvent E>void Fence(){assert(false);}
'''+f[b:]
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Isolated case6 fast path copied')
 f=f.replace('// INSERT_CONSUMER',fence+entry)
 f=f.replace('  std::vector<float> ring(2*oneC+16,1e30f);', '''  const size_t prefix=(B*s.baseM+127)/128*128;
  st.ringBase=prefix+size_t(worker)*2*oneC;
  std::vector<float> ring(prefix+workers*2*oneC+16,1e30f);''')
 f=f.replace('  AscendC::TPipe pipe;\n  RunSmallFullInputsVector(pipe,{&ring,0},output.data()+8,s,worker,sub);st.Drain();writers=st.writers;', '''  C7KernelShape q{B,M,N,384,s.baseM,s.baseN,workers,80};
  bmmms_c7_manual_frame<int16_t>(nullptr,nullptr,ring.data(),output.data()+8,q);
  // No model destructor may complete manual-frame DMA for the kernel.
  for(auto& engine:st.queues)assert(engine.empty());writers=st.writers;''')
 f=f.replace('st.primes==2','st.primes==(batches?2u:0u)')
 f=f.replace('st.credits[0]==1&&st.credits[1]==1','st.credits[0]==(batches?1:0)&&st.credits[1]==(batches?1:0)')
 f=f.replace('  for(size_t i=2*oneC;i<ring.size();++i)assert(ring[i]==1e30f);', '  for(size_t i=0;i<ring.size();++i)if(i<st.ringBase||i>=st.ringBase+2*oneC)assert(ring[i]==1e30f);')
 return f

def cube(s,entry):
 f=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
 f=f.replace('#define __aicore__','#define __DAV_CUBE__\n#define __global__\n#define __schedmode__(x)\n#define __mix__(...)\n#define __gm__\nusing GM_ADDR=void*;\n#define __aicore__')
 f=f.replace('constexpr int PIPE_MTE2=1,PIPE_M=2,PIPE_FIX=3;','constexpr int PIPE_MTE2=1,PIPE_M=2,PIPE_FIX=3,PIPE_ALL=4;')
 extra='''using TEventID=int;
uint32_t block=0;uint32_t GetBlockIdx(){return block;}
void SetAtomicNone(){}void SetMaskNorm(){}void ResetMask(){}
void SetLoadDataBoundary(uint64_t){}void SetLoadDataPaddingValue(uint64_t){}
std::map<int,std::vector<std::pair<size_t,size_t>>> ranges;
void Claim(TPosition p,size_t start,size_t bytes){
 int bank=p==TPosition::B1?int(TPosition::A1):int(p);
 size_t limit=(p==TPosition::A1||p==TPosition::B1)?512*1024:p==TPosition::CO1?128*1024:64*1024;
 assert(start%32==0&&start+bytes<=limit);
 for(auto r:ranges[bank])assert(start+bytes<=r.first||start>=r.second);
 ranges[bank].push_back({start,start+bytes});
}
std::map<uintptr_t,std::pair<size_t,bool>> registry;
'''
 f=f.replace('template<class T>struct LocalTensor {',extra+'template<class T>struct LocalTensor {')
 f=f.replace('    LocalTensor operator[]', '''    LocalTensor()=default;
    LocalTensor(std::shared_ptr<Storage> p,size_t o):mem(p),offset(o){}
    LocalTensor(TPosition p,size_t start,size_t elements){Claim(p,start,elements*sizeof(T));mem=std::make_shared<Storage>(elements*sizeof(T),p);}
    LocalTensor operator[]''')
 a=f.index('template<class T>struct GlobalTensor');b=f.index('template<TPosition P,int N>struct TQue',a)
 f=f[:a]+'''template<class T>struct GlobalTensor{
 T* data=nullptr;size_t offset=0,count=0;bool isA=false;
 void SetGlobalBuffer(T* p){uintptr_t ptr=reinterpret_cast<uintptr_t>(p);bool found=false;
  for(auto r:registry)if(ptr>=r.first&&ptr<r.first+r.second.first){data=reinterpret_cast<T*>(r.first);offset=(ptr-r.first)/sizeof(T);count=(r.first+r.second.first-ptr)/sizeof(T);isA=r.second.second;found=true;break;}assert(found);
 }
 GlobalTensor operator[](size_t i)const{assert(i<count);return {data,offset+i,count-i,isA};}
 T& at(size_t i)const{assert(i<count);return data[offset+i];}
};
'''+f[b:]
 a=f.index('void LoadData(LocalTensor<half>');b=f.index('struct MmadParams',a)
 load=f[a:b].replace('void LoadData(', 'void LoadA(')
 load+='''void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 if(p.enTranspose){LoadA(dst,src,p);return;}
 assert(dst.mem->pos==TPosition::B2&&src.mem->pos==TPosition::B1&&!src.mem->pending);
 assert(p.l1H==1&&p.l1W%16==0&&p.channelSize%16==0&&p.strideH==1&&p.strideW==1&&p.filterH==1&&p.filterW==1);
 assert(p.dilationFilterH==1&&p.dilationFilterW==1&&p.mStartPt==0&&p.kStartPt%16==0);
 const uint32_t K=p.mExtension,N=p.kExtension;
 assert(K==p.l1W&&N%16==0&&p.kStartPt+N<=p.channelSize);
 for(uint32_t k=0;k<K;++k)for(uint32_t n=0;n<N;++n){
  const uint32_t col=p.kStartPt+n;
  dst.at(((k/16)*(N/16)+n/16)*256+(n%16)*16+k%16)=src.at((col/16)*p.l1W*16+k*16+col%16);
 }
 st.bL0+=uint64_t(K)*N;++st.bLoads;
}
'''
 f=f[:a]+load+f[b:]
 f=f.replace('if(p.cmatrixInitVal) {','if(p.cmatrixInitVal && c.offset%(st.s.baseM*st.s.baseN*4)==0) {')
 f=f.replace('template<int P>void PipeBarrier(){}','template<int P>void PipeBarrier(){if(P==PIPE_ALL)assert(dma.empty());}')
 # Explicit ready event completes both ordered MTE2 copies; no TPipe allocator.
 f=f.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);', '    if(E==HardEvent::MTE2_MTE1)while(!dma.empty())Flush(dma.front().mem);\n    assert(st.events[std::make_pair(int(E),i)]--==1);')
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Isolated case6 fast path copied')
 zero=span(s,'template<typename T>\n__aicore__ inline void ManualZeroNZTail','__aicore__ inline void SmallRowMaxLaneFold')
 trans=span(s,'template<typename T>\n__aicore__ inline void ManualTransposeFullM','// Full small TF inputs use one physical frame')
 f=f.replace('// INSERT_HELPERS',zero+fence+trans+entry)
 f+=(ROOT/'tests/cpu/c7_manual_cube.cpp.in').read_text()
 return f

def delayed(f):
 f=f.replace('namespace AscendC {','std::deque<std::function<void()>> mac;\nnamespace AscendC {',1)
 f=f.replace('template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}', '''template<HardEvent E>void SetFlag(int i){
 auto flag=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};
 if(E==HardEvent::M_MTE1||E==HardEvent::M_FIX)mac.push_back(flag);else flag();
}''')
 f=f.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);', '''    if(E==HardEvent::M_MTE1||E==HardEvent::M_FIX)while(st.events[std::make_pair(int(E),i)]==0){assert(!mac.empty());auto c=mac.front();mac.pop_front();c();}
    assert(st.events[std::make_pair(int(E),i)]--==1);''')
 a=f.index('template<class T>void Mmad(');b=f.index('struct FixpipeParamsV220',a)
 m=f[a:b].replace('    for(uint32_t m=0;m<p.m;++m)', '    mac.push_back([=]{\n    for(uint32_t m=0;m<p.m;++m)',1)
 m=m.rsplit('}\n',1)[0]+'    });\n}\n';f=f[:a]+m+f[b:]
 f=f.replace('if(P==PIPE_ALL)assert(dma.empty());','if(P==PIPE_ALL)assert(dma.empty()&&mac.empty());')
 return f

def validate_host(s,entry,host,run):
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plan=span(s,'struct Plan {','// Select only an already complete TF batch')
 compact=entry[entry.index('struct C7KernelShape'):entry.index('template<typename T>')]
 main=(ROOT/'tests/cpu/c7_manual_host.cpp.in').read_text()
 code='#include <cstring>\n'+stub+shapes+compact+plan+host+main
 run('host',code);run('host-tuning',code,flags=['-DBMMMS_TUNING'])

def main():
 s=(ROOT/'kernel.asc').read_text();entry,host=scope(s)
 print('Source scope and no TPipe in manual entry PASS; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c7-frame-') as tmp:
  def run(name,code,negative=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=negative)
   if negative:assert r.returncode!=0,'negative control missed: '+name
   else:r.check_returncode()
  v=vector(s,entry);run('vector',v)
  for event in ['V_MTE2','MTE2_V','V_MTE3','MTE3_V']:
   bad=v.replace('        SingleTileDirectFence<true,AscendC::HardEvent::'+event+'>();','');assert bad!=v;run('no-'+event,bad,True)
  bad=v.replace('uint64_t(cols),rows,1,1,s.np/8,','uint64_t(64),rows,1,1,s.np/8,');assert bad!=v;run('no-N-mask',bad,True)
  bad=v.replace('AscendC::PipeBarrier<PIPE_ALL>();','');assert bad!=v;run('no-terminal-drain',bad,True)
  before='''        AscendC::DataCopyPad(c,ring[slot*oneC],cp,pad);
        // This MTE2 signal follows the last GM read, independent of V/MTE3.
        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4+slot);'''
  after='''        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4+slot);
        AscendC::DataCopyPad(c,ring[slot*oneC],cp,pad);'''
  bad=v.replace(before,after);assert bad!=v;run('early-ring-credit',bad,True)
  print('Seven Vector dependency/tail/terminal/GM credit negative controls rejected PASS',flush=True)
  c=cube(s,entry);run('cube',c);d=delayed(c);run('live-mmad',d)
  bad=d.replace('            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(free);','');assert bad!=d;run('no-last-reader',bad,True)
  bad=d.replace('SingleTileDirectFence<true,AscendC::HardEvent::MTE2_MTE1>();','');assert bad!=d;run('no-input-ready',bad,True)
  print('Cube last-reader/input readiness controls rejected PASS',flush=True)
  validate_host(s,entry,host,run)
 print('CANN9/NPU precision/latency PENDING; no FP16 native rounding or complete native scheduler model.')

if __name__=='__main__':main()
