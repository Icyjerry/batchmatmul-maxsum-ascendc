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
