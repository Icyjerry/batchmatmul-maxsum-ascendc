# OJ 分派记录

更新：2026-10-13。由主代理维护；确认新路径后追加证据，旧结论失效时写明替代关系。

## 如何读这份文档

- **已确认分派族**：真实优化版本的独立分支变化在普通 OJ 性能反馈中形成明确对应关系。没有读取 OJ 的 kernel trace。
- **较强支持**：改动和 OJ 响应支持某个函数族，但未唯一隔离布局或 dtype。
- **待确认**：只有当前逆向 shape、本地执行记录或源码条件，不能当作 OJ 的实际属性。

布局字母依次表示 X1、X2：NN=`false,false`，NT=`false,true`，TN=`true,false`，TT=`true,true`。`T` 模板类型可以是 FP16 或 BF16；没有 dtype 隔离证据时不唯一指定类型。

四布局对照基准是已通过 OJ 15/15 的 `91b64f8f795513db1fa720140492c78260d5792685306cf351ae1df3912e7457`，Git `022be22`。
[对照源码与映射](.cannbot/optimization_20261010/c6_original_k_const/submission/mapping.md)。

当前保留完整版本为 `b8817327235bc702df045114f673547a1fd04ac5846a78a543ffcb1d32728c01`，普通 OJ `6acdd94de76989292739d40b` Pass15。C12在B两阶段准备上提前直接搬raw A到原Aslab布局，该次87.93 µs；C13半块流水保持，9.11 µs。完整15项来自同一次CLI结果。
[当前源码与映射](.cannbot/optimization_20261013/c12_direct_raw_aslab/on_c13_half/candidate/mapping.md)。

## 当前结论

| Case | 证据级别 | 已知分派或对应路径 | 尚未确定 |
| --- | --- | --- | --- |
| 1–3 | 待确认 | 保留当前源码路径；本轮未做 OJ 分支隔离 | 实际 dtype/layout 与具体入口 |
| 4 | 用户已确认shape/属性 | B4/M8/N16/K128 BF16 TT；强制分派可捕获 | 当前实际normal计划待读取 |
| 5 | 已确认 full-K MIX11 优化族 | `UseSmallC5Direct` → static16×32×128 direct MIX11，B8/M16/N32/K128 | dtype/layout 未唯一隔离 |
| 6 | 用户已确认shape/属性 | B13/M23/N73/K192 BF16 NT，较早 `dual19` static direct 分支、位于 `MakeSmallFullKBatch` 前；强制分派可捕获 | 当前性能瓶颈待同源本地分析 |
| 7 | 已确认优化族 | `MakeSmallFullKBatch` 中的 NN/TN/TT static full-K MIX11 + UnitFlag3 | NN/TN/TT 中哪一种、dtype；实际 tile 仍依赖 shape |
| 8 | 已确认参数和优化路径 | B1/M1025/N1031/K1032、BF16 TT；当前精确 `dual39`，BM112/BN128/BK128、20 AIC/40 AIV，full-M K16 A准备、AB流水、lane fold、AIV0最终归约 | 五轮完成，当前OJ36.31/oj_like36.959999 µs；按用户要求停止新增C8轮次 |
| 9 | 用户已确认shape/属性 | B1/M2048/N1536/K1280 FP16 NT；资源通过时 `dual36` / `RunManualFullMCube<T,…,false,true>`；强制分派可捕获 | 当前normal计划/PMU待测 |
| 10 | 已确认 BF16 NN 分派族 | 当前 retained resident-A `dual36` / `RunManualFullMCube<T,…,false,false>`；NN 和 dtype 两步真实完整算法对照有一致响应 | 精确 shape 与完整 tiling 未直接观察 OJ；旧本地 FP16 TT 记录已失效 |
| 11 | 已确认 TT MDL 分派族 | `dual2` / `bmmms_dual_mdl<T,true,true>`；当前保留 A4/B4 分组 | dtype；M/N 精确值仍未唯一确定 |
| 12 | 较强支持 BF16 TN packed-B 分支 | `dual6` / `bmmms_manual_case12_packed<T,true,false,…>`；当前启用 A slabs 变体 | 未直接观察 OJ 属性；精确 shape 仍未唯一确定 |
| 13 | 已确认 FP16 NN single-frame 优化族 | `UseTallSingleFrame` / `UseTallHalfPipeline` → `bmmms_tall_single_frame<T,true>`，继承 `dual34` 计划 | M 的精确值；不能只凭耗时确认 M8192 |
| 14 | 已确认 BF16 NT wide-N 优化族 | `MakeWideNManualFrame` → 资源允许时 `bmmms_wide_n_single_aiv<T>`，继承 `dual21` | 完整 shape 未单独隔离 |
| 15 | 已保留，未在本轮隔离 | 已通过的 C15 MIX11 / packed finalizer 融合 | 不根据旧属性记录追加新的布局确认 |

表中“当前逆向 shape”来自用户记录与本地 manifest，不代表读取了隐藏测试集。
[15 个本地 case 的记录](.cannbot/optimization_20261008/local_case_check/cases15.jsonl)。

## C11：四次独立布局验证

四版从同一 `91b64f8f…` 基准生成，分别只选择 NN、NT、TN、TT，两种 native dtype 一起覆盖。优化函数、资源条件和其余布局保持一致。

它们把符合 K2048 通用区域和资源检查的计划转入现有手写 resident-A 流水：BM80、BN128、BK128、双 B 包 K256+。这不是原 MDL 内的优化，因此结果只能用于判定该替换影响了哪种布局。

| 版本 | C11 µs | Submission ID | 精度 |
| --- | ---: | --- | --- |
| 公共基准 | 88.31 | `6aca480c694b590c3c7353e9` | Pass15 |
| 全布局替换 | 117.65 | `6aca4a57694b590c3c751e45` | Pass15 |
| 仅 NN | 88.52 | `6aca4c5c694b590c3c769709` | Pass15 |
| 仅 NT | 87.06 | `6aca4d53694b590c3c774bb8` | Pass15 |
| 仅 TN | 87.55 | `6aca4e4f694b590c3c781120` | Pass15 |
| 仅 TT | 118.09 | `6aca4f37694b590c3c78e47b` | Pass15 |

只有 TT 复现约 30 µs 的退化，与全布局版相差 0.44 µs。TT 版另外 14 个 case 的波动为 −3.73%～+4.28%。因此确认受影响的是 TT 分派族；NN/NT/TN 没有复现该退化。

按当前 B1/M1536/N2048/K2048 的逆向记录，原 TT 路径为：

- `dual2`，`bmmms_dual_mdl<T,true,true>`，`DUAL_MDL_CONFIG`。
- BM128 / BN256 / BK64，Ns8、workers20、window1。
- `stepKa=2, depthA1=4`；`stepKb=4, depthB1=8`。
- L0A/B 双缓冲、L0C 单缓冲；`shareL1Size=327680`。

