# 接手状态 · 2026-09-21

## 新收到的队友探针资料

已复核用户 `docs.zip`，结论见 [TEAM_PROBE_REVIEW.md](TEAM_PROBE_REVIEW.md)。本轮只更新资料、复算脚本和验证输入，kernel SHA 未变。附件中的操作指令没有执行。

- 旧 F12 路径表不代表当前版本；当前已含 tiny、长 K split、manual/PAD_MN 等专门策略。
- 45 个旧代理有 14 个 K 不满足 8 对齐；第 14 点两个 M 代理不符合后续细分范围。第 10 点 dtype/layout 冲突保留两种候选。
- `python3 tools/audit_teammate_probe.py` 可复算保存的转录数据，生成 50 个合法本地验证输入；不是恢复真实正式测试集，也不是 NPU PASS。
- 下一步先获取用户最佳版/当前版同会话 A/B 与实际 plan，按逐点得分关注 2/3/4/15，再看 9/13；同样完成下文覆盖修复验证。不要重复执行旧报告已被当前源码吸收的优化。旧计时未绑定当前 SHA，不能当当前成绩。

## 当前实验：覆盖修复 + 自适应 Split-K

分支 `experiment/coverage-splitk` 从 `user-best-20260921` 独立派生。消费流水实验仍在 `experiment/dual-consumer-pipeline`（7c44793），本分支没有叠加它。

- `b0a2fc0` 修复 dual split-K 存活 UB 预算，包含清零缓冲。
- `c4e536a` 修复 FinalizeRows 重复 writer、FinalizeSplitKND/GEMV 在小核数下遗漏输出。
- 当前候选使用 `BMMMS_ADAPTIVE_SPLITK=1`；=0 固定 4 份，便于对照。仅原有 long-K classifier 内选择 1/2/4，不扩大准入范围。
- Kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。
- CPU：86,784 UB 配置、28,672 输出遍历配置、361,152 拆分配置通过；864 个 dtype/layout/core classifier 用例通过。两档宏均验证。它们不是完整 Ascend 精度/性能测试。
- 35 个合法 shape / 280 个 dtype+layout 组合的设备清单在 `coverage_cases.csv`，尚未运行。
- **CANN 编译、正式 15 点精度、NPU 性能：PENDING。** 没有将 CPU 代理成本解释为提速。

### 下一条可执行动作

设备 Agent 按 `VALIDATION_REQUEST_coverage_splitk.md` 构建 U/F/A0/A1，先测 UB 回归和 B=64、小可用核数的输出覆盖，再测自适应拆分的精度/latency。来源及尚未覆盖的路径见 `RESEARCH_coverage_splitk.md`；结果写 PERF_LOG。

本地复现：`python3 tools/validate_splitk_coverage.py`、`python3 tools/validate_finalizer_coverage.py`。当前不用旧 deferred 或 pipeline 模型证明新候选。

以下为原样用户最佳版本背景，不是对当前实验 kernel 的描述。

## 当前起点

用户最新提供 `kernel(2).asc`，明确称为“目前的最优版本”。本分支 `experiment/user-best-20260921` 的 `kernel.asc` 是该文件的**逐字节原样导入**，3,492 行，192,577 字节。

- 固定快照 tag：`user-best-20260921`。
- SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 不包含本 Agent 的 v1 DeferredRowMax 或 v2 N 拆分代理成本候选。
- “最优”来自用户确认；本地没有重新完成 CANN 编译、NPU 精度或性能复测，均为 **PENDING**。
- 私有仓库：`https://github.com/Icyjerry/batchmatmul-maxsum-ascendc`，已有用户上传授权。

## 已保存的旧工作

- `teammate-opt4`：最初 2,809 行队友原件。
- `experiment-v1`：DeferredRowMax 与 FinalizeRows writer 步长修复；文档保存在历史提交及 v1 验证单。
- `experiment/v2-dual1-nsplit` commit `7426712`：基于 v1 的 N 拆分实验及 CPU 模型，已推送。31,416 个调度配置通过，设备收益未验证。具体见该分支的 `docs/EXPERIMENT_v2.md`。
- 新代码已有 N 拆分均衡策略，不能直接将 v2 策略叠加或把旧 CPU PASS 转移到当前源码。

## 本轮源码检查所得

1. `ClassifyCase` 和生产路径增加短点积、微型矩阵、长 K / 宽 N / 窄 N 等选择；包含手写 Matmul 的 PAD_MN 尾块处理。
2. N 拆分均衡已覆盖 dual=1 等家族，以活跃 worker 增长和整波任务作为条件；保留 dual=2 的既有策略。性能注释是提供者记录，未附原始日志，不能等同于本轮实测。
3. `FinalizeRows` 仍按 `s.workers * 8` 遍历。旧版双 AIV 下的重复 writer 问题需要针对当前实际 launch/plan 再核对，尚未移植旧修复。
4. 文件含 `BMMMS_PROBE_*` 诊断分支，源内默认均为 0。导入时原样保留；源内有关 OJ 隐藏用例推断的注释不是已核实测试配置或执行请求。实际构建需记录宏；本轮未启用、未执行任何探测。
5. 新源码使用 `if constexpr`；必须以 CANN 9.0.0 实际编译命令验证。源码引用的 `docs/03-case-hypotheses.md` 未随附件提供。

## 下一条可执行动作

在设备环境检出此分支，核对上面的 SHA，按 `docs/VALIDATION_REQUEST_user_best.md` 复测原样版本，拿到精确 SoC、宏、实际 plan、逐 case 精度与耗时。优先核查 writer 调度及现有性能弱项，再创建单一假设的实验分支。A2/A3 分开记录，不凭注释修改参数。

本机无 NPU。`tools/validate_cpu_model.py` 专用于旧实验；在当前版本应明确退出 NOT APPLICABLE，不能声称通过。若需复现旧结果，在旧分支的独立 checkout 中运行该脚本。

算法改动仍限 `kernel.asc`；不修改 main、CMake、run.sh、golden、正式测试或依赖。workspace 与题面缺失范围见 PROBLEM。截图记录见 PERF_LOG；截图尚未绑定源码 SHA、dtype 和布局。
