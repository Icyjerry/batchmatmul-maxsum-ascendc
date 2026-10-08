# C9 分片内持久 Max — CPU candidate

## 实现与可验证假设

父版a2e6763，分支experiment/c9-stream-max，kernel371179B/SHA256 `8c23062f0f03f17cbd92f9813092f2f6d40fb876f4e77fdf68acac0f2f411aa8`。46新增/2删（含actual core guard）。初始归约恒等式来自experiment-v1，此处是首次在队友C9 packages真实AIV消费路径接入；不是拿历史广泛dual实验作native证据。

假设：延后横向ReduceMax，去掉N分片内重复的horizontal tree与row-max合并，有机会缩短Vector路径。新增16KiB持久lane状态及其读写成本可能抵消收益。C9 Cube主体逐字不变；没有更改K累加、A/B package、输入DMA、Cube/GM credit顺序、ring、分工、partial、最终MaxN/SumM、workspace或Plan。

- `STREAM_MAX=false`是原算法；true只在既有exact C9入口的Shape/Plan/package/capacity/no-pin检查后启动。
- guard：B1/M2048/N1536/K1280，FP16/FT，dual20，BM128/BN128/BK128，原package safe/resident且bK>BK，earlySum关闭。核心数查询平台，不固定20；预算为原保守Vector/finalizer bytes +16384+4096。
- 每任务lane64/row初始化-inf，仅实际N列做masked Max；每个C已经完成完整K。所有Nt结束才WholeReduceMax到原maxima；原Nsplit partial及全核归约保持顺序。
- 零行AIV保持原credit/barrier，padding行由原maxima初始化-inf；live c释放次序及原TQue outputstore生命周期保留。其它C9模板默认关闭算法，但多一个未InitBuffer的laneBuf声明，不能声称编译后指令完全一样。
- 三处逆向替换还原完整父文件；7个受保护文件字节一致，Cube body字节一致。

## 本地验证

`python3 tools/validate_c9_stream_max.py`：

- production/TUNING各2592actual host plan，6个exact命中（1/3/8/20/24/32核）；shape/layout/dtype、UB一字节阈值、硬件核心数、L1/L0、arena、11个Tune pin fallback；原Plan/GM不变。
- 1452真实AIV+父消费路径及真实FinalizeRows组。BM32/128、M1/17/129、N73/257/513、多Nsplit/window1/2、3/8核心、全负/混合、3种FIFO引擎优先级；精确C9 M2048/N1536在8/20/32核且正负均运行新旧消费路径。
- per-window合成complete-K Cube，两个GM槽写后可立即破坏性复用；TQue私有UB delayed DMA与generation检查，MTE3 partial延迟读取/复用；所有worker含idle/zero-row参加barrier；每行partial唯一writer、尾列positive poison、最终MaxN后有效M sum及y/arena guard。
- 精确C9实际消费代码计数：旧WholeReduceMax768，新在8/20/32核分别32/96/384。20核96不是数学预测，确实执行了真实AIV源码；仍不代表硬件指令数或耗时。
- 九个故障对照：lane初始化0、N mask越界、C pitch错误、漏最终fold、漏任务reset、漏C ready queue、漏ring release、漏全核barrier、提前Free c，全部拒绝。

### 初次故障对照未检出，已加强模型

第一次N mask对照没有失败：复用buffer的未写尾列恰好来自该N分片以前的合法C，错误读取没有改变max。该次log完整保留。重新Alloc每代UB填positive poison，并使行幅值随M变化、故障fixture包括两个任务及正负输入，以检查任意允许padding内容和跨任务泄漏。重新跑1452组和所有9个对照通过。没有修改kernel来躲避该对照。

局限：fake tiler非CANN9；synthetic Cube没有执行FP16或MMAD，此处只验证消费代码和partial/finalizer，Cube未变由source字节证明；FIFO没有Vector指令内部hazard模型，barrier仍完整保留。非native精度/时间/profile证据。

## 正式 gate

隔离 `/private/tmp/bmmms-c9-stream-max/project`，protected7来自1734f16；dry-run仅371179B/上述SHA kernel。commit/push后ONE正式提交，立即记录ID、同ID查至终态。CANN9编译、15点精度、timing PENDING，目前无ID。

只在Pass15且C9<=57.375μs（近期未改最低67.50的85%）时原样复测确认，否则不原样复测、不扫邻近lane/PK/tile；若无明确收益恢复完整a2e6763。真实dtype/layout/SoC/route/profile没由API提供，不能由耗时推断。整体冲榜目标未完成。

Raw忽略artifacts/c9-stream-max/cpu.log、cpu-initial-fault-miss.log，目录700/文件600。

实现 **ec40e0e** 已推送；唯一正式任务 **6ac7e2f8694b590c3c2010c5** 已创建一次。371179B/SHA8c23062f，native PENDING；只查询同ID。

## 正式终态：Pass15，C9没有明确收益，归档恢复

唯一 **6ac7e2f8694b590c3c2010c5**，实现 **ec40e0e**，371179B/SHA8c23062f。正式编译/15精度通过/all precision_ratio1，times μs：

`[1.9, 2.44, 3.22, 4.02, 5.22, 9.62, 7.94, 44.46, 67.62, 93.52, 87.61, 96.47, 13.01, 10.67, 8.89]`

总计 **456.61μs**，最新用户Tbest重算均分 **52.50620586**（非实时排名）。C9 **67.62μs** 落在保留路径近期 **67.50–69.04μs**范围内；没有明确收益，未满足57.375μs复测门槛。其余变动含C10=93.52完整保留，不归因于此次Vector改动。

源码CPU横向调用768->96并未建立实际速度改善；native API编译/精度通过不能证明该hidden case实际命中新guard。没有SoC/route/profile/同机A-B，不能断言Vector成本低或由哪个单元主导。无原样复测或邻近lane/package/tile扫描。下一步完整恢复a2e6763/368782B/SHA16b51684，将实现/CPU/原始反例留在本分支；main/标签不动，整体目标未完成。Raw忽略artifacts/c9-stream-max/official.json。
