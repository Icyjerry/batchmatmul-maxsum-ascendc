#!/usr/bin/env python3
"""Actual C9 banked producer with deferred-engine/tagged-storage CPU fixture."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('template<typename T>__aicore__ inline void C9BankedPrefetchB(')
b=s.index('template<typename T,bool TILE_STREAM=false',a);producer=s[a:b]
a=s.index('inline bool UseC9BankedL1(');b=s.index('using CacheKey=',a);guard=s[a:b]
hook='''if(UseC9BankedL1(s,p)){
bmmms_manual<T,false,true,true,false,false,false,false,true,true,true,false,false,false,false,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);return;}
'''
select='''if constexpr(BANKED_C9){
static_assert(TILE_STREAM&&PARTITION_STREAM&&!WIDE_K&&!TX1&&TX2&&!PACK_A&&!SPLIT_FMATRIX,"C9 banked frame uses the original NT partition stream");
RunC9BankedCube<T>(pipe,a,b,ring,s,worker);return;
}
'''
inv=s.replace(producer,'',1).replace(guard,'',1).replace(hook,'',1).replace(select,'',1)
inv=inv.replace('bool SPLIT_FMATRIX=false,bool BANKED_C9=false>', 'bool SPLIT_FMATRIX=false>')
inv=inv.replace('PACK_A,SPLIT_FMATRIX,BANKED_C9>(pipe,a,b,ring,s,worker);','PACK_A,SPLIT_FMATRIX>(pipe,a,b,ring,s,worker);',1)
assert inv==subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name])
a=s.index('constexpr AscendC::IsResetLoad3dConfig RESIDENT_NN_KEEP_LOAD3D=');b=s.index('template<typename T,bool TX2=true>',a);load=s[a:b]
a=s.index('struct ManualTaskRange{');b=s.index('template<typename T,bool TX2=true,bool PACK_B=false>',a);ranges=s[a:b]
model=(R/'tests/cpu/c9_banked_cube.cpp.in').read_text()
with tempfile.TemporaryDirectory(prefix='bmmms-c9-banked-') as tmp:
 d=Path(tmp)
 def run(src,name):
  cpp=d/(name+'.cpp');exe=d/name;cpp.write_text(model.replace('// INSERT_SOURCE',load+ranges+src))
  subprocess.run(['c++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
  return subprocess.run([str(exe)],capture_output=True,timeout=180)
 r=run(producer,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='',flush=True)
 for name,old,new in [
  ('multi_ND_stride','ap.srcNdMatrixStride=512','ap.srcNdMatrixStride=256'),
  ('bank_cursor_reset','k0=color*256;++tile','k0=0;++tile'),
  ('A_packet_view','(j/2)*32768','(j/2)*16384'),
  ('B_last_reader','if(within==128)','if(within==0)'),
  ('B_ready','if(within==0)AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(bReady[color]);',''),
  ('A_ready','if(refresh)AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE1>(aReady);',''),
  ('L0_last_reader','AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(free[bs]);',''),
  ('C_last_fix_reader','if(mp.cmatrixInitVal)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cFree[cs]);',''),
  ('MMAD_Fix_ready','Fence<AscendC::HardEvent::M_FIX>();',''),
  ('complete_K','k0<1280;k0+=128','k0<1152;k0+=128')]:
  bad=producer.replace(old,new);assert bad!=producer,name
  r=run(bad,name);assert r.returncode!=0,'missed fault:'+name;print('Rejected',name,flush=True)
print('Ten fault controls/full parent inverse/protected7 PASS; tags + separable integer numeric oracle do not prove native FP16/API scheduling or speed.')
