# C8 full-A/full-B L1 single-package frame

## Evidence → Diagnosis → One hypothesis

Retained7492776/SHA0794a2bf latest user-requested unchanged best task6ac77103694b590c3ccaa29e Pass15/allprecision1; C8=46.87us. Full result BEST_IDENTICAL_REPEAT_1008. No Web per user. Unsubmitted N-major full-B experiment268a802 showed269DMA calls both/no reduced volume, archived; it is not included here.

For user-supplied exact1025/1031/1032 and historical conditional BF16/TT route, existingA128x1040 plus completeB128x1040=532480bytes,8192over512KiB. NewN112, the next16-column granularity below128, enablesbothfull inputs499200B with originalM128 andfullK. This is a single-package architecture experiment, not a nearby tile/package sweep. No performance benefit asserted before native gate.

## Kernel scope

365832bytes/SHA256 `9f7eaa8449509b2efe686cb1bdf618023fa6497995eea2acb5413c3ee9e703b5`, 35additions/7removed lines. TT device adds compile-time FULL_B=false default, changes only B1 depth/priming/package-slot/final-credit counts. True mode consumes onefullK B package per C tile, prefetching the next complete B after last MTE1 read; two L0 A/B,C andGM rings remain. A remainsfullK cachedacross adjacent Ntiles. Same Matmul operand orientation/fullK/MMAD accumulation, Max(validN)→Sum(validM). No extra input-packing kernel or new GM allocation/path.

Host exactguard accepts original safe TT geometry/capacities/pins before overriding launch-only frameBM128/BN112/PK1040/NT10/workers=actual p.cubeBlocks. Original Plan/allocator/harness unchanged. All other code whole-byte-equal7492776 by inverse replacement; protected7byte-equal1734f16. Main and historicaltags unchanged.

Resources: L1A266240+B232960=499200 (+4096reserve), L0A65536/B57344/C114688, consumerUB57856(+4096), finalUB46208(+4096). Partialprefix46080 (old41472), per-worker doublering114688 (old131072); increased4608prefix and decreased16384eachring remaininsideoriginalsystem+allocation for every selectedworker>=1. OriginalGM path reused, not added. Ring/parts bounds checked at actual host. Input immutable, y4B only.

## CPU / static evidence

`python3 tools/validate_c8_full_inputs_frame.py`

- production/TUNING each1080actualhostplans,5exactselections across1/3/8/20/32cores; originalPlan/GM bytes, actualcorequeries, capacities, layouts/shapes/pins andsixone-byte budget failures. FakeCANN tiler is only host control evidence, not installedCANN9headers.
- 34actualproducer groups includingfull exactC8 parent/candidate at20workers, smallerM/N/K8 tails/idleworkers/positiveandallnegative/eageranddelayedFixpipe. PhysicalNZ/ZZ/ZN, Load3D/Load2D, fullK everypaddedC independentlychecked, A/B/L0/C/ring last-reader andGM/input/event guards. Sevenready/reader/fullKnegativecontrols rejected.
- 60threaded actualAIVgroups, includesexactC8 at8/20/32workers andN112 validtail23, threeFIFO enginepriorities, destructiveGMcreditreturn, uniqueoriginal partial/y writer, originalbarrier andNMax→MSum; eightcontrols rejectedincludinginvalidNmask. Cube/AIVcompanionssynthetic, notjointdevice proof. InputintegersnotnativeBF16encoding.

|Actual source at20workers|A DMA|B DMA|Total|A elements|B elements|MMADs|
|---|---:|---:|---:|---:|---:|---:|
|ParentN128/threeBpackages|26|243|269|3172368|9575928|729|
|FullinputN112/oneBpackage|27|90|117|3173400|9575928|810|

TotalDMAcalls -56.51%, Bcalls -62.96%. Totalinputelements +1032(+0.0081%), padded totalM/N1040andfullK1040 arithmetic unchanged, MMADcallcount +11.11%. These are CPU source-operation counts, NOT hardware speedup/counters. Costs: moreNtiles/C-Fixpipe/Vector credit events, noB1doublebuffer, largefullBtransfer latency, increasedpartialprefix; these may erase the call-count benefit.

## Native gate

Candidate only, CANNcompile/nativeprecision/all15latency PENDING; no taskID yet. Submit ONE isolated gate aftercommit/push anddry-run; saveID immediately, querysameID to terminal, no timeout resubmission. Actual hidden dtype/layout/SoC/plan/profile unavailable; suppliedshapeimagehas no dtype/layout, source matching does not prove route hit. Preserve all15 results/adverse samples. Require clear C8 gain outside retained46.18–46.87 spread for further unchangedconfirmation; no gain/regression means archiveandwhole-retained restore, no nearbyBN/BK/PK sweep.

CPUrawignored artifacts/c8-full-inputs-frame/cpu.log, isolatedproject/private/tmp/bmmms-c8-full-inputs-official/project; protected7from1734f16, onlykernel changed.

## Unique native task created

Implementation9782c98pushed; **6ac77690694b590c3ccea247** createdonce afterisolatedprotected7/wholeSHA dry-run. Query same ID to realterminal; no retry submission. CANN/nativeprecision/latency PENDING.

## Native terminal: Pass, C8 clearly regresses; archive

Task **6ac77690694b590c3ccea247**, implementation9782c98/SHA9f7eaa84/365832B: Pass15/15, all precision_ratio=1. Timesus:

`[1.96, 2.66, 3.18, 4.25, 5.42, 9.72, 7.78, 54.17, 67.96, 97.77, 87.28, 96.06, 12.82, 10.98, 9.02]`

Total471.03us, newest user Tbest calculatedmean51.37585466. C8=54.17us vsretained46.50/46.23/latest46.87 (latest+15.57%). Clearlyworse thanretained recent46.18–46.87; no unchangedconfirmation ornearbyBN/BK/PK sweep. Otherpoints/negativeobservations preserved; no attributionofunchangedroutes to C8. C13=12.82 consistent withretained localgain, not anothercontrolledconfirmation. Noactualhiddenshape/plan/SoC/profile; no direct route-hit/counter/causalclaim. Rawignored artifacts/c8-full-inputs-frame/official.json (600).

Source diagnosis: eliminatingB1double-buffer and issuing the next full-B onlyaftercurrentlastL1read reducesB-prefetch overlap opportunity even thoughDMAcalls269→117. MMADs729→810 andC/Fixpipe/Vectortiles81→90increase. These are code-level explanations/inferences, NOT measured hardware bottleneck/profile. Native result rejects the performance hypothesis; nativeprecision passed. Candidate remains archived onexperiment/c8-full-inputs-frame, whole-retained7492776 restored onexperiment/c13-resident-frame after recording. Noactiveformaljob; no further user repeat outstanding.
