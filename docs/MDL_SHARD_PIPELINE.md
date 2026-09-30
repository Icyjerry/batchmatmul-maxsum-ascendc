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

## 正式结果：15/15 通过，无收益

代码 `df0e049`，[正式提交 6abcbaf3694b590c3c353072](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcbaf3694b590c3c353072) **Pass，15/15，precision_ratio 均为1**。CANN9 API编译通过。

| 点 | 最快保留版 μs | MDL shard μs |
|---|---:|---:|
| 1 | 2.14 | 2.09 |
| 2 | 3.96 | 3.99 |
| 3 | 4.56 | 4.34 |
| 4 | 8.08 | 8.39 |
| 5 | 5.31 | 5.45 |
| 6 | 10.58 | 10.44 |
| 7 | 10.15 | 10.36 |
| 8 | 67.80 | 70.86 |
| 9 | 83.95 | 84.55 |
| 10 | 97.84 | 100.05 |
| 11 | 88.16 | 89.29 |
| 12 | 96.97 | 97.37 |
| 13 | 15.83 | 16.85 |
| 14 | 13.20 | 13.76 |
| 15 | 9.20 | 9.70 |

15点合计 517.73→527.49 μs。第8点67.80→70.86、第11点88.16→89.29，没有收益。未获得实际shape/plan/kernel/profile，不能断言命中MDL路由或归因退化；其它点也有单次波动。保留分支对照，不替换最快通过版、不继续相近MDL参数提交。原始JSON在Git忽略 `artifacts/mdl-shard-pipeline/`。下一条研究动作：核对A2/A3 Fixpipe直接到UB能力与Matmul输出交接实现，再判断能否削减现有GM ring通路。整体大幅提升仍未达成。

## 后续源码证据

公开真实tiler驱动80组查询均stepM/N=1，修正原先对手动step1的怀疑；不能称其为已确认缺陷。A2/A3直接L0C到UB方案缺少硬件支持，暂不实现。下一项是大K TT两个M块共享B的K面板，设计仍未实现。见 [INPUT_PIPELINE_REVIEW.md](INPUT_PIPELINE_REVIEW.md)。
