# C4：在64 lane状态中完成K128点积

## 基础与证据

父源码为 e2f1b63、ZIP078635、353179B；不是DISPATCH的b881接受源。基于用户确认的BF16 TT与记录的完整shape `(4,8,16,128)`，本机正常Launch首先命中SmallVectorK256Rows=8，早于dual28入口。没有强制route或探针。

设备9382/24AIC48AIV/dev0physical14/card7chip0/CANN9/driver26.1.1，caller budget20。原DSO `0357587a9f1f73d128bb90cf381d0400731060e6628800f96cde02a7750a907f`。完整normalPlan dual28/finalBlocks4/workers4/cubeBlocks0，不能据cube tiling的usedCoreNum4声称实际运行了Cube。实际捕获的是 `bmmms_small_vector_k256<BF16,true,true>`，纯Vector4，PMU无Cube。

全FP64实际storage golden：`[1.2438478469848633,1.3482189178466797,1.1094154119491577,1.1033282279968262]`。一次完整精度及五次性能输出通过，输入/y guards完整；具体误差在原始identity.json，不能把“通过”写成误差必定为0。

五次默认全报告TaskDuration(us)：`[2.980119,2.940118,3.120125,3.060122,3.360134]`，中位 **3.060122us**。各核均值的五次中位AIV V1.46/MTE20.419028/MTE30.149167/Scalar0.721806/ScalarVectorStall0.307917us；这些计数重叠，不相加。与队友或OJ不同硬件，不能直接当正式延迟。

首次只读parser把纯Vector的MixBlockDim=`NA`误当整数，任务退出1。实际五调用/输出/全部报告已完整生成；修正纯Vector schema后对同一组全部五报告重解析通过，原exit1及NA表保留，未重跑/丢样本/改算法或输入。独立工具只支持复核过的capture规格，其它混合路径仍按normalPlan检查。

## 新的假设

原实现每个点保存128 FP32乘积（64KiB），再把上下两个64-lane块相加；每个K128点积完成后才求N max。候选先Mul低64，再用公开MulAddDst把高64乘积加入同一64-lane状态，只需32KiB产品状态；随后原WholeReduceSum64、有效N WholeReduceMax和M Sum。

候选SHA `c6bde889f5a07fdc01423f1ce88ac244b7e7e80f4059fb4f0d61e0f2423ccce9`；只在原SmallVector资源guard通过、rows8、BF16TT公开 `(4,8,16,128)`入口启用，所有其它入口默认false。MakePlan/workspace/inputCast/Gather/输出grid未动；未增加GM通路，不用padding替代负max。

实际CANN9公开API和实现：

- `.../asc/include/interface/kernel_operator_vec_binary_intf.h` 的 MulAddDst 是 `dst += src0*src1`，接收mask/repeat/BinaryRepeatParams。
- `.../asc/impl/basic_api/dav_c220/kernel_operator_vec_binary_impl.h` 允许float/float，并发出vmla。
- FusedMulAdd 的语义是 `dst=src0*dst+src1`，不同，未使用；不凭名字推测API，也不假定vmla特定舍入方式。

新repeat描述符 `{1,1,1,8,0,16}`：每N点目标64lane，query输入在N repeats间广播，document仍以K128跨点。Mul完所有有效M行后PIPE_V，再累加高K64并PIPE_V，然后完整K归约。输入与归约依赖保持。

## CPU验证和设备门槛

工具 `tools/validate_c4_compact_k128.py` 抽取实际新旧函数，用仓库现有延迟DMA/有界UB模型：12种数据seed×正负2组×chunk1/3/8，共72完整fixture/216新旧/default执行组，4个batch独立配对、完整点积/max/sum/唯一outputwriter/guards/输入不变通过。错误高K半块的反例被拒绝；整份逆补丁恢复原版，七文件一致。整数值FP32不是BF16编码或真实硬件事件模型。

在候选采样之前固定：同输入/设备/normalPlan完整正确性与五次默认报告，至少20%中位改善（≤2.4480976us）才推进正式提交与扩展精度。低于门槛则归档，不扫描近邻chunk，不把UB或API数下降宣称为加速。

CANN候选编译、原生精度/性能 PENDING。正式15点和其它设备 PENDING；无新OJ任务。Raw忽略目录 artifacts/c4-compact-k128；server native_oj_like/results/c4-*。
