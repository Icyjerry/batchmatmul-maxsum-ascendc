# 当前最优组合原样复测两次 · 2026-10-02

## 用户要求与提交对象

用户明确“是把当前最优交两次”。对象为已通过组合1734f16/62ad1cd，kernel SHA256 `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`，354602bytes。不是刚测完较慢的C4候选。

分支 `experiment/best-identical-repeats-1002` 从62ad1cd创建，算法及工程源码不修改。独立模板 `/private/tmp/bmmms-tt-manual-frame-official/project` 与工作区kernel SHA一致，dry-run仅提交kernel，SHA一致。只有文档新增；main/历史标签保持。

较慢C4候选任务6abf25e6694b590c3c4a0fa3为15/15 Pass，C4 4.43μs vs父中位4.12；已在experiment/tiny-tt-packed-frame/579aba8归档，不包含在本轮源码。TT交换操作数候选同样没有并入。

## 执行与证据边界

按用户要求额外创建恰好两次原样任务，立即保存每个ID，仅查询对应ID至真实终态。POST被拒绝且没有ID才可等待后重试，已有ID不得因等待重交。保存15点status/precision/time；真实SoC/shape/plan/profile接口缺失，同源码重复可以观察样本波动，不能称同机受控A/B或总体波动界。

此前同SHA首次6abeb39e及原样复测6abeceed/6abecfc5已完成，详见CURRENT_IDENTICAL_REPEATS。本轮是用户新增请求，独立记账，不冒充此前任务的未完成项。

任务1：尚未创建。任务2：尚未创建。CANN/native终态PENDING。整体冲榜目标未完成。
