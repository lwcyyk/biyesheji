# 多行私密诊断：本轮结果与贡献判断

2026-11-03，multirow-explore-r3。

**本轮出现了比此前更实质的独立理论贡献候选：最优非均匀核掩码，以及最优统计隐私对字典表示的敏感性。数学论证和有限精确证书已有结果；强原创性优先权及实际协议价值仍未最终确认。**

## 1. 两项主要结果

### A：尖锐界与匹配构造

在四列三维标架、允许全部至多三故障支持、输入独立双行掩码且每个位置绝不抹除的模型中：

δ*=(q−2)/[(q−1)(q²−3)]。

下界覆盖秩1/2混合分布；采用对两条对边上的核点提高概率的分布达到该界。q>3时严格优于均匀合法核。完整手工证明见 [THEOREM.md](THEOREM.md)。

这一严格分离说明“均匀合法掩码总是最优”的推广不成立，但相对改善仅O(q^−2)，不能宣传为实际加速或大幅提升安全参数。它的价值在于给出最优结构和下界，而非多报几个小数位。

### B：同一拟阵，不同最优隐私

GF(7)上找到两个3×6字典，每个三列子矩阵均可逆，列拟阵都为U_{3,6}。在完全相同的双行、无抹除、幅值和支持契约下：

δ*(V_A)=11/204，δ*(V_B)=31/576，精确差1/9792。

两个值均有有理数原始—对偶证书，经不调用优化器/生成器的独立检查器验证。这是有限实例的精确最优结果，不只是浮点LP猜测。普通列拟阵、全部子集秩和特征多项式都不足以决定这一最优值。见 [REPRESENTATION_SEPARATION.md](REPRESENTATION_SEPARATION.md)。

模型归约本身仍是手工证明；证书只确认其有限LP实例，不能自动证明一般归约或文献原创性。

## 2. 新增的安全边界

如果公开核属于高/低概率类别的那一位，模拟误差会从L_q增加到(q−1)L_q。q=4时从2/39增加到2/13。分支虽与输入独立，却与后续掩码输出相关，不能认为公开无害。

因此当前概率分布不是已经安全部署的采样器。没有新MPC执行，没有把秘密核选择、坐标模式或预处理当成免费接口。

## 3. 已完成的核对

| 检查 | 范围 | 结果 |
|---|---|---|
| 四列标架候选/均匀基线 | GF3/4/5/7/8/9 | 6域全部符合闭式，q>3严格改进 |
| 允许秩1/2混合的独立LP | GF3/4/5/7 | 4域与手工下界一致；数值最优仅辅助 |
| 完整矩阵与输出分布 | GF3/4全部624/3780个秩2矩阵，候选432/3060个 | 140组基/幅值比较符合精确误差 |
| 相同拟阵的表示探索 | GF9的21个U3,5实例；GF7/11的12个U3,6实例 | U3,5所测实例未分离；U3,6出现不同值 |
| GF7精确最优证书 | 两个2675变量LP；各4580个不等式、21个等式 | 有理数上下界完全相等；12项篡改拒绝 |
| 证明中的符号恒等式 | 概率归一化、下界交点、严格差值等6项 | 全部约为0 |
| 公开采样类别反例 | GF3/4共35组幅值 | 联合转录误差增大，符合推导 |

## 4. 原创性与应用的准确定位

新结果可以不依赖AI代理系统独立陈述，有明确反驳条件、一般族上的匹配界和有限表示反例。这比在认证流程外再拼接几个密码组件更接近独立理论工作。

但依然不能宣布“强独立密码学原创性已确认”。群平均、射影几何、轨道LP和对偶证书是既有工具；需要核对本文具体极值和表示反例是否已有等价结果。本轮扩大了先例检索，读取了q-polymatroid网络编码与非均匀窃听集合等相关一手资料，未把领域名称不同当作排重完成。

用户提供的共享解码期刊PDF已纳入分析，先前正文缺失已关闭。它的Padé与错误定位协议是必须比较的既有机制；本文未主张发明这些子程序。来源、实际读取位置、反方审查和未决项见 [PRIORITY_AND_VALUE.md](PRIORITY_AND_VALUE.md)。

目前主要价值是理论：普通拟阵抽象对多行统计隐私不充分，以及均匀采样的最优性存在明确边界。尚无大域实用采样、完整MPC成本优势、恶意安全或主线部署结论。GF7反例的误差约5%，只能作为数学反例，不能当部署参数。

## 5. 复现与源码

从 `D:\毕业设计\研究\密码学辅助_一致性核验` 执行，输出目录需未存在：

```powershell
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/kernel_minimax.py --out results/kernels02
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/mixture_reference.py --out results/mixed02
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/full_matrix_check.py --out results/matrices02
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/certify_representation.py --out results/representation_cert02
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/check_representation_cert.py --cert-dir results/representation_cert02 --out results/representation_check03
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/algebra_checks.py --out results/symbolic02
wsl -d Ubuntu-24.04 -- python3 -B revisions/multirow_explore_2026-11-03_r3/leakage_check.py --out results/leakage02
```

纯证书验证只需Python标准库；探索使用现有NumPy/SciPy，符号核对使用现有SymPy，未安装新依赖。探索器只读复用r2的有限域定义，其哈希单列；独立证书检查器不依赖该定义。

`source_snapshot.zip`、`manifest.json`和原始results保存本轮复现材料。原r1/r2及指定输入只读核对，auth-lifecycle无写入。

## 6. 当前目标状态

数学候选已经比上一轮明显加强；本轮没有把目标标记为“强原创性完成”。接下来最重要的工作是独立复核一般归约/下界，以及完成新极值与表示敏感性的优先权核验。若不能建立更广适用性或真实协议价值，应保留为受限理论结果，不能因已经投入工作量而扩大主张。
