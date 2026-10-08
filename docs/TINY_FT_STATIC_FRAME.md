# 小 FT：编译期物理 frame 与有效 N 归约

## 证据与假设

分支experiment/tiny-ft-static-frame，父bfd5d0a/算法1734f16。上一目标turn有进展：更新用户Tbest并重新计分；没有活动设备任务。本轮按新Tbest和最近五个同SHA任务中位重新核算，与用户此前提供的历史领先耗时相比，优先C3/C13/C11/C9/C1；见SCORE_PRIORITIES_1008，不是实时榜单结论。

C3历史条件B2..3/M4..7/N8..15/K32..56/FP16/FT，不是已确认正式shape。父已按batch独立AIV、一次共享Cast、常量K分发，不再声称首次提出这些。此前storage-native/Brcb/Ktree等已失败，本轮不重做。

本轮结构：M/K/padded-N作为模板参数，整套UB地址和M循环界限编译期确定；参数从TinyKernelShape+batchGroup缩至4B实际N。直接只对真实N做点积和K归约，紧凑写M个Max值，最后只Sum实际M。省去产品尾部初始化和32B每行的零身份槽。每M增加一条WholeReduceSum，可能抵消成本降低；不预言性能。

## 实现范围

- kernel SHA `515aa1592edbb26252b06b0ec610fc96d7c1353f69347a9e3b92327f39f5e024`，新增92行，device entry/host guard+dispatch/launch三处。移除三处逐字恢复整个1734f16。
- 仅原dual24/batchGroup1/finalBlocks=B/cubeBlocks0，FP16/FT及上述范围准入。真实AIV/UB、全部显式TUNING pins保护。MakePlan、grid/批次配对、workspace、其它kernel逐字保持。算法仅kernel.asc，不改main/CMake/run/golden/正式测试/依赖、不新增GM。
- 四种M×四种K×两个NP（8/16）编译期组合；实际N一直从输入shape传递，无虚构case ID或输入值。普通C++pragma unroll提示，是否真的展开取决于CANN编译；没有反汇编证据。
- UB六区均32B对齐：合并typed输入、合并FP32 Cast目标、产品、点积、紧凑Max、输出。最大38,016B，另留1024B，平台不足保留父。DMA每行只读实际K，K8非16尾由已有DataCopyPad补零；Cast只读实际M/N的KP槽。
- Mul只写有效N/K，逐M WholeReduceSum只读这些已定义产品；WholeReduceMax只读有效N点积，Sum只读有效M。内部NP尾从不读取，不依赖尾部垃圾值。完整K FP32→MaxN→SumM，全负与唯一精确FP32[B]写保持。
- 输入ready、输出ready和terminal PIPE_ALL保持父协议，无TPipe/队列/destructor完成依赖。

## 本地验证

`python3 tools/validate_tiny_ft_static.py` exit0：

- 1024 actual entry /512软件编码FP16执行，覆盖全部256个历史C3条件shape及正负/全负。完整K FP64 oracle→FP32，maxAbs7.45058e-9、非零maxRel1.18781e-7。输入不变、y guards/唯一writer、typed UB/GM界限、逐byte定义后读取、输入/Vector/输出三FIFO通过。
- 八项负控制拒绝：输入ready、输出ready、terminal完成、缺少K尾、把N归约repeat扩成NP导致读未定义产品、Max读NP、Sum多读M、跨batch输入偏移。
- 最初保留父Npadding初始化的模型中，删除初始化没有改变输出，故未将它编造成数学必需。随后改为只计算/读取有效N，增加逐byte定义检查；新路径自身不清产品尾，也不读产品尾。没有降低输入/输出/typed界限要求。
- production/TUNING各4800 actual host配置/96选中，以及各256完整条件范围shape；UB恰好阈值与低1B、核数恰好与低1核、plan/grid不符/pins回退通过。原Schedule/GM不变。
- scope逆变换整父相等、git diff --check通过。

模型软件解码FP16、FP32算术和FIFO，不是设备SIMD子流水/延时模型。其它dtype和布局保留父入口，不把它们冒充新路径精度覆盖。CANN9编译、native精度和性能 **PENDING**。API都是原已通过入口所用的DataCopyPad/Cast/Mul/WholeReduceSum/WholeReduceMax，但新template/compact frame仍需native验证。

## 提交与当前阻碍

独立模板/private/tmp/bmmms-tiny-ft-static-official/project：其它七源码从1734f16重建且逐字一致，仅换kernel。原/tmp模板和CLI已经被OS清理，公开CLI/helper从Git忽略artifacts/tooling/cannjudge-submit恢复，未复制或读取凭据。

恢复的CLI dry-run返回“登录会话已过期或损坏，请重新运行login”，尚未得到有效dry-run或创建任务。用户回复已登录后再次重试仍失败；默认会话文件stat最后更新10月3日，已请求使用上述恢复CLI在本机login，或仅提供另一个会话文件路径，不读取其内容。下一登录成功后重新dry-run核对SHA、commit/push后仅一次结构提交，取得ID立即保存并查同ID到终态；没有ID时不虚构Running。若明显大收益才原样确认，否则归档不扫附近M/NP/K参数。

父最近五次C3 3.18/3.12/3.22/3.16/3.08μs，范围3.08–3.22、中位3.16；另更早同SHA有3.06，不择优掩盖波动。接口无实际shape/plan/SoC/profile，不能凭case编号证明新路径命中。原CPU日志忽略artifacts/tiny-ft-static-frame/，目录700/文件600。整体冲榜目标未完成。
