# C6 raw row 输入候选终态：编译通过，native 精度失败，已撤回

## 假设

基于队友 ZIP078635 / e2f1b63。C6确认BF16 NT，记录完整frame `(13,23,73,192)`，实际源码较早dual19→static32/80/192 MIX11已含UnitFlag3。

当前两个输入先ND2NZ到L1，再Load2D进入L0。尝试将GM中的连续行直接复制到原L1分配，用宽12、步长12、channel16的im2col窗口把完整K192行装成原A2 ZZ/B2 ZN。只改变输入供应；原full-K MMAD、normal C、UnitFlag3、Fixpipe、ring、AIV Max(N)/Sum(M)、输出grid原样。

这是不同于旧“NZ后1×1矩形Load3D”的输入表示改变。C13 raw-normal曾退化，本候选不修改C13或借其结果预测C6。

## 源码与准入

- 分支 `experiment/c6-raw-row-input`，初始实现 `140080d` / 639fa38 / 356750B 未编译；核对真实 SDK 后修正 RIGHT FMatrix，当前357100B，SHA256 `fa315ae8072a5a128b4e57a6e9528064b9d63d2c0c1a0ad7f27a433248cce71e`。旧冻结源码保留，不与新结果混用。
- 算法仅修改kernel.asc，初始65增/5删，RIGHT修正另增5行；`RAW_ROWS`默认false，仅已有MP32/NP80/KP192 early入口通过`UseSmallC6RawRows`时开启。
- 精确公开shape/BF16/NT、原Schedule/worker/Cube grid、输入32B对齐、actual平台core和UB/L1/L0、原system workspace/partial/ring容量全部检查；显式TUNING关闭该入口。资源或plan不符回退原函数。已实查本机正常 MakePlan 命中原13 Cube/13 Vector计划，完整frame见下。
- 静态约束限定DIRECT_BATCH/SINGLE_AIV/NT/32×80×192/2字节；其它实例输入分支逐字保留。七个受保护文件与1734f16一致。
- 现有GM分区、分配、输入只读和输出B个FP32没有改变。没有新GM通路或CPU替代输出。

## 从 padding 假设改成显式 L1 补零

初始审查把缺失9/7行映射成右padding108/84像素，需要核对未知padding字段。本候选不使用该字段：先清零原L1中完整尾行，再复制有效输入；声明feature width为padRows×12。

A：实际23×192×2=**8832B**，补零9×192×2=3456B，L1总12288B。

B：实际73×192×2=28032B，补零7×192×2=2688B，L1总30720B。

（上面A值按23×192×2计算，避免把元素数4416当字节数。）

任意有效或补零行r、K坐标k：`feature=r*12+k//16`，`channel=k%16`，原始L1下标=`feature*16+channel=r*192+k`。feature width384/960，window12/stride12完整得到32/80行；不读取GM尾部，也不依赖未写L1内容。

L0A12288B/L0B30720B/L0C10240B与原分配相同。**直接copy加清零的L1写入总字节并未减少**；每核MTE2源级操作由两次ND2NZ变成两次tail InitConstValue加两次copy。加载由A两次/B一次Load2D变为两次Load3D。减少格式转换可能被新增初始化或im2col成本抵消，不能按指令数预报速度。

## API依据与尚未验证项

所有调用及参数字段都已在这份CANN9编译过的源码中出现：InitConstValueParams/InitConstValue、普通GM→L1 DataCopy、LoadData3DParamsV2、filter/stride/dilation/extension、fMatrixCtrl与LoadData。模型不新增padList或SDK内部缓存操作。真实 CANN9 `kernel_operator_mm_base_impl.h` / dav_c220 `kernel_operator_mm_impl.h` 表明：默认 LoadData 的 Load3DSetFMatrixCal 只写 LEFT，不随 fMatrixCtrl 自动写 RIGHT。因此旧639fa38的 B 配置不完整；当前 A沿用默认 LEFT，B 显式 SetFmatrix(...FMATRIX_RIGHT) 并使用 `{false,false}` no-reset LoadData，沿用保留 C10 的公开 API 写法。CPU模型新增两个独立 FMatrix register 状态，缺 RIGHT setter 的反例必须失败。

