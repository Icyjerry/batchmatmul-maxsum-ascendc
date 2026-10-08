# Exact C13 resident-B route: explicit physical frame

## Evidence and hypothesis

User exact-shape image supplies C13=(1,8192,64,128), without dtype/layout/SoC/formal metadata. Historical FP16/FF assumption plus actual host CPU-stub audit selects dual3/tree16/earlySum, not the dual14 tails targeted by the previous manual-frame trial. That old trial did not select this supplied shape. Prior full-K/B residence trials a6c5a29/7ffb3ff remain archived; this candidate retains the ALREADY-existing B L0 residence algorithm, does not reintroduce those changed Load3D/preload algorithms.

Passed parent1734f16/a5eef105/354602bytes, recent-five C13 14.94/15.11/15.13/16.74/15.99us, median15.13. User latest leader10.20us/Tbest7.31. No controlled interleaved A/B.

## Implementation

Branch experiment/c13-resident-frame. Kernel364169bytes, SHA256 0794a2bfc777ac48c373b3085cd96fd1224b0bf0a4f6a9351d290bb421dbad2d. Three additions178lines restore the entire parent on inverse removal. No main/CMake/run/golden/tests/dependencies/other algorithm edits; no newGM or allocation.

- Only exact B1/M8192/N64/K128/FP16/FF and original resident plan with matching dims, BM128/BN64/64Mtiles/oneNtile/oneNshard/oneKpartition/window1/earlySum/tree16. Query actual capacity/core counts, preserve plan/grid/cache/original GM. ExplicitTUNINGpins fallback. Original residency requires64Mtiles>=2workers, so guardworkers<=32; does not assume physical20cores. A64core original nonresident plan remains untouched.
- One B ND2NZ copy and eight Load2D operations per ACTIVE worker, keep B2 unchanged until final MMAD completes. No repeated B preparation per M task. Original fullK128 FP32 MMAD and Load2D FF layout retained. No crossM complete-A prefetch or rectangularLoad3D.
- Double128x128A1/A2, double128x64 FP32C; explicit ready and last-reader events replace TPipe/TQue. Original strided task=worker, task+=workers and twoGM Cslots/credits0-1,4-5. Cube waits actual final MTE1/MMAD/Fixpipe reads before buffer reuse, drains events and credits on exit.
- Each AIV receives64x64 completeC rows. WholeReduceMax64 directly to row, Add to64worker accumulation lanes; same perlane accumulation order as original RESIDENT_B branch. Removes redundant -Inf/per-task maxima buffers and Max with the one completeN result. Zero initializes only SUM accumulators, never Max inputs.
- One WholeReduceSum64 after worker tasks, write exactly one original8float partial slot atworker*16+sub*8; extra7floats zero. Explicit V_MTE3 and MTE3_V plus originalallAIVSyncAll, then onlyAIV0 reuses deadUB to compress/read the same2workers partials and write one4B y. No perM partials, atomic sum or newGM path.
- L1 explicit81920B+4096reserve, L0A65536/L0B16384/L0C65536, UB33568+4096; postbarrier frame<=2368B forhostworkers<=32. Original partial prefix32768B and perworker65536B ring required, fits the existing allocation. No global workspace/metadata protocol change, 8byte M/workers argument.

## Local evidence

`python3 tools/validate_c13_resident_frame.py` exit0 at currentSHA:

- 96Cube configurations, execute everyworker actualextracted entry: M128/256/640/8192, workers1/3/8/20/32/64, mixed/allnegative, eager/deferredFixpipe. PhysicalNZ/ZZ/ZN, delayedliveMTE2/MTE1/MMAD/Fixpipe, independent everyvalidC vscompleteK dot, exactlyoneBcopy/eightBloads peractiveworker, inputunchanged/GMguards/eventbalance passed. Idleworkers never readB.
- Seven Cube negative controls rejected: A1lastreader/Binputready/Ainputready/A2lastreader/ClastFixpipereader/Mmad-Fixpipe completion/incompleteK.
- 102threaded AIV configurations at threeFIFO priorities, completeM/N negative/mixedoracle, doubleC reuse/destructiveGM release, accumulationgenerations, once-only originalpartialslots (includingidle workers), allAIVbarrier and uniqueexact4By/guards. Cube/companion credits are synthetic, not a complete hardware co-simulation.
- Seven Vector controls rejected: Clastreader/Cready/sumVready/allAIVbarrier/finalDMAready/terminalcompletion/earlyGMcredit. Removing MTE3_V alone is NOT detected because modeledSyncAll drains engines; retained the device wait, did not claim this control passes or independently proves nativeSyncAll behavior.
- production/TUNING each5120actualhostplans overhistoricalN/K range andcores1/8/20/32/64, four exactshape selections; actualplanunchanged, exactcapacity/oneBlower/workspace/core boundaries, layout/dtype/dimension/plan/pin and64core nonresident fallback passed. Not a nativeCANN tiler.
- Whole-parent scope and gitdiffcheck passed. Independenttemplate /private/tmp/bmmms-c13-resident-official/project protected7 files byte-equal1734f16; CLI dry-run uploads onlykernel/364169bytes/SHA. RawCPU log ignoredartifacts/c13-resident-frame/cpu.log.

Models use integer values, not encodedFP16 precision/latency. All API calls reused from passed source; changed event/layout combination still needs native gate. Native CANN9/FP16 formal precision/performance PENDING.

## Formal next action

Commit/push then submit ONCE; saveID immediately and query sameID to realterminal. Retain all15results and score withSCORE_REFERENCE_1008. Only clearlylarge benefit warrants one identicalconfirmation. Otherwise archive without nearbyframe/package/tile scans, restorepassedparent. ActualSoC/shape/plan/profile unavailable; do not infer devicecounter or route trace from CPU/source alone. Overallcompetition goal incomplete.

Implementation7492776 pushed; unique formal task **6ac73bd0694b590c3ca19b3d** created. Query sameID to realterminal, no resubmission; nativegatePENDING.

## First formal terminal: Pass, substantial C13 observation

Task6ac73bd0694b590c3ca19b3d /implementation7492776/SHA0794a2bf: Pass15/15, allprecision_ratio1. Timesus:

[2.02, 2.48, 3.08, 4.16, 5.37, 9.78, 8.25, 46.5, 68.11, 100.24, 88.9, 96.47, 12.62, 11.14, 9.51]

Total468.63us; latestTbest calculatedmean50.75856. C13=12.62 vsrecentfiveparent14.94-16.74/median15.13:16.59percent belowmedian,15.53percent belowfastestparent. Largerthan recentparent spread/median11.90percent, warrantsONE unchangedconfirmation. Noactualshape/plan/SoC/profile or interleavedA/B; cannotclaim stablecausalpercentage/devicecounter/route trace. C10=100.24 andC14=11.14 unfavorable observations retained; unmodifiedroutes notattributed. RawJSON ignoredartifacts/c13-resident-frame/official-one.json. Firsttask terminal, noactivejob beforeconfirmation.

One unchangedconfirmation task **6ac73c8b694b590c3ca2153b** created after kernel/template equality check. SameSHA0794a2bf. Save/querythisID toterminal; no further repeats requested.
