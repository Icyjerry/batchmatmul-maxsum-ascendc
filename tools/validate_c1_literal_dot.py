#!/usr/bin/env python3
"""Actual literal dot, delayed DMA and host dispatch; not native FP encoding/time."""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
from validate_c7_manual_frame import span, source
from validate_c10_balanced_m_shards import host as host_prefix
ROOT=Path(__file__).resolve().parents[1]
LAUNCH='''            if(aligned && UseLiteralDot(s,p)) {
                bmmms_dot_one_k32<T><<<p.finalBlocks,nullptr,stream>>>(x1,x2,y);
                return;
            }
'''

def scope(s):
 new=span(s,'// One K32 dot has no batch geometry','// Short dots keep the complete reduction in UB:')
 helper=span(s,'inline bool UseLiteralDot(', 'using CacheKey =')
 assert s.count(LAUNCH)==1
 assert s.replace(new,'',1).replace(helper,'',1).replace(LAUNCH,'',1)==source('a2e6763')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return new,span(s,'// Short dots keep the complete reduction in UB:','struct TinyKernelShape')

def device(new,old):
 f=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text().replace('// INSERT_KERNELS',new+old)
 return f+r'''
void Run(unsigned seed,unsigned poison,bool neg){
 std::vector<int16_t> a(64,12345),b(64,12345);
 auto* ap=reinterpret_cast<int16_t*>((reinterpret_cast<uintptr_t>(a.data())+31)/32*32);
 auto* bp=reinterpret_cast<int16_t*>((reinterpret_cast<uintptr_t>(b.data())+31)/32*32);
 float gold=0;for(unsigned k=0;k<32;++k){ap[k]=1+(seed*7+k*3)%17;
  bp[k]=neg?-int16_t(1+(seed*11+k*5)%23):int16_t(int((seed*13+k*7)%31)-15);
  gold+=float(ap[k])*float(bp[k]);}
 auto aa=a,bb=b;std::vector<float> y(17,1e30f);float reference=0;
 for(bool literal:{false,true}){
  AscendC::globals.clear();AscendC::globals[uintptr_t(ap)]=64;AscendC::globals[uintptr_t(bp)]=64;
  AscendC::globals[uintptr_t(y.data()+8)]=4;
  AscendC::ub=std::make_shared<std::vector<uint8_t>>(literal?544:8256,poison);
  AscendC::manualBytes=0;AscendC::writes.clear();AscendC::flags.clear();AscendC::block=0;
  std::fill(y.begin(),y.end(),1e30f);
  if(literal)bmmms_dot_one_k32<int16_t>(ap,bp,y.data()+8);
  else bmmms_dot_short<int16_t,true>(ap,bp,y.data()+8,1,32);
  assert(AscendC::dma.empty()&&AscendC::outDma.empty());for(auto flag:AscendC::flags)assert(!flag.second);
  assert(AscendC::manualBytes==(literal?544:8256));assert(y[8]==gold&&a==aa&&b==bb);
  assert(AscendC::writes.size()==1&&AscendC::writes.at(uintptr_t(y.data()+8))==1);
  if(neg)assert(y[8]<0);if(literal)assert(y[8]==reference);else reference=y[8];
  for(unsigned j=0;j<y.size();++j)if(j!=8)assert(y[j]==1e30f);
 }
}
int main(){unsigned n=0;for(unsigned seed=0;seed<64;++seed)for(unsigned poison:{0u,0x7fu,0xa5u,0xffu})
 for(bool neg:{false,true}){Run(seed,poison,neg);++n;}
 std::cout<<n<<" actual literal/parent pairs: K-varying/negative, exact UB slices/poison, delayed DMA, one y/guards, input immutability PASS\n";
}
'''

