# 验证与性能记录

每条新记录必须带代码 commit/SHA、设备、CANN、case、命令和实际结果。空白数据不得补成零或推测值。

## 2026-09-29 · CANNJudge CLI · 256 行 tall/manual tile 失败对照

- 独立分支 `experiment/tall-m256` 从直接 batch 归约 `fa3eaed` 派生，代码 `eae79e4`，kernel SHA256 `60f31c815eb2dca302ad8c2c11b586c1b57c43727ba22a14b036053195b45c93`，248426 字节。[提交 6abb3203694b590c3c6fc554](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb3203694b590c3c6fc554)，官方 CLI dry-run 确认只上传该 `kernel.asc`。
- 假设：历史探针第 13 点 M=8192、N∈[64,127]、K∈[128,248] 的 FP16 FF 路径，用 256 行 manual tile 把 64 个 M 任务降至 32 个，并减少 B 重复搬运。仅该形状类别进入显式 L1/L0/UB 预算分支；资源不足时保留 128 行候选。`python3 tools/validate_tall_m256.py` 144 组排程/输出槽/缓冲模型通过；这不是设备 tiling 证据。
- 正式结果 **Pass，15/15**，`precision_ratio=1`。第 13 点反而从直接 batch 父版 15.74 升至 16.98 μs；15 点合计 522.78→523.82 μs，按同页最优值估算均分 40.774→40.660。其它点的变化落在单次结果波动范围，未见结构性收益。正式耗时依次为 `[2.08,3.95,4.22,7.90,5.49,10.61,10.09,69.34,82.98,99.73,87.63,96.52,16.98,13.30,13.00]` μs。
- 平台不提供实际 plan、精确 SoC、msprof，故不能证明第 13 点确实选到了 256 行 tile，也不能判定退化来自 L0C 单缓冲或 Cube 负载；此分支保留失败对照，**不合并 main**。
## 2026-09-29 · CANNJudge CLI · 双缓冲消费流水

- 分支 `experiment/dual-consumer-overlap`，代码 `bea6de0`，kernel SHA256 `d55ac07aa939ffa856a7f786fade29b6179d6dd226c77842d9e6868aaa560e3f`，248362 字节。官方 CLI dry-run 仅含 `kernel.asc`；[正式提交 6abb2eeb694b590c3c6db357](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2eeb694b590c3c6db357)。父版是通过 15 点的直接 batch 归约 `fa3eaed`。
- 假设：双 VECIN 缓冲预取下一 C tile；当前 GM ring 槽的所有 MTE2 读取发出后以 `PIPE_MTE2` 归还，使 Cube 写下一窗口与 Vector 的私有 UB 归约重叠；每 tile 先在 UB 做 64-lane 树形 Max，减少横向归约调用。只改完整 K 的 dual/dual_mdl AIV 消费侧，不改 Cube/tiling/partial 布局。
- CPU：`python3 tools/validate_dual_consumer_current.py` 六种流水/归约组合分别通过 76,800 个窗口配置，34,816 组列尾/全负/污染检查与 3,840 组抽象握手交错；且源码除这两条消费者外与父版一致。CANN 编译/真实事件耗时无法由模型证明。
- 正式 **Pass，15/15**，`precision_ratio=1`。平台标注 CANN 9.0.0；精确 SoC、hidden shape、实际 plan、msprof 未取得。相对父版，第 8 点 69.69→68.53 μs、第 9 点 84.83→82.81 μs、第 11 点 87.63→86.98 μs；第 10/12 点 98.04→98.38、96.02→96.74 μs。全部时间依次为 `[2.10,3.82,4.38,8.42,5.23,10.57,10.22,68.53,82.81,98.38,86.98,96.74,15.69,13.23,13.05]` μs。
- 页面两位小数合计 522.78→520.15 μs；按同一页面最优时间估算均分 40.774→40.794，差值 +0.020。单次波动足以覆盖该差异；**不是重大突破**，不并入 main。下一实验应优先改变已知空闲核或重复读输入的结构，而不是继续调整消费者微流水。

