# Complete tiny K8 coverage with an excess-to32 fold

## Evidence and hypothesis

The storage-native and grouped K-tree experiments passed official15/15 but did not show smallcase benefit. Latest `6abec72a694b590c3c296090` / df36ef3 had C2/C3=2.57/3.28us vs baseline2.46/3.11. Their K32/64 guard excludes K40/48/56. Historical conditional probe ranges put smallcases within K32–56; this is motivation for coverage, not evidence of exact formal shapes or route hits. See TINY_GROUP_K_TREE and TEAM_PROBE_REVIEW.

This candidate finishes the same group-wide storage-native algorithm for all legal tiny K8 values. K beyond32 is added into the matching first lanes, then the common32 tree runs. For K40, products k32..39 fold into k0..7; k8..31 remain unchanged, then16/8/4/2/1 folds complete the dot. K48/56 analogous; K64 becomes the original32+32 first fold; K32 skips the first fold. Every realK contributes once before MaxN and SumM. No next-power-of-two product zero padding, no earlier Max, no input modification.

## Scope and resource changes

Branch `experiment/tiny-all-k8-fold`, kernel360054bytes, SHA `4d03162f721a879827d85d8c18c99bd49174cc636acd9b9d8f43567cf3eb29fa`. It derives from d1976d4; removing the three added regions restores entire passedbaseline1734f16 byte for byte.103 lines added versus that baseline; only kernel.asc algorithm changes. Independent officialtemplate otherseven source files equal baseline; dry-run sends only kernel/sameSHA.

- Same grouped B offsets/grid/plan, immutable `[K,N]` document, optional queryGather, batchBrcb, `[K,ar,pitchN]` products and repeated validNMax/originalMsum. FF/TF supported with K32/40/48/56/64; FT/TT remain baseline. No newGM/workspace/metadata.
- A half-precision block's logical length ar*K need not be16 aligned. DMA reads exactly ar*K elements and explicitly zero-pads the single block to ceil16(ar*K); document and combinedFP32 offsets use this rounded count. Query addressing retains actualK with no per-row K padding. Host budget includes that input rounding, not only logical elements.
- Common32 tree uses source offset step*ar*pitchN, while first-level count is (K-32)*ar*pitchN. Count and source offset are distinct for non-powerK. Add calls chunked to16320elements, Brcb repeats capped255. ActualUB/dststride guards retain baseline on failure; no group/tile retuning.
- Pipeline dependency protocol unchanged from grouped candidate, including explicit per-level PIPE_V when a level has work; all products ready before folding and validNMax. Original all-negative/paddedN/exactB float32 output contract retained.

CANN9 primary API research is recorded in TINY_STORAGE_VECTOR (Brcb/stride/PipeBarrier, plus full officialMul text retrieved). Prior native compilation does not prove this candidate's changed DMA/padding/fold precision or path coverage.

## CPU and static evidence

`python3 tools/validate_tiny_storage_vector.py`, production andTUNING each:

- 10080 exact-byte-capacity/shape/layout/group/pin/stride host controls; onebyte below neededUB rejects.
- 17616 dynamic/constant actual integer entries,121824active/15456idle blocks. All fiveK constants and dynamicK executed, FF/TF and allnegative/mixed values, three queued engines, independent integer fullK oracle and unmodified parentTinyCompute. CanonicalCast source checks every rawA/N padding position, immutableinputs, exactUB regions and unique exactB y writers/guards.
- 5652 actual encodedFP16/BF16 entries against independent FP64golden roundedFP32 and parentFP32 order; group1/2/3 with ragged tail. MaxAbs9.53674e-7/maxNonzeroRel2.93038e-6. MixedCPU check1e-4+1e-4*abs(golden) is not formal precision rules.
- 120 of17616 integer entries use synthetic512KiBUB to exercise Brcb/Add chunk boundaries, not a claim about physical A2/A3 capacity. Other integer entries use192KiB; nativeguard queriesactualcapacity.
- Nine negativecontrols rejected: input/output/terminaldependencies, batchoffset, missingfirstKlevel, invalidNmask, broadcaststride, destinationKstride, and specifically missingnonpowerKtail while retaining correctK64 firstfold.
- Entirebaseline scopeinverse, gitdiffcheck, officialtemplate sourceequality/dry-runSHA passed.

OneVectorFIFO model is not hardware subpipeline timing; softwareencodedcasts/FP32 arithmetic samples are not exhaustive native rounding or performance. No installed CANN/NPU on thisMac. CPUlog ignored artifacts/tiny-all-k8-fold/cpu.log with700/600 permissions.

## Formal gate and next action

CANN9compile/nativeprecision/NPUlatency PENDING. Commit/push, one formalstructural submission, immediatelysaveID and pollsameID toterminal. Require15/15; retain all15times and adverse observations, compare actual smallcase changes and existingC7/C14/C15 gains against passedbaseline and observedvariation. UnknownSoC/shape/plan/profile/routehit prohibits claims of controlledspeedup or actualscore. Clearlylarge improvement only warrants unchangedconfirmation. If no gain, archive the completed storage-native/K-tree direction without further variants or nearbyparameter scans, restore passed1734f16 and choose a different structure.

Main/historicaltags unchanged; overallsubstantialcompetitiongoal incomplete.

Official task **`6abec94f694b590c3c2a0c34`** created. Implementation `04bee91` pushed, kernel/template SHA4d03162f unchanged. Query this ID to terminal, native gates PENDING; never resubmit on observation timeout.

## Official terminal: Pass15/15, clear C2 regression

Task `6abec94f694b590c3c2a0c34`, implementation04bee91, SHA4d03162f: CANN compile successful,15/15Pass, precision_ratio all1. Timesus `[1.97,4.39,3.23,4.02,5.23,9.79,7.83,47.07,67.91,97.87,88.58,97.45,15.91,10.76,9.54]`. C2=4.39 vs passedbaseline2.46, a large unfavorable observation. K32/64 groupcandidate was2.57; adding nonpowerK coverage did not produce the intended gain. Without actual shapes/plan/SoC/profile this does not independently establish exact formalK, route or measured bottleneck. C7/C14 changes are on source-identical routes and not attributed to this experiment.

Archive this complete structural direction; no unchanged repeat, further storage-native/broadcast/K-tree variants or nearbyparameter scans. Restore passedbaseline1734f16/a5eef105 for the next independent work. Expanded broadcast/product movement and paddedN arithmetic are possible costs, not measured profiling explanations. Official15Pass establishes those samples, not full supported nativefloat/dependency coverage. RawJSON ignored artifacts/tiny-all-k8-fold/official.json (600); no activeofficialtask. Main/tags unchanged, overallmajorcompetitiongoal remains incomplete.

Next structure audit: examine the retained TT producer's ND-to-NZ transfer granularity versus usefulinput bytes and ManualTransposeFullM/Load3D pipeline on historical conditional M/N/K ranges. First compare archived fullMNpair/nativeNZ/ragged-resident failures, extract actual plan/resource counts with real header or existingfake-tiler model clearly labeled, then choose a structure genuinely absent from those experiments. Current TT already owns fullA1 residency, crossNt Bpackage streaming, doubleL0 and a single finalbarrier; do not propose them again or infer hidden routes from bucket numbers. No next algorithm implemented yet.
