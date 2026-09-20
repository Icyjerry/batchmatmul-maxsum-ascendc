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
