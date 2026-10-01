# 最新接手状态 · 2026-10-02

## 当前代码和任务

- 工作分支：`experiment/post-tiny-review`，算法逐字恢复通过版 `1734f16`，没有 tiny 广播/K 树候选。
- `kernel.asc`：354602 bytes；SHA256 `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`。
- 对应正式任务 `6abeb39e694b590c3c22e5d7`：CANN 编译成功，15/15 Pass，precision_ratio 全1。
- 用户本次再次要求当前版原样两次复测。复测1 `6abeceed694b590c3c2bc7a5` 已提交，终态 PENDING；必须查询此ID至终态后再提交复测2，见 [CURRENT_IDENTICAL_REPEATS](CURRENT_IDENTICAL_REPEATS.md)。算法未改。整体“大幅优化、冲榜”目标未完成。
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
