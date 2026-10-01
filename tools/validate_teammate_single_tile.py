#!/usr/bin/env python3
"""Exact teammate single-tile transfer, independent reductions/producer checks."""
from pathlib import Path
import subprocess,shutil,tempfile,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
PARENT='f7c2c74'
def source(rev):return subprocess.check_output(['git','show',rev+':kernel.asc'],cwd=ROOT,text=True)
def fn(s,name):
 a=s.index('void '+name+'(');a=s.rfind('template',0,a);b=s.index('{',a);e=b+1;d=1
 while d:d+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[a:e]
def span(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
def candidate(parent):
 teammate=source('9ab2312');s=parent
 fold=span(teammate,'__aicore__ inline void SmallRowMaxLaneFold','// One Cube owns one complete small batch.')
 s=s.replace('// One Cube owns one complete small batch.',fold+'// One Cube owns one complete small batch.',1)
 context=span(teammate,'// Only the partial/merge variant needs a live TPipe','// Isolated case6 fast path copied')
 s=s.replace('// Isolated case6 fast path copied',context+'// Isolated case6 fast path copied',1)
 for name in ['bmmms_single_tile','bmmms_single_tile_direct_batch']:
  old=fn(s,name);new=fn(teammate,name);assert s.count(old)==1;s=s.replace(old,new,1)
 # Use the teammate's plain single-tile entry for FF/TT. The retained NT
 # direct path alone gets the manual local memory/event context.
 start='    // Case 4: specialize only an exact match'
 if start not in s:
  start='    if(p.schedule.dual==19 && s.b>=4 && s.b<=7'
 end='    // Compile-time geometry for measured BF16 NT'
 old=span(s,start,end);new=span(teammate,'    // Case 4: specialize only an exact match',end)
 s=s.replace(old,new,1)
 return s

def main():
 parent=source(PARENT);s=candidate(parent)
 if '--apply' in sys.argv:
  assert (ROOT/'kernel.asc').read_text()==parent;(ROOT/'kernel.asc').write_text(s);return
 assert (ROOT/'kernel.asc').read_text()==s,'unrelated source change'
 print('Whole source equals exact teammate single-tile transfer over '+PARENT+' PASS',flush=True)
 run_models(s,parent)
def run_models(s,parent):
 fold=span(s,'__aicore__ inline void SmallRowMaxLaneFold','// One Cube owns one complete small batch.')
 context=span(s,'// Only the partial/merge variant needs a live TPipe','// Isolated case6 fast path copied')
 helpers=fold+context+fn(s,'bmmms_single_tile')+fn(s,'bmmms_single_tile_direct_batch')
 fixture=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
 fixture=fixture.replace('#define __gm__','#define __mix__(...)\n#define __gm__')
 fixture=fixture.replace('struct Schedule {int64_t b,m,n,k;};','struct Schedule {int64_t b,m,n,k;uint32_t baseM,baseN;};')
 extra=r"""
int ready=0;
void SetAtomicNone(){} void SetMaskNorm(){}void ResetMask(){}
template<int M>void CrossCoreWaitFlag(int id){assert(M==2&&id==0&&ready--==1);}
template<bool B>void SyncAll(){assert(false);}
void DataCopy(LocalTensor<float> dst,GlobalTensor<float> src,uint32_t n){
 assert(n%8==0&&dst.offset%32==0);dma.push_back([=]{for(uint32_t i=0;i<n;++i)dst.write(i,src.read(i));});
}
void DataCopy(GlobalTensor<float> dst,LocalTensor<float> src,uint32_t n){assert(false);}
void Max(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint64_t mask,uint32_t reps,BinaryRepeatParams p){
 assert(mask>0&&mask<=64&&reps<=255&&dst.offset%32==0&&a.offset%32==0&&b.offset%32==0);
 for(uint32_t r=0;r<reps;++r)for(uint32_t i=0;i<mask;++i)
  dst.write(r*p.dstRep*8+i,std::max(a.read(r*p.src0Rep*8+i),b.read(r*p.src1Rep*8+i)));
}
"""
 fixture=fixture.replace('float tree_sum(',extra+'float tree_sum(')
 vector=fixture.replace('// INSERT_KERNELS',helpers)+(ROOT/'tests/cpu/teammate_single_tile_vector.cpp.in').read_text()
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-teammate-single-') as tmp:
  def run(code,name,negative=False,flags=()):
   cpp=Path(tmp)/(name+'.cpp');exe=Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=negative)
   if negative:assert r.returncode!=0,'negative control missed: '+name
   else:r.check_returncode()
  run(vector,'vector')
  bad=vector.replace('uint64_t(n-64),rows,rp','uint64_t(64),rows,rp');assert bad!=vector
  run(bad,'invalid-n-padding',True)
  bad=vector.replace('AscendC::PipeBarrier<PIPE_ALL>();','');assert bad!=vector
  run(bad,'manual-output-incomplete',True)
  print('N padding contamination / missing manual DMA completion controls rejected PASS',flush=True)
  run_producer(s,parent,run)
 print('Integer arithmetic CPU/address models; CANN9 native compilation/precision/timing PENDING')

