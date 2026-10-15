# 当前进行：C5完整FP16批次改纯Vector，四布局native精度过，父性能对照中

experiment/c5-half-vector，sourceeb1ac4bd/356572B，50 added kernel lines over正式保留2073。新entry bmmms_c5_half_vector：B8/M16/N32/K128/F16/all4layout，每批1AIV，half Gather+两次64-lane混合FMA完成全K128→MaxN32→SumM16，直接4B y，无Cube/GM similarity交接/全核同步，原arena/MakePlan不动。BF16回原，UB159328+1024、实际core/plan/alignment/pins guard。不是旧C6 Vectorpairs或同点C2扫描。CPU320 entries+9fault/guard4/41及4/52/inverse/protected7通过。

用户新SSH已恢复master38319/pid20843，旧89986连接断开255不代表编译失败；实际原buildlog/DSO确认CANN9编译完成，不重启。DSO9f340062/wrapper994e29f/sourceeb1ac4bd。实际normalPlan FFdual19，其余dual3；其它字段相同，8Cube/原MIX11，均已逐项审查。四layout各mixed-negative-mixed同地址native全FP64/input-yguard通过，FF abs2.38e-7/negative9.54e-7。81042包含00成功和01 frame缺文件的工具失败（尚未launch），76810在实际frame审查后01/10/11均成功；无重复已成功00。

NEXT poll exec10384：原parent2073/DSOca36的01/10/11三layout一次完整default5采集中。FF parent已完整五[4.840194,4.460178,4.880195,4.580183,4.580183]median4.580183（actualMIX11/8AIC8AIV/每核1MMAD），raw全本地artifacts/c5-vector-audit。采候选前已冻结四layout独立准入>=20%median且全五低于各自父最快（FF<=3.6641464且全五<4.460178）；全5/default8表/精度/输入-yguard/实际pureVector8符号必须过。无static参数/UB/stride/K/flag扫描或重采。各layout未达回原，全部失败恢复2073，无OJ；有大收益才继续范围/正式15。详见C5_HALF_VECTOR。正式C5 dtype/layout未知，勿把FP16fixtures当hidden确认。

目前尚无candidateprofile/OJ。元数据/源码/CPU工具已可接手。新入口privateconfig、askpass删除、scp-O；9382/24AIC48AIV/dev0physical14/CANN9/caller20。C11常量metadata2.58%已归档c628c2e，不复做。整体goal active未完成。

## 以下保留历史交接（当前以上段为准）

# 当前终态：C11常量metadata通过native，仅2.58%，恢复正式Pass15保留版

experiment/c11-static-mdl，当前kernel逐字a11e2d9/2073/353255B；正式820092 Pass15/398.92us保持，无新OJ，goal active未完成。80bb3ed/source3bcc585a保留完整实现；CANN9编译/native一次+五fullFP64/input-yguard通过，真实STATICtrue/20AIC40AIV/MMAD[160]*16+[128]*4不变。

五times[74.302971,75.042999,72.642906,73.282928,74.062965]median74.062965 vs parent76.023041，改善2.57826%但未原10%gate68.4207369，已恢复2073。无重复/static字段/flags/block/step扫描/OJ，失败结构归档。Raw全本地artifacts/c11-static-mdl/c11-static-mdl-evidence.tgz，700/600；详见C11_STATIC_MDL。编译75928首轮exit2（API修复前）、46296修正exit0、native82802和download48719均终态0。

NEXT 可独立评估未测C5：用户shapeB8M16N32K128、dtype/layout未确认，先明确本地fixture并实读normalPlan/profile。原SmallVectorK256Rows刻意排除M>=16且N>=16；C5现在Cube MIX11。若实际C5 MMAD远小于跨单元交接时间，评估完整批次纯Vector直接写y是否比Cube交接更省；这是不同于已失败的C6 B13M23N73K192 Vectorpairs，不将其失败改名重做，不先凭静态FLOPS宣称提速。尚无C5候选/设备实测。其它已归档方向见前序，不复活。

SSHmaster57930/pid13934本turn有效，queue在native终态后重查空且ps无job/msprof/bisheng，9382/24AIC48AIV/dev0physical14/CANN9/caller20；下次先查实际状态。askpass已删，scp-O，凭据不入Git。

## 以下保留历史交接（当前以上段为准）

# 当前进行：C11原MDL常量tiling配置，CPU过、设备编译中

experiment/c11-static-mdl，候选3bcc585a/355430B、45增2改 kernel lines。实际CANN9 MatmulApiStaticTiling公开类型，13字段冻结为actualC11 256x128x64/step1,1,4,4/depth8,8/db2,2,1/L1393216，余字段-1回runtime，DUAL_MDL_CONFIG原值不动。非换tile/输入转置/旧full-A/N-pair/GM新通路，原MDL所有计算/事件/归约body保持。formalC11属性仍明确假设，本地BF16TT。

CPU tools/validate_c11_static_mdl.py：12/62及12/73实际guard反例/容量边界、13constants/16runtime defaults/wholeinverse2073/protected7 PASS；不是native证据。首compile75928源41ddda11因namespace/早hook错误exit2，已保留；修正source3bcc585a新独立目录。

NEXT poll exec46296，actualbisheng进程已确认live；native_oj_like/build-c11-static-mdl-fixed，log /workspace/bmmms-codex/c11-static-mdl-fixed-build.log，frozen imports/c11-static-mdl-fixed/kernel.asc。成功后写source/DSO/wrapper994e29f identity→原c11.json/c11.complete_frame/inputs/c11一次correctness→一次default完整五。采前gate<=68.4207369且全五<75.783028，对parent76.023041（原五[75.783028,76.703072,76.423058,75.923035,76.023041]）。要求statictrue/20AIC40AIV/MMAD[160]*16+[128]*4不变。失败恢复2073、不扫static字段/flags/block/step、不重采/OJ。详见C11_STATIC_MDL。

