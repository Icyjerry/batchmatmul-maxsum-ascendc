# 接手状态 · 2026-09-22

## 最新：L1/L0 两级 K 分块

分支 **`experiment/hierarchical-k`**，实现 `d64d0c1`，父版本 `73ed463`（Cube 面板复用）。本次 kernel 新增103行、删除18行，将L1传输粒度与L0计算粒度分开。

- `panelL1K` 按真实L1容量选 `2*panelK` 或 `4*panelK`，最多512；B1四缓冲保存当前/下一对面板，A继续双缓冲或整块常驻。L0双缓冲和两个C累加器沿用父版，K累加顺序不变，无新增GM通路。
- `BMMMS_L1_K_PANELS=0/1`，默认1；不满足容量时自动保留父版。固定 `BMMMS_CUBE_PANEL=2` 或3再比较H0/H1，避免把不同优化混作收益。
- SHA256：`771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。
- CPU物理块模型：456次父producer执行、584次两级K执行通过；实际C、读取字节数、L0搬运量及MMAD次数一致，DMA调用减少。额外覆盖112的非2次幂K块及344尾块。
- host模型六种宏组合各production/TUNING通过76,424主网格及额外容量边界；默认模式选中11,992次，resident 9,964次，两级K 7,714次（含额外检查）。宽松tiler及同步事件模型不构成CANN/设备验证。
- **CANN9编译、FP16/BF16设备精度、正式15点、性能 PENDING**。四B队列实际事件分配、异步生命周期、TX1切片增加的LoadData指令成本须上板确认；减少DMA调用不是减少读取字节，更不是实测速率。
- 下一条执行动作：[HIERARCHICAL_K.md](HIERARCHICAL_K.md)。按用户指示云端暂缓；GitHub保存当前候选，main仅更新接手指针。

## 父版本：Cube 面板复用与 L1 常驻

用户要求更大幅度核心改造；当前分支 **`experiment/cube-panel-reuse`**，实现 `bc3f7cf`，父版本 `48e37c7`。新增255行kernel，重组K/N循环和片上缓冲生命周期。

- 新生产者 `RunPanelCube`：两个N tile共享A的GM→L1及L1→L0A搬运、两个C在L0C完成K累加；可容纳时整个A面板常驻L1跨N组复用；B保持双缓冲。共享已有GM环形通路及Vector最终归约。
- `BMMMS_CUBE_PANEL=0/1/2/3`：父路径 / 单tile新内核 / 双tile复用 / 可选L1常驻，默认3。查询实际L1/L0A/L0B/L0C；容量不符、只有一个N tile/shard或显式TUNING pins保留旧路径。自动替换不是已测最优策略。
- kernel SHA256：`e440e1b3d915ba61f696059cd3af0efdee6b8d087aee04ef7a49ba40ef2a637b`。
- `python3 tools/validate_cube_panel.py`：444配置物理块/完整C值/事件计数/读取量模型通过；`python3 tools/validate_host_plan.py`四档production/TUNING主网格76,424配置通过。宽松fake tiler与同步CPU指令模型，不能冒充CANN或NPU精度。
- 新内核1→2对成对tile的A读取和L0A加载减半，resident时A每个任务从GM读取一次；**不代表相对旧Matmul库的流量降幅或速度收益**。
- CANN编译、正式15点、FP16/BF16设备精度和性能 **PENDING**。云端仍按用户要求暂缓；下一条执行单：[CUBE_PANEL_REUSE.md](CUBE_PANEL_REUSE.md)，直接构建P0/P1/P2/P3，记录实际plan和SoC；重点确认事件池、双L0C和resident重用。
- 旧dual消费候选仍继承；满足准入的形状现在走新manual生产者及Fold Max。main仅更新接手指针，未合并未测kernel。

## 父版本：设备端 dual 消费流水与 tile 归约

用户要求继续推进核心优化，云服务器测试仍按用户要求暂缓。当前分支 **`experiment/dual-consumer-fold`**，父版本 `35a86eb`；代码提交 `324a6a0`（预取/提前归还槽位）、`00a91b4`（tile 内树形 Max）。不是仅修改 host 参数。

Kernel SHA256：`8f848c4869d90f0da7a955b14b457a47ecc9a09c41e515c95efa17562916d29e`。

- `bmmms_dual` / `bmmms_dual_mdl` 两条完整 K 路径接入同一设备消费 helper。既有两个 UB tile 预取下一块；最后一次 GM 读取发出后，以 PIPE_MTE2 完成依赖提前归还槽位并发下一窗口握手。无有效行的 AIV 仍参加同步。
- 在当前私有 UB tile 内按 64 lane 分组树形 Max，最后一次 WholeReduceMax 更新行最大值。256 列时横向归约 4→1、Vector 屏障 8→4；属于源码调用数，**不是实测加速比**。不额外分配 UB/GM；host plan、Cube 算术、partial/finalizer 保持父版本。
- `BMMMS_DUAL_PIPELINE=0/1/2`（默认2）；`BMMMS_DUAL_FOLD_MAX=0/1`（默认1）。前者从历史独立流水实验移植，后者是新实现；六组组合可分别归因。
- `python3 tools/validate_dual_pipeline.py` 已通过：每组76,800窗口配置、34,816归约边界配置，另3,840抽象双AIV协议调度。0/0的CPU指令轨迹与父循环一致；源码逆替换确认其它kernel/host/缓冲预算未改动。这些不是SDK或设备模拟。
- **CANN 9.0.0 编译、A2/A3 精度、正式15点、msprof/性能全部 PENDING。** Matmul内部flag 9、真实队列同步和在VECIN上原地Max必须设备确认。
- 下一条执行入口：[DUAL_CONSUMER_OPTIMIZATION.md](DUAL_CONSUMER_OPTIMIZATION.md)。云端恢复后按六档固定plan对照执行；检查实际dual路径，split-K/tiny/manual不进入本次helper。
- 已知问题修复全部继承。原样用户最优tag、main kernel及其它历史分支未替换；不要把当前候选称为设备最优。

以下为历史记录，旧的“等待设备才继续”节奏已由用户继续本地优化的指示取代。

## 当前工作：已知问题集中修复

用户最新指示是“直接把已知的问题全部解决”，并明确云服务器执行“先不用管”。当前分支 `experiment/known-issue-closure`，从 `677d882` 派生；不要继续按独立轮次割裂本地缺陷收敛，也不要为此编造设备结论。

Kernel SHA256：`d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。