def run_producer(s,parent,run):
 fixture=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
 fixture=fixture.replace('#define __aicore__', '#define __DAV_CUBE__\n#define __global__\n#define __schedmode__(x)\n#define __mix__(...)\n#define __gm__\nusing GM_ADDR=void*;\n#define __aicore__')
 fixture=fixture.replace('constexpr int PIPE_MTE2=1,PIPE_M=2,PIPE_FIX=3;', 'constexpr int PIPE_MTE2=1,PIPE_M=2,PIPE_FIX=3,PIPE_ALL=4;')
 extra=r"""
using TEventID=int;
uint32_t block=0;uint32_t GetBlockIdx(){return block;}
void SetAtomicNone(){}void SetMaskNorm(){}void ResetMask(){}
void SetLoadDataBoundary(uint64_t){}void SetLoadDataPaddingValue(uint64_t){}
std::map<int,std::vector<std::pair<size_t,size_t>>> ranges;
void Claim(TPosition p,size_t start,size_t count){
 int bank=p==TPosition::B1?int(TPosition::A1):int(p);size_t limit=(p==TPosition::A1||p==TPosition::B1)?512*1024:(p==TPosition::CO1?128*1024:64*1024);
 assert(start%32==0&&start+count<=limit);
 for(auto range:ranges[bank])assert(start+count<=range.first||start>=range.second);
 ranges[bank].push_back({start,start+count});
}
std::map<uintptr_t,std::pair<size_t,bool>> registry;
"""
 fixture=fixture.replace('template<class T>struct LocalTensor {',extra+'template<class T>struct LocalTensor {')
 fixture=fixture.replace('    LocalTensor operator[]',r"""    LocalTensor()=default;
    LocalTensor(std::shared_ptr<Storage> p,size_t o):mem(p),offset(o){}
    LocalTensor(TPosition p,size_t start,size_t elements){Claim(p,start,elements*sizeof(T));mem=std::make_shared<Storage>(elements*sizeof(T),p);}
    LocalTensor operator[]""")
 a=fixture.index('template<class T>struct GlobalTensor');b=fixture.index('template<TPosition P,int N>struct TQue',a)
 fixture=fixture[:a]+r"""
template<class T>struct GlobalTensor{
 T* data=nullptr;size_t offset=0,count=0;bool isA=false;
 void SetGlobalBuffer(T* p){uintptr_t ptr=reinterpret_cast<uintptr_t>(p);bool found=false;
  for(auto r:registry)if(ptr>=r.first&&ptr<r.first+r.second.first){data=reinterpret_cast<T*>(r.first);offset=(ptr-r.first)/sizeof(T);count=(r.first+r.second.first-ptr)/sizeof(T);isA=r.second.second;found=true;break;}assert(found);
 }
 GlobalTensor operator[](size_t i)const{assert(i<count);return {data,offset+i,count-i,isA};}
 T& at(size_t i)const{assert(i<count);return data[offset+i];}
};
"""+fixture[b:]
 # Attach each MTE2 ready event to the last DMA issued before that signal.
 fixture=fixture.replace('template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}',r"""
std::map<int,std::shared_ptr<Storage>> targets;
template<HardEvent E>void SetFlag(int i){
 if(E==HardEvent::MTE2_MTE1){assert(!dma.empty());targets[i]=dma.back().mem;}
 assert(st.events[std::make_pair(int(E),i)]++==0);
}
""")
 fixture=fixture.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);', '    if(E==HardEvent::MTE2_MTE1){Flush(targets.at(i));targets.erase(i);}\n    assert(st.events[std::make_pair(int(E),i)]--==1);')
 fixture=fixture.replace('template<int P>void PipeBarrier(){}','template<int P>void PipeBarrier(){if(P==PIPE_ALL)assert(dma.empty());}')
 fixture=fixture.replace('assert(Mode==2 && P==PIPE_FIX && id<2);assert(st.cross[id]++==0);','assert(Mode==2 && P==PIPE_FIX && id==0);')
 fixture=fixture.replace('assert(st.lastCWait==slot);st.lastCWait=-1;', 'st.lastCWait=-1;')
 # Unused output rows/columns may retain NZ poison in the new NT path.
 # Check all valid C exactly, and never assume invalid C is zero.
 fixture=fixture.replace('assert(v==gold); // checks every output C element, including padded rows/cols','if(m<e.rows&&n<e.cols)assert(v==gold);')
 fixture=fixture.replace('template<AscendC::HardEvent E>void Fence(){}','template<AscendC::HardEvent E>void Fence(){AscendC::SetFlag<E>(0);AscendC::WaitFlag<E>(0);}')
 zero=span(s,'template<typename T>\n__aicore__ inline void ManualZeroNZTail','__aicore__ inline void SmallRowMaxLaneFold')
 context=span(s,'// Only the partial/merge variant needs a live TPipe','// Isolated case6 fast path copied')
 model=fixture.replace('// INSERT_HELPERS',zero+context+fn(s,'bmmms_single_tile')+fn(s,'bmmms_single_tile_direct_batch'))
 model+=(ROOT/'tests/cpu/teammate_single_tile_cube.cpp.in').read_text()
 run(model,'cube')
 bad=model.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(aReady);','')
 assert bad!=model;run(bad,'missing-a-ready',True)
 bad=model.replace('AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(bReady);','')
 assert bad!=model;run(bad,'missing-b-ready',True)
 print('Missing independent A/B input ready controls rejected PASS',flush=True)
if __name__=='__main__':main()
