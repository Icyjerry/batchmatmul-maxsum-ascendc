#!/usr/bin/env python3
"""Audit supplied exact-shape image against actual host source, all dtype/layouts.

CPU tiler stub and conditional layouts, not formal shape/route/device evidence.
"""
from pathlib import Path
import csv,hashlib,re,shutil,subprocess,tempfile
from validate_teammate_single_tile import source,span
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=(ROOT/'kernel.asc').read_text();assert s==source('1734f16'),'audit passed kernel only'
 rows=list(csv.DictReader((ROOT/'docs/teammate_probe/exact_shapes_user_1008.csv').open()))
 structs='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in ['C7KernelShape','WideNKernelShape','TTFrameShape'])
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 small=span(s,'inline uint32_t SmallVectorK256Rows','template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>')
 host=stub+span(s,'struct Shape {','template <AscendC::HardEvent')+structs+span(s,'struct Plan {','using CacheKey =')+small
 array=',\n'.join('{'+','.join(r[n] for n in ['B','M','N','K'])+'}' for r in rows)
 host+='''
int main(){int64_t cases[][4]={'''+array+'''};
 std::cout<<"case,cores,dtype,tx1,tx2,dual,bm,bn,kchunk,ns,ks,workers,window,early,tree,vector_rows,c7,wide,tt_frame,c9_package,estimated_entry\\n";
 for(int cores:{1,8,20,32})for(int ci=0;ci<15;++ci)for(int dt:{1,2})for(int x:{0,1})for(int y:{0,1}){
  auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();hw->aic=cores;hw->aiv=2*cores;
  auto a=cases[ci];Shape s{a[0],a[1],a[2],a[3],dt,x,y};auto p=MakePlan(s,cores);auto d=p.schedule;
  auto vr=SmallVectorK256Rows(s);auto c7=MakeC7ManualFrame(s,p);auto wide=MakeWideNManualFrame(s,p);
  auto tt=MakeTTManualFrame(s,p);auto c9=MakeCase9PackagePlan(s,p);
  bool packages=d.dual==20&&dt==1&&!x&&y&&c9.safe&&c9.resident&&c9.bK>d.kChunk;
  std::string entry=vr?"small_vector_k256":d.dual==28?"tiny_tt_vector":d.dual==15?"dot_short":
   d.dual==16?"tiny_direct":d.dual==24?"tiny_grouped":c7.workers?"c7_manual_frame":wide.workers?"wide_n_manual_frame":
   d.dual==33&&tt.workers?"tt_manual_frame":packages?"case9_packages":
   d.dual==19&&dt==2&&!x&&y&&s.b>=8&&s.b<16&&s.m>=16&&s.m<32&&s.n>=64&&s.n<128?"c6_direct_batch":d.dual==19?"single_tile":d.dual==3&&(d.tree&16)?"manual_resident_b":
   d.dual==6&&x&&!y?"case12_packed":d.dual==20?"manual_full_a":
   d.dual==25?"longk_split":d.dual==2?"dual_mdl_library":d.dual==1?"dual_library":"other";
  std::cout<<ci+1<<","<<cores<<","<<dt<<","<<x<<","<<y<<","<<d.dual<<","<<d.baseM<<","<<d.baseN<<","<<d.kChunk
   <<","<<d.nSplit<<","<<d.kSplit<<","<<d.workers<<","<<d.window<<","<<d.earlySum<<","<<d.tree<<","<<vr
   <<","<<c7.workers<<","<<wide.workers<<","<<tt.workers<<","<<packages<<","<<entry<<"\\n";
 }
}
'''
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-exact-shape-') as t:
  cpp,exe=Path(t)/'audit.cpp',Path(t)/'audit';cpp.write_text(host)
  subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
  print(subprocess.check_output([str(exe)],text=True),end='')
if __name__=='__main__':main()
