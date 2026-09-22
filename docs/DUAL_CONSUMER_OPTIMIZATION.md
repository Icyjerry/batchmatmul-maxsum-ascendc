# Dual 消费流水与 tile Max · 2026-09-22

## 实际实现

父版本 `35a86eb`，分支 `experiment/dual-consumer-fold`。`324a6a0` 移植已有独立流水实验，`00a91b4` 新增 tile 内树形 Max；代码只修改 `kernel.asc`。

1. `CopyDualTile` 保留原 DMA 地址与尾部填充，利用已分配的两个 UB tile，在归约当前 tile 前排入下一 tile 的复制。
2. `ConsumeDualWindow` 在窗口最后一次 GM 读取发出后，排入 `PIPE_MTE2` release；通知在读取完成后才生效。剩余归约只读私有 UB，因此 Cube 可复用 GM 槽位。原有 wrapper 下一次握手也提前。零有效行的 AIV 保留每个窗口的 ready/release。
3. `ReduceDualTile` 在当前 UB tile 内树形合并 64-lane 分组，再做一次横向最大值。例：256 列先分别合并 0/64 和 128/192 两组，再合并 0/128，最后 WholeReduceMax。每层屏障一次；非对齐尾组只更新有效 lane。

没有新 UB/GM 分配，未增加输入搬运字节；不更改 AIC 矩阵乘、K 累加、host tiling、partial 布局或最终 Sum。仅完整 K 的 `bmmms_dual`/`bmmms_dual_mdl` 进入 helper；split-K、tiny、manual 不进入。输入 dtype/layout 在产生 FP32 C 之前已处理，仍需完整入口的设备精度验证。

每个非空 tile、AIV rows≤64 的源码调用计数：

| 有效列 | 原 WholeReduceMax | 新 WholeReduceMax | 原/新 Vector 屏障 | 原/新 Max+WholeReduceMax 合计 |
|---|---:|---:|---:|---:|
| 1..64 | 1 | 1 | 2 / 2 | 2 / 2 |
| 65..128 | 2 | 1 | 4 / 3 | 4 / 3 |
| 129..192 | 3 | 1 | 6 / 4 | 6 / 4 |
| 193..256 | 4 | 1 | 8 / 4 | 8 / 5 |

更少的指令调用不保证更短耗时。新 Max 操作处理更多 lane，可能增加 UB 带宽压力；若瓶颈在 AIC 输入读取、分块或矩阵计算，消费侧收益可能有限。仅一块的窗口没有窗口内预取机会。提前释放的实际收益受 Matmul wrapper 内部同步约束。

## 依据与适用边界

- [FlashAttention-2](https://arxiv.org/abs/2307.08691)：减少非矩阵乘开销和同步通信的设计方向。这里的树形 tile Max 是本项目实现，论文不提供该 Ascend 内核或收益预测。
- [CATLASS epilogue](https://catlass.readthedocs.io/en/latest/1_Practice/07_epilogue_adaptation/)：此前独立流水实验的 AIC/AIV 分阶段后处理参考。本次移植该已保存实现，没有复制外部新代码。
- [Ascend Max 官方文档](https://www.hiascend.com/doc_center/source/zh/canncommercial/800/apiref/ascendcopapi/atlasascendc_api_07_0039.html)：核对 FP32 mask≤64、32字节地址对齐、repeat stride 和地址重叠约束。当前 Max 的 dst 与 src0 完全同址，src1 的有效组不与 dst 相交，各 repeat 属于不同的行，没有跨 repeat 数据依赖。文档是8.0资料，不冒充9.0编译证据。
- [CrossCoreSetFlag 文档](https://asc.gitcode.com/api/SIMD-API/basic_api/sync_control/inter_core_sync/CrossCoreSetFlag_ISASI.html)：核对指定 pipe 的前序完成依赖及 mode2 的一AIC/双AIV配对。该站是开发版本，仍以目标 CANN9 header/运行结果为准。

## 本地验证

运行 `python3 tools/validate_dual_pipeline.py`。从当前 kernel 抽取 helper，以父提交原循环为对照，编译六种宏组合。每组：

- 76,800 个窗口配置：N偏移、长短窗口、两个slot、两侧AIV、0行/尾行、全负/混合/相等值、已有行最大值。检查 GM 读取地址、最多两个活跃UB块、释放与握手次数、结果。
- 34,816 个直接归约配置：baseN=16..256每16一档，cols=1..baseN全部取值，rows=1/7/32/64；覆盖末列最大、全负、小有限数、旧最大值获胜、无效列及行的大正数污染，同时检查调用计数。
- pipeline=0/fold=0 的CPU指令轨迹与父循环一致；fold=0 各模式Vector顺序一致。逆替换helper后，其余源码必须与父版本完全相等。
- 另有3,840个一AIC/双AIV抽象调度检查槽位读取完成后才覆盖、同步计数及终止。

这是语义与地址模型，**不是 CANN emulator**。DMA按队列完成依赖执行、Vector算术在CPU同步执行；不证明真实并行、Matmul内部flag9行为、编译器或缓存一致性。设备全流程精度仍 PENDING。

## 云端恢复后的执行单

用户当前暂缓云端执行。恢复后直接使用服务器已有 harness，无需重新设计算法，也不修改 main、CMake、run.sh、golden。

构建同一源码的六组 `BMMMS_DUAL_PIPELINE={0,1,2}` × `BMMMS_DUAL_FOLD_MAX={0,1}`。默认2/1只是候选。编译日志核对宏实际生效，诊断probe宏保持0，记录其它宏（包括 inherited NSPLIT/SPLITK）并在所有组固定；勿开启TUNING改变生产测试分支。

1. 记录 kernel SHA、commit、精确SoC、CANN/驱动、AIC/AIV数量、UB/L1/L0C、编译命令和每个case实际plan。A2/A3分开。
2. 六组先跑正式15点完整精度，再跑专项 FP16/BF16 × FF/FT/TF/TT。使用实际输入存储值FP64 golden→FP32，正式容差，全负与普通数据，重复执行一致性。
3. 专项 `(B,M,N,K)`：`(1,513,511,2048)`、`(1,1023,513,512)`、`(2,257,513,2048)`、`(16,512,512,512)`、`(1,1536,1536,1536)`、`(1,3072,1536,1536)`、`(1,1024,5120,1024)`、`(1,129,65,128)`、`(1,129,129,128)`、`(1,129,193,128)`、`(1,129,257,128)`。先打印plan确认进入目标dual路径；未进入不能当helper覆盖。
4. 队友推测的15点shape不等于正式输入；优先实测正式点，已有 `known_issues_cases.csv` 可做继承修复的扩展覆盖。若生产选择未覆盖dual=2或非64倍数baseN，可用独立TUNING专项对照强制选同一合法plan，单列结果，不混为生产成绩。
5. 精度通过后，预热50次、设备计时200次，交替顺序至少5组，报告median/p95与波动。首次分配/plan建立耗时单列。
6. 比较0/0→1/0（预取）、1/0→2/0（提前归还）、0/0→0/1（归约）、2/0→2/1（组合中的归约），1/1用于区分组合效应。选择改善与退化case采msprof，分别报告AIC和AIV指标，尤其Task、MTE2、Vector、Cube等待。
7. PENDING关卡：CANN9能否编译、真实队列同步、VECIN原地Max的设备结果、flag9协议、六组完整精度和性能。失败保留输入/输出/错误及构建SHA；收益未确认前不合并main kernel。
