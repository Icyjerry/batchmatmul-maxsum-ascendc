# 接手状态 · 2026-10-01

## 当前工作状态：恢复 query-block，通过版未并入整 K 驻留候选

分支 `experiment/tiny-tt-query-block`；kernel代码 `55225cc`，SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，逐字不变。
手写整K M驻留的窄窗/宽窗两次候选正式均15/15通过，但无大幅收益，源码/模型保留独立分支。当前仅同步结果文档和可独立运行的父Norm缓存审查工具，main未并入候选。
没有活动正式任务；准确SoC/shape/plan/profile仍未返回，整体重大提升未达成。

**下一条可执行动作**：审查A2/A3 L1→L0 TT加载的实际指令参数与MMAD发起循环。父库窗口内full-K A缓存已由公开源码确认，不能再据每N tile重读A提出相同驻留方案。
以源码/真实header/example证明矩形/transpose加载能力，构建源/目的物理块地址模型；不能使用仅Atlas350的LoadData2DV2，不能重复已否定的普通MDL、NZ回调、Load3D非转置、full-A/window近邻参数试交。
缓存审查可在本分支运行 `python3 tools/audit_norm_fullk_cache.py --source /private/tmp/ascendc-api-adv-review`。其它候选CPU工具需要切换其实验分支。
详见 [NORM_FULLK_CACHE_AUDIT.md](NORM_FULLK_CACHE_AUDIT.md) 和 [FULLK_WIDE_WINDOW.md](FULLK_WIDE_WINDOW.md)。

## 最新：宽窗口完整 K 正式通过，无大幅收益；父缓存审查改变方向

分支 `experiment/fullk-wide-window`；代码 `9cfb159` / kernel SHA `af0d52b9c2e8f34fd43c5df4577a0d9f8d2adf456b7f57c5cbb642904ab170fc`。
[提交 6abd5fdd694b590c3c8b955d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd5fdd694b590c3c8b955d) **Pass，CANN编译成功、15/15，precision_ratio全1**。
第8点69.03→67.44μs，单次约2.3%不足以证明稳定/大幅收益。其它点不归因；无actual shape/plan/SoC/profile。没有活动正式任务。
CPU420 producer、9216消费者，以及fake/public真实8.3 tiler production/TUNING各1400 host配置（1000选择）通过。
详见 [FULLK_WIDE_WINDOW.md](FULLK_WIDE_WINDOW.md)，原始结果本机Git忽略 `artifacts/fullk-wide-window/`。

**新增诊断**：公开真实tiler1000个dual1计划均有完整K A缓存，824每shard只有一个window；抽取真实Cache Hit/Free/Reset等方法的2024窗口模型证明同窗后续N tile命中已有K面板。父库并非每N tile重复读取A，该优化对多数合成计划没有理论读取量优势。
这是公开8.3源码证据，不是安装CANN9/profile；见 [NORM_FULLK_CACHE_AUDIT.md](NORM_FULLK_CACHE_AUDIT.md)。
下一动作：归档本分支、恢复query-block通过kernel；研究A2/A3 L1→L0 TT的加载指令与MMAD发起开销，先核实实际API和物理布局。不能重试只Atlas350支持的LoadData2DV2或已否定Load3D/full-A/window参数结构。
整体重大提升尚未达成。

## 最新：手写 full-K 两半 M 正式通过，宽窗口覆盖存在缺口

分支 `experiment/manual-fullk-m`；代码 `1d2ff79`，kernel SHA `fa88b68c61ec22fdaa050f75df5aaa61aba187854476d5d462d21ac59327c1d1`。
[正式提交 6abd58a2694b590c3c88d669](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd58a2694b590c3c88d669) **Pass：CANN 编译通过，15/15，precision_ratio 全部 1**。没有活动正式任务。
耗时 `[2.21,4.16,4.28,5.54,5.33,10.35,9.56,68.73,84.13,97.61,87.17,95.93,15.05,12.72,9.71]` μs。
第8点对照69.03→68.73 μs，没有明显收益；无实际shape/plan/profile及重复A/B，不能确认新路径命中。
158 producer CPU 执行及 production/TUNING 各1400 host配置（16选择）通过，与正式证据分别报告。

覆盖审查发现：同一1400网格，旧dual1共1000配置，其中984的window为4/5/6/8，被候选window≤2限制直接排除。例B1/M1024/N1024/K1024 TT原M128/N128/W4；B1/M1025/N1025/K1032为W5。这是抽取真实host/fake tiler控制流证据，非实际NPU或隐藏case路由。
下一动作：独立覆盖修复分支，实现bounded N-tile Vector消费者，保留原宽GM窗口/任务及两半M A驻留producer；检查双AIV窗口credit、最后DMA后释放、尾块及UB资源，完成实际源码模型后才考虑正式候选。
详见 [MANUAL_FULLK_M.md](MANUAL_FULLK_M.md)。原始结果本机Git忽略 `artifacts/manual-fullk-m/`。整体重大提升尚未达成。

## 当前工作状态：恢复query-block通过kernel

当前分支 `experiment/tiny-tt-query-block`，kernel代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，未改变。
本次仅同步库内完整K M预载的源码反例与研究文档。完整候选、真实公开tiler/host及外K模型保留 `experiment/fullk-m-preload` / `863c6ae`。
该候选因模型同步反例停止提交，没有活动正式任务。下一动作是下面描述的手写A预取协议研究；整体重大提升尚未达成。



## 最新：完整K库内M预载被外K同步审查否定，未提交

分支 `experiment/fullk-m-preload` 的候选 `1b278c9` / SHA `0c37471e6b6b703bda9735fef64dd47523def338c2f338d6000d6f17d80bbdec` 已归档，**不得直接提交或并入通过版**。
新增完整实际ReduceKMultiIter模型：16个A完整K/B非完整K配置复现一次Async、两次Await，补上此前只检查预载谓词的模型缺口。
这是固定公开8.3源码与标准队列元数据模型反例，不是安装CANN9缺陷的设备证明。未发起正式提交；没有活动评测ID。
资源模型和host128选择不能证明整个库同步正确，详见 [FULLK_M_PRELOAD.md](FULLK_M_PRELOAD.md)。

下一动作：恢复query-block通过kernel，独立研究手写完整K A ping/pong和下一M预取；明确B K面板释放以及下一M只等待一次，复用现有manual AIV/GM ring。
先核对现有manual与归档paired-M源，不能复制公开库上述partial-B等待顺序；没有新GM通路许可。该手写方案未实现、未验证，整体重大提升仍未达成。



## 当前：完整 K 的 M 方向预载候选待正式验证

分支 `experiment/fullk-m-preload`，kernel SHA `0c37471e6b6b703bda9735fef64dd47523def338c2f338d6000d6f17d80bbdec`。
库基本M减半、基本N覆盖整个既有窗口，完整K A双缓冲提前读取下一M块；现有GM ring、任务、AIV与finalizer字节保持一致（仅Matmul配置选择改变）。
公开真实tiler与抽取host：production1775/TUNING1779配置、各128选择；2304实际公开preload谓词/尾块/延迟转移执行通过。700 tiny源码回归通过。
详见 [FULLK_M_PRELOAD.md](FULLK_M_PRELOAD.md)；这些是公开8.3 CPU源码证据，安装CANN9编译/NPU性能精度PENDING。
下一动作：独立官方模板dry-run、正式CLI一次并记录ID，查询同一ID至终态。没有收益则归档此架构、恢复query-block。整体重大提升仍未达成。



