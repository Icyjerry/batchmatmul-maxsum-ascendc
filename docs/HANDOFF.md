# 当前：C15两MMAD结构验证终态，恢复正式Pass15保留版

- kernel逐字a11e2d9/2073f48e，正式Pass15/398.92us不变。新producer永久保存在273073e，native精度/全负/同地址变化输入/guard全部PASS，但五完整默认报告中位10.800432us对parent10.940437仅快1.28%，未采前10%且全五快于父最快门槛。40个Cube记录确实全部仅2次MMAD；无OJ、无重采、无参数扫描。
- times[10.760430,10.800432,10.740430,11.060442,10.900436]，详见C15_TWO_MMAD_FRAME。raw已完整下载artifacts/c15-two-mmad-frame，目录700/files600。编译/正确性12330/交替52815/profile38701/下载55679全部terminal0，queue空。
- 唯一执行归约的AIV block0平均time8.051/Vec.936667/MTE2.685us，另7AIV time6.172508/Vec.015556us；PMU重叠不相加，证明归约集中而不证明瓶颈因果。下一结构应研究原GM arena内按行分配8个AIV归约，保留全K先于MaxN、确定性SumM及ready通知；不要重做BK/slot/split参数。
- C3正式dtype/layout仍未确认，用户回复“可能有问题”。不将本地BF16TN当隐藏事实。

## 以下保留前序记录（当前以上段为准）

# 当前进行：C15完整L0单缓冲两MMAD新producer已编译，native精度验证中

- 分支experiment/c15-two-mmad-frame，当前kernel20ee2dde864cc79ec7cd395dfc0c4a2c3f7bfd9a8d6585f63d80715c85cfa1c4，77新增行；parent2073f48e/a11e2d9正式Pass15/398.92us。只增加新producer/guard/dispatch，原函数/GM/MakePlan/其它kernel逐字保持。
- 固定原C15 FP16TT/B1M64N64K8192/dual25/8splitK1024/8workers，L1完整split262144B、单L0A/B各65536B、两次K512 MMAD/4次Load2D，Cube无源级TPipe队列、仅4GM ABI。原Fix通知→AIV等待→全AIVbarrier→原packed finalizer不变。旧resident8MMAD反例未直接并入、不扫BK参数。
- CPU实际producer4194304地址/32split/4full数学golden/7反例，guard54/65+满容量临界、inverse/保护7通过；不是native布局/速度证明。详见C15_TWO_MMAD_FRAME。
- CANN9/dav2201编译PASS，DSOf8f1da4c8d1af3a8ea691fef9433f8219370f109fb704cd6d02588776b76747d /source20ee2dde/wrapper994e29f。frozen imports/c15-two-mmad-20ee2dde864c/kernel.asc，native_oj_like/build-c15-two-mmad/libnative_bmmms.so。
- **NEXT poll exec12330**，results/c15-two-mmad-correctness；成功后同frozen c15.json/c15.complete_frame.json/inputs/c15跑原c15_input_sequence.json的A/B/A correctness，再一次default五报告，actual新symbol/8Cube8Vector/每核每次2MMAD必须确认。
- 新active目标采前准入：median<=9.8463933us（parent10.940437降低>=10%），所有5样本<父最快10.540421，且完整精度/全负/变化输入/guard全部通过，才能进一步正式15验证。20%目标8.7523496仍保留。未达归档恢复2073、不扫参数/重采/OJ。尚无性能结论或新OJ。
- 连接master35585已实际检查有效、hostname2ef29bca0f61/9382/24AIC48AIV/dev0physical14/CANN9；queue初始空，编译97125 terminal0，当前仅12330一次correctness。凭据不入Git，scp-O。

## 以下为前序完整终态与操作约定（当前状态以上段为准）

# 当前：三条新结构验证终态，恢复正式Pass15的2073

## 有效保留版本与Git

- 当前分支experiment/c3-flat-gather，kernel **2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b /353255B**，逐字a11e2d9。正式任务820092/6ad046feaad397b6d98aa318已Pass15/allprecision1，总398.92us；含实际修复C15零输出的Cube PIPE_FIX→AIV就绪通知，不回退已反证的ZIP078635。
- 用户本轮要求开始优化，已完成C6/C1/C3三条独立结构试验，均未达到预设20%提交门槛，未增加任何OJ任务。失败代码和数据完整保存，不混入保留版。
- 算法仅kernel.asc；保护7等1734f16，正式测试/阈值/SDK/main/CMake均未改。GitHub允许push实验分支，不移动tags/main或改写历史。

## 三条本次实验（native实测）

