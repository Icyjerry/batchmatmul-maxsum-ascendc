#!/usr/bin/env python3
"""Offline address audit of a proposal, not an implemented or native-tested kernel."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
assert hashlib.sha256((root / 'kernel.asc').read_bytes()).hexdigest() == '0786352034e77506894d4094083960f4f6af82782bf7cee6a0386148437ca436'


def nz(n, d, stride, start):
    """Model existing aligned ND2NZ layout as source element addresses."""
    out = [None] * (n * d)
    for row in range(n):
        for col in range(d):
            out[(col // 16 * n + row) * 16 + col % 16] = start + row * stride + col
    assert all(x is not None for x in out)
    return out


def check(m, n, k):
    chunk, bk = k // 8, 128
    # Each split retains all eight/four A matrices in precisely the old panel order.
    for split in range(8):
        begin = split * chunk
        a_batch = []
        for rel in range(0, chunk, bk):
            a_batch.extend(nz(bk, m, m, (begin + rel) * m))
        b_full = nz(n, chunk, k, begin)
        for rel in range(0, chunk, bk):
            old_a = nz(bk, m, m, (begin + rel) * m)
            old_b = nz(n, bk, k, begin + rel)
            assert a_batch[rel * m:(rel + bk) * m] == old_a
            assert b_full[rel * n:(rel + bk) * n] == old_b
            assert all(0 <= x < m * k for x in old_a)
            assert all(0 <= x < n * k for x in old_b)
    # A single large NZ matrix has a different outer block order than panel-packed A.
    if m > 16:
        assert nz(chunk, m, m, 0) != sum((nz(bk, m, m, rel * m) for rel in range(0, chunk, bk)), [])
    old_dma, new_dma = 2 * chunk // bk, 2
    old_l1, new_l1 = 4 * (m + n) * bk, 2 * (m + n) * chunk
    print(f'M{m} N{n} K{k}: modeled panel addresses identical; ND2NZ calls/split {old_dma}->{new_dma}; L1 bytes {old_l1}->{new_l1}; GM bytes unchanged')


if __name__ == '__main__':
    for m, n, k in [(16, 16, 4096), (64, 64, 4096), (64, 64, 8192), (128, 128, 8192)]:
        check(m, n, k)
    print('Proposal only: no new ASC code. Batched DMA hardware semantics, actual normalPlan, correctness, overlap and performance PENDING.')
