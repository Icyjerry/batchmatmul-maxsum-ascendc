# 紧凑 NZ 环形输出与 MaxSim 消费

分支 `experiment/nz-ring-max`，从正式 15/15 通过的手写 Split-K 父版派生。目标是减少大 TT 完整 K 路径的 Fixpipe NZ→ND 转换，不改变矩阵乘、N 分片、窗口、两级归约顺序及 GM ring 容量。

## 实现与依据

- 只在 B=1、TX1/TX2=true、M/N/K≥512、现有 dual=1 且 kSplit=1 时设置 NZ 标记。其它路线保留父路径。
- C 类型和 host tiler 保留 GM ND；自定义 DataCopyOut 回调负责实际输出布局，以 `Fixpipe<float,float,CFG_NZ>` 写入既有环形槽。每个 N tile 的偏移为 `curN*baseN*ceil(rows/16)*16`，dstStride 为 `ceil(rows/16)*16*16*4/32` 个 32B 单位。
- AIV 从每个 16 列 NZ slab 读取各自负责的行，压紧到 UB；屏蔽无效 N lane 为负无穷，树形 Max 合并 slab，最后做 16 lane 行 Max。后续 partial 和 Sum(M) 复用父版。
- 不能仅调用 `IterateAll(...,0,true)` 并假设多 tile 自动连续追加。开源 scheduler 明确将顺序写各 tile 送到同一 gm 起点；此实现的回调显式补充 curN 偏移。

源码依据为官方开源 [ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv)，本地参考 commit `c7dfa2d901a314e1ae69e9cef850057593f2a58b`：`matmul_call_back.h`、`matmul_utils.h`、`copy_cube_out_fixpipe.h`、`scheduler_base.h`。该版本不等于本地已安装的 CANN 9.0.0 header；精确 API 可用性须由正式编译证明。

## 验证

`python3 tools/validate_nz_ring.py`：host 路由及既有 ring 容量检查通过；抽取实际回调的 90 组 tile/window/单位检查通过；1,344 组 NZ 行半块、M/N 尾块、全负和污染 padding 地址模型通过。

`validate_manual_splitk.py` 48 组模型、`validate_direct_batch.py` 1,458 组模型通过。CPU 模型不验证真实 Fixpipe、回调同步、Matmul 内部 L0C 布局或设备性能。

首版 `9c7a006` 同时把库 C 类型/tiler 改为 GM NZ，[提交 6abca137694b590c3c249f19](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abca137694b590c3c249f19) 编译通过，但第 8 点新 BF16 TT NZ kernel 在设备 4 上发生 507015 Runtime Error；前 7 点 Pass、后 7 点 Skipped。平台没有给出底层异常地址。原始 query 日志在 `/private/tmp/nz-ring-query.log`，不入 Git。

下一修正版恢复库 C/tiler 为父版 ND，仅输出回调写 NZ，以排除新增的库 NZ 调度/原始奇数 M/N 约束。此为待检验的隔离假设，尚不能宣称它是已定位的错误原因。该修正版正式精度和 latency：PENDING。精确 SoC、实际隐藏 shape/plan、完整 msprof 及重复 A/B：PENDING。
