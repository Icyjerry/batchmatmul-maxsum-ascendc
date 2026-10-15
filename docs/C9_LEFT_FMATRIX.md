# C9：复用非转置 A 的 Load3D FMatrix

## 实测依据与撤销的方向

从正式Pass15保留2073f48e/a11e2d9开始，C15三条结构native终态已经保存：两MMAD仅1.28%、按行6.2157%、Cube collective无额外中位改善，均未达提交gate。本次不继续C15邻近参数。

新入口提供时原master仍实际有效（pid9058/63301），只更新私有重连授权，未中断现有连接。当前hostname2ef29bca0f61、9382/actual24AIC48AIV/dev0physical14/CANN9/caller20，queue复查为空。

C9用户确认FP16 NT及记录全shape1/2048/1536/1280。原source2073/DSOca36真实normalPlan：dual36、BM128BN128BK128、Mt16Nt12、**Ns5/window3**、Kchunk256、workers20、final1；不是旧audit的Ns3/window2。system16777216/total24682496。完整frame已保存，不修改正式main/tests或输入。

先前提出stationary-B+完整tile均衡，但真实计划已按连续task分配，实测每核90/100MMAD即9/10完整tile。`audit_c9_stationary_b.py`用已捕获plan计数：旧总GM输入73400320B，新72089600B仅少1.7857%，两者最忙核均3932160B，且每核tile数量完全相同。新方案还需要转置归约，因此**取消，不写stationary-B kernel**。这些是输入字节/任务数学，不是硬件cache或延时预测。

正确parent全FP64实际storage golden191.8094940185547，一次correctness及default全部8表×5输出、输入不变/yguard通过。五TaskDuration **[55.142204,54.922195,56.122246,55.062202,55.382214]us**，中位 **55.142204us**，实际原NT/20Cube40AIV；不是OJ耗时。全部五报告每Cube90或100MMAD且pattern一致。

PMU平均Cube MTE1 25.904378/MTE2 30.282717/MAC28.281706/Scalar MTE1 stall32.607439us；Vector compute5.624116us。这些重叠，不相加或据此直接证明FMatrix为瓶颈；它们与源码每K重设Load3D控制的事实支持本次单独测量。

## 单一新假设与修改范围

原C9 A=false，B=true；A由Load3D从完整resident NZ加载，B仅Load2D，不写FMatrix。每个K128面板默认Load3D会重设FMatrix和padding。C10现有NN路径已支持显式LEFT/RIGHT及`IsResetLoad3dConfig{false,false}`，但C9当前SPLIT_FMATRIX=false，因此没有复用该机制。

本次在原exact C9 NT full-M入口启用同一LEFT配置复用：A refresh时原代码SetFmatrix(1,rows,zeroPad,LEFT)，后续K面板用原ManualTransposeFullM的reset=false调用。B Load2D不触碰LEFT，原Cube entry已经SetLoadDataPaddingValue(0)。完整K/FP32 MMAD、两个L0槽、double Bpackage、C/credits/Vector/最终归约/原GM/MakePlan/allocator逐字保持。

源码 **4693eb7a60827baa354522fe83748eb0c00313459a6f4c9d713e59c429c183f0 /354840B**，31增2删，仅拓宽现有compile-time断言允许NT、精确host guard、guard命中时开启现有最后一个template bool。不是静态Schedule替换、Kchunk/窗口/BK扫描，也没有再实现旧Bpackage加载变体。C10默认行为不变。

Guard仅FP16NT/B1M2048N1536K1280、原dual36/BM128BN128BK128/fullK/匹配计划/arena；真实AIC/AIV按workers查询，支持不同预算，不假设物理20核。检查原A+双Bpackage L1、满L0A/B和双L0C、保守UB和原workspace。所有显式TUNING pin回退，NN/TT/TN及其它case仍原入口。

## 真实SDK依据

实际读取CANN9安装文件`aarch64-linux/asc/impl/basic_api/kernel_operator_mm_base_impl.h`：IsResetLoad3dConfig字段isSetFMatrix/isSetPadding，默认true,true；LoadDataImplV2按这两个编译期条件调用Load3DSetFMatrixCal/Load3DSetPaddingCal，再执行同一LoadData3DV2L12L0ACal。本次沿用原已编译的false,false对象，不改SDK/编译选项。全部K面板参数和源目的布局相同，硬件配置生命周期仍需native验证。

