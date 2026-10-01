# 当前通过版原样复测两次

用户再次要求一模一样提交两次，以观察测评耗时波动。这次对象是当前通过版 `1734f16`，与较早 `03c3996` 的两次复测独立。

- kernel SHA256：`a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742`；354602 bytes。
- 首次正式任务：`6abeb39e694b590c3c22e5d7`，15/15 Pass，precision_ratio 全1。
- 独立工程：`/private/tmp/bmmms-tt-manual-frame-official/project`。8个工程源码逐字等于 `1734f16`；CLI仅上传kernel。CLI生成的 `.cannjudge-project.json` 为本机配置，不属于工程源码或提交文件。
- 不修改算法、测试或构建；不增加CPU测试。两次按前一任务终态后再提交，取得ID立即保存，查询同一ID至终态。
- 复测1：`6abeceed694b590c3c2bc7a5`，Pass，15/15，precision_ratio 全1。
- 复测2：`6abecfc5694b590c3c2c1347`，已提交，终态 PENDING。首次POST HTTP429拒绝、无ID；等待45秒后重试成功生成此唯一第二个任务。

API没有实际SoC/shape/plan/profiling。这是同源码重复测量，不是受控同机A/B；三次范围只能描述这三个样本，不能给出总体波动界。

复测1耗时（μs）：`[1.93,2.62,3.08,4.12,5.26,9.76,8.11,46.51,67.88,97.92,87.73,96.34,15.56,10.88,9.05]`。原JSON忽略保存 `artifacts/current-identical-repeats/repeat1.json`。
