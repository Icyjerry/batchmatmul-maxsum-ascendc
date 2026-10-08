# C10 FF B-package 实验已结束：归档 · 2026-10-08

- 实现 fd23d39/SHA31bc978f，唯一任务6ac7aefd694b590c3cfe44d9，正式 Pass15/全部precision1。
- C10=97.06在原路径历史96.98–100.24内，没有明确性能收益；总464.17/latestTmean51.08302483，不是排名。全15与不利样本见 [C10_FF_B_PACKAGES](C10_FF_B_PACKAGES.md)。不重交/不扫附近B包。
- 此分支归档候选；下一条可执行动作：切回 experiment/c8-phased-a-ready，确认 kernel 逐字节等于 af886e1，再复制结果交接文档。不得退回更早7492776，保留已通过的 C8 phased-A。
- 无在跑任务。下一独立方向先核实 C10 正式 storage/dtype/plan，历史 BF16/FF vs FP16/TT 冲突尚未解决。无 Web，不新增 GM，不修改受保护七文件/main/tags。

# 当前执行状态：C10 FF B 分包候选 · 2026-10-08

- 分支 experiment/c10-ff-b-packages；以已 Pass 的 af886e1/C8 phased-A 为父。
- 实际实现改为原 manual 的 B_PACKAGE=192，保留原 Vector/事件/Plan/GM；没有改用 C9 消费流程。kernel369094B/SHA31bc978fbf8555a8ff8dd5dafa76b0df5c5fb06f3b4b5245dfbff9ae379b5ff1。
- 完整 FF 源码 CPU/地址模型通过：960 B DMA/2880 MMAD/输入量不变；8 producer、生产和 TUNING 各40 host/5命中、六故障控制通过。native TQue 最后读者契约仍建模假设；实际正式 dtype/layout 冲突未消除。
- 实现 fd23d39 已推送；正式唯一任务 **6ac7aefd694b590c3cfe44d9** 已创建。编译/精度/性能 PENDING，查询同一任务至终态，不能重交。详见 [C10_FF_B_PACKAGES](C10_FF_B_PACKAGES.md)。有回退需要时整份恢复 af886e1，保留 C8；不恢复更早版本。
- 用户无 Web；main/历史标签不动；没有未完成原样复测请求。CPU原始日志 artifacts/c10-ff-b-packages/cpu.log 不入 Git。

# Current passed experimental baseline · 2026-10-08

- Current experiment/c8-phased-a-ready, implementationaf886e1/kernel365948B/SHAb87ec00643094e19c3c0433113480791494f8e00771887982a1766276d13e08b. Whole-parentinverse7492776; AIV/Plan/GM/harness unchanged. PhasedresidentAready384/384/264 keepsoriginaldoubleB.
- Native **6ac7a921694b590c3cf97c01** terminalPass15/allprecision1: C8=44.09 vsretained46.18–46.87; singlemodestlocalobservation(-5.93%vslatest), NOTlarge/stable/wholecompetitiongain. Total466.89/newestTmean50.38880654. AdverseC10/C11/C15 retained. See C8_PHASED_A_READY/PERF_LOG. Noactivejobs, no unchangedconfirmation or nearbyphase scans.
- Keep this passed code as experimental forward baseline; main/tags/retainedcompetitionbranch NOTpromoted. Originalretained7492776/SHA0794a2bf remains onexperiment/c13-resident-frame.
- Source/CubeCPU30groups/ninecontrols, host2160/fivehits eachproduction/TUNING, per-byte region readiness and live operands; onlyintegers/syntheticcredits, notBF16hardware/profileproof.
- NEXT: [C10_EXACT_ROUTE_AUDIT](C10_EXACT_ROUTE_AUDIT.md), actual32hostconfigurations confirmconditional BF16/FFdual20 andFP16/TTdual29 (alreadymanual, NOTlibrary). Implement ONEexact FF B-package192 hypothesis throughexistinggenericCase9helpers/defaultTX2=truepreserved; verifyactualsource/physicalNZ→ZN/liveTQue/capacities/oldGM beforeonegate. Proposed18→6Bpackages notyetverified; noC10edit/taskyet. No broad TTguard/parameter sweep/newGM.
- User noWeb. Fullmajoroptimizationgoal stillactive/incomplete. PreviousgoalturnmadeverifiedC8regressionprogress; thisturnmadepassedphasedAandC10sourcediagnosisprogress, notblocked.

