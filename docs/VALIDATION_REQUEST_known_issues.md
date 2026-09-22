# 集中修复版本：后续设备验证入口

用户当前暂缓云端执行；本单供恢复时直接使用，不要求设备Agent重新设计实现。

分支 `experiment/known-issue-closure`；kernel SHA256 `d218864289599e2b39ef09d83cfdde68988908bf9400fa42b5bc9b03031783bb`。

## 版本与记录

- 用户最佳 `user-best-20260921`；父候选 `677d882`；当前集中修复版本。先保持BALANCED_NSPLIT/ADAPTIVE_SPLITK宏一致比较修复，再单独比较性能候选开关。
- 精确SoC/CANN9版本、kernel SHA、宏、实际AIC/AIV/UB、可用核数、入口、baseM/N/K、window、ns/ks、workspace、误差和device latency必须绑定保存。
- 不修改正式测试/输入/golden/容差；生产构建关闭probe，不定义TUNING。

## 必须专门覆盖的变化

1. `known_issues_cases.csv` 全部151shape×2dtype×4layout，包含负值和K非16对齐。正式15点单列，任何缺失/失败不记为通过。
2. manual 3/14对齐/尾块路径：systemBytes应为0；首次冷启动及连续复用都检查guard区、输出和性能。普通Matmul仍使用查询到的systemBytes。
3. 同context/stream复用：generic→manual→short-dot→generic、generic→GEMV→generic、大小shape反复切换；检查数据不依赖历史workspace内容、无提前释放。单一shape稳定态不应多出同步/memset。
4. TUNING诊断单独跑：同shape先ns3再ns1再ns3，核对实际plan和时间；再改变其它Tune字段。该测试不能与production性能混报。
5. earlySum=1的调参诊断：B64、小可用核数1/2/4，输出预填哨兵，检查所有batch唯一且完整；比较earlySum=0。另跑dual10的B64/M=N1/K512/availableCoreNum1，确认parts不为0。
6. `release_kernel_resources`在所属context、stream销毁前调用；长时间多stream生命周期验证。main不允许改动的正式评测按其生命周期执行，不能声称框架已帮忙调用release。
7. 需要比较的R1–R18性能策略见KNOWN_ISSUES。已有Tune可固定family/tile/window/cores/ns，若想绕过ClassifyCase，显式设置Tune.dual。缓存修复后仍须核对最终plan；不以参数赋值作为命中证据。

先确认精度与资源安全，再同capture交替测候选/父版，预热、median/p95、msprof及host初始化时间分别记录。不要用首次分配成本代替kernel Task Duration，也不要用当前模型宣称已经提速。
