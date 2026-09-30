# 独立 AIC 库会话 + C tile 流水

## Evidence → Diagnosis

从通过版 `experiment/manual-splitk-tiny` / `11de38b` 派生。此前手写 TT 常驻退化，Matmul 外层移除 End 无明显收益；不再重复相近变体。

核对官方 [ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv) commit `c7dfa2d901a314e1ae69e9cef850057593f2a58b`，`version.info=8.3.T9.0.B066`，**不是已安装 CANN9 的精确 header**：

- `impl/matmul/kfc/matmul_server_aux.h`：dual-master `IterateAll` 调用底层 `mul.End()`；外层 `End()` 是空实现。该源码说明此前移除外层 End 不能消除内部 End，修正旧实验的缓存保留假设。
- 同文件禁止 dual-master LocalTensor A/B、逐 tile Iterate/GetTensorC。不能直接在旧 wrapper 添加 TSCM 或逐 tile API。
- `impl/matmul/stage/copy_cube_in/base/copy_cube_in_norm.h`：SetInput 清缓存；`resource/cube_in_buffer/cube_in_buffer_normal.h` 支持 K tile 缓存。Scheduler 在结束 N/M loop 或 End 时清理缓存。
- `lib/matmul/matmul_intf.h` 的 CUBE_ONLY Matmul 是 MatmulImpl 别名。官方 `examples/matrix/matmul_splitk/op_kernel/matmul_splitk_custom_impl.h` 直接实例化 MatmulImpl 并调用 Init(tiling,pipe)、SetSubBlockIdx(0)。本实现只在新 AIC 模板内选择该 engine，没有全局定义 CUBE_ONLY 改变旧 kernel。
- `copy_cube_out_fixpipe.h`：GetTensorC sequential mode 写当前目标起点，ND stride=当前 baseWidth，包含紧凑 N 尾块；消费者按实际 cols 读取。

官方 CANN9 的 [WaitGetTensorC](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0659.html) 和 [AsyncGetTensorC](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0661.html) 同样声明双主模式限制。具体 MatmulImpl 编译、顺序写尾块与跨核行为仍须正式编译/运行确认。

## 实现

`bmmms_dual<...,STREAM=true>` 让每个 M tile / N shard 只设置一次 A/B，使用独立 AIC CFG_NORM engine 对整个 N shard 连续 Iterate/GetTensorC。计算下一块 C 可在等待 GM 槽位前进行；每块 C 顺序写入现有双槽 ND ring，再沿用原 AIV Max 与 finalizer。库会话结束一次/任务，而非每输出 window 一次。AIV 没有 KFC client，也不发送 flag9 启动消息。

仅替换现有 dual=1、完整 K、B1 TT、M/N/K≥1024，且每个 N shard 至少两 tile 的计划。保留 tile、nSplit、workers 和任务归属，重新查询库 tiler：singleCoreN 为最大 shard 宽度，singleCoreM 为一个 M tile，K 完整；资源或 tiler 拒绝、显式 pins 时回退父路径。window=1 表示逐 tile 交接，GM ring 缩小；无新增 GM 通路，没有引入此前失败的 NZ callback。

对源码已有的 20 核 measured plan：1536³ BF16 TT 的任务/会话数为原 36/72 → 新 36/36；1536×3072×3072 FP16 TT 为原 60/168 → 新 60/60。这些是调度调用次数，不是实测速率。库缓存量和性能取决于正式 tiler、输入和设备；不能宣称 A 从 GM 只读取一次。

## 本地验证

- `python3 tools/validate_cube_stream.py`：production/TUNING 各 96 个 host 路由/workspace 检查，包含新 tiler 拒绝回退和显式 pins；fake tiler 不是 CANN。
- 抽取实际 streaming producer、consumer DMA/WholeReduceMax/Max 代码，在 CPU mock 执行 384 个配置，比较完整点积→Max→Sum 独立 oracle；覆盖紧凑 ND 尾块、多任务、不同 worker、N shard、batch 一一配对、全负输入、GM 槽位边界。mock Matmul 不证明库内部缓存、事件或数值误差。
- `validate_manual_splitk.py` 48 组、`validate_direct_batch.py` 1,458 个既有模型回归通过。
- **CANN 编译、正式15点、设备精度/性能 PENDING**。

## 正式验证

CLI 下载独立正式模板，仅替换 kernel.asc，dry-run 确认上传 SHA 后提交结构候选；记录同一 submission 至终态。若失败/退化，保留分支并恢复通过版，不用相近小参数变体重复提交。

设备专项：BF16/FP16 TT `(1,1025,1537,1032)`、`(1,1536,1536,1536)`、`(1,1537,3073,3072)`，全负、尾块、重复执行。输出精确 SoC/CANN、dual=26、tile/step/cache depth、ns/workers、median/p95 和 Cube/MTE/Vector profile，与父版交替同设备对照。
