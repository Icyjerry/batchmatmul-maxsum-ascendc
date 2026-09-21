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

## 2026-09-21 · 用户提供的性能截图（未绑定源码）

截图标记环境为 910B3 / 20 Cube / CANN 9.0.0，msprof。尚缺 kernel SHA、dtype、tx1/tx2、构建宏和原始日志，不能归因到 v1、v2 或新导入版本。也没有正式 15 case 精度通过证据。

| (B,M,N,K) | op | 耗时 | blocks | Cube | MTE2 | MAC | fixpipe（保留截图单位） |
|---|---|---|---|---|---|---|---|
| (1,513,511,2048) | bmmms_dual | 107.2 us | 5/20 | 23.5% | 88.4% | 17.0% | 25% |
| (1,1023,513,512) | bmmms_dual | 123.5 us | 16/20 | 71.7% | 89.3% | 2.9% | 40.7% |
| (2,257,513,2048) | bmmms_dual_mdl | 48.0 us | 18/20 | 65.0% | 58.3% | 14.7% | 1.9% |
| (16,512,512,512) | bmmms_dual | 65.7 us | 20/20 | 78.2% | 58.7% | 31.0% | 23.1 us |
| (4,2048,2048,2048) | bmmms_dual_mdl | 387.1 us | 20/20 | 80.1% | 80.1% | 76.7% | 23.1 us |

截图提及的 3–4 倍空间属于外推，未经实验确认。MTE2 时间占比不能直接解释为带宽饱和度。

## 2026-09-21 · 当前用户最优版本导入

- 用户确认当前最优：kernel(2).asc，3,492 行、192,577 字节。
- SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 逐字节复制并核对 SHA；没有移植 v1/v2 改动。
- 源码注释记录的性能属于提供者数据，未在本轮复现。
- 旧 CPU helper 模型对该源码不适用；脚本明确非零退出，不能误报 PASS。
- 当前版本 CANN 编译 / NPU 精度 / NPU 性能：PENDING。

## 2026-09-21 · coverage-splitk

分支 `experiment/coverage-splitk` 从用户最优 tag 派生，不含流水实验。
当前 kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。

修复提交：`b0a2fc0`（存活 UB 预算），`c4e536a`（输出遍历）。后续候选只在原 long-K 类中按工作量选择 1/2/4 份，宏 `BMMMS_ADAPTIVE_SPLITK=0/1` 做对照。

| 检查 | 命令/范围 | 结果 |
|---|---|---|
| 实际 InitBuffer 表达式和 classifier | `python3 tools/validate_splitk_coverage.py`；M=16..128、N=1..256、128/192/256 KiB UB | 86,784 配置通过；识别并阻止 3,328 组旧超预算选择 |
| 关键 UB 反例 | (1,112,192,8192)，192 KiB UB | 旧预算 192,448 bytes；源码显式存活分配 217,120 bytes；新版不强制 Split-K |
| 拆分选择器与独立逐 task oracle | 同上；B=1..64、K=4096..8192 步长 8、11 种核数 | 361,152 配置通过；208,482 组少于 4 份；选 1/2/4 各 115,629/92,853/152,670 |
| classifier dtype/layout/core | 同上；两种 dtype、四布局和代表性 B/K/核数 | 864 配置通过；宏 0 始终固定 4，宏 1 符合选择器与完整 M/N tile 要求 |
| 输出唯一与完整覆盖 | `python3 tools/validate_finalizer_coverage.py` | 28,672 配置通过；旧版 320 组遗漏、896 组重复 |
| 设备清单输入合法性 | docs/coverage_cases.csv | 35 个不同 shape 符合当前实现的边界和 2^26 元素约束；280 个 dtype/layout 组合待设备运行 |
| CANN 9.0.0 编译 | A2/A3 | PENDING |
| 正式 15 点、真实精度、NPU 性能 | U/F/A0/A1 | PENDING |

Split-K host 模型两档宏均编译运行，统计是各档相同模型空间，不将两档相加声称独立覆盖率。输出模型按实际 for-loop 头部计数，但没有执行完整设备算术或同步。代理工作量非增不等于真实耗时非增。

验证资料：`RESEARCH_coverage_splitk.md`、`VALIDATION_REQUEST_coverage_splitk.md`。下一步先验证 UB 回退能被真实 CANN tiler 接受，再验证低核数的输出覆盖与 A1 的 FP32 精度/latency。
