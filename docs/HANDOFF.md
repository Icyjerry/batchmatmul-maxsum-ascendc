# 当前工作：C6 raw row，SSH恢复后正在 CANN9 编译

## 当前源码与边界

- 分支 `experiment/c6-raw-row-input`；parent e2f1b63 / ZIP078635，当前 kernel357100B / SHA `fa315ae8072a5a128b4e57a6e9528064b9d63d2c0c1a0ad7f27a433248cce71e`。
- 初始140080d/639fa38未经设备编译；本轮核对实际SDK发现默认LoadData只配置LEFT，不能自动配置B的RIGHT。当前修正显式SetFmatrix RIGHT + public no-reset LoadData，与保留C10写法一致。CPU新增register模型和第8个故障反例。没有新增GM，原MMAD/Fix/AIV/Plan/其它路径保留。
- 算法仅改kernel.asc，七个受保护文件与1734f16相同；未并main/未新OJ。ZIP078635与DISPATCH接受源b881不同，后者Pass15/401.13us不是当前源的结果。

## 本轮已完成：真实 C6 baseline

- 2026-10-15新入口成功，hostname2ef29bca0f61，9382/24AIC48AIV/CANN9/driver26.1.1/dev0→physical14/card7chip0；core_limit20是caller budget。
- C6 BF16NT13/23/73/192，实际normalPlan原dual19/BM32BN80/K192/workers13/cubeBlocks13/finalBlocks2。完整reviewed frame保存在remote native_oj_like/c6.complete_frame.json。
- baseline DSO0357587a绑定ZIP078635；全storage FP64golden，一次精度+五性能输出通过，maxabs2.3841858e-7/maxrel6.52273e-8，输入不变/y后guard完整。
- default全部8表×5，实际single_tile_direct_batch_mix11 baseline符号/13AIC13AIV/每core一次MMAD。TaskDuration `[8.260330,9.000360,8.780352,8.860354,9.240370]`μs，中位8.860354。候选预设20%门槛<=7.0882832μs，不挑样本、不重复未改源码。
- CPU实际raw helper+producer78batch pairs/fullK/正负/显式尾零/ready/bounds、8个反例PASS；guard production46/TUNING57反例PASS；不是实际Load3D布局或BF16设备精度证据。
- C4 compact旧候选raw两个包已补回 `artifacts/c4-compact-k128`，没有重测。C6baseline完整plan/correctness/profile包在 `artifacts/c6-input-layout-audit`，权限700/600。

## 正在进行与下一条动作

- fixed candidate冻结 `/workspace/bmmms-codex/imports/c6-raw-rows-fa315ae8072a/kernel.asc`，独立CMake build-c6-raw正在编译，日志 `native_oj_like/build-c6-raw.log`。旧639fa38冻结目录保留但不编译/不把结果借给新源。
- 编译成功后生成真实source/DSO/wrapper SHA manifest；同fixture/frame/input运行一次correctness，再五默认完整profile。actual符号须含RAW true，正常计划应一致，输出全部fullgolden通过才比较中位。
- 20%门槛失败：保存原始证据，归档候选、恢复整份ZIP，不扫相邻filter/stride/不重复采集/不OJ；达到门槛：补全负与相关边界、正式15点后才谈冲榜成果。
- 新filter12/stride12/channel16组合，字段及后台调用已核对真实9SDK，但真实支持/目的ZZ-ZN/速度未验证。不要以CPU模型或字段宽度代替设备证据。

## 既有失败结论与交接

- C13 fullK MMAD4→2，native仅9.100364→9.040361us，未15%门槛；archive experiment/c13-full-k-halves/520f27d，无OJ/重测。
- C12 strided Bprep MTE3指令实降2688，83.123322→82.683304us仅0.53%，未10%门槛；archive b159f99，无OJ/重测。
- C4 compact K128产品64KiB→32KiB，3.060122→3.100124us慢1.31%，未20%门槛；archive3b6a05d。parser纯Vector MixBlockDim NA仅重解析原五报告，未重采。
- 尊重队友C8已完五轮/C7 parked/C9常量Schedule paused，历史失败方向详见 TEAMMATE_777734_REVIEW 和独立档案，不重命名复做。
- 接受源readonly CLI查询6acdd94d本机会话加载成功但HTTP403，未取到source/result；不是明确401，不据此要求重新登录。原始脱敏摘要ignored accepted-identity-read.json。无新OJ任务。

## 环境与资源

- 私有SSH config `/private/tmp/bmmms-remote-access/config`，前台master98210 / exec75384 / ControlPersist=no；用 `ssh -O check` 复核，不保证长期存活。凭据/askpass不入Git，askpass已删除。
- 设备工具 `/workspace/bmmms-codex/native_oj_like`；私有NumPy2.2.6 Python `/workspace/bmmms-codex/test-venv/bin/python`。source CANN set_env，runtime driver/lib64/common和driver/lib64/driver加入LD_LIBRARY_PATH。
- 真globalfilelock+active/pending queue序列化设备，编译可以并行。baseline任务已终态，最新是否有活动任务以真实queue/ps为准。shared_assets只读未改。
- GitHub私有 `Icyjerry/batchmatmul-maxsum-ascendc` 已授权，push当前实验分支；不移动历史tag/不重写已推送历史。
- 当前目标active，历史三轮platform-denied已因新入口解除；仍未验证candidate编译/native/full15/另一SoC/ZIP-accepted绑定，整体冲榜未完成。
