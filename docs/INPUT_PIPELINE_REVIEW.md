# 输入流水与结果交接源码审查 · 2026-09-30

## 当前证据

独立MDL shard候选 `df0e049` / [正式评测](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcbaf3694b590c3c353072) 15/15通过，但15点耗时合计517.73→527.49μs，无收益。详见 [MDL_SHARD_PIPELINE.md](MDL_SHARD_PIPELINE.md)。不要继续相近会话/MDL参数提交。

## 修正原先对 stepM/N 的怀疑

运行 `tools/inspect_public_matmul_tiling.py --source /path/to/ascendc-api-adv`，直接编译**未修改的**官方公开 `matmul_tiling.cpp` / `matmul_tiling_base.cpp` / `matmul_tiling_algorithm.cpp` / `math_util.cpp`。仅以shim提供外部platform/log/layout/securec支持头文件。固定源码revision `c7dfa2d901a314e1ae69e9cef850057593f2a58b` / `8.3.T9.0.B066`，来源 [官方仓库](https://gitee.com/ascend/ascendc-api-adv)。这不是CANN9 header、installed tiler、硬件仿真或性能测试。

示例平台L1=512KiB、L0A/B=64KiB、L0C=128KiB、UB=192KiB；查询TT BF16、orgM=1536/orgN=3072，固定baseM/N=128，UB留给库110KiB。config0/1 × singleM128/256 × singleN128/256/512/1024 × K1024/1536/2048/3072/4096，共80个查询均接受；**stepM/N全部为1**。源码默认MDL并不代表这80个查询一定生成不同于Norm的tiling；不能继续把强制step1称为已确认性能缺陷。

代表查询（不是正式case plan）：

| singleM | singleN | K | baseK | stepKa/Kb | depthA1/B1 | 判读 |
|---:|---:|---:|---:|---|---|---|
|128|256或512|1536|128|12/2|12/4|A完整K可缓存，B非全载|
|256|256或512|1536|128|2/6|4/12|扩大M后A不再完整K缓存|
|128或256|256或512|3072|128|2/6|4/12|A/B都非完整K缓存|

因此把M从128扩大到256可能失去A缓存；不可仅凭B读取次数下降选宽泛规则。源码 `scheduler_mdl_common.h::ReduceKMultiIter` 完成一个C基本块的整个K后调用 `ResetCopyInBuffer`，`scheduler_mdl_base.h` 对非全载A/B执行Reset。`stepM=1` 时扩大singleM也不会自动变成“同一个B K面板连续用于两个M基本块”的计算顺序。

80组CSV保存于本机Git忽略 `artifacts/mdl-shard-pipeline/public-tiler.csv`；可用工具独立重建。CPU驱动的PlatformInfo为示例值，不能代替CANNJudge的精确设备与实际plan。

## 排除直接 L0C→UB 假设

[CANN商用9.0逻辑位置映射](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/ascendcopapi/atlasascendc_api_07_0004.html)将A2/A3的CO2映射为GM。公开 `feature_trait/matmul_chip_cap.h` V220 的 `ifSupportL0CToUB=false`，仅C310为true；`copy_cube_out_utils.h` 只有该能力为true才选择UB Fixpipe配置。因此不能把C310的直接UB能力套用到本项目dav-2201/A2/A3，未经9.0实际header/设备证明不实现这条路径。当前GM ring继续保留。

## 下一条明确的结构假设

研究大K、A/B均非全载的TT路径，**两个M基本块共享B的每个K面板**：

1. 每个worker同时保留两个128×128 FP32 L0C累加器；同一B面板加载到L1/L0B一次，依次与两个不同的A面板MMAD，两个C都完成K以后输出。
2. 每个M对只有一个现有GM ring槽位，内含上下两个C；两名AIV各消费一个128行段。保留逐行Max(N)，最后Sum(M)；不得把K分片的最大值先归约。
3. 这不是单个256行MMAD；两个独立C让B在跨M的K循环内共享。也不同于此前失败的两个N tile共享A。
4. K循环应是 `for N tile → for K panel → load B once → for M in pair → load A/MMAD`；旧库是完成一个M/N C块的整个K后转到下一M/N块。
5. 手工资源预算：baseM=128/baseN=128/baseK=128，L0A/B各双缓冲64KiB，L0C两块128KiB；A1四队列128KiB、B1双队列64KiB。须查询真实容量并为其它存活缓冲留余量。M/N/K尾块沿用经模型检查的NZ补零逻辑，AIV只读有效行列。
6. 先限定K>=2048且原baseM/N=128的TT完整K路径；不能把K1536 A全载类一并替换。具体分支准入需要资源和真实逐任务调度模型，无“case编号=路径”的假设。

**状态：设计待实现，未提交此架构，未取得性能结果。** 下一条执行动作是从较快通过版实现配对M producer，复用bmmms_manual的AIV协议与finalizer；抽取真实producer检查物理NZ地址、B复用次数、FP32 C数学结果、双C的FIX_M生命周期、尾部单M，以及低核数/多波task覆盖。CPU只确认这些语义，性能仍由同设备实测决定。
