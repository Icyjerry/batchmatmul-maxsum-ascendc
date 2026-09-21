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

## 2026-09-21 · dual-consumer-pipeline

- 分支：`experiment/dual-consumer-pipeline`，基于 `user-best-20260921`。
- Kernel SHA256：`07993447be9814aa7d502e9ddd51a9099bcea5c963f4be7a5e09b15e798cf5c4`。
- 假设：现有双 UB 缓冲用于预取，并在 MTE2 完成后提前归还双槽 ring，可减少消费侧串行等待。默认实验宏 BMMMS_DUAL_PIPELINE=2，0/1 为消融对照。
- 命令：`python3 tools/validate_dual_pipeline.py`；macOS、系统 clang++ C++14 -O2；退出码 0。

| 检查 | 结果 | 边界 |
|---|---|---|
| 模式 0 | 76,800 次用例执行通过；完整模型 trace 与从用户原件抽取的循环一致 | CPU 模型，不是编译后的 NPU 指令 |
| 模式 1 | 76,800 次通过；23,040 次实际占用两个 UB 槽 | 原版相同的地址、Max 结果及 Vector 调用顺序 |
| 模式 2 | 76,800 次通过；23,040 次占用两个 UB 槽；release 后立即污染 GM 仍结果一致 | 假定 PIPE_MTE2 完成语义成立 |
| 抽象跨核协议 | 3,840 组随机交错通过；0–9 个窗口、双槽终态信用配对 | 不模拟 Matmul 内部 wrapper / CANN 硬件 |
| 改动范围 | 恢复两处旧消费循环并剔除新 helper/宏后，源码与用户 tag 全文一致 | host plan、分配、Cube、finalizer 均未混改 |
| CANN 9.0.0 编译 | PENDING | 本机无 SDK |
| NPU 正式精度 / latency / msprof | PENDING | 不能宣称比用户最优更快 |

初轮 mode 2 检查脚本将 release trace ID 写为 700/701，实际模型编码为 702/703，导致测试断言失败。修正测试编号后重跑全套通过，kernel 未因该断言修改；此前失败不是设备错误。

研究来源：`RESEARCH_dual_pipeline.md`。下一步：设备 Agent 按 `VALIDATION_REQUEST_dual_pipeline.md` 构建 U/P0/P1/P2；若 P0 对 U 退化，先定位 helper 提取对编译的影响；若仅 P2 失败/退化，用 P1 隔离提前 wrapper 握手的影响。
