# Supplied exact-shape image: host routing audit, 2026-10-08

## Source and limits

User supplies an image attributed to another probe: exact B/M/N/K and baseline us, without dtype/layout/SoC/CANN/script/formal task ID. Transcription: [CSV](teammate_probe/exact_shapes_user_1008.csv). Treat shapes as the new working assumption, not formal metadata. Baseline times are neither Tbest nor our current kernel times. Historical dtype/layout remain assumptions; C10 still has a conflict.

Passed kernel restored byte-equal1734f16, SHA a5eef105ef83a805315b3fbccf8bbe755fd33ef1ff330cfa4384324c4bd8e742. `python3 tools/audit_user_exact_shapes.py` extracts actual MakePlan, resource helpers and front SmallVector selector. CPU tiler stub: cores1/8/20/32, all8dtype/layouts, 480configurations. Stub capacities UB192KiB/L1512KiB/L0A-B64KiB/L0C128KiB. Not a real CANN tiler or device trace. estimated_entry explains relevant source branches, not a complete Launch simulator.

## 20 cores, historical dtype/layout assumptions

|Case|B,M,N,K|Assumed dtype/layout|dual / tree|BM x BN|workers / Nsplit / Ksplit|Estimated entry|
|---|---|---|---|---|---|---|
|C1|1,1,1,32|fp16/FF|15 / 0|0 x 0|0 / 0 / 1|dot_short|
|C2|1,3,5,40|bf16/TF|16 / 0|0 x 0|1 / 0 / 1|tiny_direct|
|C3|2,7,13,48|fp16/FT|24 / 0|0 x 0|2 / 0 / 1|tiny_grouped|
|C4|4,8,16,128|bf16/TT|28 / 0|16 x 16|4 / 1 / 1|small_vector_k256|
|C5|8,16,32,128|fp16/FF|19 / 0|16 x 32|8 / 1 / 1|single_tile|
|C6|13,23,73,192|bf16/FT|19 / 0|32 x 80|13 / 1 / 1|c6_direct_batch|
|C7|16,32,128,256|fp16/TF|3 / 0|32 x 128|16 / 1 / 1|c7_manual_frame|
|C8|1,1025,1031,1032|bf16/TT|33 / 0|128 x 128|20 / 9 / 1|tt_manual_frame|
|C9|1,2048,1536,1280|fp16/FT|20 / 0|128 x 128|20 / 3 / 1|case9_packages|
|C10|1,4096,1280,1152|bf16/FF (CONFLICT)|20 / 8|128 x 256|20 / 1 / 1|manual_full_a|
|C11|1,1536,2048,2048|fp16/TT|2 / 0|128 x 256|20 / 8 / 1|dual_mdl_library|
|C12|1,1280,4096,1536|bf16/TF|6 / 0|128 x 128|20 / 2 / 1|case12_packed|
|C13|1,8192,64,128|fp16/FF|3 / 16|128 x 64|20 / 1 / 1|manual_resident_b|
|C14|1,64,8192,128|bf16/FT|21 / 0|64 x 128|16 / 16 / 1|wide_n_manual_frame|
|C15|1,64,64,8192|fp16/TT|25 / 0|64 x 64|8 / 1 / 8|longk_split|

## Diagnosis changes

1. C13(1,8192,64,128), assuming FP16/FF, takes existing dual3/tree16/earlySum resident-B route. Archived C13 frame only selected dual14 tails, so this supplied shape is excluded. Its16.00us cannot reject removing TPipe from the actual resident route. Prior failed full-K/B residence algorithms remain archived; next frame must retain one B load/L0 residence and original full-K/GM/event lifetimes.
2. C11(1,1536,2048,2048), assuming FP16/TT, is dual2/BM128BN256/Nsplit8/workers20. Current TT frame only covers BF16 dual33. Design from this actual library route, not by blindly widening dtype/N guards without capacity/GM/synchronization proof.
3. C8(1,1025,1031,1032) has M/N/K8 tails and already enters TT manual frame under BF16/TT assumption. Do not substitute aligned1536 proxy shapes or repeat failed TT swap/paired-N/NZ scans.
4. C4(4,8,16,128), assuming BF16/TT, fits all8M rows in SmallVector UB. DIRECT_BATCH Cube measured7.81 vs original about4.08: clear regression archived, do not resubmit after seeing this image.
5. C6(13,23,73,192), assuming BF16/FT, is BM32/BN80/KP192. Existing dynamicKP DIRECT_BATCH selected, not fully constant BM32/BN96/KP192. Compare from the selected entry, not another nonmatching constant geometry.
6. C1/B1/K32, C2/M3/N5/K40, C3/B2/M7/N13/K48 narrow future independent model targets. C3 static-frame already formally showed no clear gain; do not repeat that structure.

Audit only, no new formal task. C4 task6ac736e7 terminal; no active task. Raw CPU CSV ignored artifacts/exact-shape-audit-1008/host.csv. Next executable action: inspect bmmms_manual RESIDENT_B and C13 earlySum; model its actual resident operand lifetime for a new explicit-frame route, retaining original full-K/GM. C11 is a separate later hypothesis.
