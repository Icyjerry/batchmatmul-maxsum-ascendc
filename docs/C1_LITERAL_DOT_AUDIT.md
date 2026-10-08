# C1 independent audit: literal single K32 dot frame

## Current evidence

Kernel wholepassed a2e6763/368782B/SHA16b51684 onexperiment/c1-literal-dot-audit. ThreeC10 experiments wereCPU/native15precisionpassed butnot faster: fullM178.32, latecredit92.84, directA2 92.98 versusparent91.53. Archived74f9937/44d25e2/35480f2; noactivejobs/repeats/nearbyparameter scans. CurrentC10balanced/C8phasedA/C13residentframe retained. Main/tagsunchanged.

Actual shortdot kernel handlesup to8batches perblock with runtimebatchCount/kCount, GetBlockIdx, pitch/elements/operandoffset arithmetic, two-GM plusoutput/count/count signature, manual8256BUB frame. ItalreadyavoidsTPipe andcombinesbothinputsintooneCast; do not reintroduceTPipe/claimremovingitalreadyisnew. C1recentunmodifiedtimes1.89..2.04us, latestuserTbest1.18; differentSoC/frequency/routeunknown, no guaranteed1.18floorclaim.

User suppliedC1logicalB1/M1/N1/K32. AtM=N=1 bothtranspose storagebitsleave the same linearK-vectororder, so thisshapehaslesslayoutambiguitythanC10. That doesnot establishactualformalC1 metadata fromthepublicAPI. FP16/BF16 mustretainactualT andFP32cast/product/reduction.

## Independent hypothesis (not implemented/submitted)

A dedicatedliteralK32,one-outputVector kernel withonlythreeGMarguments andno runtimegeometry/BlockIdx/group8 calculations, retainingtwoinputDMA/onejointFP32Cast/oneMul/oneWholeReduceSum/exact4-byteoutput andrequiredcompletion barriers. StaticUBexample:

|Area|byteoffset|bytes|
|---|---:|---:|
|64inputT values(two32-vectors)|0|128|
|64convertedFP32values|128|256|
|32FP32products|384|128|
|8FP32outputUBlanes|512|32|

544B, allboundaries32aligned andnonoverlapping. Bothinputstransferred32actualelements,nooverread. Onlyone4-byteywrite, not8lanes. Do notinitMaxzero: withN=M=1 y isexactdot, negativeoutputsretained. WholeReduceSumK32 ordering equivalenttooriginalshortdotonebatch, notscalarFP32sumorFP16accumulation.

Host onlys.b=s.m=s.n=1/k32, originaldual15/finalBlocks1, actualinputGM32-bytealignmentandoriginalresourceplan, allBMMMS_TUNINGpinsfallback. UnalignedGM/batches>1/K!=32 keeporiginalshortdot includingDataCopyPad. Do notmodifyMakePlan/GM/ABI/harness/C2+ routes. No nearbyK/batch/UB-offset scan. This isonefixed-workloadframe hypothesis, not performanceproven byconstantfoldreasoning.

## Required next actions

- Implementliteralbodyusingexistingpassed APIs withexplicitMTE2_V/V_MTE3 pairs andfinalPIPE_ALL. Wholeinversekernel/protected7proof.
- Reuseactualteammate_tinyCPU tensor/event/DMA models. PositiveK-varying andall-negative cases, bothstoragebits/dtypesasintegerlayoutproxies, unknownUBpoison/input/yguards, oneuniqueoutput, delayedDMAoutputcompletion. Parentactualshortdotreference. MissingPIPE_ALL, wrongFP/rawslice/overlongywrite controlsmustreject; ensureunmutatedreferencespass.
- Actualhostselection/pins/GMunalignment/fallback/UBcapacityboundary plusoutside-sourceproof. Separateinteger modelsfromBF16/FP16encoding/CANN9/hardwaretime.
- Commit/push/dryrun, ONEformaljob, immediatelysaveIDandquerysameIDto terminal; all15precisionrequired. CompareC1againstobservedrange, notrandomotherrouteimprovements. Largegainonlywarrantsoneunchangedconfirmation; modest/no gainarchivewholechangewithoutnearbyvariants.

No C1 code/nativecandidate yet. The bodycanonlybenefitsetup/prologue/argumentoverhead; globalinputbytes/FLOPs/launchcountunchanged. Nativecompiler mayalreadyremoveequivalentwork orlaunchfloor maydominate. NoWeb/subagents/newGM.
