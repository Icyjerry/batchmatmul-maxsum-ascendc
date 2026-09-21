# 上板验证单：dual 消费侧流水

## 获取与构建

- 分支：`experiment/dual-consumer-pipeline`。
- 原版：固定 tag `user-best-20260921`，SHA256 `e512c0d5d21ff4f065cabcd16278e097a2678f327334b85156939b35fc8f4cdc`。
- 候选 kernel SHA256：`07993447be9814aa7d502e9ddd51a9099bcea5c963f4be7a5e09b15e798cf5c4`。
- 目标：CANN 9.0.0，A2/A3 分开验证；精确型号、核数、驱动、编译命令必须记录。

用已有服务器 harness 在独立构建目录生成以下四组，不修改 main/CMake/run.sh/golden/正式测试。

| 组 | 源码与宏 | 用途 |
|---|---|---|
| U | user-best-20260921 原件 | 用户现有最优 |
| P0 | 当前源码，`-DBMMMS_DUAL_PIPELINE=0` | 验证提取 helper 未引入退化 |
| P1 | 当前源码，`-DBMMMS_DUAL_PIPELINE=1` | 仅 UB 预取 |
| P2 | 当前源码，`-DBMMMS_DUAL_PIPELINE=2` | 预取 + 提前 release/启动握手，实验默认 |

以 verbose 构建日志确认宏真正传到 ASC 编译器；可以尝试 CMake ASC flags，但不要假定选项一定生效。保持 BMMMS_TUNING 未定义、全部 BMMMS_PROBE_* 为 0。先确认 CANN 9.0.0 的 TQue 深度 2、CrossCoreSetFlag PIPE_MTE2 和双主模式 IterateAll 的头文件/编译行为。新调用点提前了 AIV wrapper 握手，尤其需要检查其内部 flag 9 无额外完成依赖。

## 精度与同步门槛

1. 四组均运行正式 15 case，使用原精度判定；FP16/BF16、FF/FT/TF/TT、全负、混合值和重复执行。没有正式用例时明确标记未完成，不能用固定 run.sh smoke 代替。
2. 记录每个 case 的实际入口和 plan：dual/baseM/baseN/window/nSplit/kSplit/cubeBlocks/workers。只把确实命中 dual=1/2 且 kSplit=1 的 case 算入候选路径。
3. 补充 M=17/33/65/129/513 的尾块，覆盖第二个 AIV 零有效行；N=31/63/65/127/129/257/511/513/1025，覆盖多个 tile、短尾窗、非对齐读取；K=128/512/2048。选择实际进入目标路径的合法组合，避免误把小形状专用路径当作目标覆盖。
4. 覆盖每个 worker 的总窗口数为 1、2、3、更多以及跨 task 的槽位复用。若生产 plan 无法命中某分支，可在独立诊断构建使用已有 Tune 接口强制 dual 1/2、window 1/2/4，明确标注为诊断，不计入生产性能。
5. 给每次执行设置服务器现有超时机制；遇到挂起、精度失败或 runtime 报错先保存 case、完整日志和宏，不继续计时或提交榜单。

## 性能对照

- 对用户截图五个 shape 及实际 15 case 测量；shape 次序为 (B,M,N,K)。必须补全 dtype/layout 后再比较。
- 各组预热至少 50 次，测量 200 次，U/P0/P1/P2 轮换顺序至少 5 轮。报告设备稳定态 median/p95、跨轮波动；首次分配和 host 总耗时单列。
- P0 对 U 应无超出噪声的退化；否则先研究抽取 helper 导致的编译变化，不归因于流水。
- P1 对 P0、P2 对 P1 分开分析。保留退化结果，不只报告最快一次。
- msprof 看 Task Duration、AIV MTE2 与 Vector 时间/重叠、Cube 等待与 FIX、AIC MTE2 及带宽。AIC MTE2 占比与 AIV 消费端搬运不是同一瓶颈。
- 若仅某一 plan 有收益，回传数据后再制定启用条件。未经实测不合并 main，不移动用户最优 tag。

## 本地预检

`python3 tools/validate_dual_pipeline.py`

这是 CPU 地址/指令顺序/抽象协议模型，不是 Ascend 编译或 NPU 性能测试。

回传字段：commit、kernel SHA、SoC/CANN/driver、完整编译命令与宏、case shape/dtype/layout、实际 plan、最大绝对/相对误差、重复一致性、四组 latency、msprof 与失败日志位置。大型原始日志不进 Git。
