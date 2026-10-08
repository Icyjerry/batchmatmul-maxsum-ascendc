# C11 exact TT frame experiment · 2026-10-08

## Evidence and hypothesis

The user's image supplies C11 `(B,M,N,K)=(1,1536,2048,2048)`; dtype/layout are absent. Historical FP16/TT remains an assumption. Its baseline 783.84us is neither Tbest nor our implementation timing. Retained C13 source7492776/SHA0794a2bf is the parent, with recent formal C11=88.90/88.78us. No real SoC, route trace or profiling is available.

Under the actual MakePlan CPU tiler stub, cores8/20/32/64 select dual2/BM128/BN256/Nsplit8/window1/Kchunk2048; existing general TT frame excludes that plan. Hypothesis: routing this exact point through the existing full-A TT frame amortizes its A1 input across adjacent N tiles and removes library bookkeeping. BM64/BN256/BK64/packageK256 fits explicit frames. Halving M tile size may increase B traffic; native timing decides. This does not repeat the failed swapped-operands, paired-N, worker-Max or native-NZ experiments.

## Implementation scope

Only34 added kernel lines: MakeC11TTFrame and a Launch override. Whole inverse restores the entire retained C13 source7492776. Existing TT device function, all other device functions, MakePlan, cache, ABI and allocator byte-identical. No new API or GM pathway. Original full-K FP32 MMAD then MaxN then SumM remains.

Require exact shape/FP16/TT, matching schedule dimensions and original dual2/BM128/BN256/12Mtiles/8Ntiles/8Nsplit/Ksplit1/Kchunk2048/window1/no earlySum/tree, matching actual grid and sufficient AIC/AIV. All explicit TUNING pins fallback. One/four-core original plans fallback. No fixed physical core assumption. Lower memory capacity also falls back; package size is not scanned.

The new192 M-major tasks use24 Mtiles x8 Ntiles on original workers. Full A1=262144B and two B1=262144B, exactly512KiB L1; explicit device entry allocates no TPipe metadata. Double L0A16384/L0B65536/L0C131072B. AIV C/row65792B plus4096 guard. Final merge49152B plus grouped sums/output fits that UB requirement. Check actual capacity inclusive, one byte short falls back.

Original and new N-shard/m partial prefix both12288floats=49152B. New rings131072B/worker are within old262144B/worker allocation; no allocator or metadata changes. Shorter ring stride is local to the new entry, with no old consumer launched. All original input/output bounds retained.

## Verification

Candidate365998bytes/SHA4ce9ab293b8a24b80a3741f8195ccee217856a5b9c0d330404fa7013f5c7300d.

`python3 tools/validate_c11_exact_frame.py`: production and TUNING each2592 actual-host plans/four exact hits; plan immutability, equal partial prefix, smaller ring, dimension/layout/type/plan/core/grid/workspace/capacity and one-byte boundaries, explicit-pin fallback. Six actual physical TT Cube configuration groups: complete K2048/BN256/BK64/PK256/N8 stream on reduced-M proxy, mixed/all-negative, eager/deferred Fixpipe, delayed live operands, M-boundary A reuse, idle workers and physical NZ/ZZ/ZN, input/GM/event guards. Six Cube negative controls rejected. Sixty threaded actual AIV groups: full supplied M1536/N2048 and tail proxy, cores1/8/20/32/64, three engine priorities, both signs, destructive ring credit, immutable unique N partials, barrier and exact4B y; seven Vector negative controls rejected.

CPU integers and synthetic cross-core companions, not native FP16 encoding, real tiling, timing or complete hardware co-simulation. Cube tests reduce M to control cost; full host/consumer dimensions are exercised. Native CANN compilation,15-case FP16/BF16 precision and timing PENDING. The existing TT entry's prior BF16 Pass does not establish this new FP16 route's result.

Protected seven template files byte-identical to1734f16; separate official template `/private/tmp/bmmms-c11-exact-frame-official/project`. CPU log ignored `artifacts/c11-exact-tt-frame/cpu.log`. Submit one unique gate after dry-run; record ID before polling same ID to terminal. Only a clear substantial observation warrants one unchanged confirmation. Preserve all15 timings/adverse points and C13 gain; no failed nearby variant scans.

Implementation9160eb2 pushed. Unique formal task **6ac73fd0694b590c3ca4be61** created after matching dry-run. Query this ID to terminal; native gate PENDING, do not submit again on observation timeout.

## Formal terminal: Pass, no clear C11 improvement; archive

Task6ac73fd0694b590c3ca4be61 / implementation9160eb2 / SHA4ce9ab29: terminal Pass15/15, precision_ratio all1. Native compile and those precision samples passed; real SoC/shape/layout/route/profiling still unavailable. Full timings us:

|Case|Time us|
|---|---:|
|C1|1.90|
|C2|2.56|
|C3|3.19|
|C4|4.01|
|C5|5.29|
|C6|9.56|
|C7|7.95|
|C8|46.18|
|C9|67.15|
|C10|97.08|
|C11|87.16|
|C12|96.47|
|C13|12.85|
|C14|10.59|
|C15|9.02|

Total460.96us, calculated mean52.148476871 with user1008 Tbest. This is not a reported live leaderboard position. C11=87.16 below the two C13-parent samples88.90/88.78, but within broader same-C11-source historical range86.97–88.91 (BEST_IDENTICAL_REPEATS_1002/1003); no substantial or stable benefit. Do not repeat or scan nearby BM/BN/package values. Other unchanged points and adverse C2/C3/C12 observations retained, not attributed to the C11 route. C13=12.85 remains consistent with retained12.62/13.19 but is not another C13 A/B test.

Archive this branch with implementation/models/results; restore entire retained7492776 kernel/SHA0794a2bf for future independent experiments. No active task, no confirmation. Raw JSON ignored artifacts/c11-exact-tt-frame/official.json. Next assessment should use the exact C8 K1032/N1031/M1025 tails and selected C6 BM32/BN80/KP192 entry; previously failed TT pairedN/swapped/NZ and tiny packed structures remain rejected.
