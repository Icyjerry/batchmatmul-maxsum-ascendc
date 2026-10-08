# C10 independent audit: direct NZ-to-ZZ A2 loading

## Evidence / current state

Kernel restoredwholea2e6763/368782B/SHA16b51684 onexperiment/c10-a2-load-audit. PassedC10balancedownershipsingle91.53us retained. FullM178.32 andlateGMcredit92.84 didnot improve target; archived74f9937/44d25e2 respectively. No livejobs, no repeat/nearbytiling/credit scans.

Current guardedFF A2 path alwaysusesLoadData3D because RESIDENT_PAD is true. Its input alreadyhas resident NZ layout, andtheunchangedmanualbody contains directLoadData2D NZ-to-ZZ conversion as an alternatebranch, currentlynotreachableforthisguard. Tree2historydoesnot byitselfprove thisalternatewas tested: RESIDENT_PAD unconditionallyselects3D beforetree2canselect2D. Searchactual historicalsource before assuming a formalprobe covers this instruction change.

## Independent hypothesis (not implemented)

OnlyforM_BALANCE FF, bypass3DselectionandenableexistingK-major strided2D branch whenrows>count. Keeptree8/M128/N256/K64/fullA1/dualB1/dualL0/singleC/earlyGMcredits/Vector andallhost guards/GM/Plan unchanged. Do not change tree bits globally: tree2 alsochanges B2 logic elsewhere.

Existing directblockparams: lp.ifTranspose=false, lp.repeatTimes=rows/16, lp.srcStride=1, lp.dstGap=count/16-1; for eachki<count/16 LoadData(a2[ki*256],a1[ki*rows*16+k0*rows],lp). ForM-blockmi, eachdestinationblockindex is(ki+mi*(count/16))*256; sourceresidentNZblock is(ki+(k0/16))*(rows/16)*256+mi*256. Inner16x16 M/K values remainuntransposed. Thus physical NZ->ZZ blockordering matchesexisting3D output. Ifrows<=count, keeporiginalM-major directbranch. This algebra is an audit, not actualsourceCPU/nativevalidation.

At targetK1152 all18Kchunks are64. EachA2 conversion usesfourLoad2D calls versusoneLoad3D; totalestimated Acommands3600->14400. Inputelements/A2volume/MMAD/Ctilesunchanged. Morecommands can regress despite simplerhardwareprimitive/registersetup. No quantitative hardwarebenefit/bottleneckclaim; onlyformal gate can establish usefulperformance.

## Next execution

1. Make guardedselection changes only; wholeinversea2e6763/protected7proof, Vector/host/Plan/allocator byteunchanged.
2. Executeactualfulltarget FF producerandactual2D loads in existingdelayedMTE1/MMAD model; verify allC/paddedC, negativeMax-Sum, uniqueowners/arena/inputbounds. Ktail16/32/48, validM16/32/48/64/80/128; defaultnonbalanced/otherguard behavior unchanged. Count actualcommands/elementvolumes. Faultcontrols forNZpitch/ZZgap/k0offset/lastreader/L0ready/M_FIX mustreject.
3. CPUinteger layout/TQue assumptions separatefromCANN9/BF16/actualSoC/route/profile/latency. Ifpass, commit/push/dryrunandoneisolatedformaljob,saveIDbeforepolling. No immediate unchangedrepeatfor modestgain orN/K/M sweeps.
4. Clearregression/no usefulgain: archivewholechange/restorea2e6763. Main/tagsuntouched,goalremainsfullcompetition improvement.

No code/nativecandidate fordirectA2existsyet. NoWeb needed; usesactualretainedsourceandindependentphysical-layoutmodels.
