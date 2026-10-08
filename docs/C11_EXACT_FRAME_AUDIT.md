# C11 exact-boundary frame assessment (not implemented)

User image C11=(1,1536,2048,2048), missing dtype/layout; historicalFP16/TT remains assumption. Actualparenthost CPUstub: cores8/20/32 choose dual2/BM128/BN256/Nsplit8/window1/workers=min(cores,tasks). Core1 usesNsplit2/window2 and mustretainfallback. Existing hand-written TTFrame is type-generic but hostguards onlyadmit BF16 dual33; this suppliedFP16 boundary doesnot selectit.

## Proposed single structural direction

Reuse existing bmmms_tt_manual_frame<T> on this exactassumedpoint only, after actual capacity/core/workspace validation. Noaxesexchange, pairedN, workerMax or previouslyfailedNZ algorithm. Keep originalMakePlan/cache/allocation. A compact standaloneFrame may useBM64/BN256, BK64 fromtheexistingcode, 24Mtiles x8Ntiles, continuousM-major task ranges onoriginalworkers. OriginalFP32 fullK beforeMax/Sum preserved. This is switchinglibrary entry/packing/reuse task order, notscanning nearbyvariants.

### Original GM mapping remains viable

Originalpartialcount=Nsplit8 xMtiles12 xBM128=12288floats. ProposedTTpartialcount=Ntiles8 xpaddedM1536=12288floats, exactlythe sameprefix49152bytes andsameN-partition/m addressing. Originalworkers' dualC rings need2x128x256x4=262144bytes/worker; proposed2x64x256x4=131072bytes/worker, withinoriginal budget. NoextraGM pathway orlargerworkspace required. Need actualhostmodelsforallresource/plan/pin fallback before implementation, andverifyonecore/nonmatchingoldplansnever override.

### L1/L0/UB arithmetic from existing entry

A1=64x2048x2=262144bytes. TwoB1packages consume4x256xpackageKbytes. Actual512KiB L1 permitspackageK256 exactly; existing explicitframe needs noTPipe allocation inL1, anditscurrentguard accepts exactfit. Query realcapacity, capL1 byexisting512KiB rule, floor packageK byBK64; do notinfer installedheaders ornewbufferallowances. If loweractualcapacityonly permitsa smallerpackage, definefitting scope/predicate beforecandidate, do notparametertrialscan.

DoubleL0A=4x64x64=16384, doubleL0B=4x256x64=65536, doubleL0C=8x64x256=131072bytes. UBproducerC/row=4x64x256+4x64=65792bytes; postbarrier12,288float Npartial merge is49152bytes plusaligned24group sum/smalloutput, withinoriginal192KiB stub. These are memorycounts, not runtime/throughput predictions.

Afull-K L1 read is amortized across adjacentNtiles bycurrentTTframe; M64 halvesA residency footprint versuslibrary'shostBM128, increasesMtilecount and mayincreaseBtraffic. No msprof/SoC/realtiler data; exactwinner notknown. Formaltimingmust decide.

## Next executable steps

AfterC13confirmationterminal (nowcomplete), branchfrom retained7492776-derivedhead/SHA0794a2bf. Add a narrowactual-hostFrame helper andLaunch overrideonly, reuseexistingdeviceentry byte-for-byte. Prove wholeparentinverse (retainingC13gain), full actualMakePlan/core/workspace fallback, andexistingactualCube/AIV modelsat64x256,K2048 with package boundaries/full-M proxy andraworiginalringprefix. Native15precision+alltimingsuniquegate; clearmajorbenefit onlywarrantsoneconfirmation. NoC11candidate orformaljob existsyet.
