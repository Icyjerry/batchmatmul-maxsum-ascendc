# Cube K/N 循环重组与 L1 常驻

分支 `experiment/cube-panel-reuse`；父提交 `48e37c7`；实现提交 `bc3f7cf`。
当前 kernel SHA256：`e440e1b3d915ba61f696059cd3af0efdee6b8d087aee04ef7a49ba40ef2a637b`。
**CANN9 编译、NPU 精度、正式15点与性能全部 PENDING。云端按用户要求暂缓。**

## 核心变化

新增 `RunPanelCube`，实际接入 `bmmms_manual` 的生产选择；不是仅保留在调参分支的示例。

旧手写循环：`N tile → 全部K块 → 输出C`。
新循环：`一组N tiles → K块 → 组内N tiles → 完整C输出`。

- 两块FP32结果同时保留在L0C。每个A的K面板在L0A只加载一次，供两个相邻N tile的MMAD读取。先完成全部K，再输出供Vector做Max，绝不对不完整K点积取Max。
- 分段模式：A1和B1各两级队列、L0A和L0B各两个缓冲；B按 `(K块,组内N tile)` 顺序提前两次搬运。A的释放事件排在组内最后一次MMAD之后，B各自释放。
- 常驻模式：若实际L1容量允许，在当前 `(batch,M tile,N shard)` 任务开始时，将整个A query面板转换到L1，跨全部N组复用；L0A仍逐K加载并在组内复用。K/M尾部按16补零；四种存储布局共用相同逻辑。
- AIV沿用既有双槽GM环形缓冲、两块UB预取和DMA完成后归还槽位；新生产者的归约接入父版本 `ReduceDualTile`。输出partial布局、最终Sum与batch配对不变，没有新增GM通路。
- `PanelKCapacity` 查询真实L1/L0A/L0B/L0C，选择16对齐的K块；查询缺失或容量不足时保留父路径。没有给新路径硬编码A2/A3内存容量。

## 四档对照

`BMMMS_CUBE_PANEL`：

| 值 | 行为 | 对照目的 |
|---|---|---|
| 0 | 保留父版本路径 | 整体替换的实际收益/退化 |
| 1 | 新生产者，单个N tile，分段A | 隔离更换库/手写内核的影响 |
| 2 | 新生产者，两个N tile，共享分段A | 与1比较，隔离组内A复用 |
| 3（默认候选） | 同2；放得下时A常驻L1 | 与2比较，隔离跨N组的GM读取复用 |

1/2使用相同准入、tile、K块、任务分配和缓冲预算，都分配两个C缓冲。3的L1分配按常驻状态改变，其它几何量保留。显式TUNING的family、tile、window、ns/ks、worker、tree设置会禁用自动替换，避免悄悄覆盖调参意图。

准入范围：原dual=1/2/3/14，完整K，M≥16、K≥128，每个N shard至少2个tile；baseM≤128、baseN≤256，两个C tile必须放得下L0C，合法K块至少64。这里的门槛是实验选择，不是实测最优分界。长K split、tiny、GEMV等保留父路径。

例如128×256的两个FP32 C需要256KiB；在128KiB L0C上不会启用。128×128或64×256可按实际容量检查。不能用“支持大shape”暗示所有shape都进入新路径。

## 可验证的流量变化及限制

设一个任务有q个N tile，A的有效元素数为`validM*K`：

- 模式1：读取A共q次。
- 模式2：读取A共ceil(q/2)次；完整成对tile的A GM读取和L0A搬入量减半。
- 模式3且常驻：该任务从GM读取A一次；L0A搬入次数仍与模式2相同。
- B有效读取量、MMAD次数、完整C输出数量不因这些模式变化。

**这些对比针对新内核的1/2/3模式，不能当作相对父版Matmul库的流量降幅。** 原库可能已有自己的L1复用。成对C占满L0C会减少原来单tile Fixpipe与后续计算重叠的机会；小任务的新事件/标量成本、resident全K加载延迟、库内优化优势，都可能导致退化。必须测0对默认3的真实端到端耗时。

## 一手资料

