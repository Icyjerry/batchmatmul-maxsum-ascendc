# Group-wide tiny K tree and repeated Max

## Evidence and structural hypothesis

The previous storage-native candidate `155fbd9` / SHA19cd486e passed native task `6abec499694b590c3c288b4a` 15/15 but did not improve small cases: C2=2.54 vs passed parent2.46, C3=3.16 vs3.11. No repeat/parameter scan; its result is archived in `TINY_STORAGE_VECTOR.md` and branch `experiment/tiny-storage-vector` / cec9a1b.

Actual source evidence: the first storage-native implementation repeats K-tree Add/PIPE_V and N Max for every query row. This candidate rearranges product scratch to `[K,B*M,pitchN]`, broadcasts the full query group, multiplies independent rows, then folds each K level across all rows at once and uses one repeated validN Max. It changes reduction scheduling and scratch lifetime; no tile/package/core parameter tuning.

For B1,M8,N64,K64, previous entry makes48 Add calls/K-level barriers,8 Brcb calls and8 WholeReduceMax calls. New entry makes7 Add calls (first level explicitly splits the16384 elements into16320+64),6 K-level barriers,1 Brcb and1 repeated WholeReduceMax. Mul calls remain8. These are source API counts, not native instructions or latency predictions. Expanded live scratch and strided stores may counteract the savings.

## Source and resources

Branch `experiment/tiny-group-ktree` derives from archived cec9a1b. Algorithm scope inverse restores entire passed baseline1734f16:102 added lines in three regions, kernel359932bytes, SHA `eeef7efc6189e9da80cbe9fae60901b51f7c73e4edc7806b4adbc23532218029`. No raw-bit transpose or failed TT experiments. Only kernel.asc algorithm changes; all seven other official project sources byte-equal1734f16; dry-run sends only kernel with this SHA.

- Same original plan/grid/batch grouping/paired offsets/GM/input/output contract. Only FF/TF tiny K32/64; other K/layouts and resource failures use baseline. This restriction comes from the complete binary K tree, not hidden case inference.
- Query Gather, if TF, packs every row into separate canonical query UB. FF reads canonical A directly. One batched Brcb sequence expands all query elements into8-lane blocks; repeat chunks capped255.
- Each query row's Mul writes into its slice of `[K,ar,pitchN]`; dst repeat stride is ar*pitchN/8 blocks. Actual stride>255 falls back. Immutable document `[K,pitchN]` reads keep their original row stride.
- All K products are ready before the common FP32 K tree. Add chunks capped16320 elements to avoid relying on oversized low-level repeats. Per-level PIPE_V separates true RAW dependencies; independent chunks/rows have disjoint writes. ValidN repeated Max executes only after completeK; original validM Sum follows, all-negative and paddedN semantics retained.
- Eight32byte rounded UB regions: combined16bit inputs, combinedFP32 cast, optional canonicalA, optional indices, ar*K*32byte broadcast, ar*K*pitchN*4byte products, ar*32byte rows,32byte sums. Host independently budgets all regions with1024 reserve and real UB capacity. Larger scratch means some previously selected frames safely fall back to original tiny; no retuning batch groups to force entry.
- Explicit inputready/outputready/terminalcompletion and Vector dependency barriers. No new GM path, metadata or synchronization flags.

Official CANN9 primary Brcb, BinaryRepeatParams, stride guide, Mul and PipeBarrier text was retrieved for the preceding candidate; links and limitations in `TINY_STORAGE_VECTOR.md`. Its native Pass verifies compilation on fifteen cases but does not establish which branch ran. This candidate's changed address strides and scheduling still require native verification.

## Independent checks

Reproduce `python3 tools/validate_tiny_storage_vector.py`. Production/TUNING each:

- 10080 shape/layout/group/exact-byte UB controls, one byte below budget rejects; stride and explicit tuning-pin fallback included.
- 7200 actual dynamic/constant integer entries;49344 active/6336 idle blocks. Three queued engine priorities, pairedB and tailgroup, FF/TF, K32/64, validN/negative maxima, unchanged parent arithmetic reference, unique y writes, immutable inputs and UB/y guards. Canonical cast-source checks include allN padding.
- 2292 actual encodedFP16/BF16 entries, group1/2/3 including raggedB=3/group2; independent FP64 golden roundedFP32 and parentFP32 order. MaxAbs9.53674e-7/maxNonzeroRel2.93038e-6 under mixedCPU tolerance1e-4+1e-4*abs(golden), not formal precision rules.
- 48 of7200 entries use a synthetic512KiB UB to exercise Brcb repeat chunks and Add chunk boundaries. This is a model capacity, not a claim about A2/A3 hardware. Other entries use192KiB; real guard still queries hardware.
- Eight negative controls rejected: missinginputready/outputready/terminalcompletion, wrongbatchoffset, incompleteK, invalidNmask, wrongbroadcast blockstride, wrongK destinationrepeatstride.
- Entire baseline scope inverse, git diff --check, otherseven source equality and CLI dry-run SHA checked.

An initial validation-script indentation error placed the eighth negative control after the temporary directory was removed; fixed the script, then the full verification completed. Kernel SHA was unchanged by this model fix. No softened controls/tolerances.

OneVectorFIFO represents command order, not every native hardware subpipeline. Software decoding is not native Cast/rounding, integer guards and samples are not exhaustive float coverage, CPU timing not reported as NPU performance. CPU log ignored `artifacts/tiny-group-ktree/cpu.log`, permissions700/600. No installed CANN/NPU on thisMac.

## Formal gate / next action

CANN9compile/nativeprecision/NPUtiming PENDING. Commit/push; one structural submission; saveID immediately and poll that sameID toterminal. Require15/15 and retain all15times. Compare against passed1734f16 and preceding structural result, keepC7/C14/C15 gains, do not attribute unchanged-route timing or claim route hits/SoC/profile/bestscore. Clearly large benefit only justifies unchanged confirmation; otherwise archive without nearby parameter scans. Main/tags unchanged; overallmajoroptimizationgoal incomplete.

Official task **`6abec72a694b590c3c296090`** created, implementation `df36ef3` pushed, kernel/template SHAeeef7efc unchanged. Query this sameID to terminal; native gates PENDING.
