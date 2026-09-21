# 当前最优版本复核单

版本：`user-best-20260921`，kernel SHA256 `e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。

目的：建立用户当前最佳实现的可复现测量，后续每次改动都与它比较。沿用服务器已有 harness，不重新开发正确性基线，不更改正式测试或判分逻辑。

1. 记录精确 SoC、CANN 9.0.0/驱动、AIC/AIV 数及实际编译命令，确认 kernel SHA 与上面一致。先按生产默认构建；BMMMS_TUNING 不开启，BMMMS_PROBE_* 保持 0。源码的 if constexpr / InitConstValue 等以真实编译结果为准。
2. 使用正式 15 case 评测；记录 (B,M,N,K)、FP16/BF16、tx1/tx2、实际 plan（dual/baseM/baseN/window/nSplit/kSplit/cubeBlocks/workers）、误差及重复一致性。没有正式 case 时明确说明，不将额外自测称为正式通过。
3. 重点补充当前生产分支覆盖：短 K=32/40/56/64 的微型矩阵、K=40/72 尾块、全负数据、M/N 非对齐、长 K split-K、PAD_MN、较大 B 和小核数下的 FinalizeRows。覆盖所有四种存储布局及两种 dtype，并遵守实际输入规模限制。
4. 对用户截图的五个 shape 复测；先补全 dtype/layout，不能直接与未知布局耗时比较。预热至少 50 次，再测 200 次，交替顺序重复 5 轮；记录稳定态 median/p95 与波动，首次分配和 host 初始化另列。
5. msprof 回传 Task Duration、Cube/Vector 与 MTE 指标及单位；区分 MTE 指令时间占比和带宽值。A2/A3 分开归档。
6. 检查 FinalizeRows 的实际 AIV 编号与步长：用可用核数 1/2/4、B=64 的合法 case 确认每个 y 元素 writer 唯一性。即使数值一致，重复写仍应单独记录。若确认问题，另建单改动分支修复，再做原版/修复版对照。

回传：构建日志、SHA、逐 case 表、实际 plan、精度结果、latency 和 msprof 摘要、原始日志位置。源码注释的历史耗时不填入本轮结果。大型日志留在受权限控制的位置，结果摘要写入 PERF_LOG。