- [CATLASS优化指南](https://catlass.readthedocs.io/en/latest/1_Practice/11_matmul_optimization/)：核对L1/L0各自双缓冲容量、16对齐、预取策略和形状适用范围。本文使用其容量/流水设计原则，没有复制其代码或借用其加速比。
- [GetCoreMemSize官方API](https://www.hiascend.com/document/detail/en/canncommercial/850/API/ascendcopapi/atlasascendc_api_07_1034.html)：核对L0_A/L0_B/L0_C等枚举和容量查询；这是8.5文档，CANN9实际头文件仍需设备环境确认。
- [AdaptCore论文摘要](https://arxiv.org/abs/2608.10803)：将空间分块与指令组织分开、按硬件约束选择实现的思路，与这里保留任务几何量、独立比较生产者相符。这里只核对摘要，没有实现该论文的性能模型，不引用其速度作为本算子预测。

## 已完成的本地检查

1. `python3 tools/validate_cube_panel.py`：从当前kernel抽取Copy/Load/RunPanelCube实际函数，按物理16×16 NZ/ZZ/ZN块模拟ND2NZ、LoadData转置、MMAD及Fixpipe。444个生产者执行配置，覆盖四布局、三种新模式、M/N尾、K=40/136/248/264及8192、多task/worker/N分片、奇数最后N组、空worker。逐元素比较C及补零区、事件计数、队列退出、读取量；检查常驻A确实只读一次/任务。
2. 模型输入采用FP16/BF16都可精确表示的小整数，以2字节存储模拟布局；**没有模拟半精度编码、NPU舍入、真实异步事件或CANN编译**。不能称为两个dtype的设备精度PASS。
3. `python3 tools/validate_host_plan.py`：76,424个主网格配置，另做资源边界/缺失查询检查；四档×production/TUNING。模式1/2/3累计11,989次选择，模式3中9,963次常驻。tiler为宽松CPU替身，这些数字不是正式case覆盖率或可编译证明。
4. 父版dual消费模型六档检查、finalizer覆盖检查通过。消费模型范围现在只要求两条库dual kernel的非消费部分保持一致，不再误称整个host/其它kernel未改。
5. main.asc、CMakeLists.txt、run.sh未修改。模式0保留父策略；历史tag和main kernel未替换。

## 云端恢复后的直接执行单

固定本SHA、现有NSPLIT/SPLITK/消费宏，probe宏全0，分别构建P0/P1/P2/P3，对应上表。确认verbose编译命令宏生效。四档均先过正式15点，再做专项精度，不能只测模式3。

专项 `(B,M,N,K)`：`(1,1536,1536,1536)`、`(1,3072,1536,1536)`、`(1,65,8192,248)`、`(2,33,97,136)`、`(1,129,257,136)`、`(1,128,1024,2048)`、`(1,128,1024,4096)`、`(1,1024,5120,1024)`、`(1,513,511,2048)`。前后各形状用于常驻/非驻留、成对/余单tile、尾块、容量回退。以设备实际plan为准；部分shape故意不进入新路径。

每个case覆盖FP16/BF16×四布局，普通/全负数据与重复执行，实际存储值FP64 golden→FP32，正式容差不放宽。记录：SoC、CANN/驱动、核数、四种内存容量、宏、SHA，以及dual/baseM/baseN/nSplit/workers/panelK/panelGroup/panelResident、误差与一致性。

精度过后预热50次、设备计时200次，交替四档至少5组，报告median/p95；首次host分配单列。采AIC MTE2/MTE1/MAC/Fixpipe、AIV Vector/MTE2、Task Duration及等待指标；A2/A3分开。优先确认M_MTE1事件池还能分配4个ID、队列free依赖、resident重用、双L0C累加和跨核flag计数。CPU事件是同步计数模型，不能证明这些硬件行为。

若P1慢于P0、P2优于P1，说明复用有效但新基础路径仍有代价；不能因此声称P2优于原实现。P3相对P2只在resident=1的case评价驻留收益。结果写PERF_LOG，保留失败日志；设备证据足够前不合并main kernel。