## 2026-09-29 · CANNJudge CLI · 直接 batch 归约

- 分支 `experiment/direct-batch-reduce`，代码提交 `45efd1f`，`kernel.asc` SHA256 `e06ce50abb27dc9315d1b64437c2086473ffe53295c843c39aa61aa3feadefc2`。正式[提交 6abb2b8d694b590c3c6b89a2](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abb2b8d694b590c3c6b89a2)由官方 CLI 发起；dry-run 确认仅上传 `kernel.asc`，246853 字节，SHA 一致。
- 假设：历史探针第 4/5/7 点的单 M/N tile 可由一个 AIV 完成全 batch Max(N)→Sum(M) 并直接写 y，省掉 partial 写回、全核 `SyncAll` 和末级读回。第 4/5 点复用第 6 点已通过的 direct kernel；第 7 点对手写 Cube 路径增加 full-row direct specialization。其它分支仍用原逻辑。
- `python3 tools/validate_direct_batch.py`：探针范围的 1,458 组 batch/shape/core 边界排程和 192 KiB UB 显式分配模型通过；`git diff --check` 通过。模型不验证 Ascend 指令和性能。
- 正式结果：**Pass，15/15**，每点 `precision_ratio=1`。平台标注 CANN 9.0.0；精确 SoC、hidden shape/layout/dtype、实际 plan、编译命令和 msprof 未取得。平台时间单位按页面为 μs。

| 点 | 队友 498576 | direct | 差值 direct−队友 |
|---:|---:|---:|---:|
| 1 | 2.22 | 2.10 | -0.12 |
| 2 | 4.10 | 3.92 | -0.18 |
| 3 | 4.26 | 4.28 | +0.02 |
| 4 | 8.48 | 8.33 | -0.15 |
| 5 | 6.53 | 5.26 | -1.27 |
| 6 | 10.60 | 10.60 | 0.00 |
| 7 | 11.69 | 10.12 | -1.57 |
| 8 | 67.21 | 69.69 | +2.48 |
| 9 | 84.65 | 84.83 | +0.18 |
| 10 | 95.37 | 98.04 | +2.67 |
| 11 | 87.36 | 87.63 | +0.27 |
| 12 | 95.95 | 96.02 | +0.07 |
| 13 | 14.93 | 15.74 | +0.81 |
| 14 | 13.02 | 13.12 | +0.10 |
| 15 | 13.34 | 13.10 | -0.24 |

按页面两位小数时间与相同页面最优值估算均分 40.39→40.77（+0.38）；15 点时间合计 519.71→522.78 μs。单次运行的非目标点存在波动，不能把估算分差当已复现实测收益。第 5/7 点局部改善明确，但整体未达到用户要求的重大突破；暂不并入 main，也不再为小改动重复提交。

## 2026-09-28 · CANNJudge 正式提交 498576 · 队友合并 v3

- 提交：[BatchMatmulMaxSum / 498576](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3dbb694b590c3cd8f427)，2026-09-28 18:13:15 CST；分支 `experiment/teammate-c6-c10-c12-v3`，导入提交 `d9d74eb`。
- 用户附件逐字节导入并通过网页版代码编辑器提交。平台保存的 `kernel.asc` 复制回本地逐字节比对一致：244979 字节，SHA256 `ce2e12e425883fc207d0dd5d08a7a72b485c439b65fbbb8db33165905aecce52`。仅提交 `kernel.asc`；未修改赛题工程其他文件。
- 结果：**Pass，15/15**；每点输出错误占比 **0.00%**。平台标注 CANN 9.0.0；精确 SoC、设备核数、case shape/layout/dtype、实际 plan、编译命令和 msprof 未展示。

