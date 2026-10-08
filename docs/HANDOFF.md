# C9 persistent lane Max — CPU verified, formal gate next

- 当前分支experiment/c9-stream-max，kernel371179B/SHA8c23062f0f03f17cbd92f9813092f2f6d40fb876f4e77fdf68acac0f2f411aa8，父a2e6763。C9默认false模板接入分片内64lane持久Max/末尾一次horizontal；原Cube body/Plan/GM/ring/partial/finalizer逐字不变，旧failed C8/C1/C10未带入。
- actual CPU production&TUNING各2592plan/6命中，1452actual AIV+父版+FinalizeRows，9fault controls全拒绝；精确20核横向APIs768->96。初次Nmask控制逃逸已加强UBpadding poison/跨任务M变化/两任务正负fixture，重跑通过。source Cube字节不变不等于执行了nativeCube，fake tiler/软件FIFO/syntheticcompleteK伙伴局限保留。
- 隔离protected7/dryrun只kernel371179B/8c23062f通过。实现ec40e0e已推送，唯一正式任务 **6ac7e2f8694b590c3c2010c5** 已创建；下一条动作仅查同ID至terminal。Pass15且C9<=57.375us才复测；否则无明确收益完整恢复a2e6763。不做原样小收益repeat/近邻lane/PK/tile扫描。
- CANN9/15精度/耗时PENDING，当前唯一活动任务为上述ID。详细 [C9_STREAM_MAX](C9_STREAM_MAX.md)，raw忽略artifacts/c9-stream-max/{cpu.log,cpu-initial-fault-miss.log}。main/历史标签不动，整体目标未完成。
- C8 balanced-tail archived940ec4e/native6ac7d7afPass15但56.78明显回退；C6无TPipe/fullK frame已做，不重复；tiny transpose/storage/Ktree/staticFT/literal已失败，不复活。

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
