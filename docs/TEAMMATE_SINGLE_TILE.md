# 队友single_tile片上缓冲与直接输出

## 当前：队友single_tile缓冲/同步/直接输出移植候选

`experiment/teammate-single-tile`，父15/15 tiny通过版 `f7c2c74`，kernel SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597bytes。kernel+165/-91，仅原版两single_tile设备实现、其context/lane-fold helper及FF/TT对应入口；没有混入队友扩大Cube分类/dual23或其它内核。MakePlan/workspace/tiny/C8/C9/C15代码保持。普通single_tile的一个AIV完成有效M Sum→4byte y，伴随AIV只消费完成flag；NT direct_batch手动L1/L0/UB、0/1 A/B就绪、A先Load、精确N lane-fold和PIPE_ALL结束，不重复TPipe 初始化/partial merge。代码按队友原版移植，不声称本Agent新算法。
6864实际Vector执行与1280实际Cube生产者通过；4布局、K8/M/N尾、物理NZ/ZZ/ZN、有界片上内存区间、每个有效C独立点积核对、负数及唯一合法y。污染无效N、缺PIPE_ALL、缺A/B等待四负控制检出。完整kernel等于对父明确移植变换，其它路径保持；重现 `python3 tools/validate_teammate_single_tile.py`。
CPU输入为整数值，不是FP16/BF16编码；Vector操作同步、Cube仅MTE2可延迟，MMAD/Fixpipe同步。跨核ready抽象，不能证明全硬件流水、误差或性能。模型首次补全未实例化branch API声明、修正预期offset的C++窄化及registry内GM子指针相对基址；没改正式测试/依赖来通过。
CANN9编译/正式15点/性能PENDING。原日志忽略 `artifacts/teammate-single-tile/`；下一仅官方原模板换kernel、dry-run、commit/push、一次提交存ID并查终态。重点父C5 5.34/C6 10.72，同时C3 3.06/C15 9.47。队友原版C5 5.21/C6 9.73不是重复同机A/B，不能推断隐藏路线或稳定差异。main/历史标签不动。


正式任务 **`6abe860d694b590c3c0f02a5`** 已创建，下一 `python3 /private/tmp/query_bmmms_submission.py 6abe860d694b590c3c0f02a5`，只查同一ID到终态，不重复提交。

## 最新通过组合：tiny容量/batch分组 + 队友single_tile，15/15通过

当前 `experiment/teammate-single-tile`，实现 `889afe0`，kernel SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597byte。正式任务 **`6abe860d694b590c3c0f02a5` Pass，CANN编译成功、15/15、precision_ratio全1**。μs `[1.97,2.39,3.12,4.04,5.28,9.85,9.59,49.78,67.51,97.43,86.97,95.62,14.76,12.61,9.34]`。
本实验父tiny分组版C6 10.72→9.85，单次降低8.1%；C5 5.34→5.28，仅小幅；C3 3.06→3.12略退，不能忽略。两次学习合计对更早组合 `d5cd4af`：C3 3.66→3.12（单次14.8%），C6 10.75→9.85（单次8.4%）。队友原版C3/C5/C6 3.14/5.21/9.73，与当前相近；当前C15 9.34保留原组合相对原版12.53的优势，但C15本实验源码未改，不归因变化。
C2 2.39、C8 49.78/C9 67.51及其它未改路径的变化不称本实验收益。没有实际shape/plan/SoC/profile或重复同机A/B，不保证稳定幅度、路径命中或推算榜单分数。全部改动仅kernel，独立原模板其它8文件不变；原始JSON/CPU日志Git忽略 `artifacts/teammate-single-tile/`。
6864实际Vector/1280实际物理Cube模型及四负控制通过；模型同步Vector/MMAD/Fixpipe、MTE2可延迟，整数转换不模拟FP16/BF16编码，跨核ready抽象。实际设备编译/15点精度通过单独报告。父tiny分组 `f7c2c74` 和更早组合/队友原版分支保持，main和历史标签不动；当前工作区干净，没有活动正式任务。
下一可执行动作：`git switch -c experiment/small-tile-coverage`，对照 `git show 9ab2312:kernel.asc` 的 `previousSmall/expandedSmall/SmallFullTileFits/dual23` 与当前 `ClassifyMeasured`：目前完整batch Cube仍只覆盖历史三个桶，队友泛化到资源允许的全部小矩阵，并通过round-robin处理B>AIC。先审核UB/L1/L0和repeat/mask限制、实际队列/唯一writer，再决定移植；不能直接粘整个host、重交相邻参数或丢当前tiny/C15。这个泛化目前**尚未实现/未提交**，C9窗口WIP仍独立归档。

