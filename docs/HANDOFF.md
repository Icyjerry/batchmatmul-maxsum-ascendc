# 接手状态

> **最新工作（2026-09-22）：**检出 `experiment/hierarchical-k`，提交 `76d6c28`（核心实现 `d64d0c1`，父版 `73ed463`）。Cube已新增成对N tile共享A、可选L1常驻，并进一步将L1大K面板与L0小K计算分离，B四缓冲预取。实际容量不足时回退，保留独立对照开关。456次父producer执行和584次两级K CPU模型执行通过；读取字节/MMAD数不变、DMA调用减少，不代表实测加速。CANN/NPU精度、正式15点、性能PENDING；用户暂缓云端执行。检出后阅读 `docs/HANDOFF.md`、`docs/HIERARCHICAL_K.md` 与父版 `docs/CUBE_PANEL_REUSE.md`。main kernel仍为历史v1，此处仅更新接手指针。

> **历史起点：**用户确认的最佳原件保存在 `user-best-20260921` tag（`23e3e5a`），当前设备端候选建立在它的后续修复版本上。以下v1内容是main的历史记录，后续开发以顶部新分支接手单为准。

更新日期：2026-09-20。此文件与 Git 中的代码、验证单一起足以独立接手。

## 当前最重要的结论

- `kernel.asc` 已基于队友版本实现实验 v1；不是最初的 Vector fallback。
- 当前候选开启 `BMMMS_DEFERRED_MAX=1`，只影响默认 dual=1/2 的合适形状。
- **尚无本轮 NPU 编译成功、正式 15 case 通过或性能提升证据。**
- CANN 9.0.0，A2/A3 均可能；不要把任一设备的最佳参数未经验证推广到另一种。
- 用户当前要求把项目放到 GitHub 并用 Git 保留交接信息。GitHub 仓库私有，接手环境需要相应权限。

## 已完成

1. 审阅队友 2,809 行实现：默认 dual-master Cube/Vector、GM ring、N/K split、小形状专用路径、host plan/cache。
2. 研究 FlashAttention-2、Flash-MaxSim 源码和 CATLASS epilogue。来源、采用/未采用内容见验证单。
3. v1 在 `bmmms_dual` / `bmmms_dual_mdl` 接入 DeferredRowMax：每行 64 lane 最大值跨 N chunk 累计，末尾一次 WholeReduceMax。
4. 保留 `BMMMS_DEFERRED_MAX=0` 对照，0/1 两组的 UB 预留与 host tiling 逻辑相同。最多新增 16 KiB/AIV。
5. 修复 FinalizeRows 中把 AIC worker 数误用为 AIV 遍历步长的问题。
6. CPU C++ helper 模型 2,304 个分片、54,828 个有效行最大值逐位一致。Python 补充模型、任务覆盖与 UB 预算结果见 PERF_LOG。没有 NPU 结果。

## 下一条具体动作

**有 NPU 环境：**按 `docs/VALIDATION_REQUEST_v1.md` 编译 T0/T1/T2，并回传逐 case 精度、耗时和 msprof。T0 从 `teammate-opt4` tag 获取；T1/T2 使用当前代码但分别定义宏为 0/1。

**只有本地开发环境：**运行 `python3 tools/validate_cpu_model.py`，检查当前 Git 状态和验证资料，准备交接；不要凭 CPU 计时修改性能分块策略。

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