## 当前：恢复 query-block，通过版未并入 packed-B 流水

当前分支 `experiment/tiny-tt-query-block`，通过kernel代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`。
packed-B双缓冲实验正式15/15通过但无收益，保留 `experiment/packed-b-pipeline` 的源码、宏0/1各650延迟DMA模型执行与正式结果；这里仅同步结果文档，kernel恢复原样，没有活动的正式任务。

下一条明确动作：[MTE2_PRELOAD_REVIEW.md](MTE2_PRELOAD_REVIEW.md)。已核对CANN9的GetSpecialMDLConfig支持A2/A3 M方向完整K预载及DoubleBuffer条件；先查询公开真实tiler和preload源码，区分库baseM64与现有GM窗口128行，检查完整K、depth/step/DB/L1/L0C所有条件。
这不是此前普通MDL或单M块N-session方案；不能只开配置而没有下一M块，也不能硬改depth字段不核对总容量。尚未实现或取得此方向设备结果。
整体重大提升仍未达成，不继续packed-B或resident-B相近变体提交。

## 2026-10-01 · packed-B 双缓冲正式通过，无收益

代码 `c763281`，kernel SHA `119f145b81270e2994cd686bb4c621f58c48367be8629b921e6f8705b69813b4`，[正式提交 6abd423a694b590c3c7ee13d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd423a694b590c3c7ee13d) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.34, 3.89, 4.14, 5.54, 5.29, 10.64, 10.16, 68.97, 83.48, 99.95, 88.57, 97.14, 16.18, 13.58, 9.78]` μs，合计519.65 μs，父通过版511.66 μs。
第12点95.91→97.14μs，没有收益。只改已有case12 pack阶段，其余kernel未改，不归因其它点变化。
没有实际shape/plan/SoC/profile或重复A/B，不能证明此正式case命中新流水或判定具体退化原因。
宏0/1各650实际源码延迟DMA模型执行通过；完成真实CPU发起顺序重叠、晚释放UB源保护，但不构成硬件加速证明。
保留 `experiment/packed-b-pipeline` 的源码/模型/结果，恢复 `experiment/tiny-tt-query-block` 通过kernel；不提交预取深度或pack矩形相近变体。
原始JSON本机Git忽略 `artifacts/packed-b-pipeline/`；详见 [PACKED_B_PIPELINE.md](PACKED_B_PIPELINE.md)。整体重大提升尚未达成。

## 当前：恢复 query-block，通过版未并入新 B 驻留实验

当前分支 `experiment/tiny-tt-query-block`，通过kernel代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`。
完整B驻留实验已结束，15/15通过但没有明显整体收益；代码及296实际producer/consumer模型保留在 `experiment/resident-b-column`。
当前仅同步实验结果文档，kernel恢复原样；没有活动的正式任务。

下一条明确动作：审查case12既有packed-B预处理的双缓冲。当前 `bmmms_manual_case12_packed` 的AIV pack循环在每个矩形的MTE3后立即Fence，再FreeTensor，然后才读取下一矩形；cq已经有两个buffer但没有pack输入预取。
先按实际队列/事件生命周期实现前后矩形的MTE2/MTE3重叠，仍只用已有packed-B区和cq；保留全局完成屏障/flag12及原Cube计算。不得增加新的输入GM通路或据DMA调用数声明收益。
这项预处理流水尚未实现，不是已验证提速；整体重大突破仍未达成。

## 2026-10-01 · 完整 B 驻留正式通过，无明显整体收益

代码 `c9bfb58`，kernel SHA `280ab900d186365fb999d4bc83fc04109aa89baeaf54cfaa0b06d9b5f9e96e2d`，[正式提交 6abd3e5d694b590c3c7d644c](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd3e5d694b590c3c7d644c) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.1, 4.35, 4.27, 5.53, 5.54, 10.59, 10.1, 68.03, 85.04, 99.18, 88.75, 96.85, 16.24, 13.34, 9.21]` μs，合计519.12 μs，父通过版511.66 μs。
第8点69.03→68.03μs，单次约1.5%差异不证明稳定收益；其余路径未修改，变化不能归因。
没有实际shape/plan/SoC/profile或重复A/B，也不能证明新路由命中；本结果只证明此kernel通过15点。
完整B N块驻留L1、N外M内、多个M块UB Max状态及按列核心分组已实现；296个抽取producer和两名consumer模型、production/TUNING各480host配置（各384选择）通过。
保留 `experiment/resident-b-column` 为结构对照，恢复 `experiment/tiny-tt-query-block` 的代码 `55225cc`；不继续相近分组参数提交。
原始JSON本机Git忽略 `artifacts/column-b-residence/`，详见 [COLUMN_B_RESIDENCE.md](COLUMN_B_RESIDENCE.md)。整体重大提升尚未达成。

## 当前工作起点：恢复 query-block 通过版

当前分支 `experiment/tiny-tt-query-block`，kernel仍为代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，正式15/15通过，第4点5.66μs。
矩形Load3D候选已完成正式评测，未见明显收益，保留独立分支；此处只同步结果文档，没有并入其算法改动。
下一条可执行动作：审查大TT输入ND2NZ的实际K流水/缓冲生命周期，寻找能减少重复输入搬运或重叠Scalar开销的新结构；先以当前源码和官方API排除已有失败路径，不继续Load3D/MDL/session相近变体提交。
精确隐藏shape、路由、SoC和profile仍缺失；不能将第8–12点的耗时变化归因到某种计划。整体重大提升尚未达成。

## 2026-10-01 · 矩形 Load3D 正式通过，无明显收益

代码 `c4d591b`，kernel SHA `8bf5cf4568efe55df1793a30cef649a4ec29e2849027e29e0aeb93ca0e7ad0ac`，[正式提交 6abd38b5694b590c3c7aac99](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd38b5694b590c3c7aac99) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

逐点耗时 `[2.14, 4.11, 4.35, 5.67, 5.27, 10.57, 9.61, 68.95, 83.02, 97.13, 86.78, 97.74, 15.1, 13.02, 9.1]` μs，合计512.56 μs，父版511.66 μs。
第6点10.57→10.57，第12点95.91→97.74，未见明确收益；其余单次差异不能归因，没有实际shape/plan/profile或重复A/B。
六个非转置A/B调用点使用typed Load3Dv2，CPU宏0/1各2888真实块布局检查通过。
这次正式结果证明当前kernel通过15点，不证明所有加载分支命中或全部支持范围已完成设备覆盖。
保留分支 `experiment/rectangular-load3d` 为反例；后续恢复 `experiment/tiny-tt-query-block` / `909294b` 通过kernel，不继续此加载结构的相近参数提交。
原始JSON本机Git忽略 `artifacts/rectangular-load3d/`；详见 [RECTANGULAR_LOAD3D.md](RECTANGULAR_LOAD3D.md)。整体重大突破仍未达成。

