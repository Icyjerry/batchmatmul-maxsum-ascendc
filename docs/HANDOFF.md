# 最新接手状态 · 2026-10-08

## 当前工作区：通过版恢复，C13待实现

分支 `experiment/c13-frame-audit-1008`，kernel逐字恢复通过算法1734f16，354602bytes/SHA `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`。C3候选与模型/结果保留已推送 `experiment/tiny-ft-static-frame` /16ce102；在该历史分支复现其入口模型，恢复源码不包含新C3入口。当前无活动评测任务，CLI登录已恢复可复用，无需再次索要登录。

C13审查工具 `python3 tools/audit_c13_plan.py` 可在恢复版执行；下一按 [C13_FRAME_AUDIT](C13_FRAME_AUDIT.md) 实现一个保持原K-panel和GM的独立frame，需实际源码生命周期模型与资源/精度验证后才交，不重复无收益完整K/B驻留结构。尚未实现C13新算法或声称提速，main/历史标签不动，整体目标未完成。

## 最新正式终态：C3候选归档

任务 **6ac72eaa694b590c3c97d81d** 已Pass15/15、precision_ratio全1。C3=3.10μs，处于父最近五次3.08–3.22范围（中位3.16），未见明显收益；全部15点和局限见 [TINY_FT_STATIC_FRAME](TINY_FT_STATIC_FRAME.md)。总472.19μs，新Tbest换算均分55.19646。候选保留本分支，不合main、不重复提交、不扫附近参数。没有活动任务；下面PENDING/Running是历史状态。下一恢复通过1734f16并继续C13独立frame假设；整体目标未完成。

## 历史：正式任务创建与查询

用户重新登录后CLI dry-run成功，仅kernel.asc /359206bytes /SHA515aa159…，其它七模板源码逐字1734f16。候选代码 `a3c6217` 已推送。正式任务 **`6ac72eaa694b590c3c97d81d`** 已创建；下一执行 `python3 /private/tmp/query_bmmms_submission.py 6ac72eaa694b590c3c97d81d` 查询同ID至真实终态，不重交。终态/精度/性能PENDING。下面“没有任务/登录阻碍”是创建任务前历史状态，已解除。

## 当前候选与下一动作（优先于下方历史条目）

- 分支 `experiment/tiny-ft-static-frame`，父 `bfd5d0a` / 通过算法 `1734f16`。候选仅 kernel 三处新增92行，SHA256 `515aa1592edbb26252b06b0ec610fc96d7c1353f69347a9e3b92327f39f5e024`，359206 bytes。main/历史标签不动。
- 小FT路径将M/K/NP和UB地址编译期确定，只算有效N点积，紧凑写M个最大值。保留原batch/grid/plan/workspace；仅FP16 FT历史C3条件及实际UB/AIV、原dual24、无显式调参pins准入。父已经有共享Cast和独立batch，不重复声称新增这些。详情 [TINY_FT_STATIC_FRAME](TINY_FT_STATIC_FRAME.md)。
- 本地模型通过1024次入口/512软件编码FP16、八项负控制；production/TUNING各4800 host配置与全部256条件shape、资源阈值/回退通过；去除三处逐字恢复整个父。CPU不是设备模型。CANN9编译、正式精度/性能 **PENDING**。
- 当前**没有正式任务ID或活动任务**。旧临时模板/CLI被OS清理，已从Git通过快照/本机公开工具缓存恢复。用户回复已登录后，CLI再次dry-run仍报会话过期/损坏；仅stat显示默认会话文件10月3日更新，不读取其内容。已请求在本机运行 `python3 /private/tmp/cannjudge_cli.py login`，或提供另一个会话文件路径（不提供内容/凭据）。
- 登录可用后：独立模板 `/private/tmp/bmmms-tiny-ft-static-official/project` dry-run，核对本候选SHA及其它七文件逐字1734f16；commit/push后只创建一次结构评测。取得ID立即存入交接并push，查询同ID至真实终态，记录完整15点。明显大收益才原样确认，否则归档，不扫描附近M/NP/K参数。父最近五次C3中位3.16μs、范围3.08–3.22；更早有3.06，不择优。
- 计分用用户最新Tbest，[SCORE_REFERENCE_1003](SCORE_REFERENCE_1003.md)。新参考下相对用户历史第一名的差距优先C3/C13/C11/C9/C1，见 [SCORE_PRIORITIES_1008](SCORE_PRIORITIES_1008.md)；不是实时榜单。C13本轮尚无算法修改；完整4096个CPU stub host计划审查见 [C13_FRAME_AUDIT](C13_FRAME_AUDIT.md)，已排除重复完整K/B驻留试交。原CPU日志忽略 `artifacts/tiny-ft-static-frame/cpu.log`。
- 下方10月3日及更早的“当前分支”“下一动作”“会话可复用”均为历史记录，以本段为准。整体优化目标未完成；不将本地通过称为已提速。

## 当前计分参考更新

