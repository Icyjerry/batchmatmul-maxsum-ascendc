# 完整 M 流水：四种输入布局与单 C 缓冲

## Evidence → Diagnosis

TT 完整 M 候选 `d2eeb78` 已正式15/15通过，第8点单次69.03→65.29μs；整体大幅收益未达成。
其原生加载只接受TT，不能覆盖其它输入布局的大矩阵。query-block父版的FT/FF resident家族为dual20，TF的已有packed-B家族为dual6；这些计划在MakePlan后段才完成窗口和workspace计算。
因此在MakePlan开头替换dual会跳过父计划的后续调整。新转换放在末尾，只改dual，保留全部其它schedule字段、blocks、system和totalBytes。

## 实现假设

同一个完整M producer直接支持四种存储布局，将L1的NZ输入按原始16位数据搬到A2 ZZ和B2 ZN。对于已有packed-B家族不再执行pack阶段，直接读原始x2；原有pack区域仍分配但不使用，没有新增GM通路。
当两份完整M C超出实际L0C而一份可容纳时，使用单C缓冲，复用前必须等待FIX_M。L0A/B仍双缓冲，GM仍两个slot，Vector消费者逐字未改。
这是布局和流水覆盖扩展，不是更换近邻tile参数。是否降低Scalar/加载和预处理成本只能由正式结果判断。

|输入|物理ND2NZ|L1→L0|
|---|---|---|
|A，TX1=true|K×validM，NZ pitch=round16(K)|整矩形Load3D transpose，K panel起点在mStartPt|
|A，TX1=false|validM×K，NZ pitch=round16(validM)|Load3D无transpose，K panel起点在kStartPt|
|B，TX2=true|validN×validK，NZ pitch=round16(validN)|已有bulk Load2D到B2|
|B，TX2=false|validK×validN，NZ pitch=round16(validK)|Load3D无transpose，到B2的ZN|

full-M模式dual29使用两个C，dual30使用一个C。K panel在baseN256时为64，否则128。每个K panel一次A加载、一次B加载、一次完整M MMAD；每个N块完成整个K以后一次Fixpipe。单C不会增加GM slot或改变跨核credit。
只选择B1、M/N/K≥1024、kSplit1、无earlySum、原dual1/20/6、原BM64/128、BN≤256、window1..8并且真实L1/L0A/L0B/L0C/UB预算允许的计划。显式调优pins保留。

## 官方来源与局限

[CANN9 Load3D](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00170.html)：A2/A3支持A1→A2和B1→B2，B2目的格式为ZN；enTranspose只适用于half源和A2目的。
沿用正式通过TT版本的half类型ReinterpretCast搬运，MMAD仍使用实际FP16/BF16类型，无Cast算术。非转置A/B采用同一16位搬运指令，无整矩形transpose。
固定公开8.3源码和官方CANN9文档是设计依据；公开8.3不是本机安装CANN9。CPU全bit搬运不能证明所有硬件位模式或所有shape精度。

## 验证

`python3 tools/validate_fullm_storage.py`

- A的两种布局各160矩形，对照独立旧Load2D寻址，所有65536位模式确实经过搬运并逐bit一致。
- 2976实际producer源码执行：四种storage、单/双C、M/N/K尾块、K为8但非16倍数、全负、多个batch/task/shard、window1/2/4/5/8、延迟输入DMA及events/queue/资源收支、每个C和有效Max(N)再Sum(M)验证。
- 单C专项BM128/BN256/K1032、1536；正确C槽、完整K及尾块检查。每K panel一次MMAD和A/B加载，BQ copy次数等于MMAD，原始A/B读取量与理论匹配。
- 9216已通过消费者源码回归，双AIV延迟GM→UB、释放后破坏性覆写GM、tails/全负/window wrap；函数体与正式通过父版逐字一致。
- production/TUNING各8064 host控制流配置，各5888选择。所有schedule字段（仅dual归一后对照）、blocks和workspace与完成的query-block父计划一致；低容量和pins回退。
- 代表FT dual20→29 BM128/BN128/W1；FF dual20→30 BM128/BN256/W1；TF dual6→30 BM128/BN256/W1。它们是模型shape，不是正式case已知shape。
- `python3 tools/validate_fullm_storage_public_tiler.py --source /private/tmp/ascendc-api-adv-review`：未修改公开真实8.3 tiler arithmetic，production/TUNING各8064/5888通过。

首次完整脚本的producer和consumer通过后，host测试夹具误引用当前Schedule不存在的旧字段，编译失败；已删除这些测试引用，实际Schedule全部现存字段仍逐项比较，修正后的独立host和public tiler检查均通过。修正后的统一脚本exit0，producer、consumer、production/TUNING host全部通过；最终日志 `/private/tmp/bmmms-fullm-storage-cpu.log`。
模型的MTE1/MMAD/Fixpipe是同步执行，小整数FP32累加；不是硬件异步流水、实际BF16精度或速度证明。

## 正式状态

kernel SHA `3d2904d008155f2e8be3995b13f1295dfce130aac36ad47fbc0f8a9582bcf5f4`，271683 bytes。
独立官方模板 `/private/tmp/bmmms-judge-fullm-storage/project`，dry-run仅kernel.asc且SHA一致。
CANN9编译、正式精度和性能：PENDING，尚未创建提交。
通过模型后仅提交这一结构候选一次，记录ID并查询同一任务至终态；没有同设备重复A/B时只报告单次变化。
如果没有明显收益，保留反例和已通过TT父版，不提交相邻tile参数。整体重大提升仍未达成。
