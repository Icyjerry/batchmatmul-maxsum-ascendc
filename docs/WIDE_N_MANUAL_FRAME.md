# 宽 N 的手动缓冲、B 预取与批量分片归并

## Evidence → Diagnosis

父 `124658d` 是当前已通过组合，C7正式两次8.00/7.88 μs。原宽N BF16/FT已dual21/完整A驻L0A，不能再把A驻留称新优化。源码 `bmmms_manual<...,FULL_A=true>` 的BK=K，每Nt才调用ManualCopyK；`s.k>bk`和`k0+2*bk<s.k`均不成立，所以两份B1 queue没有跨Nt预取。C0是一个两Nt块缓冲，配对起点等待其全部Fixpipe释放；Vector末级SyncAll后block0串行ns-1次Max/PipeBarrier。

本次假设：让两份现有B1跨Nt预取，两个C0 tile独立归还，减少TPipe/queue/参数开销，并批量归并N分片。不是重复此前ragged wide-N的布局覆盖候选；不改N分片数、M/BN/分区/任务或GM。

## 算子改动

kernel新增205行、三个区域：32byte紧凑参数/独立混合入口（及两个小helper）、资源选择、原partial后的launch override。删除三个区域逐字恢复父全部kernel。

只替换已经选出的B1/BF16/FT/dual21、M16..128/N>=4096/K32..256且M/N/K16对齐、单Mtile/Ksplit/window1、workers=nSplit的原路径。全部显式TUNING pins回退；实际AIC/AIV与L1/L0A/L0B/L0C/UB再次查询，GM capacity/原plan也核对；其它布局、tails、C7/C8/C9/所有旧路径不改。

- A完整ND2NZ、一次装L0A；仍不改变每个点积的FP32完整K累加。
- 两个B1 panel预读首两个Nt；消费一个panel的最后MTE1读取后才能写下一个Nt+2。单B2保留，下一次LoadB2之前等待上一MMAD完成，避免live operand覆盖。
- 现有一段双Nt的C0拆为两个不重叠区域，各自FIX_M保护；每两Nt写回原一个宽度2BN的GM窗口。原ready0/free4、两个AIV、partial前缀和ring地址/容量完全保留，无新GM输入/metadata/同步通路。
- AIV两份原尺寸C缓冲，MTE2读完原GM即归还信用，V_MTE2/MTE2_V保护每个UB槽；有效N lane fold→分片行Max。零行伴随核仍参与协议和全AIV barrier，不提前离开。
- SyncAll后block0复用已消费C的UB区域读取原N分片行Max；连续两半按repeat批量Max，奇数尾折入第0组。16分片、MP64的原15次Max变为4次；最后仅对有效M求和，M>64拆成两次合法WholeReduceSum后Add，写唯一4byte y。

源码调用数/缓冲依赖不是性能结果。真实隐藏shape/route/SoC/profile未知，“C14”仅历史桶名称。

## 文档与 API 依据

