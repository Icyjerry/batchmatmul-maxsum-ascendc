# 完整 K、两 M 基本块的库内预载

## 最终源码审查：停止提交，保留反例

候选代码 `1b278c9`，kernel SHA `0c37471e6b6b703bda9735fef64dd47523def338c2f338d6000d6f17d80bbdec`。
**没有正式提交，也没有CANN9编译、NPU精度或性能结果。**独立官方模板下载成功；未将候选打包提交。

补充完整外K循环后发现：公开 `MatmulMDLSchedulerCommon::ReduceKMultiIter` 在每个K outer块后调用DoPreloadAWait，
而DoPreloadLoad只在FirstOuterIter发起下一M读取。M有下一块、A完整K、B非完整K时，第二个外K块产生第二次Await而没有新的EnQue。
在dav220的CubeInBuffer中Await继续调用qid.DeQue；若按模型中标准队列契约执行，就会等待/消费不存在的转移。
此外ClearL1BufferCache在M/N preload启用时同时跳过A和B的Clear；B非完整K的缓存生命周期也需要真实安装header核对。

`tools/validate_m_preload.py`新增抽取**完整实际ReduceKMultiIter方法**的运行模型，16个代表配置都在第二个outer块复现：一次Async读取、两次Await。
其它Compute/CopyIn/queue由明确的元数据mock替代，不是完整库/NPU模拟；**不能据此宣称安装CANN9存在同一缺陷**。
它足以否定先前2304个只检查预载谓词的模型能证明整个候选同步正确；仅A完整K的条件不足以放行当前设计。
必须先取得安装header或采用独立手写队列协议，不能把该风险带入比赛提交。

原1536K/库64×256的设计若把B也完整驻留：A双buffer384KiB+B单完整buffer768KiB，共1152KiB，超过示例512KiB L1。
不能靠修正depth几行闭环，也不提交相近参数。此分支保留设计和反例，恢复query-block通过kernel。
下一项可执行结构研究是独立手写完整K的A双buffer预载：先阅读现有manual/paired-M队列，保留GM ring与AIV，明确B每K块的释放和下一M只等待一次。
它尚未实现，容量/布局/K尾块与异步顺序仍需模型及正式验证；总体重大提升尚未达成。

以下是实现与初步模型的历史记录，不能覆盖上面的停止结论。


## 假设与区别

保留 query-block 父版 `4f39f98` / kernel `55225cc` 的核心任务、schedule、GM ring、AIV消费和finalizer。
只对原dual1、B1/BF16/TT、M/N/K≥1024、schedule.baseM64/128、窗口宽128/256启用候选；显式dispatch pins仍保留。
内部库baseM=旧schedule.baseM/2、baseN=整个窗口宽，因此一个会话最多两个M基本块、只有一个N基本块。
`GetMDLConfig(false,false,1)`使用真实完整K A ping/pong，预载下一M块；不是此前普通MDL preload0，也不是单M块的全N会话。

现有128行×256列窗口示例（非正式隐藏shape）：库64×256×64；A每slot保存ceil(K/64)*64的完整K，两个slot；B为256×64的两个slot。
K1536时A共384KiB、B共64KiB，另留4096字节；L0A/B采用库返回的DB2。旧M128完整A只需单buffer；新方案改变读取时序，**没有减少A的总读取元素数**。
BK减小时MMAD次数可能增加，速度必须由设备检验，不能据预载次数推导加速。

## 官方依据与资源

- [CANN9 GetMDLConfig](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/API/ascendcopapi/atlasascendc_api_07_0622.html)：A2/A3支持M方向预载；要求完整K和M方向DoubleBuffer。Mix(1,2)要求A/B的IBSHARE；本路径保持原类型配置与IterateAll。
- [官方预载示例入口](https://gitcode.com/cann/asc-devkit/tree/9.0.0/examples/01_simd_cpp_api/03_libraries/00_matrix/matmul_preload)。网页抓取超时；可读的公开源码checkout中同名示例采用GetMDLConfig、显式base/step/depth。
- 实际审查与CPU链接的公开仓库：[ascendc-api-adv](https://gitee.com/ascend/ascendc-api-adv)，固定revision `c7dfa2d901a314e1ae69e9cef850057593f2a58b`，版本8.3.T9.0.B066。**不是安装的CANN9 header**。
  `scheduler_mdl_base.h`的DoPreloadLoad/DoPreloadAWait；`copy_cube_in_mdl_base.h`的下一buffer与Await；`cube_in_buffer_double_buffer.h`的depth/step、实际InitBuffer容量。

先由真实tiler生成所需baseM/N/K，检查返回一致、dbL0A/B=2及L0C，然后按官方示例明确设置stepM/N1、stepKa=ceilK/baseK、depthA1=2*stepKa、stepKb1/depthB1=2。
重新记录shareL1Size=两个完整A+两个B面板，检查实际L1/L0A/L0B/L0C/UB容量；失败回退父版。没有增加GM区或修改输入。
只保留一个基本N块，避免同一下一M缓存被多个N块反复Await；不使用SpecialMDL的另一套buffer偏移逻辑。

## 本地验证

`python3 tools/validate_m_preload.py --source /private/tmp/ascendc-api-adv-review`

- 将当前与父版完整host源码编入未修改的公开真实MatmulApiTiling算法，shim只替代平台/日志/tiling存储。
- production1775 / TUNING1779个shape/core/capacity/pin配置，各128个选择新路径；schedule所有字段、worker、workspace和finalBlock与父版完全一致（只有dual1→29）。包含K1032/1544尾块与低L1/L0B回退、布局/dtype与pins。
- 执行公开源码的真实DoPreloadLoad/DoPreloadAWait方法，2304个M32/64基本块、1..128行、K1024/1032/1536/1544/2048/3072、K面板64/128的条件/延迟转移模型；下一M只有一次发起/等待，单M尾块不发起，转移行数严格有效。
- byte comparison证明已有bmmms_dual的Cube/AIV函数体仅Matmul配置选择不同，其余字节一致；tail、GM stride和事件调用未改。
- 既有tiny TT：700实际源码模型执行、production/TUNING各432尝试/360选择、30量化FP64对照通过。

这些不是CANN指令模拟、硬件异步事件或性能证明。正式CANN编译、NPU精度/latency PENDING；准确SoC、实际shape/plan/profile仍未取得。

## 正式验证计划

独立官方模板只替换kernel.asc，dry-run后CLI提交一次；同一ID查询到终态。比较第8点与父通过版69.03μs，其它路径单次差异不归因。
若没有明显收益保留结构反例并恢复query-block，不继续相近baseK/预载参数提交。整体重大提升仍未达成。
