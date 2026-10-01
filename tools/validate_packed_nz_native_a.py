#!/usr/bin/env python3
"""Execute the isolated packed Cube body, with documented CPU instruction models.

B's actual preprocessing/copy/load bits are checked separately by the parent
packed_b_nz model. This validates composition and source/event ownership,
not CANN hardware event timing or FP16/BF16 arithmetic.
"""
from pathlib import Path
import subprocess,shutil,tempfile,hashlib
root=Path(__file__).resolve().parents[1];src=(root/'kernel.asc').read_text()
a=src.index('void bmmms_manual_case12_packed(');b=src.index('struct Plan {',a);family=src[a:b]
a=family.index('    AscendC::SetAtomicNone();');b=family.index('\n#else',a);body=family[a:b]
body=body.replace('AscendC::GetBlockIdx()','worker')
redirect='        b.SetGlobalBuffer(reinterpret_cast<__gm__ T*>(partial+packedBOffset));'
assert redirect in body;body=body.replace(redirect,'        // CPU B argument already points to the existing packed region.')
helpers=src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
a=src.index('template<typename T>\n__aicore__ inline void ManualTransposeFullM(');b=src.index('template<typename T>\n__aicore__ inline void ManualFullMReadB(',a)
helpers+=src[a:b]
a=src.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false,bool NZ_B=false>');helpers+=src[a:src.index('// Isolated case12 packed-B kernel',a)]
helpers+='''template<class T>void RunPackedCube(AscendC::TPipe& pipe,AscendC::GlobalTensor<T> a,
 AscendC::GlobalTensor<T> b,AscendC::GlobalTensor<float> ring,const Schedule& s,uint32_t worker){
 constexpr bool TX1=true,TX2=false,PAD_MN=false,RESIDENT_PAD=false,FULL_A=false,RESIDENT_B=false,NZ_B=true;
 const uint32_t span=1,slots=2,slotSize=s.baseM*s.baseN;const uint64_t packedBOffset=1;
 const int64_t tasks=s.b*s.mTiles*s.nSplit;uint32_t sequence=0;
'''+body+'\n}\n'
parent=subprocess.check_output(['git','show','99fc974:kernel.asc'],cwd=root,text=True)
added='''                if constexpr(NZ_B) {
                    // This family holds the complete aligned TT-stored A in L1.
                    // One raw-bit rectangle replaces the per-M16 Load2D loop.
                    ManualTransposeFullM(a2,a1,s.k,rows,count,k0);
                } else if((s.tree&4) && residentA) {'''
assert src.count(added)==1
assert src.replace(added,'                if((s.tree&4) && residentA) {')==parent, 'mutation outside native A loading'
model=(root/'tests/cpu/packed_nz_cube_model.cpp.in').read_text().replace('// INSERT_HELPERS',helpers)
compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
print('Actual Cube body CPU model; kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
with tempfile.TemporaryDirectory(prefix='bmmms-packed-native-a-') as d:
 cpp,exe=Path(d)/'cube.cpp',Path(d)/'cube';cpp.write_text(model)
 subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('CANN9 composition compile/NPU accuracy and latency PENDING.')