这些完整 tiling 字段最初来自该本地 frame 的真实 DSO 导出。后续 `groups5` 实验只在原 TT `dual2`、BM128/BN256/BK64、stepM/N1、A2/depth4、B4/depth8、L0A/B 双缓冲和 L0C 单缓冲等条件匹配时改分组，C11 达到 102.93 µs，较原 88.31 µs 退化 16.6%。其余大 case 的漂移不足以解释这一变化。这进一步支持上述入口和匹配字段在 OJ C11 中生效。

仍未直接读取 OJ tiling。M1536/N2048、Ns8、workers20、window1 和完整 TCube 描述仍是本地 frame 的对应值，不能全部升级为 OJ 精确参数。两种 dtype 同时修改，也未唯一识别 dtype。

**后续原则：优化原 TT MDL，不重新采用这次退化的 BM80 手写替换。**

[四版源码、SHA、完整 15 例时间与对照](.cannbot/optimization_20261010/c11_layout_trials/summary.md)；
[原本地 tiling 证据](.cannbot/import_claude_20261010/ready_for_oj/20261010__UNMERGED__LATEST_CANDIDATE__c11_bm80_selective__53356880/evidence/cube_details.json)。

## C7：实际有效版本已更正

用户提供的 `kernel_maybe_c7.asc` SHA `883f7a82…`，与 `c6_c7_nonnt_stream__6a7b30a3` 仅差末尾一个 LF。该版本原报告中的“无 OJ 收益”已被用户后续确认和本工作区 OJ 结果替代。

它在原 `MakeSmallFullKBatch` 入口中增加 MP32/NP80 或 NP128 的静态 NN/TN/TT 调用，并让既有 `STREAM_C` 的 UnitFlag3 覆盖这些布局。保持完整 K、FP32 MMAD、maxN→sumM；NT 保持原路径。

融合前 C7 为 8.00 µs，融合后为 6.90 µs，后续完整版本为 6.60 µs：

- C13 基准：`6aca43f8694b590c3c70660a`。
- C13+C7+C8 实验组合：`6aca463c694b590c3c7200df`，Pass15。
- 撤回 C8 后的当前基准：`6aca480c694b590c3c7353e9`，Pass15。

**此优化使用原有效 full-K 入口；没有切换到另一个 generic 算法族。** 不能根据三种布局一起生效的结果进一步指定 C7 是 NN、TN 或 TT。

[源码绑定与最新反馈更正](.cannbot/import_claude_20261010/latest_feedback_corrections.json)。

## C6：较早返回会遮挡较晚的候选调用

原源码中，BF16 NT `dual19` 的静态 direct 分支在 `MakeSmallFullKBatch` 之前返回。当前记录的 B13/M23/N73/K192 对应 MP32/NP80/KP192。

队友 NT 候选 `ff940442` 只在后面的 `MakeSmallFullKBatch` 中增加静态调用，不能改动这个较早入口。该 BF16 NT 入口本来已经启用了 UnitFlag3；搬用相同调用不构成新的优化。

本工作区已把 KP192 常量化直接加在原 MP32/NP80 分支，OJ `6aca480c…` Pass15，C6=9.66 µs，没有超出近期 9.34～9.85 µs 波动的明确收益。**不能以这次无收益证明或排除实际 OJ 属性。**

后续改动应先确认修改的是原入口还是较晚的 fallback，并记录是否有新的计算或搬运收益。

## C12、C13、C14 的有效路径证据

### C12

原 TN packed-B 改成直接读取 raw B，局部测试曾快约 6.8%，但 OJ `6ac8c141694b590c3c994c75` 的 C12 达到 116.50 µs，原 packed 版本约 96.47 µs。该改动已撤回。

这支持 C12 被 `dual6 && TX1 && !TX2` 的 packed-B 路径覆盖。它不单独证明 dtype。原 `BM128/BN128/BK128`、two-C、Ns2/W20 是当前本地 frame 的已测计划。

后续 A slabs 优化只选择 BF16 TN、继承 dual6/BM128/BN128/window1 的 full-K resident-A 计划，M/K 为128倍数；原B packed和two-C保持。同一完整SHA两次Pass15，C12=93.68/94.40 µs，旧版本多轮为96.37～96.96 µs，支持小幅收益。它进一步支持 BF16 TN 及该匹配计划，但不将有限性能反馈写成直接读取了 OJ 属性。

**保留 packed B。** 已做过的 Zn+A3D（包括 BN128）、BN256/BK64、A3D-only、增加 prepRows、跨 N 队列及 PairA 重用均有记录；不要把同一方法换名后重做。

[raw-B 完整结果](.cannbot/optimization_20261009/local_merge_c8_raw_c12/submission/oj_results.json)；
[实际瓶颈报告](.cannbot/optimization_20261008/confirmed_pipeline_analysis/c12_v3/analysis.md)。

### C13

只增加三个 single-frame 代码块的 d52edf 版本，OJ `6aca43f8…` Pass15，C13=10.90 µs，之前为 12.66 µs。其 selector 只接受 FP16 NN、B1、N64、K128、M 为 512 的倍数且在 [2048,8192]，每 worker 恰好一块 M512，并继承 `dual34`。

因此确认这一分派族；M8192 是当前逆向记录，尚未由本轮单独确定。当前融合保留该原样代码。

[三个代码块的原始 diff 与条件](.cannbot/import_claude_20261010/ready_for_oj/20261009_c13_single_frame_d52edf/evidence/change.patch)。

### C14

外部提供的融合版只增加 wide-N device frame、host resource selector 和提前 launch，C14 从约 13.14 降到 10.94 µs，后续约 10.7 µs。selector 只接受 BF16 NT、B1、M16～128、N≥4096、K32～256、16 对齐，以及原 `dual21` 的匹配计划和资源。

最新源码核对：当前raw B2已经是**单缓冲**，由原 M_MTE1(0)保护复用。M64/N8192/K128本地记录的最终计划为dual21、Ns/workers16、Nt64、host window1；raw设备独立固定每两个NP128合成一个256列frame，每worker4个Nt/2个frame。host window1不能被读成raw frame只有一个pane；较早dual1的Ns10/BN256/Ns5描述不对应此入口。上述数值是当前源码对记录shape的计划推导，未观察OJ tiling。

原有效入口是 raw `bmmms_wide_n_manual_frame<T>`，MIX(1,2)。新增 full-row `bmmms_wide_n_single_aiv<T>` 为 MIX(1,1)，在原 selector 与 full-window UB 容量检查通过后接替它；容量不够仍用原入口。

OJ `6aca5407694b590c3c7c6988` Pass15，C14=9.84 µs，较紧邻基准 10.78 µs 快 8.72%。后续 C11 A4/B4 组合版为 9.87 µs，收益保持；该入口现已保留。

[原融合 manifest](.cannbot/optimization_20261009/c14_teammate_fused/manifest.json)。

## 当前优化与最新反馈

