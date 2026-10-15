# 当前工作：C15就绪修复native通过；resident split输入候选已编译并通过混合精度

## 当前源码和身份

- 分支 `experiment/c15-resident-split-input`，parent a11e2d9/2073f48e（正确就绪修复）。当前kernel356494B/SHAdda7b307090859d1ec4f9f2d88b3622c5d85b26c50eb7f7b32388002b86bce67，新增默认false resident input，仅完整C15 frame开启。
- 原始ZIP078635 C15输出0已被native反证，2073f48e两行通知修复混合/全负/五调用通过；失败时应恢复2073f48e，不恢复错误ZIP。
- C6 raw失败源留0689e2d，原始日志已补回；ZIP与接受b881身份不同，后者Pass15不能借给当前源。保护7不动，未main/OJ。

## 当前实际设备证据

- 新入口恢复，hostname2ef29bca0f61，9382/24AIC48AIV/CANN9/driver26.1.1，dev0physical14/card7chip0；caller core_limit20。
- C15 FP16TT1/64/64/8192实际normalPlan dual25/BM64BN64/kSplit8/kChunk1024/workers8/cubeBlocks8/finalBlocks1，systemBytes16777216/total16908288，完整reviewed c15.complete_frame.json已冻结。
- 原baseline DSO0357587a第一次correctness输出0.0，对fullstorage FP64golden1.6493455171585083，rel1/exit1；actual+guard原始bits和失败JSON已保存。没有性能采集。shape由用户提供，dtype/layout仍为历史对应假设；本机失败则是真实明确的证据。
- 实际CANN9 SyncAllImpl<true>只同步AIV，不等Cube。原手写SplitTT没有Cube partial完成通知，当前两行修复建立本Cube Fix→本AIV→全AIVbarrier→finalizer依赖。源码诊断需native结果确认。
- CPU实际函数位置/whole inverse/保护7、15task-owner DAG以及无通知/早通知反例通过，不当硬件证据。详见C15_PRODUCER_READY。

## 正在进行与下一条动作

- 正确parent2073f48e，DSOca36b327：混合1.6493455171585083精确/全负-40.06380844116211通过/五输出相同，default8表×5实际8AIC8AIV。TaskDuration[10.540421,10.940437,11.080443,11.540462,10.760430]μs，中位10.940437；原始包已下载artifacts/c15-producer-ready。
- 新resident源dda7b307/DSO59878aa0独立CANN9编译PASS、同完整frame混合precision PASS；负值+五default profile正在exec54174运行，不能重启同任务。
- 新分支每split A一次batched ND2NZ/B一次整split NZ，原两次Load2D/8MMAD/K顺序/Fix/就绪通知/AIV/GM不变，L1 64KiB→256KiB、GM字节不减。真实资源/精确frame/alignment/tuning guard，默认false回退。
- CPU实际Read/select/Load2D：全8split/1048576源地址tag一致/五故障反例，guard47/58资源边界通过；不是FP16硬件证据。详见C15_RESIDENT_SPLIT_INPUT。
- NEXT poll54174同handle；完整五报告与actualRESIDENT true/8AIC8AIV核查后，比较20%gate<=8.7523496μs。失败归档恢复2073f48e、不扫参数或重采；过gate再补回退/native/正式15并考虑OJ。当前无性能结论或正式任务。
- 独立native driver失败原始bits诊断已部署，原main/CMake/golden/阈值不改。最新SoC/queue以真实设备状态为准。

## 既有失败结论与交接

- C13 fullK MMAD4→2，native仅9.100364→9.040361us，未15%门槛；archive experiment/c13-full-k-halves/520f27d，无OJ/重测。
- C12 strided Bprep MTE3指令实降2688，83.123322→82.683304us仅0.53%，未10%门槛；archive b159f99，无OJ/重测。
- C4 compact K128产品64KiB→32KiB，3.060122→3.100124us慢1.31%，未20%门槛；archive3b6a05d。parser纯Vector MixBlockDim NA仅重解析原五报告，未重采。
- 尊重队友C8已完五轮/C7 parked/C9常量Schedule paused，历史失败方向详见 TEAMMATE_777734_REVIEW 和独立档案，不重命名复做。
- 接受源readonly CLI查询6acdd94d本机会话加载成功但HTTP403，未取到source/result；不是明确401，不据此要求重新登录。原始脱敏摘要ignored accepted-identity-read.json。无新OJ任务。

## 连接与资源

- 私有SSH配置/private/tmp/bmmms-remote-access/config，新前台master/exec55033，ControlPersist=no；用ssh -O check验证。askpass已删除，凭据不入Git。不沿用旧三轮blocked结论判断新入口。
- 私有工具/workspace/bmmms-codex/native_oj_like，Python /workspace/bmmms-codex/test-venv/bin/python；source CANN9/set_env，driver lib64/common和lib64/driver加入LD_LIBRARY_PATH。
- 真filelock+queue串行NPU，编译/offline可并行。此轮初始queue空/无msprof/bisheng；最新任务以真实queue/exec handle为准。
- GitHub已授权push当前实验分支，不移动tag/不改写历史。整体冲榜未完成；修复版CANN/native/full15/另一SoC仍待证据。
