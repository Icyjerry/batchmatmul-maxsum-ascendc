# C10：完整 M 分段复用 B

## 证据与假设

父实现 a2e6763（experiment/c10-balanced-m-shards）正式任务6ac7b3c8694b590c3c0218c4通过15点，C10单次91.53μs。负载均衡已降低最重核行数，但每核两个M微块重复读取同一B。新假设：在实际容量允许时，一块C持有核负责的完整M分段，用原双缓冲B/双L0流水遍历全部N，减少重复B输入。正式dtype/layout仍有历史冲突，BF16/FF命中是条件假设；没有从耗时推断实际route。

## 实现与成本

分支experiment/c10-full-m-shard，kernel370786B，SHA256 `f2ea9e355ad98709a3c1c0a4cce72d1ccc6bb8c8067624e7236ffdddd13eef78`，39行新增/1行删除。只新增host容量选择和改变既有balanced launch的局部Schedule；device/Vector/Plan/GM分配/其余launch逐字节保持父版本。不新增GM通路或分配。

继承UseBalancedMShards的dtype/layout/shape/pin/真实核数限制。先按16行单元计算完整M分段，再由真实L1/L0A/L0B/L0C/UB及原arena确定最大可用16列对齐N宽；至少N128，否则回退原balanced路径。生产Plan及allocator仍不变。初稿N128只经过本地模型，容量推导后选择N144；没有正式扫参。

条件目标4096/1280/1152、20核：M208/N144/K64，半M104行（8对齐但不16对齐），完整A1=479232B，双B1=36864B，闲置A队列1024B；加4096B余量521216≤524288B。L0A53248/L0B36864/L0C119808B。新partial prefix16896B、双C ring每核239616B，共4809216B；旧arena5259264B，system偏移不变。通过实际资源检查才启用；不是固定20核。

抽取真实Cube源码的完整目标执行比较：

|计数|父balanced|完整M|变化|
|---|---:|---:|---:|
|B输入元素|58982400|29491200|−50%|
|C/Fixpipe块|200|180|−10%|
|MMAD/B复制调用|3600|3240|−10%|
|A2元素|23592960|42467328|+80%|
|B2元素|58982400|29491200|−50%|
|总L0操作数元素|82575360|71958528|−12.857%|

完整K点积、完整N的Max、原顺序FinalizeRows求Sum不变。A2开销和较大C归约可能抵消B读取收益；上述计数不是硬件速度预测。

## 本地验证

`python3 tools/validate_c10_full_m_shard.py`最终全通过，日志忽略路径artifacts/c10-full-m-shard/cpu.log。

- 8组抽取实际manual Cube源码：完整目标及父对照、K/N尾块、24/28核和小代理、全负数据。整数NZ/ZZ/ZN物理布局、延迟MTE2/MTE1/MMAD，每个完整K的C及Max-Sum正确，旧arena前缀/其他核/尾部边界守卫不变。
- 160组实际Vector所有权/store与实际FinalizeRows：半M104等8对齐但不16对齐、尾行、空闲核、每行唯一写入、未写padding污染/负数/唯一y。该部分用合成已完成maxima隔离地址问题。
- 912组实际ManualCopyC与原非fullK Max树：半M72..128、列尾、两个UB缓冲和释放后破坏GM环槽。分别模拟AIV与合成已完成的伴随核，不是真实硬件Cube/AIV并发。
- 生产及TUNING各1120实际host控制配置/31命中：实际容量/边界/pins/各布局及核数、Plan不变、原arena容量。库tiler是CPU替身，不是CANN库plan证明。
- 四故障控制（写padding、硬编码半块64偏移、过早GM释放、Max改Sum）均被拒绝。
- 完整逆向移除本次helper/launch后kernel逐字节等于a2e6763，受保护七文件逐字节等于1734f16。

队列Alloc等待最后MTE1读者是模型显式契约假设，不是CANN/NPU证据。整数模型不验证BF16精度或速度。正式CANN9编译/15点精度/实际route/SoC/profile/latency均PENDING。隔离提交目录/private/tmp/bmmms-c10-full-m-shard/project已核对SHA及七文件，dry-run只含kernel。仅提交一个正式gate；无收益/回退则恢复a2e6763，保留反例，不扫相邻N宽。

Implementation **c1a52ef** 已push；唯一正式任务 **6ac7bcb6694b590c3c08ce0e** 创建成功，同370786B/SHA f2ea9e35。Native PENDING；仅查询该ID，不重交。

## Native terminal: Pass15, clear regression, archived

Unique task **6ac7bcb6694b590c3c08ce0e**, implementation **c1a52ef**, kernel370786B/SHA f2ea9e35. Formal compile and15/15 precision passed, allprecision_ratio=1. Timesus:

`[1.89, 2.9, 3.28, 3.97, 5.42, 9.86, 8.0, 44.43, 67.96, 178.32, 88.39, 97.17, 13.14, 11.03, 9.57]`

Total **545.33us**, latestuserTbest calculatedmean **49.13404004**, notlive rank. C10 **178.32us** vsparent91.53us is **94.82% slower**, also clearly aboveolder96.98-100.24 range. Do not retain this candidate. No identicalrepeat or nearbyN/BM scans. All adverse C2=2.90/C3=3.28/C8=44.43 etc retained; unmodifiedroute changes notattributed.

CPU Breads-50%/Ctiles-MMAD-10%/totalL0elements-12.857% didnot establish hardware speed. A2+80%, largerM/nearlyfullL1/consumer andpipeline costs are diagnostic clues only, not measured bottlenecks. Actualroute/SoC/profile/bounddevice A-B unavailable. Raw ignored artifacts/c10-full-m-shard/official.json.

Archive this experiment, restore wholepassed **a2e6763** (368782B/SHA16b51684), retaining balanced ownership/C8phasedA. Main/historicaltags untouched, overallgoal remains incomplete.
