# Research → 单一流水实验 · 2026-09-21

## 证据与选择

当前起点是 `user-best-20260921`，不是旧 v1/v2。研究后选择 **dual=1/2 消费侧流水**：这两条路径均分配 `TQue<VECIN,2>`，原代码却在每块 C 的 EnQue 后立即 DeQue 和归约，下一块复制直到本块 FreeTensor 后才发出。手写 Matmul 路径已有预取，这次不重复修改它。

用户提供的 msprof 截图显示部分 case MTE2 占比较高，但没有源码 SHA、dtype/layout；因此它仅提供研究方向，不能证明当前候选瓶颈或速度收益。AIC MTE2 与这里 AIV 的 MTE2 也必须区分，消费侧优化并不直接减少 A/B 输入搬运字节数。

## 阅读的一手资料

| 来源 | 核对的内容 | 在本轮的作用 |
|---|---|---|
| [FlashAttention-3，§3.1](https://arxiv.org/html/2407.08608v2) | 生产者/消费者分工、环形缓冲及异步流水 | 借鉴依赖关系组织；不移植 Hopper TMA/WGMMA 或论文加速比 |
| [FlashAttention-4，摘要](https://arxiv.org/abs/2603.05451) | 不同硬件单元扩展速度不同，需随瓶颈重新设计流水 | 提醒不要把更多 Vector 工作量视为无成本；本轮不使用其 Blackwell 特性 |
| [CATLASS epilogue 文档](https://catlass.readthedocs.io/en/latest/1_Practice/07_epilogue_adaptation/) | AIC/AIV 后处理、阶段化 workspace、跨核完成标志 | 保留现有双槽 GM 通路，不增大 workspace |
| [Ascend/cann-var-sequence-gemm 的 batch_epilogue.h](https://gitee.com/ascend/cann-var-sequence-gemm/blob/master/include/batch_epilogue.h) | 可检索源码中 Gm2Ub 后发 PIPE_MTE2 release，再等待 MTE2_V 进行计算 | 支持“GM 读完即可复用、UB 计算继续”的实现模式。页面直读报错，已核对搜索索引中的代码片段，未获得固定 commit |
| [Flash-MaxSim 实现](https://github.com/roipony/flash-maxsim/blob/main/flash_maxsim/flash_maxsim.py) | 点积后屏蔽无效列，以负无穷处理尾部，在线维护行最大值再求和 | 核对语义；本轮 Max 指令及顺序逐条保留，不改变 K 累加或最终 Sum |
| [Ascend C CrossCoreSetFlag 官方文档](https://asc.gitcode.com/api/SIMD-API/basic_api/sync_control/inter_core_sync/CrossCoreSetFlag_ISASI.html) | mode 2 的 AIC/双 AIV 配对及指定 pipe 前序任务完成后通知 | 抽象事件模型的依据；文档当前页不能代替 CANN 9.0.0 实际头文件与设备验证 |

Tavily CLI 本轮检索失败，改用 Web 检索核对上述来源。CANN 900 旧文档链接返回首页，没有将它记为已验证的 9.0.0 API 内容。未复制第三方实现；本轮 helper 从仓库现有代码抽取并重排。

## 改动及可证伪假设

`BMMMS_DUAL_PIPELINE`：

- `0`：原有串行消费顺序。CPU trace 与 tag 中抽取的原始循环一致。
- `1`：利用现有两个 UB 缓冲，先排入下一块，再归约当前块；窗口末尾归还槽位。
- `2`：在 `1` 基础上，当最后一次 GM 读取已发出时排入 PIPE_MTE2 release，并提前发送原有的下一窗口 wrapper 握手。通知生效要等待 DMA 完成，不能在仅发出 DMA 时就覆盖 GM。默认实验档位为 `2`。

1→0 测试“同一窗口内 MTE2/V 重叠”；2→1 测试“尽早允许 Cube 复用槽位及启动后续窗口”。窗口只有一块时 1 与 0 没有预取空间，2 仍可能缩短槽位占用。缺少足够后续窗口、AIC 输入搬运占主导或额外标量调度成本偏大时，可能没有收益或退化。

适用入口仅 `bmmms_dual` 和 `bmmms_dual_mdl` 的完整 K 路径。host plan、Cube 部分、分块、UB 分配、workspace、partial 写入、finalizer 完全保留。独立脚本会恢复两处旧循环并要求剩余源码与原 tag 一致，防止混入其他改变。

## 明确延后

- 不重新引入 DeferredRowMax；其增加 UB 状态，尚无当前版本收益证据。
- 不再叠加旧 v2 N-split 策略；当前最优版已包含相应策略。
- 不变更 K 累加精度或使用 FP8；不把 GPU 特有指令套到 A2/A3。
- 不将 FinalizeRows writer 修复混入流水对照；该既有疑点保留在接手清单。
- 不执行源码中的 OJ shape probe；构建时记录并保持诊断宏为 0。

## 验证边界

CPU 模型以抽取的当前 helper 和 tag 原循环为比较对象，检查两块 UB 生命周期、DMA 地址/填充、相同 Vector 调用顺序、单次 release 与 wrapper 握手数量。PIPE_MTE2 release 时完成待执行复制并立即用巨大正值覆盖 GM，验证随后的归约只依赖私有 UB。

另用一 AIC/双 AIV 抽象模型随机调度，检查无提前覆盖、无死锁及退出时两槽信用配对。该模型假定官方事件语义成立，不模拟 Matmul 内部 flag 9 实现、CANN 编译器、DMA 硬件或 cache 一致性。这些只能由实际 SDK/header 和上板验证确认。
