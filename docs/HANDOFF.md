# 接手状态 · 2026-10-02

## 当前：宽N结构候选正式15/15，C14 10.93μs

分支 `experiment/c14-manual-frame`，实现 `8e6959b`，kernel SHA `b0e0b66495df9606156f73f1d4a1399801ab18f203ff0f9458a7051caca4150f`，340070bytes。首任务host-only std::min编译错误已仅三元运算修复；修复任务 `6abea479694b590c3c1e1f2d` Pass，CANN编译成功、15/15、precision_ratio全1。C14 10.93μs，最新通过父四次12.72–13.26、中位13.04，低于最快父14.1%、低于中位16.2%，超出观察波动4.1%；仅单次收益，无同机交错A/B和actualshape/plan/SoC/profile，不称稳定因果百分比。C7 7.78在旧四次7.67–8.04范围内，其它路线源码未改不归因。

原GM/plan/grid/flags0/4/完整K→MaxN→SumM保持。205行结构候选与模型/native限制和15点结果见 `docs/WIDE_N_MANUAL_FRAME.md`；原JSON忽略 `artifacts/wide-n-manual-frame/official-fixed.json`。下一原样确认一次较大收益、存ID查询终态，不扫附近参数。main/历史标签不动，整体冲榜尚未完成；C7四次重复资料在 `experiment/c7-identical-repeats`。没有活动任务。

## 最新指令：同一通过源码再复测两次

用户要求原样再提交两次。当前宽N任务 `6abea08e694b590c3c1c90f5` 已终态Compile Error（设备kernel第2765行调用host-only std::min），无性能结果。该候选保留本分支、不在复测中修代码。复测采用最近通过的C7实现 `c17077f` / SHA `45234d7945b6013cc75d2e6c3092c911c9c8ecd5618b82a7c51fd7d9084e0c61`，在独立分支保存两次新任务，不能把旧两次历史复测当本次任务。宽N后续需要替换设备std::min后再独立验证；当前没有活动任务。失败原JSON Git忽略 `artifacts/wide-n-manual-frame/compile-error.json`。

## 当前：宽N手动frame + 跨Nt B预取 + 批量末级Max候选

分支 `experiment/c14-manual-frame`，父 `124658d`，kernel SHA `a52b0436a89ac9d1558760efce3a80715d3cb79bb54f81d0d51175e66bdd4cc1`，340024bytes。仅kernel新增204行/三个区域，删除即逐字恢复父所有源码；MakePlan/grid/原partial与单双Nt宽GM窗口、ready0/free4、其它路线保持。双B1真正预取Nt+2（原FULL_A的BK=K没有跨Nt预取），C0两tile独立释放，32byte入口取消TPL，Vector有效N fold与两个原UB槽，SyncAll后复用C区、Nsplit批量树形Max→有效M Sum。16分片MP64的末级Max API15→4，不作为速度预测。
434延迟MTE2/MTE1/MMAD/Fixpipe真实producer、729真实AIV/三引擎/全AIV线程barrier、四Cube/八Vector负控制、production/TUNING各4800 host/600选择，整数CPU不是BF16/native硬件证明。API900静态正文已取到，确认无workspace硬同步和batchmode；内部安装9.0 header未取得，无TPL native行为仍待正式编译/运行。文档详见 `docs/WIDE_N_MANUAL_FRAME.md`。
下一：全CPU最终SHA完成，官方独立模板仅换kernel/其它8文件一致、dry-run核SHA，commit/push后一次提交存ID查询终态；不能观察超时重交。父C14 13.15/13.26及历史同代码12.61–13.38为参考，C7约7.9–8.0保持；若小于波动差距不叫突破。CANN9/NPU精度/时间PENDING；正式任务 **`6abea08e694b590c3c1c90f5`** 已创建，代码 `d57fddf` 已push；下一只查询同ID至终态，不重交。原通过C7分支保留，main/标签不动；无新GM通路，未混入旧失败ragged覆盖或near-tile扫描。

## 最新通过父版：C7两次8.00/7.88 μs，均15/15

当前 `experiment/c7-manual-frame`，实现 `c17077f`，kernel SHA `45234d7945b6013cc75d2e6c3092c911c9c8ecd5618b82a7c51fd7d9084e0c61`，329378bytes；首测 `6abe9804694b590c3c18f362`、原样确认 `6abe98e5694b590c3c195fc5` 均Pass、CANN编译成功、15/15，precision_ratio全1。
确认μs `[1.99,2.49,3.08,4.04,5.28,9.73,7.88,50.72,67.77,98.46,88.48,96.56,16.04,13.26,9.55]`。C7两次8.00/7.88、中位7.94；父同SHA三次9.59–10.28、中位10.14；候选均低于父样本区间，中位耗时低21.7%、最慢候选比最快父低16.6%。无实际同机交错A/B/actualshape/plan/SoC/profile，不能保证因果百分比或算榜分；其它路径未改不归因。CPU/负控制/源码范围与两个终态完整见 `docs/C7_MANUAL_FRAME.md`；原JSON忽略 `artifacts/c7-manual-frame/`。没有活动任务，main/历史标签不动。整体极限性能目标仍未完成。
下一具体动作：从当前通过版独立 `experiment/c14-manual-frame`。源码 `MakePlan` 的 short-M/wide-N BF16路径已dual21、完整A留L0A，不能重做A驻留。`bmmms_manual<...,FULL_A=true>` 仍TPipe/两份placeholderA queue、单份B2/一个两Ntile C0/一个两Ntile GM窗口；Vector终态SyncAll后block0用 `for(ns=1;ns<nSplit;++ns) Max+PipeBarrier` 串行归并。历史64行/8192列/20核代理nSplit16，归并15个API可按连续两半向量repeat折叠成4个API；须仍Max(N)后Sum(M)，不重分M/N任务、不增加GM。先对比历史FULL_A试验，建立实际producer/Vector/末级跨线程模型，再选择“紧凑manual frame + 分片并行归并”这个结构假设。C7已通过不要回退/混未验证。
同步API研究：900官方SyncAll网页正文通过web未能读取，只能导航壳；9.1或PTO源码不能冒充9.0 header。下一要核实际9.0 SyncAll硬同步是否依赖TPipe、flag保留槽；当前未确认，无C14代码。现有900入口 `https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0204.html`；PTO官方文档是硬件barrier比较资料，未从其拷实现/未增加依赖。不能用当前核数/shape注释冒充真正case profile。

## 最新：手动C7入口正式15/15通过，C7 8.00 μs

分支 `experiment/c7-manual-frame`，实现 `c17077f`，kernel SHA `45234d7945b6013cc75d2e6c3092c911c9c8ecd5618b82a7c51fd7d9084e0c61`，329378bytes。正式任务 **`6abe9804694b590c3c18f362` Pass，CANN编译成功、15/15，precision_ratio全1**，μs `[1.99,2.48,3.16,4.01,5.46,9.96,8.00,50.67,67.89,98.21,88.06,96.43,15.76,13.15,9.81]`。
C7 8.00，比父同SHA三次最快9.59低16.6%、比中位10.14低21.1%，超过观察范围9.59–10.28和极差6.8%；可保留单次较大结构收益，但没有同机A/B/actualshape/plan/SoC/profile，不称稳定因果百分比。其它路线未改，不归因各自波动。CPU/实际实现与限制详见 `docs/C7_MANUAL_FRAME.md`。
下一原样确认一次本较大收益，commit/push后提交存ID查终态；不是继续两次已完成的父版重复，也不是N参数扫描。若回到父波动带如实记录。原始JSON忽略 `artifacts/c7-manual-frame/official.json`。原通过组合和main/标签保持；原样确认任务 **`6abe98e5694b590c3c195fc5`** 已创建；下一 `python3 /private/tmp/query_bmmms_submission.py 6abe98e5694b590c3c195fc5` 只查该ID至终态，不重交。

## 当前：C7完整输入 + 手动物理frame候选

分支 `experiment/c7-manual-frame`，父 `0fe38f0`，kernel SHA `45234d7945b6013cc75d2e6c3092c911c9c8ecd5618b82a7c51fd7d9084e0c61`。仅kernel新增173行：32byte独立入口、资源选择、launch override，原host plan/GM/grid/其它路径逐字保持。旧full-input/lean两次没有明显收益，本次结合队友manual LocalTensor，移除本路线TPipe/TBuf/事件分配，并保留原全输入/全A2/单B2 N slab/双C0和精确N树Max→有效M Sum。不扫描N参数、不重做失败窄N驻留，无新GM。
264立即/264延迟live MMAD、1296三引擎Vector、production/TUNING各6144 host/768选择、硬事件/尾部/信用负控制见 `docs/C7_MANUAL_FRAME.md`，用整数CPU模型，不是native半精度或硬件速度证据。CANN9/NPU精度/性能PENDING；代码 `c17077f` 已push，正式任务 **`6abe9804694b590c3c18f362`** 已创建，下一只查询同一ID至终态，不重交。
下一：最终CPU/负控制完成，独立官方模板仅换kernel并核其它8文件，dry-run、commit/push后一次提交、即存ID查终态。父C7同SHA三次9.59–10.28、中位10.14 μs，候选若落同波动区间不称大突破；无actual shape/SoC/plan/profile，不归因其它路径波动。小矩阵泛化方向经源码比较可能主要增加覆盖，暂让位于这个比赛性能假设；原通过分支及main/标签不动。

## 当前：同一kernel两次复测已完成，三次均15/15通过

用户要求“一模一样再交两次”，已严格完成两次，未额外创建其它任务。首次 `6abe860d694b590c3c0f02a5`、复测1 `6abe87e6694b590c3c102b8c`、复测2 `6abe88a7694b590c3c109c3a`，均Pass、CANN编译成功、15/15、precision_ratio全1。kernel全程不动，实现 `889afe0`，SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597bytes；独立模板和每次提交文本一致，按前一个任务终态后才提交下一个。

| Case | 首次 μs | 复测1 μs | 复测2 μs | 中位数 μs | min–max μs | 极差/中位数 |
|---|---:|---:|---:|---:|---:|---:|
| C1 | 1.97 | 1.90 | 1.98 | 1.97 | 1.90–1.98 | 4.1% |
| C2 | 2.39 | 2.46 | 2.56 | 2.46 | 2.39–2.56 | 6.9% |
| C3 | 3.12 | 3.18 | 3.21 | 3.18 | 3.12–3.21 | 2.8% |
| C4 | 4.04 | 4.04 | 4.04 | 4.04 | 4.04–4.04 | 0.0% |
| C5 | 5.28 | 5.31 | 5.19 | 5.28 | 5.19–5.31 | 2.3% |
| C6 | 9.85 | 9.72 | 9.46 | 9.72 | 9.46–9.85 | 4.0% |
| C7 | 9.59 | 10.28 | 10.14 | 10.14 | 9.59–10.28 | 6.8% |
| C8 | 49.78 | 49.59 | 50.26 | 49.78 | 49.59–50.26 | 1.3% |
| C9 | 67.51 | 67.60 | 68.27 | 67.60 | 67.51–68.27 | 1.1% |
| C10 | 97.43 | 98.18 | 99.33 | 98.18 | 97.43–99.33 | 1.9% |
| C11 | 86.97 | 88.17 | 88.85 | 88.17 | 86.97–88.85 | 2.1% |
| C12 | 95.62 | 96.84 | 96.62 | 96.62 | 95.62–96.84 | 1.3% |
| C13 | 14.76 | 15.48 | 15.76 | 15.48 | 14.76–15.76 | 6.5% |
| C14 | 12.61 | 13.33 | 13.38 | 13.33 | 12.61–13.38 | 5.8% |
| C15 | 9.34 | 9.42 | 9.13 | 9.34 | 9.13–9.42 | 3.1% |

波动指标定义为 `(max-min)/median`，不是置信区间、变异系数或稳定误差界。C2 6.9%、C7 6.8%、C13 6.5%、C14 5.8%，说明几%的单次差异不能直接当算法收益。C3中位3.18、范围3.12–3.21；C6中位9.72、范围9.46–9.85；C15中位9.34、范围9.13–9.42。
C3/C6的新版本三次均低于更早组合 `6abe7b90694b590c3c08ed48` 的单次3.66/10.75，但旧版未同样复测且没有实际同机shape/plan/SoC/profile元数据，不把具体百分比称为稳定或因果收益；三次也不足以界定总体分布。C5与父tiny分组版5.34、队友原版5.21的单次微小差距均不构成可靠新收益。C7/C13/C14及其它不相关路径未改，其变化不归因。
全部资料推送当前 `experiment/teammate-single-tile`，main/历史标签不动。原JSON分别忽略 `artifacts/teammate-single-tile/official.json`、`repeat1.json`、`repeat2.json`；摘要见 `docs/SINGLE_TILE_REPEATS.md`。没有活动任务，kernel保持通过版。
下一可执行动作：继续当前源码与 `git show 9ab2312:kernel.asc` 的资源化small-tile覆盖审查，按此前执行单先验证 `previousSmall/expandedSmall/SmallFullTileFits/dual23` 的容量、repeat、batch ownership和同步。不继续原样重交；若之后要精确量化某算法收益，需旧版与新版交错重复A/B和实际设备元数据。小矩阵泛化尚未实现/未提交。

## 当前：同一kernel原样复测两次，第一次任务已创建

用户要求最新通过版一模一样再交两次。kernel保持 `889afe0` / SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597byte；独立提交模板仍仅kernel，dry-run匹配。按顺序执行，第一次 **`6abe87e6694b590c3c102b8c`** 已创建，第二次尚未提交。
下一：`python3 /private/tmp/query_bmmms_submission.py 6abe87e6694b590c3c102b8c` 查询同任务至终态，再原样创建第二次并立刻保存ID，查至终态。与首次任务 `6abe860d694b590c3c0f02a5` 的15点一起列三次耗时、中位数、min/max及极差/中位数；不额外提交其它候选、不改kernel、不将同版本波动当优化收益。没有实际同机元数据，重复正式任务不等价受控同机A/B。小矩阵Cube泛化工作等这两次复测完成再继续。

