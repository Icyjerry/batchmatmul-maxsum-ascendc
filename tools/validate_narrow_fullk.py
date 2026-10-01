#!/usr/bin/env python3
"""Execute source producer with bounded physical layout/DMA models.

MTE2 copies are delayed; MTE1/MMAD/Fixpipe remain synchronous. Small integer
FP32 arithmetic is not NPU half rounding or performance evidence.
"""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'kernel.asc').read_text()
parent_src=subprocess.check_output(['git','show','a05035e:kernel.asc'],cwd=ROOT,text=True)
def vector_body(s):
 a=s.index('void bmmms_manual(');a=s.index('\n#else\n    AscendC::TQue',a)
 return s[a:s.index('\n#endif\n}',a)]
assert vector_body(src)==vector_body(parent_src), 'consumer changed'
zero=src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
helpers=src[src.index('// Narrow N:'):src.index('// Consume wide GM windows')]
# Reuse the physical NZ/ZZ/ZN, delayed MTE2 and bounded queue model.
model=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
a=model.index('void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p)')
b=model.index('struct MmadParams',a)
model=model[:a]+r'''
void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 assert(!p.enTranspose && dst.mem->pos==TPosition::A2 && src.mem->pos==TPosition::A1 && !src.mem->pending);
 assert(p.l1H==1 && p.l1W%16==0 && p.channelSize%16==0 && p.mStartPt==0 && p.kStartPt==0);
 assert(p.strideH==1 && p.strideW==1 && p.filterH==1 && p.filterW==1);
 assert(p.dilationFilterH==1 && p.dilationFilterW==1);
 assert(p.mExtension==p.l1W && p.kExtension==p.channelSize);
 const uint32_t rows=p.mExtension,count=p.kExtension;
 for(uint32_t m=0;m<rows;++m)for(uint32_t k=0;k<count;++k)
  dst.at(((m/16)*(count/16)+k/16)*256+(m%16)*16+k%16)=src.at((k/16)*rows*16+m*16+k%16);
 st.aL0+=uint64_t(rows)*count;++st.aLoads;
}
'''+model[b:]
model=model.replace('template<AscendC::HardEvent E>void Fence(){}',r'''
template<AscendC::HardEvent E>void Fence(){
 if(E==AscendC::HardEvent::MTE2_MTE1)
  while(!AscendC::dma.empty()){auto x=AscendC::dma.front();AscendC::dma.pop_front();x.op();x.mem->pending=false;}
}
''')
model=model.replace('// INSERT_HELPERS',zero+helpers)
model+=r'''
void Run(uint32_t m,uint32_t n,uint32_t k,uint32_t workers,bool neg){
 Schedule s{1,m,n,k,128,(n+15)/16*16,(m+127)/128,1,1,workers,0,0};negativeInput=neg;
 std::vector<int16_t> a(m*k),b(k*n);
 for(uint32_t r=0;r<m;++r)for(uint32_t q=0;q<k;++q)a[r*k+q]=A(0,r,q);
 for(uint32_t q=0;q<k;++q)for(uint32_t c=0;c<n;++c)b[q*n+c]=B(0,q,c);
 const auto originalA=a,originalB=b;
 std::vector<float> maxima(m,-std::numeric_limits<float>::infinity());
 std::map<int64_t,int> seen;uint64_t aReads=0,bReads=0,mmads=0,bLoads=0,streamWrites=0;
 float streamedSum=0;
 for(uint32_t worker=0;worker<workers;++worker){
  st=State{};st.s=s;st.tx1=st.tx2=false;uint32_t seq=0,ntasks=0;
  for(uint32_t mt=worker;mt<s.mTiles;mt+=workers,++seq){
   assert(++seen[mt]==1);++ntasks;
   st.expected.push_back({0,int64_t(mt)*128,0,std::min(128u,m-mt*128),n,0,size_t((seq&1)*128*s.baseN)});
  }
  std::vector<float> ring(2*128*s.baseN+16,1e30f);AscendC::TPipe pipe;
  RunManualNarrowCube<int16_t>(pipe,{&a,0,true},{&b,0,false},{&ring},s,worker);
  assert(AscendC::dma.empty() && st.fixes==ntasks && st.mmads==ntasks && st.aCopies==ntasks && st.aDeques==ntasks);
  assert(st.aLoads==ntasks && st.bCopies==(ntasks?1:0) && st.bLoads==(ntasks?(k+15)/16:0));
  for(auto e:st.events)assert(e.second==0);assert(!st.cross[0]&&!st.cross[1]);
  for(size_t i=2*128*s.baseN;i<ring.size();++i)assert(ring[i]==1e30f);
  float laneSums[2][64]={};
  for(auto e:st.maxima){auto r=std::get<1>(e.first);assert(maxima[r]==-std::numeric_limits<float>::infinity());
   maxima[r]=e.second;const uint32_t lane=r%128;laneSums[lane/64][lane%64]+=e.second;}
  for(auto& half:laneSums)for(float v:half)streamedSum+=v;
  streamWrites+=2; // actual unchanged consumer writes two 8-float slots per worker
  aReads+=st.aReads;bReads+=st.bReads;mmads+=st.mmads;bLoads+=st.bLoads;
 }
 assert(a==originalA && b==originalB && seen.size()==s.mTiles);
 assert(aReads==uint64_t(m)*k && bReads==uint64_t(std::min(workers,s.mTiles))*n*k && mmads==s.mTiles);
 float golden=0;
 for(uint32_t r=0;r<m;++r){float mx=-std::numeric_limits<float>::infinity();
  for(uint32_t c=0;c<n;++c){float v=0;for(uint32_t q=0;q<k;++q)v+=float(A(0,r,q))*float(B(0,q,c));mx=std::max(mx,v);}
  assert(maxima[r]==mx);if(neg)assert(mx<0);golden+=mx;
 }
 assert(streamedSum==golden && streamWrites==2*workers);
}
int main(){unsigned checked=0;
 for(uint32_t m:{1u,17u,64u,65u,127u,128u,129u,257u,513u})
 for(uint32_t n:{16u,17u,64u,65u,96u,127u,128u})for(uint32_t k:{32u,40u,128u,136u,192u,248u,256u})
 for(uint32_t workers:{1u,3u,8u})for(bool neg:{false,true}){
  Run(m,n,k,workers,neg);++checked;
 }
 for(uint32_t n:{64u,127u})for(uint32_t k:{128u,248u})for(bool neg:{false,true}){
  Run(8192,n,k,20,neg);++checked;
 }
 std::cout<<checked<<" source narrow complete-K producers, delayed MTE2, physical NZ/ZZ/ZN, exact C/padding, input/ring bounds, event/queue credits, negative Max then per-worker Sum PASS\n";
}
'''
shapes=src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host=src[src.index('struct Plan {'):src.index('using CacheKey =')]
parent=parent_src[parent_src.index('struct Plan {'):parent_src.index('using CacheKey =')]
hostmain=r'''
int main(){unsigned checked=0,selected=0;
 auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{1,8,20,32})for(int m:{2048,2049,8192})for(int n:{16,64,65,96,127,128,129})
 for(int k:{32,40,128,136,192,248,256,264})for(int dt:{1,2})for(int layout=0;layout<4;++layout){
  Shape s{1,m,n,k,dt,layout/2,layout%2};auto a=Parent::MakePlan(s,cores);auto b=Candidate::MakePlan(s,cores);++checked;
  auto x=a.schedule,y=b.schedule;
  if(y.dual==32){++selected;assert((x.dual==3||x.dual==14)&&dt==1&&!s.tx1&&!s.tx2);
   assert(y.nTiles==1&&y.nSplit==1&&y.kSplit==1&&y.window==1&&y.earlySum==1&&y.baseM==128);
   const uint64_t kp=Ceil(k,16)*16,ab=2ULL*y.baseM*kp,bb=2ULL*y.baseN*kp;
   assert(2*ab+bb+4096<=hw->l1 && ab<=hw->l0a && bb<=hw->l0b && 8ULL*y.baseM*y.baseN<=hw->l0);
   assert(4ULL*y.baseM*y.baseN+22ULL*y.baseM+12ULL*y.vectorTile+64+4096<hw->ub);
   y.dual=x.dual;y.earlySum=x.earlySum;
  }
  assert(a.totalBytes==b.totalBytes&&a.systemBytes==b.systemBytes&&a.cubeBlocks==b.cubeBlocks&&a.finalBlocks==b.finalBlocks);
  assert(!std::memcmp(&x,&y,sizeof(x)));
 }
 Shape hit{1,8192,127,248,1,0,0};assert(Candidate::MakePlan(hit,20).schedule.dual==32);
 for(auto p:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){
  auto old=*p;*p=4096;try{assert(Candidate::MakePlan(hit,20).schedule.dual!=32);}catch(const std::runtime_error&){}*p=old;
 }
#ifdef BMMMS_TUNING
 for(auto pin:{&Candidate::Tune().bm,&Candidate::Tune().bn,&Candidate::Tune().window,&Candidate::Tune().ns,
  &Candidate::Tune().ks,&Candidate::Tune().workers,&Candidate::Tune().tree,&Candidate::Tune().dual,&Candidate::Tune().early}){
  Candidate::Tune()=Candidate::TuneConfig{};*pin=1;
  try{assert(Candidate::MakePlan(hit,20).schedule.dual!=32);}catch(const std::exception&){}
 }
 Candidate::Tune()=Candidate::TuneConfig{};
#endif
 assert(selected>0);std::cout<<checked<<" host cases, "<<selected<<" narrow selections: capacities, tails/layout/dtype exclusions, pins, finished geometry/workspace unchanged PASS\n";
}
'''
hostmodel='#include <cstring>\n'+(ROOT/'tests/cpu/planner_stub.hpp').read_text()+shapes+'namespace Parent{'+parent+'}\nnamespace Candidate{'+host+'}\n'+hostmain

def main():
 compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
 print('Kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
 with tempfile.TemporaryDirectory(prefix='bmmms-narrow-fullk-') as d:
  for name,code,flags in [('cube',model,[]),('host',hostmodel,[]),('host-tuning',hostmodel,['-DBMMMS_TUNING'])]:
   cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
 print('Vector body byte-identical to passing TT seed; independent per-worker Sum model. CANN9/NPU PENDING.')
if __name__=='__main__':main()
