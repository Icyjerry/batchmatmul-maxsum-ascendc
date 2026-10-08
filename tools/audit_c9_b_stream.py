#!/usr/bin/env python3
"""Packet FIFO arithmetic audit only; kernel stays the passed baseline."""
from collections import deque
from pathlib import Path
from validate_c7_manual_frame import source,span
ROOT=Path(__file__).resolve().parents[1]
def retained(B,M,N,K,BM,BN,PK,NS,W,worker):
 out=[]
 for task in range(worker,B*((M+BM-1)//BM)*NS,W):
  ns=task%NS;batch=task//(NS*((M+BM-1)//BM))
  for nt in range(ns*((N+BN-1)//BN)//NS,(ns+1)*((N+BN-1)//BN)//NS):
   for k in range(0,K,PK):out.append((task,batch,nt,k,min(PK,K-k),min(BN,N-nt*BN)))
 return out

def cursor(B,M,N,K,BM,BN,PK,NS,W,worker):
 # Proposed three-coordinate persistent cursor. Not an Ascend source execution.
 mt=(M+BM-1)//BM;ntiles=(N+BN-1)//BN;tasks=B*mt*NS
 task=worker;nt=(task%NS)*ntiles//NS;k=0;out=[]
 while task<tasks:
  out.append((task,task//(NS*mt),nt,k,min(PK,K-k),min(BN,N-nt*BN)))
  k+=PK
  if k>=K:
   k=0;nt+=1
   if nt>=(task%NS+1)*ntiles//NS:
    task+=W;nt=(task%NS)*ntiles//NS
 return out

def fifo(seq):
 q=deque(seq[:2]);ahead=min(2,len(seq));got=[];cross=0
 while q:
  current=q.popleft();got.append(current)
  if ahead<len(seq):
   nxt=seq[ahead];q.append(nxt);ahead+=1
   # Next tile's packet is allowed while the current tile is still live.
   cross+=((nxt[0],nxt[2])!=(current[0],current[2]))
 assert got==seq and ahead==len(seq)
 return cross

def main():
 s=(ROOT/'kernel.asc').read_text();assert s==source('a2e6763')
 e=span(s,'void bmmms_case9_packages(','// Isolated case12 packed-B');cube=e[:e.index('#else\n    AscendC::TQue')]
 assert 'Case9CopyBPackage<T,TX2,PAD_MN>(bq,b,s,bPackK,validCols,batch,n0,0);' in cube
 assert 'if(s.k>bPackK)Case9CopyBPackage' in cube
 assert 'if(bStart+2*bPackK<s.k)' in cube
 assert 'cq.EnQue(c);c=cq.DeQue<float>();' in e
 configs=0;packets=0
 for B in [1,2]:
  for M in [17,129,513]:
   for N in [73,257,1536]:
    for K in [40,264,1280]:
     for PK in [128,256,384]:
      for NS in [1,3]:
       if NS>(N+127)//128:continue
       for W in [1,3,20,32]:
        for worker in range(W):
         args=(B,M,N,K,128,128,PK,NS,W,worker)
         old=retained(*args);new=cursor(*args);assert old==new;fifo(new)
         packets+=len(new);configs+=1
 # Exact 20-core source geometry previously executed in the host audit.
 old_prime=new_prime=total=reads=cross=0
 for worker in range(20):
  old=retained(1,2048,1536,1280,128,128,256,3,20,worker)
  tiles={(p[0],p[2]) for p in old};old_prime+=len(tiles)*2;new_prime+=min(2,len(old));total+=len(old)
  reads+=sum(p[4]*p[5] for p in old);cross+=fifo(old)
 assert total==960 and old_prime==384 and new_prime==40 and reads==31457280
 print(configs,'worker packet sequences;',packets,'packets, exact source ordering/tails/batch/task/idle/FIFO equivalence PASS')
 print('Exact conditional20-core C9: total B DMA packets',total,'elements',reads,
       'old per-tile startup calls',old_prime,'new one-time priming calls',new_prime,
       'packets allowed across live tile boundary',cross)
 print('344 startup copies are moved earlier, NOT removed. No changed kernel/CANN/protocol/layout/native latency proof.')
if __name__=='__main__':main()
