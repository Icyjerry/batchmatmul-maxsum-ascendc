# 小 TT：共享 Cast 与连续 K 分组归约

## 假设与实际父路线

分支 `experiment/tiny-tt-packed-frame`，父62ad1cd/算法1734f16。按用户计分参考，C3/C11/C1/C4/C9贡献约75%的追赶差距；本项针对C4历史条件范围，不是已知正式shape。

关键诊断纠正：Launch首先调用SmallVectorK256Rows。M8..15/N16..31/K128..248/TT原本通常走bmmms_small_vector_k256，不是后面的bmmms_tiny_tt_vector。实际父已经手动UB、按B独立AIV、K-only索引/逐M Gather及顺序K折叠，不得描述为本轮首次优化。

结构假设：两输入放同一typed UB frame，一次Cast；乘积从行优先改为[Kgroups,microRows,paddedN,64]，K分组连续Add折叠；所有M最大值留本地，最后一次SumM。显式手动调度入口/24B参数。减少操作或参数大小不等于延时收益，microRows4/2也可能增加父原本较大M块的循环次数。

## 实现范围

- kernel SHA256 `bd87dde9612d3c41d0b45550824f7cc75ac4419860e7a22ac579112c5f58431a`；新entry/guard/前置launch三处，删除后逐字恢复整个1734f16。
- guard在通用Vector之前，TT/K128..256/M1..16/N1..32/K8；原前置Vector准入使用原B个AIV，否则只兼容原dual28单AIV计划。真实UB/AIV容量、显式TUNING pins回退。原host Plan/workspace不变，无新GM通路或metadata，main/测试/golden/依赖未动。
- 32B对齐UB frame：typed输入、共享FP32 Cast目标、canonical query、K索引、Kgroup-major products、dots、全部M Max状态、输出。实际容量决定4或2行，每点完整K FP32后Max有效N，最后Sum有效M。
- 复用已通过父helper SmallVectorManualIndex，避免无TPipe时K>64 CreateVecIndex事件分配依赖。保留输入就绪、输出最后读取、batch复用、terminal retirement事件。
- 新entry只处理TT，保留其它路线。只真实N参加Max，输入不变，y唯一合法writer。

## CPU与静态证据

`python3 tools/validate_tiny_tt_packed_frame.py` exit0：

- 3201 actual entry /576软件编码FP16/BF16；FP64实际存储值oracle→FP32，maxAbs1.19209e-7、非零maxRel1.18938e-7。M/N尾、K128/136/184/192/200/248/256、全负、多batch循环/idle workers、typed UB/GM/索引/产品界限、唯一y writer、输入不变、延迟DMA/store通过。
- 七负控制拒绝：输入ready、batch输出retirement、Kpadding、完整K、Ntail、query offset、terminal完成。原先只删除terminal PIPE_ALL不会失败，因为末尾Wait已完成队列；控制改为删除末尾retirement+barrier，不能把冗余barrier描述成必需。
- production/TUNING各3000 actual host配置/258准入/220四行；Plan/workspace不变，低容量/核数/pins回退。各16384完整历史C4 conditional范围配置均准入前置候选，不是正式shape或native路径证明。
- launch位置和删除三处恢复整个parent的scope检查、git diff --check通过。

模型Vector同步、DMA/store排队，不是设备时序模拟；软件FP16/BF16解码/FP32算术不能代替native。CANN9编译、NPU精度、性能 **PENDING**，接口没有实际SoC/shape/plan/profile。

## 正式对照与交接

独立模板 `/private/tmp/bmmms-tiny-tt-packed-official/project`，其它七源码与1734f16逐字一致，仅kernel替换。commit/push/dry-run后只提交一次，立即保存ID查询至终态。父三次C4 4.12/4.12/4.15μs。明确大收益再原样确认；否则归档恢复父，不扫描附近M块参数，其它未改路线波动不归因。

原始日志忽略artifacts/tiny-tt-packed-frame/，目录700/文件600。整体冲榜目标未完成。