当前无NPU/OJ job，master57930/pid13934实际有效，queue本turn重查空，设备9382/24AIC48AIV/dev0physical14/CANN9/caller20。正式保留2073/820092不变。前轮C2半精度Gather已失败归档371556b，不复做。目标active未完成。

## 以下保留历史交接（当前以上段为准）

# 当前终态：新SSH恢复；C2新混合流水完成native但变慢，恢复保留版2073

- experiment/c2-half-gather-mla；当前kernel逐字a11e2d9/2073f48e/353255B，正式820092 Pass15/398.92us保持，本turn无OJ，整体冲榜目标active未完成。
- 新结构ba24cd1/source9c29cf19/DSOc88f3a71：FP16 B1M3N5K40/all4storage，half Gather+Tuple<float,half> VMLA省Cast/FP32Gather。CANN9编译PASS；CPU536+8faults/actualguard5/31和5/42/inverse/protected7通过；四layout各mixed-negative-mixed同地址native完整FP64/input/yguard精确通过。正式C2 dtype/layout仍未知，BF16明确回原。
- 一次FF default8表×5实际half_mla40/vector1，无Cube。parent2073/ca36五[2.600104,2.600104,2.060082,1.980079,2.060082]median2.060082；新五[2.440098,2.640105,2.060082,2.160086,2.040082]median2.160086，慢4.85437%，未预定<=1.8540738且全五<1.980079。已恢复2073，不删高值/重采/初始化或stride/UB/K扫描/OJ。Vector .427778→.441111us，scalar下降未变成完整收益。详见C2_HALF_GATHER_MLA。
- 所有raw完整下载artifacts/c2-half-gather-mla/c2-half-mla-evidence.tgz，700/600；含四完整plan/四序列/全部8份input及fullFP64/父与候选5×8表/source/DSOidentity/buildlog/采前gate。native编译82714/四correct+parent45886/candidateprofile28061/download45799均terminal0。
- 新SSHmaster57930/pid13934曾实际有效，新授权已写privateconfig、askpass删除、scp-O；9382/24AIC48AIV/logical0→physical14/caller20。下次先核对socket/真实queue/ps，不沿用本次启动前空队列假称现在空闲。
- NEXT：当前没有可提交新优化。先比较已下载完整PMU与保留kernel实际设备源码，寻找能减少真实临界路径的新结构；不复做C1mixed32、C2halfGather、C3flatten、C4compact、C6raw/compactNZ、C9LEFTFmatrix、C11Cᵀ、C15twoMMAD/row/collective及停测C8等已归档方向。新候选先明确shape/属性假设、实际完整plan、SDK依据和可复现gate，再写源/CPU/native；不能把历史评论耗时当本轮实测。

## 以下保留历史交接（当前以上段为准）

# 当前：新 SSH 已恢复，C2 half Gather/mixed FP32 原生精度通过，性能对照中

experiment/c2-half-gather-mla，source9c29cf19/+68lines over retained2073；CANN9/9382/24AIC48AIV/caller20已编译，DSOc88f3a71。CPU536/all4layout+8faults、guard5/31及5/42、inverse/protected7通过。Native四layout各mixed-negative-mixed同地址三调用full FP64/output/input guards精确通过，真实plan dual16/vector1/noGM。正式C2 dtype/layout未知，勿把FP16fixture冒充隐藏配置；BF16回原。详见C2_HALF_GATHER_MLA。

NEXT poll exec45886（四correctness已终态0，现parent FF default8表×5 profile进行中）。父source2073/DSOca36。父完成先冻结gate=median*.9且所有五<父最快，再采候选一次default5，actualsymbol必须half_mla40/1AIV。失败归档恢复2073，不重采/扫近邻/OJ；成功才进一步提交门槛验证。新SSHmaster57930/pid13934有效，config已更新/askpass删除，scp-O。当前无OJ。原正式任务820092/2073 Pass15保持，整体目标active未完成。

## 以下保留历史交接（当前以上段为准）

# 最新连接状态：本turn验证已完成后master断开，备用授权重连被拒

本turn C9与C1所有任务已terminal0、raw完整下载、kernel已恢复2073并push8e9d473；随后最后检查control socket缺失、pid9058不存在，原master63301已terminal（内部SSH exit255）。使用用户备用授权+原root认证干净重连实际platform authorization denied，askpass已删除，private master-reconnect.log0600。已异步请求新入口，无需重复root密码。这是完成本turn设备工作之后的新阻碍，不把前序已解除的blocked直接沿用；当前goal仍active，不标完成。

远端queue最后一次实际检查为空发生在master断开前，目前未知；我方无未终态NPU/OJ job，不能凭旧queue文件说现在verified wait。接下来可独立准备C2 half Gather+mixed FP32 product模型（API已有实际SDK依据），新入口后先核对真实plan/设备/queue及完整parentprofile，再验证一个新候选；不重启本turn已完成任务。

## 以下为完整实验结果与下一方向

# 当前终态：C9及C1新结构均完成native，恢复正式Pass15的2073

