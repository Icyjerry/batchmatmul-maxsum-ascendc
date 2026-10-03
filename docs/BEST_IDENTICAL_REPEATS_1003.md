# 当前最优组合新增两次原样复测 · 2026-10-03

## 用户随后新增一次复测

此前两次已完成后，用户明确“再交一次”。新增任务 `6ac0d57f694b590c3c252456` 已15/15 Pass、precision_ratio全1，kernel/template SHA仍a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742/354602bytes，源码和参数不变。新增这一次已完全完成，无活动任务；完整结果见本文末尾。总耗时468.89μs、按用户T换算平均分50.58201。下文“不创建第三次”仅约束此前两次请求，不取消用户新要求。原结果保存artifacts/best-identical-repeats-1003/extra-one.json，不入Git。

用户新增要求“再交两次”。对象延续上一组：最优组合1734f16，kernel SHA256 `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742` /354602bytes，源码和参数完全不变。

分支experiment/best-identical-repeats-1003从cf52f5e创建。独立模板/private/tmp/bmmms-tt-manual-frame-official/project与工作区kernel SHA一致；dry-run仅kernel，SHA一致。其它七源码逐字保持1734f16；只改交接文档，不改main/标签。

上一组任务6abfc955694b590c3ca51a64 /6abfca4d694b590c3ca5b6a8已经15/15 Pass，详见BEST_IDENTICAL_REPEATS_1002。本轮独立新增恰好两次，不复用旧ID冒充新提交。

任务1 `6ac08cd7694b590c3cf7a7d8` /任务2 `6ac08d9c694b590c3cf806ec` 均CANN编译成功、15/15 Pass、precision_ratio全1。新增两次已完全完成，无活动任务，不创建第三次。任务1终态后提交任务2，没有429。完整15点、总耗时和分数在本文末尾。原日志忽略artifacts/best-identical-repeats-1003/，目录700/文件600。

保存全部15点status/precision/time；同源码样本不能证明同机受控A/B或新优化收益，接口没有实际SoC/shape/plan/profile。平均分只按用户T换算，不当榜单排名证据。整体冲榜目标尚未完成。

## 任务1正式结果

任务 `6ac08cd7694b590c3cf7a7d8` Pass，CANN编译成功、15/15、precision_ratio全1。μs：`[1.90,2.65,3.22,3.94,5.30,9.85,7.85,46.51,67.35,97.58,87.35,96.12,15.13,10.81,8.96]`。源码SHA保持。


## Final: both unchanged repeats complete

Both tasks compiled and passed all15 cases, all precision_ratio=1. IDs: 6ac08cd7694b590c3cf7a7d8, 6ac08d9c694b590c3cf806ec. No active task; exactly two created; no rate-limit failures this group. Source and parameters unchanged.

| Case | Repeat1 us | Repeat2 us | Two-run median us | Range / median |
|---|---:|---:|---:|---:|
| C1 | 1.90 | 1.90 | 1.900 | 0.00% |
| C2 | 2.65 | 2.59 | 2.620 | 2.29% |
| C3 | 3.22 | 3.16 | 3.190 | 1.88% |
| C4 | 3.94 | 4.12 | 4.030 | 4.47% |
| C5 | 5.30 | 5.60 | 5.450 | 5.50% |
| C6 | 9.85 | 9.59 | 9.720 | 2.67% |
| C7 | 7.85 | 8.36 | 8.105 | 6.29% |
| C8 | 46.51 | 46.29 | 46.400 | 0.47% |
| C9 | 67.35 | 68.07 | 67.710 | 1.06% |
| C10 | 97.58 | 97.76 | 97.670 | 0.18% |
| C11 | 87.35 | 88.91 | 88.130 | 1.77% |
| C12 | 96.12 | 97.77 | 96.945 | 1.70% |
| C13 | 15.13 | 16.74 | 15.935 | 10.10% |
| C14 | 10.81 | 11.25 | 11.030 | 3.99% |
| C15 | 8.96 | 9.11 | 9.035 | 1.66% |

Scoring uses the user-provided referenceT and 100/(1+log_1.5(t/T)), then mean over15 cases. This calculation does not prove a public leaderboard rank.

- Repeat1: total 464.52us = 0.00046452s, mean score 50.84691.
- Repeat2: total 471.22us = 0.00047122s, mean score 50.01648.

All measurements retained. C13 15.13/16.74us (two-run range/median10.1%) demonstrates substantial single-case variation on unchanged source. C4 3.94/4.12, C9 67.35/68.07, C11 87.35/88.91. No source change or new optimization benefit inferred. Actual SoC/shape/plan/profile unavailable; not controlled same-device A/B or a general variation bound.

The user-requested two new repeats are fully complete. Raw JSON stays ignored under artifacts/best-identical-repeats-1003 with directory700/file600. No further submission is needed for this request. Overall competition optimization goal remains active.


## Extra user-requested single repeat: final Pass

Task 6ac0d57f694b590c3c252456, CANN compile success, Pass15/15, all precision_ratio=1. Same1734f16/a5eef105... source and parameters. Exactly one new task for this request; no active task.

Times(us): `[1.9, 2.53, 3.08, 4.08, 5.27, 9.8, 8.18, 46.78, 67.95, 98.24, 88.02, 97.08, 15.99, 10.77, 9.22]`.

Total 468.89us = 0.00046889s. User-referenceT mean score 50.58201; calculated score, not public leaderboard rank evidence. No new algorithm improvement inferred from unchanged-source timing. Raw ignored artifacts/best-identical-repeats-1003/extra-one.json, file600. Overall competition optimization goal remains active.


## New user Tbest supersedes prior scoring reference

See SCORE_REFERENCE_1003. Same runs/timings now calculate57.00705 /55.29167 /56.42050 using the new user Tbest. The old50.x numbers remain historical calculations with the oldT; no algorithm change, new timing, or public ranking claimed.
