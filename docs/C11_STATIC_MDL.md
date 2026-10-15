# Native终态：完整精度通过，中位仅改善2.58%，恢复2073

实现80bb3ed/source3bcc585a/DSO3c470ca010d4f7d5fcaad100915de0d0ec32b8692cc252cb1897a03dafaea8f1，wrapper994e29f。CANN9/dav2201实际编译PASS。一次正确性及五性能调用native fullFP64/Input/yguard均通过，116.72545623779297与parent逐位一致，abs7.6293945e-6/rel6.5361869e-8。

五default完整8表actualSTATIC_C11=true/20Cube40AIV/MMAD[160]*16+[128]*4全部确认。TaskDuration `[74.302971,75.042999,72.642906,73.282928,74.062965]`us，中位74.062965，对parent76.023041改善2.57826%，五次均低于父最快75.783028，但未预定10%门槛68.4207369。没有重采/扫描static字段、flags、block或step，没有OJ，恢复完整2073。FP16/全负/变化输入/另一SoC/候选正式15 NOT RUN。

相同input/golden/normalPlan/SoC精确绑定逐项通过。完整raw已下载artifacts/c11-static-mdl/c11-static-mdl-evidence.tgz（700/600），含两轮编译source/log/候选完整五报告及正确性/DSO身份/实际frame/input元数据/golden/采前gate；parent原完整报告保留artifacts/c11-mdl-output-audit。不是正式隐藏属性确认。原正式820092/2073 Pass15不变，整体冲榜目标未完成。

## 以下保留采前实现记录

# C11 MDL compile-time tiling metadata

## Hypothesis and scope

Parent a11e2d9/source2073/353255B, current formal820092 Pass15/398.92us. Exact C11 local fixture B1/M1536/N2048/K2048/BF16/TT on Ascend910_9382, actual24AIC48AIV/caller20. User confirms TT MDL family; formal dtype/exact shape remain local assumptions, not uniquely read hidden metadata.

Actual baseline BM256/BN128/BK64, stepM=N1/Ka=Kb4/depthA=B8/dbL0A=B2/C1/shareL1393216.96 tasks,20 workers, each gets4/5 output tiles,32MMAD per tile. Original all five MMAD counts `[160]*16+[128]*4`. No M/N/K tails.

Use SDK public `MatmulApiStaticTiling` as MM_CFG to let compilation specialize the EXISTING MDL input/load pipeline. Freeze precisely13 matching fields above. Keep all other fields default-1 and original cfg=DUAL_MDL_CONFIG, so original runtime values remain used. No retile, operand swap, full-A rewrite, N-pair, bank/layout flag change, altered handshake/arena/finalizer or new GM.

Actual CANN9 primary SDK evidence:
- include/adv_api/matmul/tiling.h public MatmulApiStaticTiling field defaults=-1 and cfg.
- impl/adv_api/tiling/matmul/matmul_constant_tiling_struct.h getters select constant iff field!=-1; otherwise runtime tiling_->field. This permits partial static metadata; we do not invoke internal APIs in kernel.
- impl/adv_api/detail/matmul/param/matmul_shape_tiling.h uses static tiling checks/L0 bounds and public MM_CFG type detection.
The type is in the public global namespace, not AscendC; compile verifies this rather than relying on guessed API namespace.

## Source and validation

Candidate SHA3bcc585af7ecd3f0203f50c5d5f7d02122b908ba508ee643f8ee152d5c27fd4b/355430B,45 added/2 changed kernel lines. New default-false STATIC_C11 template only changes the config binding. Entire MDL compute/Vector/events/partial/finalizer function body otherwise identical. Actual matching Shape/Plan/13 cube fields/cores/UB/L1/L0/system and ring capacity required; tuning overrides fallback. Both2-byte dtypes accepted if actualplan exactly matches; FP16 native validation is a separate later gate, not claimed now.

CPU `python3 tools/validate_c11_static_mdl.py`: production12 accepts/62 rejects, tuning12/73. Bothdtype/1,8,20,24,32 core-budget artificial plans, exact resource and one-byte-short, plan fields/workspace/pin fallback.13 constants and16 runtime defaults checked; source inverse restores2073 and protected7 byte-equal1734f16. This uses host stubs, not real SDK tiler or NPU math/scheduling.

First compile source41ddda11 failed: public type namespace guessed wrongly and early Launch hook referenced partial/workspace before declarations. Preserved frozen first source/buildlog; fixed actual public global type with value-init and moved hook directly before existing dual2 launch, after original pointers are declared. No SDK/template/test threshold modifications. This is compile/API repair before any native candidate collection, not a performance parameter scan.

Fixed source compiling in native_oj_like/build-c11-static-mdl-fixed, frozen imports/c11-static-mdl-fixed/kernel.asc; CANN9/dav2201. Native full precision/performance/OJ PENDING.

## Gate fixed before candidate collection

Existing same actual C11 parent full five/default8 table reports at artifacts/c11-mdl-output-audit/c11-baseline-profile.tgz. Source2073/DSOca36, seed1746 inputs/full golden116.7254638671875. Times `[75.783028,76.703072,76.423058,75.923035,76.023041]`us, median76.023041. New gate: median<=68.4207369 (>=10% reduction), and all five<75.783028; same exact case/input/golden/normalPlan/SoC binding required. No new parent sampling or dropping unfavorable samples.

First one native correctness, then one default complete five. Verify actual static=true symbol/20Cube40AIV/same MMAD counts, all outputs and guards. On failure archive/restore2073, no static-field/flag/block/step scan or unchanged resampling/OJ. If substantial benefit, add all-negative/input alternation/FP16 and further formal validation. Overall competition objective remains incomplete.
