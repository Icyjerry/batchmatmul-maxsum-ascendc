# 性能结构审查 · 2026-09-22

审查代码：`76d6c28`，kernel SHA256 `771b0cf9b1472ed8c0efee350275413a89aedb79000325b64d78353aa6a27d59`。此次未改kernel；没有新增NPU性能结论。

## 结论

存在明显的实验堆叠与规则耦合倾向，新增Cube producer也引入了问题。4044行本身不是性能证据；更值得处理的是容量可行性被当作默认选路条件、规则覆盖顺序、没有收益的驻留和跨组流水限制。先收敛这些问题，再增加新路径。

## 优先级与证据

### 1. 高：新producer默认覆盖先前调度结果，缺少收益准入

`kernel.asc:3717`在旧tile/window/nSplit已经选定之后，按容量与每shard至少两tile切换到manual；`3730`强制`dual=14/window=1`。前面按库路径建立的窗口成本和N拆分决策没有随生产者变化重新评估。

真实planner加CPU宽松tiler复现：

| B,M,N,K / layout | panel=0 | 默认panel=3 |
|---|---|---|
| 1,64,8192,128 / tx01 | dual1、64×128、window2、ns10 | dual14、同tile/ns、window1、resident |
| 1,1536,1536,1536 / tx11 | dual1、128×128、window4、ns3 | dual14、同tile/ns、window1、resident |

这证明实际覆盖关系，不证明新路径更慢。尤其前者来自case profile，后者经过新的N工作量选择器；两者均可被末尾替换。应将producer选型、tile和拆分的成本放在同一次候选评价中，设备胜出的配置再进入正式默认。最近新增的默认切换由本Agent引入，不能把容量检查和CPU PASS视为速度证据。

### 2. 高：A常驻存在无复用收益且LoadData调用增加的路径

`kernel.asc:3725`只根据容量启用常驻，没有要求一个task拥有多组N tile。`PanelLoadA`的TX1分支（2156）只要`fullK != 0`就按16行循环LoadData，即使`k0=0 && count=fullK`、整个切片实际连续。

复现 `(16,128,256,128), tx10`：tile128×128、ns1、panelK128，每task恰好两个N tile。panel2和panel3均只读取一次完整A；panel3常驻不再减少GM读取，却将L0A加载从一次repeat=64的LoadData变成8次repeat=8。还新增了驻留加载后的显式fence。这里的8倍是源码调用数，不是耗时倍数。

修复方向：完整连续切片走合并LoadData；仅在跨N组或较大K面板确有预期收益时启用驻留，保留布局成本。不要把所有`fullK != 0`都当成不连续切片。

### 3. 中高：两个C累加器限制了跨组Fixpipe/MMAD重叠

`kernel.asc:2332`等待本组MMAD完成，然后依次输出两块C；下一组在2239先等待两个`FIX_M`事件，才进入MMAD。它们是当前N组的两个独立累加器，并不构成当前组/下一组交替使用的C缓冲。下一组首个MMAD也依赖另一块C的Fixpipe完成。

这是可确认的依赖链；与旧路径相比的净收益未知。A复用可能抵消重叠损失，不能直接删掉配对生产者。优先将C释放等待移至首次真正覆写对应C的位置并验证事件协议；不要未经容量评估直接翻倍L0C。

### 4. 高（调参有效性）：显式tile/split/window被case profile覆盖

`kernel.asc:3534`附近应用Tune字段，3555随后应用caseProfile。只有显式`Tune().dual`会让顶层跳过profile；单独pin其它参数仍可被覆盖。

复现 `(1,64,8192,128), tx01`，设置`bm=32,bn=64,ns=2,window=1`，结果为`bm=32,bn=128,ns=10,window=2`。这会令预期的A/B实验实际测到不同配置，浪费调优或导致归因错误。

应确定统一优先级：显式pin覆盖自动profile；不可行的pin应明确报错或记录fallback，不能静默被历史规则改写。同步保护完整K、UB与布局条件。

### 5. 中：host规则和历史候选需要整理，但不能等同于设备热路径开销

`MakePlan`约635行，顺序经过case classification、普通形状规则、离线规则、调参、profile回填、tile fallback、两层N均衡和panel替换。`dual`混用布尔含义及0..16家族编号，同一含义散落在planner、workspace与Launch。历史实验入口仍在Launch中，但其中若干只由TUNING选择。

这增加了维护和归因成本。probe在默认宏下编译为空；MakePlan有缓存，同shape稳态不会每次执行全部规则。删除注释、压缩行数、删除未调用函数不能自动降低Device Task Duration。当前每stream只保存一个plan、全局mutex覆盖launch，是host延迟/多stream审查项，不应冒充单kernel已测瓶颈。

## 复现与下一步

```sh
python3 tools/audit_plan_precedence.py
```

脚本抽取当前真实MakePlan，用现有宽松CPU tiler分别打印panel0/2/3及显式pin结果；不运行CANN或设备。上述源码位置对应审查SHA。

建议实施顺序：先修完整连续A切片和pin优先级；再评估C释放等待位置；最后收敛producer/tile/partition选择及历史候选。每项都保留可归因对照，不把这些修改再组合成未经验证的“新最优”。CPU布局/事件模型与NPU验证仍分开报告；云端按用户指示暂缓。