- 队友manual LocalTensor/显式事件已用于当前通过的C7及NT小tile；本次沿用同类硬件初始化与PIPE_ALL结束。
- [CANN9.0 SyncAll静态正文](https://www.hiascend.com/doc_center/source/zh/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0204.html)经HTTP取得，文档表列A2/A3硬同步支持、无GM/UB workspace的`SyncAll()`原型、仅AIV的true语义，以及直调batchmode约束。公开网页与Tavily Extract只返回导航壳，不作为正文证据；静态页本机原件/解码文本 `/private/tmp/bmmms-sync-src-0`、`/private/tmp/bmmms-syncall-900.txt`。
- 文档不是安装CANN9 header。未取得实际SyncAll内部header，无TPipe的native行为仍需正式编译/运行；不移用9.1的可定制pipe配置，不复制PTO实现或增加依赖。保留原Mix(1,2)/schedmode1/SyncAll<true>，Cross flags仍0/4。
- 既有 [FlashAttention-2](https://arxiv.org/abs/2307.08691) 减少非矩阵乘工作和通信的结论支持优化准备、流水及末级归约的方向；本实现是针对现有Ascend路径的推导，不移用GPU接口或论文速度数字。

## 本地验证

```sh
python3 tools/validate_wide_n_manual_frame.py
```

- 434实际producer：物理NZ/ZZ/ZN、手动内存范围；MTE2延迟、MTE1 live读取、MMAD live读取、Fixpipe live读取各自排队。每Nt完整C与独立K点积核对；两个B1独立生命周期、配对/奇数Nt、M/N对齐尾、混合/全负、actual8192/16和4112/20代理、输入不可变、scratch/ring guards、事件/信用收支。
- 四Cube负控制：删B1最后读、B2最后读、C0最后读等待或B input-ready，均被拒绝。
- 729实际AIV entry配置：三个独立引擎及三优先顺序、返还GM信用即破坏ring、逐元素UB generation、真实多线程全AIV barrier、零行伴随核、唯一partial writer和y、有效N/M、非2幂分片、C区域barrier后复用、output/partial/UB guards。
- 八Vector负控制：删C reader/C ready/partial ready/barrier/final-copy ready/PIPE_ALL，放宽N尾mask，或最后GM读前返还信用；均被拒绝。
- production/TUNING各4800真实host配置/600选择，全部资源/shape/launch/GM不足回退、显式pins、不更改原plan。

模型使用整数数值，不模拟BF16编码/舍入、硬件Load2D寄存器时序或FP32溢出；Cube伴随消费者、Vector伴随Cube和native跨核协议仍是抽象，不能替代CANN/NPU。首次Vector模型编译缺未实例化Cube helper API声明，补fixture声明后通过；N-tail负控制最初漏检，发现网格没触及65..128的单tile尾，增加80/112/592代理后检出，没有改kernel/正式测试使错误通过。最后host std::min显式int64匹配已有平台代码习惯；当前SHA对应全套重跑。

## 正式请求

独立官方原模板只换kernel，其它7个源文件逐字不变；dry-run SHA核对，commit/push后提交一次、立刻保存ID，只查同任务至终态。CANN9编译/NPU精度/性能 **PENDING**。
对照最近通过版 C14 13.15/13.26 μs以及更早相同宽N代码12.61–13.38的正式波动样本；必须15精度全部通过并保留C7约7.9–8.0。实际同机/shape/plan/profile缺失，不将不相关路径浮动归因本次；无收益归档恢复通过父，不能扫描附近tile/分片参数。

正式任务 **`6abea08e694b590c3c1c90f5`** 已创建，代码 `d57fddf` 已commit/push，SHA保持。下一 `python3 /private/tmp/query_bmmms_submission.py 6abea08e694b590c3c1c90f5` 只查同一ID至终态，不能超时重交。CANN9/NPU精度/性能PENDING。

## 2026-10-02 · 设备编译错误修复

首任务 `6abea08e694b590c3c1c90f5` 已Compile Error。唯一native error：设备入口第2765行std::min解析到host-only标准库函数，不允许从aicore调用。普通C++ CPU模型未模拟host/device注解，所以原CPU通过不能证明Ascend编译成功。只将本行拆为非负remaining和三元min，不更改shape/分区/流水/算术/其它源码；host资源选择中的std::min保留。失败原JSON忽略 `artifacts/wide-n-manual-frame/compile-error.json`。

修复源码SHA `b0e0b66495df9606156f73f1d4a1399801ab18f203ff0f9458a7051caca4150f`，340070bytes。实际CPU全套重跑：434producer、四Cube负控制、729AIV、八Vector负控制、production/TUNING各4800host/600选中通过，三个区域去除仍逐字恢复父；整数/抽象协议和native注解限制不变。原日志忽略 `artifacts/wide-n-manual-frame/fixed-cpu.log`。

C7新两次复测均Pass，结合四次C14范围12.72–13.26μs、中位13.04、极差/中位数4.1%；更早宽N同代码范围12.61–13.38仍保留。新候选必须15/15且耗时超过波动范围才称明显收益。没有实际shape/plan/SoC/profile，改动与桶对应未知。独立模板只换kernel，dry-run确认新SHA；下一commit/push后仅提交修复版一次，记录ID并查询终态。新的CANN9/NPU精度/性能PENDING，先前错误任务不是PENDING且不得重新查询/重交它。

修复候选正式任务 **`6abea479694b590c3c1e1f2d`** 已创建，代码 `8e6959b` 已push，SHA b0e0b664…保持。下一只查询同ID至终态，观察超时不得重交；首任务Compile Error已终态。

## 2026-10-02 · 修复候选正式15/15，C14 10.93μs

正式任务 `6abea479694b590c3c1e1f2d` **Pass，CANN编译成功、15/15、precision_ratio全1**。代码 `8e6959b`，kernel SHA `b0e0b66495df9606156f73f1d4a1399801ab18f203ff0f9458a7051caca4150f`，340070bytes。μs：

```text
[1.91, 2.68, 3.23, 3.98, 5.2, 9.92, 7.78, 49.67, 67.24, 97.67, 87.67, 96.19, 15.12, 10.93, 9.09]
```

C14 10.93，相比最新父四次12.72–13.26、中位13.04，低于最快父约14.1%，低于中位约16.2%；大于父样本极差/中位数4.1%，可保留单次结构收益。无actualshape/plan/SoC/profile或同机交错A/B，不能证明因果稳定百分比、路径命中或计算榜单分。C7 7.78在旧候选四次7.67–8.04范围内；它和其它路线源码未改，不归因其波动。没有扩大对齐准入、不改变N分片/GM/完整K→MaxN→SumM、main/标签保持。

正式编译与15点精度表明此次无TPL入口可用于这些正式样本，不代表所有形状/SoC或者完整合法空间通过；整数模型和native证据仍分开。原始JSON Git忽略 `artifacts/wide-n-manual-frame/official-fixed.json`。下一原样确认一次该较大收益，commit/push后创建并立即保存ID，只查同ID至终态，不能继续附近参数扫描。

原样确认任务 **`6abea54c694b590c3c1e7459`** 已创建，kernel/template SHA保持，下一只查询同ID至终态，不重交。
