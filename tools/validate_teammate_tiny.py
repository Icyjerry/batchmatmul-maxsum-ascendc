#!/usr/bin/env python3
"""Execute transplanted tiny kernels and prove complete scope versus passed parent.

Typed UB and Gather/vector address semantics, delayed MTE2/output; arithmetic
is integer-valued FP32, not native FP16/BF16 encoding, scheduling or timing.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def span(text, start, end):
    a = text.index(start)
    b = text.index(end, a)
    return text[a:b]

def main():
    src = (ROOT/'kernel.asc').read_text()
    parent = subprocess.check_output(['git','show','e1b3634:kernel.asc'],cwd=ROOT,text=True)
    start = '// Short dots keep the complete reduction in UB:'
    end = 'template<typename T>\n__aicore__ inline void DotGroupCopy('
    oldshort, short = span(parent,start,end), span(src,start,end)
    small = span(src,'// One AIV owns a complete batch; K partial sums',
                 'template<typename T,bool TRANSPOSED>\n__aicore__ inline void GemvCopy(')
    host = span(src,'inline uint32_t SmallVectorK256Rows(', 'template <typename T>\ninline void Launch(')
    launch = src[src.index('template <typename T>\ninline void Launch('):]
    oldlaunch = parent[parent.index('template <typename T>\ninline void Launch('):]
    newtiny = span(launch,'    if(p.schedule.dual==16)', '    if (s.m == 1 && s.n == 1)')
    oldtiny = span(oldlaunch,'    if(p.schedule.dual==16)', '    if (s.m == 1 && s.n == 1)')
    vector = span(src,'    const uint32_t vectorRows=SmallVectorK256Rows(s);', '    if(p.schedule.dual==28)')
    newdot = span(src,'        if(p.schedule.dual==15)', '        if(p.schedule.dual==10)')
    olddot = span(parent,'        if(p.schedule.dual==15)', '        if(p.schedule.dual==10)')
    restored = src.replace(short,oldshort).replace(small,'').replace(host,'')
    restored = restored.replace(vector,'').replace(newtiny,oldtiny).replace(newdot,olddot)
    assert restored == parent, 'unrelated large kernels/host/plan/workspace/main/C9/TT changed'
    reference = oldshort.replace('bmmms_dot_short(', 'ReferenceShort(').replace('bmmms_tiny_direct(', 'ReferenceTiny(')
    selector = host[:host.index('template<typename T,bool TX1,bool TX2,uint32_t KCONST>')]
    shape = span(src,'struct Shape {','struct Schedule {')
    code = (ROOT/'tests/cpu/planner_stub.hpp').read_text() + shape
    code += (ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text().replace('// INSERT_KERNELS',reference+short+small+selector)
    maincpp = r'''
struct Inputs {
 std::vector<int16_t> a,b;std::vector<float> y;int16_t* ap;int16_t* bp;
 Inputs(uint32_t B,uint32_t M,uint32_t N,uint32_t K,bool X,bool Y,bool neg):a(B*M*K+32,12345),b(B*N*K+32,12345),y(B+16,1e30f){
  ap=reinterpret_cast<int16_t*>((reinterpret_cast<uintptr_t>(a.data())+31)/32*32);
  bp=reinterpret_cast<int16_t*>((reinterpret_cast<uintptr_t>(b.data())+31)/32*32);
  for(uint32_t z=0;z<B;++z)for(uint32_t k=0;k<K;++k){
   for(uint32_t m=0;m<M;++m)ap[z*M*K+(X?k*M+m:m*K+k)]=int16_t(1+(z*5+m*3+k)%5);
   for(uint32_t n=0;n<N;++n)bp[z*N*K+(Y?n*K+k:k*N+n)]=int16_t(neg?-int(1+(z*7+n*3+k)%7):int((z*7+n*3+k)%11)-5);
  }
  AscendC::globals.clear();AscendC::globals[reinterpret_cast<uintptr_t>(ap)]=B*M*K*2;
  AscendC::globals[reinterpret_cast<uintptr_t>(bp)]=B*N*K*2;
  AscendC::globals[reinterpret_cast<uintptr_t>(y.data()+8)]=B*4;
 }
 void Prepare(){
  assert(AscendC::dma.empty()&&AscendC::outDma.empty());
  AscendC::ub=std::make_shared<std::vector<uint8_t>>(256*1024,0x7f);
  AscendC::manualBytes=0;AscendC::writes.clear();AscendC::lastBytes=0;AscendC::flags.clear();
  std::fill(y.begin(),y.end(),1e30f);
 }
 void Verify(uint32_t B,uint32_t M,uint32_t N,uint32_t K,bool X,bool Y,bool neg){
  assert(AscendC::dma.empty()&&AscendC::outDma.empty());for(auto f:AscendC::flags)assert(f.second==0);
  for(uint32_t z=0;z<B;++z){float sum=0;
   for(uint32_t m=0;m<M;++m){float mx=-INFINITY;
    for(uint32_t n=0;n<N;++n){float dot=0;for(uint32_t k=0;k<K;++k)
     dot+=float(ap[z*M*K+(X?k*M+m:m*K+k)])*float(bp[z*N*K+(Y?n*K+k:k*N+n)]);
     mx=std::max(mx,dot);}
    if(neg)assert(mx<0);sum+=mx;
   }
   assert(y[8+z]==sum&&AscendC::writes.at(reinterpret_cast<uintptr_t>(y.data()+8+z))==1);
  }
  for(int i=0;i<8;++i)assert(y[i]==1e30f&&y[8+B+i]==1e30f);
 }
};
template<bool X,bool Y>void Tiny(uint32_t B,uint32_t M,uint32_t N,uint32_t K,bool neg){
 Inputs in(B,M,N,K,X,Y,neg);const auto a=in.a,b=in.b;
 in.Prepare();AscendC::block=0;ReferenceTiny<int16_t,X,Y>(in.ap,in.bp,in.y.data()+8,Schedule{B,M,N,K});
 in.Verify(B,M,N,K,X,Y,neg);auto ref=in.y;
 in.Prepare();bmmms_tiny_direct<int16_t,X,Y>(in.ap,in.bp,in.y.data()+8,TinyKernelShape{B,M,N,K});
 in.Verify(B,M,N,K,X,Y,neg);assert(in.y==ref&&in.a==a&&in.b==b&&AscendC::manualBytes<=192*1024);
 in.Prepare();switch(K){
  case 32:bmmms_tiny_direct<int16_t,X,Y,32>(in.ap,in.bp,in.y.data()+8,{B,M,N,K});break;
  case 40:bmmms_tiny_direct<int16_t,X,Y,40>(in.ap,in.bp,in.y.data()+8,{B,M,N,K});break;
  case 48:bmmms_tiny_direct<int16_t,X,Y,48>(in.ap,in.bp,in.y.data()+8,{B,M,N,K});break;
  case 56:bmmms_tiny_direct<int16_t,X,Y,56>(in.ap,in.bp,in.y.data()+8,{B,M,N,K});break;
  case 64:bmmms_tiny_direct<int16_t,X,Y,64>(in.ap,in.bp,in.y.data()+8,{B,M,N,K});break;
 }in.Verify(B,M,N,K,X,Y,neg);assert(in.y==ref&&in.a==a&&in.b==b);
}
template<bool X,bool Y>bool Small(uint32_t B,uint32_t M,uint32_t N,uint32_t K,uint32_t chunk,bool neg){
 const uint32_t cap=SmallVectorK256Rows(Shape{B,M,N,K,1,X,Y});
 if(!cap||chunk>cap)return false;
 Inputs in(B,M,N,K,X,Y,neg);const auto a=in.a,b=in.b;in.Prepare();
 for(uint32_t z=0;z<B;++z){AscendC::block=z;
  AscendC::ub=std::make_shared<std::vector<uint8_t>>(256*1024,0x7f);
  bmmms_small_vector_k256<int16_t,X,Y>(in.ap,in.bp,in.y.data()+8,{M,N,K,chunk});
 }
 in.Verify(B,M,N,K,X,Y,neg);assert(in.a==a&&in.b==b);
 assert(AscendC::manualBytes+1024<=platform_ascendc::PlatformAscendCManager::GetInstance()->ub);return true;
}
void Short(uint32_t B,uint32_t K,bool neg){
 Inputs in(B,1,1,K,false,false,neg);const auto a=in.a,b=in.b;
 for(bool aligned:{false,true}){
  if(aligned&&K%16)continue;in.Prepare();
  for(uint32_t z=0;z<(B+7)/8;++z){AscendC::block=z;
   AscendC::ub=std::make_shared<std::vector<uint8_t>>(8256,0x7f);
   if(aligned)bmmms_dot_short<int16_t,true>(in.ap,in.bp,in.y.data()+8,B,K);
   else bmmms_dot_short<int16_t>(in.ap,in.bp,in.y.data()+8,B,K);
  }in.Verify(B,1,1,K,false,false,neg);assert(in.a==a&&in.b==b);
 }
 in.Prepare();for(uint32_t z=0;z<(B+7)/8;++z){AscendC::block=z;ReferenceShort<int16_t>(in.ap,in.bp,in.y.data()+8,Schedule{B,1,1,K});}
 in.Verify(B,1,1,K,false,false,neg);
}
int main(){unsigned tiny=0,small=0,shorts=0;
 for(uint32_t B:{1u,2u,3u})for(uint32_t M:{1u,2u,3u,5u,8u})for(uint32_t N:{1u,4u,7u,8u,15u,16u})
 for(uint32_t K:{32u,40u,48u,56u,64u})for(bool neg:{false,true}){
  Tiny<false,false>(B,M,N,K,neg);Tiny<false,true>(B,M,N,K,neg);Tiny<true,false>(B,M,N,K,neg);Tiny<true,true>(B,M,N,K,neg);tiny+=4;
 }
 for(uint32_t B:{1u,3u})for(uint32_t M:{2u,3u,7u,16u})for(uint32_t N:{2u,7u,16u,31u,32u})
 for(uint32_t K:{72u,88u,128u,136u,192u,248u,256u})for(uint32_t chunk:{1u,3u,M})for(bool neg:{false,true}){
  small+=Small<false,false>(B,M,N,K,chunk,neg);small+=Small<false,true>(B,M,N,K,chunk,neg);
  small+=Small<true,false>(B,M,N,K,chunk,neg);small+=Small<true,true>(B,M,N,K,chunk,neg);
 }
 for(uint32_t B:{1u,3u,7u,8u,9u,15u,16u,31u,64u})for(uint32_t K:{32u,40u,48u,56u,64u})for(bool neg:{false,true}){
  Short(B,K,neg);++shorts;
 }
 std::cout<<tiny<<" actual tiny dynamic/specialized + parent comparisons / "<<small<<" actual K65..256 chunked kernels / "<<shorts<<" short-dot aligned/fallback/parent cases PASS\n";
 std::cout<<"Four storage layouts, K8/N/M tails, all-negative, typed UB bounds/poison, delayed DMA, complete K then Max then Sum, unique y/guards and input immutability PASS\n";
}
'''
    code += maincpp
    tune = span(src,'#ifdef BMMMS_TUNING\nstruct TuneConfig', '// ---- forced dispatch')
    hostcpp = (ROOT/'tests/cpu/planner_stub.hpp').read_text() + shape + tune + selector + r'''
int main(){unsigned count=0,selected=0;auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{8,20,64})for(uint64_t ub:{8192ull,65536ull,196608ull,262144ull})
 for(int B:{1,4,9,32,64})for(int M:{1,2,7,15,16,17})for(int N:{1,2,7,16,31,32,33})
 for(int K:{32,64,72,128,136,248,256,264})for(int dt:{1,2})for(int lay=0;lay<4;++lay){
  hw->aiv=cores;hw->ub=ub;Shape s{B,M,N,K,dt,lay/2,lay%2};auto rows=SmallVectorK256Rows(s);++count;
  if(rows){++selected;assert(B<=cores&&M>=2&&M<=16&&N>=2&&N<=32&&K>64&&K<=256&&!(M>=16&&N>=16)&&rows<=M);
   uint64_t kp=Ceil(K,16)*16,np=Ceil(N,8)*8;
   uint64_t fixed=6*(M+N)*kp+(s.tx1?Ceil(M*K,16)*16*4:32)+(!s.tx2?Ceil(N*K,16)*16*4:32)+3*256*4+64;
   auto bytes=[&](uint32_t r){return fixed+r*(np*kp*4+np*8)+Ceil(r,8)*32;};
   assert(bytes(rows)+1024<=ub);if(rows<M)assert(bytes(rows+1)+1024>ub);
  }
 }
 assert(selected);
#ifdef BMMMS_TUNING
 hw->aiv=40;hw->ub=196608;Shape hit{4,7,7,256,1,1,0};assert(SmallVectorK256Rows(hit));
 for(auto p:{&Tune().group,&Tune().rows,&Tune().dual,&Tune().early,&Tune().tree,&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,&Tune().workers}){
  Tune()=TuneConfig{};*p=1;assert(SmallVectorK256Rows(hit)==0);
 }Tune()=TuneConfig{};
#endif
 std::cout<<count<<" actual small Vector selector controls / "<<selected<<" selections, physical AIV/UB/chunk capacities, preserved explicit tuning PASS\n";
}
'''
    compiler = shutil.which('clang++') or shutil.which('c++')
    print('kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
    with tempfile.TemporaryDirectory(prefix='bmmms-teammate-tiny-') as tmp:
        cpp,exe=Path(tmp)/'model.cpp',Path(tmp)/'model'
        cpp.write_text(code)
        subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
        for flags in [[],['-DBMMMS_TUNING']]:
            hcpp,hexe=Path(tmp)/'host.cpp',Path(tmp)/'host'
            hcpp.write_text(hostcpp)
            subprocess.run([compiler,'-std=c++17','-O2',*flags,str(hcpp),'-o',str(hexe)],check=True)
            subprocess.run([str(hexe)],check=True)
        unsafe=code.replace('    AscendC::PipeBarrier<PIPE_ALL>();','')
        assert unsafe!=code
        cpp.write_text(unsafe)
        subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],capture_output=True)
        assert r.returncode!=0,'missing output completion not detected'
        print('Missing output completion correctly rejected PASS')
        unsafe=code.replace('    AscendC::Duplicate(row,0.0f,ar*8);','')
        assert unsafe!=code
        cpp.write_text(unsafe)
        subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],capture_output=True)
        assert r.returncode!=0,'missing sparse Sum identities not detected'
        print('Missing sparse row Sum identities correctly rejected PASS')
    print('Scope proof: complete parent restored, host plans/GM/C9/TT unchanged. CANN9/NPU precision/performance PENDING.')

if __name__=='__main__':
    main()
