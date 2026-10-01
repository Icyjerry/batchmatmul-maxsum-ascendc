# 队友tiny_dot与已通过TT/C9组合

## 来源与范围

用户提供 `2026-10/kernel_tiny_dot.asc`，5455行、CRLF，原始SHA `72454276ca665e0dd80d2bea6d972a34270442cad8fd3ccf0bd2a6674d4323e7`。截图显示队友前几项明显更快，但没有该源码的正式提交ID/SHA，不能把截图作为本候选精度或时间证明。
分支 `experiment/teammate-tiny-dot`；算法以正式15/15通过的 `e1b3634` kernel为父，父SHA `8c03d710d5394a0660e6bedc4c172f7784a1cbe3ef9f1cbc450f231aa1d6a052`，历史C8 49.38/C9 67.48μs。
候选SHA `7d629cfb0bb821fa8be65cfbb7164f72486f8845882fd974b86aa326cd1168e3`，313296byte；kernel+358/-119。只移植short-dot、原单核tiny和K65..256小矩阵Vector及对应launch。没有整份覆盖队友代码，没有移植其grouped tiny或其它Cube selector。
原C9消费WIP在 `experiment/c9-window-review` / `8a69048` 单独保存，CPU/CANN/NPU仍PENDING、未提交，**不在当前候选中**。

## 结构变化

- short-dot：两个半精度输入放连续UB区域，合并一次FP32 Cast；K16且两个GM指针32byte对齐时使用原生DataCopy，其余仍用DataCopyPad。固定8256byte UB，batch每核最多8，K精确mask≤64、只写有效batch。
- 单核tiny：16byte几何参数，手动32byte对齐UB cursor替代TPipe/TBuf；保留四种布局的FP32 Gather。FT物理连续输入共用一次Cast；其它布局使用原Gather地址。K32/40/48/56/64分别编译，通用K分支保留。
- tiny归约：行Max写每32byte块的首元素，另7lane为Sum零身份；完整K点积后一次有效N Max、再一次有效M×8 Sum。零是Sum身份，**不参与Max**；全负输出正确。
- K65..256小矩阵：每AIV独立完整batch，输入只搬一次；按实际UB选择M chunk，K按64lane完整累加后Max(N)，最后逐chunk累加M Sum；没有GM中间通路。M/N均至少2，M≤16/N≤32；M/N都≥16时保留旧Cube。实际AIV与UB查询，不假设固定核数。
- 移除TPipe后，显式0号S_V/MTE2_V/V_MTE3事件各自独立配平，末尾PIPE_ALL保留输出完成依赖。K index helper避免CreateVecIndex隐式依赖TPipe。

保留父MakePlan、workspace/grid及所有大矩阵代码；新增SmallVectorK256Rows只在Launch覆盖其合法小矩阵范围。适配时删除未使用的grouped host参数，并保护BMMMS_TUNING任何显式pin，避免新launch覆盖旧实验选择。
这份代码来自队友，不声称是本Agent新算法；合并后的收益必须由独立正式测试给出。减少调用/参数/框架开销不保证提速。

## 本地验证

运行 `python3 tools/validate_teammate_tiny.py`。

- 3600组实际tiny，动态K与5个K常量分别执行，与整个父tiny及独立数学oracle逐元素一致。
- 5040组**实际selector和192KiB预算允许**的K65..256原生小矩阵，含chunk1/3/整M、尾chunk、四layout、K8非16尾、全负/正负混合。
- 90组short-dot：B1/3/7/8/9/15/16/31/64、K32/40/48/56/64、负/混合；实际aligned/fallback及父核对，输出唯一且不越界。
- typed UB slice独立边界、未知内容poison、Gather地址、DMA延迟、输入不改、完整K→MaxN→SumM、每元素唯一y写和输出guards均通过。
- production/TUNING各161280实际新selector控制、各18640选择，验证实际AIV限制、UB预算、最大chunk和全部显式pin不被覆盖。
- 缺PIPE_ALL输出完成及缺稀疏行Sum零身份两个负控制正确检出。
- 剥除移植块、host新增及对应launch适配后，**整个kernel逐字恢复父**：C8/C9/其它kernel/MakePlan/GM布局/全局ABI均未变。不改main/CMake/run/golden/依赖。

模型MTE2与输出可延迟，但Vector和标量操作同步；输入采用16bit整数值模拟转换，不模拟真实FP16/BF16编码、全部硬件事件时序或性能。公开fake平台不是CANN tiler；原tiler逐字保持，此处不声称重新验证它。
首次验证修正了三个模型问题：scope抽取锚点误匹配host validator、遗漏CPU的__aicore__宏、强制运行超过实际UB所允许的chunk；最后一项改为先调用实际selector再测试，不放宽kernel检查或正式规则。
原始结果本机Git忽略 `artifacts/teammate-tiny-dot/`，不提交大型日志或凭据。

## 正式验证请求

独立官方原模板仅替换kernel，dry-run核SHA。commit/push后一次CLI，立即记录ID，只轮询同任务至终态。
优先观察C1..4，父正式时间2.15/3.97/4.30/5.60μs；同时15点全精度，保留C8/C9。没有actual shape/plan/SoC/profile或重复A/B时，只报告单次变化，不推断截图源码、路由命中或稳定加速。

CANN9编译/NPU精度/性能：PENDING。实现 `0beb87d` 已commit/push；独立原模板dry-run only-kernel、313296byte/SHA一致。
正式提交 **`6abe7b90694b590c3c08ed48`** 已创建，下一只查询这一ID到终态，不重复提交。
