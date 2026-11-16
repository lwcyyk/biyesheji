"""Targeted, source-bound manuscript patch and claim integration for v2.2.
Only document assembly, finite-scalar evidence and fingerprints; no mechanism implementation.
"""
from pathlib import Path
from fractions import Fraction
import copy,difflib,hashlib,json,platform
BASE=Path(r'D:\毕业设计')
OLD=BASE/'crypto_fi_research_manuscript_v2_1'
OUT=BASE/'crypto_fi_research_manuscript_v2_2'
FA=BASE/'crypto_fi_640_fixed_A_correctness'
REVIEW=BASE/'crypto_fi_640_fixed_A_review'
IMPL=BASE/'crypto_fi_author_implementation_audit'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def textsha(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
identity={'status':'INFORMED_AUTHOR_REVISION_AND_PROOF_INTEGRATION','description_zh':'知情作者修订与证明整合','author_proof_and_prior_reviews_visible':True,'fixed_A_positive_targeted_review_visible':True,'declared_model_family':'Codex based on GPT-6, as stated in the current developer context','exact_backend_model_id':None,'exact_weights_version':None,'independent_model_error_processes_established':False,'new_independent_reviews':0,'new_human_reviews':0,'new_cross_model_reviews':0,'new_blind_reviews':0,'new_subagents':0,'formal_proof_assistant_used':False,'empirical_calibration':'NOT_CALIBRATED'}

old_text=(OLD/'CRYPTOANALYSIS_DRAFT.md').read_text(encoding='utf-8-sig')
t=old_text
operations=[]
def replace(old,new,why):
 global t
 assert t.count(old)==1,(why,t.count(old))
 t=t.replace(old,new)
 operations.append({'purpose':why,'old_text':old,'new_text':new,'old_sha256':textsha(old),'new_sha256':textsha(new)})
def para(prefix,new,why):
 lines=[s for s in t.split('\n\n') if s.startswith(prefix)]
 assert len(lines)==1,(prefix,len(lines))
 replace(lines[0],new,why)

replace('# FrodoPKE型可更新加密的来源隐藏攻击与640参数可靠性：共同正确族、一次更新概率与假设边界','# FrodoPKE型可更新加密的来源隐藏攻击与640可靠性：共同正确族、逐固定公开矩阵与假设边界','v2.2标题突出矩阵量词扩展')
para('研究稿v2.1，','研究稿v2.2，2026-11-11（Asia/Shanghai）。身份：知情作者修订与证明整合（INFORMED_AUTHOR_REVISION_AND_PROOF_INTEGRATION）。本版正式整合已通过定向复核的固定A可靠性结论；v2.1的INC976勘误与证书闭合继续有效。引用对象为DOI **10.46298/fi.14425** 的FI论文及arXiv:2410.03948v4。本文供人工密码学审阅，来源、数学复核、程序迁移及应用优先权分别登记。','版本及本轮身份')
replace('本版从正确CDF重新生成64重整数卷积','v2.1阶段从正确CDF重新生成64重整数卷积','INC976历史执行范围')
replace('## 摘要','> **v2.2修订说明。** 新增§7.3命题640-FA与附录E：对每个预先固定A的一次更新完整错误率≥99.4956640%，初始正确条件下显示下界保持；公开seed按逐seed合同直接平均。§7.5更新迁移表；证书副本直接验收H尾指数73。本轮沿用均匀Setup更紧的99.9969655%，其数字与量词并列列示。修正闭合与指纹见[REVISION_AND_READINESS.md](D:/毕业设计/crypto_fi_research_manuscript_v2_2/REVISION_AND_READINESS.md)。\n\n## 摘要','版本增量说明')
para('对FI打印算法配官方640数值参数n=640、','对FI打印算法配官方640数值参数n=640、D=15、q=32768、m̄=n̄=8、B=2，采用精确独立χ640、两代共用A、既定Ord规范化、一次诚实未筛选TG/Upd及官方最近整数平局向上规则。对每个在全部相关原始χ抽样前固定的A和每个预先固定合法128位消息，证明初始完整正确率≥1−2^-132，更新后指定行8坐标全正确率属于[0.0000135117,0.005043360]，完整正确率≤0.005043360、错误率≥99.4956640%。条件于初始完整消息已正确，上述显示精度下的更新界保持。在均匀Setup这一较窄模型下，仍保留更紧的指定坐标区间[0.2499054,0.2500946]、行区间[0.0000152532,0.000030345]、完整正确率≤0.000030345及错误率≥99.9969655%，初始正确条件下也保持。前一结论逐A平均其后诚实币，后一结论平均均匀A及诚实币；给定A后的全部原始χ坐标和调用具有声明的独立乘积律。正文给出两种量词下的命题与证明概要，附录D/E分别列全频率与有向证书。','摘要纳入固定A及并列量词')
replace('本文贡献限于具体构造的来源隐藏失败、声明模型中的可靠性概率及证明范围审计。','本文贡献为具体构造的来源隐藏失败、声明模型中的可靠性概率、公开矩阵量词扩展及迁移前提缩减，并附证明范围审计。','摘要贡献')
para('本文给出两项主要结果。','本文给出两项主要结果。第一，原游戏合法支撑判定、逐固定A的真实fresh界及付费轮换放大，在同一CF-1参数族中与最长n次逐样本正确性同时成立。第二，FI打印算法配官方640参数的一次更新可靠性：对每个预先固定A，在给定A后的独立χ640、同一A两代、既定Ord、诚实未筛选更新及平局向上合同内，初始完整正确率≥1−2^-132、指定行区间[0.0000135117,0.005043360]、完整错误率≥99.4956640%；均匀Setup下保留更紧的指定坐标、行和完整错误率≥99.9969655%结论。两种更新界额外条件于初始已正确均保持显示端点。可靠性证明保留共享钥匙与token依赖，按真实1280系数律和八阶混合矩处理联合事件；固定A扩展以独立χ平移PGF替代均匀A的H重量步骤，重算全频率常数。该公开矩阵量词扩展及迁移前提缩减，使公共A生成器的均匀性责任从新界中解除。源LWE前提与命名混合端点的精确范围审计继续约束评价。','贡献段纳入矩阵量词扩展')
replace('应用优先权沿用下述实际检索范围；新增概率结果的全球优先权仍待专门检索。','应用优先权沿用[E13]截至2026-11-10的实际核读与检索范围；同FI对象的完整等价A/B命题直接先例在该范围尚未定位，全球优先权继续待核。本轮固定A扩展新增检索为0，其方法归属仍为上述成熟工具。','沿用实际应用优先权范围')
para('截至2026-11-08的已封存定向检索及指定原文核读，','截至2026-11-10的已封存应用与发表影响审计[E13]，A/B均保留具体新对象应用候选地位；相同FI对象、同权限、完整等价命题的公开直接先例在其实际检索范围尚未定位。最强已核方法近邻为KLR2019公开token一致性与官方Frodo基础PKE失败分析。全球优先权、Nishimaki扩展版与CJL逐版本对应继续分别待核。本轮只整合固定A定向复核及既有作者工件裁决，公开文献检索新增0。','检索截止及证据状态沿用')
para('另一项最强结论为§7.2命题640：','另一项结果具有两个最强量词版本：§7.3命题640-FA对每个预先固定A给一次更新完整错误率≥99.4956640%；§7.2命题640在均匀Setup下给更紧的≥99.9969655%。两者均有初始完整正确率≥1−2^-132，初始正确条件下的更新显示下界保持。给定A后的精确χ乘积律及其余完整合同见各命题。CF-1采用随λ增长的D/q；这两个640可靠性版本固定D=15、q=32768，分别由各自证明承担。','最强引用结论')
para('全局A∈R_q^(n×n)在后续χ抽样前固定。','全局A∈R_q^(n×n)在全部相关原始χ抽样前固定，给定A后χ坐标及调用保持声明的精确独立乘积律。FI.Setup均匀选择A。§§3–6攻击定理逐A成立，依据是父噪声的独立平移界及保留F₁的列卷积界。§7.2的更紧可靠性界平均于均匀Setup，H的二项重量来自均匀A逐列满射，见附录D。§7.3的新可靠性界对每个固定A成立，以父χ平移PGF控制w≥450，见附录E；初始正确率在消去A后也逐A成立。给定每个公共seed后若仍满足整个冻结合同，攻击与新可靠性界均可逐seed应用后平均。每代钥匙为','采样合同与A量词')

# Existing section 7.3 moves to 7.4; all inherited cross-references follow it.
for old,new in [('§7.3','§7.4'),('### 7.3 Theorem6.3','### 7.4 Theorem6.3')]:
 # The freshly introduced fixed-A section references are restored below.
 t=t.replace(old,new)
# Fresh references intentionally point to fixed-A proposition at 7.3.
t=t.replace('新增§7.4命题640-FA','新增§7.3命题640-FA').replace('§7.4命题640-FA','§7.3命题640-FA').replace('§7.4的新可靠性界','§7.3的新可靠性界')

fixed_body=r'''### 7.3 命题640-FA：每个预先固定A的一步可靠性

**命题640-FA。** 对FI期刊/v4打印算法，固定n=640、D=15、q=32768、m̄=n̄=8、B=2。任取在全部相关原始χ采样前固定的A∈R_q^(640×640)，两代共用A；给定A后，全部原始χ640坐标和调用满足§6.1精确表的独立乘积律。采用§2.2的n列位平面Ord规范化、一次诚实未筛选TG和一次Upd及官方最近整数平局向上Decode。对每个预先固定合法128位消息、预先指定行，记I为初始完整正确，J为更新后该行8坐标全正确，K为更新后完整正确。概率平均该固定A之后的两代钥匙及全部Enc/TG/Upd诚实币。

| 事件 | 每个固定A下的界 | 同一固定A下额外条件于I |
|---|---|---|
| 初始I | Pr(I\|A)≥1−2^-132 | Pr(I\|I,A)=1 |
| 指定行J | [0.0000135117,0.005043360] | 同一显示区间 |
| 完整消息K | Pr(K\|A)≤0.005043360 | Pr(K\|I,A)≤0.005043360 |
| 完整错误K^c | Pr(K^c\|A)≥99.4956640% | Pr(K^c\|I,A)≥99.4956640% |

**证明概要。** 固定A,u，父C₁的640个坐标是独立χ平移，零原子≤a₀=1161/8192。非零坐标数L≤位重量w。0<z<1时E[z^L|A,u]≤[a₀+(1−a₀)z]^640；z=2/5给Pr(w≤450|A)≤2^-73，覆盖w<450。完整R₂=Σr_i²的PGF以z_r=31/32给Pr(R₂≤3500|A)≤2^-27。故每个固定A的好事件G={w≥450,R₂≥3500}坏质量<δ=2^-26，好环境w+R₂≥3950。

取B=σ(A,U₀,F₀,R)、V=σ(B,U₁,F₁,U₂,F₂)。V层剩余钥匙/G列包iid给Pr(J|A)=E[p(V)^8|A]；B层1280个a/b系数有真实共同律T_B=Σ₁^w X_ℓ+Σr_iY_i，独立同分布。绝对Fourier矩、全49点差值律及六组全部非零频率，配合新高频ρ=16156100186665515949/18446744073709551616，给每个好B上

\[
E[|p(V)-1/4|\mid B]\le Z_A
=\frac{4559006261671696450341}{1208925819614629174706176}.
\tag{FA1}
\]

Z_A是统一常数，下标标记量词版本；它对A取值相同。逐指数64位上包络、精确ν加权、640次幂80位上包络的松弛全部进入Z_A。点态弦线与坏环境混合给

\[
U_A=(1-\delta)[4^{-8}+(21845/16384)Z_A]+\delta
=0.00504335901429038086998\ldots;
\]
\[
L_A=[(1-\delta)(1/4-Z_A)]^8
=0.000013511757524951134056\ldots.
\tag{FA2}
\]

上界来自E[p(V)^8|A]，下界来自Jensen。K⊆J给完整消息单侧上界。初始残差消去A，以原PGF和64坐标并集逐A给Pr(I^c|A)≤a_I=2^-132。先完成原实验的联合分析，再以(L_A−a_I)/(1−a_I)与U_A/(1−a_I)条件化，精确比较保持表列端点。附录E给FA1—FA5、解除条件台账及本版385项重放入口。[E10,E11] □

| 可靠性版本 | A量词与证明依据 | 更新完整正确率上界 | 完整错误率下界 |
|---|---|---:|---:|
| §7.2 / 附录D | 均匀Setup及诚实币平均；H公平位重量与原全频率常数 | 0.000030345 | 99.9969655% |
| §7.3 / 附录E | 每个预先固定A，给定A后的原始χ乘积律；χ平移PGF与重算全频率常数 | 0.005043360 | 99.4956640% |

两行均保留I条件化后的同一显示端点。均匀Setup下可选更紧第一行；任意前置矩阵分布可用第二行。公开seed推论：若公共变量Z_pub先确定A=g(Z_pub)，且每个相关Z_pub值下后续χ及算法满足本命题冻结合同，则逐seed应用并平均，行区间、完整错误及初始界均成立；初始正确条件下亦然。秘密噪声流的联合律与实际算法合同由§7.5继续核准。

'''
replace('### 7.4 Theorem6.3的充分前提与实际程序范围',fixed_body+'### 7.4 Theorem6.3的充分前提与实际程序范围','新增固定A完整命题与概要')
para('作者实际程序/commit、实际D/B/CDF/T、','作者实际程序状态沿用[E12] **WAITING_FOR_AUTHOR_ARTIFACT**：六种报告配置640/976/1344×AES/SHAKE的整体静态映射均为UNRESOLVED，带初始及更新后消息比对的作者UE运行轨迹为0。论文报告KG、Enc、Dec、TG、Upd五操作各100次计时，更新后消息比对及成功分母的对应仍待工件。已取得官方上游基础KEM代码与作者UE各有专门归属要求；数学标量脚本及精确证书承担有限核对。实际D/B/CDF/T、同A两代、秘密seed域分离与联合律、筛选重试、Ord、打包、溢出、取模和Decode继续逐项核准。','作者软件状态及性能对象')
para('来源攻击的逐固定A定理可对任意先固定A的公开seed分布平均；','来源攻击与新固定A可靠性界均可在逐seed冻结合同下对任意前置公开A生成器平均；为新可靠性界证明公开A与均匀全矩阵的距离这一责任已解除。引用更紧均匀Setup数字仍需其对应分布依据。秘密噪声流、实际公式与机器语义分别保留迁移责任。若实际第b实验攻击输出概率与理想模型偏差≤ν_b，则实际gap至少max{0,理想gap−ν₀−ν₁}；可靠性采用各自事件偏差及初始分母，见§7.5。','清除旧迁移责任的过时全称')
mapping=r'''### 7.5 v2.2模型迁移表与最小作者工件事实

本表更新[E12]中专为均匀Setup结果写出的A生成器责任，历史文件保持只读。MAPPED/DIFFERS只用于已有源位置的子事实；六组作者整体配置继续UNRESOLVED，取得认证工件后逐项判定。

| 模型/责任 | v2.2可采用的范围 | 仍需依据 |
|---|---|---|
| A：CF-1攻击/共同正确性 | 逐预先固定A，公开seed可按条件合同平均；参数要求增长D/q及χ640 | 同一原游戏与公式、原始噪声联合律、Ord及环算术；固定官方配置与增长族分别对应 |
| B_U：更紧均匀Setup界 | 完整正确≤0.000030345，错误≥99.9969655% | 真正均匀A或能支持该目标事件/环境的有效分布迁移，及其余冻结合同 |
| B_FA：新固定A界 | 每个A完整正确≤0.005043360，错误≥99.4956640%；逐seed平均覆盖任意公共A生成器 | 给定每个相关公共seed后，原始χ与算法仍满足冻结合同 |
| 公共A分布责任 | 对B_FA，公开生成器的均匀性、伪随机性、像熵与全矩阵统计距离责任已解除 | 两代复用同一A、确定A的时序、条件噪声律仍需实际源位置 |
| 秘密噪声seed | 单点CDF相符只支持边缘采样器 | seed来源、长度、域分离、切片与复用；精确联合律或具体统计/计算/随机预言机迁移损失 |
| TG/Upd与筛选 | 原式四块、P₂形状、额外噪声、全部rank未筛选 | 实际代码、重试/异常/成功分母；条件化重采样需新分布论证 |
| Ord与算术 | 配对固定行置换保持gadget及iid行律；2^w环回绕在D≤w时可同态投影到2^D | 实际置换、dtype/提升/溢出、取模代表、打包及平局向上；比较/位提取/浮点另核 |
| 作者真实性能对象 | WAITING_FOR_AUTHOR_ARTIFACT；整体静态映射0，消息比对轨迹0 | 认证commit/archive、配置导出、调用链与原始日志 |

128位确定性seed生成640矩阵与均匀全矩阵的统计距离下界1−2^-6143872，仍是[E12]的有效支撑计数；该差异已从B_FA适用前提中解除。若选用B_U的更紧数字，则须另给相关分布依据。秘密κ位seed确定性生成N个χ的像在理想iid律下质量至多min{1,2^κa^N}，单点采样表相同仍无法承担联合采样合同；具体迁移需注明可测事件、辅助视图及有限损失。

对B_FA，若更新完整正确事件偏差≤η_K、初始失败额外损失≤η_I，则正分母时

\[
\Pr_{code}(K)\le U_A+\eta_K,\qquad
\Pr_{code}(K\mid I)\le\frac{U_A+\eta_K}{1-2^{-132}-\eta_I}.
\tag{MT}
\]

保持0.005043360须作具体有限比较；B_U相应使用U_*及其迁移损失。三个最小事实组为：认证的源代码与640配置及同A两代/逐公共seed噪声合同；TG/Upd、Ord与全部失败筛选路径；环算术、打包、半向上Decode与一条含原消息、初始/更新后消息比对的未筛选轨迹。该轨迹提供路径证据，错误概率仍由模型对应或迁移引理承担。六配置规范比较中640数值子项与B_U/B_FA相符，976/1344的数值范围DIFFERS；作者实际程序均待认证。

'''
replace('## 8. 精确LWE前提的适用性',mapping+'## 8. 精确LWE前提的适用性','迁移表与最小工件')
replace('新增概率证明可优先人工核对条件列包、真实1280系数律、全频率包络、八阶弦线及初始正确事件比率。','本版增加公开矩阵量词扩展及迁移前提缩减。人工复核可优先检查附录E的逐平移PGF、两层条件环境、真实1280系数律、全部频率及新ρ、弦线/Jensen与逐A事件条件化。','人工审阅重点')
replace('核心定理及命题640在声明合同内当前已识别的未闭合证明步骤为0；','核心攻击定理、均匀Setup命题640及固定A命题640-FA在声明合同内当前已识别的未闭合证明步骤为0；','已登记数学状态')
replace('本版逐一穷举每种CDF的65536个输入字','v2.1阶段逐一穷举每种CDF的65536个输入字','三表检查执行归属')
replace('此次完整64重卷积与ε重算范围为976；','v2.1完整64重卷积与ε重算范围为976；','976重算归属')
replace('本版实际显示行另经解析核对','v2.1实际显示行另经解析核对，本版承继正确显示表','显示表执行归属')
replace('976引用本版重建且与旧文件逐字节相同的副本','976引用v2.1重建且与旧文件逐字节相同的副本','976副本位置准确')
replace('[CLAIM_EVIDENCE_MATRIX.json](D:/毕业设计/crypto_fi_research_manuscript_v2_1/CLAIM_EVIDENCE_MATRIX.json)','[CLAIM_EVIDENCE_MATRIX.json](D:/毕业设计/crypto_fi_research_manuscript_v2_2/CLAIM_EVIDENCE_MATRIX.json)','当前主张入口')
replace('**v2.1作者勘误与证书重放。** 本版身份为','**v2.1作者勘误与证书重放（历史记录）。** 该轮身份为','历史身份分开')
replace('v2.1当前执行范围另列如下。','v2.1历史执行范围另列如下。','旧执行时态')
review_note='''**固定A定向复核与v2.2整合。** [E11]登记AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW；会话01a1c652-ba78-71a0-b293-a09d61f26039，作者证明、旧正面审阅和目标均可见。FA1—FA5、逐A初始PGF、I条件化与公开seed推论为PROVED_UNDER_STATED_MODEL；385项确定性标量检查通过。E1加固建议要求作者H尾断言由70改73，当前端点影响0。本版[E14]执行加固后的作者副本及路径改向新版的复核副本，385项全部通过，精确结果与原记录相同；该执行登记为知情作者修订与证明整合。精确后端ID及权重为null，模型错误过程独立性保持未认证；本版新增独立、人工、跨模型、盲审、子代理和证明助手审阅均为0。历史385项与本版385项是两次可追溯执行，各自计数，数量未转作独立性认证。'''
replace('**数据可用性与研究声明。**',review_note+'\n\n**数据可用性与研究声明。**','固定A复核身份与本轮执行')
replace('本版五份核心文件、冻结来源、作者标量脚本、976重放程序与精确证书的访问路径和字节身份由MANIFEST固定','本版五份核心文件、冻结来源、新固定A标量副本及精确证书的访问路径和字节身份由MANIFEST固定；976重放按v2.1的历史证书引用','数据可用性本轮范围')
appendix=(OUT/'evidence/appendix_E.md').read_text(encoding='utf-8')
replace('## 参考文献与固定研究记录',appendix+'\n\n## 参考文献与固定研究记录','新增完整附录E')
refs='''
- **[E10]** 固定A作者推导：[FIXED_A_MODEL_AND_TARGET.md](D:/毕业设计/crypto_fi_640_fixed_A_correctness/FIXED_A_MODEL_AND_TARGET.md)、[PROOF_OR_OBSTRUCTION.md](D:/毕业设计/crypto_fi_640_fixed_A_correctness/PROOF_OR_OBSTRUCTION.md)及FINITE_CERTIFICATES，2026-11-10。身份INFORMED_FIXED_A_PROBABILITY_DERIVATION_AND_DETERMINISTIC_FINITE_CERTIFICATES；其当时待复核状态由后续[E11]补充，原记录保持。
- **[E11]** 固定A定向审阅：[MATHEMATICAL_REVIEW.md](D:/毕业设计/crypto_fi_640_fixed_A_review/MATHEMATICAL_REVIEW.md)、[修正报告](D:/毕业设计/crypto_fi_640_fixed_A_review/CORRECTIONS_AND_MANUSCRIPT_IMPACT.md)、REVIEW_VERDICT与INPUT_AND_REVIEW_PROVENANCE，2026-11-11。AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW；385项，精确后端ID为null。
- **[E12]** 作者实现公开溯源：[IMPLEMENTATION_MODEL_MAPPING.md](D:/毕业设计/crypto_fi_author_implementation_audit/IMPLEMENTATION_MODEL_MAPPING.md)及[VERDICT.json](D:/毕业设计/crypto_fi_author_implementation_audit/VERDICT.json)，2026-11-10。WAITING_FOR_AUTHOR_ARTIFACT；本版§7.5更新固定A界对应责任，历史审计保留原字节。
- **[E13]** 发表影响与有界应用优先权：[APPLICATION_PRIORITY_AND_IMPACT.md](D:/毕业设计/crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md)及[VERDICT.json](D:/毕业设计/crypto_fi_publication_impact_audit/VERDICT.json)，2026-11-10。具体核读、检索回执与全球优先权留项按该包。
- **[E14]** v2.2知情作者修订与确定性重放：[REVISION_AND_READINESS.md](D:/毕业设计/crypto_fi_research_manuscript_v2_2/REVISION_AND_READINESS.md)、[REPLAY_EXECUTION.json](D:/毕业设计/crypto_fi_research_manuscript_v2_2/evidence/REPLAY_EXECUTION.json)及本版MANIFEST，2026-11-11。H尾直接验收73，385项复核副本重放通过；新增独立审阅0。
'''
pos=t.index('<!--protected-hedges:')
t=t[:pos]+refs+'\n'+t[pos:]
t=t.replace('<!--protected-hedges: 截至2026-11-08的已封存定向检索及指定原文核读，尚未定位相同FI对象、相同原游戏轨迹的公开攻击。这个结论受检索范围约束；全球应用优先权仍待进一步核准。-->','<!--priority-scope: E13截至2026-11-10的有界检索；固定A扩展本轮新增检索0；全球优先权待核。-->')
(OUT/'CRYPTOANALYSIS_DRAFT.md').write_text(t,encoding='utf-8')
diff=list(difflib.unified_diff(old_text.splitlines(True),t.splitlines(True),fromfile=str(OLD/'CRYPTOANALYSIS_DRAFT.md'),tofile=str(OUT/'CRYPTOANALYSIS_DRAFT.md')))
(OUT/'evidence/MANUSCRIPT_REVISION.diff').write_text(''.join(diff),encoding='utf-8')
blocks=[]
a=old_text.splitlines(True);b=t.splitlines(True)
for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
 if tag!='equal':blocks.append({'op':tag,'v2_1_lines':[i+1,j],'v2_2_lines':[k+1,l],'old_sha256':textsha(''.join(a[i:j])),'new_sha256':textsha(''.join(b[k:l]))})
dump(OUT/'evidence/MANUSCRIPT_PATCH_LEDGER.json',{'schema':'frodo-fi-v22/targeted-revision-patch/1','authority':'Current user request: fixed-A exact endpoints, FA1-FA5, H73 hardening, migration and review provenance; historical files read-only','workflow':'ARS targeted revision principles applied inline to the explicitly authorized v2.2 deliverable; exact-source replacements and unified diff; no ARS schema authorization certification claimed','base':rec(OLD/'CRYPTOANALYSIS_DRAFT.md'),'target':rec(OUT/'CRYPTOANALYSIS_DRAFT.md'),'exact_replacements':operations,'all_changed_blocks':blocks,'unchanged_appendix_A':old_text.split('## 附录A')[1].split('## 附录B')[0]==t.split('## 附录A')[1].split('## 附录B')[0],'unchanged_appendix_D':old_text.split('## 附录D')[1].split('## 参考文献')[0].strip()==t.split('## 附录D')[1].split('## 附录E')[0].strip()})

m=load(OLD/'CLAIM_EVIDENCE_MATRIX.json')
m['schema']='frodo-fi-claim-evidence-matrix/v2.2'
m['version']='v2.2';m['date_asia_shanghai']='2026-11-11'
m['inherited_v2_1_identity']=m['identity'];m['identity']=identity
m['inherited_action_counts_v2_1']=m['action_counts']
m['action_counts']={'author_scalar_copy_runs':1,'review_scalar_copy_runs':1,'review_copy_checks_passed':385,'historical_script_executions':0,'cryptographic_samples':0,'Monte_Carlo_runs':0,'mechanism_implementations':0,'LWE_solver_runs':0,'new_web_searches':0,'author_contacts':0,'native_AS_RP_requests':0,'new_independent_reviews':0,'new_human_reviews':0,'new_cross_model_reviews':0,'new_blind_reviews':0,'new_subagents':0,'formal_proof_assistant_runs':0}
m['manuscripts']='CRYPTOANALYSIS_DRAFT.md; REVISION_AND_READINESS.md; HUMAN_REVIEW_ENTRY.md'
m['core_proof_status']='CF-1 and uniform-Setup640 proofs inherited; fixed-A FA1-FA5 integrated after author/prior-review-visible targeted review; H73 directly hardened and deterministic385 checks replayed. Contract-external author artifact and human review remain pending.'
m['priority_search_cutoff']='2026-11-10'
m['source_registry_inheritance_note']='Inherited records retain the semantic reading/execution scope of their originating stages. Current scope: relevant v2.1 sections, fixed-A proof/review and author mapping; 1789 embedded fingerprint records checked, with no new primary-source network search.'
frozen=copy.deepcopy(m['frozen_models']['640_ONE_UPDATE'])
frozen.update({'label':'FI_PRINTED_V4_OFFICIAL640_EVERY_PREFIXED_A_IID_CHI640_UNFILTERED_ONE_UPDATE_HALF_UP','Setup':'Every A fixed before all relevant raw chi draws; common to both generations','independence':'Given each pre-fixed A, all raw chi coordinates and calls have the exact independent product law','probability_quantifier':'For every pre-fixed A and every pre-coins fixed legal message/row, average all subsequent honest raw coins','row_coordinate_quantifier':'Any row fixed before coins; old tighter coordinate interval is uniform-Setup only'})
m['frozen_models']['640_FIXED_A_ONE_UPDATE']=frozen
cert=load(OUT/'FINITE_CERTIFICATES.json');review=load(REVIEW/'REVIEW_VERDICT.json')
fixed={'model_id':frozen['label'],'initial_full_correct_lower':'1-2^-132','A_quantifier':frozen['Setup'],'conditional_chi_law':frozen['independence'],'row_event':'Specified eight-coordinate row J','full_event':'Full64-coordinate event K subset J','row_interval':['0.0000135117','0.005043360'],'full_message_correct_upper':'0.005043360','full_message_error_lower':'0.994956640','full_message_error_percent_lower':'99.4956640%','condition_initial_full_correct_same_decimal_endpoints':True,'full_message_lower_bound_source':'Separate all-zero U0/F0/R witness p0^15360; row lower is not a full-message lower bound','exact_certificate':cert,'review_status':'PROVED_UNDER_STATED_MODEL','review_identity':review['identity']['status'],'historical_review_checks':385,'current_replay_checks':385}
m['probability_results']['model_id']=m['frozen_models']['640_ONE_UPDATE']['label']
m['probability_results']['scope_note']='Legacy field explicitly uniform-Setup; tighter updated coordinate/row/full numbers require that model. Fixed-A results reside in fixed_A_probability_results.'
m['fixed_A_probability_results']=fixed
m['probability_results_by_model']={'UNIFORM_SETUP':{'model_selector':'frozen_models.640_ONE_UPDATE','result_selector':'probability_results','full_correct_upper':'0.000030345','full_error_lower':'0.999969655','proof':'§7.2; AppendixD; E5-E8'},'EVERY_PREFIXED_A':{'model_selector':'frozen_models.640_FIXED_A_ONE_UPDATE','result_selector':'fixed_A_probability_results','full_correct_upper':'0.005043360','full_error_lower':'0.994956640','proof':'§7.3; AppendixE; E10-E11; E14'}}
def source(id,files,**fields):m['source_registry'][id]={'files':[rec(p) for p in files],**fields}
source('V21',[OLD/x for x in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','ERRATUM_AND_CERTIFICATE_AUDIT.md','HUMAN_REVIEW_ENTRY.md','MANIFEST.json']],scope='Read-only revision baseline; INC976 closed, old proofs/certificates inherited')
source('E10',[FA/x for x in ['FIXED_A_MODEL_AND_TARGET.md','PROOF_OR_OBSTRUCTION.md','FINITE_CERTIFICATES.json','VERDICT.json','evidence/compute_fixed_A.py']],identity=load(FA/'VERDICT.json')['identity'],reading_scope='Complete fixed-A model, proof and scalar script; exact certificate fields parsed and replayed')
source('E11',[REVIEW/x for x in ['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md','INPUT_AND_REVIEW_PROVENANCE.json','REVIEW_VERDICT.json','evidence/recompute_certificates.py','evidence/RECOMPUTED_CERTIFICATES.json']],identity=review['identity']['status'],identity_record=review['identity'],review_checks_as_recorded=385,current_reading_scope='Fixed-A targeted review/proof chain and exact corrections; author/prior-review visibility preserved',core_status=review['status'])
source('E12',[IMPL/x for x in ['IMPLEMENTATION_MODEL_MAPPING.md','VERDICT.json']],identity='INFORMED_PUBLIC_ARTIFACT_PROVENANCE_AND_STATIC_MODEL_TRANSFER_AUDIT',status='WAITING_FOR_AUTHOR_ARTIFACT',current_use='Historical source and mapping status; v2.2 AppendixE/§7.5 remove public-A distribution responsibility for new bound only')
source('E13',[BASE/'crypto_fi_publication_impact_audit'/x for x in ['APPLICATION_PRIORITY_AND_IMPACT.md','VERDICT.json']],identity='Informed application-priority and original-claim audit',search_cutoff='2026-11-10',current_new_priority_searches=0)
source('E14',[OUT/x for x in ['certificates/compute_fixed_A.py','certificates/recompute_certificates.py','FINITE_CERTIFICATES.json','evidence/RECOMPUTED_CERTIFICATES.json','evidence/SCRIPT_COPY_AND_HARDENING.json']],identity=identity['status'],checks_passed=385,H_acceptance_exponent=73,original_sources='E10/E11',exact_result_matches_historical=True)
claims={c['id']:c for c in m['claims']}
for c in m['claims']:
 c['manuscript_location']=c.get('manuscript_location','').replace('§7.3','§7.4').replace('§7.2–7.3','§7.2–7.4')
claims['C25c'].update({'evidence_status':'WAITING_FOR_AUTHOR_ARTIFACT','manuscript_location':'§2.3、§7.4–7.5','source_ids':claims['C25c']['source_ids']+['E12'],'limitations':'Authenticated author UE artifact/config not acquired; all6 author mappings UNRESOLVED; message-checked author UE traces0. Public-A uniformity responsibility removed for C29/C36 only.'})
claims['C25d'].update({'claim':'One-update high-error reliability in frozen ideal640 models','precise_object':'C25a uniform-Setup and C29 every-pre-fixed-A models, with distinct bounds','quantifiers':'Uniform Setup full error>=99.9969655%; every pre-fixed A full error>=99.4956640%, conditional raw chi product law; both retain displayed bound conditional on initial full correctness','dependencies':['C25a','C29'],'source_ids':claims['C25d']['source_ids']+['E10','E11'],'limitations':'Theorem6.3 sufficient premise unmet; finite640 behavior, each model separately scoped; author software applicability still waiting'})
claims['C25p'].update({'manuscript_location':'§2.1、§6.2 (16a)、§7.2–7.5、附录D/E','precise_object':'Fixed-A attack; uniform-Setup tighter reliability; fixed-A broader reliability;64/nu/80;B0+t_maxW','dependencies':['C08','C25a','C29'],'source_ids':claims['C25p']['source_ids']+['E10','E11']})
claims['C25r']['manuscript_location']='附录C、REVISION_AND_READINESS §3'
claims['C27']['source_ids']+=['E10','E11','E12','E14']
claims['C27']['precise_object']+='; fixed-A targeted review E11; v2.2 informed author integration and deterministic replay E14'
def add(id,claim,location,obj,quantifier,assumptions,deps,sources,limitations):
 c={'id':id,'claim':claim,'manuscript_location':location,'precise_object':obj,'quantifiers':quantifier,'assumptions':assumptions,'dependencies':deps,'source_ids':sources,'evidence_status':'PROVED_UNDER_STATED_MODEL','limitations':limitations,'review_identity_and_scope':'E11: AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW; E14 current informed revision and385-check replay; exact backend IDs null; new independent/human/cross-model/blind/formal certification0','semantic_distribution_inputs':['chi640']}
 m['claims'].append(c)
contract=['Every A fixed before all raw chi draws; common to two generations; conditional exact raw chi640 coordinate/call product law','n640,D15,q32768,mbar=nbar8,B2; Ord_n matched to Tensor_D; nearest decode ties upward','One honest unfiltered TG/Upd; every message and row fixed before coins']
add('C29','Fixed-A one-update full-message high-error theorem','§7.3、附录E','640_FIXED_A_ONE_UPDATE','For every pre-fixed A and pre-coins message: full correct<=0.005043360,error>=99.4956640%; specified row in[0.0000135117,0.005043360]; same displayed endpoints under I',contract,['C30','C31','C32','C33','C34','C35'],['S1','S2','E10','E11','E14'],'No exact full64 probability or extension to976/1344/other depths; row lower belongs only to J')
add('C30','FA1/H-tail PGF and direct73-exponent certificate','附录E.1、E.10','Independent chi translations, w>=L, z=2/5','For every fixed A,u: E[z^L|A,u]<=[a0+(1-a0)z]^640; for every A Pr(w<=450|A)<=2^-73',contract,['C02','C10_640'],['E10','E11','E14'],'Boundary450 included in conservative tail; covers w<450; no independent-bit assumption')
add('C31','FA2 R2 lower tail and bad-environment budget','附录E.2','R2=sum r_i^2; G={w>=450,R2>=3500}','For every A: Pr(R2<=3500|A)<=2^-27;Pr(Gc|A)<2^-26',contract,['C30'],['E10','E11','E14'],'Union bound only; no conditioning on rank or success')
add('C32','FA3 two layers, conditional column iid and1280 real coefficient law','附录E.3–E.4','B=sigma(A,U0,F0,R),V=sigma(B,U1,F1,U2,F2); actual TB','Every pre-fixed A and supported conditioning value; row=E[p(V)^8|A]',contract,['C02'],['E10','E11'],'Column iid used before I; no rank/output screening; ring coefficients preserve wraps')
add('C33','FA4 all-frequency bounds and directed finite arithmetic','附录E.4–E.6','w+R2>=3950;new rho;6 complete groups;49point nu;64/nu/80','Every good B under every pre-fixed A: E[abs(p(V)-1/4)|B]<=4559006261671696450341/1208925819614629174706176',contract,['C31','C32'],['E10','E11','E14'],'Unused nu mass charged1; Nyquist conservative; dyadic slack already in Z; no uncharged truncation')
add('C34','FA5 chord/Jensen row bounds and full-message containment','附录E.7','Mixed8th moment; C8=21845/16384; K subset J','Every A: L<=Pr(J|A)<=U;Pr(K|A)<=U',contract,['C31','C32','C33'],['E10','E11','E14'],'Row lower is for J; full lower has independent all-zero witness p0^15360; no cross-row independence claim')
add('C35','Initial correctness and event-ratio conditioning for every A','附录E.8','A-free initial residual;25/625-point PGFs;64-coordinate union','Every A:Pr(Ic|A)<=2^-132;conditional row in[(L-aI)/(1-aI),U/(1-aI)],full upper U/(1-aI)',contract,['C02','C10_640','C34'],['E10','E11','E14'],'Unconditional row bounds supplied by C34; I may correlate column packages; displayed endpoints certified by exact ratios')
add('C36','Conditional public-seed corollary and reduced migration premises','§7.3、§7.5、附录E.9','A=g(Zpub) fixed first; each supported Zpub conditional experiment satisfies frozen contract','Average every supported seed (or a.e. regular conditional law); fixed-A bounds, initial and I-conditioned display bounds retained',contract+['Given every relevant Zpub value, subsequent raw chi and algorithm obey frozen contract'],['C29','C35'],['E10','E11','E12'],'Public A uniformity/PRG/entropy/distance responsibility removed for new bound; old tighter uniform number still needs its distribution basis; secret seed law and arithmetic remain')
add('C37','Current author-artifact mapping status','§7.4–7.5、HUMAN_REVIEW_ENTRY §6','6 reported author UE profiles; authenticated artifact unavailable','All6 author overall model mappings UNRESOLVED; current WAITING_FOR_AUTHOR_ARTIFACT',[],['C36'],['E12'],'No author UE execution/message-checked trace; upstream KEM source is separate; no hypothetical program differences attributed to author')
m['claims'][-1]['evidence_status']='WAITING_FOR_AUTHOR_ARTIFACT'
add('C38','Fixed-A review identity and current replay provenance','附录C、E.10、REVISION_AND_READINESS §3','E11 historical385 checks and E14 current385 replay','Only actual identity/exposure and execution counts; exact backend ID null',[],[],['E11','E14'],'No human/cross-model/blind/formal certification or independent error-process attestation')
m['claims'][-1]['evidence_status']='VERIFIED_PROVENANCE_SCOPE'
claims={c['id']:c for c in m['claims']}
def closure(id):
 seen=set()
 def visit(k):
  if k in seen:return
  seen.add(k)
  for d in claims[k].get('dependencies',[]):visit(d)
 visit(id);return sorted(seen)
m['main_result_dependency_audit']={name:{'root_claim':root,'transitive_claim_dependencies':closure(root),'semantic_distribution':'chi640','depends_on_chi976':False} for name,root in [('A','C09'),('B_uniform_Setup','C25a'),('B_fixed_A','C29'),('B_public_seed','C36')]}
for name,data in m['main_result_dependency_audit'].items():assert 'C10_976' not in data['transitive_claim_dependencies'],name
m['fixed_A_review_identity']=review['identity']
m['implementation_model_migration']={'status':'WAITING_FOR_AUTHOR_ARTIFACT','historical_mapping':rec(IMPL/'IMPLEMENTATION_MODEL_MAPPING.md'),'author_artifact_verdict':rec(IMPL/'VERDICT.json'),'new_fixed_A_public_A_distribution_responsibility_removed':True,'uniform_Setup_tighter_number_distribution_basis_still_required':True,'secret_noise_and_actual_algorithm_responsibility_retained':True,'config_mappings':load(IMPL/'VERDICT.json')['author_config_mappings'],'author_UE_message_checked_traces':0}
for config in m['implementation_model_migration']['config_mappings']:
 config['result_B_uniform_Setup_transfer']=config['result_B_transfer']
 config['result_B_fixed_A_transfer']='UNRESOLVED'
 config['numeric_reference_comparison_to_B_fixed_A']=config['numeric_reference_comparison_to_B']
 config['public_A_distribution_basis_required_for_fixed_A_bound']=False
 config['remaining_fixed_A_basis']='Authenticated author source; same A across generations; raw chi joint law conditional on public seed or finite-loss transfer; formulas/filtering/Ord/arithmetic'
m['inherited_erratum_impact_by_claim_v21']=m.pop('erratum_impact_by_claim')
m['erratum_impact_by_claim']=[{'claim_id':c['id'],'depends_on_chi976':('C10_976' in closure(c['id'])),'current_revision':'Fixed-A additions and A/B use chi640; prior976 corrected display/certificate preserved'} for c in m['claims']]
m['v2_2_correction_ids']=['V22-01','FA1','FA2','FA3','FA4','FA5','FA-I','FA-SEED','E1-H73','V22-MODEL','V22-REVIEW','V22-SEAL']
m['correction_ids']+=m['v2_2_correction_ids']
dump(OUT/'CLAIM_EVIDENCE_MATRIX.json',m)

execution={'schema':'frodo-fi-v22/replay-execution/1','date_asia_shanghai':'2026-11-11','record_basis':'Two observed exec_command completions in this author-revision session, both exit_code0; output JSON and fingerprints read after completion','python':platform.python_version(),'historical_scripts_executed':0,'runs':[{'command':'python -X utf8 '+str(OUT/'certificates/compute_fixed_A.py'),'script':rec(OUT/'certificates/compute_fixed_A.py'),'source':rec(FA/'evidence/compute_fixed_A.py'),'input':{'exact_mass':[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1],'denominator':65536,'n':640,'D':15,'q':32768,'H_threshold':450,'H_acceptance_exponent':73,'R2_threshold':3500,'R2_acceptance_exponent':27,'Taylor_degree':24,'exponential_ceil_bits':64,'power_ceil_bits':80},'exit_code':0,'output':rec(OUT/'FINITE_CERTIFICATES.json'),'output_byte_equal_historical':(OUT/'FINITE_CERTIFICATES.json').read_bytes()==(FA/'FINITE_CERTIFICATES.json').read_bytes()},{'command':'python -X utf8 '+str(OUT/'certificates/recompute_certificates.py'),'script':rec(OUT/'certificates/recompute_certificates.py'),'source':rec(REVIEW/'evidence/recompute_certificates.py'),'input':rec(OUT/'FINITE_CERTIFICATES.json'),'exit_code':0,'checks':385,'all_passed':True,'output':rec(OUT/'evidence/RECOMPUTED_CERTIFICATES.json'),'output_byte_equal_historical':(OUT/'evidence/RECOMPUTED_CERTIFICATES.json').read_bytes()==(REVIEW/'evidence/RECOMPUTED_CERTIFICATES.json').read_bytes()}],'H_tail_direct_integer_check':True,'H_tail_max_exponent':73,'R2_tail_max_exponent':27,'initial_coordinate_max_exponent':138,'all_exact_endpoints_unchanged':True,'cryptographic_samples_generated':0,'Monte_Carlo_runs':0}
assert all(r['output_byte_equal_historical'] for r in execution['runs'])
dump(OUT/'evidence/REPLAY_EXECUTION.json',execution)
print(json.dumps({'draft_bytes':(OUT/'CRYPTOANALYSIS_DRAFT.md').stat().st_size,'claims':len(m['claims']),'patch_blocks':len(blocks),'certificate_matches':True,'review_replay_matches':True}))