- 当前experiment/c1-mixed-fp32-mac，kernel逐字a11e2d9/2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b。正式已确认任务820092/6ad046feaad397b6d98aa318 Pass15/398.92us，本turn无新OJ。目标active且未完成。
- C9 LEFT FMatrix：05c86ea/source4693eb7a/DSObf4054fe，真实Ns5/window3，55.142204→54.662186仅.8705%，原全部90/100MMAD/input-yguard/full精度通过但未10%gate，归档f06d202；stall分类改变并非大加速。stationary-B模型最忙核GM和9/10tile分布不变，取消未写。
- C1 mixed half->FP32 VMLA：9258c49/source43dbf4f3/DSO99fe6c90，CANN9/native5call+subnormal4call全通过。maxproduct4290774016/smallproduct1.1920929e-7/negative-32/minsubnormal*.maxhalf=.1249389648/maxsubnormal*.maxhalf=127.8125610全bits精确；mixed与原parent一致.27248996496。保护inputs/yguard完整。
- C1一次default完整8表×5 actualmixed32/pureVector1，times[1.880075,1.900076,1.600064,1.560062,1.560062]median1.600064，原median1.600064相同。未1.4400576且全五<1.560062门槛，不删前两高值、不重采/扫UB/stride/K/清零位置/OJ，恢复2073。FP16混合模式只证明这些native范围控制；all63488编码只CPU，勿冒充NPU穷举。
- raw完整本地artifacts/c9-stationary-b-audit、c9-left-fmatrix、c1-mixed-fp32-mac（源码身份/全报告/guardbits/5stress输入reference/两个序列/buildlogs），700/600。C1compile82517/correct86512/subnorm77876/profile86733/download28862均terminal0，queue再次实际空。master63301/pid9058有效，私有config备用授权已更新/askpass已删，scp-O。正式15/另一SoC未跑。
- **NEXT 新依据**：实际CANN9 GatherImpl支持half等2B类型（kernel_operator_vec_gather_impl.h），可直接half Gather整理物理布局，再Tuple<float,half> VMLA生成FP32产品，避免tiny原Cast+FP32Gather整条转换；非旧raw-bittranspose/scalar-cache/C1K扫描。先生成明确C2 FP16/alllayout fixture并读取真实normalPlan/完整parentprofile，C2正式dtype/layout未独立确认只能按fixture报告；评估half-offset/stride/K40尾与完整product0，再一个新guarded结构验证。BF16混合VMLA不支持必须回退，别借2B Gather冒充支持BF16乘积。

## 以下保留历史交接（当前以上段为准）

# 当前进行：C1混合half输入直接累加FP32，CPU过/CANN编译中

- experiment/c1-mixed-fp32-mac，当前kernel43dbf4f3a4d0f35ec6536123f5d4f14a214d4de4ff666fd1072ab2126f917e86/355211B，**未native候选**，从2073/a11e2d9派生。正式保留2073 Pass15/398.92us不变，无新OJ。
- 新实际SDK依据MulAddDst<Tuple<float,half>>，不是旧floatfloat MLA或scalarcache：prod0与input64B×2DMA重叠，MTE2ready后直接混合VMLA，省Cast依赖阶段；fullK32 ReduceSum/4B y/events/PIPE_ALL保持。只FP16B1M1N1K32、实际guard/GM32B对齐，BF16回原。M=N1四storage同物理顺序。新UB288B，无新GM/plan变更。
- CPU actualentry2115编码fullK/all63488finitehalf/随机/大乘积/小乘积/全负+5faults/guards/inverse2073/保护7PASS，actualguard25/36反例/四flags/UB/AIV边界通过。CPU混合FMA语义是假设，必须native证。
- **NEXT poll exec82517**：CANN9/dav2201 compile，imports/c1-mixed32-43dbf4f3a4d0/kernel.asc；build-c1-mixed32，log/workspace/bmmms-codex/c1-mixed32-build.log。stress输入准备完成、旧normal未改。编译成功写DSO identity/source43db/wrapper994e29f，原c1.json/c1.complete_frame/inputs/c1跑job correctness --input-sequence native_oj_like/c1_mixed_input_sequence.json（mixed→max65504^2→tiny32*(2^-14)^2→negative-32→mixed）。
- **关键必须**：完成sequence后检查actual_with_guard第1/2/3次首4B与各stress golden.f32完全一致，tiny值不能让普通atol容忍0。没有native精度/性能结论。然后一次default8表×5，actual bmmms_dot_short_mixed32/pureVector1。原baseline完整五[1.960078,2.000080,1.560062,1.560062,1.600064]median1.600064，source2073/DSOca36，raw在c1-scalar-cache-dot包。
- gate采前<=1.4400576且全部五<1.560062、fulloutputs/input-yguard/三stress exact后才考虑正式15。失败恢复2073，不扫UB/stride/清零位置/K、不重采/OJ。详见C1_MIXED_FP32_MAC。
- C9前序已归档f06d202：FMatrix新true精度/5报告过但55.142204→54.662186仅.8705%，stall分类改变非大加速。raw全本地；其compile/native/profile均terminal0。当前只有82517编译，无NPU/OJ；master63301/pid9058有效、备用授权私有config已更新/askpass删除/scp-O。

## 以下为历史交接（当前以上段为准）

# 当前：C9原生验证终态，恢复正式Pass15保留版

