
## 2026-10-02: complete tiny K8 fold, native PENDING

Terminal6abec94f694b590c3c2a0c34 /04bee91 /SHA4d03162f: CANNcompiled15/15Pass/allprecision1. Timesus `[1.97,4.39,3.23,4.02,5.23,9.79,7.83,47.07,67.91,97.87,88.58,97.45,15.91,10.76,9.54]`. C2regression4.39vsbaseline2.46; no overallgain. Does not identifyactualK/route/profile. Archive fullstorage-native/Brcb/Ktree direction, restore1734f16, no repeats/variants/parameter scan. NewTTproducergranularity audit notyetimplemented; existingfullA/Bpackages/doubleL0/singlebarrier alreadyretained. Rawignored artifacts/tiny-all-k8-fold/official.json; noactivejob, main/tags unchanged, goalincomplete.

SHA4d03162f721a879827d85d8c18c99bd49174cc636acd9b9d8f43567cf3eb29fa/kernel360054bytes, baseline1734f16 plus103lines/three regions; no plan/group/grid/GM change. Adds K40/48/56 excess-to32 fold to batchKtree, exactrawA roundup/DMA/sharedCast offsets. MotivationconditionalhistoricalK32–56, notactualroutehit. Completesalgorithmcoverage, nottile scan.

Production/TUNING each10080 hostcontrols,17616 actualintegerentries (120synthetic512KiB chunkboundaries),5652encodedFP16/BF16 group1/2/3 entries/FP64golden maxAbs9.54e-7/nonzeroRel2.93e-6, ninefaultcontrols includingnonpowerKtail. OneFIFO/softwarecasts notnative. Officialtemplateother7sources baseline/dryrunkernelSHA checked. NativePENDING/nojob yet; onecommitpush/submit/saveID/pollsameID. Clearlargegainonlyconfirm, ifnogain archive fullstorage-nativeKtree direction/restoreretainedbaseline; no furthervariants. See TINY_ALL_K8_FOLD. Goalincomplete/main/tags unchanged.

## 2026-10-02: group-wide tiny K tree, native PENDING

Terminal6abec72a694b590c3c296090 / df36ef3 / SHAeeef7efc: CANN compile successful,15/15Pass/allprecision1. Timesus `[1.94,2.57,3.28,4.03,5.42,9.83,8.03,46.44,69.04,99.12,89.01,97.22,16.41,11.22,9.17]`; no clear C2/C3 benefit versusbaseline2.46/3.11; unfavorableC9/C13 retained, unchangedroutes notattributed. HistoricalconditionalprobeK32–56 exposes currentK32/64 coverage gap, not actualhiddenroute evidence. Next exactK8 excess-to32 fold and rawA padding verification, notparameter scan. RawJSON ignored artifacts/tiny-group-ktree/official.json; no activejob, main/tags unchanged, goalincomplete.

SHAeeef7efc6189e9da80cbe9fae60901b51f7c73e4edc7806b4adbc23532218029/kernel359932bytes; baseline1734f16 plus102lines/threeaddedregions. Previous per-row storage-vector native15Pass but no benefit; this changes scratch to[K,ar,pitchN], all-queryBrcb and commonKtree/repeatedMax. ExampleB1M8N64K64: sourceAdd48→7, Kbarriers48→6, Brcb8→1, Max8→1, Mul8 unchanged. Expandedmemory/stridedwrites may offset this; no latency prediction. No plan/group/grid/GM change; realUB/uint8stride fallback.

Production/TUNING each10080 hostcontrols,7200 actualqueued integerentries (48synthetic512KiB boundaryentries),2292 encodedFP16/BF16/group1/2/3 entries, maxAbs9.54e-7/maxNonzeroRel2.93e-6 againstFP64golden, eightnegativecontrols. OneVectorFIFO/softwarecasts notnativehardware/precision. Templateother7sources parent/dry-runkernelSHA checked. CANN9/NPU gates PENDING; no activeformaljob yet; commitpush then one structural submission, ID/pollsameID. See TINY_GROUP_K_TREE. No small-gain parameter scan, main/tags unchanged, goalincomplete.

## 2026-10-02: storage-native tiny structural candidate, native PENDING

Terminal task6abec499694b590c3c288b4a / code155fbd9 / SHA19cd486e: CANN compile successful,15/15Pass/allprecision1. Timesus `[1.96,2.54,3.16,4.09,5.44,9.85,8.11,45.99,67.78,96.58,88.63,96.92,15.76,11.04,9.30]`. C2/C3 no major benefit vsparent2.46/3.11; TT C8 source-identical45.99vs46.52 only1.1%, no tiny attribution. Archive without repeats/parameter scan; next independently validate group-wide K tree reducing per-M Vector calls. UnknownSoC/shapes/plans/profile; native15sample scope only. RawJSONignored artifacts/tiny-storage-vector/official.json, no activejob, goal incomplete.

From passed1734f16, `experiment/tiny-storage-vector`, SHA19cd486e6a0ffcd4caaa4a644e64853ae994a7c0065deb577ba32184b271f794,359398bytes. Keeps document[K,N], query broadcast and fullK32/64 FP32 column tree before validNMax/Msum; removes documentGather, not another transpose/tile tweak. Source only92lines/three addedregions, no newGM/plan/grid, other7template sources byte-equal parent.

Production/TUNING each10080 hostbyte-boundary controls,8352 actualqueued integerentries,864 encodedFP16/BF16 entries/FP64golden maxAbs9.53674e-7/maxNonzeroRel2.93038e-6 under mixedCPU check, seven negativecontrols. OneVectorFIFO/decodedsoftwarecasts are not native hardware/precision/performance. API900Brcb/stride/PipeBarrier text retrieved. CANN9/NPU precision/perf PENDING; see TINY_STORAGE_VECTOR. Nativejob not yet created; commit/push then one structural submission, pollsameID. No small-gain parameter scans. Prior raw-bittranspose26beaac passednative but C2regressed4.12vs2.46; archived. Main/tags unchanged, goalincomplete.

## Official terminal result: Pass, modest single-run change

Task `6abeb39e694b590c3c22e5d7`, implementation `a770e64`, SHA `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`: CANN compile successful, 15/15 Pass, all precision_ratio=1. Times (us): `[1.99, 2.46, 3.11, 4.12, 5.39, 9.97, 8.16, 46.52, 67.79, 99.14, 88.03, 96.45, 15.49, 11.01, 9.56]`.

C8=46.52 vs three parent runs 47.24-48.88 / median48.45: single-run decrease3.98%, only1.52% below fastest parent. Parent spread3.4%. No large or stable improvement claimed; do not repeat or scan adjacent tile/package parameters. C2=2.46 overlaps old2.42-2.50; previous2.69-2.78 observations cannot establish a stable version cost. C7=8.16 above parent7.75-8.04 and C10=99.14 above parent95.19-98.35 are retained as unfavorable observations. Source unchanged paths do not establish causality for their changes. Actual SoC, shapes, plans, profile and controlled interleaved A/B remain unavailable.

No active official task. Keep this passed structural experiment separate from main; raw JSON ignored at `artifacts/tt-manual-frame/official.json`. Next investigate tiny 16-bit block transpose replacing per-token FP32 Gather/index construction, verify CANN9 TransDataTo5HD and bit/tail/dependency models first. The overall major competition optimization goal remains incomplete.

# 2026-09-30 · 配对 M / B 面板复用首版

## 2026-10-01 · 完整A1/矩形转置/连续任务的N配对正式通过，无收益

代码 `124dc31`，kernel SHA `a7555e313a0bf6bfe34bca301b8769f28c6b127ed85a859292a883a1db33fcc1`，分支 `experiment/tt-fullm-npair`。
任务 `6abe223b694b590c3cd8474e` Pass，CANN编译成功、15/15、precision_ratio全1。
耗时 `[2.07,4.54,4.28,5.46,5.36,10.36,10.19,60.83,83.67,97.80,88.19,96.38,15.67,13.04,9.65]` μs。第8点父59.66→60.83μs，无收益；无actual shape/plan/SoC/profile及重复对照，不归因未改路径或断言A2开销。
440立即+440延迟MMAD实际producer、420旧producer/160 raw-bit layouts、fake host各6912/720/144通过；host/workspace/Vector逐字保持父版。当前设计与旧非驻留/对齐限定N pair有明确区别，但仍未形成正式改善。
无活动任务，归档原始JSON/日志 `artifacts/tt-fullm-npair/`，恢复父通过版；下一检查单B1双K stage，保持L0子块/L1总容量/GM通路，避免继续相近N pair尝试。详情 [TT_FULLM_NPAIR.md](TT_FULLM_NPAIR.md)。整体重大提升未达成。

## 2026-10-01 · TT worker/M UB Max 驻留正式通过，无收益

代码 `34956fe`，kernel SHA `269c7d370b48db80e7da48733f558ea6d6675ac844e4b04878ab4eec077c9b3c`，分支 `experiment/tt-worker-max`。
正式任务 `6abe1ed9694b590c3cd68cc9` Pass，CANN编译成功，15/15、precision_ratio全1。
耗时 `[2.11,4.14,4.41,5.74,5.38,10.72,10.30,59.72,84.31,98.00,89.17,97.46,16.37,13.36,9.60]` μs；第8点父59.66→59.72μs，没有收益，无actual shape/plan/SoC/profile及重复对照，不归因未改路径。无活动任务。
1440实际消费者/稀疏末级、9216原窗口消费者、440producer/420旧producer/160位模式、288稀疏末级、fake/public8.3 host各6912/720/144通过。代理partial份数144→28是真实源码/任务计数，不是性能改善。
归档JSON/日志 `artifacts/tt-worker-max/`（Git忽略），恢复父结构；下一检查完整A1驻留/Load3D/连续任务下的A2跨N复用，避免原样重复旧无收益N pair。详情 [TT_WORKER_MAX.md](TT_WORKER_MAX.md)。整体重大提升未达成。

## 2026-10-01 · TT连续tile任务与并行末级合并正式通过

- 代码 `32c6b1c` / SHA `65e38bb155af9adb068e87dc90c01face21a7cf024d094c54846c5188e9ca120`，正式ID `6abe1a32694b590c3cd3fe15` Pass，CANN编译成功、15/15、precision_ratio全1。
- 耗时 `[2.29,4.22,4.24,5.63,5.33,10.40,9.70,59.66,83.11,96.93,87.29,96.11,15.24,12.75,8.88]` μs。第8点TT种子65.29→59.66（单次8.6%）、query-block69.03→59.66（单次13.6%）；无actual shape/plan/SoC/profile或重复A/B，不声称稳定收益或新路线命中。其它未改路线不归因。
- 连续完整K tile分配、A跨N驻留、全部AIV按M合并N最大值再求和；原partial/ring区域，无新GM/flags。440实际producer、420旧producer/65536bits、288线程barrier/延迟DMA末级，fake/public真实8.3 tiler production/TUNING各6912/720/144通过。
- 保留通过结构，下一独立方向同M相邻N最大值留UB，仅写worker/M区间partial并只合并实际相交worker，避免读未写区域。整体重大提升未达成。

## 2026-10-01 · 窄 N 完整 K 驻留正式通过，无明显收益

- 代码 `7ffb3ff` / SHA `4bf730de204af997b8eca185c2c2ffe72144874f29b4d59e10d33c81dc68672d`，正式ID `6abe0ee6694b590c3ccdd494` Pass，CANN编译成功、15/15、precision_ratio全1。
- 耗时 `[2.18,4.18,4.33,5.55,5.44,10.74,10.32,66.45,84.05,97.90,88.93,96.67,16.04,13.36,9.03]` μs。第13点通过TT父15.28→16.04，无明显收益；其它未改路径不归因，无actual shape/plan/SoC/profile及重复A/B。
- 新完整B L0驻留、A1双queue后续M预取、完整K一次MMAD、尾部补零、原Vector worker流式和；2654 producer，fake/public真实8.3 tiler production/TUNING各5376/504通过。归档实验，不并入main，不重复近邻tile提交；重大提升未达成。
- TT任务审查新增720真实公开tiler代理计划，物理8/20/24/32核各180；未满核分别0/90/120/120，最大tile关键路径/理想均分分别1.4/2/2/1.6。这是源任务计数，非隐藏case路由或NPU延迟；下一结构转向连续tile任务、相邻N的A驻留和原partial Max合并。

## 2026-10-01 · native A / NZ B 组合正式通过，无明显收益

- 代码 `297abe5` / SHA `8e1fbca3a87bc380a174fbc01a181da8c5d8f9a7b02294d9d4f5895b5914942c`，正式ID `6abe05cf694b590c3cc88e53` Pass，CANN编译成功、15/15、precision_ratio全1。
- 耗时 `[2.14,4.34,4.29,5.57,5.50,10.78,10.11,67.19,83.43,98.13,88.21,97.49,16.48,13.26,9.14]` μs。第12点TT父95.41→97.49，NZ-B父96.65→97.49；没有明显收益，无actual shape/plan/SoC/profile或重复A/B，不断言路由/根因。
- 同一接口best_time快照（case顺序）`[1.37,1.83,2.44,3.23,2.33,7.16,3.69,17.32,50.68,68.65,71.25,85.25,5.21,6.08,8.31]` μs。C8/C13/C7当前约3.88/3.16/2.74倍参考，优先级应高于C12约1.14倍。这些数不是同设备A/B或最终得分，接口score字段为0，不能据此声称获得分数。
- 724实际Cube-body模型、原ND/新NZ各2016、fake host各1728/54通过；与正式证据分开。归档 `experiment/packed-nz-native-a`；不再重复这套A/B加载近邻参数提交。整体重大提升未达成。

## 2026-10-01 · packed-B一次Cube块布局正式通过，无明显收益

- 代码 `0ad246b` / SHA `5a420968d478d3428334a42e562bbe3455d413f6db06a60a432c100282ef494a`，正式ID `6abe0163694b590c3cc61e91` Pass，CANN编译成功、15/15、precision_ratio全1。
- 耗时 `[2.18,3.78,4.39,5.62,5.38,10.78,10.17,67.93,83.85,99.64,88.43,96.65,16.28,13.33,9.51]` μs。第12点TT父95.41→96.65，无明显收益；无actual shape/plan/SoC/profile和重复A/B，不断言路由或根因，其它未改路径不归因。
- 原ND/新NZ各2016真实源码布局/延迟DMA执行、NZ全65536bit，fake/public8.3 tiler production/TUNING各1728/54通过。未新增GM/UB分配，队列后半用于预处理输出，SyncAll/flag12未改。
- 保留独立分支 `experiment/packed-b-nz-once`；下一结构组合是保留连续NZ B，使用已通过TT native A矩形搬运，检查A仍按M16发起的成本。资料 `PACKED_B_NZ_ONCE.md`，本机私有原始资料 `artifacts/packed-b-nz-once/`。整体重大提升未达成。

## 2026-10-01 · 完整 M 四种布局正式通过，但第12点退化

- 代码 `d0904f8` / SHA `3d2904d008155f2e8be3995b13f1295dfce130aac36ad47fbc0f8a9582bcf5f4`；正式ID `6abde198694b590c3cb643e2` Pass，15/15、precision_ratio全1，CANN编译成功。
- 耗时 `[2.19,3.81,4.34,5.66,5.22,10.75,10.10,67.69,83.17,98.33,88.18,116.40,15.54,13.23,9.03]` μs；第12点TT父95.41→116.40，单次约22%退化，没有整体收益。无actual shape/plan/SoC/profile和重复A/B，不断言路由或具体根因。
- 四storage原生输入、单/双C、完成父计划后仅dual转换；CPU320矩形全部65536bit、2976 producer、9216消费者和fake/public8.3 tiler production/TUNING各8064/5888通过。
- 归档 `experiment/fullm-storage-layouts`，恢复通过TT父版；旧pack的连续K面板与原GM按完整N跨行读取的差异是待验证解释。有效字节与API调用数下降不能证明带宽收益。资料 `FULLM_STORAGE_LAYOUTS.md`；本机私有原始资料 `artifacts/fullm-storage-layouts/`。整体重大提升未达成。

## 2026-10-01 · 完整 M TT 矩形转置正式通过

- 代码 `d2eeb78` / SHA `f0b3908378015b9a98fb5eed58337dd7556737e5ae18b79d1e25c19b497a1b09`；正式ID `6abdd9e6694b590c3cb2e3a9` Pass，15/15、precision_ratio全1，CANN编译成功。
- 耗时 `[2.26,4.50,4.34,5.62,5.47,10.97,9.51,65.29,83.05,97.21,87.04,95.41,15.28,12.69,9.10]` μs。第8点query-block69.03→65.29（单次约5.4%）、宽窗67.44→65.29；无actual shape/plan/profile及重复A/B，不声称稳定大幅收益或路由命中。
- 一次完整M MMAD、一次A矩形transpose、一次完整M Fixpipe替代两半M/逐M16发起；手写父版调用数消减不是对原库的速度/指令降幅。
- 160矩形实际覆盖全部65536位模式、420 producer、9216双AIV延迟DMA消费者、fake/public真实8.3 tiler各production/TUNING1400配置/1000选择通过。
- 原始资料 `artifacts/fullm-transpose-load/` 私有本机Git忽略。保留通过实验分支；下一结构审查其它storage布局，main/query-block未变。整体重大提升未达成。


## 2026-10-01 · 完整 K 宽窗口正式通过，父 Norm 缓存复核

- 代码 `9cfb159` / SHA `af0d52b9c2e8f34fd43c5df4577a0d9f8d2adf456b7f57c5cbb642904ab170fc`；正式ID `6abd5fdd694b590c3c8b955d` Pass，15/15、precision_ratio全1，CANN编译成功。
- 耗时 `[2.19,4.06,4.32,5.60,5.22,10.44,10.11,67.44,84.25,97.75,87.94,96.56,15.80,13.19,9.00]` μs；第8点69.03→67.44，单次约2.3%差异不足以证明稳定大幅收益；未改路径不归因，无actual shape/plan/profile或重复A/B。
- 420 producer、9216双AIV延迟DMA/释放后覆写消费者模型通过，fake/public真实8.3 tiler各production/TUNING1400配置/1000选择，旧候选16选择；数字不代表正式命中或速度。
- 新诊断：公开父Norm1000 dual1计划均具完整K A缓存，824每shard只一window。抽取Cache实际方法2024生命周期/21512首次K-panel读取后，后续N命中，Reset释放；该优化对多数合成计划没有理论A输入读取量优势。
- 本候选归档恢复query-block，不继续全K A/window近邻试交。下一研究L1→L0 TT搬运与MMAD指令。资料 `FULLK_WIDE_WINDOW.md`、`NORM_FULLK_CACHE_AUDIT.md`。整体重大提升未达成。


