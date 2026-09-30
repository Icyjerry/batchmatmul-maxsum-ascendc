# 完整 K 的 B 驻留与按列分组

## Evidence → Diagnosis

父版本 `18a93f3`，通过kernel代码 `55225cc`，第4点5.66μs，整体重大提升未达成。
现有大TT路径围绕每个M/N C块完成整个K；窗口会话结束后内部End清理输入状态。
当A完整K驻留、B分K块时，不能把B跨多个M块的复用算作已有保证。
此前配对M共享每个短B K面板未见收益，不能继续同一路径调参数。

本次改变驻留对象和任务顺序：B的一个N块**完整K**放入L1，N在外、M在内；
GM ND2NZ从许多短K拷贝改为一块完整K的拷贝，并跨一个worker的多个M块复用。
它可能增加A重读，不能仅根据B加载次数推断总流量或性能。

## 来源

- 官方 [ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv) 固定revision `c7dfa2d901a314e1ae69e9cef850057593f2a58b` / `8.3.T9.0.B066`，`copy_cube_in_mdl_fullload.h::LoadData` 在首个iteration CopyTileToCube，后续从CubeInBuffer取已有L1块。只借鉴full-load生命周期，未使用或定制其内部模块。它不是CANN9实际安装header。
- [CANN9 Load2D](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_00169.html) 确认A2/A3 FP16/BF16、A1→A2/B1→B2、512byte分形、repeat最大255。新路径只用现有项目已有typed API。

## 实现

- 新family `dual=29`：`RunColumnBCube` / `bmmms_column_b`。不改旧kernel实现。
- 只在已有dual1、完整K、B1、BF16 TT、大M/N、baseM/N均128时考虑；按实际L1/L0A/L0B/L0C/UB、AIC/AIV核数检查，不固定20核。K尾块支持8但非16对齐。
- L1：完整B `baseN*round16(K)*2` + 双A队列 `4*baseM*128`。L0A/B双缓冲、双L0C沿用基本API协议。B全K不适合容量时保留旧计划。
- workers=N分组×M分组；每个worker固定N分片和M余数类，按 `batch → N tile → M tile → K panel` 计算。
- host先最小化最忙worker的C tile数，再在相同tile数中减少完整B加载数；至少两个M块可复用才选择。
- 20核、1536³示例选择6个N组×3个M组=18workers，每个最多8个C块，2次完整B拷贝。仅CPU示例，不是正式隐藏shape或实际plan证明。
- AIV为本worker的多个M块持有UB行Max，沿N更新；完整K先完成再Max，N分片最后仍由原FinalizeRows合并并Sum(M)。存储位置保持 `[B,nSplit,paddedM]`。
- 沿用partial和双槽GM ring，不增加输入GM预处理。workspace库前缀保留，不改变当前缓存生命周期。
- 显式TUNING几何/调度pins保留，不被此自动路由覆盖。

## CPU与静态验证

`python3 tools/validate_column_b.py`：

- 296个抽取真实Cube producer和两名AIV consumer执行。NZ/ZZ/ZN实际块、完整C和padding逐元素对独立dense点积oracle；正负混合、全负、M/N/K尾块、多batch、多个M/N组、K1032/1536/1544。
- 每个有效行的N分片Max及最终Sum一致；所有partial位置唯一writer、尾部guard保持、输入未改；队列生命周期、event收支、ring slot地址匹配。
- B GM读数 `B*N*K*Mgroups`、拷贝次数 `B*Ntiles*Mgroups`；A读数 `B*M*K*Ntiles`，明确暴露A重读代价。
- production/TUNING各480个host配置，分别384个选择；真实容量不足、dtype/layout/batch不符合及显式pins回退。
- int16小整数、同步指令模型，不模拟BF16舍入、异步调度或缓存性能；不可当CANN/NPU精度结果。

CANN编译、正式15点精度、NPU性能、精确SoC/plan/profile：提交前PENDING。

## 下一条验证动作

下载独立正式模板，仅替换kernel，dry-run绑定SHA后CLI提交一次结构候选，观察同一ID到终态。
若无收益保留此分支和结果，恢复父通过版；不继续相近N/M分组或K深度提交。
独立设备可对比父kernel和本候选，记录实际路由、A/B GM读取、MTE2/Scalar/Cube利用率、median/p95和误差；A2/A3分别记录。