## 最新通过组合：tiny容量/batch分组 + 队友single_tile，15/15通过

当前 `experiment/teammate-single-tile`，实现 `889afe0`，kernel SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597byte。正式任务 **`6abe860d694b590c3c0f02a5` Pass，CANN编译成功、15/15、precision_ratio全1**。μs `[1.97,2.39,3.12,4.04,5.28,9.85,9.59,49.78,67.51,97.43,86.97,95.62,14.76,12.61,9.34]`。
本实验父tiny分组版C6 10.72→9.85，单次降低8.1%；C5 5.34→5.28，仅小幅；C3 3.06→3.12略退，不能忽略。两次学习合计对更早组合 `d5cd4af`：C3 3.66→3.12（单次14.8%），C6 10.75→9.85（单次8.4%）。队友原版C3/C5/C6 3.14/5.21/9.73，与当前相近；当前C15 9.34保留原组合相对原版12.53的优势，但C15本实验源码未改，不归因变化。
C2 2.39、C8 49.78/C9 67.51及其它未改路径的变化不称本实验收益。没有实际shape/plan/SoC/profile或重复同机A/B，不保证稳定幅度、路径命中或推算榜单分数。全部改动仅kernel，独立原模板其它8文件不变；原始JSON/CPU日志Git忽略 `artifacts/teammate-single-tile/`。
6864实际Vector/1280实际物理Cube模型及四负控制通过；模型同步Vector/MMAD/Fixpipe、MTE2可延迟，整数转换不模拟FP16/BF16编码，跨核ready抽象。实际设备编译/15点精度通过单独报告。父tiny分组 `f7c2c74` 和更早组合/队友原版分支保持，main和历史标签不动；当前工作区干净，没有活动正式任务。
下一可执行动作：`git switch -c experiment/small-tile-coverage`，对照 `git show 9ab2312:kernel.asc` 的 `previousSmall/expandedSmall/SmallFullTileFits/dual23` 与当前 `ClassifyMeasured`：目前完整batch Cube仍只覆盖历史三个桶，队友泛化到资源允许的全部小矩阵，并通过round-robin处理B>AIC。先审核UB/L1/L0和repeat/mask限制、实际队列/唯一writer，再决定移植；不能直接粘整个host、重交相邻参数或丢当前tiny/C15。这个泛化目前**尚未实现/未提交**，C9窗口WIP仍独立归档。

## 当前：队友single_tile缓冲/同步/直接输出移植候选

`experiment/teammate-single-tile`，父15/15 tiny通过版 `f7c2c74`，kernel SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597bytes。kernel+165/-91，仅原版两single_tile设备实现、其context/lane-fold helper及FF/TT对应入口；没有混入队友扩大Cube分类/dual23或其它内核。MakePlan/workspace/tiny/C8/C9/C15代码保持。普通single_tile的一个AIV完成有效M Sum→4byte y，伴随AIV只消费完成flag；NT direct_batch手动L1/L0/UB、0/1 A/B就绪、A先Load、精确N lane-fold和PIPE_ALL结束，不重复TPipe 初始化/partial merge。代码按队友原版移植，不声称本Agent新算法。
6864实际Vector执行与1280实际Cube生产者通过；4布局、K8/M/N尾、物理NZ/ZZ/ZN、有界片上内存区间、每个有效C独立点积核对、负数及唯一合法y。污染无效N、缺PIPE_ALL、缺A/B等待四负控制检出。完整kernel等于对父明确移植变换，其它路径保持；重现 `python3 tools/validate_teammate_single_tile.py`。
CPU输入为整数值，不是FP16/BF16编码；Vector操作同步、Cube仅MTE2可延迟，MMAD/Fixpipe同步。跨核ready抽象，不能证明全硬件流水、误差或性能。模型首次补全未实例化branch API声明、修正预期offset的C++窄化及registry内GM子指针相对基址；没改正式测试/依赖来通过。
CANN9编译/正式15点/性能PENDING。原日志忽略 `artifacts/teammate-single-tile/`；下一仅官方原模板换kernel、dry-run、commit/push、一次提交存ID并查终态。重点父C5 5.34/C6 10.72，同时C3 3.06/C15 9.47。队友原版C5 5.21/C6 9.73不是重复同机A/B，不能推断隐藏路线或稳定差异。main/历史标签不动。

## 最新：tiny容量准入/batch分组正式15/15通过，C3 3.06μs

`experiment/tiny-batch-coverage`，实现 `03e352b`，kernel SHA `e662891f722c132b93f9b3a6ab31514217c38fdf7e2221715bc138e0d01d0726`，317894byte。正式任务 **`6abe82b1694b590c3c0cf647` Pass，CANN编译成功、15/15、precision_ratio全1**。μs `[2.01,2.75,3.06,4.04,5.34,10.72,10.00,49.86,68.03,98.51,88.17,96.71,15.62,13.26,9.47]`。
C3组合父3.66→3.06，单次降低16.4%；队友原版3.14。C15 9.47、C8 49.86/C9 68.03相应源码未改，不归因波动。C2 2.63→2.75，单次有退化，不掩盖；没有实际shape/plan/SoC/profile/重复A/B，不能证明稳定幅度或确切路径。通过源/完整模型和证据保留，不合main。
下一从本通过版新分支学习队友single_tile和direct_batch：队友FF/TT单tile的Vector取消SyncAll和partial merge；NT手动L1/L0/UB取消TPipe初始化、A/B独立就绪、完整padded C DMA和lane-fold后一次树Max。不要混入更广Cube准入/其它manual或未验证C9窗口。原始结果忽略 `artifacts/tiny-batch-coverage/official.json`，没有活动正式任务。

## 当前：队友tiny按UB准入和独立batch分组候选

分支 `experiment/tiny-batch-coverage`，父通过组合 `d5cd4af`，kernel SHA `e662891f722c132b93f9b3a6ab31514217c38fdf7e2221715bc138e0d01d0726`，317894bytes。只移植队友TinyVectorFits/TinyVectorBatchGroup/dual24分派，B<=8/M<=8/N<=64/K32..64按实际UB准入；完整tiny且B>1时每AIV一个batch，其余容量允许时按最大有效batch组分派。与队友重复两套大body不同，单核/分组复用同一个inline计算体，原数学/归约/手动事件/DMA逐字保持。补K合法性和强制dual24/group资源验证。
9344实际分组动态/特化、2344单核/父对照、9344空闲block，4layouts、末组尾块、负数、UB/mask/DMA/唯一y通过；production/TUNING各20736真实classifier、1752零scratch分组plan、508单核frame，双负控制检出。模型用整数模拟转换，不是FP16/BF16编码或完整异步硬件时序。整个kernel等于对父版的明确变换，C5/C6/C8/C9/C15其它代码与workspace保持。
`python3 tools/validate_tiny_batch_coverage.py` 复现；原日志 `artifacts/tiny-batch-coverage/cpu.log` 忽略。模型首次补充父tiler已有stepKa/Kb字段，并修正B1无需分组的断言，未改正式测试/依赖。CANN9编译/NPU精度/性能PENDING。
下一独立官方原模板仅替换kernel、dry-run核SHA，commit/push后一次正式提交，立刻保存ID并查终态。对照通过组合任务 `6abe7b90694b590c3c08ed48` 和队友原版 `6abe7f04694b590c3c0ade30`（原版C3 3.14 vs组合3.66）；不要据编号推断实际shape/plan。C5/6发现队友FF走single_tile、当前FF历史桶走direct_batch，以及BF16 NT分派放宽；继续单独研究，未实现/未提交。main/历史标签不动。

## 当前通过版：队友tiny核心与TT/C9组合，15/15通过

`experiment/teammate-tiny-dot`，实现 `0beb87d`，kernel SHA `7d629cfb0bb821fa8be65cfbb7164f72486f8845882fd974b86aa326cd1168e3`。正式任务 **`6abe7b90694b590c3c08ed48` Pass，CANN编译成功、15/15、precision_ratio全1**。耗时μs `[1.98,2.63,3.66,4.13,5.70,10.75,10.25,50.72,68.02,99.81,89.21,97.18,16.30,13.44,9.64]`。
父C1..4 2.15/3.97/4.30/5.60；本次C2降低33.8%、C3降低14.9%、C4降低26.25%，均单次正式测量，不证明稳定收益。C8/C9源码保持，50.72/68.02变化不归因；没有实际shape/plan/SoC/profile。原始资料 `artifacts/teammate-tiny-dot/official.json` Git忽略。
用户要求直接测队友原版，下一独立 `experiment/teammate-tiny-original` 保存原文件逐字快照，仅官方原模板替换kernel，CLI提交、保存ID、查询终态，然后与本版逐case对比。当前通过组合保留，不混入C9 WIP，不移main/历史标签。

## 当前候选：队友tiny_dot与通过TT/C9组合，正式任务已创建

当前 `experiment/teammate-tiny-dot`，kernel SHA `7d629cfb0bb821fa8be65cfbb7164f72486f8845882fd974b86aa326cd1168e3`，313296byte。以 `e1b3634` 通过kernel为父，提取用户新 `kernel_tiny_dot.asc` short-dot合并Cast/对齐DMA、单核tiny紧凑参数/手动UB/常量K/稀疏行Sum、K65..256独立batch Vector；保留父整个MakePlan、原GM和C8/C9，TUNING显式pins仍生效。来源SHA `72454276ca665e0dd80d2bea6d972a34270442cad8fd3ccf0bd2a6674d4323e7`；截图不能代替该候选正式结果。详情 [TEAMMATE_TINY_DOT.md](TEAMMATE_TINY_DOT.md)。C9窗口WIP仅归档 `8a69048`，未混入。
CPU3600实际tiny动态/特化/父对照、5040实际容量允许的小K256、90short-dot及guards/negatives/四layout/typed UB/Gather/延迟DMA通过；production/TUNING各161280实际selector控制/18640选择，缺输出completion/稀疏Sum身份负控制通过。剥除移植块及对应launch适配后整个kernel逐字恢复 `e1b3634`。模型不是FP16/BF16设备编码/完整异步协议/性能证明。实现 `0beb87d` 已commit/push；独立原模板dry-run only-kernel、313296byte/SHA一致。正式提交 **`6abe7b90694b590c3c08ed48`** 已创建，CANN编译/15点精度/性能PENDING。
下一条：`python3 /private/tmp/query_bmmms_submission.py 6abe7b90694b590c3c08ed48`，只查询同一ID到终态，不重交。对照父C1..4 2.15/3.97/4.30/5.60、C8 49.38/C9 67.48μs；未改路径波动不归因。原始资料Git忽略 `artifacts/teammate-tiny-dot/`；main和历史标签不动，整体重大目标仍需证据。

## 新队友tiny_dot输入，C9消费WIP独立保存

用户提供 `2026-10/kernel_tiny_dot.asc`，5455行、CRLF，SHA `72454276ca665e0dd80d2bea6d972a34270442cad8fd3ccf0bd2a6674d4323e7`，截图前几项更快；截图未给kernel SHA/正式ID，需合并后独立正式验证。优先提取tiny/short-dot/K65..256小矩阵原生Vector逻辑，保留已有TT49.38+C9约68组合，不整份覆盖其它大矩阵分支。
C9消费WIP已在 `experiment/c9-window-review` 增加两个helper和唯一调用（kernel+56/-27）：两现有C queue预读，最后GM读取后PIPE_MTE2归还原2/3信用，保留原Vector运算和全部producer/host/UB/grid/其它代码。剥除helper并恢复旧loop后整个kernel逐字等于 `1d7fd08`。**实际源码CPU同步模型、CANN9编译、NPU精度和性能全部PENDING，未提交，不能混入通过代码。** 下一tiny实验从原 `e1b3634` kernel开始，C9 WIP在此分支保存供后续接替，不丢改动。

## 当前工作起点：恢复49.38μs TT与队友C9组合，准备审查C9消费window

当前分支 `experiment/c9-window-review`，kernel从 `e1b3634` **逐字恢复**，SHA `8c03d710d5394a0660e6bedc4c172f7784a1cbe3ef9f1cbc450f231aa1d6a052`。恢复的是正式任务 `6abe3059694b590c3cdf6c87` 15/15通过的代码，历史单次C8 49.38/C9 67.48μs；恢复后没有再次提交，不称本轮实测。C7两候选分别保留 `d793083` 和 `75c4d8f`，源码/实际模型/正式结果均已push；新单C消费正式C7 9.55，对照9.40，无新增收益，不合当前kernel。无活动正式任务，main/历史标签未动。
下一可执行动作：读 `bmmms_case9_packages` 的Vector window loop和 `docs/DUAL_CONSUMER_OPTIMIZATION.md`、`tools/validate_dual_pipeline.py`。当前手写C9仍serial Copy→Reduce→下一tile，完成全窗口V才还2/3信用；旧预取/早信用/fold无收益组合仅库dual1/2且含flag9。先对当前C9无库flag9协议设计两C queue预读/最后GM读后早release的**独立源码三引擎模型**：两AIV顺序、0行、window 1..8、N/M尾、queue在V读完后才重分配、信用后destructive GM覆盖和唯一partial写。保留原ReduceMax/Max指令、host/grid/UB预算/producer/C8，不混fold或微调参数。仅模型证实且能区分旧实验时才实现；这个C9新消费尚未实现/未提交，没有性能结论。整体重大优化目标仍有空间。

## 最新：C7专用单C缓冲Vector正式15/15通过，无新增收益，归档