## CPU与scope检查

实际提取ManualTransposeFullM和现有SetFmatrix初始化执行：覆盖当前20workers/80tasks/192完整tile/全部1920 K面板。新旧各31457280、合62914560物理NZ源与ZZ目的tag地址检查一致，全部K和M行、L0guard通过。设置次数1920→32，原padding初始化后保持0。4个missingSetup/wrongWidth/wrongKOffset/accidentalReset反例被拒绝。

整份逆变换精确a11e2d9/2073，保护7等1734f16，B的TX2=true源分支仅Load2D、不含SetFmatrix。actual guard production48/TUNING59反例拒绝，8/20/24/32 worker预算、精确L1/L0/UB容量临界通过。模型是integer tags/声明的控制状态，不是native FP16/时序/性能。

## 采前准入和当前状态

**先固定再采候选**：median<=49.6279836us（parent55.142204至少降低10%），全部五候选<父最快54.922195us，正确性及全部5次输出/input/yguard通过，才补全负与同地址mixed-negative-mixed等必要精度/回退验证并考虑一次正式15。只读原报告，不重采parent，不删样本，不变gate。失败归档恢复2073、不扫附近FMatrix/panel/窗口参数，不OJ。

独立CANN9/dav2201编译中**exec35373**，冻结`imports/c9-left-fmatrix-4693eb7a6082/kernel.asc`，`native_oj_like/build-c9-left-fmatrix`，log`c9-left-fmatrix-build.log`；目前native/profile/正式15 PENDING，无新OJ。

原parent raw已下载`artifacts/c9-stationary-b-audit/c9-parent-evidence.tgz`、identity/summary/PMU/分工模型同目录（700/600）。parent plan33301/correctness81085/profile93219/下载13714均terminal0，不重启这些任务。候选原始资料放`artifacts/c9-left-fmatrix`。

## Native终态：精度通过，仅0.87%，恢复保留版

实现05c86ea/source4693eb7a，CANN9/dav2201编译PASS（8条原host属性warning），DSO **bf4054fef6aa43bc641b5da09fa36f05124daa5d89c8f472ef37d34d38ceaa73**。首次correctness及一次完整default8表×5均fullFP64通过，五次输出一致191.80950927734375/maxAbs1.5258789e-5/maxRel7.95518e-8、input/yguard完整。实际新SPLIT_FMATRIX=true符号/20Cube40AIV，全部每核MMAD计数与parent90/100 pattern逐个相等。

五TaskDuration **[54.662186,55.342213,53.322132,54.662186,54.622185]us**，中位 **54.662186us**，对55.142204仅快 **0.8705%**，未采前49.6279836及全部快于54.922195门槛。无OJ/重采/FMatrix或K参数扫描；工作kernel恢复2073/a11e2d9。全负/变化输入、其它SoC/正式15未做，不能用混合输入替代。

计数的重要反例：AIC平均scalar MTE1 stall32.607439→.219244us，scalar Cube stall .070844→31.618728us，MTE1活动25.904378→25.824267us，MAC28.281706→28.274050us。等待分类明显改变，但完整耗时仅0.87%；不得以某一stall下降声称整op同幅度改善或把重叠计数相加。C9相邻N共享A的已有61.54/62.36对57.46反例继续有效，本次未另写同样Kouter-Npair方案。

全部原始correctness/5完整8表/DSO身份/buildlog已下载artifacts/c9-left-fmatrix/c9-left-fmatrix-evidence.tgz、summary和pmu-summary同目录700/600。编译35373/correct14509/profile95861/download35588均terminal0，无新NPU/OJ任务。

下一次真实SDK发现（未实现）：dav_c220 MulAddDstIntrinsicsImpl明确支持Tuple<float,half>，允许half输入乘积直接累加到FP32目标，现有C1可研究预先清零FP32产品、与输入DMA重叠，去掉依赖链中的FP32 Cast。不是已失败的float/float C4 compact MLA，也不是scalar-cache；必须验证mixed模式源block/repeat stride、真实FP32乘积精度及大half乘积不会先在half溢出，再看完整耗时。BF16不在该tuple支持范围，不能冒充可用。没有代码/设备结果，不能称加速。
