# 覆盖缺口与工作量调度 · 2026-09-21

## 起点和范围

本分支 `experiment/coverage-splitk` 从 `user-best-20260921` 派生，没有叠加未上板的 dual-consumer-pipeline。三项改变独立提交：Split-K UB 预算、末级输出遍历、自适应 Split-K。算法仍只改 kernel.asc。

这轮检查的是生产分支的边界和约束覆盖，**不是整个 kernel 的行覆盖率，也不是正式 15 点通过率**。设备、输入实际布局和正式日志未提供，以下区分静态发现、CPU 模型和上板待办。

## 已复现的覆盖问题

### 1. Split-K 的存活 UB 分配被少算

`bmmms_dual_split` 的 zerosBuf 与 `FinalizeSplitKND` 的各缓冲由同一 TPipe 分配，进入 finalizer 前未释放。显式存活空间为：

```text
zero buffer       = 2 * baseM * baseN bytes
input+accumulator = 8 * baseM * baseN bytes
row+group maxima  = 4 * baseM * (ceil(N/64)+1) bytes
grouped+output    = 256 + 32 bytes
```

`(B,M,N,K)=(1,112,192,8192)`：旧 host 预算 192,448 bytes，192 KiB UB 会放行；真实显式分配合计 217,120 bytes。这里“真实”指从实际源码 InitBuffer 表达式计算，尚无设备错误日志。新的 classifier 和最终候选检查共同取旧预算与该存活预算的最大值。超预算类不进入强制 Split-K，继续已有通用分块路径。是否能被 CANN tiler 接受仍要上板检查。

测试从源码抽取 InitBuffer 参数，按 32-byte 块对齐计数；86,784 组 M/N/UB 边界配置中，旧 classifier 有 3,328 组放行了超预算分配，新版均拒绝该 Split-K 选择。这里不包含 Matmul 库内部空间；仍由 SetBufferSpace / 真实 SDK tiler 处理。

### 2. 小核数与大 Batch 的输出遍历

- `FinalizeRows`：dual 路径 workers 是 Cube 数，实际两倍 AIV；旧步长会重复写部分 batch。改为按实际 AIV 数跨步。
- `FinalizeSplitKND`：原来每个 AIV 只处理首个 8-batch 组。加入遍历后续组的循环，并复用既有缓冲。
- `bmmms_gemv_vector`：同样只处理首组；按实际 Vector worker 数跨步。

例：B=64、availableCoreNum=1 的双 AIV Split-K，旧末级最多覆盖前 16 个 batch。普通 dual 中同样的核数限制则可能重复 writer。模型编译实际 for-loop 头部验证 28,672 配置：旧逻辑 320 组有遗漏、896 组有重复；修复后每个输出元素恰好一个 writer。统计含抽象 worker 数配置，不能声称每组均由生产 planner 实际生成。

## 论文与优质实现如何影响本轮决策

- [Stream-K，arXiv:2301.03598](https://arxiv.org/abs/2301.03598)：按工作量而非单纯 tile 数组织并行，减少工作分配不均。这启发了本轮最忙 worker 的 K 工作量模型；本轮不是 Stream-K 的完整实现。
- [NVIDIA CUTLASS Stream-K scheduler](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/gemm/threadblock/threadblock_swizzle_streamk.h)：`get_sk_blocks/get_blocks` 同时看工作波次、归并开销；不划算时保留 data-parallel。借鉴“拆分必须值得”的原则，不复制 GPU 的数值代价常量。
- [FlashAttention-2](https://arxiv.org/abs/2307.08691)及[作者说明](https://princeton-nlp.github.io/flash-atttention-2/)：对小 batch 引入额外并行，同时减少通信/非矩阵运算。这里明确区分 N 拆分与 K 拆分：N 分片可以先各取 max；K 分片必须先合并点积，绝不能先取 max。

上述资料通过 Web 核对；Tavily CLI 在前轮不可用，沿用该回退。来源均是一手论文、作者说明或项目源代码。在线 main 分支可能变化，研究日期为本文件日期。

## 自适应 Split-K 候选

只修改原 `ClassifyCase` 中已有的 `K>=4096, 16<=M<=128, N<=256` 且 UB 可容纳的类，不扩大准入范围。

- `BMMMS_ADAPTIVE_SPLITK=0`：保留原固定 4 份；覆盖修复始终保留。
- `=1`（本实验默认）：比较 1/2/4。按现有 32 对齐 K chunk 和循环 task 分派，统计各 Cube worker 的 K 工作量，选择最大工作量最少的方案；平手时少拆。
- 可用 Cube 数来自 `min(availableCoreNum, physical AIC, physical AIV/2)`，不写死 A2/A3 或 20 核。
- 选择 1 时转入已有 full-K dual 路径，保留整个 M/N tile 和一个 N 分片。沿用现有 ring/partial 分配机制，不新增 GM 通路。
- K 合并顺序随拆分数改变，因此 FP32 数值仍须和正式 FP64 golden 比较；CPU 调度模型不是精度证明。

典型代理结果（K=8192、20 Cube）：B=1 选 4；B=8 选 2；B=12 仍选 4；B=20 选 1。B=12 表明“batch 已经不少”不等于应当少拆，必须考虑尾波。

361,152 组 B/K/核数配置与独立逐 task 分派 oracle 比较，208,482 组选择少于 4 份，最忙 worker 的对齐 K 工作量均不大于固定 4 份。平手优先少拆只反映减少 partial/merge 的倾向，没有模型化 L1 复用、库 baseK、启动成本和真实带宽，**不保证更快**。

## 覆盖矩阵和仍未解决的部分

| 生产家族/边界 | 本轮证据 | 待设备覆盖 |
|---|---|---|
| tiny / dot：B<=3、K<=64，四布局 | 既有门限和源码审阅，未修改 | K=40/56、全负、BF16 的真实指令精度 |
| GEMV：M=1 或 N=1 | 输出遍历模型修复 | 转置 Gather、K=72/8192、完整计算与同步 |
| manual / PAD_MN | 保留现有路由 | 不齐 M/N/K=40/72、零填充与真尾块 |
| dual / MDL | FinalizeRows 唯一 writer 模型 | BF16、大 M/N/K、不同可用核心数 |
| split-K | 存活 UB、选择器、最终输出循环模型 | CANN tiling、长 K 精度、SyncAll、实际性能 |
| 输入规模上限 | 提供合法边界 shape 清单 | B*M*K/B*N*K 接近 2^26、8192 维度实机 |

`coverage_cases.csv` 是设备验证清单，不是正式测试替代品。每条都需两种 dtype 和四布局，并记录实际命中的 kernel/plan。不能从 CPU 模型数量推断 kernel 全覆盖，更不能将源码注释中的历史耗时当作新结果。
