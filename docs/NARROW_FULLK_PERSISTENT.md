# 窄 N 的完整 K 驻留流水

## Evidence → Diagnosis

正式任务 `6abe05cf694b590c3cc88e53` 的第13点16.48μs，接口best_time5.21μs；这些不是同设备重复A/B。队友探针把此点约束为B1/M8192/N64..127/K128..248/FP16/FF，仍是历史区间而非真实隐藏shape证明。

通过TT种子 `a05035e` 的窄N路径：完整B L0驻留只在dual3且M/N/K16对齐时开启；dual14尾块路径按每个M任务重复读取B，且没有跨M的worker累加。本次不是重复此前“大TT矩阵的按列完整B L1驻留”实验。

## 改动

仅kernel.asc算法，基于已正式通过TT种子。新dual32在父计划完成后选择：B1、FP16 FF、M>=2048、16<=N<=128、32<=K<=256/K8、BM128、一个N tile/一个N shard/K不分片；实际容量全部满足且没有显式调参pin。其它路线保留。

- 完整B先以ND2NZ放入B1；N/K尾部补零，以对齐kp作NZ pitch，完整B一次装入L0B，跨M任务复用。
- 两份完整K A1 queue预取当前/后续worker任务；一份完整A2，一次矩形非transpose Load3D，然后一次完整K FP32 MMAD。
- 双完整C仍Fixpipe到原双GM ring。沿用原ManualCopyC、两AIV credit和有效N尾部归约。
- 复用原RESIDENT_B Vector分支：每个AIV跨M按lane累计，最后写一个8-float partial slot；原FinalizeEarly汇总，不使用原子操作。
- 父schedule仅dual/earlySum变化，grid、partial/ring位置、workspace大小和其它字段保持。无新GM通路，不修改main/CMake/golden/测试/依赖。

## 依据与边界

[Goto / van de Geijn, High-Performance Implementation of the Level-3 BLAS](https://www.cs.utexas.edu/~flame/pubs/GotoTOMS2.pdf) 的Gepp把B准备放在M块循环外，摊薄准备开销。这里只借用复用顺序：B足够小，直接保留在每核L0B，不能移用CPU论文的硬件性能数字。
[CANN9 Load3D文档](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00170.html) 支持A2/A3的A1→A2 half/bfloat16类型，A2为ZZ/NZ；本次仅FF、FP16、非transpose矩形。

每核L1 = 2*BM*kp*2 + BN*kp*2；L0A=BM*kp*2；L0B=BN*kp*2；L0C=2*BM*BN*4。BM128/BN128/kp256时L0A/B各64KiB、L0C128KiB，host核对实际容量。尾部只补输入乘积零，Max始终只归约实际N，不让零替代全负最大值。

## 本地验证

`python3 tools/validate_narrow_fullk.py`

- 2654真实producer/helper源码执行，MTE2 DMA延迟、物理NZ/ZZ/ZN、逐C有效/补零元素、输入不变、ring guards、queue/event收支、单次完整K MMAD计数和每worker一次B输入通过。
- M尾、N16尾、K8非16尾、全负、1/3/8核以及M8192/20核覆盖；独立Max(N)→按worker/lane Sum与直接golden相同。小整数数学不是FP16舍入或硬件同步模拟。
- 原Vector body与通过TT父版逐字一致；本次没有声称实际Vector全体在新producer模型中协同执行，硬件时序仍需正式结果。
- fake tiler production/TUNING各5376 host配置、各504新路线选择，实际容量fallback/pins和其余finished plan逐字保持通过。

`python3 tools/validate_narrow_fullk_public_tiler.py --source /private/tmp/ascendc-api-adv-review`

- 固定官方公开8.3.T9.0.B066 tiler，production/TUNING同样各5376/504通过；不是安装CANN9编译或实际NPU证据。
- 源码SHA `4bf730de204af997b8eca185c2c2ffe72144874f29b4d59e10d33c81dc68672d`，CPU日志 `/private/tmp/bmmms-narrow-fullk-cpu.log`、公开tiler `/private/tmp/bmmms-narrow-fullk-public.log`。

## 正式验证

独立官方模板 `/private/tmp/bmmms-judge-narrow-fullk/project`，仅kernel替换。CANN9编译/15点精度/latency PENDING；一次结构候选提交并记录ID，同ID追踪至终态。重大提升未达成，不将调用数下降作为加速预测。
