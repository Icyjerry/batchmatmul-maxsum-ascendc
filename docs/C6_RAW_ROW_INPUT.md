# C6 raw row 输入候选：生产源码已建，设备验证待恢复

## 假设

基于队友 ZIP078635 / e2f1b63。C6确认BF16 NT，记录完整frame `(13,23,73,192)`，实际源码较早dual19→static32/80/192 MIX11已含UnitFlag3。

当前两个输入先ND2NZ到L1，再Load2D进入L0。尝试将GM中的连续行直接复制到原L1分配，用宽12、步长12、channel16的im2col窗口把完整K192行装成原A2 ZZ/B2 ZN。只改变输入供应；原full-K MMAD、normal C、UnitFlag3、Fixpipe、ring、AIV Max(N)/Sum(M)、输出grid原样。

这是不同于旧“NZ后1×1矩形Load3D”的输入表示改变。C13 raw-normal曾退化，本候选不修改C13或借其结果预测C6。

## 源码与准入

- 分支 `experiment/c6-raw-row-input`，实现 `140080d`；候选356750B，SHA256 `639fa38edd6adba6d4ed4869f8042d329001fbe4a7a94b6ecd7dd42bf0cf465e`。
- 算法仅修改kernel.asc，65增/5删；`RAW_ROWS`默认false，仅已有MP32/NP80/KP192 early入口通过`UseSmallC6RawRows`时开启。
- 精确公开shape/BF16/NT、原Schedule/worker/Cube grid、输入32B对齐、actual平台core和UB/L1/L0、原system workspace/partial/ring容量全部检查；显式TUNING关闭该入口。资源或plan不符回退原函数。这里不声称已采到C6实际normalPlan。
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

所有调用及参数字段都已在这份CANN9编译过的源码中出现：InitConstValueParams/InitConstValue、普通GM→L1 DataCopy、LoadData3DParamsV2、filter/stride/dilation/extension、fMatrixCtrl与LoadData。模型不新增padList或SDK内部缓存操作。LEFT/RIGHT使用公共参数，自动reset规则沿用公共LoadData默认行为。

**新filterW12/strideW12/channel16组合、实际目的ZZ/ZN与后台限值尚未核对设备header或编译结果**。因此它是隔离的未上板候选，不是已确认可运行API组合。连接恢复后先查实际CANN9 header并编译；若限值不支持，停止该方案并归档，不改SDK或假装可用。

## 事件与CPU证据

输入实际代码先issue A清零/copy/ready0，再issue B清零/copy/ready1。等ready0才load A；B仍可在MTE2途中。等ready1才load B。后续原MTE1_M保护MMAD，原UnitFlag3保护Fix，原FIX0保护Vector，终末原PIPE_ALL保留。每core只处理一个batch，无L1/L0跨task复用新增风险。

`tools/validate_c6_raw_row_input.py`抽取实际两helper与实际producer raw分支，延迟MTE2/ready前缀模型执行78batch pairs（3seed×mixed/全负×13），逐元素验证padded L1、native标签ZZ/ZN、完整M23N73K192点积及Max→Sum、输入不变与bounds。7个反例：缺tail fill、错stride、错RIGHT、错GMoffset、漏A ready、漏B ready、错batchstride，全部被拒绝。

整份逆补丁恢复e2f1b63；证明原数学/归约/GM/默认输入路径/其它kernel未改。CPU坐标与整数点积不是BF16舍入、真实Load3D或硬件流水证据。

`tools/validate_c6_raw_guard.py`抽取真实guard，production/TUNING各接受一个精确**人工构造**frame、拒绝46/57个反例，并检查内存容量的临界值。它不执行SDK MakePlan，不证明实际C6会命中；真实MakePlan复核仍是设备门槛。

原独立几何工具已改成显式L1 zero-tail构造并通过；不再依赖外部padList假设。Raw日志在忽略目录artifacts/c6-input-layout-audit，权限700/600。

## 下一条可执行设备验证

服务器入口当前转发被平台拒绝；前轮创建的设备任务均已终态，未创建新任务。已请求新入口，整个服务器的活动状态需重连后检查。

1. 验证SoC/CANN/物理映射/真实核数及队列，再补下载C4候选原始报告（旧结果路径见HANDOFF）。不重新跑同候选。
2. 冻结parent e2f1b63与当前candidate各一份source；普通baseline DSO已在`native_oj_like/build-baseline`，核对实际SHA再使用。
3. 先用`tools/native_oj_like/c6.json`+baseline DSO执行job.py的plan模式，检查实际完整Schedule/cube/finalBlocks、source预计13Cube13AIV；写reviewed c6.complete_frame.json。不得强制分派。
4. 生成全实际storage FP64golden，baseline一次完整精度+五默认报告。期间读取实际CANN9 Load3D/InitConstValue header，核对filter/stride等限值和操作数目的布局。
5. 独立SHARED工具构建candidate DSO、绑定真实source/DSO/wrapper SHA与normalPlan；如果API/编译失败保存完整日志，不运行性能。
6. 相同输入/device/normalPlan，candidate一次完整精度+五默认报告，实际符号必须含RAW true；保持0应用warmup/5calls、msprof op warm-up5/launch-count5000/replay-mode kernel/default全八表。所有输出/guards/input/报告完整性通过才比较五次TaskDuration median。
7. 采候选前固定：**至少20%中位改善**才补全负/重复/正式15点验证并准备OJ提交；否则归档恢复ZIP，不扫描filter/stride或原样重复。未达到门槛不称突破。

CPU模型PASS；实际normalPlan、CANN编译、设备BF16精度/时间/完整五报告、正式15点均 **PENDING**。没有新OJ任务、没有并main、没有移动历史标签。整体冲榜目标未达成。
