# 手写TT的原生NZ ring · 2026-10-01

## Evidence → Diagnosis

通过父 `e1b3634` / `eb4671c` 的正式任务 `6abe3059694b590c3cdf6c87` C8 49.38μs/C9 67.48μs、15/15。C8已采用完整A1/跨tile B包流水。本轮不改输入流水或tile参数。
历史 `fcbf29b` 库内建NZ在独立MatmulImpl stream上正式通过但无整体收益（C8 67.80→66.40μs）；三个自定义callback NZ变体有运行错误。本候选保留当前手写MMAD/credits，不使用Matmul callback或库NZ计划，不能把历史运行错误称为已修复。

假设：原生C0/NZ写到原ring，AIV一次DMA读取多个完整16列slab，减少FIX NZ2ND转换和DMA block粒度成本。只改变同一GM ring布局，无新GM/flags，数据量不减少；树形Vector Max可能增加指令，不预测提速。

## 修改范围与契约

分支 `experiment/tt-native-nz-ring`，kernel SHA `30a697cc03f6aa3ec39f81275ddcfa27f10aaf4f1d31e0cd4bcbfc51bf6ce233`。
仅 `RunManualFullMCube<...,true>` 的Fixpipe切为 `Fixpipe<float,float,CFG_NZ>`，以及匹配的 `ManualFullMConsumeNZWindow`/Vector dispatch。kChunk/B流水/累加次序/host/预算/workspace/完整C9/default false不变。

GM每个C槽为 `[ceil(BN/16), BM, 16]`。Cube srcStride=align16(validRows)，dstStride=BM*2（**32byte block**）；只写有效paddedRows和paddedCols。各AIV按自己的实际rows DMA：groups=ceil(validCols/16)、blockLen=rows*16*4、srcStride=(BM-rows)*16*4，紧凑UB layout `[groups, rows, 16]`。
最后不足16个N列必须置-inf，不能让Cube补零使全负行变成0。树形按对应lane合并N groups，最后ReduceMax16得到每M行Max，再按原partial/finalizer合并N并Sum(M)。空行AIV仍参与credits。
典型BM=BN128/每AIV64rows的DMA block数64→8，字节数相同32768。不是实测带宽/时间。

## API依据

- 固定官方公开8.3 revision `c7dfa2d901a314e1ae69e9cef850057593f2a58b`：`copy_cube_out_utils.h` 的NZ branch调用基本CFG_NZ；`copy_cube_out_fixpipe.h::GetCBCopyOutParams` 用目标M*16*sizeof(dst)/32算dstStride，FP32即2*M。
- 官方 [Fixpipe示例8.5](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/850/API/ascendcopapi/atlasascendc_api_07_00171.html) 包含同样stride公式及CFG_NZ调用；[CFG_NZ说明](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1alpha001/API/ascendcopapi/atlasascendc_api_07_0251.html) 声明不使能NZ2ND。
- 上述版本不是本机安装CANN9 header；实际9.0.0/A2-A3以正式编译/设备结果验证。没有使用仅350支持的L0C→UB接口。

## CPU及静态验证

`python3 tools/validate_tt_native_nz.py`：

- 440立即producer+440延迟MTE2/MTE1/MMAD+440 eagerMTE2调度，实际调用CFG_NZ Fake写入按32byte stride映射，每个有效/补零C与独立dense oracle一致，原读量/包数/credits/C0双槽/GM guards保持。
- 420原default false producer、160矩形和全部65536位模式通过。
- 9216实际NZ消费者：完整/奇数groups、M/N尾、全负、两AIV任意顺序、延迟DMA、credits后破坏性ring覆盖；初始pad/未写部分用大正值污染，实际mask保证不参与Max。
- 删除最后N列掩码的负控制被拒绝。
- 去掉新增helper并恢复两个调用片段后，整个kernel与父 `e1b3634` 逐字一致。host/workspace/UB不变，沿用父fake/公开8.3 6912/720/576容量证据，**本轮未重复运行host tiler**。
- 模型Fixpipe同步、A1 queue抽象、不是BF16舍入或完整硬件时序/性能证明。CANN9/NPU精度/时间PENDING。

## Validation Request

独立官方模板 `/private/tmp/bmmms-native-nz-official/project` 仅kernel替换，dry-run确认SHA/文件。代码 `84e830e` 已commit/push；正式任务 **`6abe3b9b694b590c3ce5450f`** 已创建，CANN/NPU终态PENDING。查询同一ID至终态，比较父C8 49.38/C9 67.48μs；勿重复提交。无收益或失败则归档并恢复父，不调相近输出格式参数。actual shape/plan/SoC/profile和重复A/B仍缺失，不据单次推断路径命中或稳定收益。
