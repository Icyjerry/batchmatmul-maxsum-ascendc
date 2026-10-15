# C3：将逐行 Gather 改为完整 offset 矩阵一次 Gather

## 假设与门槛

Parent2073f48e/a11e2d9正式Pass15/398.92us，正式C3=3.12us，但dtype/layout尚未唯一确认，已向用户询问。当前本地fixture仅明确采用BF16 TN、B2/M7/N13/K48；不得根据该耗时推断正式隐藏属性。

新的数据准备结构保持原GM DMA、FP32 Cast、乘法与两级归约：先将行号广播成每行8个相同byte offset，和原k-stride向量用重复Add生成完整[row,K48]偏移矩阵；每个需转置的输入只Gather一次，替代逐行Gather。TF需要7+13=20次变成2次，TT为7→1，FF为13→1，NT原本无Gather所以回原路径。新增Brcb/Muls和每输入一次Add/屏障，UB增加3008B，可能抵消收益。不使用此前失败的raw transpose、K-tree或静态常量frame。

设备9382/24AIC48AIV/dev0physical14/CANN9/caller20。原DSOca36实际normalPlan dual24/group1/workers2/final2/total0/Cube0，纯Vector2AIV。baseline一次及五性能输出与实际BF16storage→完整FP64golden[1.5601825714111328,1.773697018623352]精确一致，input/yguard完整。默认8表×5，times[3.420137,3.020121,2.880115,3.120125,2.920117]us，中位3.020121。

采候选前固定20%门槛 **<=2.4160968us**；未过归档恢复2073，不扫Brcb次数、repeat stride或相邻M/N/K，不重复采样/OJ。过gate再补相关布局/dtype、negative/变化输入和回退验证，之后考虑正式15。不是已确认正式C3提速。

## 源码和SDK

source **8b13ff71f8d5897048efee80c4f8817f7d4c1098308f501eb789df473d2c598b**，算法35增6删。TinyCompute/原grouped wrapper增加默认false FLAT_GATHER，仅原GROUPED/K48入口、B2M7N13/group1/blocks2、需要转置且实际UB/AIV够用时启用；任一显式TUNING pin回退。

原idx[0..47]、ia=idx[64]、ib=idx[128]保持；新增rowOffsets=idx[192]长度128、offsets=idx[320]最多624。Brcb两repeat广播前16个行号，每行8副本，再Muls4转字节。Add mask48/repeat7或13，BinaryRepeatParams{1,0,1,6,1,0}，生成offset=4*(k*rows+row)。Gather完整336或624值。两个输入顺序复用offset buffer，保留PIPE_V依赖，不增加输入padding或Cast字节。

实际CANN9 dav_c220 Brcb public接口支持int32，后台vbrcb b32按8个源标量/每标量32B块广播；不是浮点数值转换。资源guard用原TinyVectorFits(frame,UB-3008)，TF/TT/FF最低UB36608/34144/35296B（含原1024余量），原group1、2AIV/grid不变。其它layout或shape默认原路径。

## CPU证据与native状态

提取实际Brcb/Muls/Add/Gather，48组完整K48 batch/layout/mixed/allnegative样本验证canonical两输入、全部M7N13点积及MaxN→SumM、source bounds/UB guards，五故障反例被拒绝；默认false逆变换恢复整个parent，保护7一致。模型使用整数值代理，Cast/原点积源代码保持，不证明BF16硬件或SIMD子流水。

实际guard抽取production/TUNING检查TF/TT/FF接受、NT拒绝、shape/group/grid/AIV/每布局UB精确边界和pins；是控制流而非SDK tiler。CANN编译正在exec47243，候选native精度/性能/正式15 PENDING，尚无新OJ任务。

CANN9/dav2201编译PASS（8条原host GM_ADDR warnings），DSO5a7b719401d77aa7febe05a95ff17bed2b72f82a6b639d824c44620e934f2fbb/source8b13ff71/wrapper994e29f，冻结imports/c3-flat-gather-8b13ff71f8d5。guard production/TUNING分别31/64拒绝通过；独立guard脚本最初漏struct结束符、漏Tune定义，修正模型提取后重跑通过，kernel未改。一次native correctness exec97615进行中，仍无性能结论。