## 2026-10-01 · 手写 full-K 两半 M 正式通过与覆盖审查

- 代码 `1d2ff79`，SHA `fa88b68c61ec22fdaa050f75df5aaa61aba187854476d5d462d21ac59327c1d1`；正式ID `6abd58a2694b590c3c88d669` Pass，15/15、precision_ratio全1，CANN编译成功。
- 耗时 `[2.21,4.16,4.28,5.54,5.33,10.35,9.56,68.73,84.13,97.61,87.17,95.93,15.05,12.72,9.71]` μs。第8点69.03→68.73，没有明显收益；无实际shape/plan/profile及重复A/B，无法证明新路由命中。
- CPU158实际producer执行、production/TUNING各1400 host对照（16选择）通过。覆盖审查：旧dual1的1000配置中984为W4/5/6/8，被候选W≤2排除；是假tilerhost控制流证据，不是隐藏case路由或硬件覆盖率。
- 下一假设是固定UB的N块消费者支持原宽GM窗口，保留任务、producer及workspace，不继续近邻tile参数试交。详情 `MANUAL_FULLK_M.md`。整体重大提升未达成。


## 2026-10-01 · 完整K M预载：完整外K模型否定，未正式提交

候选 `1b278c9` / SHA `0c37471e6b6b703bda9735fef64dd47523def338c2f338d6000d6f17d80bbdec`，分支 `experiment/fullk-m-preload`。
库基本M减半、基本N覆盖既有窗口、完整K A双buffer，GM ring/grid/AIV保持原样。
真实公开tiler+host production1775/TUNING1779配置、各128选择；2304预载谓词模型通过。
补上**真实ReduceKMultiIter**后，16个代表配置在第二个外K块复现没有新EnQue的第二次Await；前一模型没有覆盖这层循环，不能作为候选同步通过证明。
仅A完整K且B部分K的库预载方案被当前公开源码证据否定；安装CANN9行为未知，不声称硬件缺陷。
**未提交正式平台，CANN/NPU精度/latency无结果**。归档结构反例并恢复query-block，不继续相近参数提交。详见 [FULLK_M_PRELOAD.md](FULLK_M_PRELOAD.md)。



## 2026-10-01 · packed-B 双缓冲正式通过，无收益

代码 `c763281`，kernel SHA `119f145b81270e2994cd686bb4c621f58c48367be8629b921e6f8705b69813b4`，[正式提交 6abd423a694b590c3c7ee13d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd423a694b590c3c7ee13d) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.34, 3.89, 4.14, 5.54, 5.29, 10.64, 10.16, 68.97, 83.48, 99.95, 88.57, 97.14, 16.18, 13.58, 9.78]` μs，合计519.65 μs，父通过版511.66 μs。
第12点95.91→97.14μs，没有收益。只改已有case12 pack阶段，其余kernel未改，不归因其它点变化。
没有实际shape/plan/SoC/profile或重复A/B，不能证明此正式case命中新流水或判定具体退化原因。
宏0/1各650实际源码延迟DMA模型执行通过；完成真实CPU发起顺序重叠、晚释放UB源保护，但不构成硬件加速证明。
保留 `experiment/packed-b-pipeline` 的源码/模型/结果，恢复 `experiment/tiny-tt-query-block` 通过kernel；不提交预取深度或pack矩形相近变体。
原始JSON本机Git忽略 `artifacts/packed-b-pipeline/`；详见 [PACKED_B_PIPELINE.md](PACKED_B_PIPELINE.md)。整体重大提升尚未达成。


## 2026-10-01 · 完整 B 驻留正式通过，无明显整体收益

代码 `c9bfb58`，kernel SHA `280ab900d186365fb999d4bc83fc04109aa89baeaf54cfaa0b06d9b5f9e96e2d`，[正式提交 6abd3e5d694b590c3c7d644c](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd3e5d694b590c3c7d644c) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.1, 4.35, 4.27, 5.53, 5.54, 10.59, 10.1, 68.03, 85.04, 99.18, 88.75, 96.85, 16.24, 13.34, 9.21]` μs，合计519.12 μs，父通过版511.66 μs。
第8点69.03→68.03μs，单次约1.5%差异不证明稳定收益；其余路径未修改，变化不能归因。
没有实际shape/plan/SoC/profile或重复A/B，也不能证明新路由命中；本结果只证明此kernel通过15点。
完整B N块驻留L1、N外M内、多个M块UB Max状态及按列核心分组已实现；296个抽取producer和两名consumer模型、production/TUNING各480host配置（各384选择）通过。
保留 `experiment/resident-b-column` 为结构对照，恢复 `experiment/tiny-tt-query-block` 的代码 `55225cc`；不继续相近分组参数提交。
原始JSON本机Git忽略 `artifacts/column-b-residence/`，详见 [COLUMN_B_RESIDENCE.md](COLUMN_B_RESIDENCE.md)。整体重大提升尚未达成。


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


## 2026-09-30 · 配对 M 共享 B 覆盖版正式结果

代码 `d4b9044`，kernel SHA `c6cca6ba9a120336ab4548b7f6898dd6b793291cc0b6adea0ff20d5ad86a00b3`，[正式提交 6abcc39a694b590c3c3ada93](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcc39a694b590c3c3ada93) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

逐点耗时 `[2.27,3.90,4.07,7.82,5.30,10.60,10.05,69.57,84.77,99.51,88.07,96.27,15.87,13.10,9.53]` μs，合计 **520.70 μs**，对照保留版517.73 μs。第8点67.80→69.57、第11点88.16→88.07，没有整体收益；未取得实际shape/plan/profile及重复A/B，不能证明路由命中或具体退化原因。CPU172 producer和production/TUNING各360代表host组合（120选择）通过，与正式精度证据分开。

