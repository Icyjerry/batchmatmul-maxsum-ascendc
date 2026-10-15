# C11：交换输入计算 Cᵀ，沿原 N 归约

## 固定假设与采前门槛

Parent a11e2d9/kernel2073f48e（353255B）包含已验证的 C15 producer-ready 修复。本机 C11 fixture 为 B1/M1536/N2048/K2048、BF16/TT；shape 来自用户，BF16/TT 是本地明确假设，不能据此声称读取了正式隐藏属性。

9382/24AIC48AIV、dev0physical14、CANN9.0.0，caller limit20。实际 parent plan 为 BM256/BN128/Mt6/Nt16/Ns16/workers20/dual2，并非旧注释的 BM128/BN256；system16777216/total22118400。原 GM arena、任务分配、握手与 finalizer 保持。所有七个受保护文件不变。

Parent DSOca36b327：完整实际 BF16 storage→FP64 bmm/MaxN/SumM golden116.7254638671875，native116.72545623779297，abs7.62939453125e-6/rel6.536186945404538e-8。独立一次及五次性能调用全部通过、输出一致、输入及 yguard 完整。默认8类表×5，实际 MIX20Cube40Vector。五 TaskDuration `[75.783028,76.703072,76.423058,75.923035,76.023041]` μs，中位 **76.023041μs**。

候选采集前要求完整五报告中位至少降低20%，即 **<=60.8184328μs**。不过门槛则归档并恢复完整2073，不做相邻参数扫描或无变化重复采集。通过才补负值、FP16、回退/正式15覆盖并考虑 OJ。

## 实现与 SDK 证据

候选 kernel **356971B / SHA06f3e06e0f3fde1e3cd7c63e2487f978298e0502ef6ca8ad9bcb0a6cb25050c5**，相对 parent77增11删。MDL 增默认false模板参数 TRANSPOSE_C；仅原 TT C11完整shape/plan、资源和 tuning-pin guard 允许 true。

TT physical x2[N,K] 与 x1[K,M] 交换为 NN 乘法，得到 Cᵀ[docN,queryM]，不搬运输入转置。完整 K 计算后，AIV 保持原 query 半块所有权，从 Cᵀ 每行抽取负责的 query128列，再对 doc128行做纵向二叉 Max，最后仍沿原 M 求和。原 ND ring 字节、slot、partial、credits、通知与 finalizer 不变，无新增 GM。

使用实际 CANN9 MatmulApiTiling 重新查询128×256 NN，不把旧 TT tiling 字段交换冒充合法新 tiling。独立 host-only SDK 查询（无 kernel launch）返回 NN base128/256/64、stepKa8/depthA16、stepKb2/depthB4、dbL0A/B2/C1、shareL1393216；候选保留 SDK 返回的分组，资源/返回字段不合要求则回原路径。host query 初始自建 CMake 漏 arch 导致编译失败，补 dav-2201 后编译和查询成功；没有修改原 CMake。

## 验证边界

`tools/validate_c11_transposed_c.py` 抽取实际 operand/offset/tail、GM copy 与 Max 代码，执行6个完整构造 similarity 矩阵（mixed/all-negative各3seed）的所有 tile，检查 Max原N/Sum原M、地址/guard、4个故障反例；反向删除新增true逻辑后 parent默认 MDL逐字一致，范围外及保护7逐字一致。CPU PASS；不是完整 K 点积或 SDK/硬件同步证明。

CANN9/dav-2201：原 wrapper DSO及带 actual-selector metadata export 的独立 DSO均编译成功。后一编译观察因 SSH断开中断，新入口检查真实 buildlog/DSO确认完成，没有重新编译。metadata export 查询真实 MakeTTMdlTranspose，不执行 NPU kernel。

候选 actual-selector/full-storage native precision/default五报告：PENDING。不得称性能收益、正式15通过或突破。原始 baseline 已下载 artifacts/c11-mdl-output-audit；候选原始资料使用 artifacts/c11-mdl-transposed-c。

## Native终态：精度通过，慢5.025%，归档恢复parent

候选实现commit5edc14f/source06f3e06e，metadataDSObcd8a8e0951a3d9b255088a2b7ad8e8c48b5cbcdb3506ae6151e1209414b7cde，wrapper225154c4/included994e29f。actual-selector FP16/BF16均selected1，实际符号为bmmms_dual_mdl<bf16,true,true,true>，20Cube40Vector/default8表×5。一次完整精度及全部五性能输出精确fullFP64golden116.7254638671875，input/yguard完整。

五TaskDuration `[79.703186,80.263214,79.023163,79.843193,80.363213]` μs，中位79.843193μs，parent76.023041μs，慢约5.025%，未采前20%gate。完整恢复2073f48e/a11e2d9；不扫描NN分组/相邻tile、不重复采集、不OJ。FP16仅host选择查询通过，未执行候选FP16点积；失败候选不再补正式15或其它SoC。

PMU每role核心均值五次中位parent→candidate：AIV Vector5.146000→1.953111us，MTE2 3.333153→3.940319；AIC MAC44.009944→44.391416、MTE1 25.440472→32.894028、MTE2 45.608556→49.547611、Fix4.217611→4.087889us。纵向Max减少Vector时间，完整op仍变慢；重叠计数不能相加，也不能把因果归给某个指标。此反例否定本机该NN表示的完整性能假设，不否定纵向归约数学正确性。

全部build/真实SDK查询/selector/source-DSO身份/correctness/五报告已下载artifacts/c11-mdl-transposed-c/c11-transposed-evidence.tgz，summary/pipe比较一并保存，目录700/files600。远端results/c11-transposed-*保留。CPU模型对归档候选运行；当前kernel恢复parent后不应误跑候选专属模型或放宽检查。