- 当前experiment/c9-left-fmatrix，kernel逐字a11e2d9/2073f48e，正式Pass15/398.92us不变。新source4693eb7a保存在05c86ea，native仅改善0.8705%，已归档，无新OJ。
- 实际C9parentFP16NT/1,2048,1536,1280/9382/24AIC48AIV/caller20，dual36/128x128x128/Ns5/window3/Kchunk256/W20；fullgolden191.8094940185547，五times[55.142204,54.922195,56.122246,55.062202,55.382214]median55.142204，实际9/10tile各核均衡。stationary-B模型最忙核GM字节不变，取消未写。
- LEFT FMatrix复用候选CANN9PASS/DSObf4054fe，首次及五fullFP64/input-yguard通过，actualtrue/20Cube40AIV/每核MMADpattern不变。times[54.662186,55.342213,53.322132,54.662186,54.622185]median54.662186，未10%及全五门槛。不重采/扫FMatrix或K参数/OJ。MTE1stall下降转为Cube stall，活动MTE1/MAC不变，是不能以stall单项作加速结论的反例。
- raw全本地artifacts/c9-stationary-b-audit及c9-left-fmatrix，700/600。plan33301/parentCorrect81085/parentProfile93219/原download13714、新compile35373/native14509/profile95861/download35588均terminal0。当前无活跃NPU/OJ，master63301/pid9058实际仍有效，备用授权更新私有config/askpass已删/scp-O。
- **NEXT新依据**：实际CANN9 dav_c220 MulAddDst支持Tuple<float,half>。研究C1FP16 K32用混合vmla直接生成FP32乘积，prod清零放在输入DMA期间，省Cast依赖阶段；BF16明确不支持仍回退。必须证明真实mixed stride/大half乘积在FP32不溢出/完整精度和default五报告。不是旧C4 floatfloat compact MLA或C1scalarcache。尚未写代码/无速度结论。勿复做C9相邻N共享A既有反例。整体目标未完成。

## 以下为历史交接（当前以上段为准）

# 当前进行：C9 LEFT FMatrix复用，CPU已过/CANN编译中

- experiment/c9-left-fmatrix，kernel4693eb7a60827baa354522fe83748eb0c00313459a6f4c9d713e59c429c183f0/354840B，尚未native候选。正式保留2073/a11e2d9仍Pass15/398.92us。用户已将goal控制状态active。
- C9真实parent plan已采：FP16NT1/2048/1536/1280、dual36/BM128BN128BK128/Mt16Nt12/Ns5/window3/Kchunk256/W20，原ca36DSO/9382/24AIC48AIV/caller20。一次及default5全报告/完整golden191.8094940185547/input-yguard通过。times[55.142204,54.922195,56.122246,55.062202,55.382214]median55.142204，actual20Cube40AIV/每核90或100MMAD。
- stationary-B按新真实plan审计每核tiles已9/10均衡，总input字节只省1.7857%且最忙核相同，取消未写该kernel。新候选仅启用原C10现有FMatrixLEFT复用到C9 NT：A SetFmatrix每refresh、K128 Load3D不resetFmatrix/pad，B2D不动LEFT。padding原entry0；原全K/加载/MMAD/Vector/credits/arena/MakePlan/其它分支保持。
- Actualhelper62914560地址tag/1920Kpanels新旧一致、设置1920→32/4faults，guard48/59+8/20/24/32预算/容量临界，wholeinverse2073/保护7PASS。不是native或时间证明。详见C9_LEFT_FMATRIX。
- **NEXT poll exec35373**：真实CANN9/dav2201 compile，remoteimports/c9-left-fmatrix-4693eb7a6082/kernel.asc；build-c9-left-fmatrix；log/workspace/bmmms-codex/c9-left-fmatrix-build.log。成功后写source/DSO/wrapper994e29f identity→原c9.json/c9.complete_frame/inputs/c9一次correctness→一次default8表×5。原CubeMMADpattern不变，新last-template-bool=true，20Cube40AIV。gate预定median<=49.6279836且全五<父最快54.922195，全部精度/guards后才补全负/同地址序列/正式15。失败恢复2073不扫附近参数、不重采/OJ。
- 原parent plan33301/correct81085/profile93219/download13714均terminal0，raw已本地artifacts/c9-stationary-b-audit700/600。新native未启动，无OJ。前台SSH master63301/pid9058仍实际有效；用户新备用授权仅更新私有config，askpass已删/凭据不入Git，scp-O。

## 以下为历史终态（当前以上段为准）

# 当前终态：新SSH恢复，C15 Cube collective验证完成，恢复正式Pass15保留版

- 分支experiment/c15-cube-collective，当前kernel逐字a11e2d9/2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b。正式Pass15任务820092/6ad046feaad397b6d98aa318总398.92us仍是已确认提交，本次无新OJ。
- 用户新入口已实际恢复连接：host2ef29bca0f61、9382/24AIC48AIV/dev0physical14/CANN9/caller20；当前master63301/pid9058，私有config更新且askpass已删。旧blocked/platform denial记录均为历史，不再当当前阻碍。
- sourceca66a541/ccfaecc完整候选native终态：CANN9编译PASS、DSO85f8f7296db8f27ec0a1ec59ecc21b3fc5c274ccae4fe0895c91cb77d88a6607、wrapper994e29f。首次及同context/stream/输入地址mixed-negative-mixed全PASS，input/yguard完整；混合精确/负值abs3.8146973e-6。
- default五完整8表/actualtrue/8Cube8AIV/每核8MMAD确认。times[9.980399,10.260410,10.660426,10.040401,10.360415]median10.260410，与row-only完全相同，未观察新ready协议额外中位收益。对parent10.940437的6.2157%是旧row结构已有收益，不能归新protocol。未原10%+全五快于父最快门槛，恢复2073，无重采/OJ/flag或参数扫描。
- raw全部本地artifacts/c15-cube-collective/c15-cube-collective-evidence.tgz，summary/pmu-summary同目录，700/600；包含实际首次/交替/五报告/DSO身份/buildlog。原脚本75161、下载58231 terminal0，远端queue已再次实际空，无活跃任务。
- **NEXT**：停止C15现有collective/row/BK/split近邻方向；只有证明全新结构才另开候选。继续优先关注tiny/C6得分差距，但勿复活旧bit transpose/Gather/storage-Ktree/纯Vector或旧C8参数。刚复查26beaac：原bit transpose主要tinyK<=64，正式C2严重退化，无新C4 native依据，未据此再写另一个相同transpose候选。需要新源码/真实PMU依据。全局目标未完成；get_goal的控制状态仍blocked，工具不能主动改active，但实际服务器障碍已解除并已完成本次授权设备工作。

