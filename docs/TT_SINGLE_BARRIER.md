# TT 末级归约：一次全核同步与 UB 复用

## Evidence → Diagnosis

父 `cf16501` 已正式两次15/15通过，保留C7约7.8μs、C14 10.93/10.84μs。TT dual33 的Cube完整A1/B包流水已优化，pairedN/workerMax/NZ曾无收益，不能重复。当前Vector每个Nt写原partial，第一次SyncAll后调用FinalizeFullMTiles：各AIV逐N slab DMA/Max、写M半块标量到同partial头、第二次SyncAll，再block0读取这些标量求和。

本次只研究末级通信和归约调度，不改变Cube/K/N任务、tiling、partial生成/GM布局。依据 [FlashAttention-2原摘要](https://arxiv.org/abs/2307.08691) 减少非矩阵乘工作和不必要中间通信的原则作Ascend专门推导；本轮已重新通过一手arXiv摘要核对，不将GPUwarp/API或速度移用为NPU性能证据。

## 实现

仅kernel新增59行/修改3行，三个新增段与template参数/消费调用接入；逆替换逐字恢复父cf16501。整个Cube producer、MakePlan/grid/任务/GM/跨核flags、旧消费body、C7/C14及fallback保持，算法修改仅kernel。

- 仅原已选dual33（B1/BF16/TT/M,N,K1024..2048）且workspace/实际UB和repeat容许时选择template BATCH_FINAL=true；全部显式TUNING pins保留原路。无新Schedule ABI、GM或kernel输入。
- 保留原第一次SyncAll，所有producer partial DMA完成后原C/M/row UB已无reader。block0将原有死UB从物理0起复用，读所有N分片paddedM行；其余AIV正常退出，不参与第二屏障。
- 沿用通过宽N的WideNMergeRows，按连续两半批量Max，处理奇数split，仍完整K之后Max所有N。first Max若超过255repeat或UB不足保留旧FinalizeFullMTiles，尤其MP2048/Nsplit16的256repeat。
- 按64个有效M分组WholeReduceSum，再对这些group求和。M尾mask不读padding；输出唯一4byte y。使用已有TPipe动态Fence事件避开queue事件槽，PIPE_ALL完成输出；不手动重置TPipe或修改原队列。
- 不再写M chunk标量、不再二次gather和SyncAll。原partial完全只读，GM容量不增加。

BM128/M1537/Ntiles13代理：原25个M chunk各13个N DMA，共325次；新一次bulk DMA。原每chunk12次Max共300次API，新树形Max5次API。新读13*1664*paddedM比旧有效1537行多padding，Vector从多个AIV转为单AIV，串行带宽/计算可能抵消减少的DMA/API/barrier成本。以上只是源码操作数量，不预测NPU收益。

## 本地验证

```sh
python3 tools/validate_tt_batch_finalize.py
```

- 324抽取实际末级helper/同父WideNMergeRows和原消费结束的第一barrier调用：三个延迟队列MTE2/V/MTE3读取live物理UB，真实全部AIV线程barrier，模拟原连续tile任务partial writer并延迟MTE3。有效M包括1025/1055/1087/1537，padding注入正大数；奇数Nsplit3/13、Ns8/16、实际worker1/3/20、正负/全负Max→Sum；局部UB物理范围与byte guard，唯一y、精确4byte、partial完全不可变、最后无pending DMA。
- 六负控制：删除第一次SyncAll、输入DMA ready、输出V ready、最终PIPE_ALL、全部N Max，或把M尾纳入full64，均被模型拒绝。
- production/TUNING各3000实际host控制配置/240选择；plan/GM不动、UB精确一字节容量边界、repeat256排除、shape/layout/dtype/K/显式pins/fallback通过。
- 删除新增helper、guard、launch/template/body接入后，整个kernel逐字等于cf16501，故无须重复更改未涉及的旧CPU验证脚本。

整数CPU不模拟BF16/FP32硬件舍入、TPipe内部allocator/析构和完整Cube/Vector并行；初始consumer reader退休由原SyncAll语义和source位置约束，模型模拟其队列尾部与barrier而非全consumer。新UB别名在native队列退出后是否有效必须正式运行核对。CPU通过不代表CANN编译或速度通过。

## 正式请求

kernel SHA `71ca6095958a372927c27f088bb081c43cff748169ff98e4ef80a2215b4d62c5`，343178bytes。独立原模板仅换kernel/其它7源码逐字父、CLI dry-run只kernel同SHA，日志忽略 `artifacts/tt-single-barrier/cpu.log`（目录700/文件600）。下一commit/push后提交一次，立刻存ID并查询终态；CANN9/NPU精度/性能PENDING。

父最近六次C8为49.14–50.72μs，末两次49.67/49.56μs。无actualshape/plan/SoC/profile，不保证隐藏路线命中；必须15/15且C7/C14保持，大收益原样确认、小于波动差异如实归档、不扫附近分组或tile参数。main/历史标签保持。

正式任务 **`6abea942694b590c3c1ff692`** 已创建，实现 `5c67d94` 已push，kernel/template SHA71ca6095…保持。下一只查询同ID至终态，超时不重交；CANN9/NPU精度/性能PENDING。

## 2026-10-02 · 正式通过，C8 47.24μs，仅单次小幅改善

任务 `6abea942694b590c3c1ff692` **Pass、CANN编译成功、15/15、precision_ratio全1**，实现 `5c67d94` / SHA `71ca6095958a372927c27f088bb081c43cff748169ff98e4ef80a2215b4d62c5`。μs：

```text
[1.94, 2.7, 3.22, 4.01, 5.28, 9.66, 7.85, 47.24, 67.78, 95.19, 87.89, 96.41, 15.14, 10.86, 9.53]
```

C8 47.24；父最近六次50.67/50.72/49.94/49.14/49.67/49.56，范围49.14–50.72、中位49.805。单次比中位低5.15%、比最快低3.87%；父极差/中位数3.17%，候选在父样本区间外，但没有同机A/B或重复候选，不能称大突破或稳定收益。源码有效减barrier/GM中转，native已验证这些正式样本可安全复用死UB，所有形状/TPipe版本/精确SoC仍未验证。C14 10.86与通过宽N的10.93/10.84相近；其它路线未改不归因浮动。

特别保留C2的不利观测：宽N前四次2.42–2.50，宽N两次2.68/2.78，TT本次2.70。其源码路径未改，仍不能把上升简单消除为噪声或精确归因；没有相同设备交错旧/新，整体最优/榜分未证明。不能仅C14变快就断言整体分数必升。

本候选保留独立分支作为后续结构对照，不再原样提交小幅收益、不扫描tile/分组参数，不合main；最近有两次明确结构收益的组合仍是 `experiment/c14-manual-frame` / `cf16501`。原JSON Git忽略 `artifacts/tt-single-barrier/official.json`，没有活动任务。源码/模型/终态已push，整体冲榜目标仍未完成。

下一需优先两个真实剩余风险：TT在RunManualFullMCube里仍以TPipe/A1 TQue/TBuf及动态event初始化大Schedule，Vector仍每tile重复queue/Max init（旧workerMax无收益不能重复）；研究32byte固定局部frame保留已有B包流水、完整K/MMAD及原task/GM，改变物理生命周期/框架开销，与旧frame方案逐字scope/实际live模型核对后才实现。C2需查看当前和队友tiny入口的启动/地址/归约差别，保留当前资源化batch正确处理，不能盲换whole source或把C14优化回退后总耗时直接当榜分。
