# 覆盖度与死代码报告

目标：找出默认（比赛）构建下**不可达**的策略分支与冗余，并给出可复现的瘦身结果。

方法：静态枚举 `Launch` dispatch 与 `MakePlan` 的 flag 赋值；在启用 `BMMMS_TUNING` 的
构建上用 `BMMMS_DUMP_PLAN=1` 对覆盖各 regime 的 51 个 shape 实测采样；从设备 ELF
（`.aicore_binary`）用 `nm -S` 统计每个 kernel 的编译体积。

## 1. 可达性结论

`MakePlan` 中 `dual` 的非 tuning 赋值只有 `=1`（默认）与 `=2`（若干 shape 规则）；
`dual=3..12` 全部只在 `#ifdef BMMMS_TUNING` 内由 `Tune().dual` 设置。实测 51 个 shape
完全吻合：只出现 `dual ∈ {0,1,2}`；`dual=0` 只出现在 `m==n==1 / small / micro` 的提前
return 路径，因此双 master 的 fallback 序列（`fused`/`fused_wide`）永不到达。

## 2. 默认构建不可达的 kernel（死代码）

| kernel | 触发条件（仅 tuning） | 编译字节 |
|---|---|---:|
| `bmmms_fused_wide` | `dual==0` | 303,536 |
| `bmmms_fused` | `dual==0` | 303,448 |
| `bmmms_manual` | `dual∈{3,4,6,7}` | 134,472 |
| `bmmms_gemv_vector` | `dual∈{9,11}` | 64,272 |
| `bmmms_micro_batch` | `dual==8` | 43,800 |
| `bmmms_col_sumfirst` | `dual==12` | 13,768 |
| `bmmms_dot_split` | `dual==10` | 13,736 |
| `bmmms_dot_grouped` | `dual==5` | 11,184 |
| 合计 | | **888,216** |

辅助类 `MaxSim`(51-235)、`WideMaxSim`(238-429) 仅被 `fused`/`fused_wide` 使用。

同时不可达的运行时 flag 分支：`earlySum`（12 处 + `FinalizeEarly`）与 `tree`（8 处）——
二者默认恒为 0，只有 `Tune().early/tree` 能改。

## 3. 默认构建存活的策略

| kernel | 触发 | 设备字节 |
|---|---|---:|
| `bmmms_dual` | `dual==1` | 152,896 |
| `bmmms_dual_mdl` | `dual==2` | 176,824 |
| `bmmms_dual_split` | `dual≥1` 且 `kSplit>1` | 103,240 |
| `bmmms_small_gemm_grouped` | micro, B>1 | 59,568 |
| `bmmms_small_gemm` / `_contiguous` | micro, B=1 | 50,392 / 26,048 |
| `bmmms_small` | `p.small` | 39,792 |
| `bmmms_dot` | `M=N=1` | 6,392 |

## 4. 测试覆盖缺口（重要）

原 21 case 只覆盖 `dot / small / micro / dual(1)`；**没有**覆盖存活的：

- `bmmms_dual_mdl`（`dual==2`，大 shape 主路径）
- `bmmms_dual_split`（`kSplit>1`，K≥2048 / 大 batch）

建议在外部 harness 增加以下 case（tuple 为 B,M,N,K；四种 layout 都要），已本地验证
全部通过：

| id | (B,M,N,K) | dtype | 覆盖 |
|---|---|---|---|
| 21–24 | (1,1024,2048,128) | fp16 × FF/FT/TF/TT | dual==2 |
| 25–26 | (2,257,513,2048) | fp16 × FF/TT | dual==2 |
| 27 | (1,1024,2048,2048) | fp16 FF | dual==2 |
| 28 | (2,1024,2048,2048) | bf16 FT | dual==2 |
| 29–32 | (1,17,31,8192) | fp16 × FF/FT/TF/TT | kSplit=16 → dual_split |
| 33 | (2,17,31,4096) | bf16 FF | kSplit=16 → dual_split |
| 34 | (1,64,64,4096) | fp16 FF | dual(1) 大 K 边界 |
| 35 | (64,128,128,128) | fp16 FF | B=64 边界 |

本地 36 case（原 21 + 上述 15）在 910B3 全通过：`PASS=36 FAIL=0`。

## 5. 瘦身结果

把第 2 节的死 kernel/类与其 `Launch` 分支用 `#ifdef BMMMS_TUNING` 包住（tuning 构建仍
保留全部候选）：

- 设备 ELF：`1,689,520 -> 714,736` 字节，**−58%**。
- 精度：36/36 通过；`-DBMMMS_TUNING` 构建仍可编译。
- 性能：5 个代表 shape A/B 为噪声级中性（±6%），未观察到 icache 加速。
  本项收益是**二进制体积与不可达代码的消除**，不是速度。

## 6. 复现

```sh
# 默认构建（无死代码）
cmake .. && make -j4
objcopy --dump-section .aicore_binary=aicore.bin batch_matmul_max_sum_custom
# tuning 构建（全部候选）
cmake -DCMAKE_ASC_FLAGS=-DBMMMS_TUNING .. && make -j4
# 打印实际 plan
BMMMS_DUMP_PLAN=1 ./batch_matmul_max_sum_custom B M N K 1 tx1 tx2
```
