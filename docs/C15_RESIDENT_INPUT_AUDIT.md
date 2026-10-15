# C15 长 K：原 L1 常驻完整 split 输入的结构审查

## 当前状态与来源

分支 experiment/c15-resident-input-audit，kernel保持整份 ZIP078635 / e2f1b63 /353179B。**没有新增 ASC 候选**，没有 native C15 测试或 OJ 提交。此前 C6 raw-row 已 native 精度失败，完整档案 C6_RAW_ROW_INPUT / commit0689e2d；不借它的 CPU 模型证明新布局。

用户提供 shape `(1,64,64,8192)`。FP16 TT / dual25 是历史源码与结果对应假设，最新队友 DISPATCH 未唯一隔离 C15 dtype/layout；不能当成读取了正式隐藏属性。新 fixture c15.json 明示来源，capture 中8AIC8AIV是待实际 normalPlan/符号复核的期望，不是已测结果。

历史审核：已保留 manual split-TT/MIX11/packed finalizer，旧 coverage/adaptive split、C7 whole-input、C8 full-input、C9 resident-A 与此不同。没有发现针对当前 dual25/八个 K1024 分片的这组 A多矩阵布局+B整分片输入实验；不恢复已失败的 C8/C9/C13 raw 或调整 split 数量。

## Evidence → Diagnosis

当前 kernel 的 bmmms_manual_split_tt：每 task 是一个 K 分片，BK128，AQ/BQ各深度2，L0A/B双槽，整个 split 累加到一个 C，Fix后仍保留原 SyncAll 与 FinalizeSplitKND。对记录shape，plan源码倾向 kSplit8/kChunk1024/workers8，实际需 SDK MakePlan 确认。

每个 split 8个K128面板，ManualCopyK分别做 A/B ND2NZ，16次GM→L1指令/API及queue生产消费。全算子8个split共128次输入ND2NZ；两输入总有效数据2,097,152B，没有跨split重复数学输入。不能把指令数量称为数据冗余。

## 一个待实现假设

在**原 L1**各常驻一个完整split，保留原ND2NZ与Load2D以及每一个K128 MMAD，不引入Load3D或raw表示：

- A物理 `[K,M]`：一次batched ND2NZ，ndNum8、nValue128、dValue64、srcDValue64、srcNdMatrixStride8192、dstNzC0Stride128、dstNzNStride1、dstNzMatrixStride8192。生成八个原K128 A面板的顺序拼接；**不能用一个 nValue1024 的NZ矩阵代替**，其outer-block次序不同。
- B物理 `[N,K]`：一次ND2NZ，ndNum1、nValue64、dValue1024、srcDValue8192、dstNzC0Stride64、dstNzNStride1；原K128子面板就是fullB相对offset `relK*64` 的连续片段。
- L0双槽、两次LoadData2D每步、8个MMAD、cmatrixInit首步、K累加顺序、M_FIX/Fix/FIX_M、全部AIV和packed finalizer、原GM partial分区/bytes保持。
- A就绪/B就绪各需独立MTE2_MTE1保护，不能未完成即读；跨task复用必须在原最后读者与Fix完成之后。实际输入指令从16降2，不是把K面板或输出省掉。

batched ND2NZ的所有字段在保留源码 PACK_A 分支已出现，取值模式一致。但新源组合仍需真实CANN9 header/编译/全golden；不能以源码中出现过就宣称新组合已验证。

## 容量与代价

目标M=N64、chunk1024：L1从双队列65,536B变成262,144B，增加196,608B；加4KiB余量在实查9382 L1=524,032B内。L0A/B各32,768B双槽、L0C16,384B不变。packed finalizer显式UB约131,904B（另保留1KiB余量），原GM8份C=131,072B不变。

M=N128同chunk需要524,288B L1，已超过实查524,032B，必须回退；不要套用“512KiB可用”假设。初始候选应只接资源完全匹配的原FP16TT/dual25/fulltile框架，全部显式TUNING pins及其它shape/layout保持旧路。真实资源/worker来自查询与原plan，不假定固定A2/A3核数。

**GM读字节/L1写字节不减少**，A的单条batched ND2NZ仍处理八个矩阵。更大的首批DMA会延迟首个MMAD，旧双队列的搬运计算重叠可能更好；queue/API更少并不代表更快。原packed finalizer尾部代价完全保留，本假设不能解决那部分耗时。

## 离线地址证据与未验证范围

`python3 tools/audit_c15_resident_input.py` 检查parent SHA固定，按现有ND2NZ坐标模型比较：M/N16/16 K4096，64/64 K4096，64/64 K8192，128/128 K8192；全部八个split、每个K128的A/B L1面板源地址与旧路径一致，输入界内；naive整A-NZ的不同outer顺序反例被发现。日志 ignored artifacts/c15-resident-input-audit/address-audit.log。

这是**提案地址模型**，不执行新的kernel、SDK tiler、真实DMA、LoadData或FP16累加。没有把M/N128超L1用例判成可运行。C6的反例已说明CPU模型不能代替设备验证。

## 下一条可执行动作与停止条件

1. SSH恢复先补下载C6失败raw，不重跑；复核SoC/队列/实际映射，部署独立driver的失败原始bits保存改进。
2. 现有baseline DSO0357587a+新c15 fixture执行plan，只读并人工审阅实际完整字段；若不是原dual25/M64N64/K1024/8split，先按真实计划重审，不强制分派。
3. 生成完整实际FP16storage→FP64golden，parent一次correctness+五default全部完整报告，记录真实MTE2/队列等待与完整TaskDuration。**缺这步不生成待提交候选**。
4. 仅实现这一组驻留表示，CPU抽取实际producer/Load2D分支检查地址/事件，七个受保护文件/GM/数学体逆补丁检查；独立CANN编译，candidate一次完整precision，再五完整default报告，actual新符号确认。
5. 采前门槛：完整TaskDuration中位数至少改善**20%**才补负值/重复/资源回退/native覆盖并准备正式15点；失败即归档恢复ZIP，不扫描chunk/面板/队列深度，不原样重测或提交OJ。

当前SSH目标转发授权再次被平台拒绝，已请求新入口。没有C15编译/精度/性能结果；整体大幅冲榜提升未完成。
