# C15：Cube 全部就绪后通知按行归约的 AIV

## 本次独立依据

上一目标turn已经改变authoritative state：两MMAD和8AIV按行归约均完成设备精度/完整五报告，前者中位只快1.28%，后者快6.2157%，均未过采前提交门槛，结果已归档。原保留2073f48e正式Pass15/398.92us。

本次不把两个收益相加、不改BK、split数量、行组大小或buffer。只改变已验证按行归约版本81f49ff的producer-ready协议：把“每Cube通知自己的AIV→全部AIV同步”替换为“全部Cube确认Fix输出→通知各自AIV”。原Cube数学/输入搬运/8MMAD、8个K1024 split、整个finalizer、GM arena与资源guard逐字保持。新增归约后的AIV全局屏障也保留。

假设：把就绪集合放在生产者侧，可以减少消费者开始前的协议成本；这是待验证假设，不是已有加速结论。

## 实际 CANN9 依据与风险

当前设备安装路径：
`/usr/local/Ascend/cann-9.0.0/aarch64-linux/asc/impl/basic_api/dav_c220/kernel_operator_sync_impl.h`。

已通过SSH实际读取，未修改SDK：

- `SyncAllImpl<false>` 的AIC分支使用PIPE_FIX、mode0、SYNC_AIC_FLAG的集体set/wait，随后mode2通知配对AIV。此前AIV发送的mode2是让Cube知道AIV已到达该双向barrier；本算子Cube不读取AIV准备的数据，无此生产者依赖。
- `SetNextTaskStartImpl` 的AIC分支直接使用PIPE_FIX/mode0，无AIV提前发送；与上述pattern共同支持本次单向producer-ready设计。它本身不是本算子native证明。
- `NotifyEventImpl`调用ffts_cross_core_sync(pipe,GetffstMsg(modeId,flagId))，WaitEventImpl调用wait_flag_dev(flagId)。实际GetffstMsg编码mode和4-bit flagId。
- SDK保留flags11/12/13/14，本次Cube collective用8，paired通知用9，原finalizer的SyncAll用14，互不重用。硬件本地HardEvent槽与这些跨核flag不是同一命名空间。

新true分支：每Cube完成原Fix/MTE1事件退休后，CrossCoreSetFlag<0,PIPE_FIX>(8)→CrossCoreWaitFlag<0>(8)→CrossCoreSetFlag<2,PIPE_FIX>(9)；AIV仅wait mode2/id9后进入原FinalizeSplitTTRows。全8个Cube到达collective前，任何AIV都不得读partial。现有精确guard保证tasks8/workers8/cubeBlocks8/finalBlocks1/MIX11，不存在无任务Cube缺席barrier。

mode0作用域/运行时block配置、退出与flag消费以及真实硬件FIFO仍需native确认。CPU模型只按上述SDK语义建模，不能把模型通过当成硬件协议已证。

## 采前准入，不改结果门槛

固定输入FP16TT/B1M64N64K8192、9382/CANN9/caller20的原c15.json和完整frame。全部精度、输入不变、16-word yguard、全负、同context/stream/输入地址mixed-negative-mixed通过；默认8表×5完整报告，实际新true分支/8Cube8Vector/每Cube仍8MMAD。

与正确parent2073/DSOca36已冻结五报告比较：median<=9.8463933us（原10.940437至少快10%），全部五样本<原最快10.540421us，才继续正式15验证。与已验证按行版本10.260410us也完整报告，避免把其原有收益全归因新协议。20%目标8.7523496不变。未达归档恢复2073，不重采、不降低门槛、不扫flag/row/BK/split参数。

其它dtype/layout/plan/resources及所有显式TUNING pin仍走原false入口，不扩大shape覆盖。正式C15属性仍是历史对应假设，本地fixture不证明隐藏属性；C3正式dtype/layout依然未知。

## 源码身份

kernel356814B/SHA **ca66a5417b3ba41d6dd86231e4f3e36fb28dc6ca7df9feb854c1218bee872583**，预定冻结目录imports/c15-cube-collective-ca66a5417b3b。只改kernel算法；原两个未达门槛候选没有提交比赛。

## 已完成验证

`python3 tools/validate_c15_cube_collective.py`：提取实际Cube collective和AIV等待调用，8个并发producer/8个consumer，逐个延迟每个producer共8种到达顺序。所有producer完成后各行owner才读取，所有flags均消费。4个删除集体等待/删除集体发布/错误collective ID/错误pair ID反例被拒绝。逆变换精确恢复81f49ff整个源码，因此除ready协议以外数学、原producer、完整row finalizer、guard和原GM逐字相同；保护7与1734f16一致。

`python3 tools/validate_c15_cube_collective_guard.py`：实际guard production54/TUNING65反例拒绝，精确资源容量临界通过。不是SDK tiler/native分派证据。按行完整数学、全负与workspace复用已有81f49ff CPU/native证据，本次未重复采其性能。

暂停前工具session33625/52590在恢复时均Unknown process id，无活跃handle；重新运行CPU检查session31922 terminal0，以上两项PASS。没有重新启动NPU测量。

## 当前阻碍与唯一下一动作