## 2026-09-30 · 一次 A 整理与双 query 正式结果

代码 `55225cc`，kernel SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，[正式提交 6abd3263694b590c3c776446](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd3263694b590c3c776446) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.32, 3.75, 4.19, 5.66, 5.2, 10.57, 9.6, 69.03, 83.27, 97.45, 87.37, 95.91, 15.07, 12.72, 9.55]` μs，合计511.66 μs。第4点相对原通过版8.08→5.66 μs（1.43×），相对单行Vector首版6.01→5.66。其余kernel未修改，其它点的单次差异不能归因；合计时长不是正式分数，且未经过同设备重复A/B，整体重大突破仍未达成。实际shape/plan/profile未取得，不声称新路由命中。

本分支作为后续结构研究起点，保留 `experiment/manual-splitk-tiny` 与 `experiment/tiny-tt-vector` 对照；不继续Gather或query块大小相近参数提交。下一动作审查手写Cube A/B rectangular LoadData是否能用A2/A3的真实矩形加载API减少逐行指令，此API/设计尚未核实。CPU700实际源码执行、production/TUNING各432host尝试、30量化FP64对照通过，与正式证据分别报告。原始JSON本机Git忽略 `artifacts/tiny-tt-query-block/`。

## 2026-09-30 · 单 AIV 小 TT 首版正式结果

代码 `a3c65a4`，kernel SHA `4bef4346c0e746711b41ca936510b05b319ee18f09752b2414d767d1ab453b29`，[正式提交 6abd2f7e694b590c3c75d2b6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd2f7e694b590c3c75d2b6) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.14, 4, 4.32, 6.01, 5.77, 10.62, 10.26, 69.43, 84.84, 98.39, 88.22, 96.78, 15.83, 13.32, 9.1]` μs，合计519.03 μs，对照保留版517.73 μs。第4点8.08→6.01 μs（1.34×），有局部收益，整体仍无明显提升。未取得实际shape/plan/profile及重复A/B，不声称路由命中或稳定加速。其它点的单次变化不能归因于本算法。首版CPU700个实际kernel执行、production/TUNING各432个host尝试和30个量化数值对照通过。

保留该独立分支，不并入main。下一假设：首版每M行单独Gather与归约屏障，改为一次A UB整理、两M行批量点积和归约；这项查询块重排尚未实现/验证，不是再调同一路径tile参数。整体大幅提升未达成。原始JSON本机Git忽略 `artifacts/tiny-tt-vector/`。

## 当前：恢复较快通过版，配对 M 实验无整体收益

代码 `d4b9044`，kernel SHA `c6cca6ba9a120336ab4548b7f6898dd6b793291cc0b6adea0ff20d5ad86a00b3`，[正式提交 6abcc39a694b590c3c3ada93](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcc39a694b590c3c3ada93) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

逐点耗时 `[2.27,3.90,4.07,7.82,5.30,10.60,10.05,69.57,84.77,99.51,88.07,96.27,15.87,13.10,9.53]` μs，合计 **520.70 μs**，对照保留版517.73 μs。第8点67.80→69.57、第11点88.16→88.07，没有整体收益；未取得实际shape/plan/profile及重复A/B，不能证明路由命中或具体退化原因。CPU172 producer和production/TUNING各360代表host组合（120选择）通过，与正式精度证据分开。

