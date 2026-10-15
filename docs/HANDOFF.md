# 当前工作：C15 原版native输出0，补齐Cube→Vector写回通知并编译

## 当前源码和身份

- 分支 `experiment/c15-split-producer-ready`，parent3cb10e5 / ZIP078635/e2f1b63。当前kernel353255B/SHA2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b，仅manual_split_tt新增Cube PIPE_FIX通知与Vector等待两行。保护7文件不变，未main/OJ。
- C6 raw候选fa315ae8/0689e2d已native精度失败，已归档撤回；新SSH已补回原始失败包/编译log/DSO manifest，没有重跑。原baseline C6中位8.860354us，完整五报告在artifacts/c6-input-layout-audit。
- ZIP078635与队友接受源b881不同；后者正式Pass15/401.13us不能赋予本源。当前原ZIP在C15本地已出现实际正确性失败。

## 当前实际设备证据

- 新入口恢复，hostname2ef29bca0f61，9382/24AIC48AIV/CANN9/driver26.1.1，dev0physical14/card7chip0；caller core_limit20。
- C15 FP16TT1/64/64/8192实际normalPlan dual25/BM64BN64/kSplit8/kChunk1024/workers8/cubeBlocks8/finalBlocks1，systemBytes16777216/total16908288，完整reviewed c15.complete_frame.json已冻结。
- 原baseline DSO0357587a第一次correctness输出0.0，对fullstorage FP64golden1.6493455171585083，rel1/exit1；actual+guard原始bits和失败JSON已保存。没有性能采集。shape由用户提供，dtype/layout仍为历史对应假设；本机失败则是真实明确的证据。
- 实际CANN9 SyncAllImpl<true>只同步AIV，不等Cube。原手写SplitTT没有Cube partial完成通知，当前两行修复建立本Cube Fix→本AIV→全AIVbarrier→finalizer依赖。源码诊断需native结果确认。
- CPU实际函数位置/whole inverse/保护7、15task-owner DAG以及无通知/早通知反例通过，不当硬件证据。详见C15_PRODUCER_READY。

## 正在进行与下一条动作

- CANN独立build-c15-ready编译中，冻结 imports/c15-producer-ready-2073f48e78d4/kernel.asc；日志native_oj_like/build-c15-ready.log。
- 编译通过：真实source/DSO/wrapper manifest→同c15 fixture/frame/inputs一次correctness，失败保存raw继续诊断；通过则补全负/多次重入并采5完整default全部表，actualMIX11/8Cube8Vector符号核对。
- 只有正确修复版才能作为C15有效性能基准。随后实施单一resident split input结构（C15_RESIDENT_INPUT_AUDIT）：A batched ND2NZ保留原K128块顺序，B整split NZ，原Load2D/8MMAD/Fix/AIV/GM保持；预设20%中位门槛，失败归档不扫参数。不能与原错误输出0的版本比较加速。
- 独立native driver失败前保存actual+guard原始bits和precision_failure.json已部署，正式main/CMake/golden/阈值均不改。

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
