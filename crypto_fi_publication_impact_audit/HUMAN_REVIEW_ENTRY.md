# 人工密码学审阅入口：Frodo-FI两项主结果

2026-11-10。请以**公开打印算法与明确模型中的两个命题**为审阅对象。本入口自含命题、最短轨迹及证明责任；全文证明和有限证书通过末表直接访问。当前申请的是领域判断与数学复核，已有AI记录的身份和曝光在§5列明。

## 1. 目标版本与最小原始规范

目标为Jurkiewicz–Prabucka，DOI10.46298/fi.14425，当前期刊PDF与arXiv:2410.03948v4相同，23页，SHA256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。原文pp9–11为游戏，12为Setup/Enc/Dec，13为Ord/Tensor，14为TG/Upd，15为正确性充分定理，19–20为Lemma6.8/Theorem6.9，20–22为实现声明与性能表。官方2021规范PDF10给平局向上，14给D≤16的接口，18–19给基础残差/失败方法，25给χ640与参数。

冻结规范化：Ord_t对实际t列做D位0/1分解；Upd取t=n，位平面顺序与Tensor_D(S)=[S;2S;…;2^(D−1)S]相配，Ord_n(C₁)Tensor_D(S)=C₁S modq。源域写m̄×n̄与Upd输入m̄×n之间有类型缺项。相配的固定行置换保持两项结果；改变数字展开、形状或采样需单独定义。

## 2. 两项待审命题

**A。** λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，χ=精确χ640，T=t_max=n。所有原始χ条目和调用独立；A在其后采样前任意固定。最长n次诚实更新对所有消息和支持内样本逐样本正确。原rand-ind-eu-cpa攻击只用Enc、Next、token腐化及一次Challenge，最多3n+1次调用，Δ≥1−(3/4)^n−ε_n=1−negl(λ)。这是打印一般参数模型；官方D≤16 API和作者实际程序另行对应。

**B。** 固定n=640、D=15、q=32768、m̄=n̄=8、B=2。A均匀Setup，两代共用；所有原始χ640坐标和调用独立，一次Enc、一次诚实未筛选TG、一次Upd，Decode最近整数平局向上。任意预先固定合法128位消息、预先指定坐标/行：Pr(I)≥1−2^-132；Pr(E_c)∈[0.2499054,0.2500946]；Pr(E_r)∈[0.0000152532,0.000030345]；Pr(E_m)≤0.000030345，Pr(E_m^c)≥99.9969655%。条件于I后这些更新显示界保持。更新概率对均匀Setup和全部诚实币平均；初始界逐固定A成立。

χ640的0与每个正/负点质量分子为[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]，分母65536；0只计一次。负数用声明的模代表处理，理想表由16个独立均匀位精确抽样。

## 3. 最短攻击与A的证明节点

在epoch0和phase0开始，固定消息M：Enc₀(M)取得完整诚实父C；Next到1；Corr(token,1)取得((P₁,Q₁),(P₂,Q₂))；Challenge₁(M,C)取得fresh或update。立即输出，Key/Dec/普通Upd/随机带请求及挑战后Next均为0。

取父第一行的h=Ord_n(c)及挑战第一行y。P₂可逆时算r̂=(y−hP₁)P₂^-1，属于Sχ^n则猜update；P₂奇异时公平猜测。真实update精确恢复r。空Key泄露使K*=∅，终局K*∩C*=∅；同消息和登记父满足挑战权限。

定理1的关键是**固定A、P₂以及父/H、U₁、fresh y时保留F₁随机**。记w为h的Hamming重量，μ_j=‖χ^{*j}‖∞为模群卷积峰值。逐列有hF₁=y−hU₁A−rP₂；高重量时每列卷积峰值≤μ_w0，枚举固定r只用于并集分析。n≥64时取w₀=64、h_support=25、a=maxχ=1161/8192，给

\[
\epsilon_n=\min\{1,\binom n{63}a^{n-63}+(25\mu_{64})^n\},
\quad\beta\le\alpha\epsilon_n.
\]

该ε_n式用于n≥64；n<64按v2置ε_n=1。首个可逆边界的停止只读P₂，每轮重做一份诚实父，支付真实轮换预算；条件于完整P₂序列后所选父/F₁仍有相同抽样律。χ640奇偶各半给α=p_n=∏_(i=1)^n(1−2^-i)>1/4。γ=25μ₆₄<1/2使ε_n可忽略，k=n即得A。共同正确性由B₀+nW<q/8承担，B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²，s=12。

