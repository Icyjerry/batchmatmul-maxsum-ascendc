# C10 FF B 搬运包：单项结构实验

## 假设与范围

仅选择 B=1/M=4096/N=1280/K=1152、BF16、FF、原 dual20/BM128/BN256/BK64/tree8/window1 的安全计划。正式 C10 的 dtype/layout 尚未确认；历史 FP16/TT 与 BF16/FF 探针冲突仍保留，不能凭耗时认定命中。

父版本 af886e1（C8 phased-A 已正式 Pass）。候选 kernel 369094B，SHA256 `31bc978fbf8555a8ff8dd5dafa76b0df5c5fb06f3b4b5245dfbff9ae379b5ff1`。算法只改 kernel.asc，60 行新增/5 行删除；没有更改 main、golden、正式测试或依赖。

最初拟复用 C9 内核，但源码复核发现它会同时替换 Vector 消费流程。因此实际实现是在原 bmmms_manual 末尾增加默认值为零的 B_PACKAGE 模板参数；仅目标分支传 192。原 A Load3D、双 B1、双 L0A/L0B、单 L0C、完整 K MMAD、Vector、跨核事件 4/5、任务、分块、Plan、workspace 均保留。其余实例参数为零。

B1 从每次 64 个 K 元素变为每包 192，跨三个 K64 MMAD 复用同一个 NZ 包；FF Load2D 使用包的实际 K 间距和包内 K 偏移，最后一次读取之后才释放队列槽。继续提前排入两包，释放后排入下一包。没有新 GM 路径或分配。

## 资源与验证

- 实际显式 L1：A 294912 + 双 B 196608 + 未用 A 队列 1024 = **492544B**。host 再保守预留额外空间，只在实际容量允许时选择。
- L0A=32768、L0B=65536、L0C=131072B；原 partial 16384B + 每 worker 双 ring 262144B 不变；UB 按原消费者和 finalizer 预算验证。
- `python3 tools/validate_c10_ff_b_packages.py` 执行抽取的真实 FF Cube 源码，8 组模型，包括完整 4096/1280/1152、全负/多 batch/MN 尾部、K 包尾及默认不分包路径。
- 完整形状实测源码计数：B DMA **960**、MMAD **2880**、B 输入读取 **47185920 元素**。原 K64 公式为 2880 次 B DMA；同实际 producer 的默认路径代理为 144 次，分包代理为 48 次，输入读取和结果相同。降低的是调用数，数据量与矩阵计算量不变；不推算速度。
- 每个完整 K 的 C 元素、最终 Max(N)→Sum(M)、输入不变、环形边界、事件排空均检查。40 个实际 host 控制配置/5 个命中分别在生产和 TUNING 下通过，涵盖两 dtype、四布局、1/3/8/20/32 核，资源/GM 一字节边界与所有相关调参 pin。
- 六个故障控制分别去掉包间距、包内偏移、正确释放边界、最后读者等待、L0 ready 或 C ready，均被拒绝。
- Vector 逐字节等于父版本。替换回原 manual 区域并删除新增 selector/launch 后，全 kernel 逐字节等于 af886e1；受保护七文件等于 1734f16。

CPU 模型延后 MTE2/MTE1/MMAD 并读取活跃操作数，但 **TQue Alloc 等待该槽最后 MTE1 读者是明确的建模假设**，不是对 CANN 队列实现的证明。Fixpipe/合成跨核消费者同步，整数算术不能证明硬件 BF16 精度或速度。正式 CANN 编译、15 精度和性能仍 PENDING。

## 正式入口

隔离提交目录 `/private/tmp/bmmms-c10-ff-b-packages/project`，受保护七文件来自 1734f16。CLI dry-run 确认仅 kernel.asc、上述 SHA/369094B。实现提交并推送后创建一次正式任务；保存唯一 ID，查询同一任务至终态，不能因等待重交。无明显收益则归档并整份恢复 af886e1；不扫描附近包大小。
