# 两个 M 块共享 B K 面板 · 2026-09-30

## Evidence → Diagnosis

父分支 `experiment/manual-splitk-tiny` / kernel SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5` 是当前最快正式通过起点。独立 Norm/MDL 会话、GM NZ 输出均已测无整体收益；不叠加它们。公开源码审查见 [INPUT_PIPELINE_REVIEW.md](INPUT_PIPELINE_REVIEW.md)：大K MDL按一个C块完成整个K，然后清理非全载A/B cache，扩大单核M不会自动使两个M块共享每个K面板。公开tiler是8.3源码，不是CANN9安装header。

假设：两个M基本块同时保留FP32 L0C，在K循环内共用B的GM→L1与L1→L0B搬运，减少B重复搬运；同一B L0B缓冲只在两个MMAD都使用后释放。不预测实际提速幅度。

## 实现

分支 `experiment/paired-m-breuse`，候选 kernel SHA `e3b770b876e90cc2c6796626858467099824a7c1341b4ba40a44d6e9a83cfebb`。

- 新 `RunPairedMCube`，每个任务处理最多两块128行M；K面板128，先LoadB一次，再依次Load两个A并分别MMAD。两个C独立累加完整K，保持数学与累加K次序。
- TT专用 `PairedMCopyA/B` 直接使用原输入物理stride与现有 `ManualZeroNZTail`；支持M/N尾块和K为8但非16倍数。
- 两个C完成后写同一个现有双槽ND ring，上/下各128行；沿用 `bmmms_manual` 的AIV DMA、Max、partial与finalizer。没有新输入GM预打包通路。
- 两组A/B L0释放事件和独立C的FIX_M信用；B仅在两个MMAD之后释放，ring仅在两个Fixpipe之后发布。尾部单M不执行第二MMAD/Fixpipe，仍回收未用C信用。无有效行AIV仍参与原协议。
- Host新dual=28只替换B1、TT、M/N>=1024、K>=2048、原dual1完整K且baseM/N=128路径；pairedM=256、nSplit保留、window=1，任务/worker重新按成对M计算。显式TUNING pins排除。
- 查询真实L1/L0A/L0B/L0C/UB；A1/B1各双队列64KiB，L0A/B各双缓冲64KiB，双L0C128KiB。保留UB finalizer余量，容量不够回退旧路径。原workspace前缀保留，避免当前队友缓存在shape切换后让manual覆写库前缀。

## CPU / static

`python3 tools/validate_paired_m.py`：

- 抽取实际新producer与补零helper：168个物理NZ/ZZ/ZN模型执行通过，逐元素C（含补零）与独立整数oracle一致；检查ND ring位置、完整K后Max/Sum、全负值、尾部单M、多batch、低核多波、K40/136/264/8192、双C事件收支、B copy/load次数。
- 完整M对的B搬运与LoadData次数恰为独立MMAD次数的一半，A读取量不变；这是本CPU模型的操作计数，不是相对库真实流量或设备加速比。
- 抽取实际host：360个代表shape/核数组合尝试，其中22个进入新路径；production/TUNING各自检查相同网格。workspace、任务、资源回退、布局/K/batch排除及显式pins通过。fake tiler不是CANN资源可行性证据。
- Producer模型用int16小整数模拟16位输入、同步执行Ascend指令数学语义；不模拟FP16/BF16舍入、真实异步依赖、cache行为或双AIV同时读取协议。
- 既有AIV消费逻辑直接复用，新的每块输出地址已通过producer模型；真实跨核同步、CANN编译和NPU精度仍需正式评测。

## Validation Request

原正式模板仅替换kernel.asc，CLI dry-run然后提交；记录逐点结果并对照当前最快通过版。必须CANN9编译与15/15精度全过。精确SoC、隐藏shape、实际plan、msprof和重复测量尚未取得，不按case编号断言命中新路由。整体显著改善才保留为新起点；无收益则恢复父版，保留本分支和失败证据，不继续相近参数提交。

CANN9编译 / 正式15点 / 性能：PENDING。

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

## 2026-09-30 · 配对 M 共享 B 覆盖版正式结果

代码 `d4b9044`，kernel SHA `c6cca6ba9a120336ab4548b7f6898dd6b793291cc0b6adea0ff20d5ad86a00b3`，[正式提交 6abcc39a694b590c3c3ada93](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcc39a694b590c3c3ada93) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

逐点耗时 `[2.27,3.90,4.07,7.82,5.30,10.60,10.05,69.57,84.77,99.51,88.07,96.27,15.87,13.10,9.53]` μs，合计 **520.70 μs**，对照保留版517.73 μs。第8点67.80→69.57、第11点88.16→88.07，没有整体收益；未取得实际shape/plan/profile及重复A/B，不能证明路由命中或具体退化原因。CPU172 producer和production/TUNING各360代表host组合（120选择）通过，与正式精度证据分开。

本分支保留代码、模型与失败对照，不继续同一结构相近参数提交。后续恢复 `experiment/manual-splitk-tiny` 的通过kernel，SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`；审查小矩阵的启动、同步与归约分工开销。整体大幅提升仍未达成。原始JSON在本机Git忽略 `artifacts/paired-m-breuse/`。
