#!/usr/bin/env python3
"""Actual TT physical frame: queued live operands, consumer and host models.

Integer CPU arithmetic, not native BF16, TPipe, hardware timing or a complete
Cube/Vector co-simulator. Cross-core producers/companions are synthetic.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_wide_n_manual_frame import cube as wide_cube
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 entry=span(s,'// Same TT tile/package stream','// All N-tile partials are ready')
 host=span(s,'// Existing dual33 geometry','using CacheKey =')
 call='''        const auto frame=MakeTTManualFrame(s,p);
        if(frame.workers) {
            bmmms_tt_manual_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,frame);
            return;
        }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==source('03c3996')
 assert 'TPipe' not in entry[entry.index('struct TTFrameShape'):]
 return entry,host

def cube(s,entry):
 zero=span(s,'template<typename T>\n__aicore__ inline void ManualZeroNZTail','__aicore__ inline void SmallRowMaxLaneFold')
 transpose=span(s,'// One full-M accumulator:','// Full small TF inputs use')
 f=wide_cube(s,zero+transpose+entry).split('void Run(uint32_t M,uint32_t N,uint32_t K,uint32_t workers,bool neg)')[0]
 a=f.index('void LoadData(LocalTensor<half>');b=f.index('struct MmadParams',a)
 load=f[a:b].replace('    assert(p.enTranspose', '    mte1.push_back([=]{\n    assert(p.enTranspose',1)
 load=load.rsplit('}\n',1)[0]+'    });\n}\n';f=f[:a]+load+f[b:]
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
 f=f.replace('if(P==PIPE_ALL)assert(dma.empty()&&mte1.empty()&&mac.empty()&&fix.empty()&&targets.empty());',
  'if(P==PIPE_ALL)assert(dma.empty()&&mte1.empty()&&mac.empty()&&fix.empty()&&targets.empty());else if(P==PIPE_M)while(!mac.empty())FlushCommands(mac);')
 f+=(ROOT/'tests/cpu/tt_manual_frame_cube.cpp.in').read_text()
 return f

def vector(s,entry):
 f=(ROOT/'tests/cpu/wide_n_manual_vector.cpp.in').read_text().split('void Run(uint32_t M,uint32_t N,uint32_t K,uint32_t ns,bool neg,uint32_t mode)')[0]
 f=f.replace('uint32_t m,n,k,mp,np,nt,ns;', 'uint32_t m,n,k,mp,np,nt,ns,bm,workers;')
 f=f.replace('q.ns*2*q.mp*q.np','q.workers*2*q.bm*q.np').replace('barrier(q.ns*2)','barrier(q.workers*2)')
 f=f.replace('int credit=0;', 'int credit[2]={};').replace('int ringGen=-9;', 'int ringGen[2]={-9,-9};')
 a=f.index('  if(reused)assert(');b=f.index('\n }\n LocalTensor operator[]',a)
 f=f[:a]+'''  if(reused){
   assert(elems==shared->s.ns*shared->s.mp);
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
 uint32_t total=(s.mp/s.bm)*s.nt,begin=(st.block/2)*total/s.workers,end=(st.block/2+1)*total/s.workers;
 uint32_t task=begin+st.issued;assert(task<end);int gen=st.issued++;
 st.Push(PIPE_MTE2,[=]{assert(st.credit[flag]--==1);uint32_t m0=(task/s.nt)*s.bm,n0=(task%s.nt)*s.np;
  auto first=st.ring.begin()+flag*s.bm*s.np;std::fill(first,first+s.bm*s.np,1e30f);st.ringGen[flag]=gen;
  for(uint32_t r=0;r<std::min(s.bm,s.m-m0);++r)for(uint32_t n=0;n<std::min(s.np,s.n-n0);++n)
   st.ring[flag*s.bm*s.np+r*s.np+n]=Value(m0+r,n0+n,shared->neg);
 });
}
'''+f[b:]
 a=f.index(' auto s=shared->s;uint32_t sub=',f.index('void DataCopyPad(LocalTensor<float>'));b=f.index('\n}\ntemplate<class T>void DataCopy',a)
 f=f[:a]+''' auto s=shared->s;uint32_t sub=st.block%2,start=sub*(s.bm/2),total=(s.mp/s.bm)*s.nt;
 uint32_t task=(st.block/2)*total/s.workers+st.issued-1,m0=(task/s.nt)*s.bm,ns=task%s.nt;
 uint32_t rows=start+m0>=s.m?0:std::min(s.m-m0-start,s.bm/2),cols=std::min(s.n-ns*s.np,s.np);
 int gen=st.issued-1;uint32_t slot=gen&1;
 assert(src.kind==GlobalTensor<float>::RING&&src.offset==slot*s.bm*s.np+start*s.np&&!pad.pad);
 assert(p.blockCount==rows&&p.blockLen==cols*4&&p.srcStride==(s.np-cols)*4&&p.dstStride==(s.np-cols)/8);
 assert(dst.offset==slot*(s.bm/2)*s.np);++st.copies;
 st.Push(PIPE_MTE2,[=]{assert(st.ringGen[slot]==gen&&"GM released before DMA");
  for(uint32_t r=0;r<rows;++r)for(uint32_t c=0;c<cols;++c){dst.At(r*s.np+c)=src.At(r*s.np+c);dst.Gen(r*s.np+c)=gen;}
 });'''+f[b:]
 a=f.index(' auto s=shared->s;uint32_t worker=',f.index('void DataCopy(GlobalTensor<float>'));b=f.index('\n}\nvoid DataCopy(LocalTensor<float>',a)
 f=f[:a]+''' auto s=shared->s;uint32_t worker=st.block/2,sub=st.block%2,total=(s.mp/s.bm)*s.nt;
 uint32_t task=worker*total/s.workers+st.issued-1,mt=task/s.nt,ns=task%s.nt;int gen=st.issued-1;
 assert(dst.kind==GlobalTensor<float>::PARTS&&dst.offset==ns*s.mp+mt*s.bm+sub*s.bm/2&&count==s.bm/2);
 assert(src.offset==s.bm*s.np+(gen&1)*s.bm/2);
 st.Push(PIPE_MTE3,[=]{for(uint32_t i=0;i<count;++i){assert(src.Gen(i)==gen&&"row overwritten before store or V completion");
  dst.At(i)=src.At(i);assert(shared->written[dst.offset+i].fetch_add(1,std::memory_order_release)==0);}});'''+f[b:]
 f=f.replace('void Duplicate(LocalTensor<float> dst,float v,uint32_t count){st.Push(PIPE_V,[=]{for(uint32_t i=0;i<count;++i){dst.At(i)=v;dst.Gen(i)=0;}});}',
  'void Duplicate(LocalTensor<float> dst,float v,uint32_t count){int gen=st.issued-1;st.Push(PIPE_V,[=]{for(uint32_t i=0;i<count;++i){dst.At(i)=v;dst.Gen(i)=gen;}});}')
 f=f.replace('rs==2*shared->s.np/8','rs==shared->s.np/8')
 a=f.index('void WholeReduceSum(');b=f.index('void Add(',a)
 f=f[:a]+'''void WholeReduceSum(LocalTensor<float> dst,LocalTensor<float> src,uint64_t mask,uint32_t reps,uint32_t ds,uint32_t bs,uint32_t rs){
 assert(st.synced&&mask>=1&&mask<=64&&reps<=128&&ds==1&&bs==1);
 st.Push(PIPE_V,[=]{for(uint32_t r=0;r<reps;++r){float total=0;
  for(uint32_t i=0;i<mask;++i){assert(src.Gen(r*rs*8+i)==777);total+=src.At(r*rs*8+i);}dst.At(r)=total;dst.Gen(r)=777;}});
}
'''+f[b:]
 fence=span(s,'template<bool DIRECT_BATCH,AscendC::HardEvent E>','// Isolated case6 fast path copied')
 fold=span(s,'__aicore__ inline void SmallRowMaxLaneFold','// One Cube owns one complete small batch.')
 merge=span(s,'// Fold disjoint split halves','template<typename T>\n__schedmode__(1) __global__ __mix__(1,2) void bmmms_wide_n_manual_frame')
 header=entry[:entry.index('template<typename T>')]
 kernel=entry[entry.index('template<typename T>\n__schedmode__(1)'):]
 f=f.replace('// INSERT_KERNEL',fence+fold+merge+header+kernel)
 f+=(ROOT/'tests/cpu/tt_manual_frame_vector.cpp.in').read_text()
 return f

def main():
 s=(ROOT/'kernel.asc').read_text();entry,host=scope(s)
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plan=span(s,'struct Plan {','// Select only an already complete TF batch')
 fit=span(s,'// Reuse UB only after','// Existing dual33 geometry')
 header=entry[:entry.index('template<typename T>')]
 h='#include <cstring>\n'+stub+shapes+header+plan+fit+host+(ROOT/'tests/cpu/tt_manual_frame_host.cpp.in').read_text()
 print('Three additions restore whole passed parent, unchanged tiny/C7/C14/plan/GM; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tt-frame-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed: '+name
   else:r.check_returncode()
  c=cube(s,entry);run('cube',c)
  for name,line in [('B1-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),
   ('A1-reader','            AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(2);'),
   ('L0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(bs);'),
   ('C-reader','            if(k0==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);'),
   ('A-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2);'),
   ('M-fix','        AscendC::WaitFlag<AscendC::HardEvent::M_FIX>(cs);')]:
   unsafe=c.replace(line,'');assert unsafe!=c;run('no-'+name,unsafe,True)
  print('Six live Cube input/last-reader/C/complete-K handoff controls rejected PASS',flush=True)
  v=vector(s,entry);run('vector',v)
  for name,line in [('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);'),
   ('row-reader','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(slot);'),
   ('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);'),
   ('partial-ready','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(slot);'),
   ('barrier','    AscendC::SyncAll<true>();'),
   ('final-copy-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();'),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();')]:
   unsafe=v.replace(line,'');assert unsafe!=v;run('no-'+name,unsafe,True)
  unsafe=v.replace('full=s.m/64,tail=s.m%64','full=(s.m+63)/64,tail=0');assert unsafe!=v;run('no-M-tail',unsafe,True)
  unsafe=v.replace('uint64_t(n-64),rows,rp','uint64_t(64),rows,rp');assert unsafe!=v;run('no-N-tail',unsafe,True)
  print('Nine live Vector C/row/store/barrier/final-copy/tail/completion controls rejected PASS',flush=True)
  run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CANN9/native BF16 precision/latency PENDING; Cube/AIV cross-core interaction remains synthetic.')
if __name__=='__main__':main()
