# C5: full-batch FP16 Vector computation, no similarity GM handoff

## Scope and evidence

Retained formal820092/source2073 Pass15/398.92us. Local C5 explicit B8/M16/N32/K128/FP16, formal dtype/layout unknown. Target CANN9/dav2201, actual9382/24AIC48AIV/dev0physical14/caller20. Original FF normalPlan dual19, BM16BN32K128/8workers/MIX11; other three layouts only differ in dual3, all remaining complete plan fields equal. This was read from actual MakePlan; not forced.

Original FF complete five/default8 CSV reports: `[4.840194,4.460178,4.880195,4.580183,4.580183]`us, median4.580183. PMU role mean medians: Cube MAC .032778us/MTE1 .076805625/MTE2 .365486/Fix .149097125/scalar1.326875, AIV Vector .112778/flag0wait .912916625. Counters overlap and cannot be summed; very small Cube compute motivates testing removal of the Cube/Vector handoff. It does not prove the new Vector computation faster.

## Candidate

Source eb1ac4bdb07984f470216f293464f76fff0bb349c26525ace570eef869408fab/356572B,50 added kernel lines over2073. New `bmmms_c5_half_vector<TX1,TX2>` uses one AIV per batch and directly writes one4B y; no Cube, CrossCore/SyncAll, partial write or similarity GM read/write. Existing cached GM arena/allocation/MakePlan remain unchanged; no new GM routes.

Load the complete actual A2048half/B4096half. Half Gather normalizes only the storage that requires it (K128 offsets32*k for query-transposed /64*k for document-nontransposed). No input FP32 Cast. Zero32768 FP32 product lanes; for each M16 query, two mixed `MulAddDst<float,half>` calls generate lowK64/highK64 contributions to a64-lane state for all N32 docs. Each dot is the full K128 before MaxN32 and SumM16. FP32 accumulation and barriers maintained. All-negative N values never encounter a zero identity in Max.

UB offsets: rawA0/rawB4096/canonicalA12288/B16384/indices24576/products26112/dots157184/rows159232/sum159296; end159328B plus1024 guard. Original UseSmallC5Direct plan/resource/pin checks reused, then FP16/alignment32B/AIV8/UB160352 guard. BF16 unchanged. Both dtype and layout performance are explicit coverage concerns; formal C5 type/layout are not guessed.

This is switching the complete C5 compute unit and elimination of GM handoff, not a nearby C4 floatfloat compact-product scan, old C6 Vector-pairs, or repeating the failed C2 pipeline on the same point.

## CPU and native correctness

`python3 tools/validate_c5_half_vector.py`: actual extracted kernel,320 full B entries (40x8, all4 layouts), encoded FP16 and full actual-storage FP64 K128/N32/M16 oracle, random/whole-negative/unique-last-N/low-only/high-only/distinct-batch/large products/subnormal inputs. Defined UB, deferred DMA/one Vector FIFO/output, input immutability/each y word exactly once/guards. Nine semantic faults rejected. Whole-source inverse restores2073; protected7 byte-equal1734f16. One FIFO/software FMA is not hardware scheduling proof.

`python3 tools/validate_c5_half_vector_guard.py`: actual production4 accepts/41 rejects, tuning4/52, including resource/plan/shape/type/alignment/pins/boundaries. Artificial host stubs are not SDK tiler evidence.

Actual CANN9 compile PASS. SSH89986 transport exited255 after connection loss, but fresh authorized connection inspected original build terminal `Built target native_bmmms` and existing DSO: no restart. DSO9f3400624da2d6022d159a33ffca0af40ff18763f4b64ac48351367948da5647, wrapper994e29f/sourceeb1ac4bd bound in identity. Frozen imports/c5-half-vector/kernel.asc, build-c5-half-vector.

All four actual layout plans read and reviewed. All four same-context/stream/addresses mixed-negative-mixed native full-FP64/input/yguard PASS. FF maxabs2.3841858e-7 mixed,9.5367432e-7 negative; neither tolerance nor golden changed. One validation-driver assumption incorrectly required all4 plans identical; d.dual differs19 vs3. Original 01 driver stopped before launch because frame file not created; preserved failed folder. Correct00 succeeded once; reviewed actual01/10/11 frames and used new explicit result dirs for those first actual launches. Not a kernel precision failure or resampling.

## Performance gate before any candidate collection

Evaluate four explicit layouts separately because Gather cost differs. Freeze once: each retained layout requires candidate median<=.8*its parent's median AND every one of5 candidate samples<its parent's fastest. All5 default8-table complete reports/output/guards retained; same encoded logical inputs and full golden. No tile/UB/stride/K/flag scan or repeated unchanged sampling. Branches that do not pass fall back to original; none pass -> restore2073. This rule is recorded before candidate collection, not lowered after results. Candidate performance/otherSoC/formal15 currently PENDING.

Original FF parent baseline already above; other three parent full profiles are running once. Independent fixture tools prepare_c5_half_checks.py/prepare_c5_parent_layouts.py preserve original parent bytes/golden and only use explicit capture metadata appropriate to each implementation. They do not modify formal golden/test files. Parent raw downloadedartifacts/c5-vector-audit/c5-vector-parent-evidence.tgz; candidate raw/artifacts remain private700/600.
