# 最新组合原样两次复测

## 当前：同一kernel原样复测两次，第一次任务已创建

用户要求最新通过版一模一样再交两次。kernel保持 `889afe0` / SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597byte；独立提交模板仍仅kernel，dry-run匹配。按顺序执行，第一次 **`6abe87e6694b590c3c102b8c`** 已创建，第二次尚未提交。
下一：`python3 /private/tmp/query_bmmms_submission.py 6abe87e6694b590c3c102b8c` 查询同任务至终态，再原样创建第二次并立刻保存ID，查至终态。与首次任务 `6abe860d694b590c3c0f02a5` 的15点一起列三次耗时、中位数、min/max及极差/中位数；不额外提交其它候选、不改kernel、不将同版本波动当优化收益。没有实际同机元数据，重复正式任务不等价受控同机A/B。小矩阵Cube泛化工作等这两次复测完成再继续。


首次原样复测 `6abe87e6694b590c3c102b8c` **Pass，15/15，precision_ratio全1**。μs `[1.90,2.46,3.18,4.04,5.31,9.72,10.28,49.59,67.60,98.18,88.17,96.84,15.48,13.33,9.42]`。原日志忽略 `artifacts/teammate-single-tile/repeat1.json`。下一原样创建第二次，不重复第一次任务。

第二次原样复测 **`6abe88a7694b590c3c109c3a`** 已创建，下一 `python3 /private/tmp/query_bmmms_submission.py 6abe88a7694b590c3c109c3a`，只查同一任务到终态。本次共请求两次重复，两次均已提交，不能再创建第三次重复任务。
