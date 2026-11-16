# FI发表对象、算法与原游戏归属

2026-11-08，Asia/Shanghai。身份：`INFORMED_SOURCE_AND_CONTRIBUTION_AUDIT`。本会话已知攻击推导和历史审阅结论；新增独立审阅数为0。数学输入采用[ROUND-005引用稿](../crypto_branch_monitor/round_005/THEOREM_FOR_CITATION.md)。本轮使用academic-research-suite的来源核查流程及PDF原图核读；原始材料保持只读。

## 1. 固定发表对象

**VERIFIED：当前期刊下载件与冻结arXiv v4逐字节相同。**

| 项目 | 可重放证据 |
|---|---|
| 题名、作者 | M. Jurkiewicz、K. Prabucka，*Unidirectional Key Update in Updatable Encryption, Revisited* |
| 正式入口 | [DOI 10.46298/fi.14425](https://doi.org/10.46298/fi.14425)，[出版社记录](https://fi.episciences.org/17222) |
| 当前期刊文件 | [publisher_current.pdf](sources/publisher_current.pdf)，本轮从[出版社PDF端点](https://fi.episciences.org/17222/pdf)重新取得，464697字节 |
| 冻结对象 | [FI_v4_frozen.pdf](sources/FI_v4_frozen.pdf)，arXiv:2410.03948v4，23页，结构预检PASS |
| 两文件SHA-256 | `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4` |
| 时间 | v1：2024-10-04；v2：2024-10-08；v3：2025-08-09；v4：2025-12-29。出版社：提交2024-10-10、接受2025-08-08、上线2026-01-11 |
| 年份差异 | PDF首页印2025；出版社、arXiv期刊字段和Crossref记在线发表2026-01-11。引用同时保留卷194、期4、Article4、DOI和v4，避免用年份代替版本 |
| 具体安全声明 | PDF p11：对每个PPT对手的rand-ind-eu-cpa概率差可忽略；p20 Theorem6.9：在LWE假设下，所给FrodoPKE型UE在backward-leak uni-directional设置安全 |
| 可追溯源包 | [FI_v4_source.tar](sources/FI_v4_source.tar)，37734字节，SHA-256 `eb20e59259f9f848405bf8e5212f81e9417cc49d347f2958ad0a6c4e174a3b9a` |

源包仅含`00_my_def.tex`、`00README.json`、`articlev08.bbl`、`articlev08.tex`、`fundam.bst`、`fundam.cls`。它认证排版公式，作者UE性能程序及其配置仍待取得。当前期刊文件等同v4，接受当日稿的逐字节身份另无声明。

历史v1/v2存在epoch递增等游戏排版缺口：Next首行印qid递增，Upd资格检查也使用qid−1。旧版算法第一块关系相同，游戏级结论须带修正说明。本轮主定理只绑定当前期刊/v4；v3关系使用已有定向版本比较记录。[历史版本核查](../crypto_frodo_priority_audit/SOURCE_AND_VERSION_MAP.md)保留各版哈希和实际阅读范围。

## 2. 算法字段、类型与真实联合分布

以下模数均为q=2^D；χ先取有符号整数，再嵌入Z_q。S是嵌入后的真实支持，h=|S|；当前参数q>2s，故h=2s+1。矩阵条目和各次标χ调用按理想模型独立。公开A在这些采样前固定，FI.Setup的均匀A为其特例。

| 字段 | 维度 | 源位置 |
|---|---|---|
| A | n×n | PDF p12 Setup；TeX L508起 |
| S_e、E_e、B_e=A S_e+E_e | n×n̄ | p12 KeyGen；TeX L517起 |
| 完整key_e=(S_e,B_e) | 两个n×n̄矩阵 | p13 UE.KG；TeX L607起 |
| 父C=(C1,C2) | m̄×n、m̄×n̄ | p12 Enc、p13 UE.Enc；TeX L535–546、L618起 |
| U0、F0；C1=U0 A+F0 | m̄×n | p12 Enc第一块 |
| U1、F1、G1 | nD×n、nD×n、nD×n̄ | p14 TG；TeX L635 |
| U2、F2、G2 | n×n、n×n、n×n̄ | p14 TG；TeX L636 |
| P1=U1 A+F1；Q1=U1 B_new+G1−Tensor_D(S_old) | nD×n、nD×n̄ | p14 TG第4行；TeX L637 |
| P2=U2 A+F2；Q2=U2 B_new+G2 | n×n、n×n̄ | p14 TG第5行；TeX L638 |
| token=((P1,Q1),(P2,Q2)) | 全部四块 | p14 TG第6行；TeX L639 |
| H=Ord_n(C1)、R | m̄×nD、m̄×n | p14 Upd第2–4行；TeX L649–651 |
| 更新输出 | Y=H P1+R P2；Z=C2+H Q1+R Q2 | p14 Upd第5行；TeX L652 |

χ支撑内的R是Upd唯一新随机矩阵。打印TG没有可逆筛选、重采或拒绝循环；Upd没有额外独立加性噪声。P2确为token内返回的方阵。Q块、key和C2存在共享钥匙及A的关联，固定攻击的选择和输出只读取父第一块、P1、P2和挑战第一块；完整父仍原样提交登记接口。

### Ord类型规范化

p13/TeX L580的Ord字面域写成m̄×n̄，p14却将其用于m̄×n的C1；TG相应有nD行。采用列数参数化`Ord_t:Z_q^(m̄×t)→{0,1}^(m̄×tD)`，本对象调用t=n。单行顺序为

`(c_1,0,…,c_n,0, c_1,1,…,c_n,1, …, c_1,D−1,…,c_n,D−1)`。

Tensor_D(S)=[S;2S;…;2^(D−1)S]，p13 Remark6.1/TeX L589–590的恒等式为Ord_n(C1)Tensor_D(S)=C1 S modq。逐位定义、TG行数和该恒等式共同确定这个处理。它补齐列数类型，逐元素计算配方和位平面顺序沿用原文。n≠n̄时，完全保留字面域的未补齐程序有类型缺口；本轮结论明确携带此规范化。加入噪声、隐藏字段、改变矩阵形状或改写游戏的方案需另立对象。

## 3. 最短合法见证：四次调用

固定任意消息M∈{0,1}^(B m̄ n̄)。以下b为实验内部位。

| 时刻 | 调用及返回 | 登记/权限依据 |
|---|---|---|
| epoch0 | `C←O.Enc(M)` | p9 Enc L1–4：qid加1，登记(qid,C,0;M) |
| epoch1 | `O.Next()` | p10 Next L1–3：e加1并生成key1、token1。phase=0，L4–7的挑战更新登记分支跳过 |
| epoch1 | `Δ1←O.Corr(token,1)` | p9 Corr L1、L6–8：1≤e，登记T={1}，返回完整token |
| epoch1 | `C*←O.Chall(M,C)`，计算检验并立即结束 | p10 Chall L1–5检查唯一挑战和上一代登记父；L6–9依b作Enc/Upd；L10–12登记并返回 |

终局K=K*=∅、T=T*={1}、C={1}、twf=0。p9 backward闭包只能从已有Key传播，空Key集保持空。p11终局只在K*∩C*非空时失效，所以任何由原规则得到的C*均给空交集。p11将C*的具体生成程序转引Jiang；对本攻击无需补全该外部程序：C*包含1且限于已生成epoch，K*=∅已经决定合法性。在只向未来更新的解释下C*={1}；采用更大的回推闭包也保持同一终局结论。

同消息挑战合法：父消息M与fresh消息M相同，Chall没有不相等检查。攻击辨别来源，无需消息差。Key、普通Upd、Dec、挑战版本读取和随机带请求均为0；基础游戏本身已经提供全部输入。增强随机带接口对该攻击的运行无贡献。

四次是从epoch0按所打印接口取得登记父、存在的目标token及挑战的最短见证。公平奇异分支使用对手自己的新公平比特。

## 4. 自适应首次可逆策略的完整账本

对j=1,…,k，进入epoch j−1后新做Enc(M)，再Next至j并Corr(token,j)。J是P2序列的首次可逆位置；J≤k时，用这一轮的完整父调用唯一Challenge并立即输出。全部奇异时独立公平猜测。父选择规则固定为每轮刚生成的一份，J的计算只读取P2；父特征、P1、Q块和C2均未参与停止选择。

成功停止时终局K*=∅、T*=T={1,…,J}、C={J}；全失败时C=∅。相同空Key论证核准所有终局。挑战后的Next数为0，p10的自动挑战后继登记不会发生。原游戏是对PPT对手量化，未另给常数级总调用限制；k≤T且k为多项式即可。T按p18表示最大epoch标签，T次Next对应T+1个状态。

| 资源 | 最坏调用数 |
|---|---:|
| Enc、Next、Corr(token) | 各k |
| Challenge | ≤1 |
| Corr(key)、Upd、Dec、Upd挑战读取、随机带接口 | 全为0 |
| 总调用 | ≤3k+1 |

整个b相关响应出现前，父/token/停止位置的分布完全相同。全失败公平输出在两个实验中抵消。CF-1取k=T=n，支付全部n次真实轮换。

## 5. 原图、转录与审阅证据等级

本轮定向原图核读FI pp9–15、18–20；p8闭包背景作文本核读。复杂公式以冻结PDF为准，TeX作定位补证：[articlev08.tex](sources/articlev08.tex) L342–434为游戏，L493–499为参数，L580–590为Ord/Tensor，L633–653为TG/Upd，L669–707为正确性，L818–884为混合与安全定理。源文件准确行号可按该冻结件复核。

ROUND-005 phase1是无作者推导历史的AI来源/数学审阅；phase2为同一审阅者读作者稿后的定向比对，两者计一个两阶段审阅流程。本轮重新核验phase1的23条、phase2的16条哈希及大小全部匹配。1344 N1秩细化、旧混合诊断和当前发表/优先权判断保持各自知情身份。来源与阅读登记见[sources/SOURCE_AND_READING_RECORD.json](sources/SOURCE_AND_READING_RECORD.json)。
