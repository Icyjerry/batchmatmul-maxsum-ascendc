# 库内建 NZ 输出 + NZ Vector Max

## 假设与前提

从正式15/15通过但无明显提速的 `experiment/cube-stream-sessions` / `08559b7` 派生，不替换最快通过版。新候选沿用该独立 AIC MatmulImpl，改用 GM NZ C 与顺序 GetTensorC，AIV 直接归约 NZ，尝试减少 Fixpipe NZ→ND 转换；**没有 DataCopyOut callback，没有回调 GM 指针或用户标量传递**。此前三次 callback 的 Runtime Error 不作为该路径的正确性证据。

依据官方 [ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv) `c7dfa2d901a314e1ae69e9cef850057593f2a58b`（8.3.T9.0.B066，非CANN9精确header）：`copy_cube_out_fixpipe.h::CopyOutNZ2NZ<true>` 将 stride 设为 `ceil(validM/16)*16*16*sizeof(float)/32`；`copy_cube_out_utils.h` 按 C format=NZ 选 CFG_NZ，并将 nSize 对齐到16。库内建输出代替了之前自己的 Fixpipe callback；实际可用性以正式 CANN9 编译/运行为准。

## 实现

新 dual=27、`bmmms_dual<T,true,true,STREAM=true,NZ=true>`。生产者对完整Nshard建立一次库会话，逐 C tile 顺序写已有双槽 GM ring，M 物理跨度 ceil(validM/16)*16。两 AIV 分别以二维 DMA 读16列 slab中自己负责的有效行，UB布局为 `[N groups, validRows,16]`，无需转为ND。

N尾列在最后slab置 -inf；跨N groups做树形逐lane Max，最后一次16-lane WholeReduceMax，然后更新任务的行最大值。K全部累加后才做Max；最终Sum和batch一一配对仍用原finalizer。每AIV读取有效行，不读取补齐M行。ring容量、任务、workers、片上预算沿用stream父版；无新GM通路。原ND模板仍保留、默认NZ=false。

host同一准入范围重新查询C format=NZ的实际tiler；拒绝或资源不足回退通过的默认路径，不强行覆写tiling。具体cache/step/性能需要真实plan/profile，不能由CPU模型推出。

## 本地验证

`python3 tools/validate_cube_stream.py`：production/TUNING各96配置，包含pins和新tiler拒绝回退；实际producer、DMA、tail-mask、tree-Max代码分别在ND/NZ mock运行各432配置，比较点积→Max→Sum独立oracle。新增128×128tile、完整/零有效AIV行、非对齐M/N、跨batch和全负；NZ无效列特意写巨大正值，验证不能污染最大值。模型验证stride/槽位/结果，不仿真CANN内部布局或事件时序。

## 正式结果：通过，无整体收益

`fcbf29b` / kernel SHA `895be634247274f702cfbebaba858c8087a309c0554cd44977c178ced77d9225`，259946字节。[提交 6abcb535694b590c3c317c3e](https://cannjudge.cn/public/op_challenge_shanghe_prelim/batchmatmulmaxsum/submission/6abcb535694b590c3c317c3e) **CANN编译通过，15/15 Pass**，各precision_ratio=1。本次未出现callback方案的Runtime Error。

时间 `[2.32,4.09,4.19,8.34,5.50,10.67,10.20,66.40,84.14,98.19,89.04,97.60,16.59,13.78,9.62]` µs。相对stream ND父版第8点67.89→66.40，第11点88.96→89.04；相对较快手写Split-K版第8点67.80→66.40，第11点88.16→89.04。单次第8点微降不能证明稳定收益，其余点有波动；整体没有大幅提升，不替换较快通过版。

通过case msg为空，精确SoC、shape、实际kernel/plan、msprof和重复A/B未取得，不能从15/15推断新NZ路由实际命中或Fixpipe成本下降。额外设备覆盖仍PENDING。原始JSON位于本机Git忽略 `artifacts/builtin-nz-stream/6abcb535694b590c3c317c3e.json`。该布局对照保存独立分支，不继续相近输出参数变体；下一步审查输入搬运和L1/L0分块的成本。

验证输入：BF16/FP16 TT `(1,1025,1537,1032)`、`(1,1536,1536,1536)`、`(1,1537,3073,3072)`，全负/正负/重复执行。确认dual=27和actualkernel，记录具体SoC、CANN、tile/step/cache、最大误差、median/p95和Fixpipe/MTE/Vector/Cube profile。
