# C15 完整 L0 单缓冲：每 split 固定两次 K512 MMAD

## 实际依据与本次边界

从已正式Pass15/398.92us的parent2073f48e/a11e2d9派生，保留C15 producer-ready正确性修复。前一goal turn完成C6/C1/C3三个独立结构的原始设备证据，改变了下一步选择，属于有证据的进展；本次转向完整Cube流水重构。

原正确C15本机FP16TT/B1M64N64K8192：9382/actual24AIC48AIV/dev0physical14/CANN9/caller20，actual dual25/BM64BN64/kSplit8/kChunk1024/workers8/final1，whole reviewed frame已保存。父DSOca36，mixed/negative/变化输入/五输出fullFP64通过；五完整TaskDuration[10.540421,10.940437,11.080443,11.540462,10.760430]us，中位10.940437us。

此前resident-input试验只改变GM→L1供应而保留每split8个K128 MMAD和双槽L0，10.800432us仅1.28%，已归档。其PMU MAC0.684931us、MTE1 .921389、scalar cube-stall2.889514等重叠计数不相加。本次固定重写为完整split L1、满容量单槽L0、两次K512 MMAD以及静态frame/精简ABI，不执行多点BK/chunk/队列扫描。最新用户目标明确鼓励有依据的激进实现，本次按新的完整结构假设验证，旧resident代码不直接并入，旧失败结论保留。

## 采前准入标准（先于候选性能）

完整FP64精度、输入/yguard、mixed/negative/同地址变化输入、全部5次default报告及实际新symbol/8Cube8Vector/每Cube两MMAD都必须通过。

在本次新目标下，允许**中位至少降低10%（<=9.8463933us），且全部5个候选样本均小于父版最快10.540421us**的结构进入正式15点验证；**降低20%（<=8.7523496us）**仍是追近第一名C15的目标。这是采前重新定义候选准入标准，不是结果出来后降低门槛，也不是把单点收益当整体冲榜完成。

未达新准入则完整归档/恢复2073，不反复调512大小、L0槽数或split数，不重采同源/OJ。达到后才做必要回退/正式完整15验证并评估真实成绩。正式C15 dtype/layout仍是历史对应假设，native输入属性明确，不冒充读取了隐藏数据。

## 源码与内存/事件

候选kernel SHA **20ee2dde864cc79ec7cd395dfc0c4a2c3f7bfd9a8d6585f63d80715c85cfa1c4**，77行新增。原函数/MakePlan/allocator/GM arena/所有其它算子逐字保持；仅新device入口、精确资源guard和原dual25分派。保护7不变。

每个Cube处理原唯一K1024 split，worker*1024确定输入段：

- L1 A/B各131072B共262144B，A一次batched ND2NZ（两片512×64，src/dst matrixStride32768元素），B一次64×1024 ND2NZ（GM行距8192）。GM有效输入字节仍2MiB，不增加通路。
- L0A/B各一个65536B缓冲，存64×512 native16bit元素。A2/B2每半段各一次LoadData2D、repeat128，A transpose、B no-transpose；总4次LoadData与2次MMAD，原为16次LoadData与8次MMAD。L0C仍16384B。
- M_MTE1 free0先初始化，每次加载前wait，MTE1_M ready0后才MMAD；两次累加只有首次数学清零，升序覆盖完整K1024。MMAD发出free0，第二片覆写必须等第一次reader结束；末次free在退出前consume。
- 输入A0/B1两条MTE2_MTE1，先等A并load A，再等B；第二片使用完整resident数据。原8个partial/原Fix ND64×64/PIPE_FIX→AIV通知/全AIV SyncAll/原PACKED finalizer完全保留。
- 源级Cube端直接LocalTensor和固定event0/1，无TPipe队列/动态event分配；新kernel仅4个GM参数，Vector端构造与native plan相同的constexpr Schedule、继续原TPipe finalizer。全K完成后先Sum split，再MaxN/SumM，未引入atomic或非确定性归约。

Guard限定原FP16TT/1,64,64,8192与完整Schedule/usedCoreNum/cubeBlocks8/final1，actualAIC/AIV>=8、L1>=266240/L0A/B>=65536/L0C>=16384/UB>=132928、原workspace字节精确相同、GM32B对齐；任一TUNING pin/其它输入/资源变化回原路径。L0A/B容量恰满是本次明确风险，actual SoC查询和native结果决定可用性。

## 已有验证与未完成

CPU模型提取实际整个Cube producer，延迟两次DMA、MMAD读者和Fix写入；4194304个源地址检查、32split task/每task两次MMAD、4个完整M64N64K8192整数输入golden及负输出、输入/partial guard通过。七个故障反例覆盖A矩阵stride、B GMstride、B未ready、L0早覆写、MTE1未ready、重复清C、Fix未完成就通知。完整逆变换恢复parent，literal Schedule与原frame核对、保护7一致。模型不模拟真实FP16/硬件DMA排布/速度。

真实guard production/TUNING分别54/65拒绝及所有资源容量临界值通过，L0A/B恰65536接受、少1B拒绝；不是SDK tiler或native命中证明。

CANN9/dav2201独立SHARED编译PASS，8条原host GM_ADDR attribute warnings。DSO **f8f1da4c8d1af3a8ea691fef9433f8219370f109fb704cd6d02588776b76747d**，source20ee2dde/wrapper994e29f，冻结imports/c15-two-mmad-20ee2dde864c；首次native correctness exec12330进行中，mixed/negative/变化输入/五报告/正式15结果PENDING。未创建新OJ任务，不称已提升。

## 2026-10-15 终态：未达准入，恢复保留版

CANN编译及首次native、同context/stream/输入地址的mixed→全负→mixed均PASS；混合输出精确1.6493455171585083，全负-40.063804626464844，绝对误差3.8146973e-6。输入不变及16-word输出guard通过。

一次完整默认8表×5报告：actual新two_mmad符号/8Cube8Vector，40个Cube记录全部恰2条MMAD；五完整输出fullFP64精确。TaskDuration **[10.760430,10.800432,10.740430,11.060442,10.900436]us**，中位 **10.800432us**，相对正确parent10.940437仅快 **1.2797%**，全部样本还慢于父最快10.540421。未达采前10%及全样本门槛，不提交OJ，不保留新producer，不扫描邻近参数。

PMU按实际block_id分组（不能把每核sub_block_id=vector0误当全局Vector0）：Cube平均aic_time5.360236/MTE2 2.995264/MAC0.616667us；唯一执行完整归约的Vector block0平均aiv_time8.051000/Vector0.936667/MTE2 .685000us，其余7个AIV平均aiv_time6.172508/Vector .015556us。计数重叠，不能相加或据此断言临界路径，但它直接证明归约仍集中单AIV、其余AIV未分担。

全部raw、identity、5份8表已下载artifacts/c15-two-mmad-frame/c15-two-mmad-evidence.tgz，summary/pmu-summary同目录，权限700/600。候选源码在273073e永久保留；工作kernel恢复a11e2d9:kernel.asc/2073f48e。完整正式15/其它SoC未跑，未新增OJ任务。