本分支保留代码、模型与失败对照，不继续同一结构相近参数提交。当前恢复 `experiment/manual-splitk-tiny` 的通过kernel，SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`；审查小矩阵的启动、同步与归约分工开销。整体大幅提升仍未达成。原始JSON在本机Git忽略 `artifacts/paired-m-breuse/`。

## 最新：独立 MDL shard 正式通过，无收益

`experiment/mdl-shard-pipeline` / `df0e049`，kernel SHA `9cf72c174b5ef077db5e8c06826df39718fe926d10efc86391f88e6a5359751e`，[正式提交 6abcbaf3694b590c3c353072](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcbaf3694b590c3c353072) **CANN编译通过、15/15 Pass**。独立MatmulImpl从Norm改MDL，host显式匹配并保留K面板分组step/depth/DB；96个host和384个抽取producer/consumer配置通过。第8点67.80→70.86、第11点88.16→89.29 µs，合计517.73→527.49，无收益，不替换最快保留版。详情 [MDL_SHARD_PIPELINE.md](MDL_SHARD_PIPELINE.md)，原始JSON在Git忽略 `artifacts/mdl-shard-pipeline/`。实际shape/plan/profile未取得，不声称路由命中或确切瓶颈。

后续审查已执行：80组公开真实tiler查询的stepM/N均为1，不能把强制step1称为已确认缺陷。A2/A3 CO2映射GM且V220无直接L0C→UB能力，不套用C310路径。见 [INPUT_PIPELINE_REVIEW.md](INPUT_PIPELINE_REVIEW.md)。下一条明确动作：从最快通过版实现大K TT配对M producer，使两个独立C共享每个B K面板，复用现有manual AIV/ring/finalizer；该设计待实现，不是已测优化。CPU工具 `inspect_public_matmul_tiling.py` 可重建80查询，源码固定公开8.3版本，不是installed9.0。后续起点恢复 `experiment/manual-splitk-tiny`；不继续相近MDL/session/output参数提交。整体大幅提升仍未达成。

## 最新：库内建 NZ 流水正式通过，无整体收益

`experiment/builtin-nz-stream` / `fcbf29b`，kernel SHA `895be634247274f702cfbebaba858c8087a309c0554cd44977c178ced77d9225`。[提交 6abcb535694b590c3c317c3e](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb535694b590c3c317c3e) **CANN编译通过、15/15 Pass**。在独立AIC stream engine上采用库内建 GM NZ C/GetTensorC，无DataCopyOut回调；AIV直接NZ DMA和树形Max。ND/NZ实际producer/consumer抽取各432配置通过，host各96检查通过。第8点相对最快通过版67.80→66.40、第11点88.16→89.04 µs，没有整体收益，不替换较快版本。没有实际shape/plan/kernel/profile，不能声称新路由命中或稳定提速；本次正式任务未出现之前callback的运行错误，不代表callback故障已修复。

代码、模型、正式结果已推送独立分支，说明 [BUILTIN_NZ_STREAM.md](BUILTIN_NZ_STREAM.md)，原始JSON在Git忽略 `artifacts/builtin-nz-stream/`。后续起点恢复 `experiment/manual-splitk-tiny`，kernel SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。**整体大幅提升仍未达成。**

下一条可执行动作：审查官方Matmul TT输入的 CopyCubeIn/LoadData 和实际tiler对应的 L1/L0 K 分块、cache/repack成本；优先取得准确plan/profile的同设备A/B，不继续相近会话或输出格式参数提交。独立MatmulImpl已在候选中编译通过，可用于后续结构研究；不得将public8.3源码等同于installed9.0 header。

## 最新：独立 AIC 库会话流式交接通过，无明显提速

`experiment/cube-stream-sessions` / `c7b004e`，kernel SHA `9b2a01d71abffcc4aa0ae7e04793a91ceb0f2ef172d73c06c7f369aa3367e471`，[提交 6abcb222694b590c3c2f8de6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb222694b590c3c2f8de6) **编译通过、15/15 Pass**。TT 完整K原dual=1路径在新dual=26改用独立 MatmulImpl，对整个 N shard 做一次会话，逐 tile 顺序写现有 ND 双槽 ring；AIV取消KFC对象和flag9。ND尾块按实际cols紧凑stride读取。第8点67.80→67.89、第11点88.16→88.96 µs，合计517.73→519.13，无明显收益，不替换较快通过版。CPU路由96配置、producer/consumer抽取384配置通过，真实shape/plan/profile未取得。首版有启动GM地址static_cast编译错误，最终复用现有workspace变量修正。

研究发现：官方开源 `8.3.T9.0.B066` 的 dual-master IterateAll 内部调用 mul.End，外层 End 为空；也禁止逐tile Iterate/GetTensorC与LocalTensor输入。该版本不是CANN9精确header，但说明原“移除外层End保留缓存”假设缺乏依据。详见 [CUBE_STREAM_SESSIONS.md](CUBE_STREAM_SESSIONS.md)。后续从此已通过API路径研究**库内建 GM NZ 输出**和直接NZ归约，避免此前失败的自定义回调；不提交相近会话参数变体。大幅整体提升仍未达成。

## 最新：大 TT 非对齐 A 常驻正式通过但退化

`experiment/ragged-tt-resident-a` / 代码 `4507c59`，kernel SHA `d327a0632c87335a657528005b25eb9a9578086c3691f602947159baa30f2b3d`。[提交 6abcaadc694b590c3c2ada90](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcaadc694b590c3c2ada90) **CANN 编译通过、15/15 Pass**，但第 8 点 67.80→94.15 µs，15 点合计 517.73→540.33 µs。候选对 BF16 B1 TT 大矩阵尾块改用完整 A 常驻 L1、padded K 物理跨度的 LoadData2D 和既有 ND ring/归约；无新增 GM 通路。CPU production/TUNING 各 465 个计划检查、231 组物理块及独立数值模型通过。正式通过 case 无 msg，隐藏 shape/实际 kernel/plan/profile 未取得，不能断言退化来自具体模块。

失败代码、模型和结果已推送独立分支，详细说明 [RAGGED_TT_RESIDENT_A.md](RAGGED_TT_RESIDENT_A.md)，原始 JSON 在 Git 忽略 `artifacts/ragged-tt-resident-a/`。当前后续起点恢复通过版 `experiment/manual-splitk-tiny`，kernel SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。大幅整体提升仍未达成。

下一条可执行动作：核对官方 Matmul 的 A cache/片上输入源码与 CANN9 实际 API，分析如何保留库的 K 流水同时减少重复加载或 GM handoff。不要重复提交本次 resident TT 相近参数，也不要据 CPU 读取次数声称优于库；NZ callback 故障仍按下文单独保留。

## 最新：紧凑 NZ ring 正式失败对照，当前恢复通过版

`experiment/nz-ring-max` 保留失败对照；最新代码 `21dae0d`，kernel SHA `34faa07f6d898386f0dec10da0a68fc0f013a67152529b650e9fd1d6e3644912`。大 TT 完整 K 的 dual=1 路径接入 Matmul 输出回调，L0C 以 NZ 写到原 GM ring，AIV 直接 NZ Max，保留窗口/分片/slot 容量和 finalizer。库 `enSequentialWrite=true` 写同一起点，因此回调显式按 curN 定位。抽取回调的 90 组单位/窗口检查、1,344 组尾块/负值地址模型通过，但三个正式版本均 **CANN 编译通过、第 8 点 Runtime Error 507015**：首版 `9c7a006`、恢复 ND 库调度的 `5de5952`、编译期 baseN 的 `21dae0d`。[最新提交 6abca4d0694b590c3c26d435](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abca4d0694b590c3c26d435) 前 7 点 Pass，后 7 点 Skipped。已证明第 8 点命中新 BF16 TT kernel，未得到底层异常地址；两项隔离未解决故障，不能归因于库 C 格式或用户标量传递。详情 [NZ_RING_MAX.md](NZ_RING_MAX.md)、[PERF_LOG.md](PERF_LOG.md)。

恢复通过版 `experiment/manual-splitk-tiny` 作为后续优化起点，kernel SHA 仍为 `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。NZ 方案没有可计分结果，不合并最快版，暂不提交相近变体。下一条动作：取得 CANN9 实际 callback/Fixpipe header 与 `slog`/AiCore 异常 PC/GM 地址；使用独立设备 harness 分别验证 producer NZ 输出和 AIV 消费，再决定是否继续该路径。也可从通过版继续研究另一项减少 Cube/GM 主成本的结构方案；大幅整体提升仍未达成。

本机原始失败日志已保存到 Git 忽略的 `artifacts/nz-ring-max/`，避免 `/tmp` 被清理后丢失。CLI 及公共 helper 副本在 Git 忽略的 `artifacts/tooling/cannjudge-submit/`；会话仍使用用户原有 `~/.cannjudge/session.json`，未复制凭据。新提交前使用此 CLI 下载独立正式模板并 dry-run。这些本机 artifact 不随 GitHub 分支交接，接手者可按提交链接读取结果。

## 宽 N 尾块 A 常驻实验：正式通过但退化

`experiment/ragged-wide-resident-a` 代码 `3c54597`，kernel SHA256 `60b86f28e0c98731f7c54f944dd3095d1af31e1c8a02de2dd090b8a92b67828a`。[正式提交 6abbd297694b590c3cc7d861](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbd297694b590c3cc7d861) **15/15 Pass**，但第 14 点相对其手写 Split-K 父版 13.20→13.70 µs；15 点合计 517.73→526.30 µs，按页面最优时间估算均分 40.967→40.209。该实验扩展 BF16、短 M、宽 N、短 K 的 A 常驻手写 Cube 路径，使 M/N/K 非对齐尾块可走该路径；host 路由/资源回退和 10 组独立 CPU 尾块数值模型通过。正式平台未给出隐藏 shape、实际 plan、msprof，因此不能证明第 14 点命中新增分支，也不能判断退化原因。**保留失败对照，不替换较快的 `experiment/manual-splitk-tiny`。** 完整结果见 [PERF_LOG.md](PERF_LOG.md)。

## 最新：小 TT 长 K 手写 Cube Split-K 正式通过

`experiment/manual-splitk-tiny` 代码 `568f4eb`，kernel SHA256 `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`，已推送私有 GitHub。[正式提交 6abbcdc5694b590c3cc4cac3](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbcdc5694b590c3cc4cac3) **15/15 Pass**，每点 `precision_ratio=1`。第 15 点相对直接 batch 父版 **13.10→9.20 µs（1.42×）**，15 点合计 522.78→517.73 µs；按页面最优时间估算均分 40.774→40.967，仅是估算而非平台公布分数。第 8 点 69.69→67.80 µs，但其它点也有单次波动，不能归因于新路径。候选只为 B=1、FP16、双转置、M/N≤128、K≥4096 且满足片上内存条件的现有 Split-K 计划启用 8 路手写 Cube，现有 finalizer 先合并 K 再执行 Max(N)→Sum(M)。

