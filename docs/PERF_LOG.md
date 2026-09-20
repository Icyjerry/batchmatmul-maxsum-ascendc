# 验证与性能记录

每条新记录必须带代码 commit/SHA、设备、CANN、case、命令和实际结果。空白数据不得补成零或推测值。

## 2026-09-20 · experiment-v1

Kernel SHA256：`5545fbbd049685852eb9f1e684695a670bc2de40babff0f3697a4b6e9e3bc470`

| 检查 | 环境/范围 | 结果 |
|---|---|---|
| 抽取 DeferredRowMax 的 C++ 指令语义模型 | macOS，C++14；2,304 分片 / 54,828 行 | 与直接 max 逐位一致 |
| Python mask/stride 补充模型 | 9 种 stride；1,728 分片 / 41,850 行 | 完全一致；包括非 64 倍数 stride |
| FinalizeRows 调度 | 28,672 组 B/worker/dual | 新版无遗漏或重复 writer；旧版 1,344 组有重复 |
| UB/启用条件预算 | 5,248 组 | 新分配均在预留范围内 |
| ASan/UBSan | 本机 host 模型 | 编译成功；运行启动阶段超时，未验证 |
| CANN 9.0.0 编译 | A2/A3 | PENDING |
| 正式 15 个 case | FP16/BF16、四布局 | PENDING |
| NPU latency / msprof | T0/T1/T2 | PENDING |

普通 CPU 模型验证语义与地址，不验证设备同步、CANN 指令或性能。参考验证命令：`python3 tools/validate_cpu_model.py`。记录中的 Python 补充模型属于先前检查；当前脚本复现 C++、调度、预算三项。

## 2026-09-20 · Git 交接复现

执行 `python3 tools/validate_cpu_model.py`，退出码 0：

- C++ helper：2,304 分片、54,828 有效行逐位一致。
- 调度：28,672 配置通过。
- 预算：5,248 配置通过。
- 3 个历史 tag 的 kernel SHA256 全部与保留快照一致。

这是同一候选的可移植检查脚本复现，未新增 NPU 证据。

## 2026-09-20 · experiment/wave-balance（NPU 实测）

Kernel SHA256（CRLF，仓库存储形态）：`2e301d0d104d3008037cf75a168803282885572bde5c5ff163b970832a82e493`

环境：Ascend 910B3（device 0），20 AIC / 40 AIV，CANN 9.0.0
（`V100R001C10SPC001B250`），bisheng clang 15.0.5，`--npu-arch=dav-2201`，
驱动 25.5.0；`availableCoreNum=20`。计时为 msprof `op_summary` Task Duration。

三组 A/B（同一源码，`-DBMMMS_DEFERRED_MAX=0/1`，编译命令已用 `make VERBOSE=1`
确认宏实际传入）：

| 版本 | 源码/宏 | 21-case 精度 | 备注 |
|---|---|---|---|
| T0 | teammate-opt4 `5b9d5683` | 21/21 PASS | 原版 |
| T1 | 当前代码，deferred=0 | 21/21 PASS | 旧归约 |
| T2 | 当前代码，deferred=1 | 21/21 PASS | v1 候选 |

结论：deferred Max（T1→T2）在实测形状上约 ±7% 以内、多数为噪声级，
并未带来预期收益；真正的瓶颈是 cube wave 未填满与 64 行 tile 的 B 重载。

本分支（wave-balance）改动，全部只改 host plan（`MakePlan`）：
1. 将 dual==1 的 wave 填充从“仅 dual==2”放开，并加 gate；
2. shape family `m>=128 && 512<=n<=2048` 的 `tuneM` 64 → 128；
3. 小 K（`k<=128`、`m,n>=512`、`!tx2`）走 dual==2，绕过全 C 的 ND fixpipe；
4. 新增 `BMMMS_DUMP_PLAN=1` 打印实际 plan。

T2 → 本分支（同机实测，单次 msprof）：

| shape (B,M,N,K) dtype/tx | T2 (us) | 本分支 (us) | 比 |
|---|---|---|---|
| (1,513,511,2048) f16 FF | 106.9 | 67.7 | 1.58x |
| (1,513,513,512) f16 FF | 74.6 | 55.4 | 1.35x |
| (1,1023,513,512) f16 FF | 123.4 | 79.6 | 1.55x |
| (1,257,513,256) f16 FF | 34.8 | 30.0 | 1.16x |
| (1,1023,1025,512) f16 FF | 66.5 | 53.5 | 1.24x |
| (1,1024,1024,128) f16 FF | 77.4 | 50.9 | 1.52x |
| (1,2048,2048,256) f16 FF | 38.0 | 36.0 | 1.06x |
| (1,1024,512,256) f16 FF | 72.6 | 46.5 | 1.56x |
| (1,1024,2048,128) f16 TF | 151.0 | 105.1 | 1.44x |
| (1,1024,2048,512) f16 TF | 36.9 | 37.9 | ~1.0 |
| (2,257,513,2048) f16 FF | 45.9 | 46.9 | ~1.0 |
| (1,1024,2048,2048) f16 FF | 70.2 | 72.9 | ~1.0 |
| (4,2048,2048,2048) f16 FF | 385.7 | 386.8 | ~1.0 |

（大 dual==2 形状与转置布局在 3 次重复下为噪声级中性；先前列到的 0.94x 属波动。）

仍 PENDING：正式 15 个 case 与官方评测器；A3；逐 case median/p95；
`BMMMS_DEFERRED_MAX=0/1` 在本分支上的完整 A/B；bf16 计时。

原始材料：本机 `/tmp/opencode/`（非 Git）。plan dump 可用
`BMMMS_DUMP_PLAN=1 ./batch_matmul_max_sum_custom B M N K 1 tx1 tx2` 复现。

## 2026-09-20 · 覆盖度检查与死代码瘦身

Kernel SHA256（CRLF）：`95e8c24446daf7dd4b670adea393f1f7f5344229bc54257783efc5f7e8bf2fcc`

- 静态 + 51-shape 实测确认：默认构建 `dual ∈ {0,1,2}`，8 个策略 kernel 不可达
  （见 [COVERAGE.md](COVERAGE.md)），合计 888,216 B。
- 把这些 kernel/类与其 `Launch` 分支用 `#ifdef BMMMS_TUNING` 包住：
  设备 ELF `1,689,520 -> 714,736` B（−58%）；`-DBMMMS_TUNING` 构建仍含全部候选。
- 精度：36/36 通过（新增 dual==2 与 kSplit>1 覆盖 case）。
- 性能：5 个代表 shape A/B 为噪声级中性（±6%），本项不是速度优化。
- 仍未覆盖/未验证：官方 15 case、A3、median/p95、`BMMMS_TUNING` 候选的性能。

## 后续实机记录模板

```text
Date / Commit / Kernel SHA:
SoC / device / die / CANN / driver:
Case (B,M,N,K) / dtype / tx1 / tx2:
Actual plan (dual, baseM, baseN, window, nSplit, kSplit, cubeBlocks, deferredMax):
Version T0/T1/T2:
Build command and status:
Correctness / max_abs / max_rel / repeat consistency:
Cold call / steady median / p95 / run-to-run variation:
Cube utilization / Vector utilization / MTE / Task Duration:
Log location:
Interpretation / next hypothesis:
```
