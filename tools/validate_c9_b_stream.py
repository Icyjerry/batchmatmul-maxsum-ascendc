#!/usr/bin/env python3
"""Execute extracted Cube B stream with delayed DMA/MTE1/MMAD readers.

Implicit TQue last-reader synchronization is modeled, not verified against
CANN implementation. Fixpipe is synchronous; no latency/FP16 claim.
"""
from pathlib import Path
import hashlib, re, shutil, subprocess, tempfile
from validate_c7_manual_frame import source, span
from validate_c9_stream_max import host, model as aiv_model
ROOT=Path(__file__).resolve().parents[1]
START='template <typename T, bool PAD_MN'
END='// Isolated case12 packed-B'

def scope(s):
 old=source('a2e6763')
 begin=s.index('// Advance the same two-slot FIFO');end=s.index(END,begin)
 ob=old.index(START,old.index('inline void Case9CopyBPackage'));oe=old.index(END,ob)
 e=s[begin:end];parent=old[ob:oe]
 guard=span(s,'// Only the retained exact C9 package route','// Select only an already complete TF batch')
 launch=span(s,'            if(UseC9BStream(s,p)) {','            const bool pad=s.m%16 || s.n%16 || s.k%16;')
 assert s.replace(e,parent,1).replace(guard,'',1).replace(launch,'',1)==old
 assert span(e,'#else\n    AscendC::TQue','\n#endif\n}')==span(parent,'#else\n    AscendC::TQue','\n#endif\n}')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e,parent

