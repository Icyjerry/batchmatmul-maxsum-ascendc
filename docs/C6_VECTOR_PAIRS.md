# C6 direct Vector pairs · 2026-10-08

## Evidence and single structural hypothesis

User supplied C6 B13/M23/N73/K192 but omitted dtype/layout. Historical BF16/FT remains an assumption. Actual MakePlan CPU stub selects original dual19/BM32/BN80/direct batch, not the fullyconstantBN96 branch. Recent retained source C6=9.78/9.75us, broader same-path observations include9.46–9.85; newest user's leader=6.60us. No real plan trace/SoC/profile or controlled A/B.

Replace this exact point's Cube→GM C→AIV pipeline with two AIVs per batch. Each caches the whole document embedding and half the query rows, computes two query rows' products per UB frame, completes192K in FP32, masks Max to73N and sums12/11 query rows. Store one scalar per half in the existing partial prefix; one all-AIV barrier, batch's first AIV combines two scalars and writes exactly one4B y. This removes Cube packing, MMAD, Fixpipe, C-ring traffic and Cube/Vector credits from that point, but increases Vector arithmetic and duplicates B across two AIVs. Native timing decides; no predicted speedup.

## Source and resource scope

Branch experiment/c6-vector-pairs, parent retained7492776/C13 source0794a2bf. Candidate369131bytes/SHAa9aff3a8a4f9b0f81dd519d299e7fe213952b2016f79faca82b441c62397789a.90kernel added lines in three additions; whole inverse restores7492776. Old device entries/MakePlan/allocator/cache/ABI/C13 gain unchanged. No extra GM allocation/path. The existing partial prefix has2048B;26 scalar stores of32B use832B, rings remain unused and intact.

Exact B13/M23/N73/K192/BF16/FT and actual matching schedule dimensions, dual19/BM32BN80/oneMtile/Ntile/Nsplit/Ksplit/window, originalworkers/grid==B13. Query actual AIV>=26 and UB>=194336B (190240explicit+4096reserve); originalworkspace must fit the existing2048B prefix. All explicit TUNING pins fallback, as do other shapes/layouts/types/resources/plans. No fixed physical AIC/core count assumption, new route requires the original validated batch-complete plan.

UB float elements: products30720, cached B14016, cached A2304, three dot chunks480, row16, scalar8, merge16 =47560/190240bytes. Input raw BF16 aliases only product bytes0–32640 until both casts retire. A/B FP32 caches and dot/row/output frames are disjoint. Initialize only seven unused product rows per query once; each192K dot sums three64-value chunks before N Max. Odd11-row half ignores stale second product row in its final pair. Invalid N does not participate in Max; all-negative output remains negative. No input mutation, no cross-batch pairing.

Reduction constraints checked against official CANN9 [WholeReduceMax](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0079.html) and [WholeReduceSum](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0081.html): float mask64, repeat160 below255; source32B and row-pair destination8B aligned. Installed CANN9 headers/native compiler remain the authority. Calls reuse APIs already present in the parent; no GPU paper's timing is transferred to Ascend.

## Verification and native gate

`python3 tools/validate_c6_vector_pairs.py` exit0: production/TUNING each3888actualhost plans/three exact selections across1/8/12/20/32/64cores, all dtype/layouts and neighboring dimensions; no plan/allocation mutation, UB/AIV/workspace one-unit boundaries and pin/dimension/grid fallback.72actual-entry threaded byte-UB groups: B1/3/13/20, three FIFO priorities, three input seeds, mixed/all-negative, full192K and73N,12/11rows, unique partial and y stores, input/GM guards. Six negative controls reject missing input readiness/store readiness/barrier/terminal/fullK/Nmask.

CPU inputs are integers, not encoded BF16; FIFO Vector model cannot expose internal instruction pipeline hazards (all device barriers retained). Barrier drains engines in the model; not a complete native SyncAll proof or timing model. Native BF16 precision15cases and latency PENDING. Protected seven template files byte-identical to1734f16; CLI dry-run only kernel matches SHA. Separate template `/private/tmp/bmmms-c6-vector-pairs-official/project`, raw log ignoredartifacts/c6-vector-pairs/cpu.log.

Commit/push candidate, submit one unique gate, save ID immediately and poll same ID to real terminal. Preserve all15 times, C13/C7/C14 gains and adverse points. Only a clearly substantial C6 observation warrants one unchanged confirmation. Failure/no clear gain: archive and restore parent; no neighboring row-pair/chunk/padding scans.

Implementationf4907c3 pushed; unique official task **6ac744ee694b590c3ca8ea6c** created after matching dry-run. Native gate PENDING; query this ID only to real terminal, no duplicate submission on observation timeout.

## Terminal: 15 Pass, clear C6 regression; archive

Task6ac744ee694b590c3ca8ea6c/implementationf4907c3/SHAa9aff3a8: Pass15/allprecision_ratio1. Full times us:

`[1.88,2.49,3.25,3.97,5.36,24.24,8.11,46.32,68.17,98.59,88.49,97.11,13.15,10.89,9.35]`

Total481.37us; mean49.474027063 with user1008 Tbest. C6=24.24 vs retained9.78/9.75 and broader9.46–9.85: clear regression. Pure Vector's extra arithmetic/reductions outweighed the hoped-for communication saving in this observation; no real profiling or route/SoC trace, so do not assert hardware counters or stable causal percentages. C3/C5/C12 adverse observations preserved. C13=13.15 is consistent with retained12.62/13.19, not a new A/B.

Archive the implementation/models/terminal result; no confirmation or adjacent pair/chunk/padding scan. Restore entire retained7492776 source/SHA0794a2bf. RawJSON ignoredartifacts/c6-vector-pairs/official.json. No active C6 task. User requested pause after this terminal and prohibited further Web browsing; subsequent resume requests one unchanged best submission then continued local/source/teammate analysis.
