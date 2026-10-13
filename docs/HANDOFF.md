# 当前工作：C4 完整 native 分析，C12 候选已归档

## 当前源码

- 分支 experiment/c4-compact-k128。恢复整份 e2f1b63 / 队友 ZIP078635，353179B，七个受保护文件未动。
- C13 fullK（520f27d）和 C12 strided store（b159f99）均未获明显收益，保留历史分支，不并入 main、不提交 OJ、不重复采样。
- ZIP078635 与 DISPATCH 接受源 b8817327 不同，不得把后者正式 Pass15/401.13us成绩借给当前源。

## 已完成的设备证据

- 服务器9382，实际24AIC48AIV，CANN9.0.0/driver26.1.1，logical0→physical14/card7chip0，core_limit20是明确调用者预算。
- 独立 native_oj_like 工具在私有可写 /workspace/bmmms-codex；完整实际storage FP64参考、normalPlan复核、五应用调用/全部默认报告/source-DSO-input-device绑定。原main/CMake/tests/shared_assets未修改。
- C12 BF16TN(1,1280,4096,1536) 原版83.123322us，strided store82.683304us，仅-0.53%；实际写回指令减少2688条仍不提速。详见 C12_STRIDED_PREP_STORE / PERF_LOG，raw artifacts/c12-strided-prep-store。
- C4 BF16TT(4,8,16,128)，实际 Launch先选 SmallVectorK256Rows=8，跳过较晚dual28入口。原版完整精度+五性能输出通过，原normalPlan dual28/workers4/finalBlocks4/cubeBlocks0。
- 五报告 actual纯Vector4、0Cube、符号small_vector_k256<BF16,true,true>，TaskDuration[2.980119,2.940118,3.120125,3.060122,3.360134]us，median3.060122；AIV各核均值五次中位V1.46/MTE20.419028/MTE30.149167/Scalar0.721806us，重叠不可相加。
- C4首次parser因纯Vector的MixBlockDim=NA退出1；修正只读schema后对同一组五报告重解析，完整性通过，保留原错误和全部样本，没有重新跑或挑选数据。

## 下一条动作

C4 distinct compactK128方向：实际产品目前128lane/点，先两片Mul再Add，完整K后才maxN。用32KiB的64lane/点状态，先Mul低64，再MulAddDst累加高64，原Cast/Gather/归约顺序和完整输入保留，仅合法BF16TT公开(4,8,16,128)入口启用。先actual helper CPU地址/精度/默认false回退/逆补丁，CANN9真实vmla API核对，然后native同输入全golden+五报告；采前门槛至少20%（<=2.4480976us）才继续正式提交准备。候选尚未编译/验证，不能称加速。

## 工具与交接

- SSH私有配置/private/tmp/bmmms-remote-access/config/master23895/foreground exec13910；无凭据入Git。实际状态用ssh -O check检查，授权凭据有时限。
- native工具/DSO/完整frame/inputs/reports在 /workspace/bmmms-codex/native_oj_like 和inputs；private NumPy2.2.6 Python test-venv/bin/python。
- 真实NPU文件锁及active/pending队列，当前无活动NPU任务。GitHub已授权私有仓库；push当前实验分支，不改标签/main。
- 未验证：当前源正式15点、另一SoC、ZIP与接受源绑定。无新OJ请求。整体冲榜目标未完成。
