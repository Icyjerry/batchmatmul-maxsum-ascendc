#!/usr/bin/env python3
"""Actual storage-native document entry under queued CPU engines; not CANN/NPU timing."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 entry=span(s,'// Multiply document storage [K,N]','template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>\n__global__ __vector__ void bmmms_tiny_direct')
 host=span(s,'// The storage-native K tree','template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>')
 call='''    if constexpr(!TX2)if(TinyStorageFrameFits(s,TX1,TX2,GROUPED?group:0)) {
        bmmms_tiny_storage_vector<T,TX1,KCONST,GROUPED><<<blocks,nullptr,stream>>>(x1,x2,y,s,group);
        return;
    }
'''
 assert s.count(call)==1
 assert s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==source('1734f16')
 return entry,host

def queued(f,prefix):
 a=f.index(prefix);a=f.index('{',a);depth=1;b=a+1
 while depth:
  depth+=(f[b]=='{')-(f[b]=='}');b+=1
 return f[:a+1]+'Push(1,[=]{'+f[a+1:b-1]+'});'+f[b-1:]

def model(s,entry,host):
 f=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
 f=f.replace('#include <algorithm>','#include <algorithm>\n#include <array>')
 extra='''struct Command {std::function<bool()> ready;std::function<void()> run;};
std::array<std::deque<Command>,3> engines;
unsigned mode=0,transposes=0;
void Push(int p,std::function<void()> f){engines[p].push_back({[]{return true;},f});}
void Drain(){
 const unsigned order[3][3]={{0,1,2},{1,2,0},{2,0,1}};
 while(!engines[0].empty()||!engines[1].empty()||!engines[2].empty()){
  bool progress=false;for(auto p:order[mode])if(!engines[p].empty()&&engines[p].front().ready()){
   auto c=engines[p].front();engines[p].pop_front();c.run();progress=true;break;
  }assert(progress&&"missing dependency or stalled engine");
 }
}
std::map<uint64_t,uint64_t> localEnds;
'''
 f=f.replace('namespace AscendC {','namespace AscendC {\n'+extra,1)
 a=f.index('template<HardEvent E>void SetFlag');b=f.index('\nuint32_t block=',a)
 f=f[:a]+'''template<HardEvent E>void SetFlag(int id){
 assert(id==0);auto f=[] {assert(flags[E]++==0);};
 if(E==HardEvent::S_V)f();else Push(E==HardEvent::MTE2_V?0:1,f);
}
template<HardEvent E>void WaitFlag(int id){
 assert(id==0);int p=E==HardEvent::V_MTE3?2:1;
 engines[p].push_back({[]{return flags[E]>0;},[]{--flags[E];}});
}
'''+f[b:]
 f=f.replace('void SetValue(size_t i,T v)const{write(i,v);}', '''void SetValue(size_t i,T v)const{write(i,v);}
    void* GetPhyAddr()const{
      auto p=mem->data()+offset;localEnds[reinterpret_cast<uint64_t>(p)]=reinterpret_cast<uint64_t>(mem->data()+end);return p;
    }''')
 f=f.replace('template<int P> void PipeBarrier(){if(P==PIPE_ALL){Flush(dma);Flush(outDma);}}',
  'template<int P> void PipeBarrier(){if(P==PIPE_ALL)Drain();else assert(P==PIPE_V);}')
 f=f.replace('dma.push_back([=]{','Push(0,[=]{').replace('outDma.push_back([=]{','Push(2,[=]{')
 for prefix in ['template<typename T> void Muls(',
  'template<typename T> void Adds(', 'template<typename T> void Duplicate(',
  'template<typename T> void Cast(', 'void Gather(', 'template<class T>void Adds(',
  'template<class T>void Duplicate(', 'void Mul(', 'void Add(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint32_t n)', 'void WholeReduceSum(', 'void WholeReduceMax(']:
  f=queued(f,prefix)
 trans=(ROOT/'tests/cpu/tiny_storage_vector_api.cpp.in').read_text()
 f=f.replace('enum class RoundMode',trans+'\nenum class RoundMode')
 f=f.replace('p.dstBlk==1 && p.src0Blk==1 && p.src1Blk==1','p.dstBlk==1 && p.src0Blk<=1 && p.src1Blk==1')
 f=f.replace('a.read(r*p.src0Rep*8+i)*b.read(r*p.src1Rep*8+i)','a.read(r*p.src0Rep*8+(i/8)*p.src0Blk*8+i%8)*b.read(r*p.src1Rep*8+i)')
 f=f.replace('for(unsigned i=0;i<n;++i)dst.write(i,float(src.read(i)));',
  'for(unsigned i=0;i<n;++i){if(!canonicalExpected.empty()){assert(canonicalExpected.size()==n&&src.read(i)==canonicalExpected[i]);}dst.write(i,Decode(src.read(i)));}')
 f=f.replace('void Add(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint32_t n){Push(1,[=]{','void Add(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint32_t n){Push(1,[=]{assert(n<=255*64);')
 # Keep the unmodified passed TinyCompute as an independent same-order reference.
 kernels=span(s,'struct TinyKernelShape','template<typename T>\n__aicore__ inline void DotGroupCopy(')
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text()
 tune=span(s,'struct TuneConfig {','inline bool TinyVectorFits(')
 # Only TuneConfig/Tune are required; exclude the intermediate host routines.
 tune=tune[:tune.index('\n',tune.index('inline TuneConfig &Tune()'))+1]
 f=stub+tune+f.replace('// INSERT_KERNELS',kernels+host)
 f+=(ROOT/'tests/cpu/tiny_batch_coverage_model.cpp.in').read_text().split('unsigned grouped=')[0]
 f+=(ROOT/'tests/cpu/tiny_storage_vector_model.cpp.in').read_text()
 return f

def main():
 s=(ROOT/'kernel.asc').read_text();entry,host=scope(s)
 print('Three added regions restore complete passed parent 1734f16; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 c=model(s,entry,host);compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tiny-storage-') as tmp:
  def run(name,code,bad=False,flags=()):
   p=Path(tmp)/(name+'.cpp');exe=Path(tmp)/name;p.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(p),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed '+name
   else:r.check_returncode()
  run('vector-host',c);run('vector-host-tuning',c,flags=['-DBMMMS_TUNING'])
  for name,line in [('input-ready','    AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);'),
   ('output-ready','    AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(0);'),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();'),
   ('batch-offset','        output=(GM_ADDR)(reinterpret_cast<__gm__ float*>(output)+b0);')]:
   bad=c.replace(line,'');assert bad!=c;run('no-'+name,bad,True)
  bad=c.replace('for(uint32_t step=k/2;step;step/=2)','for(uint32_t step=k/4;step;step/=2)');assert bad!=c;run('incomplete-K',bad,True)
  bad=c.replace('uint64_t(s.n),static_cast<uint8_t>(ar),8,1,stride','uint64_t(pitch),static_cast<uint8_t>(ar),8,1,stride');assert bad!=c;run('no-N-mask',bad,True)
  bad=c.replace('const AscendC::BinaryRepeatParams rp{1,0,1,static_cast<uint8_t>(ar*stride),1,stride};','const AscendC::BinaryRepeatParams rp{1,1,1,static_cast<uint8_t>(ar*stride),1,stride};');assert bad!=c;run('wrong-broadcast',bad,True)
  bad=c.replace('static_cast<uint8_t>(ar*stride),1,stride','stride,1,stride');assert bad!=c;run('wrong-K-stride',bad,True)
 print('Eight input/output/terminal/batch/K-tree/N-tail/broadcast/group-stride controls rejected PASS')
 print('CANN9 compile/native precision/NPU timing PENDING; queued CPU model is not a hardware emulator.')
if __name__=='__main__':main()
