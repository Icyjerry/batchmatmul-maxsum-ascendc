# 完整 M 单 MMAD 与 TT 矩形转置加载

## 假设与对照

父候选宽窗口手写版本 `1c2f5b9` / kernel `9cfb159` 正式15/15通过，但第8点仅69.03→67.44μs，未取得大幅收益。
父公开Norm已经具备窗口内full-K A缓存，见 `NORM_FULLK_CACHE_AUDIT.md`；本次不再声称A驻留本身是新增读流量优势。
本次针对手写producer的半M MMAD和逐M16 Load2D发起开销：用完整原baseM一次MMAD、一次整矩形TT Load3D替代两半M和逐M16转置加载。
原query-block库也可能已使用矩形Load3D；相对它是否降低Scalar/握手开销必须由硬件结果判断，不能把对手写父版的调用数消减冒充对库的降幅。

## 实现

仅kernel.asc改变：完整M full-K A1 queue1，保持整个N shard；B1两个流式K panel，完整M L0A/L0B ping/pong和两个完整M C缓冲。
BQ先提交startup两个面板再DeQue A，后续K panel预取；完成K后一次Fixpipe写完整M，GM窗口/slot/partial、任务、workers、baseM/N/window/nSplit及finalizer保留。
Vector仍使用已正式通过的bounded宽窗消费者，其函数体逐字未改；其它manual路径未改。
L0A容量相较父半M实现增加到两份完整M K panel；查询实际容量，不足回退。L1总A/B容量、L0C总字节保持不变。
示例M128/N128/BK128：L0A=64KiB，L0B=64KiB，L0C=128KiB。A1完整K1536=384KiB+B1=64KiB，含4096reserve可容纳示例512KiB L1。
示例不是正式shape/plan/SoC。显式pins及所有容量门槛保留，没有新增GM或改变输入。

## 官方依据与 BF16 处理

[CANN9 Load3D](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00170.html) 支持A2/A3的A1→A2，typed LoadData3DParamsV2的enTranspose规定为half类型、A2目的操作数。
本次使用half类型的LoadData3DParamsV2，源/目的LocalTensor通过ReinterpretCast<half>访问原16位数据；FP16/BF16都不执行Cast或数值运算。
BF16整矩形转置按原始16位bit重新排列，Mmad仍读取原T类型的A2/B2并FP32累加。文档并未直接声明BF16的enTranspose支持；本次不是以BF16类型调用该指令，硬件BF16结果需正式验证。

Load3D参数：L1 feature map 1×round16(K)，channelSize=round16(validM)，mStartPt=K panel起点，mExtension=round16(validK)，kExtension=round16(validM)，1×1 filter/stride/dilation，enTranspose=true。
原NZ的K×M矩形整体转成M×K ZZ，补零仍由原ND2NZ和ManualZeroNZTail处理。
固定公开8.3源码 `load_to_l0a_loadInstr.h::TransLoadDataToL0` 的Load3D分支同样交换M/K方向并置enTranspose=true；不是安装CANN9 header证明。

## 验证

`python3 tools/validate_fullm_transpose.py`

- 160个raw-bit物理矩形：所有65536种16位模式确实经过转置读取；与旧逐M16 Load2D寻址的结果逐bit一致。包括长K pitch、K offset、M80和尾块。
- 420抽取实际producer执行：延迟MTE2、物理NZ/ZZ/ZN/MMAD/Fixpipe、所有C及补零、有效Max(N)再Sum(M)、多task/batch/shard、window1/2/4/5/8、K8非16尾块、全负、events/queues资源收支通过。
- 每K panel恰好一次A矩形Load3D、一次B bulk Load2D和一次完整M MMAD；A/B读取量不增加，BQ copy次数等于MMAD次数。有效M足够两半时，MMAD和Fixpipe次数相对手写父版减半；这些是调用数，不是速度。
- 9216真实Vector消费者抽取执行回归：延迟GM→UB、双AIV credit、释放后立即1e30覆写GM、不同消费顺序、N尾、全负与序号wrap通过。
- production/TUNING各1400 host模型、各1000选择，全部计划字段/workspace/blocks与query-block保持一致（仅dual不同），pins、低容量、K对齐边界回退通过。
- `python3 tools/validate_fullm_transpose_public_tiler.py --source /private/tmp/ascendc-api-adv-review`：未修改公开真实8.3 tiler，production/TUNING各1400/1000通过。

CPU MMAD使用小整数→float、Load3D为明确的布局语义模型，MTE1/MMAD/Fixpipe同步执行；不是硬件指令、完整异步流水或真实BF16精度仿真。
API相容性、真实BF16 reinterpret搬运、正式精度和性能：PENDING。

## 正式计划

kernel SHA `f0b3908378015b9a98fb5eed58337dd7556737e5ae18b79d1e25c19b497a1b09`，270171 bytes。
独立官方模板dry-run只包含kernel.asc，SHA一致；没有改变main/CMake/golden/正式测试/依赖。
结构/资源/物理块模型通过后提交一次，记录ID并查询同一任务至终态；不因等待超时重提，不把CPU命中或调用数作为性能提升。
若无大幅收益则归档，不做Load3D近邻tile参数重交。整体重大提升尚未达成。

## 正式结果：15/15 通过，有单次局部改善

代码 `d2eeb78` / kernel SHA `f0b3908378015b9a98fb5eed58337dd7556737e5ae18b79d1e25c19b497a1b09`。
[提交 6abdd9e6694b590c3cb2e3a9](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abdd9e6694b590c3cb2e3a9) **Pass，CANN编译成功、15/15，precision_ratio全1**。
耗时 `[2.26,4.50,4.34,5.62,5.47,10.97,9.51,65.29,83.05,97.21,87.04,95.41,15.28,12.69,9.10]` μs。
第8点query-block69.03→65.29（单次约5.4%），手写宽窗67.44→65.29；没有同设备重复A/B或实际shape/plan/SoC/profile，不宣称稳定收益、正式路由命中或精确瓶颈。
其它未改路径的单次变化不归因。此kernel的正式15点通过，不证明所有bit模式/所有资源分支均已上板覆盖。
没有活动正式任务；原始JSON本机Git忽略 `artifacts/fullm-transpose-load/`，目录700/文件600。

整体重大提升未达成。保留该通过实验分支作为native producer研究对照，main和query-block通过kernel未改；不提交相近tile参数。
下一结构审查是同一full-M Cube流水对其它输入storage布局的原生ND2NZ/Load3D加载，维持原任务/GM窗口和预算；不得将TT核硬套到非TT数据，也不能擅改其它既有manual/packed家族。
