#!/usr/bin/env python3
"""Actual C8 task, NZ subview, queued Cube/AIV and host CPU models.

Integer arithmetic, synthetic cross-core partners and fake tiler; not CANN,
BF16 precision, hardware overlap or a performance prediction.
"""
from pathlib import Path
import hashlib,re,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_c8_phased_a_ready import producer
from validate_tt_manual_frame import vector
from audit_c8_area_partition import tail_aware,cells
ROOT=Path(__file__).resolve().parents[1]

def reference():
 # Independent Python atom enumeration/metric recomputation, all queried cores.
 out='struct RefTile {uint32_t mt,nt,row,rows;};\nstd::map<uint32_t,std::vector<std::vector<RefTile>>> refs={\n'
 for w in range(8,33):
  groups=tail_aware(w)
  out+='{'+str(w)+',{' + ','.join('{'+','.join('{%d,%d,%d,%d}'%(cells[c][0],cells[c][1],r,n) for c,r,n in g)+'}' for g in groups) + '}},\n'
 return out+'};\n'

def regions(s):
 e=span(s,'// Same TT tile/package stream','// All N-tile partials are ready')
 old=source('a2e6763');prev=span(old,'// Same TT tile/package stream','// All N-tile partials are ready')
 h=span(s,'// Exact C8 frame:','// Exact supplied C13 geometry')
 launch=span(s,'    if(p.schedule.dual==33) {','    if(p.schedule.dual==29) {')
 before=span(old,'    if(p.schedule.dual==33) {','    if(p.schedule.dual==29) {')
 assert s.replace(e,prev,1).replace(h,'',1).replace(launch,before,1)==old
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return e,h,launch

def cube(s,e,h,ref):
 c=producer(s,e).split('void Run(uint32_t M,uint32_t N,uint32_t K,')[0]
 # Make the mixed-sign input depend on K as well as M. The original m*5+k*3
 # distribution is periodic; positive nonuniform values catch wrong row origin.
 c=c.replace('int16_t A(int64_t b,int64_t m,int64_t k){return negativeInput?1+(b*13+m*7+k*3)%3:int((b*13+m*5+k*3)%7)-3;}',
  'int16_t A(int64_t b,int64_t m,int64_t k){return negativeInput?1+(m*7+k*3)%3:1+(m*5+k*11+k/17)%7;}')
 c=c.replace('int16_t B(int64_t b,int64_t k,int64_t n){return -int16_t(1+(b*11+k*3+n*2)%5);}',
  'int16_t B(int64_t b,int64_t k,int64_t n){int16_t v=1+(k*3+n*2+k/13)%5;return negativeInput?-v:((n+k)%3?-v:v);}')
 c+=h+ref+(ROOT/'tests/cpu/c8_balanced_tail_cube.cpp.in').read_text()
 return c

def consumer(s,e,h,ref):
 original='template<typename T,bool PHASED_A=false,bool WORK_BALANCE=false>'
 normalized=e.replace(original,'template<typename T>').replace('template<typename T,bool WORK_BALANCE=false>', 'template<typename T>')
 v=vector(s,normalized).split('void Run(uint32_t M,uint32_t N,uint32_t BM,')[0]
 v=v.replace('template<typename T>\n__schedmode__(1) __global__ __mix__(1,2) void bmmms_tt_manual_frame',
  original+'\n__schedmode__(1) __global__ __mix__(1,2) void bmmms_tt_manual_frame')
 v=v.replace('#include <memory>','#include <memory>\n#include <map>')
 v=v.replace('struct Barrier {',ref+'struct Barrier {',1)
 a=v.index('template<int Mode>void CrossCoreWaitFlag');b=v.index('struct DataCopyExtParams',a)
 v=v[:a]+'''template<int Mode>void CrossCoreWaitFlag(int flag){
 assert(Mode==2&&flag>=0&&flag<2&&flag==int(st.issued&1));auto s=shared->s;
 auto group=refs.at(s.workers).at(st.block/2);assert(st.issued<group.size());auto t=group[st.issued++];int gen=st.issued-1;
 st.Push(PIPE_MTE2,[=]{assert(st.credit[flag]--==1);uint32_t m0=t.mt*s.bm+t.row,n0=t.nt*s.np;
  auto first=st.ring.begin()+flag*s.bm*s.np;std::fill(first,first+s.bm*s.np,1e30f);st.ringGen[flag]=gen;
  for(uint32_t r=0;r<t.rows;++r)for(uint32_t n=0;n<std::min(s.np,s.n-n0);++n)
   st.ring[flag*s.bm*s.np+r*s.np+n]=Value(m0+r,n0+n,shared->neg);
 });
}
'''+v[b:]
 a=v.index(' auto s=shared->s;uint32_t sub=',v.index('void DataCopyPad(LocalTensor<float>'));b=v.index('\n}\ntemplate<class T>void DataCopy',a)
 v=v[:a]+''' auto s=shared->s;uint32_t sub=st.block%2,start=sub*(s.bm/2);
 auto t=refs.at(s.workers).at(st.block/2).at(st.issued-1);
 uint32_t rows=start>=t.rows?0:std::min(t.rows-start,s.bm/2),cols=std::min(s.n-t.nt*s.np,s.np);
 int gen=st.issued-1;uint32_t slot=gen&1;
 assert(src.kind==GlobalTensor<float>::RING&&src.offset==slot*s.bm*s.np+start*s.np&&!pad.pad);
 assert(p.blockCount==rows&&p.blockLen==cols*4&&p.srcStride==(s.np-cols)*4&&p.dstStride==(s.np-cols)/8);
 assert(dst.offset==slot*(s.bm/2)*s.np);++st.copies;
 st.Push(PIPE_MTE2,[=]{assert(st.ringGen[slot]==gen&&"GM released before DMA");
  for(uint32_t r=0;r<rows;++r)for(uint32_t c=0;c<cols;++c){dst.At(r*s.np+c)=src.At(r*s.np+c);dst.Gen(r*s.np+c)=gen;}
 });'''+v[b:]
 a=v.index(' auto s=shared->s;uint32_t worker=',v.index('void DataCopy(GlobalTensor<float>'));b=v.index('\n}\nvoid DataCopy(LocalTensor<float>',a)
 v=v[:a]+''' auto s=shared->s;uint32_t sub=st.block%2;int gen=st.issued-1;
 auto t=refs.at(s.workers).at(st.block/2).at(gen);uint32_t start=sub*s.bm/2;
 uint32_t rows=start>=t.rows?0:std::min(t.rows-start,s.bm/2),store=t.mt==8?s.bm/2:rows;
 assert(store&&count==store&&count%8==0);
 assert(dst.kind==GlobalTensor<float>::PARTS&&dst.offset==t.nt*s.mp+t.mt*s.bm+t.row+start);
 assert(src.offset==s.bm*s.np+(gen&1)*s.bm/2);
 st.Push(PIPE_MTE3,[=]{for(uint32_t i=0;i<count;++i){assert(src.Gen(i)==gen&&"row overwritten before store or V completion");
  dst.At(i)=src.At(i);assert(shared->written[dst.offset+i].fetch_add(1,std::memory_order_release)==0);}});'''+v[b:]
 return v+h+(ROOT/'tests/cpu/c8_balanced_tail_vector.cpp.in').read_text()