- C11 原 TT MDL `groups5`：SHA `68982261…`，Submission `6aca531e694b590c3c7bc3c7`，Pass15，但 C11=102.93 µs，已拒绝并恢复原 MDL。
- 该版只改 A/B K 分组5、depth10 和 L1 字节数；全部32个K64面板保留。K重排起点改变可能改变FP32累加顺序。不能把它的退化归为分派未命中。
- C14 full-row single-AIV：SHA `4f577cb7…`，Submission `6aca5407694b590c3c7c6988`，Pass15，C14=9.84 µs，已保留。
- C11 A4/B4 + C14：SHA `c2516e6e…`，Submission `6aca550d694b590c3c7d4e17`，Pass15，C11=83.57 µs，较紧邻 C14 基准的87.63 µs 快4.63%。它保留原B4/depth8和K256重排起点，只将A2/depth4改为A4/depth8。当前已保留。
- C12 A 面板预打包：SHA `257130d5…`，首轮 `6aca56fb694b590c3c7ed784` Pass15，C12=93.68 µs。
- 同一完整SHA确认提交 `6aca57f2694b590c3c7f88a2` Pass15，C12=94.40 µs，较紧邻96.43 µs快2.11%。两轮均低于旧多轮96.37～96.96 µs，已保留小幅收益。当前整版成绩采用第二轮完整15项，不拼接两轮最小值。

[C11 候选与约束](.cannbot/optimization_20261010/c11_tt_mdl_groups5/manifest.json)；
[C11 已保留 A4/B4 组合](.cannbot/optimization_20261010/c11_tt_mdl_groups4_on_c14/manifest.json)；
[C14 候选](.cannbot/optimization_20261010/c14_single_aiv/manifest.json)；
[C12 已保留版本及两轮结果](.cannbot/optimization_20261010/c12_a_slabs/manifest.json)。

### C9/C10：必须追踪最后一次分派赋值

当前逆向 C10 FP16 TT frame 的已测最终计划是 `dual36`、BM128/BN128/BK128、Ns5、workers20、window2、B package384。较早的 TT balance 代码会先设置 `dual35`，后面的 generic resident selector 仍可覆盖它；不能把中间值当成最终入口。

旧 C10 `dual29` PMU 和初始 B128 包的报告不对应当前最终路径。M112 减尾波或 B128→256 的想法不能直接据这些旧报告实施，且 Ns5/B384 已存在，避免重复优化。

当前新的 A3D 配置复用候选：SHA `189b6673…`，Submission `6aca5b0f694b590c3c81f209`，结果待反馈。它只对资源通过的 `dual36` TT 大 M 区间启用，保留 A/B 数据、完整 MMAD 和归约；每次刷新 A 设置真实 LEFT FMatrix，复用 kernel 的零 padding。`fMatrixCtrl=false` 只是 LEFT 选择，不是禁止设置；实际使用 `IsResetLoad3dConfig` 控制写寄存器。默认共享 helper 语义保持，C8 当前记录不在启用区间内。

这仍是 C9/C10 TT 方向的优化假设，不能提前写成它们的 OJ 布局已唯一确认。
[最终计划和候选 review](.cannbot/optimization_20261010/c10_a3d_config_reuse/manifest.json)。

该配置复用版已 Pass15，C10=78.09 µs，基准77.99 µs；没有明确收益，已拒绝并恢复原控制写法。不能用这次无收益确认或排除 TT 布局。

### C5：Claude 工作区有效版本的融合

Claude 工作区35626298版本有用户两轮4.62 µs反馈。当前融合只复制其selector和earlydispatch，共用原完整数学体；两种dtype、四种布局、原plan和资源检查均保留。

组合版 `6aca6108694b590c3c866f61` Pass15，C5=4.72 µs，基准5.20 µs，快9.23%，已保留。该selector只接受公开B8/M16/N32/K128，并用一组Cube/AIV完成每批完整计算；没有额外探测逻辑。

[融合及完整成绩](.cannbot/optimization_20261010/c5_confirmed_fusion/manifest.json)。

### 未采纳版本的快速分派复核

C6 FP16 NT 与 C7 NT 的旧候选有实测新入口，不能把旧 OJ 无收益归为早 return 遮挡。C6 BF16 NT 的确由更早分支返回，但较早入口已经是同一 static tile + UnitFlag3；重新调用它没有新的优化。

C4 的冻结 route policy 只选 NT。BF16 TT 对照两侧均为 `bmmms_small_vector_k256<__bf16,true,true>`，不是 raw MIX11。旧文字声称其他布局退化，却未给出对应 raw entry，不能把这个对照当成 raw TT 已被评估。

因此按用户要求做了一次真正的四布局前置重接：原完整数学体、工作区和资源检查保留，置于 `vectorRows` 和所有 return 之前，允许原 dual28/vector 计划中经过容量检查的四组 Cube/AIV。OJ `6aca67d0694b590c3c8c38b9` Pass15，但 C4=7.66 µs，基准4.04 µs，显著退化。已拒绝并恢复原入口；不再重试该思路，也未进行本地测试。

[快速审查表](.cannbot/optimization_20261011/unmerged_dispatch_audit/README.md)；
[C4 重接与普通 OJ 结果](.cannbot/optimization_20261011/unmerged_dispatch_audit/c4_all_layouts/manifest.json)。

`dual36` resident MAC-first：SHA `499d8aab…`，Submission `6aca6953694b590c3c8d663d`，Pass15。C9=57.46 µs（基准56.79）、C10=77.99 µs（基准78.13），没有明确收益，已拒绝并恢复d968。只把下一 B 包的释放/预取移到已就绪 MMAD 之后；两种 dtype、四种布局，原默认路径和 C8 停搁保持。没有新增事件、工作量或输出标记。
[候选资源与依赖说明](.cannbot/optimization_20261011/resident_mac_first/manifest.json)。

### C5 sole-MMAD UnitFlag 同步候选

SHA `31bd4f60…`，Submission `6aca6d5e694b590c3c908650`，Pass15，C5=4.85 µs（保留基准4.72），无明确收益，已撤回。只将原 UnitFlag gate 扩展至已有 MIX11 MP16/NP32/KP128 完整 tile，覆盖当前 C5 两种 dtype、四种布局；原 selector、完整数学体、资源、其他路径不变。该入口只有一次 initialized full-K MMAD，Fixpipe3 完整读取并清除所有生产单元，保留终末 PIPE_ALL 和列优先状态恢复。未进行本地测试；不再重试此 C5 同步方案。

[候选与静态依据](.cannbot/optimization_20261011/c5_single_mmad_unitflag/manifest.json)。

### C12 packed-A 完整 C 的 UnitFlag 候选

SHA `81687243…`，Submission `6aca6e64694b590c3c916415`，Pass15，C12=93.55 µs（基准94.36，−0.86%），收益微小且未确认，暂不采纳，恢复d968；不重复测试。原 A slabs selector/资源保留，只在 N 为128倍数时增加 UnitFlag 入口。全部 K128 面板仍升序累加，非末次MMAD=2、末次=3，Fixpipe=3 完整消费128×128；two-C、原 FIX_M/L0/ring信用仍保护复用。只替换 tile 末 M_FIX，使用行优先状态并在终末 drain 后恢复。旧 generic UnitFlag 实验只改了 C8/C11 package，未覆盖此独立 packed-C12。

