#!/usr/bin/env python3
"""Actual full-input producer and host controls, not CANN/NPU timing evidence.

Physical NZ/ZZ/ZN, delayed input DMA and deferred live MMAD operands are modeled.
Fixpipe and Load3D are synchronous; FP16 instruction rounding is not simulated.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / 'kernel.asc').read_text()
parent = subprocess.check_output(['git', 'show', 'fd72a34:kernel.asc'], cwd=ROOT, text=True)
zero = src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
transpose = src[src.index('template<typename T>\n__aicore__ inline void ManualTransposeFullM'):src.index('template<typename T>\n__aicore__ inline void ManualFullMReadB')]
a = src.index('// Small TF batches: full inputs in L1')
b = src.index('// All N-tile partials are ready', a)
producer = src[a:b]
fixture = (ROOT / 'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
a = fixture.index('void LoadData(LocalTensor<half>')
b = fixture.index('struct MmadParams', a)
load_a = fixture[a:b]
load_b = r'''
void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 if(p.enTranspose){LoadA(dst,src,p);return;}
 assert(dst.mem->pos==TPosition::B2&&src.mem->pos==TPosition::B1&&!src.mem->pending);
 assert(p.l1H==1&&p.l1W%16==0&&p.channelSize%16==0&&p.strideH==1&&p.strideW==1&&p.filterH==1&&p.filterW==1);
 assert(p.dilationFilterH==1&&p.dilationFilterW==1&&p.mStartPt==0&&p.kStartPt%16==0);
 const uint32_t K=p.mExtension,N=p.kExtension;
 assert(K==p.l1W&&N%16==0&&p.kStartPt+N<=p.channelSize);
 for(uint32_t k=0;k<K;++k)for(uint32_t n=0;n<N;++n){
  const uint32_t col=p.kStartPt+n;
  dst.at(((k/16)*(N/16)+n/16)*256+(n%16)*16+k%16)=
   src.at((col/16)*p.l1W*16+k*16+col%16);
 }
 st.bL0+=uint64_t(K)*N;++st.bLoads;
}
'''
fixture = fixture[:a] + load_a.replace('void LoadData(', 'void LoadA(') + load_b + fixture[b:]
fixture = fixture.replace('if(p.cmatrixInitVal) {', 'if(p.cmatrixInitVal && c.offset%(st.s.baseM*st.s.baseN*4)==0) {')
fixture = fixture.replace('template<AscendC::HardEvent E>void Fence(){}', '''template<AscendC::HardEvent E>void Fence(){
 if(E==AscendC::HardEvent::MTE2_MTE1)while(!AscendC::dma.empty())AscendC::Flush(AscendC::dma.front().mem);
}''')
fixture = fixture.replace('// INSERT_HELPERS', zero + transpose + producer)
main = r'''
void Run(uint32_t batches,uint32_t M,uint32_t N,uint32_t K,uint32_t workers,bool neg){
 negativeInput=neg;const uint32_t BM=(M+15)/16*16,BN=(N+15)/16*16,KP=(K+15)/16*16;
 const uint32_t NB=std::min(BN,65536/(2*KP)/16*16);
 Schedule s{batches,M,N,K,BM,BN,1,1,1,workers,0,0};
 std::vector<int16_t> a(batches*M*K),b(batches*N*K);
 for(uint32_t z=0;z<batches;++z)for(uint32_t k=0;k<K;++k){
  for(uint32_t m=0;m<M;++m)a[z*M*K+k*M+m]=A(z,m,k);
  for(uint32_t n=0;n<N;++n)b[z*N*K+k*N+n]=B(z,k,n);
 }
 const auto oldA=a,oldB=b;
 uint64_t copies=0,mmads=0;
 for(uint32_t w=0;w<workers;++w){
  st=State{};st.s=s;st.tx1=true;st.tx2=false;
  for(uint32_t z=w,seq=0;z<batches;z+=workers,++seq)
   st.expected.push_back({z,0,0,M,N,0,size_t(seq&1)*BM*BN});
  std::vector<float> ring(2*BM*BN+16,1e30f);
  {AscendC::TPipe pipe;RunSmallFullInputsCube<int16_t>(pipe,{&a,0,true},{&b,0,false},{&ring},s,w);}
  assert(AscendC::dma.empty()&&st.fixes==st.expected.size());
  assert(st.aCopies==st.fixes&&st.bCopies==st.fixes&&st.aLoads==st.fixes);
  assert(st.bLoads==st.fixes*((BN+NB-1)/NB)&&st.mmads==st.bLoads);
  assert(st.aReads==st.fixes*M*K&&st.bReads==st.fixes*N*K);
  assert(st.aL0==st.fixes*BM*KP&&st.bL0==st.fixes*BN*KP);
  assert(st.cross[0]==0&&st.cross[1]==0);for(auto e:st.events)assert(e.second==0);
  for(size_t i=2*BM*BN;i<ring.size();++i)assert(ring[i]==1e30f);
  for(uint32_t z=w;z<batches;z+=workers){float total=0,goldTotal=0;
   for(uint32_t m=0;m<M;++m){float mx=-std::numeric_limits<float>::infinity();
    for(uint32_t n=0;n<N;++n){float v=0;for(uint32_t k=0;k<K;++k)v+=float(A(z,m,k))*float(B(z,k,n));mx=std::max(mx,v);}
    assert(st.maxima.at(std::make_tuple(z,m,0))==mx);if(neg)assert(mx<0);
    total+=st.maxima.at(std::make_tuple(z,m,0));goldTotal+=mx;
   }assert(total==goldTotal);
  }
  copies+=st.aCopies+st.bCopies;mmads+=st.mmads;
 }
 assert(a==oldA&&b==oldB&&copies==2*batches&&mmads==uint64_t(batches)*((BN+NB-1)/NB));
}
int main(){unsigned count=0;
 for(uint32_t m:{32u,48u,63u})for(uint32_t n:{128u,192u,255u})for(uint32_t k:{256u,264u,384u,504u})for(bool neg:{false,true}){
  Run(3,m,n,k,2,neg);++count;
 }
 for(uint32_t k:{32u,40u,128u,512u})for(uint32_t cores:{1u,3u,8u}){
  Run(7,17,33,k,cores,true);++count;
 }
 Run(31,1,1,256,20,true);++count;Run(16,32,128,256,20,false);++count;
 std::cout<<count<<" actual full-input producers: paired batches, all-negative/tails, N slices/full-K C, cached full A, exact copies/loads, output guards and events PASS\n";
}
'''
model = fixture + main
# Read live A2/B2/C only when Cube completion is forced. Removing the last-reader
# wait must be rejected, rather than merely comparing an immediate oracle.
delayed = model.replace('namespace AscendC {', 'std::deque<std::function<void()>> mac;\nnamespace AscendC {', 1)
delayed = delayed.replace('template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}',
 'template<HardEvent E>void SetFlag(int i){auto f=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};if(E==HardEvent::M_MTE1)mac.push_back(f);else f();}')
delayed = delayed.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);',
 '    if(E==HardEvent::M_MTE1)while(st.events[std::make_pair(int(E),i)]==0){assert(!mac.empty());auto f=mac.front();mac.pop_front();f();}\n    assert(st.events[std::make_pair(int(E),i)]--==1);')
a = delayed.index('template<class T>void Mmad(')
b = delayed.index('struct FixpipeParamsV220', a)
mm = delayed[a:b].replace('    for(uint32_t m=0;m<p.m;++m)', '    mac.push_back([=]{\n    for(uint32_t m=0;m<p.m;++m)', 1)
mm = mm.rsplit('}\n', 1)[0] + '    });\n}\n'
delayed = delayed[:a] + mm + delayed[b:]
delayed = delayed.replace('template<AscendC::HardEvent E>void Fence(){',
 'template<AscendC::HardEvent E>void Fence(){\n if(E==AscendC::HardEvent::M_FIX)while(!mac.empty()){auto f=mac.front();mac.pop_front();f();}')
delayed = delayed.replace('assert(AscendC::dma.empty()', 'assert(mac.empty());assert(AscendC::dma.empty()')

# Actual reused consumer, with the active AIV owning all rows and the second
# owning zero rows while still returning each two-subcore credit.
a = src.index('// Consume wide GM windows')
b = src.index('__aicore__ inline void ManualCopyC(', a)
consumer = (ROOT / 'tests/cpu/fullk_window_consumer_model.cpp.in').read_text().replace('// INSERT_CONSUMER', src[a:b])
consumer = consumer.replace('BM/2*BN)', 'BM*BN)')
consumer = consumer.replace('st.rows=m>sub*BM/2?std::min(BM/2,m-sub*BM/2):0;', 'st.rows=sub==0?m:0;')
consumer = consumer.replace('slotSize,sub*BM/2,st.rows', 'slotSize,0,st.rows')
consumer = consumer.replace('Value(sub*BM/2+r,c,neg)', 'Value(r,c,neg)')
consumer = consumer.replace('maxima[r/(BM/2)].At(r%(BM/2))', 'maxima[0].At(r)')
consumer = consumer.replace('for(uint32_t bm:{64u,128u})', 'for(uint32_t bm:{32u,48u,64u})')
consumer = consumer.replace('for(uint32_t bn:{32u,64u,128u,256u})', 'for(uint32_t bn:{128u,144u,192u,208u,240u,256u})')
consumer = consumer.replace('for(uint32_t w:{1u,2u,3u,4u,5u,6u,7u,8u})', 'for(uint32_t w:{1u})')

# Restore the complete source, not selected hashes, to verify all old paths.
restored = src[:src.index('// Small TF batches: full inputs in L1')] + src[src.index('// All N-tile partials are ready'):]
restored = restored.replace(', bool SMALL_FULL_INPUTS=false>', '>')
a = restored.index('    if constexpr(SMALL_FULL_INPUTS) {')
b = restored.index('        static_assert(TX1 && TX2', a)
restored = restored[:a] + '    if constexpr(M_FULLK) {\n' + restored[b:]
a = restored.index('    // Full small TF inputs fit L1')
b = restored.index('    // Keep schedule/ring geometry', a)
restored = restored[:a] + restored[b:]
a = restored.index('    if(p.schedule.dual==34) {')
b = restored.index('    if(p.schedule.dual==33) {', a)
restored = restored[:a] + restored[b:]
assert restored == parent, 'unrelated kernel/host/Vector/C9/TT change'

shapes = src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host = src[src.index('struct Plan {'):src.index('using CacheKey =')]
parenthost = parent[parent.index('struct Plan {'):parent.index('using CacheKey =')]
hostmain = r'''
int main(){unsigned count=0,selected=0;auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{1,8,20,32})for(int B:{16,24,31})for(int M:{32,48,63})for(int N:{128,192,255})for(int K:{256,264,384,504})for(int dt:{1,2})for(int lay=0;lay<4;++lay){
  hw->aic=std::max(8,cores);hw->aiv=2*hw->aic;Shape s{B,M,N,K,dt,lay/2,lay%2};
  auto a=Parent::MakePlan(s,cores);auto b=Candidate::MakePlan(s,cores);++count;
  auto x=a.schedule,y=b.schedule;
  if(y.dual==34){++selected;assert(dt==1&&s.tx1&&!s.tx2&&(x.dual==3||x.dual==14));y.dual=x.dual;
   uint64_t KP=Ceil(K,16)*16,NB=std::min<uint64_t>(y.baseN,65536/(2*KP)/16*16);
   assert(NB&&2*(y.baseM+y.baseN)*KP+4096<=hw->l1&&2*y.baseM*KP<=hw->l0a&&2*NB*KP<=hw->l0b&&8ULL*y.baseM*y.baseN<=hw->l0);
   assert(8ULL*y.baseM*y.baseN+20ULL*y.baseM+4096<hw->ub);
   assert(y.mTiles==1&&y.nTiles==1&&y.nSplit==1&&y.window==1);
  }
  assert(std::tie(x.b,x.m,x.n,x.k,x.baseM,x.baseN,x.mTiles,x.nTiles,x.nSplit,x.workers,x.vectorTile,x.window,x.kSplit,x.kChunk,x.microRows,x.batchGroup,x.dual,x.earlySum,x.tree,x.balance)==
         std::tie(y.b,y.m,y.n,y.k,y.baseM,y.baseN,y.mTiles,y.nTiles,y.nSplit,y.workers,y.vectorTile,y.window,y.kSplit,y.kChunk,y.microRows,y.batchGroup,y.dual,y.earlySum,y.tree,y.balance));
  assert(a.totalBytes==b.totalBytes&&a.systemBytes==b.systemBytes&&a.cubeBlocks==b.cubeBlocks&&a.finalBlocks==b.finalBlocks);
 }
 assert(selected);Shape hit{24,48,192,384,1,1,0};
 hw->aic=20;hw->aiv=40;assert(Candidate::MakePlan(hit,20).schedule.dual==34);
 for(auto p:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){
  uint64_t saved=*p;*p=4096;try{assert(Candidate::MakePlan(hit,20).schedule.dual!=34);}catch(const std::runtime_error&){}*p=saved;
 }
#ifdef BMMMS_TUNING
 for(auto p:{&Candidate::Tune().bm,&Candidate::Tune().bn,&Candidate::Tune().window,&Candidate::Tune().ks,&Candidate::Tune().workers,&Candidate::Tune().tree,&Candidate::Tune().dual,&Candidate::Tune().early,&Candidate::Tune().ns}){
  Candidate::Tune()=Candidate::TuneConfig{};*p=1;try{assert(Candidate::MakePlan(hit,20).schedule.dual!=34);}catch(const std::exception&){}
 }
 Candidate::Tune()=Candidate::TuneConfig{};
#endif
 std::cout<<count<<" actual host controls / "<<selected<<" full-input plans, actual capacity/pins, other routes/grid/workspace unchanged PASS\n";
}
'''
stub = (ROOT / 'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {', 'struct TCubeTiling { int stepKa=1,stepKb=1;')
hostmodel = '#include <cstring>\n' + stub + shapes + 'namespace Parent{'+parenthost+'}\nnamespace Candidate{'+host+'}\n'+hostmain

def main():
    print('kernel SHA256:', hashlib.sha256(src.encode()).hexdigest(), flush=True)
    compiler = shutil.which('clang++') or shutil.which('c++')
    with tempfile.TemporaryDirectory(prefix='bmmms-c7-full-input-') as tmp:
        for name, code, flags in [('producer', model, []), ('live-mmad', delayed, []), ('consumer', consumer, []), ('host', hostmodel, []), ('host-tuning', hostmodel, ['-DBMMMS_TUNING'])]:
            cpp, exe = Path(tmp)/(name+'.cpp'), Path(tmp)/name
            cpp.write_text(code)
            subprocess.run([compiler, '-std=c++17', '-O2', *flags, str(cpp), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)
        bad = delayed.replace('AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(free);', '')
        cpp, exe = Path(tmp)/'unsafe.cpp', Path(tmp)/'unsafe'
        cpp.write_text(bad)
        subprocess.run([compiler, '-std=c++17', '-O2', str(cpp), '-o', str(exe)], check=True)
        result = subprocess.run([str(exe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode != 0, 'missing last-reader wait not detected'
        print('Missing last-reader wait correctly rejected PASS')
    print('Old implementations restored byte-for-byte; CANN9/NPU precision/latency PENDING.')

if __name__ == '__main__':
    main()
