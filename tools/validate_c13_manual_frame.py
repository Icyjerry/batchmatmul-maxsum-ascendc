#!/usr/bin/env python3
"""Extracted C13 entry: live physical operands, queued AIVs and actual host guards.

CPU integer/FIFO model; synthetic companion/Cube credits, not native FP16 timing.
"""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
from validate_c7_manual_frame import span, source
from validate_wide_n_manual_frame import cube as wide_cube
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 entry=span(s,'// Narrow FF tail plan:','// Full-A wide-N frame:')
 host=span(s,'// Only the existing FF tail/earlySum plan;','using CacheKey =')
 call='''    const auto c13=MakeC13ManualFrame(s,p);
    if(c13.workers) {
        bmmms_c13_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,c13);
        return;
    }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==source('1734f16')
 assert 'TPipe' not in entry and 'TQue' not in entry
 return entry,host

def cube(s,entry):
 zero=span(s,'template<typename T>\n__aicore__ inline void ManualZeroNZTail','__aicore__ inline void SmallRowMaxLaneFold')
 f=wide_cube(s,zero+entry).split('void Run(uint32_t M,uint32_t N,uint32_t K,uint32_t workers,bool neg)')[0]
 f=f.replace('if(p==TPosition::B1){','if(p==TPosition::A1||p==TPosition::B1){')
 f=f.replace('std::deque<std::function<void()>> mte1,mac,fix;', 'bool eagerFix=false;\nstd::deque<std::function<void()>> mte1,mac,fix;')
 a=f.index('template<int Mode>void CrossCoreWaitFlag');b=f.index('struct BinaryRepeatParams',a)
 f=f[:a]+'''template<int Mode>void CrossCoreWaitFlag(int id){
 assert(Mode==2&&id>=4&&id<6);while(st.cross[id-4]==0)FlushCommands(fix);assert(st.cross[id-4]--==1);
}
template<int Mode,int P>void CrossCoreSetFlag(int id){
 assert(Mode==2&&P==PIPE_FIX&&id>=0&&id<2);
 fix.push_back([=]{assert(st.cross[id]++==0);});
 if(eagerFix)while(!fix.empty())FlushCommands(fix);
}
'''+f[b:]
 f+=(ROOT/'tests/cpu/c13_manual_cube.cpp.in').read_text()
 return f

def vector(s,entry):
 f=(ROOT/'tests/cpu/wide_n_manual_vector.cpp.in').read_text().split('void Run(uint32_t M,uint32_t N,uint32_t K,uint32_t ns,bool neg,uint32_t mode)')[0]
 f=f.replace('uint32_t m,n,k,mp,np,nt,ns;', 'uint32_t m,n,k,mp,np,nt,ns,bm,workers;')
 f=f.replace('q.ns*2*q.mp*q.np','q.workers*2*q.bm*q.np').replace('barrier(q.ns*2)','barrier(q.workers*2)')
 f=f.replace('int credit=0;', 'int credit[2]={};').replace('int ringGen=-9;', 'int ringGen[2]={-9,-9};')
 a=f.index('  if(reused)assert(');b=f.index('\n }\n LocalTensor operator[]',a)
 f=f[:a]+'''  if(reused){
   assert(elems==(shared->s.m/128)*16);
   for(auto& q:st.queues)assert(q.empty());st.ranges.clear();
  }
  for(auto r:st.ranges)assert(bytes+elems*4<=r.first||bytes>=r.second);
  st.ranges.push_back({bytes,bytes+elems*4});++st.allocs;'''+f[b:]
 f=f.replace('(st.block/2)*2*s.mp*s.np','(st.block/2)*2*s.bm*s.np')
 a=f.index('template<int Mode,int Pipe>void CrossCoreSetFlag');b=f.index('struct DataCopyExtParams',a)
 f=f[:a]+'''template<int Mode,int Pipe>void CrossCoreSetFlag(int flag){
 assert(Mode==2&&Pipe==PIPE_MTE2&&flag>=4&&flag<6);uint32_t slot=flag-4;bool prime=st.primes<2;
 if(prime){assert(st.issued==0);++st.primes;}else ++st.releases;
 st.Push(PIPE_MTE2,[=]{assert(st.credit[slot]++==0);if(!prime){
  auto s=shared->s;std::fill(st.ring.begin()+slot*s.bm*s.np,st.ring.begin()+(slot+1)*s.bm*s.np,1e30f);st.ringGen[slot]=-7;
 }});
}
template<int Mode>void CrossCoreWaitFlag(int flag){
 assert(Mode==2&&flag>=0&&flag<2&&flag==int(st.issued&1));auto s=shared->s;
 uint32_t task=st.block/2+st.issued*s.workers;assert(task<s.m/s.bm);int gen=st.issued++;
 st.Push(PIPE_MTE2,[=]{assert(st.credit[flag]--==1);uint32_t m0=task*s.bm;
  auto first=st.ring.begin()+flag*s.bm*s.np;std::fill(first,first+s.bm*s.np,1e30f);st.ringGen[flag]=gen;
  for(uint32_t r=0;r<s.bm;++r)for(uint32_t n=0;n<s.n;++n)
   st.ring[flag*s.bm*s.np+r*s.np+n]=Value(m0+r,n,shared->neg);
 });
}
'''+f[b:]
 a=f.index(' auto s=shared->s;uint32_t sub=',f.index('void DataCopyPad(LocalTensor<float>'));b=f.index('\n}\ntemplate<class T>void DataCopy',a)
 f=f[:a]+''' auto s=shared->s;uint32_t sub=st.block%2,start=sub*64,rows=64,cols=s.n;
 int gen=st.issued-1;uint32_t slot=gen&1;
 assert(src.kind==GlobalTensor<float>::RING&&src.offset==slot*s.bm*s.np+start*s.np&&!pad.pad);
 assert(p.blockCount==rows&&p.blockLen==cols*4&&p.srcStride==(s.np-cols)*4&&p.dstStride==(s.np-cols)/8);
 assert(dst.offset==slot*64*s.np);++st.copies;
 st.Push(PIPE_MTE2,[=]{assert(st.ringGen[slot]==gen&&"GM released before DMA");
  for(uint32_t r=0;r<rows;++r)for(uint32_t c=0;c<cols;++c){dst.At(r*s.np+c)=src.At(r*s.np+c);dst.Gen(r*s.np+c)=gen;}
 });'''+f[b:]
 a=f.index(' auto s=shared->s;uint32_t worker=',f.index('void DataCopy(GlobalTensor<float>'));b=f.index('\n}\nvoid DataCopy(LocalTensor<float>',a)
 f=f[:a]+''' auto s=shared->s;uint32_t worker=st.block/2,sub=st.block%2;
 uint32_t task=worker+(st.issued-1)*s.workers;int gen=st.issued-1;
 assert(dst.kind==GlobalTensor<float>::PARTS&&dst.offset==task*16+sub*8&&count==8);
 assert(src.offset==s.bm*s.np+256+(gen&1)*8);
 st.Push(PIPE_MTE3,[=]{for(uint32_t i=0;i<count;++i){assert(src.Gen(i)==gen&&"sum overwritten before store or V completion");
  dst.At(i)=src.At(i);assert(shared->written[dst.offset+i].fetch_add(1,std::memory_order_release)==0);}});'''+f[b:]
 f=f.replace('count==shared->s.ns*shared->s.mp','count==(shared->s.m/128)*16')
 f=f.replace('void Duplicate(LocalTensor<float> dst,float v,uint32_t count){st.Push(PIPE_V,[=]{for(uint32_t i=0;i<count;++i){dst.At(i)=v;dst.Gen(i)=0;}});}',
  'void Duplicate(LocalTensor<float> dst,float v,uint32_t count){int gen=st.issued-1;st.Push(PIPE_V,[=]{for(uint32_t i=0;i<count;++i){dst.At(i)=v;dst.Gen(i)=gen;}});}')
 f=f.replace('rs==2*shared->s.np/8','rs==shared->s.np/8')
 a=f.index('void WholeReduceSum(');b=f.index('void Add(',a)
 f=f[:a]+'''void WholeReduceSum(LocalTensor<float> dst,LocalTensor<float> src,uint64_t mask,uint32_t reps,uint32_t ds,uint32_t bs,uint32_t rs){
 assert(mask>=1&&mask<=64&&reps<=128&&ds==1&&bs==1);int gen=st.synced?777:int(st.issued-1);
 st.Push(PIPE_V,[=]{for(uint32_t r=0;r<reps;++r){float total=0;
  for(uint32_t i=0;i<mask;++i){assert(src.Gen(r*rs*8+i)==gen);total+=src.At(r*rs*8+i);}dst.At(r)=total;dst.Gen(r)=gen;}});
}
'''+f[b:]
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Isolated case6 fast path copied')
 header=entry[:entry.index('template<typename T>')]
 kernel=entry[entry.index('template<typename T>\n__schedmode__(1)'):]
 f=f.replace('// INSERT_KERNEL',fence+header+kernel)
 f+=(ROOT/'tests/cpu/c13_manual_vector.cpp.in').read_text()
 return f

def main():
 s=(ROOT/'kernel.asc').read_text();entry,host=scope(s)
 print('Three additions restore complete passed1734f16; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c13-frame-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed:'+name
   else:r.check_returncode()
  c=cube(s,entry);run('cube',c)
  for name,line in [('L1-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),
   ('input-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(ks);'),
   ('L0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(ks);'),
   ('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);'),
   ('M-fix','        SingleTileDirectFence<true,AscendC::HardEvent::M_FIX>();')]:
   unsafe=c.replace(line,'');assert unsafe!=c;run('no-'+name,unsafe,True)
  unsafe=c.replace('mm.k=count;','mm.k=count-16;');assert unsafe!=c;run('no-full-K',unsafe,True)
  print('Six live Cube readiness/last-reader/complete-K controls rejected PASS',flush=True)
  v=vector(s,entry);run('vector',v)
  controls=[('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);',''),
   ('sum-reader','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(slot);',''),
   ('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);',''),
   ('sum-ready','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(slot);',''),
   ('barrier','    AscendC::SyncAll<true>();',''),
   ('final-copy-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();',''),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();',''),
   ('N-tail','uint64_t(cols),halfM,1','uint64_t(64),halfM,1')]
  for name,old,new in controls:
   unsafe=v.replace(old,new);assert unsafe!=v;run('no-'+name,unsafe,True)
  copy='        AscendC::DataCopyPad(c,ring[slot*oneC+sub*halfC],cp,pad);'
  release='        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4+slot);'
  unsafe=v.replace(copy+'\n'+release,release+'\n'+copy);assert unsafe!=v;run('early-GM-credit',unsafe,True)
  print('Nine queued AIV C/sum/store/barrier/tail/completion/GM-credit controls rejected PASS',flush=True)
  stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
  shape=span(s,'struct Shape {','template <AscendC::HardEvent')
  plan=span(s,'struct Plan {','struct Case9PackagePlan ')
  header=entry[:entry.index('template<typename T>')]
  h='#include <cstring>\n'+stub+shape+plan+header+host+(ROOT/'tests/cpu/c13_manual_host.cpp.in').read_text()
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CPU only; native FP16 precision/CANN9/latency PENDING.')
if __name__=='__main__':main()
