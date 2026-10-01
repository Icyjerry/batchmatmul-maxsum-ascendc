# C7专用单C缓冲消费路径

## 目标与范围

分支 `experiment/c7-lean-vector`，父 `d793083`，父kernel SHA `e8a1512e88e3cc71069d501b9cb934917ac2717cde772f83a9f6fad0daf7f6bb`。
候选kernel SHA `0fa24fce76929aee569311905518ee963be5097e7589161a6c525f1996eb6b05`。
只给已有 `SMALL_FULL_INPUTS` / dual34增加专用Vector helper和调用；生产者、host/选择条件、launch、grid、workspace、C8/C9及其它Vector逐字保持父版。
算法仅修改kernel.asc，不改官方模板其它文件，不新增GM/flags/输出参数。父已正式15/15通过，C7为9.40μs，原49.38μs TT + 队友约68μs C9组合保留。
当前历史C7选择条件是TF/FP16、B[16,32)、M[32,64)、N[128,256)、K[256,512)、完整一M/一N tile且实际片上容量满足；接口没有返回正式shape/plan，不能宣称实际case一定命中。

## 假设与依据

单个完整N tile不需要多tile运行Max状态；空闲AIV不消费C、不写y，可只完成原信用握手。
减少非矩阵乘计算与不必要通信，是[FlashAttention-2](https://arxiv.org/abs/2307.08691)采用的优化原则。这里据此提出独立Ascend实现假设，没有采用论文GPU性能数字，也没有声称NPU必然提速。
具体API全部来自当前已通过源码：TBuf、DataCopyPad、WholeReduceMax/Max、WholeReduceSum、四类HardEvent及mode2跨核信用。WholeReduceSum的M mask最大63，使用已有小矩阵路径的单repeat调用形式。

## 实现

两AIV各先发原4/5号空ring信用；非活动subcore和无batch的worker均不初始化UB。
活动subcore0：一个BM×BN FP32 C TBuf、四组BM行scratch和32byte sum，按原cyclic batch顺序消费。
GM→UB只读有效M/N，按BN行距落UB，尾部不进入归约；沿N的64列组WholeReduceMax、原tree Max，随后沿有效M一次WholeReduceSum。
一组只有subcore0向y[batch]写4byte。全负结果仍取负数最大值，不做零初始化。

依赖链：

1. V→MTE2：上一批Vector读完单C缓冲后，下一次MTE2才覆盖它。
2. DataCopyPad后在PIPE_MTE2归还ring信用：全部GM读完后Cube才可重用GM。
3. MTE2→V：有效C到UB后才读。
4. V→MTE3：sum完成后写y；MTE3→V：输出完成后下一批才重写sum。

父每AIV分配 `8*BM*BN + 20*BM` byte；新活动AIV `4*BM*BN + 16*BM + 32`，空闲AIV0。BM48/BN192下对应父74688byte、新37664byte。不调整host原更保守预算。
移除两个C queue和Max queue的操作、-inf状态初始化及单tile运行Max更新。数据GM读/输出字节量未变，单缓冲显式依赖可能抵消减少开销；计数不是性能证明。

## CPU与源码范围验证

运行 `python3 tools/validate_c7_lean_vector.py`。

- 从实际kernel抽取整个helper执行，1296组合：B16/24/31、M32/48/63、N128/129/191/192/193/255、workers1/8/20/32、负/正负数据、三种独立引擎调度优先序。
- MTE2/V/MTE3分别排队，Fence为源引擎signal/目标引擎wait，复用event不重复占用。通过活operand generation检查读写先后。
- GM信用完成时立即poison ring，确认UB副本仍可正确归约；单C与sum跨batch复用、输出guard、唯一4byte写、空闲subcore无UB/GM读/y写、所有信用配平。
- 分别删除V_MTE2、MTE2_V、V_MTE3、MTE3_V的四个负控制，扩大N尾mask和提前归还GM信用的负控制，全部正确检出。
- 剥除新helper和唯一调用后，**整个kernel逐字恢复父**；沿用父生产者、host和原预算的CPU/公开8.3/正式设备证据，不宣称重新验证它们。

模型Cube与另一AIV信用是合成ready/credit夹具，不是完整AIC+两AIV原生调度器；不模拟CANN硬件指令延时或FP16/BF16舍入。CPU整数FP32结果不能证明正式误差、性能或所有A2/A3同步契约。
原始资料本机Git忽略 `artifacts/c7-lean-vector/`，不提交大型日志或凭据。

## 正式验证请求

只提交独立官方模板中的kernel变化。提交前commit/push，立即保存ID，随后只轮询同一ID到终态。
检查CANN9编译、15点全精度和时间，优先比较父C7 9.40μs；C8/C9等未改路径时间不能归因该改动。
没有actual shape/plan/SoC/profile或重复A/B时，只报告单次结果，不保证稳定收益；没有显著收益则归档，不合main，不重复近邻参数提交。

CANN9/NPU精度/性能：PENDING，尚未提交。
