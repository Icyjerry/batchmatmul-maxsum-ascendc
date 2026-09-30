# 库内完整 K 的 M 方向输入预载审查

## 已核对的API依据

[CANN9 GetSpecialMDLConfig](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0623.html)
支持A2/A3。`doMTE2Preload=1`开启M方向预载，2开启N方向预载，仅对MDL有效。
M方向要求 `singleCoreK/baseK <= stepKa`，且M方向DoubleBuffer开启；N方向对应stepKb。
`isVecND2NZ`是保留参数，不可用它假设A2/A3有UB→L1能力。

此前独立MDL shard实验使用普通CFG_MDL，不等同于这里的完整K、M方向双缓冲预载。
已有Cube-stream实验扩大N会话但只有一个M tile，也不能直接证明跨M预载无益。
这些已有失败仍需保留；新的设计必须解释不同的输入时序。

## 候选设计（未实现）

保留现有schedule的128行GM C窗口，在库内部以更小M基本块计算，
让一个窗口含至少两个M基本块；完整K的当前/下一A块同时驻留L1，
在当前M块计算期间预载下一M块。继续库的K流水和既有GM ring/两名AIV。
不能只改config而保持singleCoreM/baseM=1，那样没有下一M块可预载。

示例预算，**不是实际隐藏case/tiling**：L1=512KiB，K1536，库baseM64、baseN128、baseK128。
两个完整A块需 `2*64*1536*2=384KiB`；四个B K块需 `4*128*128*2=64KiB`，
共448KiB，另留pipe/元数据余量。L0A/B的128深度双缓冲分别32/64KiB。
相较baseM128的完整A双缓冲768KiB，这个例子说明为何需要把**库基本M块**与**GM窗口M行数**区分。
实际GetTiling的stepKa、depthA1、B缓存、DB与L0C字段必须整体检查，不能只硬改depthA1或stepM。

## 下一条可执行动作

1. 在固定公开tiler源码上查询singleCoreM128/baseM64和原baseM128的完整K/资源字段，并审查MDL preload源码的A1队列、Reset和下一M块时序。公开8.3源码不冒充安装9.0 header。
2. 证明完整K和double-buffer条件满足，且没有内部L1容量越界，再从query-block通过版实现独立候选。保留schedule行跨度、ring容量、输出/归约及显式pins。
3. CPU模型检查新库基本块与原GM窗口的布局、尾块和全负；正式CANN编译/精度/性能另外验证。

尚无此方案代码或NPU结果，不声明性能收益；整体重大提升未达成。