`python3 tools/validate_manual_splitk.py` 的 host 路由/资源回退与 48 组独立 TT 数值模型通过；正式 CANN 编译和 15 点精度通过。精确 SoC、隐藏 shape、实际 plan、msprof、重复测量仍 **PENDING**。最初代码 `654347a` 的[提交 6abbccee694b590c3cc43d25](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbccee694b590c3cc43d25) 因混合类型同一条 `auto` 声明而 Compile Error；`568f4eb` 只修正该声明后重新评测。下一条动作是取得第 15 点实际 shape/plan 与同设备重复 A/B，判断这条新路径的稳定得分，再决定是否并入 main；目前保留独立分支。逐点结果见 [PERF_LOG.md](PERF_LOG.md)。

## 大 TT 双 N tile 共用 A 面板的正式结果

`experiment/tt-panel-pair` / `7b4d477`，kernel SHA256 `802026fd4949d0aa1c5622576080964a8a3734267181a7ed4019303a979084e0`。[正式提交 6abbc9e9694b590c3cc258f3](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbc9e9694b590c3cc258f3) **15/15 Pass**，但第 8 点 69.69→69.65 μs、第 11 点 87.63→88.86 μs，没有明显收益。该实验恢复并接入历史经 CPU 物理块模型检查的 `RunPanelCube`：两个相邻 N tile 的 L0C 独立累加器共享 A 的每个 K 面板；`validate_cube_panel.py` 456+584 个模型执行、`validate_tt_panel_plan.py` 代理形状/资源回退通过。正式平台未暴露隐藏 shape、实际 plan 或 msprof，不能证明第 8/11 点实际命中该分支，也不能归因瓶颈。保留为对照，**不替换较快分支**。详见 [PERF_LOG.md](PERF_LOG.md)。

## 交换 TT 计算方向的正式反例

`experiment/swapped-tt-column-max` / `345e335`，kernel SHA256 `40c5bed863c6ab9411783479c0b6921268815449434728a523b5d2a4e9fff5a0`。[正式提交 6abbc6d9694b590c3cc08c48](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbc6d9694b590c3cc08c48) **15/15 Pass**，但第 11 点相对当前较快版 **87.63→152.24 μs**，第 8 点 69.69→70.47 μs。新核把 TT 物理输入交换为 FF Matmul、在 AIV 沿原 N 做列 Max、最后 Sum(M)；独立 CPU 模型 228 组通过。实际隐藏 shape/plan/profile 未提供，不能确定每点具体路径或退化来源。此架构保留为反例，**不替换较快分支**；不要通过同一路径的小参数微调继续提交。详见 [PERF_LOG.md](PERF_LOG.md)。

## Matmul 会话复用实验结果

`experiment/norm-session-reuse` / `56ea172`，kernel SHA256 `a1c60ea079ca3c75656dc271b806d2e66268ddfc19df8f3cb70e641565cd7bb3`。[正式提交 6abb3973694b590c3c72900c](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3973694b590c3c72900c) **15/15 Pass**。改动把 dual AIC 的 `mm.End()` 从每个 C window 移到 worker 循环结束，以尝试跨 window 复用 Matmul 内部 A/B 缓冲。相对当前较快的直接 batch 归约版，第 8–12 点耗时从 `[69.69,84.83,98.04,87.63,96.02]` 到 `[70.32,84.16,97.85,88.12,96.80]` μs，有升有降，未形成大幅收益。该分支保留为失败对照，不替换较快分支。精确 SoC、实际 plan、msprof 和重复测量未取得。完整结果见 [PERF_LOG.md](PERF_LOG.md)。历史段落中“尚未删除每窗口 End”只描述当时状态，本实验已验证该改动。

上述 TT 交换方向已实测退化，随后双 N tile A 面板复用也未提速。下一条动作是优先定位第 8/11 点的实际 shape、Matmul 计划和 Cube/Vector/MTE profile，再设计另一项能减少完整计算路径成本的架构候选；没有这些指标时不得把两个反例归因于某个硬件单元。

## ragged B 常驻实验结果

`experiment/tall-ragged-resident-b` / `a6c5a29`，kernel SHA256 `92a92db0c01b93223056fc70b0cc062ebbf0eefc39b8020954e498bde370b62c`。[正式提交 6abb3724694b590c3c71cfe4](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3724694b590c3c71cfe4) 15/15 Pass，但第 13 点相对直接 batch 父版 15.74→15.93 μs，没有提速。该路径只针对历史探针推断的 B=1、M=8192、N=64–127、K=128–248、FP16 FF 非对齐类，尝试将完整 B 在每个 worker 的 L1/L0B 中复用；CPU padding/任务归属模型 384 行通过。平台未暴露实际 shape/plan/msprof，无法判断该分支是否命中或为何未见收益。保留为失败对照，不合入当前较快分支，不再提交同类微调。详细逐点结果见 [PERF_LOG.md](PERF_LOG.md)。

## 256 行 tall/manual tile 结果

`experiment/tall-m256` / `eae79e4` 的 [正式提交 6abb3203694b590c3c6fc554](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3203694b590c3c6fc554) 15/15 Pass，但目标第 13 点 15.74→16.98 μs、估算均分 40.774→40.660，未见收益。kernel SHA256 `60f31c815eb2dca302ad8c2c11b586c1b57c43727ba22a14b036053195b45c93`。独立排程/缓冲模型144组通过，但无实际 plan/msprof，因此不能确定其退化原因或真实 tile 命中。保留此分支作失败对照，不合并 main。见 [PERF_LOG.md](PERF_LOG.md)。

当前三个新正式实验均未达到重大突破：直接 batch 归约约 +0.38 估算均分；其上的消费者流水相对父版仅约 +0.02；256 行 tile 退化。后续停止以相近小变体频繁调用正式评测，优先取得精确 SoC/plan/msprof 或建立可在设备侧 A/B 的独立验证入口。保持通过版 `experiment/direct-batch-reduce` 与队友原版 `experiment/teammate-c6-c10-c12-v3` 可随时检出。
## 双缓冲消费者实验结果

`experiment/dual-consumer-overlap` 从直接 batch 归约版派生，代码 `bea6de0`，kernel SHA256 `d55ac07aa939ffa856a7f786fade29b6179d6dd226c77842d9e6868aaa560e3f`。[正式提交 6abb2eeb694b590c3c6db357](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2eeb694b590c3c6db357) 15/15 Pass。双 VECIN 预取、MTE2 完成后提前归还 GM ring、UB 树形 Max 的组合只将第 8 点 69.69→68.53 μs、估算均分 40.774→40.794；其它点有波动。该方案未达到用户的重大突破要求，不合并 main，也无需重复提交类似微调。完整验证在 [PERF_LOG.md](PERF_LOG.md)。

短 M/宽 N 路径已核查：专用计划把 64 个 N tile 分给约 16–20 核，增加分片不能降低每核最多 4 tile 的任务量。官方 CANN 9 [SetOrgShape](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0651.html) 文档支持同一 Matmul 对象复用，[WaitIterateAll](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0641.html) 文档要求显式等待异步完成，因此尚未删除 `bmmms_dual` 每窗口的 `End`。

## 当前直接 batch 归约实验

