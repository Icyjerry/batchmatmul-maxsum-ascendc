#!/usr/bin/env python3
"""Known finite C1 inputs testing actual FP32 product range; not a timing preset."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--subnormal',action='store_true');a=p.parse_args();r=Path(a.root).resolve()
case=json.loads((r/'native_oj_like/c1.json').read_text());assert case['shape']==[1,1,1,32] and case['dtype']==1
folders=[]
checks=[('minsubnormal',[2**-24]*32,[65504]*32),('maxsubnormal',[1023*2**-24]*32,[65504]*32)] if a.subnormal else [('maxproduct',[65504]+[0]*31,[65504]+[0]*31),('smallproduct',[2**-14]*32,[2**-14]*32),('negative',[1]*32,[-1]*32)]
for name,x,y in checks:
 d=r/'inputs'/('c1-mixed-'+name);d.mkdir(parents=True,exist_ok=False)
 sa=np.asarray(x,dtype='<f2');sb=np.asarray(y,dtype='<f2');assert np.all(np.isfinite(sa)) and np.all(np.isfinite(sb))
 # Full actual storage FP64 matmul -> maxN -> sumM -> FP32, without truncation.
 golden=(sa.astype(np.float64).reshape(1,1,32)@sb.astype(np.float64).reshape(1,32,1)).max(axis=-1).sum(axis=-1,dtype=np.float64).astype('<f4')
 assert np.all(np.isfinite(golden))
 raw=[sa.tobytes(),sb.tobytes()]
 for n,b in zip(['x1.b16','x2.b16'],raw):(d/n).write_bytes(b)
 (d/'golden.f32').write_bytes(golden.tobytes());(d/'reference.json').write_text(json.dumps({'case':case,'full_math':True,'stress':name,'golden':golden.tolist(),'input_sha256':[hashlib.sha256(b).hexdigest() for b in raw],'numpy':np.__version__},indent=2));folders.append(str(d))
sequence=[str(r/'inputs/c1'),*folders,str(r/'inputs/c1')]
filename='c1_mixed_subnormal_sequence.json' if a.subnormal else 'c1_mixed_input_sequence.json'
(r/'native_oj_like'/filename).write_text(json.dumps(sequence,indent=2));print('Same-address sequence:',sequence)
