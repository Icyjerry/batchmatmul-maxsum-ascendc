# 独立 MDL K 面板流水 · 2026-09-30

## Evidence → Diagnosis

当前较快通过版为 `568f4eb` / kernel SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。此前独立 Norm 长会话和 GM NZ 输出均正式 15/15 通过，未形成整体收益。本候选针对 **输入 K 面板加载**，不继续输出格式参数变体。

官方[MDL 调优案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900beta1/opdevg/Ascendcopdevg/atlas_ascendc_best_practices_10_10009.html)说明 Norm 每次搬运一个基本块，MDL 按 `stepM*stepKa` / `stepN*stepKb` 成组搬运并复用。该页面案例的加速比不能套用到本题。

本机官方公开源码 `ascend/ascendc-api-adv`，commit `c7dfa2d901a314e1ae69e9cef850057593f2a58b` / `8.3.T9.0.B066`，**不是 installed CANN9 header**：

- `lib/matmul/matmul_tiling_base.h` 默认 `mmConfigType=1`（MDL）。当前通用 host 查询没有指定类型，随后强制 `stepM=stepN=1`；Norm kernel 不按 MDL K 面板处理。不能据此直接断言原计划错误或一定退化。
- `scheduler/base/scheduler_mdl_base.h` CopyIn 使用 KLoop 的 tileShapeA/B，SplitA/B 再拆分成 L0 baseK；`scheduler_mdl_common.h` 在 ReduceKOneIter / ReduceKMultiIter 中完成整个 K 后才返回一个 C tile。
- `scheduler/iterator/n_loop/n_loop_mdl_base.h` 与 MLoop 管理内外层分块；当前每个任务只有一个 M tile，所以逐 Iterate 的 C 顺序就是 N tile 顺序，无需交换输出顺序。
- 官方 K reorder 示例建议 K>=4096 且 A/B 非全载。此候选不启用 reorder，避免把累加次序改变混入输入流水假设。

## Minimal Fix

从较快通过版派生 `experiment/mdl-shard-pipeline`，复用此前正式通过的独立 AIC stream engine：

1. TT、B=1、M/N/K>=1024 的原 dual=1 完整K任务，在 N shard 至少两个 tile 时重查整个 shard 的 tiling。
2. 显式 `SetMatmulConfigParams(1)`，独立 `MatmulImpl` 使用 `CFG_MDL`，保留新查询的 step/depth/baseK/DB。没有手动伪造这些参数。
3. 每个任务只 SetTensor/SetTail 一次；每次 Iterate 完成 K 累加，GetTensorC 顺序写旧 ND 双槽 ring。AIV按实际有效列 stride 读取尾块。
4. 保留原 baseM/baseN、nSplit、worker 和 finalizer；没有新输入预打包 GM 通路。AIV不创建 KFC client。查询失败或显式 TUNING pins 回退旧路径。

候选 kernel SHA `9cf72c174b5ef077db5e8c06826df39718fe926d10efc86391f88e6a5359751e`。

## Validation

- `python3 tools/validate_cube_stream.py`：production/TUNING 各96个路由配置；384个抽取实际 producer / 紧凑 ND consumer 的独立计算 oracle 配置通过。覆盖尾块、零有效行、全负、污染无效 padding。
- Host stub 记录显式 MDL query，注入非单位 stepN 并确认未被改写；这是控制流模型，不模拟真实 tiler。Producer mock 不实现库内部 MDL cache/浮点舍入/异步依赖。
- `git diff --check` 通过。
- CANN9 编译、NPU 15点、性能：PENDING。
- 精确SoC、隐藏shape、实际plan、msprof、重复测量：PENDING。

## Validation Request

使用 CLI 下载原正式模板，只替换 kernel.asc，先 dry-run 再正式提交。对照最快通过版及之前独立 Norm stream 的逐点耗时；只有整体明显改善且15点全过才保留为较快起点。无收益则恢复较快通过版，保留本分支、提交ID和逐点记录。