归档 `experiment/c7-lean-vector` 从 `d793083` 开始，kernel SHA `0fa24fce76929aee569311905518ee963be5097e7589161a6c525f1996eb6b05`。仅dual34专用Vector helper/调用：空闲AIV只归还原mode2 credits，活动AIV单C TBuf、行Max→直接WholeReduceSum→唯一4byte y写；显式V→MTE2/MTE2→V/V→MTE3/MTE3→V保护单UB和sum。Cube/host/launch/grid/原GM/workspace/C8/C9整个旧源码逐字保持，父正式15/15 C7 9.40μs；最佳TT+C9组合 `e1b3634` 不动。
1296实际helper CPU组合通过，三种独立引擎顺序、live generation、destructive GM复用、负数/N尾、cyclic batch/idle AIV、唯一y/guards及信用配平；缺四个Fence、N尾无mask、早信用六个负控制全部检出。模型合成Cube与另一AIV，不代替完整硬件调度/舍入/性能。详见 [C7_LEAN_VECTOR.md](C7_LEAN_VECTOR.md)。实现 `a3696cd` 已commit/push；独立原模板dry-run仅kernel、306655byte/SHA一致。正式任务 **`6abe6705694b590c3cfd63c9` Pass，CANN编译成功、15/15、precision_ratio全1**；C7父9.40→9.55μs，无新增收益。C8/C9未改，不归因49.74/67.73波动；没有actual shape/plan/SoC/profile或重复A/B。
无活动任务；归档候选，不合main、不扫描相邻参数。下一恢复 `e1b3634` 原C9约68μs+TT49.38μs组合，再审查C9手写N window消费：现有两C queue仍serial Copy→Reduce→下一tile，到全窗口Vector结束才还2/3 credit。与旧dual-consumer-overlap仅库dual1/2+flag9/fold不同；只评估同两buffer DMA/V重叠及最后GM读后信用，不混入fold/矩阵乘/参数扫描，先实际源码三引擎模型证明早credit与UB生命周期。新C9消费尚未实现。原资料Git忽略 `artifacts/c7-lean-vector/`。整体重大优化目标尚未完成。

## 最新：C7完整输入/完整A2驻留正式15/15通过，尚未形成明显收益

当前 `experiment/c7-full-inputs` 从 `fd72a34` 开始，kernel SHA `e8a1512e88e3cc71069d501b9cb934917ac2717cde772f83a9f6fad0daf7f6bb`，303787bytes。仅C7历史TF/FP16小矩阵新dual34：完整A/B一次ND2NZ到L1，完整A一次Load3D驻留L0A，按N切片在B2/原C0做完整K MMAD；复用原direct-batch Vector、原ring/credits/grid/workspace，无新GM/Schedule字段。C8/C9保持，父正式C7 9.68/C8 49.38/C9 67.48μs。
86立即+86延迟live MMAD producer、2592实际全M/零行消费者、缺last-reader wait负控制通过；fake及固定公开8.3 tiler production/TUNING各3456/432通过。旧整个kernel剥除改动后逐字恢复。代码 `2dc7f30` 已commit/push，正式任务 **`6abe5f1e694b590c3cf8ca02` Pass，CANN编译成功、15/15、precision_ratio全1**。C7 9.40μs（父9.68，单次约2.9%），C8 50.15/C9 67.59，后两点源码未改，不归因波动。细节 [C7_FULL_INPUTS.md](C7_FULL_INPUTS.md)。
没有活动任务。该候选未形成明显收益，保留通过代码和证据，不合main、不作为新增重大突破；原最优组合 `e1b3634` 不动。下一独立分支以此通过结构研究C7专用Vector消费：当前闲AIV也初始化两份C queue、MQ、scratch；活动AIV重复维护只有一个N tile的Max状态。评估空闲AIV只处理原credits、活动AIV一个C TBuf+行归约直接写y，必须证明V→MTE2的单UB复用依赖、MTE2 copy完成后才还GM credit、MTE3完成后才重用sum及唯一y writer。新消费器尚未实现，不扫N切片/双B2参数。上述TSCM方向已因CANN9实际UB→GM→L1排除。原始资料Git忽略 `artifacts/c7-full-inputs/`。main/历史标签未动，整体重大目标仍有空间。

## 当前工作起点：恢复49.38μs组合，保留队友C9

当前分支 `experiment/tt-l1-input-review`，kernel已从 `e1b3634` 逐字恢复，SHA `8c03d710d5394a0660e6bedc4c172f7784a1cbe3ef9f1cbc450f231aa1d6a052`。这是任务 `6abe3059694b590c3cdf6c87` 15/15通过的代码（C8 49.38/C9 67.48μs）；恢复后没有再次提交，不把历史时间称为本轮实测。
NZ候选源码/模型/结果保留并推送在 `experiment/tt-native-nz-ring` / `f4498bf`（C8 50.44μs），没有活动正式任务，不合入当前kernel。`validate_tt_native_nz.py` 只对归档候选适用，不用于证明恢复版。
下一条具体动作：读取官方CANN9/A2-A3共享L1/TSCM与UB→L1样例，核对双AIV对AIC的地址/队列所有权及同步规则，评估Vector准备B NZ后直接供Cube读取是否可行。此方向尚未研究或实现；不编造API/地址，不新增GM输入通路，不重复B包参数/旧NZ输出或N pair候选。先有可核对契约和实际源码模型，再决定是否值得实现及正式提交。main/历史标签未动，整体重大目标仍有空间。

## 最新：手写TT原生NZ ring正式15/15通过，未观察到新增收益

分支 `experiment/tt-native-nz-ring` 从通过 `e1b3634` 开始，kernel SHA `30a697cc03f6aa3ec39f81275ddcfa27f10aaf4f1d31e0cd4bcbfc51bf6ce233`。保留A1/B包流水/host/Vector末级/C9，仅Cube基本CFG_NZ写原ring和AIV slab DMA/tree Max；固定BM×16 FP32 block的32byte stride2BM，尾N置-inf，原credits/GM/预算保持。区别旧Matmul内建NZ/三个callback失败，不调用它们、不宣称故障修复。
440立即/440延迟引擎/440 eagerMTE2 producer、420旧producer/160所有bit模式、9216实际消费者、缺N-tail mask负控制通过。剥除三个新增区后整个kernel与父逐字一致，host/UB预算沿用已验证父。代码 `84e830e` 已推送，独立template dry-run仅kernel/SHA一致；正式任务 **`6abe3b9b694b590c3ce5450f` Pass，CANN编译成功、15/15、precision_ratio全1**。C8 50.44μs，对照父49.38；C9 68.57μs，代码未变，不归因波动。详情 [TT_NATIVE_NZ_RING.md](TT_NATIVE_NZ_RING.md)。
无活动任务；候选归档，下一恢复父 `e1b3634` 的49.38μs组合，不重复格式参数。原始资料Git忽略 `artifacts/tt-native-nz-ring/`。没有actual shape/plan/SoC/profile或重复A/B，单次结果仅说明没有观察到新增收益。下一结构研究先核对CANN9 A2/A3支持的Vector到Cube共享L1/TSCM契约，不编造共享地址或API，不新增GM输入通路。整体重大目标仍有空间。

## 最新：TT跨tile B包流水正式15/15通过，第8点49.38μs

分支 `experiment/tt-b-package-stream` 从通过 `4ac80c9` 开始，kernel SHA `8c03d710d5394a0660e6bedc4c172f7784a1cbe3ef9f1cbc450f231aa1d6a052`。原dual33任务/Vector/partial/ring和整个C9保持，B1两个手动包槽+显式MTE1↔MTE2 credit连续预读到后续tile，包K按L1余量选择；现有kChunk保存B包大小但kSplit仍1，完整s.k后才Max/Sum，无新GM/flags/ABI。
440立即+440延迟MTE2/MTE1/MMAD+440 eagerMTE2对抗模型、缺last-reader等待负控制、420旧producer/160全部bit模式通过；fake/固定公开8.3 host production/TUNING各6912/720/576通过。具体 [TT_B_PACKAGE_STREAM.md](TT_B_PACKAGE_STREAM.md)。CPU不是CANN9/nativeA queue/硬件精度或时间证明。
独立官方template dry-run仅kernel/297815bytes/SHA一致。代码 `eb4671c` 已commit/push；正式任务 `6abe3059694b590c3cdf6c87` **Pass，CANN编译成功、15/15、precision_ratio全1**。第8点59.27→49.38μs，单次降低16.7%/1.200x；第9点68.54→67.48μs，未改C9不归因该波动。没有actual shape/plan/SoC/profile或重复A/B，不保证稳定幅度或case路线/分数。没有活动任务，原始资料本机Git忽略 `artifacts/tt-b-package-stream/`。
保留当前通过版为下一实验父版，原组合 `4ac80c9` 保留。下一核对现有ring直接C0/NZ输出：先比对 `fcbf29b` 内建库NZ和三个回调NZ失败实验，确认与当前manual区别。公开固定8.3 copy_cube_out_utils.h 的NZ branch使用基本 `Fixpipe<DstT,SrcT,CFG_NZ>`；需核实安装9.0/A2-A3支持、FP32 stride、真实Vector DMA与无效N -inf模型后才实现。该方向尚未实现/验证，无新输入GM通路；不继续B包参数扫描、不重复N pair/worker Max。整体极限优化目标仍有空间，不能标记complete。

## 最新：队友C9与TT组合正式15/15通过，第9点68.54μs

当前 `experiment/c9-k-packages`，实现 `d19af3d`，kernel SHA `5dcb7230bef7e8935aabe6c6c80560dfb0f2d1103b5a5ea223b217bdbe075ebd`。从通过 `0d4bd04` 提取队友FP16/NT/dual20完整A1驻留、B大K包双queue、首tile晚ring credit及C9历史桶predicate；TT通过结构保留，无新GM/flags，其余kernel字节保持父版。
正式任务 `6abe2939694b590c3cdc011a` **Pass，CANN编译成功、15/15，precision_ratio全1**。第9点83.11→68.54μs，单次耗时降低17.5%/1.213x，复现用户报告队友约68μs，不能声称相对队友更快。第8点59.66→59.27μs，仅单次；无actual shape/plan/SoC/profile/重复A/B，不能证明路径命中或稳定收益。没有活动正式任务。
177实际producer+177延迟MMAD、9216实际Vector消费者、fake/公开固定8.3 tiler production/TUNING各2560/128通过，MTE1仍同步模型。详情 [C9_K_PACKAGES.md](C9_K_PACKAGES.md)，原始资料本机Git忽略 `artifacts/c9-k-packages/`。
下一保留该组合通过版作为实验父版，继续第8点结构研究；不要恢复旧TT父版时丢掉C9。TT单stage WIP保留并push在 `experiment/tt-b-stage` / `5b58c96`：180 layout/440 producer/420旧producer/160位模式及fake host通过；delayed MTE1/native queue/CANN/NPU仍PENDING，未正式提交、不混入当前组合。必须先完善B1最后MTE1读取后复用验证，再评价有无值得提交的结构差异；不重交已无收益N pair/worker Max。main/历史标签未移动，极限优化目标仍有空间。

## 当前工作起点：恢复59.66μs通过结构，准备B1单stage研究

分支 `experiment/tt-b-stage`，kernel与 `0d4bd04` 逐字相同，SHA `65e38bb155af9adb068e87dc90c01face21a7cf024d094c54846c5188e9ca120`。本次两项结构实验都正式15/15通过但无收益：worker UB Max第8点59.72μs，完整A1 N pair为60.83μs。代码/实际源码模型/原始结果分别保留 `experiment/tt-worker-max` / `fba8b4f` 和 `experiment/tt-fullm-npair` / `0cc9884`；均不合入当前kernel。没有活动评测任务。
下一条具体动作：核对一个 `2*BK` 的B1 NZ stage能否替代原两个 `BK` buffer。单stage容量与原双queue总容量相同，L0A/B继续原BK/双buffer；从stage的 `innerK*align16(cols)` 元素偏移加载B2，完成该stage最后MTE1读取才Free并预读下一个stage。ND2NZ调用可减半，但预读深度/等待可能抵消收益，不预测加速。先实际源码/物理layout模型验证K8尾、N尾、stage边界和live operand，之后再实现。
区别旧hierarchical设计的四B1/N pair：当前完整A1驻留，只有一个两K B1缓冲，不加L1/L0/UB或GM通路，不改变host/tasks/Vector。上述新stage尚未实现或验证；整体重大提升未达成。

## 当前：恢复59.66μs父版，仅改变完整A1下的Cube N配对

分支 `experiment/tt-fullm-npair`，基于 `0d4bd04`；kernel SHA `a7555e313a0bf6bfe34bca301b8769f28c6b127ed85a859292a883a1db33fcc1`。不合入无收益worker Max候选；其结果/代码保留独立分支。
同worker连续区间、同M的两个Nt在K循环内共享A2矩形Load3D，C独立完整K累加后按原Nt/ring顺序输出。A2在两次MMAD之后释放，B2独立release；原host/workspace/Vector逐字保持，无新GM/cross flags。
区别旧 `7b4d477`：完整A1驻留、一次矩形Load3D、连续任务、BM64及非对齐尾块；旧准入限16对齐/BM128且panelResident=0。避免无证据原样重交。
440立即MMAD+440延迟MMAD/ordered M-flag/live operand模型、420旧producer/160位模式、fake host production/TUNING各6912/720/144通过。细节 [TT_FULLM_NPAIR.md](TT_FULLM_NPAIR.md)。代码 `124dc31` 已commit/push，正式任务 `6abe223b694b590c3cd8474e` Pass，CANN编译成功、15/15、precision_ratio全1；第8点父59.66→60.83μs，无收益，无actual shape/plan/SoC/profile或重复对照。没有活动任务，原始资料Git忽略 `artifacts/tt-fullm-npair/`。下一恢复59.66μs父版，研究B1一个双K stage替代两个单K queue buffer：同L1预算、L0仍原128 K、ND2NZ调用减半，但预读等待可能增加；必须模型证明物理NZ切片/queue在最后MTE1后释放，不能重复旧4-B1/N pair参数。整体重大提升仍未达成。

