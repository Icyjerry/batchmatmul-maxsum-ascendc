#!/usr/bin/env python3
"""Actual exact-C13 resident entry: physical Cube and queued threaded AIV model.

CPU integers/synthetic companion credits, not native FP16 timing or all hardware.
"""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_teammate_single_tile import source,span
from validate_c13_manual_frame import cube as old_cube,vector as old_vector
ROOT=Path(__file__).resolve().parents[1]
def scope(s):
 e=span(s,'// Exact aligned FF resident plan:','// Full-A wide-N frame:')
 h=span(s,'// Exact supplied C13 geometry','using CacheKey =')
 c='''    const auto resident13=MakeC13ResidentFrame(s,p);
    if(resident13.workers) {
        bmmms_c13_resident_frame<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,resident13);
        return;
    }
'''
 assert s.count(c)==1 and s.replace(e,'',1).replace(h,'',1).replace(c,'',1)==source('1734f16')
 assert 'TPipe' not in e and 'TQue' not in e
 return e,h

def cube(s,e):
 f=old_cube(s,e).split('void Run(uint32_t M,uint32_t N,uint32_t K,uint32_t workers,bool neg)')[0]
 f=f.replace('if(p==TPosition::A1||p==TPosition::B1){','if(p==TPosition::A1){')
 return f+(ROOT/'tests/cpu/c13_resident_cube.cpp.in').read_text()
def vector(s,e):
 f=old_vector(s,e).split('void Run(uint32_t M,uint32_t N,uint32_t workers,bool neg,uint32_t mode)')[0]
 f=f.replace('elems==(shared->s.m/128)*16','elems==shared->s.workers*16')
 f=f.replace('count==(shared->s.m/128)*16','count==shared->s.workers*16')
 a=f.index('void DataCopy(GlobalTensor<float> dst,LocalTensor<float> src,uint32_t count)');b=f.index('\nvoid DataCopy(LocalTensor<float>',a)
 f=f[:a]+'''void DataCopy(GlobalTensor<float> dst,LocalTensor<float> src,uint32_t count){
 auto s=shared->s;uint32_t worker=st.block/2,sub=st.block%2;int gen=int(st.issued)-1;
 assert(dst.kind==GlobalTensor<float>::PARTS&&dst.offset==worker*16+sub*8&&count==8&&src.offset==8384);
 st.Push(PIPE_MTE3,[=]{for(uint32_t i=0;i<count;++i){assert(src.Gen(i)==gen);
  dst.At(i)=src.At(i);assert(shared->written[dst.offset+i].fetch_add(1,std::memory_order_release)==0);}});
}'''+f[b:]
 a=f.index('void DataCopy(LocalTensor<float> dst,GlobalTensor<float> src,uint32_t count)');b=f.index('\nvoid DataCopyPad(GlobalTensor<float>',a)
 old=f[a:b];body=old[old.index('{')+1:old.rfind('}')]
 f=f[:a]+'''void DataCopy(LocalTensor<float> dst,GlobalTensor<float> src,uint32_t count){
 if(src.kind==GlobalTensor<float>::RING){
  auto s=shared->s;uint32_t sub=st.block%2;int gen=int(st.issued)-1;uint32_t slot=gen&1;
  assert(count==4096&&src.offset==slot*8192+sub*4096&&dst.offset==slot*4096);++st.copies;
  st.Push(PIPE_MTE2,[=]{assert(st.ringGen[slot]==gen&&"GM released before last DMA");
   for(uint32_t i=0;i<count;++i){dst.At(i)=src.At(i);dst.Gen(i)=gen;}});
 }else {'''+body+'}\n}'+f[b:]
 a=f.index('void Add(');b=f.index('template<bool OnlyVector>',a)
 f=f[:a]+'''void Add(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint64_t mask,uint32_t reps,BinaryRepeatParams){
 assert(!st.synced&&mask==64&&reps==1);int gen=int(st.issued)-1;
 st.Push(PIPE_V,[=]{for(uint32_t i=0;i<mask;++i){assert(a.Gen(i)==gen-1&&b.Gen(i)==gen);
  dst.At(i)=a.At(i)+b.At(i);dst.Gen(i)=gen;}});
}
'''+f[b:]
 return f+(ROOT/'tests/cpu/c13_resident_vector.cpp.in').read_text()

def main():
 s=(ROOT/'kernel.asc').read_text();e,h=scope(s)
 print('Three additions restore entire1734f16; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c13-resident-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'missed control:'+name
   else:r.check_returncode()
  c=cube(s,e);run('cube',c)
  for name,line in [('A1-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);'),
   ('B-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2);'),
   ('A-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(slot);'),
   ('A2-reader','        AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(slot);'),
   ('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(slot);'),
   ('M-fix','        SingleTileDirectFence<true,AscendC::HardEvent::M_FIX>();')]:
   unsafe=c.replace(line,'');assert unsafe!=c;run('no-'+name,unsafe,True)
  unsafe=c.replace('mm.k=bk;','mm.k=bk-16;');assert unsafe!=c;run('no-full-K',unsafe,True)
  print('Seven live Cube operand/ready/complete-K controls rejected PASS',flush=True)
  v=vector(s,e);run('vector',v)
  for name,line in [('C-reader','        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);'),
   ('C-ready','        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);'),
   ('sum-ready','    SingleTileDirectFence<true,AscendC::HardEvent::V_MTE3>();'),
   ('barrier','    AscendC::SyncAll<true>();'),
   ('final-ready','        SingleTileDirectFence<true,AscendC::HardEvent::MTE2_V>();'),
   ('terminal','    AscendC::PipeBarrier<PIPE_ALL>();')]:
   unsafe=v.replace(line,'');assert unsafe!=v;run('no-'+name,unsafe,True)
  copy='        AscendC::DataCopy(c,ring[slot*oneC+sub*halfC],halfC);'
  release='        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4+slot);'
  unsafe=v.replace(copy+'\n'+release,release+'\n'+copy);assert unsafe!=v;run('early-GM-credit',unsafe,True)
  print('Seven queued Vector readiness/store/barrier/terminal/GM-credit controls rejected PASS',flush=True)
  stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
  head=e[:e.index('template<typename T>')]
  host='#include <cstring>\n'+stub+span(s,'struct Shape {','template <AscendC::HardEvent')+span(s,'struct Plan {','struct Case9PackagePlan ')+head+h+(ROOT/'tests/cpu/c13_resident_host.cpp.in').read_text()
  run('host',host);run('host-tuning',host,flags=['-DBMMMS_TUNING'])
 print('CPU integers/synthetic companion models only. Native CANN9/FP16 precision/latency PENDING.')
if __name__=='__main__':main()