[候选资源、依赖与范围](.cannbot/optimization_20261011/c12_packed_a_unitflag/manifest.json)。

### C9/C10 final dual36 BN256/BK64 single-C 候选

SHA `f18511d2…`，Submission `6aca6f56694b590c3c9210bc`，Pass15。C9=61.65 µs（基准56.79，+8.56%），C10=77.61 µs（基准78.13，−0.67%，无明确收益），整版拒绝并恢复d968，不重复。沿已形成的最终 dual36，把 BM128/BN128/BK128/two-C 改成 BM128/BN256/BK64/single-C。两种 native dtype/四布局，公开 M[2048,8192)、N[512,4096)、K[512,2048)，N256和K64倍数；真实资源及核数检查并重新求Ns/worker/window/工作区。原A转置、B包FIFO、每Ntile消费者和最终归约保持。

源码例子中完整MMAD/B包计数相同、A L1→L0字节减半、Fixpipe次数减半；代价为single-C等待上一Fixpipe、双CQ增为128KiB。这是源级计算，不是实测性能预测。C8、C11、C12记录shape不在选择范围。每个完整K结果都继续参与真实maxN/sumM。

[review与资源说明](.cannbot/optimization_20261011/resident_bn256_single_c/review.md)。

### C13 原 single-frame 的核心利用候选

SHA `9f9cc18d…`，Submission `6aca71e8694b590c3c940a53`，Pass15，C13=11.12 µs（基准11.05），未体现收益，撤回。无收益不单独证明新资源/availableCore selector 已捕获。沿已确认 `UseTallSingleFrame` FP16 NN 族，在实际核心/存储资源通过时将 BM512 改成416；M8192记录下worker16→20，每worker仍只处理一个完整K128 frame。读取实际M尾，C转置帧的每个实际M列仍完整max全部64个N；只把无效M输出置零，随后448分组的两级纯vector sum。工作区与worker数按新几何重新分配，容量不足保留原single-frame。

源级峰值frame宽减少18.75%，未宣称对应实测收益。完整K64+K64、单L0B复用及所有跨核/局部等待均保留，M求和分组改变可能影响FP32结合顺序，精度待普通OJ。

[候选和尾块/资源说明](.cannbot/optimization_20261011/c13_balanced_single_frame/manifest.json)。

### C11 原 TT MDL 库的 UnitFlag 候选

SHA `fd9709bf…`，Submission `6aca7320694b590c3c94e394`，Pass15，C11=84.47 µs（基准83.77），没有收益，撤回至原A4/B4配置，不重复该方案。只复制原 `DUAL_MDL_CONFIG` 并开启 SDK 公开 `enUnitFlag`，默认旧配置仍保留；选择原 TT dual2、K2048、完整M128/N256 tile与 A4/depth8、B4/depth8、单C、shareL1=393216 的匹配计划，并做真实容量、核数与工作区检查。

原计划、K重排、Ns/worker/所有GM工作量及AIV体保持。SDK按重排后的逻辑末组发MMAD3，中间2，完整Fix3；库的Init/End负责布局设置/恢复，CO1 Destroy执行FIX_M drain。仅使用公开配置，不覆写SDK内部实现。

[候选及SDK原始源码依据](.cannbot/optimization_20261011/c11_mdl_unitflag/review.md)。

### C6 转置 A 对齐搬运候选

SHA `30463f04…`，Submission `6aca758c694b590c3c966feb`，Pass15，C6=9.56 µs（对照9.76），落在旧路径多轮9.38～9.92范围，其他控制项也偏快，无明确收益，暂不采纳，恢复d968；不由此推断布局。在原 `MakeSmallFullKBatch` 容量和完整批次/worker 条件下，native FP16/BF16 TN/TT、M17～31、NP80、K192 使用 AIV 把完整 `[K192,M]` 按行补零到 `[K192,32]`，暂存原私有 ring；Cube B DMA 先启动，等真实 prep12 后读取对齐 A，随后原完整K192 MMAD与 maxN/sumM。NN/NT 和其余原入口保持默认。

临时12288B输入在原20480B私有ring内，无新GM分配；Cube完成A读取后才Fix覆盖，同一AIV只在FIX0后复用prep UB。额外DMA/信用可能抵消对齐收益，C6实际dtype/layout仍未知，不能凭无变化判定属性。没有本地测试或额外观测逻辑。

[完整依赖和资源说明](.cannbot/optimization_20261011/c6_transposed_a_align/manifest.json)。

### C14 NP256 单 tile/frame 候选

SHA `983ac851…`，5600行336058B。沿原 BF16 NT wide-N single-AIV raw路径，在MP<=64、K<=128、真实L1/L0/UB/旧GM工作区足够时选NP256/span1；原NP128/span2默认和fallback保留。原Ns/worker继承，dual21记录shape下Nt64→32，每worker仍两个256列frame；B2原本已单缓冲，two-C保留。原有帧信用和通知频次相同，完整MMAD/Fix/B请求数减少，数据和实际数学项不减。

已完成expanded/compact、资源/索引/事件审查与dry-run。最初submit因登录失效无ID；用户重新登录后成功提交 `6acb3b87694b590c3c0238b0`，Pass15。C14=10.22 µs（保留基准10.10），没有收益，已撤回原NP128/span2，canonical/mirror恢复d968。不重复该方案。不代跑login，不进行本地测试。

[完整review](.cannbot/optimization_20261011/c14_np256_single_frame/review.md)；[manifest](.cannbot/optimization_20261011/c14_np256_single_frame/manifest.json)。

### C7 full-K B 矩形与 C9 window2 组合

组合SHA `8c8201bc…`，Submission `6acb3e96694b590c3c04a3c2`，Pass15。C7=6.93 µs（对照6.78），C9=56.92 µs（对照56.79），均无收益，两项撤回，恢复d968，不单独重交相同版本。独立小case入口的静态MP32/NP80或128、native NN/TN把原完整B2的5～8个Load2D合成一个公开Load3D矩形。half位视图仅重排16位输入，原T类型完整MMAD、UnitFlag3/Fix3、AIV体、所有事件及GM/资源保持。

另一独立host表达式把finaldu36中M>=2048/K<2048的window上限改为2，两native/四布局；C9记录点window3→2，提前一Nt通知与返信用，同时实际窗口80→112，可能抵消收益。原tile/math/C2/CQ/BFIFO保持，host与device用同一window重算GMrings。C10原window2不变，其余记录case路径不变。

这两项互不重叠，用一次完整15例OJ评估；单独准备SHA8ebc2a90/ba635f37未提交，不把单项成绩和组合成绩拼接。

[组合manifest](.cannbot/optimization_20261011/c7_b_rect_c9_windows_fused/manifest.json)；[B矩形审查](.cannbot/optimization_20261011/c6_c7_operand_review/review.md)；[window审查](.cannbot/optimization_20261011/c9_c10_stream_review/review.md)。

