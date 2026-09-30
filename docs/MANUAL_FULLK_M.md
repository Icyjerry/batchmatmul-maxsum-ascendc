# 手写两半 M 的完整 K 驻留与预取

## 本次结构假设

以query-block通过kernel `55225cc` 为父版。新producer保持原任务分配、schedule.baseM/N/window/nSplit/workers、workspace prefix/partial/双slot GM ring。
同一M任务拆成两半，每半的完整K保存于A1队列的一个buffer，贯穿整个N分片。
先发起A0完整读取并DeQue；先发起B的前两个K面板，再发起A1完整读取。
第一半M可在A1 DMA尚未完成时开始MMAD；A1只在其首次产品前DeQue一次，随后重复使用，无库内每外K重复Await。
每个B K面板在L0B由两半M共同消费，两个M产品全部发出后才发布B的M_MTE1空闲事件。

**减少的是A跨N窗口的重复读取**。模型中A读取元素数为 `B*M*K*nSplit`，不随每分片N tile数增长。
父库是否在实际计划内部缓存、实际GM/L2流量和性能要由设备测量，不将源码公式冒充msprof数据。
B读取次数相对原完整M的库路径没有理论减少；B共享避免拆M引入重复读取。
相较归档paired-M，此方案保持原128/64行任务与窗口，不增大任务M，不改变并行网格，并且A在整个N分片驻留。
相较归档ragged-resident-A，增加首次下一半M预取、两半M共用B、四个C累加缓冲及保留原1/2 tile GM窗口发布协议。
这不是已证实的大幅提升；更小MMAD可能增加Scalar/L0C开销，真实速度可能退化。

## 接入与资源

仅原dual1、B1/TT、M/N/K≥1024、旧baseM64/128、window≤2且window宽≤256、无earlySum；FP16/BF16均使用相同模板。
显式调参pins保留，资源不足保留原路径。dual29通过既有manual核的M_FULLK模板参数进入新producer。
AIV代码体与父manual逐字一致，只采用既有span=1/2布局的实际schedule.window；Max只包含有效M/N，完成K以后才发布C。

- A1：两个 `(oldBaseM/2)*round16(K)*2` 字节buffer。
- B1：两个 `baseN*baseK*2`；baseN256时baseK64，其余128。
- L0A/L0B各双buffer；L0C为四个半M×baseN FP32块，N ping/pong且每个有两个M累加器。
- M_MTE1四个用户事件；从TPipe申请/释放，保留0..2既有预留。MTE1_M两个、FIX_M四个。全部最终credit回收。
- host按实际L1/L0A/L0B/L0C/UB查询，含4096余量及finalizer reserve。没有额外GM区域或input预处理。
- ring到AIV完整window才发布；两次Fixpipe可能分别写不同M半块及N半块，dstStride保持原window宽。

示例schedule M128/N128/window2/K1536：A1共384KiB+B1共64KiB，L0A32KiB、L0B64KiB、L0C128KiB。
示例不是正式隐藏shape、SoC或实际plan。

## CPU/静态验证

`python3 tools/validate_manual_fullk_m.py`

- 158个抽取真实ManualFullMReadA/RunManualFullMCube/ManualCopyK/ManualZeroNZTail执行。
- 物理NZ→ZZ/ZN加载、完整FP32整数模拟MMAD、每个C元素及M/N/K补零与独立逻辑点积相符。
- MTE2 DataCopy延迟到对应TQue.DeQue，按实际FIFO先后完成；第一半M产品确实存在pending第二A读取。A队列DeQue次数等于完整A读取次数，跨K/N不重复等待。
- K40/136/1032/1536/1544等8倍数尾块、M/N非对齐、全负、两batch、N分片1/2、workers1/3、empty worker、单双window；baseN32/128/256。
- 环缓冲每个Fixpipe起点/stride及有效/补零C精确检查；Max(N)→Sum(M)和最终task覆盖相符；A/B读取元素数与预定公式一致。
- MTE1/MMAD/Fixpipe同步模拟，event credit计数和队列所有权有界；**不是完整硬件异步仿真**，不证明所有硬件顺序或性能。
- host production/TUNING各1400配置（各16选择），假tiler仅接受请求tile；实际host字段与父版逐项对照，除dual1→29外Schedule/workers/block数/总GM allocation完全一致，低资源、布局/batch和pins回退。
- manual AIV函数体与父版逐字相同。新的span布局由producer/ring模型检查；未声称执行了Ascend Vector指令或真实BF16精度。
- tiny TT既有700个实际源码执行、production/TUNING各432尝试及30量化FP64对照另外回归。

**CANN9编译、NPU精度和性能：PENDING。**新分支不并入main；准确SoC、shape/plan/msprof与同设备重复A/B仍缺失。

## 正式计划

独立官方模板只替换kernel.asc，dry-run后提交一次。对同一ID查询到终态，保留kernel SHA、15点precision/time和原始结果的私有本机副本。
比较第8点与query-block69.03μs；第11点是否可能命中新路径以容量/实测plan为准，不假定。
没有明显收益则归档这一结构并恢复query-block，不继续相近tile参数提交。整体重大提升尚未达成。
