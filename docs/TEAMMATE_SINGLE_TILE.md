# 队友single_tile片上缓冲与直接输出

## 当前：队友single_tile缓冲/同步/直接输出移植候选

`experiment/teammate-single-tile`，父15/15 tiny通过版 `f7c2c74`，kernel SHA `2e365aaa858b9b9c82765671f108dbe0d28863c5bbc3838a8e89bc7ef842a2f2`，320597bytes。kernel+165/-91，仅原版两single_tile设备实现、其context/lane-fold helper及FF/TT对应入口；没有混入队友扩大Cube分类/dual23或其它内核。MakePlan/workspace/tiny/C8/C9/C15代码保持。普通single_tile的一个AIV完成有效M Sum→4byte y，伴随AIV只消费完成flag；NT direct_batch手动L1/L0/UB、0/1 A/B就绪、A先Load、精确N lane-fold和PIPE_ALL结束，不重复TPipe 初始化/partial merge。代码按队友原版移植，不声称本Agent新算法。
6864实际Vector执行与1280实际Cube生产者通过；4布局、K8/M/N尾、物理NZ/ZZ/ZN、有界片上内存区间、每个有效C独立点积核对、负数及唯一合法y。污染无效N、缺PIPE_ALL、缺A/B等待四负控制检出。完整kernel等于对父明确移植变换，其它路径保持；重现 `python3 tools/validate_teammate_single_tile.py`。
CPU输入为整数值，不是FP16/BF16编码；Vector操作同步、Cube仅MTE2可延迟，MMAD/Fixpipe同步。跨核ready抽象，不能证明全硬件流水、误差或性能。模型首次补全未实例化branch API声明、修正预期offset的C++窄化及registry内GM子指针相对基址；没改正式测试/依赖来通过。
CANN9编译/正式15点/性能PENDING。原日志忽略 `artifacts/teammate-single-tile/`；下一仅官方原模板换kernel、dry-run、commit/push、一次提交存ID并查终态。重点父C5 5.34/C6 10.72，同时C3 3.06/C15 9.47。队友原版C5 5.21/C6 9.73不是重复同机A/B，不能推断隐藏路线或稳定差异。main/历史标签不动。

