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
