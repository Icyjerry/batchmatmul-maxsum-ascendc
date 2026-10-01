# Tiny raw-bit transpose before shared FP32 conversion

## Evidence and hypothesis

Parent `1734f16` / implementation `a770e64` officially passed15/15, task `6abeb39e694b590c3c22e5d7`, times(us): `[1.99,2.46,3.11,4.12,5.39,9.97,8.16,46.52,67.79,99.14,88.03,96.45,15.49,11.01,9.56]`. Its TT change only improved C8 by a modest single-run3.98% against three parent measurements; not a large breakthrough. Keep this result independently and avoid adjacent TT parameter submissions.

TinyCompute already uses the teammate's manual UB, compact metadata, shared casts and K32/40/48/56/64 specialization. For transposed input storage it still creates an index vector and performs one FP32 Gather for every M or N token. Simply swapping teammate whole source would not change that body.

This hypothesis changes the layout conversion: transpose original16-bit storage in UB before casting. The selected kernel contains no Gather or index construction. Arithmetic after layout conversion keeps exactly the passed FP32 Mul and K-tree sum, then validN Max and validM Sum. This is a structural pipeline candidate, not a nearby tile scan. Fewer API calls alone do not prove a latency improvement.

## CANN9 primary API evidence

[TansDataTo5HD official CANN900 reference](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0200.html), retrieved2026-10-02 with tavily-search. A2/A3 support uint16 operands,16x16 bit transpose, address arrays from GetPhyAddr, repeat strides in32-byte blocks. Direct BF16 operand type is not listed for A2/A3, so this code uses uint16 raw bits and later casts the actual input type. All list addresses are32-byte aligned. Kpad32/48/64 means2/3/4 repeats, avoiding the documented special repeatTimes1 addressing rule. Actual installed9.0 headers are not available locally; official compile remains a separate gate.

## Implementation scope

Only kernel.asc126 added lines in three regions: raw-bit helper/entry, exact UB-fit predicate, TinyK launch override. Removing them restores the complete passed parent1734f16 byte-for-byte, including FT, allCube routes, hostMakePlan/grid/groups/GM and final outputs. No main/CMake/run/golden/formal-test/dependency edits.

- New entry still gets16-byte TinyKernelShape and the originalgroup size; complete paired batches belong to their originalAIV, including final group and idle blocks. No newGM.
- Raw transpose buffers pad M/N to16channels and K to16. Only actual storage values are DMA-read; channel padding uses original DataCopyPad, missingK rows are initialized zero in disjoint UB tail positions before transpose.
- MTE2_V orders inputDMA before transposition. Address-array uint16 transpose uses repeated16x16 tiles with source repeat stride equal to channel pitch and destination stride1. Separate source/destination buffers avoid overlap.
- Reinterpreting half/BF16 as uint16 never performs input arithmetic. A single combined cast reads the canonicalA/B16-bit buffers to FP32, followed by the original multiply/reductions.
- np8 product/dot layout and mask rules are unchanged; zero padding never participates inN Max. RowMax sits at the firstlane of each32-byte row block, otherlanes are sum-zero identities.
- V_MTE3 protects outputDMA; terminalPIPE_ALL completes it. Uniqueexact float32[B] stores, immutable inputs.
- Host computes all eight32-byte-rounded regions using the actualgroupB, queries realUB and reserves1024bytes. Wrong dimensions/K, FT layout, oversizedgroups, explicitmeaningful tuningpins, or capacity failure fall back to the original kernel. Parent grouping and task/grid stay unchanged; no assumptions about fixed SoC/cores.

For B1/M8/N16/TT, layout conversion changes8Gather calls to1transpose plus removes index setup and the separate rawFP32 cast/gather pass. FF additionally changes16Gather calls to1transpose forB. Padded channel conversion processes more data and address setup consumes scalar work, so smallM/N or grouped batches may lose performance. The guard protects correctness/resources, not a proven speed crossover. No case shapes or route hits are inferred from bucket numbers.

## Verification

```sh
python3 tools/validate_tiny_bit_transpose.py
```

Production and TUNING each:

-1152 actual helper rectangles, all65536 raw16-bit patterns, Kpad32/48/64 and pitch16/32/64, typed address bounds/guards.
-27072 actual dynamic/constant entries,185808 active/23832 idle blocks, three asynchronous engine priorities; B tails, K8/N/M boundaries, all three layouts requiring transpose, all-negative and mixed values.
-The queued Cast checks every canonical input position against an independent expected arrangement, including everyK/channel padding zero. Independent full computation and unmodified TinyCompute same-order reference agree; inputs, allocatedUB guards, output bounds and unique writes are checked.
-10080 host one-byte capacity/shape/group/layout boundaries; production andTUNING, meaningfulpins fallback. Actual manual buffer allocation equals an independently summed budget.
-Seven negative controls rejected: missing inputready, outputready, terminalcompletion, groupoutputoffset, incorrecttranspose repeat stride, wrongNmask, missingKpadding.
-Scope inverse is entire parent byte equality, git diff --check, official template other7sources byte equality and dry-run onlykernel with sameSHA.

CPU integer arithmetic is not BF16/FP16 native encoding, hardware timing, or full SIMD scheduling. Physical bit relocation is covered exhaustively, but native casts/float rounding and compiler support are separate. Vector operations use one FIFO queue; PIPE_V ordering is represented by this queue, not everyhardware subpipeline. Local address-array loads/scalar timing are not simulated. No installed CANN9 compiler/NPU on thisMac.

Kernel361238bytes, SHA `844b80051c753717db4011a3586b4fed5dcb83d9937121c62b02dbc7ade4875f`. CPU log ignored at `artifacts/tiny-bit-transpose/cpu.log`; API search raw private `/private/tmp/bmmms-tiny-transpose-search.json` is not committed.

## Official request

Commit/push then submit one structural candidate, immediately saveID and query that sameID toterminal. CANN9 compile/NPU precision/latency PENDING. Require15/15; compare all15 against parent with attention to smallcases and retainedC7/C14/C15. Same-kernel parent repeats document substantial timing variation; no hiddenshape/plan/SoC/profile or controlled deviceA/B. Confirm unchanged source only if clearly large gain; no nearby parameter scan after small/no improvement. Report unfavorable buckets as well; no overallbest/actualscore claim. Main/tags unchanged, overallmajor optimization goal remains active.
