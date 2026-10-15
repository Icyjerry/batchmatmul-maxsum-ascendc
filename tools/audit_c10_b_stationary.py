#!/usr/bin/env python3
"""C10 fixed-N/M-shard proposal only: exact traffic and ownership arithmetic."""
from collections import Counter
import json
B,M,N,K=1,4096,1280,1152
BM=BN=BK=128;PK=384;workers=20;nsplit=5;mt=32;nt=10
old=Counter();new=Counter();old_a=[];old_bytes=[];old_segments=[]
for w in range(workers):
 first,last=160*w//workers,160*(w+1)//workers
 refresh=0;cached=-1;tiles=0
 for t in range(first,last):
  m,ns=divmod(t,nsplit)
  if m!=cached:refresh+=1;cached=m
  for n in range(ns*2,(ns+1)*2):old[m,n]+=1;tiles+=1
 old_a.append(refresh)
 old_bytes.append(refresh*BM*K*2+tiles*BN*K*2)
 old_segments.append(refresh*BM+tiles*(K//PK)*PK)
 # Each N shard has four M owners. Keep old five row-max partials.
 ns,shard=divmod(w,4)
 frames=[]
 for ni in range(2):
  for local_m in range(8):
   m=shard*8+local_m;n=ns*2+ni
   new[m,n]+=1;frames.append((m,n))
 assert len(frames)==16
 # For each of the eight M tiles, the same owner merges both N tiles.
 assert all([m for m,n in frames].count(m)==2 for m in range(shard*8,(shard+1)*8))
assert old==new and len(old)==320 and set(old.values())=={1}
new_bytes=2*BN*K*2+16*BM*K*2
new_segments=2*K+16*(K//PK)*BM
assert sum(old_a)==48 and sum(old_bytes)==108527616
assert new_bytes*20==106168320 and sum(old_segments)==374784 and new_segments*20==168960
# Exact L1 intervals: full NZ B, then two MK384 A slabs. L0/C original.
regions=[(0,BN*K*2),(BN*K*2,BN*K*2+BM*PK*2),(BN*K*2+BM*PK*2,BN*K*2+2*BM*PK*2)]
assert regions==[(0,294912),(294912,393216),(393216,491520)]
assert regions[-1][1]+4096<=524032
# Two N-major passes fold into 8*64 FP32 row maxima per AIV, no new GM.
# Mixed and all-negative separable numeric proxy; not FP16/BF16/API proof.
for negative in (False,True):
 partials={};seen=set()
 for w in range(workers):
  ns,shard=divmod(w,4);acc={}
  for ni in range(2):
   for lm in range(8):
    for row in range(128):
     m=(shard*8+lm)*128+row
     value=max((1+m%3)*(-1-(n%11) if negative else n%17-8) for n in range((ns*2+ni)*128,(ns*2+ni+1)*128))
     acc[m]=max(acc.get(m,-10**9),value)
  for m,value in acc.items():assert (ns,m) not in seen;seen.add((ns,m));partials[ns,m]=value
 score=sum(max(partials[ns,m] for ns in range(5)) for m in range(M))
 golden=sum(max((1+m%3)*(-1-(n%11) if negative else n%17-8) for n in range(N)) for m in range(M))
 assert score==golden and (not negative or score<0)
assert len(seen)==5*M
# Original partial, 2x span2 rings, notification and finalizer geometry retained.
partial_bytes=5*M*4;ring_bytes=20*2*2*BM*BN*4
assert 16777216+partial_bytes+ring_bytes==22102016
v={'proposal_only':True,'old_A_full_copies':48,'old_B_package_copies':960,'new_B_full_copies':40,'new_A_package_copies':960,'old_input_bytes':sum(old_bytes),'new_input_bytes':new_bytes*20,'old_worst_worker_bytes':max(old_bytes),'new_worst_worker_bytes':new_bytes,'old_input_row_segments':sum(old_segments),'new_input_row_segments':new_segments*20,'old_MMAD':320*9,'new_MMAD':320*9,'old_Fix':320,'new_Fix':320,'old_notifications':160,'new_notifications':160,'partial_bytes':partial_bytes,'ring_bytes':ring_bytes,'L1_intervals':regions,'extra_vector_max_state_per_AIV_bytes':7*64*4}
print(json.dumps(v,indent=2))
print('Ownership/MaxN-before-SumM/traffic/capacity arithmetic PASS; no producer, event, CANN, native or speed claim.')