- 本地已修复earlySum漏写、Tune缓存陈旧、manual冗余系统workspace、低核dot split除零；增加scratch用途变更时的库前缀重置，去掉首次分配前无必要的stream同步。继承先前UB、输出及分块修复。
- 全部R1–R18审计和生命周期/异常/题面边界的明确结论见 [KNOWN_ISSUES.md](KNOWN_ISSUES.md)。其中无实测依据的性能规则仍标待判定，不能说全部性能问题已解决。
- CPU：76,424个host plan配置（真实控制流、stub tiler）、49,152个finalizer遍历配置；缓存11字段、context隔离、scratch换用途及4类失败通过。既有N/K拆分和UB模型通过。**不等于CANN编译/设备精度通过。**
- 统一清单 `known_issues_cases.csv` 共151shape/1,208组合。云端恢复时按 [VALIDATION_REQUEST_known_issues.md](VALIDATION_REQUEST_known_issues.md) 执行，不要求对方重做算法设计；目前按用户指示暂缓。
- 本地复现：`python3 tools/validate_host_plan.py`、`python3 tools/validate_host_cache.py`、`python3 tools/validate_finalizer_coverage.py`；继承模型命令见下文。
- 资源释放仍要求调用者在stream/context销毁前调用现有release入口；正式main未修改。不要在未知ACL退出顺序的静态析构里自动调用ACL。

