# 完整 K A 驻留的宽窗口消费

## 证据与假设

父分支 `experiment/manual-fullk-m` / `90be0c7`，kernel `1d2ff79` 正式15/15通过，但第8点69.03→68.73μs，没有明确收益。平台没有actual shape/plan/profile，不能确认命中。
抽取实际host的1400网格中，旧dual1的1000配置只有16为W2；另外984为W4/5/6/8，全部被父候选W≤2排除。
因此这次不是调整tile或split参数：保持父完整K Cube producer，解决manual整窗双UB无法容纳原宽窗口的问题，使同一A驻留架构覆盖原宽窗。

## 改动与不变量

- 仅kernel.asc：新增ManualFullMReadC/ManualFullMConsumeWindow，只有M_FULLK模板分支使用。
- CQ由两份半M×完整window改为两份半M×单baseN块，UB分配不随window增长。
- 对完整K producer发布的窗口，只Wait一次ready；首两N块预取，然后每块DeQue/Max/Free并发起后续块。
- 最后一次有效N块DMA发起后在PIPE_MTE2发布credit；两个AIV均完成后才允许producer覆盖slot。释放以后仍可从各自私有CQ进行Vector归约。
- 无有效行的第二AIV也按相同窗口等待并释放，没有错误读取或遗漏credit。
- 每块只归约有效N尾列，maxima初始化负无穷、跨完整N shard累积；沿M和跨N分片归约仍使用原partial/finalizer。
- 原Cube producer、其它manual模板分支、旧消费者与finalizer字节未改；任务/tiler/block数/GM system-prefix/partial/ring总分配保持父query-block计划。
- host允许原W1..8，原B1/TT、M/N/K≥1024、dual1/kSplit1/baseM64/128等条件和所有资源过滤保留。只有dual1→29，未改原window、baseM/N、nSplit或workers。

新CQ字节 `baseM*baseN*4`；MQ/RB共20*baseM，finalizer reserve原样。A1/B1、双L0A/B、四L0C资源不变且使用实际平台容量。
示例M128/N128/W8：CQ由512KiB需求降至64KiB，但GM窗口仍为原8 tile；这是分配量，不是加速预测。
K1776 round16可在512KiB L1中容纳两个64行A及两个B面板和4096reserve；K1784 round16→1792资源不足时回退。例子不是正式隐藏shape或SoC。

## 验证

`python3 tools/validate_fullk_wide_window.py`

- 420真实producer抽取执行：NZ/ZZ/ZN、完整K点积、每个Fixpipe C/补零/GM窗口偏移、A/B读取次数、队列/event计数。包括宽窗口4/5/8、M/N/K8尾块、多个任务/batch/shard及全负。
- 9216真实消费者抽取执行：W1..8、baseM64/128、baseN32/64/128/256、非对齐N尾、无有效行第二AIV、多window序号wrap、不同N shard起点及全负。
- Consumer模型延迟GM→UB DMA；核对每次地址/步长/有效cols与两缓冲容量，两个AIV各Wait/Release一次且发布credit前必须发起所有N块读取。
- 两个AIV的最后DMA均完成即用1e30覆写整slot，后续Vector仍与独立oracle相符，防止早释放或释放后从GM读取。模型在窗口之间轮换AIV顺序；不是完整硬件异步调度仿真。
- production/TUNING各1400实际host配置，与query-block父版所有Schedule字段（仅dual除外）、block数、system/总workspace完全相同；各1000选择，对照父full-K版本16。低容量、pins、布局/batch/longK和L1对齐边界回退。
- `python3 tools/validate_fullk_wide_public_tiler.py --source /private/tmp/ascendc-api-adv-review`：未修改公开真实tiler算法，固定revision c7dfa2d901a314e1ae69e9cef850057593f2a58b（8.3.T9.0.B066），production/TUNING各1400配置、1000选择通过。外部平台/日志/tiling存储为shim；不是安装CANN9 tiler。
- 既有tiny TT700实际源码模型、production/TUNING各360选择及30量化FP64对照另行通过。

CPU整数MMAD、float Vector语义、事件元数据与公开tiler不等于真实BF16精度/CANN9/hardware性能。当前没有任何新NPU性能结果。
旧validate_manual_fullk_m.py针对父版的逐字AIV断言，不适用于这次新增消费者；使用本页的新工具，父源码/模型仍保存在对应Git分支。

## 正式验证

kernel SHA `af0d52b9c2e8f34fd43c5df4577a0d9f8d2adf456b7f57c5cbb642904ab170fc`，270486 bytes。
独立官方模板dry-run仅kernel.asc，SHA一致；未修改main/CMake/golden/正式测试/依赖。
这次解决已证实的宽窗口覆盖缺口，完成源码模型后提交一次，以正式CANN编译/15点精度/latency判断其实际效果；不得把1000/16选择比当作速度提升或正式覆盖率。
若无明显收益归档，恢复query-block，不继续同一架构近邻tile参数试交。整体重大提升仍未达成。

## 正式结果：通过，未取得大幅收益

代码 `9cfb159` / kernel SHA `af0d52b9c2e8f34fd43c5df4577a0d9f8d2adf456b7f57c5cbb642904ab170fc`。
[提交 6abd5fdd694b590c3c8b955d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd5fdd694b590c3c8b955d) **Pass，CANN编译成功、15/15，precision_ratio全1**。
耗时 `[2.19,4.06,4.32,5.60,5.22,10.44,10.11,67.44,84.25,97.75,87.94,96.56,15.80,13.19,9.00]` μs。
第8点query-block69.03→67.44 μs（单次约2.3%差异），没有证实稳定/大幅收益；其它路径单次变化不归因。没有actual shape/plan/SoC/profile和重复A/B，不宣称新路由命中。
没有活动正式任务。原始JSON本机Git忽略 `artifacts/fullk-wide-window/`，目录700/文件600。

后续源码审查确认公开父Norm具有窗口内完整K A缓存。真实tiler1000 dual1计划中824每shard只有一个window，手写跨shard A驻留对它们没有理论读取量优势；实际cache方法2024生命周期模型通过。
详情 [NORM_FULLK_CACHE_AUDIT.md](NORM_FULLK_CACHE_AUDIT.md)，仅公开8.3源码，不冒充安装CANN9或NPU流量证据。
本架构归档，恢复query-block，不继续full-K驻留/window/tile近邻参数试交。整体重大提升仍未达成。