### C13 normal-C single-frame候选

SHA `032bdbbf…`，Submission `6acb4398694b590c3c087900`，Pass15，C13=11.87 µs（对照11.05，+7.42%），拒绝，恢复原C^T single-frame；不重复该方向。保留原FP16 NN confirmed single-frame guard、BM512、worker、GM工作区与K64+K64；新增NORMAL_C默认false。新true缓存整个B的L0B 16384B，两片A由3D gather装L0A 65536B并用原M_MTE1保护复用，计算normal C512×64，Fix同完整131072B。

AIV四次128repeat的WholeReduceMax遍历全部512实际M行、每行全部64个N，目标新2KB UB scratch与C不重叠；原两级纯vector Msum/workerSum及barrier保持。新实际L0A/UB容量不足沿原C^T默认入口，完整math/precision等待普通OJ，没有本地测试。

[完整review和资源](.cannbot/optimization_20261011/c13_normal_single_frame/review.md)。

C7已按用户2026-10-11指示暂搁置，保留当前有效fullK/UnitFlag分派，不再派发或提交新C7优化。C9/C10新的布局观察仅允许既有真实完整算法替换，保持提交规范及禁止行为约束。

### C12 A2重用与独立C0/C1候选

SHA `dcbe8798…`，Submission `6acb4689694b590c3c0aa717`，Pass15，C12=93.44 µs（对照94.36，−0.97%），落在旧路径近期控制项93.41～94.72范围，无明确收益，未采纳，恢复原A slabs/two-C，不重复。原p.case12PackedA BF16TN full128 family，PAIR_C默认false；true时相邻两个完整N128 tile按K-major计算，共享每片A2，各C仍升序完整K128并独立K0初始化。two-C、原GMslots2/span1、全部AIV/prepack/finalizer及实际workspace保持。

C0末K后先独立Fix128/ready，再发C1末K MMAD；原FIX_M分别保护两C。新增aFree只在最后实际A消费者之后释放，B2free每bank保持。depth2B FIFO的f+2补包延续到下一pairK0，限同Nsplit，odd尾处理完整Ntile。7/8 M_MTE1事件含SDK预留3、B2free2、A2free2，均Alloc/Drain。源级A字节减半，但当前A slabs已单A命令，合计A+B装载调用仅减少5.56%，额外控制也可能抵消，不提前宣称gain。

[完整review、FIFO和事件计数](.cannbot/optimization_20261011/c12_pair_independent_c/review.md)。

### C9/C10四布局完整Norm算法版本

用户已授权数轮普通OJ，当前NN版SHA `c5a251f6…`，Submission `6acb850c694b590c3c38f91e`。NN/NT/TN/TT每版仅选一布局、两种native dtype，在公开大M/K区域从现有resident33/36切换到**完整原MakePlanImpl dual1 Norm Plan**；全部旧设备/launch/config/body不变。旧Plan及TCube、actualL1/L0/UB/core/system/parts/ring核对通过才返回，其他条件原fallback。原CFG_NORM的UnitFlag默认true singleCO1及64KiB L0pool已由root复核，旧保守guard证据保存在superseded_legacy_guard，未提交旧组。

[完整review](.cannbot/optimization_20261011/c9_c10_layout_trials/review.md)。只有真实算法性能反馈，无额外kernel、标记、延时、故意报错或信息回传；完整K/nativeFP32/maxN/sumM保持。Flat不证明命中，也不排除布局；TT同时涵盖33/36，dtype与精确shape需更多证据。

### C8用户新增参数报告

用户提供[case8_reverse_report.md](case8_reverse_report.md)及两个补充asc。后续输入依据为B1/M1025/N1031/K1032、BF16TT；不再当此前未确定layout处理。原候选完成后进行当前正常配置的本地性能/同步分析，按sum device TaskDuration计时并记录exactSHA、dtype/layout/device/frequency；主模型保持OJ判定采纳。补充低并行验证文件仅作source参考，不重复参数验证或低并行观察提交。

**用户 2026-10-11 最新分派要求替代原先的隐式首版方案：** 后续 C8 优化使用上述 shape + BF16 TT 的精确条件，直接选择目标完整计算入口，确保其后没有 generic 覆盖。实际平台容量与工作区检查保留。在普通 OJ 测得收益后，再考虑恢复隐式区间分派。

## 新确认的更新步骤

1. 记录原/新 source SHA、提交 ID、完整 15 例结果和具体 diff。
2. 写明改变的公开 selector 条件、计划、计算函数和资源要求；检查是否被较早 return 遮挡。
3. 把源码条件、本地实际入口和 OJ 分支推断分开，记录仍未知的 dtype/shape。
4. 若后续结果与旧报告矛盾，在本文件和最新反馈更正中标注替代关系；冻结源码与原始结果保持原样。
5. 保留有效入口作为下一轮基准，不把不同 SHA 的最快 case 拼成一个成绩。

正常完整算法的性能对比不添加额外探测逻辑。禁止探测 kernel、故意延时/报错/输出标记、隐藏数据访问、CPU 代算、漏算或伪造结果。C8 已由用户新报告重新启动；沿已知 BF16 TT 参数分析当前正常路径，不重复旧参数推测实验。

## C10 NN普通算法反馈（2026-10-11）

NN-only旧Norm完整算法版本c5a251f6，OJ6acb850c Pass15，C10=110.03µs，对照78.13（+40.83%），其余控制case没有相同量级变化。这支持C10的NN替换分支；dtype 后由下表隔离，实际 payload 的完整 shape 未直接观察。C9=57.47vs56.79无明显变化，不能据此排除NN或证明其guard捕获。

用户指示无需再对C10提交NT/TN/TT，改NN dtype隔离；三个已准备layout版本尚未提交，不将其写成测试证据。恢复d968原有效resident计划。

### C10 NN dtype隔离

两版与已 Pass15 的 NN 两 dtype c5a251f6 相比，仅把新增 dtype 条件分别收窄为 1 或 2，真实旧 Norm 完整计划、资源、设备数学与其他分支不变。

| NN 选择范围 | SHA 前缀 | Submission ID | C10 µs | 结果 |
| --- | --- | --- | ---: | --- |
| FP16 + BF16 | c5a251f6 | `6acb850c694b590c3c38f91e` | 110.03 | Pass15 |
| 仅 FP16 | 3c2872d1 | `6acb8ee1694b590c3c40b879` | 77.97 | Pass15 |
| 仅 BF16 | 3a46bb68 | `6acb93f5694b590c3c450949` | 111.26 | Pass15 |

BF16-only 复现两 dtype 版的大幅变化，FP16-only 保持原 78.13 µs 水平。因此确认 C10 受影响的是 **BF16 NN** 分派族。旧 FP16 TT 本地假设不能再用于 C10 优化；可复用 case 表已更正。尚未读取 OJ trace，M4096/N1280/K1152 仍沿用用户 shape 记录。

