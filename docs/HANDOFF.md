# 当前进行：C1 NPU scalar-cache完整K32候选编译中

- 分支experiment/c1-scalar-cache-dot，实现28e1a82/source4c0818544891c4b0da051d4777417871fb179accd3d4023c23614bdd0274dbbe，parent2073f48e正式Pass15/398.92us。C6compactNZ失败已归档6fd56e0，未带入。
- C1新结构为NPU scalar GM直读/实际编码解码/FP32全K32累加，不是CPU计算/旧literal Vector。输入cacheline64B显式失效、UBcacheflush/S_MTE3/4B输出/PIPE_ALL，实际资源和对齐guard。CPU全部有限128768编码/256完整dot/6反例、guard22/33、inverse/保护7通过。
- 初始9e699fe1编译FAIL（CANN publicLocal Dcci封装const_cast错误），未改SDK。修正4c081854用SDK内部同dcci指令；当前compile exec66564/build-c1-scalar-dot-fixed。先poll同handle，不因SSH断开重编译。详见C1_SCALAR_CACHE_DOT。
- baselineC1原DSOca36一次精度及五profile通过，median1.600064us，采前20%gate<=1.2800512us。actual c1.complete_frame.json/fixture c1.json；candidate c1_scalar.json仅期望symbol不同，inputs/c1-scalar的b16/golden字节与baseline完全相同。先精度再profile全5，过gate补BF16/变化输入/全负/OJ，否则归档恢复2073，无相邻扫描。
- SSHmaster35585/hostname2ef29bca0f61/9382/dev0physical14/24AIC48AIV，queue空，askpass删；C1baseline39147 terminal0。

## 下方为C6及前序过程档案（状态以上段为准）

# 当前终态：C6 compact NZ未过性能门槛，恢复正式Pass15的2073

- 实现5fc448b/source360db6f0已归档：native完整精度及五输出通过，actualtrue/13Cube13Vector/default8表×5，8.860354→8.820353us仅0.4515%，未20%gate。不扫相邻NZ参数/重采/OJ。raw全下载，详见C6_COMPACT_NZ_OUTPUT。
- 当前kernel完整2073f48e/a11e2d9，正式Pass15/398.92us，后续从此派生C1标量GM直读结构审查，不重做已失败literal Vector。新主连接exec35585，所有C6设备任务均terminal0，队列空；凭据不入Git。

## 下方为过程及前序档案（状态以本段为准）

# 当前进行：C6紧凑NZ输出已编译，native精度验证中

- 分支experiment/c6-compact-nz-output；当前候选360db6f00491f00cf10626e867fcacd7ff741f8b5ab04c50a5115c3ae130604b。正确保留parent2073f48e/a11e2d9已经正式Pass15/398.92us，不覆盖其证据。失败恢复完整parent。
- C6保持输入/完整K192/UnitFlag3/通知/grid/arena，改变有效M23紧凑NZ交接，写10240→7360B；详见C6_COMPACT_NZ_OUTPUT。CPU fullK78pairs/5反例、default逆补丁、guard36/47通过；CANN编译PASS，DSO046682f0。
- 当前exec69188一次correctness（results/c6-compact-nz-correctness）进行中，先poll同handle；通过后同输入/frame/default五报告，门槛<=7.0882832us。失败归档恢复2073，不重采/扫参数/OJ；通过再补全负/变化输入/回退及正式15。
- 新SSHmaster35585，config同私有路径，已验证hostname/mapping/queue，askpass已删除。源imports/c6-compact-nz-360db6f00491、DSO native_oj_like/build-c6-compact-nz。

## 前一工作终态（保留历史上下文）

# 当前工作：整合保留版正式Pass15/398.92us；第一名对照348.37us

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

- 用户授权的唯一正式任务 **6ad046feaad397b6d98aa318 / 820092** 已终态Pass15/allprecision1，总398.92us；kernel2073f48e/353255B，服务端SHA、保护7及dry-run一致。向量[2.09,2.64,3.12,4.19,4.70,9.45,6.64,36.47,56.95,76.65,78.43,88.04,8.84,9.61,11.10]us。此次授权已完成，无活跃OJ，不重复提交。完整official在ignored artifacts/producer-ready-formal-20261015。

- 当前没有活跃NPU任务，exec79837/95735/8673均terminal0。全部C11编译/host SDK query/真实selector/correctness/profile包以及C15alternating包已下载，private artifacts目录700/files600。不要重新启动这些任务。
- 用户最新第一名向量总348.37us，当前总慢14.51%；C7齐平，C12仅慢3.25%。按此前固定Tbest均分收益优先C6/C1/C3（到第一名合约9.28分），再C9/C15等；最新Tbest未读取，不称实时分数/排名。要有新结构证据，不复做已失败tiny/Load3D原始布局/C11 NN/C15resident或相邻扫描。向量及计算在PERF_LOG/ignored leader-comparison.json。
- 各候选具体终态和停止规则看PERF_LOG及独立档案。CPU/编译/native/OJ分开；当前源正式15已通过；平台未提供actualSoC/plan/profile，另一明确SoC本地覆盖仍PENDING。
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
