# User-requested retained-best repeat running — query same ID

- Current branch experiment/post-c9-work-audit; whole kernel byte-equal **a2e6763** /368782B/SHA16b51684. Retains earlier C8 phased A, C10 balanced ownership, C13 frame. C9 stream implementations removed entirely.
- Latest archive **a1c945d**/implementationaf7fd63, unique6ac7e87d694b590c3c22f9f2 **Pass15/C9=67.96us**, no targetgain; previouslane-Maxarchivea07150f/C9=67.62 also no gain. All models/native JSON retained. 用户最新授权原样最优版一次复测，唯一 **6ac8459c694b590c3c493c00** 已提交；CANN/精度/耗时PENDING。
- User asks ~4h report: modest C10 balanced ownership91.53 vs96.98–100.24 retained; C8 phasedA44.09 vs46.18–46.87 earlier boundary retained. FullM178.32, latecredit92.84, directA2 92.98, literalC1 1.93, C8tail56.78, C9lane67.62/Bstream67.96 no gains/regressions archived. No major leaderboard breakthrough.
- FIRST `python3 /private/tmp/query_bmmms_submission.py 6ac8459c694b590c3c493c00`，只查询同一ID至终态；原样368782B/SHA16b51684，代码对应a2e6763/当前0705902，kernel无改动。用户要求的一次提交已创建，不能再交。
- NEXT [POST_C9_WORK_AUDIT](POST_C9_WORK_AUDIT.md) quantifies scoring gaps using complete retained submission/userleader/latestTbest. Tiny C2/C4/C3/C1/C6 gaps dominate C8 in average-score terms. Inspect actual shared tiny synchronization/conversion/teammate differences and prior literal/static/rawtranspose/Ktree/pureVector failures before a distinct structural candidate. No candidate currently exists. No repeats/nearby scans of archived hypotheses.
- Models/native/profile separate; noWeb/newGM/protected7 edits. Main/tags unchanged, overall goal incomplete.

## 先读与规则

- 算子语义、限制、workspace背景：[PROBLEM](PROBLEM.md)。原验证约定：[VALIDATION_REQUEST_v1](VALIDATION_REQUEST_v1.md)，持续正式结果：[PERF_LOG](PERF_LOG.md)。
- 用户目标仍是显著冲榜优化，不退回正确性基线，不用 Web。目标 CANN9/A2或A3，真实核数/容量查询，不能固定20核。
- 只 kernel 算法；不改 main/CMake/run/golden/正式测试/依赖；不新增GM，不修改输入/越界y，不交换MaxN与SumM，不跨batch。不移 main/历史标签，不改写push历史。
- 对 CLI 提交和私有 GitHub repo 的授权持续有效；不读取、输出或入Git凭据。

## 保留版本与已结束实验

- 较早父 af886e1：kernel365948B/SHA b87ec006，正式6ac7a921694b590c3cf97c01 Pass15，C8=44.09（单次 modest local gain）。保留 C13 resident frame（7492776），正式12.62/13.19；main/历史标签未推广。
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
