#!/usr/bin/env python3
"""Actual wide-N frame under physical operand and asynchronous consumer models.

Integer CPU arithmetic, not CANN/NPU timing or native BF16 encoding. Cube
cross-core credit uses a synthetic consumer; AIV model uses a synthetic Cube.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]
def scope(s):
 entry=span(s,'// Full-A wide-N frame:','template<typename T>\n__aicore__ inline void ManualFullMReadB')
 host=span(s,'// The original FULL_A route already owns','using CacheKey =')
 call='''    const auto wide=MakeWideNManualFrame(s,p);
    if(wide.workers) {
        bmmms_wide_n_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,wide);
        return;
    }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==source('124658d')
 assert 'TPipe' not in entry[:entry.index('// Every launched AIV')]
 return entry,host

def cube(s,entry):
 f=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
 f=f.replace('#define __aicore__','#define __DAV_CUBE__\n#define __global__\n#define __schedmode__(x)\n#define __mix__(...)\n#define __gm__\nusing GM_ADDR=void*;\n#define __aicore__')
 f=f.replace('constexpr int PIPE_MTE2=1,PIPE_M=2,PIPE_FIX=3;', 'constexpr int PIPE_MTE2=1,PIPE_M=2,PIPE_FIX=3,PIPE_ALL=4,PIPE_V=5;')
 f=f.replace('MTE2_MTE1};','MTE2_MTE1,MTE1_MTE2};')
 # Each half of the B1 array is a disjoint, independently live physical panel.
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
std::deque<std::function<void()>> mte1,mac,fix;
std::map<int,std::shared_ptr<Storage>> targets;
void FlushCommands(std::deque<std::function<void()>>& q){assert(!q.empty());auto x=q.front();q.pop_front();x();}
'''
 f=f.replace('template<class T>struct LocalTensor {',extra+'template<class T>struct LocalTensor {')
 f=f.replace('    std::shared_ptr<Storage> mem;size_t offset=0;', '    std::shared_ptr<Storage> mem;size_t offset=0;std::shared_ptr<Storage> second;')
 f=f.replace('    LocalTensor operator[](size_t i)const{assert(offset+i*sizeof(T)<mem->bytes.size());return {mem,offset+i*sizeof(T)};}', '''    LocalTensor()=default;
    LocalTensor(std::shared_ptr<Storage> p,size_t o):mem(p),offset(o){}
    LocalTensor(TPosition p,size_t start,size_t elements){
      Claim(p,start,elements*sizeof(T));size_t n=elements*sizeof(T);
      if(p==TPosition::B1){mem=std::make_shared<Storage>(n/2,p);second=std::make_shared<Storage>(n/2,p);}
      else mem=std::make_shared<Storage>(n,p);
    }
    LocalTensor operator[](size_t i)const{
      if(second&&i*sizeof(T)>=mem->bytes.size())return {second,i*sizeof(T)-mem->bytes.size()};
      assert(offset+i*sizeof(T)<mem->bytes.size());return {mem,offset+i*sizeof(T)};
    }''')
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
 a=f.index('template<HardEvent E>void SetFlag');b=f.index('struct Nd2NzParams',a)
 f=f[:a]+'''template<HardEvent E>void SetFlag(int i){
 auto flag=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};
 if(E==HardEvent::MTE2_MTE1){assert(!dma.empty()&&!targets.count(i));targets[i]=dma.back().mem;flag();}
 else if(E==HardEvent::MTE1_MTE2||E==HardEvent::MTE1_M)mte1.push_back(flag);
 else if(E==HardEvent::M_MTE1||E==HardEvent::M_FIX)mac.push_back(flag);
 else if(E==HardEvent::FIX_M)fix.push_back(flag);
 else assert(false);
}
template<HardEvent E>void WaitFlag(int i){
 if(E==HardEvent::MTE2_MTE1){Flush(targets.at(i));targets.erase(i);}
 while(!st.events[std::make_pair(int(E),i)]){
  if(E==HardEvent::MTE1_MTE2||E==HardEvent::MTE1_M)FlushCommands(mte1);
  else if(E==HardEvent::M_MTE1||E==HardEvent::M_FIX)FlushCommands(mac);
  else if(E==HardEvent::FIX_M)FlushCommands(fix);else assert(false);
 }
 assert(st.events[std::make_pair(int(E),i)]--==1);
 if(E==HardEvent::FIX_M)st.lastCWait=i;
}
template<int P>void PipeBarrier(){if(P==PIPE_ALL)assert(dma.empty()&&mte1.empty()&&mac.empty()&&fix.empty()&&targets.empty());}
template<int Mode>void CrossCoreWaitFlag(int id){
 assert(Mode==2&&id==4);while(st.cross[0]==0)FlushCommands(fix);assert(st.cross[0]--==1);
}
template<int Mode,int P>void CrossCoreSetFlag(int id){
 assert(Mode==2&&P==PIPE_FIX&&id==0);
 fix.push_back([]{assert(st.cross[0]++==0);}); // synthetic consumer's last GM-read credit
}
struct BinaryRepeatParams {uint32_t a,b,c,d,e,f;};
void Max(LocalTensor<float>,LocalTensor<float>,LocalTensor<float>,uint64_t,uint32_t,BinaryRepeatParams){assert(false);}
void Max(LocalTensor<float>,LocalTensor<float>,LocalTensor<float>,uint32_t){assert(false);}
'''+f[b:]
 # Defer Load2D and read its live L1 operand only on MTE1 completion.
 a=f.index('template<class T>void LoadData(');b=f.index('template<class T>struct LoadData3DParams',a)
 load=f[a:b].replace('    assert(!src.mem->pending);','    mte1.push_back([=]{\n    assert(!src.mem->pending);',1)
 load=load.rsplit('}\n',1)[0]+'    });\n}\n';f=f[:a]+load+f[b:]
 # MMAD reads live L0 and writes C only on Cube completion.
 a=f.index('template<class T>void Mmad(');b=f.index('struct FixpipeParamsV220',a)
 mm=f[a:b].replace('    for(uint32_t m=0;m<p.m;++m)','    mac.push_back([=]{\n    for(uint32_t m=0;m<p.m;++m)',1)
 mm=mm.rsplit('}\n',1)[0]+'    });\n}\n';f=f[:a]+mm+f[b:]
 a=f.index('void Fixpipe(');b=f.index('\n}\n}\ntemplate<AscendC::HardEvent',a)
 fp=f[a:b+2].replace('    for(uint32_t m=0;m<p.mSize;++m)','    fix.push_back([=]{\n    for(uint32_t m=0;m<p.mSize;++m)',1)
 fp=fp.rsplit('}\n',1)[0] if fp.endswith('}\n') else fp[:-1]
 fp+='    });\n}';f=f[:a]+fp+f[b+2:]
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Isolated case6 fast path copied')
 f=f.replace('// INSERT_HELPERS',fence+entry)
 f+=(ROOT/'tests/cpu/wide_n_manual_cube.cpp.in').read_text()
 return f

def vector(s,entry):
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Isolated case6 fast path copied')
 fold=span(s,'__aicore__ inline void SmallRowMaxLaneFold','// One Cube owns one complete small batch.')
 return (ROOT/'tests/cpu/wide_n_manual_vector.cpp.in').read_text().replace('// INSERT_KERNEL',fence+fold+entry)

def host_model(s,entry,host):
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plan=span(s,'struct Plan {','// Select only an already complete TF batch')
 compact=entry[entry.index('struct WideNKernelShape'):entry.index('template<typename T>')]
 return '#include <cstring>\n'+stub+shapes+compact+plan+host+(ROOT/'tests/cpu/wide_n_manual_host.cpp.in').read_text()

def main():
 s=(ROOT/'kernel.asc').read_text();entry,host=scope(s)
 print('Three new regions restore complete passed parent; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-wide-frame-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=120)
   if bad:assert r.returncode!=0,'missed control: '+name
   else:r.check_returncode()
  c=cube(s,entry);run('cube',c)
  for name,line in [('B1-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),('B2-reader','        AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(0);'),('C0-reader','        AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(slot);'),('B-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(slot);')]:
   unsafe=c.replace(line,'');assert unsafe!=c;run('no-'+name,unsafe,True)
  print('Four deferred Cube operand/ready negative controls rejected PASS',flush=True)
  v=vector(s,entry);run('vector',v)
  controls=[('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);',''),('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);',''),('partial-ready','    SingleTileDirectFence<true,AscendC::HardEvent::V_MTE3>();',''),('barrier','    AscendC::SyncAll<true>();',''),('final-copy-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();',''),('terminal-drain','AscendC::PipeBarrier<PIPE_ALL>();',''),('N-tail','uint64_t(n-64),rows,rp','uint64_t(64),rows,rp')]
  for name,old,new in controls:
   unsafe=v.replace(old,new);assert unsafe!=v;run('no-'+name,unsafe,True)
  early=v.replace('        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4);','',1)
  early=early.replace('        AscendC::CrossCoreWaitFlag<2>(0);','        AscendC::CrossCoreWaitFlag<2>(0);\n        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4);',1)
  assert early!=v;run('early-GM-credit',early,True)
  print('Eight queued Vector copy/barrier/tail/completion/credit controls rejected PASS',flush=True)
  h=host_model(s,entry,host);run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CANN9/native BF16 precision/latency PENDING; hardware barrier/credit protocol abstracted.')
if __name__=='__main__':main()