def host(s,e,launch,ref):
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 headers='\n'.join(re.search(r'struct '+n+r' \{[^}]*\};',s).group(0) for n in ['C7KernelShape','WideNKernelShape','C13ResidentFrame'])
 helpers=e[:e.index('template<typename T,')].replace('__aicore__','')
 # Preserve every actual launch guard, substitute only the three kernel calls.
 dispatch=launch[:launch.index('        if(FullMTilesBatchFits')]+'''    } return 0; }\n'''
 dispatch=re.sub(r'bmmms_tt_manual_frame<T,true,true><<<.*?>>>\(\s*x1,x2,partial,y,frame,MakeTTWorkOwners\(frame\)\);','return 2;',dispatch,flags=re.S)
 dispatch=re.sub(r'bmmms_tt_manual_frame<T,true><<<.*?>>>\(x1,x2,partial,y,frame\);','return 1;',dispatch,flags=re.S)
 dispatch=re.sub(r'bmmms_tt_manual_frame<T><<<.*?>>>\(x1,x2,partial,y,frame\);','return 0;',dispatch,flags=re.S)
 dispatch=dispatch.replace('            return;','            return 0;')
 return '#include <cstring>\n'+stub+span(s,'struct Shape {','template <AscendC::HardEvent')+headers+helpers+span(s,'struct Plan {','using CacheKey =')+'int Select(const Shape& s,const Plan& p){\n'+dispatch+ref+(ROOT/'tests/cpu/c8_balanced_tail_host.cpp.in').read_text()

def main():
 s=(ROOT/'kernel.asc').read_text();e,h,launch=regions(s);ref=reference()
 print('Whole passed-parent inverse/unchanged helper, plan, GM arena, protected7 PASS; SHA',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 c=cube(s,e,h,ref);v=consumer(s,e,h,ref);p=host(s,e,launch,ref)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c8-balance-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=240)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  run('host',p);run('host-tuning',p,flags=['-DBMMMS_TUNING'])
  run('cube',c);run('vector',v)
  for name,code,a,b in [
   ('row-origin',c,'a1[tile.row*kp]','a1[0]'),
   ('A-cache-shape',c,'TTFrameReadAPhase(a1,a,s,m0,cacheRows','TTFrameReadAPhase(a1,a,s,m0,validRows'),
   ('B-descriptor',c,'(WORK_BALANCE?TTWorkAt(s,worker,task,owners).nt:task%s.nTiles)','(task%s.nTiles)'),
   ('A-phase-ready',c,'                AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(2+aReadyPhase);',''),
   ('C-ready',c,'        AscendC::WaitFlag<AscendC::HardEvent::M_FIX>(cs);',''),
   ('fragment-store',v,'mt==mTiles-1?halfM:rows','halfM'),
   ('partial-origin',v,'m0=mt*s.bm+tile.row','m0=mt*s.bm'),
   ('GM-credit',v,'        AscendC::WaitFlag<AscendC::HardEvent::V_MTE2>(slot);',''),
   ('partial-ready',v,'        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(slot);',''),
   ('final-barrier',v,'    AscendC::SyncAll<true>();','')]:
   assert a in code,name;run('bad-'+name,code.replace(a,b),True,flags=['-DNEGATIVE_CONTROL'])
  print('Ten descriptor/NZ/cache/ready/GM/partial/barrier fault controls rejected PASS',flush=True)
 print('Native CANN9/BF16 precision/timing PENDING; synthetic Cube/AIV partners and fake tiler are explicit limitations.')
if __name__=='__main__':main()