实际 SDK 声明 filter/stride 为 uint8、channel/extension 为 uint16，dav_c220 后台直接传入 img2colv2_cbuf_to_ca/cb；这些只能证实字段和调用存在。filter12/stride12/channel16 的真实布局与限制仍须 CANN 编译和设备精度验证，不能由字段宽度推断支持。实际CANN编译通过，但 native full-FP64 精度失败，不能声称该布局解释可用。

## 事件与CPU证据

输入实际代码先issue A清零/copy/ready0，再issue B清零/copy/ready1。等ready0才load A；B仍可在MTE2途中。等ready1才load B。后续原MTE1_M保护MMAD，原UnitFlag3保护Fix，原FIX0保护Vector，终末原PIPE_ALL保留。每core只处理一个batch，无L1/L0跨task复用新增风险。

`tools/validate_c6_raw_row_input.py`抽取实际两helper与实际producer raw分支，延迟MTE2/ready前缀模型执行78batch pairs（3seed×mixed/全负×13），逐元素验证padded L1、native标签ZZ/ZN、完整M23N73K192点积及Max→Sum、输入不变与bounds。8个反例：缺tail fill、错stride、错RIGHT、错GMoffset、漏A ready、漏B ready、错batchstride、缺 RIGHT FMatrix 设置，全部被拒绝。

整份逆补丁恢复e2f1b63；证明原数学/归约/GM/默认输入路径/其它kernel未改。CPU坐标与整数点积不是BF16舍入、真实Load3D或硬件流水证据。

`tools/validate_c6_raw_guard.py`抽取真实guard，production/TUNING各接受一个精确**人工构造**frame、拒绝46/57个反例，并检查内存容量的临界值。它不执行SDK MakePlan；本轮另行读取设备实际 MakePlan，不能把 CPU guard 正例当设备证据。

原独立几何工具已改成显式L1 zero-tail构造并通过；不再依赖外部padList假设。Raw日志在忽略目录artifacts/c6-input-layout-audit，权限700/600。

## 下一条可执行设备验证

2026-10-15 用户新入口已连通；先复核队列空闲，9382实际24AIC48AIV/CANN9.0.0/logical0→physical14/card7chip0。C4旧候选 raw 两包已补回，不重测 C4。SSH需前台 ControlPersist=no master；凭据仅在私有临时配置。

1. 验证SoC/CANN/物理映射/真实核数及队列，再补下载C4候选原始报告（旧结果路径见HANDOFF）。不重新跑同候选。
2. 冻结parent e2f1b63与当前candidate各一份source；普通baseline DSO已在`native_oj_like/build-baseline`，核对实际SHA再使用。
3. 先用`tools/native_oj_like/c6.json`+baseline DSO执行job.py的plan模式，检查实际完整Schedule/cube/finalBlocks、source预计13Cube13AIV；写reviewed c6.complete_frame.json。不得强制分派。
4. 生成全实际storage FP64golden，baseline一次完整精度+五默认报告。期间读取实际CANN9 Load3D/InitConstValue header，核对filter/stride等限值和操作数目的布局。
5. 独立SHARED工具构建candidate DSO、绑定真实source/DSO/wrapper SHA与normalPlan；如果API/编译失败保存完整日志，不运行性能。
6. 相同输入/device/normalPlan，candidate一次完整精度+五默认报告，实际符号必须含RAW true；保持0应用warmup/5calls、msprof op warm-up5/launch-count5000/replay-mode kernel/default全八表。所有输出/guards/input/报告完整性通过才比较五次TaskDuration median。
7. 采候选前固定：**至少20%中位改善**才补全负/重复/正式15点验证并准备OJ提交；否则归档恢复ZIP，不扫描filter/stride或原样重复。未达到门槛不称突破。