本分支保留代码、模型与失败对照，不继续同一结构相近参数提交。后续恢复 `experiment/manual-splitk-tiny` 的通过kernel，SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`；审查小矩阵的启动、同步与归约分工开销。整体大幅提升仍未达成。原始JSON在本机Git忽略 `artifacts/paired-m-breuse/`。


## 首版正式结果与覆盖修正

首版代码 `cff0441` / SHA `e3b770b876e90cc2c6796626858467099824a7c1341b4ba40a44d6e9a83cfebb`，[正式提交 6abcc1f7694b590c3c39b751](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcc1f7694b590c3c39b751) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

| 点 | 最快保留版μs | 128行首版μs |
|---|---:|---:|
| 1 | 2.14 | 2.28 |
| 2 | 3.96 | 3.63 |
| 3 | 4.56 | 4.13 |
| 4 | 8.08 | 7.86 |
| 5 | 5.31 | 5.32 |
| 6 | 10.58 | 10.77 |
| 7 | 10.15 | 10.72 |
| 8 | 67.80 | 70.43 |
| 9 | 83.95 | 83.97 |
| 10 | 97.84 | 98.63 |
| 11 | 88.16 | 89.95 |
| 12 | 96.97 | 98.00 |
| 13 | 15.83 | 16.98 |
| 14 | 13.20 | 13.79 |
| 15 | 9.20 | 9.44 |

合计517.73→525.90 μs，第11点88.16→89.95，未见收益。没有实际shape/plan/profile，不能断言命中新producer；其它点也有单次波动。

源码覆盖检查发现首版要求旧baseM=128，排除了64行TT族。覆盖修正版保留旧MMAD行块为bm=64或128，只将两个旧M块配成任务（schedule.baseM=2*bm），不强制把64改成128。固定N/K面板不变；更小bm降低资源需求。CPU追加64行pair的完整与尾部测试，共172个producer配置通过；host360代表组合中120个选择新路径（首版22个），production/TUNING分别通过。真实隐藏case命中未知，此计数不是正式case覆盖率。

覆盖修正kernel SHA `c6cca6ba9a120336ab4548b7f6898dd6b793291cc0b6adea0ff20d5ad86a00b3`；正式编译/精度/性能PENDING。第二次评测用来验证首版漏掉的旧64行族，不引入新的算法假设或N/K参数搜索。原始首版JSON在Git忽略 `artifacts/paired-m-breuse/`。

# 2026-09-30 · 独立 MDL shard 输入流水

## 正式结果：15/15 通过，无收益

代码 `df0e049`，[正式提交 6abcbaf3694b590c3c353072](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcbaf3694b590c3c353072) **Pass，15/15，precision_ratio 均为1**。CANN9 API编译通过。

| 点 | 最快保留版 μs | MDL shard μs |
|---|---:|---:|
| 1 | 2.14 | 2.09 |
| 2 | 3.96 | 3.99 |
| 3 | 4.56 | 4.34 |
| 4 | 8.08 | 8.39 |
| 5 | 5.31 | 5.45 |
| 6 | 10.58 | 10.44 |
| 7 | 10.15 | 10.36 |
| 8 | 67.80 | 70.86 |
| 9 | 83.95 | 84.55 |
| 10 | 97.84 | 100.05 |
| 11 | 88.16 | 89.29 |
| 12 | 96.97 | 97.37 |
| 13 | 15.83 | 16.85 |
| 14 | 13.20 | 13.76 |
| 15 | 9.20 | 9.70 |

15点合计 517.73→527.49 μs。第8点67.80→70.86、第11点88.16→89.29，没有收益。未获得实际shape/plan/kernel/profile，不能断言命中MDL路由或归因退化；其它点也有单次波动。保留分支对照，不替换最快通过版、不继续相近MDL参数提交。原始JSON在Git忽略 `artifacts/mdl-shard-pipeline/`。下一条研究动作：核对A2/A3 Fixpipe直接到UB能力与Matmul输出交接实现，再判断能否削减现有GM ring通路。整体大幅提升仍未达成。

# 验证与性能记录

每条新记录必须带代码 commit/SHA、设备、CANN、case、命令和实际结果。空白数据不得补成零或推测值。

## 2026-09-30 · CANNJudge CLI · 库内建 NZ 输出流水

- 分支 `experiment/builtin-nz-stream`，代码 `fcbf29b`，SHA `895be634247274f702cfbebaba858c8087a309c0554cd44977c178ced77d9225`，259946字节。父stream ND `08559b7`。dry-run只上传kernel.asc，命令 `python3 /private/tmp/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /private/tmp/bmmms-judge-builtin-nz/project --no-wait`，查询同一任务至终态。[提交 6abcb535694b590c3c317c3e](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb535694b590c3c317c3e)。
- 假设：独立AIC MatmulImpl以库内建GM NZ C/GetTensorC顺序输出，AIV直接读取自己负责的NZ行并做tree/lane Max，减少NZ→ND转换；不使用任何DataCopyOut callback，不新增GM通路。host重新查询NZ C tiler并保留原任务/tile/worker，默认模板ND不变。
- CPU `validate_cube_stream.py`：production/TUNING各96路由/workspace/pins/tiler回退；actualproducer、DMA、tail-mask、Max分别ND/NZ各432配置与独立oracle相同，含128tile、M/Ntail、零有效AIV行、全负和巨大正值污染无效NZ列。mock不证明库输出布局/硬件事件/cache性能。
- **CANN编译通过、15/15 Pass**，各precision_ratio=1。时间 `[2.32,4.09,4.19,8.34,5.50,10.67,10.20,66.40,84.14,98.19,89.04,97.60,16.59,13.78,9.62]` µs。第8点相对ND父版67.89→66.40、第11点88.96→89.04；对较快Split-K版67.80→66.40、88.16→89.04。没有整体大幅收益，不合并最快版，不提交相近输出参数变体。
- 通过msg为空，精确SoC、shape/plan、actualkernel、新路由是否命中、重复A/B、msprof未取得。未出现此前callback Runtime Error，但不能说callback故障被修复。原始JSON在本机Git忽略 `artifacts/builtin-nz-stream/`；详细 [BUILTIN_NZ_STREAM.md](BUILTIN_NZ_STREAM.md)。下一步从输入搬运和L1/L0分块审查寻找结构候选。

## 2026-09-30 · CANNJudge CLI · 独立 AIC 库会话流式交接

- 分支 `experiment/cube-stream-sessions`，最终代码 `c7b004e`，SHA `9b2a01d71abffcc4aa0ae7e04793a91ceb0f2ef172d73c06c7f369aa3367e471`，257533字节；父 `11de38b`。仅上传kernel.asc。命令 `python3 /private/tmp/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /private/tmp/bmmms-judge-cube-stream/project --no-wait`，查询至终态。[提交 6abcb222694b590c3c2f8de6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb222694b590c3c2f8de6)。
- 假设：绕开 dual-master wrapper 每window内部End，以 MatmulImpl 对完整Nshard保持库会话并逐tile交接，保留既有GM ring/归约/任务。官方公开源码版本8.3.T9.0.B066指出外层End为空，内部IterateAll会End；不当作CANN9精确header。新 engine 编译是否可用以本次正式结果为准。
- CPU：production/TUNING各96个真实host路由/workspace/pins/tiler拒绝回退检查；实际producer和consumer DMA/Max抽取384配置与独立点积→Max→Sum oracle一致。Split-K48组、direct-batch1458配置回归通过。不是CANN scheduler/cache/event仿真。
- 首版 `9776448` / SHA `72dcd9b1b4ebc43e4d2ff51758db2a151bb0797705178691994adbb4d827cf00` [提交 6abcb16a694b590c3c2f20f7](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb16a694b590c3c2f20f7) Compile Error：launch static_cast丢失GM地址空间限定。`ff18972` 未进入评测（HTTP429）；`c7b004e` 复用已有workspace变量修正后提交。
- 修正版**CANN编译通过、15/15 Pass**，各precision_ratio=1。时间 `[2.27,3.62,4.26,7.89,5.53,10.62,10.13,67.89,85.21,98.39,88.96,96.54,15.77,13.09,8.96]` µs。第8点67.80→67.89，第11点88.16→88.96，总517.73→519.13，无明显收益，不合入最快版。通过case msg为空，实际shape/plan/kernel命中、精确SoC、重复A/B、msprof仍缺失；不推断缓存或具体硬件瓶颈。
- 原始JSON本机Git忽略 `artifacts/cube-stream-sessions/`；文档 [CUBE_STREAM_SESSIONS.md](CUBE_STREAM_SESSIONS.md)。后续验证该独立AIC上的库内建NZ输出，避免失败的自定义callback；不重复相近会话参数。

## 2026-09-30 · CANNJudge CLI · 大 TT 非对齐 A 常驻失败对照

- 分支 `experiment/ragged-tt-resident-a`，代码 `4507c59`，kernel SHA256 `d327a0632c87335a657528005b25eb9a9578086c3691f602947159baa30f2b3d`，256400 字节；从较快的 `d2718c8` 派生。dry-run 仅上传 kernel.asc。`python3 /private/tmp/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /private/tmp/bmmms-judge-ragged-tt-resident/project --no-wait`；随后查询同一任务至 Pass。[提交 6abcaadc694b590c3c2ada90](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcaadc694b590c3c2ada90)。
- 假设：BF16 B1 TT 大矩阵非对齐尾块使用手写 producer，把每个 M tile / N shard 的完整 A 在 L1 复用，B 和 L0 双缓冲。A 的 NZ slab 使用 padded K 跨度，经 2D block transpose 转成 ZZ；保留 ND ring、AIV Max 和 finalizer。host 查询实际容量，M tile 128/64 和 N shard 自适应，低资源或 pins 回退。没有新增 GM 通路。
- CPU：`validate_ragged_tt_resident.py` production/TUNING 各 465 个路由、资源和独立任务覆盖检查；231 组抽取实际加载 helper 的 NZ/ZZ/ZN、完整 tile/尾块/复用和小形状独立数值模型通过。既有 Split-K 48 组、direct batch 1,458 配置通过；不是设备性能证据。
- **CANN 编译通过，15/15 Pass**，各点 precision_ratio=1。时间 `[2.22,3.98,4.40,7.77,5.67,10.56,9.79,94.15,82.75,96.90,87.87,96.75,15.11,13.01,9.40]` µs；第 8 点相对父版 67.80→94.15 µs，15 点合计 517.73→540.33 µs，候选无整体收益，不合并最快版。
- 目标 CANN9；精确 SoC、实际 shape/layout/plan、msprof、重复 A/B 未取得，通过 case 的 msg 为空。无法确认新路径命中或具体瓶颈来源。原始 JSON 保存于本机 Git 忽略 `artifacts/ragged-tt-resident-a/6abcaadc694b590c3c2ada90.json`。详细说明 [RAGGED_TT_RESIDENT_A.md](RAGGED_TT_RESIDENT_A.md)；不再提交该路径相近参数变体。

## 2026-09-30 · CANNJudge CLI · 紧凑 NZ ring 首版 Runtime Error

编译期 callback baseN 版 `21dae0d`，kernel SHA `34faa07f6d898386f0dec10da0a68fc0f013a67152529b650e9fd1d6e3644912`，257417 字节；[提交 6abca4d0694b590c3c26d435](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abca4d0694b590c3c26d435) **编译通过，第 8 点 Runtime Error 507015，7/15 Pass**。前 7 点 `[2.12,3.98,4.27,8.32,5.12,10.83,10.14]` µs，后 7 点 Skipped。日志 device 0，目标核 `bmmms_dual<bf16,true,true,true,128>`；目标点无有效时长。取消运行时 user info 传递未解决故障，不能归因为用户标量传递。三版均不合并通过版，暂不提交相近变体。原始失败日志及 JSON 已保存至本机 Git 忽略 `artifacts/nz-ring-max/`；精确 SoC、实际 shape/plan、底层异常地址未提供。

ND 库调度隔离版 `5de5952`，kernel SHA `9e6717adbcfa291b6899e48ebd79e1b7b8f2768ab1df8ff19f96195ab300d481`，257173 字节；[提交 6abca32b694b590c3c25d63d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abca32b694b590c3c25d63d) 编译通过，仍是第 8 点 Runtime Error 507015，前 7 点 Pass，后 7 点 Skipped。前 7 点耗时 `[2.14,4.00,4.28,7.85,5.50,10.56,9.53]` µs。device 0 同步失败；目标点无有效时长，不能估算分数。原始 JSON `/private/tmp/bmmms-6abca32b694b590c3c25d63d.json`。恢复库 C/tiler ND 未解决故障；下一修正版使用编译期 baseN 消除回调用户标量传递，仅为待验证隔离，未证明根因。

- 分支 `experiment/nz-ring-max`，代码 `9c7a006`，kernel SHA256 `4d1fa214d1fc56d97be612ce0969277b317ec6e617ab07903be03698c09b9832`，257091 字节。dry-run 只上传 kernel.asc。[提交 6abca137694b590c3c249f19](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abca137694b590c3c249f19)。CLI 恢复于 `/private/tmp/cannjudge_cli.py`；`submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /private/tmp/bmmms-judge-nz-ring/project --no-wait`，随后 query。
- 假设：大 TT 的 L0C→GM NZ 输出配合 AIV 直接 NZ Max，可减少 Fixpipe NZ→ND 转换。新增输出回调为窗口中各 tile 显式定位，复用既有 ring。CPU：90 组抽取回调单位/窗口检查、1,344 组 NZ 地址/尾块/全负模型通过；不是设备证据。
- **CANN 编译通过，Runtime Error，7/15 Pass**。前 7 点时间 `[2.06,3.72,4.29,7.74,5.20,10.30,10.05]` µs；第 8 点新 `bmmms_dual<bf16,true,true,true>` 在 device 4 上 WarmUp/replay 同步失败，返回 507015。后 7 点 Skipped，无有效耗时，不纳入总时间或分数。返回日志只含同步错误及前 7 点 msprof 基本信息，无底层异常地址。原始记录 `/private/tmp/nz-ring-query.log`，不入 Git。
- 修正版保留父版库 C/tiler ND、由回调定义 NZ 实际输出，以隔离新增库 NZ 约束。错误原因未证实。当前路径不能作为通过版使用；精确 SoC、隐藏 shape/plan、目标点 profile 未取得。

## 2026-09-29 · CANNJudge CLI · 宽 N 尾块 A 常驻失败对照

- 分支 `experiment/ragged-wide-resident-a`，代码 `3c54597`，kernel SHA256 `60b86f28e0c98731f7c54f944dd3095d1af31e1c8a02de2dd090b8a92b67828a`，253301 字节；dry-run 仅上传 `kernel.asc`。[提交 6abbd297694b590c3cc7d861](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbd297694b590c3cc7d861)。命令：`python3 /tmp/cann-learning-hub/skills/cannjudge-submit/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /tmp/bmmms-judge-manual-tt/project --no-wait`，随后 `query --submission-id 6abbd297694b590c3cc7d861`。
- 假设：历史第 14 点的 BF16、短 M、宽 N、短 K 可能因 M/N/K 非对齐而回退通用 Matmul。把已有完整 A 常驻 L1/L0A、两个 N tile 共用 A 的手写 Cube 路径扩展到尾块；K 上取整分配 L1/L0，M/N/K padding 后只归约有效列和行。实际路由要求 TX1=false、TX2=true、M≤128、N≥4096、K≤256、片上容量满足预算；不限制 B。`python3 tools/validate_ragged_wide.py`：host 路由/资源回退和 10 组独立数值/全负/尾块模型通过；`validate_manual_splitk.py`、`validate_direct_batch.py` 回归通过。CPU 模型不能证明设备路径和性能。
- 正式 **Pass，15/15**，每点 `precision_ratio=1`。时间依次为 `[2.18,3.93,4.28,8.40,5.78,11.06,10.54,69.64,84.20,99.10,89.50,97.71,16.94,13.70,9.34]` µs。第 14 点相对手写 Split-K 父版 13.20→13.70 µs；15 点合计 517.73→526.30 µs，按页面最优时间估算均分 40.967→40.209（非平台公布分数）。没有目标收益，不替换父版。
- 平台标注 CANN 9.0.0；精确 SoC、隐藏 shape/layout/dtype、实际 plan、msprof 和重复 A/B 未取得。第 14 点是否命中新增路径未知，不能把退化直接归因于手写路径本身。

## 2026-09-29 · CANNJudge CLI · 小 TT 长 K 手写 Cube Split-K

- 分支 `experiment/manual-splitk-tiny`，代码 `568f4eb`，kernel SHA256 `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`，252985 字节。dry-run 确认只上传 `kernel.asc`。[正式提交 6abbcdc5694b590c3cc4cac3](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbcdc5694b590c3cc4cac3)。命令：`python3 /tmp/cann-learning-hub/skills/cannjudge-submit/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /tmp/bmmms-judge-manual-tt/project --no-wait`，随后 `query --submission-id 6abbcdc5694b590c3cc4cac3`。
- 假设：小 M/N、长 K、TT、FP16 的现有 Matmul Split-K 会话开销较高。为 B=1、M/N 16–128、K 4096–8192 且 K 为 1024 倍数、片上内存满足预算的现有 Split-K 计划，改成 8 个 Cube worker 各自计算完整 FP32 C 的一段 K，再由原 finalizer 合并 K、沿 N 取 Max、沿 M 求和。`python3 tools/validate_manual_splitk.py`：host 路由及资源回退通过，48 组独立 TT 数值/尾块/任务模型通过；`git diff --check` 通过。这些本地模型不是设备精度证据。
- 首次代码 `654347a`、SHA `6c198f0b38315efdb85c876c6520ffd22a3819a0e8bbad146b2408c986f893ab` 的[提交 6abbccee694b590c3cc43d25](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbccee694b590c3cc43d25) 为 **Compile Error**：同一 `auto` 声明将 `LocalTensor<T>` 和 `LocalTensor<float>` 混用。`568f4eb` 拆为两条声明后重新提交；不要把首次提交计为精度或性能结果。
- 修正版正式结果 **Pass，15/15**，每点 `precision_ratio=1`。15 点时间依次为 `[2.14,3.96,4.56,8.08,5.31,10.58,10.15,67.80,83.95,97.84,88.16,96.97,15.83,13.20,9.20]` µs。相对直接 batch 父版，第 15 点 13.10→9.20 µs，1.42×；第 8 点 69.69→67.80 µs。15 点时间合计 522.78→517.73 µs，按同页最优值估算均分 40.774→40.967（+0.193），不是平台公布的分数。第 8 点及非目标点的单次波动不能归因于新路径。
- 平台标注 CANN 9.0.0；精确 SoC、隐藏 shape/layout/dtype、实际 plan、msprof 与重复 A/B 未取得。候选保留在独立分支，待确认第 15 点路径和稳定收益后决定是否并入 main。

## 2026-09-29 · CANNJudge CLI · 大 TT 双 N tile A 面板复用

- 分支 `experiment/tt-panel-pair`，代码 `7b4d477`，kernel SHA256 `802026fd4949d0aa1c5622576080964a8a3734267181a7ed4019303a979084e0`，259564 字节。官方 dry-run 确认仅上传 `kernel.asc`；[提交 6abbc9e9694b590c3cc258f3](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbc9e9694b590c3cc258f3)。命令：`python3 /tmp/cann-learning-hub/skills/cannjudge-submit/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /tmp/bmmms-judge-manual-tt/project --no-wait`，随后 `query --submission-id 6abbc9e9694b590c3cc258f3`。
- 假设：大 TT 的相邻两个 N tile 可共用 A 的每个 K 面板，以两个 L0C 累加器完成完整 K 后沿用现有 Max(N)→Sum(M) 消费路径。只有平台 L1/L0/UB 容量充足、B=1、两个转置属性 true、M/N/K 大且 16 对齐、bm=bn=128、每 N 分区至少两 tile 时才尝试。`python3 tools/validate_cube_panel.py`：456 个生产者及 584 个分层 K CPU 物理块执行通过；`python3 tools/validate_tt_panel_plan.py`：两个历史目标代理形状命中、非 TT/资源不足回退通过。旧通用 `validate_host_plan.py` 仍因与当前源码不符的 `SplitKNDLiveBytes` 断言无法编译，不能作为本实验失败证据。
- 正式结果 **Pass，15/15**，每点 `precision_ratio=1`。全部时间依次为 `[2.19,3.92,4.32,8.34,5.45,10.54,10.18,69.65,83.52,97.61,88.86,97.11,15.86,13.46,13.06]` μs。相对直接 batch 父版，第 8 点 69.69→69.65 μs，第 11 点 87.63→88.86 μs，无目标收益。页面标注 CANN 9.0.0；精确 SoC、隐藏 shape、实际 plan、msprof、重复测量未取得。不能断定目标点实际走了双 tile 路径；该分支不并入较快版。

## 2026-09-29 · CANNJudge CLI · TT 交换方向失败对照

- 分支 `experiment/swapped-tt-column-max`，代码 `345e335`，kernel SHA256 `40c5bed863c6ab9411783479c0b6921268815449434728a523b5d2a4e9fff5a0`，256083 字节。官方 dry-run 确认仅上传 `kernel.asc`，SHA 与 Git 工作区一致；[提交 6abbc6d9694b590c3cc08c48](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbc6d9694b590c3cc08c48)。命令：`python3 /tmp/cann-learning-hub/skills/cannjudge-submit/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /tmp/bmmms-judge-manual-tt/project --no-wait`，随后 `query --submission-id 6abbc6d9694b590c3cc08c48`。
- 假设：两个 TT storage 输入物理上为 `X2[N,K]` 和 `X1[K,M]`，交换操作数后用 FF Matmul 得到 `Cᵀ[N,M]`，可能降低输入转置搬运；AIV 以二叉树对原 N 做列 Max，随后沿原 M 求和。专用计划只考虑大矩阵、B=1、两个属性为 true、M/N/K 16 对齐、完整 K；资源或 tiler 不接受时保留父路径。`python3 tools/validate_swapped_tt.py` 的 228 组独立 CPU 数学/任务覆盖模型通过，`git diff --check` 通过。旧 `validate_host_plan.py` 因其断言仍引用已删除的 `panelK/panelResident` 字段而编译失败，不能作为本次候选精度证据。
- 官方结果 **Pass，15/15**，每点 `precision_ratio=1`。全部时间依次为 `[2.33,4.22,4.09,8.04,5.52,10.47,10.57,70.47,84.10,99.21,152.24,97.40,16.45,13.70,13.70]` μs。相对直接 batch 归约父版，第 11 点 87.63→152.24 μs，第 8 点 69.69→70.47 μs；没有整体收益。页面标注 CANN 9.0.0；精确 SoC、实际 plan、隐藏 shape、msprof、重复测量均未取得，因此无法将第 11 点退化精确归因于某一环节。该实验不并入较快分支。

## 2026-09-29 · CANNJudge CLI · Matmul 会话复用失败对照

- 分支 `experiment/norm-session-reuse`，代码 `56ea172`，kernel SHA256 `a1c60ea079ca3c75656dc271b806d2e66268ddfc19df8f3cb70e641565cd7bb3`，246845 字节。官方 CLI dry-run 仅上传 `kernel.asc`；[提交 6abb3973694b590c3c72900c](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3973694b590c3c72900c)。命令：`python3 /tmp/cann-learning-hub/skills/cannjudge-submit/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /tmp/bmmms-judge-manual-tt/project --no-wait`，随后以同 CLI `query --submission-id 6abb3973694b590c3c72900c` 读取结果。
- 假设：`bmmms_dual` 中每个 C window 的 `mm.End()` 可能破坏 Matmul 内部 A/B 缓冲复用；把 End 移到 worker 循环末尾，保留原 ring 和 flag 同步。官方 CANN 9 Matmul 文档允许复用对象；具体内部销毁行为参考官方开源 `ascendc-api-adv` 源码，但本机副本并非 CANN 9.0.0 精确版本，不能据此推断设备收益。
- 结果 **Pass，15/15**，每点 `precision_ratio=1`。全部时间依次为 `[2.03,3.79,4.29,8.19,5.29,10.78,10.12,70.32,84.16,97.85,88.12,96.80,15.86,13.15,13.30]` μs。相对直接 batch 归约父版，第 8–12 点分别变化 `+0.63,-0.67,-0.19,+0.49,+0.78` μs；没有稳定的大幅收益。页面 CANN 9.0.0，精确 SoC、隐藏 shape/plan、msprof、重复测量未取得。该分支保留失败对照，不替换较快版。

## 2026-09-29 · CANNJudge CLI · ragged B 常驻失败对照

- 分支 `experiment/tall-ragged-resident-b`，代码 `a6c5a29`，kernel SHA256 `92a92db0c01b93223056fc70b0cc062ebbf0eefc39b8020954e498bde370b62c`。官方 CLI dry-run 确认只上传 `kernel.asc`，248519 字节；[提交 6abb3724694b590c3c71cfe4](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3724694b590c3c71cfe4)。命令：`python3 /tmp/cann-learning-hub/skills/cannjudge-submit/cannjudge_cli.py submit --problem-id 6a9aa054bf41025d6014f3ef --project-dir /tmp/bmmms-judge-manual-tt/project --no-wait`，随后以同 CLI `query --submission-id 6abb3724694b590c3c71cfe4` 读取结果。
- 假设：历史第 13 点的非对齐 FP16 FF 长 M/窄 N 路径，完整 B 可放入每 worker 的 L1/L0B；把 B 的 GM 加载由每 M tile 一次改为每 worker 一次，并把 worker 的行最大值在 AIV 内合并。按 64 个 M tile、20 个 worker 的模型，B GM 加载次数 64→20；这不是性能预测。实际选择仍受 tiler 与设备容量检查控制。
- `python3 tools/validate_ragged_resident_b.py` 的 384 个采样行覆盖 N=64/65/96/127、K=128/136/192/248、16/20/32 worker、全负相似度和 K/N padding，CPU 数值与逻辑点积相等；`git diff --check` 通过。该模型不验证 Ascend DMA、事件和真实 plan。
- 结果 **Pass，15/15**，每点 `precision_ratio=1`。目标第 13 点从直接 batch 父版 15.74 到 15.93 μs，未见收益。全部时间依次为 `[2.10,3.74,4.36,8.38,5.38,10.71,10.25,68.92,83.70,99.10,88.71,96.86,15.93,13.25,13.45]` μs。第 13 点是否满足此分支的非对齐条件未知，因此不能归因于 B 常驻的实际性能。
- 平台标注 CANN 9.0.0；精确 SoC、隐藏 shape、实际 plan、msprof、重复测量均未取得。该版本不合并较快分支；保留 Git 分支供定位，后续以实际 plan/profile 为准。

## 2026-09-29 · CANNJudge CLI · 256 行 tall/manual tile 失败对照

- 独立分支 `experiment/tall-m256` 从直接 batch 归约 `fa3eaed` 派生，代码 `eae79e4`，kernel SHA256 `60f31c815eb2dca302ad8c2c11b586c1b57c43727ba22a14b036053195b45c93`，248426 字节。[提交 6abb3203694b590c3c6fc554](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3203694b590c3c6fc554)，官方 CLI dry-run 确认只上传该 `kernel.asc`。
- 假设：历史探针第 13 点 M=8192、N∈[64,127]、K∈[128,248] 的 FP16 FF 路径，用 256 行 manual tile 把 64 个 M 任务降至 32 个，并减少 B 重复搬运。仅该形状类别进入显式 L1/L0/UB 预算分支；资源不足时保留 128 行候选。`python3 tools/validate_tall_m256.py` 144 组排程/输出槽/缓冲模型通过；这不是设备 tiling 证据。
- 正式结果 **Pass，15/15**，`precision_ratio=1`。第 13 点反而从直接 batch 父版 15.74 升至 16.98 μs；15 点合计 522.78→523.82 μs，按同页最优值估算均分 40.774→40.660。其它点的变化落在单次结果波动范围，未见结构性收益。正式耗时依次为 `[2.08,3.95,4.22,7.90,5.49,10.61,10.09,69.34,82.98,99.73,87.63,96.52,16.98,13.30,13.00]` μs。
- 平台不提供实际 plan、精确 SoC、msprof，故不能证明第 13 点确实选到了 256 行 tile，也不能判定退化来自 L0C 单缓冲或 Cube 负载；此分支保留失败对照，**不合并 main**。
## 2026-09-29 · CANNJudge CLI · 双缓冲消费流水

- 分支 `experiment/dual-consumer-overlap`，代码 `bea6de0`，kernel SHA256 `d55ac07aa939ffa856a7f786fade29b6179d6dd226c77842d9e6868aaa560e3f`，248362 字节。官方 CLI dry-run 仅含 `kernel.asc`；[正式提交 6abb2eeb694b590c3c6db357](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2eeb694b590c3c6db357)。父版是通过 15 点的直接 batch 归约 `fa3eaed`。
- 假设：双 VECIN 缓冲预取下一 C tile；当前 GM ring 槽的所有 MTE2 读取发出后以 `PIPE_MTE2` 归还，使 Cube 写下一窗口与 Vector 的私有 UB 归约重叠；每 tile 先在 UB 做 64-lane 树形 Max，减少横向归约调用。只改完整 K 的 dual/dual_mdl AIV 消费侧，不改 Cube/tiling/partial 布局。
- CPU：`python3 tools/validate_dual_consumer_current.py` 六种流水/归约组合分别通过 76,800 个窗口配置，34,816 组列尾/全负/污染检查与 3,840 组抽象握手交错；且源码除这两条消费者外与父版一致。CANN 编译/真实事件耗时无法由模型证明。
- 正式 **Pass，15/15**，`precision_ratio=1`。平台标注 CANN 9.0.0；精确 SoC、hidden shape、实际 plan、msprof 未取得。相对父版，第 8 点 69.69→68.53 μs、第 9 点 84.83→82.81 μs、第 11 点 87.63→86.98 μs；第 10/12 点 98.04→98.38、96.02→96.74 μs。全部时间依次为 `[2.10,3.82,4.38,8.42,5.23,10.57,10.22,68.53,82.81,98.38,86.98,96.74,15.69,13.23,13.05]` μs。
- 页面两位小数合计 522.78→520.15 μs；按同一页面最优时间估算均分 40.774→40.794，差值 +0.020。单次波动足以覆盖该差异；**不是重大突破**，不并入 main。下一实验应优先改变已知空闲核或重复读输入的结构，而不是继续调整消费者微流水。

## 2026-09-29 · CANNJudge CLI · 直接 batch 归约

- 分支 `experiment/direct-batch-reduce`，代码提交 `45efd1f`，`kernel.asc` SHA256 `e06ce50abb27dc9315d1b64437c2086473ffe53295c843c39aa61aa3feadefc2`。正式[提交 6abb2b8d694b590c3c6b89a2](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2b8d694b590c3c6b89a2)由官方 CLI 发起；dry-run 确认仅上传 `kernel.asc`，246853 字节，SHA 一致。
- 假设：历史探针第 4/5/7 点的单 M/N tile 可由一个 AIV 完成全 batch Max(N)→Sum(M) 并直接写 y，省掉 partial 写回、全核 `SyncAll` 和末级读回。第 4/5 点复用第 6 点已通过的 direct kernel；第 7 点对手写 Cube 路径增加 full-row direct specialization。其它分支仍用原逻辑。
- `python3 tools/validate_direct_batch.py`：探针范围的 1,458 组 batch/shape/core 边界排程和 192 KiB UB 显式分配模型通过；`git diff --check` 通过。模型不验证 Ascend 指令和性能。
- 正式结果：**Pass，15/15**，每点 `precision_ratio=1`。平台标注 CANN 9.0.0；精确 SoC、hidden shape/layout/dtype、实际 plan、编译命令和 msprof 未取得。平台时间单位按页面为 μs。

| 点 | 队友 498576 | direct | 差值 direct−队友 |
|---:|---:|---:|---:|
| 1 | 2.22 | 2.10 | -0.12 |
| 2 | 4.10 | 3.92 | -0.18 |
| 3 | 4.26 | 4.28 | +0.02 |
| 4 | 8.48 | 8.33 | -0.15 |
| 5 | 6.53 | 5.26 | -1.27 |
| 6 | 10.60 | 10.60 | 0.00 |
| 7 | 11.69 | 10.12 | -1.57 |
| 8 | 67.21 | 69.69 | +2.48 |
| 9 | 84.65 | 84.83 | +0.18 |
| 10 | 95.37 | 98.04 | +2.67 |
| 11 | 87.36 | 87.63 | +0.27 |
| 12 | 95.95 | 96.02 | +0.07 |
| 13 | 14.93 | 15.74 | +0.81 |
| 14 | 13.02 | 13.12 | +0.10 |
| 15 | 13.34 | 13.10 | -0.24 |

按页面两位小数时间与相同页面最优值估算均分 40.39→40.77（+0.38）；15 点时间合计 519.71→522.78 μs。单次运行的非目标点存在波动，不能把估算分差当已复现实测收益。第 5/7 点局部改善明确，但整体未达到用户要求的重大突破；暂不并入 main，也不再为小改动重复提交。

## 2026-09-28 · CANNJudge 正式提交 498576 · 队友合并 v3

- 提交：[BatchMatmulMaxSum / 498576](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3dbb694b590c3cd8f427)，2026-09-28 18:13:15 CST；分支 `experiment/teammate-c6-c10-c12-v3`，导入提交 `d9d74eb`。
- 用户附件逐字节导入并通过网页版代码编辑器提交。平台保存的 `kernel.asc` 复制回本地逐字节比对一致：244979 字节，SHA256 `ce2e12e425883fc207d0dd5d08a7a72b485c439b65fbbb8db33165905aecce52`。仅提交 `kernel.asc`；未修改赛题工程其他文件。
- 结果：**Pass，15/15**；每点输出错误占比 **0.00%**。平台标注 CANN 9.0.0；精确 SoC、设备核数、case shape/layout/dtype、实际 plan、编译命令和 msprof 未展示。

| 点 | 上次 498385 (μs) | 本次 498576 (μs) | 本次/上次 | 页面最优 (μs) |
|---:|---:|---:|---:|---:|
| 1 | 2.12 | 2.22 | 1.047× | 1.22 |
| 2 | 3.80 | 4.10 | 1.079× | 1.58 |
| 3 | 4.29 | 4.26 | 0.993× | 2.13 |
| 4 | 11.43 | 8.48 | 0.742× | 2.92 |
| 5 | 9.55 | 6.53 | 0.684× | 1.89 |
| 6 | 16.87 | 10.60 | 0.628× | 7.07 |
| 7 | 12.36 | 11.69 | 0.946× | 3.68 |
| 8 | 70.08 | 67.21 | 0.959× | 14.88 |
| 9 | 92.33 | 84.65 | 0.917× | 50.68 |
| 10 | 111.21 | 95.37 | 0.858× | 72.39 |
| 11 | 87.48 | 87.36 | 0.999× | 74.82 |
| 12 | 131.15 | 95.95 | 0.732× | 91.20 |
| 13 | 16.55 | 14.93 | 0.902× | 5.14 |
| 14 | 16.39 | 13.02 | 0.794× | 5.40 |
| 15 | 14.04 | 13.34 | 0.950× | 4.05 |

本次 13 点较快、2 点较慢；页面两位小数耗时合计 599.65→519.71 μs。按题面公式和页面显示的最优时间估算均分 34.80→40.39；页面并未公布这两个实际得分，且时间取整、单次提交和未知设备状态会影响推断。旧 CPU host 校验脚本依赖前版结构，不能用于当前附件；其编译失败不是本次设备失败。后续要记录对应 shape、路径、SoC 和重复测量，尤其第 1/2 点退化以及第 8 点与最优的差距。

## 2026-09-28 · CANNJudge 正式提交 498385

- 提交：[BatchMatmulMaxSum / 498385](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3abb694b590c3cd6cbe3)，2026-09-28 18:00:27 CST；分支 `experiment/performance-structure-fixes`，代码提交 `a3c1f7d`。
- 平台保存的 `kernel.asc` 与本地文件逐字节一致：216575 字节，SHA256 `1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。通过网页版代码编辑器提交，仅提交 `kernel.asc`。
- 结果：**Pass，15/15**；每点输出错误占比均为 **0.00%**。平台标注 CANN 9.0.0；精确 SoC、设备核数、case shape/layout/dtype、实际 plan、编译命令和 msprof 未展示，均记为未取得。

