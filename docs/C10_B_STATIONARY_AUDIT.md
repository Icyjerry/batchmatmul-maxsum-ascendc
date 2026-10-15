# C10：固定N组/M分片、完整B驻留（实现前审计）

## 原版真实设备证据

2026-10-15，当前保留kernel2073f48e/a11e2d9/353255B，实际DSOca36b327。9382/24AIC48AIV、logical0→physical14、CANN9/caller20。明确本地fixture `(B,M,N,K)=(1,4096,1280,1152)`/BF16 NN；shape来自用户记录，dtype/layout来自队友DISPATCH，不能当所有正式隐藏属性重新独立确认。

本次实际完整normalPlan：dual36 BM128/BN128/BK128/Mt32/Nt10/Ns5/workers20/window2/PK384/tree8，system16777216/total22102016；cube stepKa18/stepKb2/depthA18/B4/dbA2/B2/C1/shareL1425984。tree8不改变这个full-M生产者实际two-C。actual symbol为bmmms_manual<BF16,NN,...SPLIT_FMATRIX=true>，20Cube40AIV，五报告每核均144MMAD（全2880）。

全storage FP64 golden398.5837707519531，一次和五次实际输出完全相同（本fixtureabs/rel=0），输入/yguard通过。一次default8表×5，TaskDuration `[72.642906,73.422935,73.242928,73.782951,72.682907]us`，median **73.242928us**，不是队友另一source/设备的78.58us。完整报告/source/DSO/input/plan/SoC绑定。

PMU每报告核心均值再五次median：AIC62.852750/MAC41.734167/MTE1 37.848472/MTE2 52.074611/Fix7.886306us；AIV68.833764/Vector9.431486/MTE2 5.068958/flag0wait32.120083/flag1wait23.230319/SyncAllflag14 4.261014。统计重叠，不能求和为临界路径或断言可全部回收。

## 排重与新假设

C9 stationary-B审计只有1.8%总字节收益且最忙核不变，已取消；C10 Bpack曾本地慢1.73%/OJ80.60vs77.22，BN256/BK64 single-C、MAC-first、旧包大小/晚credit等也已归档。不重新pack到GM，不换L0 tile/BK/PK/offset/flags救旧方向。

新方案针对NN输入的**实际连续读取片段与工作所有权**：每N shard分4个M owner；worker `ns=worker/4, shard=worker%4`，负责M tile `[8*shard,8*shard+8)`、N tile `2*ns`与`2*ns+1`。每N tile依次处理8个M tile：B完整K1152一次驻留L1，A按K384包pingpong。与旧A驻留不同，但不是C9 NT总GM无改善的相同负载结构。所有320个MN tile唯一计算，每tile升序9×K128 MMAD，完整C后才Max。

- 完整B NZ `[K1152,N128]` 294912B，L1[0,294912)。两A NZ `[M128,K384]`分别[294912,393216)、[393216,491520)；加4096安全区仍在实际L1524032以内。无新GM分配、无新GM预处理/通路。
- B ND2NZ一次nValue1152/dValue128/srcD1280/dstNzC0Stride1152/NStride1；每M A三包nValue128/dValue384/srcD1152/dstNzC0Stride128/NStride1。
- A2沿原LEFT Load3D，channel384，K在包内0/128/256；B2沿原RIGHT transposed Load3D，l1W1152/channel128，mStartPt=完整k0，mExtension128/kExtension128。使用原公开Load3D及原reset/FMatrix模式；实际API语义必须源码模型+CANN+native证明，审计未证明。
- 每核原16 C frames、144MMAD不变；L0A/B仍双32768B，two-C各65536B；原span2/two-GM-slots不变。

## 必须改变的Vector所有权

原窗口拼接相邻两个N tile；新窗口拼接相邻两个**M tile**，同一行号位置属于不同M。因此不能原样调用ManualFullMConsumeWindow合并两个C：每帧先独立完成MaxN128，写入8×64 FP32的本地行最大状态（每AIV处理64行）。第二N pass再与对应8×64状态合并，最后写原 `(batch*Ns+ns)*M + m0+rowStart` partial。两个N pass始终在同一worker，保持原五份完整M partial和原FinalizeFullMTiles。

每AIV比原64个状态多1792B，无新GM。保持C ring span2布局：pair=localM%2，Fix dstStride256。Vector每window先用原CQ双缓冲读取两M frames，等MTE2已读后返同一个slot credit，逐帧归约/更新对应M的本地状态，不能把两帧当同一M的不同N取max。此变化保留160次窗口通知（每worker8），防止把span缩1而翻倍信用开销。全部N→M合并顺序和最终MaxN→SumM保持。

## 可复现算术审计（不是生产者模型）

`python3 tools/audit_c10_b_stationary.py`通过：320 tile完整唯一覆盖、正负可分离整数proxy/全部5×4096 partial独占/MaxN→SumM；原new L1区间与原GM容量核对。没有执行实际新producer或事件、FP16/BF16或NPU时序。

| 指标 | 原 | 提议 |
|---|---:|---:|
| A输入调用 | 48完整A | 960 K384包 |
| B输入调用 | 960 K384包 | 40完整B |
| 输入总字节 |108527616|106168320|
| 最忙核输入字节 |5603328|5308416|
| 逻辑GM连续行片段 |374784|168960|
| MMAD / Fix / 通知 |2880 / 320 / 160|相同|
| partial / ring字节 |81920 / 5242880|相同|

总字节仅降2.17%、最忙核5.26%；片段降54.92%。这不是54.92%提速预测。多包A调度、B跨N覆盖等待、更多UB状态等可能抵消供应收益。

## 实现与验证门槛

当前**未写新kernel**，kernel仍2073。下步仅新增独立默认关闭C10入口/精确guard，不改MakePlan、main、golden、正式测试/依赖。仅原本地同plan20workers/Ns5/window2/PK384和真实资源/原GM容量命中，其它预算/plan回原；不假设硬件总核20。公开B1/M4096/N1280/K1152/BF16NN，tuning pins回原。

生产者须证明：B初次ready、8个M最后B reader之后才覆盖下一N、A包两个槽三BK128最后reader/跨M游标、L0 MMAD最后reader、two-C最后Fix、GM窗口信用和新的M帧消费者、原partial唯一写者/全局排空。先实际源延迟模型+fault controls+wholeinverse/protected7/guard容量，后CANN9、一次mixed完整FP64/guards，再一次默认8表×5。实际入口/20Cube40AIV/每核144MMAD必须捕获。

采前固定准入：median<=**65.9186352us**（parent73.242928下降10%），且全五<**72.642906us**。失败归档恢复2073，不扫M shard数/PK/BK/flags/offset/再采同source。大收益才全负/同地址变化输入/正式15。NPU候选精度/性能/正式15均PENDING，整体冲榜未完成。

原版raw完整本地artifacts/c10-native-audit/c10-retained-audit-evidence.tgz（14893593B/174members/40CSV，input/golden身份逐一核对，目录700/文件600）；原DSO/source身份引用原冻结保留构建，未重新编译。plan14712/native45209/download22313均终态0，实际queue再次空。
