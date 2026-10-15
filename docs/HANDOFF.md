# 当前阻碍：等待新的云平台 SSH 授权入口

恢复后连续三个goal turn遭遇同一远端访问阻碍；前两turn已完成候选CPU协议检查/提交与冻结验证包，本turn再次核对工作区clean/7b65ab5、kernelca66a541、bundle0de34414均未变。干净SSH仍exit255/Connection closed by UNKNOWN port65535；此前platform authorization denied是历史明确诊断。本机bisheng/npu-smi均不存在。无可确认的活跃远端任务handle，queue未知。

当前候选未经CANN/native，不是已通过最优。离线可执行准备已经完成，按项目约定不再叠加未上板算法、不以CPU代替native、不绕过采前大收益门槛提交OJ。下一条实际必需动作是用户刷新云平台授权并给新SSH入口（不需重复root密码），随后执行下文冻结包验证链。此前异步请求仍待答。保留全部scope和冲榜目标，不称已完成。

## 以下为完整候选与验证包交接

# 当前进行：C15 Cube端ready集合，CPU已过，待刷新SSH后编译

- experiment/c15-cube-collective，当前kernel356814B/SHAca66a5417b3ba41d6dd86231e4f3e36fb28dc6ca7df9feb854c1218bee872583，**未经CANN/native验证的实验候选**，不是已确认最优。正式Pass15保留版仍a11e2d9/2073f48e，任务820092总398.92us。
- 从已验证按行8AIV版本81f49ff只改变producer-ready：Cube完成原Fix后mode0 PIPE_FIX flag8全Cube set/wait→mode2 flag9通知各AIV；Vector仅wait9直接进原row finalizer，消除初始AIVbarrier，末尾AIVbarrier不动。原数学/8MMAD/Ksplit8/GM/资源guard逐字81f49ff。不是把two-MMAD与row收益相加。
- 实际CANN9 dav_c220 SyncAllImpl<false>/SetNextTaskStartImpl已有同AIC mode0集合pattern，SDKflags11..14与本8/9分离；全8Cube参与由精确guard保证。mode作用域/运行时配置/消息退休必须native验证，不凭CPU模型宣称硬件正确。
- tools/validate_c15_cube_collective.py：实际协议8producer+8consumer/8种延迟完成顺序/全partial就绪后才允许AIV读、每Cube集合与每AIV配对消息各消费一次/4fault controls/source inverse整81f49ff/保护7 PASS。actual guard production54/TUNING65+容量临界PASS。完整row数学已有81f49ff native证据，未重采。
- 暂停/恢复后旧CPUhandle33625/52590 Unknown process id，恢复新31922/37085 terminal0；原SSH master/control socket消失，干净重连platform authorization denied（无密码错误），已请求刷新入口。上次queue空是在暂停前，**当前远端queue未知**，无新NPU/OJ启动。private reconnect-current.log0600，凭据不入Git。
- **NEXT**：等新入口→检查真实master/queue/ps→冻结imports/c15-cube-collective-ca66a5417b3b/kernel.asc→独立build-c15-cube-collective（wrapper994e29f/原CMake，不改保护7）→绑source/DSO identity→c15.json/c15.complete_frame.json一次correctness→原c15_input_sequence mixed-negative-mixed→一次default8表×5。actual<half,true,true>/8Cube8AIV/每Cube8MMAD。CANN/native/性能/正式15全PENDING。
- gate采前保持median<=9.8463933且全五<父最快10.540421、完整精度/全负/同地址变化/guard后才正式15；另对上一row10.260410报告，20%目标8.7523496。失败恢复2073、不扫flag/row/BK/split、不重采，不降低门槛。C3dtype/layout仍未知。详见C15_CUBE_COLLECTIVE。

## 当前补充：冻结验证包可直接运行，仍未恢复SSH

- 此goal turn先复查ccfaecc/源ca66a541及远端；干净重连仍exit255，仅Connection closed by UNKNOWN port65535。没有收到新入口，不把此前platform拒绝反复说成新明确诊断。远端queue/ps未知，无新活跃handle。
- 已准备tools/native_oj_like/c15_cube_collective/run.sh（tracked）和私有artifacts/c15-cube-collective/c15-cube-collective-validation.tgz（63748B/SHA0de344140d01b8dceb4db104d75e2fded50609a3b49743a6843d403c74c3b660）。source/wrapper/harness/frame/fixture/两input及golden/序列核对，已有结果目录拒绝重启，CANN→identity→一次correctness/alternating/default五报告→打印原gate，无自动OJ。
- Bash语法/三Python AST/九file SHA/wrapper994e29f/archive私有权限和安全路径PASS，仅静态包验证，未执行CANN/native/profile。下条新入口先真实连接/queue/SoC检查→scp-O上传/解压→bash包内run.sh /workspace/bmmms-codex；完整说明见C15_CUBE_COLLECTIVE。用户刷新入口请求仍待答，无需重复root密码。

