# 队友tiny完整准入和batch分组

## 当前：队友tiny按UB准入和独立batch分组候选

分支 `experiment/tiny-batch-coverage`，父通过组合 `d5cd4af`，kernel SHA `e662891f722c132b93f9b3a6ab31514217c38fdf7e2221715bc138e0d01d0726`，317894bytes。只移植队友TinyVectorFits/TinyVectorBatchGroup/dual24分派，B<=8/M<=8/N<=64/K32..64按实际UB准入；完整tiny且B>1时每AIV一个batch，其余容量允许时按最大有效batch组分派。与队友重复两套大body不同，单核/分组复用同一个inline计算体，原数学/归约/手动事件/DMA逐字保持。补K合法性和强制dual24/group资源验证。
9344实际分组动态/特化、2344单核/父对照、9344空闲block，4layouts、末组尾块、负数、UB/mask/DMA/唯一y通过；production/TUNING各20736真实classifier、1752零scratch分组plan、508单核frame，双负控制检出。模型用整数模拟转换，不是FP16/BF16编码或完整异步硬件时序。整个kernel等于对父版的明确变换，C5/C6/C8/C9/C15其它代码与workspace保持。
`python3 tools/validate_tiny_batch_coverage.py` 复现；原日志 `artifacts/tiny-batch-coverage/cpu.log` 忽略。模型首次补充父tiler已有stepKa/Kb字段，并修正B1无需分组的断言，未改正式测试/依赖。CANN9编译/NPU精度/性能PENDING。
下一独立官方原模板仅替换kernel、dry-run核SHA，commit/push后一次正式提交，立刻保存ID并查终态。对照通过组合任务 `6abe7b90694b590c3c08ed48` 和队友原版 `6abe7f04694b590c3c0ade30`（原版C3 3.14 vs组合3.66）；不要据编号推断实际shape/plan。C5/6发现队友FF走single_tile、当前FF历史桶走direct_batch，以及BF16 NT分派放宽；继续单独研究，未实现/未提交。main/历史标签不动。

## 假设

此前只提取算术内核，仍保留B<=3/N<=16的旧准入和一核完成全部B。队友容量准入和batch独立并行是本次唯一性能假设。不能仅凭C3单次差距声称隐藏shape、路径或稳定收益；若无收益，保留通过父版并归档。
