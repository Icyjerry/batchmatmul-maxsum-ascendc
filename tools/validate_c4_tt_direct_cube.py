#!/usr/bin/env python3
"""Actual existing TT Cube/AIV source and new route over the passed whole parent.

CPU integer physical/address/FIFO model and host control flow, not CANN/BF16 timing.
"""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
from validate_teammate_single_tile import fn, span, source, run_producer
ROOT=Path(__file__).resolve().parents[1]

def scope(s):
 h=span(s,'// Route the original small TT single-tile allocation','using CacheKey =')
 c=span(s,'    if(C4DirectCubeFits(s,p)) {','    const uint32_t vectorRows=SmallVectorK256Rows(s);')
 assert s.replace(h,'',1).replace(c,'',1)==source('1734f16')
 assert '<<<s.b,nullptr,stream>>>' in c and c.count('bmmms_single_tile_direct_batch<T,true,true,16,')==2
 return h

def vector(s):
 fold=span(s,'__aicore__ inline void SmallRowMaxLaneFold','// One Cube owns one complete small batch.')
 context=span(s,'// Only the partial/merge variant needs a live TPipe','// Isolated case6 fast path copied')
 helpers=fold+context+fn(s,'bmmms_single_tile')+fn(s,'bmmms_single_tile_direct_batch')
 f=(ROOT/'tests/cpu/teammate_tiny_model.cpp.in').read_text()
 f=f.replace('#define __gm__','#define __mix__(...)\n#define __gm__')
 f=f.replace('struct Schedule {int64_t b,m,n,k;};','struct Schedule {int64_t b,m,n,k;uint32_t baseM,baseN;};')
 extra=r'''
int ready=0;
void SetAtomicNone(){} void SetMaskNorm(){}void ResetMask(){}
template<int M>void CrossCoreWaitFlag(int id){assert(M==2&&id==0&&ready--==1);}
template<bool B>void SyncAll(){assert(false);}
void DataCopy(LocalTensor<float> dst,GlobalTensor<float> src,uint32_t n){
 assert(n%8==0&&dst.offset%32==0);dma.push_back([=]{for(uint32_t i=0;i<n;++i)dst.write(i,src.read(i));});
}
void DataCopy(GlobalTensor<float> dst,LocalTensor<float> src,uint32_t n){assert(false);}
void Max(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint64_t mask,uint32_t reps,BinaryRepeatParams p){
 assert(mask>0&&mask<=64&&reps<=255&&dst.offset%32==0&&a.offset%32==0&&b.offset%32==0);
 for(uint32_t r=0;r<reps;++r)for(uint32_t i=0;i<mask;++i)
  dst.write(r*p.dstRep*8+i,std::max(a.read(r*p.src0Rep*8+i),b.read(r*p.src1Rep*8+i)));
}
'''
 f=f.replace('float tree_sum(',extra+'float tree_sum(')
 driver=(ROOT/'tests/cpu/c4_tt_direct_vector.cpp.in').read_text()
 return f.replace('// INSERT_KERNELS',helpers)+driver

def main():
 s=(ROOT/'kernel.asc').read_text();h=scope(s)
 print('Two additions restore whole passed1734f16; SHA '+hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c4-cube-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed:'+name
   else:r.check_returncode()
  def producer_run(code,name,negative=False,flags=()):
   code=code[:code.index('unsigned producers=0;')]+(ROOT/'tests/cpu/c4_tt_direct_cube.cpp.in').read_text()
   run(name,code,negative,flags)
  run_producer(s,source('1734f16'),producer_run)
  v=vector(s);run('vector',v)
  for name,old,new in [('M-tail','uint64_t(rows),1','uint64_t(mp),1'),
    ('N-tail','uint64_t(n<64?n:64),rows','uint64_t(pitch),rows'),
    ('input-ready','SingleTileDirectFence<DIRECT_BATCH,AscendC::HardEvent::MTE2_V>();',''),
    ('terminal','AscendC::PipeBarrier<PIPE_ALL>();','')]:
   unsafe=v.replace(old,new);assert unsafe!=v;run('no-'+name,unsafe,True)
  print('Four M/N mask, input DMA-ready and terminal controls rejected PASS',flush=True)
  stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
  host='#include <cstring>\n'+stub+span(s,'struct Shape {','template <AscendC::HardEvent')+span(s,'struct Plan {','struct Case9PackagePlan ')+h+(ROOT/'tests/cpu/c4_tt_direct_host.cpp.in').read_text()
  run('host',host);run('host-tuning',host,flags=['-DBMMMS_TUNING'])
 print('Integer CPU models only; CANN9/BF16 native precision/latency PENDING.')
if __name__=='__main__':main()
