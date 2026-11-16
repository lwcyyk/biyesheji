> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_research_manuscript_v3/HUMAN_REVIEW_ENTRY.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 人工密码学审阅入口：Frodo-FI研究稿v3

2026-11-11，Asia/Shanghai。本入口供人工独立检查两条主线：A，共同正确CF-1族的原游戏来源隐藏攻击；B，三组官方参数在明确理想合同下的一次更新高错误率。完整证明位于本版正文及附录A—G，有限证书、全部平移覆盖及实际审阅身份可由末表直接进入。

## 1. 目标版本、规范与类型合同

目标为Mariusz Jurkiewicz、Kamila Prabucka，*Unidirectional Key Update in Updatable Encryption, Revisited*，DOI10.46298/fi.14425；期刊冻结PDF与arXiv:2410.03948v4相同，23页，SHA256：

`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。

源TeX articlev08.tex SHA256为`16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b`。PDF9—11为游戏，12为Setup/Enc/Dec，13为Ord/Tensor，14为TG/Upd，15为正确性，19—20为Lemma6.8/Theorem6.9，20—22为实现/性能。官方2021规范PDF10、15—16、25支持半向上舍入、严格阈值采样与质量参数；2023物理PDF15—16/印刷11—12为A.3/A.4，1344结合官方issue35的2024-11-27勘误。

Ord按父C₁的实际n列作D位0/1位平面展开，与Tensor_D(S)=[S;2S;…;2^(D−1)S]配对，满足H·Tensor_D(S)=C₁S modq。源Ord域的n̄与Upd的n列类型差异透明携带。S、E按KeyGen和矩阵乘积取n×n̄；源证明一处E写n×n的记号依此对应。匹配固定行置换保持gadget与iid行律。

## 2. 精确主张A与最短轨迹

λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，χ=精确χ640，T=t_max=n。A在全部相关χ币之前任意固定，给定A后原始χ坐标和调用精确独立；采用§1的Ord规范化。初始及最长n次诚实更新对所有合法消息和支持内样本逐样本正确。原rand-ind-eu-cpa游戏存在PPT来源区分器，≤3n+1次调用取得Δ→1。

最短轨迹在epoch0、phase0固定消息M：Enc₀(M)取得完整父C；Next至1；Corr(token,1)取得四块；Challenge₁(M,C)取得fresh或update，立即输出。Key腐化、Dec、普通Upd请求和挑战后Next均为0。空Key泄露使K*=∅，终局K*∩C*=∅，同消息及登记父满足挑战资格。

取父第一行h=Ord_n(c)、挑战第一行y。P₂可逆时，r̂=(y−hP₁)P₂^-1；r̂∈Sχ^n则猜update，奇异时公平猜测。真实update精确恢复r。真实fresh保留共享A和真实token分布，固定A/P₂/父/U₁/fresh y时F₁仍有独立列卷积律，给β≤α_inv ε_n，其中α_inv=Pr(P₂可逆)。n≥64时

\[
\epsilon_n=\min\{1,\binom n{63}a_0^{n-63}+(25\mu_{64})^n\},\quad a_0=1161/8192.
\]

n<64取ε_n=1。χ640奇偶各半使α_inv=∏_(i=1)^n(1−2^-i)>1/4。首个可逆边界停止只读取P₂，真实轮换付费并逐轮生成诚实父；条件于P₂序列后父/F₁抽样律保留。n轮的gap≥1−(3/4)^n−ε_n。25μ₆₄<1/2由完整卷积认证。共同正确性由B₀+nW<q/8承担，B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²，s=12。打印域成员、官方D≤16接口及LWE前件分别评价。最关键证明在正文§§3—6。

## 3. 精确主张B：三组参数与两种A量词

共同合同：两代共用A；A、合法消息及指定行/坐标在全部相关原始χ之前固定；给定A后两代KeyGen及Enc/TG/Upd所有原始χ坐标和调用精确独立；一次诚实未筛选TG/Upd，全部P₂秩自然计入；采用§1的Ord及官方最近整数平局向上Decode。m̄=n̄=k=8，概率平均这些诚实币。

| 配置 | n,D,q,B／消息位数 | 初始完整失败：逐A | 更新完整正确：逐固定A、不平均A | 更新完整错误：逐固定A | 更新完整正确：均匀Setup、平均A | 更新完整错误：均匀Setup |
|---|---|---:|---:|---:|---:|---:|
| 640 | 640,15,32768,2／128 | ≤2^-132 | ≤0.005043360 | ≥99.4956640% | ≤0.000030345 | ≥99.9969655% |
| 976 | 976,16,65536,3／192 | ≤2^-193 | ≤0.078020625 | ≥92.1979375% | ≤0.017137631 | ≥98.2862369% |
| 1344 | 1344,16,65536,4／256 | ≤2^-246 | ≤0.206115312 | ≥79.3884688% | ≤0.082813443 | ≥91.7186557% |

均匀Setup两列额外要求A独立均匀于整个n×n环矩阵空间。所有显示更新端点额外条件于相应初始完整消息已正确时保持。六个精确原/条件分数见附录G.1及统一选择器；指定行与坐标显示区间在正文§7.3完整列示。行下界只属于行，完整上界使用K⊆J。

三组精确质量共同分母65536，按0及每个±j列分子：

| χ | 整数支持 | 质量分子 | 偶/奇分子 |
|---|---|---|---|
| 640 | [−12,12] | 9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1 | 32768/32768 |
| 976 | [−10,10] | 11278,10277,7774,4882,2545,1101,396,118,29,6,1 | 32768/32768 |
| 1344 | [−6,6] | 18286,14320,6876,2023,364,40,2 | 32770/32766 |

0计一次、非零正负各一次。976采用INC976已更正质量；1344采用完整CDF含32765、32767，θ=ψ(q/2)=1/16384。实际seed流是否生成所需精确联合律需专门对应。

## 4. 参数化概率链与最关键核验节点

两代B_x=AS_x+E_x；父C₁=U₀A+F₀、C₂=U₀B_old+G₀+Encode(M)。TG四块与Upd给C′₁=HP₁+RP₂、C′₂=C₂+HQ₁+RQ₂。消去A及gadget，真实残差为

\[
N=U_0E_{old}-F_0S_{old}+G_0
+(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2\pmod q.
\]

它包含初始与全部更新噪声并保留回绕。正确残差集合为640/976的{−4096,…,4095}、1344的{−2048,…,2047}，标签平移后相同，π₀=|𝓓|/q分别1/4、1/8、1/16。

**条件结构。** 𝓑=σ(A,U₀,F₀,R)，V=σ(𝓑,U₁,F₁,U₂,F₂)。V固定后，钥匙/G的k个剩余列包iid，p_row=E[p(V)^k]。在𝓑层，a=hU₁+rU₂、b=hF₁+rF₂共2n个系数独立同律于T_𝓑=Σ₁^wX_ℓ+Σr_iY_i modq。令ψ为χ字符函数，φ_𝓑(s)=ψ(s)^w∏ψ(sr_i)，ν_d=Pr(X−X′=d)。则

\[
E[|\Phi_V(t)|\mid\mathcal B]\le(E_T|\psi(tT)|^2)^n,
\quad E_T|\psi(tT)|^2=\sum_d\nu_d\varphi_{\mathcal B}(td).
\]

公钥/token输出与rank均未额外筛选条件化，全部原始U/F在外层自然积分。关键位置：附录F.1—F.3；640特化在D.3/E.3—E.4。

**好事件和Z。** 对好环境𝓖∈𝓑，Pr(𝓖^c)≤δ，每个好𝓑内E|p(V)−π₀|≤Z。C_k首先用有限和Σ₀^(k−1)π₀^j定义，F=π₀^k+C_kZ。点态弦线、p^k≤p≤1与坏环境混合给

\[
U_J=(1-\delta)\min\{1,F,\pi_0+Z\}+\delta.
\]

Jensen给L_J=(1−δ)(π₀−Z)₊^k；指定坐标区间[(1−δ)(π₀−Z)₊,(1−δ)min{1,π₀+Z}+δ]。π₀=0/1、k=1、δ=1、Z≥π₀、F≥1及B=0/D等端点在§7.2/F.4/F.12列全；F−1=C_k[Z−(1−π₀)]给F≥1时U_J=1。当前640采用已封存的较弱全局Jensen下端，均在一般判据允许范围内。

**全平移PGF。** 先固定A,u，父坐标为确定平移加独立χ。令g_H(z)=max_a Eχ[z^wt_D(a+X modq)]，则E[z^w|A,u]≤g_H(z)^n，Markov后对u积分给逐A下尾。976/1344各枚举65536平移，以17维重量质量向量去重；1484/1000个代表均用整数共同分子比较，唯一最大平移4/2。H阈值1477/1644的含等号尾≤2^-40，覆盖严格坏尾。R₂阈值3669/2030尾≤2^-40，故δ_FA=2^-39。

完整映射按平移a的偏移2a存little-endian uint16代表ID，各131072字节；代表JSON记录全部向量、频数、精确PGF共同分子及非负最大差。关键位置：F.8/G.2。枚举成本包含q=2^D，关于D指数增长；具体D=16证书成本与参数化数学判据分别陈述。

**全部频率。** 低频使用精确矩与ψ正性，域半径512、1024、2048、4096；976采用K_j=105,104,100,83，1344为40,40,39,37。高频保留d=±1及0/±1原子，覆盖模子群/Nyquist，包括1344真实偏差。全部差值质量保留，未改善项按1；24/59个实际组各覆盖32768个正代表，负频率配对、Nyquist保守多计。每指数64位上包、精确ν加权、n次幂80位上包，松弛全部进入Z。关键位置：F.9—F.10及逐组JSON。

均匀Setup改用u含奇数时的nD公平位，H7339/10205，δ_U=2^-38；单位坏质量分别2^-976和(16385/32768)^1344≤2^-1343。固定A两组Z约0.06826799845、0.19323310441，均匀Setup约0.01499537554、0.07763760183。640使用其自身H/δ/Z，完整列于§7.3和D/E。

**初始与条件化。** A消去后，初始单坐标PGF为Aχ(z)Bχ(z)^(2n)。tilt21/20、107/100、59/50给坐标失败2^-138、2^-199、2^-252；64并集给α。先完成原实验，再用[max{0,(L−α)/(1−α)},min{1,U/(1−α)}]条件化；K取行上界。各组精确比较确认显示裕量。完整下界另由全部行U₀=F₀=R=0见证γ=a₀^(24n)同时保证I∩K。关键位置：F.5—F.6、G.1；640 D.5/E.8。

## 5. 原声明、实际软件和公开seed的范围

三组Theorem6.3打印前件的左端22649448960、32387837760、13265908992，右端4096/T、4096/T、2048/T，整数T≥1均未满足。当前定理评价这些固定配置在前件之外的一步行为。完整充分式B₀+t_maxW<h_dec包含初始项，T按单链最大更新次数对应，当前可靠性t_max=1。

Theorem6.9沿用精确LWE审计：CF-1丰富独立同秘密样本困难前件失效；固定n/3n样本、FI完整归约与实际辅助视图继续待核。Nishimaki2024扩展版Lemma5.7/构造邻文、CJL原PDF及逐版本对应有各自来源缺项。三个有限可靠性界无需LWE困难性前提。

若公共Z_pub先确定A=g(Z_pub)，每个相关z下后续χ与算法仍满足相应冻结合同，固定A三组界可逐seed平均；条件于I也保持显示端点。公开A均匀性/伪随机性/像熵和全矩阵距离责任对这些固定A数字已经解除。更紧均匀Setup数字仍携带其分布依据。

作者软件保持**WAITING_FOR_AUTHOR_ARTIFACT**，六配置整体映射均UNRESOLVED。数学三尺寸已覆盖；作者UE源文件、配置、秘密噪声seed联合律、公式、筛选重试、Ord与机器算术需工件或有效有限损失迁移。已取得消息比对作者UE轨迹数0。官方基础KEM源码各按自身作用登记。

若软件更新正确事件偏差≤η_K、初始失败额外损失≤η_I，正分母时可用min{1,U_n+η_K}及min{1,(U_n+η_K)/(1−α_n−η_I)}。具体显示端点须代入有限损失。单条消息轨迹认证路径，概率合同另核。最小软件材料为认证UE版本/配置/依赖、随机性与算法/算术规格，以及一条未筛选的原消息和两次解密比对轨迹；性能表对应另需六配置与原100次五操作日志。

应用优先权沿用2026-11-10有界审计及E15在2026-11-11登记的六条查询范围，v3新增检索0。KLR2019与官方基础PKE失败分析承担成熟方法近邻；参数化判据为640直接抽象，完整平移PGF和两组实例属具体应用增量。全球优先权继续待核。

## 6. 现有AI复核身份与本版执行

| 记录 | 实际身份/曝光 | 计算范围 |
|---|---|---|
| ROUND-005 | 一名AI两阶段，第一阶段未见作者推导，第二阶段读稿比对 | 旧攻击、CF-1及有限表按封存范围 |
| 精确LWE复核 | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 丰富/固定样本及环上线性化，按v2.2继承 |
| 640首轮/补充轮 | 分别AUTHOR_PROOF_VISIBLE…与AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE… | 原375项含100文件指纹；补充303项 |
| 640固定A复核/v2.2 | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW；随后知情作者整合 | 原385项及v2.2副本385项分别引用，H73加固 |
| 最新976/1344复核E16 | **AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW**，作者/目标/旧正面审阅可见 | 9196项具名算术重建、3194项作者副本核对、全平移与来源事件复算 |
| 当前v3整合E17 | INFORMED_AUTHOR_REVISION_PARAMETRIC_PROOF_INTEGRATION_AND_STAGE_HANDOFF | 相同脚本副本9196/3194项重放通过，作者证书字节匹配；两组卷积另重放 |

E16 chat_id为01a1c8ef-6688-7b71-9943-f98a9c3ff068。声明家族Codex基于GPT-6，精确后端ID、权重及作者/旧审阅后端对应为null。代码路径算术重建与模型错误过程独立性分别登记；E16和本版新增人工、跨模型、盲审、子代理、证明助手及独立模型错误过程认证均为0，校准NOT_CALIBRATED。不同会话与检查数量各承担其实际证据含义。

## 7. 三个人工判断问题

| 问题 | 最小输入 | 请判断的明确命题及影响 |
|---|---|---|
| H1：原游戏与共同正确族是否相配？ | 目标PDF9—15；v3 §§2—6；χ640完整64重证书 | Ord_n类型补齐、四查询/空Key终局、逐P₂保留F₁及P₂-only停止是否完整支持≤3n+1与Δ→1，且同一CF-1合同逐样本正确。请给接受范围或具体游戏行/条件反例 |
| H2：参数化链与三组有限证书是否完整？ | v3 §7、附录D—G；三组证书/统一选择器；976/1344全部平移映射与代表比较；原算法PDF12—15 | p_row混合、2n真实系数、一般端点、全平移最大化、坏环境、全频率/有向链、K⊆J及I比率能否推出全部六个完整显示上界。请优先核F.3—F.6、F.8—F.11、G.1—G.3，指出具体失效式或可接受范围 |
| H3：原条件安全与实际软件影响应如何表述？ | 目标PDF19—22；v3 §§8—10与附录A、§7.5；作者实现取证；待补Nishimaki2024邻文或认证UE工件 | 精确(n,m,q,χ、秘密先验、辅助视图、时间/对手类别)归约与CF-1前件范围是否准确；实际代码若满足哪些最小合同可承接三尺寸结论；当前贡献是否足以作为独立短文/论文核心章节 |

H1/H2已有完整纸面与有限证据可先审。H3的程序与前驱部分在对应工件到位后重开。继续收紧数值、更多更新深度及精确64坐标概率分别提升精度或扩展范围，当前三尺寸一次更新判定已完成。下一项最能改变现实适用性的材料为认证作者UE工件及带消息比对的未筛选轨迹。

## 8. 直接阅读和证书入口

| 材料 | 入口及用途 |
|---|---|
| 完整v3 | [CRYPTOANALYSIS_DRAFT.md](CRYPTOANALYSIS_DRAFT.md)：A §§2—6；B §7、D—G；条件安全§§8—9/A；阶段交接§10.4 |
| 主张与修订 | [CLAIM_EVIDENCE_MATRIX.json](../../frozen/crypto_fi_research_manuscript_v3/CLAIM_EVIDENCE_MATRIX.json)、[REVISION_AND_READINESS.md](REVISION_AND_READINESS.md)、[MANIFEST.json](../../frozen/crypto_fi_research_manuscript_v3/MANIFEST.json) |
| 原论文/源TeX | [FI期刊PDF](../../frozen/crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf)、[articlev08.tex](../../frozen/crypto_fi_research_manuscript_v1/sources/articlev08.tex) |
| 官方规范 | [2021](../../frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf)、[2023](../../frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf) |
| 统一模型与精确分数 | [UNIFIED_RESULT_SELECTORS.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/UNIFIED_RESULT_SELECTORS.json)：profiles.n.fixed_A/uniform_Setup及conditioned_on_initial |
| 976/1344完整证书 | [OFFICIAL_PROFILE_CERTIFICATES.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/OFFICIAL_PROFILE_CERTIFICATES.json)：分布、全部差值、PGF、频率与端点 |
| 640固定A/均匀来源 | [640_FIXED_A_CERTIFICATES.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/640_FIXED_A_CERTIFICATES.json)、[640_UNIFORM_RESULTS.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/640_UNIFORM_RESULTS.json) |
| 976完整平移覆盖 | [PGF_FULL_COVERAGE_976.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_FULL_COVERAGE_976.json)、[65536项映射](../../frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_SHIFT_TO_REP_976.u16le) |
| 1344完整平移覆盖 | [PGF_FULL_COVERAGE_1344.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_FULL_COVERAGE_1344.json)、[65536项映射](../../frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_SHIFT_TO_REP_1344.u16le) |
| 当前9196项与执行指纹 | [INDEPENDENT_RECOMPUTATION.json](../../frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/INDEPENDENT_RECOMPUTATION.json)、[REPLAY_EXECUTION.json](../../frozen/crypto_fi_research_manuscript_v3/evidence/REPLAY_EXECUTION.json) |
| 最新复核及身份 | [MATHEMATICAL_REVIEW.md](../crypto_fi_official_profile_review/MATHEMATICAL_REVIEW.md)、[INPUT_AND_REVIEW_PROVENANCE.json](../../frozen/crypto_fi_official_profile_review/INPUT_AND_REVIEW_PROVENANCE.json) |
| A卷积与LWE原审阅 | [χ640完整系数](../../frozen/crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json)、[LWE定向审阅](../crypto_fi_lwe_independent_review/MATHEMATICAL_REVIEW.md) |
| 软件取证/最小轨迹规格 | [作者工件VERDICT](../../frozen/crypto_fi_author_implementation_audit/VERDICT.json)、[MINIMAL_REPRODUCTION_SPEC.md](../crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md)：数学覆盖更新按v3 §7.5 |
| 应用影响与976勘误 | [发表影响审计](../crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md)、[INC976闭合](../crypto_fi_research_manuscript_v2_1/ERRATUM_AND_CERTIFICATE_AUDIT.md) |

建议顺序为原算法/游戏→精确命题→对应完整证明→有限证书→迁移与外部问题。当前材料足以启动人工密码学复核，来源、实际计算和历史字节身份由MANIFEST及evidence固定。
