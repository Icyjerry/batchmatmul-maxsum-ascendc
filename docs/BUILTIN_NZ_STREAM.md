# 库内建 NZ 输出 + NZ Vector Max

## 假设与前提

从正式15/15通过但无明显提速的 `experiment/cube-stream-sessions` / `08559b7` 派生，不替换最快通过版。新候选沿用该独立 AIC MatmulImpl，改用 GM NZ C 与顺序 GetTensorC，AIV 直接归约 NZ，尝试减少 Fixpipe NZ→ND 转换；**没有 DataCopyOut callback，没有回调 GM 指针或用户标量传递**。此前三次 callback 的 Runtime Error 不作为该路径的正确性证据。

依据官方 [ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv) `c7dfa2d901a314e1ae69e9cef850057593f2a58b`（8.3.T9.0.B066，非CANN9精确header）：`copy_cube_out_fixpipe.h::CopyOutNZ2NZ<true>` 将 stride 设为 `ceil(validM/16)*16*16*sizeof(float)/32`；`copy_cube_out_utils.h` 按 C format=NZ 选 CFG_NZ，并将 nSize 对齐到16。库内建输出代替了之前自己的 Fixpipe callback；实际可用性以正式 CANN9 编译/运行为准。

## 实现

新 dual=27、`bmmms_dual<T,true,true,STREAM=true,NZ=true>`。生产者对完整Nshard建立一次库会话，逐 C tile 顺序写已有双槽 GM ring，M 物理跨度 ceil(validM/16)*16。两 AIV 分别以二维 DMA 读16列 slab中自己负责的有效行，UB布局为 `[N groups, validRows,16]`，无需转为ND。

N尾列在最后slab置 -inf；跨N groups做树形逐lane Max，最后一次16-lane WholeReduceMax，然后更新任务的行最大值。K全部累加后才做Max；最终Sum和batch一一配对仍用原finalizer。每AIV读取有效行，不读取补齐M行。ring容量、任务、workers、片上预算沿用stream父版；无新GM通路。原ND模板仍保留、默认NZ=false。

host同一准入范围重新查询C format=NZ的实际tiler；拒绝或资源不足回退通过的默认路径，不强行覆写tiling。具体cache/step/性能需要真实plan/profile，不能由CPU模型推出。

## 本地验证

`python3 tools/validate_cube_stream.py`：production/TUNING各96配置，包含pins和新tiler拒绝回退；实际producer、DMA、tail-mask、tree-Max代码分别在ND/NZ mock运行各432配置，比较点积→Max→Sum独立oracle。新增128×128tile、完整/零有效AIV行、非对齐M/N、跨batch和全负；NZ无效列特意写巨大正值，验证不能污染最大值。模型验证stride/槽位/结果，不仿真CANN内部布局或事件时序。

**CANN9编译、正式15点与NPU性能 PENDING**。正式模板仅替换kernel.asc，dry-run确认SHA后提交。若故障则保存完整日志，不能猜测根因；若无收益，不继续相近布局参数微调。

验证输入：BF16/FP16 TT `(1,1025,1537,1032)`、`(1,1536,1536,1536)`、`(1,1537,3073,3072)`，全负/正负/重复执行。确认dual=27和actualkernel，记录具体SoC、CANN、tile/step/cache、最大误差、median/p95和Fixpipe/MTE/Vector/Cube profile。
