# C12：合并 B 预处理写回

## 假设与范围

基于 `e2f1b63:kernel.asc`，即队友 ZIP 的实际源码 `0786352034e77506894d4094083960f4f6af82782bf7cee6a0386148437ca436`，353179 字节。这不是 DISPATCH 所记 `b8817327`，不得借用其正式成绩。

现有两阶段 B 预处理每次处理 K16×N1024，转成八块连续 UB N128 native Zn，再向八个等距 GM panel 发出八次 DataCopy。候选合并成一次八 burst 的带 stride DMA。两阶段划分、队列、事件、Cube、归约、所有 GM 分区和 host guard 原样；只有 `PHASED_B` 原有入口的两处调用启用新模板参数。其他调用默认关闭。

候选 SHA `e00469b59130940f199e4b5f3a9fa4ab9c64cf34da965a2e7a064985679d94ae`，353524 字节。差异 9 增 / 5 删；指令压缩幅度与修改行数无关。

## API 和地址证明

实际 CANN 9.0.0 SDK：

- `/usr/local/Ascend/cann-9.0.0/aarch64-linux/asc/include/interface/kernel_struct_data_copy.h`：DataCopyParams 的四个参数均为 uint16。
- `.../asc/impl/basic_api/dav_c220/kernel_operator_data_copy_impl.h`：UB2GM 直接传这些参数到 `copy_ubuf_to_gm`。blockLen、源/目标 gap 以 32 字节计。

描述符为 `{8,128,0,12160}`：每块4096B，UB源连续；目标步长 `(128+12160)*32 = 393216B = K1536*N128*2B`。起点仍是第一个 N128 panel 的 K16位置。最后一个 panel 的最后 K16块恰好终止在原 packedB 边界；无新增 workspace。原 znq EnQue/DeQue/FreeTensor 保护源生命周期；phase SyncAll 和 MTE3 ready flag 保护全部写回可见性。

CPU 验证工具 `tools/validate_c12_strided_prep_store.py` 抽取实际 helper、执行旧 false/新 true 分支，独立建模字节 DMA 与转置。覆盖完整 K1536/N4096/40AIV/两阶段、所有6291456个元素、前后guard、native Zn坐标；整份逆补丁及受保护七文件检查。故意错误 dstGap 必须被拒绝。该模型不验证设备事件或浮点数值。

## 冻结原版的本机证据

设备 Ascend910_9382、实际24AIC/48AIV，logical0→physical14/card7chip0；调用者 core_limit20。CANN9.0.0、dav-2201、driver26.1.1。与队友9362机不同，不直接比较历史耗时。

正常 MakePlan：BF16 TN `(1,1280,4096,1536)`，dual6，BM128/BN128，mTiles10/nTiles32/Ns2/workers20，窗口1；case12PackedA/nativeZn/phasedB均 true；原 direct raw A 特化。system16777216B/total35923968B。DSO SHA `0357587a9f1f73d128bb90cf381d0400731060e6628800f96cde02a7750a907f`。

实际 storage 全 FP64 bmm→Max(N)→Sum(M)→FP32 golden：118.35807037353516；一次正确性与五次性能输出均精确一致，输入不变/y guards完整。0应用预热/5完整调用，msprof op warm-up5/launch-count5000/replay-mode kernel/default metrics，无过滤。五次全部具备八类报告/20Cube40AIV/实际符号/192 MMAD每Cube/source-DSO-input-plan-device身份。

Task Duration(us)：`[83.123322,83.063324,83.403336,83.323334,82.023277]`，中位 **83.123322**。

每次各核均值再取五次中位的 PMU：AIC MAC55.810417/MTE152.463472/MTE256.412639/FIX8.147611/flag12等待9.551250us；AIV V14.888778/MTE214.589070/MTE33.740444/MTE3 scalar stall7.828042/Sync14等待6.173903us。这些重叠计数不可相加或据此作因果归因。

## 提交门槛及待验

在采候选前固定：独立 CANN 编译、相同输入/计划/设备完整正确性和默认五报告，中位耗时至少降低10%（≤74.8109898us）才进入正式提交准备；否则归档，不反复提交或扫描临近参数。即使指令数下降也不当成实际加速。通过性能门槛再补全负等风险用例；正式全部15点仍需实际OJ通过，不能由本机单case替代。

CPU实际helper模型 PASS：旧/新完整字节一致、native Zn坐标/guard/整份逆补丁/七文件检查通过，错误stride被检出。首版CPU stub将GlobalTensor的指针索引当成值比较，编译失败；修正模型为 np.p[offset] 后通过，kernel未因此修改。当前 CANN候选编译/精度/性能：PENDING。无新OJ任务。

原始资料在权限受控忽略目录 `artifacts/c12-strided-prep-store` 和服务器 `/workspace/bmmms-codex/native_oj_like/results/c12-*`。原版首采集完整，无丢弃样本/跨任务最小值拼接。

## Native 终态：指令压缩成立，未取得明显提速

CANN9编译通过（8条既有风格警告）；实际DSO SHA `3016603906cb7ab6ce14ca9d856acf598d4c951592f95c7db8008d307f449e21`。一次正确性及性能五次结果均精确匹配完整FP64 storage golden，输入与输出guards完整，原normalPlan完全相同。

五次完整 Task Duration(us)：`[83.063324,82.683304,83.123322,82.563301,82.683304]`，中位 **82.683304us**，较原83.123322仅下降 **0.52936%**。每次全8默认报告、20Cube40AIV、完整身份通过。每个报告实际MTE3指令总数恰少2688，各AIV少56或70条，匹配源模型3072→384写回。AIV MTE2指令均值26.7原样，证明没有省略输入读取。

PMU各核均值的五次中位：AIC MAC55.810417→55.809028，MTE152.463472→52.274139，MTE256.412639→56.823805，flag12等待9.551250→9.039278us；AIV MTE33.740444→4.178486、Scalar MTE3 stall7.828042→0、Sync14等待6.173903→5.420236us。计数重叠，不相加，不据此声明因果。消掉scalar等待没有同步消掉数据搬运耗时。

未达到预设≤74.8109898us的10%门槛，不提交OJ、不重复采同版、不作临近burst/stride参数扫描。原版和候选全报告归档；后续恢复整份ZIP078635。全负及其他family扩展未执行，因为性能门槛未通过；正式15点与另一机型未验证。
