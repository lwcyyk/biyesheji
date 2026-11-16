# 行空间构造的开发验证与反方比较

## Material Passport

origin_skill: academic-research-suite；origin_mode: run-and-validate；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: rowspace-validation-01；repro_lock: null。

本轮未进行 H-A、H-B 或 H-AB 的正式实验。所有数据均为合成数据；结果支持限定实现与数学实例的开发核验，不支持新颖性或普适性能优势结论。

## 1. 新增实现

| 文件 | 内容 |
|---|---|
| construction/rowspace.py | 2k² 乘法编码、一般 k 的 RREF 行空间解码、有限理想 GL2 采样 |
| construction/rowspace_reference.py | 独立域乘法、直接矩阵乘法、k=2 叉积解码；不调用候选 |
| construction/validate_rowspace.py | 稀疏向量穷尽、完整 GL2 分布、独立解码比较与安全反例 |
| construction/rowspace_limits.py | 列数不足和线性矩数量不足的具体碰撞 |
| construction/old_bound_refinement.py | 收紧旧方案误差界的精确枚举，保留强比较对象 |
| mpc/rowspace2.mpc | k=2 真实认证 MPC，私密矩阵采样与行空间公开解码 |
| mpc/rowspace_sweep.py | 同输入、同 gate、同底座的三个方法对照 |

原有源码未被替换。新程序继续使用已固定的 MP-SPDZ v0.4.4 官方二进制、真实在线预处理、两方加密通信、--preserve-mem-order。GF(2^128) 数据域和底座统计参数 40 分别记录，不混称完整 128 位安全。

## 2. 有限范围及实际结果

- GF(16)、n=4，所有 1,411 个支持大小≤2 的向量；每个用六个合法矩阵核对，共 8,466 次候选/独立参考一致。
- k=1,…,4，GF(16)、GF(256)、GF(2^128) 共 192 个带完整输入记录的种子例，编码值及恢复支持一致。
- 4,096 个任意公开 2×3 矩阵，元素取 GF(16) 的子集 {0,1,2,3}；两种不同解码算法一致。没有声称穷尽所有 GF(16) 的 2×3 矩阵。
- 对一个双位置和一个单位置支持，各选两组不同幅值，逐个枚举 GL2(GF16) 的全部 61,200 个矩阵，共 244,800 次编码，公开分布精确相等。双位置有 61,200 种输出，各一次；单位置有 255 种，各240次。
- 四个故意不安全反例完整保存：SL2 泄漏、奇异矩阵擦除、稠密输入伪装、跨批次复用。
- 限定最小性检查另外枚举两组输入各61,200个 GL2 矩阵，证明只有两列时不同双位置支持产生同一分布；保存三个线性矩不足的具体碰撞。
- rowspace_algebra01/02 的输出文件作确定性重放核对；有限检查不能替代一般证明。

原始入口：results/rowspace_algebra02/summary.json、results/rowspace_limits01/summary.json。

## 3. 对旧方案的加强，而不是弱化

旧文档采用的 A ε_V² 是保守界。本轮对 k=2 的稀疏输入得到更紧结论：

- s=0 或1时，遗漏检查不会错误接受。遗漏一个非零项时 E 是单项式，对非零挑战不可能为零。
- s=2、位置 i<j 时，只有 R 同时在两位置为零才可能误接纳；这要求一次掩码的两个系数都为零，概率 q^−2。
- 设原二项式 E(X)=d_iX^i+d_jX^j 在 F* 有 h 个根，则 h 为零或 gcd(j−i,q−1)。一次错误接纳的精确概率为 p_bad=h²/[q²(q−1)²]。

令 p_correct=(1−1/q)^s，p_retry=1−p_correct−p_bad。至多 A 次时，错误接纳概率为 p_bad·Σ_(t=0)^(A−1)p_retry^t，耗尽概率为 p_retry^A。对固定位置差及固定 A，双故障误接纳是 O(q^−4)，而不是仅用原保守界描述的 O(q^−2)。这个结论只针对稀疏诊断层；稠密 gate 的误差没有消失。

