# 当前工作：C11 Cᵀ MDL 完整精度通过，五次默认性能采集中

## 当前源码与保留 parent

- 分支 experiment/c11-mdl-transposed-c，parent a11e2d9/kernel2073f48e/353255B 是当前有效保留版本：含 C15 Cube PIPE_FIX→AIV 等待修复。不要回退到已被本机反证 C15输出0的原 ZIP078635；接受源b881与ZIP不同，不能借其Pass15。
- 当前候选 kernel356971B/SHA06f3e06e0f3fde1e3cd7c63e2487f978298e0502ef6ca8ad9bcb0a6cb25050c5。C11 TT 用物理输入交换计算 NN Cᵀ，再沿原 N 纵向Max，原 M Sum/任务/GM arena/credits/finalizer不变。其它入口及保护7保持。详见 C11_TRANSPOSED_MDL.md。
- C15 resident-input 候选42d3e95/dda7b307已经完整验证且归档6d2c47b：10.940437→10.800432us仅1.28%，未20%门槛；不重复/参数扫描/OJ，完整恢复2073后才开展当前 C11。

## 当前 native 证据

- hostname2ef29bca0f61，Ascend910_9382/24AIC48AIV/CANN9/driver26.1.1，dev0physical14/card7chip0，callerlimit20。FP16/BF16属性是本地fixture明确假设，不是已读取隐藏OJ属性。
- C15正确parent2073/DSOca36b327：mixed/fullnegative/五默认报告全部通过，中位10.940437us；新同context/stream/workspace mixed→negative→mixed三次再次通过，输出[1.6493455171585083,-40.063804626464844,1.6493455171585083]，最大abs3.8147e-6，input/yguard完整。独立工具 optional input-sequence 仅correctness可用，不改性能preset。
- C11 BF16TT1/1536/2048/2048实际parentnormalPlan BM256BN128/Mt6Nt16Ns16/dual2/workers20/final1（旧注释128/256不是当前plan）。source2073/DSOca36完整FP64golden及五性能输出通过：76.023041us中位，actual MIX20Cube40Vector/default全部8表×5。raw已下载artifacts/c11-mdl-output-audit。
- C11候选两份独立wrapper均CANN9/dav2201编译成功；带metadata export的DSObcd8a8e0951a3d9b255088a2b7ad8e8c48b5cbcdb3506ae6151e1209414b7cde，source06f3，wrapper225154c4/base994e29f身份绑定。新入口检查上一SSH断开时的编译实际已经完成，没有重编译。
- actual host selector（无kernel launch）BF16及FP16均selected1，freshNN tiling128/256/64、stepKa8/depthA16、stepKb2/depthB4、dbl2/2/1/shareL1393216；独立host query初始漏arch编译失败，补自建CMake dav2201后通过。原CMake没改。
- C11候选一次完整native precision PASS，实际116.7254638671875与fullBF16storage→FP64golden精确，input/yguard完整。完整性能采集正在exec79837，不能重复启动同任务。
- CPU抽取实际operand、offset/tail、GM copy、纵向Max，6个完整构造C矩阵及4反例/默认分支逆补丁/范围/保护7通过；不是完整K硬件计算证据。

## 下一条可执行动作

1. poll exec79837；远端 results/c11-transposed-profile 和queue判断真实状态，不能因SSH观察失效重跑。
2. 只比较全部五报告完整TaskDuration中位、actual TRANSPOSE_Ctrue/20AIC40AIV、8表×5、五golden/guards/input。采前20%门槛 **<=60.8184328us**（baseline76.023041）；未达则保存证据、恢复完整2073/a11e，不做相邻参数/无变化重采。通过才补FP16/fullnegative/回退与正式15覆盖，考虑OJ。
3. 下载candidate build/metadata/correctness/profile与C15alternating原始资料，更新PERF_LOG及本文件，commit/push当前分支。目录700/files600，凭据不入Git。
4. 当前无新正式OJ任务，无突破声明。既有 CLI会话加载成功但HTTP403不是401，不凭此要求重新登录。整体冲榜任务未完成。

## 连接与工具

- 私有SSH配置 /private/tmp/bmmms-remote-access/config，前台master exec60861，ControlPersist=no；先ssh -O check。askpass已删除。fresh入口已实际连接，不沿用旧blocked结论。
- 独立工具 /workspace/bmmms-codex/native_oj_like；Python /workspace/bmmms-codex/test-venv/bin/python。source /usr/local/Ascend/cann-9.0.0/set_env.sh，并把driver/lib64/common和driver/lib64/driver加LD_LIBRARY_PATH。
- filelock+queue串行NPU，状态/workspace/bmmms-codex/npu_test_state.json。传输scp需-O（默认sftp Connection closed），未涉及平台权限问题。
- 当前候选冻结 imports/c11-transposed-mdl-06f3e06e0f3f/kernel.asc；metadataDSO build-c11-transposed-metadata/libnative_bmmms.so；correctness results/c11-transposed-correctness，真实host query results/c11-transposed-host-query，reviewed c11.complete_frame.json仍为原MakePlan完整frame。
- 正确parent冻结 imports/c15-producer-ready-2073f48e78d4/kernel.asc / build-c15-ready/libnative_bmmms.so；新序列结果 results/c15-ready-alternating。

## 失败档案与边界

C6 raw-row native精度FAIL已归档0689e2d（raw已下载，CPU布局假设被反证，不扫描救活）；C13fullK9.100364→9.040361us未15%gate；C12stridedB83.123322→82.683304未10%；C4compact3.060122→3.100124变慢；C15resident仅1.28%。队友C8五轮已结束/C7parked/C9constantSchedule paused，C10/C11旧失败见独立档案和TEAMMATE_777734_REVIEW，不改名复做。

所有正式15/另一SoC尚待验证，不把本机单fixture当正式全部通过。算法仅kernel.asc；保护7不变，不移动历史tag/main或改写Git历史。GitHub允许push当前实验分支。