| 点 | 上次 498385 (μs) | 本次 498576 (μs) | 本次/上次 | 页面最优 (μs) |
|---:|---:|---:|---:|---:|
| 1 | 2.12 | 2.22 | 1.047× | 1.22 |
| 2 | 3.80 | 4.10 | 1.079× | 1.58 |
| 3 | 4.29 | 4.26 | 0.993× | 2.13 |
| 4 | 11.43 | 8.48 | 0.742× | 2.92 |
| 5 | 9.55 | 6.53 | 0.684× | 1.89 |
| 6 | 16.87 | 10.60 | 0.628× | 7.07 |
| 7 | 12.36 | 11.69 | 0.946× | 3.68 |
| 8 | 70.08 | 67.21 | 0.959× | 14.88 |
| 9 | 92.33 | 84.65 | 0.917× | 50.68 |
| 10 | 111.21 | 95.37 | 0.858× | 72.39 |
| 11 | 87.48 | 87.36 | 0.999× | 74.82 |
| 12 | 131.15 | 95.95 | 0.732× | 91.20 |
| 13 | 16.55 | 14.93 | 0.902× | 5.14 |
| 14 | 16.39 | 13.02 | 0.794× | 5.40 |
| 15 | 14.04 | 13.34 | 0.950× | 4.05 |

本次 13 点较快、2 点较慢；页面两位小数耗时合计 599.65→519.71 μs。按题面公式和页面显示的最优时间估算均分 34.80→40.39；页面并未公布这两个实际得分，且时间取整、单次提交和未知设备状态会影响推断。旧 CPU host 校验脚本依赖前版结构，不能用于当前附件；其编译失败不是本次设备失败。后续要记录对应 shape、路径、SoC 和重复测量，尤其第 1/2 点退化以及第 8 点与最优的差距。

## 2026-09-28 · CANNJudge 正式提交 498385

- 提交：[BatchMatmulMaxSum / 498385](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6aba3abb694b590c3cd6cbe3)，2026-09-28 18:00:27 CST；分支 `experiment/performance-structure-fixes`，代码提交 `a3c1f7d`。
- 平台保存的 `kernel.asc` 与本地文件逐字节一致：216575 字节，SHA256 `1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。通过网页版代码编辑器提交，仅提交 `kernel.asc`。
- 结果：**Pass，15/15**；每点输出错误占比均为 **0.00%**。平台标注 CANN 9.0.0；精确 SoC、设备核数、case shape/layout/dtype、实际 plan、编译命令和 msprof 未展示，均记为未取得。

| 点 | 本次用时 (μs) | 页面最优用时 (μs) | 本次/最优 |
|---:|---:|---:|---:|
| 1 | 2.12 | 1.22 | 1.74× |
| 2 | 3.80 | 1.58 | 2.41× |
| 3 | 4.29 | 2.13 | 2.01× |
| 4 | 11.43 | 2.92 | 3.91× |
| 5 | 9.55 | 1.89 | 5.05× |
| 6 | 16.87 | 7.07 | 2.39× |
| 7 | 12.36 | 3.68 | 3.36× |
| 8 | 70.08 | 14.88 | 4.71× |
| 9 | 92.33 | 50.68 | 1.82× |
| 10 | 111.21 | 72.39 | 1.54× |
| 11 | 87.48 | 74.82 | 1.17× |
| 12 | 131.15 | 91.20 | 1.44× |
| 13 | 16.55 | 5.14 | 3.22× |
| 14 | 16.39 | 5.40 | 3.04× |
| 15 | 14.04 | 4.05 | 3.47× |

比值根据页面两列四舍五入后的时间计算，只用于排序；未把它当作官方分数。正式结果证明该提交通过 15 点，不代表已取得本地可复现的 SoC 和 profiling 数据。下一步优先识别第 5、8、4 点及第 13–15 点的实际配置。

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

## 2026-09-21 · 队友 docs.zip 资料复核

- 仅资料算术/来源检查，无新 NPU 测量，无 kernel 改动。
- `python3 tools/audit_teammate_probe.py`：保存转录哈希一致；75 个粗维度/属性读数最大整数残差 0.144667；section 15 总时间复算 626.96µs。其构建归属来自队友材料，未独立验证。
- 旧 45 代理发现 14 个 K 非 8 倍数、第 14 点两个 M 超出后续推断范围，第 10 点属性存在冲突；生成 50 个合法本地验证配置，设备结果 PENDING。
- 来源、当前路径对应、旧报告矛盾与下一轮优先级见 `TEAM_PROBE_REVIEW.md`。不将历史 F12 耗时、旧路径表或单个 big08 profile 计为当前性能证据。

## 2026-09-21 · n-split-critical-work

父提交8fb1e72；kernel SHA256 `e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。新增65行kernel host调度代码；不改设备算术和事件代码。

