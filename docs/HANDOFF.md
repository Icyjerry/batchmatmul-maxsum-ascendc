# 当前工作：C6 native失败已撤回；C15完整split输入常驻L1审查完成

## 当前源码与边界

- 当前分支 `experiment/c15-resident-input-audit`（从C6归档5767186派生）；kernel已恢复整份 e2f1b63 / ZIP078635 /353179B / SHA0786352034e77506894d4094083960f4f6af82782bf7cee6a0386148437ca436。失败候选357100B/fa315ae8完整保存在0689e2d。
- 初始140080d/639fa38未经设备编译；本轮核对实际SDK发现默认LoadData只配置LEFT，不能自动配置B的RIGHT。当前修正显式SetFmatrix RIGHT + public no-reset LoadData，与保留C10写法一致。CPU新增register模型和第8个故障反例。没有新增GM，原MMAD/Fix/AIV/Plan/其它路径保留。
- 算法仅改kernel.asc，七个受保护文件与1734f16相同；未并main/未新OJ。ZIP078635与DISPATCH接受源b881不同，后者Pass15/401.13us不是当前源的结果。

## 本轮已完成：真实 C6 baseline

- 2026-10-15新入口成功，hostname2ef29bca0f61，9382/24AIC48AIV/CANN9/driver26.1.1/dev0→physical14/card7chip0；core_limit20是caller budget。
- C6 BF16NT13/23/73/192，实际normalPlan原dual19/BM32BN80/K192/workers13/cubeBlocks13/finalBlocks2。完整reviewed frame保存在remote native_oj_like/c6.complete_frame.json。
- baseline DSO0357587a绑定ZIP078635；全storage FP64golden，一次精度+五性能输出通过，maxabs2.3841858e-7/maxrel6.52273e-8，输入不变/y后guard完整。
- default全部8表×5，实际single_tile_direct_batch_mix11 baseline符号/13AIC13AIV/每core一次MMAD。TaskDuration `[8.260330,9.000360,8.780352,8.860354,9.240370]`μs，中位8.860354。候选预设20%门槛<=7.0882832μs，不挑样本、不重复未改源码。
- CPU实际raw helper+producer78batch pairs/fullK/正负/显式尾零/ready/bounds、8个反例PASS；guard production46/TUNING57反例PASS；不是实际Load3D布局或BF16设备精度证据。
- C4 compact旧候选raw两个包已补回 `artifacts/c4-compact-k128`，没有重测。C6baseline完整plan/correctness/profile包在 `artifacts/c6-input-layout-audit`，权限700/600。

## C6候选已终态，下一条动作

- 候选fa315ae8独立CANN9编译PASS/8条host GM_ADDR warnings，DSOe0e6aa7f绑定source/wrapper994e29f。
- 一次native correctness/fullFP64比较FAIL/exit1，最大绝对误差约0.47670078、相对约0.12828762；原版同输入误差2.38e-7。CPU Load3D布局假设被native反证，具体错误排列未证明，不能假装已知enTranspose一行可修。
- 不采候选性能/不OJ/不重复或扫邻近filter-stride。恢复整份ZIP，失败实现留0689e2d，细节C6_RAW_ROW_INPUT。
- SSHmaster随后超时，原始候选编译日志/失败目录补下载PENDING；revalidate跳板已认证但target转发platform authorization denied，新入口问题已发出。baseline三个完整包已下载；本地candidate-terminal-observation.json明确仅保存工具已返回失败，不冒充原始FP32。
- 下一条设备动作：恢复后先下载build-c6-raw.log/DSO manifest/results/c6-raw-correctness，不重跑失败候选；检查queue/SoC/映射。
- C15结构审查已完成，见 C15_RESIDENT_INPUT_AUDIT：A使用保留API的batched ND2NZ拼成原K128面板顺序，B整split NZ；目标输入ND2NZ每split16→2，GM字节不减/L1由64KiB增256KiB。离线4组全部八split面板地址一致，naive fullA NZ次序反例被检出。M=N128需要524288B>actual524032B，必须拒绝。尚未生成ASC候选；缺C15真实normalPlan/完整baseline profile，先补这步，20%门槛明确。不能把逆向FP16TT frame当唯一正式属性。
- 独立native driver增加校验前保存actual+guard原始bits及precision_failure.json，便于未来失败诊断；不改正式阈值/7文件或此次结果。工具更新尚未部署服务器。

## 既有失败结论与交接

- C13 fullK MMAD4→2，native仅9.100364→9.040361us，未15%门槛；archive experiment/c13-full-k-halves/520f27d，无OJ/重测。
- C12 strided Bprep MTE3指令实降2688，83.123322→82.683304us仅0.53%，未10%门槛；archive b159f99，无OJ/重测。
- C4 compact K128产品64KiB→32KiB，3.060122→3.100124us慢1.31%，未20%门槛；archive3b6a05d。parser纯Vector MixBlockDim NA仅重解析原五报告，未重采。
- 尊重队友C8已完五轮/C7 parked/C9常量Schedule paused，历史失败方向详见 TEAMMATE_777734_REVIEW 和独立档案，不重命名复做。
- 接受源readonly CLI查询6acdd94d本机会话加载成功但HTTP403，未取到source/result；不是明确401，不据此要求重新登录。原始脱敏摘要ignored accepted-identity-read.json。无新OJ任务。

## 环境与资源

- 私有SSH config `/private/tmp/bmmms-remote-access/config`；前台master98210 / exec75384 已超时exit255/socket消失，干净重连platform authorization denied；脱敏判断见private revalidate日志，不输出凭据。需新入口，root密码无需重复。
- 设备工具 `/workspace/bmmms-codex/native_oj_like`；私有NumPy2.2.6 Python `/workspace/bmmms-codex/test-venv/bin/python`。source CANN set_env，runtime driver/lib64/common和driver/lib64/driver加入LD_LIBRARY_PATH。
- 真globalfilelock+active/pending queue序列化设备，编译可以并行。baseline任务已终态，最新是否有活动任务以真实queue/ps为准。shared_assets只读未改。
- GitHub私有 `Icyjerry/batchmatmul-maxsum-ascendc` 已授权，push当前实验分支；不移动历史tag/不重写已推送历史。
- 当前目标active，历史block曾因新入口解除，本轮完成native实测后再次失去target授权；这按新的阻塞周期计。候选已明确编译PASS/nativeFAIL，不再写PENDING。当前源full15/另一SoC/ZIP-accepted绑定仍未验证，整体冲榜未完成。