## 当前：TT worker/M 的 UB Max 驻留正式通过，但没有收益

分支 `experiment/tt-worker-max`，从当前正式通过59.66μs的 `0d4bd04` 开始。kernel SHA `269c7d370b48db80e7da48733f558ea6d6675ac844e4b04878ab4eec077c9b3c`。
同M相邻N tile的行最大值留MQ/UB，切M或连续区间尾才写worker partial；nSplit=workers，但任务仍为M×N tiles。末级只读取真正与M相交的worker，未写槽位不初始化也不读取。原dual33选择/完整K Cube/A驻留/ring/flags/标量复用保持，不增加GM通路。
1440实际新消费者+稀疏末级线程模型、9216原窗口消费者、440producer、420旧producer/160位模式复制回归、288稀疏末级、fake/public固定8.3 production/TUNING各6912/720/144通过。M=N1536/BM=BN128/20核代理partial份数144→28，非时间预测。
详情 [TT_WORKER_MAX.md](TT_WORKER_MAX.md)。代码 `34956fe` 已commit/push；正式任务 `6abe1ed9694b590c3cd68cc9` Pass，CANN编译成功、15/15、precision_ratio全1；第8点父59.66→59.72μs，没有收益。原始JSON/模型日志本机Git忽略 `artifacts/tt-worker-max/`，无活动任务。下一恢复父 `0d4bd04`，检查Cube侧跨N的A2转换复用；旧N pair `7b4d477` 无收益且限16对齐/BM128/A非驻留，不能原样重交，必须核对新完整A1/Load3D/连续任务差异。整体重大提升仍未达成。

## 当前：TT连续tile任务正式通过，第8点单次改善8.6%

分支 `experiment/tt-contiguous-tiles`，基于通过TT种子 `a05035e`，kernel SHA `65e38bb155af9adb068e87dc90c01face21a7cf024d094c54846c5188e9ca120`。没有并入窄N驻留或NZ-B候选。
dual33覆盖B1/BF16/TT的1024..2048 M/N/K区间（父dual1/29且容量满足、没有显式pin）：完整tile连续均分；相邻N tile保留同一M的A1；nSplit=nTiles/W1；全部AIV按M块完成N Max合并再Sum，复用原Ns0行头标量。原partial/ring通路，无新GM/flags。长K容量不足时BM128→64，其余容量全部实际查询。
440实际producer、420旧producer/all65536bit回归、288真实线程barrier/延迟DMA末级模型通过；fake/public固定8.3 tiler production/TUNING各6912计划/720选择/144容量降M通过。代码 `32c6b1c` 已push；正式任务 `6abe1a32694b590c3cd3fe15` Pass，CANN编译成功、15/15、precision_ratio全1；第8点TT种子65.29→59.66μs（单次8.6%），query-block69.03→59.66（单次13.6%）。无actual shape/plan/SoC/profile或重复A/B，不声称稳定收益或新路线命中。详情 [TT_CONTIGUOUS_TILES.md](TT_CONTIGUOUS_TILES.md)。没有活动评测任务，重大提升仍未达成。
源码计数补充：20核M1408/N1025/K1536最忙10→5tiles，但A读取8.65→11.01MB；M1536/N1536/K1536最忙8→8，A14.16→11.01MB，partial18.4→73.7KB。均是实际host/fake tiler任务代理计数，非测量带宽。
下一动作：保留该通过结构，在独立分支将Vector的同M相邻N tile最大值留在UB，只在切M/区间末尾写一份worker partial。最终M行块只合并真正与它相交的worker区间；复用原partial布局，不能读取未写的worker/M组合。需要实际源码模型覆盖任务边界、唯一writer、未写区域污染和末级并发，再考虑正式验证。

## 当前：窄 N 完整 K 驻留正式通过，无收益；TT任务波次审查

分支 `experiment/narrow-fullk-persistent`，从正式通过TT种子 `a05035e` 出发；kernel SHA `4bf730de204af997b8eca185c2c2ffe72144874f29b4d59e10d33c81dc68672d`。没有并入无收益NZ-B候选。
新dual32覆盖FF窄N、小K的N/K尾部：每核完整B L0B驻留；完整A1双queue提前读后续M任务；一次矩形Load3D/完整K MMAD；旧双C/双GM ring与Vector有效N归约保持，worker跨M累加只写最终2个8float slots。父schedule仅dual/earlySum变动，不新增GM。
2654实际producer CPU、fake/public8.3 tiler production/TUNING各5376/504通过；Vector source与父版逐字一致，独立Max→worker Sum模型通过。代码 `7ffb3ff` 已commit/push，正式任务 `6abe0ee6694b590c3ccdd494` Pass，CANN编译成功、15/15、precision_ratio全1；第13点通过TT父15.28→16.04μs，没有收益。没有活动任务，整体重大提升未达成。详见 [NARROW_FULLK_PERSISTENT.md](NARROW_FULLK_PERSISTENT.md)。
新增 `tools/audit_tt_task_waves.py`：固定公开8.3真实tiler、显式物理8/20/24/32核，720个历史C8区间代理计划，330个workers少于物理cores，576选择native29，部分max tiles是理想均分的2倍。例20核M1408/N1025/K1536，NS2/tasks22，最忙10tiles/理想5；M1537/N1537/K1536为14/9。计数不是实测、未知正式shape/route；不能据此预测速度。
下一动作：保存归档后从 `a05035e` 的通过TT代码建立独立连续tile任务分支。每worker分配M-major扁平tile的连续区间、在区间内相邻N tile保留同一M的完整A；Nsplit按Nt作原partial行槽，最后合并Max再Sum。保持原GM partial/ring通路与flags，不新增GM通路；先验证唯一writer、实际producer/consumer任务顺序、A queue跨任务生命周期、容量和末级N合并，再考虑正式结构候选。该新设计尚未实现或验证，不能算进收益。

## 当前：连续NZ B + native完整M A组合正式通过，无明显收益

分支 `experiment/packed-nz-native-a`，kernel SHA `8e1fbca3a87bc380a174fbc01a181da8c5d8f9a7b02294d9d4f5895b5914942c`。只在已通过NZ_B家族接入既有raw-bit A矩形Load3D，保留连续B、原pack屏障/flag12、events、buffers、plan与workspace。
724实际packed Cube-body执行（C1/C2、完整K/尾块/全负/延迟DMA/资源和事件收支）通过；原ND/新NZ B源码各2016执行和全部65536bit，host各1728/54通过。恢复A分支后kernel与父 `99fc974` 逐字一致。
代码 `297abe5` 已commit/push，独立官方模板dry-run仅kernel.asc/SHA一致；正式任务 `6abe05cf694b590c3cc88e53` Pass，CANN编译成功、15/15、precision_ratio全1。第12点95.41→97.49μs，没有明显收益。没有活动正式任务；详细 [PACKED_NZ_NATIVE_A.md](PACKED_NZ_NATIVE_A.md)。原始结果本机私有Git忽略 `artifacts/packed-nz-native-a/`。
正式接口新增证据：C8当前67.19/best_time17.32，C13 16.48/5.21，C7 10.11/3.69，差距大于C12 97.49/85.25。这是接口参考，不保证同设备可达速度或最终评分。下一动作：恢复通过TT代码，优先审查窄N的完整B驻留是否覆盖非对齐N/K；保留既有workspace，不再重复C12加载微调。整体重大提升未达成。

## 最新：packed-B一次块布局转换正式通过，无明显收益

分支 `experiment/packed-b-nz-once`，kernel SHA `5a420968d478d3428334a42e562bbe3455d413f6db06a60a432c100282ef494a`。在原packed GM区域中一次准备 `[K/16,baseN,16]`，Cube线性copy和bulk非transpose B2 load；使用原C queue空余半区，无新UB/GM分配。A/C/归约和SyncAll/flag12保持原样；原模板默认false，dual31只转换已完成dual6计划。
CPU原ND/新NZ各2016真实源码执行、全部65536bit（NZ模式）和fake/public8.3 tiler production/TUNING各1728/54通过，首次host夹具auto类型声明已修正。详细 [PACKED_B_NZ_ONCE.md](PACKED_B_NZ_ONCE.md)。
代码 `0ad246b` 已commit/push，正式任务 `6abe0163694b590c3cc61e91` **Pass，CANN编译成功、15/15、precision_ratio全1**。第12点TT父95.41→96.65μs，无明显收益；无actual shape/plan/SoC/profile和重复A/B，不断言路由/根因。没有活动正式任务。
下一动作：在本次连续NZ B布局基础上，组合已通过TT的整M raw-bit Load3D A搬运，核对resident全K pitch、C1以及真实Cube producer同步/输出。保留原pack SyncAll/flag12，不新增GM/UB，不再试相邻packing参数。整体重大提升未达成。

## 当前工作起点：恢复已通过 TT 完整 M 版本

当前分支 `experiment/fullm-transpose-load`，kernel SHA `f0b3908378015b9a98fb5eed58337dd7556737e5ae18b79d1e25c19b497a1b09`，与正式15/15通过的 `d2eeb78` 完全一致。四布局候选与正式退化结果完整保留 `experiment/fullm-storage-layouts` / `acc84d7`；这里同步结果文档，不合入退化算法。没有活动正式任务。
新增 `python3 tools/audit_b_panel_locality.py`：独立整数地址模型核对原packed与direct来源公式、相同有效字节和不同连续性。示例N6144/K64/BN256：32KiB有效数据，direct64连续段/774656字节地址跨度，packed1段/32768字节跨度；这不是带宽或TLB实测。
下一动作：保留packed输入视图，研究预处理与Cube消费的重叠是否能在既有全局屏障、跨核flags和full-K A容量内成立。先列出队列/事件与任务依赖，再核对公开CANN/CATLASS流水；不直接删除pack，不重复已否定的pack阶段双缓冲或近邻tile试交。整体重大提升未达成。

## 最新：完整 M 四种存储布局正式通过，但性能退化，归档

分支 `experiment/fullm-storage-layouts`，基于通过TT父版 `b7147a1`；当前kernel SHA `3d2904d008155f2e8be3995b13f1295dfce130aac36ad47fbc0f8a9582bcf5f4`。
仅kernel算法改动：完整M producer支持TT/TF/FT/FF，新增单C容量选择；在完成父MakePlan最后只转换dual1/20/6→29/30，保留原ring/partial/packed allocation、其它schedule和grid。旧pack区域不使用，没有新GM通路；Vector消费者逐字未改。
CPU320矩形（A两storage全部65536bit）、2976 producer和9216消费者执行通过；fake/public真实8.3 tiler production/TUNING各8064/5888通过。首次脚本host测试夹具引用不存在字段，已修正，统一脚本exit0，日志 `/private/tmp/bmmms-fullm-storage-cpu.log`。
代码 `d0904f8` 已commit/push；正式任务 `6abde198694b590c3cb643e2` **Pass，CANN编译成功、15/15、precision_ratio全1**，没有活动正式任务。第12点TT父95.41→116.40μs（单次约22%退化），其它大点未见收益；无actual shape/plan/SoC/profile和重复A/B，不断言路由或具体根因。
下一动作：归档push后恢复 `experiment/fullm-transpose-load` 的通过kernel，再核对旧packed K面板的GM连续性/输入复用。不要重交直接B或tile参数相近版本；旧pack双缓冲也已正式否定，没有新GM许可。详细 [FULLM_STORAGE_LAYOUTS.md](FULLM_STORAGE_LAYOUTS.md)。整体重大提升未达成。

## 最新：完整 M TT 转置候选正式通过，第8点单次5.4%改善

分支 `experiment/fullm-transpose-load`；代码 `d2eeb78`，kernel SHA `f0b3908378015b9a98fb5eed58337dd7556737e5ae18b79d1e25c19b497a1b09`。
[提交 6abdd9e6694b590c3cb2e3a9](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abdd9e6694b590c3cb2e3a9) **Pass，CANN编译成功、15/15，precision_ratio全1**。
第8点query-block69.03→65.29μs（单次约5.4%）、宽窗67.44→65.29。无actual shape/plan/SoC/profile和重复A/B，不声称稳定/大幅收益或新路由命中；其它路径变化不归因。
CPU160实际复制全部65536位模式的矩形、420 producer、9216消费者、fake/public8.3 tiler production/TUNING各1400/1000配置通过。没有活动正式任务。
资料 [FULLM_TRANSPOSE_LOAD.md](FULLM_TRANSPOSE_LOAD.md)，原始结果本机Git忽略 `artifacts/fullm-transpose-load/`。
保留通过实验分支，不并入main/query-block，也不做近邻tile参数提交。
下一动作：原生支持同一full-M流水的其它storage布局（尤其非转置A/转置B的大矩阵），核对完整A的NZ pitch、K offset、B的ZN目的布局和实际预算；不新增GM、不修改其它manual/packed家族。整体重大提升尚未达成。

## 最新：宽窗口完整 K 正式通过，无大幅收益；父缓存审查改变方向

分支 `experiment/fullk-wide-window`；代码 `9cfb159` / kernel SHA `af0d52b9c2e8f34fd43c5df4577a0d9f8d2adf456b7f57c5cbb642904ab170fc`。
[提交 6abd5fdd694b590c3c8b955d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd5fdd694b590c3c8b955d) **Pass，CANN编译成功、15/15，precision_ratio全1**。
第8点69.03→67.44μs，单次约2.3%不足以证明稳定/大幅收益。其它点不归因；无actual shape/plan/SoC/profile。没有活动正式任务。
CPU420 producer、9216消费者，以及fake/public真实8.3 tiler production/TUNING各1400 host配置（1000选择）通过。
详见 [FULLK_WIDE_WINDOW.md](FULLK_WIDE_WINDOW.md)，原始结果本机Git忽略 `artifacts/fullk-wide-window/`。