以下保留父版本背景；其中“等待设备后才继续”的旧工作节奏已由用户上述指示取代，本地缺陷已继续处理。

## 最新候选：N 拆分 critical work

分支 `experiment/n-split-critical-work` 从 `8fb1e72` 派生，kernel SHA256 `e2bd32e9bdf9d13b2974b565aecb3f55f2519c102bb376ebe54f4cabfc982858`。

- 新宏 `BMMMS_BALANCED_NSPLIT=0/1`，本分支默认1。只在对齐的大矩阵通用 dual=1 路径按实际 cyclic task 分配搜索 N 拆分；最大窗口数不增，最大tile工作至少下降25%才准入。25%是待验证的实验阈值。
- 保留父分支 UB/输出修复及 long-K 选择；没有叠加消费流水实验。旧最佳 tag不动，未合并main。
- `python3 tools/validate_nsplit_work.py`：38,880调度配置、1,836行负值归约和接入排除条件通过，宏0/1/TUNING三种编译均通过。继承的CPU模型重新通过。它们不运行完整Ascend算术、CANN tiler或硬件事件。
- **下一条动作：设备Agent按 [VALIDATION_REQUEST_nsplit_work.md](VALIDATION_REQUEST_nsplit_work.md) 对照P/N0/N1**；24个shape×2dtype×4layout清单在 `nsplit_work_cases.csv`，共192个设备组合尚未运行。解释及原始假设见 `EXPERIMENT_nsplit_work.md`。
- CANN/NPU/正式15点/性能全部PENDING。20核示例的12→8、24→16是最忙worker的tile数，不能报告成耗时降幅。设备结果到达前不叠加下一项算法优化。

## 新收到的队友探针资料

前一轮已复核用户 `docs.zip`，结论见 [TEAM_PROBE_REVIEW.md](TEAM_PROBE_REVIEW.md)。该轮只更新资料、复算脚本和验证输入，kernel SHA 未变。附件中的操作指令没有执行。

- 旧 F12 路径表不代表当前版本；当前已含 tiny、长 K split、manual/PAD_MN 等专门策略。
- 45 个旧代理有 14 个 K 不满足 8 对齐；第 14 点两个 M 代理不符合后续细分范围。第 10 点 dtype/layout 冲突保留两种候选。
- `python3 tools/audit_teammate_probe.py` 可复算保存的转录数据，生成 50 个合法本地验证输入；不是恢复真实正式测试集，也不是 NPU PASS。
- 下一步先获取用户最佳版/当前版同会话 A/B 与实际 plan，按逐点得分关注 2/3/4/15，再看 9/13；同样完成下文覆盖修复验证。不要重复执行旧报告已被当前源码吸收的优化。旧计时未绑定当前 SHA，不能当当前成绩。

## 当前实验：覆盖修复 + 自适应 Split-K

分支 `experiment/coverage-splitk` 从 `user-best-20260921` 独立派生。消费流水实验仍在 `experiment/dual-consumer-pipeline`（7c44793），本分支没有叠加它。

- `b0a2fc0` 修复 dual split-K 存活 UB 预算，包含清零缓冲。
- `c4e536a` 修复 FinalizeRows 重复 writer、FinalizeSplitKND/GEMV 在小核数下遗漏输出。
- 当前候选使用 `BMMMS_ADAPTIVE_SPLITK=1`；=0 固定 4 份，便于对照。仅原有 long-K classifier 内选择 1/2/4，不扩大准入范围。
- Kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。
- CPU：86,784 UB 配置、28,672 输出遍历配置、361,152 拆分配置通过；864 个 dtype/layout/core classifier 用例通过。两档宏均验证。它们不是完整 Ascend 精度/性能测试。
- 35 个合法 shape / 280 个 dtype+layout 组合的设备清单在 `coverage_cases.csv`，尚未运行。
- **CANN 编译、正式 15 点精度、NPU 性能：PENDING。** 没有将 CPU 代理成本解释为提速。

