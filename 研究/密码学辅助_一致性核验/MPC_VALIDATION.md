# 真实主动安全底座的开发验证与同功能基线

## Material Passport

origin_skill: academic-research-suite；origin_mode: run-and-validate；origin_date: 2026-11-02；verification_status: UNVERIFIED；version_label: crypto-aux-mpc-01；repro_lock: null。

运行记录已实测；完整协议实现安全和原创性未获独立验证。原 Python 内核依然是明文代数模拟；新增 mpc/locate2.mpc 才是本轮执行于 MP-SPDZ 的程序。

## 配置与真实性

- MP-SPDZ 官方 v0.4.4 发行包，[下载来源](https://github.com/data61/MP-SPDZ/releases/download/v0.4.4/mp-spdz-0.4.4.tar.xz)。SHA-256：73d6473526101b4433999fc4f7521fdfdc53ddf018e5f64480518d6293f62760。
- 使用发行包中的 Linux ADX mascot-party.x；二进制 SHA-256：47d9ae6f52003825946a4abb6cf9dc62f62a4e2fc2c19a5e3ee6f59a6889b07e。本轮未从源代码重编译或独立审计该二进制的全部构建选项。
- Ubuntu-24.04/WSL，两方、同一物理机器、加密通道 -e、GF(2^128) 数据域、在线生成真实预处理。未使用 Fake-Offline、预制乘法相关量文件或 -F。
- 使用 get_random_inverse 产生非零盲因子和公开随机挑战，使用新鲜乘法 triple 的首项产生包含零的秘密均匀掩码；丢弃未使用的相关量，全部成本照实计入。
- 两方分别输入合成加法份额。测试驱动者知道完整输入，两个本地进程不构成独立管理域；这是协议执行实验，不是针对本机管理员的秘密隔离。
- 所有可影响分支的打开值在使用前执行 check_point；输入在生成挑战前完成。最终验证同时要求两方正常退出、PROTOCOL_DONE 和精确输出匹配。
- 编译使用 --preserve-mem-order，避免初次探索运行中的内存重排警告。成功基线结果没有该警告。
- **运行统计安全参数为 40。** 尝试 -S128 时底座拒绝执行，原始错误保留。数据域为 128 位不等于端到端统计安全为 128 位，更不等于代数平方误差界可以直接当作整个实现的安全级别。

运行于主动安全底座的诚实执行不等于完成恶意行为穷尽。恶意网络篡改、份额伪造、选择性中止、重启和端到端输入来源攻击尚未系统测试。

## 实现与强基线

同一份 mpc/locate2.mpc 的 mode 参数控制两种方法，它们使用相同输入、gate、域、批准范围（纯合成实验）和底座配置。

moments：两个秘密 gate 结果用范数组合；公开四个数值隐藏矩；使用公开 Prony 解码、全部矩重算与新鲜挑战遗漏复核，最多两次尝试。运行器不向解码器提供真实支持集。

coordinate：通过相同 gate 后，每个 d_i 乘以独立均匀秘密非零盲因子，再公开结果判断位置。对稀疏输入，它完全隐藏非零幅值且不会因零掩码遗漏；对稠密输入，gate 偶然误放行可能泄漏位置，其概率由同一 gate 界覆盖。这是简单、合法、同功能的基线，不是随机探测或不安全全公开。

候选的遗漏检查引入额外小概率误差与 INCONCLUSIVE，基线没有这项稀疏输入误差；比较没有通过弱化基线制造优势。此基线尚不代表所有可能的最优草图/分组定位方法。

## 测试范围

主比较为 n∈{8,64}，每种模式每个规模运行两次，每次八个固定合成批次，次序在重复间交换。每次有六个支持大小≤2 的批次、两个稠密批次。覆盖零残差、首/尾位置单故障、相同位置不同幅值、两个不同/相同非零幅值、三故障和全稠密输入。

共八次两方运行、64 个逻辑批次，两方输出均由独立检查器按原始合成向量的非零坐标直接判定，全部一致。没有用候选输出反过来生成期望值；没有发现安全反例不等于不存在攻击。该规模没有观察到 INCONCLUSIVE，不能把这个观察写成零失败概率。

数据域兼容性 smoke 额外检查 (2^127)·2=0x87，及秘密预处理逆元乘积为 1。通常素数域初始化日志来自底座的辅助域；实际程序的输入、乘法和打开统计均为 gf2n。

## 结果：明确保留负结果

下表为每次八个批次的两次算术平均值；MB 为底座报告单位，通信包括预处理。秒数为底座报告的含预处理 Time，不含编译、证书生成及完整进程建立时间。

| n | 方法 | 全部参与方发送量 MB | 含预处理秒 | 在线秒 | triples 消耗 | inverse tuples 消耗 |
|---:|---|---:|---:|---:|---:|---:|
| 8 | moments | 14.0360 | 0.428681 | 0.226157 | 242 | 74 |
| 8 | coordinate | 19.0365 | 0.410694 | 0.200565 | 224 | 104 |
| 64 | moments | 15.8853 | 0.424127 | 0.221387 | 242 | 74 |
| 64 | coordinate | 55.8262 | 0.506517 | 0.196546 | 560 | 440 |

小批次的简单基线更快且消耗更少 triples；候选即使在 n=64 时，在线耗时仍较慢。候选在此本机配置下减少了通信，n=64 时含预处理总耗时较低。只有两次重复，不能给出普适加速、统计显著性或生产吞吐结论。预处理按批产生与填充，不能用这些小样本外推线性通信系数。

成本核对：k=2 候选每个稀疏批次一轮含 31 个算术秘密乘积，另有两个用作均匀掩码的 triples，故总需求 33；每个被 gate 拒绝的批次为 22。六稀疏、两稠密合计 6×33+2×22=242。coordinate 的相同表达式为 6×(22+n)+2×22，分别是 224、560，与底座消耗记录一致。秘密随机性和输入认证没有从总成本中抹掉。

## 可复现命令

在 PowerShell 进入本隔离目录后运行。输出目录必须不存在，避免覆盖证据。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
wsl -d Ubuntu-24.04 -- python3 mpc/setup_backend.py
wsl -d Ubuntu-24.04 -- python3 mpc/run_backend.py --out results/my_smoke
wsl -d Ubuntu-24.04 -- python3 mpc/sweep.py --out results/my_paired --sizes 8 64 --repeats 2
wsl -d Ubuntu-24.04 -- python3 construction/validate_general.py --out results/my_general
wsl -d Ubuntu-24.04 -- python3 construction/leakage_barrier.py --out results/my_barrier
wsl -d Ubuntu-24.04 -- python3 construction/simulation_barrier.py --out results/my_simulation_bound
wsl -d Ubuntu-24.04 -- python3 construction/mds_barrier.py --out results/my_mds_bound
```

MPC 随机转录、密钥和耗时不会逐字复现；要求输出语义及检查结果一致。代数有限检查 general_mask02/general_mask03 已进行文件级确定性重放，复核结果及补充紧界检查在 results/construction_mpc_delivery03/manifest.json。

原始主比较入口：results/mpc_paired01/summary.json。每个运行子目录保留 compile.log、party0.log、party1.log、运行命令 manifest.json、源码副本、字节码和独立 verification.json。Player-Data 下为合成输入及本地测试密钥，不能当作生产凭据管理示例。

## 已保留的失败与未运行项目

- mpc_smoke01：误用了 -G 128，编译失败；改为 --galoissize 128 后 smoke02 通过。
- mpc_locate_n8_01：输出正确但出现内存排序警告；最终主比较启用 --preserve-mem-order。
- mpc_locate_n8_02：-S128 导致 no suitable field for minimum degree 128，两方均拒绝，未把失败改写为通过。
- 尚未执行真实跨主机/广域网实验、完整恶意攻击测试、TLS 到份额绑定、k>2 完整 MPC、机器形式化证明或正式 H-A/H-B/H-AB 统计判定。

数学上一般阈值的条件性论证见 CONSTRUCTION_EXTENSION.md；新颖性否决风险见 NOVELTY_REASSESSMENT.md。
