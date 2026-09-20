# 接手状态

更新日期：2026-09-20。此文件与 Git 中的代码、验证单一起足以独立接手。

## 当前最重要的结论

- `kernel.asc` 已基于队友版本实现实验 v1 + wave-balance 调度优化；不是最初的 Vector fallback。
- **本轮已完成真实 NPU 编译与精度**：T0/T1/T2 三组在 910B3 / CANN 9.0.0 上均 21/21 通过
  （自建多 case harness，含 FP16/BF16、FF/FT/TF/TT、全负、K 跨 tile、多 batch）。
- **deferred Max（T1 vs T2）实测收益约 ±7% 以内、多数为噪声，未观察到预期加速。**
  真正瓶颈是 cube wave 未填满和 64 行 tile 的 B 重载。
- 当前候选为 `experiment/wave-balance`：只改 host plan，实测 1.16–1.58x（多个 shape），
  大 dual==2 与转置布局中性。详见 PERF_LOG。
- 覆盖度检查发现默认构建有 8 个策略 kernel 不可达（占设备码 59%）；已用
  `#ifdef BMMMS_TUNING` 包住，设备 ELF 1.69MB→0.71MB（−58%），性能中性；
  并为 dual==2 / kSplit>1 补了覆盖 case（36/36）。详见 COVERAGE.md。
- **正式 15 个 case 与官方评测器仍未运行**（本地只有自建 harness，不是官方判分）。
- CANN 9.0.0，A2/A3 均可能；不要把任一设备的最佳参数未经验证推广到另一种。
- 用户当前要求把项目放到 GitHub 并用 Git 保留交接信息。仓库现已公开。

## 已完成

1. 审阅队友 2,809 行实现：默认 dual-master Cube/Vector、GM ring、N/K split、小形状专用路径、host plan/cache。
2. 研究 FlashAttention-2、Flash-MaxSim 源码和 CATLASS epilogue。来源、采用/未采用内容见验证单。
3. v1 在 `bmmms_dual` / `bmmms_dual_mdl` 接入 DeferredRowMax：每行 64 lane 最大值跨 N chunk 累计，末尾一次 WholeReduceMax。
4. 保留 `BMMMS_DEFERRED_MAX=0` 对照，0/1 两组的 UB 预留与 host tiling 逻辑相同。最多新增 16 KiB/AIV。
5. 修复 FinalizeRows 中把 AIC worker 数误用为 AIV 遍历步长的问题。
6. CPU C++ helper 模型 2,304 个分片、54,828 个有效行最大值逐位一致。Python 补充模型、任务覆盖与 UB 预算结果见 PERF_LOG。没有 NPU 结果。
7. **[wave-balance, 2026-09-20]** 910B3 实测：T0/T1/T2 各 21/21 精度通过；msprof 证明
   `(1,513,511,2048)` 只跑 5/20 block、cube util 24%。三项 host-plan 修复：dual==1
   wave 填充、shape family `tuneM` 64→128、小 K 走 dual==2 避开全 C fixpipe；加
   `BMMMS_DUMP_PLAN`。实测 1.16–1.58x（见 PERF_LOG），转置与已调优的多 split 形状经
   gate 后保持中性。

## 下一条具体动作

**有 NPU 环境：**把 `experiment/wave-balance` 与 T0/T1/T2 在同一 harness 上跑
`BMMMS_DEFERRED_MAX=0/1` 完整 A/B，并对有收益/退化的代表 case 采 median/p95 与 msprof；
重点确认 `(1,513,511,2048)`、`(1,1023,513,512)`、`(1,1024,512,256)` 的收益可复现，
以及 `BMMMS_TUNING` 分支（env：`BMMMS_BM/BN/NS/DUAL/WINDOW/WORKERS`）覆盖更多 shape。

**只有本地开发环境：**运行 `python3 tools/validate_cpu_model.py`，检查 Git 状态和验证资料；
不要凭 CPU 计时修改分块策略。

T0/T1/T2 差异：

| 版本 | 源码/宏 | 对照用途 |
|---|---|---|
| T0 | teammate-opt4 | 原版性能与精度 |
| T1 | 当前代码，宏=0 | 相同 UB 预留的旧归约 |
| T2 | 当前代码，宏=1 | 新归约效果 |

收到结果后先看：是否真的进入 deferredMax 路径；T1/T2 plan 是否相同；增益是否超过运行波动；UB 访问开销是否抵消横向归约收益。若有退化，用实测筛选启用条件，而非全局宣称优化成功。

## 风险与明确未完成项

- 整个 kernel 尚未在本轮 CANN 9.0.0 编译。特别保留的内部 Matmul/跨核握手需真实 header/日志验证。
- 本地 ASan/UBSan 版本可编译，但未观察到 main 首条输出就超时；不能报告 sanitizer 通过。普通 C++ CPU 模型运行通过。
- 既有 run.sh 只跑 main 中固定的单点积样例，不覆盖新算法；它不是正式 15-case harness。
- 队友源码注释的历史耗时未复现；许多手写 MMAD/GEMV 候选并非默认启用。
- `release_kernel_resources` 是可选 helper；正式 harness 的 stream/context 生命周期需要检查，避免旧缓存影响测试。此轮未改缓存策略。
- workspace 规则历史与题面丢失的数值范围见 PROBLEM。
- 该候选只重排 Max，对正负零的位模式和设备 denormal 行为仍以实机为准；最终 Sum 顺序及 Cube 算法未有意修改。

## 快速定位

```sh
rg -n 'DeferredRowMax|deferredMax|finalWorkers|BMMMS_DEFERRED_MAX' kernel.asc
git diff teammate-opt4 experiment-v1 -- kernel.asc
```

历史 tag 保留各版原始 kernel 字节。当前 v1 kernel SHA256：
`5545fbbd049685852eb9f1e684695a670bc2de40babff0f3697a4b6e9e3bc470`。

## 持续维护

每次继续工作前读此文件和 PERF_LOG。结束前写清改动、运行命令、真实结果、剩余问题、下一条动作，并 commit/push；不要让下一位 Agent 依赖这次聊天或某台机器的 /tmp。
