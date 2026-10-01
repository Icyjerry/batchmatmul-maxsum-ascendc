# 队友tiny完整准入和batch分组

## 当前：队友tiny按UB准入和独立batch分组候选

分支 `experiment/tiny-batch-coverage`，父通过组合 `d5cd4af`，kernel SHA `e662891f722c132b93f9b3a6ab31514217c38fdf7e2221715bc138e0d01d0726`，317894bytes。只移植队友TinyVectorFits/TinyVectorBatchGroup/dual24分派，B<=8/M<=8/N<=64/K32..64按实际UB准入；完整tiny且B>1时每AIV一个batch，其余容量允许时按最大有效batch组分派。与队友重复两套大body不同，单核/分组复用同一个inline计算体，原数学/归约/手动事件/DMA逐字保持。补K合法性和强制dual24/group资源验证。
9344实际分组动态/特化、2344单核/父对照、9344空闲block，4layouts、末组尾块、负数、UB/mask/DMA/唯一y通过；production/TUNING各20736真实classifier、1752零scratch分组plan、508单核frame，双负控制检出。模型用整数模拟转换，不是FP16/BF16编码或完整异步硬件时序。整个kernel等于对父版的明确变换，C5/C6/C8/C9/C15其它代码与workspace保持。
`python3 tools/validate_tiny_batch_coverage.py` 复现；原日志 `artifacts/tiny-batch-coverage/cpu.log` 忽略。模型首次补充父tiler已有stepKa/Kb字段，并修正B1无需分组的断言，未改正式测试/依赖。CANN9编译/NPU精度/性能PENDING。
下一独立官方原模板仅替换kernel、dry-run核SHA，commit/push后一次正式提交，立刻保存ID并查终态。对照通过组合任务 `6abe7b90694b590c3c08ed48` 和队友原版 `6abe7f04694b590c3c0ade30`（原版C3 3.14 vs组合3.66）；不要据编号推断实际shape/plan。C5/6发现队友FF走single_tile、当前FF历史桶走direct_batch，以及BF16 NT分派放宽；继续单独研究，未实现/未提交。main/历史标签不动。

## 假设

此前只提取算术内核，仍保留B<=3/N<=16的旧准入和一核完成全部B。队友容量准入和batch独立并行是本次唯一性能假设。不能仅凭C3单次差距声称隐藏shape、路径或稳定收益；若无收益，保留通过父版并归档。

正式任务 **`6abe82b1694b590c3c0cf647`** 已创建，下一 `python3 /private/tmp/query_bmmms_submission.py 6abe82b1694b590c3c0cf647`，仅查询同一ID到终态，不重交。

## 最新：tiny容量准入/batch分组正式15/15通过，C3 3.06μs

`experiment/tiny-batch-coverage`，实现 `03e352b`，kernel SHA `e662891f722c132b93f9b3a6ab31514217c38fdf7e2221715bc138e0d01d0726`，317894byte。正式任务 **`6abe82b1694b590c3c0cf647` Pass，CANN编译成功、15/15、precision_ratio全1**。μs `[2.01,2.75,3.06,4.04,5.34,10.72,10.00,49.86,68.03,98.51,88.17,96.71,15.62,13.26,9.47]`。
C3组合父3.66→3.06，单次降低16.4%；队友原版3.14。C15 9.47、C8 49.86/C9 68.03相应源码未改，不归因波动。C2 2.63→2.75，单次有退化，不掩盖；没有实际shape/plan/SoC/profile/重复A/B，不能证明稳定幅度或确切路径。通过源/完整模型和证据保留，不合main。
下一从本通过版新分支学习队友single_tile和direct_batch：队友FF/TT单tile的Vector取消SyncAll和partial merge；NT手动L1/L0/UB取消TPipe初始化、A/B独立就绪、完整padded C DMA和lane-fold后一次树Max。不要混入更广Cube准入/其它manual或未验证C9窗口。原始结果忽略 `artifacts/tiny-batch-coverage/official.json`，没有活动正式任务。

