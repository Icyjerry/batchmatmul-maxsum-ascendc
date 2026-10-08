#!/usr/bin/env python3
"""Actual manual FF producer in an integer physical-layout/queue model.

Queue allocation waits for the last MTE1 reader: an explicit assumed native
TQue contract, NOT a validation of CANN implementation or hardware timing.
"""
from pathlib import Path
import hashlib,re,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 old=source('af886e1')
 e=span(s,'// The basic-API path owns','// Resident A and larger B packages')
 p=span(old,'// The basic-API path owns','// Resident A and larger B packages')
 assert e[e.index('#else\n    AscendC::TQue'):]==p[p.index('#else\n    AscendC::TQue'):], 'Vector changed'
 h=span(s,'// Keep the exact FF plan','struct Case9PackagePlan')
 launch=span(s,'    if(UseC10BPackages(s,p)) {','    if(p.schedule.dual==20 && s.dtype==1')
 assert s.replace(e,p,1).replace(h,'',1).replace(launch,'',1)==old
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e

def model(s,e):
 f=(ROOT/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
 f=f.replace('window=1;', 'window=1,kChunk=64,dual=20,tree=8;')
 f=f.replace('MTE2_MTE1};','MTE2_MTE1,MTE1_MTE2};').replace('next[5]','next[6]')
 f=f.replace('namespace AscendC {','namespace AscendC {\nvoid SetAtomicNone(){}\nvoid SetLoadDataBoundary(uint64_t){}\nvoid SetLoadDataPaddingValue(uint64_t){}',1)
 # Storage remains live until commands execute. A released B1 queue slot may
 # be logically free while its final Load2D has not completed.
 f=f.replace('bool pending=false;', 'bool pending=false;uint32_t readers=0;')
 f=f.replace('std::deque<Pending> dma;', 'std::deque<Pending> dma;\nstd::deque<std::function<void()>> mte1,mac;\nvoid Step(std::deque<std::function<void()>>& q){assert(!q.empty());auto x=q.front();q.pop_front();x();}')
 f=f.replace('if(!used[i]){used[i]=true;', 'if(!used[i]){while(mem[i]->readers)Step(mte1);used[i]=true;')
 f=f.replace('assert(!dst.mem->pending);dst.mem->pending=true;', 'assert(!dst.mem->pending && !dst.mem->readers);dst.mem->pending=true;')
 f=f.replace('template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}', '''template<HardEvent E>void SetFlag(int i){
 auto mark=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};
 if(E==HardEvent::M_MTE1)mac.push_back(mark);
 else if(E==HardEvent::MTE1_M)mte1.push_back(mark);else mark();
}''')
 f=f.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);', '''    if(E==HardEvent::MTE1_M)while(!st.events[std::make_pair(int(E),i)])Step(mte1);
    if(E==HardEvent::M_MTE1)while(!st.events[std::make_pair(int(E),i)])Step(mac);
    assert(st.events[std::make_pair(int(E),i)]--==1);''')
 a=f.index('void LoadData(LocalTensor<half>');b=f.index('struct MmadParams',a)
 f=f[:a]+'''void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 assert(!p.enTranspose&&dst.mem->pos==TPosition::A2&&src.mem->pos==TPosition::A1&&!src.mem->pending);
 uint32_t rows=p.mExtension,count=p.kExtension;
 assert(p.l1H==1&&rows==p.l1W&&count%16==0&&p.kStartPt+count<=p.channelSize);
 ++src.mem->readers;
 mte1.push_back([=]{
 for(uint32_t m=0;m<rows;++m)for(uint32_t k=0;k<count;++k){
  uint32_t logicalK=p.kStartPt+k;
  dst.at(((m/16)*(count/16)+k/16)*256+(m%16)*16+k%16)=
   src.at((logicalK/16)*p.l1W*16+m*16+logicalK%16);
 }assert(src.mem->readers--);
 });st.aL0+=uint64_t(rows)*count;++st.aLoads;
}
'''+f[b:]
 a=f.index('template<class T>void LoadData(');b=f.index('template<class T>struct LoadData3DParamsV2',a)
 t=f[a:b];t=t.replace('    for(uint32_t r=0;', '    ++src.mem->readers;mte1.push_back([=]{\n    for(uint32_t r=0;',1)
 t=t.replace('    (dst.mem->pos', '    assert(src.mem->readers--);});\n    (dst.mem->pos',1)
 f=f[:a]+t+f[b:]
 a=f.index('template<class T>void Mmad(');b=f.index('struct FixpipeParamsV220',a)
 t=f[a:b].replace('    for(uint32_t m=0;', '    mac.push_back([=]{\n    for(uint32_t m=0;',1)
 t=t.rsplit('}\n',1)[0]+'    });\n}\n';f=f[:a]+t+f[b:]
 f=f.replace('template<AscendC::HardEvent E>void Fence(){}', '''template<AscendC::HardEvent E>void Fence(){
 if(E==AscendC::HardEvent::MTE2_MTE1)while(!AscendC::dma.empty())AscendC::Flush(AscendC::dma.front().mem);
 if(E==AscendC::HardEvent::MTE1_MTE2)while(!AscendC::mte1.empty())AscendC::Step(AscendC::mte1);
 if(E==AscendC::HardEvent::M_FIX)while(!AscendC::mac.empty())AscendC::Step(AscendC::mac);
}''')
 zero=span(s,'template<typename T>\n__aicore__ inline void ManualZeroNZTail','__aicore__ inline void SmallRowMaxLaneFold')
 copy=span(s,'template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>','// One full-M accumulator:')
 body=span(e,'    uint32_t bk=256;','\n#else\n    AscendC::TQue').rsplit('    }',1)[0]
 producer='''template<class T,bool PAD_MN,uint32_t B_PACKAGE>
