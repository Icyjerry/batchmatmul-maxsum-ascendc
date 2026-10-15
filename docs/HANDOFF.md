# 当前进行：C3 flattened Gather 已编译，native精度验证中

## 当前源码与有效保留版

- 分支experiment/c3-flat-gather。候选kernel SHA **8b13ff71f8d5897048efee80c4f8817f7d4c1098308f501eb789df473d2c598b**，仅在原grouped K48/B2M7N13/group1/2AIV需转置输入时，Brcb/Add生成完整offset矩阵，每input一次Gather代替逐行Gather。原DMA/Cast/Mul/Ksum/Nmax/Msum和GM不变，UB额外3008B；其它/pins回默认。35增6删。详见C3_FLAT_GATHER。
- 有效保留parent **a11e2d9/kernel2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b/353255B**，正式任务820092/6ad046feaad397b6d98aa318已Pass15/allprecision1，总398.92us。含C15 Cube PIPE_FIX→AIV就绪修复，别回退到本机C15输出0的ZIP078635。接受队友b881与ZIP不同，不借它成绩。
- 算法只kernel.asc；七保护文件等1734f16。main/历史tags不动，无SDK/编译规则/正式测试/容差改动。GitHub允许push实验分支，不改写历史。

## 本次C3证据与下一条动作

- 正式C3 dtype/layout尚未唯一确认，已通过async询问用户；当前本地fixture **BF16 TN** /B2M7N13K48。不能把此假设当隐藏属性。TT/FF也具备Flatten入口，NT原无Gather回原路径。
- 原source2073/DSOca36实际plan dual24/group1/workers2/final2/Cube0/total0，纯Vector2AIV；fullstorageFP64golden[1.5601825714111328,1.773697018623352]，一次及五性能输出精确通过/input及yguard完整。
- baseline默认8表×5 times[3.420137,3.020121,2.880115,3.120125,2.920117]us，中位3.020121。采前20%gate **<=2.4160968us**。不过归档恢复完整2073，不扫repeat/stride或相邻M/N/K、不重采/OJ。通过再补相关dtype/layout/negative/变化输入/回退并考虑正式15。
- CPU实际Brcb/Muls/Add/Gather执行48 fullK batch-layout/mixed-negative pairs，canonical operands/全部dot/MaxN-SumM/bounds/UBguard/5反例通过；default inverse恢复parent全文件及保护7。guard production/TUNING31/64拒绝、每布局UB临界TF36608/TT34144/FF35296通过。只是模型，非硬件证据。
- source8b13ff71独立CANN9/dav2201编译PASS；DSO **5a7b719401d77aa7febe05a95ff17bed2b72f82a6b639d824c44620e934f2fbb** /wrapper994e29f。完整identity sidecar已写。
- **NEXT poll exec97615**，当前一次correctness results/c3-flat-gather-correctness。通过才运行一次default五报告；actual mangled symbol须有FLAT_GATHERtrue，2AIV/default8表×5/五golden/guards/input完整。若transport观察丢失先查queue/ps/results，别重跑。
- reviewed frame native_oj_like/c3.complete_frame.json；case c3.json；inputs/c3；baseline results/c3-baseline-{plan,correctness,profile}；candidate frozen imports/c3-flat-gather-8b13ff71f8d5，DSO native_oj_like/build-c3-flat-gather/libnative_bmmms.so；buildlog同工具根。raw待终态下载artifacts/c3-flat-gather。

## 本次已结束的独立候选

- C6 compact NZ：实现5fc448b/source360db6f0，archive6fd56e0。完整FP64及五输出通过，实际true/13Cube13Vector/default8表×5；8.860354→8.820353us仅0.4515%，未20%。已恢复2073，不扫format/stride/重采/OJ。全部raw下载artifacts/c6-compact-nz-output。C6_COMPACT_NZ_OUTPUT详述。
- C1 scalar-cache：实现28e1a82/source4c081854，archive34f72b0。初始9e699fe1因SDK publicLocal Dcci封装const_cast错误编译FAIL，未改SDK；修正源采用对应dcci指令编译PASS/DSObf9f52ce。native FP16 mixed及同输入分配/stream/context A/B/A全负变化通过，input/yguard完整。五time[7.840313,7.880315,2.240090,2.280091,2.340094]中位2.340094，parent1.600064，慢46.25%；高值全保留，不删缓存维护/扫unroll/accumulator/重采/OJ。BF16硬件/正式15 NOT RUN。全部raw已下载artifacts/c1-scalar-cache-dot/c1-scalar-evidence.tgz，目录700/files600。C1_SCALAR_CACHE_DOT详述。
- 上述均未带入当前C3，当前结构从完整2073派生。无活跃正式OJ任务，本次仅开展本地优化；只有重大已验证收益才考虑新任务，不默认重复提交。

## 比赛对照与此前失败

- 现保留源正式15向量[2.09,2.64,3.12,4.19,4.70,9.45,6.64,36.47,56.95,76.65,78.43,88.04,8.84,9.61,11.10]us，398.92us；用户最新第一名总348.37us，我方总慢14.51%。计分均分不是总耗时，固定旧Tbest敏感度C6/C1/C3优先。最新实时Tbest未读取，不称实时排名。
- C15resident仅1.28%归档6d2c47b；C11 NN Cᵀ慢5.025%归档3ff5ff4；C6raw Load3D精度FAIL归档0689e2d；C13fullK仅.66%；C12stridedB仅.53%；C4compact变慢。不要改名复做/附近参数扫。
- 旧tiny raw transpose/storage Ktree/static FT/literal Vector候选已经无明确收益；当前C3是只改变Gather地址生成与批处理的新结构。队友C8五轮已结束/C7parked/C9constantSchedule paused，其它反例见TEAMMATE_777734_REVIEW及PERF_LOG。

## 服务器与操作

- 私有config /private/tmp/bmmms-remote-access/config，前台master exec35585/ControlPersist=no，先ssh -O check；askpass删除，不记录/提交凭据。scp需-O。
- hostname2ef29bca0f61，实际Ascend910_9382/24AIC48AIV/dev0physical14/card7chip0/CANN9/driver26.1.1，callerlimit20。fresh入口已实际连接，不沿用旧blocked结论。
- 工作根/workspace/bmmms-codex；工具native_oj_like；Python test-venv/bin/python。source /usr/local/Ascend/cann-9.0.0/set_env.sh，driver/lib64/common及driver/lib64/driver进LD_LIBRARY_PATH。
- filelock+queue串行NPU，状态npu_test_state.json。编译47243已terminal0；C3baseline28094/8286 terminal0，当前只97615 correctness。所有CPU/编译/native/OJ分开报告；9382本地不是另一SoC覆盖，正式平台未提供actualSoC/plan/profile。
- 正确parent DSO build-c15-ready/libnative_bmmms.so/ca36b327，frozen imports/c15-producer-ready-2073f48e78d4/kernel.asc。整体冲榜目标未完成。
