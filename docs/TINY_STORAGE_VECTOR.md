# Tiny document storage-native broadcast and K reduction

## Evidence and hypothesis

Passed parent `1734f16` / implementation `a770e64`, kernel SHA `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`, official task `6abeb39e694b590c3c22e5d7` passed 15/15. Small cases C1–C6 were `[1.99,2.46,3.11,4.12,5.39,9.97]` us. Parent TT repeat records demonstrate timing variation; no hidden shape/layout/plan/profile is available.

The intermediate raw-bit input-transpose branch `experiment/tiny-bit-transpose` / `26beaac` is archived: task `6abebe23694b590c3c265928` passed 15/15 but C2 increased to4.12us versus2.46us. Its larger padded casts and scalar address arrays are possible explanations, not measured bottlenecks. This experiment starts from the passed parent1734f16, without that transpose implementation.

Hypothesis: for document storage `[K,N]`, keep that arrangement and broadcast query K values into N lanes, avoiding document Gather and index construction. Multiply all K rows in one repeat-based Vector call, reduce completeK with an FP32 binary tree, then validN Max and original validM Sum. This changes the local algorithm, not tile tuning. It may reduce Gather cost; padded multiplication and a different reduction tree may still make it slower. Only formal timing can decide.

## Scope and implementation

Branch `experiment/tiny-storage-vector`, kernel359398bytes, SHA `19cd486e6a0ffcd4caaa4a644e64853ae994a7c0065deb577ba32184b271f794`.

Only kernel.asc algorithm changes: 92 added lines in three regions (device entry, host resource guard, LaunchTinyK override). Removing these regions restores the entire parent byte for byte. MakePlan, core/grid selection, batch grouping, workspace and all other kernels remain parent. Official template other seven source files are byte-equal parent; dry-run sends only this kernel with the same SHA. No main/CMake/run/golden/formal-test/dependency changes, no new GM path or metadata.

- Applies to FF/TF storage (`transposeX2=false`) and K32/64. The tree halves are complete at these K values; K40/48/56, FT/TT and guard failures use the passed implementation. Does not infer hidden cases from bucket numbers.
- Preserves paired batches and original grouped blocks, including final batch and idle blocks. Physical offsets follow storage lengths.
- N pitch is ceil16N. Original document rows are DMA copied with zero padding; A remains physical storage order. A and B share one FP32 cast. Only transposed-query storage requires a query Gather.
- Brcb forms K blocks of eight identical FP32 query values. Mul uses zero query block stride within each N repeat, advances the query block by one per K repeat, and reads/writes contiguous N lanes. Product scratch is reused for each M row, not replicated across M or batches.
- FP32 K tree finishes before validN WholeReduceMax. PaddedN never participates in Max, including all-negative rows. The existing row-slot representation and validM WholeReduceSum are preserved. Writes exactly B float32 values.
- Eight 32-byte-aligned UB regions, independently budgeted by actual UB capacity with1024byte reserve. Explicit MTE2_V, V_MTE3 and terminal PIPE_ALL; PIPE_V between all dependent Vector operations. No fixed SoC/core count.

## CANN9 primary API evidence

Retrieved full900 static official text, not older version search snippets:

- [Brcb](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0089.html): float is supported for A2/A3; eight source values per repeat each fill a32byte block; aligned non-overlapping source/destination, params `{1,8}`.
- [BinaryRepeatParams](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0013.html) and [vector stride guide](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/programug/Ascendcopdevg/atlas_ascendc_10_0022.html): block/repeat address-stride definitions. The zero query block stride follows these address semantics; installed headers/native behavior remain a separate verification gate.
- [PipeBarrier](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0271.html): same-pipeline dependent operations need ordering; explicit PIPE_V included here. Compiler automatic synchronization does not substitute for CPU model coverage of hardware subpipelines.

Private raw research JSONs in `/private/tmp/bmmms-tiny-storage-vector-*.json`, not committed. This Mac has no installed CANN9 headers/compiler or NPU.

## CPU and static evidence

Reproduce: `python3 tools/validate_tiny_storage_vector.py`. Production and BMMMS_TUNING each:

- 10080 host shape/layout/group/exact-byte-capacity controls; one byte below required capacity rejected, meaningful explicit tuning pins fall back.
- 8352 actual dynamic/constant entries,54432 active /7488 idle blocks, three queued DMA/Vector/output priorities. Independent integer full-K oracle and unmodified parent TinyCompute agree. Canonical cast-source arrangement checks every N padding element; paired batches, all-negative maxima, unique y writers, immutable inputs and UB/y guards checked.
- 864 actual entries on encoded FP16/BF16 values, FF/TF, full/tailN, M1/5/8, K32/64, negative/mixed values and three engine orders. FP64 golden rounded toFP32; max absolute error9.53674e-7 and max nonzero relative error2.93038e-6. Comparison used mixed CPU tolerance `1e-4+1e-4*abs(golden)`, not a replacement for formal precision rules. The new K addition order differs from parent.
- Seven negative controls rejected: missing inputready/outputready/terminalcompletion, wrong batch output offset, incomplete K tree, missing validN mask, wrong broadcast block stride.
- Scope inverse entire-parent equality, `git diff --check`, isolated template and CLI dry-run verified.

CPU model uses one Vector FIFO, not hardware SIMD subpipelines or real instructions. Quantized values are decoded in software; no native cast/rounding/performance claim. Grouped quantized runs use group1; other groups have integer coverage. It is not full exhaustive floating precision coverage. CPU log Git-ignored `artifacts/tiny-storage-vector/cpu.log` (directory700/file600).

## Formal request and next action

CANN9 compile / native precision / NPU latency PENDING. Commit/push this structural candidate, submit once, save ID immediately, query only that ID to terminal. Require15/15, retain all fifteen times and compare against passed parent and observed variation, particularly C2/C3 and existing C7/C14/C15 gains. No actual SoC/shapes/plans/profile means no route-hit or overall-score claim. Only clearly large benefit justifies unchanged confirmation; small/no benefit is archived without nearby parameter scans.

Main and historical tags unchanged. Overall substantial competition improvement remains incomplete.

Official task **`6abec499694b590c3c288b4a`** created, implementation `155fbd9` pushed. Kernel/template SHA19cd486e unchanged. Query this ID to terminal; never resubmit on observation timeout. CANN9/nativeprecision/timing PENDING.