| 点 | 本次用时 (μs) | 页面最优用时 (μs) | 本次/最优 |
|---:|---:|---:|---:|
| 1 | 2.12 | 1.22 | 1.74× |
| 2 | 3.80 | 1.58 | 2.41× |
| 3 | 4.29 | 2.13 | 2.01× |
| 4 | 11.43 | 2.92 | 3.91× |
| 5 | 9.55 | 1.89 | 5.05× |
| 6 | 16.87 | 7.07 | 2.39× |
| 7 | 12.36 | 3.68 | 3.36× |
| 8 | 70.08 | 14.88 | 4.71× |
| 9 | 92.33 | 50.68 | 1.82× |
| 10 | 111.21 | 72.39 | 1.54× |
| 11 | 87.48 | 74.82 | 1.17× |
| 12 | 131.15 | 91.20 | 1.44× |
| 13 | 16.55 | 5.14 | 3.22× |
| 14 | 16.39 | 5.40 | 3.04× |
| 15 | 14.04 | 4.05 | 3.47× |

比值根据页面两列四舍五入后的时间计算，只用于排序；未把它当作官方分数。正式结果证明该提交通过 15 点，不代表已取得本地可复现的 SoC 和 profiling 数据。下一步优先识别第 5、8、4 点及第 13–15 点的实际配置。

## 2026-09-20 · experiment-v1

Kernel SHA256：`5545fbbd049685852eb9f1e684695a670bc2de40babff0f3697a4b6e9e3bc470`

| 检查 | 环境/范围 | 结果 |
|---|---|---|
| 抽取 DeferredRowMax 的 C++ 指令语义模型 | macOS，C++14；2,304 分片 / 54,828 行 | 与直接 max 逐位一致 |
| Python mask/stride 补充模型 | 9 种 stride；1,728 分片 / 41,850 行 | 完全一致；包括非 64 倍数 stride |
| FinalizeRows 调度 | 28,672 组 B/worker/dual | 新版无遗漏或重复 writer；旧版 1,344 组有重复 |
| UB/启用条件预算 | 5,248 组 | 新分配均在预留范围内 |
| ASan/UBSan | 本机 host 模型 | 编译成功；运行启动阶段超时，未验证 |
| CANN 9.0.0 编译 | A2/A3 | PENDING |
| 正式 15 个 case | FP16/BF16、四布局 | PENDING |
| NPU latency / msprof | T0/T1/T2 | PENDING |

普通 CPU 模型验证语义与地址，不验证设备同步、CANN 指令或性能。参考验证命令：`python3 tools/validate_cpu_model.py`。记录中的 Python 补充模型属于先前检查；当前脚本复现 C++、调度、预算三项。

## 2026-09-20 · Git 交接复现

执行 `python3 tools/validate_cpu_model.py`，退出码 0：

- C++ helper：2,304 分片、54,828 有效行逐位一致。
- 调度：28,672 配置通过。
- 预算：5,248 配置通过。
- 3 个历史 tag 的 kernel SHA256 全部与保留快照一致。

这是同一候选的可移植检查脚本复现，未新增 NPU 证据。

## 后续实机记录模板

```text
Date / Commit / Kernel SHA:
SoC / device / die / CANN / driver:
Case (B,M,N,K) / dtype / tx1 / tx2:
Actual plan (dual, baseM, baseN, window, nSplit, kSplit, cubeBlocks, deferredMax):
Version T0/T1/T2:
Build command and status:
Correctness / max_abs / max_rel / repeat consistency:
Cold call / steady median / p95 / run-to-run variation:
Cube utilization / Vector utilization / MTE / Task Duration:
Log location:
Interpretation / next hypothesis:
```

## 2026-09-21 · 用户提供的性能截图（未绑定源码）

截图标记环境为 910B3 / 20 Cube / CANN 9.0.0，msprof。尚缺 kernel SHA、dtype、tx1/tx2、构建宏和原始日志，不能归因到 v1、v2 或新导入版本。也没有正式 15 case 精度通过证据。

| (B,M,N,K) | op | 耗时 | blocks | Cube | MTE2 | MAC | fixpipe（保留截图单位） |
|---|---|---|---|---|---|---|---|
| (1,513,511,2048) | bmmms_dual | 107.2 us | 5/20 | 23.5% | 88.4% | 17.0% | 25% |
| (1,1023,513,512) | bmmms_dual | 123.5 us | 16/20 | 71.7% | 89.3% | 2.9% | 40.7% |
| (2,257,513,2048) | bmmms_dual_mdl | 48.0 us | 18/20 | 65.0% | 58.3% | 14.7% | 1.9% |
| (16,512,512,512) | bmmms_dual | 65.7 us | 20/20 | 78.2% | 58.7% | 31.0% | 23.1 us |
| (4,2048,2048,2048) | bmmms_dual_mdl | 387.1 us | 20/20 | 80.1% | 80.1% | 76.7% | 23.1 us |

截图提及的 3–4 倍空间属于外推，未经实验确认。MTE2 时间占比不能直接解释为带宽饱和度。

## 2026-09-21 · 当前用户最优版本导入

- 用户确认当前最优：kernel(2).asc，3,492 行、192,577 字节。
- SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 逐字节复制并核对 SHA；没有移植 v1/v2 改动。
- 源码注释记录的性能属于提供者数据，未在本轮复现。
- 旧 CPU helper 模型对该源码不适用；脚本明确非零退出，不能误报 PASS。
- 当前版本 CANN 编译 / NPU 精度 / NPU 性能：PENDING。

## 2026-09-21 · coverage-splitk

分支 `experiment/coverage-splitk` 从用户最优 tag 派生，不含流水实验。
当前 kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。

修复提交：`b0a2fc0`（存活 UB 预算），`c4e536a`（输出遍历）。后续候选只在原 long-K 类中按工作量选择 1/2/4 份，宏 `BMMMS_ADAPTIVE_SPLITK=0/1` 做对照。

| 检查 | 命令/范围 | 结果 |
|---|---|---|
| 实际 InitBuffer 表达式和 classifier | `python3 tools/validate_splitk_coverage.py`；M=16..128、N=1..256、128/192/256 KiB UB | 86,784 配置通过；识别并阻止 3,328 组旧超预算选择 |
| 关键 UB 反例 | (1,112,192,8192)，192 KiB UB | 旧预算 192,448 bytes；源码显式存活分配 217,120 bytes；新版不强制 Split-K |
| 拆分选择器与独立逐 task oracle | 同上；B=1..64、K=4096..8192 步长 8、11 种核数 | 361,152 配置通过；208,482 组少于 4 份；选 1/2/4 各 115,629/92,853/152,670 |
| classifier dtype/layout/core | 同上；两种 dtype、四布局和代表性 B/K/核数 | 864 配置通过；宏 0 始终固定 4，宏 1 符合选择器与完整 M/N tile 要求 |
| 输出唯一与完整覆盖 | `python3 tools/validate_finalizer_coverage.py` | 28,672 配置通过；旧版 320 组遗漏、896 组重复 |
| 设备清单输入合法性 | docs/coverage_cases.csv | 35 个不同 shape 符合当前实现的边界和 2^26 元素约束；280 个 dtype/layout 组合待设备运行 |
| CANN 9.0.0 编译 | A2/A3 | PENDING |
| 正式 15 点、真实精度、NPU 性能 | U/F/A0/A1 | PENDING |

Split-K host 模型两档宏均编译运行，统计是各档相同模型空间，不将两档相加声称独立覆盖率。输出模型按实际 for-loop 头部计数，但没有执行完整设备算术或同步。代理工作量非增不等于真实耗时非增。

验证资料：`RESEARCH_coverage_splitk.md`、`VALIDATION_REQUEST_coverage_splitk.md`。下一步先验证 UB 回退能被真实 CANN tiler 接受，再验证低核数的输出覆盖与 A1 的 FP32 精度/latency。

## 2026-09-21 · 队友 docs.zip 资料复核

- 仅资料算术/来源检查，无新 NPU 测量，无 kernel 改动。
- `python3 tools/audit_teammate_probe.py`：保存转录哈希一致；75 个粗维度/属性读数最大整数残差 0.144667；section 15 总时间复算 626.96µs。其构建归属来自队友材料，未独立验证。
- 旧 45 代理发现 14 个 K 非 8 倍数、第 14 点两个 M 超出后续推断范围，第 10 点属性存在冲突；生成 50 个合法本地验证配置，设备结果 PENDING。
- 来源、当前路径对应、旧报告矛盾与下一轮优先级见 `TEAM_PROBE_REVIEW.md`。不将历史 F12 耗时、旧路径表或单个 big08 profile 计为当前性能证据。

## 2026-09-21 · n-split-critical-work

父提交8fb1e72；kernel SHA256 `e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。新增65行kernel host调度代码；不改设备算术和事件代码。

- `python3 tools/validate_nsplit_work.py`：38,880调度配置与独立逐tile oracle一致，8,893个配置满足工作量准入；1,836行全负数据分片归约一致；宏0/1/1+TUNING及接入条件通过。数字按单套参数空间计，不将三档相加。
- 20 Cube 示例 B1/M1536/N1536/K1536：ns2→3，最忙worker tiles12→8、最大windows2→2；M3072：ns1→3、tiles24→16、windows4→4。均为CPU代理计数，非NPU时间。
- 继承回归：UB86,784、finalizer28,672、Ksplit361,152及classifier864配置通过。
- 24shape×2dtype×4layout设备清单已列；CANN编译、完整精度、正式15点、稳定态latency及msprof **PENDING**。
- 对照入口：`VALIDATION_REQUEST_nsplit_work.md`；不将这次计数改善计入性能成绩。

## 2026-09-22 · 已知问题集中修复（云端按用户指示暂缓）

分支 `experiment/known-issue-closure`；kernel SHA256 `d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。

- `31a5715`：earlySum多batch完整输出。finalizer模型扩展至49,152配置，全部唯一且完整；对照旧循环在该空间有928组遗漏、896组重复。
- `e579d8c`：manual不再申请未使用的库workspace，低核dot split的parts下限为1。
- `0d6fae8`：缓存包含全部11个Tune字段。同shape改参数不再复用旧计划。
- 追加保护：offset-zero scratch使用后标记库前缀脏；重新进入Matmul时同步并清零前缀；保留跨无workspace计划的脏状态。首次新分配不等待旧scratch使用者，因为不存在旧分配；实际resize与用途转换仍同步。
- 完整host控制流模型76,424配置通过，production和TUNING分别运行。fake tiler不构成CANN资源可行性证明。
- 真实run_kernel/cache/release代码的CPU替身检查通过：同shape调参、context隔离、复用/幂等释放、malloc/memset/sync/free失败、generic/manual/dot/GEMV之间用途转换及重试。
- 统一计划覆盖151shape×2dtype×4layout；设备未运行。CANN/NPU/正式15点/latency/msprof依然PENDING。本记录没有新增任何NPU性能数字。

## 2026-09-22 · dual-consumer-fold 设备端优化

- 分支 `experiment/dual-consumer-fold`，父版本 `35a86eb`；kernel SHA256 `8f848c4869d90f0da7a955b14b457a47ecc9a09c41e515c95efa17562916d29e`。
- `324a6a0` 将历史消费流水候选移植到当前修复版；`00a91b4` 新增原地树形tile Max，复用已有UB双缓冲。
- 默认 pipeline=2/fold=1；两条完整K dual路径接入。256列tile的WholeReduceMax调用4→1，Vector屏障8→4；无新增workspace。这是操作计数，非性能结果。
- 六种开关组合各76,800窗口配置与34,816全部列尾/行跨度配置通过；3,840抽象协议调度通过。0/0与父循环CPU轨迹一致，其余模式结果及GM读取地址一致。
- 源码逆替换验证：host planner、Cube侧、缓冲分配、末级输出、其它算子路径与父版本逐字一致。无需用host stub的重复大网格充当本次设备验证。
- CANN/NPU/正式15点/latency/msprof **PENDING**。现场依赖待确认：CANN9队列事件、Matmul flag9握手、VECIN原地Max、A2/A3分别运行。
- 执行单：`DUAL_CONSUMER_OPTIMIZATION.md`。本机未新增任何NPU耗时或速度结论。

## 2026-09-22 · cube-panel-reuse