# 最新接手状态 · 2026-10-08

## Current retained code and next executable action

- Current experiment/c13-resident-frame, kernel364169bytes/SHA0794a2bfc777ac48c373b3085cd96fd1224b0bf0a4f6a9351d290bb421dbad2d, implementation7492776. Parent1734f16 +threeadditions178lines only; C4regression/oldC13tail excluded.
- Formalfirst6ac73bd0694b590c3ca19b3d andoneunchangedconfirmation6ac73c8b694b590c3ca2153b bothterminalPass15/allprecision1. C13=12.62/13.19, bothbelowparentrecent14.94-16.74/median15.13; pairmidpoint12.905 (-14.71percent vsparentmedian), sloweststill11.71percent belowfastestparent. Retainlocalizedgain, notwholecompetitionbreakthrough orstablecausal A/B. Full15/totals/scores in[C13_RESIDENT_FRAME](C13_RESIDENT_FRAME.md).
- User requested ONE unchanged retained-best submission on 2026-10-08: **6ac77103694b590c3ccaa29e**, same SHA0794a2bf/364169B. Terminal Pass15/allprecision1; C8=46.87/C13=13.44. No active job/no further repeat. [BEST_IDENTICAL_REPEAT_1008](BEST_IDENTICAL_REPEAT_1008.md). Native compile/15 precision passed. OriginaloneBload/L0residence/fullK128/stridedM/doubleC/workerpartials/originalGM retained, frameworkandVectorredundancyremoved. Nativecompile/15precision passed; allshape/profile/SoC coverage notclaimed.
- C11 assessment was implemented/verified/submitted on independent experiment/c11-exact-tt-frame, archived3c916aa/implementation9160eb2. Task6ac73fd0694b590c3ca4be61 Pass15/allprecision1, C11=87.16 within historicalsame-source86.97–88.91, no clear improvement. No repeat/nearby tile/package scan. Candidate34host lines restored out by switching back here; full kernel byte-equal7492776/SHA0794a2bf confirmed. Results [C11_EXACT_TT_FRAME](C11_EXACT_TT_FRAME.md), CPU models on archivedbranch, rawignoredartifacts/c11-exact-tt-frame. No activejob.
- C6 pure Vector row-pairs archived a45ef9d/implementationf4907c3 on experiment/c6-vector-pairs: task6ac744ee694b590c3ca8ea6c Pass15/allprecision1, C6=24.24us vsretained9.78/9.75, clear regression. No repeat/nearby pair/chunk/padding scans. [C6_VECTOR_PAIRS](C6_VECTOR_PAIRS.md); whole retained source restored.
- User instructs no Web; continue local source/model/teammate/formal evidence. Latest request resumes optimization after one best submission.
- C8 N-major resident-B stream archived268a802 on experiment/c8-resident-b-stream, CPU-only/unsubmitted: totalDMA269both, inputvolume+0.34%, no large-gain call/volume evidence. Actualsource34Cube/60threadedAIV groups passed in scope; hostmodel/native PENDING. See [C8_RESIDENT_B_STREAM](C8_RESIDENT_B_STREAM.md). Not merged.
- C8 full-input one-B-package frame archived748c4b7/implementation9782c98 on experiment/c8-full-inputs-frame. SourceDMA269→117(-56.51%), full-A/BL1499200B usingM128/N112; originalGM reused, no allocator/plan change. Native6ac77690694b590c3ccea247 Pass15/allprecision1 butC8=54.17 vsretained46.18–46.87: clear regression; no repeat/nearbyBN/BK/PK scan. [C8_FULL_INPUTS_FRAME](C8_FULL_INPUTS_FRAME.md), models onarchivebranch/rawignoredartifacts. SingleBbuffer reduces overlap opportunity and extraNt increasesMMAD/creditcalls; code-level explanation, nothardwareprofile. Whole retained7492776 restored here, noactivejobs.
- NEXT independent assessment must preserve useful B1 double-buffer overlap. Start from exact selected TT producer's input-ready/last-reader and scalar-loop instruction counts, compare existing teammate source; reject merely changing resident operand or eliminating B double-buffer to reduce API calls. No nearby scan of archived full-input structure. No Web; actualSoC/plan/profile still unavailable. Overallmajoroptimizationgoal incomplete.
- Userexactshapeimage andbaseline [EXACT_SHAPE_AUDIT_1008](EXACT_SHAPE_AUDIT_1008.md), dtype/layoutmissing andC10conflictremain. Baseline notTbest. Overallmajoroptimizationgoal incomplete.