**新增诊断**：公开真实tiler1000个dual1计划均有完整K A缓存，824每shard只有一个window；抽取真实Cache Hit/Free/Reset等方法的2024窗口模型证明同窗后续N tile命中已有K面板。父库并非每N tile重复读取A，该优化对多数合成计划没有理论读取量优势。
这是公开8.3源码证据，不是安装CANN9/profile；见 [NORM_FULLK_CACHE_AUDIT.md](NORM_FULLK_CACHE_AUDIT.md)。
下一动作：归档本分支、恢复query-block通过kernel；研究A2/A3 L1→L0 TT的加载指令与MMAD发起开销，先核实实际API和物理布局。不能重试只Atlas350支持的LoadData2DV2或已否定Load3D/full-A/window参数结构。
整体重大提升尚未达成。

## 最新：手写 full-K 两半 M 正式通过，宽窗口覆盖存在缺口

分支 `experiment/manual-fullk-m`；代码 `1d2ff79`，kernel SHA `fa88b68c61ec22fdaa050f75df5aaa61aba187854476d5d462d21ac59327c1d1`。
[正式提交 6abd58a2694b590c3c88d669](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd58a2694b590c3c88d669) **Pass：CANN 编译通过，15/15，precision_ratio 全部 1**。没有活动正式任务。
耗时 `[2.21,4.16,4.28,5.54,5.33,10.35,9.56,68.73,84.13,97.61,87.17,95.93,15.05,12.72,9.71]` μs。
第8点对照69.03→68.73 μs，没有明显收益；无实际shape/plan/profile及重复A/B，不能确认新路径命中。
158 producer CPU 执行及 production/TUNING 各1400 host配置（16选择）通过，与正式证据分别报告。

覆盖审查发现：同一1400网格，旧dual1共1000配置，其中984的window为4/5/6/8，被候选window≤2限制直接排除。例B1/M1024/N1024/K1024 TT原M128/N128/W4；B1/M1025/N1025/K1032为W5。这是抽取真实host/fake tiler控制流证据，非实际NPU或隐藏case路由。
下一动作：独立覆盖修复分支，实现bounded N-tile Vector消费者，保留原宽GM窗口/任务及两半M A驻留producer；检查双AIV窗口credit、最后DMA后释放、尾块及UB资源，完成实际源码模型后才考虑正式候选。
详见 [MANUAL_FULLK_M.md](MANUAL_FULLK_M.md)。原始结果本机Git忽略 `artifacts/manual-fullk-m/`。整体重大提升尚未达成。

## 当前工作状态：恢复query-block通过kernel

当前分支 `experiment/tiny-tt-query-block`，kernel代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，未改变。
本次仅同步库内完整K M预载的源码反例与研究文档。完整候选、真实公开tiler/host及外K模型保留 `experiment/fullk-m-preload` / `863c6ae`。
该候选因模型同步反例停止提交，没有活动正式任务。下一动作是下面描述的手写A预取协议研究；整体重大提升尚未达成。



## 最新：完整K库内M预载被外K同步审查否定，未提交

分支 `experiment/fullk-m-preload` 的候选 `1b278c9` / SHA `0c37471e6b6b703bda9735fef64dd47523def338c2f338d6000d6f17d80bbdec` 已归档，**不得直接提交或并入通过版**。
新增完整实际ReduceKMultiIter模型：16个A完整K/B非完整K配置复现一次Async、两次Await，补上此前只检查预载谓词的模型缺口。
这是固定公开8.3源码与标准队列元数据模型反例，不是安装CANN9缺陷的设备证明。未发起正式提交；没有活动评测ID。
资源模型和host128选择不能证明整个库同步正确，详见 [FULLK_M_PRELOAD.md](FULLK_M_PRELOAD.md)。

下一动作：恢复query-block通过kernel，独立研究手写完整K A ping/pong和下一M预取；明确B K面板释放以及下一M只等待一次，复用现有manual AIV/GM ring。
先核对现有manual与归档paired-M源，不能复制公开库上述partial-B等待顺序；没有新GM通路许可。该手写方案未实现、未验证，整体重大提升仍未达成。



## 当前：完整 K 的 M 方向预载候选待正式验证

分支 `experiment/fullk-m-preload`，kernel SHA `0c37471e6b6b703bda9735fef64dd47523def338c2f338d6000d6f17d80bbdec`。
库基本M减半、基本N覆盖整个既有窗口，完整K A双缓冲提前读取下一M块；现有GM ring、任务、AIV与finalizer字节保持一致（仅Matmul配置选择改变）。
公开真实tiler与抽取host：production1775/TUNING1779配置、各128选择；2304实际公开preload谓词/尾块/延迟转移执行通过。700 tiny源码回归通过。
详见 [FULLK_M_PRELOAD.md](FULLK_M_PRELOAD.md)；这些是公开8.3 CPU源码证据，安装CANN9编译/NPU性能精度PENDING。
下一动作：独立官方模板dry-run、正式CLI一次并记录ID，查询同一ID至终态。没有收益则归档此架构、恢复query-block。整体重大提升仍未达成。



## 当前：恢复 query-block，通过版未并入 packed-B 流水

当前分支 `experiment/tiny-tt-query-block`，通过kernel代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`。
packed-B双缓冲实验正式15/15通过但无收益，保留 `experiment/packed-b-pipeline` 的源码、宏0/1各650延迟DMA模型执行与正式结果；这里仅同步结果文档，kernel恢复原样，没有活动的正式任务。

下一条明确动作：[MTE2_PRELOAD_REVIEW.md](MTE2_PRELOAD_REVIEW.md)。已核对CANN9的GetSpecialMDLConfig支持A2/A3 M方向完整K预载及DoubleBuffer条件；先查询公开真实tiler和preload源码，区分库baseM64与现有GM窗口128行，检查完整K、depth/step/DB/L1/L0C所有条件。
这不是此前普通MDL或单M块N-session方案；不能只开配置而没有下一M块，也不能硬改depth字段不核对总容量。尚未实现或取得此方向设备结果。
整体重大提升仍未达成，不继续packed-B或resident-B相近变体提交。

## 2026-10-01 · packed-B 双缓冲正式通过，无收益

代码 `c763281`，kernel SHA `119f145b81270e2994cd686bb4c621f58c48367be8629b921e6f8705b69813b4`，[正式提交 6abd423a694b590c3c7ee13d](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd423a694b590c3c7ee13d) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.34, 3.89, 4.14, 5.54, 5.29, 10.64, 10.16, 68.97, 83.48, 99.95, 88.57, 97.14, 16.18, 13.58, 9.78]` μs，合计519.65 μs，父通过版511.66 μs。
第12点95.91→97.14μs，没有收益。只改已有case12 pack阶段，其余kernel未改，不归因其它点变化。
没有实际shape/plan/SoC/profile或重复A/B，不能证明此正式case命中新流水或判定具体退化原因。
宏0/1各650实际源码延迟DMA模型执行通过；完成真实CPU发起顺序重叠、晚释放UB源保护，但不构成硬件加速证明。
保留 `experiment/packed-b-pipeline` 的源码/模型/结果，恢复 `experiment/tiny-tt-query-block` 通过kernel；不提交预取深度或pack矩形相近变体。
原始JSON本机Git忽略 `artifacts/packed-b-pipeline/`；详见 [PACKED_B_PIPELINE.md](PACKED_B_PIPELINE.md)。整体重大提升尚未达成。

## 当前：恢复 query-block，通过版未并入新 B 驻留实验

当前分支 `experiment/tiny-tt-query-block`，通过kernel代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`。
完整B驻留实验已结束，15/15通过但没有明显整体收益；代码及296实际producer/consumer模型保留在 `experiment/resident-b-column`。
当前仅同步实验结果文档，kernel恢复原样；没有活动的正式任务。

下一条明确动作：审查case12既有packed-B预处理的双缓冲。当前 `bmmms_manual_case12_packed` 的AIV pack循环在每个矩形的MTE3后立即Fence，再FreeTensor，然后才读取下一矩形；cq已经有两个buffer但没有pack输入预取。
先按实际队列/事件生命周期实现前后矩形的MTE2/MTE3重叠，仍只用已有packed-B区和cq；保留全局完成屏障/flag12及原Cube计算。不得增加新的输入GM通路或据DMA调用数声明收益。
这项预处理流水尚未实现，不是已验证提速；整体重大突破仍未达成。

## 2026-10-01 · 完整 B 驻留正式通过，无明显整体收益

代码 `c9bfb58`，kernel SHA `280ab900d186365fb999d4bc83fc04109aa89baeaf54cfaa0b06d9b5f9e96e2d`，[正式提交 6abd3e5d694b590c3c7d644c](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd3e5d694b590c3c7d644c) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.1, 4.35, 4.27, 5.53, 5.54, 10.59, 10.1, 68.03, 85.04, 99.18, 88.75, 96.85, 16.24, 13.34, 9.21]` μs，合计519.12 μs，父通过版511.66 μs。
第8点69.03→68.03μs，单次约1.5%差异不证明稳定收益；其余路径未修改，变化不能归因。
没有实际shape/plan/SoC/profile或重复A/B，也不能证明新路由命中；本结果只证明此kernel通过15点。
完整B N块驻留L1、N外M内、多个M块UB Max状态及按列核心分组已实现；296个抽取producer和两名consumer模型、production/TUNING各480host配置（各384选择）通过。
保留 `experiment/resident-b-column` 为结构对照，恢复 `experiment/tiny-tt-query-block` 的代码 `55225cc`；不继续相近分组参数提交。
原始JSON本机Git忽略 `artifacts/column-b-residence/`，详见 [COLUMN_B_RESIDENCE.md](COLUMN_B_RESIDENCE.md)。整体重大提升尚未达成。

## 当前工作起点：恢复 query-block 通过版

当前分支 `experiment/tiny-tt-query-block`，kernel仍为代码 `55225cc` / SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，正式15/15通过，第4点5.66μs。
矩形Load3D候选已完成正式评测，未见明显收益，保留独立分支；此处只同步结果文档，没有并入其算法改动。
下一条可执行动作：审查大TT输入ND2NZ的实际K流水/缓冲生命周期，寻找能减少重复输入搬运或重叠Scalar开销的新结构；先以当前源码和官方API排除已有失败路径，不继续Load3D/MDL/session相近变体提交。
精确隐藏shape、路由、SoC和profile仍缺失；不能将第8–12点的耗时变化归因到某种计划。整体重大提升尚未达成。

## 2026-10-01 · 矩形 Load3D 正式通过，无明显收益

代码 `c4d591b`，kernel SHA `8bf5cf4568efe55df1793a30cef649a4ec29e2849027e29e0aeb93ca0e7ad0ac`，[正式提交 6abd38b5694b590c3c7aac99](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd38b5694b590c3c7aac99) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

逐点耗时 `[2.14, 4.11, 4.35, 5.67, 5.27, 10.57, 9.61, 68.95, 83.02, 97.13, 86.78, 97.74, 15.1, 13.02, 9.1]` μs，合计512.56 μs，父版511.66 μs。
第6点10.57→10.57，第12点95.91→97.74，未见明确收益；其余单次差异不能归因，没有实际shape/plan/profile或重复A/B。
六个非转置A/B调用点使用typed Load3Dv2，CPU宏0/1各2888真实块布局检查通过。
这次正式结果证明当前kernel通过15点，不证明所有加载分支命中或全部支持范围已完成设备覆盖。
保留分支 `experiment/rectangular-load3d` 为反例；后续恢复 `experiment/tiny-tt-query-block` / `909294b` 通过kernel，不继续此加载结构的相近参数提交。
原始JSON本机Git忽略 `artifacts/rectangular-load3d/`；详见 [RECTANGULAR_LOAD3D.md](RECTANGULAR_LOAD3D.md)。整体重大突破仍未达成。

## 2026-09-30 · 一次 A 整理与双 query 正式结果

代码 `55225cc`，kernel SHA `6f8c8a16abee84126186928f38c82c9a4c479b0aa571d55727513bea76397b0c`，[正式提交 6abd3263694b590c3c776446](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd3263694b590c3c776446) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.32, 3.75, 4.19, 5.66, 5.2, 10.57, 9.6, 69.03, 83.27, 97.45, 87.37, 95.91, 15.07, 12.72, 9.55]` μs，合计511.66 μs。第4点相对原通过版8.08→5.66 μs（1.43×），相对单行Vector首版6.01→5.66。其余kernel未修改，其它点的单次差异不能归因；合计时长不是正式分数，且未经过同设备重复A/B，整体重大突破仍未达成。实际shape/plan/profile未取得，不声称新路由命中。

本分支作为后续结构研究起点，保留 `experiment/manual-splitk-tiny` 与 `experiment/tiny-tt-vector` 对照；不继续Gather或query块大小相近参数提交。下一动作审查手写Cube A/B rectangular LoadData是否能用A2/A3的真实矩形加载API减少逐行指令，此API/设计尚未核实。CPU700实际源码执行、production/TUNING各432host尝试、30量化FP64对照通过，与正式证据分别报告。原始JSON本机Git忽略 `artifacts/tiny-tt-query-block/`。

## 2026-09-30 · 单 AIV 小 TT 首版正式结果

代码 `a3c65a4`，kernel SHA `4bef4346c0e746711b41ca936510b05b319ee18f09752b2414d767d1ab453b29`，[正式提交 6abd2f7e694b590c3c75d2b6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd2f7e694b590c3c75d2b6) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

耗时 `[2.14, 4, 4.32, 6.01, 5.77, 10.62, 10.26, 69.43, 84.84, 98.39, 88.22, 96.78, 15.83, 13.32, 9.1]` μs，合计519.03 μs，对照保留版517.73 μs。第4点8.08→6.01 μs（1.34×），有局部收益，整体仍无明显提升。未取得实际shape/plan/profile及重复A/B，不声称路由命中或稳定加速。其它点的单次变化不能归因于本算法。首版CPU700个实际kernel执行、production/TUNING各432个host尝试和30个量化数值对照通过。

保留该独立分支，不并入main。下一假设：首版每M行单独Gather与归约屏障，改为一次A UB整理、两M行批量点积和归约；这项查询块重排尚未实现/验证，不是再调同一路径tile参数。整体大幅提升未达成。原始JSON本机Git忽略 `artifacts/tiny-tt-vector/`。

## 当前：恢复较快通过版，配对 M 实验无整体收益

代码 `d4b9044`，kernel SHA `c6cca6ba9a120336ab4548b7f6898dd6b793291cc0b6adea0ff20d5ad86a00b3`，[正式提交 6abcc39a694b590c3c3ada93](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcc39a694b590c3c3ada93) **CANN编译通过，15/15 Pass，precision_ratio均为1**。

逐点耗时 `[2.27,3.90,4.07,7.82,5.30,10.60,10.05,69.57,84.77,99.51,88.07,96.27,15.87,13.10,9.53]` μs，合计 **520.70 μs**，对照保留版517.73 μs。第8点67.80→69.57、第11点88.16→88.07，没有整体收益；未取得实际shape/plan/profile及重复A/B，不能证明路由命中或具体退化原因。CPU172 producer和production/TUNING各360代表host组合（120选择）通过，与正式精度证据分开。

本分支保留代码、模型与失败对照，不继续同一结构相近参数提交。当前恢复 `experiment/manual-splitk-tiny` 的通过kernel，SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`；审查小矩阵的启动、同步与归约分工开销。整体大幅提升仍未达成。原始JSON在本机Git忽略 `artifacts/paired-m-breuse/`。