## 4. B的概率链与应保留的依赖

更新残差为η₀+δ modq，η₀=U₀E_old−F₀S_old+G₀，δ=(HU₁+RU₂)E_new−(HF₁+RF₂)S_new+HG₁+RG₂。正确集合为D={−4096,…,4095} mod32768，逐消息标签一致。

单坐标先固定两代钥匙、父侧币及R的环境F，保留独立TG行：Φ_F(t)=ζ^(tη₀)G(t)^w∏_iG(tr_i)。坏环境<2^-22，全频率给1/4±(1/10600+2^-46+2^-22)。均匀Setup在u含奇数时使uA+f逐列均匀，H的9600位公平独立；这是B更新概率的A量词依据。

行级改用V=σ(A,U₀,F₀,U₁,F₁,U₂,F₂,R)。钥匙/G的8个列包此时iid，故p_row=E[p(V)^8]。在B_env=σ(A,U₀,F₀,R)下，a=hU₁+rU₂和b=hF₁+rF₂的1280系数有真实共同律T=Σ_(ℓ=1)^wX_ℓ+Σ_ir_iY_i modq。先合并共享钥匙系数，再对每个特征函数因子取模，得

\[
E[|\Phi_V(t)|\mid B_{env}]\le(E_T|\psi(tT)|^2)^{640},\quad
E_T|\psi(tT)|^2=\sum_{d=-24}^{24}\nu_d\varphi_B(td).
\]

全部rank在原始U/F外层积分；未改善的ν质量用单位包络保留。全部频率1–16384按1、2–3、4–7、8–15、16–63、64–16384覆盖，负频率配对，Nyquist保守计费。每个指数的Taylor倒数包络先向上取64位，再精确ν加权，最后对640次幂向上取80位。

\[
Z_*={27303052442598203493\over2417851639229258349412352},\quad\delta_B=2^{-25},
\]
\[
L_*=[(1-\delta_B)(1/4-Z_*)]^8,\quad
U_*=(1-\delta_B)[4^{-8}+(21845/16384)Z_*]+\delta_B.
\]

行下界来自Jensen，上界来自逐点弦线。完整事件E_m⊆E_r给完整消息上界；全零U₀/F₀/R事件另给完整非空性下界，行下界保持自己的事件范围。初始PGF Aχ(z)Bχ(z)^1280在z=21/20处给单坐标尾≤2^-138，64坐标并集给Pr(I^c)≤a_I=2^-132。无条件联合链完成后，用(L−a_I)/(1−a_I)与U/(1−a_I)限定I，条件显示端点保持；给定V和I的列独立性无需额外假定。

## 5. 现有AI复核身份

| 记录 | 实际身份/曝光 | 范围与计算 |
|---|---|---|
| ROUND-005旧攻击复核 | 一名AI的两阶段流程；phase1未见作者推导，phase2同审阅者读稿比对 | 固定A、选择、有限表与CF-1按各自封存范围沿用 |
| 精确LWE复核 | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 作者证明可见；丰富/固定样本与环上线性化范围；v2修正已落实 |
| 640首轮，01a1c4d6… | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 两份作者证明可见；375项总检查含100条引用指纹，作者脚本副本重放 |
| 640补充轮，01a1c4ed… | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 作者与前轮通过结论均可见；303项标量检查，两作者脚本副本重放 |
| v2作者整合及本轮审计 | 知情作者整合；知情应用/原声明审计 | v2重放303项；本轮不新增独立概率证明认证 |

两次概率审阅记录的精确后端型号均为null，所声明家族为GPT-6或Codex基于GPT-6；不同会话仅表明不同调用上下文，模型错误过程独立性未认证。新增人工、跨模型、盲审和证明助手认证均为0。检查计数记录执行范围，方法优先权与数学充分性由具体证明承担。

## 6. 三个最有决定性的人工问题

