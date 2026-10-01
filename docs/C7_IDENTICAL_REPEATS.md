# C7 原样两次复测（2026-10-02）

用户要求“一模一样再交两次”。本次采用最近通过版本 c17077f，kernel SHA `45234d7945b6013cc75d2e6c3092c911c9c8ecd5618b82a7c51fd7d9084e0c61`，329378 bytes；当前宽N实验编译失败保留 experiment/c14-manual-frame。

独立官方模板kernel与Git源码逐字一致，其它7个源文件与父版本逐字一致，CLI dry-run只上传kernel。源码、模板、所有参数保持原样，不修改kernel或测试。首轮终态后才提交第二轮，每个任务查询同ID至终态。与已有两次C7结果比较，不能把旧结果冒充本次新提交。

- 本次复测1：`6abea238694b590c3c1d35d8`，PENDING。
- 本次复测2：尚未提交。

下一动作：查询复测1，终态后提交原样第二次；汇总四次同SHA结果的中位数/min/max，不把波动归因优化。无真实shape/plan/SoC/profile，非受控同机A/B。