def producer(s,e):
 zero=span(s,'template<typename T>\n__aicore__ inline void ManualZeroNZTail','__aicore__ inline void SmallRowMaxLaneFold')
 copies=span(s,'template<typename T,bool TX1,bool PAD_MN>\n__aicore__ inline void Case9CopyAPackage',START)
 body=span(e,'    AscendC::SetAtomicNone();','\n#else\n    AscendC::TQue')
 wrapper='''template<class T,bool PAD_MN,bool B_STREAM=true>void RunCase9(
 AscendC::TPipe& pipe,AscendC::GlobalTensor<T> a,AscendC::GlobalTensor<T> b,
 AscendC::GlobalTensor<float> ring,Schedule s,uint32_t worker,uint32_t bPackK){
 constexpr bool TX1=false,TX2=true,RESIDENT_A=true;
 const uint32_t aPackK=bPackK,width=s.baseN*s.window,slotSize=s.baseM*width;
 const int64_t tasks=s.b*s.mTiles*s.nSplit;uint32_t sequence=0;
'''+body+'\n}\n'
 f=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
 f=f.replace('window=1;','window=1,kChunk=128;')
 f=f.replace('MTE2_MTE1};','MTE2_MTE1,MTE1_MTE2};').replace('next[5]','next[6]')
 f=f.replace('id>=4 && id<6','id>=2 && id<4').replace('st.cross[id-4]','st.cross[id-2]')
 f=f.replace('uint64_t aDeques=0,overlap=0;', 'uint64_t aDeques=0,overlap=0,bAhead=0;')
 f=f.replace('bool pending=false;', 'bool pending=false;uint64_t readIssued=0,readDone=0,released=0,epoch=0;std::map<size_t,uint64_t> versions;')
 f=f.replace('namespace AscendC {','''std::deque<std::function<void()>> mte1,mac;
void Drain(std::deque<std::function<void()>>& q){while(!q.empty()){auto op=q.front();q.pop_front();op();}}
namespace AscendC {
void SetAtomicNone(){} void SetLoadDataBoundary(uint64_t){} void SetLoadDataPaddingValue(uint64_t){}
void LastReader(std::shared_ptr<Storage>); // declaration moved below Storage
''',1)
 f=f.replace('void LastReader(std::shared_ptr<Storage>); // declaration moved below Storage\n','')
 f=f.replace('struct Pending {','''void LastReader(std::shared_ptr<Storage> mem,uint64_t ticket){
 while(mem->readDone<ticket){assert(!mte1.empty());auto op=mte1.front();mte1.pop_front();op();}
}
struct Pending {''')
 f=f.replace('used[i]=false;return;', 'mem[i]->released=mem[i]->readIssued;used[i]=false;return;')
 f=f.replace('template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}', '''template<HardEvent E>void SetFlag(int i){
 auto op=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};
 if(E==HardEvent::MTE1_M)mte1.push_back(op);else if(E==HardEvent::M_MTE1)mac.push_back(op);else op();
}''')
 # Seed M_MTE1 tokens must be visible immediately, before initial load waits.
 # SetFlag dispatch above queues seeds; waits drain those seed markers as well.
 f=f.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);','''    if(E==HardEvent::MTE1_M)while(st.events[std::make_pair(int(E),i)]==0){assert(!mte1.empty());auto op=mte1.front();mte1.pop_front();op();}
    if(E==HardEvent::M_MTE1)while(st.events[std::make_pair(int(E),i)]==0){assert(!mac.empty());auto op=mac.front();mac.pop_front();op();}
    assert(st.events[std::make_pair(int(E),i)]--==1);''')
 a=f.index('template<class T>void InitConstValue(');b=f.index('template<class T>void DataCopy(',a)
 f=f[:a]+'''template<class T>void InitConstValue(LocalTensor<T> dst,InitConstValueParams<T> p){
 auto ticket=dst.mem->released;
 dma.push_back({dst.mem,[=]{LastReader(dst.mem,ticket);
    for(uint32_t r=0;r<p.repeats;++r)for(uint32_t j=0;j<p.blocks*16;++j)
        dst.at(r*(p.blocks+p.gap)*16+j)=p.value;
 }});
}
'''+f[b:]
 # Flush pending must not clear readiness on an earlier zero-fill command.
 f=f.replace('struct Pending {std::shared_ptr<Storage> mem;std::function<void()> op;};','struct Pending {std::shared_ptr<Storage> mem;std::function<void()> op;bool completes=false;};')
 f=f.replace('x.op();x.mem->pending=false;', 'x.op();if(x.completes)x.mem->pending=false;')
 f=f.replace('    dma.push_back({dst.mem,[=]{\n    for(uint32_t r=0;r<p.nValue;', '    const auto ticket=dst.mem->released;\n    dma.push_back({dst.mem,[=]{LastReader(dst.mem,ticket);++dst.mem->epoch;\n    for(uint32_t r=0;r<p.nValue;')
 f=f.replace('    }});\n    (src.isA?', '    },true});\n#ifdef EAGER_MTE2\n    Flush(dst.mem);\n#endif\n    (src.isA?')
 f=f.replace('    ++(src.isA?st.aCopies:st.bCopies);', '''    ++(src.isA?st.aCopies:st.bCopies);
    if(!src.isA&&st.fixes<st.expected.size()){
      auto e=st.expected[st.fixes];const auto batch=src.offset/(st.s.n*st.s.k),n0=src.offset%(st.s.n*st.s.k)/st.s.k;
      if(batch!=e.b||n0!=e.n)++st.bAhead;
    }''')
 a=f.index('template<class T>void LoadData(LocalTensor<T>');b=f.index('struct MmadParams',a)
 f=f[:a]+'''
