# N 拆分：减少最忙 worker 的 tile 数

分支：`experiment/n-split-critical-work`，父提交 `8fb1e72`。本轮只增加一个调度假设，继承 coverage 分支的 UB/输出修复和 long-K 选择器，没有混入消费流水实验。

Kernel SHA256：`e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。

## Evidence → Diagnosis

队友 `docs.zip / docs/10-tiling-opportunity.md` 报告同 capture 的旧构建结果：

| shape (B,M,N,K) | 原计划 | dual=1, bn128, ns3 |
|---|---:|---:|
| (1,1536,1536,1536) | 70.49µs | 53.39µs |
| (1,3072,1536,1536) | 126.46µs | 92.14µs |

这两行不是当前源码的实测，也不足以直接硬编码 ns3。当前 planner 的非 MDL 均衡规则要求 `workers1 >= 2*workers0`，因而当原计划已占满所有核心时，即使任务尾波很不均匀，也不会调整 N 拆分。

以 20 个 Cube、baseM/baseN=128、原始 window=8 为例：

| M/N/K，B=1 | 原 ns | 候选 ns | 最忙 worker tile 数 | 最大窗口数 | 最终 window |
|---|---:|---:|---:|---:|---:|
| 1536/1536/1536 | 2 | 3 | 12→8 | 2→2 | 6→4 |
| 3072/1536/1536 | 1 | 3 | 24→16 | 4→4 | 8→4 |

这是给定计划条件的 CPU 计数。实际硬件可能产生不同 tile/family，必须记录最终 plan。不能把少 1/3 tile 工作直接称为少 1/3 时间。

## 论文经验与本轮实现

[Stream-K 原论文](https://arxiv.org/abs/2301.03598) 用工作量分配缓解固定 tile 划分的资源利用问题。本轮借鉴其关注实际 worker 工作量的思路；实现仍沿 N 分片，完整 K 点积先完成，再归约 Max。没有移植论文的 GPU 协议或使用其加速数字。

`NPartitionWork` 模拟当前 bmmms_dual 的真实循环：

- tasks = B × mTiles × nSplit，worker 循环步长是实际 min(core cap, tasks)。
- ns = task % nSplit，N 分片为 `[floor(ns*nTiles/nSplit), floor((ns+1)*nTiles/nSplit))`。
- window 随拆分按现有逻辑裁剪；累加每 worker 的 tile 数和窗口数，分别取最大值。
- 枚举所有合法 ns。只接受最大窗口数不超过原计划的候选；先最小化最大 tile 数，再最小化最大窗口数，再选择更少的 ns。
- 最终只有最大 tile 数至少下降 25% 才替换旧计划。**25% 是本次实验的准入假设，不是测得的最优阈值。**

当前范围限定：通用 dual=1、kSplit=1、baseM/baseN=128、M≥1024 且 M/N 均128对齐、1024≤N≤2048、1024≤K<2048。排除 case profile 强制路径、已有 ns pin 和显式 tile/window/core/K-split tuning pins。物理核数仍来自当前 platform；不假设固定20核。

`BMMMS_BALANCED_NSPLIT=0` 保留父版本计划；`=1` 启用候选（该实验分支默认）。不增加新的 kernel、输入重排或 GM 通路；沿用已有 partial/ring 的动态尺寸计算。N 拆分可能增加 partial 数量，不能称为零额外带宽。

## Validation

`python3 tools/validate_nsplit_work.py` 抽取当前源码 helper 和 planner 接入块，用独立的逐 tile 归属 oracle 对照循环计数。

- 38,880 个调度配置；8,893 个配置满足候选准入（**不是实际合法 shape 的命中率**）。
- 1,836 行全负数据检查 N 分片完整、唯一覆盖以及 partial max 合并结果。
- 宏0、宏1、宏1+TUNING 三种编译各自通过；14 个范围/路径排除条件、5 种显式 tuning pin 检查通过。
- 继承的 UB 模型 86,784 配置、输出模型28,672配置、自适应 K 拆分361,152配置与864个classifier配置再次通过。
- CPU 模型不执行 K 点积、真实 Matmul tiler、CANN 指令或事件同步，不替代完整数值验证。
- **CANN 编译、NPU 精度、正式15点、耗时和 msprof：PENDING。**

## 仍需设备回答

1. 更多任务的 partial max 写回与最终归约，是否抵消更均匀的 Cube 工作？同 worker 的最大窗口数不增加，不代表全设备总窗口数不增加。
2. 较窄的单次 Matmul 窗口是否减少 A 复用，改变 L1/MTE2/FIX 效率？模型没有假装知道这些时延。
3. 现有 tiler 先按原 window 生成计划，再由 schedule 裁剪实际宽度；此候选沿用原代码机制，需确认实际 window/尾部/布局在 CANN 9.0.0 的行为。
4. host 搜索仅发生在 shape plan 构建时；本范围 nTiles≤16，最多约13.1万次 task 计数/plan。需要分别记录首次 host plan 成本与稳定态设备耗时。

按 [设备验证单](VALIDATION_REQUEST_nsplit_work.md) 执行。未完成上板对照前不合并 main，也不叠加下一项算法优化。
