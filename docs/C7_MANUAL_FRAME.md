# C7 完整输入、手动片上缓冲与紧凑入口

## 假设与范围

父版 `0fe38f0`，实现仅修改 kernel.asc 的三个新增区域：32byte参数/独立混合入口、容量选择函数、原 partial 建好后的 launch override。删除这三个区域逐字恢复父版，MakePlan、workspace 分配、grid、C1–C6/C8–C15及其它布局/dtype路径未修改。正式 case 编号只是历史桶名称，没有 actual shape/plan 元数据，不能保证路径命中。

采用此前通过的完整输入 Cube `d793083` 和单C消费 `75c4d8f` 的数学/几何/归约，把 TPipe、TBuf 初始化、队列和运行时事件分配替换为队友 single_tile 已采用的 LocalTensor 物理缓冲与显式事件。原两次候选分别只有波动范围内的小改善/无改善，本次假设是进一步降低入口与初始化成本，不能把之前通过或减少调用数当成本次性能证据。

- 固定 TF FP16 历史桶 B16..31/M32..63/N128..255/K256..511、合法K8；原 plan 必须 dual3/14，单M/Ntile、单N/K分片、window1、完整 padded MP/NP。
- 每 batch 完整A/B一次ND2NZ；A留L0A，每个N slab完成全KP MMAD，写不重叠C0 NZ区域；完整C Fixpipe后才交Vector。
- N slab保留旧公式，只按实际L0B容量收缩，无双B2/参数扫描。L1/L0A/L0B/L0C/UB均查询；不足时退回父路径，全部显式TUNING pins不覆盖。
- 单AIV保留一个C和4组行最大值，精确N树形Max→一次有效M Sum→4byte y；另一AIV仅消费ready/返还信用。闲worker三核均提前返回。
- 原partial前缀、每worker双GM ring、ready0/1/free4/5不变；无新GM通路。显式硬事件保护B2/A2 MMAD最后读取、双C0 Fixpipe、C被Vector读取、GM信用及sum被MTE3读取；无TPipe析构，用PIPE_ALL终结。
- 原Schedule96byte变为独立32byte参数；原host plan没有变更。

以代理48×192×384、64KiB L0B为例：完整输入ND2NZ2次、A2加载1次、80列N slab的MMAD3次。父分K路径相应12/6/6。代理调用数不是本次实际shape、设备时间或加速预测。

## 来源与已有证据

- 用户队友 `9ab2312:kernel.asc` manual LocalTensor/显式硬事件及 `889afe0` 的已通过移植；本次沿用其初始化和结束规则，不是发明新API。
- 完整输入 Cube 与原矩形Load3D：`docs/C7_FULL_INPUTS.md`，旧候选正式15Pass；单C树形归约：`docs/C7_LEAN_VECTOR.md`，旧候选正式15Pass、没有性能收益。
- 既有 [Goto/van de Geijn论文](https://www.cs.utexas.edu/~flame/pubs/GotoTOMS_revision.pdf) 的准备成本摊薄，以及 [FlashAttention-2](https://arxiv.org/abs/2307.08691) 减少非矩阵乘工作，作为推导此Ascend实现的动机，不套用论文硬件/速度数字；此前调研已核对。

## CPU验证

```sh
python3 tools/validate_c7_manual_frame.py
```

直接抽取当前完整入口，不以手写理想算法代替生产代码：

- 264立即+264延迟live MMAD：物理L1共享范围、NZ/ZZ/ZN、满K与N slab、K8/M/N尾、负数、跨batch/闲核、每个C独立点积核对、完整padded C、immutable输入、scratch/ring guards与硬事件收支。
- 1296实际Vector：三个独立引擎队列、三种优先顺序、信用返还即破坏GM、C/sum generation、闲核零分配、唯一合法4byte y。
- 七Vector负控制：删除四依赖Fence、无N尾mask、无PIPE_ALL结束、最后GM读之前返信用；均需拒绝。
- 两Cube负控制：删B2最后MMAD读等待、删输入ready；均需拒绝。
- production/TUNING各6144真实host分派配置/768选择：实际查询资源、L0B缩小32KiB、边界拒绝、workspace不足回退、全部pins、原plan/GM不变。

模型Load3D/Fixpipe同步、Cube信用抽象、Vector Cube/伴随核合成；整数计算不模拟half编码、原生舍入、全部配置寄存器或原生硬件调度。不是CANN9编译、正式精度或性能结果。日志本机忽略 `artifacts/c7-manual-frame/cpu.log`。

## 正式验证请求

独立官方原模板只换kernel，其余8文件逐字一致；commit/push后一次CLI提交，立即保存ID并查询同一任务至终态。先CANN编译/15精度，再比较父C7三次9.59/10.28/10.14 μs，中位10.14、极差6.8%；落在原9.59–10.28区间不能叫突破。其它路径源码没变，不归因耗时浮动、不改main或测试适配失败。

CANN9编译、NPU精度、性能 **PENDING**。若有条件另采actual shape/dtype/layout/plan、SoC/核数、CANN、误差、repeat、msprof和交错A/B；CLI结果缺这些元数据时如实保留限制。

正式任务 **`6abe9804694b590c3c18f362`** 已创建，代码 `c17077f`，kernel SHA保持。下一仅查询 `python3 /private/tmp/query_bmmms_submission.py 6abe9804694b590c3c18f362` 至终态；观察超时不能重复提交。CANN9编译/NPU精度/时间PENDING。
