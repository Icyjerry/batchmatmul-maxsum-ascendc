# 队友tiny_dot原版正式对照

## 当前：队友tiny_dot原版直接正式对照

分支 `experiment/teammate-tiny-original`，kernel与用户 `kernel_tiny_dot.asc` **逐字相同**，300625bytes、CRLF SHA `72454276ca665e0dd80d2bea6d972a34270442cad8fd3ccf0bd2a6674d4323e7`。CLI按文本读取转LF，实际提交295170bytes、SHA `6b42fe18e0d5ce1f3312b7f10545ca52c1f61edfb157db927f57e39bdedf7387`；仅换行转换，没有算法/参数/分派修改。
通过组合保留 `experiment/teammate-tiny-dot` / `d5cd4af`；不以原版覆盖该分支。独立官方原模板 `/private/tmp/bmmms-teammate-tiny-original/project`，dry-run仅kernel。下一执行CLI一次 `--no-wait`，立即保存ID，再查同一任务至终态；原版CPU模型未新增，设备编译/精度/性能PENDING。

对照已通过组合任务 `6abe7b90694b590c3c08ed48`，15点μs `[1.98,2.63,3.66,4.13,5.70,10.75,10.25,50.72,68.02,99.81,89.21,97.18,16.30,13.44,9.64]`。只比较正式同一编号；无实际shape/plan/SoC/profile与重复A/B，不推断隐藏路径或稳定速度。

正式任务 **`6abe7f04694b590c3c0ade30`** 已创建。下一 `python3 /private/tmp/query_bmmms_submission.py 6abe7f04694b590c3c0ade30`，只查同一ID到终态，不重复提交。CANN编译/NPU精度/性能PENDING。
