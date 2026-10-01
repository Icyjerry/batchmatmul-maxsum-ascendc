# 保留 packed-B，将 Cube 块布局转换移至一次预处理

## Evidence → Diagnosis

四storage direct-B候选 `d0904f8` 正式15/15通过，但第12点TT父95.41→116.40μs，没有收益。原packed K面板的连续性应保留，见 `FULLM_STORAGE_LAYOUTS.md`。
旧packed路径仍以ND的K×baseN写GM；每个M任务的每K面板重复ND→NZ，然后每K16块发起一次B1→B2转置Load2D。一次pack只改变连续性，未消除这个按M重复的格式转换。
本次将B整理成 `[K/16,baseN,16]`，保留连续面板，再由Cube直接搬入B1、bulk非转置Load2D到B2的ZN。
这是预处理/计算之间的数据格式变化，不是再次给已失败pack阶段加double buffer，也不删除全局屏障。

## 实现与容量

- `ManualPackBToNZ` 使用16位原始数据转置，输入位于已分配C队列前半，输出放在同一buffer后半。该队列原本按float C分配，预处理输入为2字节，空间正好可容纳两份。没有新UB或GM分配。
- 输出依旧写原packed offset，每N tile占K×baseN×2字节；布局内部改为K16 plane，没有增加region、input或output。
- Cube BQ使用线性GM→B1复制；完整N块一次bulk Load2D，无transpose。N尾块保留按K16 plane搬运，正确跳过padding。
- 仅新模板NZ_B=true接入dual31；原dual6模板默认为false。A1/A2、MMAD、C缓冲、Fixpipe、归约、finalizer、pack的SyncAll及flag12逐字保持原样。
- MakePlan最后只dual6→31，已完成父计划的schedule其它字段、grid和workspace保持一致。仅TX1=true/TX2=false、K/N为16倍数、原packed家族、无earlySum、window1、BM64/128、BN≤256且为16倍数。显式pins保留。
- 每个完整B K面板，旧路径的K/16个转置Load2D变为1个非转置Load2D；ND2NZ的按M重复次数变为0。新增一次AIV预处理转换，按K16 plane执行，未重复到各M任务。调用数不是硬件提速预测。

## API依据

[官方CANN9 TransDataTo5HD](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0200.html) 支持A2/A3的uint16_t与half原始16位块转置及repeat strides。
使用uint16_t类型操作地址列表，FP16/BF16输入没有数值Cast。repeat=baseN/16，dst stride16 blocks、src stride1 block；repeat1必须将两者设0，已按文档处理。
固定公开8.3 `impl/quantization/antiquant/ascend_antiquant_m200_impl.h` 也采用GetPhyAddr地址列表并处理repeat1的stride0；是公开源码参考，不是安装CANN9编译结果。

## 论文中的复用原则与本题映射

Goto / van de Geijn 的 [High-Performance Implementation of the Level-3 BLAS](https://www.cs.utexas.edu/~flame/pubs/GotoTOMS2.pdf) 在Gepp算法中将B面板packing放在M循环外，供多个A块重复消费。它提供的是CPU分层矩阵乘的成本摊销思路，不提供Ascend指令或本题速度结论。
本题原实现已将B的连续化放在M循环外；本候选进一步将Cube的块布局也提前准备，避免同一面板在各M任务反复转换。为此付出额外一次Vector转置，是否划算由正式对照判断。
示例B1/M1536/N6144/K1536、BM128/BN256/BK64：Cube有6912次B面板消费，旧B2转置load发起27648次，新完整N面板6912次；AIV新增2304次K16-plane转换。示例不是正式case shape/plan，调用数也不是延迟预测。

## CPU/host验证

`python3 tools/validate_packed_b_nz.py`

- 原ND及新NZ各2016个**实际预处理、Cube B复制和B2 LoadData源码**执行。MTE2及MTE3延迟完成，检查queue所有权、source晚释放、输入不变、GM/UB界限、唯一writer与padding。
- 新模式实际搬运全部65536种16位模式；GM格式和B2 ZN每个元素对照原始逻辑B，含N16尾块、K16但非64/128倍数、不同packRows/BK、多个batch/worker、早/晚DMA完成。
- 生产/TUNING各1728 host配置、各54选择；其它字段/workspace/blocks和pins对照通过。
- 按新增input格式分支回退后，隔离packed kernel body与 `a05035e` 逐字一致；通用manual/full-M Cube/Vector体未改。
- 首次host夹具以同一auto声明两个不同namespace的Plan类型而编译失败；已拆成独立声明，统一脚本重跑通过，不修改算法来通过测试。
- `python3 tools/validate_packed_b_nz_public_tiler.py --source /private/tmp/ascendc-api-adv-review`：固定真实公开8.3 tiler arithmetic，production/TUNING各1728/54通过。

CPU TransDataTo5HD为文档中的16位转置语义模型，非完整异步矩阵仿真。B2逐bit相等加上未改A/C/归约，只是源码证据，正式精度仍需硬件验证。

## 正式状态

kernel SHA `5a420968d478d3428334a42e562bbe3455d413f6db06a60a432c100282ef494a`，272471 bytes。
独立官方模板 `/private/tmp/bmmms-judge-packed-b-nz/project`，dry-run仅kernel.asc/SHA一致。
代码 `0ad246b` 已推送私有GitHub分支。正式任务 [6abe0163694b590c3cc61e91](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe0163694b590c3cc61e91) 已创建；CANN9编译、NPU精度、latency：PENDING。
仅提交本次格式结构一次；同一ID查至终态，不用CPU调用数宣称速度。没有大幅收益则保留反例，不提交类似tile/stride参数。

## 正式终态：15/15通过，未见大幅收益

[6abe0163694b590c3cc61e91](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe0163694b590c3cc61e91) **Pass，CANN编译成功、15/15，precision_ratio全1**。
逐点耗时 `[2.18,3.78,4.39,5.62,5.38,10.78,10.17,67.93,83.85,99.64,88.43,96.65,16.28,13.33,9.51]` μs。
第12点TT父95.41→96.65，query-block95.91→96.65，没有明显收益。其它未修改路径不归因；无actual shape/plan/SoC/profile和重复A/B，不证明新路径命中或具体瓶颈。
保留 `0ad246b` 的已通过格式结构和源码模型，原始结果私有本机Git忽略 `artifacts/packed-b-nz-once/`。没有活动正式任务；不做类似packing stride/tile试交。
剩余源码成本：TF A的resident K面板仍按M16循环Load2D；M128时每K面板8次。可在保留本次连续NZ B的基础上，组合已通过TT的整M raw-bit Load3D A，减少两侧的逐小块搬运发起。这是新的组合假设，不是已证明提速。整体重大提升未达成。
