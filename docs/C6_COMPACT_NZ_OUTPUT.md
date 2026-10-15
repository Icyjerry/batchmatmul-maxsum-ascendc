# C6 紧凑 NZ 输出：完整 K 后改变 Cube/Vector 交接布局

## 假设和固定门槛

Parent a11e2d9 / kernel2073f48e/353255B，正式任务820092 Pass15/allprecision1，C6=9.45us。此前本机原ZIP078635的 C6 body 与 parent逐字相同（parent只在C15加两行就绪依赖），使用其已完整保存的五报告，不重复采 baseline：BF16NT/13,23,73,192，9382/24AIC48AIV/dev0physical14/CANN9/caller20，actual dual19/BM32BN80/K192/workers13/MIX11。DSO0357587a，一次及五fullFP64输出通过，中位8.860354us，times[8.260330,9.000360,8.780352,8.860354,9.240370]，default全部8表×5。

此已采C6五报告PMU核心均值五次中位：AIC MTE2=2.779701us、MAC=.090556、Fix=3.868675、scalar4.642222；AIV Vec=.239444、flag0wait4.389872。计数重叠，不相加、不将Fix时间全当转换或带宽。

A2/A3 dav2201不能L0C直接写UB，实际public Fixpipe local重载只支持L1；不再尝试该不支持路径。新假设是保留原输入、完整K192 MMAD和GM arena，以紧凑NZ格式写有效M23行，AIV沿NZ doc16组归约，跳过ND输出转换及9行padding写回。源级输出10240→7360B（-28.125%），AIV原来就只读7360B，读取字节不减少；新Max多阶段可能抵消收益。

采候选前固定：完整五报告中位至少降低20%，**<=7.0882832us**。失败归档恢复2073，不扫相邻format/stride/tile、不重复收集或OJ；过gate再补全负/输入变化/回退，之后考虑正式15提交。沿用现有输入和先前完整baseline，不筛报告或混入别源成绩。

## 源码和SDK

候选SHA360db6f00491f00cf10626e867fcacd7ff741f8b5ab04c50a5115c3ae130604b，kernel变更36增6删。只改SingleTileDirectBatchCompute默认false COMPACT_NZ及mix11模板透传、host guard和原较早C6调用；不是已失败raw Load3D/纯Vector/静态K的重复。原GM→L1→L0输入、MMAD维度/K顺序/UnitFlag3、Fix完成通知、MIX11网格及唯一y store不变。

true选择column-major L0C，Fixpipe<float,float,CFG_NZ>，nSize80/mSize23/srcStride32/dstStride46（NZ dstStride单位32B，所以23*16FP32/32B=46）。输出每doc16组紧凑23×16，5组共1840FP32落在原2560FP32 slot内。AIV仍拷1840FP32，先合并四个完整doc16组，再以mask9合入最后组，然后每query WholeReduceMax16、原Sum23，Npadding绝不参与全负max。

实际CANN9 dav_c220 Fixpipe header显示CFG_NZ和上述32B stride、NZ mSize非16倍合法；这不代替native布局证据。资源guard仅原完整BF16NT B13M23N73K192/dual19/32x80/13workers等计划，再调用原MakeSmallFullKBatch检查实际AIC/AIV、L1/L0/UB/原workspace。显式TUNING全部回退，默认false函数反向恢复parent，保护7不变。

## 验证与状态

CPU实际Fix descriptor和NZ reduction提取执行78个完整M23N73K192 batch pairs（3seed/mixed/allnegative/13batch），input点积为整数代理，invalidN设巨大正毒值；descriptor范围/紧凑GM与UBguard/Max原N→Sum原M通过，五故障反例拒绝。最初“漏最后有效doc”反例未触发，因为重复输入最大值有并列；补充使最后有效doc唯一最大的数据后全部通过。没有改kernel掩盖失败。

真实host guard抽取production/TUNING拒绝36/47个shape/layout/type/plan/core/capacity/workspace/pin反例及实际容量临界值。模型不是SDK tiler/硬件同步证明。

CANN9/dav2201独立SHARED编译PASS，8条原host GM_ADDR attribute warnings。冻结imports/c6-compact-nz-360db6f00491，build-c6-compact-nz/libnative_bmmms.so；source/DSO/wrapper绑定。一次full-storage native correctness正在运行，默认五报告性能/正式15仍PENDING。
