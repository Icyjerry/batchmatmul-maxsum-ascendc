# 本地 oj_like 测试

## 测量口径

- 使用已确认的 shape、dtype、transpose 属性生成输入；每个候选与基准使用相同输入、同一设备。
- 应用 warmup 为 **0**，执行 **5 次完整算子调用**。外部采集使用 `msprof op --warm-up=5 --launch-count=5000 --replay-mode=kernel`，默认 metrics；5000 是采集上限，统计保留应用的全部五份报告。
- 性能取完整 NPU mixed task 的 **Task Duration（µs）**，包含准备、矩阵计算和归约；报告全部样本及中位数，以相对基准的变化判断候选。OJ 最终确认收益。
- 输入保持实际 FP16/BF16 存储，保存为 `.b16`；独立参考读取这些存储，执行完整 FP64 matmul → 全 N max → 全 M sum，核对正确性调用和五次性能调用的 FP32 输出。
- 源码、实际 DSO、输入、normal plan、设备及报告均绑定 SHA。提交时使用与本地测试相同的冻结源码。

## 使用的文件

主工具目录：`.cannbot/local_oj_like_cases_20261012/`

| 文件/目录 | 用途 |
|---|---|
| `init_candidate.py` | 从显式冻结源码和 case/frame 建立候选 |
| `run_device.py` | 编译、读取正常计划、正确性验证、oj_like 采集 |
| `complete_frame.py` | 审阅实际 normal plan 后绑定完整 frame |
| `validate_capture.py`、候选内 `runner/reference.py` | 实际输入存储的完整 FP64 参考验证 |
| `analyze_oj_like.py` | 离线解析已有五份报告 |
| `fixtures/` | C10/C12/C13 的 case 与部分已知 frame；其他 case 显式提供 JSON |
| `candidates/<名称>/` | 冻结 kernel、case、frame、runner、编译 DSO 与正确性结果 |
| `oj_like_eval/<名称>/<run>/` | 全部性能报告、输入存储、输出、身份 manifest 和统计 |

源码与展开副本/行映射在对应 `.cannbot/optimization_*/` 或独立 worktree 的候选目录；当前保留源码路径见 `.cannbot/resume_20261001/state.json` 的 `retained_kernel`。

## 执行顺序与设备

`init → build → read_plan → 审阅并 complete_frame → correctness → validate → oj_like`。

设备调用通过 `.cannbot/npu_serial.py` 排队，`.cannbot/npu_test_state.json` 记录 `active` / `pending`，全局文件锁保证一次一个设备测试。子代理先与主代理协调排程；编译和离线分析可并行。

当前设备参数：`--device 0 --expected-physical 4 --smi-card 2 --smi-chip 0`；CANN 环境：`/home/developer/Ascend/cann-9.0.0/set_env.sh`。服务器重启后重新核对映射。C8 旧采集保存在独立 `.cannbot/local_oj_like_20261012/`。
