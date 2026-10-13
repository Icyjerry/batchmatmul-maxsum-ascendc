#!/usr/bin/env python3
"""Coordinate oracle for proposed raw row im2col; DOES NOT execute SDK Load3D."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def panel(rows,padded,K,role,batch):
 # Interpret row-major [R,K] as [C1=1,H=1,W=R*K/16,C0=16].
 group=K//16;width=rows*group;right=(padded-rows)*group
 assert K%16==0 and padded%16==0 and 0<=right<=255
 assert (width+right-group)//group+1==padded
 raw=[(batch,r,k) for r in range(rows) for k in range(K)]
 out=[None]*(padded*K)
 for r in range(padded):
  for k in range(K):
   x=r*group+k//16;channel=k%16
   value=raw[x*16+channel] if x<width else None
   pos=((r//16*(K//16)+k//16)*256+(r%16)*16+k%16 if role=='ZZ' else
        (k//16*(padded//16)+r//16)*256+(r%16)*16+k%16)
   assert out[pos] is None
   out[pos]=value if value is not None else ('pad',r,k)
 # Independent retained NZ->native address mapping, with explicit padded tags.
 for r in range(padded):
  for k in range(K):
   pos=((r//16*(K//16)+k//16)*256+(r%16)*16+k%16 if role=='ZZ' else
        (k//16*(padded//16)+r//16)*256+(r%16)*16+k%16)
   assert out[pos]==((batch,r,k) if r<rows else ('pad',r,k))
 return raw,out,right

def main():
 assert (ROOT/'kernel.asc').read_bytes()==subprocess.check_output(['git','show','e2f1b63:kernel.asc'],cwd=ROOT),'no speculative kernel API changes'
 for b in range(13):
  ar,a,padA=panel(23,32,192,'ZZ',b);br,z,padB=panel(73,80,192,'ZN',b)
  assert padA==108 and padB==84
  for m in range(23):
   for n in range(73):
    for k in range(192):
     ap=(m//16*12+k//16)*256+(m%16)*16+k%16
     bp=(k//16*5+n//16)*256+(n%16)*16+k%16
     assert a[ap]==ar[m*192+k] and z[bp]==br[n*192+k]
 assert 32*192*2<=65536 and 80*192*2<=65536 and 32*80*4<=131072
 assert (32+80)*192*2+4096<=524032
 # Wrong pixel-vs-row stride consumes mixed query rows; reject independently.
 wrong=[(r*1+k//16)*16+k%16 for r in range(23) for k in range(192)]
 assert wrong!=list(range(23*192))
 print('Raw-im2col coordinate model PASS:13 batches/full M23 N73 K192/read addresses/nativeZZ+ZN/padding108+84/capacity')
 print('SDK field names, filter/stride/padding support, native load layout, timings ALL PENDING; not production code evidence.')
if __name__=='__main__':main()