## 以下为前序终态（当前以上段为准）

# 当前：两条C15结构均完成设备验证，未达门槛，恢复正式Pass15保留版

- 当前experiment/c15-row-finalize，kernel逐字a11e2d9/2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b。正式任务820092/6ad046feaad397b6d98aa318仍是已确认Pass15/398.92us；本次没有新增OJ。
- 新C15完整L0两MMAD source20ee2dde/273073e，归档87ff608：CANN/native精度/全负/同地址变化输入及五报告全通过，actual40个Cube各2MMAD，median10.800432相对正确父10.940437仅快1.28%，未采前10%+全五快于父最快准入。
- 新C15八AIV按行归约 source00c23fa0/81f49ff：原Cube8MMAD不变、全K先于MaxN/原arena行所有权复用。CANN/实际native精度/全负/同地址变化/guard通过，actual<half,true,true>/8Cube8AIV/default8表×5全部完整。times[10.300412,10.360415,9.900396,10.260410,10.080403]，median10.260410仅快6.2157%；五次均快于父最快，但未采前median<=9.8463933。不降低门槛、不重采、不扫邻近行数/核数/slot/BK/split。正式15及其它layout/dtype/SoC未跑。
- raw完整下载artifacts/c15-two-mmad-frame及artifacts/c15-row-finalize，均700/600，包含identity/全部五报告8表/正确性/变化输入/成功编译log及工具错误路径log。详见C15_TWO_MMAD_FRAME/C15_ROW_FINALIZE。两条候选完整源码在原commit可恢复，当前不混入保留版。
- PMU证明两MMAD的归约集中AIV0，按行版本全部8AIV参与；计数有重叠，不能相加或无证据认定同步临界路径。仅改变finalizer一项的latency对照以上正确parent为准，勿用两MMAD PMU当相同producer的因果证据。
- native51976/交替72374/profile1728/下载54635均terminal0，远端queue应空，无活跃OJ。前台SSH master35585仍实际有效；先检查真实连接/queue再开新任务，不要重跑已完成case。
- C3正式只有shape2/7/13/48，dtype/layout用户回复“可能有问题”，仍未知。旧BF16TN native只是fixture，不能反推正式隐藏属性。
- **NEXT**：先只读比较这两条与正确parent的现有完整PMU和实际SDK同步实现，解释额外barrier/原producer-ready约束，识别可证的新同步架构；不凭CrossCore modeId名字删全AIVbarrier，不把两个未达门槛小收益简单相加。若无新语义证据换方向，避免重复已失败结构。整体冲榜目标未完成，继续保留正式Pass15来源并按新完整结构验证。

## 以下为历史完整记录（当前以上段为准）

# 当前进行：C15八AIV按行归约新结构，CPU通过/设备编译中

- experiment/c15-row-finalize，kernel00c23fa0f42564df10187e01ed0b1da03f2c405b64119b8ac3c8e47060bbc406。从正式Pass15保留2073派生，原Cube函数体/GM arena不变，仅新ROW_FINAL默认false/template真分派/精确guard及原arena按行复用finalizer。失败two-MMAD不并入。
- 每AIV覆盖8个完整N64行在全部8Ksplit的贡献，先FP32 SumK再MaxN/Sum8M，自己split0行起点写32B得分槽，MTE3_S+全AIVbarrier后AIV0固定顺序Sum8组分数，4B写y，无atomic/新GM。额外barrier可能抵消收益。详见C15_ROW_FINALIZE。
- CPU实际完整finalizer8线程/4个完整partial张量/6故障控制，host实际guard54+65/资源临界，inverse恢复2073/保护7一致均PASS；不是native证据。
- **NEXT poll exec67879**：CANN9/dav2201 compile，远端/workspace/bmmms-codex/c15-row-finalize-build.log，build-c15-row-finalize，冻结imports/c15-row-finalize-00c23fa0f425。初始95664工具误填目录kernel找不到，已记录/修正，源码未改。成功后写DSO identity（wrapper994e29f/source00c23fa0），仅一次correctness及原c15_input_sequence mixed-negative-mixed，然后一次完整default五profile。native捕获新ROW_FINAL=true/8Cube8Vector/每Cube仍8MMAD。
- 采前门槛median<=9.8463933且所有五<父最快10.540421us、完整精度/全负/变化输入/guard通过，才做进一步正式15验证。20%目标8.7523496；失败恢复2073，不扫行数/核数/buffer/stride，不重采/OJ。当前无新OJ，整体冲榜仍未完成。
- C15两MMAD结果已归档87ff608并推送：真实40个Cube均2MMAD但median10.800432/仅1.28%；raw完整本地。C3dtype/layout仍未知，用户“可能有问题”。连接master35585实际仍有效，凭据不入Git/scp-O。

## 以下保留前序终态（当前以上段为准）

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
