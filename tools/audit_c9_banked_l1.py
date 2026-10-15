#!/usr/bin/env python3
"""C9 address/packet design audit; not an NPU bank, event or latency model."""
import argparse, hashlib, json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('plan',nargs='?',default=root/'tests/cpu/c9_captured_plan.json');a=p.parse_args()
assert hashlib.sha256((root/'kernel.asc').read_bytes()).hexdigest()=='2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b'
record=json.loads(Path(a.plan).read_text());s=record['normal_plan']['schedule']
assert record['build']['kernel_sha256']=='2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b'
assert tuple(s[k] for k in ['b','m','n','k','baseM','baseN','mTiles','nTiles','nSplit','workers','window','kChunk','dual'])==(1,2048,1536,1280,128,128,16,12,5,20,3,256,36)
BM=BN=128;K=1280;PK=256;HALF=262144;PACK_BYTES=65536
B_BASE=[196608,393216];END=458752
def a_base(j):return (j%2)*HALF+(j//2)*PACK_BYTES
def a_addr(m,k):
    j,local=divmod(k,PK)
    return a_base(j)+2*((local//16)*BM*16+m*16+local%16)
def a_source(m,k):return m*K+k

# Independent full tagged-storage packing. Every original element appears once.
def pack_a(source_matrix_stride=512):
    slots={}
    # Public Nd2Nz stride units are elements. Two multi-ND descriptors, not five calls.
    for color,nd_num in [(0,3),(1,2)]:
        for nd in range(nd_num):
            for m in range(BM):
                for local in range(PK):
                    dst=color*HALF+2*(nd*32768+(local//16)*BM*16+m*16+local%16)
                    src=color*PK+nd*source_matrix_stride+m*K+local
                    assert dst not in slots and dst%2==0 and 0<=dst<END and 0<=src<BM*K
                    slots[dst]=src
    for m in range(BM):
        for k in range(K):assert slots[a_addr(m,k)]==a_source(m,k)
    return slots
slots=pack_a();a_bytes={b for dst in slots for b in (dst,dst+1)}
for m in range(BM):
    for k in range(K):assert slots[a_addr(m,k)]==a_source(m,k)
for color,base in enumerate(B_BASE):
    assert base//HALF==color and (base+PACK_BYTES-1)//HALF==color
    assert not a_bytes.intersection(range(base,base+PACK_BYTES))
assert len(a_bytes)==327680 and max(B_BASE)+PACK_BYTES==END
assert all((a_base(j)+PACK_BYTES-1)//HALF==j%2 for j in range(5))
assert 327680+2*PACK_BYTES==END # Same total L1 payload as the original.

def advance(cursor,color):
    tile,k=cursor;k+=2*PK
    return (tile+1,color*PK) if k>=K else (tile,k)

def worker(core,wrong_wrap=False):
    first=s['mTiles']*s['nSplit']*core//s['workers']
    last=s['mTiles']*s['nSplit']*(core+1)//s['workers']
    begin=(first//s['nSplit'])*s['nTiles']+(first%s['nSplit'])*s['nTiles']//s['nSplit']
    end=(last//s['nSplit'])*s['nTiles']+(last%s['nSplit'])*s['nTiles']//s['nSplit']
    cursor=[(begin,0),(begin,PK)];buffer=[None,None];free=[True,True]
    issued=[];consumed=[]
    def prefetch(c):
        if cursor[c][0]>=end:return
        assert free[c];buffer[c]=cursor[c];free[c]=False;issued.append(cursor[c])
        cursor[c]=advance(cursor[c],0 if wrong_wrap else c)
    prefetch(0);prefetch(1)
    for tile in range(begin,end):
        for j in range(5):
            c=j%2;assert buffer[c]==(tile,j*PK),(core,tile,j,buffer,c)
            # Both original BK128 readers must finish before this B packet is recycled.
            for inner in (0,128):
                assert not free[c] and buffer[c]==(tile,j*PK)
                for k in (j*PK+inner,j*PK+inner+127):
                    assert a_addr(0,k)//HALF==B_BASE[c]//HALF
                assert (inner+128)*BN*2<=PACK_BYTES
            consumed.append(buffer[c]);buffer[c]=None;free[c]=True;prefetch(c)
    assert all(free) and all(v is None for v in buffer)
    assert sorted(issued)==sorted(consumed)==[(tile,k) for tile in range(begin,end) for k in range(0,K,PK)]
    return len(consumed),end-begin

counts=[worker(c) for c in range(20)]
assert sum(x[0] for x in counts)==192*5
assert [x[1] for x in counts]==[9,10,9,10,10]*4
try:worker(0,True)
except AssertionError:pass
else:raise AssertionError('odd packet-count reset fault was not detected')
try:pack_a(256)
except AssertionError:pass
else:raise AssertionError('wrong multi-ND source stride fault was not detected')
# Five is odd: global parity flips between N tiles and does not match local A colors.
assert any(((tile*5+j)%2)!=(j%2) for tile in range(2) for j in range(5))
parent_a_copies=0
for core in range(20):
    tasks=range(80*core//20,80*(core+1)//20)
    parent_a_copies+=len({task//5 for task in tasks})
print(json.dumps({'address_tags':BM*K,'A_bytes':327680,'B_slot_bytes':PACK_BYTES,'A_package_bases':[a_base(j) for j in range(5)],'B_slot_bases':B_BASE,'L1_end_bytes':END,'parent_L1_payload_bytes':END,'B_packets':sum(x[0] for x in counts),'tiles_per_worker':[x[1] for x in counts],'A_DMA_calls_parent':parent_a_copies,'A_DMA_calls_proposed':2*parent_a_copies,'A_ND_matrices_proposed':5*parent_a_copies,'A_GM_bytes_both':parent_a_copies*327680,'B_GM_bytes_both':192*128*1280*2,'fault_controls':'wrong color reset and multi-ND stride detected; global parity mismatch demonstrated','scope':'Independent addresses and packet-order arithmetic only; production code/native pipeline/speed remain PENDING'},indent=2))
