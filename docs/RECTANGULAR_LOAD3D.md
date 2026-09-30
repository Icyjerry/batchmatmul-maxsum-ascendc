# 手写 Cube 矩形加载

## Evidence → Diagnosis

父代码 `55225cc`，正式15点通过；结果记录 `909294b`。
非转置 A 和非转置 B 的 L1 NZ → L0 ZZ/ZN 原路径用循环逐分形加载。
本次假设：在不改变数据量、分块、workspace和事件协议的前提下，
1×1 Load3Dv2 一条矩形加载可降低指令发射成本。减少调用数不是实测加速。

## API 与开源依据

- [CANN9 Load3D](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00170.html)：typed `LoadData3DParamsV2<T>` 支持 A2/A3、FP16/BF16、A1→A2/B1→B2；目的布局分别 ZZ/ZN。默认自动设置 FeatureMap。1×1窗口、步长/膨胀1，NC1HWC0正好表示NZ slab。
- [CANN9 Load2D](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00169.html)：矩形 Load2Dv2 不是 A2/A3 可用的替换，不采用。
- 官方 [ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv) 固定 `c7dfa2d901a314e1ae69e9cef850057593f2a58b`，公开版本 `8.3.T9.0.B066`，`impl/matmul/stage/split/load_to_l0a/load_to_l0a_loadInstr.h` 和对应 `load_to_l0b` 使用Load3D进行矩形加载。它不是本机安装的CANN9 header；库内部Pro调用也不作为公开CANN9 Pro API可用性的证据，本次只用已存在的typed V2 API。

## Minimal Fix

`ManualLoadRectangle`描述NZ源的物理row/channel跨度和目标矩形，输出排列由A2/B2决定。
接入 `bmmms_single_tile_direct_batch`、`bmmms_manual`、`bmmms_manual_case12_packed`，共六个加载点。
仅替换TX1=false的A和TX2=false的非resident B；转置输入、resident B、已有tree4加载保留。
resident A 的sourceCols为完整K，kStartPt为k0；非resident A为当前K块。
PAD_MN使用已有round16的rows/count/cols，避免把baseM当成尾块的NZ物理跨度。
case12 B仍由既有ND2NZ搬入，不增加GM预处理或新的workspace。

`BMMMS_RECT_LOAD3D=0`保留原Load2D循环；默认1。
不改host分类/tiling、缓冲容量、队列生命周期、跨核flag、MMAD、Fixpipe和归约。

## Validation

- `python3 tools/validate_rectangular_load.py`：抽取六个真实调用块和真实helper，宏0/1分别执行2888个布局检查；独立dense值oracle逐元素验证NZ→ZZ/ZN，包含非正方形、padding负值、K=8192常驻切片和边界写保护。输入保持不变。
- 同步CPU指令替身不证明硬件Load3D语义、事件流水或性能；int16小整数仅检验布局，不模拟FP16/BF16舍入。
- `python3 tools/validate_tiny_tt_vector.py`：700实际源码执行、production/TUNING各432host尝试（各360选择）、30量化FP64对照通过。该路径未修改。
- [正式提交 6abd38b5694b590c3c7aac99](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abd38b5694b590c3c7aac99)：CANN编译通过，15/15精度通过，各precision_ratio=1；总时长512.56μs，父版511.66μs，第6点不变、第12点95.91→97.74，没有明显收益。未取得实际shape/plan/profile和同机重复对照，不证明六个加载点全部命中。
- 代码 `c4d591b`，SHA `8bf5cf4568efe55df1793a30cef649a4ec29e2849027e29e0aeb93ca0e7ad0ac`；保留失败性能对照，后续恢复父通过版本。整体重大突破未达成。

## Validation Request

CLI下载独立正式模板，仅替换kernel，dry-run核对所有文件，再提交一次结构候选。
保存准确SHA、编译/运行错误、15点精度和耗时；没有shape/plan/profile不宣称具体路径命中。
独立设备入口可编译宏0/1同设备交替A/B；记录SoC、核数、CANN、实际路由、MTE1/Scalar/Cube profile和median/p95。
若无收益则保留此分支和反例，恢复父通过版本，不继续相近参数提交。
