# C15 resident split input：实际分支实现与独立 native 验证

## Parent 与 gate

Parent a11e2d9 / kernel2073f48e/353255B，包含已native验证的Cube PIPE_FIX→AIV等待修复。原ZIP C15输出0，不能作为有效性能对照。正确parent混合输入和全负通过，五完整调用一致，默认五TaskDuration中位10.940437μs；本候选预设20%门槛 **<=8.7523496μs**。

设备9382/24AIC48AIV/dev0physical14/CANN9，callerlimit20；actualnormalPlan dual25/BM64BN64/kSplit8/kChunk1024/workers8/cube8/final1，完整frame逐字段固定。完整用户shape1/64/64/8192，FP16TT为历史对应假设，本机实测入口与数据类型明确。不是正式隐藏属性读取。

## 实现

kernel **356494B / SHAdda7b307090859d1ec4f9f2d88b3622c5d85b26c50eb7f7b32388002b86bce67**，69增5删；算法只改kernel.asc，七个保护文件保持1734f16。

`bmmms_manual_split_tt`新增默认false的RESIDENT_INPUT，保留PACKED finalizer和producer-ready修复：

- 每task A使用一次batched ND2NZ，八个128×64矩阵顺序拼接，字段取值模式沿用原PACK_A；B一次完整64×1024 ND2NZ。每split两次输入DMA，GM总有效2MiB不变。
- A/B各独立MTE2_MTE1就绪。首K面板先wait A，保留A2 LoadData2D，再wait B，执行原B2 LoadData2D；后七面板读相同resident的对应连续片段。
- 原双槽LoadFree/LoadReady、完整8个MMAD、首次cmatrixInit、K顺序、M_FIX/Fix/FIX_M、producer-ready、全部AIV/SyncAll/packed finalizer保持。
- L1由双队列65536B改为两完整split262144B；L0A/B各32768B/L0C16384B，原GM arena和partial总131072B均不变。没有增加GM通路或读写y以外位置。

`UseSplitTTResidentInput`只接受原FP16TT/B1M64N64K8192/dual25/8split1tile/workers8/cube8等真实计划、32B输入对齐、原workspace足够。实际查询L1/L0/UB及至少8AIC/8AIV，L1另留4KiB、UB1KiB。资源不符、任何显式TUNING pin、其它shape/layout/dtype或packed finalizer装不下均回原2073f48e路径，不假定硬件固定20核。资源参数和元数据仍由原MakePlan提供，未强制路由。

## CPU 与 SDK 证据的边界

真实CANN9 Nd2NzParams在dav2201为uint16字段，当前8/128/64/8192均在声明范围；后台copy_gm_to_cbuf_multi_nd2nz_b16直传这些字段。字段存在不代替新组合精度验证。

`tools/validate_c15_resident_input.py`抽取实际新增Read、实际L1选择、实际原LoadData2D块，CPU以唯一源地址tag模拟ND2NZ/2D转置，完整8split/1,048,576个L0元素与parent逐地址一致；A/B两个延迟DMA/ready读取检查、5个故障反例（A matrix stride/B GM stride/A ready/B ready/B panel offset）被拒绝。实际MMAD至Fix和AIV body逐字保持；允许变化范围以parent全文件逆替换检查，保护7文件相同。模型不模拟FP16算术/真实DMA时序，不当硬件布局证明。

`tools/validate_c15_resident_guard.py`抽取实际guard，production/TUNING拒绝47/58个shape/layout/type/plan/align/resource/workspace/pin反例及容量临界值。真实native normalPlan另外读取，guard模型不是SDK tiler。

## Native 状态

新源冻结 imports/c15-resident-input-dda7b3070908；独立CANN9/dav-2201编译PASS，DSO **59878aa09210d0e9be2fdd8a887127f32cb959424320a4e48b2e49319b2b203d** 绑定source/wrapper994e29f。混合输入同frame/fullFP64 correctness PASS。全负及五default报告正在同私有queue串行运行，性能结论PENDING。

比较全部五报告的完整TaskDuration中位，actual符号须为RESIDENT true、8AIC8AIV/默认全部8表/5真实调用，输出/guards/input全部通过。未过20%gate归档恢复正确2073f48e，不重跑或扫参数；过gate才补正式15/相关回退验证并考虑OJ。当前未创建正式任务，不称突破。


## Native终态：正确，但未达到性能门槛，归档

commit42d3e95/source dda7b307/356494B，DSO59878aa0。混合/全负一次correctness和全部五性能输出通过，混合精确fullFP64golden1.6493455171585083，input/yguard完整。默认8表×5，实际符号包含PACKED true/RESIDENT true，8Cube8Vector，每核8个完整K128 MMAD。

五TaskDuration `[10.980439,10.580423,10.800432,10.860435,10.760430]` μs，中位 **10.800432μs**，正确parent10.940437，仅 **-1.279702%**，未达到<=8.7523496us的采前20%gate。不称突破、不重复采集、不扫描BK/chunk/队列深度、不OJ。当前恢复完整正确parent2073f48e/a11e2d9，保留Cube→AIV修复。

PMU各role核心均值五次中位parent→candidate：AIC MTE2 3.659375→2.958681us、MTE1 1.086945→0.921389、MAC0.748125→0.684931、scalar5.270903→2.468750；candidate scalar cube-stall2.889514us而parent0；AIV flag0wait4.678958→4.649792、barrier14wait0.697431→0.786458、Vector0.131320不变。重叠计数不能相加；供料指令变少和部分计数降低没有形成完整op大幅收益，不能将差异单归因于一个计数。

全部原始正确性/负值/profile包、source/DSO/build/summary已下载 `artifacts/c15-resident-split-input`，与远端结果保留。正式15/另一SoC未验证。后续换结构方向前保留本反例，不把相邻面板参数当新方案。
