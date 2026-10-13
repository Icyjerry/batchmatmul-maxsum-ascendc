#!/usr/bin/env python3
"""Actual compact-K helper versus retained helper and independent complete dots."""
from pathlib import Path
import subprocess,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
START='__aicore__ inline void SmallVectorManualIndex('
END='template<typename T,bool TRANSPOSED>\n__aicore__ inline void GemvCopy'
EXTRA=r'''
namespace AscendC {
void MulAddDst(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint64_t mask,uint32_t reps,BinaryRepeatParams p){
 assert(mask>0&&mask<=64&&reps<=255&&dst.offset%32==0&&a.offset%32==0&&b.offset%32==0);
 assert(p.dstBlk==1&&p.src0Blk==1&&p.src1Blk==1);
 for(unsigned r=0;r<reps;++r)for(unsigned i=0;i<mask;++i){size_t d=r*p.dstRep*8+i;
  dst.write(d,dst.read(d)+a.read(r*p.src0Rep*8+i)*b.read(r*p.src1Rep*8+i));}
}
}
'''
MAIN=r'''
int main(){
 constexpr unsigned B=4,M=8,N=16,K=128;
 for(unsigned seed=0;seed<12;++seed)for(unsigned negative=0;negative<2;++negative)for(unsigned chunk:{1u,3u,8u}){
  std::vector<int16_t>a(B*M*K+32),b(B*N*K+32);std::vector<float>y(B+16,1e30f),ref;
  auto ap=reinterpret_cast<int16_t*>((reinterpret_cast<uintptr_t>(a.data())+31)/32*32);
  auto bp=reinterpret_cast<int16_t*>((reinterpret_cast<uintptr_t>(b.data())+31)/32*32);
  for(unsigned z=0;z<B;++z)for(unsigned k=0;k<K;++k){
   for(unsigned m=0;m<M;++m)ap[z*M*K+k*M+m]=1+(seed+z*5+m*3+k)%5;
   for(unsigned n=0;n<N;++n)bp[z*N*K+n*K+k]=negative?-int(1+(seed+z*7+n*3+k)%7):int((seed+z*7+n*3+k)%11)-5;
  }
  auto aa=a,bb=b;
  AscendC::globals.clear();AscendC::globals[reinterpret_cast<uintptr_t>(ap)]=B*M*K*2;
  AscendC::globals[reinterpret_cast<uintptr_t>(bp)]=B*N*K*2;
  AscendC::globals[reinterpret_cast<uintptr_t>(y.data()+8)]=B*4;
  for(unsigned mode=0;mode<3;++mode){
   std::fill(y.begin(),y.end(),1e30f);AscendC::writes.clear();AscendC::flags.clear();AscendC::manualBytes=0;
   for(unsigned z=0;z<B;++z){AscendC::block=z;AscendC::ub=std::make_shared<std::vector<uint8_t>>(196352,0x7f);
    if(mode==0)Parent<int16_t,true,true>(ap,bp,y.data()+8,{M,N,K,chunk});
    else if(mode==1)bmmms_small_vector_k256<int16_t,true,true,false>(ap,bp,y.data()+8,{M,N,K,chunk});
    else bmmms_small_vector_k256<int16_t,true,true,true>(ap,bp,y.data()+8,{M,N,K,chunk});
   }
   assert(AscendC::dma.empty()&&AscendC::outDma.empty());for(auto f:AscendC::flags)assert(f.second==0);
   for(unsigned z=0;z<B;++z){float sum=0;
    for(unsigned m=0;m<M;++m){float mx=-INFINITY;
     for(unsigned n=0;n<N;++n){float dot=0;for(unsigned k=0;k<K;++k)dot+=float(ap[z*M*K+k*M+m])*float(bp[z*N*K+n*K+k]);mx=std::max(mx,dot);}
     if(negative)assert(mx<0);sum+=mx;
    }
    assert(y[8+z]==sum&&AscendC::writes.at(reinterpret_cast<uintptr_t>(y.data()+8+z))==1);
   }
   for(unsigned i=0;i<8;++i)assert(y[i]==1e30f&&y[B+8+i]==1e30f);
   if(mode==0)ref=y;else assert(y==ref);assert(a==aa&&b==bb&&AscendC::manualBytes<=196352);
  }
 }
 std::cout<<"Actual parent/default/compact helper:72 mixed/negative/chunk fixtures,216 launchesets, full dots/guards/inputs PASS\n";
}
'''
def main():
 s=(ROOT/'kernel.asc').read_text();old=subprocess.check_output(['git','show','e2f1b63:kernel.asc'],cwd=ROOT,text=True)
 a=s.index(START);b=s.index(END,a);oa=old.index(START);ob=old.index(END,oa)
 h=s[a:b];parent=old[oa:ob];parent=parent[parent.index('template<typename T,bool TX1,bool TX2>'):].replace('bmmms_small_vector_k256','Parent')
 guard='''if(s.dtype==2&&s.b==4&&s.m==8&&s.n==16&&s.k==128&&s.tx1&&s.tx2&&vectorRows==8){
bmmms_small_vector_k256<T,true,true,true><<<blocks,nullptr,stream>>>(x1,x2,y,v);
return;
}
'''
 assert guard in s;inverse=(s[:a]+old[oa:ob]+s[b:]).replace(guard,'',1);assert inverse==old
 for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=ROOT)
 stub=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
 with tempfile.TemporaryDirectory(prefix='bmmms-c4-compact-') as temp:
  p=Path(temp);code=stub.replace('// INSERT_KERNELS',EXTRA+h+parent)+MAIN;(p/'model.cpp').write_text(code)
  subprocess.run(['c++','-std=c++17','-O2',str(p/'model.cpp'),'-o',str(p/'model')],check=True);subprocess.run([str(p/'model')],check=True)
  fault=h.replace('fa[(m0+m)*kp+64],fb[64]','fa[(m0+m)*kp],fb[64]');assert fault!=h
  (p/'fault.cpp').write_text(stub.replace('// INSERT_KERNELS',EXTRA+fault+parent)+MAIN)
  subprocess.run(['c++','-std=c++17','-O2',str(p/'fault.cpp'),'-o',str(p/'fault')],check=True)
  r=subprocess.run([str(p/'fault')],stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert r.returncode!=0
 print('Source inverse/protected7/wrong K half negative control PASS',hashlib.sha256(s.encode()).hexdigest())
 print('Integer-valued FP32 model, not BF16/native API/events/timing evidence.')
if __name__=='__main__':main()
