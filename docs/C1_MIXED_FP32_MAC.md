# C1：half 双输入直接乘加到 FP32

## 本次新依据

从正式Pass15保留2073f48e/a11e2d9派生；C9 LEFT FMatrix已完成native，仅0.8705%，恢复原版，不混入本候选。新方向来自实际CANN9 SDK，而不是重做scalar-cache或旧float/float MLA。

实际读取`aarch64-linux/asc/include/basic_api/kernel_operator_vec_binary_intf.h`的MulAddDst<T,U>及`impl/basic_api/dav_c220/kernel_operator_vec_binary_impl.h`：MulAddDstIntrinsicsImpl明确允许Tuple<float,half>，发出vmla；Level2混合类型的dst/src repeat stride为8/4/4。BF16不在该tuple中，保持原路径。

假设：C1先把FP32 product清零，与两输入64B DMA重叠；MTE2完成后直接混合MulAddDst，再WholeReduceSum32，去掉原依赖链中的half→FP32 Cast阶段。虽然少一个转换阶段，但增加零初始化，native可能无收益，不能按API数预言速度。

## 源码、范围与算法

source **43dbf4f3a4d0f35ec6536123f5d4f14a214d4de4ff666fd1072ab2126f917e86 /355211B**。仅新bmmms_dot_short_mixed32入口、UseMixedDot32 guard及原dual15内提前调用；整份逆变换恢复2073，保护7等1734f16。MakePlan、workspace/cache/GM、其它kernel均不变，不加GM。

只接受FP16/B1M1N1K32、原dual15/1final/0Cube/0workspace/无small或micro，真实UB>=288+1024/AIV>=1、GM32B对齐。全部TUNING pin、BF16、批次/shape/对齐或资源不符回原实现。M=N=1时四种storage属性均按相同32元素顺序存储，不额外转置。

UB rawA0..63/rawB64..127/product128..255/sum256..287，均32B对齐，无别名。DataCopy输入与Duplicate0/PIPE_V分离，MTE2_V保证VMLA只读已完成输入，VMLA后PIPE_V才ReduceSum，V_MTE3和terminalPIPE_ALL保留。完整32K乘加至FP32，无需Max/Sum交换：此shape的N/M归约各只有一个元素。唯一输出4B。

关键精度风险：SDK支持混合tuple并不单独证明内部乘积没有先在FP16舍入/溢出/下溢，必须native验证；不能依赖普通归一化数据的小误差掩盖错误。

## CPU与资源检查

`validate_c1_mixed32.py`提取实际入口，2115个完整编码K32向量，包括全部63488有限FP16编码（逐32组成/与1相乘）、128随机符号向量及max-half product、normal-half tiny product、全负精确控制。软件解码→FP32 FMA→FP32 sum对FP64存储golden通过，独立deferred DMA/Vector/output、UB/yguard与输入不变通过。5个missingInputReady/missingZero/wrongK/missingOutputReady/missingTerminal反例拒绝，整source inverse/保护7一致。软件FMA语义是待native证的假设，不冒充硬件结果或完整Vector子流水。

actual guard production25/TUNING36拒绝，4种storage属性、dtype/shape/对齐/plan/UB/AIV/pins临界通过。不是SDK tiler或native命中证明。

## native 准备与采前门槛

使用原c1.json/c1.complete_frame/inputs/c1，不修改旧输入或golden；family前缀bmmms_dot_short覆盖新入口，但必须检查actual完整symbol有mixed32。正确parent2073/DSOca36五报告已冻结：[1.960078,2.000080,1.560062,1.560062,1.600064]us，中位1.600064，全部样本保留；同SoC9382/24AIC48AIV/dev0physical14/CANN9/caller20，pureVector1。实际input SHA b10537f9…/1cff1460…，golden dd c1 c29c…，实际输出.2724899649620056/abs2.9802322e-8。引用旧完整报告，不重采parent。

**采前准入**：median<=1.4400576us（至少10%），全部五候选<父最快1.560062us，全部5full输出/input/yguard通过，且native大/小乘积和全负精确检查通过，才考虑正式15。BF16/其它shape仍回原路径。未达则归档恢复2073，不扫UB/stride/零初始化位置/K变体、不重采/OJ。

`prepare_c1_mixed_checks.py`建立独立本地stress输入：maxproduct仅首元素65504×65504、smallproduct32个(2^-14)^2、全负32个1×(-1)，均实际storage完整FP64 matmul→MaxN→SumM→FP32。它们是已知有限输入的精度测试，不是隐藏case探针、不参与性能采样。新同地址序列mixed→maxproduct→smallproduct→negative→mixed使用同context/stream/输入地址，旧normal文件未动。

**必须**额外比对stress三次actual保存的FP32 bits与golden bits完全相同：smallproduct结果很小，普通absolute tolerance会错误容许0，故这里明确要求精确非零；maxproduct检查FP32范围而非FP16Inf。该要求不修改正式验证器/容差。

当前CANN9/dav2201编译exec82517，冻结imports/c1-mixed32-43dbf4f3a4d0/kernel.asc，build-c1-mixed32/log c1-mixed32-build.log；stress准备已完成，编译/native/性能/正式15 PENDING，无新OJ。成功后写绑定source/DSO/wrapper994e29f identity，先原job.py correctness+上述5call sequence，保存并精确查stress bits，再一次default8表×5。原baseline完整summary在artifacts/c1-scalar-cache-dot/c1-scalar-evidence.tgz内results/c1-baseline-profile/summary.json。