## 最新：独立 MDL shard 正式通过，无收益

`experiment/mdl-shard-pipeline` / `df0e049`，kernel SHA `9cf72c174b5ef077db5e8c06826df39718fe926d10efc86391f88e6a5359751e`，[正式提交 6abcbaf3694b590c3c353072](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcbaf3694b590c3c353072) **CANN编译通过、15/15 Pass**。独立MatmulImpl从Norm改MDL，host显式匹配并保留K面板分组step/depth/DB；96个host和384个抽取producer/consumer配置通过。第8点67.80→70.86、第11点88.16→89.29 µs，合计517.73→527.49，无收益，不替换最快保留版。详情 [MDL_SHARD_PIPELINE.md](MDL_SHARD_PIPELINE.md)，原始JSON在Git忽略 `artifacts/mdl-shard-pipeline/`。实际shape/plan/profile未取得，不声称路由命中或确切瓶颈。

后续审查已执行：80组公开真实tiler查询的stepM/N均为1，不能把强制step1称为已确认缺陷。A2/A3 CO2映射GM且V220无直接L0C→UB能力，不套用C310路径。见 [INPUT_PIPELINE_REVIEW.md](INPUT_PIPELINE_REVIEW.md)。下一条明确动作：从最快通过版实现大K TT配对M producer，使两个独立C共享每个B K面板，复用现有manual AIV/ring/finalizer；该设计待实现，不是已测优化。CPU工具 `inspect_public_matmul_tiling.py` 可重建80查询，源码固定公开8.3版本，不是installed9.0。后续起点恢复 `experiment/manual-splitk-tiny`；不继续相近MDL/session/output参数提交。整体大幅提升仍未达成。

## 最新：库内建 NZ 流水正式通过，无整体收益

`experiment/builtin-nz-stream` / `fcbf29b`，kernel SHA `895be634247274f702cfbebaba858c8087a309c0554cd44977c178ced77d9225`。[提交 6abcb535694b590c3c317c3e](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb535694b590c3c317c3e) **CANN编译通过、15/15 Pass**。在独立AIC stream engine上采用库内建 GM NZ C/GetTensorC，无DataCopyOut回调；AIV直接NZ DMA和树形Max。ND/NZ实际producer/consumer抽取各432配置通过，host各96检查通过。第8点相对最快通过版67.80→66.40、第11点88.16→89.04 µs，没有整体收益，不替换较快版本。没有实际shape/plan/kernel/profile，不能声称新路由命中或稳定提速；本次正式任务未出现之前callback的运行错误，不代表callback故障已修复。

代码、模型、正式结果已推送独立分支，说明 [BUILTIN_NZ_STREAM.md](BUILTIN_NZ_STREAM.md)，原始JSON在Git忽略 `artifacts/builtin-nz-stream/`。后续起点恢复 `experiment/manual-splitk-tiny`，kernel SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。**整体大幅提升仍未达成。**

下一条可执行动作：审查官方Matmul TT输入的 CopyCubeIn/LoadData 和实际tiler对应的 L1/L0 K 分块、cache/repack成本；优先取得准确plan/profile的同设备A/B，不继续相近会话或输出格式参数提交。独立MatmulImpl已在候选中编译通过，可用于后续结构研究；不得将public8.3源码等同于installed9.0 header。

## 最新：独立 AIC 库会话流式交接通过，无明显提速

`experiment/cube-stream-sessions` / `c7b004e`，kernel SHA `9b2a01d71abffcc4aa0ae7e04793a91ceb0f2ef172d73c06c7f369aa3367e471`，[提交 6abcb222694b590c3c2f8de6](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb222694b590c3c2f8de6) **编译通过、15/15 Pass**。TT 完整K原dual=1路径在新dual=26改用独立 MatmulImpl，对整个 N shard 做一次会话，逐 tile 顺序写现有 ND 双槽 ring；AIV取消KFC对象和flag9。ND尾块按实际cols紧凑stride读取。第8点67.80→67.89、第11点88.16→88.96 µs，合计517.73→519.13，无明显收益，不替换较快通过版。CPU路由96配置、producer/consumer抽取384配置通过，真实shape/plan/profile未取得。首版有启动GM地址static_cast编译错误，最终复用现有workspace变量修正。

研究发现：官方开源 `8.3.T9.0.B066` 的 dual-master IterateAll 内部调用 mul.End，外层 End 为空；也禁止逐tile Iterate/GetTensorC与LocalTensor输入。该版本不是CANN9精确header，但说明原“移除外层End保留缓存”假设缺乏依据。详见 [CUBE_STREAM_SESSIONS.md](CUBE_STREAM_SESSIONS.md)。后续从此已通过API路径研究**库内建 GM NZ 输出**和直接NZ归约，避免此前失败的自定义回调；不提交相近会话参数变体。大幅整体提升仍未达成。

## 最新：大 TT 非对齐 A 常驻正式通过但退化

`experiment/ragged-tt-resident-a` / 代码 `4507c59`，kernel SHA `d327a0632c87335a657528005b25eb9a9578086c3691f602947159baa30f2b3d`。[提交 6abcaadc694b590c3c2ada90](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcaadc694b590c3c2ada90) **CANN 编译通过、15/15 Pass**，但第 8 点 67.80→94.15 µs，15 点合计 517.73→540.33 µs。候选对 BF16 B1 TT 大矩阵尾块改用完整 A 常驻 L1、padded K 物理跨度的 LoadData2D 和既有 ND ring/归约；无新增 GM 通路。CPU production/TUNING 各 465 个计划检查、231 组物理块及独立数值模型通过。正式通过 case 无 msg，隐藏 shape/实际 kernel/plan/profile 未取得，不能断言退化来自具体模块。

