# BatchMatmulMaxSum 实验 v1：延后 Max 归约

## 交付与范围

- 工作文件：`kernel.asc`
- 候选 SHA256：`5545fbbd049685852eb9f1e684695a670bc2de40babff0f3697a4b6e9e3bc470`
- 本轮算子改动以用户提供的 2,809 行队友版本为基础，只修改 kernel.asc；后续 GitHub 交接新增文档和独立 CPU 模型。
- 队友原件 SHA256：`5b9d5683b24d9814520f2f7287bbd21f586f803923b1b6dc3f14a894b981586f`，原件保持不变。
- 旧项目 Vector 版本：Git tag `vector-v0.2`，通过 `git show vector-v0.2:kernel.asc` 读取。
- 队友原版：Git tag `teammate-opt4`；差异通过 `git diff teammate-opt4 experiment-v1 -- kernel.asc` 读取。
- 目标：CANN 9.0.0，dav-2201，A2/A3 分别实测。当前环境没有 CANN 编译器或 NPU。

## RESEARCH FINDINGS

1. **FlashAttention-2**：减少非矩阵乘计算和不必要的通信，有助于提高融合内核效率。
   来源：https://arxiv.org/abs/2307.08691
   用途：据此提出本轮自己的 Ascend C 假设——沿 N 的循环只维护分 lane 最大值，结束时再做一次横向归约。论文没有直接给出本轮 Ascend 实现。
   状态：论文结论已核对；在本题的性能收益 UNVERIFIED。

2. **Flash-MaxSim 项目源码**：`tl.dot -> 无效列置 -inf -> tl.max/maximum -> 最终 sum`，并流式处理文档块。
   来源：https://github.com/roipony/flash-maxsim/blob/main/flash_maxsim/flash_maxsim.py
   用途：核对在线 MaxSim 与尾块语义。GPU 上的共享内存路径和性能数字不直接套用到 NPU；其接口包含查询/文档组合，本题仍严格 batch 一一配对。
   状态：源码关键路径 CONFIRMED。

3. **CATLASS Epilogue**：AIC 写阶段化 workspace，AIV 读取并做后处理，以跨核事件控制缓冲复用。
   来源：https://catlass.readthedocs.io/en/latest/1_Practice/07_epilogue_adaptation/
   用途：支持保留当前分阶段 GM 环形缓冲架构；本轮不更换其事件协议。
   状态：文档及代码片段 CONFIRMED；队友内核 CANN 9.0.0 的内部握手仍需实机核对。

## 实现假设

对完整 K 点积得到的有限 C：

    max_n C[r,n] = max_lane max_chunk C[r,64*chunk+lane]

每个 AIV 对负责的行保留 64 个 FP32 lane 最大值。每个 64 列 chunk 用 Max 更新，任务结束时调用一次 WholeReduceMax。N 尾块只更新有效 mask，未访问 lane 保留 -inf。

只接入 `bmmms_dual` / `bmmms_dual_mdl`；split-K、手写 MMAD、微型路径继续使用原算法。N 平均分片宽度不超过 64 时保留旧归约。K 累加、最终 M 求和顺序、GM ring 和跨核协议均未改动。

当一个任务处理 q 个 64 列 chunk 时，横向归约 API 调用由 q 次变为 1 次。**这不是 q 倍加速预测**：lane 状态更大，逐元素 Max 要处理更多数据，初始化及 UB 带宽成本可能抵消收益。

额外状态最多 16 KiB/AIV。最大的 128x256 分块，包含本轮状态与最终归约缓冲的源码显式 UB 分配估算为 161,376 字节，host 保守预算为 169,056 字节；Matmul 内部空间仍由平台查询和 tiling API 约束。

另修复 FinalizeRows 遍历步长：dual 路径 workers 是 AIC 数，实际有两倍 AIV。旧步长在较小核数、大 B 时造成同一输出重复写入。新步长按实际 AIV 数遍历。

## 本地验证

- 新增 C++ helper 直接从工作 kernel.asc 抽取，通过 C++14 普通编译，在 CPU 指令语义模型下执行：2,304 个 N 分片用例、54,828 个有效行最大值与直接 max 逐位一致；包含全负、正负混合、相同最大值、极小有限值、正大数污染无效尾块、零有效行以及状态重复使用。
- 该模型用 CPU 实现 Max/WholeReduceMax 的 mask 和 stride 语义；不验证 Ascend 指令、同步或性能。
- FinalizeRows 调度模型：28,672 个 B/核数/dual 配置全部覆盖且每个输出仅一个 writer；旧步长在其中 1,344 个配置存在重复 writer。
- UB/调度条件模型：5,248 个组合通过，新增分配均不超过预留空间。
- 补充 Python 地址模型覆盖 64/80/96/112/128/160/192/224/256 行跨度：1,728 个分片、41,850 个有效行最大值完全一致，重点检查非 64 倍数 stride。
- C++ ASan/UBSan 可编译，但执行未观察到 main 的首条输出并超时终止；不能报告 sanitizer 通过。普通 C++ 模型执行通过。
- 项目其他 7 个文件的 SHA256 与修改前一致。队友原件不变。
- CANN 编译、NPU 精度、15 个正式 case、latency、msprof：全部 PENDING。