## 最新计分参考与差距

用户最新Tbest：`[1.18,1.54,2.13,2.37,3.57,6.38,6.37,13.88,48.30,64.85,67.87,80.65,7.31,7.59,7.84]`μs。用 [SCORE_REFERENCE_1008](SCORE_REFERENCE_1008.md)，100/(1+log_1.5(t/Tbest))后15点平均。用户榜首Young耗时重算82.15390，与82.15一致；通过版最新6ac0d57f重算50.99873。旧56.42050/50.x分数均属各自旧参考，耗时/精度未改。

相对用户提供的最新榜首行，最近五次同SHA逐点中位差距排序C4/C2/C3/C6/C1/C10。C13 tail gate showed no gain but did not select the newly supplied aligned shape; current resident-frame gate targets its actual assumed route. C4 Cube gate regressed and is archived.用户最新前十快照见[LEADER_REFERENCE_1008](LEADER_REFERENCE_1008.md)，重算均吻合显示分。没有实时榜单/实际SoC/隐藏shape/plan/profile，不凭case号证明新路径命中。

## 最近结束、不能重复的实验

- C3静态M/K/NP及valid-N-only候选 `experiment/tiny-ft-static-frame` /16ce102，任务6ac72eaa694b590c3c97d81d Pass15/15；C3=3.10在父最近五次3.08–3.22内，没有明显收益。全部15点见 [TINY_FT_STATIC_FRAME](TINY_FT_STATIC_FRAME.md)，不重交/扫描附近M/NP/K。
- C4 packed-vector frame候选6abf25e6694b590c3c4a0fa3 Pass15/15但C4=4.43，父4.12，无收益；归档experiment/tiny-tt-packed-frame。此前tiny storage-native/Brcb/K树/K8折叠都无收益，不重做。
- C13完整K/B驻留：a6c5a29正式15.74→15.93，7ffb3ff正式15.28→16.04，均无收益。见 [NARROW_FULLK_PERSISTENT](NARROW_FULLK_PERSISTENT.md) 和 [C13_FRAME_AUDIT](C13_FRAME_AUDIT.md)。
- 大TT交换操作数、full-M N配对、worker Max驻留、nativeNZ ring及库full-K预载均有已归档反例；读各实验正式终态再设计，不能包装为新方向。

## 保留的通过组合

1734f16保留C7/C14手动frame、TT连续tile/frame、C9 packages等此前收益。最近用户额外五次原样复测全部完成且15Pass：6abfc955/6abfca4d/6ac08cd7/6ac08d9c/6ac0d57f；无剩余复测请求。结果 [BEST_IDENTICAL_REPEATS_1002](BEST_IDENTICAL_REPEATS_1002.md)、[BEST_IDENTICAL_REPEATS_1003](BEST_IDENTICAL_REPEATS_1003.md)。C13最近14.94/15.11/15.13/16.74/15.99，中位15.13，波动不能择优删除。

## 执行与交接

先读 [PROBLEM](PROBLEM.md)、[原始验证约定](VALIDATION_REQUEST_v1.md)、[PERF_LOG](PERF_LOG.md)。CANN9/A2或A3，真实容量/核数查询，不假设20核。算法只kernel，不改main/CMake/run/golden/正式测试/依赖、不新增GM，不修改输入/越界y，不跨batch/交换Max与Sum。

Git实验分支、单假设commit/push；main和历史标签不动。CLI由 `/private/tmp/cannjudge_cli.py` 与 `/private/tmp/query_bmmms_submission.py` 复用已保存会话，不读/输出凭据。工具临时文件消失时公开源码从忽略artifacts/tooling/cannjudge-submit恢复；模板其它七文件从1734f16重建。云SSH按用户先不用管。

原CPU日志/JSON只放忽略artifacts目录700、文件600，摘要进Git。较早接手历史见 [10月8日归档](HANDOFF_HISTORY_20261008.md)、[10月2日归档](HANDOFF_HISTORY_20261002.md)；历史PENDING/Running/当前分支不代表现状。
