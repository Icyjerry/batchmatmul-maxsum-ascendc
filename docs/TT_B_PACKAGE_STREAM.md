# TT 跨 tile 的 B1 K 包流水 · 2026-10-01

## Evidence / Diagnosis

父版 `4ac80c9` 的正式任务 `6abe2939694b590c3cdc011a` 15/15 Pass：C8 59.27μs、C9 68.54μs。TT已完整A1驻留、连续tile任务、A2/B2双buffer；完整A下的N pair与worker UB Max分别正式无收益，不再重复。

当前TT每Nt重新发起首两个BK输入，最后K面板Free后没有预读后续Nt。K搬运包固定等于L0 BK，L1还有余量。这个源码事实不能证明正式C8的硬件瓶颈，但给出不同于前两项的可验证假设：让B搬运跨完整Nt任务连续，且用L1余量把K包放大；减少ND2NZ调用并把下一Nt输入提前到当前输出前。

## 实现

分支 `experiment/tt-b-package-stream`，kernel SHA `8c03d710d5394a0660e6bedc4c172f7784a1cbe3ef9f1cbc450f231aa1d6a052`，从通过C9+TT父版出发。

- 只改 `RunManualFullMCube<...,true>` 路径与dual33的包K计划；算法修改仅kernel.asc。
- 一个B1 TBuf切成两个包槽，替代原B1双TQue。每槽有MTE2→MTE1 ready及MTE1→MTE2 free事件，显式保护最后reader；不依赖新的B TQue复用语义。
- 输入cursor遍历该worker的连续 `(完整tile,K包)` 序列；初始两个包在A copy之后预发；当前包最后MTE1读之后，立即预发序列中的后续包，可越Nt/M/batch边界；不能越过worker range.end。
- packageK按实际剩余L1向下整BK并不超过ceil(K/BK)的BK整数。与C9已通过的完整A+双B包一样检查实际L1总量，最多512KiB。L0仍原BK/双buffer，C仍两份，原资源guard先保证准入。
- 使用已有dual33的 `kChunk` 保存B1 packageK，**kSplit仍1，MMAD循环始终覆盖原完整s.k，不按kChunk拆K**；此字段在原full-M/Vector路线未参与计算。没有扩展Schedule ABI、GM workspace、ring、partial、cross flags。
- 包内用k0-packageStart寻址，避免在每次K循环对动态packageK多次取模；NZ pitch始终为align16(validCols)，M/N/K8尾保持原语义。
- C9设备实现/host包计划/整个Launch，以及TT整个Vector/finalizer与通过父版逐字一致；default false仍原双queue/逐BK，在CPU回归中检查。

## 模型与实际证据边界

```sh
python3 tools/validate_tt_b_stream.py
python3 tools/validate_tt_b_stream_public_tiler.py --source /private/tmp/ascendc-api-adv-review
```

- 440实际producer立即调度：全K逐C、尾块/补零、全负Max/Sum、batch一一配对、cached A生命周期、两ring槽哨兵、任务/事件收支、B实际读字节保持、每Nt的ND2NZ份数ceil(K/packageK)、实际next-tile预读早于当前Fixpipe。
- 440延迟MTE2/MTE1/MMAD：MTE1 callback读live L1，MMAD callback读live L0/C，依对应事件推进引擎，不提前snapshot。
- 440 MTE2 eager、MTE1/MMAD deferred的对抗顺序；删除B1最后reader等待的负控制触发断言，模型会拒绝该非法复用。
- 420原default false producer、160矩形/raw-bit场景及全部65536模式通过。
- fake host和固定公开8.3真实tilerproduction/TUNING，各6912控制配置/720双package路线/576包K大于原BK；实际核8/20/24/32、物理预算/显式pins/fallback/workspace其它dtype布局保持。公开源revision固定 `c7dfa2d901a314e1ae69e9cef850057593f2a58b`，不是安装CANN9。
- M=N=K1536/BM=BN128代理，包K256时ND2NZ份数1728→864，B读取字节不变；不由此预测NPU时间。包数减少和跨tile流水可能被事件、L1竞争抵消。
- fixture最初把整块TBuf视为单个pending DMA导致两个不相交slot误报，已改为按byte span追踪，并保留读写范围/重叠assert；早期误用了只存在于旧CPU fixture的panelL1K字段，真实host编译揭示问题后改为上述现有kChunk，未扩展接口。

A1 TQue依旧是抽象完成模型，Fixpipe同步；CPU不是native queue实现、所有引擎的完整仿真、BF16硬件舍入或性能证据。

同步类型依据官方 [SetFlag/WaitFlag API](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900beta1/API/ascendcopapi/atlasascendc_api_07_0270.html) 的源→目标方向、TPipe AllocEventID和A2/A3事件范围；本轮来源为9.0beta1页面搜索提取，**具体安装9.0.0仍以正式编译/设备结果为准**。没有将GPU论文性能移植成此方案加速数字。

## Validation Request

官方独立模板 `/private/tmp/bmmms-tt-b-stream-official/project`，仅kernel替换；dry-run 297815字节、SHA同上。代码 `eb4671c` 已commit/push，正式任务 `6abe3059694b590c3cdf6c87` 已Pass，結果如下。没有活动任务。

## 正式结果

[正式任务 6abe3059694b590c3cdf6c87](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe3059694b590c3cdf6c87) **Pass，CANN编译成功、15/15、precision_ratio全1**。kernel SHA与上文一致，耗时μs：

```text
[2.15,3.97,4.30,5.60,5.40,10.51,9.68,49.38,67.48,98.19,87.77,96.70,15.25,13.02,9.20]
```

第8点父59.27→49.38μs，单次耗时降低16.7%/1.200x。第9点68.54→67.48μs，其路径逐字未改，不将1.06μs变化归因于TT优化。保留当前候选作为下一实验父版，原组合仍保留 `4ac80c9`。

没有actual shape/plan/SoC/profile或重复A/B，不确认隐藏case路线、不将单次幅度称为稳定收益、不宣称排行榜分数。原始JSON/模型在本机Git忽略 `artifacts/tt-b-package-stream/`，权限700/600。

下一研究现有ring直接存C0/NZ是否能减少FIX格式转换和AIV细粒度DMA。先比对 `fcbf29b` 内建库NZ及三个回调NZ失败实验，它们改变Matmul库，与当前手写完整M producer不同。核实基本Fixpipe `CFG_NZ` 的A2/A3接口和FP32 GM stride后才考虑独立改变同一ring格式；无新输入GM通路、不再试B包参数。该方案尚未实现或验证，不能计作收益。
