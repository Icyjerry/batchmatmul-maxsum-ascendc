# Native终态：四布局精度通过，完整op慢4.85%，恢复2073

实现ba24cd1/source9c29cf19540bd3c0e9364e9445e8e3076aa6af7f154db5e94e0a76fc2b5399aa。CANN9/9382 actual24AIC48AIV/caller20，DSOc88f3a71c8cf43ea057f72a1d8d783fce117e8f4d1bbacbfe03d590c407847d7；真实新符号half_mla40/单AIV，无Cube。

四layout各mixed-negative-mixed同context/stream/input地址完整FP64及input/yguard均精确通过。性能仅显式FP16/FF：parent2073/DSOca36五times `[2.600104,2.600104,2.060082,1.980079,2.060082]`us，中位2.060082；候选五times `[2.440098,2.640105,2.060082,2.160086,2.040082]`，中位2.160086，慢4.85437%。全部样本/default8表×5保留，不能删前两高值或称DVFS已证明。相同input/golden/plan/SoC绑定逐项一致。未预定<=1.8540738且所有五<1.980079门槛，归档并恢复完整2073，不扫初始化/stride/UB/K近邻、不重采/OJ。

五次核心均值的中位：Vector .427778→.441111us、MTE2 .500556→.522222、scalar .576667→.450000，计数重叠不可相加/作单因素因果。源码移除Cast阶段没有降低完整耗时。正式C2 dtype/layout仍未知，BF16/另一SoC/正式15候选NOT RUN。保留版正式820092 Pass15/398.92us保持。

原始完整包本地 `artifacts/c2-half-gather-mla/c2-half-mla-evidence.tgz`，目录700/files600；含完整父/候选五报告、四plans/四变化输入序列/全8份实际input及golden、候选source/DSOidentity/buildlog、采前gate。远端results/c2-*保留。CPU模型只对归档候选执行，恢复后应通过git show ba24cd1:kernel.asc在独立临时checkout运行，不修改模型去伪造parent通过。

## 以下保留实现及采前记录

# C2 half Gather + mixed FP32 products

## Hypothesis and scope

FP16 B=1/M=3/N=5/K=40 only, all four storage layouts. Formal C2 dtype/layout remain unconfirmed. Direct half Gather uses byte offsets 6*k and 10*k, then mixed `MulAddDst<float,half>` writes FP32 products. This removes the original Cast and FP32 Gather dependency stages. BF16 uses the original implementation because CANN9 mixed VMLA has no BF16 tuple.

The current candidate is source `9c29cf19540bd3c0e9364e9445e8e3076aa6af7f154db5e94e0a76fc2b5399aa`, +68 kernel lines over retained a11e2d9/2073. Original MakePlan/arena/other paths are unchanged. Source inverse and protected7 checked.

## Layout and precision contract

- Raw A: 3 padded half rows or one physical KxM block; raw B: 5 padded half rows or one physical KxN block. Exact source byte lengths, no input padding reads.
- Canonical K pitch 48 half elements (96B). Products pitch 48 floats (192B). Mixed repeats use dst stride6 / broadcast query stride0 / document stride3, in 32B blocks; 40 active FP32 destination lanes, 5 repeats.
- Initialize all 1152 FP32 product slots, then generate the 15 valid dot products. Reduce full K40, mask valid N5, sum the three row maxima using zero identities. Invalid N is never a maximum candidate.
- UB end6848B, guard reserves another1024B. Output only4B. No GM workspace or allocation.
- Guard rejects BF16, neighboring dimensions, other plans, GM misalignment, insufficient UB/AIV or tuning overrides. Both dual16/24 are allowed only with complete matching dimensions and K split/chunk.

## Evidence

CPU `python3 tools/validate_c2_half_mla40.py`: actual extracted entry, 536 full encoded-half fixtures/all four layouts, random and full-negative/last K8/last N winner/cancellation/large product/subnormal controls, FP64 full math. Defined UB, deferred DMA/one Vector FIFO/output, input/y guards. Eight faults rejected. This is a software stride/math model, not hardware scheduling or precision proof.

CPU `python3 tools/validate_c2_half_mla40_guard.py`: production 5 accepts/31 rejects and tuning 5/42, including dual24 acceptance, exact UB7872 boundary, AIV0/1 and alignment. Source7 unchanged.

CANN9/dav2201 compilation PASS on Ascend910_9382, actual24AIC/48AIV, caller20. DSO `c88f3a71c8cf43ea057f72a1d8d783fce117e8f4d1bbacbfe03d590c407847d7`; wrapper994e29f. Remote frozen `/workspace/bmmms-codex/imports/c2-half-gather-mla/kernel.asc`.

Native actual normalPlan for all four: vector-only final1/dual16/workers1/Ksplit1/Kchunk40/batchGroup8/microRows3/noGM. All four same-context/address mixed-negative-mixed sequences PASS, values .661040186882019 and -1.7459709644317627, exactly match FP64->FP32. Input/y guards pass. Full plan and raw outputs preserved under remote results/c2-{00,01,10,11}-half-mla-correctness. This is explicit FP16 fixture coverage, not hidden formal attribute confirmation.

## Performance gate fixed before candidate collection

Retained source2073/DSOca36: one default complete five-report profile, FF fixture. Candidate collection follows after the parent completes; require >=10% median reduction and all five candidate times below parent fastest. All five/default eight CSV tables and full input/output validation retained. Do not drop slow samples, resample unchanged source, tune nearby stride/UB/K parameters or submit OJ on failure. Other layouts' native performance, other SoC and formal15 PENDING. Formal retained 2073/820092 remains unchanged.
