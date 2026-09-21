# 设备验证：N 拆分 critical work 候选

分支 `experiment/n-split-critical-work`，kernel SHA256 `e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。本轮对照只切换 `BMMMS_BALANCED_NSPLIT`，沿用服务器已有 harness；不修改 main、CMake、run.sh、golden、正式测试或依赖。

## 构建

| 组 | 来源 | 宏 |
|---|---|---|
| P | 父提交8fb1e72 | 原有默认 |
| N0 | 当前候选 | BMMMS_BALANCED_NSPLIT=0 |
| N1 | 当前候选 | BMMMS_BALANCED_NSPLIT=1 |

先确认 N0 与 P 的计划一致，随后 N1 vs N0。BMMMS_ADAPTIVE_SPLITK 两组保持一致（默认1）；关闭 probe，生产组不定义 BMMMS_TUNING。若用已有 bmmms_plan 调试 ABI 获取 plan，明确记录该构建区别，保持 Tune 默认；任何显式 tile/ns/core pin 会绕过新选择器，不得把未命中结果写成候选结果。

## 必测

1. 记录精确 SoC、CANN9版本、编译命令、availableCoreNum、实际 AIC/AIV/UB/L1/L0C、kernel SHA。A2/A3 分开，不能只写“910”。
2. 正式15点全过精度才评价分数；缺少正式输入/提交结果明确 PENDING。
3. `nsplit_work_cases.csv` 每条跑 FP16/BF16、四种布局。记录最终 family、baseM/N/K、mTiles/nTiles、ns、window、workers、workspaceBytes、最大绝对/相对误差。列出真正命中 N1 的行；不要只报全体平均。
4. 对 anchor 的可用核数分别取1/4/8/16/20/24及物理上限（超物理上限的项跳过），验证不硬编码20核。低核数通常应保留旧 ns；不能通过调试 Tune().workers 强制这组测试，要使用正常 availableCoreNum。
5. 全负相似度、混合符号、重复执行与 FP64 golden；Ns 改变可能影响 Matmul 窗口与数值舍入。CPU partial-max 等价不替代这一步。
6. 先测正式精度和 anchor，再看排除路径的回退：M/N±1、K=1016/2048、N=2176、既有小矩阵/longK/manual/profile。若 anchor 未命中，保存真实计划后停止根据预期 ns 猜性能。

## 性能记录及判定

- 预热50次、每组200次 device timing，交替N0/N1至少5轮，同一 capture 内做对照；报告 median/p95 和跨轮波动。host plan/首次分配单列。
- 对命中行采 Task Duration、Cube/MAC、Vector、MTE2、FIX、每核工作分布。记录总窗口数/partial大小变化，不只看最忙worker代理值。
- 优先看 `(1,1536,1536,1536)`、`(1,3072,1536,1536)` 的实际ns变化，其余邻近/布局/设备是准入范围回退检查。旧资料53.39/92.14µs不是当前目标承诺。
- 精度失败立即保留输入、实际plan和日志；发生重复性性能回退则保持宏0，缩小范围必须有同会话证据。
- 确认正式精度全部通过、有可重复收益、未改路径无明显回退后再决定合并。结果摘要写 PERF_LOG，大日志留受控目录。

本机只完成 `python3 tools/validate_nsplit_work.py` 及继承模型回归，尚无CANN/NPU结果。