GF(16) 的四组输入精确枚举了 230,400 组“掩码×两次挑战”，与公式一致。结果见 results/old_bound_refinement01/summary.json。原始旧文档和旧结果保留，不回写历史。

新行空间方案的区别是把稀疏诊断误接纳降为严格零，而不是把整个协议从二阶错误改善为四阶错误；整个协议仍受同一 gate 约束。新矩阵采样还可能给全有效或单故障输入引入额外 INCONCLUSIVE，这些情况下不具有统一的可用性优势。

## 4. 真实 MPC 三方比较

每个规模 n∈{8,64}，比较原 moments、逐项非零掩码 coordinate、新 rowspace，分别两次，顺序在第二次反转。每次九个固定批次，其中六个稀疏、三个稠密，第九个是专门构造的行空间伪装输入。共12次两方运行、108个逻辑批次，两方输出全部通过按原始残差生成期望值的独立检查。

下表是每次九个批次的两次算术均值。通信含真实预处理；Time 是底座报告的含预处理耗时，不含编译、证书生成和完整进程建立。原始每次结果及编译/参与方日志完整保留。

| n | 方法 | 总发送 MB | Time 秒 | 在线秒 | triples | inverse tuples |
|---:|---|---:|---:|---:|---:|---:|
| 8 | moments | 15.7858 | 0.485943 | 0.257656 | 264 | 81 |
| 8 | coordinate | 21.4095 | 0.459860 | 0.229151 | 246 | 111 |
| 8 | rowspace | 15.7838 | 0.494851 | 0.256123 | 288 | 69 |
| 64 | moments | 17.8663 | 0.486352 | 0.264486 | 264 | 81 |
| 64 | coordinate | 62.7939 | 0.590844 | 0.243767 | 582 | 447 |
| 64 | rowspace | 17.8643 | 0.487054 | 0.260182 | 288 | 69 |

**解释：** 新方案与旧方案通信和总耗时接近，没有稳定加速优势；它消耗更多 triples、较少 inverse tuples。n=8 时简单基线的总耗时和在线耗时更低；n=64 时简单基线通信与总耗时较高，但在线仍更低。只运行两次，不能把小差异写成统计显著优势。

计数核对：rowspace 为 6×37+3×22=288 triples，7×9+6=69 inverse tuples；moments 为 6×33+3×22=264 triples，7×9+3×6=81 inverse tuples。生成秘密矩阵的成本已包含，没有为了优势改变成本口径。预处理按批生成，消耗数与实际生成/发送量不能按一比一解释。

原始入口：results/rowspace_paired01/summary.json。每个运行子目录包含源码副本、字节码、compile.log、party0.log、party1.log、manifest.json、verification.json。RESULT 的 attempts 在 rowspace 模式指 GL2 采样尝试，不是旧方案的遗漏重试；日志显式标记 ATTEMPT_KIND。

## 5. 可复现命令

输出目录必须是新的，不会自动覆盖历史结果。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
wsl -d Ubuntu-24.04 -- python3 construction/validate_rowspace.py --out results/my_rowspace_algebra
wsl -d Ubuntu-24.04 -- python3 construction/rowspace_limits.py --out results/my_rowspace_limits
wsl -d Ubuntu-24.04 -- python3 construction/old_bound_refinement.py --out results/my_old_bound
wsl -d Ubuntu-24.04 -- python3 mpc/rowspace_sweep.py --out results/my_rowspace_paired --sizes 8 64 --repeats 2
```

代数检查确定性可逐字重放；实际 MPC 的随机密钥、转录和耗时不应要求逐字相同。判断依据是检查结果和功能输出，而不是复用私密随机带。

## 6. 仍未运行或证明的事项

未完成跨机器、恶意份额/网络篡改、并发重启、侧信道、残差来源绑定或端到端 TLS 安全验证。当前真实运行是主动安全底座上的诚实执行，不能改称本项目已独立证明主动安全实现。一般 k 只有代数层，不是完整真实 MPC；新的精确稀疏定位也没有消除 gate 的概率错误或恶意中止。
