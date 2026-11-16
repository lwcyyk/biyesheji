from pathlib import Path
import shutil,json,hashlib
B=Path(r'D:\毕业设计');O=B/'crypto_fi_external_review_package';W=Path(__file__).resolve().parent
def write(rel,s):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf-8')
def dump(rel,x):write(rel,json.dumps(x,ensure_ascii=False,indent=2))
write('START_HERE.md',r'''
# Frodo-FI v3 人工密码学审阅包

2026-11-11，Asia/Shanghai。用途：在另一台机器离线阅读两项主结果、核对冻结原规范、重放必要的有限数学证书。当前交付身份为 **INFORMED_HANDOFF_ASSEMBLY_AND_DETERMINISTIC_SCALAR_REPLAY**。真实人工意见待填入 [REVIEW_FORM.md](REVIEW_FORM.md)。

## 1. 从这里开始

1. 阅读本页的命题、量词和三问。
2. 对照 [目标 FI PDF](frozen/crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf) 的物理 PDF 页9–15，按 [原规范定位表](SOURCE_GUIDE.md) 核游戏、Ord、TG/Upd、χ和舍入。
3. 阅读 [可移交 v3 研究稿](reading/crypto_fi_research_manuscript_v3/CRYPTOANALYSIS_DRAFT.md)：A 为§§2–6；B 为§7、附录D–G。章节与式号均沿用冻结原稿。
4. 依 [三个人工问题](HUMAN_QUESTIONS.md) 核证明；在 [审阅表](REVIEW_FORM.md) 写明所读范围与具体式号。
5. 按 [REPLAY.md](REPLAY.md) 运行公开入口。只需 Python 3.11+ 标准库；指定新的包外工作目录。包内含全部重放输入。

可进一步查看 [主张矩阵阅读副本](reading/crypto_fi_research_manuscript_v3/CLAIM_EVIDENCE_MATRIX.json)、[人工入口阅读副本](reading/crypto_fi_research_manuscript_v3/HUMAN_REVIEW_ENTRY.md)、[修订报告](reading/crypto_fi_research_manuscript_v3/REVISION_AND_READINESS.md) 及 [v3 原封存清单](frozen/crypto_fi_research_manuscript_v3/MANIFEST.json)。当前版本以 v3 主稿为准；历史 pending/REPAIR_REQUIRED 记录按其原阶段解释。

## 2. 目标及精确命题A

目标为 Jurkiewicz–Prabucka，*Unidirectional Key Update in Updatable Encryption, Revisited*，DOI [10.46298/fi.14425](https://doi.org/10.46298/fi.14425)，冻结 FI 期刊 PDF 与 arXiv:2410.03948v4 字节相同，23页，SHA-256：

`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`

**A：CF-1共同正确族的原游戏来源隐藏攻击。** 整数λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，χ为精确χ640，T=t_max=n。对每个在相关χ币之前固定的A，给定A后的原始χ坐标/调用精确独立，采用n列Ord与匹配Tensor_D。初始加密及最长n次诚实更新对所有合法消息和支持内样本逐样本正确；原rand-ind-eu-cpa游戏存在PPT区分器，调用≤3n+1，

Δ_n ≥ 1−(3/4)^n−ε_n → 1，

ε_n=min{1,binom(n,63)a₀^(n−63)+(25μ₆₄)^n}（n≥64），a₀=1161/8192，25μ₆₄<1/2；n<64取ε_n=1。逐样本正确性由B₀+nW<q/8承担，B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²，s=12。有限例n=128、D=56给ε≤2^-59，调用≤385。正文定理1–4、式(8)–(19)承担一般结论，有限证书承担具体算术。

### 最短四查询轨迹

epoch0、phase0预先固定M：① Enc₀(M)取得并登记完整父C；② Next进入epoch1；③ Corr(token,1)读取四块；④ Challenge₁(M,C)后立即输出。P₂可逆时以第一行h=Ord_n(C₁)、y构造r̂=(y−hP₁)P₂⁻¹，检查r̂∈Sχ^n；奇异时公平输出。Key腐化、Dec、普通Upd和挑战后Next计数均为0。空Key泄露给K*=∅，终局K*∩C*=∅。放大时每轮生成一份诚实父，仅按P₂首次可逆位置停止，并支付全部真实Next。

## 3. 精确命题B与三组可靠性结果

**B：三组参数在明确理想合同下的一次更新高错误率，分别采用逐固定A及均匀Setup两种量词。** m̄=n̄=8；A、消息及指定行/坐标先于全部相关原始χ币固定；两代共用A；给定A后两代KeyGen、Enc、TG、Upd的全部原始χ坐标与调用具有所列精确独立乘积律。采用n列Ord、匹配Tensor_D、打印公式、一次诚实未筛选TG/Upd，全部P₂秩自然计入。Decode(c)=floor(c2^B/q+1/2) mod2^B，平局向上。

| 参数 | (n,D,q,B)／消息位数 | 初始完整失败≤（逐A） | 更新完整正确≤：逐固定A | 更新完整错误≥：逐固定A | 更新完整正确≤：均匀Setup | 更新完整错误≥：均匀Setup |
|---|---|---|---|---|---|---|
| 640 | (640,15,32768,2)／128 | 2^-132 | 0.005043360 | 99.4956640% | 0.000030345 | 99.9969655% |
| 976 | (976,16,65536,3)／192 | 2^-193 | 0.078020625 | 92.1979375% | 0.017137631 | 98.2862369% |
| 1344 | (1344,16,65536,4)／256 | 2^-246 | 0.206115312 | 79.3884688% | 0.082813443 | 91.7186557% |

六个显示更新端点同时适用于原实验及额外条件于初始完整消息正确的实验。精确原/条件分数位于稿件G.1及 [统一选择器](frozen/crypto_fi_research_manuscript_v3/certificates/UNIFIED_RESULT_SELECTORS.json)。完整成功K采用指定行J的上界K⊆J；行下界保留其行事件对象。均匀Setup列额外要求A独立均匀于整个n×n矩阵空间，概率对A和诚实币共同平均；固定A列逐A成立，概率只平均后续诚实币。

## 4. 必须随结论携带的边界

- CF-1属于FI打印一般参数域，D随λ增长；官方D≤16接口的延展标签随族携带。
- 976使用已更正的χ976；1344结合官方issue35勘误，偶/奇质量为32770/32766，θ=1/16384。CDF严格比较、半向上舍入与模回绕均纳入合同。
- Ord按父C₁的实际n列展开，位平面顺序与Tensor_D配对，使H·Tensor_D(S)=C₁S modq；S/E均取n×n̄。源打印记号中的维度补齐由H1判断。
- B采用一次更新；token筛选、复用及更深链需各自分布证据。A的停止规则只看P₂。初始正确条件化在原实验联合分析之后用事件比率完成。
- 公共seed确定A后，固定A界可逐seed平均，前提是后续秘密流和算法仍符合冻结合同。秘密seed的完整联合律及机器算术映射需另核。
- 三组配置均处于源Theorem6.3的充分前件之外。Theorem6.9的精确LWE前件、固定n/3n样本和完整归约保留各自责任。

## 5. 核心证明顺序及证书

A：FI PDF9–15 → 稿§2类型合同 → §3式(6)支撑判定 → §4逐P₂真实fresh → §5 P₂-only停止 → §6共同正确性与放大 → 附录B χ640卷积。

B：FI PDF12–15及官方χ/Decode → 稿§7.2、F.1–F.6的残差/条件列包/2n系数律/判据/条件化 → 640附录D/E → 976/1344 F.7–F.11 → G.1精确端点、G.2全平移覆盖、G.3成本。优先核F4–F8、F10–F20、F22–F32。

有限入口：[证书与重放说明](REPLAY.md)。主证书为 [976/1344完整证书](frozen/crypto_fi_research_manuscript_v3/certificates/OFFICIAL_PROFILE_CERTIFICATES.json)、[640逐A](frozen/crypto_fi_research_manuscript_v3/certificates/640_FIXED_A_CERTIFICATES.json)、[640均匀](frozen/crypto_fi_research_manuscript_v3/certificates/640_UNIFORM_RESULTS.json)、[χ640全部1537系数](frozen/crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json)。全平移映射、全部代表及重放比较规则见REPLAY。

## 6. 三个人工问题

**H1**：原游戏权限、Ord类型规范化、固定P₂条件化、P₂-only停止和CF-1共同正确性，是否足以支持所列攻击结论？

**H2**：条件列包、真实2n系数律、参数化判据、全平移PGF、全部频率、有向算术和初始正确条件化，是否严格支持三组可靠性数字？

**H3**：对FI条件安全定理、性能配置及实际软件，当前贡献措辞和适用范围是否准确？该成果作为独立短文或毕业论文核心章节的价值如何评价？

每问的最小阅读材料、准确章节/式号及待判断命题见 [HUMAN_QUESTIONS.md](HUMAN_QUESTIONS.md)。审阅结论由真实审阅者填写；当前表格保持空白。

## 7. 实际AI审阅身份、来源缺项及作者软件

最新E16为 **AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW**，作者证明、目标数字和既有正面审阅可见；chat_id为01a1c8ef-6688-7b71-9943-f98a9c3ff068。其9196项是同一AI上下文内的算术重建比较，3194项为作者标量脚本副本核对。v3为知情作者整合与重放。ROUND-005为一名AI的两阶段审阅；640和LWE各有其作者证明可见范围。详细身份保留在 [E16溯源](reading/crypto_fi_official_profile_review/INPUT_AND_REVIEW_PROVENANCE.json) 与 [v3人工入口§6](reading/crypto_fi_research_manuscript_v3/HUMAN_REVIEW_ENTRY.md)。

可见模型家族为Codex基于GPT-6；精确后端ID/权重为null。模型错误过程独立性、人工、跨模型、当前盲审、形式证明助手认证的本轮新增数均为0，校准NOT_CALIBRATED。本包由一个知情Codex上下文装配及确定性重放；检查数量只承担其实际算术范围。

CJL原PDF及逐版本对应、Nishimaki 2024扩展版Lemma5.7原图仍有缺项；它们影响方法归属/继承归约及优先权评价，稿内A/B自含证明和有限算术可先审。详见 [SOURCE_GUIDE.md](SOURCE_GUIDE.md)。

作者程序状态为 **WAITING_FOR_AUTHOR_ARTIFACT**：认证作者UE源文件0、完整配置映射0、已取得消息比对作者UE轨迹0，六组AES/SHAKE配置整体映射均UNRESOLVED。等待认证UE版本/配置/依赖、秘密流联合律与算术/失败路径、未筛选Enc→TG→Upd→Dec的原消息及两次比对轨迹、性能表原100次五操作日志。详见 [最小作者工件规格](reading/crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md)；本包采用v3 §7.5的三尺寸更新状态。

## 8. 包结构、版本与测试

`frozen/` 保存原字节；`reading/` 提供相对链接阅读副本；`replay/` 提供公开入口及路径适配副本；`provenance/` 保存来源标识、映射与差分。历史源码只供审阅，公开运行命令统一见REPLAY。

[PATH_MAP.json](provenance/PATH_MAP.json) 将原绝对路径映到冻结原件和阅读副本；[转换记录](provenance/READING_TRANSFORMATIONS.json) 记录来源哈希、变更范围及完整正文一致性；[脚本差分](provenance/SCRIPT_ADAPTATIONS.json) 固定三份路径适配。嵌入历史JSON中的其余绝对路径承担审阅溯源标识；公开重放的全部输入均从包内冻结文件复制。

[MANIFEST.json](MANIFEST.json) 覆盖除自身外的全部包内文件；压缩包SHA-256写在包外同名.sha256文件，避免循环。实际环境、异路径解压、不同工作目录、全载荷比较及输入起止指纹见 [PORTABILITY_REPORT.json](PORTABILITY_REPORT.json)。测试范围为同一台Windows机器的路径迁移；另一物理机器及其他操作系统保留实际运行记录后再评价。
''')
write('HUMAN_QUESTIONS.md',r'''
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
''')
write('REVIEW_FORM.md',r'''
# 实际人工密码学审阅记录表

本表由实际审阅者填写。当前全部意见栏为空，AI整理与标量重放记录保留在包内溯源文件。

## 审阅者与输入身份

- 姓名/可公开身份：
- 单位、专长及联系方式（自愿）：
- 审阅日期/时区：
- 利益关系、共同作者关系及先前接触范围：
- 使用的包ZIP SHA-256：
- MANIFEST.json文件SHA-256：
- 实际所用FI PDF版本/SHA-256：
- 是否使用AI、CAS或形式证明助手；工具/版本及介入范围：
- 是否允许向作者转交意见、实名引用或公开意见（分别填写）：

## 实际阅读与运行范围

| 文件及版本 | 精确章节/式号/物理PDF页 | 阅读方式：全文/选段/原图/代码/重放 | 实际核对内容 | 保留意见 |
|---|---|---|---|---|
| | | | | |
| | | | | |

- 重放环境（OS、架构、Python/依赖）：
- 解压目录、调用时cwd、新输出目录：
- 实际命令及退出码：
- REPLAY_RESULT.json路径/哈希；是否核完整数学载荷及输入起止指纹：
- 运行失败、环境差异或跳过项：

## H1 结论

对应 [H1材料及命题](HUMAN_QUESTIONS.md#h1-原游戏攻击与共同正确性)。

- 结论（接受所列范围／部分接受／需修正／发现反例／待补证据）：
- 接受的版本、模型、量词、攻击权限及参数族：
- 已核具体游戏行、章节、式号和证明步骤：
- 固定P₂条件化、P₂-only停止、共同正确性和成本的分别判断：
- 反例（参数/输入/事件/概率或资源）、失效式及其影响：
- 修正建议和建议替换文字：

## H2 结论

对应 [H2材料及命题](HUMAN_QUESTIONS.md#h2-三参数可靠性)。

| 参数/量词 | 初始界判断 | 更新显示端点判断 | 条件于I端点判断 | 具体式号/证书字段/保留条件 |
|---|---|---|---|---|
| 640 固定A | | | | |
| 640 均匀Setup | | | | |
| 976 固定A | | | | |
| 976 均匀Setup | | | | |
| 1344 固定A | | | | |
| 1344 均匀Setup | | | | |

- 两层条件结构、2n系数律、判据端点的判断：
- 全平移覆盖/最大值、全频率/质量、有向算术的判断：
- K⊆J、初始PGF及最后I条件化的判断：
- 反例、失效式、重放差异、修正建议：

## H3 结论

对应 [H3材料及命题](HUMAN_QUESTIONS.md#h3-条件安全软件与贡献)。

- 条件LWE定理、有限配置、性能表与实际软件范围的判断：
- 需要作者工件或前驱原文才能判断的事项：
- 作为独立短文的价值、建议定位与依据：
- 作为毕业论文核心章节的价值、建议定位与依据：
- 贡献措辞、方法归属、优先权和软件迁移表述的修正建议：

## 逐项问题记录（按需复制）

- 编号及严重性：
- 所属H1/H2/H3、版本/文件/章节/准确式号或代码行：
- 原命题：
- 推导、反例或证据：
- 影响范围及仍可保留的结论：
- 建议修正及复核办法：

## 交回与后续

- 总体结论及适用范围：
- 建议优先修正的事项：
- 希望作者补交的最小材料：
- 后续复核承诺/限制：
- 签名或记录确认（自愿）：
''')
write('SOURCE_GUIDE.md',r'''
# 冻结来源、规范和缺项

来源标识S1–S13、E1–E17沿用v3，原始记录见 [REVIEW_SOURCE_REGISTRY.json](provenance/REVIEW_SOURCE_REGISTRY.json)。实际携带的每个文件及其来源/阅读路径、字节数、SHA-256见 [PATH_MAP](provenance/PATH_MAP.json) 和 [MANIFEST](MANIFEST.json)。哈希核对与语义阅读分别登记。

## 原规范阅读定位

| 来源标识/冻结版本 | 包内原件 | 准确定位及用途 |
|---|---|---|
| S1 FI期刊，arXiv2410.03948v4，23页 | [PDF](frozen/crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf)、[TeX articlev08](frozen/crypto_fi_research_manuscript_v1/sources/articlev08.tex) | 9–11游戏/终局；12初始PKE；13 Ord/Tensor；14 TG/Upd；15 Theorem6.3；19–20 Lemma6.8/Theorem6.9；20–22实现/性能 |
| S2 官方2021-06-04，59页 | [PDF](frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf) | 物理10最近整数平局向上；15 Encode/Decode及CDF质量关系；16 Algorithm5严格t>Tχ(j)、末项未访问；25 Table3质量和参数 |
| S11 官方2023-03-14，21物理页 | [PDF](frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf) | 物理8/印刷4 Sample；物理15/印刷11 TableA.3质量；物理16/印刷12 TableA.4 CDF；1344须结合S10 |
| S10 官方issue35，Patrick Longa，2024-11-27 | [E16只读工具回执](frozen/crypto_fi_official_profile_review/evidence/OFFICIAL_1344_ERRATUM_LIVE_RECEIPT.json)、[回执0](frozen/crypto_fi_research_manuscript_v2_1/evidence/official_1344_erratum_0.json)、[回执1](frozen/crypto_fi_research_manuscript_v2_1/evidence/official_1344_erratum_1.json) | Tχ(5)=32765，Tχ(6)=32767；[原URL](https://github.com/microsoft/PQCrypto-LWEKE/issues/35#issuecomment-2504969837) |

关键身份：FI PDF SHA-256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`；TeX `16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b`；2021规范 `5c3440b311c7ee4fba8b9a12e0ff567eb75c29fef66843f3eecc16f137164f7d`；2023规范 `4688192bf5f5ac29e622ef359860890d2e97c224216baea2216dc42ef8d1547f`。

本轮对上述三个PDF重新运行结构预检，分别23/59/21页、PASS。Windows下预检器的--output分支要求POSIX dirfd；本轮采用其stdout JSON并由外层保存，预检数学/结构逻辑保持原样。新提取文本和stdout侧录位于provenance。结构预检仅承担读取完整性。原规范关键页图和E16语义阅读范围保持在冻结溯源中。

## 必须核对的合同

Ord：实际n列、D个位平面，与Tensor_D(S)=[S;2S;…;2^(D−1)S]同序。源Ord一般记号为n̄列，Upd传入n列；S/E按KeyGen与乘积取n×n̄。稿§2及F.1明确补齐，H1判断其对象合理性。

精确χ：分母65536，0计一次、其余正负各一次。640分子9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1；976分子11278,10277,7774,4882,2545,1101,396,118,29,6,1；1344分子18286,14320,6876,2023,364,40,2。已更正976及1344勘误均由CDF与全部输入字核对。Encode/Decode最近整数平局向上给640/976正确残差[-4096,4095]、1344为[-2048,2047]，模q解释。

概率合同：同A两代、全部相关原始χ之前固定A/消息、给定A的精确iid联合律；B采用一次未筛选TG/Upd、全部P₂秩自然积分。均匀Setup界额外平均独立均匀全矩阵A。初始事件在原实验完成后条件化。

## 来源缺项与实际影响

| 缺项 | 已有材料 | 实际影响/可先审范围 |
|---|---|---|
| CJL原PDF、2025索引文本至CRYPTO2026逐版本对应 | S5指定索引节选；ePrint2025/968及DOI题录身份 | 公式原图认证、编号和方法归属/优先权需补核；附录A自含算法/证明可按当前模型判断。A来源隐藏与B有限可靠性均有自含论证 |
| Nishimaki FI所引2024扩展版§5/Lemma5.7原图、会议版编号对应 | ePrint2021/221身份、FI引用及既有转录范围 | FI继承归约和Theorem6.9完整前件链保留待核；H3按精确样本/视图/时间逐项判断。当前A/B无LWE困难性前提 |
| 可归属作者UE源、配置、依赖和原消息轨迹 | 公开来源审计及上游基础KEM参照，WAITING_FOR_AUTHOR_ARTIFACT | 六配置的软件适用性、秘密seed联合律、筛选/算术及100次计时分母保持UNRESOLVED。单条完整消息轨迹可认证具体路径，概率迁移仍需联合律/有限损失证据 |
| 全球应用优先权的完整覆盖 | E13截至2026-11-10的有界审计、E15于11-11登记的六条查询 | 现有贡献措辞按实际检索范围使用，全球优先权待外部判断 |

## 载荷及封存规则

本包携带两项结果直接证明、证书、所用原论文/规范和相关身份/修正溯源。主稿直接超链接的历史版本形成辅助阅读闭包；JSON内未被运行入口读取的更早路径作为历史标识保留，记录所载文件与原包的完整性主张分别解释。原历史MANIFEST可以核其原始载荷哈希；该MANIFEST列举的更大历史目录按其原边界解释。

阅读转换记录使用原件SHA-256和副本SHA-256。Markdown逐字符保留所有链接目标以外正文，另加明确说明和必要行定位锚点；JSON仅改完整路径字符串，反向替换后整对象相等。原章节、式号、质量、分数和身份均保持。运行脚本适配仅增加os导入及根路径替换，完整差分随包。
''')
write('REPLAY.md',r'''
# 最小有限证书重放

## 运行

安装Python 3.11+后解压整个包。运行仅使用Python标准库；PDF阅读器用于人工阅读。当前实际测试环境及路径见 [PORTABILITY_REPORT.json](PORTABILITY_REPORT.json)。

Windows PowerShell示例；将两个绝对路径替换为本机实际值：

```powershell
python -I -S -B -X utf8 'E:\FrodoReview\replay\run.py' --output 'E:\FrodoReviewWork\run_001'
python -I -S -B -X utf8 'E:\FrodoReview\replay\verify_package.py' --output 'E:\FrodoReviewWork\links_001.json'
```

POSIX同一入口：

```sh
python3 -I -S -B -X utf8 /path/to/FrodoReview/replay/run.py --output /path/to/new_work/run_001
```

`--output`为必须参数，要求新的绝对包外目录；运行前该目录应不存在。cwd可为任意目录。入口先按MANIFEST核全部包内文件，再将frozen输入复制到新工作目录sandbox，执行标量副本。历史目录和包内文件仅被读取。每份脚本硬超时600秒，失败通过非零退出码及具体日志暴露。使用`-I -S -B`隔离用户模块和第三方site，并抑制字节码写入。

## 输入、输出与覆盖

| 运行标签/复用脚本 | 包内输入 | 新工作目录输出及核验 |
|---|---|---|
| author_compute / compute_profile_certificates.py | 冻结DISTRIBUTION_TABLES及官方CDF常量 | 重新生成976/1344整份OFFICIAL_PROFILE_CERTIFICATES；要求与v3冻结证书逐字节相同 |
| author_verify / verify_profile_certificates.py | 新生成证书、包内全部登记来源/输入副本 | CERTIFICATE_CHECK，3194项；完整JSON比较，含CDF/全标签Decode/PGF/全部频率/条件化及640特化 |
| review_976_1344 / recompute_review.py | 新生成官方证书、640固定A证书 | 9196项重建；INDEPENDENT_RECOMPUTATION；两个65536项u16le映射及1484/1000代表；全部数学字段比较 |
| source_event_976_1344 / verify_historical_relations.py | PARAMETER_CERTIFICATES及976/1344卷积原件 | 全部1281/769系数及ε≤2^-1118/2^-1532；与v3 HISTORICAL_EVENT_RELATIONS全对象比较 |
| fixed_A_640 / recompute_certificates.py | 640 FINITE_CERTIFICATES | 385项、H尾73、全频率、初始PGF及I条件端点；完整载荷比较 |
| uniform_Setup_640 / recompute_probability_chain.py | 640 SCALAR及JOINT_SCALAR证书 | 303项、均匀Setup的坐标/行/完整上界和I端点；完整JSON精确比较 |
| A_all_convolutions / ROUND-005 math_verify.py | 三组精确χ常量，与包内全部冻结卷积对照 | 重新卷积三组；完整1537/1281/769整数数组摘要比对；ε640≤2^-751；CF-1有限正确性例；A_EXTRA_CHECKS额外绑定χ640、25μ<1/2及n128的ε≤2^-59 |

主结果绑定另输出 `UNIFIED_SELECTOR_BINDINGS.json`，将三参数×两种A量词的原/条件精确端点绑定至v3统一选择器，核全部显示上界。全卷积比较包括offset、分母、归一化、完整整数数组摘要；源脚本同时重建峰值及32重L₂恒等式。有限例与一般符号定理的证据范围分别保留。

最终汇总 `REPLAY_RESULT.json` 记录命令、cwd、环境、脚本哈希、退出码、完整载荷比较、路径元数据改造、包内全部输入的起止指纹。详细日志位于logs；所有重放产物位于sandbox及工作目录根。`INPUT_FINGERPRINTS_BEFORE/AFTER.json` 必须完全一致。每次使用新目录即可保留多次执行记录。

## 完整数学载荷与元数据比较规则

采用递归整对象比较：字典键集合、列表长度/顺序和每个值精确匹配；二进制平移映射按全部131072字节比较。仅以下**具体JSON Pointer**采用元数据规则：

- review重建结果的 `/script_sha256` 必须等于实际路径适配脚本哈希；冻结值必须是有效SHA-256。该差异由包内差分解释。
- review结果 `/seconds`、`/profiles/976/H/enumeration_seconds`、`/profiles/976/total_seconds`、`/profiles/1344/H/enumeration_seconds`、`/profiles/1344/total_seconds` 仅比较数值类型及非负；它们是运行时钟。
- 两个PGF代表JSON的 `/map_path` 必须实际指向新sandbox内存在的映射；map_sha256及其余全部字段精确比较。
- 640固定A重建的 `/python` 必须等于实际Python版本；冻结值保留其原环境身份。

除此之外零字段排除。原始精确分子、分母、大整数哈希、质量、CDF、频率、全部代表、最大差、分组和条件端点均必须相同。历史脚本的展示近似值也按完整JSON比较；若跨平台运行出现展示浮点差异，入口会报告差异，当前版本保留严格行为。

作者生成器和核对器保持原脚本字节；仅运行工作副本的INPUT_SNAPSHOT/SOURCE_PAGES中path/png改指向sandbox，来源哈希保持，全部被核path均来自包内。三份适配脚本通过FRODO_FI_SANDBOX读取复制后的根，数学语句保持；[适配记录](provenance/SCRIPT_ADAPTATIONS.json) 给出来源哈希与完整差分。运行器中新增的A_EXTRA_CHECKS和选择器绑定属于确定性整数/分数核对，候选机制实现数为0。

## 解释运行结果

PASS说明包内有限数学证书在记录环境下重建并匹配，且输入字节保持。模型解释、符号证明和实际软件迁移分别由H1/H2/H3判断。全部动作均为本地文件、确定性标量算术；该入口的范围涵盖包装/重放，真实UE采样、作者程序执行、Monte Carlo及LWE求解的计数均为0。

## 封存与文件核查

`MANIFEST.json`按包内相对路径列举全部文件，唯一自排除项为自身；其字节哈希可由外部ZIP及.sha256链核对。`PORTABILITY_REPORT.json`被MANIFEST覆盖。ZIP及其.sha256放在包外，ZIP哈希对象为最终压缩字节。包的阅读副本、运行输入和路径适配记录均被清单覆盖。
''')
(O/'replay').mkdir(exist_ok=True)
shutil.copyfile(W/'run.py',O/'replay/run.py')
print('Wrote handoff documents and public replay entry')