失败代码、模型和结果已推送独立分支，详细说明 [RAGGED_TT_RESIDENT_A.md](RAGGED_TT_RESIDENT_A.md)，原始 JSON 在 Git 忽略 `artifacts/ragged-tt-resident-a/`。当前后续起点恢复通过版 `experiment/manual-splitk-tiny`，kernel SHA `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。大幅整体提升仍未达成。

下一条可执行动作：核对官方 Matmul 的 A cache/片上输入源码与 CANN9 实际 API，分析如何保留库的 K 流水同时减少重复加载或 GM handoff。不要重复提交本次 resident TT 相近参数，也不要据 CPU 读取次数声称优于库；NZ callback 故障仍按下文单独保留。

## 最新：紧凑 NZ ring 正式失败对照，当前恢复通过版

`experiment/nz-ring-max` 保留失败对照；最新代码 `21dae0d`，kernel SHA `34faa07f6d898386f0dec10da0a68fc0f013a67152529b650e9fd1d6e3644912`。大 TT 完整 K 的 dual=1 路径接入 Matmul 输出回调，L0C 以 NZ 写到原 GM ring，AIV 直接 NZ Max，保留窗口/分片/slot 容量和 finalizer。库 `enSequentialWrite=true` 写同一起点，因此回调显式按 curN 定位。抽取回调的 90 组单位/窗口检查、1,344 组尾块/负值地址模型通过，但三个正式版本均 **CANN 编译通过、第 8 点 Runtime Error 507015**：首版 `9c7a006`、恢复 ND 库调度的 `5de5952`、编译期 baseN 的 `21dae0d`。[最新提交 6abca4d0694b590c3c26d435](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abca4d0694b590c3c26d435) 前 7 点 Pass，后 7 点 Skipped。已证明第 8 点命中新 BF16 TT kernel，未得到底层异常地址；两项隔离未解决故障，不能归因于库 C 格式或用户标量传递。详情 [NZ_RING_MAX.md](NZ_RING_MAX.md)、[PERF_LOG.md](PERF_LOG.md)。

恢复通过版 `experiment/manual-splitk-tiny` 作为后续优化起点，kernel SHA 仍为 `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`。NZ 方案没有可计分结果，不合并最快版，暂不提交相近变体。下一条动作：取得 CANN9 实际 callback/Fixpipe header 与 `slog`/AiCore 异常 PC/GM 地址；使用独立设备 harness 分别验证 producer NZ 输出和 AIV 消费，再决定是否继续该路径。也可从通过版继续研究另一项减少 Cube/GM 主成本的结构方案；大幅整体提升仍未达成。

本机原始失败日志已保存到 Git 忽略的 `artifacts/nz-ring-max/`，避免 `/tmp` 被清理后丢失。CLI 及公共 helper 副本在 Git 忽略的 `artifacts/tooling/cannjudge-submit/`；会话仍使用用户原有 `~/.cannjudge/session.json`，未复制凭据。新提交前使用此 CLI 下载独立正式模板并 dry-run。这些本机 artifact 不随 GitHub 分支交接，接手者可按提交链接读取结果。

## 宽 N 尾块 A 常驻实验：正式通过但退化

`experiment/ragged-wide-resident-a` 代码 `3c54597`，kernel SHA256 `60b86f28e0c98731f7c54f944dd3095d1af31e1c8a02de2dd090b8a92b67828a`。[正式提交 6abbd297694b590c3cc7d861](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbd297694b590c3cc7d861) **15/15 Pass**，但第 14 点相对其手写 Split-K 父版 13.20→13.70 µs；15 点合计 517.73→526.30 µs，按页面最优时间估算均分 40.967→40.209。该实验扩展 BF16、短 M、宽 N、短 K 的 A 常驻手写 Cube 路径，使 M/N/K 非对齐尾块可走该路径；host 路由/资源回退和 10 组独立 CPU 尾块数值模型通过。正式平台未给出隐藏 shape、实际 plan、msprof，因此不能证明第 14 点命中新增分支，也不能判断退化原因。**保留失败对照，不替换较快的 `experiment/manual-splitk-tiny`。** 完整结果见 [PERF_LOG.md](PERF_LOG.md)。

## 最新：小 TT 长 K 手写 Cube Split-K 正式通过

`experiment/manual-splitk-tiny` 代码 `568f4eb`，kernel SHA256 `6e264a6b1979210a58744b2f33ac3aaa5c18ab46a975690d83c7338ab7f2aef5`，已推送私有 GitHub。[正式提交 6abbcdc5694b590c3cc4cac3](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbcdc5694b590c3cc4cac3) **15/15 Pass**，每点 `precision_ratio=1`。第 15 点相对直接 batch 父版 **13.10→9.20 µs（1.42×）**，15 点合计 522.78→517.73 µs；按页面最优时间估算均分 40.774→40.967，仅是估算而非平台公布分数。第 8 点 69.69→67.80 µs，但其它点也有单次波动，不能归因于新路径。候选只为 B=1、FP16、双转置、M/N≤128、K≥4096 且满足片上内存条件的现有 Split-K 计划启用 8 路手写 Cube，现有 finalizer 先合并 K 再执行 Max(N)→Sum(M)。

`python3 tools/validate_manual_splitk.py` 的 host 路由/资源回退与 48 组独立 TT 数值模型通过；正式 CANN 编译和 15 点精度通过。精确 SoC、隐藏 shape、实际 plan、msprof、重复测量仍 **PENDING**。最初代码 `654347a` 的[提交 6abbccee694b590c3cc43d25](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbccee694b590c3cc43d25) 因混合类型同一条 `auto` 声明而 Compile Error；`568f4eb` 只修正该声明后重新评测。下一条动作是取得第 15 点实际 shape/plan 与同设备重复 A/B，判断这条新路径的稳定得分，再决定是否并入 main；目前保留独立分支。逐点结果见 [PERF_LOG.md](PERF_LOG.md)。

## 大 TT 双 N tile 共用 A 面板的正式结果

`experiment/tt-panel-pair` / `7b4d477`，kernel SHA256 `802026fd4949d0aa1c5622576080964a8a3734267181a7ed4019303a979084e0`。[正式提交 6abbc9e9694b590c3cc258f3](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbc9e9694b590c3cc258f3) **15/15 Pass**，但第 8 点 69.69→69.65 μs、第 11 点 87.63→88.86 μs，没有明显收益。该实验恢复并接入历史经 CPU 物理块模型检查的 `RunPanelCube`：两个相邻 N tile 的 L0C 独立累加器共享 A 的每个 K 面板；`validate_cube_panel.py` 456+584 个模型执行、`validate_tt_panel_plan.py` 代理形状/资源回退通过。正式平台未暴露隐藏 shape、实际 plan 或 msprof，不能证明第 8/11 点实际命中该分支，也不能归因瓶颈。保留为对照，**不替换较快分支**。详见 [PERF_LOG.md](PERF_LOG.md)。

## 交换 TT 计算方向的正式反例

`experiment/swapped-tt-column-max` / `345e335`，kernel SHA256 `40c5bed863c6ab9411783479c0b6921268815449434728a523b5d2a4e9fff5a0`。[正式提交 6abbc6d9694b590c3cc08c48](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abbc6d9694b590c3cc08c48) **15/15 Pass**，但第 11 点相对当前较快版 **87.63→152.24 μs**，第 8 点 69.69→70.47 μs。新核把 TT 物理输入交换为 FF Matmul、在 AIV 沿原 N 做列 Max、最后 Sum(M)；独立 CPU 模型 228 组通过。实际隐藏 shape/plan/profile 未提供，不能确定每点具体路径或退化来源。此架构保留为反例，**不替换较快分支**；不要通过同一路径的小参数微调继续提交。详见 [PERF_LOG.md](PERF_LOG.md)。

## Matmul 会话复用实验结果

`experiment/norm-session-reuse` / `56ea172`，kernel SHA256 `a1c60ea079ca3c75656dc271b806d2e66268ddfc19df8f3cb70e641565cd7bb3`。[正式提交 6abb3973694b590c3c72900c](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3973694b590c3c72900c) **15/15 Pass**。改动把 dual AIC 的 `mm.End()` 从每个 C window 移到 worker 循环结束，以尝试跨 window 复用 Matmul 内部 A/B 缓冲。相对当前较快的直接 batch 归约版，第 8–12 点耗时从 `[69.69,84.83,98.04,87.63,96.02]` 到 `[70.32,84.16,97.85,88.12,96.80]` μs，有升有降，未形成大幅收益。该分支保留为失败对照，不替换较快分支。精确 SoC、实际 plan、msprof 和重复测量未取得。完整结果见 [PERF_LOG.md](PERF_LOG.md)。历史段落中“尚未删除每窗口 End”只描述当时状态，本实验已验证该改动。

上述 TT 交换方向已实测退化，随后双 N tile A 面板复用也未提速。下一条动作是优先定位第 8/11 点的实际 shape、Matmul 计划和 Cube/Vector/MTE profile，再设计另一项能减少完整计算路径成本的架构候选；没有这些指标时不得把两个反例归因于某个硬件单元。

## ragged B 常驻实验结果

`experiment/tall-ragged-resident-b` / `a6c5a29`，kernel SHA256 `92a92db0c01b93223056fc70b0cc062ebbf0eefc39b8020954e498bde370b62c`。[正式提交 6abb3724694b590c3c71cfe4](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3724694b590c3c71cfe4) 15/15 Pass，但第 13 点相对直接 batch 父版 15.74→15.93 μs，没有提速。该路径只针对历史探针推断的 B=1、M=8192、N=64–127、K=128–248、FP16 FF 非对齐类，尝试将完整 B 在每个 worker 的 L1/L0B 中复用；CPU padding/任务归属模型 384 行通过。平台未暴露实际 shape/plan/msprof，无法判断该分支是否命中或为何未见收益。保留为失败对照，不合入当前较快分支，不再提交同类微调。详细逐点结果见 [PERF_LOG.md](PERF_LOG.md)。

## 256 行 tall/manual tile 结果

`experiment/tall-m256` / `eae79e4` 的 [正式提交 6abb3203694b590c3c6fc554](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3203694b590c3c6fc554) 15/15 Pass，但目标第 13 点 15.74→16.98 μs、估算均分 40.774→40.660，未见收益。kernel SHA256 `60f31c815eb2dca302ad8c2c11b586c1b57c43727ba22a14b036053195b45c93`。独立排程/缓冲模型144组通过，但无实际 plan/msprof，因此不能确定其退化原因或真实 tile 命中。保留此分支作失败对照，不合并 main。见 [PERF_LOG.md](PERF_LOG.md)。

当前三个新正式实验均未达到重大突破：直接 batch 归约约 +0.38 估算均分；其上的消费者流水相对父版仅约 +0.02；256 行 tile 退化。后续停止以相近小变体频繁调用正式评测，优先取得精确 SoC/plan/msprof 或建立可在设备侧 A/B 的独立验证入口。保持通过版 `experiment/direct-batch-reduce` 与队友原版 `experiment/teammate-c6-c10-c12-v3` 可随时检出。
## 双缓冲消费者实验结果

`experiment/dual-consumer-overlap` 从直接 batch 归约版派生，代码 `bea6de0`，kernel SHA256 `d55ac07aa939ffa856a7f786fade29b6179d6dd226c77842d9e6868aaa560e3f`。[正式提交 6abb2eeb694b590c3c6db357](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2eeb694b590c3c6db357) 15/15 Pass。双 VECIN 预取、MTE2 完成后提前归还 GM ring、UB 树形 Max 的组合只将第 8 点 69.69→68.53 μs、估算均分 40.774→40.794；其它点有波动。该方案未达到用户的重大突破要求，不合并 main，也无需重复提交类似微调。完整验证在 [PERF_LOG.md](PERF_LOG.md)。

短 M/宽 N 路径已核查：专用计划把 64 个 N tile 分给约 16–20 核，增加分片不能降低每核最多 4 tile 的任务量。官方 CANN 9 [SetOrgShape](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0651.html) 文档支持同一 Matmul 对象复用，[WaitIterateAll](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0641.html) 文档要求显式等待异步完成，因此尚未删除 `bmmms_dual` 每窗口的 `End`。

## 当前直接 batch 归约实验

`experiment/direct-batch-reduce` 从 15/15 通过的队友版 `21dfc40` 独立派生；代码 `45efd1f`，kernel SHA256 `e06ce50abb27dc9315d1b64437c2086473ffe53295c843c39aa61aa3feadefc2`。用户已授权官方 CLI 提交，但要求只有较大突破才继续提交。

- [正式提交 6abb2b8d694b590c3c6b89a2](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2b8d694b590c3c6b89a2)：15/15 Pass；第 5/7 点 6.53→5.26、11.69→10.12 μs，第 4 点 8.48→8.33 μs。按页面最优时间估算均分 40.39→40.77，仅 +0.38；第 8/10 点单次用时上升，合计时间反而 519.71→522.78 μs。完整逐点数据见 [PERF_LOG.md](PERF_LOG.md)。
- 本地 1,458 组历史探针范围排程/缓冲模型通过；正式评测证明当前源码在 15 点精度通过。精确 SoC、隐藏 shape、实际路径、msprof 和重复测量未取得。该实验保留为小幅有效候选，不并入 main。
- 下一条动作：从本分支或队友版继续研究能明显降低 Cube/GM 主耗时的结构性方案；只有形成重大收益候选再调用 CLI。保留失败的 `experiment/large-tt-manual` 作为反例；不要把其中的 TT 强制路由合入本分支。

## 当前候选：队友 C6/C10/C12 合并 v3

- 工作分支 `experiment/teammate-c6-c10-c12-v3`，导入提交 `d9d74eb`。用户提供的 `kernel_c6_c10_c12_merged_v3.asc` 已逐字节原样导入 `kernel.asc` 并推送；244979 字节，SHA256 `ce2e12e425883fc207d0dd5d08a7a72b485c439b65fbbb8db33165905aecce52`。不要把附件中的性能注释当成本轮测量。
- [正式提交 498576](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3dbb694b590c3cd8f427)，2026-09-28 18:13:15 CST：**Pass，15/15**，每点输出错误占比 0.00%。平台保存的 `kernel.asc` 再次复制回本地并与原件逐字节比对，SHA 一致。
- 相比上个已通过的提交 498385，页面两位小数耗时有 13 点降低、2 点升高；15 点合计 599.65→519.71 μs。按页面展示的最优用时和题面公式估算均分约 34.80→40.39，仅用于同页对照，不是平台公布分数。完整逐点数据见 [PERF_LOG.md](PERF_LOG.md)。
- 旧 CPU host 检查脚本依赖上一版 `Schedule`、`TuneConfig` 结构，对新原件不适用；执行时因字段缺失而编译失败，不能记为候选精度失败或 CPU PASS。正式评测已给出 15 点正确性结果。精确 SoC、case shape/layout/dtype、实际 plan、编译命令、msprof 和重复测量仍未取得。
- 下一动作：保留此实验分支为目前正式评测较快的候选。优先识别第 1/2 点的小幅退化和第 8 点剩余较大最优差距，再针对一个可复现的形状及设备路径提出单一优化假设；设备记录须绑定本 SHA。未经额外验证不把新候选合并进 `main`。

## 上一个通过版本：CANNJudge 498385

- 分支 `experiment/performance-structure-fixes` 的 `kernel.asc` 已提交到 [BatchMatmulMaxSum 正式评测](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3abb694b590c3cd6cbe3)：提交 ID **498385**，2026-09-28 18:00:27 CST，最终状态 **Pass，15/15**，每点输出错误占比均为 0.00%。
- 提交页面保存的 `kernel.asc` 经复制回本地逐字节比对，216575 字节、SHA256 `1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`，与本分支文件一致；提交对应代码提交 `a3c1f7d`。逐点耗时和平台显示的最优用时见 [PERF_LOG.md](PERF_LOG.md)。
- 平台标注 CANN 9.0.0，但该页面未给出精确 SoC、15 点 shape/layout/dtype、实际 plan、msprof 或编译日志。这些仍待单独采集。旧段落中的“正式15点 PENDING”是提交前历史状态。
- 下一步先定位耗时比最高的第 5、8、4 点及第 13–15 点对应的 shape/layout/dtype 和实际路径，再按单一假设开实验分支做同机对照；不要根据隐藏 case 的编号猜形状。

## 最新：性能结构四项集中修复

当前分支 **`experiment/performance-structure-fixes`**，代码 `a3c1f7d`，父 `3ca0d7c`。四项均已落到kernel：完整连续A切片合并LoadData、显式tile/window/ns优先且不静默回退、取消新producer的默认自动替换、C事件延至各自首次覆写前获取。合并单级/两级K重复主循环，单N组不再启用无收益常驻。

- 默认 `BMMMS_CUBE_PANEL=0`；显式1/2/3仍可测试修复后的新内核。默认AIC/AIV预处理移除panel调用分支。此前文档“默认3”现为历史记录。
- SHA256：`1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。
- CPU物理块456+584配置及完整切片反例、严格pins/预处理、host planner、缓存、N/K拆分和UB模型通过。原反例LoadData从8次降到1次；不代表耗时8倍改善。
- CANN9/NPU/正式15点/latency/msprof仍 **PENDING**，云端按用户指示暂缓；源码修复完成不等于设备性能问题已实测闭环。
- 交接与下一条设备执行动作：[PERFORMANCE_STRUCTURE_FIXES.md](PERFORMANCE_STRUCTURE_FIXES.md)。历史规则未被臆造的成本模型替换，main只更新接手指针。

## 历史审查：性能结构与实验堆叠

用户要求检查代码是否出现屎山倾向；已审查当前4044行kernel，未修改算法。见 [PERFORMANCE_STRUCTURE_REVIEW.md](PERFORMANCE_STRUCTURE_REVIEW.md)。实际planner CPU复现了自动producer覆盖旧窗口、单N组无收益常驻导致TX1 LoadData 1→8次，以及显式bn/ns/window被case profile回写。另确认两个C累加器跨组的Fixpipe→MMAD依赖；净性能影响仍PENDING。复现：`python3 tools/audit_plan_precedence.py`。下一步优先修连续A切片和pin优先级，再处理C释放等待及统一路径选择，先收敛已有代码。当前实现分支和SHA如下。

## 最新：L1/L0 两级 K 分块

分支 **`experiment/hierarchical-k`**，实现 `d64d0c1`，父版本 `73ed463`（Cube 面板复用）。本次 kernel 新增103行、删除18行，将L1传输粒度与L0计算粒度分开。