- 实现 `bc3f7cf`，父 `48e37c7`，SHA `e440e1b3d915ba61f696059cd3af0efdee6b8d087aee04ef7a49ba40ef2a637b`；kernel新增255行。
- 新Cube生产者按N组/K面板重排，双L0C累加，A跨两个N tile复用，可选全K A常驻L1；接入既有manual AIV与Fold Max。查询实际片上容量，保留旧路径与四档对照。
- 444个物理块模型执行通过；四布局、三种新模式、K8非16对齐、M/N尾、长K、多task、奇数N组；逐元素C、补零、队列/事件计数与读取量检查。小整数输入不是FP16/BF16设备编码/舍入模拟。
- host四档production/TUNING各76,424主网格配置与额外资源检查；模式1/2/3选择11,989次，模式3中9,963次resident。fake tiler不能证明CANN可用。
- 前版消费模型与finalizer模型通过；没有新增NPU性能数字。模式1→2的A读取及L0A搬入量在成对tile上减半；resident进一步减少A GM重复读取。**不能据此报告对父版Matmul库的流量降幅/提速**。
- CANN9/A2/A3/正式15点/latency/msprof全部PENDING；四档同机执行单在 `CUBE_PANEL_REUSE.md`。用户仍暂缓云端执行。


## 2026-09-22 · hierarchical-k

- 分支 `experiment/hierarchical-k`，实现 `d64d0c1`，父 `73ed463`；kernel SHA256 `771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。
- L1面板K为L0 K的2/4倍（最多512），B1四缓冲、A1双缓冲或常驻；容量不符保留父路径。`BMMMS_L1_K_PANELS=0/1`默认1。
- `validate_cube_panel.py`：456父producer执行及584两级K执行通过；逐元素C/补零一致、读字节/L0搬运/MMAD计数不变、ND2NZ调用减少；含四布局、尾块、BK112、K8192。
- `validate_host_plan.py`：六种宏组合×production/TUNING，各76,424主网格与额外内存边界通过。模式2/H1选中两级K 9,403次，模式3/H1 7,714次。计数包含额外检查，不是正式case覆盖率。
- 同步CPU模型和fake tiler；CANN编译、真实队列/事件、NPU精度/正式15点/latency/msprof全部PENDING。较少DMA调用可能被TX1切片LoadData及队列开销抵消，没有新增NPU性能数据。
- 设备执行入口 `HIERARCHICAL_K.md`；按用户指示云端暂缓。main kernel未合并。


## 2026-09-22 · performance-structure-fixes

- 代码 `a3c1f7d`，父 `3ca0d7c`；SHA `1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。
- 完整连续TX1切片LoadData 8→1；单N组无收益驻留取消；各C首次MMAD前才获取自己的释放事件；两份K主循环合一。
- 显式tile/window/ns最后应用且拒绝静默覆盖；split-K完整M/N保护。默认P0及预处理隔离保留原家族，显式P2/P3提供修复后候选。
- CPU：456常规+584两级K+2针对性执行通过；逐元素C/补零/地址/事件收支/操作量检查。六种host宏组合production/TUNING各76,424主网格及容量边界通过；pin与预处理、缓存、N/K/UB回归通过。旧nsplit模型抽取误包含PanelL1Capacity导致的CPU编译错误已修正。
- P3（显式）驻留选择6,026次、P3/H1两级K 8,410次；包含额外边界，不是正式case命中率。kernel净减少15行，不能作为速度证据。
- CANN编译、真实异步事件、FP16/BF16设备精度、正式15点与性能全部PENDING；没有新增NPU耗时。设备入口 `PERFORMANCE_STRUCTURE_FIXES.md`。

## 2026-10-01 · C9队友K packages与通过TT组合

- `experiment/c9-k-packages` / `d19af3d`，kernel SHA `5dcb7230bef7e8935aabe6c6c80560dfb0f2d1103b5a5ea223b217bdbe075ebd`；从 `0d4bd04` 仅提取队友FP16/NT/dual20完整A+B大K包/晚ring credit与C9桶覆盖。
- [正式任务 6abe2939694b590c3cdc011a](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe2939694b590c3cdc011a) Pass，CANN编译成功、15/15、precision_ratio全1。耗时μs `[2.16, 4.15, 4.51, 5.54, 5.39, 10.64, 10.26, 59.27, 68.54, 96.11, 88.66, 97.11, 16.38, 13.44, 9.75]`。
- C9父83.11→68.54，单次耗时降低17.5%/1.213x；这是复现用户报告队友约68μs，非超越队友。C8父59.66→59.27，TT保留，不宣称稳定微小收益。其它路径未改，时间变化不归因。没有actual shape/plan/SoC/profile或重复A/B，不推断case路线或排行榜得分。
- CPU177producer+177延迟MMAD、9216消费者；fake/公开固定8.3 tiler production/TUNING各2560/128通过。MTE1仍同步，不把模型当硬件精度/同步/时间证明。无新GM/flags或main/golden修改。
- 无活动任务；原始JSON/模型本机Git忽略 `artifacts/c9-k-packages/`。交接 [C9_K_PACKAGES.md](C9_K_PACKAGES.md)。后续以此组合为父版，勿丢C9收益。

## 2026-10-01 · TT跨tile B1包流水

- `experiment/tt-b-package-stream` / `eb4671c`，kernel SHA `8c03d710d5394a0660e6bedc4c172f7784a1cbe3ef9f1cbc450f231aa1d6a052`，父组合 `4ac80c9`。两个B1手动slot、显式MTE1↔MTE2 credit、按L1选包K、跨Nt/M/batch cursor预读；无新GM/flags/ABI，kSplit仍1、完整K后Max，原Vector与C9逐字保留。
- [正式任务 6abe3059694b590c3cdf6c87](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe3059694b590c3cdf6c87) Pass，CANN编译成功、15/15、precision_ratio全1。耗时μs `[2.15,3.97,4.30,5.60,5.40,10.51,9.68,49.38,67.48,98.19,87.77,96.70,15.25,13.02,9.20]`。
- C8 59.27→49.38，单次耗时降低16.7%/1.200x；C9 68.54→67.48，其路径未改，不归因波动。没有actual shape/plan/SoC/profile或重复A/B，不称稳定或推断分数。
- CPU440立即/440延迟MTE2-MTE1-MMAD/440 eagerMTE2、缺reader等待负控制；原420producer/160全部bit模式通过；fake/公开固定8.3 host production/TUNING各6912/720/576通过。A1 queue仍抽象、Fixpipe同步，不代替native时序/硬件精度。
- 保留为新的通过父版，无活动任务。原始JSON/模型本机Git忽略 `artifacts/tt-b-package-stream/`；交接 [TT_B_PACKAGE_STREAM.md](TT_B_PACKAGE_STREAM.md)。下一核对manual基本NZ ring输出，先对比历史库/回调NZ无收益或runtime失败，避免重复。

## 2026-10-01 · 手写TT原生NZ ring

- `experiment/tt-native-nz-ring` / `84e830e`，kernel SHA `30a697cc03f6aa3ec39f81275ddcfa27f10aaf4f1d31e0cd4bcbfc51bf6ce233`，父 `e1b3634`。仅手写TT基本Fixpipe CFG_NZ写原ring、AIV slab DMA/tree Max；输入流水/host/UB/GM/flags/C9保持，无新GM通路，不使用旧Matmul callback。
- [正式任务 6abe3b9b694b590c3ce5450f](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe3b9b694b590c3ce5450f) Pass，CANN编译成功、15/15、precision_ratio全1。耗时μs `[2.09,4.18,4.34,5.38,5.72,10.78,10.21,50.44,68.57,97.94,89.23,96.42,15.90,13.43,9.11]`。
- C8 49.38→50.44，单次未观察到新增收益，归档并恢复父。C9未改，不归因67.48→68.57波动；无actual shape/plan/SoC/profile或重复A/B，不推断路径命中、瓶颈或稳定差异。
- CPU440立即/440延迟引擎/440 eagerMTE2、420旧producer/160 raw-bit、9216实际NZ消费者及无N-tail mask负控制通过；host/预算逐字父，沿用父证据。本模型Fixpipe同步、A1 queue抽象，不是完整硬件时序或舍入模拟。
- 无活动任务，原始资料本机Git忽略 `artifacts/tt-native-nz-ring/`；交接 [TT_NATIVE_NZ_RING.md](TT_NATIVE_NZ_RING.md)。后续勿重复NZ格式/旧callback候选，保留C9与49.38μs组合。

## 2026-10-01 · C7完整输入与完整A2驻留

- `experiment/c7-full-inputs` / `2dc7f30`，kernel SHA `e8a1512e88e3cc71069d501b9cb934917ac2717cde772f83a9f6fad0daf7f6bb`，父 `fd72a34`。完整A/B一次ND2NZ到L1、完整A留L0A、按N片段完成全K MMAD，复用原direct-batch Vector/ring/credits/grid/workspace；C8/C9逐字保持，无新GM/ABI。
- [正式任务 6abe5f1e694b590c3cf8ca02](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe5f1e694b590c3cf8ca02) Pass，CANN编译成功、15/15、precision_ratio全1。耗时μs `[2.17,4.04,4.36,5.56,5.37,10.35,9.40,50.15,67.59,97.01,86.89,96.13,15.28,13.00,8.96]`。
- C7父9.68→9.40，单次约2.9%，尚未形成明显收益，不当新增重大突破；C8/C9未改，不归因变化。无actual shape/plan/SoC/profile或重复A/B，不推断路线命中、稳定差异或瓶颈。
- CPU86立即/86延迟live MMAD、2592实际原全M/零行消费者、缺last-reader wait负控制通过；fake及固定公开8.3 production/TUNING各3456/432。模型MTE1/Fixpipe同步，没有FP16舍入和全硬件配置时序，不代替设备精度/时间。
- 无活动任务，源码和证据保留独立分支，不合main；原49.38μs组合保持。资料Git忽略 `artifacts/c7-full-inputs/`；交接 [C7_FULL_INPUTS.md](C7_FULL_INPUTS.md)。下一评估C7专用Vector消费，当前未实现，不重复附近N块参数。

## 2026-10-01 · C7专用单C缓冲Vector

- `experiment/c7-lean-vector` / `a3696cd`，kernel SHA `0fa24fce76929aee569311905518ee963be5097e7589161a6c525f1996eb6b05`，父 `d793083`。仅dual34专用消费：空闲AIV零UB，活动AIV单C TBuf、有效N树形Max→一次有效M WholeReduceSum→唯一4byte y；四个HardEvent保护C/sum和原GM信用。Cube/host/grid/原GM/workspace/C8/C9及其它Vector逐字保持父。
- [正式任务 6abe6705694b590c3cfd63c9](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe6705694b590c3cfd63c9) Pass，CANN编译成功、15/15、precision_ratio全1。耗时μs `[2.12,3.91,4.33,5.53,5.46,10.72,9.55,49.74,67.73,99.48,88.31,96.83,15.95,13.30,9.12]`。
- C7父9.40→9.55，无新增收益，归档；C8/C9未改，不归因波动。没有actual shape/plan/SoC/profile或重复A/B，不推断路线、瓶颈或稳定差异。原49.38μs TT+约68μs队友C9组合保持，不合main。
- CPU1296实际helper：三独立引擎队列/live generation、poison ring、负数/尾块、cyclic/idle、零行无分配及唯一y/guard/credits通过；缺四个Fence、无N尾mask、早信用六负控制通过。合成Cube/companion不是完整原生协议，不模拟舍入或硬件时间。
- 无活动任务；原始资料本机Git忽略 `artifacts/c7-lean-vector/`；交接 [C7_LEAN_VECTOR.md](C7_LEAN_VECTOR.md)。下一恢复 `e1b3634`，审查C9手写完整window的serial DMA/V与late信用，必须区分旧库dual1/2+flag9/fold组合，先源码同步模型，不重复旧组合提交。

## 2026-10-01 · 队友tiny核心与通过TT/C9组合

`experiment/teammate-tiny-dot`，实现 `0beb87d`，kernel SHA `7d629cfb0bb821fa8be65cfbb7164f72486f8845882fd974b86aa326cd1168e3`。正式任务 **`6abe7b90694b590c3c08ed48` Pass，CANN编译成功、15/15、precision_ratio全1**。耗时μs `[1.98,2.63,3.66,4.13,5.70,10.75,10.25,50.72,68.02,99.81,89.21,97.18,16.30,13.44,9.64]`。
父C1..4 2.15/3.97/4.30/5.60；本次C2降低33.8%、C3降低14.9%、C4降低26.25%，均单次正式测量，不证明稳定收益。C8/C9源码保持，50.72/68.02变化不归因；没有实际shape/plan/SoC/profile。原始资料 `artifacts/teammate-tiny-dot/official.json` Git忽略。
用户要求直接测队友原版，下一独立 `experiment/teammate-tiny-original` 保存原文件逐字快照，仅官方原模板替换kernel，CLI提交、保存ID、查询终态，然后与本版逐case对比。当前通过组合保留，不混入C9 WIP，不移main/历史标签。


## 最新：tiny容量准入/batch分组正式15/15通过，C3 3.06μs

`experiment/tiny-batch-coverage`，实现 `03e352b`，kernel SHA `e662891f722c132b93f9b3a6ab31514217c38fdf7e2221715bc138e0d01d0726`，317894byte。正式任务 **`6abe82b1694b590c3c0cf647` Pass，CANN编译成功、15/15、precision_ratio全1**。μs `[2.01,2.75,3.06,4.04,5.34,10.72,10.00,49.86,68.03,98.51,88.17,96.71,15.62,13.26,9.47]`。
C3组合父3.66→3.06，单次降低16.4%；队友原版3.14。C15 9.47、C8 49.86/C9 68.03相应源码未改，不归因波动。C2 2.63→2.75，单次有退化，不掩盖；没有实际shape/plan/SoC/profile/重复A/B，不能证明稳定幅度或确切路径。通过源/完整模型和证据保留，不合main。
下一从本通过版新分支学习队友single_tile和direct_batch：队友FF/TT单tile的Vector取消SyncAll和partial merge；NT手动L1/L0/UB取消TPipe初始化、A/B独立就绪、完整padded C DMA和lane-fold后一次树Max。不要混入更广Cube准入/其它manual或未验证C9窗口。原始结果忽略 `artifacts/tiny-batch-coverage/official.json`，没有活动正式任务。


## 最新通过组合：tiny容量/batch分组 + 队友single_tile，15/15通过

当前 `experiment/teammate-single-tile`，实现 `889afe0`，kernel SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597byte。正式任务 **`6abe860d694b590c3c0f02a5` Pass，CANN编译成功、15/15、precision_ratio全1**。μs `[1.97,2.39,3.12,4.04,5.28,9.85,9.59,49.78,67.51,97.43,86.97,95.62,14.76,12.61,9.34]`。
本实验父tiny分组版C6 10.72→9.85，单次降低8.1%；C5 5.34→5.28，仅小幅；C3 3.06→3.12略退，不能忽略。两次学习合计对更早组合 `d5cd4af`：C3 3.66→3.12（单次14.8%），C6 10.75→9.85（单次8.4%）。队友原版C3/C5/C6 3.14/5.21/9.73，与当前相近；当前C15 9.34保留原组合相对原版12.53的优势，但C15本实验源码未改，不归因变化。
C2 2.39、C8 49.78/C9 67.51及其它未改路径的变化不称本实验收益。没有实际shape/plan/SoC/profile或重复同机A/B，不保证稳定幅度、路径命中或推算榜单分数。全部改动仅kernel，独立原模板其它8文件不变；原始JSON/CPU日志Git忽略 `artifacts/teammate-single-tile/`。
6864实际Vector/1280实际物理Cube模型及四负控制通过；模型同步Vector/MMAD/Fixpipe、MTE2可延迟，整数转换不模拟FP16/BF16编码，跨核ready抽象。实际设备编译/15点精度通过单独报告。父tiny分组 `f7c2c74` 和更早组合/队友原版分支保持，main和历史标签不动；当前工作区干净，没有活动正式任务。
下一可执行动作：`git switch -c experiment/small-tile-coverage`，对照 `git show 9ab2312:kernel.asc` 的 `previousSmall/expandedSmall/SmallFullTileFits/dual23` 与当前 `ClassifyMeasured`：目前完整batch Cube仍只覆盖历史三个桶，队友泛化到资源允许的全部小矩阵，并通过round-robin处理B>AIC。先审核UB/L1/L0和repeat/mask限制、实际队列/唯一writer，再决定移植；不能直接粘整个host、重交相邻参数或丢当前tiny/C15。这个泛化目前**尚未实现/未提交**，C9窗口WIP仍独立归档。


## 当前：同一kernel两次复测已完成，三次均15/15通过

用户要求“一模一样再交两次”，已严格完成两次，未额外创建其它任务。首次 `6abe860d694b590c3c0f02a5`、复测1 `6abe87e6694b590c3c102b8c`、复测2 `6abe88a7694b590c3c109c3a`，均Pass、CANN编译成功、15/15、precision_ratio全1。kernel全程不动，实现 `889afe0`，SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597bytes；独立模板和每次提交文本一致，按前一个任务终态后才提交下一个。

| Case | 首次 μs | 复测1 μs | 复测2 μs | 中位数 μs | min–max μs | 极差/中位数 |
|---|---:|---:|---:|---:|---:|---:|
| C1 | 1.97 | 1.90 | 1.98 | 1.97 | 1.90–1.98 | 4.1% |
| C2 | 2.39 | 2.46 | 2.56 | 2.46 | 2.39–2.56 | 6.9% |
| C3 | 3.12 | 3.18 | 3.21 | 3.18 | 3.12–3.21 | 2.8% |
| C4 | 4.04 | 4.04 | 4.04 | 4.04 | 4.04–4.04 | 0.0% |
| C5 | 5.28 | 5.31 | 5.19 | 5.28 | 5.19–5.31 | 2.3% |
| C6 | 9.85 | 9.72 | 9.46 | 9.72 | 9.46–9.85 | 4.0% |
| C7 | 9.59 | 10.28 | 10.14 | 10.14 | 9.59–10.28 | 6.8% |
| C8 | 49.78 | 49.59 | 50.26 | 49.78 | 49.59–50.26 | 1.3% |
| C9 | 67.51 | 67.60 | 68.27 | 67.60 | 67.51–68.27 | 1.1% |
| C10 | 97.43 | 98.18 | 99.33 | 98.18 | 97.43–99.33 | 1.9% |
| C11 | 86.97 | 88.17 | 88.85 | 88.17 | 86.97–88.85 | 2.1% |
| C12 | 95.62 | 96.84 | 96.62 | 96.62 | 95.62–96.84 | 1.3% |
| C13 | 14.76 | 15.48 | 15.76 | 15.48 | 14.76–15.76 | 6.5% |
| C14 | 12.61 | 13.33 | 13.38 | 13.33 | 12.61–13.38 | 5.8% |
| C15 | 9.34 | 9.42 | 9.13 | 9.34 | 9.13–9.42 | 3.1% |

