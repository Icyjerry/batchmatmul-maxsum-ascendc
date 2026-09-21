# v2：dual=1 的 N 拆分候选（归档）

日期：2026-09-21；分支 `experiment/v2-dual1-nsplit`。
Kernel SHA256：`07d0e5af66aff7a243af41aa7bb680898c1a2824d387a0d789bf1317705a9d3d`。

## 假设和改动

用户提供的 910B3 / 20 Cube / CANN 9.0.0 截图显示 `(1,513,511,2048)` 仅使用 5 个 Cube，Task Duration 107.2 us。但截图缺少源码 SHA、dtype、布局和完整日志，不能绑定到本分支。

在 v1 上添加 `BMMMS_DUAL1_BALANCE` 开关及 host 调度候选：当 dual=1、K 不拆分、N split 未显式固定且任务不足时，比较循环分派到各 worker 的最大 N tile 工作量，只接受该代理成本严格下降的拆分。窗口数用于候选之间的次级比较。代理成本不是设备耗时预测；任务重启、数据复用损失和最终归约成本仍需实测。

## CPU 验证

命令：`python3 tools/validate_cpu_model.py`。

- 从实际源码抽取 host helper，通过 C++14 模型比较 31,416 个配置；6,496 个发生改变，代理成本均严格下降。
- 54 组负数、混合值及尾块分片合并验证通过。
- v1 模型：2,304 分片 / 54,828 行；28,672 个 writer 调度；5,248 个预算配置通过。
- CANN 编译、NPU 精度、NPU 性能：**PENDING**。

## 新基准到来后的处理

用户随后提供 `kernel(2).asc` 并明确称为当前最优版本，SHA256 为 `e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。其中已有另一种 dual=1 N 拆分策略。本实验单独保留，不直接叠加到新版本。

若以后重新评估本候选，先关闭 Deferred Max，以同一设备、同一输入、相同构建比较 `BMMMS_DUAL1_BALANCE=0/1`，记录实际 plan、精度和稳定态 latency。不能用本分支的 CPU PASS 证明新基准正确。
