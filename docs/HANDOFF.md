# C12 strided Bprep store — baseline measured

- Branch experiment/c12-strided-prep-store restores exact e2f1b63 / ZIP078635 kernel (353179B); C13 fullK archived without gain at520f27d. Keep native tools.
- Actual C12 BF16 TN normal plan dual6/BM128/BN128/Ns2/W20, case12Zn/phased/directrawA; source-bound one correctness +five default complete reports all outputs exact full FP64-storage golden118.35807037353516, inputs/yguards intact. Native five TaskDuration83.123322/83.063324/83.403336/83.323334/82.023277 us, median83.123322, on9382 logical0physical14 / callerbudget20 / actual24AIC48AIV.
- NEXT one distinct Bprep output issue compression: each K16N1024 group has8 contiguous UB N128 blocks destined to equally spaced packedGM panels; public DataCopyParams one strided 8-burst call can preserve byte layout while reducing3072 stores to384. Audit SDK byte units/address coverage/events, then native full golden+five reports; only >=10% native gain qualifies for formal submission and further family correctness. Not a 3phase/barrier scan.
- Raw ignored artifacts/c12-strided-prep-store and remote native_oj_like/results. SSH13910/master23895 verified; no active NPU job. Overall goal remains incomplete.

## Current source and identities

- Current branch experiment/teammate-777734-review. Worktree now experimental importedZIP078635, with source identity distinction below retained. No protectedseven changes or new OJ submission.
- New ZIP kernel **0786352034e77506894d4094083960f4f6af82782bf7cee6a0386148437ca436** /353179B/5600lines, while imported DISPATCH latest accepted source is **b8817327…** /350604B/OJ6acdd94de76989292739d40b. Do not attribute b881's Pass15/times toZIP078635. Newdocumented wholevector401.13us/reference60.2591 is teammate evidence, not our newserver measurement.
- Read [TEAMMATE_777734_REVIEW](TEAMMATE_777734_REVIEW.md), imported [DISPATCH](teammate_20261013/DISPATCH.md), [LOCAL_TEST](teammate_20261013/LOCAL_TEST.md). Prior fullstate archived HANDOFF_HISTORY_20261013_PRE_TEAMMATE.md. Older NEXT tiny-priority does not override newer teammate successes/constraints.

## Native server independently verified

- User authorizes serveruse. New refreshed jump established persistentforegroundSSH execsession13910/privatealiasconfig /private/tmp/bmmms-remote-access (credentials neverrepo/logs; sessionavailability notguaranteed).
- Newdevice **Ascend910_9382 /24AIC48AIV**, logical0→physical14/card7chip0, logical1→physical15/card7chip1. InstalledCANN9 /usr/local/Ascend/cann-9.0.0, driver26.1.1. Do NOTcopy old expectedphysical4/card2/20cores or /home/developer path.
- Frozen eightZIPfiles under /workspace/bmmms-codex/imports/teammate-777734-0786352034e7/project. NativeASCcompile PASS; original C1FP16NN/allnegative readiness smoke exactFP64golden-FP32 -5.40625 PASS. No full15/route capture/latency/profile measured; all PENDING. Rawignored artifacts/teammate-777734/0786352034e7/native-readiness. No liveNPU task; SSHtransport only.
- Teammate's .cannbot runners/queue not bundled or found in newserver. Readinesssmoke usedownflock only, notfullprotocol. Shared assetsread-only untouched.

## New measurement and scope

- Candidate selection: actualstorage fullFP64golden; source/DSO/input/normalPlan/device identity; app0warmup/5fullcalls; msprofop warmup5/launchcount5000/replaykernel/defaultmetrics; allfive completeTaskDuration+median. Native single-call is diagnostic only. No dropped reports/countersums/partialgoldens/minima mixing or probes/markers/intentional errors/CPU result replacement.
- Imported newer attributes: C4BF16TT, C6BF16NT, C9FP16NT; C10BF16NN andC11TT family evidence; preserve uncertainty for non-isolated properties. Confirm final dispatch after all assignments/early returns.
- Keep successful C8full-MK16prep, C10splitFMatrix, C12nativeZn/phasedB/directrawA, C13twoM256pipeline, C7fullK andC14singleAIV. Respect recorded C8stop/C7park/C9staticSchedulepause; don't revive nativecounterexamples (C9adjacentNsharedA/C13rawnormal/C10Bpack/etc).

## NEXT

Resolve ZIP078635 vsacceptedb881 mapping/result beforeusingreportedOJ. Import complete oj_like runner dependencies or implement independent equivalent harness without modifying protectedseven. Frozenbaseline fullgolden/normalPlan/capture/5reports on C12/C13/newdevice0 first; calibrate againstsame-source OJ rather than olddevice timings. Then use a distinct larger-benefit hypothesis. No automatic codeoverwrite/newsubmission in this review. No pendingunchanged-best repeat; overall performancegoal incomplete/main/tags untouched.


CLI readiness: earlier /private/tmp/cannjudge_cli.py and query_bmmms_submission.py are now absent (2026-10-13). Local archived client is available in artifacts/tooling/cannjudge-submit with its dependencies. It was loaded for an authorized read of the supplied documented submission ID, but the request returned HTTPError; status/cause not captured, no source/OJ data fetched and no login-expiry claim. No new submission. ZIP078635-to-b881 binding remains PENDING; avoid treating missing temporary scripts as an authentication failure.
