# 队友tiny_dot原版正式对照

## 当前：队友tiny_dot原版直接正式对照

分支 `experiment/teammate-tiny-original`，kernel与用户 `kernel_tiny_dot.asc` **逐字相同**，300625bytes、CRLF SHA `72454276ca665e0dd80d2bea6d972a34270442cad8fd3ccf0bd2a6674d4323e7`。CLI按文本读取转LF，实际提交295170bytes、SHA `6b42fe18e0d5ce1f3312b7f10545ca52c1f61edfb157db927f57e39bdedf7387`；仅换行转换，没有算法/参数/分派修改。
通过组合保留 `experiment/teammate-tiny-dot` / `d5cd4af`；不以原版覆盖该分支。独立官方原模板 `/private/tmp/bmmms-teammate-tiny-original/project`，dry-run仅kernel。下一执行CLI一次 `--no-wait`，立即保存ID，再查同一任务至终态；原版CPU模型未新增，设备编译/精度/性能PENDING。

对照已通过组合任务 `6abe7b90694b590c3c08ed48`，15点μs `[1.98,2.63,3.66,4.13,5.70,10.75,10.25,50.72,68.02,99.81,89.21,97.18,16.30,13.44,9.64]`。只比较正式同一编号；无实际shape/plan/SoC/profile与重复A/B，不推断隐藏路径或稳定速度。

正式任务 **`6abe7f04694b590c3c0ade30`** 已创建。下一 `python3 /private/tmp/query_bmmms_submission.py 6abe7f04694b590c3c0ade30`，只查同一ID到终态，不重复提交。CANN编译/NPU精度/性能PENDING。

## 最新：队友tiny_dot原版正式对照，15/15通过

分支 `experiment/teammate-tiny-original` 保存用户原文件逐字快照（实现 `9ab2312`），无算法修改。正式任务 **`6abe7f04694b590c3c0ade30` Pass，CANN编译成功、15/15、precision_ratio全1**。原文件SHA `72454276ca665e0dd80d2bea6d972a34270442cad8fd3ccf0bd2a6674d4323e7`；CLI CRLF→LF后的提交SHA `6b42fe18e0d5ce1f3312b7f10545ca52c1f61edfb157db927f57e39bdedf7387`，295170byte。原模板其它8文件不变，原始JSON Git忽略 `artifacts/teammate-tiny-original/official.json`。
对照通过组合 `experiment/teammate-tiny-dot` / `d5cd4af` / 任务 `6abe7b90694b590c3c08ed48`：

| Case | 队友原版 μs | 当前组合 μs | 组合相对原版耗时变化 |
|---|---:|---:|---:|
| C1 | 1.94 | 1.98 | +2.1% |
| C2 | 2.50 | 2.63 | +5.2% |
| C3 | 3.14 | 3.66 | +16.6% |
| C4 | 4.03 | 4.13 | +2.5% |
| C5 | 5.21 | 5.70 | +9.4% |
| C6 | 9.73 | 10.75 | +10.5% |
| C7 | 10.52 | 10.25 | -2.6% |
| C8 | 50.66 | 50.72 | +0.1% |
| C9 | 68.66 | 68.02 | -0.9% |
| C10 | 97.89 | 99.81 | +2.0% |
| C11 | 88.32 | 89.21 | +1.0% |
| C12 | 96.77 | 97.18 | +0.4% |
| C13 | 16.64 | 16.30 | -2.0% |
| C14 | 14.03 | 13.44 | -4.2% |
| C15 | 12.53 | 9.64 | -23.1% |

队友原版C3明显更快（3.14对3.66，组合慢16.6%），C5/C6也更快；组合C15更快（9.64对12.53）。C8/C9接近。均单次不同任务，不能证明稳定幅度或实际隐藏shape/plan/SoC/路径命中。截图C3与原版实测接近，但仍不证明截图对应同SHA。此对照优先于继续猜测入口或盲目整份覆盖。
下一可执行动作：`git switch experiment/teammate-tiny-dot`，从通过组合新建独立覆盖实验，比较队友 `TinyVectorFits` / `TinyVectorBatchGroup` / dual24及原版C5/C6分派，先用实际资源查询与源码模型验证，再提交一个有明确差异的候选。保留组合C15及已有C8/C9，不能仅凭编号推断路径；C9 WIP仍仅独立归档。没有活动任务，main/历史标签保持。

