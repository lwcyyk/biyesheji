> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_research_manuscript_v2_2/HUMAN_REVIEW_ENTRY.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 人工密码学审阅入口：Frodo-FI研究稿v2.2

2026-11-11，Asia/Shanghai。审阅对象为已发表FI打印算法在明确Ord与采样合同下的两个主结果：共同正确族的来源隐藏攻击，以及官方640的一步可靠性分析。可靠性结果包含均匀Setup更紧界B_U和本版新增的逐固定A界B_FA。本入口给出精确命题、最短轨迹、关键依赖及完整证明/有限证书入口，供人工独立判断。

## 1. 目标版本与原始规范

目标论文为Mariusz Jurkiewicz、Kamila Prabucka的 *Unidirectional Key Update in Updatable Encryption, Revisited*，DOI10.46298/fi.14425，期刊当前冻结PDF与arXiv:2410.03948v4逐字节相同。PDF23页，SHA256：

`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。

源TeX articlev08.tex的SHA256为`16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b`。原文PDF9–11为游戏，12为Setup/Enc/Dec，13为Ord/Tensor，14为TG/Upd，15为正确性充分定理，19–20为Lemma6.8/Theorem6.9，20–22为实现与性能声明。官方2021规范PDF10给半向上舍入，14给D≤16接口，18–19给基础PKE残差/失败分析，25给精确质量与参数。直接数值CDF见2023物理PDF16/印刷12 TableA.4；1344采用官方2024-11-27勘误。

Ord规范化：对实际t列取D位0/1展开，Upd取t=n；按位平面排列，与Tensor_D(S)=[S;2S;…;2^(D−1)S]配对，满足H·Tensor_D(S)=C₁S modq。源定义的n̄列与Upd的n列间有类型缺项，本稿显式携带该解释。相配固定行置换保留gadget恒等式、矩阵乘积及iid行律。其它数字展开、形状或采样规格须按实际对象对应。

## 2. 两项精确结果及其参数/量词

**结果A。** λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，χ为精确χ640，T=t_max=n。A在全部相关原始χ之前任意固定，给定A后χ坐标与调用独立，Ord按§1规范化。初始加密至最长n次诚实更新对所有消息和支持内样本逐样本正确。原rand-ind-eu-cpa游戏存在合法PPT来源区分器，调用Enc、Next、token腐化及一次Challenge，最多3n+1次调用，Δ≥1−(3/4)^n−ε_n=1−negl(λ)，故Δ→1。该族属于打印一般参数模型；官方D≤16接口与作者固定配置分别对应。

**结果B的共同合同。** n=640、D=15、q=32768、m̄=n̄=8、B=2；两代共用A。给定A后，全部原始χ640坐标和调用满足精确独立乘积律。两次诚实KeyGen、一次Enc_old、一次诚实未筛选TG、一次Upd、Dec_new；全部P₂秩质量计入。采用§1的Ord规范化及官方最近整数平局向上Decode。每个合法128位消息及指定行/坐标均在相关币之前固定。记I为初始完整消息正确，J为预先指定一行的8坐标全正确，K为更新后完整64坐标正确。

| 结果版本 | A与概率量词 | 初始完整正确 | 指定行全正确 | 更新完整正确/错误 |
|---|---|---|---|---|
| B_U：§7.2、附录D | A真正均匀Setup，平均A与全部诚实币 | ≥1−2^-132；该初始界还逐A成立 | [0.0000152532,0.000030345] | 正确≤0.000030345；错误≥99.9969655% |
| B_FA：§7.3、附录E | 对每个在全部原始χ之前固定的A，平均给定A后的全部诚实币 | ≥1−2^-132 | [0.0000135117,0.005043360] | 正确≤0.005043360；错误≥99.4956640% |

两行额外条件于I后，同一显示行区间及完整正确/错误单侧端点仍成立。B_U另有指定坐标区间[0.2499054,0.2500946]及其I条件界；该更紧坐标区间只在均匀Setup模型引用。B_FA允许奇异、零矩阵及任意前置seed生成矩阵。

χ640的0和每个±k原子分子为`[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]`，共同分母65536；0计一次，非零正负各计一次。支持[−12,12]，奇偶各半，最大原子a₀=1161/8192。16个独立均匀位经严格阈值CDF规则精确采该表；秘密seed流是否产生所需多坐标/多调用联合律由实际迁移证明承担。

## 3. 最短攻击轨迹与共同正确性

在epoch0、phase0固定消息M：Enc₀(M)取得完整诚实父C；Next至1；Corr(token,1)取得((P₁,Q₁),(P₂,Q₂))；Challenge₁(M,C)取得fresh或update。立即输出。Key腐化、Dec请求、普通Upd请求及挑战后Next均为0。空Key泄露使K*=∅，终局K*∩C*=∅；同消息与登记父满足原游戏权限。

取父第一行h=Ord_n(c)、挑战第一行y。P₂可逆时，公开计算r̂=(y−hP₁)P₂^-1，若r̂∈Sχ^n猜update；P₂奇异时公平猜测。真实update逐样本恢复r。真实fresh的界须保留共享A及真实父/token分布：固定A、P₂、父/H、U₁与fresh y时，F₁仍独立；逐列卷积及支撑并集给β≤αε_n。

对n≥64，令μ₆₄为χ640的模群64重卷积峰值，

\[
\epsilon_n=\min\{1,\binom n{63}a_0^{n-63}+(25\mu_{64})^n\}.
\]

n<64置ε_n=1。χ640奇偶各半给α=p_n=∏_(i=1)^n(1−2^-i)>1/4。首个可逆边界的停止只读P₂，每轮支付Next/token及诚实父费用；条件于完整P₂序列后，所选父与F₁保留真实采样合同。25μ₆₄<1/2使ε_n可忽略，n轮得到结果A。

共同正确性逐A、逐样本由B₀+nW<q/8承担：s=12，B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²。通用充分式为B₀+t_maxW<q/2^(B+1)。s=12时源W_print的初始项吸收关系限于n,D正整数、T≥1、0≤t_max≤T及合法维度/编码合同。完整证明见v2.2 §§2–6。

## 4. 可靠性概率链及最关键证明位置

两代B_x=AS_x+E_x，父C₁=U₀A+F₀。原TG/Upd代入后，gadget抵消，真实残差为

\[
N=U_0E_{old}-F_0S_{old}+G_0
+(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2\pmod q.
\]

官方半向上Decode对四个编码标签具有同一正确集合D={−4096,…,4095} mod32768。消息标签平移与gadget消去使概率逐个预固定合法消息成立。

**B_FA的新增步骤。** 固定任意A、再固定u，C₁[k]=(uA)_k+f_k是独立χ平移，零质量≤a₀。非零坐标数L≤H位重量w；对0≤z≤1，

\[
E[z^L\mid A,u]\le[a_0+(1-a_0)z]^{640}.
\]

z=2/5时，以N_H=19867^640·5^450、D_H=40960^640·2^450精确认证2^73N_H≤D_H<2^74N_H。先界Pr(w≤450|A,u)，再对u平均，逐A得到Pr(w≤450|A)≤2^-73，覆盖w<450。R₂=Σr_i²以完整25点PGF及z_r=31/32给Pr(R₂≤3500|A)≤2^-27。好事件G={w≥450,R₂≥3500}是B环境可测，逐A坏概率<δ=2^-26，且w+R₂≥3950。关键位置：附录E.1–E.2。

**两层依赖。** B_env=σ(A,U₀,F₀,R)，V=σ(B_env,U₁,F₁,U₂,F₂)。V层剩余旧/新钥匙及G的8个列包iid，令p(V)为一坐标条件正确率，则Pr(J|A)=E[p(V)^8|A]。在B_env层，a=hU₁+rU₂、b=hF₁+rF₂的全部1280系数独立同分布于真实T=Σ₁^wX_ℓ+Σr_iY_i modq。公钥、Q输出及rank未额外条件化，全部P₂ rank在外层按原始U/F质量积分。关键位置：附录E.3–E.4，原残差与列包逐项可核。

令ψ为χ的特征函数，φ_B(s)=ψ(s)^w∏ψ(sr_i)，ν_d=Pr(X−X′=d)为完整49点差值律。Cauchy–Schwarz给

\[
E[|\Phi_V(t)|\mid B_{env}]\le
(E_T|\psi(tT)|^2)^{640},\quad
E_T|\psi(tT)|^2=\sum_{d=-24}^{24}\nu_d\varphi_B(td).
\]

全部频率按1、2–3、4–7、8–15、16–63、64–16384覆盖；负频率配对，Nyquist保守多计。B_FA新高频ρ=16156100186665515949/18446744073709551616；保留的低/中频项核对未回绕域，其余ν质量及高频r因子以单位包络计入。每指数Taylor倒数先向上取64位，再精确ν加权，对640次幂向上取80位。关键位置：附录E.4–E.6与全部有限证书。

\[
Z=\frac{4559006261671696450341}{1208925819614629174706176},\quad C_8=21845/16384,
\]
\[
U=(1-\delta)(4^{-8}+C_8Z)+\delta,
\qquad L=[(1-\delta)(1/4-Z)]^8.
\]

点态弦线x^8≤4^-8+C₈(x−1/4)_+给行上界，Jensen给行下界。K⊆J给完整消息上界；行下界留在J。完整消息非空性另取U₀=F₀=R=0见证。关键位置：附录E.7。

**初始与条件化。** A消去后的初始单坐标PGF为Aχ(z)Bχ(z)^1280，z=21/20精确Chernoff≤2^-138，64坐标并集逐A得a_I=2^-132。无条件联合分析完成后，以(L−a_I)/(1−a_I)和U/(1−a_I)给J的I条件界，K使用上界与事件包含。精确比较保持显示端点；I条件下列包可能相关。关键位置：附录E.8与逐A解除条件台账E.9。

**B_U的更紧依据。** 其H重量来自均匀A：u含奇数项时uA+f逐列均匀，9600位独立公平；附录D的好事件w≥4500、坏预算δ_B=2^-25及原高频常数给Z_* =27303052442598203493/2417851639229258349412352。其余真实环境、弦线、Jensen及条件化分别在附录D完整展开。更紧数字继续携带均匀Setup量词。

## 5. 公开seed推论与迁移表更新

若公共变量Z_pub先确定A=g(Z_pub)，且每个相关z下后续原始χ、同A两代、TG/Upd、Ord及Decode满足B_FA合同，则逐seed应用固定A定理并平均，得到同一行区间、完整错误下界和初始界；I条件下也保持显示端点。公开A生成器的均匀性、伪随机性、像熵及全矩阵统计距离责任对新界已经解除。秘密噪声seed联合律、输出筛选/重试、公式与机器语义继续核准。

引用B_U更紧数字时，仍须提供均匀Setup或能支撑其环境/事件的有效对应依据。具体统计或计算迁移若给更新正确事件损失η_K与初始失败额外损失η_I，则正分母下Pr_code(K|I)≤(U+η_K)/(1−2^-132−η_I)；保留同一显示端点需要有限损失比较。详见v2.2 §7.5。

## 6. 作者程序、原声明、来源与优先权状态

作者程序状态为**WAITING_FOR_AUTHOR_ARTIFACT**。六组报告配置640/976/1344×AES/SHAKE整体静态映射均UNRESOLVED，已取得带原消息和初始/更新后消息比对的作者UE轨迹数为0。论文报告KG、Enc、Dec、TG、Upd五操作的100次计时；性能对象的源代码、配置、随机性与正确性分母需专门对应。官方上游KEM文件承担基础参照作用，UE实现归属由论文、作者或机构的关联证据认证。

最小外部材料为：认证的不可变UE源包/commit和640配置/依赖；同A两代、逐公共seed的秘密流规格及算法/筛选/Ord/算术对应；一条诚实未筛选Enc→TG→Upd→Dec的消息比对轨迹。对应完整性能表另需六配置与原100次日志。路径事实与概率模型分别核准。

Theorem6.3在固定640的打印充分前提未满足，B_U/B_FA刻画其前提之外的有限一步行为。Theorem6.9沿用精确LWE前提审计：CF-1的丰富独立同秘密样本前件失效，固定n/3n样本与FI完整归约继续待核。Nishimaki2024扩展版Lemma5.7/构造邻文、CJL原PDF/逐版本对应保持各自来源缺项。

应用优先权沿用2026-11-10封存范围：相同FI对象的完整等价A/B命题直接先例在实际检索内尚未定位，全球优先权待核。KLR2019公开token一致性为A的最强已核方法近邻，官方Frodo基础PKE有限失败分析为B的成熟方法来源。本版固定A扩展检索新增0。贡献增加公开矩阵量词扩展及迁移前提缩减，经典概率/Fourier工具按原归属引用。

INC976已在v2.1闭合：χ976的正确分子为[11278,10277,7774,4882,2545,1101,396,118,29,6,1]/65536。v2.1完整重放1281系数及ε₉₇₆≤2^-1118，三表与CDF/证书输入逐点相同。本版继承这些历史记录；A、B_U、B_FA的数学依赖均为χ640，各自无χ976传递依赖。

## 7. 实际AI审阅身份

| 记录 | 实际曝光/身份 | 范围 |
|---|---|---|
| ROUND-005 | 同一AI两阶段：phase1未见作者推导，phase2读稿比对 | 旧攻击、CF-1与有限表按封存范围 |
| 精确LWE复核 | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 丰富/固定样本及环上线性化，修订按v2.1继承 |
| 640首轮概率复核 | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 原记录375项含100文件指纹 |
| 640补充概率复核 | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 原记录303项；均匀Setup完整链 |
| 固定A定向复核 | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 作者证明、目标及旧正面结论可见；FA1—FA5、初始/条件化/公开seed，原记录385项通过 |
| 当前v2.2作者修订 | INFORMED_AUTHOR_REVISION_AND_PROOF_INTEGRATION | 同一固定A证书链重放385项；H尾直接断言73；新增独立审阅0 |

固定A复核会话01a1c652-ba78-71a0-b293-a09d61f26039，声明家族Codex基于GPT-6；精确后端ID与权重为null。各审阅模型错误过程独立性未认证；现有身份记录给出的人工、跨模型、盲审及证明助手新增认证均为0。当前作者整合亦采用这些实际证据边界。检查数量记录执行范围，数学充分性仍由证明链承担。

## 8. 三个最有决定性的人工问题

| 问题 | 最小输入 | 需要判断的明确命题 |
|---|---|---|
| H1：原游戏与共同正确族是否准确匹配？ | 目标PDF9–15；v2.2 §§2–6；χ640卷积证书 | Ord_n类型补齐和权限是否准确；四查询/空Key终局、保留F₁的逐P₂界及P₂-only停止是否推出≤3n+1与Δ→1；同一CF-1合同是否保证最长n次逐样本正确。请指出具体失效游戏行或条件样本，或给可接受范围 |
| H2：逐A扩展是否在每次解除条件时保留量词？ | 目标PDF12–15、官方10/25；v2.2 §7.3及附录E；新FINITE_CERTIFICATES与385项结果 | 对每个预固定A，χ平移PGF/H73、R₂27、两层真实系数律、w+R₂≥3950、新ρ/全频率、八阶弦线/Jensen和I事件比率，是否完整推出完整错误≥99.4956640%及行区间；逐seed合同是否足以解除公共A分布责任。请核查E.1、E.3、E.5–E.9或给具体反例 |
| H3：条件安全声明对应哪个精确困难前件？ | 目标PDF19–20；v2.2 §§8–9与附录A；另需2024版Nishimaki Lemma5.7及构造/参数邻文 | 能否恢复(n,m,q,χ、秘密先验、辅助视图、时间、PPT/QPT)归约，判定其与CF-1成员资格、丰富样本前件失效及固定n/3n边界的关系；何种已认证非空困难前提可支持评价原条件定理 |

H3缺失前驱全文可由附版本、日期与哈希的合法PDF补齐。H1/H2已有完整纸面证明和有限数据入口；人工作出的判断及作者程序对应可分别回写后续版本。

## 9. 直接阅读与重放入口

| 材料 | 入口/用途 |
|---|---|
| v2.2完整研究稿 | [CRYPTOANALYSIS_DRAFT.md](CRYPTOANALYSIS_DRAFT.md)：A §§2–6；B_U §7.2/附录D；B_FA §7.3/附录E；迁移§7.5 |
| v2.2机器主张 | [CLAIM_EVIDENCE_MATRIX.json](../../frozen/crypto_fi_research_manuscript_v2_2/CLAIM_EVIDENCE_MATRIX.json)：C29–C38新增，精确模型/结果/依赖 |
| 修正闭合 | [REVISION_AND_READINESS.md](REVISION_AND_READINESS.md)与[MANIFEST.json](../../frozen/crypto_fi_research_manuscript_v2_2/MANIFEST.json) |
| 目标PDF/源TeX | [FI期刊PDF](../../frozen/crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf)、[articlev08.tex](../../frozen/crypto_fi_research_manuscript_v1/sources/articlev08.tex) |
| 官方规范 | [2021](../../frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf)、[2023](../../frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf) |
| 固定A精确证书 | [FINITE_CERTIFICATES.json](../../frozen/crypto_fi_research_manuscript_v2_2/FINITE_CERTIFICATES.json)：χ/ν、尾界、全频率、Z/U/L及条件化分数 |
| 当前385项结果 | [RECOMPUTED_CERTIFICATES.json](../../frozen/crypto_fi_research_manuscript_v2_2/evidence/RECOMPUTED_CERTIFICATES.json)、[执行指纹](../../frozen/crypto_fi_research_manuscript_v2_2/evidence/REPLAY_EXECUTION.json) |
| 当前标量脚本 | [compute_fixed_A.py](../../frozen/crypto_fi_research_manuscript_v2_2/certificates/compute_fixed_A.py)、[recompute_certificates.py](../../frozen/crypto_fi_research_manuscript_v2_2/certificates/recompute_certificates.py)：在v2.2按此顺序运行，只计算有限标量 |
| 固定A作者与定向审阅 | [原证明](../crypto_fi_640_fixed_A_correctness/PROOF_OR_OBSTRUCTION.md)、[MATHEMATICAL_REVIEW.md](../crypto_fi_640_fixed_A_review/MATHEMATICAL_REVIEW.md)、[REVIEW_VERDICT.json](../../frozen/crypto_fi_640_fixed_A_review/REVIEW_VERDICT.json) |
| B_U原单坐标/联合证书 | [SCALAR_CERTIFICATES.json](../../frozen/crypto_fi_640_correctness_audit/evidence/SCALAR_CERTIFICATES.json)、[JOINT_SCALAR_CERTIFICATES.json](../../frozen/crypto_fi_640_joint_correctness/evidence/JOINT_SCALAR_CERTIFICATES.json) |
| B_U补充审阅/303项 | [MATHEMATICAL_REVIEW.md](../crypto_fi_640_probability_review/review_01a1c4ed/MATHEMATICAL_REVIEW.md)、[RECOMPUTED_PROBABILITY_CHAIN.json](../../frozen/crypto_fi_640_probability_review/review_01a1c4ed/evidence/RECOMPUTED_PROBABILITY_CHAIN.json) |
| A卷积与LWE审阅 | [χ640完整64重系数](../../frozen/crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json)、[LWE定向审阅](../crypto_fi_lwe_independent_review/MATHEMATICAL_REVIEW.md) |
| 作者工件审计与最小轨迹规格 | [VERDICT.json](../../frozen/crypto_fi_author_implementation_audit/VERDICT.json)、[MINIMAL_REPRODUCTION_SPEC.md](../crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md)：历史迁移表的公共A责任按本版§7.5更新 |
| INC976历史闭合 | [ERRATUM_AND_CERTIFICATE_AUDIT.md](../crypto_fi_research_manuscript_v2_1/ERRATUM_AND_CERTIFICATE_AUDIT.md)、[REPLAY_976.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/REPLAY_976.json) |
| 应用优先权/发表影响 | [APPLICATION_PRIORITY_AND_IMPACT.md](../crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md)：沿用实际检索范围与重开条件 |

阅读顺序：原算法/游戏→本入口§2精确命题→相应完整证明→有限证书→模型迁移与外部问题。文件版本、实际来源与输入结果指纹由本版MANIFEST及evidence固定，历史文件保持只读。
