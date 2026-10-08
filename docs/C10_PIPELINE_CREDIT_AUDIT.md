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
