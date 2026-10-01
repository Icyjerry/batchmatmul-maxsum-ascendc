# TT 紧凑手动 frame 与直接 tile Max

## Evidence → Diagnosis → Hypothesis

父 `03c3996` 的实现 `5c67d94` 已三次正式 Pass 15/15。三次任务 `6abea942694b590c3c1ff692`、`6abeb052694b590c3c220fa2`、`6abeb132694b590c3c223f34`，同SHA `71ca6095958a372927c27f088bb081c43cff748169ff98e4ef80a2215b4d62c5`。C8 47.24/48.88/48.45，中位48.45，极差/中位3.4%；C13波动9.9%，C14 5.8%。详情 `TT_IDENTICAL_REPEATS.md`。父的末级单屏障比更早父仅观察低2.72%，不能当大突破。

此前 TT fullMN pair、workerMax、NZ 和邻近分块实验都未带来明显收益，现有完整 A1 驻留/矩形 Load3D/B 双 package 流水已经保留，不能重复“首次提出”这些优化。C7和宽N手动frame分别已取得较大正式观察收益。本候选把同样的紧凑入口和显式物理缓冲方式用于已选中的 TT dual33，同时替换该路径的逐 tile 重复归约。

假设：移除本路径 TPipe/queue/dynamic event 大量初始化和逐 tile MQ/CQ 管理，并直接归约当前完整K tile，可能显著减少框架和Vector非矩阵乘开销。FlashAttention-2 中减少非矩阵乘与不必要通信的原则是研究背景（[原论文](https://arxiv.org/abs/2307.08691)，前期已核对），不是 Ascend API 或本轮速度证据。

## 源码范围与实现

仅 `kernel.asc` 新增210行，三个添加区（device入口/helper、host guard、launch override）；移除三个添加区后整个kernel逐字等于 `03c3996`。没有修改 MakePlan、任务/grid、B包大小、GM路径/容量、其它kernel和输入/输出契约，没有改main/CMake/run/golden/正式测试。

- 32byte独立 TTFrameShape，B=1由guard保证。仍按连续M-major tile partition分给原workers，使用原Ntile partials和双slot GM ring。
- A1为完整BM×ceil16K，一旦M tile改变重新装入；B1仍是已有双package预取序列，跨Nt/M边界提前搬运，完整K之后才写C。
- 两份A2/B2和两份C0保持原BK、paddedM/N、MMAD与Fixpipe布局。所有本地事件显式0/1，A1 reader/ready独立2；M_FIX按Cslot分配，C0等FIX_M后才覆写。
- Vector在原两个UB C槽读取有效N，读取完成后按原PIPE_MTE2返回GM信用；每tile用已有SmallRowMaxLaneFold直接生成该tile行Max，没有额外的四组row scratch或Max到另一个MQ。
- row输出也为双slot，MTE3_V保护GMstore的最后reader，V_MTE3按slot；padding初始化负无穷，真实M/N尾mask；零有效行伴随AIV和idle worker仍完成信用和barrier协议。
- 全部AIV在原硬件SyncAll后退休UB，block0复用物理UB做父已经通过的批量Ntile Max与有效M分组Sum，只写4byte y。没有新GM元数据/同步区，没有交换Max/Sum。
- host只在原FullMTilesBatchFits guard内选择，并查询真实AIC/AIV及UB/L1/L0A/B/C、原GM空间；BN128/256、packageK/BK倍数及任务数不符保留原路线，显式TUNING pins保留原路线。

BN128完整tile，旧消费每次2个WholeReduceMax+1个合并Max+1个更新MQ Max，新为1个lane-fold Max+1个WholeReduceMax；BN256旧4个WholeReduceMax+3个合并Max+1个MQ Max，新3个lane-fold Max+1个WholeReduceMax。只是源码API调用数量，lane操作/带宽不同，不是速度预测。

## 同步审查发现与修复

未提交的初版模型报错后发现两处实际协议风险，并在首次native前修复：

1. 单个固定V_MTE3事件可能在两个输出slot并行时过早复用。改为按slot0/1 Set/Wait，旧row的MTE3_V消费证明对应事件已消费。
2. M_FIX只建立M→FIX依赖，不能替代MTE1→MTE2的A1覆写依赖。在M块末次Load3D之后设置A1 free事件2，新M DMA前等待2；初始化/终态配平，不引入全流水PIPE_ALL。

Cube模型的1544K代理原选PK768需要591872byte L1，超过512KiB，host会拒绝；修正为能容纳的PK512并增加fixture容量断言。不是放宽模型/host容量来通过。

## CPU / 静态验证

复现：`python3 tools/validate_tt_manual_frame.py`。

- 304抽取真实producer执行（延迟MTE2/MTE1/MMAD/Fixpipe，延迟和立即Fixpipe两模式）：实际NZ/ZZ/ZN、Load3D/Load2D、完整K和padded C逐元素独立点积核对，K8非16尾、M/N尾、正负/全负、A跨Nt缓存、B包次数、输入不变/GM guard、idle workers和所有flag配平。
- 六Cube负控制拒绝：缺B1最后reader、缺A1最后reader、缺L0最后reader、缺C最后reader、缺Aready、缺完整K的M_FIX handoff。
- 558抽取真实AIV执行，三个引擎优先级、全部AIV真实线程barrier、逐元素UB generation、归还GM后毒化旧slot：保护C/row双buffer、半M无有效行、idle workers、唯一partial和不可变输入、完整Nmax与有效Msum、唯一4byte y及guard。
- 九Vector负控制拒绝：缺C/row最后reader、缺Cready、缺partialready、缺barrier、缺finalDMAready、缺PIPE_ALL、错误M尾、错误N尾。
- production/TUNING各5000实际host控制配置/480选择，Fake CANN tiler；plan/GM不变，实际核数/各片上容量/GM fallback和显式pins。
- scope逆变换逐字恢复父kernel，`git diff --check`通过；独立官方模板其它源码逐字父，dry-run仅kernel，源码SHA如下。

整数CPU不模拟native BF16/FP32舍入、硬件flag与queue分派延迟，也不是完整Cube/AIV co-sim（双方cross-core对端用合成模型）；L1fill同步、部分local WaitFlag在CPU立即驱动依赖队列。负控制有助检出已知缺陷，不能证明所有真实硬件交错。未取得安装CANN9 headers，不以CPU当CANN9编译或NPU性能通过。

## 正式验证请求

分支 `experiment/tt-manual-frame`，kernel354602bytes，SHA `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`。仅新增入口，不含其它未测优化。CANN9编译/NPU精度/性能 PENDING；CPU日志Git忽略 `artifacts/tt-manual-frame/cpu.log`。

commit/push之后正式提交一次，立刻保存ID，只查同ID至终态。必须15/15。重点C8与父三次47.24–48.88/中位48.45对照；若收益小于此观察波动或无收益，不称突破且不提交邻近参数。只有明显结构收益才原样确认一次。记录全部15点，特别C7/C14既有收益和C2不利变化；没有actualshape/plan/SoC/profile，不将桶编号当作路由已命中，不推算实际榜分。

整体冲榜目标仍未完成；main/历史标签不动。

正式任务 **`6abeb39e694b590c3c22e5d7`** 已创建，实现 `a770e64` 已push、kernel/template SHA a5eef105…保持。下一仅查询同ID至终态，不因等待超时重交。CANN9/NPU精度/性能 PENDING。

## Official terminal result: Pass, modest single-run change

Task `6abeb39e694b590c3c22e5d7`, implementation `a770e64`, SHA `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`: CANN compile successful, 15/15 Pass, all precision_ratio=1. Times (us): `[1.99, 2.46, 3.11, 4.12, 5.39, 9.97, 8.16, 46.52, 67.79, 99.14, 88.03, 96.45, 15.49, 11.01, 9.56]`.

C8=46.52 vs three parent runs 47.24-48.88 / median48.45: single-run decrease3.98%, only1.52% below fastest parent. Parent spread3.4%. No large or stable improvement claimed; do not repeat or scan adjacent tile/package parameters. C2=2.46 overlaps old2.42-2.50; previous2.69-2.78 observations cannot establish a stable version cost. C7=8.16 above parent7.75-8.04 and C10=99.14 above parent95.19-98.35 are retained as unfavorable observations. Source unchanged paths do not establish causality for their changes. Actual SoC, shapes, plans, profile and controlled interleaved A/B remain unavailable.

No active official task. Keep this passed structural experiment separate from main; raw JSON ignored at `artifacts/tt-manual-frame/official.json`. Next investigate tiny 16-bit block transpose replacing per-token FP32 Gather/index construction, verify CANN9 TransDataTo5HD and bit/tail/dependency models first. The overall major competition optimization goal remains incomplete.
