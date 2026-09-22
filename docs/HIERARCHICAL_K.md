# L1/L0 两级 K 分块

分支 `experiment/hierarchical-k`，实现 `d64d0c1`；父 `73ed463`。
kernel SHA256：`771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。
**CANN9/NPU/正式15点/性能 PENDING，云端按用户要求暂缓。**

## 假设与实现

父版 `RunPanelCube` 的每次GM→L1传输只有一个L0 K块。小块多时会产生大量ND2NZ调用。本版一次传输较宽L1面板，再按原来的K块逐次加载L0、执行MMAD。完整K完成后才输出C并做Max；配对、归约顺序和GM环形通路沿用父版。

- L1 K优先取L0 K的4倍，再试2倍，最多512；不超过当前K所需的整L0块数。L0块仍由实际L0A/L0B容量和LoadData重复数约束。
- A非驻留：两个L1面板；A驻留：整个query面板一次载入。保留父版驻留选择，不能为扩大B面板挤掉已选驻留A。
- B使用四个L1缓冲，当前两个N tile和下一对面板并存。当前面板在最后一个L0切片搬运后释放，随后补入未来面板；L0A/B仍双缓冲，两个FP32 C累加器不变。
- 一个N shard末尾只有单tile时仍正确排队、排空；K非16倍数、M/N尾块按原语义补零。全K顺序不改，没有split-K或额外GM中间结果。

设BM/BN为tile、K1为L1面板、Kp为完整K向16取整。显式L1预算：

| A模式 | A字节 | B字节 | 余量 |
|---|---:|---:|---:|
| 分段 | `4*BM*K1` | `8*BN*K1` | 1024 |
| 常驻 | `2*BM*Kp` | `8*BN*K1` | 1024 |

总量超过实际L1容量时不启用。B的TQue深度和InitBuffer数量均为4，A队列为2；这不是仅调大一个host参数。

## 研究依据和限制

- [CATLASS官方优化指南](https://catlass.readthedocs.io/en/latest/1_Practice/11_matmul_optimization/)讨论L1/L0分层分块、双缓冲容量与预取；其实现建议的K层级比例不能当作本题最优值。本版据容量选2/4倍并保留对照。
- [CANN 9.0.0 TQue API](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0137.html)区分连续入队/出队所需的队列深度与物理bufferNum。本版确有最多连续4次B预取；真实事件分配仍需设备编译和执行确认。

本改动只减少搬运调用次数，读取字节数、L0加载量与MMAD数量不变。较大L1占用、四队列开销和TX1非连续K切片的多条LoadData，可能抵消收益。CPU同步模型不能证明实际流水重叠或无死锁。

## 本地检查

```sh
python3 tools/validate_cube_panel.py
python3 tools/validate_host_plan.py
```

实际kernel函数抽取模型：456次父producer执行、584次两级K执行通过，逐元素C（含补零）一致，字节数/L0搬运/MMAD计数不变，ND2NZ调用减少。包含四布局、驻留/分段、奇数N组、多task、空worker、BK112、K尾及8192。输入为可精确表示的小整数；不是FP16/BF16编码或设备舍入模型。

host真实控制流配宽松tiler：宏组合(P0,H1)、(P1,H1)、(P2,H0/H1)、(P3,H0/H1)，各production/TUNING主网格76,424配置及额外容量检查通过。默认P3/H1有7,714次选择两级K，P2/H1有9,403次；这些计数含额外边界，不代表15点覆盖率。

## 云端可直接执行

固定源码SHA，沿用已有harness、正式golden和容差，禁止probe延时。先比较两对：

| 构建 | 编译宏 | 用途 |
|---|---|---|
| P2H0 | `BMMMS_CUBE_PANEL=2 BMMMS_L1_K_PANELS=0` | 分段A父路径 |
| P2H1 | `BMMMS_CUBE_PANEL=2 BMMMS_L1_K_PANELS=1` | 分段A两级K |
| P3H0 | `BMMMS_CUBE_PANEL=3 BMMMS_L1_K_PANELS=0` | 可选驻留A父路径 |
| P3H1 | `BMMMS_CUBE_PANEL=3 BMMMS_L1_K_PANELS=1` | 默认候选 |

宏需用编译器`-D`传入，确认verbose命令生效。其它NSPLIT、SPLITK、消费宏固定；不启用会取消自动选择的TUNING pins。P0整体对照和专项shape列表见 [父版执行单](CUBE_PANEL_REUSE.md)；追加 `(1,33,97,344)`、`(1,128,1024,8192)`，各两dtype×四布局×普通/全负输入，所有构建先过正式15点与重复一致性。

记录精确SoC、CANN、四种内存容量、SHA、宏、误差和实际plan，尤其 `panelK/panelL1K/panelGroup/panelResident`。`panelL1K=0`是回退，不能拿其耗时评价两级K。先检查四B队列、显式事件池、面板最后切片释放及双C累加。

精度通过后固定设备、预热50次、计时200次，交替四档至少5组，记录median/p95与MTE2/MTE1/MAC/Fixpipe/Vector/Task Duration；首次host分配单列。A2/A3分别记录，不能把一台机器结果泛化。任何退化按布局/容量/shape写入PERF_LOG，设备证据充分前不合并main kernel。