旧 Norm 替换更慢，三版均未采纳，canonical/mirror 已恢复 d968。按用户要求停止剩余 C10 NT/TN/TT 提交。C9 三版均近 57 µs，其布局/dtype 仍未知。

[FP16 完整结果](.cannbot/optimization_20261011/c10_nn_dtype_trials/fp16/oj_results.json)；[BF16 完整结果](.cannbot/optimization_20261011/c10_nn_dtype_trials/bf16/oj_results.json)。

## C10 NN FMatrix 复用候选

SHA `27c01794…`，5600 行、336429 B，普通 OJ `6acb9cf1694b590c3c4d3546` Running。沿原 finaldual36 的 NN/native b16 入口分别初始化 A LEFT 和 B RIGHT，随后公开 LoadData resetfalsefalse 复用配置。保持全部原搬运描述、完整 K/MMAD/Fix、资源/工作区、FIFO、event/归约；未运行本地测试。已核对安装 dav2201 SDK 的标准 V2 + RIGHT + resetfalsefalse 完整调用链，记录网页旧限制与 SDK 实际使用差异，不改 SDK、不直接调用底层 intrinsic。

[源码与依赖审查](.cannbot/optimization_20261011/c10_nn_split_fmatrix/review.md)；[安装 SDK 调用链](.cannbot/optimization_20261011/c10_nn_split_fmatrix/sdk_call_chain.md)。

C10 NN FMatrix 候选已 Pass15，C10=76.45 µs，对照78.13，单轮下降2.15%；其余控制项有不同方向波动。保留为待融合候选，不将这次小幅收益直接否决，也不冒充稳定复验收益。完整15数组见 [oj_results.json](.cannbot/optimization_20261011/c10_nn_split_fmatrix/oj_results.json)。为保持本地/OJ源码一致，当前先完成从d968冻结的C8 A-only精确分派验证，再评估融合。canonical/mirror暂恢复d968。

C8正常配置本地分析已完成：[runtime_report.md](.cannbot/optimization_20261011/c8_runtime_confirmed/runtime_report.md)。native d968=35.381、normalpacked=41.021 µs（各一个代表性调用）；两个source的native/PMU输出均与完整FP64 golden转FP32完全一致。PMU中Bpack MTE2median34.427→15.524，但新增flag12wait median12.923，AIC own/nonMAC暴露基本未改善；这些PMU时间不作为native延迟。TimelineDetail两版kernel参数dump失败，不能分出内部A启动/B后续阶段；未追加采集。C8 A-only exact候选d3d0945f（dual39/Ns2W18/PK384/win4）独立本地验证中，未提交OJ。

## 2026-10-12 C8 交接融合与测试口径更新

已只读导入 ascend-op_claude 的 C8_HANDOFF_20261011、15轮源码/结果索引和完整best工程/证据。当前基准正是对方冻结父本d968，因此直接采用已Pass15的C8修订c1fff45d，没有生成新的融合SHA；7个固定工程文件逐字节一致。canonical/mirror均c1fff，main7455ba7。已有OJ C8=40.94µs，相比原d968的51.92µs下降21.15%。用户明确无需再次验证对面最快候选，未重测或重交此版。完整15项取同一份已有OJ结果，不拼最小值。

本地性能选择已改为oj_like：应用0warmup、5次完整调用；msprof op --warm-up=5 --launch-count=5000 --replay-mode=kernel、默认指标、无skip/符号过滤。保存全部5个TaskDuration并取中位数；5000是采集上限。native单次只用于历史诊断，不能继续用于候选排名。交接同版本五组校准的oj_like/OJ偏差0.40%–2.95%；不认为官方聚合/缓存行为已完全复现。当前已有best5值40.100803/39.860798/39.840797/40.360806/40.380806µs，中位40.100803。

新增本地默认入口 [.cannbot/local_oj_like_20261012/run_device.py](.cannbot/local_oj_like_20261012/run_device.py)，活动工具迁移中；旧native/旧PMU采集脚本保留历史身份。本轮新候选完整正确性和source/DSO/input/plan/device身份gate后才收5完整报告，漏项或未归属多kernel调用判采集失败。源工作区只读。

用户最新安排：工具迁移成功后C8只尝试4轮新优化，保持精确BF16TT路径，完成后保留最快OJ版并转向9–13，只选属性确定或现有分派已经有明确捕获证据的case。15轮交接方向均已归档，不重复；A-only d3d0945f已由用户在对方上下文反馈OJ约58µs（无ID/全15表），因此不再按本工作区未提交状态重交。C10 NN FMatrix27c01794仍保留待融合候选；C7继续park。

## C8 新四轮结果与第五轮分析（2026-10-12）

| 轮次/方案 | SHA前缀 | oj_like中位µs | 普通OJ C8µs | Submission | 决定 |
| --- | --- | ---: | ---: | --- | --- |
| 1 BK256单bank/PK512 | c357f2e3 | 48.259998 | 48.83 | 6acc5456694b590c3ca6655f | 撤回 |
| 2 末K144合并 | 2899c6cd | 41.880001 | 41.56 | 6acc55f0694b590c3ca76463 | 撤回 |
| 3 真实N128 lane fold | 7f7d410d | 40.139999 | 40.16 | 6acc51aa694b590c3ca4daba | 当前保留 |
| 4 BN256单bank/单C | 99631998 | 49.439999 | 49.27 | 6acc5a4a694b590c3caa1f07 | 撤回 |

四版全部完整golden与OJ Pass15，每版只提交一次；全部五个本地样本和各版完整15项反馈单独绑定SHA。R3仅普通OJ比导入40.94低1.91%，本地中位与旧40.100803持平，不称稳定本地改善。其余三版减少MMAD但失去重叠或增加依赖，真实整体变慢，不重复。

用户强调后续策略需性能分析支持并再授权一次C8，因此总限额5轮。复用新工具已经收集的5×60核counter，未新采集或重测best。当前R3 flag12 prep等待中位16.828µs；MAC9.077/MTE1 8.315/MTE2 5.993µs，AIV全程MTE2 12.017/Scalar9.345/MTE3 1.325µs。指标互相重叠且AIV包含prep/consume/FF，不把12µs全归A。当前ring无slot复用，id4含初始/最终信用排空，不能当持续回压；sample1 AIC own-time异常约5ms保留标注，五TaskDuration未删。完整[性能分析](.cannbot/optimization_20261012/c8_current_pmu_analysis/REPORT.md)与8400原counter核行可复查。

唯一第五轮从R3改变A准备为K16×wholeM（pad1040），65A tasks+原81B tasks：源行段10320→1032、A转置650→65，所有真实bit/packed布局/compute/FF保持。代价A GM写90→650scatter、prepUBguard137216；这是针对测得prep曝光的输入/地址发射探索，尚无收益结论。第五轮后停止C8，转9–13的确定属性/已确认分派路径；不新增第六轮。

## C8 第五轮已保留，转当前 C10/C12 分析