用户提供新Tbest：`[1.23,1.73,2.34,2.76,3.92,6.46,6.40,17.32,50.10,68.52,70.09,81.09,9.04,9.52,8.11]`μs。后续用此参考，见SCORE_REFERENCE_1003。最新6ac0d57f同468.89μs重新换算平均分56.42050；10月3日前两次分别57.00705/55.29167。下面50.x均是旧T历史换算，耗时/精度/源码未改，无新评测任务。旧得分差距优先级需重新核算，不混用新旧T。

## 用户随后新增一次：已完成

用户明确“再交一次”，新增任务 `6ac0d57f694b590c3c252456` 已CANN编译成功、15/15 Pass、precision_ratio全1。总耗时468.89μs，按用户T换算平均分50.58201。仍在experiment/best-identical-repeats-1003，最优组合1734f16/a5eef105…/354602bytes，算法/参数未改，dry-run一致。本新增请求恰好一次已完成，无活动任务，不再提交；原结果忽略artifacts/best-identical-repeats-1003/extra-one.json。完整15点见BEST_IDENTICAL_REPEATS_1003末尾；同源码波动不是新优化收益。下一继续既定重点结构优化，整体冲榜目标尚未完成。

## 10月3日新增两次复测

当前分支experiment/best-identical-repeats-1003，从cf52f5e延续最优组合1734f16/a5eef105…/354602bytes，算法与参数未改。用户新增两次已完全完成：`6ac08cd7694b590c3cf7a7d8` / `6ac08d9c694b590c3cf806ec` 均CANN编译成功、15/15 Pass、precision_ratio全1。总耗时464.52/471.22μs；按用户T换算平均分50.84691/50.01648，不是榜单排名证明。没有活动任务，不创建第三次。

完整15点和样本波动见BEST_IDENTICAL_REPEATS_1003：C13 15.13/16.74μs（极差/中位10.1%）、C4 3.94/4.12、C9 67.35/68.07、C11 87.35/88.91。同源码变化不是新优化；真实SoC/shape/plan/profile未知，不是受控同机A/B。两次均无429；源码和八文件模板逐字1734f16。原JSON忽略artifacts/best-identical-repeats-1003/，目录700/文件600。下一继续原已确认C3/C11/C1/C4/C9结构优化，不重复本组任务；整体冲榜未完成。以下10月2日为历史状态，当前以本段为准。

## 当前用户新增复测请求

当前分支 `experiment/best-identical-repeats-1002` 从62ad1cd恢复最优组合1734f16，kernel SHA a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742/354602bytes。用户要求当前最优原样再交两次，已经完全完成：`6abfc955694b590c3ca51a64` / `6abfca4d694b590c3ca5b6a8` 均CANN编译成功、15/15 Pass、precision_ratio全1。总耗时464.23/465.68μs，按用户T换算平均分50.58646/50.82629，不是榜单排名证据。

完整15点和波动见BEST_IDENTICAL_REPEATS_1002。C4 4.11/4.08、C9 67.34/67.91、C11 86.99/86.97；同源码变化不是新优化收益。第二次POST两次429无ID后等待成功；本轮恰好两任务，没有活动任务，不创建第三次。源码和其它七工程文件逐字等于1734f16；原JSON忽略artifacts/best-identical-repeats-1002/，目录700/文件600。

C4候选6abf25e6694b590c3c4a0fa3 15/15但C4 4.43vs父4.12，无收益，归档experiment/tiny-tt-packed-frame/579aba8；交换操作数TT也归档。当前不包含这两个候选。下一继续已确认重点C3/C11/C1/C4/C9，尊重已否定结构，优先分析C3维度专门化的动态地址/循环开销；尚未实现，不据此提交参数扫描。整体冲榜未完成。

## 当前代码和任务

- 工作分支：`experiment/best-identical-repeats-1003`，算法逐字恢复通过版 `1734f16`，没有 tiny 广播/K 树候选。
- `kernel.asc`：354602 bytes；SHA256 `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`。
- 对应正式任务 `6abeb39e694b590c3c22e5d7`：CANN 编译成功，15/15 Pass，precision_ratio 全1。
- 当前版原样两次复测已完成：`6abeceed694b590c3c2bc7a5` / `6abecfc5694b590c3c2c1347`，均15/15 Pass。C8三次46.52/46.51/46.48 μs，C9三次67.79/67.88/67.91；C2极差/中位6.4%、C15 5.8%。见 [CURRENT_IDENTICAL_REPEATS](CURRENT_IDENTICAL_REPEATS.md)。没有活动任务，不继续第三次；算法未改，整体“大幅优化、冲榜”目标未完成。
- main 的算法和历史标签不动。main 接手文档应指向本实验分支，不能把 main 历史 kernel 当作上述通过组合。

先读 [PROBLEM](PROBLEM.md)、[原始验证约定](VALIDATION_REQUEST_v1.md)、[PERF_LOG](PERF_LOG.md)。旧接手条目完整保存在 [历史记录](HANDOFF_HISTORY_20261002.md)；其 PENDING/下一步是历史状态，优先以本文和各实验文档最后的正式终态为准。

