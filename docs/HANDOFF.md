# 最新接手状态 · 2026-10-02

## 当前用户新增复测请求

任务2 `6abfca4d694b590c3ca5b6a8` 已创建，终态PENDING；任务1已经15Pass。本轮恰好两次任务均已创建，下一只查任务2同ID至终态，不创建第三次。下文“任务2尚未创建”已过期。

最新：任务1 `6abfc955694b590c3ca51a64` 已15/15 Pass；任务2两次POST HTTP429且无ID，尚未创建。下一等待限流解除，仅提交缺少的第二次；下文任务1PENDING已过期。源码仍为最优组合1734f16/a5eef105…，见BEST_IDENTICAL_REPEATS_1002。

任务1已创建 `6abfc955694b590c3ca51a64`，终态PENDING；任务2尚未创建。下一只查任务1同ID，并创建恰好一次任务2、保存新ID再查询。下文“两任务尚未创建”是提交前状态，已被本条替代。

当前分支 `experiment/best-identical-repeats-1002` 从62ad1cd恢复最优组合1734f16，kernel SHA a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742/354602bytes。用户明确复测当前最优组合两次，详见BEST_IDENTICAL_REPEATS_1002；算法未改，下面“不要第三次”仅约束此前已经完成的复测，不取消本次新增请求。当前两任务尚未创建。

C4候选6abf25e6694b590c3c4a0fa3 15/15但C4 4.43vs父4.12，没有收益，归档experiment/tiny-tt-packed-frame/579aba8；交换操作数TT也归档。当前不包含这两个候选。下一创建恰好两次最优版任务、立即保存ID、只查对应ID至终态；提交模板dry-run与当前SHA一致。完整源码不修改，原资料忽略artifacts/best-identical-repeats-1002/。整体冲榜未完成。

## 当前代码和任务

- 工作分支：`experiment/current-identical-repeats`，算法逐字恢复通过版 `1734f16`，没有 tiny 广播/K 树候选。
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