## 以下保留历史交接（当前以上段为准）

# 当前已恢复连接：C15 Cube collective冻结包正在编译

- 用户提供新授权后实际连接成功，hostname2ef29bca0f61，npu mapping逻辑0/physical14/card7chip0保持，实际queue为空且ps无旧job/msprof/build。前台master exec63301/pid9058，私有config已更新；临时askpass连接后已删除，凭据不入Git。原访问阻碍已解除，下面blocked记录均为历史。
- **NEXT poll exec75161，不要重启**：已上传冻结63748B/0de34414包到/workspace/bmmms-codex/imports/c15-cube-collective-ca66a5417b3b/，解压c15-cube-collective-validation。脚本已确认source/harness/frame/两input/golden身份，现在实际CANN9/dav2201编译中（ps确认bisheng活跃），build-c15-cube-collective。日志在包内build.log。
- 成功后原脚本自动只跑一次correctness→mixed-negative-mixed→default五报告，队列沿用/workspace/bmmms-codex。实际source路径为包内source/kernel.asc（ca66a541），不是旧文档预想的imports根文件；DSO identity将绑定实际路径。没有新OJ，native/perf仍PENDING。
- 原不变gate：median<=9.8463933且全五<10.540421、完整精度/全负/变化输入/guard通过才考虑正式15；对正确parent10.940437及row-only10.260410都报告，不降低门槛。新代码无改动，仍ccfaecc/ca66a541。注意get_goal控制状态仍blocked，当前用户提供新入口已实际恢复工作；工具不能主动改active，不据此假称服务器仍受阻。

## 以下为历史交接（当前以上段为准）

# 当前阻碍：等待新的云平台 SSH 授权入口

恢复后连续三个goal turn遭遇同一远端访问阻碍；前两turn已完成候选CPU协议检查/提交与冻结验证包，本turn再次核对工作区clean/7b65ab5、kernelca66a541、bundle0de34414均未变。干净SSH仍exit255/Connection closed by UNKNOWN port65535；此前platform authorization denied是历史明确诊断。本机bisheng/npu-smi均不存在。无可确认的活跃远端任务handle，queue未知。

当前候选未经CANN/native，不是已通过最优。离线可执行准备已经完成，按项目约定不再叠加未上板算法、不以CPU代替native、不绕过采前大收益门槛提交OJ。下一条实际必需动作是用户刷新云平台授权并给新SSH入口（不需重复root密码），随后执行下文冻结包验证链。此前异步请求仍待答。保留全部scope和冲榜目标，不称已完成。

## 以下为完整候选与验证包交接

# 当前进行：C15 Cube端ready集合，CPU已过，待刷新SSH后编译

- experiment/c15-cube-collective，当前kernel356814B/SHAca66a5417b3ba41d6dd86231e4f3e36fb28dc6ca7df9feb854c1218bee872583，**未经CANN/native验证的实验候选**，不是已确认最优。正式Pass15保留版仍a11e2d9/2073f48e，任务820092总398.92us。
- 从已验证按行8AIV版本81f49ff只改变producer-ready：Cube完成原Fix后mode0 PIPE_FIX flag8全Cube set/wait→mode2 flag9通知各AIV；Vector仅wait9直接进原row finalizer，消除初始AIVbarrier，末尾AIVbarrier不动。原数学/8MMAD/Ksplit8/GM/资源guard逐字81f49ff。不是把two-MMAD与row收益相加。
- 实际CANN9 dav_c220 SyncAllImpl<false>/SetNextTaskStartImpl已有同AIC mode0集合pattern，SDKflags11..14与本8/9分离；全8Cube参与由精确guard保证。mode作用域/运行时配置/消息退休必须native验证，不凭CPU模型宣称硬件正确。
- tools/validate_c15_cube_collective.py：实际协议8producer+8consumer/8种延迟完成顺序/全partial就绪后才允许AIV读、每Cube集合与每AIV配对消息各消费一次/4fault controls/source inverse整81f49ff/保护7 PASS。actual guard production54/TUNING65+容量临界PASS。完整row数学已有81f49ff native证据，未重采。
- 暂停/恢复后旧CPUhandle33625/52590 Unknown process id，恢复新31922/37085 terminal0；原SSH master/control socket消失，干净重连platform authorization denied（无密码错误），已请求刷新入口。上次queue空是在暂停前，**当前远端queue未知**，无新NPU/OJ启动。private reconnect-current.log0600，凭据不入Git。
- **NEXT**：等新入口→检查真实master/queue/ps→冻结imports/c15-cube-collective-ca66a5417b3b/kernel.asc→独立build-c15-cube-collective（wrapper994e29f/原CMake，不改保护7）→绑source/DSO identity→c15.json/c15.complete_frame.json一次correctness→原c15_input_sequence mixed-negative-mixed→一次default8表×5。actual<half,true,true>/8Cube8AIV/每Cube8MMAD。CANN/native/性能/正式15全PENDING。
- gate采前保持median<=9.8463933且全五<父最快10.540421、完整精度/全负/同地址变化/guard后才正式15；另对上一row10.260410报告，20%目标8.7523496。失败恢复2073、不扫flag/row/BK/split、不重采，不降低门槛。C3dtype/layout仍未知。详见C15_CUBE_COLLECTIVE。

## 当前补充：冻结验证包可直接运行，仍未恢复SSH

