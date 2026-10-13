# Teammate 777734 import and new server readiness

## Identities and scope

User supplied batchmatmulmaxsum_submission_777734.zip, DISPATCH.md and LOCAL_TEST.md on2026-10-13, then authorized SSH server use. Original documents preserved in docs/teammate_20261013. Their instructions/results are imported teammate records, not independent OJ trace or a request to run every listed experiment. No web, subagents or new OJ submission in this review.

- ZIP SHA256:26b2dbced707d5ce56b8cacb97dc33bed79f7acf4df2ffa285f4069b07e4e7fc.
- ZIP kernel:353179B/5600lines/SHA256 **0786352034e77506894d4094083960f4f6af82782bf7cee6a0386148437ca436**.
- DISPATCH newest retained source:350604B/5600lines/SHA256 **b8817327235bc702df045114f673547a1fd04ac5846a78a543ffcb1d32728c01**, reported OJ **6acdd94de76989292739d40b** Pass15. This is NOT the ZIP byte identity. LF/trailing-space normalization of ZIP still078635; CRLF produces e0bfb709, notb881. Without b881 source/mapping or ZIP-specific full result, semantic equivalence and OJ attribution remain unestablished. User textual Image#1 has no readable attached image in the received turn.
- ZIP's other seven project files byte-equal current project and protected1734f16. Local working kernel stays historicala2e6763/368782B/SHA16b51684, no algorithm/main/build/golden/test changes.
- Raw imported kernel/diff/native logs kept ignored artifacts/teammate-777734/0786352034e7; not called current best or formally tested078635.

## What changes our earlier assumptions

| Case | Imported dispatch knowledge | Consequence |
|---|---|---|
| C4 | User-confirmed BF16 TT,4/8/16/128 | Build fixture from this; old TN speculation superseded |
| C6 | User-confirmed BF16 NT,13/23/73/192 | Earlier static direct return already handles it; changes below that return may be irrelevant |
| C8 | BF16 TT,1/1025/1031/1032,exactdual39 BM112BN128BK128; full-M K16 prep | Five authorized rounds finished; record says stop new C8 rounds |
| C9 | User-confirmed FP16 NT,1/2048/1536/1280; residentdual36 | Use final dispatch, not earlier dual value; static Schedule direction paused in teammate record |
| C10 | BF16 NN family confirmed by distinct full-algorithm/dtype responses; shape not directly traced | Retained split LEFT/RIGHT FMatrix reuse; old FP16TT assumption superseded |
| C11 | TT MDL family confirmed, dtype/exactshape not unique | Optimize original MDL; A4/B4 retained; BM80 manual/groups5/UnitFlag counterexamples |
| C12 | Strongly supported BF16 TN packed-B + Aslab family | Preserve nativeZn B, phasedBprep, directrawA into originalAslab |
| C13 | FP16 NN single-frame family; exactM not directly proven | Retain C-transposed representation and twoM256-half pipeline |
| C14 | BF16 NT wideN family; fullshape not isolated | Retained singleAIV MIX11, originalNP128/span2; NP256 rejected |

C1–3 and C15 did not receive new independent layout/dtype isolation. C7 retained optimized fullK/UnitFlag family but remains parked in teammate record. Do not upgrade all local frames into directly observed hidden OJ properties.

Static ZIP inspection finds C8 FULL_M_A_PREP, C10 SPLIT_FMATRIX and separate LEFT/RIGHT setup with public reset configuration, C12 PACK_B_ZN/PHASED_B/DIRECT_RAW_A, C13 UseTallHalfPipeline, C5 direct MIX11 and C14 fullrow singleAIV. Feature presence and compiler acceptance do not prove actual capture for every case. Old-vs-ZIP textual diff5501added/6684removed is dominated by compact formatting; token alignment was interrupted, no lexical/semantic equivalence claim.

## Imported successes and useful counterexamples

Newest documented b881 whole15 timesus:
`[1.90,2.51,3.16,4.08,4.76,9.58,6.89,36.45,57.35,76.33,82.55,87.93,9.11,9.88,8.65]`
Total401.13us, latestuserTbest reference mean60.25914497. These are teammate-reported, tied to b881; NOT measured on this server/ZIP078635 or a live rank. Relative to our earlier complete459.02us vector they indicate substantial progress, not a controlled same-device comparison.

- C8 full-M K16 Aprep: reported OJ36.31 versus40.16/local36.959999 versus40.139999. Moves A preparation from many M fragments toward65wholeM K16 tasks; counters support less exposed prep, not additive PMU time.
- C10 splitFMatrix: same source rebased11edits, reported local76.139999 versus78.580002/OJ76.05 versus77.22; reuse left A and right B configuration, preserve full math.
- C12 nativeZn+phasedBprep overlap: reported phase OJ88.63 versus91.76/local88.741776 versus91.721832. Early directrawA added limited gain: OJ87.93/local88.161766. Preserve two-C and fullK.
- C13 halfM pipeline: retainC-transpose/ND2NZ/native2D, first halfFix/reduction overlaps second halfMAC; reported OJ9.24 versus11.34/local8.900178 versus11.140223. Newest documented combo9.11.
- Counterexamples to respect: C9 adjacentN sharedA local61.541/62.361 versus57.461 despite fewerMTE1 calls; C13 rawnormal13.880 versus11.140, normalC/BM416 rejected; C10 nativeBpack79.940 versus78.580/OJ80.60 versus77.22; C12 rawB/PairA/B3D/group changes and C8 failed rounds documented. Do not rename and repeat these directions.

