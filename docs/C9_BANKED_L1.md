# C9 双半区 L1 生产者

## 假设与范围

设计依据与布局审计见 [C9_BANKED_L1_AUDIT.md](C9_BANKED_L1_AUDIT.md)。从正式保留2073/a11e2d9派生，仅C9 FP16 NT B1/M2048/N1536/K1280、dual36/BM128/BN128/BK128/PK256进入新分支；其余回原。A按K包分两半区，两条multi-ND DMA；B两独立颜色游标，解决每tile五包的奇偶翻转。最高L1字节458752与原payload相同，无新GM分配/通路，原MMAD/fullK/Fixpipe/C ring/Vector/MaxN→SumM保持。

新helper约90行，原RunManualFullMCube和bmmms_manual追加默认false BANKED_C9并透传；默认false主体不改。实际host guard查询AIC/AIV和L1/L0/UB容量、原workspace精确容量、拒绝tuning pins。PK严格256，不能接受512。没有修改MakePlan或protected7。

## 分层验证（2026-10-15）

- CPU地址审计：`python3 tools/audit_c9_banked_l1.py`，原actual captured plan；163840 A标签、多ND两个描述符、全部A/B区间和960B包/192tiles通过。
- CPU实际源码生产者：`python3 tools/validate_c9_banked_l1.py`抽取两个新helper、原Load3D封装和原任务函数。在四延迟FIFO引擎/三调度优先序/混合和全负两个整数proxy上运行120个worker；每完整run1920 MMAD的全部A/B索引标签、192 Fix C元素、原C ring窗口、在线MaxN/SumM与独立oracle相符，L1/L0/GM边界/原typed事件归还通过。
- 10故障控制均拒绝：多ND源stride、颜色重置、A包视图、B最后reader、B ready、A ready、L0最后reader、C最后Fix reader、MMAD→Fix ready、截断K。whole-parent inverse逐字a11e2d9/protected7逐字1734f16通过。
- 模型明确限制：不是Ascend硬件队列、FP16精度或时序模型。数值部分是可分离整数proxy，实际源码的每个输入元素用标签逐项核对。通用Fence按每代依赖建模，不模拟SDK FetchEventID复用；最初将其误设固定7号使无限队列调度报告重复置位，已纠正模型。SDK TPipe::FetchEventID实际取eventOccupy第一个空位且不占位；不据此声称硬件事件复用已由CPU证明。显式生产者事件仍检查配额和token。另一SoC/其它动态plan未上板。
- host guard：`python3 tools/validate_c9_banked_guard.py`，49/60反例（普通/tuning）和8/20/24/32预算/容量逐字临界通过。
- 首份source a8c905bcb389626d4597af744b1a61f642a504ba8884b989e577877041aed1ae CANN9/dav2201编译通过，未launch。随后仅收紧PK保护为256，新source **86c85293ec13261c260b51ce7e3f402ee6a47b6527cec9f796d3bdc5f0238484**，361136B，独立冻结并编译中。必须用新source的DSO做native，禁止混用首份产物。
- NPU精度、完整性能、正式15点：**PENDING**；没有本轮速度结论/OJ。

## 固定设备验证与性能门槛

当前实际9382/24AIC48AIV/logical0→physical14/CANN9/caller20。原c9.json、完整c9.complete_frame.json和inputs/c9/fullFP64 golden191.8094940185547保持。先一次native精度/input/y guards；成功后一次默认完整8表×5报告，要求实际BANKED_C9=true/20Cube40AIV、每核90或100 MMAD原样。

parent source2073/DSOca36五次[55.142204,54.922195,56.122246,55.062202,55.382214]us，median55.142204。预定准入median<=49.6279836且所有五<54.922195。不达则归档恢复2073，不重采同source，不扫offset/PK/BK/flags。大收益才继续全负/同地址变化输入/正式15。整体冲榜目标未完成。

## 文件与接续

- 当前冻结：远端imports/c9-banked-l1-86c85293/kernel.asc；build native_oj_like/build-c9-banked-l1-86c85293；log c9-banked-l1-86c85293-build.log。
- 旧首份单独保留imports/c9-banked-l1与build-c9-banked-l1，不能把其编译PASS冒充当前DSO。
- 原始日志/构建/input/凭据仅私有artifacts/远端，不入Git。
