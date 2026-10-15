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
