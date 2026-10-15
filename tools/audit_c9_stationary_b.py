#!/usr/bin/env python3
"""Count complete tile ownership and input bytes using the captured C9 schedule."""
import json,sys
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text());s=p['normal_plan']['schedule']
assert p['build']['kernel_sha256']=='2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b'
assert (s['b'],s['m'],s['n'],s['k'],s['baseM'],s['baseN'],s['nSplit'],s['workers'],s['dual'])==(1,2048,1536,1280,128,128,5,20,36)
mt,nt,ns,w=s['mTiles'],s['nTiles'],s['nSplit'],s['workers'];tile_bytes=128*1280*2
parent=[];alternative=[];seen=[];seen_alt=[]
for core in range(w):
 tasks=list(range(mt*ns*core//w,mt*ns*(core+1)//w));owners=[];mcache=[]
 for task in tasks:
  m,nshard=divmod(task,ns)
  if not mcache or mcache[-1]!=m:mcache.append(m)
  owners.extend((m,n) for n in range(nshard*nt//ns,(nshard+1)*nt//ns))
 seen.extend(owners);parent.append({'core':core,'tiles':len(owners),'cached_A_loads':len(mcache),'B_loads':len(owners),'GM_bytes':(len(mcache)+len(owners))*tile_bytes})
 tasks=range(mt*nt*core//w,mt*nt*(core+1)//w);owners=[(x%mt,x//mt) for x in tasks];ncache=[]
 for _,n in owners:
  if not ncache or ncache[-1]!=n:ncache.append(n)
 seen_alt.extend(owners);alternative.append({'core':core,'tiles':len(owners),'A_loads':len(owners),'cached_B_loads':len(ncache),'GM_bytes':(len(owners)+len(ncache))*tile_bytes})
assert sorted(seen)==sorted(seen_alt)==[(m,n) for m in range(mt) for n in range(nt)]
result={'parent':parent,'stationary_B':alternative,'parent_total_GM_bytes':sum(x['GM_bytes'] for x in parent),'alternative_total_GM_bytes':sum(x['GM_bytes'] for x in alternative),'parent_max_GM_bytes_per_core':max(x['GM_bytes'] for x in parent),'alternative_max_GM_bytes_per_core':max(x['GM_bytes'] for x in alternative),'parent_tiles_per_core':[x['tiles'] for x in parent],'alternative_tiles_per_core':[x['tiles'] for x in alternative],'verdict':'Do not implement: complete ownership already balanced, same max input bytes per core; counts are not timing or hardware-cache predictions'}
print(json.dumps(result,indent=2))
