# C8：主块分片与缓存匹配尾块

## 假设及范围

现有 M-major 整块分工把大部分 M 尾块集中于最后两核。按实际 padded Cube 工作拆分主块，再分散整尾块，有机会缩短最慢核的路径。额外 B 搬运和任务映射开销可能抵消收益；不根据 FLOP/计数预测 latency。

精确既有 C8 guard：BF16/TT、B1/M1025/N1031/K1032、dual33、M128/N128/PK384、nTiles9，既有资源/pin/arena 检查通过，实际 workers 在8..32。其余配置保持旧算法。真实正式 shape/layout/SoC/route/profile 尚未由 API 提供，不能从耗时反推。

父版本 `a2e6763`，候选 372771B，SHA256 `aa2aabc1ab1cea9270173966aa93748762e3ce0514383b81512be4fa1d784bec`。kernel 104 加/25 删；整个 TT 区域、host owner helper、launch 三处替换可恢复父版本全文件。protected7 字节一致；不修改输入、GM allocation/arena、plan、K 累加或最终 MaxN/SumM。

## 实现

- 64 个完整 M128/N128 cell 拆为 512 个 M16 atom；每核取连续 atom 范围，将同 cell 连续 atom 合并成一次 C fragment。
- Host 按 padded area、small-MMAD barrier、C count 依次比较，附加 N 尾块给最后仍缓存相同 M 的核，再分配 M 尾块；corner 优先复用 M-tail A。owner 编码为两个 uint64，传入 kernel，无 GM 表。
- `TTWorkAt` 是 Cube、B 预取、AIV 共用的唯一任务映射。B 双包 FIFO 按新 Nt 流前进；完整原始 M 面板仍驻留 A1，缓存失效和最后 MTE1 reader 协议保留。
- NZ M16 slab 的来源是 `(m/16)*kp*16 + k*16 + m%16`。fragment 起点16对齐，子视图偏移 `row*kp` 与该地址一致；调用原 Load3D helper，channelSize 使用 fragment padded rows，kStartPt 仍为0。CPU 物理地址模型通过，native API/编码仍需 gate。
- C/Ring 容量保留 M128/N128，Fixpipe 只输出 fragment padded rows。AIV 按相对64行拆分，写回包含 fragment offset；full-M fragment 只写自己的有效行。整 M1 tail 仍填满旧 M128 partial cell 的两个半块，避免最终 merge 读未初始化 padding。所有零行 AIV 仍完成双 ring credit。
- 默认关闭模板仍沿原算法；kernel 增加16B默认零 owner argument，旧 TT launch ABI 有变化。这不是所有路径完全不变的声明。

## 真实源码 CPU 验证

命令 `python3 tools/validate_c8_balanced_tail_frame.py`：

- Host production 和 TUNING 各3024计划、4命中；actual resource/pin/shape fallback、plan和GM总量不变。
- 8..32所有核数2393任务逐一对照独立 Python atom枚举及重新计算贪心 metric；每个有效 M/Ntile行恰好一个 owner。
- 8组真实 Cube producer：8/20/32核 K776 proxy 与20核精确K1032，正负且依赖K的输入、延迟/立即 Fixpipe；NZ/ZZ/ZN、逐元素 fullK C含padding、A分区ready、最后reader、输入/GM/event guard通过。
- 精确20核计数 A/B DMA96/291、MMAD873、A/B source elements3178560/11689464，与先前纯数学审计一致；旧78/243、MMAD729，B元素9575928。风险计数不删。
- 42组真实 queued AIV：8/9/13/20/24/31/32核、全负/混合、三种引擎优先级。破坏性 GM release、UB复用、所有worker barrier、每个partial唯一writer、poison-padding、MaxN后SumM、y/arena guard通过。
- 十个负对照（错row origin、错cache shape、错B映射、漏A phase ready、漏M_FIX、整64行覆盖相邻fragment、错partial origin、漏GM credit、漏partial ready、漏最终barrier）均拒绝。

局限：整数模拟不是 BF16/FP32误差评估；两边分别执行真实kernel并用合成伙伴处理跨核credit，不是完整硬件协同仿真；host是假tiler；没有设备耗时或profiling。

## 正式 gate

隔离 `/private/tmp/bmmms-c8-balanced-tail-frame/project`，protected7来自1734f16；dry-run仅372771B/上述SHA kernel。commit/push后只交一次，立刻保存ID并查询终态。CANN9编译、15点精度、实际耗时 PENDING，无ID。

只有15点Pass且C8<=37.111μs（近期父最低43.66的85%）才原样复测确认明显收益。否则保留证据并恢复完整a2e6763；不扫描邻近tiles/package或重复失败方向。原始日志在忽略的 `artifacts/c8-balanced-tail-frame`，目录700/文件600。