波动指标定义为 `(max-min)/median`，不是置信区间、变异系数或稳定误差界。C2 6.9%、C7 6.8%、C13 6.5%、C14 5.8%，说明几%的单次差异不能直接当算法收益。C3中位3.18、范围3.12–3.21；C6中位9.72、范围9.46–9.85；C15中位9.34、范围9.13–9.42。
C3/C6的新版本三次均低于更早组合 `6abe7b90694b590c3c08ed48` 的单次3.66/10.75，但旧版未同样复测且没有实际同机shape/plan/SoC/profile元数据，不把具体百分比称为稳定或因果收益；三次也不足以界定总体分布。C5与父tiny分组版5.34、队友原版5.21的单次微小差距均不构成可靠新收益。C7/C13/C14及其它不相关路径未改，其变化不归因。
全部资料推送当前 `experiment/teammate-single-tile`，main/历史标签不动。原JSON分别忽略 `artifacts/teammate-single-tile/official.json`、`repeat1.json`、`repeat2.json`；摘要见 `docs/SINGLE_TILE_REPEATS.md`。没有活动任务，kernel保持通过版。
下一可执行动作：继续当前源码与 `git show 9ab2312:kernel.asc` 的资源化small-tile覆盖审查，按此前执行单先验证 `previousSmall/expandedSmall/SmallFullTileFits/dual23` 的容量、repeat、batch ownership和同步。不继续原样重交；若之后要精确量化某算法收益，需旧版与新版交错重复A/B和实际设备元数据。小矩阵泛化尚未实现/未提交。


## 2026-10-02 · C7手动物理frame正式通过

## 正式结果

[任务 6abe9804694b590c3c18f362](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe9804694b590c3c18f362) **Pass，CANN编译成功、15/15，precision_ratio全1**，kernel SHA保持。μs：

```text
[1.99,2.48,3.16,4.01,5.46,9.96,8.00,50.67,67.89,98.21,88.06,96.43,15.76,13.15,9.81]
```

C7 8.00，比父三次最快9.59低16.6%，比中位10.14低21.1%，已超出父样本9.59–10.28区间和6.8%极差/中位数，形成值得保留的单次结构收益。不是同机受控A/B或稳定因果收益证明，actual shape/plan/SoC/profile仍缺失；其它路线未改，不归因其波动。下一原样再确认一次该较大差距，不扫描参数；若复测回到父波动带如实记录。

原始JSON Git忽略 `artifacts/c7-manual-frame/official.json`。通过版保留独立实验分支，main/历史标签不动。

## 2026-10-02 · C7手动frame原样确认7.88 μs

## 原样确认结果

[任务 6abe98e5694b590c3c195fc5](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe98e5694b590c3c195fc5) **Pass，CANN编译成功、15/15、precision_ratio全1**。代码/kernel/template原样保持，μs：

```text
[1.99,2.49,3.08,4.04,5.28,9.73,7.88,50.72,67.77,98.46,88.48,96.56,16.04,13.26,9.55]
```

新C7两次8.00/7.88、中位7.94；父同kernel三次9.59/10.28/10.14、中位10.14、区间9.59–10.28。候选两次均低于父样本区间，中位耗时低21.7%；最快父到最慢候选仍低16.6%。两次不是总体统计或严格同机交错A/B，actual shape/plan/SoC/profile仍未知；不保证稳定因果百分比，不推算排行榜分数。其它代码路径没改，不归因其波动。父/候选5个正式任务各15Pass仍不能证明所有合法shape的native精度覆盖。

本次目标假设已有正式编译/精度/两次速度证据，可作为下一结构实验父版。没有活动任务；原始JSON Git忽略 `artifacts/c7-manual-frame/confirm.json`。main/历史标签不动，整体冲榜目标尚未完成。

## 2026-10-02 · 修复候选正式15/15，C14 10.93μs

正式任务 `6abea479694b590c3c1e1f2d` **Pass，CANN编译成功、15/15、precision_ratio全1**。代码 `8e6959b`，kernel SHA `b0e0b66495df9606156f73f1d4a1399801ab18f203ff0f9458a7051caca4150f`，340070bytes。μs：

```text
[1.91, 2.68, 3.23, 3.98, 5.2, 9.92, 7.78, 49.67, 67.24, 97.67, 87.67, 96.19, 15.12, 10.93, 9.09]
```

C14 10.93，相比最新父四次12.72–13.26、中位13.04，低于最快父约14.1%，低于中位约16.2%；大于父样本极差/中位数4.1%，可保留单次结构收益。无actualshape/plan/SoC/profile或同机交错A/B，不能证明因果稳定百分比、路径命中或计算榜单分。C7 7.78在旧候选四次7.67–8.04范围内；它和其它路线源码未改，不归因其波动。没有扩大对齐准入、不改变N分片/GM/完整K→MaxN→SumM、main/标签保持。

正式编译与15点精度表明此次无TPL入口可用于这些正式样本，不代表所有形状/SoC或者完整合法空间通过；整数模型和native证据仍分开。原始JSON Git忽略 `artifacts/wide-n-manual-frame/official-fixed.json`。下一原样确认一次该较大收益，commit/push后创建并立即保存ID，只查同ID至终态，不能继续附近参数扫描。

## 2026-10-02 · 同SHA确认，C14 10.84μs

确认任务 `6abea54c694b590c3c1e7459` **Pass、CANN编译成功、15/15、precision_ratio全1**，kernel/template原样。μs：

```text
[1.99, 2.78, 3.09, 4.01, 5.42, 9.55, 7.88, 49.56, 67.49, 97.37, 87.11, 95.56, 15.01, 10.84, 8.97]
```

两次C14 10.93/10.84、中位10.885μs；最新通过父四次12.72/12.94/13.15/13.26，中位13.045μs，候选中位低16.56%；最慢候选10.93仍比最快父12.72低14.07%，两次均低于父样本区间，可保留结构收益。没有实际同机交错A/B/shape/plan/SoC/profile，不称稳定因果百分比。C7 7.78/7.88保持父范围，其它未改路线不归因。

本候选已有CPU/negative controls、正式编译/15点精度/两次速度证据，保留为下一实验父；main/历史标签不动，无活动任务。原JSON忽略 `artifacts/wide-n-manual-frame/confirm-fixed.json`。整体冲榜目标仍未完成。
下一结构假设：TT原FinalizeFullMTiles分片M合并、写同GM partial内chunk标量、第二次SyncAll、block0二次gather/sum。评估第一barrier后复用死C UB、batch Max所有N分片并只Sum有效M，减少第二barrier和中间M scalar写/读；不得复做失败TT paired-N/worker-Max/NZ或B包扫描。当前尚未实现，需要实际helper/host容量模型、输出/尾mask/同步负控制后才能正式提交。

## 2026-10-02 · 正式通过，C8 47.24μs，仅单次小幅改善

任务 `6abea942694b590c3c1ff692` **Pass、CANN编译成功、15/15、precision_ratio全1**，实现 `5c67d94` / SHA `71ca6095958a372927c27f088bb081c43cff748169ff98e4ef80a2215b4d62c5`。μs：

```text
[1.94, 2.7, 3.22, 4.01, 5.28, 9.66, 7.85, 47.24, 67.78, 95.19, 87.89, 96.41, 15.14, 10.86, 9.53]
```

C8 47.24；父最近六次50.67/50.72/49.94/49.14/49.67/49.56，范围49.14–50.72、中位49.805。单次比中位低5.15%、比最快低3.87%；父极差/中位数3.17%，候选在父样本区间外，但没有同机A/B或重复候选，不能称大突破或稳定收益。源码有效减barrier/GM中转，native已验证这些正式样本可安全复用死UB，所有形状/TPipe版本/精确SoC仍未验证。C14 10.86与通过宽N的10.93/10.84相近；其它路线未改不归因浮动。

特别保留C2的不利观测：宽N前四次2.42–2.50，宽N两次2.68/2.78，TT本次2.70。其源码路径未改，仍不能把上升简单消除为噪声或精确归因；没有相同设备交错旧/新，整体最优/榜分未证明。不能仅C14变快就断言整体分数必升。

本候选保留独立分支作为后续结构对照，不再原样提交小幅收益、不扫描tile/分组参数，不合main；最近有两次明确结构收益的组合仍是 `experiment/c14-manual-frame` / `cf16501`。原JSON Git忽略 `artifacts/tt-single-barrier/official.json`，没有活动任务。源码/模型/终态已push，整体冲榜目标仍未完成。

下一需优先两个真实剩余风险：TT在RunManualFullMCube里仍以TPipe/A1 TQue/TBuf及动态event初始化大Schedule，Vector仍每tile重复queue/Max init（旧workerMax无收益不能重复）；研究32byte固定局部frame保留已有B包流水、完整K/MMAD及原task/GM，改变物理生命周期/框架开销，与旧frame方案逐字scope/实际live模型核对后才实现。C2需查看当前和队友tiny入口的启动/地址/归约差别，保留当前资源化batch正确处理，不能盲换whole source或把C14优化回退后总耗时直接当榜分。


## 2026-10-02 · 当前通过组合版再次原样复测两次

用户再次要求当前版同源码两次，已完成 `6abeceed694b590c3c2bc7a5` / `6abecfc5694b590c3c2c1347`；两次均15/15 Pass、precision_ratio全1，与首次 `6abeb39e694b590c3c22e5d7` 同SHA `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742` /354602bytes。第二次第一次POST HTTP429无ID，等待45秒后成功。全部工程源码逐字等于1734f16，只有kernel提交；无算法修改。

| Case | 首次 μs | 复测1 μs | 复测2 μs | 中位数 μs | 极差/中位数 |
|---|---:|---:|---:|---:|---:|
| C1 | 1.99 | 1.93 | 1.92 | 1.93 | 3.6% |
| C2 | 2.46 | 2.62 | 2.49 | 2.49 | 6.4% |
| C3 | 3.11 | 3.08 | 3.06 | 3.08 | 1.6% |
| C4 | 4.12 | 4.12 | 4.15 | 4.12 | 0.7% |
| C5 | 5.39 | 5.26 | 5.43 | 5.39 | 3.2% |
| C6 | 9.97 | 9.76 | 9.87 | 9.87 | 2.1% |
| C7 | 8.16 | 8.11 | 8.38 | 8.16 | 3.3% |
| C8 | 46.52 | 46.51 | 46.48 | 46.51 | 0.1% |
| C9 | 67.79 | 67.88 | 67.91 | 67.88 | 0.2% |
| C10 | 99.14 | 97.92 | 99.35 | 99.14 | 1.4% |
| C11 | 88.03 | 87.73 | 88.30 | 88.03 | 0.6% |
| C12 | 96.45 | 96.34 | 96.90 | 96.45 | 0.6% |
| C13 | 15.49 | 15.56 | 15.71 | 15.56 | 1.4% |
| C14 | 11.01 | 10.88 | 10.93 | 10.93 | 1.2% |
| C15 | 9.56 | 9.05 | 9.60 | 9.56 | 5.8% |

C8中位46.51、极差0.09%，C9中位67.88、极差0.18%；C2极差6.4%、C15极差5.8%。这是三个同源码样本，不是受控同机A/B或总体波动界。C8比父三次中位48.45低4.0%，仍为小幅观察收益；C7本组8.11–8.38高于较早四次7.67–8.04，完整保留，不择优报告。无实际SoC/shape/plan/profile，不能推算榜分。完整摘要见CURRENT_IDENTICAL_REPEATS，原JSON忽略artifacts/current-identical-repeats。没有活动任务；Git分支experiment/current-identical-repeats，算法SHA保持，main和标签不动。


## 2026-10-02: best-source two extra repeats requested by user

Same1734f16/62ad1cd kernel SHA a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742, 354602bytes. 6abfc955694b590c3ca51a64 / 6abfca4d694b590c3ca5b6a8 both Pass15/15, precision all1. Totals 464.23/465.68us; means using userT 50.58646/50.82629, calculated not public leaderboard evidence. Second task creation encountered two429 responses without IDs, waited before success. Exactly two tasks created, no active task. Full15 times/spreads and evidence limits in BEST_IDENTICAL_REPEATS_1002. No algorithm changes. Overall optimization incomplete.


## 2026-10-03: two more unchanged best-kernel repeats requested

Same1734f16/a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742/354602bytes. 6ac08cd7694b590c3cf7a7d8 / 6ac08d9c694b590c3cf806ec both CANN compile success, Pass15/15, precision all1. Totals 464.52/471.22us; calculated means using userT 50.84691/50.01648. C13 15.13/16.74us, C4 3.94/4.12, C9 67.35/68.07, C11 87.35/88.91; unchanged-source variation, not algorithm improvement. Actual SoC/shape/plan/profile unavailable. Exactly two new tasks; no active task or429. Full results in BEST_IDENTICAL_REPEATS_1003. No source changes; raw artifacts ignored. Overall competition goal incomplete.


## 2026-10-03: additional single repeat requested

Task 6ac0d57f694b590c3c252456 Pass15/15, all precision_ratio=1, CANN compile success. Same1734f16 SHA a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742, 354602bytes, no algorithm or parameter change. Times(us): `[1.9, 2.53, 3.08, 4.08, 5.27, 9.8, 8.18, 46.78, 67.95, 98.24, 88.02, 97.08, 15.99, 10.77, 9.22]`. Total 468.89us, userT mean score 50.58201 (calculated, not leaderboard evidence). Single request complete, no active task. Full record BEST_IDENTICAL_REPEATS_1003; raw artifact ignored extra-one.json. Overall optimization incomplete.


## 2026-10-03: user supplies corrected Tbest

NewTbest(us)=[1.23,1.73,2.34,2.76,3.92,6.46,6.40,17.32,50.10,68.52,70.09,81.09,9.04,9.52,8.11]. Latest task6ac0d57f still468.89us, now56.42050 calculated mean instead of old-reference50.58201. Prior two October3 runs57.00705 /55.29167. Full latest per-case and recent-five recalculation in SCORE_REFERENCE_1003. All native results/source unchanged; no new task. Historical oldT results preserved, do not mix scoring references or infer optimization/rank from recalculation.


## 2026-10-08: C3 static frame / validN-only dot reductions

Branch experiment/tiny-ft-static-frame, parentbfd5d0a/algorithm1734f16. New userTbest priorities from five same-SHA medians and the historical supplied leader: C3/C13/C11/C9/C1; see SCORE_PRIORITIES_1008. New candidate only three additions92lines, SHA515aa1592edbb26252b06b0ec610fc96d7c1353f69347a9e3b92327f39f5e024. StaticM/K/NP UB map,4B actualN, validN-only dots, compactM Max/Sum; no newGM or plan/grid changes. CPU1024entries/512 encodedFP16/eight queued negative controls; production andTUNING each4800host/96hits+256 complete conditional range/exactUB/core checks passed. Models are not native timing/precision. Full evidence TINY_FT_STATIC_FRAME.

Temporary publicCLI/template files were purged byOS. Restored source template other7 files from1734f16, publicCLI from ignored local tooling cache, no credential read/copy. CLI dry-run failed because saved session expired/damaged; requested user relogin. No native submission created, compile/precision/performance PENDING. Candidate code ready for review/continuation; whole goal incomplete.

User replied logged in; retry still fails before native task creation. Default session metadata (stat only, no content read) last modified October3; requested login via restored CLI or alternate session file path. Native gate still PENDING, no task ID.

CLI login restored; dry-run payload and protected-seven template equality passed. a3c6217 pushed; task6ac72eaa694b590c3c97d81d created once, native result PENDING. Query same ID to terminal; no resubmission.

## 2026-10-08: C3 static-frame terminal, no clear gain

Task6ac72eaa694b590c3c97d81d /implementationa3c6217/SHA515aa159… Pass15/15, allprecision1. Timesus `[2.01,2.71,3.10,3.92,5.48,9.83,8.31,46.51,68.55,98.23,88.84,97.73,16.50,11.40,9.07]`; total472.19us, newTbest calculatedmean55.19646. C3=3.10 within parent recent-five3.08–3.22/median3.16, earlier3.06; no clear gain. No actualshape/plan/SoC/profile, no route-hit evidence; unchanged-route timings not attributed. Archive candidate, no identical confirmation or nearby scans, restore1734f16. RawJSON ignored artifacts/tiny-ft-static-frame/official.json. No activejob; whole competition goal incomplete. C13 actualhost CPU-stub audit4096plans separately saved, not device/profile evidence.

Restored whole kernel byte-equal1734f16/a5eef105…/354602bytes on experiment/c13-frame-audit-1008. Candidate/results remain pushed16ce102. C13 next frame hypothesis unimplemented; no activejob, login available, goal incomplete.

## 2026-10-08: user supplies newest Tbest and 82.15 leader row

NewestTbestus=[1.18,1.54,2.13,2.37,3.57,6.38,6.37,13.88,48.30,64.85,67.87,80.65,7.31,7.59,7.84], supersedes prior reference. User leader FDTIANGONG/Young timesus=[1.24,1.58,2.16,2.41,4.00,6.60,6.68,26.12,50.95,68.01,69.59,83.43,10.20,9.51,9.04]; supplied timestamp2026/10/07 07:32:10/score82.15. Recalculated82.15390 matches rounded supplied score. Latest passed parent6ac0d57f now50.99873; rawtimings/source unchanged. New gap priorities from five sameSHA medians C4/C2/C3/C6/C1/C10; full15 contribution table SCORE_REFERENCE_1008. C13 frame already underway and will finish this single structural gate; not an unchanged repetition or parameter scan. No live leaderboard/actualplan/profile claim.

## 2026-10-08: C13 manual physical frame candidate ready

