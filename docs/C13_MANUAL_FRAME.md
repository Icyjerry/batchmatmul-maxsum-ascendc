# C13 FF尾块：固定物理frame

## 证据与假设

父通过算法1734f16/a5eef105，最新五次同SHA C13=14.94/15.11/15.13/16.74/15.99μs，中位15.13。用户最新榜首C13=10.20μs，最新Tbest=7.31μs；均非同机A/B。历史条件B1/M8192/N64..127/K128..248/FP16/FF不是已确认正式shape。

实际CPU host审查4096计划显示每核数条件空间1024个shape中992走dual14，32个双对齐shape走已有dual3/tree16驻留B。此前完整K/B驻留已经两次正式无收益，不重复。此候选保留dual14原K-panel大小/顺序和原任务/GM，改变TPipe/TQue与局部、末级归约的物理生命周期；借用本仓库C7/TT已通过的手动frame模式，不据此保证C13提速。

## 实现及范围

- 分支experiment/c13-manual-frame；kernel365034bytes/SHA256 `92c3654faef7db189c167846215a96ab0dcf937b0833ef36b90f8b35d3158d28`。191行/三处新增，逆移除恢复整个1734f16。其它算法、MakePlan、main/CMake/run/golden/正式测试/依赖保持逐字。
- 新entry bmmms_c13_manual_frame、20B实际shape参数，仅已有dual14/B1/M8192/FP16 FF条件、BM128/BN=ceilN16、64个M tile/一个N tile、kSplit1/earlySum及完整资源准入。全部显式TUNING pins回退。原dual3驻留路径不进入。
- Cube仍两份128深A1/B1、两份A2/B2、两份完整FP32 C。K128一段，其它K分两段，K8尾ND2NZ补零；Load2D物理ZZ/ZN和原MMAD顺序保持，不改成完整K驻留/矩形Load3D/跨M预取。原task=worker;task<64;task+=workers、跨核flags0/1及4/5、双ring和partial前缀保持。
- ready/free事件明确保护L1最后读取、L0最后MMAD读取、C最后Fixpipe读取。完成完整K后才能Fixpipe通知Vector。没有TPipe事件ID冲突或析构完成依赖。
- 两AIV各64实际M行；双C/row/sum UB。只读真实N，分组Max后WholeReduceSum64，直接写与父一致的task*16+sub*8早归约槽；其余7float为0。省去-Inf初始化/与单个完整N结果Max、通用ReduceSum与queue。MTE2最后GM读取后释放ring，MTE3完成后才可复用sum源。
- 一次原all-AIV barrier后，0号AIV复用死UB读取原1024float early partials，压紧128个sum，经两个64组求和后唯一写4B y[0]。未新增GM通路、原子、workspace分配或跨batch计算。末级UB地址向32B对齐；小M代理发现并修正了原地址计算的对齐问题，正式M8192地址相同。
- 查询真实AIC/AIV/L1/L0A/L0B/L0C/UB；最大显式L1=128KiB，L0A/B各64KiB、L0C128KiB、UB精确为4*128*BN+1088B（最大66624B），另留4096B。末级4672B复用该UB。workspace需覆盖原32KiB partial前缀与每worker双128*BN FP32 ring，不依赖固定20核或SoC。

## 本地验证及边界

`python3 tools/validate_c13_manual_frame.py` exit0：

- 324组producer配置，每组执行所有worker的实际抽取entry；延迟MTE2、live MTE1/完整K MMAD/Fixpipe、物理NZ/ZZ/ZN，输入不变、GM guards、事件/credit收支和复制/MMAD次数通过。所有16种K8、N/K尾、两段ping-pong、单段奇数slot跨任务、全负、idle worker、小M代理及8192/65/136/20核代理覆盖。CPU整数运算，不是FP16编码/精度模型。
- 六项Cube破坏负控制被拒绝：L1最后reader、输入ready、L0最后reader、C最后reader、MMAD→Fixpipe完成、完整K。
- 768组Vector配置，两倍workers实际线程及all-AIV barrier；三FIFO优先级、读后破坏ring、C/sum源复用、early slot全部8float唯一写、无未写partial读取、全负及唯一合法y通过。Cube/伙伴credit为合成模型，没有声称完整硬件协同模拟。
- 九项Vector负控制被拒绝：C最后reader、sum最后MTE3 reader、C ready、sum ready、all-AIV barrier、末级DMA ready、terminal完成、N尾mask、过早GM释放。
- production/TUNING各4096实际MakePlan控制流（显式CPU tiler stub），各3968新entry准入，全部1024历史条件shape/4种核心数；精确容量与低1B、核心与低1核、workspace与低1B、plan/layout/dtype/shape/pin回退通过。Schedule/grid/GM容量未被helper修改。初版fixture误将earlySum非零值999当关闭；已用0验证实际关闭谓词，无放宽语义。
- whole-parent scope逆变换与git diff --check通过。其它七工程模板文件逐字1734f16；CLI dry-run仅kernel.asc/365034bytes/SHA一致。

CANN9编译、正式FP16精度及latency **PENDING**。所有API均来自原正式通过源码，但新事件/布局组合必须native验证；15Pass也不能作为全shape/所有硬件交错证明。

## 下一正式动作

实现/模型/本文件commit/push，独立模板/private/tmp/bmmms-c13-frame-official/project只提交一次；取得ID立即保存，查询同ID至终态，不因观察超时重复创建。保存完整15点，并用SCORE_REFERENCE_1008的新Tbest计分。明显大收益才原样确认；否则归档，不扫附近BM/K分段/队列深度变体。原CPU日志忽略artifacts/c13-manual-frame/cpu.log。整体冲榜目标尚未完成。