- `python3 tools/validate_nsplit_work.py`：38,880调度配置与独立逐tile oracle一致，8,893个配置满足工作量准入；1,836行全负数据分片归约一致；宏0/1/1+TUNING及接入条件通过。数字按单套参数空间计，不将三档相加。
- 20 Cube 示例 B1/M1536/N1536/K1536：ns2→3，最忙worker tiles12→8、最大windows2→2；M3072：ns1→3、tiles24→16、windows4→4。均为CPU代理计数，非NPU时间。
- 继承回归：UB86,784、finalizer28,672、Ksplit361,152及classifier864配置通过。
- 24shape×2dtype×4layout设备清单已列；CANN编译、完整精度、正式15点、稳定态latency及msprof **PENDING**。
- 对照入口：`VALIDATION_REQUEST_nsplit_work.md`；不将这次计数改善计入性能成绩。

## 2026-09-22 · 已知问题集中修复（云端按用户指示暂缓）

分支 `experiment/known-issue-closure`；kernel SHA256 `d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。

- `31a5715`：earlySum多batch完整输出。finalizer模型扩展至49,152配置，全部唯一且完整；对照旧循环在该空间有928组遗漏、896组重复。
- `e579d8c`：manual不再申请未使用的库workspace，低核dot split的parts下限为1。
- `0d6fae8`：缓存包含全部11个Tune字段。同shape改参数不再复用旧计划。
- 追加保护：offset-zero scratch使用后标记库前缀脏；重新进入Matmul时同步并清零前缀；保留跨无workspace计划的脏状态。首次新分配不等待旧scratch使用者，因为不存在旧分配；实际resize与用途转换仍同步。
- 完整host控制流模型76,424配置通过，production和TUNING分别运行。fake tiler不构成CANN资源可行性证明。
- 真实run_kernel/cache/release代码的CPU替身检查通过：同shape调参、context隔离、复用/幂等释放、malloc/memset/sync/free失败、generic/manual/dot/GEMV之间用途转换及重试。
- 统一计划覆盖151shape×2dtype×4layout；设备未运行。CANN/NPU/正式15点/latency/msprof依然PENDING。本记录没有新增任何NPU性能数字。

## 2026-09-22 · dual-consumer-fold 设备端优化

- 分支 `experiment/dual-consumer-fold`，父版本 `35a86eb`；kernel SHA256 `8f848c4869d90f0da7a955b14b457a47ecc9a09c41e515c95efa17562916d29e`。
- `324a6a0` 将历史消费流水候选移植到当前修复版；`00a91b4` 新增原地树形tile Max，复用已有UB双缓冲。
- 默认 pipeline=2/fold=1；两条完整K dual路径接入。256列tile的WholeReduceMax调用4→1，Vector屏障8→4；无新增workspace。这是操作计数，非性能结果。
- 六种开关组合各76,800窗口配置与34,816全部列尾/行跨度配置通过；3,840抽象协议调度通过。0/0与父循环CPU轨迹一致，其余模式结果及GM读取地址一致。
- 源码逆替换验证：host planner、Cube侧、缓冲分配、末级输出、其它算子路径与父版本逐字一致。无需用host stub的重复大网格充当本次设备验证。
- CANN/NPU/正式15点/latency/msprof **PENDING**。现场依赖待确认：CANN9队列事件、Matmul flag9握手、VECIN原地Max、A2/A3分别运行。
- 执行单：`DUAL_CONSUMER_OPTIMIZATION.md`。本机未新增任何NPU耗时或速度结论。

## 2026-09-22 · cube-panel-reuse

- 实现 `bc3f7cf`，父 `48e37c7`，SHA `e440e1b3d915ba61f696059cd3af0efdee6b8d087aee04ef7a49ba40ef2a637b`；kernel新增255行。
- 新Cube生产者按N组/K面板重排，双L0C累加，A跨两个N tile复用，可选全K A常驻L1；接入既有manual AIV与Fold Max。查询实际片上容量，保留旧路径与四档对照。
- 444个物理块模型执行通过；四布局、三种新模式、K8非16对齐、M/N尾、长K、多task、奇数N组；逐元素C、补零、队列/事件计数与读取量检查。小整数输入不是FP16/BF16设备编码/舍入模拟。
- host四档production/TUNING各76,424主网格配置与额外资源检查；模式1/2/3选择11,989次，模式3中9,963次resident。fake tiler不能证明CANN可用。
- 前版消费模型与finalizer模型通过；没有新增NPU性能数字。模式1→2的A读取及L0A搬入量在成对tile上减半；resident进一步减少A GM重复读取。**不能据此报告对父版Matmul库的流量降幅/提速**。
- CANN9/A2/A3/正式15点/latency/msprof全部PENDING；四档同机执行单在 `CUBE_PANEL_REUSE.md`。用户仍暂缓云端执行。


## 2026-09-22 · hierarchical-k

- 分支 `experiment/hierarchical-k`，实现 `d64d0c1`，父 `73ed463`；kernel SHA256 `771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。
- L1面板K为L0 K的2/4倍（最多512），B1四缓冲、A1双缓冲或常驻；容量不符保留父路径。`BMMMS_L1_K_PANELS=0/1`默认1。
- `validate_cube_panel.py`：456父producer执行及584两级K执行通过；逐元素C/补零一致、读字节/L0搬运/MMAD计数不变、ND2NZ调用减少；含四布局、尾块、BK112、K8192。
- `validate_host_plan.py`：六种宏组合×production/TUNING，各76,424主网格与额外内存边界通过。模式2/H1选中两级K 9,403次，模式3/H1 7,714次。计数包含额外检查，不是正式case覆盖率。
- 同步CPU模型和fake tiler；CANN编译、真实队列/事件、NPU精度/正式15点/latency/msprof全部PENDING。较少DMA调用可能被TX1切片LoadData及队列开销抵消，没有新增NPU性能数据。
- 设备执行入口 `HIERARCHICAL_K.md`；按用户指示云端暂缓。main kernel未合并。


## 2026-09-22 · performance-structure-fixes

- 代码 `a3c1f7d`，父 `3ca0d7c`；SHA `1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。
- 完整连续TX1切片LoadData 8→1；单N组无收益驻留取消；各C首次MMAD前才获取自己的释放事件；两份K主循环合一。
- 显式tile/window/ns最后应用且拒绝静默覆盖；split-K完整M/N保护。默认P0及预处理隔离保留原家族，显式P2/P3提供修复后候选。
- CPU：456常规+584两级K+2针对性执行通过；逐元素C/补零/地址/事件收支/操作量检查。六种host宏组合production/TUNING各76,424主网格及容量边界通过；pin与预处理、缓存、N/K/UB回归通过。旧nsplit模型抽取误包含PanelL1Capacity导致的CPU编译错误已修正。
- P3（显式）驻留选择6,026次、P3/H1两级K 8,410次；包含额外边界，不是正式case命中率。kernel净减少15行，不能作为速度证据。
- CANN编译、真实异步事件、FP16/BF16设备精度、正式15点与性能全部PENDING；没有新增NPU耗时。设备入口 `PERFORMANCE_STRUCTURE_FIXES.md`。
