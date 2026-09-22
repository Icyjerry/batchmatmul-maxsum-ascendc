# BatchMatmulMaxSum · Ascend C

目标：CANN 9.0.0、A2/A3 上的 BatchMatMul → Max(N) → Sum(M) 融合性能。

**当前开发起点为用户确认的最优 kernel(2).asc，已原样导入；本 Agent 尚未完成该版本的设备复测。**

## 最新设备端优化候选

检出 **`experiment/dual-consumer-fold`**。两条dual路径采用UB双缓冲预取、按DMA完成提前归还GM槽位，以及tile内树形Max合并。保留独立开关做同机对照。

- [实现、论文/API依据及设备执行单](docs/DUAL_CONSUMER_OPTIMIZATION.md)
- 本地抽取源码模型：`python3 tools/validate_dual_pipeline.py`，六种开关组合通过。
- CANN编译、NPU精度和性能：**PENDING**；云端暂缓。不把减少调用数换算成加速比。

## 父版本集中修复

检出 `experiment/known-issue-closure`。已修复末级输出、UB、调参缓存和workspace用途转换问题，并保留可对照的分块候选。

- [全部已知问题状态](docs/KNOWN_ISSUES.md)
- [统一设备验证入口](docs/VALIDATION_REQUEST_known_issues.md)（用户当前暂缓云端执行）
- [接手状态](docs/HANDOFF.md)
- 当前kernel SHA256：`d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。CPU控制流/资源模型通过，CANN/NPU精度和性能未验证。

## 已包含的性能候选

分支 `experiment/n-split-critical-work`：在父分支覆盖修复基础上增加单项 N 拆分实验，缓解已占满核心时的任务尾波不均衡。宏 `BMMMS_BALANCED_NSPLIT=0/1` 可对照。

- [假设、证据与CPU验证](docs/EXPERIMENT_nsplit_work.md)
- [设备验证单](docs/VALIDATION_REQUEST_nsplit_work.md)
- 当前候选 kernel SHA256：`e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`；CANN/NPU/正式性能 PENDING。

## 父分支覆盖实验

分支 `experiment/coverage-splitk`：修复 Split-K UB 预算及小核数输出遍历，再对 long-K 类比较 1/2/4 份拆分。独立于 `experiment/dual-consumer-pipeline`，当前未完成 NPU 验证。

- [缺口与论文依据](docs/RESEARCH_coverage_splitk.md)
- [设备对照请求](docs/VALIDATION_REQUEST_coverage_splitk.md)
- [边界 shape 清单](docs/coverage_cases.csv)
- 本地模型：`python3 tools/validate_splitk_coverage.py` 和 `python3 tools/validate_finalizer_coverage.py`

## 接手

1. 当前工作检出 `experiment/dual-consumer-fold`；原样用户最优检出 `experiment/user-best-20260921`，阅读 [HANDOFF](docs/HANDOFF.md) 和 [AGENTS](AGENTS.md)。
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

原样用户最佳 kernel SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。

## 验证范围

`tools/validate_cpu_model.py` 只适用于旧 v1/v2 实验，在当前源码上应提示 NOT APPLICABLE 并非零退出。旧实验的 CPU PASS 不证明新版本正确。

原有 run.sh/main.asc 仅跑固定小样例。使用服务器已有 harness 按当前验证单复测，记录精确 SoC、编译宏、实际 plan、正式精度和稳定态性能。A2/A3 分开记录。

算法只修改 kernel.asc；原 main、CMake、run.sh、golden、正式测试保持原样。研究与历史验证仍可从 docs/VALIDATION_REQUEST_v1.md 和 Git 历史追溯。