## VALIDATION_REQUEST

**Version:** teammate-derived v1 / deferred Max experiment

**Goal:** 检验延后横向 Max 归约在 CANN 9.0.0 的正确性与真实收益，同时排除 host tiling、缓存热身和设备差异的干扰。

**Changed:** 两条默认 dual-master 路径增加 DeferredRowMax；保留旧归约开关；预留 UB；修复 FinalizeRows 的 AIV 遍历步长。

### Please run

1. 记录精确 SoC、设备/die ID、CANN/驱动版本、AIC/AIV 核数、UB/L1/L0C 容量。
2. 编译三组独立可执行文件：
   - T0：队友原始 kernel.asc。
   - T1：当前 kernel.asc，`-DBMMMS_DEFERRED_MAX=0`。
   - T2：当前 kernel.asc，`-DBMMMS_DEFERRED_MAX=1`（当前默认）。
   T1/T2 的 UB 预算和 host tiling 逻辑一致，适合隔离归约效果；T0 用于检查更大 UB 预留是否改变原版表现。不要开启 BMMMS_TUNING 或启用其他候选。
3. 在独立构建目录，可尝试使用 `-DCMAKE_ASC_FLAGS=-DBMMMS_DEFERRED_MAX=0` / `1` 传入定义；务必通过 verbose 编译日志确认最终 ASC 编译命令实际包含宏。不要修改 CMakeLists、main、golden 或项目测试。外部驱动使用服务器已有的评测 harness。
4. 先跑 15 个正式 case。FP16/BF16、FF/FT/TF/TT、全负、奇数尾块和重复执行均覆盖，使用输入实际存储值的 FP64 golden -> FP32，以及正式评测器。记录最大绝对/相对误差、失败输入和输出；不要放宽容差。
5. 缺少专项覆盖时增加以下外部 harness 用例，tuple 次序为 `(B,M,N,K)`：
   - `(1,129,65,128)`、`(1,129,127,128)`、`(1,129,129,128)`、`(1,129,257,128)`：lane/N 尾部及第二个 AIV 无有效行。
   - `(1,513,511,2048)`、`(2,257,513,2048)`、`(1,1024,2048,2048)`：默认 dual 1/2、N 分片与多窗口；实际路径以 host plan 为准。
   - `(1,17,31,8192)`：split-K 回归；它不使用本轮新归约。
   - `(64,129,129,128)`，availableCoreNum 分别限制为 1/2/4：Finalizer 唯一 writer 与覆盖。
   每个用例覆盖两个 dtype、四种存储布局，并增加全负数据、重复执行。全负可构造 x1 为正值、x2 为负值，确保每个相似度都为负。
6. 精度通过后，以相同输入和同一设备测 T0/T1/T2。每组先预热至少 50 次，再采 200 次，交替顺序重复至少 5 轮；报告设备计时 median/p95，同时单列首次调用与 host 总耗时。workspace 分配和 plan 首建不混入稳定态计时。
7. 打印或从外部调试 harness 记录每个 case 实际 `dual/baseM/baseN/window/nSplit/kSplit/cubeBlocks/deferredMax`，确认 T1/T2 的分块完全相同且目标路径实际开启。
8. 对有收益和退化的代表 case 用 msprof 采 Task Duration、Cube/Vector 利用率、MTE 带宽和可用的流水等待指标。A2/A3 分开比较；如果只能用一种设备，明确另一种仍未验证。A3 条件允许时覆盖不同 die。

### Please return

- 完整构建日志，具体编译命令与内核 SHA256。
- 每个 case 的 shape/dtype/layout/plan、正确性、最大误差、重复一致性。
- T0/T1/T2 的冷启动、median/p95、波动范围和 msprof 摘要。
- 失败时提供 expected/actual、完整 runtime 信息及最小复现。
- 不修改算法或判分逻辑；编译适配所需修改先给出具体 API/header 证据。

## PERF_LOG

| Version | Correctness on NPU | Latency | Cube/Vector/MTE | Interpretation |
|---|---|---|---|---|
| T0 teammate | 待回传 | 未测 | 未测 | 源码注释的性能不是本轮实测 |
| T1 deferred=0 | 待回传 | 未测 | 未测 | 相同 UB 预留的旧归约对照 |
| T2 deferred=1 | 待回传 | 未测 | 未测 | 数学与地址模型通过，收益待验证 |
