#!/usr/bin/env python3
"""Independent fullK physical addressing oracle and source scope, not timing."""
from pathlib import Path
import subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1]
def entry(s):
 a=s.index('template<typename T,bool PIPELINE_HALVES=');b=s.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>',a)
 return s[a:b]
def main():
 s=(ROOT/'kernel.asc').read_text();old=subprocess.check_output(['git','show','e2f1b63:kernel.asc'],text=True,cwd=ROOT)
 e,oe=entry(s),entry(old)
 assert s.replace(e,oe,1).replace('bmmms_tall_single_frame<T,true,true><<<','bmmms_tall_single_frame<T,true><<<',1)==old
 assert e[e.index('#else\nauto x='):]==oe[oe.index('#else\nauto x='):]
 for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
  assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=ROOT)
 # ND2NZ and blockwise transpose are independent coordinate-tag oracles.
 N,K,H=64,128,256
 cached=[None]*(N*K)
 for k in range(K):
  for n in range(N):cached[n//16*K*16+k*16+n%16]=(n,k)
 a2=[None]*(N*K)
 for block in range(N*K//256):
  for i in range(16):
   for j in range(16):a2[block*256+i*16+j]=cached[block*256+j*16+i]
 for n in range(N):
  for k in range(K):assert a2[(n//16*(K//16)+k//16)*256+(n%16)*16+k%16]==(n,k)
 seen=set()
 for half in range(2):
  panel=[None]*(H*K)
  for m in range(H):
   for k in range(K):panel[k//16*H*16+m*16+k%16]=(half*H+m,k)
  # Non-transposed load copies the whole contiguous NZ into native ZN.
  for m in range(H):
   for k in range(K):assert panel[(k//16*(H//16)+m//16)*256+(m%16)*16+k%16]==(half*H+m,k)
  co=[None]*(N*H)
  for n in range(N):
   for m in range(H):co[m//16*N*16+n*16+m%16]=(n,half*H+m)
  for n in range(N):
   for m in range(H):
    assert co[m//16*N*16+n*16+m%16]==(n,half*H+m)
    offset=half*N*H+n*H+m;assert offset not in seen;seen.add(offset)
 assert len(seen)==N*H*2
 assert N*K*2<=65536 and H*K*2==65536 and 2*N*H*4==131072
 print('Source whole-inverse/unchanged AIV/protected7; fullK A2 ZZ/B2 ZN/CO1-ND bothhalf coverage and capacity PASS',hashlib.sha256(s.encode()).hexdigest())
 print('This oracle does not execute Ascend events/native float accumulation. Native full golden and capture required.')
if __name__=='__main__':main()
