# C8 resident A: phased ready events

## Hypothesis

The retained TT producer waits for the complete1032-row A ND2NZ before its first K128 MMAD. Publish that same resident A in384/384/264 K regions, interleaved with the existing B package startup. Allow ready A regions to feed Cube while later A regions transfer. Preserve original A reuse across N, double B1/L0/C/rings, task order/geometry/GM/Vector. This differs from rejected full-input single-B buffer (54.17us) and resident-operand swap; no adjacent parameter sweep. User requests no Web.

Reference retained7492776/SHA0794a2bf, C8 latest46.87 and prior46.50/46.23; recent46.18–46.87. Candidate365948B/SHA256 `b87ec00643094e19c3c0433113480791494f8e00771887982a1766276d13e08b`,42additions/10removedkernel lines. All unrelated source restored by inverse replacement of one TT region and one Launch block. AIV body, Plan/allocator/GM/harness bytes unchanged. Default PHASED_A=false preserves old input stream.

## Implementation and invariants

New TTFrameReadAPhase writes `a1[k0*16]` with full1040-row NZ slab pitch, original GM[K,M] stride1025. Disjoint threeKregions stay in the same266240B A1. K-padding8 rows zeroed by original ManualZeroNZTail; each partial ND2NZ clears only D/M padding. Ready eventsMTE2_MTE1 IDs2/3/4; B IDs0/1 unchanged. MTE1_MTE2 ID2 still protects resident A's last reader before next M overwrite.

First worker tile input queue: A0→B0→A1→B1→A2, publishing each ready marker; waitA0 andB0 for first K blocks, then waitA1/A2 only at K384/768 on fresh-M tile. Next adjacentN tile reuses all already-ready A and never repeats those waits. At subsequent M changes existing B stream stays ahead; three A regions refresh original cache. FullK FP32 MMAD order unchanged, Max(validN) onlyafter completeK thenSum(validM). No new cross-core flags/barriers/GM routes/allocations/API names.

Select only exactuserC8dimensions1025/1031/1032 and original safe TT frameBM128/BN128/PK384/NT9. OriginalMakeTTManualFrame enforces BF16/TT/B1, actualcore/capacity/workspace/pin fallback. Original32Bmetadataunchanged. L1462848, L0A/B65536each, L0C131072, partialprefix41472/rings131072perworker, originalUB budgets unchanged. Native hidden dtype/layout and route hit not directly observed.

## Local verification

`python3 tools/validate_c8_phased_a_ready.py`

- production/TUNING each2160actualhostplans/fiveexacthits at1/3/8/20/32cores. Shape/layout/dtype/B exclusions, unchangedPlan/GM/resources, oldcapacity/AIV/pin fallback. Fake tiler is only host control evidence, not installedCANN9headers.
- 30actualproducer groups, including full exact C8 parent/candidate at20workers, smallerM/N proxies withfull1032K, K136default-path regressions, positive/allnegative, eager/delayedFixpipe, idleworkers. Every valid/padded C checked against independentfull-Kdot; originalinput/GM guards and balanced local/cross credits.
- Upgraded model to pending byte ranges and FIFO ready markers: waiting first A event cannot silently flush/publish all A. Exact candidate observed234deferred-MMAD snapshots with laterA DMA still pending, parent0. This proves overlap is *permitted in the synthetic order*, not elapsed-time benefit.
- Nine intentional faults rejected: first/laterAready, Bready, A/Breaderprotocol, L0/Creader, finalKhandoff, partial-NZwrongpitch. Reader/control rejection also checks flag balance; it does not prove every independent hardware race is detected.
- AIV unchanged byte-for-byte; no repeated fullconsumer suite for an untouched algorithm. Native15gate needed because new template instantiation still compiles its vector variant.

Source counts at20workers: A DMA26→78, B243 unchanged; total269→321 (+19.33%). A reads3172368 andB9575928 unchanged; MMAD729/Ctiles81 unchanged. Only largest blocking fresh-A region1032→384rows (-62.79%). This does NOT predict a speedup; extra DMA/events/control may erase overlap benefit. CPU integers do not emulate nativeBF16 roundoff; producer uses syntheticconsumer credits, not jointCube/AIVhardware proof.

First local harness compile lost existing CrossCore helper declarations while replacing its flag model; restored unchanged synthetic helpers. Kernel was not modified to hide that model error. Raw ignored artifacts/c8-phased-a-ready/cpu.log (700directory/600file).

## Native gate

CANNcompile/native15precision/latency PENDING; noIDyet. Isolatedproject/private/tmp/bmmms-c8-phased-a-official/project, protected7byte-equal1734f16, onlykernel changed. Commit/push/dryrun then ONE native gate; immediatelysaveID andquerysameID to terminal, no timeoutresubmission. Require all15Pass; preserve adverse observations and original C13 gain. OnlyclearlargeC8 observation outside parent range warrants ONE unchanged confirmation. No gain/regression: archiveandrestorewhole7492776, no nearbyphase-size or delaywait scans. SoC/actualhiddenplan/msprof unavailable; report these limits.
