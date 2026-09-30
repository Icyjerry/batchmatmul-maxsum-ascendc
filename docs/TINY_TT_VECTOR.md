# 小 TT 整批单 AIV 计算

## Evidence / Diagnosis

较快通过版 `568f4eb` 的正式15点合计517.73 μs，第4点8.08 μs。历史探针第4族为BF16 TT、B4–7、M8–15、N16–31、K128–248；它是形状假设范围，不是公开正式shape。源码该族dual19已直接写y，没有全核finalizer，但仍经过ND2NZ、LoadData、MMAD、Fixpipe到既有GM槽、跨核flag与AIV DMA。

假设：该小算量族的交接成本高于FP32 Vector点积成本，整批在单AIV完成可明显降低固定开销。本机没有设备profile，假设尚未证明。已有micro_batch是K32/64按8批分组的另一个算法，不能据其历史退化判断本方案有效或无效。

## Implementation

分支 `experiment/tiny-tt-vector`，kernel SHA `4bef4346c0e746711b41ca936510b05b319ee18f09752b2414d767d1ab453b29`。

- 新 `bmmms_tiny_tt_vector`：一个AIV拥有完整batch，输入只读；X1物理[K,M]先Cast FP32再Gather当前query行，X2物理[N,K]一次带K尾padding的DMA和Cast。
- 点积产品在UB以[ceil(K/64),N,64]分组，先对所有K组作FP32逐lane累加，再WholeReduceSum64得到完整C行；此后WholeReduceMax(N)，最终WholeReduceSum(M)。没有跨K求Max。
- 只对有效K发Mul；最后K组未用lane始终为0。只对实际N求Max，支持全负值。Max结果按2*m定位以满足8字节对齐，奇数lane为0，最后Sum这些合法Max与0。
- 无Cube、输入GM预打包、相似度GM输出、跨核flag、SyncAll或新GM通路；MTE3通过DataCopyPad精确写一个FP32。
- Host仅从现有dual19、TT、M<=16、N<=32、K128–256且K%8==0计划转dual28，按实际平台查询UB并留4KiB；显式TUNING pins回退。没有扩大已验证的原形状分类。每次launch按实际workers唯一分配batch，保留原workspace容量/前缀以避免shape缓存生命周期变化。

## Research/API evidence

- [FlashAttention-2](https://arxiv.org/abs/2307.08691)关于减少非矩阵乘工作与通信的思路只是动机，论文未给出本Ascend算法，也不证明Vector比Cube快。
- CANN9 [WholeReduceSum](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0081.html)：A2/A3支持float，单repeat最多64，源32字节对齐，内部树形加法。
- CANN9 [WholeReduceMax](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0079.html)：A2/A3支持ORDER_ONLY_VALUE，float目标需8字节对齐。API名称/签名也沿用此前正式通过源码，但此新kernel需正式CANN编译。

## CPU/static validation

`python3 tools/validate_tiny_tt_vector.py`：

- 抽取整个新kernel，同步执行带Local/GM边界、对齐、DMA pad/stride和queue生命周期检查的CPU模型；700组组合含M1/8/11/15/16、N1/16/23/31/32、K128/136/184/192/200/248/256、混合/全负、单/多worker与重复batch。逐batchy与独立整数点积oracle相等，输入不变，输出两侧guard不变。
- 抽取实际host，production和TUNING各432个代表组合，其中360选新路径；低UB、其它布局/dtype、超范围和pins回退。
- 30组输入实际FP16/BF16量化值，在独立Python模拟FP32 K分组和树形归约；对FP64 oracle→FP32最大绝对误差9.54e-7，非零golden最大相对误差2.37e-7。含归一化随机、全负和正负抵消；不是所有合法数据的精度证明。
- `git diff --check`通过。CPU模型不模拟真实Ascend异步、Gather延迟、输入精度Cast指令或性能。CANN编译、正式15点、NPU性能PENDING。

## Validation request

下载正式模板，仅替换kernel.asc，dry-run后CLI提交并查询同一任务至terminal。对照通过版第4点和全部15点精度/时长；若未显著提速保留实验分支并恢复通过版，不连续提交相近参数变体。必须记录SHA与任务ID，不能按case编号断言命中，SoC/shape/plan/profile与重复A/B仍未取得。整体大幅提升目标未达成。

## 2026-09-30 · 单 AIV 小 TT 首版正式结果

代码 `a3c65a4`，kernel SHA `4bef4346c0e746711b41ca936510b05b319ee18f09752b2414d767d1ab453b29`，[正式提交 6abd2f7e694b590c3c75d2b6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd2f7e694b590c3c75d2b6) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.14, 4, 4.32, 6.01, 5.77, 10.62, 10.26, 69.43, 84.84, 98.39, 88.22, 96.78, 15.83, 13.32, 9.1]` μs，合计519.03 μs，对照保留版517.73 μs。第4点8.08→6.01 μs（1.34×），有局部收益，整体仍无明显提升。未取得实际shape/plan/profile及重复A/B，不声称路由命中或稳定加速。其它点的单次变化不能归因于本算法。首版CPU700个实际kernel执行、production/TUNING各432个host尝试和30个量化数值对照通过。

保留该独立分支，不并入main。下一假设：首版每M行单独Gather与归约屏障，改为一次A UB整理、两M行批量点积和归约；这项查询块重排尚未实现/验证，不是再调同一路径tile参数。整体大幅提升未达成。原始JSON本机Git忽略 `artifacts/tiny-tt-vector/`。