| 问题 | 最小输入 | 请判断的明确命题及改变后果 |
|---|---|---|
| H1：A是否为同一原游戏内的共同正确族攻击？ | 目标pp9–15；v2 §§2–6与附录B的640卷积证书；本入口§§1–3 | Ord列数规范化是否准确保持源对象；四查询/空Key终局是否合法；固定P₂后F₁保留与P₂-only停止是否足以支持所列优势，并与CF-1全样本正确性同合同。任何反例应指出具体输入、条件化或原游戏行 |
| H2：B的真实联合概率链是否完整？ | 目标pp12–15；官方规范10/25；v2 §7.2和附录D；两份作者标量证书及补充轮重算证书 | 同行列包、1280系数律、全频率绝对矩/弦线、坏质量、64/80位上取整、事件包含与I条件化能否严格推出完整错误≥99.9969655%，且保持均匀Setup量词。请给通过范围或具体失效式 |
| H3：哪些源条件安全声明能被严格评价？ | 目标pp19–20 Lemma6.8/Theorem6.9；v2 §§8–9及附录A；另需2024版Nishimaki Lemma5.7与构造/参数邻文 | 源归约究竟对应哪个(n,m,q,χ、秘密先验、辅助视图、时间、PPT/QPT)前提；能否给与CF-1匹配且已认证的非空困难前提。若仅能恢复H_rich，应将前件失效与构造攻击分别登记；若为H_fixed，须给足参数化模拟 |

H3所需前驱PDF当前403；可先审H1/H2，H3在取得带版本/公开日期/哈希的合法全文后完成。作者实际性能对象的判断另需commit/config/随机带和更新后消息比对轨迹，本入口不把缺失程序当作已实测的失败。

## 7. 直接阅读入口与文件分工

| 材料 | 入口 | 用途 |
|---|---|---|
| 目标期刊/v4 | [arxiv_v4.pdf](D:/毕业设计/crypto_fi_publication_impact_audit/sources/arxiv_v4.pdf) | 原始游戏、算法、定理与性能表 |
| 官方2021规范 | [official_frodo_2021.pdf](D:/毕业设计/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf) | 舍入、χ640、参数及基础正确性 |
| 完整研究稿v2 | [CRYPTOANALYSIS_DRAFT.md](D:/毕业设计/crypto_fi_research_manuscript_v2/CRYPTOANALYSIS_DRAFT.md) | A：§§2–6、附录B；B：§7.2、附录D；LWE：§§8–9、附录A |
| 机器主张v2 | [CLAIM_EVIDENCE_MATRIX.json](D:/毕业设计/crypto_fi_research_manuscript_v2/CLAIM_EVIDENCE_MATRIX.json) | C08/C09、C25a/C25d及完整精确概率证书 |
| 640卷积证书 | [chi_640_64fold_coefficients.json](D:/毕业设计/crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json) | A的完整64重整数系数 |
| 作者单坐标证书 | [SCALAR_CERTIFICATES.json](D:/毕业设计/crypto_fi_640_correctness_audit/evidence/SCALAR_CERTIFICATES.json) | B初始PGF、坏环境、单坐标整数比较 |
| 作者联合证书 | [JOINT_SCALAR_CERTIFICATES.json](D:/毕业设计/crypto_fi_640_joint_correctness/evidence/JOINT_SCALAR_CERTIFICATES.json) | B的ν、全部频率、R/Q及L/U分数 |
| 首轮概率审阅 | [MATHEMATICAL_REVIEW.md](D:/毕业设计/crypto_fi_640_probability_review/MATHEMATICAL_REVIEW.md) | 作者证明可见的完整概率链 |
| 补充概率审阅 | [MATHEMATICAL_REVIEW.md](D:/毕业设计/crypto_fi_640_probability_review/review_01a1c4ed/MATHEMATICAL_REVIEW.md) | 作者与前轮审阅可见的完整链及呈现修正 |
| 补充轮重算证书 | [RECOMPUTED_PROBABILITY_CHAIN.json](D:/毕业设计/crypto_fi_640_probability_review/review_01a1c4ed/evidence/RECOMPUTED_PROBABILITY_CHAIN.json) | 303项检查与全部精确分数 |
| 补充轮标量脚本 | [recompute_probability_chain.py](D:/毕业设计/crypto_fi_640_probability_review/review_01a1c4ed/evidence/recompute_probability_chain.py) | 确定性有限数学；阅读或复制重放均可，历史目录保持只读 |
| 精确LWE审阅 | [MATHEMATICAL_REVIEW.md](D:/毕业设计/crypto_fi_lwe_independent_review/MATHEMATICAL_REVIEW.md) | H_rich/H_fixed与环上线性化的已登记范围 |

原始阅读顺序为目标算法/游戏→命题A或B→对应完整证明→有限证书。人工审阅无需重读本项目业务系统材料。应用优先权的检索范围与缺项见同目录APPLICATION_PRIORITY_AND_IMPACT.md。旁支INC976仅涉及v2附录B的976显示表，两个主结果均使用χ640；当前历史文件保持只读。
