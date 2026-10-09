# C9 two-slot B FIFO across C tiles

## Candidate

Branch experiment/c9-b-package-stream, parent a2e6763; kernel371544B/SHA256 8ebc3eafd391c48c3f7242107c7fdd7ee2db2fea85ddfc454227340c68ed7724. 57added/4removed kernel lines. Default-false B_STREAM specialization, three-coordinate task/nt/k cursor, existing Case9CopyBPackage/TQue B1. Prime once, replenish after last package LoadData/FreeTensor across N tile and task/batch boundaries. No new allocation/GM/launch parameters; original geometry, A residency, K panels/FP32 MMAD, complete windows/ring/credits and partial layout stay unchanged. Exact C9 FP16/FT, dual20/BM=BN=BK128/no earlySum/queried capacities and actual cores/arena/no explicit tuning pins. Package K uses existing selection, not a parameter scan.

## Evidence and limits

`python3 tools/validate_c9_b_stream.py`:

- Whole inverse to a2e6763; protected seven files and complete AIV branch byte-identical. Default specialization still declares an unused cursor; no native instruction identity claim.
- Actual host production and TUNING: 2592 plans/6 exact hits each, one-byte UB threshold, memory/core/arena/layout/dimensions/pins fallback; original Plan unchanged.
- 68 actual new Cube configurations, same68 parent, and68 new eager-MTE2/deferred-MTE1-MMAD cases: paired batches, K/N/M tails, packages larger than K, multiple windows/shards/tasks, idle workers, completeK C element oracle, negative Max then Sum, input/y-ring guards and unchanged traffic/packet totals.
- Live L1 reads and L0 MMAD use generation checks; independent physical NZ/ZZ/ZN mappings. TQue Free/Alloc models implicit last-reader synchronization. Model counts next-tile/batch B issue before current Fixpipe: 916 new versus0 parent across the proxy suite, not a timing/hardware instruction claim.
- 1452 extracted unchanged AIV + actual FinalizeRows tests under delayed DMA/threaded final barriers; original horizontal calls remain768 on exact8/20/32-core C9 geometry. Producer and AIV models run separately, not a single combined hardware scheduler.
- Eight K/N/task/batch/end/B1-last-reader/L0-last-reader/fullK-before-Fix fault controls compiled and rejected. Initial model tracked both L0 slots as one epoch (false alarm), changed to per-offset versions. Initial all-negative input had constant K A and periodic B hiding batch mismatch; strengthened K and batch values. Initial tiny fault fixture PIPE_M barrier masked missing M_FIX; replaced with128x128 configuration. Kernel unchanged during these model corrections. Failed logs retained.

Fixpipe remains synchronous, implicit queue behavior modeled not validated against installed CANN9 implementation; integer/software float data/fake host tiler do not establish native FP16/BF16 accuracy, queue protocol or speed. Moving DMA earlier can delay next-task A refresh on MTE2. Same total bytes; no bandwidth reduction claim. Exact conditional20-core arithmetic audit: 960packets/31457280elements, startup384->40, 344 same copies moved earlier; details [audit](C9_B_PACKAGE_STREAM_AUDIT.md).

## Native gate

Dry isolated /private/tmp/bmmms-c9-b-package-stream/project from1734f16 protected seven files; onlykernel371544B/aboveSHA submitted. CANNcompile/15precision/native latency PENDING, no ID yet. ONE unique submission after commit/push; record immediately and query sameID to terminal. Confirmation only if all15Pass/C9<=57.375us; otherwise archive without unchanged repeats or nearby package/BN/Nsplit variants. No actual SoC/route/profile supplied. Overall goal incomplete, main/tags untouched.

Raw ignored artifacts/c9-b-package-stream/cpu.log plus initial compiler/whole-buffer-epoch/batch-fault/Fix-fault logs, directory700/file600.


Implementation **af7fd63** pushed; unique formal submission **6ac7e87d694b590c3c22f9f2** created once,371544B/SHA8ebc3eaf. NativePENDING; poll sameID to terminal, no duplicate submit.


## Formal terminal: Pass15, no C9 gain, archive

Unique **6ac7e87d694b590c3c22f9f2**, implementation **af7fd63**,371544B/SHA8ebc3eaf. Native compile/15precision passed/allprecision_ratio1. Timesus:

`[1.91,2.53,3.22,4.06,5.28,9.90,7.92,43.99,67.96,93.90,88.19,96.76,13.15,10.75,8.88]`

Total **458.40us**, latestuserTbest calculatedmean **52.03803336** (not live rank). C9 **67.96us** lies in retained recent67.50–69.04 range; no clear benefit, below neither old latency nor the57.375us confirmation threshold. Do not attribute unrelated C2/C8/C10/etc changes to this Cube edit. Native compile/accuracy does not disclose actual shape/route/SoC/profile and cannot establish why overlap failed to improve timing.

Archive implementation/model/result and restore whole **a2e6763**/368782B/SHA16b51684. No unchanged confirmation or neighboring package/Nsplit/BN scans. Model next-B-before-Fix916 versus0 did not establish hardware improvement. Rawignoredartifacts/c9-b-package-stream/official.json. No live task, main/tags unchanged, overall goal incomplete.
