# 三个人工密码学审阅问题

统一原稿：[v3阅读副本](reading/crypto_fi_research_manuscript_v3/CRYPTOANALYSIS_DRAFT.md)。全部页码采用物理PDF页。请在 [REVIEW_FORM.md](REVIEW_FORM.md) 分别判断，各问允许“部分范围通过”“需修正”“证据待补”。

## H1 原游戏攻击与共同正确性

**问题：原游戏权限、Ord类型规范化、固定P₂条件化、P₂-only停止和CF-1共同正确性，是否足以支持所列攻击结论？**

最小阅读：

- [FI PDF](frozen/crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf) 页9–11（Corr/Next/Chall/终局）、12–15（算法/类型/正确性），[原TeX](frozen/crypto_fi_research_manuscript_v1/sources/articlev08.tex) 的游戏及Construction of EU scheme。
- v3 §§2.1–2.3、3.1–3.2、4.1–4.2、5、6.1–6.3；重点式(6)–(12)、(13)–(19)、(16a)及定理1–4。
- [官方2021规范](frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf) 页10、15–16、25；[χ640卷积](frozen/crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json) 与 [源事件参数证书](frozen/crypto_fi_research_manuscript_v1/sources/PARAMETER_CERTIFICATES.json)。标量重放为REPLAY的A_all_convolutions及A_EXTRA_CHECKS。

需要判断：四查询的父/消息资格、空Key终局及Δ定义；Ord_n补齐是否保持目标对象；固定A/P₂/父/U₁/fresh y后F₁独立列律是否成立；逐P₂界β≤α_invε_n；停止只看P₂且每轮诚实父时的虚拟补全/积分；同一CF-1族所有支持样本下B₀+nW<q/8；采样、通信、求逆和所有轮换计费后仍为PPT，≤3n+1且Δ→1。请标明接受的模型/版本，给出失效的游戏行、条件变量或参数反例。

可选溯源：[ROUND-005定理](reading/crypto_branch_monitor/round_005/THEOREM_FOR_CITATION.md)、[phase1推导](reading/crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/PHASE1_DERIVATION.md)。它们保留其历史身份及范围。

## H2 三参数可靠性

**问题：条件列包、真实2n系数律、参数化判据、全平移PGF、全部频率、有向算术和初始正确条件化，是否严格支持三组可靠性数字？**

最小阅读：

- FI PDF12–15；官方2021 PDF10、15–16、25；[2023规范](frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf) 物理15–16／印刷11–12；[官方1344勘误回执](frozen/crypto_fi_official_profile_review/evidence/OFFICIAL_1344_ERRATUM_LIVE_RECEIPT.json)。
- v3 §7.2判据P、§7.3 OFFICIAL-1；F.1–F.6，式(F1)–(F20)，尤其(F4)条件行矩、(F5)真实系数律、(F7)–(F8)绝对矩、(F10)–(F13)判据、(F17)–(F20)事件比率/初始PGF。
- 640：D.1–D.5及E.1–E.8；重点D-J1–D-J6、D-IC、E-C1/E-C2/E-F2/E-F3/E-U/E-IC；采用旧较弱Jensen下界时核其具体对象。
- 976/1344：F.7–F.11，式(F21)–(F32)；G.1–G.4；[统一选择器](frozen/crypto_fi_research_manuscript_v3/certificates/UNIFIED_RESULT_SELECTORS.json)、[官方参数完整证书](frozen/crypto_fi_research_manuscript_v3/certificates/OFFICIAL_PROFILE_CERTIFICATES.json)、[976代表](frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_FULL_COVERAGE_976.json)、[976映射](frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_SHIFT_TO_REP_976.u16le)、[1344代表](frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_FULL_COVERAGE_1344.json)、[1344映射](frozen/crypto_fi_research_manuscript_v3/certificates/review/evidence/PGF_SHIFT_TO_REP_1344.u16le)。重放全部组见 [REPLAY](REPLAY.md)。

需要判断：原始币两层σ代数与剩余列包iid；2n系数相同加权和律及全部P₂秩的自然积分；有限和C_k的端点、弦线/Jensen及坏环境混合；每个A下χ平移PGF的乘积化；65536平移到1484/1000代表、最大平移4/2及含边界尾；1344真实奇偶偏差、模子群/Nyquist、全部频率和全部差值质量；64位→精确ν→80位有向链；初始AχBχ^(2n)、64并集、K⊆J与最后的I条件比率。请分别判断三尺寸×两种A量词的六个端点，并核初始失败2^-132/193/246。有限计算通过与条件证明成立各写其判断。

最小审阅溯源：[E16复核](reading/crypto_fi_official_profile_review/MATHEMATICAL_REVIEW.md) §§2–11及 [C1–C6修正](reading/crypto_fi_official_profile_review/CORRECTIONS_AND_MANUSCRIPT_IMPACT.md)；v3修订报告§2记录采用位置。

## H3 条件安全、软件与贡献

**问题：对FI条件安全定理、性能配置及实际软件，当前贡献措辞和适用范围是否准确？该成果作为独立短文或毕业论文核心章节的价值如何评价？**

最小阅读：

- FI PDF15的Theorem6.3、19–20的Lemma6.8/Theorem6.9、20–22实现/性能段。
- v3 §§7.4–7.5、8.1–9.2、10.3–10.4，附录A.1–A.6；式(16a)、(MT)，并与H1/H2的已接受范围对应。
- [精确LWE复核](reading/crypto_fi_lwe_independent_review/MATHEMATICAL_REVIEW.md) 与 [其修正及主张影响](reading/crypto_fi_lwe_independent_review/CORRECTIONS_AND_CLAIM_IMPACT.md)；[作者软件映射](reading/crypto_fi_author_implementation_audit/IMPLEMENTATION_MODEL_MAPPING.md)、[VERDICT](frozen/crypto_fi_author_implementation_audit/VERDICT.json)、[最小工件规格](reading/crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md)；[发表影响审计](reading/crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md)。
- 方法归属和先例对照：[KLR2019](frozen/crypto_fi_research_manuscript_v1/sources/KLR2019.pdf) AppB.2／物理44；[AG2011作者稿](frozen/crypto_fi_research_manuscript_v1/sources/AG2011_author.pdf) 及 [CJL指定索引节选](frozen/crypto_fi_research_manuscript_v1/sources/CJL2025_scoped_indexed_excerpts.txt)。来源缺项影响见 [SOURCE_GUIDE](SOURCE_GUIDE.md)。

需要判断：CF-1丰富同秘密样本前件的结论与固定n/3n样本、秘密先验、辅助视图、时间预算、FI完整归约之间的关系；Theorem6.3前件与一次更新概率结果的关系；六配置及原100次计时能支持的事实；真实软件承接固定A或均匀Setup端点所需最小合同/有限损失；既有通用工具、对象应用增量、全平移PGF加固及全球优先权措辞。请给出独立短文和毕业论文核心章节的分别评价、最小补充材料及理由。CJL原PDF、Nishimaki2024扩展版和认证UE工件到位后，对应判断可重开。
