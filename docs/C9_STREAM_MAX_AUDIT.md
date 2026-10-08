# C9 streaming Max audit — retained kernel, no candidate yet

## 当前状态及本轮反例

正式通过的完整 `a2e6763` kernel 已恢复，368782B/SHA256 `16b51684cc8628121d7e359c89561c248d04b449b6ecb449f0b4f2da2ffa3a94`。

C8 balanced-tail 实现/模型/正式结果全部留在 `experiment/c8-balanced-tail-frame` /940ec4e；唯一任务6ac7d7af694b590c3c1a2cb8：15点通过，C8=56.78μs，比父近期43.66–45.83明显回退，未复测。没有保留其新参数、调度或默认ABI变化。

C6进一步源码核对：历史BF16/FT假设下实际选择 `bmmms_single_tile_direct_batch<T,false,true,32,80,0,true>`。`SingleTileDirectContext<true>`没有TPipe；A1/B1/A2/B2/C/UB均为手动 LocalTensor；两输入完整一次加载，完整KP一次MMAD；单AIV直接23行Max/Sum，另一个仅消费完成。移除队列或改成fullK frame已实现，拒绝重复该假设。不是实际正式route/profile确认。不能把C6当成TT或BN96常量分支。

C2 raw-bittranspose、storage-native/Brcb/Ktree、C3staticFT、C1literal的历史失败已在PERF_LOG保留，不根据新的scope描述复活。

## 选定的独立 C9 假设

现有队友 `bmmms_case9_packages` 的 Cube 完整K、resident-A、B双包和late ring credit保留；只研究Vector在一个N分片内保留每行64lane最大值，直到该分片全部Nt完成才横向ReduceMax一次。随后沿用原partial和全核最终MaxN/SumM。

这沿用初始 `experiment-v1` 的归约恒等式，但C9 packages入口没有这个实现；初始广泛dual实现不是本次native验证。绝不采用C8已失败分片/B搬运增加策略，也不是PK/BN扫描。

`max_n C[m,n] = max_lane max_chunk C[m,64*chunk+lane]`，前提是每个C已完成全K且只fold实际有效N。Nsplit之间仍须merge Max后才Sum M。初始化-inf，全负值正确；idle/零行AIV仍正常归还ring并参加SyncAll。

## 执行的实际host/source算术审计

命令 `python3 tools/audit_c9_stream_max.py`；从当前a2e6763提取真实MakePlan、MakeCase9PackagePlan，fake tiler，仅四种actual-source host配置（8/20/24/32）。C9依据用户supplied B1/M2048/N1536/K1280、历史FP16/FT假设，正式dtype/layout/SoC依旧未知。

|cores|BM/BN/BK|Nsplit/workers|Bpackage|原WholeReduceMax API|新算法预计WholeReduceMax API|
|---:|---|---|---:|---:|---:|
|8|128/128/128|1/8|256|768|32|
|20|128/128/128|3/20|256|768|96|
|24|128/128/128|1/16|256|768|32|
|32|128/128/128|12/32|256|768|384|

每组原row-Max /新lane-Max API数量均为768，但处理元素数量不相同：新lane状态每个Max要读写64列，增加UB流量及repeat数。横向归约次数减少不是耗时预测。旧显式Vector buffers67104B，新lane多16384B，再预留4096B不超过fake192KiB UB；native TPipes/实际容量及guard必须再核对。MakePlan/GM/ring/输入搬运不拟改动。

仅host/source算术，不是执行改后的AIV、Ascend API、FP16精度或性能证据。原始日志忽略 `artifacts/c9-stream-max-audit/host.log`。

## 下一条可执行动作

1. 默认false bool模板只接入现有精确C9 host资源/pin guard；actual UB查询够时才选择。完整parent inverse/原Cube body字节不变/protected7/Plan/GM证据先做。
2. 每任务初始化一个64lane/row UB，masked Max更新；最后WholeReduceMax到原maxima，沿用原partialstore、SyncAll和最终归约。源码重复数据缓存的event/readiness与queuefree次序不能因延后归约而提前释放live c。
3. 执行真实C9 AIV控制流/实际helper的FIFO模型，正负/poisonNtail/多Nt/Nsplit/不同核心/零行/idle/反复slot/部分尾块；与逐行直接max比对，漏ready/credit/FullK/Nmask/最后fold/barrier/terminal故障对照。
4. CPU过后commit/push/dryrun/ONE正式任务/立即ID/同ID终态。显著收益门槛先定：Pass15且C9<=57.375μs（近期未改C9最低67.50的85%）才复测；否则归档恢复、不扫邻近lane/tile/PK参数。实际SoC/route/profile未知时不宣称已因果优化。

当前无kernel候选/新正式任务，整体冲榜目标未完成；无需Web/其他agent/NPU登录批准。