- 此goal turn先复查ccfaecc/源ca66a541及远端；干净重连仍exit255，仅Connection closed by UNKNOWN port65535。没有收到新入口，不把此前platform拒绝反复说成新明确诊断。远端queue/ps未知，无新活跃handle。
- 已准备tools/native_oj_like/c15_cube_collective/run.sh（tracked）和私有artifacts/c15-cube-collective/c15-cube-collective-validation.tgz（63748B/SHA0de344140d01b8dceb4db104d75e2fded50609a3b49743a6843d403c74c3b660）。source/wrapper/harness/frame/fixture/两input及golden/序列核对，已有结果目录拒绝重启，CANN→identity→一次correctness/alternating/default五报告→打印原gate，无自动OJ。
- Bash语法/三Python AST/九file SHA/wrapper994e29f/archive私有权限和安全路径PASS，仅静态包验证，未执行CANN/native/profile。下条新入口先真实连接/queue/SoC检查→scp-O上传/解压→bash包内run.sh /workspace/bmmms-codex；完整说明见C15_CUBE_COLLECTIVE。用户刷新入口请求仍待答，无需重复root密码。

## 以下为前序终态（当前以上段为准）

# 当前：两条C15结构均完成设备验证，未达门槛，恢复正式Pass15保留版

- 当前experiment/c15-row-finalize，kernel逐字a11e2d9/2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b。正式任务820092/6ad046feaad397b6d98aa318仍是已确认Pass15/398.92us；本次没有新增OJ。
- 新C15完整L0两MMAD source20ee2dde/273073e，归档87ff608：CANN/native精度/全负/同地址变化输入及五报告全通过，actual40个Cube各2MMAD，median10.800432相对正确父10.940437仅快1.28%，未采前10%+全五快于父最快准入。
- 新C15八AIV按行归约 source00c23fa0/81f49ff：原Cube8MMAD不变、全K先于MaxN/原arena行所有权复用。CANN/实际native精度/全负/同地址变化/guard通过，actual<half,true,true>/8Cube8AIV/default8表×5全部完整。times[10.300412,10.360415,9.900396,10.260410,10.080403]，median10.260410仅快6.2157%；五次均快于父最快，但未采前median<=9.8463933。不降低门槛、不重采、不扫邻近行数/核数/slot/BK/split。正式15及其它layout/dtype/SoC未跑。
- raw完整下载artifacts/c15-two-mmad-frame及artifacts/c15-row-finalize，均700/600，包含identity/全部五报告8表/正确性/变化输入/成功编译log及工具错误路径log。详见C15_TWO_MMAD_FRAME/C15_ROW_FINALIZE。两条候选完整源码在原commit可恢复，当前不混入保留版。
- PMU证明两MMAD的归约集中AIV0，按行版本全部8AIV参与；计数有重叠，不能相加或无证据认定同步临界路径。仅改变finalizer一项的latency对照以上正确parent为准，勿用两MMAD PMU当相同producer的因果证据。
- native51976/交替72374/profile1728/下载54635均terminal0，远端queue应空，无活跃OJ。前台SSH master35585仍实际有效；先检查真实连接/queue再开新任务，不要重跑已完成case。
- C3正式只有shape2/7/13/48，dtype/layout用户回复“可能有问题”，仍未知。旧BF16TN native只是fixture，不能反推正式隐藏属性。
- **NEXT**：先只读比较这两条与正确parent的现有完整PMU和实际SDK同步实现，解释额外barrier/原producer-ready约束，识别可证的新同步架构；不凭CrossCore modeId名字删全AIVbarrier，不把两个未达门槛小收益简单相加。若无新语义证据换方向，避免重复已失败结构。整体冲榜目标未完成，继续保留正式Pass15来源并按新完整结构验证。

## 以下为历史完整记录（当前以上段为准）

# 当前进行：C15八AIV按行归约新结构，CPU通过/设备编译中

- experiment/c15-row-finalize，kernel00c23fa0f42564df10187e01ed0b1da03f2c405b64119b8ac3c8e47060bbc406。从正式Pass15保留2073派生，原Cube函数体/GM arena不变，仅新ROW_FINAL默认false/template真分派/精确guard及原arena按行复用finalizer。失败two-MMAD不并入。
- 每AIV覆盖8个完整N64行在全部8Ksplit的贡献，先FP32 SumK再MaxN/Sum8M，自己split0行起点写32B得分槽，MTE3_S+全AIVbarrier后AIV0固定顺序Sum8组分数，4B写y，无atomic/新GM。额外barrier可能抵消收益。详见C15_ROW_FINALIZE。
- CPU实际完整finalizer8线程/4个完整partial张量/6故障控制，host实际guard54+65/资源临界，inverse恢复2073/保护7一致均PASS；不是native证据。
- **NEXT poll exec67879**：CANN9/dav2201 compile，远端/workspace/bmmms-codex/c15-row-finalize-build.log，build-c15-row-finalize，冻结imports/c15-row-finalize-00c23fa0f425。初始95664工具误填目录kernel找不到，已记录/修正，源码未改。成功后写DSO identity（wrapper994e29f/source00c23fa0），仅一次correctness及原c15_input_sequence mixed-negative-mixed，然后一次完整default五profile。native捕获新ROW_FINAL=true/8Cube8Vector/每Cube仍8MMAD。
- 采前门槛median<=9.8463933且所有五<父最快10.540421us、完整精度/全负/变化输入/guard通过，才做进一步正式15验证。20%目标8.7523496；失败恢复2073，不扫行数/核数/buffer/stride，不重采/OJ。当前无新OJ，整体冲榜仍未完成。
- C15两MMAD结果已归档87ff608并推送：真实40个Cube均2MMAD但median10.800432/仅1.28%；raw完整本地。C3dtype/layout仍未知，用户“可能有问题”。连接master35585实际仍有效，凭据不入Git/scp-O。

