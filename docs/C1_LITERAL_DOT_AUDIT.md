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

## Implemented / CPU PASS / native PENDING

Branch experiment/c1-literal-dot, kernel370984B/SHA256 `b8ab2f9faa564a99d40fcbf93a6b4ee922c42d5cbf82c12ab679a3ff15e3d79c`,47addedkernel lines. Three-GM-argument bmmms_dot_one_k32 hasliteral544BUBslices andnoGetBlockIdx/pitch/batchgroup/countargs. Same two64-byteinputDMA/oneCast64/oneMul32/oneWholeReduceSum32/4-byteoutput/flagpairs/PIPE_ALL. Source-declaredUBspan8256->544, notinputtraffic/launch/FLOP reduction or native compilerinstruction count.

UseLiteralDot queriesactualUB/AIV andrequiresUB>=544/AIV>0, originaldual15/finalBlocks1/exactshape/consistentcachedschedule; callerrequiresactual32-byteGMinputalignment. All11Tune pinsfallback. Existingshortdotandallotheralgorithms/MakePlan/GMbyteunchanged. Wholeinverseparenta2e6763 andprotected7=1734f16 proof.

`python3 tools/validate_c1_literal_dot.py` finalexit0:

- 512actualliteral/parentpairs: 64K-varyinginputseeds, fourUBpoisons, mixed/all-negative. RootUBexact544vs8256, typedtensorbounds, jointcast/FP32Mul/treeSum, delayedinput/outputDMA, exactoneoutputwrite/guards/inputimmutability. No floating-point inputencoding simulation; arithmetic usesint16valuesexactlyrepresentable inFP32. Storageflags do notalterunitM/N addressing, and hosttestscoverallfour.
- Production/TUNINGeach7776actualMakePlan+extractedlaunchconfigurations/24literalhits: twohostdtypevalues/fourlayouts/1-20-32cores/shape-neighbors/GMoffset0-2-16, fallbackaligned/Pad calls, UB543/544 andAIV0 rejection, cache-shape/grid/dual boundaries, allTune pinsoldlaunchpreserved. Fakecube tiler is notnativeCANN plan; targetVectorplanselection/control are actual source.
- Fivefaultcontrols removedPIPE_ALL/inputready orcreated FP/rawalias/overlongywrite/inputoverread; allrejected afterunmodifiedreference passed. Vectorops synchronous; V_MTE3/PIPE_V timingnotverified bymodel.

FormalCANN9compile/FP16-BF16precision/actualroute/SoC/profile/latencyPENDING. No guarantee1.18us referencefloor; compiler mayalreadyeliminateequivalentsetup andphysicalUBreservation not proven. Rawignoredartifacts/c1-literal-dot/cpu.log dir700/file600.

Finalisolated/private/tmp/bmmms-c1-literal-dot/project protected7restored1734f16; dry-runonly370984B/b8ab2f9fkernel. Nextcommit/pushthenONEgate,saveIDbeforepolling. Large-localconfirmationcriterion beforeseeingresults: all15Pass andC1atleast15%belowfastestrecent1.89us (<=1.6065us) justifiesONEunchangedconfirmation; modestgain no repeat/nearbyvariants. Thiscriterion isnotcompletionoftheoverallcompetitiongoal or proof ofstablecausalperformance. No benefit/regressionrestorea2e6763.

Implementation **7925ee2** pushed; uniqueformaljob **6ac7ce8e694b590c3c14baa6** createdonce. Same370984B/SHAb8ab2f9f. NativePENDING, querysameIDtoterminal.
