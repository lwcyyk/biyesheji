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
