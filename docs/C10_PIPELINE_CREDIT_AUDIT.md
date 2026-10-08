# C10 independent pipeline audit: defer GM write-credit acquisition

## Current evidence

Passed experimentalbaseline a2e6763/368782B/SHA16b51684 uses balancedactualM ownership, C10single91.53us. Full-M candidatec1a52ef/unique6ac7bcb6694b590c3c08ce0e Pass15 but178.32us was archived74f9937 and fullyremoved; not a basis for N/BM scans. Kernel currentlybyteequalpassedbaseline onexperiment/c10-pipeline-audit. No livejob.

Actual manual FF source has these ordered steps for each C tile:

1. CrossCoreWaitFlag(4+slot): acquire GM ring write credit.
2. Wait FIX_M(cFree): acquire L0C reuse credit.
3. Copy B / load A2-B2 / issue all K MMAD.
4. M_FIX fence, Fixpipe, FIX_M release and crosscore slot-ready.

The GM ring is only written at Fixpipe. Requiring GM credit before MMAD can block otherwise available Cube work while the previous AIV reads the same ring slot. L0C credit remains independently mandatory before accumulating. Existing retained C9 package producer already uses late ring acquisition, but its positive historical observation includes B packaging; this does not prove isolated wait-placement gain for FF.

## Independent hypothesis (not implemented/submitted)

Only on the currently guarded M_BALANCE FF route, defer its existing GM wait until all K MMAD have been issued and before M_FIX/Fixpipe. Preserve originalM128/N256/K64, fullA1, twoB1/twoL0/singleC/Max tree, all originalhost guards/Plan/GM/ownership and Vector byte-for-byte. All other template instances retain early wait, including old FULL_A behavior. No allocation, newevents or flagcount changes.

This reduces no mathematical work/inputbytes/launches; the hypothesis is overlap of Cube work with GM reuse waits, not a claimed bandwidth saving. Native latency/actual blocked-credit frequency/SoC/route remainunknown. Ring credit cannot replace C credit or data-readiness fences. Do not remove either side's acknowledgement.

## Required next execution

- Make only the guarded wait-placement change, prove inversefullkernel equalsa2e6763 and protected7 equals1734f16.
- Extend actual FF source CPU model so reused GM slots become writable only at an explicit consumer release; observe K work issued before blocked credit but verify no Fixpipe/write until acquisition. Preserve async liveMTE1/MMAD and originalC/input/guard/Max-Sum checks. Include negative controls for removed late wait, removed C wait and removed M_FIX fence; each must fail. No artificial CPU time used as latency evidence.
- Check default false/nonbalanced instances identical behavior and Vector/Plan/allocator byteunchanged. FullK and actualarena remain original balanced model.
- Only if these pass, commit/push/dryrun and oneisolated nativegate. RecorduniqueID immediately, querysameID toterminal. Compare all15, specificallyC10 parent91.53 but retain alladverse samples; no inferredroute/profile or controlledA-B claims.
- Clear regression/no benefit: restorea2e6763, archive. No neighboringwait/parameter scans or unchangedconfirm for modestgain.

No code change/nativecandidate exists for this hypothesis yet. The user prohibits Web; source audit uses retained teammate C9 and actual current source only.

## Implemented and CPU verified, native PENDING

Branch experiment/c10-late-ring-credit, kernel368904B/SHA256 `dcf715a21b2ec6fa8ec3ba27f13bd3b00216bbfdba88817103349174ee3b5337`. Threeadded/tworemovedlines: early GM wait excludesM_BALANCE; late wait includesM_BALANCE. Current guardedbalancedFF instance only; otherdefaultfalse/FULL_A instances retain their original predicates after constexpr evaluation. No geometry/host/Plan/allocator/Vector/math/inputvolume/newGM edits. Entire inversekernel byteequalsa2e6763, protected7 equals1734f16.

`python3 tools/validate_c10_late_ring_credit.py` finalPASS:

- 13actualproducer groups: full4096/1280/1152/20core plus1/3/8/20/24/32core negative-tail proxies, balancedanddefaultinstances. LiveMTE2/MTE1/MMAD physicalNZ/ZZ/ZN, all full-K C/negativeMax-Sum/input/ringbounds. Previousringgeneration remainsownedbybothAIVs until explicitmodelrelease, checkedbeforeeveryFixpipe. BothAIV release orders exercised, noFixpipeuntilbothcomplete.
- Candidate164blockedGM acquisitions, 2884K workissued beforecredit and2884executed whilepreviousGMstillowned, 5817344validAIVreads. The fulltarget accountsfor160blocked/2880Kwork; proxy subsetfourblocked/fourKwork. These countpermittedordering in a synthetic scheduler, not elapsedtime or actualNPU stallfrequency.
- Parentactualsource12proxy groups withsame release model: fourblockedacquisitions, zeroKworkissued/executedbeforecredit. Parentfulltarget notrerun; no claimedapples-to-applesfulltime comparison. Originalsource log's inherited13label is corrected to12inrunner; kernelSHA/validation unchanged.
- 96actualownership/store+FinalizeRows groups andproduction/TUNINGeach192actualhostplans/ninehits passed. Syntheticcompletedmaxima/faketiler limits unchanged.
- Fivefaultcontrols removedlateGMwait/Cwait/M_FIX/L0ready orreturnedcreditafteroneAIV; allrejected.

CPU TQueAlloc-last-MTE1-reader contract remains an explicitassumption. SequentialsyntheticAIVrelease is not hardwareprotocol/concurrency orBF16precision proof. FormalCANN9compile/15precision/actualroute/SoC/profile/latency PENDING. Rawignoredartifacts/c10-late-ring-credit/cpu.log, directory700/file600.

Isolated/private/tmp/bmmms-c10-late-ring-credit/project protected7 restored1734f16 andkernelSHAchecked. Dry-run only368904B/dcf715a2kernel. Next commit/pushthenonegate; saveuniqueIDimmediatelyandquerysameIDtoterminal. No repeatfor modestgain/noadjacentwaitscan.

Implementation **1a56211** pushed; uniqueformaljob **6ac7bfcb694b590c3c0ae962** createdonce, same368904B/SHAdcf715a2. NativePENDING, querysameIDtoterminal.

## Formal terminal: Pass15, no target gain, archive

Task **6ac7bfcb694b590c3c0ae962**, implementation **1a56211**, 368904B/SHAdcf715a2. Formalcompile/15precision passed, allprecision_ratio=1. Timesus:

`[1.91, 2.83, 3.14, 4.1, 5.22, 9.97, 8.07, 44.08, 67.5, 92.84, 88.37, 96.05, 13.18, 10.7, 9.37]`

Total **457.33us**, latestuserTbest calculatedmean **51.35378426**, notlive rank. C10 **92.84us** vsparentsingle91.53us (+1.43%) doesnotimprove thetarget. Noactualroute/SoC/profile/bounddevice A-B orGMwait frequency. Syntheticallowedoverlapdidnotestablish actualspeed. Allotherpoint fluctuations/adverseC6=9.97/C13=13.18/C15=9.37 retained; unrelatedroutes' improvements notattributed.

Archiveandrestorewholepassed **a2e6763** /368782B/SHA16b51684; noidenticalrepeat/nearbywait variants. CPUmodels/rawnativeJSON remainarchivedbranch/ignored artifacts/c10-late-ring-credit/official.json. Main/tagsuntouched, noactiveformaljobs. Independentnextaudit: actualFF A2loadinstruction/data-layout conversion, preserving currenttilegeometry/GM/Plan.