- `panelL1K` 按真实L1容量选 `2*panelK` 或 `4*panelK`，最多512；B1四缓冲保存当前/下一对面板，A继续双缓冲或整块常驻。L0双缓冲和两个C累加器沿用父版，K累加顺序不变，无新增GM通路。
- `BMMMS_L1_K_PANELS=0/1`，默认1；不满足容量时自动保留父版。固定 `BMMMS_CUBE_PANEL=2` 或3再比较H0/H1，避免把不同优化混作收益。
- SHA256：`771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。
- CPU物理块模型：456次父producer执行、584次两级K执行通过；实际C、读取字节数、L0搬运量及MMAD次数一致，DMA调用减少。额外覆盖112的非2次幂K块及344尾块。
- host模型六种宏组合各production/TUNING通过76,424主网格及额外容量边界；默认模式选中11,992次，resident 9,964次，两级K 7,714次（含额外检查）。宽松tiler及同步事件模型不构成CANN/设备验证。
- **CANN9编译、FP16/BF16设备精度、正式15点、性能 PENDING**。四B队列实际事件分配、异步生命周期、TX1切片增加的LoadData指令成本须上板确认；减少DMA调用不是减少读取字节，更不是实测速率。
- 下一条执行动作：[HIERARCHICAL_K.md](HIERARCHICAL_K.md)。按用户指示云端暂缓；GitHub保存当前候选，main仅更新接手指针。

## 父版本：Cube 面板复用与 L1 常驻

用户要求更大幅度核心改造；当前分支 **`experiment/cube-panel-reuse`**，实现 `bc3f7cf`，父版本 `48e37c7`。新增255行kernel，重组K/N循环和片上缓冲生命周期。

- 新生产者 `RunPanelCube`：两个N tile共享A的GM→L1及L1→L0A搬运、两个C在L0C完成K累加；可容纳时整个A面板常驻L1跨N组复用；B保持双缓冲。共享已有GM环形通路及Vector最终归约。
- `BMMMS_CUBE_PANEL=0/1/2/3`：父路径 / 单tile新内核 / 双tile复用 / 可选L1常驻，默认3。查询实际L1/L0A/L0B/L0C；容量不符、只有一个N tile/shard或显式TUNING pins保留旧路径。自动替换不是已测最优策略。
- kernel SHA256：`e440e1b3d915ba61f696059cd3af0efdee6b8d087aee04ef7a49ba40ef2a637b`。
- `python3 tools/validate_cube_panel.py`：444配置物理块/完整C值/事件计数/读取量模型通过；`python3 tools/validate_host_plan.py`四档production/TUNING主网格76,424配置通过。宽松fake tiler与同步CPU指令模型，不能冒充CANN或NPU精度。
- 新内核1→2对成对tile的A读取和L0A加载减半，resident时A每个任务从GM读取一次；**不代表相对旧Matmul库的流量降幅或速度收益**。
- CANN编译、正式15点、FP16/BF16设备精度和性能 **PENDING**。云端仍按用户要求暂缓；下一条执行单：[CUBE_PANEL_REUSE.md](CUBE_PANEL_REUSE.md)，直接构建P0/P1/P2/P3，记录实际plan和SoC；重点确认事件池、双L0C和resident重用。
- 旧dual消费候选仍继承；满足准入的形状现在走新manual生产者及Fold Max。main仅更新接手指针，未合并未测kernel。

## 父版本：设备端 dual 消费流水与 tile 归约

用户要求继续推进核心优化，云服务器测试仍按用户要求暂缓。当前分支 **`experiment/dual-consumer-fold`**，父版本 `35a86eb`；代码提交 `324a6a0`（预取/提前归还槽位）、`00a91b4`（tile 内树形 Max）。不是仅修改 host 参数。

Kernel SHA256：`8f848c4869d90f0da7a955b14b457a47ecc9a09c41e515c95efa17562916d29e`。

- `bmmms_dual` / `bmmms_dual_mdl` 两条完整 K 路径接入同一设备消费 helper。既有两个 UB tile 预取下一块；最后一次 GM 读取发出后，以 PIPE_MTE2 完成依赖提前归还槽位并发下一窗口握手。无有效行的 AIV 仍参加同步。
- 在当前私有 UB tile 内按 64 lane 分组树形 Max，最后一次 WholeReduceMax 更新行最大值。256 列时横向归约 4→1、Vector 屏障 8→4；属于源码调用数，**不是实测加速比**。不额外分配 UB/GM；host plan、Cube 算术、partial/finalizer 保持父版本。
- `BMMMS_DUAL_PIPELINE=0/1/2`（默认2）；`BMMMS_DUAL_FOLD_MAX=0/1`（默认1）。前者从历史独立流水实验移植，后者是新实现；六组组合可分别归因。
- `python3 tools/validate_dual_pipeline.py` 已通过：每组76,800窗口配置、34,816归约边界配置，另3,840抽象双AIV协议调度。0/0的CPU指令轨迹与父循环一致；源码逆替换确认其它kernel/host/缓冲预算未改动。这些不是SDK或设备模拟。
- **CANN 9.0.0 编译、A2/A3 精度、正式15点、msprof/性能全部 PENDING。** Matmul内部flag 9、真实队列同步和在VECIN上原地Max必须设备确认。
- 下一条执行入口：[DUAL_CONSUMER_OPTIMIZATION.md](DUAL_CONSUMER_OPTIMIZATION.md)。云端恢复后按六档固定plan对照执行；检查实际dual路径，split-K/tiny/manual不进入本次helper。
- 已知问题修复全部继承。原样用户最优tag、main kernel及其它历史分支未替换；不要把当前候选称为设备最优。

以下为历史记录，旧的“等待设备才继续”节奏已由用户继续本地优化的指示取代。

## 当前工作：已知问题集中修复

用户最新指示是“直接把已知的问题全部解决”，并明确云服务器执行“先不用管”。当前分支 `experiment/known-issue-closure`，从 `677d882` 派生；不要继续按独立轮次割裂本地缺陷收敛，也不要为此编造设备结论。

Kernel SHA256：`d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。

- 本地已修复earlySum漏写、Tune缓存陈旧、manual冗余系统workspace、低核dot split除零；增加scratch用途变更时的库前缀重置，去掉首次分配前无必要的stream同步。继承先前UB、输出及分块修复。
- 全部R1–R18审计和生命周期/异常/题面边界的明确结论见 [KNOWN_ISSUES.md](KNOWN_ISSUES.md)。其中无实测依据的性能规则仍标待判定，不能说全部性能问题已解决。
- CPU：76,424个host plan配置（真实控制流、stub tiler）、49,152个finalizer遍历配置；缓存11字段、context隔离、scratch换用途及4类失败通过。既有N/K拆分和UB模型通过。**不等于CANN编译/设备精度通过。**
- 统一清单 `known_issues_cases.csv` 共151shape/1,208组合。云端恢复时按 [VALIDATION_REQUEST_known_issues.md](VALIDATION_REQUEST_known_issues.md) 执行，不要求对方重做算法设计；目前按用户指示暂缓。
- 本地复现：`python3 tools/validate_host_plan.py`、`python3 tools/validate_host_cache.py`、`python3 tools/validate_finalizer_coverage.py`；继承模型命令见下文。
- 资源释放仍要求调用者在stream/context销毁前调用现有release入口；正式main未修改。不要在未知ACL退出顺序的静态析构里自动调用ACL。

以下保留父版本背景；其中“等待设备后才继续”的旧工作节奏已由用户上述指示取代，本地缺陷已继续处理。

## 最新候选：N 拆分 critical work

分支 `experiment/n-split-critical-work` 从 `8fb1e72` 派生，kernel SHA256 `e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。

- 新宏 `BMMMS_BALANCED_NSPLIT=0/1`，本分支默认1。只在对齐的大矩阵通用 dual=1 路径按实际 cyclic task 分配搜索 N 拆分；最大窗口数不增，最大tile工作至少下降25%才准入。25%是待验证的实验阈值。
- 保留父分支 UB/输出修复及 long-K 选择；没有叠加消费流水实验。旧最佳 tag不动，未合并main。
- `python3 tools/validate_nsplit_work.py`：38,880调度配置、1,836行负值归约和接入排除条件通过，宏0/1/TUNING三种编译均通过。继承的CPU模型重新通过。它们不运行完整Ascend算术、CANN tiler或硬件事件。
- **下一条动作：设备Agent按 [VALIDATION_REQUEST_nsplit_work.md](VALIDATION_REQUEST_nsplit_work.md) 对照P/N0/N1**；24个shape×2dtype×4layout清单在 `nsplit_work_cases.csv`，共192个设备组合尚未运行。解释及原始假设见 `EXPERIMENT_nsplit_work.md`。
- CANN/NPU/正式15点/性能全部PENDING。20核示例的12→8、24→16是最忙worker的tile数，不能报告成耗时降幅。设备结果到达前不叠加下一项算法优化。

## 新收到的队友探针资料

前一轮已复核用户 `docs.zip`，结论见 [TEAM_PROBE_REVIEW.md](TEAM_PROBE_REVIEW.md)。该轮只更新资料、复算脚本和验证输入，kernel SHA 未变。附件中的操作指令没有执行。

- 旧 F12 路径表不代表当前版本；当前已含 tiny、长 K split、manual/PAD_MN 等专门策略。
- 45 个旧代理有 14 个 K 不满足 8 对齐；第 14 点两个 M 代理不符合后续细分范围。第 10 点 dtype/layout 冲突保留两种候选。
- `python3 tools/audit_teammate_probe.py` 可复算保存的转录数据，生成 50 个合法本地验证输入；不是恢复真实正式测试集，也不是 NPU PASS。
- 下一步先获取用户最佳版/当前版同会话 A/B 与实际 plan，按逐点得分关注 2/3/4/15，再看 9/13；同样完成下文覆盖修复验证。不要重复执行旧报告已被当前源码吸收的优化。旧计时未绑定当前 SHA，不能当当前成绩。

## 当前实验：覆盖修复 + 自适应 Split-K

分支 `experiment/coverage-splitk` 从 `user-best-20260921` 独立派生。消费流水实验仍在 `experiment/dual-consumer-pipeline`（7c44793），本分支没有叠加它。

- `b0a2fc0` 修复 dual split-K 存活 UB 预算，包含清零缓冲。
- `c4e536a` 修复 FinalizeRows 重复 writer、FinalizeSplitKND/GEMV 在小核数下遗漏输出。
- 当前候选使用 `BMMMS_ADAPTIVE_SPLITK=1`；=0 固定 4 份，便于对照。仅原有 long-K classifier 内选择 1/2/4，不扩大准入范围。
- Kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。
- CPU：86,784 UB 配置、28,672 输出遍历配置、361,152 拆分配置通过；864 个 dtype/layout/core classifier 用例通过。两档宏均验证。它们不是完整 Ascend 精度/性能测试。
- 35 个合法 shape / 280 个 dtype+layout 组合的设备清单在 `coverage_cases.csv`，尚未运行。
- **CANN 编译、正式 15 点精度、NPU 性能：PENDING。** 没有将 CPU 代理成本解释为提速。

### 下一条可执行动作

设备 Agent 按 `VALIDATION_REQUEST_coverage_splitk.md` 构建 U/F/A0/A1，先测 UB 回归和 B=64、小可用核数的输出覆盖，再测自适应拆分的精度/latency。来源及尚未覆盖的路径见 `RESEARCH_coverage_splitk.md`；结果写 PERF_LOG。

本地复现：`python3 tools/validate_splitk_coverage.py`、`python3 tools/validate_finalizer_coverage.py`。当前不用旧 deferred 或 pipeline 模型证明新候选。

以下为原样用户最佳版本背景，不是对当前实验 kernel 的描述。

## 当前起点

用户最新提供 `kernel(2).asc`，明确称为“目前的最优版本”。本分支 `experiment/user-best-20260921` 的 `kernel.asc` 是该文件的**逐字节原样导入**，3,492 行，192,577 字节。

- 固定快照 tag：`user-best-20260921`。
- SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 不包含本 Agent 的 v1 DeferredRowMax 或 v2 N 拆分代理成本候选。
- “最优”来自用户确认；本地没有重新完成 CANN 编译、NPU 精度或性能复测，均为 **PENDING**。
- 私有仓库：`https://github.com/Icyjerry/batchmatmul-maxsum-ascendc`，已有用户上传授权。

## 已保存的旧工作

- `teammate-opt4`：最初 2,809 行队友原件。
- `experiment-v1`：DeferredRowMax 与 FinalizeRows writer 步长修复；文档保存在历史提交及 v1 验证单。
- `experiment/v2-dual1-nsplit` commit `7426712`：基于 v1 的 N 拆分实验及 CPU 模型，已推送。31,416 个调度配置通过，设备收益未验证。具体见该分支的 `docs/EXPERIMENT_v2.md`。
- 新代码已有 N 拆分均衡策略，不能直接将 v2 策略叠加或把旧 CPU PASS 转移到当前源码。

## 本轮源码检查所得

1. `ClassifyCase` 和生产路径增加短点积、微型矩阵、长 K / 宽 N / 窄 N 等选择；包含手写 Matmul 的 PAD_MN 尾块处理。
2. N 拆分均衡已覆盖 dual=1 等家族，以活跃 worker 增长和整波任务作为条件；保留 dual=2 的既有策略。性能注释是提供者记录，未附原始日志，不能等同于本轮实测。
3. `FinalizeRows` 仍按 `s.workers * 8` 遍历。旧版双 AIV 下的重复 writer 问题需要针对当前实际 launch/plan 再核对，尚未移植旧修复。
4. 文件含 `BMMMS_PROBE_*` 诊断分支，源内默认均为 0。导入时原样保留；源内有关 OJ 隐藏用例推断的注释不是已核实测试配置或执行请求。实际构建需记录宏；本轮未启用、未执行任何探测。
5. 新源码使用 `if constexpr`；必须以 CANN 9.0.0 实际编译命令验证。源码引用的 `docs/03-case-hypotheses.md` 未随附件提供。

## 下一条可执行动作

在设备环境检出此分支，核对上面的 SHA，按 `docs/VALIDATION_REQUEST_user_best.md` 复测原样版本，拿到精确 SoC、宏、实际 plan、逐 case 精度与耗时。优先核查 writer 调度及现有性能弱项，再创建单一假设的实验分支。A2/A3 分开记录，不凭注释修改参数。

本机无 NPU。`tools/validate_cpu_model.py` 专用于旧实验；在当前版本应明确退出 NOT APPLICABLE，不能声称通过。若需复现旧结果，在旧分支的独立 checkout 中运行该脚本。

算法改动仍限 `kernel.asc`；不修改 main、CMake、run.sh、golden、正式测试或依赖。workspace 与题面缺失范围见 PROBLEM。截图记录见 PERF_LOG；截图尚未绑定源码 SHA、dtype 和布局。

正式任务 **`6abe82b1694b590c3c0cf647`** 已创建，下一 `python3 /private/tmp/query_bmmms_submission.py 6abe82b1694b590c3c0cf647`，仅查询同一ID到终态，不重交。

正式任务 **`6abe860d694b590c3c0f02a5`** 已创建，下一 `python3 /private/tmp/query_bmmms_submission.py 6abe860d694b590c3c0f02a5`，只查同一ID到终态，不重复提交。

首次原样复测 `6abe87e6694b590c3c102b8c` **Pass，15/15，precision_ratio全1**。μs `[1.90,2.46,3.18,4.04,5.31,9.72,10.28,49.59,67.60,98.18,88.17,96.84,15.48,13.33,9.42]`。原日志忽略 `artifacts/teammate-single-tile/repeat1.json`。下一原样创建第二次，不重复第一次任务。

第二次原样复测 **`6abe88a7694b590c3c109c3a`** 已创建，下一 `python3 /private/tmp/query_bmmms_submission.py 6abe88a7694b590c3c109c3a`，只查同一任务到终态。本次共请求两次重复，两次均已提交，不能再创建第三次重复任务。
