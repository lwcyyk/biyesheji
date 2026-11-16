# 定向先例与贡献裁决

2026-11-07。身份为知情来源审计及推导整理，独立复核0次。本轮使用academic-research-suite的来源／阅读记录方法及PDF原图核对；工具审计与学术独立性分别登记。原文及哈希见 [来源记录](sources/SOURCE_AND_READING_RECORD.json)。所有概括限定于实际阅读位置。

## 1. 直接先例：隐藏重加密钥匙、接收方秘密与平均

[Cohen、Cousins、Genise、Kline、Polyakov、Saraswathy RV，HRA-Secure Homomorphic Lattice-Based Proxy Re-Encryption with Tight Security](https://cic.iacr.org/p/2/1/22/pdf)，IACR Communications in Cryptology 2(1)，31页，DOI [10.62056/ab0l5wol7](https://doi.org/10.62056/ab0l5wol7)。固定出版PDF于2025-01-10收到、2025-03-11接受；本轮下载全文，SHA-256为99c8e230633ff62d0d91c8a2f6a13c1e000d8cee0cd46f4cda7c36d9cb6902a7，31页结构预检PASS。ePrint2024/681的修订历史未与此字节自动等同。

实际阅读：pp.1–4引言相关段，§2.2／Definitions5–8 pp.6–9，§3相关pp.10–12，Appendix B pp.28–29；公式原图核对pp.8、11、12、28、29。全文取得与全文逐页审阅分别登记。

| 比较项 | 原文内容与本轮对应 |
|---|---|
| 攻击权限 | Definition7 p.8允许非挑战诚实源到腐化目标的ReEnc，目标sk已知；相应重加密钥匙不给攻击者 |
| 同父重复 | ReEnc检查登记表并追加子记录，父保留；Appendix B明确重复重加密同一密文 |
| 算法关系 | Algorithm8 p.28：bit decomposition、固定key switching，再加fresh Enc(0) |
| 原始误差 | p.29分为固定key-switch误差作用、fresh目标加密噪声、固定父误差ect |
| 攻击方法 | 先处理公开二进制矩阵形成的(R)LWE关系，再用重复输出平均恢复固定ect，继而恢复源秘密 |
| 概率／样本 | 附录给攻击草图及均值估计的平方级噪声依赖，脚注6提及Hoeffding／Bernstein；所读段未给本轮Q、R、δ的完整gap式 |
| 安全口径 | 论文采用带输出概率和条件成功项的混合安全度量及bit-security参数；其具体优势数值与本轮实验概率差各有定义 |

这份公开原文直接覆盖“隐藏重加密token时，已知接收方秘密＋重复输出仍可利用误差进行平均攻击”的中心方法。对其DDLM19目标算法的批评，本稿表述为该论文的攻击结果，DDLM原版全文尚未核准。

与本轮的精确差别：本轮直接恢复每父固定μ标签，结合诚实样本生成模学习HAΔ；无需先恢复附录的x，也无需恢复完整源秘密。随后使用实际可见C闭包和mean-update解码形成fresh/update单侧分类。这些差别支持技术映射与显式边界命题；单凭差别列表无法认证原创性。

## 2. 线性残差与无偏噪声平均已有基础

[Baiyu Li、Daniele Micciancio，On the Security of Homomorphic Encryption on Approximate Numbers](https://par.nsf.gov/servlets/purl/10340712)，EUROCRYPT2021，LNCS12696 pp.648–677，DOI10.1007/978-3-030-77870-5_23。本轮取得30页会议排版全文，SHA-256为3189ba0432e73a90aa2cb55065a03b2c9e9ce31144719fae80bff931d231f5ea，结构预检PASS。

实际阅读：§3相关oracle定义段；§4.1印刷pp.665–667；§6印刷pp.673–674；图像核对PDF18／26／27，对应印刷665／673／674。

§4.1给已知密文和近似解密结果生成精确线性秘密作用的关系，再解线性系统。§6 pp.673–674明确讨论重复请求同一密文的解密、对无偏新增噪声求平均、舍入或线性／格方法消除剩余误差。其接口为受限近似解密oracle，本轮用未来完整S₃在本地计算原始残差；接口的合法来源不同，平均和线性恢复工具已有成熟基础。

该源还讨论确定性扰动、限制重复调用、noise flooding及精确舍入。这里没有自动导入它对任何UE的完整安全结论，也没有将CKKS的数值实验数据赋给本轮查询量。

## 3. 噪声淹没与总重复预算

CiC2025 §3／Theorem2原图p.11将HRA查询上限τ显式纳入安全参数。其引用LMSS22的噪声标准差形式为

\[
\sigma=\sqrt{12\tau}\,2^{\nu/2}t,
\]

其中t是要掩盖的误差尺度，ν是统计参数。Theorem2给KL模拟距离ρ到至多τ次查询的混合bit-security保证；Algorithm6原图p.12包含额外flooding、key switching及modulus switching。后两项也可能改变本轮未经压缩的整数残差表示。

因此“存在隐藏随机性”本身无法确定重复攻击成本。需区分固定父噪声、固定token误差与每次新鲜噪声，并将查询总量与新鲜噪声参数共同冻结。本轮CF2的V=Θ(λ²)，Hoeffding给多项式估计；当新鲜V数值超多项式、重复次数受限，或舍入消除了可读取残差时，当前实例定理的前提可能改变。

LMSS22原文的完整最优界未在本轮取得；以上公式及应用范围依据CiC2025原图，未登记为对LMSS全文的新审阅。CiC的HRA正面构造与本轮矩阵对象各有算法和预算，当前证明没有攻击该正面构造。

## 4. UE模型和正面对照

| 原文／固定对象 | 实际核读位置 | 与本攻击的关系 |
|---|---|---|
| FI-v4，DOI10.46298/fi.14425，冻结PDF与本地arXiv2410.03948v4字节记录 | §§4–6，重点原图pp.10、12、14、15；已读历史原图记录另列 | 原始矩阵／小噪声结构匹配；Next直接登记C使本轮未来Key轨迹无效。结论约束其算法在MATRIX-SELECT接口中的使用 |
| CANS2024，Updatable Encryption Secure Against Randomness Compromise，LNCS14906 pp.47–69，DOI10.1007/978-981-97-8016-7_3 | 印刷pp.52–55、Figs.1–2、Def.3.1，RISE §4 | 普通带、重复父、未来Key及实际可见C已有发表接口先例 |
| IEICE2026，E109-A(3):232–245，DOI10.1587/transfun.2025CIP0020 | 印刷pp.235–238、Figs.1–3、§§3–4 | RISE满足其UE-R定理；原始密文为群元素，无法直接形成本文小整数均值观测 |
| GP23，Backward-Leak Uni-Directional Updatable Encryption from (Homomorphic) Public Key Encryption，PKC2023，冻结出版PDF | §5.1印刷p.417及§5.3／Fig.5印刷pp.419–420 | 本轮冻结GP群实例添加新pad／钥匙坐标，属于正面对照。一般框架中的LWE举例还需完整实例映射 |
| 项目GP23/CTX1 SELECT／SPEC2 | SELECT_CONSOLIDATED_2及SAMPLER_AND_FAILURE_SPEC | 已给定群／域接口和有限终局；当前仅使用其游戏骨架实例化矩阵对象，群证明继续限定自身 |

RISE和GP群实例的输出在有效指数表示上有计算边界。将群元素的字节看作整数，对center求均值，会失去算法要求的线性作用及小噪声关系。故“未来Key＋重复普通输出导致所有UE不安全”的扩大主张缺少依据。

项目已有ROUND-007诚实模生成学习结论、HNF/SNF及Hoeffding均作为已知／已有工具引用。本轮增加的是在有效更新系数隐藏时，通过未来秘密和重复输出生成其训练标签的充分条件，以及完整错误预算。

## 5. 保留来源缺项

| 缺项 | 已取得证据 | 能改变判断的具体内容 |
|---|---|---|
| Cohen，What about Bob?，PKC2019／ePrint2017/785 | 作者主页确认书目信息；CiC2025追溯其HRA和秘密恢复。IACR原PDF本轮抓取403／TLS失败 | 原版攻击是否已给诚实父模生成、固定token作用学习及相同UE闭包映射 |
| DDLM19，Strong Post-Compromise Secure Proxy Re-Encryption，ACISP2019／ePrint2019/368 | 主源索引和CiC附录攻击；原PDF抓取403 | 正式算法、参数、源隐藏量词、重复重加密oracle及原声明的准确范围 |
| LMSS22完整正文 | CiC2025已读原图给明确引用和使用公式 | 对相同完整接口、重复上限及具体矩阵族的更强覆盖定理 |
| Nishimaki RtR正式原图／完整参数及采样 | 历史档案文本映射 | smudging初始噪声与fresh更新噪声的真实幅度；是否共同无回绕、未来Key是否合法；±1支撑下mean-update的解码界 |
| 实际FI性能程序与种子联合律 | 论文性能表、此前源记录 | 是否限制父重用、公开S₃、输出压缩及固定参数上可验证的条件方差／提升界 |

这些缺项不会撤销已经从全文确认的平均方法覆盖，也不影响具名CF2的纸面证明；它们约束原创性、其它发表构造及实用性扩张。

## 6. 最强可支持贡献与结束裁决

**数学：VERIFIED，限知情纸面审查。** 在明确MATRIX-SELECT输出模型与CF2族，隐藏有效更新系数以后，未来完整秘密和重复诚实父更新足以恢复解密作用，并获得常数fresh/update优势。其完整证明包含整数提升、条件均值、模块遗漏、mean-update正确性和两实验失败计费。

**方法先例：VERIFIED_COVERED。** 重复输出平均、从解密误差学习秘密作用，以及诚实到腐化目标PRE的隐藏重加密钥匙攻击已有直接全文先例。

**发表构造作用域：VERIFIED_SCOPED。** 当前是FI-v4算法在具名实际可见C接口中的边界实例。该轨迹未形成新的FI-v4原游戏反例；RISE及冻结GP群实例的正面定理保留。其它格UE原游戏攻击继续等待逐式来源映射。

**原创性／硕士论文主创新：SOURCE_UNRESOLVED / NEEDS_CLARIFICATION。** 当前最强表述是：

> 将已有平均攻击与诚实父模生成工具结合，明确证明一类可读取小整数解密残差、具有合法未来完整Key及重复更新接口的矩阵UE，即使隐藏有效更新随机性，仍可学习隐藏边界的解密作用；给出FI打印算法在MATRIX-SELECT中的共同正确多项式族和完整优势账本。

这是可供独立审阅的范围明确的密码分析／模型边界命题。现有证据支持作为论文中的边界分析或攻击章节；作为独立核心创新，需要进一步证明发表原游戏中的新增适用范围、实质更强定理或经原文对照确认的技术增量。保护机制实现资格门继续保留，严格资源分离实例尚未建立，本轮没有启动实现。

下一次独立审阅的最小输入：本轮四份MD、VERDICT、固定输入锁、FI原图pp.10/12/14/15、χ₆₄₀表、SELECT §3／失败规范、ROUND-007模生成引理，以及CiC2025 Appendix B。重点反驳点是合法性登记、固定θ后的零均值、整数提升、r=0解码、训练错误两次扣费和先例覆盖。

## 7. 主线合同与资源范围

沿用ONLINE_TRUSTED_STATE_V1已有的证据边界。本轮没有取得新增的未来完整Key曝光、可重复调用次数、token隔离或有效系数日志泄露业务合同，CF2的权限是纸面游戏假设。已有投影中的operation_limit为null，不能据此引入确定的硬查询上限或认证约10¹⁹次调用可行。凭据存储机密性与原生AS/RP撤回仍使用各自证据，本轮原生请求为0。
