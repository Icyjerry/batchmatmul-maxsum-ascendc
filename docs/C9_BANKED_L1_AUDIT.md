# C9：按 K 包重排 L1 双半区及两路独立预取（实现前审计）

## 当前事实与新假设

当前kernel仍逐字2073/a11e2d9；无新C9设备代码/编译/采样/OJ。正式820092保留。C9本机actual captured plan FP16NT B1/M2048/N1536/K1280，BM=BN=BK128、PK256、Ns5/window3/workers20/dual36，9382/24AIC48AIV/caller20。原parent五报告median55.142204us，min54.922195；各完整输入/实际frame见C9_LEFT_FMATRIX和artifacts/c9-stationary-b-audit。老stationary-B已证明最忙核GM不减少，老FMatrix只.87%，旧N-pair共享A也失败，不重做。

新的问题不是FMatrix设置次数。现有RunManualFullMCube先给完整A327680B分配连续L1，再给两个B包分配各65536B；按该布局，两B缓冲起点327680/393216均在512KiB L1的第二半区。需要检查MTE2写未来B与MTE1读当前A/B的供数重叠。

实际CANN9 SDK `.../asc/impl/adv_api/detail/matmul/resource/l1_manager/l1_manager.h`（SHA2259fc34725473c222a64965af21e711bbc68970987c45c6ecbee116909d58f7）以及`cube_in_buffer/cube_in_buffer_double_buffer.h`（SHA9a4c532e5407c7900c03edbda967bc8d1dd66642fc3206d033ed7abe7de64d5f）显示enableL1BankConflictOptimise的参考实现把双缓冲分别放在0/262144开始的两个半区。该内部类不在kernel直接调用。header旧注释关于支持设备并不完整；这些分配代码是设计依据，不是9382物理端口/电气bank映射或性能证明。不能靠字段名称保证速度。

## 提议的真实表示改变

同一个原始完整A，按5个K256包重新摆放；每包A=128x256x2=65536B。

| K包j | 原K起点 | A L1 byte base | 区域 |
|---|---:|---:|---|
|0|0|0|half0|
|1|256|262144|half1|
|2|512|65536|half0|
|3|768|327680|half1|
|4|1024|131072|half0|

B缓冲0起点196608，B缓冲1起点393216，各65536B；所有A/B真实字节不重叠，最高458752B，和原327680+2x65536总L1 payload相同。每个K包的A、B当前reader同半区，另一B包的MTE2写放到另一半区。保留完整A跨相邻Ntiles复用，无新GM、无输入修改、无跨batch、原L0双缓冲/fullK/MMAD/GM C ring/Vector/输出/credits不动。

**A只需两条multi-ND ND2NZ描述符，不需要五次DataCopy调用**：

- even: ndNum3，GM起点K0，srcNdMatrixStride512，srcDValue1280，nValue128/dValue256，dstNzC0Stride128/NStride1/MatrixStride32768，L1base0。
- odd: ndNum2，GM起点K256，同src/dst stride，L1base262144。

srcNdMatrixStride和dstNzMatrixStride单位都是元素，实际CANN9公开`include/basic_api/kernel_operator_data_copy_intf.h`已核对；dav_c220实现把这些字段直接传给copy_gm_to_cbuf_multi_nd2nz_b16。当前kernel自身在C12 Aslab已有multi-ND调用，不编造新API。原每A刷新1条DMA→新2条；总A刷新32→64条调用、实际ND矩阵160份，A GM字节10485760不变。B960包/GM62914560B不变。多一次descriptor开销可能抵消半区供数收益，必须native决定。

A到L0：选择j=k0/256的A slab，以channelSize256、localK=k0%256调用原NT ManualTransposeFullM；不是raw-im2col新解释，仍是原ND2NZ数据，每包原两个BK128读取。B从原NT ND2NZ包用原Load2D读两个BK128。源级地址证明不等于真实Load3D解释已验证。

## 关键协议：不能沿用全局packageSequence奇偶

K1280/PK256=5为奇数。旧全局FIFO序号在下一个N tile翻转；新A包j的物理区域始终j%2，直接套旧ps会把A/B分到不同半区。不能只改B地址或填offset救性能。

需独立的两个aheadTask[c]/aheadK[c]游标：初始K=c*256，每次同路+512，超过K时tile++并重置K=c*256。bank0消费j0,2,4，bank1消费j1,3，均各自预取下一同路包。每包必须等两个BK128 MTE1 reader完成后归还free，再向同一个物理B槽写下一同路包。bank1可提前装下一Ntile的j1，bank0在旧j4读完才装下一tile的j0。不能因按两条路执行MTE2就打乱**消费**的原K顺序。

A换M之前必须等旧A最后MTE1 reader，所有两条A DMA完成后新A才可读；A区不与两个B区重叠。保留M_MTE1、MTE1_M、M_FIX、FIX_M和GM C credits原协议。独立prefix FIFO模型尚未写，不能提前声称同步安全。

## 当前可复现模型证据

`python3 tools/audit_c9_banked_l1.py`（默认使用tests/cpu/c9_captured_plan.json，实际完整plan结果摘要，不是新SDK tiler执行）通过：163840个A标签/两multi-ND描述符真实stride单位/全部A-B不重叠/每个末尾L1界限、20worker共960B包、全部192tile及原9/10分工、完整两路包序列和所有K消费一致；错误同路reset和multi-ND源stride反例检出，全局parity错位直接证明。原source2073 hash受约束。私有JSON artifacts/c9-banked-l1-audit/address-packet-audit.json。

**仅地址及包顺序算术模型**。未执行新生产代码、实际SDK数据格式、并发引擎、FP16舍入或NPU速度。不要把此模型写成完整K native验证。

## 下一条可执行动作

1. 从2073新实现一个默认false BANKED_C9 分支。可在RunManualFullMCube前调用独立helper，保留原false整个body；bmmms_manual只透传该模板到Cube，Vector body逐字不动。精确C9 FP16NT/原dual36/BM128BN128/PK256/完整K/实际core与L1/L0/UB/原GM容量和tuning回退guard。不能写新GM或改变MakePlan。
2. 用显式LocalTensor A1/B1固定地址（原DIRECT_BATCH已用公共API）及原L0/CO1 TBuf/event池，确保未再同时分配旧aq/stagedB导致L1重叠。两条A多ND及每bank B游标按上文。独立完整producer模型执行实际源、延迟MTE2/MTE1/MMAD/Fix/当前M转换和5包跨N边界，增加覆盖旧A最后reader/包最后reader/输入ready/完整K/独立cursor反例。新增wholeparent inverse/host容量临界/pin回退。
3. 新SSH先查实际queue/ps/SoC，冻结source→实际CANN9编译→原c9.json/c9.complete_frame/inputs/c9一次fullFP64/input-yguard→一次default完整五报告。ActualBANKEDtrue/20Cube40AIV、原每核90/100MMAD不变必须确认。
4. 预定gate仍median<=49.6279836（正确parent55.142204降低>=10%）且全五<54.922195。同source不重复采样，不扫半区offset/包大小/PK/BK/flags；失败归档恢复2073，不OJ。大收益才全负/变化输入/其余gate/正式15。

当前无新native candidate或OJ。整体冲榜目标active，未完成。
