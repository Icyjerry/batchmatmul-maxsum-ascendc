# C10 exact dimensions and conflicting layouts

## Evidence / limits

Userimageprovides B1/M4096/N1280/K1152 withoutdtype/layout. Historical probes conflict: BF16/FF versusFP16/TT. CPUsourceauditdoesnotresolveactualformalmetadata. Do not inferonefromlatency alone.

`python3 tools/audit_c10_exact_routes.py` extracts actualcurrenthostPlan/selectionhelpers and executes32configurations: all8dtype/layouts at1/8/20/32cores. FakeCANNtiler, notnativeplanning/header/profile proof. Currentkernelaf886e1(SHAb87ec006) onlyC8phasedchanges; C10hostunchangedbywhole-sourceproof. CSV ignored artifacts/c10-exact-routes/host.csv (700dir/600file).

At20cores:

| dtype/layout | dual | BM/BN | K chunk | N tiles / N split / window | workers | TT frame |
|---|---:|---|---:|---|---:|---:|
| FP16/FF | 1 | 128/256 | 1152 | 5 / 1 / 4 | 20 | 0 |
| FP16/FT | 1 | 128/128 | 1152 | 10 / 1 / 8 | 20 | 0 |
| FP16/TF | 1 | 128/256 | 1152 | 5 / 1 / 4 | 20 | 0 |
| FP16/TT | 29 | 128/128 | 1152 | 10 / 1 / 8 | 20 | 0 |
| BF16/FF | 20 | 128/256 | 64 | 5 / 1 / 1 | 20 | 0 |
| BF16/FT | 1 | 128/128 | 1152 | 10 / 1 / 8 | 20 | 0 |
| BF16/TF | 1 | 128/256 | 1152 | 5 / 1 / 4 | 20 | 0 |
| BF16/TT | 29 | 128/128 | 1152 | 10 / 1 / 8 | 20 | 0 |

Actual Launch text maps BF16/FF dual20 to `bmmms_manual<T,false,false,true,true>`: fullresidentA, K64/B256, oneL0C (tree8), originalM-shard andtwoGMslots. FP16/TT dual29 goes to `bmmms_manual<T,true,true,true,false,false,false,false,true>`: full-M residentA/Load3D, originalNwindow8 andB K128 TQue packages. It is **already manual**, not a library fallback; an earlier speculative library diagnosis is invalid for this actualshape and must not guide implementation.

Neither canhitC8TTframe duecurrent BF16/TT/M<=2048 guard; broadeningthat guardblindlywouldnotcoverFF orsingleC/merge-repeatoverflow.

## Next executable independent hypothesis

Start exact BF16/FF dual20 branch, retaining BM128/BN256/K64, originalPlan/tasks/ns/window/oneC/twoGMslots. ExistingCase9CopyBPackage alreadytemplatedTX2 and containsFF ND2NZ layout; bmmms_case9_packages hardcodes TX2=true but has compile-time false LoadData branch with per-packagepaddedK pitch. Expose onlytheexactFFcase via a TX2 template defaulttrue; existingC9remainsdefault. NewC10 B-packmaximum192 = largestK64multipleinsideactualL1 afterresidentA:

- fullA294912B + twoB256x192 panels196608B =491520B (+4096reserve).
- originalL0A32768/B65536/C131072, originalpartial16384/twoC-GMrings262144perworker.
- predicted sourceBpackages18→6perCtile, exact20cores M32/N5total160Ctiles, B DMA2880→960 withsamebytes; producer/kernel mustactuallyexecutedtoverifythese counts, notyetclaimedverified.
- Both L1 B buffers stay, unlike rejected singleB full-inputC8. FF layout differs fromtestedC9 FT, so physicalNZ→ZN andlast-reader/actualC/golden/Vector/plan/pin modelsneededbeforeONE nativegate. No existingC9packet-size sweep ornewGM allocation.

IfactualcaseisFP16/TT thisFFguardwillnotselect; absenceofC10gainwouldnotproveFFdoesn'thit, andmayreflectcosts. Preserveconditionaldtype/layout. The alternativeTTwhole-M quantizationhas32Mtasks/20cores(max2Mtiles)vs320completeNt tasksideal16/worker, butcontinuousschedulingraisesAduplicatecopies andfullfinalmerge320Vectorrepeats>255. Do notimplementtheTTandFFhypotheses together. FutureTThypothesisneedslocal boundedmerge andworkspaceproof; keepseparate.

No C10kernel edits/native task yet. No Web. NextAgent should implement the FFpackage-only hypothesis withsource/capacity/physicalmodels, keepingC8phasedexperimental gain and originalretainedsnapshotavailable.