## 以下保留前序终态（当前以上段为准）

# 当前：C15两MMAD结构验证终态，恢复正式Pass15保留版

- kernel逐字a11e2d9/2073f48e，正式Pass15/398.92us不变。新producer永久保存在273073e，native精度/全负/同地址变化输入/guard全部PASS，但五完整默认报告中位10.800432us对parent10.940437仅快1.28%，未采前10%且全五快于父最快门槛。40个Cube记录确实全部仅2次MMAD；无OJ、无重采、无参数扫描。
- times[10.760430,10.800432,10.740430,11.060442,10.900436]，详见C15_TWO_MMAD_FRAME。raw已完整下载artifacts/c15-two-mmad-frame，目录700/files600。编译/正确性12330/交替52815/profile38701/下载55679全部terminal0，queue空。
- 唯一执行归约的AIV block0平均time8.051/Vec.936667/MTE2.685us，另7AIV time6.172508/Vec.015556us；PMU重叠不相加，证明归约集中而不证明瓶颈因果。下一结构应研究原GM arena内按行分配8个AIV归约，保留全K先于MaxN、确定性SumM及ready通知；不要重做BK/slot/split参数。
- C3正式dtype/layout仍未确认，用户回复“可能有问题”。不将本地BF16TN当隐藏事实。

## 以下保留前序记录（当前以上段为准）

# 当前进行：C15完整L0单缓冲两MMAD新producer已编译，native精度验证中

- 分支experiment/c15-two-mmad-frame，当前kernel20ee2dde864cc79ec7cd395dfc0c4a2c3f7bfd9a8d6585f63d80715c85cfa1c4，77新增行；parent2073f48e/a11e2d9正式Pass15/398.92us。只增加新producer/guard/dispatch，原函数/GM/MakePlan/其它kernel逐字保持。
- 固定原C15 FP16TT/B1M64N64K8192/dual25/8splitK1024/8workers，L1完整split262144B、单L0A/B各65536B、两次K512 MMAD/4次Load2D，Cube无源级TPipe队列、仅4GM ABI。原Fix通知→AIV等待→全AIVbarrier→原packed finalizer不变。旧resident8MMAD反例未直接并入、不扫BK参数。
- CPU实际producer4194304地址/32split/4full数学golden/7反例，guard54/65+满容量临界、inverse/保护7通过；不是native布局/速度证明。详见C15_TWO_MMAD_FRAME。
- CANN9/dav2201编译PASS，DSOf8f1da4c8d1af3a8ea691fef9433f8219370f109fb704cd6d02588776b76747d /source20ee2dde/wrapper994e29f。frozen imports/c15-two-mmad-20ee2dde864c/kernel.asc，native_oj_like/build-c15-two-mmad/libnative_bmmms.so。
- **NEXT poll exec12330**，results/c15-two-mmad-correctness；成功后同frozen c15.json/c15.complete_frame.json/inputs/c15跑原c15_input_sequence.json的A/B/A correctness，再一次default五报告，actual新symbol/8Cube8Vector/每核每次2MMAD必须确认。
- 新active目标采前准入：median<=9.8463933us（parent10.940437降低>=10%），所有5样本<父最快10.540421，且完整精度/全负/变化输入/guard全部通过，才能进一步正式15验证。20%目标8.7523496仍保留。未达归档恢复2073、不扫参数/重采/OJ。尚无性能结论或新OJ。
- 连接master35585已实际检查有效、hostname2ef29bca0f61/9382/24AIC48AIV/dev0physical14/CANN9；queue初始空，编译97125 terminal0，当前仅12330一次correctness。凭据不入Git，scp-O。

## 以下为前序完整终态与操作约定（当前状态以上段为准）

# 当前：三条新结构验证终态，恢复正式Pass15的2073

## 有效保留版本与Git

- 当前分支experiment/c3-flat-gather，kernel **2073f48e78d4fa86c409c4befc620744b2532d5f01223cf94564900f35d1ec2b /353255B**，逐字a11e2d9。正式任务820092/6ad046feaad397b6d98aa318已Pass15/allprecision1，总398.92us；含实际修复C15零输出的Cube PIPE_FIX→AIV就绪通知，不回退已反证的ZIP078635。
- 用户本轮要求开始优化，已完成C6/C1/C3三条独立结构试验，均未达到预设20%提交门槛，未增加任何OJ任务。失败代码和数据完整保存，不混入保留版。
- 算法仅kernel.asc；保护7等1734f16，正式测试/阈值/SDK/main/CMake均未改。GitHub允许push实验分支，不移动tags/main或改写历史。

## 三条本次实验（native实测）