`experiment/direct-batch-reduce` 从 15/15 通过的队友版 `21dfc40` 独立派生；代码 `45efd1f`，kernel SHA256 `e06ce50abb27dc9315d1b64437c2086473ffe53295c843c39aa61aa3feadefc2`。用户已授权官方 CLI 提交，但要求只有较大突破才继续提交。

- [正式提交 6abb2b8d694b590c3c6b89a2](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2b8d694b590c3c6b89a2)：15/15 Pass；第 5/7 点 6.53→5.26、11.69→10.12 μs，第 4 点 8.48→8.33 μs。按页面最优时间估算均分 40.39→40.77，仅 +0.38；第 8/10 点单次用时上升，合计时间反而 519.71→522.78 μs。完整逐点数据见 [PERF_LOG.md](PERF_LOG.md)。
- 本地 1,458 组历史探针范围排程/缓冲模型通过；正式评测证明当前源码在 15 点精度通过。精确 SoC、隐藏 shape、实际路径、msprof 和重复测量未取得。该实验保留为小幅有效候选，不并入 main。
- 下一条动作：从本分支或队友版继续研究能明显降低 Cube/GM 主耗时的结构性方案；只有形成重大收益候选再调用 CLI。保留失败的 `experiment/large-tt-manual` 作为反例；不要把其中的 TT 强制路由合入本分支。

## 当前候选：队友 C6/C10/C12 合并 v3

- 工作分支 `experiment/teammate-c6-c10-c12-v3`，导入提交 `d9d74eb`。用户提供的 `kernel_c6_c10_c12_merged_v3.asc` 已逐字节原样导入 `kernel.asc` 并推送；244979 字节，SHA256 `ce2e12e425883fc207d0dd5d08a7a72b485c439b65fbbb8db33165905aecce52`。不要把附件中的性能注释当成本轮测量。
- [正式提交 498576](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3dbb694b590c3cd8f427)，2026-09-28 18:13:15 CST：**Pass，15/15**，每点输出错误占比 0.00%。平台保存的 `kernel.asc` 再次复制回本地并与原件逐字节比对，SHA 一致。
- 相比上个已通过的提交 498385，页面两位小数耗时有 13 点降低、2 点升高；15 点合计 599.65→519.71 μs。按页面展示的最优用时和题面公式估算均分约 34.80→40.39，仅用于同页对照，不是平台公布分数。完整逐点数据见 [PERF_LOG.md](PERF_LOG.md)。
- 旧 CPU host 检查脚本依赖上一版 `Schedule`、`TuneConfig` 结构，对新原件不适用；执行时因字段缺失而编译失败，不能记为候选精度失败或 CPU PASS。正式评测已给出 15 点正确性结果。精确 SoC、case shape/layout/dtype、实际 plan、编译命令、msprof 和重复测量仍未取得。
- 下一动作：保留此实验分支为目前正式评测较快的候选。优先识别第 1/2 点的小幅退化和第 8 点剩余较大最优差距，再针对一个可复现的形状及设备路径提出单一优化假设；设备记录须绑定本 SHA。未经额外验证不把新候选合并进 `main`。

## 上一个通过版本：CANNJudge 498385

- 分支 `experiment/performance-structure-fixes` 的 `kernel.asc` 已提交到 [BatchMatmulMaxSum 正式评测](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3abb694b590c3cd6cbe3)：提交 ID **498385**，2026-09-28 18:00:27 CST，最终状态 **Pass，15/15**，每点输出错误占比均为 0.00%。
- 提交页面保存的 `kernel.asc` 经复制回本地逐字节比对，216575 字节、SHA256 `1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`，与本分支文件一致；提交对应代码提交 `a3c1f7d`。逐点耗时和平台显示的最优用时见 [PERF_LOG.md](PERF_LOG.md)。
- 平台标注 CANN 9.0.0，但该页面未给出精确 SoC、15 点 shape/layout/dtype、实际 plan、msprof 或编译日志。这些仍待单独采集。旧段落中的“正式15点 PENDING”是提交前历史状态。
- 下一步先定位耗时比最高的第 5、8、4 点及第 13–15 点对应的 shape/layout/dtype 和实际路径，再按单一假设开实验分支做同机对照；不要根据隐藏 case 的编号猜形状。

## 最新：性能结构四项集中修复

当前分支 **`experiment/performance-structure-fixes`**，代码 `a3c1f7d`，父 `3ca0d7c`。四项均已落到kernel：完整连续A切片合并LoadData、显式tile/window/ns优先且不静默回退、取消新producer的默认自动替换、C事件延至各自首次覆写前获取。合并单级/两级K重复主循环，单N组不再启用无收益常驻。

- 默认 `BMMMS_CUBE_PANEL=0`；显式1/2/3仍可测试修复后的新内核。默认AIC/AIV预处理移除panel调用分支。此前文档“默认3”现为历史记录。
- SHA256：`1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。
- CPU物理块456+584配置及完整切片反例、严格pins/预处理、host planner、缓存、N/K拆分和UB模型通过。原反例LoadData从8次降到1次；不代表耗时8倍改善。
- CANN9/NPU/正式15点/latency/msprof仍 **PENDING**，云端按用户指示暂缓；源码修复完成不等于设备性能问题已实测闭环。
- 交接与下一条设备执行动作：[PERFORMANCE_STRUCTURE_FIXES.md](PERFORMANCE_STRUCTURE_FIXES.md)。历史规则未被臆造的成本模型替换，main只更新接手指针。

## 历史审查：性能结构与实验堆叠

用户要求检查代码是否出现屎山倾向；已审查当前4044行kernel，未修改算法。见 [PERFORMANCE_STRUCTURE_REVIEW.md](PERFORMANCE_STRUCTURE_REVIEW.md)。实际planner CPU复现了自动producer覆盖旧窗口、单N组无收益常驻导致TX1 LoadData 1→8次，以及显式bn/ns/window被case profile回写。另确认两个C累加器跨组的Fixpipe→MMAD依赖；净性能影响仍PENDING。复现：`python3 tools/audit_plan_precedence.py`。下一步优先修连续A切片和pin优先级，再处理C释放等待及统一路径选择，先收敛已有代码。当前实现分支和SHA如下。

## 最新：L1/L0 两级 K 分块

分支 **`experiment/hierarchical-k`**，实现 `d64d0c1`，父版本 `73ed463`（Cube 面板复用）。本次 kernel 新增103行、删除18行，将L1传输粒度与L0计算粒度分开。

- `panelL1K` 按真实L1容量选 `2*panelK` 或 `4*panelK`，最多512；B1四缓冲保存当前/下一对面板，A继续双缓冲或整块常驻。L0双缓冲和两个C累加器沿用父版，K累加顺序不变，无新增GM通路。
- `BMMMS_L1_K_PANELS=0/1`，默认1；不满足容量时自动保留父版。固定 `BMMMS_CUBE_PANEL=2` 或3再比较H0/H1，避免把不同优化混作收益。
- SHA256：`771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。
- CPU物理块模型：456次父producer执行、584次两级K执行通过；实际C、读取字节数、L0搬运量及MMAD次数一致，DMA调用减少。额外覆盖112的非2次幂K块及344尾块。
- host模型六种宏组合各production/TUNING通过76,424主网格及额外容量边界；默认模式选中11,992次，resident 9,964次，两级K 7,714次（含额外检查）。宽松tiler及同步事件模型不构成CANN/设备验证。
- **CANN9编译、FP16/BF16设备精度、正式15点、性能 PENDING**。四B队列实际事件分配、异步生命周期、TX1切片增加的LoadData指令成本须上板确认；减少DMA调用不是减少读取字节，更不是实测速率。
- 下一条执行动作：[HIERARCHICAL_K.md](HIERARCHICAL_K.md)。按用户指示云端暂缓；GitHub保存当前候选，main仅更新接手指针。

