# 大 TT 非对齐 A 常驻 L1

## 假设与实现

从 `experiment/manual-splitk-tiny` / `d2718c8` 派生。本机当前没有 CANN/NPU；使用正式 CLI 验证候选。

BF16、B=1、TT、M/N≥1024、1024≤K≤2048，且 M/N/K 至少一维非 16 对齐：在原完整 K dual=1/2 路径上尝试手写 producer。每个 M tile / N shard 将完整 A 读入 L1 一次，跨 N tile 使用；B 的 K 面板和 L0A/B 保留双缓冲。没有新增 GM 通路，沿用现有双槽 ND ring、AIV 行 Max 和最终 Sum。

新的 `ManualLoadResidentTT` 按 padded K 而非实际 K 定位 L1 的 NZ slab，逐 16×16 块转成 L0A ZZ。ND2NZ 清 D 尾块，`ManualZeroNZTail` 清 K 尾行，MMAD 使用完整 K 的 FP32 累加，消费者只归约实际 M/N。

host 查询实际 L1、L0A/B/C、UB 和 AIC/AIV 数量；优先 M tile=128，容量不足试 64，N/K panel=128。N shard 数按 M tile 数和可用核数决定，每个 shard 至少两个 N tile。计入 resident A、B 双队列、A placeholder、双 L0A/B/C、消费者和 finalizer 的存活资源；不满足条件保留原路径。显式 tiling pins 禁止该覆盖。

这是新 producer 的源码读取次数承诺。原 Matmul 库的真实 L1 复用情况未知，不能把它当成相对原库已确认的带宽降幅或耗时收益。已有对齐 TT 手写实验没有收益，本实验不覆盖那些对齐形状。

## 本地证据

`python3 tools/validate_ragged_tt_resident.py`：

- production/TUNING 各 465 个选中计划配置：真实 host 控制流、逐 (M,N tile) 唯一覆盖、实际核数和 workspace 大小；检查 dtype/layout/B/K 排除、低资源回退和显式 pins。
- 125 组 NZ→ZZ/ZN 物理块模型，抽取实际 A copy、zero-tail、resident loader、B copy；验证零填充、重复复用、有效元素、合法块地址。小形状执行物理 dot→Max→Sum 与独立 oracle 比较，含全负相似度。
- 模型里的 A `DataCopy` 每次任务恰好一次，读取 `validRows*K` 个元素。CPU 模型同步执行，不验证硬件事件流水。
- `validate_manual_splitk.py` 48 组和 `validate_direct_batch.py` 1,458 个既有回归通过。

**CANN 编译、正式精度、性能 PENDING**。尤其需要检查 TT 非对齐 producer 是否被实际 case 命中；没有实际 shape/plan/profile 时不能推断具体耗时原因。

## 设备验证与交接

正式模板只替换 `kernel.asc`，dry-run 后提交一次结构候选。记录提交 ID、SHA、逐点精度和时间；运行失败或无显著收益则保留独立分支，恢复通过版，不把参数微调继续当新结构候选提交。

外部 harness 可验证 `(1,1025,1537,1032)`、`(1,1537,1537,1536)`、`(1,1025,1537,2040)`、`(1,1024,1025,2048)`，BF16 TT，正负/全负/重复执行。记录实际 dual=26、bm=128/64、ns、workers 与精确 SoC/CANN。性能与父版同设备交替运行，采 median/p95 和 MTE/Cube profile；A2/A3 分别保存结论。
