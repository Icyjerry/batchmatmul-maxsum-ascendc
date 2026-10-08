#!/usr/bin/env python3
"""Actual FF NZ->ZZ loads with live MTE1/MMAD; not native timing/precision."""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
from validate_c7_manual_frame import span, source
from validate_c10_balanced_m_shards import cube, ownership, host
ROOT=Path(__file__).resolve().parents[1]
A='if(((s.tree&4) || (RESIDENT_PAD && !M_BALANCE)) && residentA)'
B='if(((s.tree&2) || M_BALANCE) && rows>count)'

def scope(s):
 assert s.count(A)==s.count(B)==1
 assert s.replace(A,'if(((s.tree&4) || RESIDENT_PAD) && residentA)',1).replace(B,'if((s.tree&2) && rows>count)',1)==source('a2e6763')
 for f in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show','1734f16:'+f])
 return span(s,'// The basic-API path owns','// Resident A and larger B packages'),span(s,'// Partition actual M rows','// The basic-API path owns')

def producer(s,e,h):
 f=cube(s,e,h).replace('struct State {','bool directExpected=true;\nstruct State {uint64_t a3D=0;',1)
 f=f.replace('st.aL0+=uint64_t(rows)*count;++st.aLoads;', 'st.aL0+=uint64_t(rows)*count;++st.aLoads;++st.a3D;',1)
 f=f.replace('uint64_t mmads=0,breads=0,bcopies=0,maxRows=0,expectedRows=0,tiles=0;',
  'uint64_t mmads=0,breads=0,bcopies=0,maxRows=0,expectedRows=0,tiles=0,a3D=0,a2D=0,a2elements=0,b2commands=0;')
 f=f.replace('uint64_t expectedA=0,expectedB=0,ctiles=0;',
  'uint64_t expectedA=0,expectedB=0,ctiles=0,expectedA2=0,expectedCommands=0;')
 f=f.replace('    expectedB+=uint64_t(cols)*s.k;++ctiles;', '''    expectedB+=uint64_t(cols)*s.k;++ctiles;
    for(uint32_t k0=0;k0<s.k;k0+=64){
     uint32_t count=(std::min<uint32_t>(64,s.k-k0)+15)/16*16;
     uint32_t rounded=(rows+15)/16*16;
     expectedA2+=uint64_t(rounded)*count;
     expectedCommands+=(BAL&&directExpected)?(rounded>count?count/16:rounded/16):1;
    }''')
 f=f.replace('  assert(st.mmads==ctiles*((s.k+63)/64)&&st.bCopies==st.mmads);', '''  assert(st.mmads==ctiles*((s.k+63)/64)&&st.bCopies==st.mmads);
  assert(st.aLoads==expectedCommands && st.aL0==expectedA2);
  assert(st.a3D==((BAL&&directExpected)?0:st.mmads));''')
 f=f.replace('  mmads+=st.mmads;', '  a3D+=st.a3D;a2D+=st.aLoads-st.a3D;a2elements+=st.aL0;b2commands+=st.bLoads;mmads+=st.mmads;')
 f=f.replace('<<breads<<"\\n";', '<<breads<<" A3D="<<a3D<<" A2D="<<a2D<<" A2elements="<<a2elements<<" B2commands="<<b2commands<<"\\n";')
 f=f.replace(' std::cout<<"13 actual manual FF producers:', ''' for(uint32_t m:{16u,32u,48u,64u,80u,128u})for(uint32_t k:{1104u,1120u,1136u}){
  Schedule s{1,m,272,k,128,256,0,0,1,1,0,0};Run<true>(s,true);
 }
 std::cout<<"31 actual manual FF producers:''',1)
 return f

def main():
 s=(ROOT/'kernel.asc').read_text();e,h=scope(s);c=producer(s,e,h)
 old=source('a2e6763');oe=span(old,'// The basic-API path owns','// Resident A and larger B packages')
 parent=producer(old,oe,h).replace('bool directExpected=true;','bool directExpected=false;')
 full='Run<true>({1,4096,1280,1152,128,256,0,0,1,20,0,0},false);'
 assert full in c and full in parent
 print('kernel SHA256',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 cc=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c10-direct-a2-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([cc,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=180)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  run('direct-producer',c)
  run('parent-3D-producer',parent.replace(full,'').replace('31 actual manual FF producers:','30 actual manual FF producers:'))
  run('ownership-finalizer',ownership(s,e,h))
  p=host(s);run('host',p);run('host-tuning',p,flags=['-DBMMMS_TUNING'])
  # Negative A fixture is constant along K. A positive reference must exercise
  # K-offset faults without confusing a reference-data assertion with a fault.
  proxy=c[:c.index('int main(){')]+'''int main(){
   Run<true>({1,80,272,256,128,256,0,0,1,1,0,0},false);
  }
  '''
  run('positive-fault-reference',proxy)
  controls=[('NZ-pitch','lp.repeatTimes=rows/16;lp.srcStride=1;lp.dstGap=count/16-1;',
     'lp.repeatTimes=rows/16;lp.srcStride=2;lp.dstGap=count/16-1;'),
   ('ZZ-gap','lp.repeatTimes=rows/16;lp.srcStride=1;lp.dstGap=count/16-1;',
     'lp.repeatTimes=rows/16;lp.srcStride=1;lp.dstGap=count/16;'),
   ('K-offset','a1[ki*rows*16+(residentA?k0*rows:0)]','a1[ki*rows*16]'),
   ('last-reader','while(mem[i]->readers)Step(mte1);',''),
   ('L0-ready','AscendC::WaitFlag<AscendC::HardEvent::MTE1_M>(loadReady[ks]);',''),
   ('C-ready','Fence<AscendC::HardEvent::M_FIX>();','')]
  for name,a,b in controls:
   assert a in proxy,name;run('bad-'+name,proxy.replace(a,b,1),True)
  print('Six physical pitch/gap/offset/live-reader/readiness controls rejected PASS')
 print('No geometry/Plan/allocator/Vector edits; native CANN9/BF16/queues/latency/route PENDING.')
if __name__=='__main__':main()
