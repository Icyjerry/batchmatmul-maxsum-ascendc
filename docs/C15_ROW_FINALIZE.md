# C15 八 AIV 按行归约，复用原 partial arena

## 假设与采前标准

C15两MMAD候选真实每核8→2MMAD，完整耗时只改善1.28%，已恢复正式Pass15的2073f48e。默认五报告实际block_id显示仅AIV0执行整个8×64×64 partial求和/MaxN/SumM，其余7AIV基本不执行Vector运算。计数重叠，不声称证明临界路径；本次固定尝试改变归约任务所有权。

本次从2073f48e/a11e2d9派生，原Cube producer逐字不变，不并入失败两MMAD代码。固定FP16TT/B1M64N64K8192、原8K1024 splits/8Cube8AIV/原workspace。每AIV负责8个完整N64行，读取这8行在全部8个K split的贡献，升序FP32求和后MaxN，再Sum这8行。最终AIV0确定性累加8个行组分数。无atomic，无新GM allocation/通路，不把Max提前到K归约之前。

**采前准入**：全部精度/输入guard/yguard/全负/同地址mixed-negative-mixed通过；一次默认8表×5完整报告，实际新ROW_FINAL=true符号/8Cube8Vector，原Cube每核仍8MMAD；中位<=9.8463933us（比正确父10.940437至少快10%），且全部五次<父最快10.540421us，才进一步正式15验证。20%目标<=8.7523496us保持。未达则完整归档恢复2073，不重复采样或扫描行数、核数、buffer/stride。不把本地FP16TT属性当正式隐藏元数据确认。

## 别名与同步

原partial为8×4096float。AIV w读取每个split的[w*512,(w+1)*512)，一次strided DMA共4096float/16384B，原单核为32768float/131072B。不同AIV的行范围不重叠。

每个AIV完成本地MTE2→Vector读、7次512元素Add、8行WholeReduceMax、8行Sum后，将一个分数和7个零写回**split0自己行范围开头32B**。没有其它AIV会读取此行范围，且自身完整read已完成，因此无需在覆写前增加全局barrier。写回之后MTE3_S fence，再8AIV SyncAll，AIV0按2048B行组步距读8个32B槽，Sum64个float（仅8个分数非零），精确4B写y。

原Cube PIPE_FIX通知→各AIV等待→原全AIV barrier仍保留；新增最后一次全AIV barrier可能抵消并行读取/计算收益，这是需要设备反证的主要风险。实际SDK dav_c220 SyncAllImpl先PIPE_ALL，再PIPE_MTE3 ffts_cross_core_sync/wait_flag_dev；未修改SDK。

本地UB16384+32+256+256=16928B，额外1024B guard；原CubeL1/L0A/L0B/L0C 65536/32768/32768/16384B保持。host guard精确匹配完整Schedule/plan/对齐/workspace/resources，任何TUNING pin或其它case/layout/dtype回原入口。模板新增ROW_FINAL默认false，生产true仅该guard。

## 源码与验证状态

kernel **00c23fa0f42564df10187e01ed0b1da03f2c405b64119b8ac3c8e47060bbc406**，冻结imports/c15-row-finalize-00c23fa0f425。只新增finalizer/guard、默认false模板项及dispatch，whole-source逆变换精确恢复2073，保护7等1734f16。

CPU提取实际完整finalizer、8个并发线程、延迟DMA读写，4个完整32768partial有符号张量（含全负）、全部行/全部split的独立double参考归约、行所有权/完成后复用、发布后barrier/读可见性、原partial未覆盖区域和16-word yguard均通过；6个stride/owner/read-ready/publish-ready/barrier故障控制拒绝。实际guard production54/TUNING65拒绝+容量临界通过。不是FP16 native布局/速度证明。

第一次独立工具构建误填不存在的冻结目录，报kernel.asc找不到；这是工具路径错误，无源码修改。已改为上列实际SHA目录，CANN9/dav2201编译进行中exec67879。native精度、全负/变化输入、默认五报告、正式15全部PENDING，无新OJ任务。
