# BatchMatmulMaxSum · Ascend C

> **最新工作（2026-09-22）：**检出 `experiment/hierarchical-k`，提交 `76d6c28`（核心实现 `d64d0c1`，父版 `73ed463`）。Cube已新增成对N tile共享A、可选L1常驻，并进一步将L1大K面板与L0小K计算分离，B四缓冲预取。实际容量不足时回退，保留独立对照开关。456次父producer执行和584次两级K CPU模型执行通过；读取字节/MMAD数不变、DMA调用减少，不代表实测加速。CANN/NPU精度、正式15点、性能PENDING；用户暂缓云端执行。检出后阅读 `docs/HANDOFF.md`、`docs/HIERARCHICAL_K.md` 与父版 `docs/CUBE_PANEL_REUSE.md`。main kernel仍为历史v1，此处仅更新接手指针。

> **历史起点：**用户确认的最佳原件保存在 `user-best-20260921` tag（`23e3e5a`），当前设备端候选建立在它的后续修复版本上。以下v1内容是main的历史记录，后续开发以顶部新分支接手单为准。

目标：在 CANN **9.0.0**、**A2 / A3** 上优化 `BatchMatMul → Max(N) → Sum(M)`，支持 FP16/BF16 输入、四种存储布局和 FP32 输出。

**当前状态：实验候选，尚未完成本轮 NPU 编译、15 个正式 case 验证或性能测量。** CPU 模型通过不代表设备测试通过。

## 新 Agent 从这里接手

1. 阅读 [AGENTS.md](AGENTS.md) 和 [HANDOFF.md](docs/HANDOFF.md)。
2. 阅读 [算子约束](docs/PROBLEM.md) 和 [v1 研究与验证单](docs/VALIDATION_REQUEST_v1.md)。
3. 使用 [CPU 检查](#cpu-检查) 复现本地模型；上板执行验证单中的 T0/T1/T2 对照。
4. 将实际结果和下一步写入 [PERF_LOG.md](docs/PERF_LOG.md)、更新 HANDOFF，然后 commit / push。

## Git 中保存的版本

| Tag | 内容 |
|---|---|
| `vector-v0.2` | 早期 Vector 版本，保留用于追溯 |
| `teammate-opt4` | 用户提供的 2,809 行队友原版，字节级保留 |
| `experiment-v1` | 当前延后 Max 归约候选，以及最终归约 writer 步长修复 |

`main` 包含当前候选及完整交接资料。只需克隆此仓库，不依赖原对话、微信路径或本机 `/tmp`。

```sh
git clone https://github.com/Icyjerry/batchmatmul-maxsum-ascendc.git
cd batchmatmul-maxsum-ascendc
git status --short --branch
git log --oneline --decorate -6
git diff teammate-opt4 experiment-v1 -- kernel.asc
```

仓库为私有；其他 Agent 的执行环境需要使用有该仓库权限的 GitHub 身份。

## CPU 检查

需要 Python 3 标准库及支持 C++14 的 `clang++` 或 `c++`，不需要 NPU 或新增 Python 依赖。

```sh
python3 tools/validate_cpu_model.py
```

脚本从当前 `kernel.asc` 提取 `DeferredRowMax`，编译 CPU 指令语义模型，在临时目录执行，并检查输出任务覆盖与 UB 预算。**它不编译整个 Ascend kernel、不模拟硬件同步，也不测 NPU 性能。**

## 上板

原有 `run.sh` / `main.asc` 仅提供一个固定小样例，不能代表 15 个正式用例通过，而且该小样例不进入本轮优化路径。

先设置服务器的 CANN 环境，再按 [VALIDATION_REQUEST_v1.md](docs/VALIDATION_REQUEST_v1.md) 用已有评测 harness 编译和测试。A2/A3 分开记录结果。

- `BMMMS_DEFERRED_MAX=1`：当前默认候选。
- `BMMMS_DEFERRED_MAX=0`：相同 UB 预留和分块策略下的旧归约对照。
- 不默认开启 `BMMMS_TUNING` 或额外手写 MMAD 候选。

## 目录

- `kernel.asc`：算子实现，比赛代码改动集中于此。
- 原有 `main.asc`、`CMakeLists.txt`、`run.sh`、`data_utils.h`、`scripts/`：保持原模板。
- `docs/`：任务约束、研究、验证请求、结果记录和接手状态。
- `tests/cpu/`、`tools/`：独立本地模型验证，不修改正式 golden 或评测器。