## New testing/competition rules to carry forward

Use imported LOCAL_TEST as the measurement specification:
1. Freeze source and actual FP16/BF16 storage input; same inputs/device for baseline and candidate.
2. init → build → read normalPlan → review/completeFrame → correctness → validate → oj_like. Bind sourceSHA, actual DSO, inputs, plan, device and all reports.
3. Application0warmup,5complete calls; external `msprof op --warm-up=5 --launch-count=5000 --replay-mode=kernel`, defaultmetrics/no filtering. 5000 is collection ceiling, not5000 application samples. Preserve all five completeTaskDuration values and median.
4. Validate fullFP64 matmul→fullNmax→fullMsum from actual b16 bytes, outputFP32 for correctness and all five performance calls. Do not use sampled/truncated reference.
5. Preserve all mixed tasks/preparation/reduction; fail collection if kernels/reports/identity missing. Native single-call latency is historical diagnostics, not candidate ranking. OJ final confirmation remains separate.
6. Serialize NPU use through queue/globalfilelock; compile/offline work may overlap. Teammate npu_serial/run_device/init/completeFrame/capture tools are NOT included in this ZIP and not present in the supplied fresh server. Our one readiness smoke used an independent ownfilelock; this is not claimed equivalent to their full queue/performance runner.
7. No added probing kernel, intentional delays/errors/markers, hidden-input access, CPU substitute output, omitted math or forged results. Host resource queries and external full-math reference are readiness/validation only.

Respect teammate's current scope limits (no new C8 rounds, C7 parked, C9 constantSchedule paused) pending explicit revised user direction. SDK installed headers/native compile govern APIs; fewer calls or summed overlapping counters do not prove speed.

## New server independently verified

SSH connected after user refreshed short-lived jump authorization; credentials remain outside repo/logs. Persistent foreground local SSH transport execsession13910 (may expire/disappear; not a durable login guarantee), private aliasconfig under /private/tmp/bmmms-remote-access; no credential values in this record.

- Linuxaarch64; CANN9.0.0 installed `/usr/local/Ascend/cann-9.0.0/set_env.sh`, compiler/runtime versions9.0.0; msprof/compiler available after sourcing it.
- npu-smi26.1.1: NPUcard7, chip0 logical0 physical14; chip1 logical1 physical15. ACL reports two logicaldevices, both **Ascend910_9382**. This differs from teammate's9362/card2/physical4.
- Device0 native platformAPI: **24AIC/48AIV**, UB196352B, L1524032B, L0A/B65536B each, L0C131072B. Host resource probe required original tiling_api/register/platform/unified_dlog dependencies; initial incomplete link commands failed, full dependency link passed. Queries are not operator kernel trace or latency.
- No teammate .cannbot/tooling workspace found in root/home/workspace/opt/mnt/data depth3 search. `/workspace/shared_assets` explicitly read-only and untouched.
- Frozen eight files uploaded to `/workspace/bmmms-codex/imports/teammate-777734-0786352034e7/project` with SHA check. Original CMake/main/others unchanged, CANN9 native ASC build/defaultdav-2201 **PASS**,11warnings mainly mainGMattribute, executableSHA **b1caf71435d238dc989525e33b95e342c72df34f7a909a2ee5bda9ad7038fe0e**.
- Original main's C1-only execution ondevice0: actualFP16NNB1/M1/N1/K32/allnegative dot, fullFP64reference→FP32 **-5.40625**, actual **-5.40625**, abs error0. **Readiness smoke PASS only**. No performance measured, no15case/nativeBF16/layout coverage or source-route capture established. Native fullprecision/oj_like/profile **PENDING**.
- Native logs+smoke JSON downloaded to ignored native-readiness folder; no active NPU job, just SSH transport.

## Next executable action

Before optimization: resolve ZIP078635 versus documentedb881 identity/results; import teammate's complete runner dependencies or build a separate equivalent harness without modifying protected seven files. Use newdevice0→physical14/card7chip0, actual24/48/resources andnormalhostPlan. Start frozen baseline fullgolden/capture/5-report validation on C12/C13; calibrate same-source behavior on this server before trusting local ranking. Keep fullscope math/resource fallbacks. Do not automatically overwrite current kernel or submit ZIP as already validated15Pass.


CLI readiness: earlier /private/tmp/cannjudge_cli.py and query_bmmms_submission.py are now absent (2026-10-13). Local archived client is available in artifacts/tooling/cannjudge-submit with its dependencies. It was loaded for an authorized read of the supplied documented submission ID, but the request returned HTTPError; status/cause not captured, no source/OJ data fetched and no login-expiry claim. No new submission. ZIP078635-to-b881 binding remains PENDING; avoid treating missing temporary scripts as an authentication failure.