## 父版本：Cube 面板复用与 L1 常驻

用户要求更大幅度核心改造；当前分支 **`experiment/cube-panel-reuse`**，实现 `bc3f7cf`，父版本 `48e37c7`。新增255行kernel，重组K/N循环和片上缓冲生命周期。

- 新生产者 `RunPanelCube`：两个N tile共享A的GM→L1及L1→L0A搬运、两个C在L0C完成K累加；可容纳时整个A面板常驻L1跨N组复用；B保持双缓冲。共享已有GM环形通路及Vector最终归约。
- `BMMMS_CUBE_PANEL=0/1/2/3`：父路径 / 单tile新内核 / 双tile复用 / 可选L1常驻，默认3。查询实际L1/L0A/L0B/L0C；容量不符、只有一个N tile/shard或显式TUNING pins保留旧路径。自动替换不是已测最优策略。
- kernel SHA256：`e440e1b3d915ba61f696059cd3af0efdee6b8d087aee04ef7a49ba40ef2a637b`。
- `python3 tools/validate_cube_panel.py`：444配置物理块/完整C值/事件计数/读取量模型通过；`python3 tools/validate_host_plan.py`四档production/TUNING主网格76,424配置通过。宽松fake tiler与同步CPU指令模型，不能冒充CANN或NPU精度。
- 新内核1→2对成对tile的A读取和L0A加载减半，resident时A每个任务从GM读取一次；**不代表相对旧Matmul库的流量降幅或速度收益**。
- CANN编译、正式15点、FP16/BF16设备精度和性能 **PENDING**。云端仍按用户要求暂缓；下一条执行单：[CUBE_PANEL_REUSE.md](CUBE_PANEL_REUSE.md)，直接构建P0/P1/P2/P3，记录实际plan和SoC；重点确认事件池、双L0C和resident重用。
- 旧dual消费候选仍继承；满足准入的形状现在走新manual生产者及Fold Max。main仅更新接手指针，未合并未测kernel。

## 父版本：设备端 dual 消费流水与 tile 归约

用户要求继续推进核心优化，云服务器测试仍按用户要求暂缓。当前分支 **`experiment/dual-consumer-fold`**，父版本 `35a86eb`；代码提交 `324a6a0`（预取/提前归还槽位）、`00a91b4`（tile 内树形 Max）。不是仅修改 host 参数。

Kernel SHA256：`8f848c4869d90f0da7a955b14b457a47ecc9a09c41e515c95efa17562916d29e`。

- `bmmms_dual` / `bmmms_dual_mdl` 两条完整 K 路径接入同一设备消费 helper。既有两个 UB tile 预取下一块；最后一次 GM 读取发出后，以 PIPE_MTE2 完成依赖提前归还槽位并发下一窗口握手。无有效行的 AIV 仍参加同步。
- 在当前私有 UB tile 内按 64 lane 分组树形 Max，最后一次 WholeReduceMax 更新行最大值。256 列时横向归约 4→1、Vector 屏障 8→4；属于源码调用数，**不是实测加速比**。不额外分配 UB/GM；host plan、Cube 算术、partial/finalizer 保持父版本。
- `BMMMS_DUAL_PIPELINE=0/1/2`（默认2）；`BMMMS_DUAL_FOLD_MAX=0/1`（默认1）。前者从历史独立流水实验移植，后者是新实现；六组组合可分别归因。
- `python3 tools/validate_dual_pipeline.py` 已通过：每组76,800窗口配置、34,816归约边界配置，另3,840抽象双AIV协议调度。0/0的CPU指令轨迹与父循环一致；源码逆替换确认其它kernel/host/缓冲预算未改动。这些不是SDK或设备模拟。
- **CANN 9.0.0 编译、A2/A3 精度、正式15点、msprof/性能全部 PENDING。** Matmul内部flag 9、真实队列同步和在VECIN上原地Max必须设备确认。
- 下一条执行入口：[DUAL_CONSUMER_OPTIMIZATION.md](DUAL_CONSUMER_OPTIMIZATION.md)。云端恢复后按六档固定plan对照执行；检查实际dual路径，split-K/tiny/manual不进入本次helper。
- 已知问题修复全部继承。原样用户最优tag、main kernel及其它历史分支未替换；不要把当前候选称为设备最优。

以下为历史记录，旧的“等待设备才继续”节奏已由用户继续本地优化的指示取代。

## 当前工作：已知问题集中修复

用户最新指示是“直接把已知的问题全部解决”，并明确云服务器执行“先不用管”。当前分支 `experiment/known-issue-closure`，从 `677d882` 派生；不要继续按独立轮次割裂本地缺陷收敛，也不要为此编造设备结论。

Kernel SHA256：`d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。

- 本地已修复earlySum漏写、Tune缓存陈旧、manual冗余系统workspace、低核dot split除零；增加scratch用途变更时的库前缀重置，去掉首次分配前无必要的stream同步。继承先前UB、输出及分块修复。
- 全部R1–R18审计和生命周期/异常/题面边界的明确结论见 [KNOWN_ISSUES.md](KNOWN_ISSUES.md)。其中无实测依据的性能规则仍标待判定，不能说全部性能问题已解决。
- CPU：76,424个host plan配置（真实控制流、stub tiler）、49,152个finalizer遍历配置；缓存11字段、context隔离、scratch换用途及4类失败通过。既有N/K拆分和UB模型通过。**不等于CANN编译/设备精度通过。**
- 统一清单 `known_issues_cases.csv` 共151shape/1,208组合。云端恢复时按 [VALIDATION_REQUEST_known_issues.md](VALIDATION_REQUEST_known_issues.md) 执行，不要求对方重做算法设计；目前按用户指示暂缓。
- 本地复现：`python3 tools/validate_host_plan.py`、`python3 tools/validate_host_cache.py`、`python3 tools/validate_finalizer_coverage.py`；继承模型命令见下文。
- 资源释放仍要求调用者在stream/context销毁前调用现有release入口；正式main未修改。不要在未知ACL退出顺序的静态析构里自动调用ACL。

以下保留父版本背景；其中“等待设备后才继续”的旧工作节奏已由用户上述指示取代，本地缺陷已继续处理。

## 最新候选：N 拆分 critical work

分支 `experiment/n-split-critical-work` 从 `8fb1e72` 派生，kernel SHA256 `e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。