def host(s):
 f=host_prefix(s).split('int main(){')[0]
 launch=span(s,'        if(p.schedule.dual==15)', '        if(p.schedule.dual==10)')
 launch=launch.replace('<<<p.finalBlocks,nullptr,stream>>>','')
 return f+r'''
using GM_ADDR=void*;unsigned literalCalls=0,oldCalls=0;bool oldAligned=false;
template<class T>void bmmms_dot_one_k32(GM_ADDR,GM_ADDR,GM_ADDR){++literalCalls;}
template<class T,bool A=false>void bmmms_dot_short(GM_ADDR,GM_ADDR,GM_ADDR,uint32_t,uint32_t){++oldCalls;oldAligned=A;}
template<class T>void TestLaunch(GM_ADDR x1,GM_ADDR x2,GM_ADDR y,const Shape& s,const Plan& p){
'''+launch+r'''
}
int main(){unsigned n=0,hits=0;auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{1,20,32})for(int b:{1,2,8})for(int m:{1,2})for(int cols:{1,2})for(int k:{32,40,64})
 for(int dt:{1,2})for(int lay=0;lay<4;++lay){
  hw->aic=cores;hw->aiv=2*cores;Shape s{b,m,cols,k,dt,lay/2,lay%2};auto p=MakePlan(s,cores);
  bool shape=b==1&&m==1&&cols==1&&k==32;
  assert(UseLiteralDot(s,p)==shape);
  for(uintptr_t a:{0u,2u,16u})for(uintptr_t bOffset:{0u,2u,16u}){
   literalCalls=oldCalls=0;TestLaunch<int16_t>((void*)(0x1000+a),(void*)(0x2000+bOffset),(void*)0x3000,s,p);++n;
   bool hit=shape&&!a&&!bOffset;hits+=hit;assert(literalCalls==hit);
   assert(oldCalls==(p.schedule.dual==15&&!hit));
   if(oldCalls)assert(oldAligned==(k%16==0&&!a&&!bOffset));
  }
 }
 hw->aic=20;hw->aiv=40;Shape s{1,1,1,32,1,0,0};auto p=MakePlan(s,20);assert(UseLiteralDot(s,p));
 hw->ub=544;assert(UseLiteralDot(s,p));hw->ub=543;assert(!UseLiteralDot(s,p));hw->ub=196608;
 hw->aiv=0;assert(!UseLiteralDot(s,p));hw->aiv=40;
 for(auto field:{&p.schedule.b,&p.schedule.m,&p.schedule.n,&p.schedule.k}){++*field;assert(!UseLiteralDot(s,p));--*field;}
 ++p.finalBlocks;assert(!UseLiteralDot(s,p));--p.finalBlocks;++p.schedule.dual;assert(!UseLiteralDot(s,p));--p.schedule.dual;
#ifdef BMMMS_TUNING
 for(auto field:{&Tune().group,&Tune().rows,&Tune().dual,&Tune().early,&Tune().tree,&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,&Tune().workers}){
  Tune()=TuneConfig{};*field=1;assert(!UseLiteralDot(s,p));literalCalls=oldCalls=0;
  TestLaunch<int16_t>((void*)0x1000,(void*)0x2000,(void*)0x3000,s,p);assert(!literalCalls&&oldCalls==1);
 }Tune()=TuneConfig{};
#endif
 assert(hits);std::cout<<n<<" actual host plan+launch configurations/"<<hits<<" literal hits, four layouts/two dtypes/alignment fallback/UB543-544/core/pins PASS\n";
}
'''

def main():
 s=(ROOT/'kernel.asc').read_text();new,old=scope(s);d=device(new,old);h=host(s)
 print('kernel SHA256',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 cc=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c1-literal-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([cc,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  run('device',d);run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
  controls=[('completion','AscendC::PipeBarrier<PIPE_ALL>();',''),
   ('FP-alias','VECCALC,128,64','VECCALC,96,64'),
   ('y-overrun','op{1,4,0,0,0}','op{1,8,0,0,0}'),
   ('input-overread','AscendC::DataCopy(raw[32],b,32);','AscendC::DataCopy(raw[32],b,64);'),
   ('input-ready','AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(0);\n    AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(0);','')]
  for name,a,b in controls:
   assert a in new,name;bad=new.replace(a,b,1);run('bad-'+name,device(bad,old),True)
  print('Five completion/alias/output/input/readiness controls rejected PASS')
 print('Whole inverse parent/protected7 proof; native CANN9/FP16-BF16/Vector scheduling/latency/route PENDING.')
if __name__=='__main__':main()
