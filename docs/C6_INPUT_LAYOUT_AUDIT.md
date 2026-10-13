# C6 输入供应结构：待设备验证

## 当前源码与范围

分支 experiment/c6-input-layout-audit 恢复整份 `e2f1b63:kernel.asc`（ZIP078635/353179B）。本分支暂未加入任何新算子实现，C12 strided写回和C4 compact产品候选已归档：前者仅0.53%中位下降，后者慢1.31%，都未达到预设门槛/未提交OJ。

C6用户已确认BF16 NT，记录完整frame `(13,23,73,192)`。源码实际较早的dual19 static32/80/192 MIX11直接返回，并且已经UnitFlag3；不对较晚fallback修改后假装它命中C6。原输入query `[B,M,K]`、document `[B,N,K]`，都按K连续。

C6本机normalPlan、实际符号、完整golden及五报告 **尚未采集**。当前仅源码路由分析，fixture的capture是待复核期望，不能代替actual capture。云平台长连接断开，最新入口重连跳板认证成功但目标转发报 `platform authorization denied`；已请求新入口。当前没有活动NPU任务，不把网络阻碍说成编译/精度失败。

## 不重做的方向

- 矩形Load3D旧候选仍先ND2NZ，然后仅把NZ→L0多个Load2D换成1×1矩形Load3D；没有明显正式收益。不要重接该代码。
- C6 staticKP192与既有UnitFlag3已运行，不是新优化。
- C6 TN/TT Vector预打包A与当前NT入口不同，无明确收益，不借用它的性能结论。
- C13 raw-normal在不同大M/小N/分K族中退化24.6%，不得恢复C13该分支，也不据此预测C6必然快或慢。

## 待核对的新结构

目标是去掉C6两个输入的GM→L1 ND2NZ转换，保留原正常C布局、同一完整K192 MMAD、UnitFlag/Fixpipe/Vector归约、输入/输出与GM arena。

把连续row-major `[R,K192]`作为channel16、单C1/H1、width=`R*12`的raw feature map。以宽12窗口、步长12、channel16采出每个原矩阵行的完整K192：

`source_offset = (row*12 + k//16)*16 + k%16 = row*192+k`。

query的R23→padded32，对应右padding `(32-23)*12=108`；document的R73→padded80，右padding84。目标A2应为原ZZ32×192，目标B2为原ZN192×80。这里是im2col坐标假设，不是已验证的CANN调用。

两输入实际长度均32B对齐；直接DataCopy应只读原有效输入，L1容量沿用原pad32/80分配，共43008B，L0A12288B/L0B30720B/L0C10240B。输入地址对齐、原完整plan/dtype/layout/core/UB/L1/L0/workspace需在host guard中检查，失败完全回退；不增加GM分配或新GM通路。

仅在确认实际CANN9公共header的LoadData3D filter/stride/padding字段、限值、目的ZZ/ZN、FMatrix LEFT/RIGHT与自动reset规则后才能实现。尤其不能编造padList顺序、依靠未写L1尾区、沿用旧NZ的物理跨度或改SDK内部缓存。具体参数表达尚未写入kernel。

## 当前验证

`tools/validate_c6_raw_row_geometry.py`：独立raw-im2col坐标模型覆盖13batch/full M23 N73 K192、所有有效reader、两种目标布局/补零、资源尺寸，故意错误pixel步长与正确行布局不同；同时要求实际kernel仍等于冻结baseline。**PASS仅说明该数学地址构造可行**，不执行Ascend API/浮点/设备同步，不能当成新生产代码验证。

## 下一条可执行动作

1. 新SSH恢复后，先补下载已完成的C4候选两个完整结果目录（正确性、五报告）。其summary已由工具读出并在C4文档记录；SSH断开时原始候选表尚未下载，保留server路径。
2. 用旧baseline DSO+新c6.json读normalPlan，只读复核完整frame；再生成完整实际storage FP64golden，跑一次精度和五默认报告（独立queue/锁、source-DSO-input-plan-device绑定）。不改main/CMake/golden。
3. 采actual API headers并核对上述raw解释，依据真实C6 MTE2/MTE1/Scalar证据决定是否值得实现。不能没有瓶颈证据就盲目跑raw变体。
4. 如实施则只做一个上述结构候选，实际CPU源/尾块/事件+native全golden/五报告验证；采前固定较大收益门槛，失败即归档，不扫描filter/stride邻近参数。正式15点另行验证。

原始本机模型日志在忽略目录 artifacts/c6-input-layout-audit；SSH脱敏失败日志/private/tmp/bmmms-remote-access/reconnect-sanitized.log，原凭据不入Git。全局冲榜目标仍未达成。