CPU模型PASS；parent 实际normalPlan/完整BF16精度/五默认完整报告PASS；candidate CANN编译PASS，设备BF16精度 **FAIL**，五报告/正式15点 **NOT RUN**。没有新OJ任务、没有并main、没有移动历史标签。整体冲榜目标未达成。

## 2026-10-15 parent 实际设备结果

ZIP078635 source / DSO0357587a。BF16 NT `(13,23,73,192)`，caller core_limit20；actual hardware24/48。
完整实际normalPlan：cubeBlocks13/finalBlocks2/systemBytes16777216/totalBytes17045504；Schedule baseM32/baseN80/mTiles1/nTiles1/nSplit1/workers13/window1/kSplit1/kChunk192/microRows23/batchGroup0/dual19/earlySum0/tree0/balance1/vectorTile1024。Cube usedCoreNum13/baseM32/baseN80/baseK192/stepM=N=Ka=Kb=1/depthA1=B1=1/dbL0A=B=2/dbL0C1/shareL1Size43008。

一次完整精度与五性能调用通过，maxabs2.384185791015625e-7，maxrel6.522730018203635e-8，输入不变/y后16word guard完整。Full-storage FP64 reference，不采样；seed1746实际BF16。
五 TaskDuration `[8.260330,9.000360,8.780352,8.860354,9.240370]` μs，中位 **8.860354μs**。实际符号 baseline single_tile_direct_batch_mix11 BF16/NT/32/80/192/DIRECT true，13AIC13AIV，每核一次Cube instruction；默认全部8表×5报告。20%候选门槛 **<=7.0882832μs**，不重测/筛样本。

私有原始完整包、summary在 `artifacts/c6-input-layout-audit/c6-baseline-{plan,correctness,profile}.tgz` 和 remote `native_oj_like/results/c6-baseline-*`，source/DSO/input/SoC/完整frame绑定。不是正式15/OJ结果。

## Native 候选终态：精度失败，无性能数据

候选 source `fa315ae8072a5a128b4e57a6e9528064b9d63d2c0c1a0ad7f27a433248cce71e` /357100B，commit **0689e2d**；实际 DSO **e0e6aa7f11d8f30d6a193d5009234215bb0404735be768a34ad741189e595723**，wrapper994e29f/CANN9/dav-2201。独立编译exit0，8条host GM_ADDR attribute warnings，无编译错误。

同一输入/同一reviewed完整normalPlan运行correctness，synchronize返回后full FP64参考比较失败，exit1。NumPy日志展示actual `[3.6244779,3.7302272,3.621674,3.6902914,3.8839386,3.575931,3.9058902,3.801205,3.6137536,4.1241126,3.7799401,4.0446800,3.9897780]`；这些是**显示舍入值，不是完整原始FP32位**。最大绝对/相对误差日志约 **0.47670078 / 0.12828762**。原版相同输入最大误差2.38e-7，不把此失败解释成精度容差或环境抖动。

输入模型中假设的 Load3D 目的布局/行展开没有得到硬件支持。错误的具体排列尚未证明，不能仅凭输出差异归因为 RIGHT、enTranspose 或某个block维度。离线两个outer-block排列假设也未复现actual，未据此改参数或重测。**不采性能、不提交OJ、不扫描filter/stride、不换名重做此 raw 表示。** 当前kernel恢复整份e2f1b63/ZIP078635；候选完整实现留在0689e2d，CPU模型通过不能覆盖这条native反证。

完整baseline原始包已下载。候选编译日志/失败correctness原始目录仍在remote `native_oj_like/build-c6-raw.log`、`results/c6-raw-correctness`，本地补下载时SSH超时断开，重连跳板认证成功但目标转发platform authorization denied。候选raw下载 **PENDING**；本地 `candidate-terminal-observation.json`明确记录工具返回的失败信息及其显示精度限制，不伪装成已下载raw。已请求新入口，无活动profile/OJ任务。

独立native driver随后增加在校验前保存实际输出及guard原始bits、数值失败JSON；这只加强未来失败诊断，阈值/正式测试不变，也不能追补已结束调用丢失的FP32原始bits。该工具补丁不改变此前编译或失败结论。
