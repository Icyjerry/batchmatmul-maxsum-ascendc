# C15 手写 Split-K：补齐 Cube 写回到 Vector finalizer 的依赖

## 新的实际反证

2026-10-15 用户刷新SSH入口后恢复访问，服务器2ef29bca0f61 / Ascend910_9382 /24AIC48AIV/CANN9/driver26.1.1，logical0→physical14/card7chip0；caller budget20。C6候选原始失败目录、编译log与DSO manifest已补下载，未重跑失败候选。独立driver失败bits诊断与C15 fixture已部署。

ZIP078635 baseline DSO0357587a读取实际 C15 normalPlan：FP16TT `(1,64,64,8192)`，dual25，baseM=N64，kSplit8/kChunk1024/workers8/cubeBlocks8/finalBlocks1，systemBytes16777216/totalBytes16908288；其余小路径flag0。完整frame已审阅冻结。Cube tiler metadata的baseK256与手写函数实际BK128不同；执行手写函数时以后者为准，不混为实测矩阵指令。

新完整实际storage FP16→FP64 matmul→maxN→sumM，golden FP32 **1.6493455171585083**。baseline第一次correctness实际输出原始bits为 **0.0**，maxabs1.6493455171585083/rel1，exit1；不是采样模型、容差问题或性能抖动。输出后guard未变，独立driver在失败前保存actual_with_guard_0.u32和precision_failure.json。

**原版此输入正确性失败，不采其性能，也不能把它作为有效性能基准。** 最新队友DISPATCH的b881与ZIP078635源码不同，Pass15记录不得借给本源。本地fixture的正式属性对应仍未唯一确认；本机输入与执行错误则是直接证据。

## 源码诊断与最小修复

原 `bmmms_manual_split_tt` Cube完成本核任务、Fix写回和槽位释放后结束；Vector直接 `SyncAll<true>` 再调用 packed finalizer。两者之间没有显式生产者就绪通知。

实际SDK `asc/impl/basic_api/dav_c220/kernel_operator_sync_impl.h:309` 的SyncAllImpl在isAIVOnly=true时只发SYNC_AIV_ONLY_ALL并等待；它不等待Cube。即使所有Vector到达，也不能保证各Cube partial已写回。缓存arena初始清零，读到0与这一竞态相容；具体时序仍由修复设备结果检验，不将源码诊断提前写成已通过。

候选 **353255B / SHA2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b**：仅新增两行，Cube尾部 `CrossCoreSetFlag<2,PIPE_FIX>(0)`，Vector先 `CrossCoreWaitFlag<2>(0)`，随后原AIV barrier/finalizer。MIX11配对通知写法已用于原C6等路径。每个Vector等本Cube的全部task完成后加入全Vector barrier，finalizer由此依赖全部Cube的Fix写回。既有event释放和所有计算顺序不变。

算法只改kernel.asc，无新GM、无新workspace/plan/输入/输出/正式测试变化。两行逆补丁逐字恢复e2f1b63；七个保护文件与1734f16相同。

## 验证与后续性能比较

`python3 tools/validate_c15_producer_ready.py` 抽取实际函数，检查send位于全部Fix和event drain后，wait在原barrier前，整份逆补丁和保护7文件。15个task-owner DAG（workers1/2/3/4/8 × tasks8/16/32）检查所有Fix均为finalizer前驱；原无通知及过早通知负例被拒绝。这是同步语义模型，不是硬件验证。

CANN独立编译在 `native_oj_like/build-c15-ready`，冻结source路径 imports/c15-producer-ready-2073f48e78d4。编译、同输入/full frame精度、全负/重复及五完整default报告尚待设备验证。若修复仍失败，保存原始bits/日志，继续诊断，不开始性能优化。

修复通过后，以这份**正确的修复版**作为C15性能对照，才考虑 C15_RESIDENT_INPUT_AUDIT 的batched A/完整split B常驻L1；不以原错误输出0的耗时估计加速。驻留优化预设20%完整TaskDuration中位改善门槛不变，正确性修复本身不冒充性能突破，不自动创建OJ任务。

Raw私有 `artifacts/c15-producer-ready` 与remote native_oj_like/results/c15-baseline-*。正式15点/另一SoC/当前ZIP接受源绑定尚未验证。


## 修复版 native 终态：PASS，成为有效性能对照

实际CANN9编译PASS，source2073f48e/353255B，DSOca36b327c9104b3006de2bb7ec732a3b817ae8fff447c6ce2a37e2d9c5fd28e6 /wrapper994e29f。相同case/full frame和输入，一次correctness精确输出1.6493455171585083，abs/rel均0。全负storage fullFP64golden -40.06380844116211，独立native correctness PASS。五次性能调用全部精确fullgolden，inputs/yguard完整，重复调用结果逐位相同。

默认全部8表×5，actual MIX11/8AIC8AIV/FP16+PACKED true完整符号。五TaskDuration `[10.540421,10.940437,11.080443,11.540462,10.760430]` μs，中位 **10.940437μs**。不是对错误原版的速度提升；原版输出0，不采性能。这证明该设备/输入的写回通知修复有效，不替代正式15点或其它SoC。

五sample内各role core-mean的中位：AIC MTE2 3.659375us、MTE1 1.086945us、Cube0.748125us、Fix0.218334us，AIV wait-id0 4.678958us、Vector0.131320us、barrier wait-id14 0.697431us。PMU时间重叠，不能相加或据此保证驻留收益。

下一resident split input实验以本2073f48e为parent，预设20%gate **<=8.7523496μs**；失败恢复本正确修复版，不恢复已实测错误的原ZIP。正确修复保留在独立分支，未OJ/未main。全部raw包已下载 artifacts/c15-producer-ready/c15-ready-*，完整source/DSO/输入/Plan/SoC绑定。
