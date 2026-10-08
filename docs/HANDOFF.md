# Current passed experimental baseline: C10 balanced M shards

- Branch experiment/c10-balanced-m-shards, implementationa2e6763, kernel368782B/SHA16b51684cc8628121d7e359c89561c248d04b449b6ecb449f0b4f2da2ffa3a94. Parentaf886e1/C8 phased-A retained.
- Native6ac7b3c8694b590c3c0218c4 terminalPass15/allprecision1, C10=91.53 vs prior96.98-100.24: single local improvement, not stable/causal/large overall breakthrough. Full15 including adverseC2 in [C10_BALANCED_M_SHARDS](C10_BALANCED_M_SHARDS.md). Total457.04/latestTmean51.45446223, not live rank.
- Keep forward experimental baseline; main/tags untouched. No live tasks, no unchanged confirmation or nearby partition scans. Complete-N maxima/oldPlan/GM/Vector arithmetic preserved.
- CPU13Cube/96ownership-store+actualFinalizeRows/production&TUNING192host9hits/sixcontrols pass. Fake tiler/synthetic maxima/native queue limits explicit; native route/SoC/profile remain unknown.
- NEXT independent hypothesis: when whole owned M fits one L0C, remove the second M microtile's duplicate B input. At supplied4096/1280/1152/20cores, max208rows: fullM208/N128/K64 predicts L1A479232+doubleB32768+aq1024=513024, L0A53248/B32768/C106496. Original arena has space. Same200C/3600MMAD as current two-M-microtile/N256, expectedBreads half, A2reads double, totalL0operand reads slightly lower. Must execute actual resource/address/C/halfM104rowAIV stores/GMprefix/finalizer models first; NOT implemented or submitted. This removes repeated B input through whole-M ownership, no neighboring partition scan/newGM allocation.

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
- 当前实现a2e6763，任务记录17e4eec已push。每次记录uniqueID/终态、更新本文件/PERF_LOG，push当前分支。
- CPU/native/profile分开报告；正式case命中、SoC/profile未知时不能从耗时反推。原始logs/JSON放忽略artifacts目录700/file600。
- 最新用户Tbest=[1.18,1.54,2.13,2.37,3.57,6.38,6.37,13.88,48.30,64.85,67.87,80.65,7.31,7.59,7.84]μs；100/(1+log1.5(t/T))逐点平均，不代表实时排名，不拼接不同job最小值。
