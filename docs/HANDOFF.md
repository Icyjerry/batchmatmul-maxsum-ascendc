# 接手状态 · 2026-09-21

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
