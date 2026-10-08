#!/usr/bin/env python3
"""Partition mathematics only, not executed Ascend source or NPU timing."""
import bisect
from collections import Counter
M,N,K,BM,BN,PK=1025,1031,1032,128,128,384
NT=(N+BN-1)//BN
cells=[(mt,nt,min(BM,M-mt*BM),min(BN,N-nt*BN))
       for mt in range((M+BM-1)//BM) for nt in range(NT)]
atoms=[];prefix=[0]
for cell,(mt,nt,rows,cols) in enumerate(cells):
 for row in range(0,rows,16):
  count=min(16,rows-row)
  atoms.append((cell,row,count))
  # MMAD pads both M and N, including the M=1 and N=7 tails.
  prefix.append(prefix[-1]+16*((cols+15)//16*16))

def grouped(seq):
 out=[]
 for cell,row,count in seq:
  if out and out[-1][0]==cell and out[-1][1]+out[-1][2]==row:
   c,r,n=out[-1];out[-1]=(c,r,n+count)
  else:out.append((cell,row,count))
 return out

def describe(groups,label):
 coverage=Counter();max_area=max_tiles=max_barriers=0
 a_reads=b_reads=a_copies=tiles=0
 per_worker=[]
 for worker,group in enumerate(groups):
  cache=-1;area=barriers=0
  for cell,row,count in group:
   mt,nt,full_rows,cols=cells[cell]
   for m in range(mt*BM+row,mt*BM+row+count):coverage[(m,nt)]+=1
   padded_rows=(count+15)//16*16;padded_cols=(cols+15)//16*16
   area+=padded_rows*padded_cols;b_reads+=cols*K;tiles+=1
   if cache!=mt:a_copies+=1;a_reads+=full_rows*K;cache=mt
   if padded_rows//16*(padded_cols//16)<10:barriers+=(K+127)//128
  max_area=max(max_area,area);max_tiles=max(max_tiles,len(group));max_barriers=max(max_barriers,barriers)
  per_worker.append((worker,len(group),area,barriers))
 assert len(coverage)==M*NT and all(v==1 for v in coverage.values())
 print(label,'workers',len(groups),'max padded C area',max_area,'max C tiles',max_tiles,
       'max small-MMAD barriers',max_barriers,'Ctiles',tiles,'B packages',tiles*((K+PK-1)//PK),
       'A copies',a_copies,'A elements',a_reads,'B elements',b_reads)
 if len(groups)==20:print('20-worker (worker,Ctiles,paddedArea,small-MMAD barriers):',per_worker)
 return max_area,max_tiles,max_barriers,a_reads,b_reads,tiles

def tail_aware(workers):
 if workers<8:return None
 heavy=[atom for atom in atoms if cells[atom[0]][2:]==(BM,BN)]
 groups=[grouped(heavy[len(heavy)*w//workers:len(heavy)*(w+1)//workers]) for w in range(workers)]
 if any(not group for group in groups):return None
 def metrics(group):
  area=barriers=0
  for c,_,r in group:
   cols=(cells[c][3]+15)//16*16;rows=(r+15)//16*16;area+=rows*cols
   if rows//16*(cols//16)<10:barriers+=(K+127)//128
  return area,barriers,len(group)
 # Keep the N-tail on a worker whose final full-M panel is already resident.
 for cell,(mt,nt,rows,cols) in enumerate(cells):
  if rows==BM and cols<BN:
   eligible=[w for w,g in enumerate(groups) if cells[g[-1][0]][0]==mt]
   assert eligible
   worker=min(eligible,key=lambda w:metrics(groups[w]));groups[worker].append((cell,0,rows))
 # M-tail packets are distributed, rather than accumulated on the last worker.
 for cell,(mt,nt,rows,cols) in enumerate(cells):
  if rows<BM:
   eligible=range(workers)
   if cols<BN:
    eligible=[w for w,g in enumerate(groups) if cells[g[-1][0]][0]==mt]
   worker=min(eligible,key=lambda w:metrics(groups[w]));groups[worker].append((cell,0,rows))
 return groups

def main():
 for workers in [1,3,8,20,24,32]:
  old=[[(i,0,cells[i][2]) for i in range(len(cells)*w//workers,len(cells)*(w+1)//workers)] for w in range(workers)]
  boundaries=[bisect.bisect_right(prefix,prefix[-1]*w//workers)-1 for w in range(workers)]+[len(atoms)]
  assert boundaries[0]==0 and boundaries[-1]==len(atoms)
  new=[grouped(atoms[boundaries[w]:boundaries[w+1]]) for w in range(workers)]
  a=describe(old,'retained whole tile');b=describe(new,'padded-area boundary splits')
  tail=tail_aware(workers)
  if tail is not None:
   describe(tail,'full-cell split plus cache-aware tails')
   assert sum((r+15)//16*16*((cells[c][3]+15)//16*16) for g in tail for c,_,r in g)==prefix[-1]
  assert sum((r+15)//16*16*((cells[c][3]+15)//16*16) for g in new for c,_,r in g)==prefix[-1]
  if workers==20:
   print('Critical padded-area change %',(b[0]/a[0]-1)*100,'global B-read change %',(b[4]/a[4]-1)*100)
 print('6 area / 4 tail-aware comparisons: every valid M/Ntile row covered once, total padded work unchanged PASS')
 print('Unfavorable tile/barrier/extra B costs retained; no kernel change/native candidate/timing claim.')
if __name__=='__main__':main()