Parent1734f16/a5eef105; experiment/c13-manual-frame candidate365034bytes/SHA92c3654faef7db189c167846215a96ab0dcf937b0833ef36b90f8b35d3158d28. Three additions191lines restore whole parent. Removes TPipe/TQue from FF dual14 tails, retains128K panels/stridedM tasks/double C/ring/earlyslots, 64row completeN sum and deadUB final frame. No newGM/plan change. CPU324 producer configurations/six negative controls,768 threaded AIV configurations/nine controls; production/TUNING each4096actualhost/3968hits and exactmemory/core/workspace/adjacent fallback passed. CPUinteger/syntheticcredits, not nativeFP16/CANN. Independenttemplate protected7 equal1734f16; dry-run onlykernel/SHAconsistent. Native compile/precision/latency PENDING, no taskID yet. Full evidence C13_MANUAL_FRAME. NewestT priorities C4/C2/C3/C6/C1/C10, current C13 sole structuralgate completed first; no parameter scan.

C13 implementation59c59e2 pushed; unique formal task6ac733cd694b590c3c9b7892 created. Query sameID to terminal, native gate PENDING. No resubmission.

## 2026-10-08: C13 manual-frame terminal


任务 `6ac733cd694b590c3c9b7892`：Pass15/15，precision_ratio全部1。耗时μs：

[2.02, 2.54, 3.1, 4.14, 5.09, 9.72, 8.16, 45.99, 67.71, 98.7, 88.42, 96.59, 16.0, 10.76, 9.62]

总耗时468.56μs；最新10月8日Tbest重算均分50.61753。C13=16.00μs，父最近五次14.94–16.74、中位15.13；没有明显收益，不原样确认或附近参数扫描。其它点变化不归因于C13路径。没有实际隐藏shape/plan/SoC/profile，不能证明路径命中或硬件全shape安全。原JSON在忽略artifacts/c13-manual-frame/official.json，摘要保留。候选及模型留在experiment/c13-manual-frame，后续从通过1734f16恢复独立C4方向。

## 2026-10-08: C4 TT direct Cube routing ready

Parent restored whole1734f16; candidate356697bytes/SHAe30524ac5ffa748457f3e0c10712251366083c1ff8349341bf0d0c0c38d69664, only40lines/twoadditions. Existing TT DIRECT_BATCH function reused ahead of SmallVector, full actualcore/capacity/originalworkspace/plan/TUNING guard; no device/API/GM changes. CPU768physicalCube configurations,11264AIVentries, production/TUNING each32768actualhost plans/18432hits, six negative controls rejected (A/B inputready and M/N mask/inputDMA/terminal). Vector model is synchronous and cannot detect missing V_MTE3; no such claim. Protected7 byteequal1734f16, dry-run onlykernel/SHAverified. Native CANN/BF16 precision/latency PENDING, no taskIDyet. Full evidence C4_TT_DIRECT_CUBE.

C4实现6bad2b4已push；唯一正式任务 **6ac736e7694b590c3c9db696** 已创建。只查询同ID至终态，不重交；native gate PENDING。

## 正式终态：通过但明显退化，归档

任务6ac736e7694b590c3c9db696，实现6bad2b4，SHA e30524ac…：Pass15/15、precision_ratio全部1。耗时μs：

[1.85, 2.47, 3.28, 7.81, 5.29, 9.47, 7.71, 46.3, 67.93, 97.84, 88.56, 96.89, 15.98, 10.82, 9.19]

总471.39μs，最新Tbest计算均分50.30139。C4=7.81μs，父最近五次3.94–4.12，中位4.08；明显退化，不能保留，不原样确认或附近参数扫描。所有其它点完整保留，未改路线变化不归因本轮。原JSON忽略artifacts/c4-tt-direct-cube/official.json。候选/测试/结果保存在本分支，后续恢复完整1734f16。用户此时提供具体shape图片；独立CPU审查并保留dtype/layout的缺失，不冒充正式metadata或profiling。当前无活动任务。

## 2026-10-08: exact-shape image changes routing diagnosis

Supplied15B/M/N/K and baseline times withoutdtype/layout/SoC/formalID/script; CSV exact_shapes_user_1008. Baseline notTbest. Whole1734f16 restored. Actualhost CPUstub480configurations across1/8/20/32cores/all8dtype/layouts: under20cores+historicaltype/layout C13(8192,64,128) dual3/tree16 excludedbydual14frame; C11(1536,2048,2048) dual2/BM128BN256/Nsplit8 excludedbyTTframe; C6(23,73,192) existingdynamicKP DIRECT_BATCH, notfullyconstantBN96. Notdevicepath/profile evidence, C10conflictpreserved. Fullsummary EXACT_SHAPE_AUDIT_1008. No newformaljob. NextactualC13resident-B framework retainingoneBload/L0residence/fullK/GM; requiresnewphysicalmodels. Initial documentation generation failed before writing due stdin encoding; retried ASCII source, no algorithm/model/result altered.

## 2026-10-08: exact C13 resident-frame candidate ready

Parentwhole1734f16; 178lines/threeadditions,364169bytes/SHA0794a2bfc777ac48c373b3085cd96fd1224b0bf0a4f6a9351d290bb421dbad2d. New suppliedexactshape C13(1,8192,64,128), historicalFP16/FF, targetsoriginaldual3/tree16 notoldtaildual14. OneBload/L0Bresidence, fullK128, originalstridedM/doubleC/workerpartials/GM retained, explicitframes replaceTPipe/TQue andredundantMax. CPU96producer/sevencontrols,102threadedAIV/sevencontrols, production/TUNING each5120host/fourhits passed; SyncAllmodeldrainsMTE3 so removalofMTE3_Valone undetected, devicewaitretained/nofalsecontrolclaim. Whole-parent/protected7/CLI dry-runonlykernel/SHAverified. NoformalIDyet, nativegatePENDING. FullC13_RESIDENT_FRAME.

Implementation7492776 pushed; unique formal task **6ac73bd0694b590c3ca19b3d** created. Query sameID to realterminal, no resubmission; nativegatePENDING.

## First formal terminal: Pass, substantial C13 observation

Task6ac73bd0694b590c3ca19b3d /implementation7492776/SHA0794a2bf: Pass15/15, allprecision_ratio1. Timesus:

[2.02, 2.48, 3.08, 4.16, 5.37, 9.78, 8.25, 46.5, 68.11, 100.24, 88.9, 96.47, 12.62, 11.14, 9.51]

Total468.63us; latestTbest calculatedmean50.75856. C13=12.62 vsrecentfiveparent14.94-16.74/median15.13:16.59percent belowmedian,15.53percent belowfastestparent. Largerthan recentparent spread/median11.90percent, warrantsONE unchangedconfirmation. Noactualshape/plan/SoC/profile or interleavedA/B; cannotclaim stablecausalpercentage/devicecounter/route trace. C10=100.24 andC14=11.14 unfavorable observations retained; unmodifiedroutes notattributed. RawJSON ignoredartifacts/c13-resident-frame/official-one.json. Firsttask terminal, noactivejob beforeconfirmation.

One unchangedconfirmation task **6ac73c8b694b590c3ca2153b** created after kernel/template equality check. SameSHA0794a2bf. Save/querythisID toterminal; no further repeats requested.

## Unchanged confirmation terminal: keep the local C13 gain

Confirmation6ac73c8b694b590c3ca2153b, sameSHA0794a2bf/364169bytes; protected7/template byte checks passed. Pass15/15, allprecision_ratio1. No more repeats outstanding; no activejob.

|Case|First us|Confirmation us|
|---|---:|---:|
|C1|2.02|1.92|
|C2|2.48|2.67|
|C3|3.08|3.18|
|C4|4.16|4.07|
|C5|5.37|5.29|
|C6|9.78|9.75|
|C7|8.25|8.02|
|C8|46.50|46.23|
|C9|68.11|68.48|
|C10|100.24|99.34|
|C11|88.90|88.78|
|C12|96.47|97.11|
|C13|12.62|13.19|
|C14|11.14|10.93|
|C15|9.51|9.62|

Totals468.63/468.58us; newestTbest calculatedmeans50.75856/50.71136. C13 pair12.62/13.19, midpoint12.905us, 14.71percent belowparentrecentfive median15.13. Slowestcandidate13.19 remains 11.71percent belowfastestparent14.94. Both belowparent14.94-16.74 range: retain this localized structural observation. These are two samples, not controlledsameSoC A/B or proof ofstablecausalpercent/route trace. Otherpoint fluctuations andadverseC2/C10/C11/C14 samples retained; scores/totals do NOT establish wholecompetition breakthrough. Noidenticalthirdrepeat or nearbyparameter scan.

New working baseline implementation7492776/SHA0794a2bf, onexperiment/c13-resident-frame; main/historicaltags unchanged. All other algorithms parent1734f16 intact bywhole-parent inverse proof. Native15precision gate passes, fullhardware/allshape/profile coverage stillnotclaimed. Next independent C11 library-to-existingTT-frame hypothesis, seeC11_EXACT_FRAME_AUDIT. Overallgoal active/incomplete.

## C11 independent gate archived; C13 source restored

Experimentbranch experiment/c11-exact-tt-frame terminal3c916aa/implementation9160eb2, kernel365998B/SHA4ce9ab29.34host lines routeexactassumedFP16 TT1536/2048/2048 throughunchangedmanualTT frame BM64BN256BK64PK256; noGM/plan/allocator/devicebodychanges. CPU production/TUNING each2592hostplans/fourhits, sixphysical full-K reduced-M Cube groups/sixcontrols, sixtyfullM/N threadedconsumer groups/sevencontrols passed (integers/synthetic companions only).

Formal6ac73fd0694b590c3ca4be61 Pass15/allprecision1, timesus [1.90,2.56,3.19,4.01,5.29,9.56,7.95,46.18,67.15,97.08,87.16,96.47,12.85,10.59,9.02]. Total460.96/latestuserTbest calculatedmean52.148476871. C11=87.16 within historicalunchangedroute86.97–88.91: no substantial/stable benefit, no confirmation/nearbyscan. C13=12.85 consistent withretained12.62/13.19 butnotcontrolledA/B. All adverse samples preserved, no attributionofunchangedroutes/profile/actualSoC claims. Fullresults C11_EXACT_TT_FRAME, rawignoredartifacts/c11-exact-tt-frame/official.json; models stayarchivedbranch.

Switched backexperiment/c13-resident-frame; wholekernel verifiedbyte-equal7492776/364169B/SHA0794a2bf. Noactiveformaljob/main/tag change. Nextconcrete assessment exact-C8 tails andselected C6BM32BN80KP192, respectingfailedstructures, missingdtype/layout and C10conflict. Overallgoal incomplete.

## C6 regression archived, user requests one retained-best submission

C6 archived a45ef9d/implementationf4907c3; terminal6ac744ee694b590c3ca8ea6c Pass15/allprecision1, C6=24.24us vsretained9.78/9.75. Pure Vector two-row product/reduction structure clearly regressed; no repeat/nearby scan. Full15 in C6_VECTOR_PAIRS, raw ignored archived branch artifacts. Returned whole7492776/364169B/SHA0794a2bf.

User requested one unchanged best submission plus continuing optimization, no Web. Task **6ac77103694b590c3ccaa29e** submitted once after whole-kernel/protected7/template byte checks and dry-run. Native result PENDING; query same ID to terminal. No further repeat request. C8 exact tails/local structure next; do not revive failed C6/C11/TT swaps.

## Terminal result

Task6ac77103694b590c3ccaa29e **Pass15/15**, all precision_ratio=1. Timesus:

`[1.92, 2.47, 3.09, 4.16, 5.25, 9.84, 8.36, 46.87, 68.33, 98.47, 88.61, 96.97, 13.44, 11.05, 9.22]`

Total468.05us; latest user Tbest calculated mean **51.04335964** (not a live rank). C8=46.87, C13=13.44; prior retained C13=12.62/13.19. All observations retained, no overall speed gain established. Raw ignored artifacts/best-identical-repeat-1008/official.json. No active job or further unchanged request. Actual SoC/plan/profiling unavailable.

## 2026-10-08: C8 assessments complete, retained best restored

Unsubmitted N-major268a802 physicalmodels passed butDMA269both/input+0.34%, no volume/call gain; archived, noformalID. Full-A/full-B singlepackage9782c98 native6ac77690694b590c3ccea247 Pass15/allprecision1, C8=54.17us vsretained46.18–46.87, rejecteddespite sourceDMA269→117. Full15 [1.96,2.66,3.18,4.25,5.42,9.72,7.78,54.17,67.96,97.77,87.28,96.06,12.82,10.98,9.02], total471.03/newestTmean51.37585466. Otherroutefluctuations/adverse samples retained; computedmean doesn'toverrideclear C8regression. No unchangedconfirmation/nearbyscan. Archived748c4b7/experiment/c8-full-inputs-frame; noactivejobs. Bothdocs copiedhere; actualmodels remainarchivedbranches. NoactualSoC/route/profileclaims.

Wholekernelrestoredbyteequal7492776/364169B/SHA0794a2bf onexperiment/c13-resident-frame, retainingC13localgain. User-requested ONE bestsubmission6ac77103694b590c3ccaa29e terminalPass15/all1/total468.05/newTmean51.04335964; no furtherrepeatrequests. NoWeb. Furtherindependenthypothesis must respect double-buffer overlap andactual API/state costs, not repeatresident-operand swap orsinglepackageparameter scan.

## C8 phased resident-A input ready candidate

Candidate365948B/SHAb87ec00643094e19c3c0433113480791494f8e00771887982a1766276d13e08b,42additions/10removedkernel lines; sameA1regionspublished384/384/264, fullNZ1040pitch, existingdoubleBinput preserved. NoPlan/GM/AIV/harness changes; whole7492776inversepass. CPU2160hostplans/fivehits eachproduction/TUNING,30actualproducer groups withper-byte pendingregions/fullK/paddedC/guards, ninecontrolsrejected. Exactobserved234deferredMAC snapshots withlaterAregionspending (parent0); onlysyntheticpermittedoverlap,nolatencyclaim. Input/MMADsame, DMA269→321(+19.33%), blockedfreshA1032→384rows; addedDMA/events maycostmore. NativePENDING/noIDyet, onegateaftercommit/dryrun, noWeb. FullC8_PHASED_A_READY.

Implementationaf886e1pushed; unique native **6ac7a921694b590c3cf97c01** createdonce. SameSHAb87ec006/365948B, protected7/dry-run verified. NativePENDING; querysameIDto terminal, no resubmit.

## Native terminal: Pass, modest single C8 improvement

Task **6ac7a921694b590c3cf97c01**, implementationaf886e1/SHA b87ec006/365948B, **Pass15/15**, allprecision_ratio1. Timesus:

`[1.94, 2.58, 3.21, 4.0, 5.33, 9.8, 8.32, 44.09, 68.18, 99.56, 88.9, 97.09, 12.94, 11.1, 9.85]`

Total466.89us, newestuserTbest calculatedmean **50.38880654**, notliverank. C8=44.09 vsretained latest46.87 (-5.93%), medianof46.50/46.23/46.87=46.50 (-5.18%), andfastestrecent46.18 (-4.53%). Outsideobservedretained46.18–46.87, modestsingle-localobservation; no controlledsameSoC A/B or directroute/profile evidence. C10=99.56/C11=88.90/C15=9.85 unfavorablepointsretained; otherunmodifiedroutechangesnotattributed. ThisdoesNOTprovewholecompetitiongain/largebreakthrough/stablecausalpercentage.

Keep the passed phased-A code on experiment/c8-phased-a-ready as an *experimental* forward baseline, without promoting main or the retained best branch. No unchangedconfirmation or nearbyphase-size scans (userrequireslarge gainsbefore repeats). Nativeprecisiongatepassed; fullhardwarecoverage/SoC/profileunknown. Noactivejobs/furtherbestrepeatrequests. Rawignored artifacts/c8-phased-a-ready/official.json. Originalretained7492776/SHA0794a2bf remainsavailableon experiment/c13-resident-frame.

## C10 FF B-package 正式终态：精度通过，无明确性能收益，归档

唯一任务 **6ac7aefd694b590c3cfe44d9**，实现 fd23d39/SHA31bc978f，CANN 正式编译和 **15/15 精度通过**，全部 precision_ratio=1。耗时 μs：

`[1.94,2.48,3.22,4.00,5.34,9.71,8.36,44.87,68.14,97.06,88.47,97.39,13.00,10.86,9.33]`

总和 **464.17 μs**，用户最新 Tbest 换算平均 **51.08302483**，不是实时排名。

C10=97.06，相比单次父99.56看似下降2.51%，但旧 C10 未改路径的已保存实测是96.98/98.17/97.58/97.76/98.24/98.47/99.34/100.24，候选在该范围内。没有控制同设备 A/B、命中记录或 profiling，不能宣称速度突破，也不能仅据此判定 FF 路径未命中。未改的 C8=44.87 相比父44.09略差等不利样本全部保留；整次总和和得分变化不证明此分包方案有益。

**归档，不保留这次 kernel 变化；整份恢复 af886e1/C8 phased-A**。不原样复测、不扫附近 B_PACKAGE。原始 JSON/log 在忽略的 artifacts/c10-ff-b-packages。下一步应核实正式 C10 的实际 storage/dtype/plan；不能再次用互相冲突的历史布局假设同时扩分支。

## C10 balanced actual M ownership: CPU candidate

Parentaf886e1;368782B/SHA16b51684,60additions/11removed. At4096/1280/1152/20coresmaxRows256→208, butCtiles160→200,MMAD/Bcopies2880→3600/Breads47185920→58982400(+25%). Same total math, complete N maxima andoriginal Plan/arena/credits. CPU13Cube/96 actualAIVownership-store+FinalizeRows/prod&TUNING192plans9hits/sixfaultcontrols pass. Arithmetic/sync outsideownership unchanged. NativePENDING,noID. PublicproblemAPI givesonlytestcaseIDs,noformalmeta;FF/TTconflictconditional. C10_BALANCED_M_SHARDS containsboundaries/nextgate.

Implementationa2e6763 pushed; one unique native **6ac7b3c8694b590c3c0218c4**, sameSHA16b51684/368782B, createdonce. NativePENDING; querysameID toterminal, no resubmit.

## Native terminal: Pass15, single local improvement

Task **6ac7b3c8694b590c3c0218c4**, implementation a2e6763 / SHA16b51684 / 368782B. Formal compile and 15/15 precision passed, all precision_ratio=1. Times us:

