#!/usr/bin/env python3
"""Whole-M B reuse in actual manual source; integer models, not NPU timing."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_c10_balanced_m_shards import cube as make_cube,ownership as make_ownership,host as make_host
ROOT=Path(__file__).resolve().parents[1]
OLD='''    if(UseBalancedMShards(s,p)) {
        bmmms_manual<T,false,false,true,true,false,false,false,false,false,false,true><<<p.cubeBlocks,nullptr,stream>>>(
            x1,x2,partial,y,p.schedule);
        return;
    }'''
NEW='''    if(UseBalancedMShards(s,p)) {
        Schedule shard;
        const bool full=MakeFullMShard(s,p,shard);
        bmmms_manual<T,false,false,true,true,false,false,false,false,false,false,true><<<p.cubeBlocks,nullptr,stream>>>(
            x1,x2,partial,y,full?shard:p.schedule);
        return;
    }'''
def scope(s):
 h=span(s,'// Hold the complete balanced M shard','struct Case9PackagePlan')
 assert s.count(NEW)==1 and s.replace(h,'',1).replace(NEW,OLD,1)==source('a2e6763')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return span(s,'// The basic-API path owns','// Resident A and larger B packages'),span(s,'// Partition actual M rows','// The basic-API path owns')

def cube(s,e,h):
 f=make_cube(s,e,h)
 f=f[:f.index('int main(){')]
 # Model the actual unchanged ring offset on the original arena, including
 # increased aligned partial prefix and smaller per-worker C rings.
 layout=span(e,'    const uint32_t span=M_FULLK','\n#ifdef __DAV_CUBE__')
 f=f.replace(' uint64_t mmads=0,breads=0,bcopies=0,maxRows=0,expectedRows=0,tiles=0;',
  ' uint64_t mmads=0,breads=0,bcopies=0,maxRows=0,expectedRows=0,tiles=0,aloads=0,bloads=0;\n std::vector<float> arena(((s.m+127)/128*128)+s.workers*2*128*256+16,1e30f);')
 f=f.replace('  st=State{};', '  constexpr bool M_FULLK=false,FULL_A=false;\n'+layout+'\n  const size_t base=alignedCount+int64_t(worker)*slots*slotSize;\n  assert(base+2*slotSize+16<=arena.size());\n  st=State{};',1)
 f=f.replace('size_t((sequence&1)*s.baseM*s.baseN)', 'size_t(base+(sequence&1)*s.baseM*s.baseN)')
 f=f.replace('  std::vector<float> ring(2*s.baseM*s.baseN+16,1e30f);AscendC::TPipe pipe;',
  '  AscendC::TPipe pipe;')
 f=f.replace('{&ring},s,worker,64','{&arena,base},s,worker,64')
 f=f.replace('  for(size_t i=2*s.baseM*s.baseN;i<ring.size();++i)assert(ring[i]==1e30f);',
  '  for(size_t i=0;i<alignedCount;++i)assert(arena[i]==1e30f);\n  for(size_t i=base+2*slotSize;i<arena.size();++i)assert(arena[i]==1e30f);')
 f=f.replace('  mmads+=st.mmads;', '  aloads+=st.aL0;bloads+=st.bL0;mmads+=st.mmads;')
 f=f.replace('<<breads<<"\\n";', '<<breads<<" A2elements="<<aloads<<" B2elements="<<bloads<<"\\n";')
 f+='''int main(){
 Run<true>({1,4096,1280,1152,208,144,0,0,1,20,0,0},false);
 Run<true>({1,4096,1280,1152,128,256,0,0,1,20,0,0},false);
 for(auto s:std::vector<Schedule>{
  {1,4096,272,1104,208,144,0,0,1,20,0,0},
  {1,4096,272,1152,176,176,0,0,1,24,0,0},
  {1,4112,272,1152,160,192,0,0,1,28,0,0},
  {1,176,144,128,80,128,0,0,1,3,0,0},
  {1,176,144,128,48,128,0,0,1,4,0,0},
  {1,80,144,128,16,128,0,0,1,8,0,0}})Run<true>(s,true);
 std::cout<<"8 actual whole-M/parent producers: every full-K C, reused original arena/ring/prefix, live operands and negative Max-Sum PASS\\n";
}
'''
 return f

def ownership(s,e,h):
 f=make_ownership(s,e,h)
 f=f.replace('void Run(int64_t M,uint32_t workers,bool neg){','void Run(int64_t M,uint32_t workers,uint32_t BM,uint32_t BN,bool neg){')
 f=f.replace('Schedule s{1,M,1280,1152,128,256,uint32_t((M+127)/128),5,1,workers};',
  'Schedule s{1,M,1280,1152,BM,BN,uint32_t((M+BM-1)/BM),uint32_t((1280+BN-1)/BN),1,workers};')
 f=f.replace('pipe.bytes=128*256*4+5*128*4;', 'pipe.bytes=BM*BN*4+5*BM*4;')
 f=f[:f.index('int main(){')]+'''int main(){unsigned count=0;
 for(int64_t m:{80,176,4096,4112,6144,8176})for(uint32_t w:{3u,8u,20u,24u,28u,32u})for(bool neg:{false,true}){
  uint32_t bm=uint32_t(((m/16+w-1)/w)*16);if(bm>256)continue;for(uint32_t bn:{128u,144u,176u,192u}){if(4ULL*bm*bn>131072)continue;Run(m,w,bm,bn,neg);++count;}
 }
 std::cout<<count<<" whole-M ownership/store+actualFinalizeRows, half-M 8 but not16 alignment/tails/zero rows/unique y PASS\\n";
}
'''
 return f

def consumer(s):
 f=(ROOT/'tests/cpu/fullk_window_consumer_model.cpp.in').read_text().split('// INSERT_CONSUMER')[0]
 f=f.replace('uint32_t baseM,baseN,window;', 'uint32_t baseM,baseN,window,tree=8;')
 f=f.replace('unsigned completed=0;', 'unsigned completed=0,next=0,released=0;int gen[2]={-1,-1};bool neg=false;')
 a=f.index('void DataCopyPad(LocalTensor<float>');b=f.index('template<int P>void PipeBarrier',a)
 f=f[:a]+'''void DataCopyPad(LocalTensor<float> dst,GlobalTensor<float> src,DataCopyExtParams p,DataCopyPadExtParams<float> pad){
 assert(!pad.pad&&!dst.mem->pending&&p.blockCount==st.rows);
 uint32_t cols=p.blockLen/4,BN=st.s.baseN;assert(p.srcStride==(BN-cols)*4&&p.dstStride==(BN-cols)/8);
 uint32_t slot=st.slot;int gen=st.gen[slot];assert(gen>=0);
 assert(src.offset==slot*st.slotSize+st.sub*(st.s.baseM/2)*BN);++st.copies;dst.mem->pending=true;
 st.dma.push_back([=]{assert(st.gen[slot]==gen);
  for(uint32_t r=0;r<p.blockCount;++r)for(uint32_t j=0;j<cols;++j)dst.At(r*BN+j)=src.At(r*BN+j);
  dst.mem->pending=false;
 });
}
float TestValue(uint32_t r,uint32_t n,bool neg);
template<int Mode>void CrossCoreWaitFlag(uint32_t slot){
 assert(Mode==2&&slot==(st.next&1));st.slot=slot;uint32_t nt=st.next++;st.gen[slot]=nt;
 auto& ring=*st.ring;std::fill(ring.begin()+slot*st.slotSize,ring.begin()+(slot+1)*st.slotSize,1e30f);
 for(uint32_t r=0;r<uint32_t(st.s.m);++r)for(uint32_t n=0;n<st.s.baseN&&nt*st.s.baseN+n<uint32_t(st.s.n);++n)
  ring[slot*st.slotSize+r*st.s.baseN+n]=TestValue(r,nt*st.s.baseN+n,st.neg);
}
template<int Mode,int P>void CrossCoreSetFlag(uint32_t flag){
 assert(Mode==2&&P==PIPE_MTE2&&flag==4+st.slot);uint32_t slot=st.slot;st.Flush();++st.released;
 auto& ring=*st.ring;std::fill(ring.begin()+slot*st.slotSize,ring.begin()+(slot+1)*st.slotSize,1e30f);st.gen[slot]=-2;
}
'''+f[b:]
 copy=span(s,'__aicore__ inline void ManualCopyC(', '// Partition actual M rows')
 a=s.index('    const uint32_t lead=FULL_A?1:',s.index('void bmmms_manual('));b=s.index('\n        }\n        if constexpr(DIRECT_BATCH)',a)
 loop=s[a:b]
 helper='''void TestConsume(AscendC::TQue<AscendC::TPosition::VECIN,2>& cq,AscendC::GlobalTensor<float> ring,
 Schedule s,uint32_t rowStart,uint32_t rows,AscendC::LocalTensor<float> maxima,AscendC::LocalTensor<float> row){
 constexpr bool FULL_A=false;const uint32_t begin=0,end=(s.n+s.baseN-1)/s.baseN,slots=2,span=1,slotSize=s.baseM*s.baseN;
 uint32_t sequence=0;
'''+loop+'\n}\n'
 f+=copy+helper+'''namespace AscendC {float TestValue(uint32_t r,uint32_t n,bool neg){return neg?-float(1+(r*7+n*13)%59):float((r*11+n*17)%67)-33;}}
void Run(uint32_t BM,uint32_t BN,uint32_t M,uint32_t N,bool neg){
 Schedule s{1,M,N,1152,BM,BN,1};uint32_t size=BM*BN;
 float sum=0,gold=0;
 for(uint32_t sub=0;sub<2;++sub){
  std::vector<float> ring(2*size+16,1e30f);AscendC::TQue<AscendC::TPosition::VECIN,2> cq(BM/2*BN);
  AscendC::LocalTensor<float> maxima{std::make_shared<AscendC::Storage>(BM),0},row{std::make_shared<AscendC::Storage>(4*BM),0};
  std::fill(maxima.mem->data.begin(),maxima.mem->data.end(),-std::numeric_limits<float>::infinity());
  st=Model{};st.s=s;st.sub=sub;st.rows=M>sub*BM/2?std::min(BM/2,M-sub*BM/2):0;st.slotSize=size;st.ring=&ring;st.neg=neg;
  TestConsume(cq,{&ring},s,sub*BM/2,st.rows,maxima,row);assert(st.next==(N+BN-1)/BN&&st.released==st.next&&st.dma.empty());
  for(uint32_t r=0;r<st.rows;++r){float mx=-std::numeric_limits<float>::infinity();
   for(uint32_t n=0;n<N;++n)mx=std::max(mx,AscendC::TestValue(sub*BM/2+r,n,neg));
   assert(maxima.At(r)==mx);if(neg)assert(mx<0);sum+=maxima.At(r);gold+=mx;
  }for(size_t i=2*size;i<ring.size();++i)assert(ring[i]==1e30f);
 }assert(sum==gold);
}
int main(){unsigned n=0;
 for(uint32_t bm:{144u,160u,176u,192u,208u,224u,240u,256u})for(uint32_t m:{bm,bm-16,bm/2,bm/2-8})
 for(uint32_t bn:{128u,144u,176u,192u})for(uint32_t cols:{16u,bn,bn+16,272u,1280u,1296u})for(bool neg:{false,true}){if(4ULL*bm*bn>131072)continue;Run(bm,bn,m,cols,neg);++n;}
 std::cout<<n<<" actual non-fullK ManualCopyC+tree Max consumers, halfM72..128, two UB buffers/destructive GM reuse/negative tails PASS\\n";
}
'''
 return f

def host(s):
 f=make_host(s).split('int main(){')[0]
 return f+'''#include <cstring>
int main(){auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();unsigned n=0,hits=0;
 for(int cores:{1,3,8,20,24,28,32})for(int m:{4096,4112,6144,8176})for(int k:{1024,1104,1152,1280,1536})
 for(int dt:{1,2})for(int x:{0,1})for(int y:{0,1}){
  hw->aic=cores;hw->aiv=2*cores;Shape s{1,m,1280,k,dt,x,y};auto p=MakePlan(s,cores),old=p;Schedule q;
  bool hit=MakeFullMShard(s,p,q);++n;
  assert(!std::memcmp(&p.schedule,&old.schedule,sizeof(Schedule))&&p.totalBytes==old.totalBytes&&p.cubeBlocks==old.cubeBlocks);
  if(hit){++hits;assert(dt==2&&!x&&!y&&q.baseM>128&&q.baseM%16==0&&q.baseN>=128&&q.baseN%16==0&&q.nSplit==1);
   assert(uint64_t(q.baseM)*s.k*2+4ULL*q.baseN*q.kChunk+5120<=hw->l1);
   assert(4ULL*q.baseM*q.kChunk<=hw->l0a&&4ULL*q.baseN*q.kChunk<=hw->l0b&&4ULL*q.baseM*q.baseN<=hw->l0);
   assert(p.totalBytes>=p.systemBytes+Ceil(q.mTiles*q.baseM*4,512)*512+8ULL*q.workers*q.baseM*q.baseN);
  }
 }
 hw->aic=20;hw->aiv=40;Shape s{1,4096,1280,1152,2,0,0};auto p=MakePlan(s,20);Schedule q;assert(MakeFullMShard(s,p,q));
 assert(q.baseM==208&&q.baseN==144&&q.mTiles==20&&q.nTiles==9);
 for(auto field:{&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}){auto old=*field;*field=1024;assert(!MakeFullMShard(s,p,q));*field=old;}
 hw->l1=208ULL*1152*2+4ULL*128*64+5120;assert(MakeFullMShard(s,p,q));--hw->l1;assert(!MakeFullMShard(s,p,q));hw->l1=512*1024;
 hw->l0a=208ULL*64*4;assert(MakeFullMShard(s,p,q));--hw->l0a;assert(!MakeFullMShard(s,p,q));hw->l0a=65536;
#ifdef BMMMS_TUNING
 for(auto field:{&Tune().group,&Tune().rows,&Tune().dual,&Tune().early,&Tune().tree,&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().ks,&Tune().workers}){
  Tune()=TuneConfig{};*field=1;assert(!MakeFullMShard(s,p,q));
 }Tune()=TuneConfig{};
#endif
 assert(hits);std::cout<<n<<" actual host configurations/"<<hits<<" full-M hits, actual capacities/pins/unchanged Plan/old allocation PASS\\n";
}
'''

def main():
 s=(ROOT/'kernel.asc').read_text();e,h=scope(s);c=cube(s,e,h);v=ownership(s,e,h);a=consumer(s);p=host(s)
 print('kernel SHA256',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c10-whole-m-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=180)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  for name,code,flags in [('cube',c,()),('ownership',v,()),('consumer',a,()),('host',p,()),('host-tuning',p,('-DBMMMS_TUNING',))]:run(name,code,flags=flags)
  for name,code,x,y in [('rows-store',v,'maxima,rows);','maxima,s.baseM/2);'),
   ('half-offset',v,'sub*(s.baseM/2)','sub*64'),
   ('GM-early-release',a,'st.Flush();++st.released;','++st.released;'),
   ('max-order',a,'std::max(a.At(i),b.At(i))','a.At(i)+b.At(i)')]:
   assert x in code;run('bad-'+name,code.replace(x,y,1),True)
  print('Four larger-shard store/offset/GM-readiness/Max-order controls rejected PASS')
 print('Device source unchanged; native CANN9, BF16 precision, route and latency PENDING.')
if __name__=='__main__':main()
