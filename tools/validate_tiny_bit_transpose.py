#!/usr/bin/env python3
"""Actual bit-transpose entry under queued CPU engines; not CANN/NPU timing."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 entry=span(s,'// Transpose raw 16-bit storage','template<typename T,bool TX1,bool TX2,uint32_t KCONST=0>\n__global__ __vector__ void bmmms_tiny_direct')
 host=span(s,'// The padded 16-bit transpose frame','template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>')
 call='''    if constexpr(TX1 || !TX2)if(TinyBitFrameFits(s,TX1,TX2,GROUPED?group:0)) {
        bmmms_tiny_bit_transpose<T,TX1,TX2,KCONST,GROUPED><<<blocks,nullptr,stream>>>(x1,x2,y,s,group);
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
  'template<class T>void Duplicate(', 'void Mul(', 'void WholeReduceSum(', 'void WholeReduceMax(']:
  f=queued(f,prefix)
 trans='''std::vector<int16_t> canonicalExpected;
struct TransDataTo5HDParams {bool dstHighHalf=false,srcHighHalf=false;uint8_t repeatTimes=0;uint16_t dstRepStride=0,srcRepStride=0;};
template<class T>void TransDataTo5HD(uint64_t da[16],uint64_t sa[16],TransDataTo5HDParams p){
 static_assert(sizeof(T)==2);assert(!p.dstHighHalf&&!p.srcHighHalf&&p.repeatTimes>=2&&p.repeatTimes<=4);
 std::array<uint64_t,16>d,a;std::copy(da,da+16,d.begin());std::copy(sa,sa+16,a.begin());++transposes;
 for(unsigned i=0;i<16;++i){assert((a[i]-reinterpret_cast<uint64_t>(ub->data()))%32==0);
  assert((d[i]-reinterpret_cast<uint64_t>(ub->data()))%32==0);assert(localEnds.count(a[i])&&localEnds.count(d[i]));}
 Push(1,[=]{for(unsigned r=0;r<p.repeatTimes;++r)for(unsigned i=0;i<16;++i)for(unsigned j=0;j<16;++j){
  uint64_t from=a[i]+r*p.srcRepStride*32+j*2,to=d[j]+r*p.dstRepStride*32+i*2;
  assert(from+2<=localEnds.at(a[i])&&to+2<=localEnds.at(d[j]));
  uint16_t value;std::memcpy(&value,reinterpret_cast<void*>(from),2);std::memcpy(reinterpret_cast<void*>(to),&value,2);
 }});
}
'''
 f=f.replace('enum class RoundMode',trans+'\nenum class RoundMode')
 f=f.replace('for(unsigned i=0;i<n;++i)dst.write(i,float(src.read(i)));',
  'for(unsigned i=0;i<n;++i){if(!canonicalExpected.empty()){assert(canonicalExpected.size()==n&&src.read(i)==canonicalExpected[i]);}dst.write(i,float(src.read(i)));}')
 # Keep the unmodified passed TinyCompute as an independent same-order reference.
 kernels=span(s,'struct TinyKernelShape','template<typename T>\n__aicore__ inline void DotGroupCopy(')
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text()
 tune=span(s,'struct TuneConfig {','inline bool TinyVectorFits(')
 # Only TuneConfig/Tune are required; exclude the intermediate host routines.
 tune=tune[:tune.index('\n',tune.index('inline TuneConfig &Tune()'))+1]
 f=stub+tune+f.replace('// INSERT_KERNELS',kernels+host)
 f+=(ROOT/'tests/cpu/tiny_batch_coverage_model.cpp.in').read_text().split('unsigned grouped=')[0]
 f+=(ROOT/'tests/cpu/tiny_bit_transpose_model.cpp.in').read_text()
 return f

def main():
 s=(ROOT/'kernel.asc').read_text();entry,host=scope(s)
 print('Three added regions restore complete passed parent 1734f16; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 c=model(s,entry,host);compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tiny-bits-') as tmp:
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
  bad=c.replace('cp.dstRepStride=1;cp.srcRepStride=pitch;','cp.dstRepStride=1;cp.srcRepStride=1;');assert bad!=c;run('wrong-repeat',bad,True)
  bad=c.replace('uint64_t(s.n),ar,8,1,np/8','uint64_t(np),ar,8,1,np/8');assert bad!=c;run('no-N-mask',bad,True)
  bad=c.replace('if(kp!=k)AscendC::Duplicate(raw[k*am].template ReinterpretCast<uint16_t>(),uint16_t(0),(kp-k)*am);','')
  bad=bad.replace('if(kp!=k)AscendC::Duplicate(raw[k*bn].template ReinterpretCast<uint16_t>(),uint16_t(0),(kp-k)*bn);','')
  assert bad!=c;run('no-K-pad',bad,True)
 print('Seven input/output/terminal/batch/repeat/N-tail/K-padding negative controls rejected PASS')
 print('CANN9 compile/native precision/NPU timing PENDING; queued CPU model is not a hardware emulator.')
if __name__=='__main__':main()
