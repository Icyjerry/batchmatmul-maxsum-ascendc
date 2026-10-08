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

## Implemented / final CPU PASS / native PENDING

Branch experiment/c10-direct-a2, kernel368813B/SHA256 `526d7f94b8aef59e82a91556fa311695cd9d90f39893662f638a58e2c9733d35`. Twoadded/tworemovedpredicate lines, no newdevicebody/API: M_BALANCE guardedFF bypasses3D andactivatesexisting strided2D onlyforA2. Tree8/defaultfalseinstances, M128/N256/K64, originalcreditordering/Vector/host/Plan/allocator/GM untouched. Wholeinverse equalsa2e6763; protected7 equals1734f16.

`python3 tools/validate_c10_direct_a2.py` finalexit0:

- 31actualproducer groups: full4096/1280/1152/20core;1/3/8/20/24/32core negative-tail/defaultfalse proxies; actualM16/32/48/64/80/128 andK1104/1120/1136 (lastK16/32/48). PhysicalNZ/ZZ/ZN, liveMTE2/MTE1/MMAD, everyfull-K C/paddedC, disjointowners/negativeMax-Sum/input/ringguards. Smallerproxygeometry is not a claim it passes the host selector.
- Fulltarget actualcounts: Ctiles200/MMAD3600/Bcopies3600/Binput58982400 unchanged; A3D0/A2D14400/A2elements23592960/B2commands14400. Parent3DAPI calls3600 are source-derived fromoneperMMAD; parentfulltarget notrerun. APIcallcounts do NOT identify lowered hardware instruction counts or time.
- Parentactualsource30sameproxygroups validatesold3D andsameelementvolumes; allother/defaultfalseinstance behavior preserved byconstexpr predicates, wholeoutside-changebyteproof.
- 96actualAIVownership/store+FinalizeRows andproduction/TUNINGeach192hostplans/ninehits PASS, syntheticmaxima/faketiler limitations explicit.
- FirstnegativeKoffsetcontrol wasnotrejected becausenegativeAfixtureisconstantalongK; no kernel failure. Added positiveK-varyingM80/N272/K256 actualreference, verifiedunmutated passes, thenNZpitch/ZZgap/Koffset/lastreader/L0ready/M_FIX sixcontrols allrejected. Initialfailedrunner logpreservedignored cpu-initial-failed.log; final cpu.logis authoritativeforgate.

ExplicitTQueAlloc-waits-lastMTE1-reader assumption persists; integerlayout testsarenotCANN9/BF16precision/hardwarequeue or latency proof. NoactualSoC/route/profile. NativePENDING/noIDyet. Original/fulltargetcache geometry andtraffic unchanged, more APIcalls mayregress.

Finalisolated/private/tmp/bmmms-c10-direct-a2/project protected7restored1734f16; dry-runonly368813B/SHA526d7f94 kernel. ONEformaljobaftercommit/push, saveIDbeforepolling, noidenticalrepeatformodestgain/noadjacentparameter scans. No gain/regression restoresa2e6763. Rawlogsignored artifacts/c10-direct-a2 dir700/file600.
