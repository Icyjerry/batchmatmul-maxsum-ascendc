# TT document 原生行布局 / 交换 Cube 操作数

## 证据与假设

分支 `experiment/tt-native-document`，父算法1734f16/current repeat62ad1cd。用户已确认优先计分差距 C3/C11/C1/C4/C9，并允许激进尝试及利用历史探针。C11历史条件为FP16/TT/M1024..2047/N2048..4095/K2048..4088，它不是已确认正式shape。TT父手动frame只覆盖BF16较小K，C11范围代理原计划仍为Matmul dual1。

此前 N pair、worker Max、NZ ring、直接取消packed-B、raw-bit tiny/广播K树已正式否定。本方案没有重做这些：交换矩阵乘操作数，计算 `C^T[N,M]=document[N,K] * query[K,M]`，改变 document L1 排列及匹配AIV归约。性能仍需native，不以调用数预测加速。

## 实现与范围

- kernel 369170 bytes；SHA256 `bb8fb8407486cb388cf9678f9fac359dfab693a4b30d9eb8f80e8040c615d160`。
- 新TTDocumentShape仅32B；一套完整Cube/AIV物理frame，259行新增，原所有kernel/host plan/输入/output/workspace逐字保留。工具删除新entry/guard/launch三处后恢复整个1734f16。
- doc每行作为独立1×count ND矩阵：ndNum=validN，srcNdMatrixStride=K，dstNzMatrixStride=packageK，dstNzC0Stride=1；写L1原生[N,packageK]，D尾DMA补零，N尾显式补零。仍调用ND2NZ，不把它称为零格式转换成本。
- Cube document进入A2、query进入B2。NC1HWC0 feature：document H=paddedN/W=packageK/16/C=16/filterW=packageK/16；query H=1/W=paddedK/C=paddedM/filter1。两者enTranspose=false，完整K FP32 MMAD后C0/NZ→ND写原GM ring[N,M]。
- AIV两个消费者各取半M列，DataCopyPad每N行读实际query列，补-inf到halfM；补N尾-inf，再沿N树形Max，跨Ntiles在线Max，写原nSplit×paddedM partial。单全AIV barrier后只Sum有效M，输出唯一FP32[B]。
- 使用原dual1/29/33 TT计划的BN、nSplit、workers和原GM总分配；资源紧时BM128→64，内部group连续分配，K packages按实际L1余量整BK分配，非扫描参数。父host Plan不变；内部BM/tasks/L1布局/C stride改变。资源不足/非TT/显式pins走原路径。
- 每槽MTE2/MTE1/MMAD/FIX及GM credits保留，查询真实L0A/B/C、L1、UB、AIC/AIV容量；无新增GM通路、元数据或输入修改。

## API依据（CANN9官方）

- [ND2NZ](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00127.html)：nValue允许1、dstNzC0Stride允许1，ndNum<=4095；src/dst矩阵间距单位elements；A2/A3支持GM→A1/B1、FP16/BF16。
- [Load3D](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00170.html)：A1→A2 ZZ/NZ、B1→B2 ZN，NC1HWC0/im2col映射；enTranspose不能用于B2，因此本方案均false。filterW<=255，guard检查packageK/16。
- [DataCopyPad](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0265.html)：A2/A3不支持GM→L1的Pad通路，因此使用上述矩阵身份搬运；AIV rightPadding最多7float（28B）。

设计来自本题原源码物理布局推导，不把GPU论文表现外推到Ascend。没有本机安装CANN9 header，实际编译是独立gate。

## 本地验证

`python3 tools/validate_tt_native_document.py` exit0：

- 596 actual Cube entries，独立NC1HWC0/im2col→ZZ/ZN模型，live延迟MTE2/MTE1/MMAD/Fixpipe读取；每个有效和padded C与dense oracle一致，K40/136/1032/1544/2040/3072、BM64/128、BN128/256、shards1/全部/非整除、worker1/3/8/20及idle、全负、GM/input guards、所有events/credits收支通过。
- 1098 actual AIV entries，synthetic transposed Cube与destructive GM release、真实线程barrier、三种DMA/Vector/store队列优先序；N65/80/112/257/592/1537/3073、M尾、query零有效行、odd shard、在线N Max、exact M sum和唯一partial/y writer通过。
- 六Cube/六AIV负控制（last reader、C0、docstride/Npad、Cready/rowlastreader、barrier、Ntree、Mtail）全部被拒绝。
- fake host production/TUNING各5000配置，各932命中/472 FP16；所有原计划字段和总GM未改，低容量/worker/pins回退。代理(1,1537,3073,3080) FP16/TT旧dual1/BM128/NS5，内部BM64/BN128/PK128/NS5/20cores。不是正式路径证据。
- 两处测试夹具错误已修复：Vector声明替换遗漏；零有效query行只保留初始化的-inf，generation应按group初始代数检查，不能要求tile Max的代数。最终用实际有效列/初始代数分别检查last reader，没有降低越界/唯一writer要求。

模型使用小整数→float，不模拟native FP16/BF16舍入；Cube和AIV cross-core各自使用synthetic peer，不是完整设备流水模拟。CANN编译、native精度、latency **PENDING**。正式15Pass也不能证明全shape空间。

## 正式验证计划

独立原模板 `/private/tmp/bmmms-tt-native-document-official/project`，其它7个源码与1734f16逐字一致；仅换kernel。commit/push/dry-run后提交一次，取得ID立即保存，只查同ID至终态。对照当前三次C8 46.52/46.51/46.48、C11 88.03/87.73/88.30。无实际shape/plan/SoC/profile，native接口无法确认候选命中。

如果明确大收益再原样确认；否则保留结果并恢复父，不扫同结构附近参数。原始日志忽略artifacts/tt-native-document、目录700/文件600。整体冲榜未完成。

## 已创建正式任务

实现83a0bd2已push，dry-run仅kernel/SHA一致。任务 `6abf2077694b590c3c47a088` 已创建，CANN/native终态PENDING。下一只查询此ID至终态，不因等待重交。

## 正式终态：15/15通过，速度未获收益，归档

任务 `6abf2077694b590c3c47a088` **Pass**，CANN编译成功，15/15、precision_ratio全1。实现83a0bd2和SHA保持。耗时（μs）：`[2.0, 2.51, 3.12, 4.16, 5.31, 9.64, 7.92, 59.72, 68.61, 99.81, 89.37, 96.79, 16.44, 10.75, 9.14]`；总耗时485.29μs，按用户参考T算49.88095分。

C8 59.72，相比父三次46.52/46.51/46.48（中位46.51）慢约28.4%，明显不利；C11 89.37，比父三次88.03/87.73/88.30（中位88.03）略高，未见提速。没有实际plan/shape/SoC/profile，不能断言哪条指令导致回退或路径命中；其它未改路径不归因。完整CANN/15点证明此结构可在正式输入编译执行，不证明全shape精度或所有目标路径命中。

本实验归档保留分支、代码、models和负控制；不合入下一通过版，不扫描docfilter/package/BM附近参数。原JSON忽略artifacts/tt-native-document/official.json。没有活动评测任务。下一恢复1734f16算法，核对tiny手动frame入口的编译器调度模式，尊重已存在的独立batch AIV，不重做分组或失败K树。整体冲榜目标未完成。
