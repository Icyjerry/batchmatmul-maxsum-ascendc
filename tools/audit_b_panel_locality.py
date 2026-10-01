#!/usr/bin/env python3
"""Address geometry of original/direct vs existing packed-B views.

This is an independent integer-address model, not execution of Ascend APIs,
NPU cache/TLB simulation, profiling, or a bandwidth prediction.
"""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
source=subprocess.check_output(['git','show','acc84d7:kernel.asc'],cwd=root,text=True)
# Bind the modeled formulas to the archived implementation, fail if it changes.
direct=source[source.index('__aicore__ inline void ManualFullMReadB('):source.index('__aicore__ inline void RunManualFullMCube(')]
packed=source[source.index('__aicore__ inline void ManualCopyKCase12Packed('):source.index('// Isolated case12 packed-B kernel')]
assert 'cp.srcDValue=TX2?s.k:s.n' in direct
assert 'int64_t(k0)*s.n+n0' in direct
assert 'bp.srcDValue=packedB?s.baseN:' in packed
assert '(batch*s.nTiles+n0/s.baseN)*s.k*s.baseN+int64_t(k0)*s.baseN' in packed

def geometry(start,rows,cols,stride):
    intervals=[(2*(start+r*stride),2*(start+r*stride+cols)) for r in range(rows)]
    runs=0;end=None;buckets=set()
    for lo,hi in intervals:
        if lo!=end:runs+=1
        end=hi
        buckets.update(range(lo//4096,(hi-1)//4096+1))
    return rows*cols*2,runs,intervals[-1][1]-intervals[0][0],len(buckets)

panels=0
for n in (257,1025,6144):
    for k in (136,1536):
        for bn in (128,256):
            tiles=(n+bn-1)//bn;bk=64 if bn==256 else 128
            for batch in range(2):
                for nt in range(tiles):
                    n0=nt*bn;cols=min(bn,n-n0)
                    for k0 in range(0,k,bk):
                        rows=min(bk,k-k0)
                        d0=batch*n*k+k0*n+n0
                        p0=(batch*tiles+nt)*k*bn+k0*bn
                        d=geometry(d0,rows,cols,n)
                        p=geometry(p0,rows,cols,bn)
                        assert d[0]==p[0] # equal valid bytes, different address geometry
                        if cols==bn:assert p[1]==1
                        assert d[1]==rows
                        # Independently decode the packed coordinate back to original.
                        for r in range(rows):
                            for c in (0,cols-1):
                                index=p0+r*bn+c;q,nc=divmod(index,bn)
                                z,q=divmod(q,tiles*k);tile,kc=divmod(q,k)
                                assert z*n*k+kc*n+tile*bn+nc==d0+r*n+c
                        panels+=1
n,k,bn,bk=6144,1536,256,64
print('Independent packed-to-original coordinate checks:',panels,'panels PASS')
print('Illustrative K64/N256 panel from N6144, aligned byte-zero model:')
print('  view,valid_bytes,contiguous_runs,address_span_bytes,4KiB_address_buckets')
print('  direct,',geometry(0,bk,bn,n),sep='')
print('  packed,',geometry(0,bk,bn,bn),sep='')
print('Address span/buckets are NOT bytes transferred or measured NPU cache/TLB cost.')
print('Packing adds startup reads/writes but preserves contiguous Cube input panels;')
print('formal regression is evidence to retain this tradeoff, not proof of its cause.')
