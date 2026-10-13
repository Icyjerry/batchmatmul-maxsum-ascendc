# 当前工作：C4 完整 native 分析，C12 候选已归档

## 当前源码

- 分支 experiment/c6-input-layout-audit。恢复整份 e2f1b63 / 队友 ZIP078635，353179B，七个受保护文件未动。
- C13 fullK（520f27d）和 C12 strided store（b159f99）均未获明显收益，保留历史分支，不并入 main、不提交 OJ、不重复采样。
- ZIP078635 与 DISPATCH 接受源 b8817327 不同，不得把后者正式 Pass15/401.13us成绩借给当前源。

## 已完成的设备证据

- 服务器9382，实际24AIC48AIV，CANN9.0.0/driver26.1.1，logical0→physical14/card7chip0，core_limit20是明确调用者预算。
- 独立 native_oj_like 工具在私有可写 /workspace/bmmms-codex；完整实际storage FP64参考、normalPlan复核、五应用调用/全部默认报告/source-DSO-input-device绑定。原main/CMake/tests/shared_assets未修改。
- C12 BF16TN(1,1280,4096,1536) 原版83.123322us，strided store82.683304us，仅-0.53%；实际写回指令减少2688条仍不提速。详见 C12_STRIDED_PREP_STORE / PERF_LOG，raw artifacts/c12-strided-prep-store。
- C4 BF16TT(4,8,16,128)，实际 Launch先选 SmallVectorK256Rows=8，跳过较晚dual28入口。原版完整精度+五性能输出通过，原normalPlan dual28/workers4/finalBlocks4/cubeBlocks0。
- 五报告 actual纯Vector4、0Cube、符号small_vector_k256<BF16,true,true>，TaskDuration[2.980119,2.940118,3.120125,3.060122,3.360134]us，median3.060122；AIV各核均值五次中位V1.46/MTE20.419028/MTE30.149167/Scalar0.721806us，重叠不可相加。
- C4首次parser因纯Vector的MixBlockDim=NA退出1；修正只读schema后对同一组五报告重解析，完整性通过，保留原错误和全部样本，没有重新跑或挑选数据。

## C4 候选终态及下一条动作

- C4 compact实现7f76eed/c6bde889/353918B，CANN9编译+一次精度+五报告通过，actual true符号确认；所有输出与parent逐位一致，maxabs1.1920929e-7/maxrel1.0804517e-7。五时长3.180127/3.100124/3.080123/3.120125/3.060122，中位3.100124us，比3.060122慢1.31%。已在3b6a05d归档，无OJ/重复/参数扫描；32KiB产品状态不代表加速。
- SSH长连接随后断开，新入口转发报platform authorization denied（跳板认证通过）。已请求新入口，当前无NPU任务；不虚构设备编译失败或将goal标为完成。C4原版全部raw已下载，候选raw仍在remote结果目录，下载PENDING；已读取真实summary并完整记入文档。
- NEXT见C6_INPUT_LAYOUT_AUDIT：恢复访问后先补C4候选raw两个目录，再用冻结baseline DSO读C6 BF16NT(13,23,73,192) normalPlan，复核frame、全FP64golden+一次精度+五default报告。c6.json是源码推导的待核对capture期望。
- C6新raw-row im2col数学模型PASS，但没有生产实现/API/native证据。目标去掉两个连续NT输入ND2NZ，以channel16/filterW12/stride12解释完整K192，query/doc补零右像素108/84；保持原ZZ/ZN、正常C、UnitFlag/Fix/GM/归约。先actual SDK header/瓶颈核实再实现，不能重做旧NZ 1x1矩形Load3D/C13raw-normal。没有新未经编译的kernel分支。

## 工具与交接

- SSH私有配置/private/tmp/bmmms-remote-access/config；旧master23895/exec13910已断开，无凭据入Git。实际状态用ssh -O check检查，需新有效入口。
- native工具/DSO/完整frame/inputs/reports在 /workspace/bmmms-codex/native_oj_like 和inputs；private NumPy2.2.6 Python test-venv/bin/python。
- 真实NPU文件锁及active/pending队列，当前无活动NPU任务。GitHub已授权私有仓库；push当前实验分支，不改标签/main。
- 未验证：当前源正式15点、另一SoC、ZIP与接受源绑定。无新OJ请求。整体冲榜目标未完成。