暂停后前台SSH master/control socket消失，现有入口干净重连返回platform authorization denied，脱敏结果已确认；原始private log留/private/tmp/bmmms-remote-access/reconnect-current.log/0600，凭据不入Git。已请求用户刷新云平台访问授权，无需重复root密码。上次实际queue为空发生在暂停前；当前远端queue状态未知，不能写成已确认无任务。

CANN编译、native精度、输入切换、五报告及正式15 **PENDING**，未创建任何新OJ任务。下一新SSH到达后：先检查真实master/queue/ps，上传本候选到按SHA命名的冻结目录，只构建一次独立native_oj_like shared；写source/DSO/wrapper身份；correctness→同地址序列→一次default五报告→对照上述gate。不要把阻碍归因成源码编译错误。

## 2026-10-15 离线验证包已准备

再次读取当前Git状态仍ccfaecc/源ca66a541，干净重连仍失败，当前脱敏stderr为Connection closed by UNKNOWN port65535；此前一次明确platform authorization denied仍是历史证据，不能把当前模糊关闭说成新增的明确授权诊断。没有新的SSH入口或活跃远端任务handle。

新增独立验证脚本`tools/native_oj_like/c15_cube_collective/run.sh`，不修改算法/保护7/现有harness实现。其冻结传输包`artifacts/c15-cube-collective/c15-cube-collective-validation.tgz` **SHA0de344140d01b8dceb4db104d75e2fded50609a3b49743a6843d403c74c3b660 /63748B**，所有目录700/文件600，不含凭据、大日志或输入原件。包不入Git；脚本和流程说明入Git。

包包含原sourceca66、原wrapper994e29f、原CMake/driver/job/analyze/c15fixture、从正确parent完整summary抽取的frame，以及9文件SHA manifest。启动前核对两个已有input的实际字节SHA、两份golden SHA、原完整frame、原fixture、同地址序列准确顺序和harness/source哈希；若已有任何该候选结果目录，拒绝重启以免覆盖未知/活跃job。成功编译后才创建source/DSO/wrapper identity，按原job.py串行correctness→alternating→一次完整default五报告，保留全样本、核对8Cube8AIV/8MMAD/true符号并打印原gate结果，不自动创建OJ。

新入口恢复后，先核对真实SoC/queue/ps，再用scp -O上传包、解压到固定路径：

```sh
tar -xzf c15-cube-collective-validation.tgz
bash c15-cube-collective-validation/run.sh /workspace/bmmms-codex
```

只有脚本开始启动后产生的新handle才可作为verified wait。当前仅`bash -n`、三个嵌入Python段AST解析、9文件hash/实际wrapper身份、archive安全路径及权限检查PASS；**没有运行build.sh/编译/NPU/profile**。启动时对原server输入/完整frame依赖缺失或属性变化应停止并审阅，不静默生成替换数据或放宽检查。

## 2026-10-15 Native 终态：协议正确，中位无新增收益

用户刷新入口后连接恢复：host2ef29bca0f61、Ascend910_9382、24AIC48AIV、dev0/physical14/card7chip0、CANN9、caller20。先检查实际queue空/ps无旧任务；前台master63301/pid9058，临时askpass连接后删除，凭据未入Git。冻结包实际源路径为`imports/c15-cube-collective-ca66a5417b3b/c15-cube-collective-validation/source/kernel.asc`。

原包脚本75161 terminal0，CANN9/dav2201编译PASS，DSO **85f8f7296db8f27ec0a1ec59ecc21b3fc5c274ccae4fe0895c91cb77d88a6607**，wrapper994e29f/sourceca66a541绑定。首次mixed、同context/stream/输入地址mixed→negative→mixed全部PASS，混合输出精确1.6493455171585083，全负-40.063804626464844/maxAbs3.8146973e-6/maxRel9.52155e-8；输入不变与16-word yguard通过。

一次完整default8表×5报告，actual bmmms_manual_split_tt<half,true,true>/8Cube8Vector，40个Cube记录均8MMAD，五完整输出fullFP64通过。TaskDuration **[9.980399,10.260410,10.660426,10.040401,10.360415]us**，中位 **10.260410us**。与row-only版本中位完全相同；对正确parent10.940437的6.2157%改善是按行归约已有收益，**没有观察到新ready协议的额外中位收益**。且10.660426慢于父最快10.540421，median也未<=9.8463933；未过原准入，无OJ/重采/flag或参数扫描。恢复工作kernel到2073/a11e2d9，候选源码保存在ccfaecc。

PMU按实际block_id：Cube平均time6.259736/MTE2 3.573542/MAC.735111us；AIV0平均time7.653333/Vector.267778/MTE2.304111us；其它7AIV平均time7.312667/Vector.229444/MTE2.197413us。相较旧row-only，Cube统计time提高而Vector统计未减少，符合协议未产生新延时改善的观察；这些重叠计数仍不能相加或证明某条指令的因果成本。

全部原始correctness/alternating/五份默认8表、身份、成功build.log已下载`artifacts/c15-cube-collective/c15-cube-collective-evidence.tgz`，summary与pmu-summary同目录、目录700/files600；下载58231 terminal0。实际远端queue再次空，无活跃NPU/OJ。正式15及其它SoC/dtype/layout未测；全局冲榜目标仍未完成。新入口已解决此前服务器阻碍，不继续报告旧platform denial为当前状态。
