#!/usr/bin/env python3
"""Execute packing, Cube input copy and B2 load source in an integer-bit model.

Not CANN compilation, hardware transpose precision, full asynchronous Cube
simulation or performance evidence. Keeps the passed A/C/Vector/event paths.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
src=(root/'kernel.asc').read_text()
parent_src=subprocess.check_output(['git','show','a05035e:kernel.asc'],cwd=root,text=True)
a=src.index('template<typename T>\n__aicore__ inline void ManualPackBToNZ(')
helper=src[a:src.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false,bool NZ_B=false>',a)]
a=src.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false,bool NZ_B=false>')
cube=src[a:src.index('// Isolated case12 packed-B kernel',a)]
block=src[src.index('void bmmms_manual_case12_packed('):src.index('struct Plan {')]
a=block.index('        const uint32_t packRows=');b=block.index('        // The signal is issued only after every packed panel',a)
pack=block[a:b]
a=block.index('                lp.dstGap=0;lp.ifTranspose=!TX2;');b=block.index('                if(!residentA)',a)
load=block[a:b];load=load[:load.rfind('\n                }')]
cube+='''template<bool NZ_B>void LoadB(AscendC::LocalTensor<uint16_t> b2,AscendC::LocalTensor<uint16_t> b1,
 const Schedule& s,uint32_t count,uint32_t cols){
 constexpr bool TX2=false;AscendC::LoadData2DParams lp;
'''+load+'\n}\n'
model=(root/'tests/cpu/packed_b_nz_model.cpp.in').read_text().replace('// @HELPER@',helper).replace('// @CUBE@',cube).replace('// @PACK@',pack)
# Kernel bodies outside this isolated family must remain byte-identical.
def region(s,start,end):return s[s.index(start):s.index(end,s.index(start))]
assert region(src,'// One full-M accumulator:','// Isolated case12 packed-B kernel').split('// Prepare one Cube-ready')[0]==region(parent_src,'// One full-M accumulator:','// Isolated case12 packed-B kernel').split('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>\n__aicore__ inline void ManualCopyKCase12Packed')[0]
# In packed kernel, restore only the three input-stage edits, then compare body.
a=block.index('                if constexpr(NZ_B) {',block.index('lp.dstGap=0;lp.ifTranspose=!TX2;'));b=block.index('                } else if constexpr(TX2)',a)
restore=block[:a]+block[b:].replace('                } else if constexpr(TX2)','                if constexpr(TX2)',1)
restore=restore.replace('PAD_MN,RESIDENT_B,NZ_B>','PAD_MN,RESIDENT_B>')
a=restore.index('            auto ready=data;');b=restore.index('            Fence<AscendC::HardEvent::V_MTE3>();',a)
restore=restore[:a]+restore[b:]
restore=restore.replace('],ready,kr*s.baseN);','],data,kr*s.baseN);')
native="""                if constexpr(NZ_B) {
                    // This family holds the complete aligned TT-stored A in L1.
                    // One raw-bit rectangle replaces the per-M16 Load2D loop.
                    ManualTransposeFullM(a2,a1,s.k,rows,count,k0);
                } else if((s.tree&4) && residentA) {"""
if native in restore:restore=restore.replace(native,'                if((s.tree&4) && residentA) {')
assert restore==region(parent_src,'void bmmms_manual_case12_packed(','struct Plan {'), 'unrelated packed-kernel mutation'
shapes=src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host=src[src.index('struct Plan {'):src.index('using CacheKey =')]
parent=parent_src[parent_src.index('struct Plan {'):parent_src.index('using CacheKey =')]
hostmodel=(root/'tests/cpu/planner_stub.hpp').read_text()+shapes+'namespace Parent{'+parent+'}\nnamespace Candidate{'+host+'}\n'+r'''
int main(){unsigned checked=0,selected=0;auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
 for(int cores:{4,20,32})for(int batch:{1,2})for(int m:{1024,1536,2048})for(int n:{4096,4112,6144})
 for(int k:{1024,1040,1536,2048})for(int dt:{1,2})for(int tx1:{0,1})for(int tx2:{0,1}){
  Shape s{batch,m,n,k,dt,tx1,tx2};auto p=Parent::MakePlan(s,cores);auto q=Candidate::MakePlan(s,cores);++checked;
  auto x=p.schedule,y=q.schedule;
  if(y.dual==31){++selected;assert(x.dual==6&&tx1&&!tx2&&k%16==0&&n%16==0);y.dual=x.dual;
   assert(y.window==1&&!y.earlySum&&y.kSplit==1);
   const uint64_t rows=y.baseM/2,bn=y.baseN;
   assert(2*rows*bn*2==rows*bn*4); // both source and transformed output fit one original C buffer
   assert(y.baseM*bn*4+20ULL*y.baseM+12ULL*y.vectorTile+64+4096<hw->ub);
  }
  assert(p.cubeBlocks==q.cubeBlocks&&p.finalBlocks==q.finalBlocks&&p.systemBytes==q.systemBytes&&p.totalBytes==q.totalBytes);
  assert(std::tie(x.b,x.m,x.n,x.k,x.baseM,x.baseN,x.mTiles,x.nTiles,x.nSplit,x.workers,x.vectorTile,x.window,x.kSplit,x.kChunk,x.microRows,x.batchGroup,x.dual,x.earlySum,x.tree,x.balance)==
   std::tie(y.b,y.m,y.n,y.k,y.baseM,y.baseN,y.mTiles,y.nTiles,y.nSplit,y.workers,y.vectorTile,y.window,y.kSplit,y.kChunk,y.microRows,y.batchGroup,y.dual,y.earlySum,y.tree,y.balance));
 }
 assert(selected>0);Shape hit{1,1536,6144,1536,2,1,0};assert(Candidate::MakePlan(hit,20).schedule.dual==31);
#ifdef BMMMS_TUNING
 for(auto pin:{&Candidate::Tune().bm,&Candidate::Tune().bn,&Candidate::Tune().window,&Candidate::Tune().ns,
    &Candidate::Tune().ks,&Candidate::Tune().workers,&Candidate::Tune().tree,&Candidate::Tune().dual,&Candidate::Tune().early}){
  Candidate::Tune()=Candidate::TuneConfig{};*pin=1;
  try{assert(Candidate::MakePlan(hit,20).schedule.dual!=31);}catch(const std::invalid_argument&){}
 }
 Candidate::Tune()=Candidate::TuneConfig{};
#endif
 std::cout<<checked<<" host configurations with permissive fake tiler, "<<selected<<" selected; original grid/workspace/schedule and pins PASS\n";
}
'''
compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
print('CPU bit/address model; kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
with tempfile.TemporaryDirectory(prefix='bmmms-packed-nz-') as d:
 for name,code,flags in [('pack-nd',model,['-DBMMMS_NZ_B=0']),('pack-nz',model,['-DBMMMS_NZ_B=1']),('host',hostmodel,[]),('host-tuning',hostmodel,['-DBMMMS_TUNING'])]:
  cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name;cpp.write_text(code)
  subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True)
print('CANN9 compile, NPU accuracy/latency PENDING.')
