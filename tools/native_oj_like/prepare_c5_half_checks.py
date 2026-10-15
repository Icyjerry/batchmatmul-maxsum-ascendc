#!/usr/bin/env python3
"""Relayout an existing C5 fixture; retain encoded values and full FP64 golden."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args()
r=Path(a.root).resolve();original=json.loads((r/'native_oj_like/c5.json').read_text())
assert original['shape']==[8,16,32,128] and original['dtype']==1 and original['transpose']==[0,0]
ref=json.loads((r/'inputs/c5/reference.json').read_text());assert ref['case']==original and ref['full_math']
raw=[(r/'inputs/c5'/n).read_bytes() for n in ['x1.b16','x2.b16']]
assert ref['input_sha256']==[hashlib.sha256(b).hexdigest() for b in raw]
x=np.frombuffer(raw[0],dtype='<f2').reshape(8,16,128).copy()
z=np.frombuffer(raw[1],dtype='<f2').reshape(8,128,32).copy()
expected=(r/'inputs/c5/golden.f32').read_bytes()
for tx1 in (0,1):
    for tx2 in (0,1):
        tag=f'{tx1}{tx2}';case=dict(original);case['transpose']=[tx1,tx2]
        case['provenance']='Explicit C5 FP16 four-layout local fixture; same encoded logical values as parent FF. Formal dtype/layout remain unconfirmed.'
        case['capture']={'op_type':'vector','family':'bmmms_c5_half_vector','block_dim':8,'mix_block_dim':0,'aic':0,'aiv':8}
        cp=r/f'native_oj_like/c5-half-{tag}.json';assert not cp.exists();cp.write_text(json.dumps(case,indent=2))
        folders=[]
        for negative in (False,True):
            q=np.abs(x) if negative else x
            d=-np.abs(z) if negative else z
            sx=(q.transpose(0,2,1) if tx1 else q).copy()
            sz=(d.transpose(0,2,1) if tx2 else d).copy()
            # Full original logical M/K/N math, using actual half values, not a subset.
            golden=(q.astype(np.float64)@d.astype(np.float64)).max(axis=-1).sum(axis=-1,dtype=np.float64).astype('<f4')
            assert np.all(np.isfinite(golden))
            if not negative:assert golden.tobytes()==expected
            folder=r/'inputs'/f'c5-half-{tag}{"-negative" if negative else ""}'
            folder.mkdir(parents=True,exist_ok=False)
            payload=[sx.tobytes(),sz.tobytes()]
            if tag=='00' and not negative:assert payload==raw
            for name,data in zip(['x1.b16','x2.b16'],payload):(folder/name).write_bytes(data)
            (folder/'golden.f32').write_bytes(golden.tobytes())
            (folder/'reference.json').write_text(json.dumps({'case':case,'full_math':True,'golden':golden.tolist(),'numpy':np.__version__,'all_negative':negative,'input_sha256':[hashlib.sha256(b).hexdigest() for b in payload],'original_parent_input_sha256':ref['input_sha256']},indent=2))
            folders.append(str(folder))
        (r/f'native_oj_like/c5-half-{tag}.sequence.json').write_text(json.dumps([folders[0],folders[1],folders[0]],indent=2))
print('Four C5 layouts and mixed-negative-mixed sequences prepared; parent inputs/golden unchanged.')
