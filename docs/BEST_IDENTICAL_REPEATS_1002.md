# 当前最优组合原样复测两次 · 2026-10-02

## 用户要求与提交对象

用户明确“是把当前最优交两次”。对象为已通过组合1734f16/62ad1cd，kernel SHA256 `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`，354602bytes。不是刚测完较慢的C4候选。

分支 `experiment/best-identical-repeats-1002` 从62ad1cd创建，算法及工程源码不修改。独立模板 `/private/tmp/bmmms-tt-manual-frame-official/project` 与工作区kernel SHA一致，dry-run仅提交kernel，SHA一致。只有文档新增；main/历史标签保持。

较慢C4候选任务6abf25e6694b590c3c4a0fa3为15/15 Pass，C4 4.43μs vs父中位4.12；已在experiment/tiny-tt-packed-frame/579aba8归档，不包含在本轮源码。TT交换操作数候选同样没有并入。

## 执行与证据边界

按用户要求额外创建恰好两次原样任务，立即保存每个ID，仅查询对应ID至真实终态。POST被拒绝且没有ID才可等待后重试，已有ID不得因等待重交。保存15点status/precision/time；真实SoC/shape/plan/profile接口缺失，同源码重复可以观察样本波动，不能称同机受控A/B或总体波动界。

此前同SHA首次6abeb39e及原样复测6abeceed/6abecfc5已完成，详见CURRENT_IDENTICAL_REPEATS。本轮是用户新增请求，独立记账，不冒充此前任务的未完成项。

当前终态：两次均15/15 Pass，源码未改，没有活动任务。完整结果见本文末尾；以下为提交过程记录，PENDING和下一动作只代表当时状态。

## 任务1正式终态

`6abfc955694b590c3ca51a64` Pass，CANN编译成功，15/15，precision_ratio全1。同SHA。μs：`[1.96,2.53,3.18,4.11,5.36,9.45,7.76,46.98,67.34,96.98,86.99,96.13,14.94,10.95,9.57]`。

任务2前两次POST均HTTP429且无ID，间隔等待45秒；未创建第二任务、未重复任务1。下一等待限流解除，仅完成尚缺的一次提交。原始任务1JSON忽略artifacts/best-identical-repeats-1002/repeat-one.json。模型/源码未修改。

## 任务2已创建

任务1结束并继续等待45秒后，任务2创建成功：`6abfca4d694b590c3ca5b6a8`。同一原模板/同SHA，终态PENDING。用户要求的两次任务均已创建，没有第三次；下一只查询任务2同ID到终态。


## Both repeats complete: same source, 15/15 Pass

Both tasks compiled and passed all15 cases, all precision_ratio=1. IDs: 6abfc955694b590c3ca51a64, 6abfca4d694b590c3ca5b6a8. No active task; no third submission.

| Case | Repeat1 us | Repeat2 us | Two-run median us | Range / median |
|---|---:|---:|---:|---:|
| C1 | 1.96 | 1.96 | 1.960 | 0.00% |
| C2 | 2.53 | 2.43 | 2.480 | 4.03% |
| C3 | 3.18 | 3.12 | 3.150 | 1.90% |
| C4 | 4.11 | 4.08 | 4.095 | 0.73% |
| C5 | 5.36 | 5.26 | 5.310 | 1.88% |
| C6 | 9.45 | 9.72 | 9.585 | 2.82% |
| C7 | 7.76 | 7.98 | 7.870 | 2.80% |
| C8 | 46.98 | 46.96 | 46.970 | 0.04% |
| C9 | 67.34 | 67.91 | 67.625 | 0.84% |
| C10 | 96.98 | 98.17 | 97.575 | 1.22% |
| C11 | 86.99 | 86.97 | 86.980 | 0.02% |
| C12 | 96.13 | 95.87 | 96.000 | 0.27% |
| C13 | 14.94 | 15.11 | 15.025 | 1.13% |
| C14 | 10.95 | 10.70 | 10.825 | 2.31% |
| C15 | 9.57 | 9.44 | 9.505 | 1.37% |

User-reference scoring uses 100/(1+log_1.5(t/T)), mean over15 cases; these are calculated scores, not leaderboard rank evidence.

- Repeat1: total 464.23us = 0.00046423s; mean score 50.58646.
- Repeat2: total 465.68us = 0.00046568s; mean score 50.82629.

C4 4.11/4.08 overlaps prior best-source range4.12-4.15 closely. C8 46.98/46.96 is higher than prior46.48-46.52; C11 86.99/86.97 is lower than prior87.73-88.30. These are unchanged-source samples, not a new optimization or controlled same-device A/B; actual SoC/shape/plan/profile unavailable. Full observations retained, no cherry-picked minimum used to claim a stable score.

Repeat1 total464.23us is lower than the earlier saved minimum464.70us. Repeat2 total465.68us. Minimum sum is not maximum mean score. The user-requested two repeats are fully complete; overall competition optimization goal remains active.
