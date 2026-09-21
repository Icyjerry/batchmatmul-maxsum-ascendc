# 设备验证单：覆盖修复与自适应 Split-K

分支：`experiment/coverage-splitk`，基于用户固定最优 tag，未混入消费流水实验。
Kernel SHA256：`be1d551930b1a951ec765fe0212180d67a6627cebb0aaf9202004198c3c4014a`。

## 构建对照

| 组 | 内容 |
|---|---|
| U | user-best-20260921 原样源码 |
| F | c4e536a：UB 预算和三个末级输出遍历修复，固定 4 份策略 |
| A0 | 当前源码，BMMMS_ADAPTIVE_SPLITK=0；应与 F 路由一致 |
| A1 | 当前源码，BMMMS_ADAPTIVE_SPLITK=1，实验默认 |

保存真实编译命令、SHA、精确 SoC、CANN 9.0.0/driver、物理 AIC/AIV/UB 及 availableCoreNum；不要假定 20 核。BMMMS_TUNING 不定义、PROBE 宏全 0，使用已有服务器 harness，不修改正式测试或容差。

## 正确性与覆盖

1. 首先编译并跑正式 15 点；未取得正式用例要明确标为 PENDING。
2. 使用 `coverage_cases.csv` 的 shape 覆盖边界，每条 FP16/BF16、FF/FT/TF/TT；全负、混合值、重复执行。记录入口、baseM/baseN/baseK/window/nSplit/kSplit/kChunk/cubeBlocks/workers、workspace 与误差。
3. UB 回归 `(1,112,192,8192)`、`(1,111,191,8192)`：检查 A0/A1 没进入超预算 Split-K，而是由现有通用分块承接。CPU 模型不能替代这一步。原版若在该硬件超预算，记录失败并跳过其性能，不运行到超时后继续猜结果。
4. 输出遗漏/重复：B=64 的 GEMV、Split-K 和普通 dual case，将 availableCoreNum 设为 1/2/4 和物理上限。输出预填哨兵检查是否全部覆盖，并比较完整 golden。哨兵仅检查遗漏；重复 writer 需设备调试工具或执行跟踪核对，单靠精度通过不能证明唯一 writer。
5. K=4104 等非 32 倍数长 K 和 B=1/8/12/20/64，用 A0/A1 比较精度；不同拆分改变 FP32 累加分组，不能因调度模型通过就省略实际精度。
6. A1 选择 1 份时走完整 K 的 bmmms_dual，应保持整块 M/N、nSplit=1。确认 B=20/20 Cube 的示例；其他设备按实际 plan 判断。
7. 对 B*M*K/B*N*K 达 2^26 的大 case 单独记录内存与超时；不要把未完成的大 shape 写成已覆盖。

## 性能与合并条件

- U/F/A0/A1 用同一输入、同一设备。先检查 F vs U 的修复影响，再检查 A0 vs F，最后 A1 vs A0。
- 每组预热至少 50 次、200 次设备计时，轮换顺序至少 5 轮；报告 median/p95 与跨轮波动。首次分配、host planner 计时另列。
- 核查预测的拆分数、任务波次及 C partial/ring 读写量是否实际减少；msprof 分开记录 AIC/AIV MTE2、Cube/Vector、FIX、Task Duration 和带宽单位。
- 只有 A1 有可重复收益且正式精度全部通过，才考虑启用或按测得的 shape/设备条件筛选；不能凭 CPU 代理成本合并 main。
- 这套对照不启用 dual-consumer-pipeline。两条实验分别验证后才能组合，组合版本还需重新验证同步与精度。

## 本地预检

```sh
python3 tools/validate_splitk_coverage.py
python3 tools/validate_finalizer_coverage.py
```

前者抽取真实 classifier、selector 和 InitBuffer 表达式，后者抽取真实输出循环头。它们不执行完整 Ascend kernel、真实 Matmul tiler 或设备同步。