`[1.9, 2.87, 3.1, 4.13, 5.37, 9.66, 8.02, 43.66, 68.75, 91.53, 88.38, 96.57, 13.02, 10.86, 9.22]`

Total **457.04us**, newest user Tbest calculated mean **51.45446223**, not a live rank. C10=91.53, 5.62% below the prior unchanged-C10 range minimum96.98 (range96.98-100.24), and8.06% below the most recent parent99.56. Consistent with the ownership hypothesis but only a single observation: no bound-device A/B, route hit or profiling. Not stable causal proof or a large whole-competition breakthrough. Adverse C2=2.87 retained; its independent tiny route was unchanged. Extra C8=43.66 fluctuation is not attributed to this C10 edit.

Keep this passed candidate as the experimental forward baseline; main/historical tags unchanged. User requires large gains before repeats, so no unchanged confirmation or neighboring ownership scans. Native15 precision passed, full A2/A3 coverage/SoC/all envelope/stable performance still unproven. No live tasks. Raw JSON ignored artifacts/c10-balanced-m-shards/official.json. Passed parentaf886e1 remains recoverable.

## C10 full M shard: CPU-verified candidate

Parenta2e6763，branch experiment/c10-full-m-shard，kernel370786B/SHA f2ea9e355ad98709a3c1c0a4cce72d1ccc6bb8c8067624e7236ffdddd13eef78，39additions/1removed。完整M分段复用B，条件4096/1280/1152/20cores在实际容量下选M208/N144/K64；oldPlan/arena/device/Vector/其余launch不变。实际抽取Cube Breads58982400→29491200，Ctiles200→180，MMAD3600→3240，A2元素23592960→42467328。速度PENDING，A2增加80%可能抵消收益。

CPU8producer/160ownership+actualFinalizeRows/912actualManualCopyC+treeMax/生产&TUNING各1120hostplans31hits/四controls PASS。BF16精度/native队列契约/实际route/SoC/profile不由整数模型证明。完整逆向等于a2e6763，protected7等于1734f16。最终隔离dry-run只有370786B/f2ea9e35kernel。尚无正式ID；仅创建一个gate，无收益恢复a2e6763，不扫相邻N。完整说明C10_FULL_M_SHARD，rawCPU ignored artifacts/c10-full-m-shard/cpu.log。

Implementation **c1a52ef** 已push；唯一正式任务 **6ac7bcb6694b590c3c08ce0e** 创建成功，同370786B/SHA f2ea9e35。Native PENDING；仅查询该ID，不重交。

## Native terminal: Pass15, clear regression, archived

Unique task **6ac7bcb6694b590c3c08ce0e**, implementation **c1a52ef**, kernel370786B/SHA f2ea9e35. Formal compile and15/15 precision passed, allprecision_ratio=1. Timesus:

`[1.89, 2.9, 3.28, 3.97, 5.42, 9.86, 8.0, 44.43, 67.96, 178.32, 88.39, 97.17, 13.14, 11.03, 9.57]`

Total **545.33us**, latestuserTbest calculatedmean **49.13404004**, notlive rank. C10 **178.32us** vsparent91.53us is **94.82% slower**, also clearly aboveolder96.98-100.24 range. Do not retain this candidate. No identicalrepeat or nearbyN/BM scans. All adverse C2=2.90/C3=3.28/C8=44.43 etc retained; unmodifiedroute changes notattributed.

CPU Breads-50%/Ctiles-MMAD-10%/totalL0elements-12.857% didnot establish hardware speed. A2+80%, largerM/nearlyfullL1/consumer andpipeline costs are diagnostic clues only, not measured bottlenecks. Actualroute/SoC/profile/bounddevice A-B unavailable. Raw ignored artifacts/c10-full-m-shard/official.json.

Archive this experiment, restore wholepassed **a2e6763** (368782B/SHA16b51684), retaining balanced ownership/C8phasedA. Main/historicaltags untouched, overallgoal remains incomplete.

Restored wholea2e6763/368782B/SHA16b51684 onexperiment/c10-pipeline-audit. FailedfullM source/models retained74f9937 onexperiment/c10-full-m-shard; terminaldocs carriedforward. No activejob/repeat/nearby scans. Nextsource pipeline audit only; no newoptimization yet.

Source audit complete: FF GMslot credit acquiredbeforeK MMAD thoughonlyFixpipe writesring; retained C9 useslateacquisition. Independent deferred-credit hypothesis documentedC10_PIPELINE_CREDIT_AUDIT, unimplemented/unsubmitted. Originalgeometry/Plan/Vector unchanged, no inputvolumeclaim. Requiredblocked-credit/readiness faultmodels beforeonegatednativeexperiment. No livejob; kernel remainswholea2e6763.

## C10 late ring credit CPU candidate

Kernel368904B/SHAdcf715a21b2ec6fa8ec3ba27f13bd3b00216bbfdba88817103349174ee3b5337, branch experiment/c10-late-ring-credit, parenta2e6763. OnlyM_BALANCEGMcreditplacementdeferred untilallKissued/beforeFixpipe; nogeometry/Plan/Vector/allocator/GM/math changes. Actualproducer delayedtwo-AIVrelease sees164blockedacquisitions/2884Kworkissued-executedwhileoldGMowned (fulltarget160/2880); nothardwaretime. Parent12sameproxygroups fourblocked/0work. CPU13producer/96ownership+FinalizeRows/production&TUNING192plans9hits/fivecontrols PASS. Wholeinversea2e6763/protected7proof. Finaldryrunonly368904B/dcf715a2kernel. NativePENDING/noIDyet, ONEgateafterpush; seeC10_PIPELINE_CREDIT_AUDIT. Rawignoredartifacts/c10-late-ring-credit/cpu.log.

Implementation **1a56211** pushed; uniqueformaljob **6ac7bfcb694b590c3c0ae962** createdonce, same368904B/SHAdcf715a2. NativePENDING, querysameIDtoterminal.

## Formal terminal: Pass15, no target gain, archive

Task **6ac7bfcb694b590c3c0ae962**, implementation **1a56211**, 368904B/SHAdcf715a2. Formalcompile/15precision passed, allprecision_ratio=1. Timesus:

`[1.91, 2.83, 3.14, 4.1, 5.22, 9.97, 8.07, 44.08, 67.5, 92.84, 88.37, 96.05, 13.18, 10.7, 9.37]`

Total **457.33us**, latestuserTbest calculatedmean **51.35378426**, notlive rank. C10 **92.84us** vsparentsingle91.53us (+1.43%) doesnotimprove thetarget. Noactualroute/SoC/profile/bounddevice A-B orGMwait frequency. Syntheticallowedoverlapdidnotestablish actualspeed. Allotherpoint fluctuations/adverseC6=9.97/C13=13.18/C15=9.37 retained; unrelatedroutes' improvements notattributed.

Archiveandrestorewholepassed **a2e6763** /368782B/SHA16b51684; noidenticalrepeat/nearbywait variants. CPUmodels/rawnativeJSON remainarchivedbranch/ignored artifacts/c10-late-ring-credit/official.json. Main/tagsuntouched, noactiveformaljobs. Independentnextaudit: actualFF A2loadinstruction/data-layout conversion, preserving currenttilegeometry/GM/Plan.

Wholekernelrestored **a2e6763**/368782B/SHA16b51684 onexperiment/c10-a2-load-audit; lateGMcredit source/models archived44d25e2, nativePass15/C1092.84notretained. IndependentdirectA2audit: actualRESIDENT_PAD selects3Dregardless tree2; existingstridedLoad2D NZ->ZZ couldbeactivated M_BALANCEonly withsamegeometry/volume, estimatedAcommands4x (risk). Addressalgebra documentedC10_DIRECT_A2_AUDIT; notimplemented/submitted, noactivejobs. Nextactualsourcephysicalmodelbeforeonegate.

## C10 direct A2 CPU candidate

Kernel368813B/SHA526d7f94b8aef59e82a91556fa311695cd9d90f39893662f638a58e2c9733d35, experiment/c10-direct-a2, parenta2e6763. OnlyguardedFF A2selection changes3D->existingdirectstrided2D; geometry/tree8/GM/Plan/Vector/creditsunchanged. FullactualA2D14400/A3D0/A2elements23592960/C200/MMAD3600/Breads58982400; parentderived3D3600APIcalls nothardwareinstruction/timecounts. CPU31producer/parent30proxies/positiveK-varyingreference/96ownership+FinalizeRows/prod&TUNING192plans9hits/sixcontrols PASS. FirstnegativeKoffsetfaultescapedconstantKdata, fixedreferencevalidatesandcatchesfault; rawfailed/final logskeptignoredartifacts/c10-direct-a2. Wholeinversea2e6763/protected7pass. Finaldryrunonly368813B/526d7f94kernel. NativePENDING/noID,ONEgateafterpush. C10_DIRECT_A2_AUDIT recordslimits/risk.

Implementation **3f58655** pushed; uniqueformaljob **6ac7c376694b590c3c0d4fab** createdonce. Same368813B/SHA526d7f94. NativePENDING, querysameIDtoterminal.

## Formal terminal: Pass15, no C10 gain, archive

Unique **6ac7c376694b590c3c0d4fab**, implementation **3f58655**,368813B/SHA526d7f94. Formalcompile and15/15precision passed, allprecision_ratio=1. Timesus:

`[2.04, 2.56, 3.25, 4.12, 5.2, 9.6, 8.08, 44.08, 68.39, 92.98, 88.59, 97.2, 13.15, 10.83, 9.19]`

Total **459.26us**, latestuserTbest calculatedmean **51.36499667**, notlive rank. C10 **92.98us** vsparentsingle91.53us (+1.58%) doesnotimprove target. Otheradverse C1=2.04/C3=3.25/C11=88.59/C12=97.20 etc retained, unrelatedroute improvements notattributed. Noactualroute/SoC/profile/bounddeviceA-B; APIcall/layout proofdidnotestablish latency benefit.

Archivewholechange, restorepassed **a2e6763**/368782B/SHA16b51684. No unchangedrepeat/neighboringLoad2D/3D ortiling scans. Failedmodels/source retainedarchivedbranch, rawignoredartifacts/c10-direct-a2/official.json. FullM178.32/latecredit92.84/directA2 92.98 now all excluded. Noactivejob, main/tagsuntouched, overallgoalincomplete.

NEXT independenttarget C1 singleK32 dot: literal one-output UBframe/three-GM-argumentkernel versusgeneric grouped8shortdot runtimeparameters. Itslayout ambiguityvanishes atM=N=1, dtype stillsameT. Audit scope/pins/alias/actualCast-Mul-Reduce/outputcompletion first; no nativecandidate existsyet.

Restoredwholea2e6763/368782B/SHA16b51684 onexperiment/c1-literal-dot-audit. DirectA2source/models/native15PassbutC1092.98 archived35480f2; nolivejobs. IndependentC1literalone-outputK32auditdocumentedC1_LITERAL_DOT_AUDIT, actualshortdotstillruntimegroup8. Fixed544Bframe/threeGMargswouldremovegeometryprologuebutnotbytes/FLOPs/launch; compiler/launchfloorbenefitunknown. NoC1implementation/submissionyet; actualtensor/DMA/alias/output/pinmodelsrequiredbeforeonegatedjob.

## C1 literal K32 CPU candidate

Branch experiment/c1-literal-dot,370984B/SHAb8ab2f9faa564a99d40fcbf93a6b4ee922c42d5cbf82c12ab679a3ff15e3d79c,parenta2e6763.47addedkernel lines: literal544B/threeGMarg/singleoutputkernel; exactB=M=N1/K32/dual15/grid1/alignedGM/actualUB-AIV/noPinsguard. OriginalPlan/GM/allotheralgorithms/shortdot unchangedbywholeinverseproof/protected7. CPU512literal-parentpairs/production&TUNING7776plans+launch24hits/fivefaultcontrols PASS. NativePENDING/noID, finaldryrunonly370984B/b8ab2f9f. SourceUBspanlessnottraffic/launch/FLOP/hardwareinstructionclaim. Nativeonegateafterpush; predeclaredconfirmationonlyall15Pass/C1<=1.6065us, otherwise no unchangedrepeat/nearbyscans. DetailsC1_LITERAL_DOT_AUDIT, rawignoredartifacts/c1-literal-dot/cpu.log.

Implementation **7925ee2** pushed; uniqueformaljob **6ac7ce8e694b590c3c14baa6** createdonce. Same370984B/SHAb8ab2f9f. NativePENDING, querysameIDtoterminal.

## Formal terminal: Pass15, C1 within old range, archive

Unique **6ac7ce8e694b590c3c14baa6**, implementation **7925ee2**,370984B/SHAb8ab2f9f. Formalcompile/15precision passed, allprecision_ratio=1. Timesus:

`[1.93, 2.48, 3.05, 4.05, 5.24, 9.89, 8.09, 45.83, 68.81, 93.21, 89.16, 96.88, 13.1, 10.93, 9.32]`

Total **461.97us**, latestuserTbest calculatedmean **51.56738723**, notlive rank. C1 **1.93us** lieswithinrecentold1.89-2.04; neither clearbenefit norpredeclared15%confirmationcriterion(<=1.6065) met. No unchangedconfirmation/neighboringK/batch/UBoffset/epiloguevariants. OtheradverseC8=45.83/C9=68.81/C10=93.21/C11=89.16 etc retained, tinyC2/C3 fluctuationsnotattributed tosourceunchangedroutes.

NoactualSoC/route/profile/bounddeviceA-B, no conclusionthatlaunchfloor orPIPE_ALL dominates. Source-declaredUBspan/ABI improvementdidnotestablish latencygain. Archiveandrestorewholepassed **a2e6763**/368782B/SHA16b51684, retainingC10balanced/C8phasedA/C13frame. Rawignoredartifacts/c1-literal-dot/official.json, noactivejobs/main/tagsuntouched, goalincomplete.

NEXT C8 actual-workweighted ownership audit: existing81M-majorCtiles include8Mtail/8Ntail pluscorner; twocores receivealmostonlyMtail whilemaxworkerhasfourfull128x128tiles. RespectfailedresidentB/fullinput/PK/BNexperiments; investigate splittingonlyboundaryCtiles at16-row granularity byactualvalidarea, retainingcurrentCdimensions/Bpackages/Aphase/GM andcountingextraBrefreshes. Notimplemented/submitted.

Wholekernelrestoreda2e6763/368782B/SHA16b51684 onexperiment/c8-workload-audit. C1literalnativePass15/C1=1.93no clearbenefit archived2e10a23, no confirmation/livejobs.

ExecutedpureC8partition arithmetic: sixarea/fourcache-awaretailcomparisons, exactvalidrowcoverage/unchangedpaddedwork. At20coresnaivearea max13C/90small-MMADbarriers rejectedbeforeimplementation. Full-cellM16boundarysplits+cache-awareNt-tail/distributedMt-tail projectsmaxarea65536->55552/maxC5->6/barriers45->18,globalC81->97/Binput9575928->11689464(+22.07%)/Ainput3172368->3178560(+0.195%). At32coresmax49152->35072/sameglobalC81/Bvolume. Counts aremathematicalprojections, NOTactualkernel/CANN/NPU tests. C8_WORKLOAD_PARTITION_AUDIT specifiespackedhosttailmetadata/sharedtask mapping/nonzeroLoad3Dchannel-start legality/nativePENDING/partialstore hazards. NoC8kernelcandidate/jobyet; actualprotocol/layout/hostmodel requirednext. Rawignoredartifacts/c8-workload-audit/partition.log.

## C8 balanced tail frame: actual source CPU candidate

Candidate372771B/SHAaa2aabc1ab1cea9270173966aa93748762e3ce0514383b81512be4fa1d784bec, parenta2e6763. NewactualM16heavy fragments/cache-awareNtail/distributedMtail withsharedCube/Bprefetch/AIVmapping, exactfragmentstores andoldA1/phase/GM/ring/merge. OriginalManualTransposeFullMunchanged; NZsubview row*kp passesaddressmodel. Two64bitownerlaunchargs add16BdefaultmetadataforoldTTinstances: ABI/nativegate riskretained. NoPlan/newGM/protected7changes.

CPUactualproduction&TUNING3024plans/4hits each; all8..32cores2393tasks versusindependentPython;8actualCubeproducerpositiveK-varying/allnegative/tails/liveoperand tests;42queuedAIVpriorities/unique partial/padding poison/MaxN-SumM/yguard;10faultcontrols rejected. Exact20coreA/B DMA96/291/MMAD873/sourceelements3178560/11689464 matchmath. AddedBtraffic22.07%/Ctasks19.75%retained;notlatency claim. NativeCANN9/BF16/precision/timingPENDING,noID. Dryonlykernelverified. ONEgateafterpush;confirmationonlyPass15andC8<=37.111us,otherwisearchive/restorewithoutneighbor scans. DetailsC8_BALANCED_TAIL_FRAME.

实现 **1cb15f9** 已推送；唯一正式任务 **6ac7d7af694b590c3c1a2cb8** 已创建。372771B/SHAaa2aabc1，native PENDING，只查询同一 ID。

## 正式终态：15 点通过，C8 明显回退，归档

唯一任务 **6ac7d7af694b590c3c1a2cb8**，实现 **1cb15f9** /372771B/SHAaa2aabc1。CANN编译和15点正式精度通过，所有 precision_ratio=1。耗时 μs：

`[2.0, 2.54, 3.12, 4.23, 5.22, 9.6, 7.99, 56.78, 67.5, 89.53, 87.66, 95.22, 12.99, 10.85, 9.24]`

总计 **464.47 μs**，按最新用户Tbest重算均分 **51.81580052**（非实时排名）。C8 **56.78 μs**，比父近期43.66–45.83明显慢；相对于父单次43.66增加30.05%。没有满足预先设定的37.111μs复测门槛。C10=89.53等未改算法分支的变化不归因于本实验；默认TT新增16B参数的影响也无法在缺少profile/受控同机A-B时分离。

不原样复测、不扫邻近分片或核数。保留全部反例，恢复完整a2e6763（368782B/SHA16b51684），不带入新helper/metadata/launch。数学负载下降并未证明硬件收益；无法仅凭此次测评确定回退由B搬运、scalar mapping、MMAD或同步哪部分导致。原始结果忽略 artifacts/c8-balanced-tail-frame/official.json。无活动任务，main/标签不动，整体冲榜目标未完成。
