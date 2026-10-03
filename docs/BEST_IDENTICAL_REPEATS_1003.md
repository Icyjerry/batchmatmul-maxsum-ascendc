# 当前最优组合新增两次原样复测 · 2026-10-03

用户新增要求“再交两次”。对象延续上一组：最优组合1734f16，kernel SHA256 `a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742` /354602bytes，源码和参数完全不变。

分支experiment/best-identical-repeats-1003从cf52f5e创建。独立模板/private/tmp/bmmms-tt-manual-frame-official/project与工作区kernel SHA一致；dry-run仅kernel，SHA一致。其它七源码逐字保持1734f16；只改交接文档，不改main/标签。

上一组任务6abfc955694b590c3ca51a64 /6abfca4d694b590c3ca5b6a8已经15/15 Pass，详见BEST_IDENTICAL_REPEATS_1002。本轮独立新增恰好两次，不复用旧ID冒充新提交。

任务1 `6ac08cd7694b590c3cf7a7d8` 已15/15 Pass，precision_ratio全1；任务2 `6ac08d9c694b590c3cf806ec` 已创建，终态PENDING。下一只查询任务2同ID至终态；本轮两任务已创建，不创建第三次。先等任务1结束后POST任务2，成功，没有429。原日志忽略artifacts/best-identical-repeats-1003/，目录700/文件600。

保存全部15点status/precision/time；同源码样本不能证明同机受控A/B或新优化收益，接口没有实际SoC/shape/plan/profile。平均分只按用户T换算，不当榜单排名证据。整体冲榜目标尚未完成。

## 任务1正式结果

任务 `6ac08cd7694b590c3cf7a7d8` Pass，CANN编译成功、15/15、precision_ratio全1。μs：`[1.90,2.65,3.22,3.94,5.30,9.85,7.85,46.51,67.35,97.58,87.35,96.12,15.13,10.81,8.96]`。源码SHA保持。
