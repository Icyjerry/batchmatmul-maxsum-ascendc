# TT 连续 tile 任务与并行末级合并

## Evidence → Diagnosis

窄N完整K驻留候选正式15/15通过，第13点没有收益，已归档。当前从通过TT种子 `a05035e` 开始，不包含窄N候选。

固定公开8.3真实tiler、物理8/20/24/32核的720个历史C8区间代理计划中，330个workers少于物理cores，最忙核tile数最多为理想均分的2倍。例20核M1408/N1025/K1536，NS2/tasks22，最忙10tiles；全部99tiles理想均分为5。正式C8真实shape/plan/profile仍未知，这不是正式瓶颈证明。

## 结构改动

仅kernel.asc算法。新dual33在父计划完成后选择B1/BF16/TT、M/N/K各1024..2048，父dual1或29、K不分片、没有earlySum或显式Tune pin，并核对真实L1/L0A/B/C/UB。

1. 将M-major的全部M×N tiles划为每worker连续区间 `[total*w/workers,total*(w+1)/workers)`，而非每M整N shard的round-robin。核间完整tile数量差<=1，各tile唯一owner；每tile仍完成完整K。
2. 相邻任务属于同一M时保留完整A1；只在M/batch切换时释放/重新搬入。B继续用原两K面板queue，L0 A/B ping/pong、原Load3D、MMAD/Fixpipe和GM ring flags保持；C按跨任务sequence在两个buffer间交替。
3. nSplit=nTiles、window=1，原partial布局为每N tile的逐M行最大值。Vector只改变任务顺序和末级入口；消费、有效N尾部Max及逐行partial写入与通过父版一致。
4. 最后按M半块分给全部AIV，每名AIV合并自己的全部N最大值，再求和。标量写回原Ns0的同一M半块首8float，其他AIV不会读该范围；第二次全局屏障后AIV0用一次strided DMA读取各块标量并汇总y。没有新增GM区域、flags或原子操作。
5. 完整A超出L1时，BM128→64以满足实际容量；不是对K精度的近似。重新计算mTiles/workers/grid/partial和双ring大小，沿用原partial/ring通路，workspace无输入预打包区。

## 论文与项目映射

[Stream-K原论文](https://arxiv.org/abs/2301.03598) 通过均分总内循环工作处理tile量化造成的尾波问题。[CUTLASS Stream-K调度源码](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/gemm/kernel/sm90_tile_scheduler_stream_k.hpp) 维护线性工作区间和跨输出tile状态。
本次借用工作量分配与持久任务状态的原则，以完整K tile为最小任务；没有实施论文的K拆分，也没有套用GPU性能数字。原生Ascend容量、GM/Vector协议和两级归约是本题自己的实现。

## 本地验证

`python3 tools/validate_tt_contiguous.py`

- 440抽取实际producer/helper执行：连续区间覆盖、逐C有效与补零元素、A跨任务驻留/刷新/释放、双C、延迟MTE2、队列/局部事件与cross credits、input/ring guards、两batch独立配对、全负Max→Sum通过。
- 原producer默认false的420回归、160矩形/all65536bit复制对照通过，保留其它TT路线语义。
- 逆替换task range与新finalizer入口后，整个Vector body与 `a05035e` 逐字相同；新range本身由独立整数partition oracle核对。
- fake tiler production/TUNING各6912计划、各720新路线/144容量降M选择通过；其它dtype/layout计划、explicit pin、容量fallback/partial-ring大小均核对。

`python3 tools/validate_tt_parallel_finalize.py`

- 288抽取真实末级函数执行：多个AIV线程/真实barrier、延迟MTE2/MTE3、输出唯一writer、Ns0原地复用的独立M所有权、长M/尾部/全负/污染无效M/GM guards通过。
- 新增队列FIFO在首个源码审查中改为先seed两个shard再DeQue，避免下一shard越过当前shard。没有声称硬件异步指令被CPU完整模拟。

`python3 tools/validate_tt_contiguous_public_tiler.py --source /private/tmp/ascendc-api-adv-review`

- 未改动官方公开8.3.T9.0.B066 tiler算术；production/TUNING同样各6912/720/144通过。不是安装CANN9或NPU证据。
- 首次producer夹具使用不满足L0C的BM128/BN256双C，改为host实际允许的BM64；首次host夹具auto同一声明混用不同namespace Plan，已拆开；末级夹具补齐空__gm__宏。上述都是模型修正，未改kernel去放宽容量或精度。

## 资源与风险

L1=`2*BM*align16(K)+4*BN*BK`，L0A/B分别`4*BM/BN*BK`，L0C=`8*BM*BN`。Vector预算包含原消费、全部新merge buffer和4096预留，实际平台容量不满足则保留父路径。
连续任务可改善tile数量均衡，但可能提高跨核A重复读取、增加每tile credit/partial写入和第二次barrier成本。M/N尾块的实际矩阵工作量也不全相等。没有操作计数到时间的倍数预测。
Max始终只取有效N；每个K点积完成以后才做Max，所有N partial合并后才做M和。末级求和分组改变，正式FP64 golden容差仍是必须通过的门槛。

## 正式状态

kernel SHA `65e38bb155af9adb068e87dc90c01face21a7cf024d094c54846c5188e9ca120`。
日志 `/private/tmp/bmmms-tt-contiguous-cpu.log`、`...-public.log`、`bmmms-tt-merge-cpu.log`。
独立官方模板 `/private/tmp/bmmms-judge-tt-contiguous/project`，只替换kernel.asc，dry-run276755字节/SHA一致。代码 `32c6b1c` 已commit/push；正式任务 [6abe1a32694b590c3cd3fe15](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe1a32694b590c3cd3fe15) 已创建。CANN9编译/15点精度/latency PENDING；查询同ID至终态，不因观察超时重提。重大提升尚未达成。
