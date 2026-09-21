# BatchMatmulMaxSum · Ascend C

目标：CANN 9.0.0、A2/A3 上的 BatchMatMul → Max(N) → Sum(M) 融合性能。

**当前开发起点为用户确认的最优 kernel(2).asc，已原样导入；本 Agent 尚未完成该版本的设备复测。**

## 接手

1. 检出 `experiment/user-best-20260921`，阅读 [HANDOFF](docs/HANDOFF.md) 和 [AGENTS](AGENTS.md)。
2. 阅读 [题目约束](docs/PROBLEM.md)、[当前版本验证单](docs/VALIDATION_REQUEST_user_best.md) 和 [性能记录](docs/PERF_LOG.md)。
3. 后续优化从当前版本另建实验分支，保留逐 case 的真实对照。

私有仓库：[Icyjerry/batchmatmul-maxsum-ascendc](https://github.com/Icyjerry/batchmatmul-maxsum-ascendc)。接手环境需要对应访问权限。

## 保存的版本

| Git 引用 | 内容 |
|---|---|
| `user-best-20260921` | 当前用户最优，3,492 行，逐字节保留 |
| `experiment/v2-dual1-nsplit` | 旧基准上的 N 拆分 CPU 实验，设备未验证 |
| `experiment-v1` | 旧 Deferred Max 候选及 writer 步长修复 |
| `teammate-opt4` | 最初 2,809 行队友原件 |
| `vector-v0.2` | 早期 Vector 版本 |

当前 kernel SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。

## 验证范围

`tools/validate_cpu_model.py` 只适用于旧 v1/v2 实验，在当前源码上应提示 NOT APPLICABLE 并非零退出。旧实验的 CPU PASS 不证明新版本正确。

原有 run.sh/main.asc 仅跑固定小样例。使用服务器已有 harness 按当前验证单复测，记录精确 SoC、编译宏、实际 plan、正式精度和稳定态性能。A2/A3 分开记录。

算法只修改 kernel.asc；原 main、CMake、run.sh、golden、正式测试保持原样。研究与历史验证仍可从 docs/VALIDATION_REQUEST_v1.md 和 Git 历史追溯。
