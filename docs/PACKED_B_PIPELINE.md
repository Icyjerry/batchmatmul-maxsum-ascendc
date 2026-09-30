# case12 packed-B 输入/输出搬运流水

## Evidence → Diagnosis

父分支 `experiment/tiny-tt-query-block`，提交 `3e9b090`，通过kernel代码 `55225cc`。
`bmmms_manual_case12_packed` 已有二深度CQ和既有packed-B GM区域，但pack循环对每个矩形：
读取→CQ DeQue→写出→MTE3完成Fence→Free，之后才开始下一个读取。
因此当前矩形的MTE3与下一个矩形的MTE2不能由这一循环主动重叠。
Cube等待既有全局完成屏障/flag12；预处理耗时进入整条路径启动成本。

## Minimal Fix

新增 `ManualPackBInput`，沿用旧地址、DataCopyPad和尾列清零，返回目标地址和实际K行数。
第一次输入预取后，循环在发起当前输出DMA后先分配另一个CQ buffer并发起下一输入DMA，
再等待当前MTE3完成并Free当前buffer；下一轮DeQue保证输入完成。
不提前Free，不覆盖正在写出的UB源；每个矩形的坐标只解码一次。

`BMMMS_PACK_B_PIPELINE=0`保留原pack循环，默认1。
只修改case12既有预处理；CQ数量、大小、host调度、workspace布局、Cube输入、MMAD、Max/Sum、SyncAll与flag12完全不变。
没有新增输入GM预处理区域，也未改原来全量packed-B路径的规则授权范围。

## API依据

[CANN9 TQueBind介绍](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0147.html)说明TQue以逻辑位置插入队列同步；GM→VECIN对应VECIN队列。
此候选使用原项目已有CQ和Fence API；CQ在预处理后还用于Vector归约，因此保持其原类型和生命周期。
不把文档的另一种TQueBind路径直接套到这条复用CQ上。

## Validation

`python3 tools/validate_packed_b_pipeline.py`：

- 从当前kernel抽取真实helper和宏0/1两条pack循环；各650个执行，325几何配置×输入DMA早/晚完成两种顺序。
- 覆盖Mtile32/128、Ntile32/128/256、N尾列、K40/136/1536尾行、B1/2、1/3/20 Cube workers，包含没有pack任务的AIV和只一个任务的AIV。
- 模型输出DMA延迟读取UB数据到MTE3完成Fence；Free/覆写正在使用的buffer会失败。
- 新模式两个CQ buffer同时存活，未来输入DMA在当前输出DMA未完成时发起；原模式无此重叠。只验证指令发起顺序，不报告硬件带宽或加速比。
- 输入原始16bit字保持，packed-B逐字与独立ND切片oracle一致；所有目标含补零位置唯一writer、尾部guard不变，queue无遗留，完成前不得Free。
- 去掉新增helper并选择宏0后，kernel与父版本逐字节一致：host、Cube、归约、flag、资源和其它路径未改。

这是带延迟DMA的CPU语义模型，不是CANN模拟器；不模拟硬件真实queue事件分配、乱序流水、缓存或BF16计算。
CANN9编译、正式15点精度和性能：提交前PENDING。

## 下一条动作

独立正式模板只替换kernel，dry-run核对SHA，CLI提交一次流水候选并观察同一ID至终态。
记录精确kernel SHA、15点误差状态/耗时；没有实际shape/plan/profile不声明某点命中或稳定提速。
若无明显收益，保留本分支并恢复父版，不继续预取深度或pack矩形相近参数提交。
独立设备可对比宏0/1，分别测pack阶段和Cube阶段、MTE2/MTE3重叠、冷启动与稳态median/p95；A2/A3分开。
