# 小TF矩阵完整输入驻留 · 2026-10-01

## Evidence → Diagnosis

通过父 `fd72a34` 的kernel与 `e1b3634` 逐字一致，正式任务 `6abe3059694b590c3cdf6c87` 15/15，C7 9.68/C8 49.38/C9 67.48μs。没有actual shape/plan/SoC/profile；C7的B16..31/M32..63/N128..255/K256..504/FP16/TF是队友历史桶，不能声称已获得真实shape。

此桶当前使用dual3/14的direct-batch手写K循环。A/B输入字节相同，但K分块导致多次GM→L1 ND2NZ，B的L1→L0B也需要多条Load2D；完整A/B能放入L1，完整A能放入L0A。假设把循环从K改为N，使A2在整个batch保持，减少输入转换与小Load2D的发起成本。旧direct-batch输出已经存在，本次不把免SyncAll收益重复归因。

另已排除之前的“Vector直接准备共享L1”方向：[CANN9 DataCopyPad](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0265.html)明确A2/A3的VECIN/VECOUT→TSCM实际经过GM中转。TSCM不是该设备上的直接共享UB/L1通路，不新增此GM输入通路。

## 实现

分支 `experiment/c7-full-inputs`，kernel SHA `e8a1512e88e3cc71069d501b9cb934917ac2717cde772f83a9f6fad0daf7f6bb`，303787bytes。

- 新 `RunSmallFullInputsCube`：每batch一次完整A和一次完整B的ND2NZ；A1/B1尾K补零，DMA补M/N的D尾。
- A2通过一次原生矩形transpose Load3D接收完整M×KP，在N循环中驻留。B2一个不超过64KiB的完整K×N片段，由非transpose Load3D直接从完整B1取得。
- 每个N片段完成KP的FP32 MMAD，写到原L0C的独立N slab；全部N完成以后原Fixpipe一次输出完整C至原双GM ring。两份C0、原ready0/1/free4/5、local last-reader事件保留。不同batch仍一一配对。
- 复用原 `bmmms_manual<...,DIRECT_BATCH=true>` Vector源码，按实际N取Max、实际M求Sum、唯一AIV只写该batch一个FP32；第二AIV没有有效行但仍返还credit。沒有原子/新GM/新Schedule字段。
- 新dual34只替换上述历史桶中已经选出一个M tile/一个N tile、K不拆分的dual3/14。查询真实L1/L0A/L0B/L0C/UB，完整输入/完整A/B片段/双C0/两份完整C UB必须满足容量；显式TUNING pins不进入。只改变Schedule.dual，原grid/partial/ring/workspace保持，其余kernel（包括C8/C9）逐字保持。

例如48×192×384，旧源码BK64：A/B ND2NZ共12次、A2 Load6次、MMAD6次。新源码B片段80列：ND2NZ共2次、A2 Load1次、MMAD3次。L1输入184320B、L0A36864B、L0B61440B、双L0C73728B；输入/输出字节不减少。调用数不是耗时或加速比，单B2串行加载可能抵消收益。

## 依据

- [Goto / van de Geijn论文](https://www.cs.utexas.edu/~flame/pubs/GotoTOMS_revision.pdf)：准备/布局转换开销需要由后续计算和复用摊薄。本候选按实际片上容量改变准备粒度和循环次序，不移用CPU硬件参数或论文性能数字。
- [CANN9 Load3D](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00170.html)：A2/A3支持half的A1→A2及B1→B2；B2输出ZN，A2可ZZ；全矩阵transpose只用于half/A2。B2不设置transpose。
- 官方公开 `ascendc-api-adv` 固定8.3 revision `c7dfa2d901a314e1ae69e9cef850057593f2a58b`：`impl/matmul/stage/split/load_to_l0b/load_to_l0b_loadInstr.h`通过K/N起点与extension从L1作非transpose矩形Load3D；此源码不是本机安装CANN9 header。当前使用已在项目使用的typed LoadData3DParamsV2，设备编译仍待正式结果。

## CPU与公开源码验证

```sh
python3 tools/validate_c7_full_inputs.py
python3 tools/validate_c7_full_inputs_public_tiler.py --source /private/tmp/ascendc-api-adv-review
```

- 86实际producer立即执行，86延迟live MMAD：物理NZ/ZZ/ZN、全负、M/N/K尾、多个batch、worker跨batch、闲worker、逐C及补零、输入不可变、ring guards、精确读量/加载量/MMAD次数、事件收支通过。
- 删除last-reader wait负控制被拒绝。模型MTE2延迟、MTE1/Fixpipe同步，没有模拟真实Load3D配置寄存器时序或FP16舍入。
- 2592实际原消费helper模型：单AIV持有全部有效M行、另一个零行，延迟DMA、两个subcore任意先后、credit返还后破坏性ring覆盖、N尾/负值Max/Sum通过。原直接输出代码未改，本模型不等于完整两个引擎的NPU执行。
- fake tiler production/TUNING各3456控制配置、432新选择；固定公开8.3真实tiler同网格各3456/432。测试可用核心1/8/20/32，物理核心至少8，实际内存缩小回退及pins，完整Schedule除dual及grid/workspace均相同。
- 第一版fixture把Parent/Candidate不同Plan类型放进同一auto声明引发CPU编译错误；分开声明后通过。第二次fixture将物理AIV设为2却提供B31，触发父已有ceil(B/8)组数检查；改为物理至少8核、可用核数仍包含1，保留真实低可用核与idle覆盖，没有修改kernel来绕过错误。
- 撤销三个新增区域和模板分支后，整个kernel恢复父 `fd72a34` 逐字一致。只修改kernel、独立模型和交接文档；main/CMake/run/golden/正式测试/依赖没有修改。

日志 `/private/tmp/bmmms-c7-full-inputs-cpu.log`、`/private/tmp/bmmms-c7-full-inputs-public.log`，另存本机Git忽略 `artifacts/c7-full-inputs/`。CPU/公开8.3不代替CANN9/native时序/设备精度或耗时。

## Validation Request

独立官方模板 `/private/tmp/bmmms-c7-full-inputs-official/project`，仅kernel替换；dry-run仅kernel/SHA一致。代码 `2dc7f30` 已commit/push，正式任务 **`6abe5f1e694b590c3cf8ca02`** 已创建，CANN9/NPU终态PENDING。查询同一ID至终态，勿重复提交。比较父C7 9.68/C8 49.38/C9 67.48μs，全部15点必须通过；无收益则归档恢复父，不扫描附近N片段参数。actual shape/plan/SoC/profile与重复A/B仍缺失，不据单次时间断言路径命中或稳定幅度。
