# 最新接手状态 · 2026-10-08

## 当前代码与正式任务

- 当前分支 `experiment/c13-manual-frame`；父算法为正式通过组合1734f16/a5eef105/354602bytes。C13候选kernel365034bytes/SHA `92c3654faef7db189c167846215a96ab0dcf937b0833ef36b90f8b35d3158d28`，191行/三处新增，仅算法kernel.asc。
- 固定物理frame/事件替换dual14 FF尾块的TPipe/TQue，保留128深双K panels、原M任务与双C/ring/early partial。简化完整N后的64行sum和barrier后末级frame。不是再次完整K/B驻留。详情 [C13_MANUAL_FRAME](C13_MANUAL_FRAME.md)。
- CPU324组producer/六项负控制、768组Vector/九项负控制、production/TUNING各4096host/3968准入与容量/core/workspace/回退通过。whole-parent scope和七个保护工程文件通过。CPU不是FP16/CANN/硬件时序模型。
- CLI登录已恢复；独立模板 `/private/tmp/bmmms-c13-frame-official/project` dry-run确认仅kernel/SHA一致。**当前无正式任务ID，CANN9/正式精度/性能PENDING**。
- 下一：commit/push候选后一次正式结构提交。立即保存ID并push，查同ID至真实终态，完整15点及新参考计分；明显大收益才原样确认，否则归档，不扫描附近参数。整体冲榜目标未完成。

## 最新计分参考与差距

用户最新Tbest：`[1.18,1.54,2.13,2.37,3.57,6.38,6.37,13.88,48.30,64.85,67.87,80.65,7.31,7.59,7.84]`μs。用 [SCORE_REFERENCE_1008](SCORE_REFERENCE_1008.md)，100/(1+log_1.5(t/Tbest))后15点平均。用户榜首Young耗时重算82.15390，与82.15一致；通过版最新6ac0d57f重算50.99873。旧56.42050/50.x分数均属各自旧参考，耗时/精度未改。

相对用户提供的最新榜首行，最近五次同SHA逐点中位差距排序C4/C2/C3/C6/C1/C10。C13候选已进入可验证阶段，本次完成其唯一结构 gate；后续按新优先级。没有实时榜单/实际SoC/隐藏shape/plan/profile，不凭case号证明新路径命中。

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