void RunCase9(AscendC::TPipe& pipe,AscendC::GlobalTensor<T> a,AscendC::GlobalTensor<T> b,
 AscendC::GlobalTensor<float> ring,Schedule s,uint32_t worker,uint32_t unused){
 constexpr bool TX1=false,TX2=false,RESIDENT_PAD=true,FULL_A=false,RESIDENT_B=false;
 const uint32_t span=1,slots=2,slotSize=s.baseM*s.baseN;
 const int64_t tasks=s.b*s.mTiles*s.nSplit;uint32_t sequence=0;
'''+body+'\n}\n'
 main=(ROOT/'tests/cpu/c9_packages_model.cpp.in').read_text().split('int main()')[0]
 main=main.replace('template<bool PAD>','template<bool PAD,uint32_t PACK>')
 main=main.replace('assert(package>s.kChunk&&package%s.kChunk==0);','assert(package>=s.kChunk&&package%s.kChunk==0);')
 main=main.replace('b[z*s.n*s.k+n*s.k+k]', 'b[z*s.n*s.k+k*s.n+n]')
 main=main.replace('st.tx2=true;', 'st.tx2=false;')
 main=main.replace('RunCase9<int16_t,PAD>', 'RunCase9<int16_t,PAD,PACK>')
 main=main.replace('st.bLoads==st.mmads', 'st.bLoads==tiles*((s.k+15)/16)')
 main=main.replace('assert(AscendC::dma.empty());', 'assert(AscendC::dma.empty()&&AscendC::mte1.empty()&&AscendC::mac.empty());')
 main=main.replace(' assert(a==oldA', ' std::cout<<"M="<<s.m<<" N="<<s.n<<" K="<<s.k<<" package="<<package<<" Bcopies="<<bCopies<<" MMAD="<<mmads<<" readsB="<<readsB<<"\\n";\n assert(a==oldA')
 main+='''int main(){
 Schedule exact{1,4096,1280,1152,128,256,0,0,1,20,0,0};
 Run<true,192>(exact,192,false);
 Schedule proxy{2,145,273,1152,128,256,0,0,1,3,0,0};
 Run<true,192>(proxy,192,true);Run<true,0>(proxy,64,true);
 for(int k:{64,192,256,448,528}){
  Schedule t{2,33,273,k,32,256,0,0,1,3,0,0};
  Run<true,192>(t,192,true);
 }
 std::cout<<"8 actual FF producers: live B1/L0/C, actual package K pitch, negative Max/Sum, input/ring bounds PASS\\n";
}
'''
 return f.replace('// INSERT_HELPERS',zero+copy+producer)+main

def host(s):
 headers='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in ['C7KernelShape','WideNKernelShape','TTFrameShape','C13ResidentFrame'])
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 return stub+span(s,'struct Shape {','template <AscendC::HardEvent')+headers+span(s,'struct Plan {','using CacheKey =')+r'''
int main(){auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();unsigned n=0,hits=0;
 for(int cores:{1,3,8,20,32})for(int dt:{1,2})for(int x:{0,1})for(int y:{0,1}){
  hw->aic=cores;hw->aiv=2*cores;Shape s{1,4096,1280,1152,dt,x,y};auto p=MakePlan(s,cores);
  bool hit=UseC10BPackages(s,p);assert(hit==(dt==2&&!x&&!y));++n;hits+=hit;
 }
 Shape s{1,4096,1280,1152,2,0,0};hw->aic=20;hw->aiv=40;auto p=MakePlan(s,20);assert(UseC10BPackages(s,p));
 for(auto field:{&s.b,&s.m,&s.n,&s.k}){++*field;assert(!UseC10BPackages(s,p));--*field;}
 for(auto field:{&p.schedule.baseM,&p.schedule.baseN,&p.schedule.kChunk,&p.schedule.tree,
  &p.schedule.mTiles,&p.schedule.nTiles,&p.schedule.nSplit,&p.schedule.kSplit,&p.schedule.window}){
  ++*field;assert(!UseC10BPackages(s,p));--*field;
 }
 for(auto field:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){auto old=*field;*field=1024;assert(!UseC10BPackages(s,p));*field=old;}
 hw->l1=128ULL*1152*2+256ULL*192*4+2048+4096;assert(UseC10BPackages(s,p));--hw->l1;assert(!UseC10BPackages(s,p));hw->l1=512*1024;
 p.totalBytes=p.systemBytes+16384+uint64_t(p.schedule.workers)*262144;assert(UseC10BPackages(s,p));--p.totalBytes;assert(!UseC10BPackages(s,p));
#ifdef BMMMS_TUNING
 for(auto field:{&Tune().group,&Tune().rows,&Tune().dual,&Tune().early,&Tune().tree,&Tune().bm,&Tune().bn,
 &Tune().window,&Tune().ns,&Tune().ks,&Tune().workers}){
  Tune()=TuneConfig{};*field=1;auto q=MakePlan(s,20);assert(!UseC10BPackages(s,q));
 }Tune()=TuneConfig{};
#endif
 std::cout<<n<<" actual host plans/"<<hits<<" selections, exact guard, resource/GM one-byte boundaries and pins PASS\n";
}
'''

def main():
 s=(ROOT/'kernel.asc').read_text();e=scope(s);f=model(s,e);h=host(s)
 print('kernel SHA256',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c10-ff-') as t:
  for name,code,flags in [('producer',f,[]),('host',h,[]),('host-tuning',h,['-DBMMMS_TUNING'])]:
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
  # Proxy-only fault controls, keeping full-shape computation out of each control.
  proxy=f.replace('Run<true,192>(exact,192,false);','')
  controls={'pitch':('((bCount+15)/16)','(count/16)'),
    'offset':('(B_PACKAGE?(k0-bStart)*16:0)','0'),
    'release':('if(k0+bk>=bStart+bCount)','if(true)'),
    'last-reader':('while(mem[i]->readers)Step(mte1);',''),
    'L0-ready':('AscendC::WaitFlag<AscendC::HardEvent::MTE1_M>(loadReady[ks]);',''),
    'C-ready':('Fence<AscendC::HardEvent::M_FIX>();','')}
  for name,(a,b) in controls.items():
   assert a in proxy;bad=proxy.replace(a,b,1);cpp,exe=Path(t)/'bad.cpp',Path(t)/'bad';cpp.write_text(bad)
   subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   assert r.returncode,'control did not fail: '+name
   print('rejected control:',name,flush=True)
 print('Vector/Plan/all other source and protected7 byte unchanged; native TQue/CANN/precision/latency PENDING.')
if __name__=='__main__':main()
