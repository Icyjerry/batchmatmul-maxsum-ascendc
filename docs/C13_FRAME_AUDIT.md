# C13现有计划审查 · 2026-10-08

本次只审查，未新增C13算法或正式任务。源码为C3候选515aa159…，C13部分逐字通过父1734f16。历史探针条件B1/M8192/N64..127/K128..248/FP16/FF不是正式shape证明。

## 可复现计划覆盖

运行 `python3 tools/audit_c13_plan.py`。抽取当前实际MakePlan控制流，在仓库明确标注的CPU tiler stub上执行；显式1/8/20/32 AIC、两倍AIV与夹具容量，各完整遍历1024个条件shape，共4096个计划。全部通过，四种核数均：

| dual | earlySum | 已有完整B驻留标志 | 条件shape数 |
|---|---:|---:|---:|
| 3 | 1 | 1 | 32 |
| 14 | 1 | 0 | 992 |

所有计划BM128、BN=N向上对齐16、64个M tile、一个N tile/分片、完整K不切分、window1；workers分别1/8/20/32。32个双对齐shape为4个N×8个K，其余992个含N或K尾。统计是条件空间中的配置数，不是正式用例频率、实际CANN9计划或设备命中率。没有profiling和速度预测。

## 已有实现与已否定方向

- dual3/tree16的完整B L0驻留、跨M worker累加已经存在；不能再次称为新优化。
- dual14已有完整N后的每M tile局部Sum，两AIV各写8float slot，末级FinalizeEarly。该路径仍由TPipe/TQue组织双A/B K panel、C/ring与Vector输入，未采用C7/TT的固定物理frame。
- `experiment/tall-ragged-resident-b` /a6c5a29：正式C13 15.74→15.93μs，无收益。
- `experiment/narrow-fullk-persistent` /7ffb3ff：双完整A1预读、一次完整K矩形Load3D/MMAD、B驻留和workerSum已做过，正式C13 15.28→16.04μs，无收益，见NARROW_FULLK_PERSISTENT。不继续此结构的相近tile变体。

## 后续独立假设（尚未实现）

保留dual14原task/grid、K panel大小与顺序、原partial/ring和有效N归约，只研究把该路径TPipe/TQue元数据替换为固定物理frame及显式ready/free事件。必须把MTE2→MTE1→MMAD→Fixpipe、两个AIV ring credit、跨M局部Sum及最终barrier全部建模；不能合并先前未获益的完整K/B驻留改动，不能以“减少queue”代替测量结论。

C3任务6ac72eaa694b590c3c97d81d已Pass15/15，但3.10μs在父波动范围内，归档无收益。当前分支experiment/c13-frame-audit-1008已逐字恢复1734f16。本审查工具可在恢复版执行；审查不构成再提交C13的依据，尚无新实现或本地生命周期模型。
