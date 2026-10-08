# C10：按真实 M 行数均衡核负载

## 证据与假设

上轮 FF B 分包任务6ac7aefd694b590c3cfe44d9 Pass15但C10=97.06在旧96.98–100.24范围内，已归档/全部恢复。公开 CANNJudge CLI 的 get_problem 当前只给15个 testcase_id，get_submission 的通过结果没有 shape/layout/日志；没有请求未公开的测试点端点或下载隐藏输入。历史属性探针(169.77−110.17)/15=3.9733较支持BF16/FF，旧pathJSON记FP16/TT，构建归属不足以消除冲突。本实验明确条件化，不宣称正式命中。

新假设：原 M128 whole-tile strided ownership 在 M4096/20核时，12核负责256行、8核负责128行。按16行Cube单元先划分实际M区间，再在各区间内做原M128微块，可使最重核负责208行（−18.75%）。每个M行仍由一个核在完整N范围内取最大，再经原FinalizeRows做SumM；不切N、不拆K、不合并跨batch。

## 实现

父af886e1，分支experiment/c10-balanced-m-shards，kernel368782B/SHA256 `16b51684cc8628121d7e359c89561c248d04b449b6ecb449f0b4f2da2ffa3a94`，60additions/11removed。仅kernel算法。

新增默认false的M_BALANCE参数与共享M区间helper，原Cube/Vector使用同一范围。最末微块截到核区间终点。Vector只写有效rows个maxima，防止末块的补齐行覆盖下一核有效行；16行对齐使DataCopy仍满足32字节要求。现有Max树、Sum、跨核GMcredits、A1/L0双缓冲、单C、Plan、system工作区/partials/rings均保留，无新GM通路/分配。

选择已有安全BF16/FF dual20/BM128/BN256/BK64/tree8/window1/ns1/ks1/b1、对齐shape，M4096..8192/N1024..2047/K1024..2047，且真实最重核行数模型改善≥10%。实际workers来自原Plan，不假定20核；所有显式调参pin回退。原部分prefix和每worker262144B ring的总arena预算检查，原资源计划不增容量。

### 成本边界

完整4096/1280/1152、20核的抽取真实Cube执行：maxRows208，Ctiles200、MMAD3600、Bcopies3600、Breads58982400元素；原分别256、160、2880、2880、47185920。**C块/B总搬运增加25%**，原总数学点积量保持（4096x1280x1152），不是25%更多数学运算。关键核K64 MMAD调用次数仍180，只有MMAD M尺寸和A搬运量减小。全局带宽/固定开销可能使方案更慢，不能由18.75%行数减少推算真实加速。

## 本地验证

`python3 tools/validate_c10_balanced_m_shards.py`：

- 13组真实manual FF Cube源码执行：完整目标形状、1/3/8/20/24/32核代理与默认不均衡路径，活跃MTE2/MTE1/MMAD操作数，每个完整K的C/Max/Sum、输入不变、环形/事件、每行唯一所有者。
- 96组抽取真实Vector ownership/store与真实FinalizeRows：4096/4112/6144/8176/8192及小代理，零有效行、核区间尾部、负数、未写padding正大值污染，逐行唯一writer、最终精确y和边界。此模型提供合成已完成的行maxima隔离地址问题；没有重新执行未改Vector max树或模拟真实Cube/AIV并发。
- 生产/TUNING分别192实际host控制配置/9命中，dtype/四布局/各核数，GM一字节边界、所有相关pins。fake tiler，不是实际CANN9库plan。
- 六故障控制：去掉Cube区间尾约束/L0ready/Cready、Vector补齐行存储/错误M起点/错误区间尾，全部拒绝。
- Vector除ownership与写有效行外整个body逐字节等于父版本；去掉新增helper/selector/launch并恢复manual后全kernel等于af886e1，受保护七文件等于1734f16。

CANN9编译/硬件TQue契约/BF16指令精度/正式15点/latency/真实route/profile：**PENDING**。无Web。只创建一个正式gate；失败或无明确收益则整份恢复af886e1并保留反例，不扫附近分区粒度。

Implementationa2e6763 pushed; one unique native **6ac7b3c8694b590c3c0218c4**, sameSHA16b51684/368782B, createdonce. NativePENDING; querysameID toterminal, no resubmit.

## Native terminal: Pass15, single local improvement

Task **6ac7b3c8694b590c3c0218c4**, implementation a2e6763 / SHA16b51684 / 368782B. Formal compile and 15/15 precision passed, all precision_ratio=1. Times us:

`[1.9, 2.87, 3.1, 4.13, 5.37, 9.66, 8.02, 43.66, 68.75, 91.53, 88.38, 96.57, 13.02, 10.86, 9.22]`

Total **457.04us**, newest user Tbest calculated mean **51.45446223**, not a live rank. C10=91.53, 5.62% below the prior unchanged-C10 range minimum96.98 (range96.98-100.24), and8.06% below the most recent parent99.56. Consistent with the ownership hypothesis but only a single observation: no bound-device A/B, route hit or profiling. Not stable causal proof or a large whole-competition breakthrough. Adverse C2=2.87 retained; its independent tiny route was unchanged. Extra C8=43.66 fluctuation is not attributed to this C10 edit.

Keep this passed candidate as the experimental forward baseline; main/historical tags unchanged. User requires large gains before repeats, so no unchanged confirmation or neighboring ownership scans. Native15 precision passed, full A2/A3 coverage/SoC/all envelope/stable performance still unproven. No live tasks. Raw JSON ignored artifacts/c10-balanced-m-shards/official.json. Passed parentaf886e1 remains recoverable.
