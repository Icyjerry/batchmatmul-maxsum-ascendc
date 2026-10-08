# C8 balanced tail frame — CPU validated, native gate next

- 当前分支 `experiment/c8-balanced-tail-frame`。候选 kernel：372771 字节，SHA256 `aa2aabc1ab1cea9270173966aa93748762e3ce0514383b81512be4fa1d784bec`；父版本为正式 Pass15 的 `a2e6763`。
- 实现了完整 C8 调度改动：M16 主块分片、缓存匹配的 N 尾块、分散 M 尾块、共享 Cube/AIV/B 预取任务描述、精确分片写回。原 A1 面板/三阶段发布、双 B/C/ring、GM arena、最终归约保留。
- 简化原审计方案：A1 NZ 子视图 `a1[tile.row*kp]` 调用原 ManualTransposeFullM；没有改 Load3D 参数或 helper。两个 uint64 的尾块 owner 是 launch metadata，非 GM 表。其他 TT 模板默认关闭新算法，但增加了默认零值 16B 参数，原有 TT 入口 ABI 的变化是待正式 gate 检查的风险。
- CPU 通过：生产/TUNING 各 3024 host plan /4 命中；8..32 核共 2393 任务与独立 Python 枚举一致；8 个真实 Cube producer（含精确 K1032 正负输入）；42 个真实异步 AIV；10 个故障对照拒绝。整数模型、假 tiler、合成跨核伙伴不能证明 CANN/BF16/性能。
- 已完成隔离 protected7 /只 kernel dry-run，尚无提交 ID。下一步 commit/push 后创建 ONE 正式任务，立即记录 ID，然后仅查询这个 ID 到终态。通过 15 点且 C8 <=37.111 μs（比近期保留版最低43.66少15%）才复测，否则不原样重复、不扫附近 BM/BN/PK。
- C1 literal 已归档 `2e10a23`，正式 Pass15 但 C1=1.93 无收益；失败 C10 fullM/late-credit/directA2 未带入。无其他活动任务，main/历史标签不动。详情 [C8_BALANCED_TAIL_FRAME](C8_BALANCED_TAIL_FRAME.md)。

## 先读与规则

- 算子语义、限制、workspace背景：[PROBLEM](PROBLEM.md)。原验证约定：[VALIDATION_REQUEST_v1](VALIDATION_REQUEST_v1.md)，持续正式结果：[PERF_LOG](PERF_LOG.md)。
- 用户目标仍是显著冲榜优化，不退回正确性基线，不用 Web。目标 CANN9/A2或A3，真实核数/容量查询，不能固定20核。
- 只 kernel 算法；不改 main/CMake/run/golden/正式测试/依赖；不新增GM，不修改输入/越界y，不交换MaxN与SumM，不跨batch。不移 main/历史标签，不改写push历史。
- 对 CLI 提交和私有 GitHub repo 的授权持续有效；不读取、输出或入Git凭据。

## 保留版本与已结束实验

- 当前实验父 af886e1：kernel365948B/SHA b87ec006，正式6ac7a921694b590c3cf97c01 Pass15，C8=44.09（单次 modest local gain）。保留 C13 resident frame（7492776），正式12.62/13.19；main/历史标签未推广。
- 用户要求一次原样最佳提交6ac77103694b590c3ccaa29e已完成Pass15，没有待复测请求。较早5次重复也全部完成。
- FF B_PACKAGE192：experiment/c10-ff-b-packages/3a0e9c1，实现fd23d39，任务6ac7aefd694b590c3cfe44d9 Pass15/C10=97.06在旧96.98–100.24范围内，无明确收益，已全部移出当前kernel。不扫描附近B包。
- C8 full-input单B包任务6ac77690694b590c3ccea247 Pass15但54.17回退，已归档；C6纯Vector24.24回退；C4Cube7.81回退；C11 exact TT gate87.16无明确收益。都不原样重交或邻近扫参。
- 历史实验/完整旧入口见 [late archive](HANDOFF_HISTORY_20261008_LATE.md)、[earlier archive](HANDOFF_HISTORY_20261008.md)。历史PENDING/Running/分支名称不是当前状态。

## CLI 与 Git 交接

- 题目6a9aa054bf41025d6014f3ef。CLI `/private/tmp/cannjudge_cli.py`，查询 `/private/tmp/query_bmmms_submission.py ID`；同一live ID轮询至终态，等待超时不可重交。
- CLI消失时公开源码可由忽略artifacts/tooling/cannjudge-submit恢复；受保护七文件从1734f16恢复，候选kernel隔离提交，dry-run核对SHA/只kernel。
- 当前候选实现和uniqueID每次分别commit/push。每次记录终态、更新本文件/PERF_LOG，push当前分支。
- CPU/native/profile分开报告；正式case命中、SoC/profile未知时不能从耗时反推。原始logs/JSON放忽略artifacts目录700/file600。
- 最新用户Tbest=[1.18,1.54,2.13,2.37,3.57,6.38,6.37,13.88,48.30,64.85,67.87,80.65,7.31,7.59,7.84]μs；100/(1+log1.5(t/T))逐点平均，不代表实时排名，不拼接不同job最小值。
