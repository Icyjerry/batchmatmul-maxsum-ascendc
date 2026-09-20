# Agent 工作约定

## 先读

`docs/HANDOFF.md` 是最新接手入口；再读 `docs/PROBLEM.md`、`docs/VALIDATION_REQUEST_v1.md` 和 `docs/PERF_LOG.md`。

## 用户目标与范围

- 用户要求以队友 Cube/Vector 版本追求比赛性能，已有实现继续迭代；不要重新退回从零开发正确性基线。
- 目标环境 CANN 9.0.0，设备可能是 A2 或 A3，不能假设固定型号或固定核数。
- 算法/比赛实现只修改 `kernel.asc`。不修改既有 main、CMake、run.sh、golden、正式测试或依赖来让错误通过。
- 用户已要求 GitHub 和 Git 交接维护，允许更新交接文档、独立 CPU 模型与 Git 配置文件。
- 当前使用队友版本内部分配的 workspace；不要擅自增加新的 GM 通路或将其视作正式赛规许可。规则历史见 PROBLEM。
- 不修改输入、不越界写 y，不交换 Max(N) 和 Sum(M)，不跨 batch 配对。

## Karpathy Coding Guidelines

1. Think before coding：写清假设和可验证目标；发现歧义说明，不编造 API 或运行结果。
2. Simplicity first：只实现当前假设需要的内容，不为凑行数堆分支。
3. Surgical changes：匹配现有风格，不重构无关代码；保留队友版本的有效优化。
4. Goal-driven execution：每轮按 Evidence → Diagnosis → Minimal Fix → Validation Request 推进。

## 验证与交接

- CPU 模型、静态检查、CANN 编译、NPU 精度、NPU 性能必须分开报告。
- 上板仍未验证时明确写 PENDING。源码注释中的历史耗时不是本轮实测。
- 关键 Ascend API 以 CANN 9.0.0 实际 header、example 或设备编译结果为准。
- 不并入大批未经设备验证的优化。每次性能修改对应一个假设和可复现对照。
- 服务器验证按 docs 中的 VALIDATION_REQUEST 交给 OpenCode 或其他设备 Agent；不要期待对方重新设计算法。
- 保存 case 的 shape/layout/dtype、kernel SHA、精确 SoC、CANN 版本、实际 plan、误差、latency 和 profiling。
- 原始大型日志、输入数据、构建产物和任何凭据不要入 Git；结果摘要进 PERF_LOG，可选原始资料保存到受权限控制的位置。

## Git 工作方式

- 开始工作先查看 `git status`、近期日志与 HANDOFF，保留别人的未提交改动。
- 优化在 `experiment/<简短名字>` 分支进行；验证充分后再合并 main。
- `vector-v0.2`、`teammate-opt4`、`experiment-v1` 为历史快照，不移动标签，不改写已推送历史。
- 一次 commit 对应一个明确假设/修复/结果记录；push 当前分支，使其他 Agent 能接替。
- 暂停或额度不足前更新 HANDOFF 的已完成、未完成、下一条可执行动作及失败日志位置，然后 commit/push。
- GitHub 认证失败时请求用户在本机完成登录，不收集或把 token 写入聊天/仓库。
