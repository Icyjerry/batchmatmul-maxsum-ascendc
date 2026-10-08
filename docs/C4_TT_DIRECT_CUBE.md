# C4 TT：复用现有手动Cube完整batch入口

## 证据、假设及范围

原算法1734f16/a5eef105/354602bytes；C4最近五次同SHA为4.11/4.08/3.94/4.12/4.08μs，中位4.08，用户最新榜首2.41、Tbest2.37。历史探针条件B4..7/M8..15/N16..31/K128..248/BF16 TT并非正式shape证据。

实际Launch中SmallVectorK256Rows优先于dual28/19：该条件原来实际走Vector产品张量及归约。旧packed-vector实验6abf25e6为4.43，无收益。本候选改变计算单元：在SmallVector前选择已存在的bmmms_single_tile_direct_batch<T,true,true,16,16或32,0,true>。该入口C6已正式使用DIRECT_BATCH；本次TT实例/路由仍需正式CANN与精度验证。没有新device函数/API，没有矩阵交换、低精度累加或近邻参数扫描。

## 实现

experiment/c4-tt-direct-cube，kernel356697bytes，SHA256 `e30524ac5ffa748457f3e0c10712251366083c1ff8349341bf0d0c0c38d69664`。恢复整个1734f16后仅新增40行/两处；逆移除helper/call逐字恢复whole-parent，包括全部已有Cube/Vector函数和planner。

- 仅上述历史条件、原dual19或其dual28覆盖、单M/N完整K，baseM16/baseNceilN16/workers=B/原plan字段一致才可进入。实际plan的kChunk为ceilK32（初版CPU审查发现不能错误要求等于实际K）；device原函数仍按真实K加载、ceilK16 MMAD，所有K完成后才Max(N)/Sum(M)。
- 每batch独立一个Cube，一对AIV；sub0读完整C、有效N最大值/实际M求和/唯一4B y，sub1仅消费完成通知，没有全局barrier/final kernel。复用原one-shot ND2NZ/TT Load2D/MMAD/Fixpipe和显式frame/events，设备源码逐字未变。
- 复用原GM prefix=ceil(B*16floats,128)和每B双16*NP FP32 ring；不写partial，不增加GM、分配、cache或systemworkspace。dual28原cubeBlocks0，实际本次启动B个MIXblocks；原Schedule/Plan/workspace不修改。需真实AIC>=B/AIV>=2B，不足完全回退原Launch。
- 查询真实L1/L0A/L0B/L0C/UB；上限显式L1=24576B+4096预留，L0A8192/L0B16384/L0C2048/UB2240+4096，原GM需覆盖系统prefix+512Bpartials+8*B*16*NP。全部显式TUNINGpins不覆盖。

## 本地验证

`python3 tools/validate_c4_tt_direct_cube.py` exit0：

- 768实际TT producer配置（每个B的entry均运行），B4/7、M8/11/15、N16/17/23/31、所有16种K8、正负混合/全负；物理NZ/ZZ/ZN、独立validC点积、输入不变、GM/局部边界、A/B独立DMA ready和完成事件通过。移除A或Bready负控制均拒绝。CPU整数，不是编码BF16或硬件并行时序。
- 11264实际AIVentries，完整B4..7/M8..15/N16..31及正负两类；完整pad poison排除、唯一4B y写、守卫、idle companion无分配、读取ready和末级DMA完成通过。四项负控制M/N掩码、输入DMAready、terminal完成被拒绝。模型Vector运算同步，因此删V_MTE3不能检测；未报告这项控制通过，也不声称完整V/MTE3并行模型。设备V_MTE3代码本轮未改变。
- production/TUNING各32768actual MakePlan控制流/18432准入（CPU tiler stub）；四核数1/4/20/32，每种完整8192shape范围；Plan/Schedule/GM不变、精确内存阈值/少1B、精确核数/少1核、实际workspace/少1B、非法plan、layout/dtype/相邻shape和显式pins回退通过。初版fixture变量B遮蔽oracle函数已修复，仅测试驱动改动。
- whole-parent scope通过。保护7工程文件均逐字1734f16。独立模板/private/tmp/bmmms-c4-tt-cube-official/project，CLI dry-run确认只上传kernel/356697bytes/SHA一致；原日志忽略artifacts/c4-tt-direct-cube/cpu.log。

## 正式gate PENDING

先commit/push实现及摘要，提交一次结构候选；获得ID立即保存/推送，只查询同ID到终态。完整15点均过才能考虑计分，用SCORE_REFERENCE_1008最新Tbest。明显大收益才原样确认，不因波动或观察超时重交；否则归档恢复parent。没有实际SoC/shape/plan/profile前不冒充路径命中或profiling结论。CANN/BF16精度/性能目前PENDING。
