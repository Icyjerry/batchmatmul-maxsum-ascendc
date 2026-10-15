#!/usr/bin/env python3
"""Use identical full-math fixture bytes with original MIX capture metadata."""
import argparse, hashlib, json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();r=Path(a.root)
capture=json.loads((r/'native_oj_like/c5.json').read_text())['capture']
for tag in ['01','10','11']:
    source=r/'inputs'/f'c5-half-{tag}';ref=json.loads((source/'reference.json').read_text())
    assert ref['full_math'] and ref['case']['shape']==[8,16,32,128] and ref['case']['dtype']==1
    case=dict(ref['case']);case['capture']=capture
    cp=r/f'native_oj_like/c5-parent-{tag}.json';assert not cp.exists();cp.write_text(json.dumps(case,indent=2))
    folder=r/'inputs'/f'c5-parent-{tag}';folder.mkdir(exist_ok=False)
    for n in ['x1.b16','x2.b16','golden.f32']:(folder/n).write_bytes((source/n).read_bytes())
    ref['case']=case
    assert ref['input_sha256']==[hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ['x1.b16','x2.b16']]
    (folder/'reference.json').write_text(json.dumps(ref,indent=2))
print('Three original-layout fixtures prepared, same input/golden bytes; original FF fixture unchanged.')