1. **C6 compact NZ**，实现5fc448b/source360db6f0，归档6fd56e0。保持输入/完整K192/UnitFlag3/握手/arena，将有效M23紧凑NZ交接，写10240→7360B。native精度一次+五输出通过，actualtrue/13Cube13Vector/default8表×5。8.860354→8.820353us仅0.4515%，未gate7.0882832。不扫format/stride/重采/OJ。raw artifacts/c6-compact-nz-output，详见C6_COMPACT_NZ_OUTPUT。
2. **C1 scalar-cache fullK32**，实现28e1a82/source4c081854，归档34f72b0。NPU scalar GM直读真实编码、FP32两链累加、输入失效/UB刷新/S_MTE3/4B输出/PIPE_ALL。初始9e699fe1因CANN publicLocal Dcci封装const_cast非法编译FAIL，未改SDK；修正用实际内部同dcci指令，CANN通过/DSObf9f52ce。FP16一次及同context/stream/input地址A/B/A全负变化通过，guard/input完整。五times[7.840313,7.880315,2.240090,2.280091,2.340094]，median2.340094，parent1.600064，慢46.25%；高值全保留不无证据归因，不删缓存维护/扫unroll或accumulator救性能，不OJ。raw artifacts/c1-scalar-cache-dot/c1-scalar-evidence.tgz，详见C1_SCALAR_CACHE_DOT。BF16硬件/正式15未做。
3. **C3 flattened Gather**，实现a55b767/source8b13ff71/DSO5a7b7194。Brcb/Add完整offset矩阵每input一次Gather，原DMA/Cast/Mul/Ksum/Nmax/Msum不变/extraUB3008。native一次+五完整输出fullFP64精确，actualbf16/TN/K48/FLAT_GATHERtrue/pureVector2AIV/default8表×5。parent[3.420137,3.020121,2.880115,3.120125,2.920117]median3.020121，candidate[3.320133,2.740110,3.160126,2.820113,2.840114]median2.840114，约快5.96%，样本重叠，未gate2.4160968。不重复/扫stride/附近shape/OJ，恢复2073。raw artifacts/c3-flat-gather/c3-flat-gather-evidence.tgz，详见C3_FLAT_GATHER。

全部raw已下载，目录700/files600，精确source/DSO/input/plan绑定、所有样本保留。CPU模型均只对各冻结候选运行：不要改成在parent运行也报告PASS。default逆变换/保护7、实际资源边界/负控制完整，不能替代硬件精度/时序。

## 属性与下一条可执行动作

- 正式C3只有用户shape记录2/7/13/48，dtype/layout未唯一确认；用户本轮回复“可能有问题”。本地BF16TN仅明确fixture，不用本地耗时反推隐藏属性，不将native改善当正式覆盖。
- 当前全部设备任务terminal0、queue空，无活跃OJ或新性能候选。下一先检查已有编译对象的NPU指令/代码生成和PMU，解释源级Gather/GM减少为何完整收益有限，避免复做三条邻近参数。工具发现可用objdump后只读既有binary，不需要再采同输入性能。若编译对象不支持读，记录限制后选真正不同的结构，别强行解释延时。
- 当前正确parent DSO **ca36b327c9104b3006de2bb7ec732a3b817ae8fff447c6ce2a37e2d9c5fd28e6**，native_oj_like/build-c15-ready/libnative_bmmms.so；source imports/c15-producer-ready-2073f48e78d4/kernel.asc。
- C6 candidate build-c6-compact-nz、C1 candidate build-c1-scalar-dot-fixed、C3 candidate build-c3-flat-gather，各.so及identity.json/源都在/workspace/bmmms-codex。完整reviewed c1/c3/c6.complete_frame.json及inputs/c1/c3/c6保留。

## 比赛目标与旧反例

当前正式向量[2.09,2.64,3.12,4.19,4.70,9.45,6.64,36.47,56.95,76.65,78.43,88.04,8.84,9.61,11.10]us，总398.92；用户第一名总348.37，整体慢14.51%。按固定旧Tbest敏感度C6/C1/C3优先，计分非总时长。最新实时Tbest未读取，不称排名。

C15resident仅1.28%归档6d2c47b；C11NN Cᵀ慢5.025%归档3ff5ff4；C6raw Load3D精度FAIL0689e2d；C13fullK仅.66%；C12stridedB仅.53%；C4compact变慢。旧tiny raw transpose/storage Ktree/static FT/literal Vector无明确收益。本轮三结构同样不换名复做。队友C8五轮结束/C7parked/C9constantSchedule paused，其它见TEAMMATE_777734_REVIEW/PERF_LOG。接受队友b881与ZIP078635身份不同，不能借其成绩。

## 连接与操作

私有config /private/tmp/bmmms-remote-access/config，前台master exec35585/ControlPersist=no，先ssh -O check；askpass已删、凭据不入Git，scp需-O。hostname2ef29bca0f61、Ascend910_9382/actual24AIC48AIV/dev0physical14/card7chip0/CANN9/driver26.1.1，caller20不等于硬件核数。新入口已实际连接，不沿用旧blocked结论。

工具/workspace/bmmms-codex/native_oj_like，Python /workspace/bmmms-codex/test-venv/bin/python。source /usr/local/Ascend/cann-9.0.0/set_env.sh，driver/lib64/common及driver/lib64/driver加LD_LIBRARY_PATH。filelock+queue串行NPU，状态/workspace/bmmms-codex/npu_test_state.json，启动前查真实state/ps。最后C3profile28889、baseline28094、编译47243均terminal0。

当前parent正式15已过；平台未给actualSoC/plan/profile，不能把本地9382当OJ机器或另一SoC覆盖。整体冲榜目标未完成。

## 只读codegen检查已完成的限制

已从保留build-c15-ready/library.asc.o解析两份现有device ELF，源对象SHA bf99376c。当前llvm-objdump能读函数symbol尺寸（C6AIC504/AIV1072、C1 FP16group2 876、C3BF16TN/K48 2116B），但反汇编opcode全not available，显式mcpu也无效；不能据此声称多少条指令或瓶颈原因。SDK msobjdump对新ASC fatbin也不列出，未改工具。原始包artifacts/native-codegen-audit/codegen-audit-evidence.tgz（下载完成后），远端codegen-audit保存extract.py/ELFs/summary/失败asm。

后续可核对bisheng实际help中的save-temps/汇编输出选项，仅在独立工具构建保留同源时保存生成汇编；这比再扫三条失败方向的参数更有证据价值。当前没有第四个性能候选，正式保留源仍2073。
