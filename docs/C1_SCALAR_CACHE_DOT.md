# C1：由 NPU 标量单元直接读取完整 K32 点积

## 假设与对照

Parent2073f48e/a11e2d9正式Pass15，总398.92us/C1=2.09us。本地fixture B1M1N1K32/FP16，dtype是明确本地假设；M=N=1时四storage flags不改变线性数据。设备9382/24AIC48AIV/CANN9/dev0physical14，caller20。

这不是此前无收益的literal Vector544B/常量ABI实验。本候选去掉该点的输入MTE2 DMA、Vector cast/mul/reduction和相关跨流水握手，改为NPU scalar DCache读取两组16个uint32 packed words，解码真实FP16/BF16、even/odd两条FP32累加链完成全部K32。输入缓存每调用显式失效，UB输出显式清缓存、S_MTE3等待，最后仍原4B DataCopyPad和PIPE_ALL。不是CPU替代输出，不修改输入，不新增GM arena。

Parent DSОca36b327实际C1 normalPlan dual15/batchGroup2/final1/Cube0/totalBytes0，原bmmms_dot_short<half,true,2>。一次完整golden及五性能输出通过：reference0.272489994764328/native0.2724899649620056，abs2.9802322387695312e-8/rel1.0937033638050027e-7，输入/yguard完整。默认8表×5，纯Vector1AIV，times[1.960078,2.000080,1.560062,1.560062,1.600064]us，中位1.600064us，全部保留。

采候选前20%门槛 **<=1.2800512us**，不过则归档恢复2073，不扫unroll/accumulator/UBoffset/相邻K参数，不重复/OJ。通过再补BF16/变化输入/全负及正式15验证；正式计分不拿native单点代替。

## 实现与实际 SDK

初始source9e699fe1的LocalTensor DataCacheCleanAndInvalid public重载编译FAIL：实际CANN9 tikcfw/kernel_operator_cache_intf_impl.h把GetPhyAddr返回uint64_t用const_cast转成UB指针，不合法。没有改SDK/main/CMake。当前source **4c0818544891c4b0da051d4777417871fb179accd3d4023c23614bdd0274dbbe** 改用该实现DcciUBImpl内部同一编译器dcci指令和实际CacheLine/DcciDst枚举。失败源保留冻结，修正源单独目录，不混用身份。

输入 public GlobalTensor<uint32_t>::GetValue在本SDK是直接GM scalar load。初次每输入执行CACHELINE_OUT单cacheline失效；guard仅接受64B对齐两输入、B=M=N1/K32/dual15/final1，SDK自身superkernel AlignPtr亦按64B cacheline对齐。各16word恰好64B不越读。FP16 normal/subnormal/zero显式bit decode，BF16高16位直组FP32；仅有限输入。两条FP32累加链改变加法顺序，需fullFP64实际验证。

NPU UB只用一个32B输出buffer，预留64B cacheline+1024资源余量，显式UB dcci后S_MTE3与4B DMA，只写y[0]。实际AIV/UB资源查询，显式TUNING各pin、其它形状和非64B对齐输入回原路径。MakePlan/ABI/workspace/C2+函数逐字不变；算法仅kernel.asc增加43行。

## CPU证据边界

`validate_c1_scalar_dot.py` 提取实际完整device helper/body，逐位验证全部 **128768** 个有限FP16/BF16模式，Python struct独立提供期望；执行256组实际编码fullK32 mixed/allnegative/subnormal/zero/cancellation输入与FP64golden比较。输入/yguard、cache失效、scalar输出cacheflush/S_MTE3/terminal的六故障反例拒绝；去掉三处新增段恢复parent全文件，保护7逐字1734f16。

缓存/事件是mock，不是NPU coherence/时序证明。`validate_c1_scalar_guard.py` 抽取实际guard，8种dtype/layout接受，production/TUNING22/33个shape/alignment/plan/core/UB边界/pin拒绝；非SDK tiler。

候选修正后CANN编译/nativeFP16/BF16/缓存变化输入/五默认性能：PENDING。当前没有新OJ任务。