struct LoadData2DParams {uint32_t repeatTimes=1,srcStride=1,dstGap=0;bool ifTranspose=false;};
template<class T>void LoadData(LocalTensor<T> dst,LocalTensor<T> src,LoadData2DParams p){
 assert(!src.mem->pending&&p.repeatTimes>0&&p.repeatTimes<=255&&dst.offset%512==0&&src.offset%512==0);
 const auto epoch=src.mem->epoch,ticket=++src.mem->readIssued;
 mte1.push_back([=]{assert(src.mem->epoch==epoch);++dst.mem->versions[dst.offset];
 for(uint32_t r=0;r<p.repeatTimes;++r)for(uint32_t i=0;i<16;++i)for(uint32_t j=0;j<16;++j)
  dst.at(r*(p.dstGap+1)*256+i*16+j)=src.at(r*p.srcStride*256+(p.ifTranspose?j*16+i:i*16+j));
 src.mem->readDone=ticket;
 });
 (dst.mem->pos==TPosition::A2?st.aL0:st.bL0)+=p.repeatTimes*256;
 ++(dst.mem->pos==TPosition::A2?st.aLoads:st.bLoads);
}
template<class T>struct LoadData3DParamsV2 {
 uint32_t l1H=1,l1W=0,channelSize=0,strideH=1,strideW=1,filterH=1,filterW=1;
 uint32_t dilationFilterH=1,dilationFilterW=1,mStartPt=0,kStartPt=0,mExtension=0,kExtension=0;
 bool enTranspose=false;
};
void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 assert(!p.enTranspose&&dst.mem->pos==TPosition::A2&&src.mem->pos==TPosition::A1&&!src.mem->pending);
 assert(p.l1H==1&&p.l1W%16==0&&p.channelSize%16==0&&p.strideH==1&&p.strideW==1&&p.filterH==1&&p.filterW==1);
 assert(p.dilationFilterH==1&&p.dilationFilterW==1&&p.mStartPt==0&&p.kStartPt%16==0);
 uint32_t rows=p.mExtension,count=p.kExtension;
 assert(rows==p.l1W&&count%16==0&&p.kStartPt+count<=p.channelSize);
 const auto epoch=src.mem->epoch,ticket=++src.mem->readIssued;
 mte1.push_back([=]{assert(src.mem->epoch==epoch);++dst.mem->versions[dst.offset];
 for(uint32_t m=0;m<rows;++m)for(uint32_t k=0;k<count;++k){
  uint32_t logicalK=p.kStartPt+k;
  dst.at(((m/16)*(count/16)+k/16)*256+(m%16)*16+k%16)=src.at((logicalK/16)*p.l1W*16+m*16+logicalK%16);
 }
 src.mem->readDone=ticket;
 });
 st.aL0+=uint64_t(rows)*count;++st.aLoads;
}
'''+f[b:]
 # Remove original 2D parameter definition retained before the replacement.
 line='struct LoadData2DParams {uint32_t repeatTimes=1,srcStride=1,dstGap=0;bool ifTranspose=false;};\n'
 assert f.count(line)==2;f=f.replace(line,'',1)
 a=f.index('template<class T>void Mmad(');b=f.index('struct FixpipeParamsV220',a)
 mm=f[a:b]
 mm=mm.replace('    for(uint32_t m=0;m<p.m;++m)','    const auto ae=a.mem->versions[a.offset],be=b.mem->versions[b.offset];\n    mac.push_back([=]{assert(a.mem->versions[a.offset]==ae&&b.mem->versions[b.offset]==be);\n    for(uint32_t m=0;m<p.m;++m)',1)
 mm=mm.rsplit('}\n',1)[0]+'    });\n}\n'
 f=f[:a]+mm+f[b:]
 f=f.replace('template<int P>void PipeBarrier(){}','template<int P>void PipeBarrier(){if(P==PIPE_M)Drain(mac);}')
 f=f.replace('template<AscendC::HardEvent E>void Fence(){}','''template<AscendC::HardEvent E>void Fence(){
 if(E==AscendC::HardEvent::M_FIX)Drain(mac);
 if(E==AscendC::HardEvent::MTE1_MTE2)Drain(mte1);
 if(E==AscendC::HardEvent::MTE2_MTE1)while(!AscendC::dma.empty()){auto x=AscendC::dma.front();AscendC::dma.pop_front();x.op();if(x.completes)x.mem->pending=false;}
}''')
 # Strong values vary along M/N/K/batch, including all-negative cases.
 f=f.replace('1+(b*13+m*7+k*3)%3', '1+(b*13+m*5+k*2+k/7)%7')
 f=f.replace('int16_t B(int64_t b,int64_t k,int64_t n){return -int16_t(1+(b*11+k*3+n*2)%5);}', 'int16_t B(int64_t b,int64_t k,int64_t n){return negativeInput?-int16_t(1+b*7+(k*3+n*2+k/11)%11):int16_t((b*11+k*3+n*2)%11-5);}')
 f=f.replace('// INSERT_HELPERS',zero+copies+wrapper)
 main=(ROOT/'tests/cpu/c9_packages_model.cpp.in').read_text().split('int main(){')[0]
 main='uint64_t totalAhead=0;\n'+main
 main=main.replace('readsA+=st.aReads;', 'totalAhead+=st.bAhead;readsA+=st.aReads;')
 main=main.replace('assert(AscendC::dma.empty());','assert(mte1.empty()&&mac.empty()&&AscendC::dma.empty());')
 main+='''int main(){unsigned count=0;
#ifdef NEGATIVE_CONTROL
 Schedule s{2,129,257,520,128,128,0,0,2,3,0,0};s.window=2;s.kChunk=128;Run<true>(s,256,true);++count;
#else
 for(uint32_t bm:{32u,128u})for(uint32_t bn:{32u,128u})for(uint32_t k:{40u,264u,520u})
 for(uint32_t package:{256u,512u})for(bool neg:{false,true}){
  Schedule s{2,bm+17,2*bn+9,k,bm,bn,0,0,2,3,0,0};s.window=2;s.kChunk=128;
  Run<true>(s,package,neg);++count;
 }
 for(uint32_t ns:{1u,2u,3u})for(uint32_t win:{1u,4u})for(uint32_t workers:{1u,3u,20u}){
  Schedule s{2,64,192,512,32,64,0,0,ns,workers,0,0};s.window=win;s.kChunk=128;
  Run<false>(s,256,true);++count;
 }
 for(auto s:std::vector<Schedule>{{1,129,257,1280,128,128,0,0,3,8,0,0},{1,17,33,8192,16,32,0,0,1,3,0,0}}){
  s.kChunk=128;Run<true>(s,256,true);++count;
 }
#endif
 std::cout<<count<<" extracted producer configurations: delayed DMA/MTE1/MMAD live generations, fullK/tails/batch/task/idle/Max-Sum PASS; B ahead="<<totalAhead<<"\\n";
}
'''
 return f+main

def main():
 s=(ROOT/'kernel.asc').read_text();e,parent=scope(s);v=producer(s,e)
 # Parent source body with identical deferred engine infrastructure.
 old=source('a2e6763');p=producer(old,parent)
 hp=host(s).replace('UseC9StreamMax','UseC9BStream').replace('+uint64_t(d.baseM/2)*64*4','')
 av=aiv_model(s,e).replace('actual==(workers==8?32u:workers==20?96u:384u)', 'actual==768')
 compiler=shutil.which('clang++') or 'c++'
 print('Whole parent inverse/protected7/AIV byte identity PASS; SHA',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 with tempfile.TemporaryDirectory(prefix='bmmms-c9-b-stream-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=240)
   assert (r.returncode!=0) if bad else r.returncode==0,name
  run('host',hp);run('host-tuning',hp,flags=['-DBMMMS_TUNING'])
  run('stream',v);run('parent',p);run('stream-eager-MTE2',v,flags=['-DEAGER_MTE2']);run('unchanged-aiv-finalizer',av)
  faults=[('K-cursor','next.k+=packageK;','next.k+=2*packageK;'),
          ('N-cursor','next.k=0;++next.nt;','next.k=0;next.nt+=2;'),
          ('task-stride','next.task+=s.workers;','next.task+=1;'),
          ('batch','batch=next.task/(s.nSplit*s.mTiles)','batch=0'),
          ('end','if(next.task>=s.b*s.mTiles*s.nSplit)return;','if(next.task+1>=s.b*s.mTiles*s.nSplit)return;'),
          ('last-B1-reader','mem[i]->released=mem[i]->readIssued;','mem[i]->released=0;'),
          ('last-L0-reader','                    AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(loadFree[ks]);',''),
          ('fullK-before-Fix','                Fence<AscendC::HardEvent::M_FIX>();','')]
  for name,a,b in faults:
   assert a in v,name;run('bad-'+name,v.replace(a,b),True,['-DNEGATIVE_CONTROL','-DEAGER_MTE2']);print('Rejected',name,flush=True)
  print('Eight cursor/batch/end/B1-last-reader/L0-last-reader/fullK fault controls rejected PASS',flush=True)
 print('TQue implicit synchronization modeled; Fixpipe synchronous, software integer data/fake tiler, native compile/precision/latency PENDING.')
if __name__=='__main__':main()