R5 full-M K16 Aprep SHA83c52930，5600行346711B，OJ6acc9ab7 Pass15，C8=36.31µs，对R3 40.16下降9.59%；localoj_like中位36.959999，对R3 40.139999下降7.92%。五轮全部完成，canonical/mirror83c52930、main97df229；不再新增C8轮。五次原样本36.700001/36.959999/37.299999/36.98/36.900002，完整15项在[oj_results.json](.cannbot/optimization_20261012/c8_round5_fullm_prep/oj_results.json)，无跨SHA拼值。

PMU同法比较R3→R5：prepflag12 median16.828→13.158µs，AIV全程MTE2 12.017→8.495、scalar-vectorstall5.529→0，CubeMAC9.077→9.080、MTE1 8.315→8.325接近。支持收益来自准备曝光缩短，不能把全程MTE2唯一归A或sumcounter当总latency；原数据在[pmu_delta.json](.cannbot/optimization_20261012/c8_round5_fullm_prep/pmu_delta.json)。

新的通用私有[oj_like工具](.cannbot/local_oj_like_cases_20261012/README.md)支持明确C10/C12/C13 fixture和normalhostPlan、FP16/BF16实际storage/golden、mixed1/2；C10/C12已实际采到当前source83同五报告。C10 BF16NN localmedian78.580002，realdual36 BM128BN128BK128 Ns5W20/win2/PK384/tree8unused；C12 BF16TN localmedian93.300003，realdual6/p.case12PackedA true BM128BN128BK128 Ns2W20/win1，全golden通过。

C10五PMU显示MAC45.898/MTE254.425/MTE143.200µs、ScalarMTE1stall49.635，B输入请求94,371,840B占108,527,616B的86.96%；AIV主要等Cube。flags4/5含初始/复用/最终排空不能直接当单独瓶颈，L2请求不是HBM流量。依据[当前报告](.cannbot/optimization_20261012/c10_current_analysis/report.md)，准备同mixed一次B nativeZn pack，保持A3D原样、PK/BFIFO/fullmath/FF；新增prep同步及5.898MB读写可能抵消，候选尚无收益结论。C12当前新PMU与AslabB-localND/8Load2D路径分析中；旧Aslab前计数不直接套当前。

## 2026-10-12 当前源码的本地性能分析

使用冻结 R5 SHA `83c52930…` 与 `oj_like` 五次完整 TaskDuration，C10 BF16 NN 为 `[79.080002,78.400002,79.040001,78.120003,78.580002]` µs，中位78.580002；C12 BF16 TN 为 `[93.32,93.300003,93.080002,93.540001,92.919998]` µs，中位93.300003。分别接近同版 OJ 的77.22/93.51 µs。实际 normal MakePlan、DSO、原生输入字节、完整 FP64 golden 与所有默认 PMU 表均绑定同一源码。

C10 当前最终计划 dual36/BM128/BN128/BK128/Ns5/W20/window2/PK384。B 请求字节占86.96%，AIC MTE2 median54.425 µs、MAC45.898 µs，AIV多数等待Cube；这些重叠计数不能相加或当作可直接回收时间。新候选 `70643224…` 将一次 native Zn B准备纳入原mixed task，guard仅将已validated native NN dual36转dual40，保留所有乘加与归约；静态source/resource/address证明已完成，正在编译及实际plan/正确性/性能验证，尚无新OJ结论。

[当前 C10 完整分析](.cannbot/optimization_20261012/c10_current_analysis/report.md)；[C10 候选静态审阅](.cannbot/optimization_20261012/c10_nn_bpack/REVIEW.md)。

### C10 NN Bpack：第一次同源本地验证

`70643224…` 编译和 normal MakePlan dual40/25,051,136 B 实际确认，BF16全输入/FP64完整数学golden通过。五次完整 `oj_like` 为 `[80.459999,79.900002,80.239998,79.940002,79.800003]` µs，中位79.940002，对照冻结R5的78.580002为+1.73%。尚未OJ，未采纳；只用已有默认metrics排查代价，不把静态供给改善当成耗时收益。

### C12 当前瓶颈与旧 B3D 解释更正

冻结R5 actual dual6 Aslab 下，MTE1为1733/core=192×(A1+B8)+5，旧3077/core已失效。Cube busy均61.482 µs、MTE1 58.121、MTE2 57.184、flag12 wait15.854；流水计数重叠，不能相加。Bprep仍输出局部ND，B1仍ND2NZ，B2仍每片8次transposed Load2D。新K16×N1024 native-Zn分组方向保留Aslab和MMAD-before-Free/preload，输入行片段49152→6144、输出store768→3072，整体收益仍需实测。

旧B3D候选 `c111dc4b…` 的normal tree=0，不能沿用“每K先A3D再B3D互相改FMatrix”的旧解释；旧review已添加优先更正，原文副本保留。它本身Pass15但97.74vs96.93无收益，缺少当前plan/PMU绑定。

[完整分析与排重](.cannbot/optimization_20261012/c12_current_analysis/review.md)。

### C13 当前 single-frame 瓶颈分析

R5 actual normal计划dual34/BM512/N64/K128、workers=mTiles=cubeBlocks16，MIX1:1实际16/16；平台20/40是容量。五次完整oj_like `[10.88,10.94,11.08,11.20,11.40]` µs，中位11.08，与同版OJ11.07接近。每Cube两次Mmad完整134,217,728 FLOPs；MAC中位0.672727 µs，MTE2 1.821515、Fixpipe0.814545；AIV vector0.789697、flag0 wait4.245152、SyncAll flag14 wait0.988182，计数不能相加。FP16 NN完整golden五次全通过。

当前NN A源连续（srcDValue=dValue128），不能称为C10的大行间距问题；ND2NZ转换和后续加载仍处于供应依赖中。单AIV尾归约额外vector仅0.122424 µs，PMU不能拆其尾DMA wall时长。已否决normalC和BM416，不重新尝试。新输入表示方向先核公开Load3D的layout/参数；半C交接新增issue可能抵消约0.8µs重叠空间，暂不实施。

[完整五报告分析](.cannbot/optimization_20261012/c13_current_pmu_analysis/pmu_report.md)。

## 2026-10-12 用户控制变量确认

用户补充多轮独立控制变量结果：C4=BF16 TT、C6=BF16 NT、C9=FP16 NT，shape均为performance.txt最新版逆向值且已确认，可通过强制分派捕获。本地这些真实属性的性能分析有较高OJ符合度。这取代旧C4 TN近时推测、C6待确认和C9未隔离的历史结论；普通OJ无变化不能再用来恢复旧属性假设。

### C10 Bpack 普通 OJ 复核

按用户要求将小幅本地退化版本 `70643224…` 仍提交普通OJ。`6accf6d2e7698929279297b9` Pass15、所有precision_ratio1，完整时长 `[1.96,2.59,3.13,4.22,4.78,9.63,6.88,36.84,58.08,80.60,83.81,94.56,11.09,9.93,8.76]` µs。C10 80.60 vs保留R5的77.22无增益，未采纳；同向本地79.940002 vs78.580002退化。不拼接其他case波动最小值；保留R5整体源码/成绩。