### 下一条可执行动作

设备 Agent 按 `VALIDATION_REQUEST_coverage_splitk.md` 构建 U/F/A0/A1，先测 UB 回归和 B=64、小可用核数的输出覆盖，再测自适应拆分的精度/latency。来源及尚未覆盖的路径见 `RESEARCH_coverage_splitk.md`；结果写 PERF_LOG。

本地复现：`python3 tools/validate_splitk_coverage.py`、`python3 tools/validate_finalizer_coverage.py`。当前不用旧 deferred 或 pipeline 模型证明新候选。

以下为原样用户最佳版本背景，不是对当前实验 kernel 的描述。

## 当前起点

用户最新提供 `kernel(2).asc`，明确称为“目前的最优版本”。本分支 `experiment/user-best-20260921` 的 `kernel.asc` 是该文件的**逐字节原样导入**，3,492 行，192,577 字节。

- 固定快照 tag：`user-best-20260921`。
- SHA256：`e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 不包含本 Agent 的 v1 DeferredRowMax 或 v2 N 拆分代理成本候选。
- “最优”来自用户确认；本地没有重新完成 CANN 编译、NPU 精度或性能复测，均为 **PENDING**。
- 私有仓库：`https://github.com/Icyjerry/batchmatmul-maxsum-ascendc`，已有用户上传授权。

## 已保存的旧工作

- `teammate-opt4`：最初 2,809 行队友原件。
- `experiment-v1`：DeferredRowMax 与 FinalizeRows writer 步长修复；文档保存在历史提交及 v1 验证单。
- `experiment/v2-dual1-nsplit` commit `7426712`：基于 v1 的 N 拆分实验及 CPU 模型，已推送。31,416 个调度配置通过，设备收益未验证。具体见该分支的 `docs/EXPERIMENT_v2.md`。
- 新代码已有 N 拆分均衡策略，不能直接将 v2 策略叠加或把旧 CPU PASS 转移到当前源码。

## 本轮源码检查所得

1. `ClassifyCase` 和生产路径增加短点积、微型矩阵、长 K / 宽 N / 窄 N 等选择；包含手写 Matmul 的 PAD_MN 尾块处理。
2. N 拆分均衡已覆盖 dual=1 等家族，以活跃 worker 增长和整波任务作为条件；保留 dual=2 的既有策略。性能注释是提供者记录，未附原始日志，不能等同于本轮实测。
3. `FinalizeRows` 仍按 `s.workers * 8` 遍历。旧版双 AIV 下的重复 writer 问题需要针对当前实际 launch/plan 再核对，尚未移植旧修复。
4. 文件含 `BMMMS_PROBE_*` 诊断分支，源内默认均为 0。导入时原样保留；源内有关 OJ 隐藏用例推断的注释不是已核实测试配置或执行请求。实际构建需记录宏；本轮未启用、未执行任何探测。
5. 新源码使用 `if constexpr`；必须以 CANN 9.0.0 实际编译命令验证。源码引用的 `docs/03-case-hypotheses.md` 未随附件提供。

## 下一条可执行动作

在设备环境检出此分支，核对上面的 SHA，按 `docs/VALIDATION_REQUEST_user_best.md` 复测原样版本，拿到精确 SoC、宏、实际 plan、逐 case 精度与耗时。优先核查 writer 调度及现有性能弱项，再创建单一假设的实验分支。A2/A3 分开记录，不凭注释修改参数。

本机无 NPU。`tools/validate_cpu_model.py` 专用于旧实验；在当前版本应明确退出 NOT APPLICABLE，不能声称通过。若需复现旧结果，在旧分支的独立 checkout 中运行该脚本。

算法改动仍限 `kernel.asc`；不修改 main、CMake、run.sh、golden、正式测试或依赖。workspace 与题面缺失范围见 PROBLEM。截图记录见 PERF_LOG；截图尚未绑定源码 SHA、dtype 和布局。