- 新宏 `BMMMS_BALANCED_NSPLIT=0/1`，本分支默认1。只在对齐的大矩阵通用 dual=1 路径按实际 cyclic task 分配搜索 N 拆分；最大窗口数不增，最大tile工作至少下降25%才准入。25%是待验证的实验阈值。
- 保留父分支 UB/输出修复及 long-K 选择；没有叠加消费流水实验。旧最佳 tag不动，未合并main。
- `python3 tools/validate_nsplit_work.py`：38,880调度配置、1,836行负值归约和接入排除条件通过，宏0/1/TUNING三种编译均通过。继承的CPU模型重新通过。它们不运行完整Ascend算术、CANN tiler或硬件事件。
- **下一条动作：设备Agent按 [VALIDATION_REQUEST_nsplit_work.md](VALIDATION_REQUEST_nsplit_work.md) 对照P/N0/N1**；24个shape×2dtype×4layout清单在 `nsplit_work_cases.csv`，共192个设备组合尚未运行。解释及原始假设见 `EXPERIMENT_nsplit_work.md`。
- CANN/NPU/正式15点/性能全部PENDING。20核示例的12→8、24→16是最忙worker的tile数，不能报告成耗时降幅。设备结果到达前不叠加下一项算法优化。

## 新收到的队友探针资料

前一轮已复核用户 `docs.zip`，结论见 [TEAM_PROBE_REVIEW.md](TEAM_PROBE_REVIEW.md)。该轮只更新资料、复算脚本和验证输入，kernel SHA 未变。附件中的操作指令没有执行。

- 旧 F12 路径表不代表当前版本；当前已含 tiny、长 K split、manual/PAD_MN 等专门策略。
- 45 个旧代理有 14 个 K 不满足 8 对齐；第 14 点两个 M 代理不符合后续细分范围。第 10 点 dtype/layout 冲突保留两种候选。
- `python3 tools/audit_teammate_probe.py` 可复算保存的转录数据，生成 50 个合法本地验证输入；不是恢复真实正式测试集，也不是 NPU PASS。
- 下一步先获取用户最佳版/当前版同会话 A/B 与实际 plan，按逐点得分关注 2/3/4/15，再看 9/13；同样完成下文覆盖修复验证。不要重复执行旧报告已被当前源码吸收的优化。旧计时未绑定当前 SHA，不能当当前成绩。

## 当前实验：覆盖修复 + 自适应 Split-K

分支 `experiment/coverage-splitk` 从 `user-best-20260921` 独立派生。消费流水实验仍在 `experiment/dual-consumer-pipeline`（7c44793），本分支没有叠加它。

- `b0a2fc0` 修复 dual split-K 存活 UB 预算，包含清零缓冲。
- `c4e536a` 修复 FinalizeRows 重复 writer、FinalizeSplitKND/GEMV 在小核数下遗漏输出。
- 当前候选使用 `BMMMS_ADAPTIVE_SPLITK=1`；=0 固定 4 份，便于对照。仅原有 long-K classifier 内选择 1/2/4，不扩大准入范围。
- Kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。
- CPU：86,784 UB 配置、28,672 输出遍历配置、361,152 拆分配置通过；864 个 dtype/layout/core classifier 用例通过。两档宏均验证。它们不是完整 Ascend 精度/性能测试。
- 35 个合法 shape / 280 个 dtype+layout 组合的设备清单在 `coverage_cases.csv`，尚未运行。
- **CANN 编译、正式 15 点精度、NPU 性能：PENDING。** 没有将 CPU 代理成本解释为提速。

### 下一条可执行动作

设备 Agent 按 `VALIDATION_REQUEST_coverage_splitk.md` 构建 U/F/A0/A1，先测 UB 回归和 B=64、小可用核数的输出覆盖，再测自适应拆分的精度/latency。来源及尚未覆盖的路径见 `RESEARCH_coverage_splitk.md`；结果写 PERF_LOG。

本地复现：`python3 tools/validate_splitk_coverage.py`、`python3 tools/validate_finalizer_coverage.py`。当前不用旧 deferred 或 pipeline 模型证明新候选。

以下为原样用户最佳版本背景，不是对当前实验 kernel 的描述。

## 当前起点

用户最新提供 `kernel(2).asc`，明确称为“目前的最优版本”。本分支 `experiment/user-best-20260921` 的 `kernel.asc` 是该文件的**逐字节原样导入**，3,492 行，192,577 字节。

- 固定快照 tag：`user-best-20260921`。
- SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 不包含本 Agent 的 v1 DeferredRowMax 或 v2 N 拆分代理成本候选。
- “最优”来自用户确认；本地没有重新完成 CANN 编译、NPU 精度或性能复测，均为 **PENDING**。
- 私有仓库：`https://github.com/Icyjerry/batchmatmul-maxsum-ascendc`，已有用户上传授权。

## 已保存的旧工作

- `teammate-opt4`：最初 2,809 行队友原件。
- `experiment-v1`：DeferredRowMax 与 FinalizeRows writer 步长修复；文档保存在历史提交及 v1 验证单。
- `experiment/v2-dual1-nsplit` commit `7426712`：基于 v1 的 N 拆分实验及 CPU 模型，已推送。31,416 个调度配置通过，设备收益未验证。具体见该分支的 `docs/EXPERIMENT_v2.md`。
- 新代码已有 N 拆分均衡策略，不能直接将 v2 策略叠加或把旧 CPU PASS 转移到当前源码。

## 本轮源码检查所得

1. `ClassifyCase` 和生产路径增加短点积、微型矩阵、长 K / 宽 N / 窄 N 等选择；包含手写 Matmul 的 PAD_MN 尾块处理。
2. N 拆分均衡已覆盖 dual=1 等家族，以活跃 worker 增长和整波任务作为条件；保留 dual=2 的既有策略。性能注释是提供者记录，未附原始日志，不能等同于本轮实测。
3. `FinalizeRows` 仍按 `s.workers * 8` 遍历。旧版双 AIV 下的重复 writer 问题需要针对当前实际 launch/plan 再核对，尚未移植旧修复。
4. 文件含 `BMMMS_PROBE_*` 诊断分支，源内默认均为 0。导入时原样保留；源内有关 OJ 隐藏用例推断的注释不是已核实测试配置或执行请求。实际构建需记录宏；本轮未启用、未执行任何探测。
5. 新源码使用 `if constexpr`；必须以 CANN 9.0.0 实际编译命令验证。源码引用的 `docs/03-case-hypotheses.md` 未随附件提供。

## 下一条可执行动作

在设备环境检出此分支，核对上面的 SHA，按 `docs/VALIDATION_REQUEST_user_best.md` 复测原样版本，拿到精确 SoC、宏、实际 plan、逐 case 精度与耗时。优先核查 writer 调度及现有性能弱项，再创建单一假设的实验分支。A2/A3 分开记录，不凭注释修改参数。

本机无 NPU。`tools/validate_cpu_model.py` 专用于旧实验；在当前版本应明确退出 NOT APPLICABLE，不能声称通过。若需复现旧结果，在旧分支的独立 checkout 中运行该脚本。

算法改动仍限 `kernel.asc`；不修改 main、CMake、run.sh、golden、正式测试或依赖。workspace 与题面缺失范围见 PROBLEM。截图记录见 PERF_LOG；截图尚未绑定源码 SHA、dtype 和布局。
