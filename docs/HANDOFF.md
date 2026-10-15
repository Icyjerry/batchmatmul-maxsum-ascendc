# 当前工作：C15就绪修复保留版已按用户授权正式提交一次，待同ID终态

## 当前可继续的源码

- 分支 experiment/c11-mdl-transposed-c，当前kernel **353255B/SHA2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b**，完整恢复a11e2d9：只保留C15 Cube PIPE_FIX→AIV wait就绪修复。
- 不回退到ZIP078635：该份本机C15第一次输出0已反证。接受源b881与ZIP不同，不能借它的Pass15/401.13us证明当前源。七个保护文件保持1734f16；未改main/正式测试/阈值，未main合并；本次用户新授权一次OJ，见下一条动作。
- C11候选实现保留commit5edc14f/source06f3e06e/356971B；CPU候选模型需对该冻结源运行，当前parent不应误跑或放宽候选模型。

## 本次已完成的真实设备验证

9382/24AIC48AIV/dev0physical14/card7chip0/CANN9/driver26.1.1，hostname2ef29bca0f61。caller limit20不等于物理核数，fixture dtype/layout是明确本地假设，不是读取隐藏OJ属性。

1. C15正确parent2073/DSOca36b327：mixed/fullnegative/五默认报告通过，中位10.940437us。另同context/stream/workspace mixed→negative→mixed三次输出[1.6493455171585083,-40.063804626464844,1.6493455171585083]，最大abs3.8147e-6/rel9.52155e-8；input/yguard完整。原零输出问题已在此机/fixture修复，正式15和另一SoC尚未全证。
2. C15 resident-input42d3e95/dda7b307：编译/精度全部通过，中位10.800432us仅快1.28%，未预设20%gate，归档6d2c47b并恢复2073。不扫描BK/chunk/queue，不OJ。详见C15_RESIDENT_SPLIT_INPUT。
3. C11 BF16TT1/1536/2048/2048 parent actual完整plan BM256BN128/Mt6Nt16Ns16/dual2/workers20/final1（旧128/256不是当前plan），DSOca36。golden116.7254638671875，parent116.72545623779297/abs7.6294e-6；一次及五报告全通过。times[75.783028,76.703072,76.423058,75.923035,76.023041]us，中位76.023041。
4. C11候选 NN交换物理输入计算Cᵀ+原N纵向Max，原GM/任务/credits/finalizer不变，真实SDK新query返回12825664/Ka8Kb2/depthA16B4/db2/2/1。两wrapper独立CANN9/dav2201编译成功，actual selector BF16/FP16均selected1，metadataDSObcd8a8e0/source06f3/wrapper225154c4+included994e29f。
5. C11实际profile TRANSPOSE_Ctrue/20Cube40Vector/default8表×5，一次精度及五性能输出均精确golden/input/yguard完整。但times[79.703186,80.263214,79.023163,79.843193,80.363213]us，中位79.843193，比parent慢5.025%，未预设20%gate<=60.8184328。已经归档并恢复完整2073，不重复采集/相邻NN参数扫描/OJ。Vector5.146→1.953us下降，但AIC MTE1/MTE2上升，不能相加或作单因素因果。详见C11_TRANSPOSED_MDL。

## 下一条可执行动作

- 用户澄清比较最早队友版本，授权一次正式验证；唯一新任务 **6ad046feaad397b6d98aa318** 已创建，kernel2073f48e/353255B、七保护文件及dry-run一致。立即查询同ID到终态，不重复提交。本次授权已用，不沿用此前“无新任务”状态。CANN/15precision/perf PENDING，raw ignored artifacts/producer-ready-formal-20261015。

- 当前没有活跃NPU任务，exec79837/95735/8673均terminal0。全部C11编译/host SDK query/真实selector/correctness/profile包以及C15alternating包已下载，private artifacts目录700/files600。不要重新启动这些任务。
- 后续应从2073出发选择有新证据且未失败的结构方向，或补本机shape/layout/dtype正确性覆盖；不复活C11 NN tiling/C15resident微调。没有达到重大性能突破；仅执行本次用户明确授权的唯一OJ验证，不额外创建任务。
- 各候选具体终态和停止规则看PERF_LOG及独立档案。CPU/编译/native/OJ分开；正式15/另一SoC仍PENDING。
- 用户授权GitHub push当前实验分支，不移动tag/不改写历史；接手先git status/log及本文件。整体冲榜未完成。

## 连接与工具

- 私有SSH配置 /private/tmp/bmmms-remote-access/config，前台master exec60861，ControlPersist=no；先ssh -O check。askpass已删除，凭据不入Git。新入口已实际连接，不沿用旧blocked结论。
- 工作根/workspace/bmmms-codex，工具native_oj_like，Python test-venv/bin/python。source /usr/local/Ascend/cann-9.0.0/set_env.sh，driver/lib64/common及driver/lib64/driver加入LD_LIBRARY_PATH。
- filelock+queue串行NPU，状态npu_test_state.json，启动前检查实际queue/ps。scp需-O（默认sftp Connection closed与平台认证无关）。
- 正确parent冻结imports/c15-producer-ready-2073f48e78d4/kernel.asc，DSO native_oj_like/build-c15-ready/libnative_bmmms.so（ca36b327），完整c11/c15.complete_frame.json均保留。
- C11候选冻结imports/c11-transposed-mdl-06f3e06e0f3f/kernel.asc，DSO build-c11-transposed-metadata/libnative_bmmms.so（bcd8a8e0）；结果results/c11-transposed-{host-query,correctness,profile}。本地artifacts/c11-mdl-transposed-c/c11-transposed-evidence.tgz及summary/pipe比较。
- C15变化输入结果results/c15-ready-alternating，本地artifacts/c15-producer-ready/c15-ready-alternating.tgz。工具input-sequence只用于correctness，性能preset未改。
- 接受源readonly CLI查询6acdd94d会话加载成功但HTTP403，不是401；未取到source/result，不据此要求重登录。

## 避免重复的失败方向

C6 raw-row native精度FAIL归档0689e2d（raw已下载、CPU布局假设被反证，不扫描救活）；C13fullK9.100364→9.040361未15%gate；C12stridedB83.123322→82.683304未10%；C4compact3.060122→3.100124变慢；C15resident仅1.28%；C11 NN Cᵀ慢5.025%。队友C8五轮已结束/C7parked/C9constantSchedule paused，其它历史见TEAMMATE_777734_REVIEW，不改名复做。
