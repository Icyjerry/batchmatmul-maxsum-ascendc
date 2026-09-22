# 性能结构集中修复 · 2026-09-22

分支 `experiment/performance-structure-fixes`，实现 `a3c1f7d`，父 `3ca0d7c`。
kernel SHA256：`1e92ea2c6a15db6869df08429f3f468fb74b7fb0ed09d6a7cc02f1ff71bbc6a3`。

## 审查四项的处理结果

| 问题 | 已落实的修复 | 验证边界 |
|---|---|---|
| 连续A切片被拆为8次加载、无收益常驻 | TX1完整连续切片合并LoadData；驻留要求每个N shard至少有两个N组且容量可行 | 原反例LoadData 8→1；单N组不再启用驻留；不是8倍耗时收益 |
| 显式参数被profile或fallback覆盖 | 顺序统一为自动规则→profile→显式pins；候选不允许改变已pin的M/N；统一出口拒绝不兼容的tile/window/ns，含早退Vector路径；split-K禁止截断M/N | 四布局、单字段/组合pins、无效pin和完整K约束通过 |
| 新producer默认覆盖已有路径 | `BMMMS_CUBE_PANEL`默认改为0；1/2/3保留为显式实验。默认预处理移除manual AIC/AIV中的panel调用分支 | 不再以容量可行为由自动认定新路径更快；原库路径与既有修复仍保留 |
| C0启动被C1的Fixpipe阻挡 | 每块C只在第一次MMAD覆写前获取自己的FIX_M事件；后续K累加不重复获取 | 逐元素C一致、事件收支平衡；C0开始时C1信用尚未消费。真实异步重叠待测 |

同时合并 `RunPanelCube` 的单级/两级K重复主循环；两种配置共用地址计算、队列释放、MMAD和C获取逻辑，B在首次实际使用时出队。L1 K和队列深度仍按原配置不同，没有新增缓冲、GM通路或算子接口。kernel从4044行变为4029行；行数变化不是性能结果。

默认模式不是已测最优结论。它撤销未经设备证据的自动替换，避免继续将独立实验叠成提交默认。显式panel1/2/3仍沿用既有tile/partition以做受控对照；不宣称已建立跨producer的最优成本模型。历史shape规则仍需目标机器重新测量，不在本地臆造新胜出阈值。

## CPU与静态验证

- `python3 tools/validate_cube_panel.py`：456常规执行、584两级K执行及两次针对性完整切片执行通过。实际函数抽取、四布局、K/M/N尾、负值、完整C、读字节/L0搬运/MMAD计数、队列和C事件获取顺序；输入为可精确表示的小整数。
- `python3 tools/audit_plan_precedence.py`：源码默认P0与显式P2/P3，自动profile被正确覆盖；单N组不驻留；无效pins报错；AIC/AIV预处理确认P0不存在panel调用分支。
- `python3 tools/validate_host_plan.py`：六种宏组合各production/TUNING主网格76,424配置及资源边界通过。P3驻留选择由9,964降至6,026；P3/H1两级K选择8,410次，统计含额外边界检查。
- `python3 tools/validate_host_cache.py`：11调参字段、重建、context隔离、scratch用途转换、释放和4类失败通过。切换到不支持ns的Vector场景前显式清除ns pin，符合新的严格语义。
- `python3 tools/validate_nsplit_work.py` 与 `python3 tools/validate_splitk_coverage.py`：既有N工作量、全负分片、K拆分和UB模型通过。修复旧脚本过宽抽取范围导致的CPU编译错误（误包含需要Schedule的PanelL1Capacity）；检查主体和预期值没有放宽。
- `git diff --check`通过。main.asc、CMakeLists.txt、run.sh与用户最佳tag逐字节一致；正式测试/golden/依赖未改。

**上述均不是CANN编译或NPU精度/性能验证。CANN9、A2/A3、正式15点、latency/msprof全部PENDING。** 用户要求暂缓云端执行，未连接服务器。

## 设备接手的下一条动作

1. 检出本分支，按实际SHA构建默认P0和显式P2/P3；P2/P3各构建 `BMMMS_L1_K_PANELS=0/1`。原审查版本 `3ca0d7c` 作为同机父对照。固定其它宏，probe全0。
2. 所有构建先跑正式精度；专项四布局×FP16/BF16覆盖 `(16,128,256,128)`、`(1,64,8192,128)`、`(1,1536,1536,1536)`、`(2,33,97,136)`、`(1,33,97,344)` 以及父验证单的长K/尾块。记录实际plan，禁止把没有命中panel的case当作panel结果。
3. 显式pin测试的预期是 `(1,64,8192,128)` 接受 `bm32/bn64/ns2/window1`；不兼容pins现在抛错。设备harness应清空不适用的pins，不再依赖静默覆盖。
4. 精度通过后按父验证单做交替计时/msprof。特别核对FIX_M获取推迟后的硬件事件依赖、连续LoadData、B队列首次使用时出队。记录SHA/SoC/CANN/宏/plan/误差/median/p95；没有实测前不合并main kernel。
