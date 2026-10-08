# C8 workload / cache-aware tails: mathematical assessment

## Current authoritative state

Kernel restoredwholea2e6763/368782B/SHA16b51684 onexperiment/c8-workload-audit. FailedC1literal archived2e10a23 (implementation7925ee2), native6ac7ce8e694b590c3c14baa6 Pass15/C1=1.93withinold1.89-2.04, noconfirmation. Noactivejobs, C10balanced/C8phasedA/C13frame retained, main/tagsuntouched. No C8 kernelcandidate yet.

Retained C8 TT frame conditionally matches supplied1025/1031/1032 andBF16/TT; actualnativeSoC/route/meta stillunknown. M128/N128/PK384/BK128,81M-major tiles splitbycountacrossworkers, fullresidentA reusedwhileMtileunchanged, Btwo-package/A2-B2-Ctwo buffers, phasedA andoldGM remain. Modelbelowuses20onlyasonequeried-device example, notfixedhardwareassumption.

## Executed mathematical enumeration

`python3 tools/audit_c8_area_partition.py`, purepartition arithmetic, **not executed Ascendsource/actualTensor/instruction/timing validation**. Six1/3/8/20/24/32core old-vs-area pairs plusfour8/20/24/32core cache-tail groups. EveryvalidM/Ntile row coveredexactlyonce, totalpaddedMMADoutputarea unchanged. NativeM=1/N=7 tails cost16padded rows/cols, not1/7; balancedweight mustincludethis.

At20cores:

|Schedule|MaxpaddedCarea/core|MaxCtiles/core|Maxsmall-MMAD PIPE_M barriers/core|GlobalCtiles|Bpackages|Ainputelements|Binputelements|
|---|---:|---:|---:|---:|---:|---:|---:|
|Retainedwholecells|65536|5|45|81|243|3172368|9575928|
|Area-only boundaryM16 splits|55552|13|90|96|288|3567624|11557368|
|Full-cell splits + cache-aware tails|55552|6|18|97|291|3178560|11689464|

Area-only lastcorecollectsalltailpackets: rejectthisnaiveformbeforeanynative submission. Improvedmathematicalplan splitsonlyfull128x128cells on16-rowboundaries. FullM/Ntailcellspersistwhole; attachN-tailtoacorewhoseendingMpanelisresident, distributeMtail packets bypaddedwork/barrier/Ccount, cornergoestocorealreadyholdingMtailA. Greedysequence isreproducible in script, notvalidateddevicecost optimization.

Improved20core worstpaddedarea -15.234375%, maximumsmall-MMADbarriers45->18; globalCtiles81->97(+19.75%),Binput +22.0713486578%,Ainput +0.1951847809%. MoreDMA/MMAD/scalar/partial workcanerasebenefit. Thisdoesnotpredict15%latencygain. At32coresmaxarea49152->35072(-28.6458%) andsameglobal81Ctiles/Bvolume; Ainput4363296->4235328. At8coresglobal81/Bvolumeunchanged andAinput1982472->1065024; at1/3cores useexistingframe. Allunfavorablecountskept.

## Next concrete implementation design (PENDING)

- OriginalM128/N128/PK384/Aphases/GM kept. Heavycell virtualgrid8x8 has8M16atoms/cell=512atoms; perworkerheavyboundariesfloor512*w/W. GatherconsecutiveatomswithinonecellintooneCfragment; partialrowOffset may16..112 androws16..128.
- Precomputeonlysmalltail ownership onhost (existingqueriedworkers), preservinggreedycachechoice. PackeightN-tail ownerIDs andnineM-tail/cornerIDs into **two64-bit kernelarguments**; atmost32workers requireonebyte or6bits/owner. Thisislaunchmetadata, notGMallocation/path/Planorworkspacechange. AvoidrecomputingO(W^2)greedychoicesoneverydeviceCtile. ExistingTTFrameShape32B staysunchanged; newdefaultfalse templateinstance onlyforcurrentexactC8guard withworkers>=8.
- One shared actualtask descriptor forCube/AIV/Bprefetch mapsvirtualheavy/tailtask tooriginalMt/Nt, M16fragmentoffset/count. BprefetchmustfollowdescriptorN inbothpackage startupandend advance, notoldtask%s.nTiles. CountersforactualB/A/cells mustmatchmathematicalestimate beforegate.
- KeepfulloriginalMpanel A1 cache/phase publication; Load3D selectsfragmentviachannelstartrowOffset butfullcacheRows remainschannelSize. Current ManualTransposeFullM haskStartPt0; supportednonzerochannelstart withenTranspose andBF16raw-half interpretation needsactualsourcephysicalmodel and**nativeCANN9 compile/precision**, notassumptionfromCPU. Defaultoldhelpercallskeepidenticalparameters.
- L0C/ringallocatedBM128 unchanged; Fixpipewritesonlypaddedfragmentrows atoldBNpitch. AIVsubrowStart64 unchangedbutGMpartialpositionincludesfragmentoffset. Partialstoresonlyownedvalidrows toavoidpaddingoverwritinganotherworker. LastoriginalMt'sfinalfragmentmayfillpaddingonlywithinoriginalpaddedM1152; nevercrossplane/arena. BothAIVzero-row/idle creditsremaincomplete.
- OriginalNtplane partials/finalMerge/SyncAll/y unchanged, soMaxN precedesSumM. Actualpositive-K-varying/allnegative, fragmentedA2NZ->ZZ addresses, delayedA/B/M/Fixpipe, destructiveGM reuse, uniquepartial/y/guards, padding poison, allworker mappings required. Integer modelsalonearenotnativeprecision/protocol/time.
- Wholeinversea2e6763/protected7 proof; scope/noTune/capacity/SoC queries guardnewroute. Ifactualmodels andcounts succeed, commit/push/dryrunONEgate/saveuniqueID/pollterminal. No repeatedresidentB/full-input/N-major/nearbyPK/BN/BM scans. No nativecandidate currentlyexists.

NoWeb/subagents/newGM/harnesschanges. Rawignoredartifacts/c8-workload-audit/partition.log (700dir/600file). Mathematicalownership correctness doesnotproveCube/AIV/finalizer correctness or actualworkbalance oncefixedcosts apply. Overallmajorcompetitiongoal incomplete.
