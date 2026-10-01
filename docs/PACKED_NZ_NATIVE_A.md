# 连续 Cube-ready B 与原生完整 M 的 A 加载组合

## Evidence → Diagnosis → Fix

父版 `0ad246b` 已正式15/15通过，但第12点95.41→96.65μs，没有明显收益。它保留连续B，在原packed region一次准备NZ，再线性读入B1和bulk非转置Load2D到B2。
A的resident full-K slab仍按M16循环转置Load2D，M128时每K面板8次。因此仅移除B的重复格式转换不足以消除两侧逐块加载开销。
本次在NZ_B=true家族复用正式通过TT版本的 `ManualTransposeFullM` raw-bit矩形加载。其它路径保持原A2实现；默认模板、GM、packed格式、Vector预处理与消费、局部/跨核events全部不变。

同一示例M128/N256/BK64：旧A/B的加载发起8+4次，NZ-B父版8+1，本次1+1。样例源调用数，不是对库的速度比例或正式plan。
4-storage候选也用了native A，但同时撤销pack，第12点退化22%；本次保留连续NZ B和原屏障，与该候选的数据通路不同。不重复其direct B方案。

## 容量与 API

没有新buffer或plan变化。A1依然完整K、resident A2 ping/pong；用s.k作为完整K NZ pitch。此家族K/N为16倍数，host原packed条件保证完整A驻留，raw helper的rows/count/K offset均对齐。
该 helper 使用CANN9支持的half类型Load3D enTranspose，通过ReinterpretCast访问原FP16/BF16位；MMAD仍用实际T和FP32。文档/正式TT依据见 `FULLM_TRANSPOSE_LOAD.md`，B的uint16_t转换依据见 `PACKED_B_NZ_ONCE.md`。
已有TT结果证明其测试范围内的raw-bit搬运可用，不证明本组合的所有shape或精度；正式组合仍PENDING。

## 验证

`python3 tools/validate_packed_nz_native_a.py`

- 直接抽取实际 `bmmms_manual_case12_packed` Cube计算体；仅把原GM packed指针重绑定改为模型已准备的B参数，数学/局部同步、flag12 wait、GM ring写入、C/event清理按实际源码运行。
- 724执行：多B/M任务/N分片/worker，M/N16尾块、K16但非64/128倍数、全负、C1/C2、完整K以后Max(N)与Sum(M)对照。
- 原始A输入到resident NZ的DMA延迟到Fence，BQ复制延迟到DeQue；每个C输出与独立完整K golden相等，input/source ownership及events/credits收支、容量、A/B实际复制/加载次数通过。
- 每K面板A矩形恰好一次；完整N块B bulk一次，N尾块B按K16 plane加载。首次测试沿用“一次B load”的TT假设而在N尾失败，已改为独立统计完整/尾块的期望次数，没有修改kernel来满足断言。
- kernel仅native A if分支与 `99fc974` 不同，脚本回退该分支后全文件逐字一致，证明plan/其它算法和所有预处理字节保持不变。

`python3 tools/validate_packed_b_nz.py`：新组合B预处理/复制/加载原ND和新NZ各2016执行、新NZ全65536bit；fake tiler production/TUNING各1728/54通过。源比较定位至B分支，并允许确切新增A片段回退，防止误删A循环。
公开真实8.3 tiler的相同host原版已各1728/54通过；本次host逐字未改，不重测无关tiling参数。
模型MTE1/MMAD/Fixpipe同步执行，A/B数学为小整数FP32；不是hardware异步时序或FP16/BF16舍入仿真。

## 正式请求

kernel SHA `8e1fbca3a87bc380a174fbc01a181da8c5d8f9a7b02294d9d4f5895b5914942c`。
独立官方模板 `/private/tmp/bmmms-judge-packed-nz-native-a/project`；只kernel.asc，main/CMake/golden/正式测试/依赖不变。
CANN9组合编译、NPU精度、逐点latency PENDING，尚未创建任务。
在这次组合结构上提交一次、查询同一ID至终态；没有大幅收益则归档，不继续相邻tile或LoadData stride试交。整体重大提升未达成。