## 本次完成与否定的方向

| 实验 / 已推送分支 | 正式任务 | 结果与下一步 |
|---|---|---|
| `experiment/tiny-storage-vector` / cec9a1b | `6abec499694b590c3c288b4a` | 15/15；C2/C3 2.54/3.16 μs，没有明显收益，归档 |
| `experiment/tiny-group-ktree` / d1976d4 | `6abec72a694b590c3c296090` | 15/15；C2/C3 2.57/3.28 μs，没有明显收益，归档 |
| `experiment/tiny-all-k8-fold` / 8ab42c6 | `6abec94f694b590c3c2a0c34` | 15/15；C2 4.39 μs，对照2.46，明显不利，归档 |

从取消 document Gather，到整组广播/K树，再完成 K40/48/56 的非二次幂尾部折叠，均已实现并正式测试。减少调用没有变成正式收益；不继续这条 storage-native/Brcb/K树方向的变体、原样复测或附近参数扫描。

实现、CPU模型、误差、全部15个耗时和证据边界分别见 [storage-native](TINY_STORAGE_VECTOR.md)、[整组K树](TINY_GROUP_K_TREE.md)、[完整K8](TINY_ALL_K8_FOLD.md)。在对应已推送分支的独立 worktree 复现模型；恢复版中的模型不包含这些候选。它们使用排队整数模型、软件解码 FP16/BF16 与 FP64 golden，不能当真实硬件模拟。最后一项 production/TUNING 各17616入口/5652编码浮点用例、九项负控制通过；正式15Pass仍不证明所有shape或事件交错。

原始CPU日志/评测JSON保存在本机根工作区的 Git 忽略目录 `artifacts/tiny-storage-vector/`、`artifacts/tiny-group-ktree/`、`artifacts/tiny-all-k8-fold/`，目录700/文件600。不要提交大型日志、输入或凭据。先前 raw-bit transpose 的不利结果在 `experiment/tiny-bit-transpose` /26beaac（C2 4.12），也不要重做。

## 保留的收益及波动

- C7 手动frame：四次同SHA为8.00/7.88/8.04/7.67 μs，对照旧9.59–10.28；保留，详见 [C7_MANUAL_FRAME](C7_MANUAL_FRAME.md)。
- C14 宽N手动frame：确认10.93/10.84 μs，对照12.72–13.26；保留，详见 [WIDE_N_MANUAL_FRAME](WIDE_N_MANUAL_FRAME.md)。
- TT 手动frame C8 46.52 μs；父三次47.24/48.88/48.45，仅小幅单次变化，不能称突破，详见 [TT_MANUAL_FRAME](TT_MANUAL_FRAME.md)。
- 用户“同一份再交两次”已完成 `6abeb052694b590c3c220fa2` / `6abeb132694b590c3c223f34`，均15/15，分支74e0dd2已推送。见 [TT_IDENTICAL_REPEATS](TT_IDENTICAL_REPEATS.md)，不要再创建第三次。三次C8极差3.4%，C13极差9.9%。
- 接口没有实际SoC、case shape/layout/dtype、plan或profiling。未知路径不能根据case编号认定命中，不归因源码相同路线的计时变化，不以接口score0或历史best_time推算真实榜分。新 C2 大回退没有被噪声解释抹除。

## 下一条可执行动作

1. 在恢复版上审查 TT producer 的 ND-to-NZ 传输粒度、有效输入字节、ManualTransposeFullM/Load3D 与 L0 复用。结合 `docs/teammate_probe/hypothesis_ranges.csv` 的历史条件范围选择独立代理，明确其不是正式shape；记录实际模型plan、容量和调用/字节计数，不预测耗时。
2. 先读 [TT_FULLM_NPAIR](TT_FULLM_NPAIR.md)、[TT_WORKER_MAX](TT_WORKER_MAX.md)、[TT_NATIVE_NZ_RING](TT_NATIVE_NZ_RING.md)、[RAGGED_TT_RESIDENT_A](RAGGED_TT_RESIDENT_A.md) 及相关正式结果，排除已经失败的结构。当前已含 fullA1驻留、跨Nt Bpackage预取、doubleL0与单末级barrier，不重新声称首次提出。
3. 找出此前未实现的结构后，核对 CANN9 实际API、独立实际源码/同步/精度模型、资源与scope，再 commit/push 并正式提交。没有可信结构假设时不提交参数扫描。当前下一项算法尚未实现。

## 执行约束

算法只修改 `kernel.asc`；不改main/CMake/run/golden/正式测试/依赖，不增加GM通路。保留配对B、完整FP32 K点积后MaxN再SumM、四布局、负值/尾块、输入不变和唯一合法y写。CANN9目标A2/A3，实际容量/核数查询，不假设固定SoC。

CLI保存的会话可复用，不读取或输出token。每次提交先独立模板仅换kernel/dry-run SHA、commit/push，取得ID立即写交接再查询同ID至真实终态；观察超时不能重交。只有明显大收益才原样确认。云SSH按用户“先不用管”，不要重复索要。