### C10 splitFMatrix 在 C8 R5 上融合并保留

`f3f6ab6a…` 是旧已通过的27c01794候选精确重基，11 edits、仅4处模板参数位置适配。旧NNguard/GM/描述符/所有事件/FP32数学原样，反向补丁恢复整份R5；当前SDK19引用/9文件SHA全同。normal plan仍dual36，actual full BF16 golden通过。本地五次 `[76.720001,76.139999,76.220001,76.0,75.580002]` 中位76.139999 vs78.580002(-3.105%)。

`6accf973e76989292794f188` Pass15，C10=76.05 vs77.22(-1.515%)，旧独立候选76.45有同向反馈。保留本版；整版成绩 `[1.95,2.78,3.19,4.00,4.89,9.68,6.74,36.43,57.57,76.05,82.69,93.14,11.48,10.14,8.58]` 如实记录，不拼跨版case最小值。

## 2026-10-13 C12 native Zn 保留（最新源码）

最新保留完整源码为 `486677843608d985caf4406659011f0172214a0812e226c7fcbd5a796f71865e`，普通OJ `6acd021ae7698929279b7ebd` Pass15。C12=91.76 vs93.14(-1.48%)，本地五次median90.459999 vs93.300003(-3.04%)，完整BF16 TN数学与所有golden通过。已融合C10 splitFMatrix与C8 full-M Aprep；本版完整时间 `[1.98,2.58,3.00,4.16,4.66,9.76,6.72,36.91,57.55,77.49,83.39,91.76,10.93,9.91,8.46]` 如实记录，不拼跨版本最小值。

C12仍normaldual6/原完整GM分区，只在资源完整guard通过后 `Case12K16GroupZn` → `bmmms_manual_case12_packed<BF16,true,false,…,PACK_A=true,PACK_B_ZN=true>`；B K16×N1024 nativeZn，A Aslab、fullK/two-C/FP32归约保留。

用户最新要求优先较大收益方向，暂缓未编译的C9 constantSchedule，优先分析C12准备/计算重叠及C13 raw输入表示。

### C9 新常量化候选暂缓

私有 `1b152870…` static Schedule候选已完成：20字段恒等常量、actualnormal25与资源完整guard、99反例、defaultfalse/true数学body不变，尚未build/NPU/OJ。用户要求优先幅度较大方向，暂缓该小发射成本探索，转向C12准备与计算重叠及C13raw输入表示。旧NT配置缓存751595da原机制收益不明确，未重新提交。

## 2026-10-13 新设备核对与 C13 raw normal 否决

重启后logical0→physical4、card2/chip0；ACL实际SoC `Ascend910_9362`，SDK ShortSoC `Ascend910_93`，正常plan资源20AIC/40AIV。用户允许以保留版性能相符作为配置正确标准。冻结486的C13 FP16NN在device4五样本 `[11.220224,11.140223,11.340227,10.620213,10.600212]` µs，中位11.140223，对同源OJ10.93仅+1.92%，按该标准接受资源。

raw normal7c39a102同device/同shape/fullgolden通过，但五样本 `[13.52027,13.880278,13.700274,14.320287,14.660294]` 中位13.880278，较11.140223退化24.6%，否决且不OJ。不能用该候选退化推断资源错误，也不要再次提交同raw表示。新大幅方向保留C^T/ND2NZ/原native2D，并对两M256半帧实现输入/计算/Fix/归约流水；静态准备中。C9常量化按用户要求暂缓。

## 2026-10-13 C12 phased Bprep 保留

`bbdce7cd…` 当前保留。普通OJ `6acdaf1fe7698929270f9253` Pass15，所有precision_ratio1，完整时长 `[1.94,2.54,3.21,4.06,4.86,9.48,7.08,36.11,56.73,75.75,82.19,88.63,11.34,10.05,8.46]` µs。C12 88.63vs91.76(-3.41%)，same-device4 localmedian88.741776vs91.721832(-3.25%)，true分支mangle已核。

仅当原Case12K16GroupZn加current single-task Ns2/Nt32/W20完整guard满足：PHASED_B=true先完整A、B ng0/2，Sync14后12+初始free4/5；ng1/3 Sync14+13后原consumer；Cube在begin+8首B读之前仅一次等13。Source所有A/B/完整K/FP32归约、GMslots/offset保持。公开TQue生命周期证明允许跨phase FreeAllEvent后lazy event重新分配；本地/15case OJ均已验证。未推进新的C8轮次。


## 2026-10-13 C13 半块流水：用户完整 OJ 反馈

用户提交冻结组合源 `486d4a88…`，15项均Pass、显示误差0.00%。C13=9.24 µs，相比前一完整源11.34 µs减少18.52%；此前通常约11 µs。保留native C^T布局，将M512拆为两段M256，第一段Fix/归约与第二段MAC重叠；全部K128和N64保留。C12 phase完整body逐字保留；C12本次89.74 µs，前次88.63 µs，属于未改路径的单次差异。

完整15项（µs）：`2.12, 2.76, 3.24, 4.18, 4.64, 9.5, 6.89, 36.54, 57.32, 76.45, 83.14, 89.74, 9.24, 9.79, 8.44`。submission ID尚未提供；身份依据是用户指明的精确文件。主代理不重复提交该源码。本地结果另记，不能把原baseline测量当作候选测量。

C13同源码本地验证完成：五次oj_like `[9.180183,8.860177,8.700174,9.200184,8.900178]`，中位8.900178 µs；device4原486基准11.140223 µs，-20.11%。实际true分支、4MMAD/核、完整payload与全部golden通过。新分析见[报告](.cannbot/optimization_20261013/c13_half_pipeline/on_c12_phase/actual_analysis/review.md)。


## 2026-10-13 C12 direct raw A：完整 OJ 验收

组合源b8817327，OJ `6acdd94de76989292739d40b` 全15Pass、precision_ratio均1。完整用时：`1.9, 2.51, 3.16, 4.08, 4.76, 9.58, 6.89, 36.45, 57.35, 76.33, 82.55, 87.93, 9.11, 9.88, 8.65` µs。C12=87.93，前一phase-only CLI88.63（-0.79%）、用户C13组合版89.74（-2.02%）；同device4 local88.161766对88.741776（-0.65%）。保留有限收益，不宣称大幅提速。实际captured true分支/完整192MMAD每核，原B、C与归约不变；MTE2多11指令，与额外raw slabs DMA一致。C13true body逐字保留，9.11 µs。当前source350604B/5600行已普通OJ接受。


## 2026-10-13 C9 相邻N共享A：本地排除

同device4当前保留b881中位57.461151µs，OI57.35相符。FP16 NT共享A两版实际捕获且全golden通过，V1中位61.541229（+7.10%）、V2中位62.361248（+8.53%）。MTE1指令389→269、busy下降约5.3µs但整体生产端变慢；恢复B预取/Fix分组无效。不保留、不提交OJ，原C9 dispatch保持。全部证据在c9_nt_pair_stream及v2。
