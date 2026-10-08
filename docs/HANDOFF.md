# 最新接手状态 · 2026-10-08

## Current C11 experiment

- Branch experiment/c11-exact-tt-frame from retained60ba0d7/C13 source7492776. Candidate365998bytes/SHA4ce9ab293b8a24b80a3741f8195ccee217856a5b9c0d330404fa7013f5c7300d. Only34 host/Launch additions; device TT entry and C13 gain intact, whole-parent inverse proven. Exact supplied C11 shape with historical FP16/TT assumption; original workspace unchanged.
- Actual source CPU models: production/TUNING2592plans each/four hits, six physical full-K Cube proxy groups/six rejected controls, sixty full-M/N threaded AIV groups/seven rejected controls. No native precision/performance claim; see [C11_EXACT_TT_FRAME](C11_EXACT_TT_FRAME.md).
- NEXT: protected-template/dry-run and one formal gate, save ID then query same ID to terminal; clear substantial gain only warrants one confirmation. No C11 formal ID yet. Retained C13 remains fallback baseline, main/tags untouched.

## Previous retained C13 baseline and assessment

## Current retained code and next executable action

- Current experiment/c13-resident-frame, kernel364169bytes/SHA0794a2bfc777ac48c373b3085cd96fd1224b0bf0a4f6a9351d290bb421dbad2d, implementation7492776. Parent1734f16 +threeadditions178lines only; C4regression/oldC13tail excluded.
- Formalfirst6ac73bd0694b590c3ca19b3d andoneunchangedconfirmation6ac73c8b694b590c3ca2153b bothterminalPass15/allprecision1. C13=12.62/13.19, bothbelowparentrecent14.94-16.74/median15.13; pairmidpoint12.905 (-14.71percent vsparentmedian), sloweststill11.71percent belowfastestparent. Retainlocalizedgain, notwholecompetitionbreakthrough orstablecausal A/B. Full15/totals/scores in[C13_RESIDENT_FRAME](C13_RESIDENT_FRAME.md).
- Noactiveformaljob, nofurtherrepeatrequests. OriginaloneBload/L0residence/fullK128/stridedM/doubleC/workerpartials/originalGM retained, frameworkandVectorredundancyremoved. Nativecompile/15precision passed; allshape/profile/SoC coverage notclaimed.
- NEXT independentbranchfromthisretainedhead: C11 exact(1,1536,2048,2048), historicalFP16/TT, originaldual2/BM128BN256/Nsplit8. ExistingTTframecanuseBM64BN256/BK64, existingpartialprefixidentical49152B/ringhalfsize withinoldallocation. Add onlynarrowactualhost/Launch route, retaindevicecodebyteforbyte; verifyresources/plan/pins andactualsourcephysicalmodelsbeforeoneformalgate. Detailedmemoryarithmetic/risks/steps[C11_EXACT_FRAME_AUDIT](C11_EXACT_FRAME_AUDIT.md). Unimplemented, noC11jobyet. Do notblindlywidenthegeneralTTguard.
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
