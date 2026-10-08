#!/usr/bin/env python3
"""Actual FF producer with delayed two-AIV GM release; no hardware timing."""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile
from validate_c7_manual_frame import span, source
from validate_c10_balanced_m_shards import cube, ownership, host
ROOT=Path(__file__).resolve().parents[1]
EARLY='if constexpr(!FULL_A && !M_BALANCE)'
LATE='''// GM reuse is needed at writeback; Cube may run while AIV reads the old slot.
                if constexpr(FULL_A || M_BALANCE)'''

def scope(s):
 assert s.count(EARLY)==s.count(LATE)==1
 assert s.replace(EARLY,'if constexpr(!FULL_A)',1).replace(LATE,'if constexpr(FULL_A)',1)==source('a2e6763')
 for p in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/p).read_bytes()==subprocess.check_output(['git','show','1734f16:'+p])
 return span(s,'// The basic-API path owns','// Resident A and larger B packages'),span(s,'// Partition actual M rows','// The basic-API path owns')

def producer(s,e,h):
 f=cube(s,e,h)
 f=f.replace('struct State {','''bool expectLate=true;
uint64_t totalBlocked=0,totalIssued=0,totalExecuted=0,totalAivReads=0;
struct State {
 bool late=false,acquired[2]={false,false};unsigned pending[2]={0,0};
 std::vector<float>* ringData[2]={nullptr,nullptr};size_t ringOffset[2]={0,0};
 std::vector<float> snapshot[2];Expected prior[2];uint64_t completed=0;''',1)
 a=f.index('template<int Mode>void CrossCoreWaitFlag');b=f.index('struct Nd2NzParams',a)
 f=f[:a]+'''void ReleaseReaders(unsigned slot){
 assert(st.pending[slot]==3 && !st.acquired[slot] && st.cross[slot]==0);
 const auto& e=st.prior[slot];auto& data=*st.ringData[slot];size_t offset=st.ringOffset[slot];
 // Cube is allowed to progress while both AIVs still own the previous GM slot.
 while(!mac.empty())Step(mac);
 for(size_t j=0;j<st.snapshot[slot].size();++j)assert(data[offset+j]==st.snapshot[slot][j]);
 if(st.fixes<st.expected.size()){
  uint64_t kt=(st.s.k+63)/64;
  assert(st.completed-st.fixes*kt==(st.late?kt:0));
  totalExecuted+=st.completed-st.fixes*kt;
 }
 for(unsigned order=0;order<2;++order){
  unsigned sub=(st.fixes+order)&1;assert(st.cross[slot]==0);
  unsigned first=sub*(st.s.baseM/2),end=std::min(first+st.s.baseM/2,e.rows);
  for(unsigned r=first;r<end;++r)for(unsigned n=0;n<e.cols;++n){
   assert(data[offset+r*st.s.baseN+n]==st.snapshot[slot][r*st.s.baseN+n]);++totalAivReads;
  }
  st.pending[slot]&=~(1u<<sub);
  if(!st.pending[slot])st.cross[slot]=1;
 }
 assert(st.cross[slot]==1 && !st.pending[slot]);
}
template<int Mode>void CrossCoreWaitFlag(int id){
 assert(Mode==2 && id>=4 && id<6);unsigned slot=id-4;
 if(st.fixes<st.expected.size()){
  uint64_t kt=(st.s.k+63)/64,issued=st.mmads-st.fixes*kt;
  assert(issued==(st.late?kt:0));
  if(st.pending[slot]){++totalBlocked;totalIssued+=issued;}
 }
 if(st.pending[slot])ReleaseReaders(slot);
 assert(st.cross[slot]--==1);st.acquired[slot]=true;
}
template<int Mode,int P>void CrossCoreSetFlag(int id){
 assert(Mode==2 && P==PIPE_FIX && id<2 && st.acquired[id] && !st.pending[id] && !st.cross[id]);
 auto& data=*st.ringData[id];size_t offset=st.ringOffset[id];
 st.snapshot[id]=std::vector<float>(data.begin()+offset,data.begin()+offset+st.s.baseM*st.s.baseN);
 st.acquired[id]=false;st.pending[id]=3;
}
'''+f[b:]
 f=f.replace('    mac.push_back([=]{','    mac.push_back([=]{++st.completed;',1)
 f=f.replace('    assert(st.fixes<st.expected.size());const auto e=st.expected[st.fixes++];',
 '''    assert(st.fixes<st.expected.size());const auto e=st.expected[st.fixes++];
    unsigned slot=(st.fixes-1)&1;
    assert(st.acquired[slot] && !st.pending[slot] && st.cross[slot]==0);
    st.ringData[slot]=dst.data;st.ringOffset[slot]=dst.offset;st.prior[slot]=e;''',1)
 f=f.replace('st.s=s;st.tx1=false;st.tx2=false;','st.s=s;st.tx1=false;st.tx2=false;st.late=expectLate&&BAL;',1)
 f=f.replace(' assert(a==oldA&&b==oldB',
 ''' assert(a==oldA&&b==oldB''',1)
 f=f.replace(' std::cout<<"13 actual manual FF producers:',
 ''' std::cout<<"Blocked GM acquisitions="<<totalBlocked<<" K work issued before credit="<<totalIssued<<" K work executed while previous GM owned="<<totalExecuted<<" AIV valid elements="<<totalAivReads<<"\\n";
 assert(totalBlocked && totalAivReads);
 assert(expectLate?(totalIssued && totalExecuted):(!totalIssued && !totalExecuted));
 std::cout<<"13 actual manual FF producers:''',1)
 return f

def main():
 s=(ROOT/'kernel.asc').read_text();e,h=scope(s);c=producer(s,e,h)
 old=source('a2e6763');oe=span(old,'// The basic-API path owns','// Resident A and larger B packages')
 parent=producer(old,oe,h).replace('bool expectLate=true;','bool expectLate=false;')
 full='Run<true>({1,4096,1280,1152,128,256,0,0,1,20,0,0},false);'
 assert full in c and full in parent
 print('kernel SHA256',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 cc=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-c10-late-credit-') as t:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(t)/(name+'.cpp'),Path(t)/name;cpp.write_text(code)
   subprocess.run([cc,'-std=c++17','-O2',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],stdout=subprocess.DEVNULL if bad else None,stderr=subprocess.DEVNULL if bad else None,timeout=180)
   assert (r.returncode!=0) if bad else (r.returncode==0),name
  run('late-producer',c)
  run('parent-early-producer',parent.replace(full,'').replace('13 actual manual FF producers:', '12 actual manual FF producers:'))
  run('ownership-finalizer',ownership(s,e,h))
  p=host(s);run('host',p);run('host-tuning',p,flags=['-DBMMMS_TUNING'])
  proxy=c.replace(full,'')
  controls=[('GM-wait',LATE+'AscendC::CrossCoreWaitFlag<2>(4+slot);',''),
   ('C-wait','if(pairIndex==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cFree[cs]);',''),
   ('C-ready','Fence<AscendC::HardEvent::M_FIX>();',''),
   ('one-AIV-credit','if(!st.pending[slot])st.cross[slot]=1;','st.cross[slot]=1;'),
   ('L0-ready','AscendC::WaitFlag<AscendC::HardEvent::MTE1_M>(loadReady[ks]);','')]
  for name,a,b in controls:
   assert a in proxy,name;run('bad-'+name,proxy.replace(a,b,1),True)
  print('Five GM/C/L0/two-AIV readiness controls rejected PASS')
 print('No geometry/Plan/allocator/Vector edits; CANN9 queue/precision/latency/route PENDING.')
if __name__=='__main__':main()