1. **C6 compact NZ**，实现5fc448b/source360db6f0，归档6fd56e0。保持输入/完整K192/UnitFlag3/握手/arena，将有效M23紧凑NZ交接，写10240→7360B。native精度一次+五输出通过，actualtrue/13Cube13Vector/default8表×5。8.860354→8.820353us仅0.4515%，未gate7.0882832。不扫format/stride/重采/OJ。raw artifacts/c6-compact-nz-output，详见C6_COMPACT_NZ_OUTPUT。
2. **C1 scalar-cache fullK32**，实现28e1a82/source4c081854，归档34f72b0。NPU scalar GM直读真实编码、FP32两链累加、输入失效/UB刷新/S_MTE3/4B输出/PIPE_ALL。初始9e699fe1因CANN publicLocal Dcci封装const_cast非法编译FAIL，未改SDK；修正用实际内部同dcci指令，CANN通过/DSObf9f52ce。FP16一次及同context/stream/input地址A/B/A全负变化通过，guard/input完整。五times[7.840313,7.880315,2.240090,2.280091,2.340094]，median2.340094，parent1.600064，慢46.25%；高值全保留不无证据归因，不删缓存维护/扫unroll或accumulator救性能，不OJ。raw artifacts/c1-scalar-cache-dot/c1-scalar-evidence.tgz，详见C1_SCALAR_CACHE_DOT。BF16硬件/正式15未做。
3. **C3 flattened Gather**，实现a55b767/source8b13ff71/DSO5a7b7194。Brcb/Add完整offset矩阵每input一次Gather，原DMA/Cast/Mul/Ksum/Nmax/Msum不变/extraUB3008。native一次+五完整输出fullFP64精确，actualbf16/TN/K48/FLAT_GATHERtrue/pureVector2AIV/default8表×5。parent[3.420137,3.020121,2.880115,3.120125,2.920117]median3.020121，candidate[3.320133,2.740110,3.160126,2.820113,2.840114]median2.840114，约快5.96%，样本重叠，未gate2.4160968。不重复/扫stride/附近shape/OJ，恢复2073。raw artifacts/c3-flat-gather/c3-flat-gather-evidence.tgz，详见C3_FLAT_GATHER。

全部raw已下载，目录700/files600，精确source/DSO/input/plan绑定、所有样本保留。CPU模型均只对各冻结候选运行：不要改成在parent运行也报告PASS。default逆变换/保护7、实际资源边界/负控制完整，不能替代硬件精度/时序。

## 属性与下一条可执行动作

- 正式C3只有用户shape记录2/7/13/48，dtype/layout未唯一确认；用户本轮回复“可能有问题”。本地BF16TN仅明确fixture，不用本地耗时反推隐藏属性，不将native改善当正式覆盖。
- 当前全部设备任务terminal0、queue空，无活跃OJ或新性能候选。下一先检查已有编译对象的NPU指令/代码生成和PMU，解释源级Gather/GM减少为何完整收益有限，避免复做三条邻近参数。工具发现可用objdump后只读既有binary，不需要再采同输入性能。若编译对象不支持读，记录限制后选真正不同的结构，别强行解释延时。
- 当前正确parent DSO **ca36b327c9104b3006de2bb7ec732a3b817ae8fff447c6ce2a37e2d9c5fd28e6**，native_oj_like/build-c15-ready/libnative_bmmms.so；source imports/c15-producer-ready-2073f48e78d4/kernel.asc。
- C6 candidate build-c6-compact-nz、C1 candidate build-c1-scalar-dot-fixed、C3 candidate build-c3-flat-gather，各.so及identity.json/源都在/workspace/bmmms-codex。完整reviewed c1/c3/c6.complete_frame.json及inputs/c1/c3/c6保留。

## 比赛目标与旧反例

当前正式向量[2.09,2.64,3.12,4.19,4.70,9.45,6.64,36.47,56.95,76.65,78.43,88.04,8.84,9.61,11.10]us，总398.92；用户第一名总348.37，整体慢14.51%。按固定旧Tbest敏感度C6/C1/C3优先，计分非总时长。最新实时Tbest未读取，不称排名。

C15resident仅1.28%归档6d2c47b；C11NN Cᵀ慢5.025%归档3ff5ff4；C6raw Load3D精度FAIL0689e2d；C13fullK仅.66%；C12stridedB仅.53%；C4compact变慢。旧tiny raw transpose/storage Ktree/static FT/literal Vector无明确收益。本轮三结构同样不换名复做。队友C8五轮结束/C7parked/C9constantSchedule paused，其它见TEAMMATE_777734_REVIEW/PERF_LOG。接受队友b881与ZIP078635身份不同，不能借其成绩。

## 连接与操作

私有config /private/tmp/bmmms-remote-access/config，前台master exec35585/ControlPersist=no，先ssh -O check；askpass已删、凭据不入Git，scp需-O。hostname2ef29bca0f61、Ascend910_9382/actual24AIC48AIV/dev0physical14/card7chip0/CANN9/driver26.1.1，caller20不等于硬件核数。新入口已实际连接，不沿用旧blocked结论。

工具/workspace/bmmms-codex/native_oj_like，Python /workspace/bmmms-codex/test-venv/bin/python。source /usr/local/Ascend/cann-9.0.0/set_env.sh，driver/lib64/common及driver/lib64/driver加LD_LIBRARY_PATH。filelock+queue串行NPU，状态/workspace/bmmms-codex/npu_test_state.json，启动前查真实state/ps。最后C3profile28889、baseline28094、编译47243均terminal0。

当前parent正式15已过；平台未给actualSoC/plan/profile，不能把本地9382当OJ机器或另一SoC覆盖。整体冲榜目标未完成。

## 只读codegen检查已完成的限制

已从保留build-c15-ready/library.asc.o解析两份现有device ELF，源对象SHA bf99376c。当前llvm-objdump能读函数symbol尺寸（C6AIC504/AIV1072、C1 FP16group2 876、C3BF16TN/K48 2116B），但反汇编opcode全not available，显式mcpu也无效；不能据此声称多少条指令或瓶颈原因。SDK msobjdump对新ASC fatbin也不列出，未改工具。原始包artifacts/native-codegen-audit/codegen-audit-evidence.tgz（下载完成后），远端codegen-audit保存extract.py/ELFs/summary/失败asm。

后续可核对bisheng实际help中的save-temps/汇编输出选项，仅在独立工具构建保留同源时保存生成汇编；这比再扫三条失败方向的参数更有证据价值。当前没有第四个性能候选，正式保留源仍2073。
