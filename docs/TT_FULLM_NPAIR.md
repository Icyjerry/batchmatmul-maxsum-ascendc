# 完整 A1 / 矩形转置下的 N tile 配对

## 证据与差异

UB worker Max候选 `34956fe` 正式15/15通过，但第8点59.66→59.72μs，没有收益。本次恢复父 `0d4bd04` / kernel `65e38bb155af9adb068e87dc90c01face21a7cf024d094c54846c5188e9ca120`，不合入该UB候选。

历史 `experiment/tt-panel-pair` / `7b4d477` 正式无收益。源码最后的准入要求M/N/K均16对齐、BM=BN128、每N shard至少两个tile，并设置panelResident=0；A按K面板重复GM读取。不能将该历史结果当成非对齐/64行、完整A驻留加Load3D流水的结论。

当前已通过父完整A1驻留，A矩形Load3D每K每Nt执行一次，连续任务使同M相邻Nt在同worker内。本次只修改这个producer，复用已有两份L0C和双GM ring：同M的两个相邻N tile在每K共享一次A2转换。

## 实现与不变量

- worker原始连续tile区间不变，不为配对改变任务分配；仅在区间内、同M/batch且仍有第二N tile时成对，边界余tile走单个。BM64/128、M/N尾、K非16倍数沿用父的补零与有效范围。
- 同对有两个独立C累加器，完整K之后按原Nt顺序分别输出原slot0/1。Mmad K顺序和FP32累加保持，不对部分K取Max。
- A2双缓冲仍按K交替；B2两缓冲分别属于组内N tile，B1双queue按K-major/N顺序读。A release在组内最后MMAD之后，B分别在自己MMAD之后release；多两枚局部M_MTE1事件，无新增cross flags。
- 沿用完整A1、原B1/L0A/B/C分配；host Plan/workspace、整个Vector body与 `0d4bd04` 逐字一致。partial仍逐Nt，不引入worker sparse partial或输入预打包GM区。

## 模型

`python3 tools/validate_tt_contiguous.py` exit0：

- 440实际paired producer：两batch、M/N/K尾、全负、worker/M边界余单tile/idle worker、A1刷新和释放、逐C及padding、ring guards、所有events/credits最终归零；独立枚举paired组数检查实际A2 Load次数，B读数/MMAD数量保持。
- 再440个同样实际源码执行，将MMAD及M-pipe SetFlag排队，等待对应event或M_FIX才执行。MMAD callback读取活的A2/B2/C存储，不提前复制值，因此提前覆盖operand会改变C并失败；检查两个MMAD对A2的最后使用。ND2NZ依旧延迟，L1→L0和Fixpipe同步；不是完整NPU pipeline emulator。
- 原default false的420producer、160矩形与65536位模式回归通过；fake host production/TUNING各6912/720/144通过。host本次逐字未动，因此不重建公开tiler去重复同一容量证明。
- 旧Vector本次逐字未动；其父已经正式通过。CPU小整数不是BF16硬件舍入模型。

## 来源和成本

[Stream-K论文](https://arxiv.org/abs/2301.03598) 和 [CUTLASS工作调度源码](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/gemm/kernel/sm90_tile_scheduler_stream_k.hpp) 支持连续工作区间的原设计；当前以完整K tile为最小任务，不实现论文K拆分。本次A2复用来自本题物理缓冲/生命周期分析，不把GPU性能外推到NPU。

代理计数会减少A2转换，但B仍逐Nt读/转换、MMAD和C输出数不减；B1预读从同Nt两K变为两个Nt同K，可能改变等待成本，新增局部event也有成本。没有性能倍数预测。

## 正式验证

分支 `experiment/tt-fullm-npair`，kernel SHA `a7555e313a0bf6bfe34bca301b8769f28c6b127ed85a859292a883a1db33fcc1`，280265字节。
模型日志 `/private/tmp/bmmms-tt-fullm-npair-cpu.log`。独立官方模板 `/private/tmp/bmmms-judge-tt-fullm-npair/project` 仅kernel替换，dry-run需核对同SHA。
代码 `124dc31` 已commit/push，dry-run仅kernel/SHA一致；正式活动任务 [6abe223b694b590c3cd8474e](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abe223b694b590c3cd8474e) 已创建。正式终态 **Pass：CANN编译成功、15/15、precision_ratio全1**。
耗时 `[2.07,4.54,4.28,5.46,5.36,10.36,10.19,60.83,83.67,97.80,88.19,96.38,15.67,13.04,9.65]` μs。第8点父59.66→60.83μs，无收益；无actual shape/plan/SoC/profile或重复对照，不归因未改路径，也不能据此证明A2转置不是瓶颈。
没有活动任务；归档在本机Git忽略 `artifacts/tt-fullm-npair/`，不替换父版本。不继续N pair相近微调。下一研究B1单个两K面板stage，在相同L1/L0/GM预算内减半ND2NZ提交；区别旧hierarchical四B1/paired-N设计，先核对NZ stage切片和最后MTE1读取后的释放/预读。
