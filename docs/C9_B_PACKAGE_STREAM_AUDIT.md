# C9 cross-tile B package stream audit

## Evidence and hypothesis

Passed kernel restored byte-for-byte from a2e6763 (368782B, SHA256 16b51684cc8628121d7e359c89561c248d04b449b6ecb449f0b4f2da2ffa3a94). C9 persistent lane Max archived a07150f: unique 6ac7e2f8694b590c3c2010c5 Pass15/C9=67.62us, no clear gain; no repeat.

Current Cube primes two B packages for each C tile, and replenishes only within that tile. Hypothesis: maintain the existing two-slot B1 FIFO across N tiles and worker task/batch boundaries, moving next tile startup DMA ahead of the current tile final MMAD/Fixpipe. Geometry, K accumulation, A residency, GM ring, AIV, finalizer and total data volume remain the same. This differs from historical 8a69048 Vector C-consumer prefetch and the rejected persistent lane Max; retained TT B-stream code supplies a local example, not C9 timing evidence.

## Executed arithmetic audit

`python3 tools/audit_c9_b_stream.py`: 15120 worker sequences/83328 packets match independent nested-loop ordering exactly, including K/N tails, batch/task strides and idle workers. Conditional 20-core C9 BM/BN/BK=128, PK=256, Nsplit=3: 192 C tiles, 960 B packets, 31457280 source elements. Per-tile priming 384 calls becomes one-time 40; 344 copies move earlier, none are removed. Pure cursor/FIFO arithmetic, not changed Ascend execution or CANN proof.

## Risks and next action

Implement a default-false exact C9 specialization with task/nt/k cursor and the existing Case9CopyBPackage/TQue. Execute actual producer with deferred MTE2/MTE1/MMAD and protected last readers, independent physical NZ/ZZ/ZN mapping, tails, task/batch transitions and fault controls. Keep old paths byte-identical. Guard actual resources/cores and tuning overrides. Native compile/precision/latency PENDING, no job exists. Next task A refresh can wait behind queued B on MTE2; cross-tile scheduling can regress despite identical traffic. One formal gate only after model verification; confirmation requires Pass15 and C9 <=57.375us, otherwise archive without nearby scans.

Raw arithmetic output: ignored artifacts/c9-b-package-stream-audit/packets.log (directory700/file600). No active native tasks. Main/tags untouched.
