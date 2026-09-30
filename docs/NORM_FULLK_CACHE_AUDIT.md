# 父 Norm 路径完整 K 缓存审查

## 为什么需要这项审查

手写完整K A驻留的窄窗和宽窗候选均正式15/15通过，但都没有取得大幅收益。不能以producer自己的读取公式证明相对父库减少了流量。
宽窗补齐后，继续核对未修改公开真实tiler及Norm缓存实现，发现父库已经具备窗口内完整K A缓存。

## 可复现证据

`python3 tools/audit_norm_fullk_cache.py --source /private/tmp/ascendc-api-adv-review`

公开官方源码固定 `c7dfa2d901a314e1ae69e9cef850057593f2a58b`，版本8.3.T9.0.B066；不是正式服务器安装CANN9的header。
父kernel为query-block通过版 `968e957` / kernel `55225cc`。

- 未修改真实MatmulApiTiling算法的1400网格中，1000个dual1计划均 `iterateOrder=ORDER_N,stepM=stepN=1,depthA1>=ceil(K/baseK)`。
- 其中824个计划每个N shard只有一个window。对这824种父计划，手写A跨N shard完整驻留与父完整K窗口缓存**没有理论A输入读取量优势**。
- 例 `(M,N,K)=(1024,1024,1024)`：W4/ns2、baseK128、stepKa8/depthA1=8；每个shard只有一个4-tile窗口。
- 例 `(1025,1025,1032)`：W5/ns2、baseK128、stepKa9/depthA1=9，非对齐K没有破坏整K缓存。
- 例 `(1536,1536,1536)`：W2/ns3、baseK128、stepKa12/depthA1=12；同一shard有多个小窗，才可能通过跨窗A驻留进一步减少读取。

直接抽取 `cube_in_buffer_normal.h` 的实际AllocTensor/FreeTensor/Reset/Hit/GetBuffer方法执行，2024个窗口生命周期、21512次K-panel缓存缺失通过。
同窗后续N tile调用Hit获得已有K面板，FreeTensor对缓存范围不释放，Reset才释放cacheHead；完整K N复用不是凭字段名推断。
模型中实际缓存方法源码SHA `7fc61bc1d5be9a5cce939fd436a81f467fa6d374db0d23d28153e78ce00d3e89`。

窗口边界与ORDER_N单M的K索引由抽取父host及人工控制的队列元数据提供；没有执行完整库scheduler、KFC、CopyTileToCube、真实DMA或硬件异步事件。CacheSize初始化按已查明full-load分支的depth赋值；队列转移语义是mock。
公开源码 `copy_cube_in_norm.h` 的LoadData先Hit再Copy；`scheduler_norm_base.h` 的ORDER_N循环保持A缓存到N遍历完成；父bmmms_dual每window SetTensorA/IterateAll/End重新建立会话，故不能把跨窗口复用也算入父版。
不能宣称安装CANN9具有完全相同缓存、正式case命中或具体NPU退化原因。

## 对优化方向的影响

1000计划的逻辑A元素读取模型合计：父窗口缓存3,717,561,600，手写跨shard驻留3,184,688,384，理论差异约14.3%；只是该合成网格的加总，不能代表任何单个正式case、GM/L2流量或速度。
此前将父库简单视为每N tile重新读取A是不成立的；已完成的wide候选验证不能证明存在相应量级的流量消减。
这与正式缺少大幅收益相容，但不构成实际瓶颈证明。

停止继续整K A驻留/近邻窗口参数试交。恢复query-block通过版，下一项源码研究需针对尚未被缓存解决的L1→L0 TT搬运与MMAD发起开销：先核对A2/A3可用的实际矩形/转置加载能力，再建调用与物理布局模型，不能复制仅Atlas350支持的LoadData2DV2或把Load3D非转置方案换名再提交。
实际shape/plan/profile仍需要设备证据；总体大幅提升尚未达成。
