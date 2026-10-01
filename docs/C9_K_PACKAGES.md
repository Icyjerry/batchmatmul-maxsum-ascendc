# C9完整A1驻留与B K packages · 2026-10-01

## 来源和范围

用户提供队友 `kernel_c9.asc`，SHA `83d40a7171a2a770a92115564ad3f4366f0386a47880fce0139c83e9442d7d3a`（6712行），报告第9点“68s”，本次暂按68μs理解。没有队友正式ID/原始结果/硬件信息，**该数是用户报告，不是本次实测**。

从正式15/15通过的 `0d4bd04` 分出 `experiment/c9-k-packages`，当前kernel SHA `5dcb7230bef7e8935aabe6c6c80560dfb0f2d1103b5a5ea223b217bdbe075ebd`。只提取队友C9 kernel、实际容量selector、FP16/NT/dual20 dispatch和C9 measured predicate整个历史桶覆盖；未整份覆盖其它路线。移除selector不能进入该专用kernel的streaming-A fallback，device body/Vector保留队友原逻辑。

假设：在已有完整A驻留下，B的L1 K包大于原L0 BK可减少ND2NZ发起；晚获取GM ring credit可让第一tile的矩阵乘与旧slot消费重叠。调用数或源码等待位置**不证明NPU收益**。该组合有用户报告改善，值得一次结构候选正式对照，不提交相近参数扫描。

## 实现与容量

- A1完整K驻留，非转置A一次ND2NZ，原BK矩形Load3D到A2。
- B1两package buffer，包K取实际 `TCubeTiling.baseK*stepKb` 并按BK对齐、至少2BK；实际L1不足逐BK缩小，不能大于BK则dispatch回退旧dual20。
- 每个B1包按 `(innerK*align16(validCols))` 加载B2；只在完整K后Fixpipe和Max。L0A/B仍原BK双buffer，C原1/2 buffer。
- 第一个N tile的完整K计算后才等待原window slot credit；Vector全部有效N读完且两个AIV均释放后才复用。
- 沿用原system/partial/ring和workspace尺寸，没有新GM通路或cross flags。物理核数、L1/L0/UB实际查询；20核配方保留队友历史条件，不硬编码设备总核数。
- 调度谓词仅扩大FP16/NT/B1/M[2048,4096)/N[1024,2048)/K[1024,2048)在20核的历史配方覆盖；其它dtype/layout区域保持通过父版。

## CPU/公开源码验证

命令：

```sh
python3 tools/validate_c9_packages.py
python3 tools/validate_c9_packages_public_tiler.py --source /private/tmp/ascendc-api-adv-review
```

- 177实际producer：物理NZ/ZZ/ZN映射、双C、全负、B配对、M/N/K尾、K8非16尾、K8192、K package边界、ring哨兵及事件收支。
- 177延迟MMAD：在M事件强制完成时读取live A2/B2/C，检查提前复用；MTE1仍同步，未模拟CANN native queue事件。
- 9216实际C9内联Vector窗口：延迟GM DMA、两AIV先后顺序、返还credit后破坏性ring复用、有效列Max和Sum。
- fake host production/TUNING各2560控制配置、128新dispatch；公开固定8.3 `c7dfa2d901a314e1ae69e9cef850057593f2a58b`真实tiler同网格各2560/128。包括实际核心、容量收缩到BK回退、内存变小、无效geometry/workspace保护。
- 移除上述C9三个插入区并恢复一条predicate后，kernel与父版逐字一致；无main/CMake/run/golden/依赖修改。
- 第一次fixture错误把不满足L1的package直接喂producer触发容量assert；修正fixture为只执行有效容量，保留host不够容量的回退断言。fake tiler缺少stepKa/Kb用本模型局部shim补充；真实公开tiler保留原算法/字段。

**CPU不是CANN编译、FP16硬件精度、硬件异步协议或性能证明。候选代码 `d19af3d` 的正式任务已Pass，详见下方正式结果；dry-run只含kernel.asc且SHA一致。** 没有actual shape/plan/SoC/profile；正式单次对照也不能证明稳定收益。

## 保留的B-stage实验

`experiment/tt-b-stage` 的 `5b58c96` 保存一个2BK B1 stage、原总L1预算的TT WIP；180物理布局/440 producer/420旧producer/160位模式及fake host通过。延迟MTE1+native queue/CANN/NPU仍PENDING，未正式提交、不混入本候选。

## 提交前执行计划（已完成）

独立官方template dry-run确认仅kernel.asc、SHA一致；commit/push后CLI一次正式提交，立即保存ID并查询同一ID至终态。与父版第9点83.11μs、第8点59.66μs比较；无收益则归档，不把用户报告当作自身结果。

## 提交记录

正式任务 `6abe2939694b590c3cdc011a`，代码 `d19af3d`，kernel SHA保持上文。查询：

```sh
python3 /private/tmp/query_bmmms_submission.py 6abe2939694b590c3cdc011a
```

## 正式结果

代码 `d19af3d`，[正式任务 6abe2939694b590c3cdc011a](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe2939694b590c3cdc011a) **Pass，CANN编译成功、15/15、precision_ratio全部1**。kernel SHA与上文一致。耗时（μs）：

```text
[2.16, 4.15, 4.51, 5.54, 5.39, 10.64, 10.26, 59.27, 68.54, 96.11, 88.66, 97.11, 16.38, 13.44, 9.75]
```

第9点通过父版83.11→68.54μs，单次耗时降低17.5%、1.213x，复现用户报告的队友约68μs水平；不是相对队友68μs的新增提速。第8点父59.66→59.27μs，TT保留，没有重复A/B，不宣称0.39μs是稳定改善。
此次正式评测证明组合版通过15点且出现上述单次耗时；没有actual shape/plan/SoC/profile或重复对照，不能证明隐藏case一定命中新路径或把不同改动分开归因。其它路径byte-identical，时间变化不归因；theory_score/score未用于宣称排行榜分数。
没有活动评测任务。原始JSON/CPU日志本机Git忽略目录 `artifacts/c9-k-packages/`，mode700/600。

下一从本组合通过版保持队友C9+TT，继续研究第8点的结构瓶颈。B-stage WIP保留 `experiment/tt-b-stage` / `5b58c96`，不能不经delayed MTE1/native queue检查直接混入；后续正式候选必须保持这里的C9组合，以免丢掉收益。主分支/历史标签未移动，整体极限优化目标仍有空间。
