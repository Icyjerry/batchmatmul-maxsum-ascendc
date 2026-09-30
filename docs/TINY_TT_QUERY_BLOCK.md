# 一次 A UB 整理与双 query 归约

## Evidence → Diagnosis → Fix

首版单AIV `a3c65a4` / [正式任务 6abd2f7e694b590c3c75d2b6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd2f7e694b590c3c75d2b6) 15/15通过，第4点8.08→6.01 μs，合计519.03 μs；局部有效但整体仍没有重大收益。实际shape/plan/profile未取得。

首版每M行都Adds(index)、Gather(A)、K组计算和两级横向归约，在小算量场景留下串行指令与屏障。本候选假设一次整理全部query行并批量归约两行可进一步降低这些开销；这不是设备瓶颈实测。

## 实现与不变量

分支 `experiment/tiny-tt-query-block`，kernel SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`。

- 保留原dual28形状准入、单AIV整批、直接写y；不扩大dtype/layout范围，不改其它kernel。
- A在UB整理为[M,128/256]一次：复用已有MicroIndices TT索引，在输入Cast/Gather前借用fa/raw缓冲作索引临时空间；完成后这些临时值不再使用。只持久保留一个完整索引表，没有新GM预打包。
- 产品改为[K组,2个query,N上取8,64]，两行共享每个计算/归约阶段的屏障；K组全累加后一次WholeReduceSum得到两行C，再以重复数2与源Npad stride执行Max。尾部单行只处理实际countM。
- 无效K lane和Npad产品为0，仅对真实N执行Max；全负时无效列不参与。输出Max位于偶数float lane，目标8字节对齐，最后Sum(M)与零占位。
- Host按实际新UB分配重新预算并留4KiB；资源不足回退已有dual19。输入加载/Gather scratch缓冲有明确使用顺序，索引表在整次launch复用。

## 验证

`python3 tools/validate_tiny_tt_vector.py`：抽取实际新kernel与MicroIndices执行700个整数算术/边界/对齐/生命周期/尾块/全负/重复batch配置；每个y恰有一个writer，输入和y两端guard不变，实际InitBuffer总量逐case等于host预算。production/TUNING各432host尝试、360选择，资源/pins/布局等回退通过。30个独立实际FP16/BF16存储值的FP32/FP64对照通过，最大绝对误差9.54e-7。

该CPU模型同步执行，不证明真实Ascend事件、指令或速度。正式CANN编译、15/15精度、性能PENDING；仍应独立正式模板只替换kernel.asc，dry-run并提交一次，记录SHA/ID，不能按case编号断言命中。无收益保留该分支，不继续相近参数试验。整体大幅提升目标仍未达成。

## 2026-09-30 · 一次 A 整理与双 query 正式结果

代码 `55225cc`，kernel SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，[正式提交 6abd3263694b590c3c776446](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd3263694b590c3c776446) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.32, 3.75, 4.19, 5.66, 5.2, 10.57, 9.6, 69.03, 83.27, 97.45, 87.37, 95.91, 15.07, 12.72, 9.55]` μs，合计511.66 μs。第4点相对原通过版8.08→5.66 μs（1.43×），相对单行Vector首版6.01→5.66。其余kernel未修改，其它点的单次差异不能归因；合计时长不是正式分数，且未经过同设备重复A/B，整体重大突破仍未达成。实际shape/plan/profile未取得，不声称新路由命中。

本分支作为后续结构研究起点，保留 `experiment/manual-splitk-tiny` 与 `experiment/tiny-tt-vector` 对照；不继续Gather或query块大小相近参数提交。下一动作审查手写Cube A/B rectangular LoadData是否能用A2/A3的真实矩形加载API减少逐行指令，此API/设计尚未核实。CPU700实际源码执行、production/TUNING各432host尝试、30量化FP64对照通过，与正式证据分别报告。原始JSON本机Git忽略 `artifacts/tiny-tt-query-block/`。
