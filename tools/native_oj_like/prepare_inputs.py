#!/usr/bin/env python3
"""Generate native storage then evaluate ALL FP64 products/N maxima/M rows."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--negative',action='store_true');a=p.parse_args()
 case=json.loads(Path(a.case).read_text());B,M,N,K=case['shape'];dt=case['dtype'];tx1,tx2=case['transpose']
 rng=np.random.default_rng(1746);x=rng.normal(size=(B,M,K)).astype(np.float32);z=rng.normal(size=(B,N,K)).astype(np.float32)
 if a.negative:x=np.abs(x);z=-np.abs(z)
 x/=np.sqrt(np.sum(x*x,axis=-1,keepdims=True));z/=np.sqrt(np.sum(z*z,axis=-1,keepdims=True))
 def native(v):
  if dt==1:return v.astype('<f2').view('<u2')
  bits=v.view('<u4');return ((bits+0x7fff+((bits>>16)&1))>>16).astype('<u2')
 def expand(v):
  if dt==1:return v.view('<f2').astype(np.float64)
  return (v.astype('<u4')<<16).view('<f4').astype(np.float64)
 sx=native(x.transpose(0,2,1).copy() if tx1 else x);sz=native(z if tx2 else z.transpose(0,2,1).copy())
 logicalx=expand(sx);logicalz=expand(sz)
 if tx1:logicalx=logicalx.transpose(0,2,1)
 if tx2:logicalz=logicalz.transpose(0,2,1)
 golden=(logicalx@logicalz).max(axis=-1).sum(axis=-1,dtype=np.float64).astype('<f4')
 assert np.all(np.isfinite(golden));out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 for name,data in [('x1.b16',sx.tobytes()),('x2.b16',sz.tobytes()),('golden.f32',golden.tobytes())]:(out/name).write_bytes(data)
 (out/'reference.json').write_text(json.dumps({'case':case,'seed':1746,'numpy':np.__version__,'all_negative':a.negative,'golden':golden.tolist(),'full_math':True,'input_sha256':[hashlib.sha256(sx.tobytes()).hexdigest(),hashlib.sha256(sz.tobytes()).hexdigest()]},indent=2))
 print('Full FP64 storage reference',golden.tolist(),flush=True)
if __name__=='__main__':main()
