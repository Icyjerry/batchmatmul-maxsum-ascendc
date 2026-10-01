# TT worker 内跨 N 的 UB Max 驻留

## Evidence → Diagnosis

父版 `0d4bd04` / kernel `65e38bb155af9adb068e87dc90c01face21a7cf024d094c54846c5188e9ca120` 正式15/15通过，第8点59.66μs。连续任务已经让同M相邻N tile留在同一核，但Vector仍每tile分配/初始化最大值、写partial，末级再全部读取。

本次假设：每worker的连续区间内，同M的N tile可以共享UB行最大值；仅在M切换或worker区间结束时写回。所有N区间完整Max之后再做M Sum，无K拆分或近似。

## 实现

仅 `kernel.asc` 算法修改，分支 `experiment/tt-worker-max`；保留父dual33准入、实际容量、BM/BN、完整K Cube、A1驻留、双C/ring和现有flags。

- 连续任务总数改为 `B*mTiles*nTiles`，与partial的nSplit独立。默认非连续旧路线仍使用原nSplit。
- 新 `ManualFullMConsumeTasks` 调用原实际窗口消费者。MQ中的最大值跨同M相邻N tile驻留，切M/区间尾才EnQue、写出并Free；有效N及全负处理不变。
- partial仍为原逐行slab，nSplit=workers。worker只写自己实际覆盖的M半块；没覆盖的worker/M组合不初始化，也不得读取。
- 末级每个M半块仅合并与该M的tile区间相交的worker。tile t的owner为 `((t+1)*workers-1)/total`；使用首末tile找贡献者，不遍历无效slab。host已保证workers<=total，因此贡献者之间不存在空worker。
- 原Ns0行头标量复用、第二次全局屏障及最终单writer保持。复用原partial/ring区域；没有新增GM通路或flags。partial容量可能变大，但活跃读写数量下降。

## 论文/项目对应

[Flash-MaxSim实际源码](https://github.com/roipony/flash-maxsim/blob/main/flash_maxsim/flash_maxsim.py) 在document块循环内保留FP32行最大值，完成后再求和。本次将这一在线Max原则用于Ascend双AIV/worker局部分片，并显式合并不同worker的贡献；不搬用其query/document配对、mask或CUDA/Triton API。
[FlashAttention-2](https://arxiv.org/abs/2307.08691) 强调工作分配及减少非矩阵计算/中间通信。本次减少的是partial写读和queue周转，不把GPU论文速度作为NPU预测。

## 源码模型与计数

- `python3 tools/validate_tt_worker_max.py`：1440抽取实际新任务消费者+实际稀疏末级执行，真实多线程barrier、延迟MTE2/MTE3、释放后破坏ring、任务/M区间边界、未写slab正大数污染、唯一partial/output writer、M/N尾块、全负Max→Sum通过。合成完整K C用于隔离Vector流程；不是BF16硬件精度或Cube/Vector并行时间模型。
- 同脚本原窗口消费者9216回归：共享ring的双AIV最后DMA后释放credit、破坏性复用、宽窗口/尾块通过。
- `python3 tools/validate_tt_contiguous.py`：440实际producer（nSplit与nTiles不同）、420默认旧producer、160矩形及全部65536bit复制通过。逆替换新Vector入口后，原消费者body仍与通过TT种子 `a05035e` 逐字一致。
- fake host production/TUNING各6912配置/720选择/144容量降M；固定公开8.3.T9.0.B066真实tiler同样各6912/720/144通过，workspace大小、其它layout/dtype/显式pin和容量fallback通过。公开8.3不是安装CANN9。
- `python3 tools/validate_tt_parallel_finalize.py`：288实际末级线程模型，独立逐tile枚举生成仅真实worker/M贡献，未写区域污染/唯一行所有权/延迟DMA通过。

20核、BM=BN=128代理：M=N=1536的144个tile partial变28个worker/M partial，逻辑行partial写+读147456→28672字节；M1408/N1025为99→28；M1537/N1537为169→31。最后标量搬运、padding、同步、Cube开销不包含在这些计数中，不能据此预测加速比。

## 正式验证

kernel SHA `269c7d370b48db80e7da48733f558ea6d6675ac844e4b04878ab4eec077c9b3c`，278860字节。
本机模型日志 `/private/tmp/bmmms-tt-worker-{producer,consumer,final,public}.log`。首次脚本因注释抽取锚点改变退出，修正锚点后全部exit0；没有改变kernel容差/准入来绕过错误。
独立官方模板 `/private/tmp/bmmms-judge-tt-worker-max/project` 仅替换kernel。dry-run核对仅kernel/SHA一致；代码 `34956fe` 已commit/push，正式活动任务 [6abe1ed9694b590c3cd68cc9](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe1ed9694b590c3cd68cc9) 已创建。正式终态 **Pass：CANN编译成功、15/15、precision_ratio全1**。
耗时 `[2.11,4.14,4.41,5.74,5.38,10.72,10.30,59.72,84.31,98.00,89.17,97.46,16.37,13.36,9.60]` μs。第8点父59.66→59.72μs，没有收益；无actual shape/plan/SoC/profile及重复对照，不断言硬件瓶颈或路由命中。没有活动任务，保留失败对照，不替换父通过结构。
原始JSON和模型日志本机Git忽略 `artifacts/tt-worker-max/`。下一检查Cube L1→L0A跨相邻N复用；旧 `7b4d477` N pair正式无收益，但仅16对齐/BM128、A不驻留；新研究必须证明与该旧路线有实际差异，不能重复原样提交。
