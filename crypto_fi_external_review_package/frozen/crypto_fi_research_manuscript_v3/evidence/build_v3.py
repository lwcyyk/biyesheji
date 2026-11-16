"""Source-bound document patches and machine-claim integration for v3."""
from pathlib import Path
from fractions import Fraction as F
import copy,difflib,hashlib,json,re
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_research_manuscript_v3';OLD=BASE/'crypto_fi_research_manuscript_v2_2'
PROFILE=BASE/'crypto_fi_official_profile_correctness';REVIEW=BASE/'crypto_fi_official_profile_review'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sh(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def rd(x):return F(int(x['numerator']),int(x['denominator']))
def enc(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def frac(x):return f"{x['numerator']} / {x['denominator']}"
identity=dict(status='INFORMED_AUTHOR_REVISION_PARAMETRIC_PROOF_INTEGRATION_AND_STAGE_HANDOFF',description_zh='知情作者修订、参数化证明整合与阶段交接',author_proofs_numerical_targets_prior_positive_reviews_visible=True,declared_model_family='Codex based on GPT-6 per current developer context',exact_backend_model_id=None,exact_weights_version=None,model_error_process_independence_established=False,new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,formal_proof_assistant_used=False,calibration='NOT_CALIBRATED')
cert=load(OUT/'certificates/OFFICIAL_PROFILE_CERTIFICATES.json');oldm=load(OLD/'CLAIM_EVIDENCE_MATRIX.json');review=load(REVIEW/'REVIEW_VERDICT.json')
old=(OLD/'CRYPTOANALYSIS_DRAFT.md').read_text(encoding='utf-8-sig');t=old;ops=[]
def replace(a,b,purpose):
 global t
 assert t.count(a)==1,(purpose,t.count(a));t=t.replace(a,b)
 ops.append(dict(purpose=purpose,old_text_sha256=sh(a),new_text_sha256=sh(b),old_text=a,new_text=b))
def para(prefix,new,purpose):
 found=[x for x in t.split('\n\n') if x.startswith(prefix)];assert len(found)==1,(prefix,len(found));replace(found[0],new,purpose)
replace(t.splitlines()[0],'# FrodoPKE型可更新加密的来源隐藏与可靠性密码分析：共同正确族、三组官方参数及条件安全边界','C1标题统一两条主线')
para('研究稿v2.2，','研究稿v3，2026-11-11（Asia/Shanghai）。身份：知情作者修订、参数化证明整合与阶段交接（INFORMED_AUTHOR_REVISION_PARAMETRIC_PROOF_INTEGRATION_AND_STAGE_HANDOFF）。本版整合640、976、1344三组官方参数的一次更新可靠性及最新定向复核C1—C6；CF-1来源隐藏攻击、精确LWE前提审计与INC976勘误按各自证据范围承继。冻结对象为DOI **10.46298/fi.14425**、arXiv:2410.03948v4打印算法。','版本身份')
replace('两个主结果仅依赖χ640。','该次勘误时的CF-1与640结果仅依赖χ640；v3新增976可靠性使用已更正χ976，1344使用官方勘误后的χ1344。','INC976影响随新主张更新')
para('> **v2.2修订说明。**','> **v3修订说明。** §7以共同判据与三参数统一定理组织可靠性主线；附录D/E保留640特化证明，新增附录F参数化完整推导与976/1344实例、附录G全平移覆盖及精确分数选择器。C1—C6逐项闭合，来源事件ε与解码正确事件分开引用。修订、阶段裁决和外部重开条件见[REVISION_AND_READINESS.md](D:/毕业设计/crypto_fi_research_manuscript_v3/REVISION_AND_READINESS.md)。','C1-C6版本说明')
para('对FI打印算法配官方640数值参数n=640、','对FI打印算法配官方640、976、1344三组数值参数，在同A两代、给定A后精确独立官方χ、既定n列Ord、一次诚实未筛选TG/Upd及官方半向上Decode合同内，任意预先固定合法消息的初始完整失败率分别≤2^-132、2^-193、2^-246，消息长度分别128、192、256位。对每个在全部相关原始χ之前固定的公开矩阵A，更新完整正确率分别≤0.005043360、0.078020625、0.206115312，即完整错误率分别≥99.4956640%、92.1979375%、79.3884688%。额外对独立均匀全矩阵Setup平均，完整正确率分别≤0.000030345、0.017137631、0.082813443，错误率分别≥99.9969655%、98.2862369%、91.7186557%。全部显示更新端点在条件于初始完整消息已正确时保持。统一条件行矩判据处理共享钥匙与token依赖，976/1344以完整全平移位重量PGF、真实分布和全频率有向证书取得各自有限结论。','C1摘要三尺寸及量词')
replace('本文贡献为具体构造的来源隐藏失败、声明模型中的可靠性概率、公开矩阵量词扩展及迁移前提缩减，并附证明范围审计。','本文贡献为具体构造的来源隐藏失败、三组官方配置的一步可靠性分析、参数化证明与全平移PGF证书、公开矩阵量词扩展及迁移前提缩减，并附证明范围审计。','C1摘要贡献')
para('本文给出两项主要结果。','本文给出两条主线。A：在同一CF-1共同正确参数族中，原游戏支撑判定、逐固定A的真实fresh界及付费轮换放大，得到最长n次更新逐样本正确且≤3n+1次调用取得Δ→1。B：对三组官方数值参数，统一真实残差、条件列包、2n系数律、绝对Fourier矩、弦线/Jensen及初始事件比率，分别认证逐固定A和均匀Setup的一次更新高错误率。976/1344以全部65536平移的位重量PGF最大化认证超过n的H阈值1477、1644，配合各自R₂、频率与1344真实奇偶偏差；640保留原更紧数值与完整特化证明。公开矩阵量词扩展解除固定A数字的公共A生成器分布责任，秘密噪声、实际算法和机器算术继续按工件核准。','C1贡献覆盖')
replace('具体增量为FI真实残差的条件分解、完整频率证书与一次更新概率结论。','具体增量为FI真实残差的条件分解、三尺寸全频率证书，以及976/1344完整平移PGF在具体实例中的应用。','方法归属及对象增量')
replace('本轮固定A扩展新增检索为0，其方法归属仍为上述成熟工具。','976/1344作者包[E15]另记录2026-11-11六条定向查询及题录核对；本版整合新增联网检索0，其原始返回范围与全球优先权分别保留。','最新先例记录范围')
para('截至2026-11-10的已封存应用与发表影响审计','应用优先权沿用[E13]截至2026-11-10的实际审计，并补充[E15]于2026-11-11登记的六条定向查询回执；在这些实际核读与返回范围内，同FI对象、相同合同的完整等价A/B命题直接先例尚未定位。最强已核方法近邻仍为KLR2019公开token一致性及官方Frodo基础PKE失败分析。参数化弦线是640论证的直接抽象；全平移最大化采用成熟有限概率工具。全球优先权、Nishimaki扩展版与CJL逐版本对应继续待外部核准。本版联网检索新增0。','优先权证据截止及限度')
para('另一项结果具有两个最强量词版本：','可靠性主线的最强引用为§7.3定理OFFICIAL-1：在各自官方参数、精确χ联合律和一次未筛选更新合同内，对每个预先固定A，640/976/1344完整错误率分别至少99.4956640%、92.1979375%、79.3884688%；均匀全矩阵Setup下分别至少99.9969655%、98.2862369%、91.7186557%。相应初始完整失败≤2^-132、2^-193、2^-246，I条件下显示更新端点保持。CF-1增长D/q与固定官方参数行为分别由其自己的正确性和概率证明承担。','最强三参数引用')
para('全局A∈R_q^(n×n)在全部相关原始χ抽样前固定，','全局A∈R_q^(n×n)在全部相关原始χ抽样前固定，给定A后χ坐标及调用保持声明的精确独立乘积律。FI.Setup原样均匀选择A；§§3–6攻击和§7.3三尺寸固定A可靠性各对每个A成立，可在逐公共seed合同下平均。§7.3均匀Setup的更紧数字另平均独立均匀全矩阵A，其H公平位论证见附录D/F.11。固定A的640用χ平移非零坐标PGF，976/1344用全平移位重量PGF，见附录E/F.8。初始残差消去A，三尺寸初始正确性均逐A成立。每代钥匙为','C4量词合同')
# Replace section 7.2–7.5 as one explicitly authorized, source-bound block.
a=t.index('### 7.2 ');b=t.index('## 8. 精确LWE前提',a)
replace(t[a:b],(OUT/'evidence/section7.md').read_text(encoding='utf-8')+'\n','C1-C6共同判据与三参数正文')
para('本文保持**具体UE来源隐藏密码分析与证明审计核心候选**','本文的阶段定位为**已发表UE构造的来源隐藏密码分析与三组官方参数可靠性分析**，附条件安全前提审计。A/B各有精确对象、量词、自含证明和有限证书，支持独立密码分析短文或毕业论文核心章节的实质内容判断；领域贡献强度、方法应用新颖性及投稿适配仍交人工密码学判断。本版加入参数化判据、全平移覆盖及三尺寸理想配置的闭合，程序映射依工件继续核准。','阶段贡献与论文载体')
para('原PDF身份缺项的作用已分开：','原PDF身份缺项继续各有作用：CJL影响方法引文的逐版本认证，自含附录A仍可核；Nishimaki扩展版影响FI继承/归约来源；作者UE程序影响软件和性能实例迁移。当前已识别的模型内核心未闭合证明步骤为0，三尺寸一次更新高错误率已闭合；更多更新深度、精确跨行联合概率、实际软件迁移、全球优先权及条件安全定理的非空困难前提各按实际证据留项。','C2旧可靠性留项闭合')
research='''### 10.4 阶段裁决、继续研究价值与外部交接

理论阶段裁决为**THEORETICAL_RESULTS_INTEGRATED_AND_READY_FOR_HUMAN_CRYPTOGRAPHIC_REVIEW**。共同正确族的原游戏攻击与三组官方尺寸的一次更新高错误率，已在明确打印/类型/独立采样合同内完成。9196项算术重建、3194项作者核对和本版副本重放支持有限不等式；人工、跨模型及模型错误过程独立性认证按实际记录为0。具体业务系统与基础FrodoKEM各有其对象及工程证据，本稿的配置性结论首先适用于所列FI数学实验。

收紧数值可改进风险刻画，特别是1344的低频与全区间八阶弦线较松；当前高错误率分类已成立，进一步数值工作的贡献取决于实际收紧幅度。一个明确精度研究对象是好环境内Pr(p(V)>τ|𝓑)≤ε_τ的证书（π₀≤τ<1），它将弦线斜率降为Στ^(k−1−j)π₀^j并加入ε_τ。该引理尚待证明，当前结论使用τ=1。

更多更新深度与token复用将扩展使用范围，需研究迭代父密文与旧token/钥匙依赖下的新联合律；一次更新定理的诚实父合同分别核准。精确64坐标概率需要跨行共享钥匙与TG的联合矩或条件结构，能改进成功率估计；当前完整上界由指定行包含关系已经足够支撑三组失败裁决。这些问题提升精度或扩展对象，保持与已完成命题的依赖边界。

| 最小外部材料 | 到位后的核验步骤 | 能改变的裁决 |
|---|---|---|
| 论文/作者/机构认证的UE commit/archive、配置与依赖 | 核归属和不可变指纹；静态对应参数、同A、原始随机流、TG/Upd、Ord和机器算术 | 三尺寸数学模型能否迁移到作者软件；各配置MAPPED/DIFFERS/UNRESOLVED |
| 一条含原消息及初始/更新后消息比较的未筛选轨迹，附随机重放与失败记录 | 核入口、代次/token、输出、筛选/异常与分母；按后续授权复现 | 具体程序路径及正确性事实；概率责任继续由模型或有限损失承担 |
| 六配置与原100次五操作计时日志 | 对应预处理、缓存、计时窗口、消息检查及分母 | 原性能表的实际对象和可靠性解释 |
| 人工审阅意见，指出明确式子/条件或给接受范围 | 优先核原游戏/CF-1、判据与全平移/频率链、精确LWE前件及归约 | 数学结论可信范围、贡献定位与发表影响 |
| 带版本日期/哈希的Nishimaki2024扩展版、CJL原PDF或同对象先例 | 核完整命题、权限、参数/采样与可直接推出关系 | 归约继承、引文版本与应用优先权 |

下一项最能改变现实适用范围的输入是认证作者UE工件及所选配置的消息比对轨迹。下一项决定论文论证与贡献评价的外部判断是[HUMAN_REVIEW_ENTRY.md](D:/毕业设计/crypto_fi_research_manuscript_v3/HUMAN_REVIEW_ENTRY.md)的三个具体人工问题。

'''
replace('## 附录A　',research+'## 附录A　','阶段裁决与重开条件')
replace('ε是来源区分中真实fresh误接受事件的上界，976的解码可靠性仍属于§7.4的独立问题。','ε是来源区分中真实fresh误接受事件的上界；976/1344的更新Decode可靠性由§7.3定理及各自证书另行认证。最新复核和本版副本均重建两组完整64重整数卷积与ε，分别核准2^-1118、2^-1532。[E16,E17]','C2来源事件与解码留项')
replace('640/1344沿用原卷积及概率证据，同时完成上述输入一致性检查。','当时640/1344沿用原卷积证据；最新参数复核与本版另重放976/1344来源事件卷积，640继续沿用其已封存卷积。三组解码可靠性则见§7.3及附录D—G。','当前与历史重算范围')
replace('[CLAIM_EVIDENCE_MATRIX.json](D:/毕业设计/crypto_fi_research_manuscript_v2_2/CLAIM_EVIDENCE_MATRIX.json)','[CLAIM_EVIDENCE_MATRIX.json](D:/毕业设计/crypto_fi_research_manuscript_v3/CLAIM_EVIDENCE_MATRIX.json)','当前机器入口')
appendix_c='''**976/1344定向复核及v3整合。** [E16]准确登记AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW；作者证明、数值目标和旧正面审阅均可见。9196项具名算术比较、作者脚本副本重放及3194项核对按其原记录引用；代码路径的算术重建与模型错误过程独立性分别登记。C1—C6为旧稿采用/呈现修正，核心PROVED_UNDER_STATED_MODEL。v3[E17]重放字节相同的生成器/核对器/重建器副本，9196与3194项通过、整份作者证书匹配，并复算两组来源事件。精确后端ID/权重均按可见记录为null；本版新增独立、人工、跨模型、盲审、子代理及证明助手审阅均为0。当前身份为知情作者修订、参数化证明整合与阶段交接。'''
para('**固定A定向复核与v2.2整合。**','**固定A定向复核与v2.2整合（历史执行）。** [E11]登记AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW，会话01a1c652-ba78-71a0-b293-a09d61f26039；作者证明、旧正面审阅和目标均可见。FA1—FA5、逐A初始PGF、I条件化与公开seed推论通过，原385项检查与v2.2[E14]加固副本385项重放分别封存。H尾断言由70改73，端点影响0。该两次历史执行各自引用，v3本轮的640核对限于9196项中的C与U特化及原证书指纹。精确后端/权重和模型错误过程独立性按历史记录保留，人工等新增认证计数各按原身份。','640历史385项执行归属')
replace('**数据可用性与研究声明。**',appendix_c+'\n\n**数据可用性与研究声明。**','E16与当前实际身份')
para('**数据可用性与研究声明。**','**数据可用性与研究声明。** 本版五份核心文件、三尺寸证书、完整平移映射/代表比较、当前标量副本和重放记录由MANIFEST固定。历史原件保持只读。研究对象为公开算法及精确理想分布，本轮执行为确定性有限数学和文档/指纹核对。人工署名、CRediT、利益冲突及资助仍由责任作者按事实填写。旧业务材料只采用确认合同与工程报告；本轮原生服务操作、密码机制实现及随机实验为0。','数据可用性三尺寸')
replace('## 附录D　640一次更新概率链的完整可复核推导\n','## 附录D　640均匀Setup的特化证明\n\n本附录保留640已封存的具体概率证明与精确常数，统一记号及一般判据见§7.2、附录F。这里的计算执行沿用[E5—E8]及v2.2记录，当前三尺寸副本重放另见附录G。\n','640旧证据执行范围')
replace('## 附录E　逐固定公开矩阵的640可靠性推导与有限证书\n','## 附录E　逐固定公开矩阵的640可靠性推导与有限证书\n\n本附录保留640逐A特化。原385项及H73加固属于[E11,E14]历史执行；v3保留对应证书字节，并在9196项重建中核对640判据特化，当前记录见[E17]及附录G。\n','640固定A历史执行范围')
start=t.index('### E.10 ');end=t.index('## 参考文献',start)
replace(t[start:end],'''### E.10 640证书与实际执行归属

本版[640_FIXED_A_CERTIFICATES.json](D:/毕业设计/crypto_fi_research_manuscript_v3/certificates/640_FIXED_A_CERTIFICATES.json)为v2.2证书的逐字节副本，保留χ、ν、H/R₂/初始尾、全频率及Z/U/L/条件化分数。H尾直接73指数加固及385项重放按v2.2[E14]引用，原始定向审阅[E11]为AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW。v3未重跑这组385项，当前9196项脚本核对了640的C与U特化。三尺寸最新核对与身份见附录G及[E16,E17]。

公开矩阵量词扩展及迁移前提缩减继续有效；共同工具归属与三尺寸贡献定位见§1.2、§10.4。

''','清楚区分640历史385项与v3执行')

# The new appendix is the full scientific proof, not just a pointer to it.
proof=(PROFILE/'PARAMETRIC_CORRECTNESS_BOUND.md').read_text(encoding='utf-8')
f=proof[proof.index('## 1. 参数范围'):proof.index('## 12. 直接推论')]
f=re.sub(r'^## (\d+)\. ',lambda m:'### F.'+m[1]+' ',f,flags=re.M)
f=re.sub(r'^### (\d+\.\d+) ',lambda m:'#### F.'+m[1]+' ',f,flags=re.M)
for i in range(32,0,-1):
 f=f.replace('\\tag{'+str(i)+'}','\\tag{F'+str(i)+'}').replace('('+str(i)+')','(F'+str(i)+')')
f=f.replace('C_k按连续延拓取k','C_k由有限和直接取k')
f=f.replace('F≥1时上界按(F12)截为1。','F≥1时由F−1=C_k[Z−(1−π₀)]知π₀+Z≥1，故U_J=1，原始U_raw≥1。')
f=f.replace('Z\\le\\pi_0\\sum_{t=1}^{q-1}R_t^n.','Z_{\\rm adopt}=\\pi_0\\sum_{t=1}^{q-1}R_t^n.')
f=f.replace('即可收紧(F14)','即可收紧(F14)')
f=f.replace('[官方issue35回复](https://github.com/microsoft/PQCrypto-LWEKE/issues/35#issuecomment-2504969837)','[官方issue35回复](https://github.com/microsoft/PQCrypto-LWEKE/issues/35#issuecomment-2504969837) [S10]')
f=f.replace('本轮','本节')
f=f.replace('初始已正确事件I留到§6用事件比率处理。','初始已正确事件I留到F.5用事件比率处理，初始PGF见F.6。')
f=f.replace('在§1—3合同','在F.1—F.3合同').replace('由此取得§10的额外平均界','由此取得F.10的额外平均界')
f='''## 附录F　参数化概率链与976/1344的完整有限实例证明

以下从[E15]参数化证明整合，落实[E16]的有限和、端点及量词要求。本附录自含共同推理与两组实例；640的同一结构在附录D/E按自己的环境常数特化。公式(F1)—(F32)在本附录内编号。δ、Z、π₀与n每次按所列实例取值，执行身份与计算成本另见附录G。

'''+f
f+='''
### F.12 端点、条件化及完整下界的补充

C_k首先是有限和，π₀=1时C_k=k，π₀=0时C_k=1。δ=1的通用区间为[0,1]；恒等式F−1=C_k[Z−(1−π₀)]和C_k>0说明F≥1时π₀+Z≥1，故U_J=1；Z≥π₀时解析下界为0。B=0的唯一标签和B=D的正确集合{0}按F.4.2直接处理。n,D,m̄,k≥1、0≤B≤D为一般分解域；FI打印实例另携带8∣n。χ=δ₀使实际正确率为1，说明非平凡高错误率依赖具体Z证书，而非仅依赖维度合同。

指定行可用全零U₀/F₀/R的3n个条目见证；完整消息使用全部m̄行的3m̄n个条目见证。官方m̄=8时γ976=(5639/32768)^23424、γ1344=(9143/32768)^32256，同时保证I∩K，给原实验及I条件实验的完整正下界。行Jensen下界只用于J。四组新增S/J区间与条件分数见§7.3及附录G，不对跨行作乘积假设。

所有逐A解除条件依次保持同一固定矩阵：平移最大PGF对每个A,u成立，随后对u积分；R₂用给定A后的乘积律；好事件𝓑可测，剩余U/F律保留；从V到𝓑用真实2n系数律；好环境包络对每个支持内环境同常数，从𝓑到A用坏预算；完整消息用事件包含；初始I条件最后用比率。均匀Setup分支另外对独立均匀A平均，公共seed分支逐seed满足合同后平均。

'''

# Unified certificate selectors include exact conditional fractions, not decimal claims alone.
profiles={}
legacy=oldm['probability_results'];fa640=load(OUT/'certificates/640_FIXED_A_CERTIFICATES.json')
profiles['640']=dict(parameters=dict(n=640,D=15,q=32768,mbar=8,nbar=8,B=2,message_bits=128,support_radius=12,decode_half_width=4096,pi0=enc(F(1,4))),initial=dict(full_failure_power=132,coordinate_failure_power=138,tilt=enc(F(21,20))),fixed_A=dict(A_quantifier='EVERY_PRE_FIXED_A',averages_A=False,H_min=450,R2_min=3500,adopted_delta=fa640['environment']['adopted_delta'],Z=fa640['Z'],row_correct_lower=fa640['row_lower_Jensen'],row_correct_upper=fa640['row_and_full_correct_upper'],full_correct_upper=fa640['row_and_full_correct_upper'],conditioned_on_initial=dict(row_correct_lower=fa640['initial_correct_conditioned_row_lower'],row_correct_upper=fa640['initial_correct_conditioned_row_and_full_upper'],full_correct_upper=fa640['initial_correct_conditioned_row_and_full_upper']),display=dict(row_lower='0.0000135117',row_full_upper='0.005043360',full_error_percent_lower='99.4956640%'),row_lower_version='Legacy weaker global Jensen; general per-good-environment Jensen lower is at least as large',source=rec(OUT/'certificates/640_FIXED_A_CERTIFICATES.json')),uniform_Setup=dict(A_quantifier='UNIFORM_FULL_MATRIX_SETUP_AVERAGE_ONLY',averages_A=True,H_min=4500,R2_min=3500,adopted_delta=enc(F(1,2**25)),Z=legacy['Z_star']['exact'],row_correct_lower=legacy['row_exact_lower'],row_correct_upper=legacy['row_exact_upper'],full_correct_upper=legacy['row_exact_upper'],conditioned_on_initial=dict(row_correct_lower=legacy['conditional_exact']['row_lower']['exact'],row_correct_upper=legacy['conditional_exact']['row_upper']['exact'],full_correct_upper=legacy['conditional_exact']['row_upper']['exact']),display=dict(scalar_lower='0.2499054',scalar_upper='0.2500946',row_lower='0.0000152532',row_full_upper='0.000030345',full_error_percent_lower='99.9969655%'),row_lower_version='Legacy weaker global Jensen',source=rec(OUT/'certificates/640_UNIFORM_RESULTS.json')))
u640=profiles['640']['uniform_Setup']
u640['scalar_correct_lower']=legacy['coordinate_exact_lower'];u640['scalar_correct_upper']=legacy['coordinate_exact_upper']
u640['conditioned_on_initial']['scalar_correct_lower']=legacy['conditional_exact']['coordinate_lower']['exact']
u640['conditioned_on_initial']['scalar_correct_upper']=legacy['conditional_exact']['coordinate_upper']['exact']
u640['scalar_proof_selector']='AppendixD.2 dedicated coordinate certificate;epsilon=1/10600+2^-46+2^-22;distinct from row Z/delta'
for n,p in cert['profiles'].items():
 profiles[n]=dict(parameters=p['parameters'],distribution=p['distribution'],difference_law=p['difference_law'],initial=dict(full_failure_power=p['initial']['full_failure_power_of_two'],coordinate_failure_power=p['initial']['coordinate_tail_certificate']['exponent'],tilt=p['initial']['tilt'],exact_initial_certificate=p['initial']),source=rec(OUT/'certificates/OFFICIAL_PROFILE_CERTIFICATES.json'))
 for mode in ['fixed_A','uniform_Setup']:
  profiles[n][mode]=copy.deepcopy(p[mode]);profiles[n][mode]['averages_A']=(mode=='uniform_Setup')
  profiles[n][mode]['certificate_selector']=f'profiles.{n}.{mode}'
  profiles[n][mode]['initial_correct_conditioning_selector']=f'profiles.{n}.{mode}.conditioned_on_initial'
dump(OUT/'certificates/UNIFIED_RESULT_SELECTORS.json',dict(schema='frodo-fi-v3/unified-result-selectors/1',profiles=profiles,scope='Exact model-specific endpoints and selectors; display values apply before and after conditioning on initial full correctness'))

g='''## 附录G　全平移覆盖、精确分数、计算成本与重放身份

### G.1 三尺寸精确分数选择器

[UNIFIED_RESULT_SELECTORS.json](D:/毕业设计/crypto_fi_research_manuscript_v3/certificates/UNIFIED_RESULT_SELECTORS.json)按profiles.n.mode统一登记参数、δ、Z、初始α及原/条件端点；mode为fixed_A或uniform_Setup。976/1344的原始逐点证书为[OFFICIAL_PROFILE_CERTIFICATES.json](D:/毕业设计/crypto_fi_research_manuscript_v3/certificates/OFFICIAL_PROFILE_CERTIFICATES.json)，选择器profiles.n.mode.full_correct_upper与profiles.n.mode.conditioned_on_initial.full_correct_upper。640的原始选择器在统一文件中另绑定各自来源。以下分数为完整成功率采用的行上界。

| 配置/量词 | 原实验精确U | 条件于I的精确U/(1−α) |
|---|---|---|
'''
for n,p in profiles.items():
 for mode in ['fixed_A','uniform_Setup']:
  v=p[mode];g+=f"| {n} / {'逐A' if mode=='fixed_A' else '均匀Setup平均'} | {frac(v['full_correct_upper'])} | {frac(v['conditioned_on_initial']['full_correct_upper'])} |\n"
g+='''
每项显示上界由条件精确分数向外取整；显示错误下界为其补。S/J的完整下端分数保存在同一mode及conditioned_on_initial对象，1344的0下端属于解析包络。三组α分别2^-132、2^-193、2^-246，均逐A成立；均匀Setup条件化先对A平均，再作事件比率。原实验和I条件实验各使用自己的精确分数。

### G.2 全部平移到代表的覆盖与最大值证明

976与1344各对a=0,…,65535构造17维向量v_a(j)=Σ_x w_x1{wt₁₆(a+x mod65536)=j}。给定z=a_H/b_H，以共同分母65536·b_H^16计算整数N_a=Σ_jv_a(j)a_H^jb_H^(16−j)。只合并完全相同的向量；每个不同向量均精确比较其N_a与全局最大值。

| 配置 | 映射及完整代表比较 | 代表数 | 唯一最大平移 | H阈值与含边界尾 |
|---|---|---:|---:|---|
'''
for n in ['976','1344']:
 root=OUT/'certificates/review/evidence';cover=load(root/f'PGF_FULL_COVERAGE_{n}.json');h=cert['profiles'][n]['environment']['fixed_A_H']
 g+=f"| {n} | [65536项映射]({(root/f'PGF_SHIFT_TO_REP_{n}.u16le').as_posix()})、[全部代表/最大差比较]({(root/f'PGF_FULL_COVERAGE_{n}.json').as_posix()}) | {cover['representatives']} | {h['maximizing_shifts'][0]} | {h['threshold']}，≤2^-40 |\n"
g+='''
映射按a顺序存little-endian uint16代表ID，字节偏移2a，各文件131072字节。每个代表记录id、first_shift、shift_count、全部17个重量分子、pgf_common_numerator与gap_to_max_numerator。全部ID覆盖、shift_count之和65536及映射往返均核对。完整平移顺序的N_a ASCII行流哈希也与原作者证书相同；每个最大差非负且最大平移唯一，因而给出g_H(z)的有限穷尽认证。两组最大向量完整列于F.8；全部映射和代表文件的大小/哈希由MANIFEST固定。

### G.3 参数化命题与有限计算成本

判据P是给定模型、δ及Z后的数学条件命题，其成立性由条件期望、凸性和有限Fourier恒等式证明。全平移证书的构造额外枚举q=2^D个平移，并非关于D的通用多项式算法。采用popcount表及向量去重时，字操作量级O(q(2sχ+1+D)+LD)，存储O(q+LD)，L≤q为不同向量数；比较整数位长O(log65536+D log b_H)，任意精度运算另计位成本。当前D=16，L分别1484、1000。频率证书覆盖q/2个正代表，实际低/中/高分组分别24、59；有理n次幂和大整数尾比较按其有限位长计费。

这些成本说明具体有限证书如何复核；当前理论未声称对任意增长D都以相同资源完成枚举。CF-1攻击/正确性定理有自己的参数及复杂度分析，有限枚举脚本只承担本节实例认证。

### G.4 执行记录、舍入与来源事件

本版未修改的作者生成器副本与核对器副本分别运行1次，核对器3194项通过，整份OFFICIAL_PROFILE_CERTIFICATES与历史原件逐字节相同。审阅重建器副本运行1次，9196项具名比较通过；与历史结果比较时仅排除seconds、total_seconds、enumeration_seconds等时钟字段，全部算术载荷相同。两个平移二进制文件字节相同、全部代表比较相同。来源事件脚本另重建976的1281和1344的769个64重卷积系数，并核准ε976≤2^-1118、ε1344≤2^-1532。该执行范围与全攻击游戏证明分别登记。

每个指数先用正Taylor倒数，再向上取64位；精确ν加权后，R_g^n向上取80位。剩余差值质量按1，全部频率覆盖，Nyquist保守多计一次；Taylor解析松弛与dyadic松弛均已进入Z。指数上包另经原复核脚本的交错区间方法比较。精确概率判断使用整数/有理数，浮点显示与时钟字段只供阅读。

复算在本版副本目录执行：

```powershell
python -X utf8 certificates/author/crypto_fi_official_profile_correctness/evidence/compute_profile_certificates.py
python -X utf8 certificates/author/crypto_fi_official_profile_correctness/evidence/verify_profile_certificates.py
python -X utf8 certificates/review/evidence/recompute_review.py
python -X utf8 certificates/review/evidence/verify_historical_relations.py
```

脚本依据的相邻输入副本已提供；审阅脚本的绝对来源路径仍读取固定历史字节，具体输入与来源哈希见[evidence/REPLAY_EXECUTION.json](D:/毕业设计/crypto_fi_research_manuscript_v3/evidence/REPLAY_EXECUTION.json)。正式封存后继续修改应写后续目录，复核人员可复制完整包重放。原历史脚本本轮执行0次，密钥/密文/token采样、Monte Carlo、LWE求解和候选密码机制实现均为0。

### G.5 新增审阅与作者整合身份

[E16]实际身份为AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW，作者证明、目标及旧正面审阅均可见；chat_id为01a1c8ef-6688-7b71-9943-f98a9c3ff068。其9196项算术重建、作者脚本重放3194项与原结果逐字节匹配按原记录引用。C1—C6呈现/采用修正已在v3落实，核心数学裁决PROVED_UNDER_STATED_MODEL。

本版[E17]为知情作者修订、参数化证明整合与阶段交接，重放同一脚本提供当前执行记录。原复核与当前整合均声明可见家族Codex基于GPT-6；精确后端ID、权重与作者轮后端对应为null。当前与原复核新增人工、跨模型、盲审、子代理、证明助手及模型错误过程独立性认证均为0，经验校准NOT_CALIBRATED。不同代码路径的算术重建与审阅错误过程独立性各自保留证据含义。

'''
replace('## 参考文献与固定研究记录',f+'\n'+g+'\n## 参考文献与固定研究记录','C3-C5参数化完整证明与可追溯全平移证书')
refs='''
- **[E15]** 参数化作者证明与976/1344实例：[PARAMETRIC_CORRECTNESS_BOUND.md](D:/毕业设计/crypto_fi_official_profile_correctness/PARAMETRIC_CORRECTNESS_BOUND.md)、[PROFILE_RESULTS_AND_SCOPE.md](D:/毕业设计/crypto_fi_official_profile_correctness/PROFILE_RESULTS_AND_SCOPE.md)及OFFICIAL_PROFILE_CERTIFICATES，2026-11-11；身份INFORMED_PARAMETRIC_PROBABILITY_RESEARCH_AND_DETERMINISTIC_FINITE_CERTIFICATE_CHECK。
- **[E16]** 最新定向复核：[MATHEMATICAL_REVIEW.md](D:/毕业设计/crypto_fi_official_profile_review/MATHEMATICAL_REVIEW.md)、[C1—C6修正文本](D:/毕业设计/crypto_fi_official_profile_review/CORRECTIONS_AND_MANUSCRIPT_IMPACT.md)、REVIEW_VERDICT、INPUT_AND_REVIEW_PROVENANCE及MANIFEST，2026-11-11。实际身份AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW；9196项重建、3194项作者脚本重放、全平移覆盖及来源事件复算，按其执行记录引用。
- **[E17]** v3知情作者整合与重放：[REVISION_AND_READINESS.md](D:/毕业设计/crypto_fi_research_manuscript_v3/REVISION_AND_READINESS.md)、[REPLAY_EXECUTION.json](D:/毕业设计/crypto_fi_research_manuscript_v3/evidence/REPLAY_EXECUTION.json)及本版MANIFEST，2026-11-11。C1—C6闭合，当前脚本副本3194及9196项通过；新增独立审阅0。
- **[S12]** Herman Chernoff. *A Measure of Asymptotic Efficiency for Tests of a Hypothesis Based on the Sum of Observations*. Annals of Mathematical Statistics23(4),493–507,1952，DOI[10.1214/aoms/1177729330](https://doi.org/10.1214/aoms/1177729330)。[Stanford原始技术报告目录](https://statistics.stanford.edu/technical-reports/measure-asymptotic-efficiency-tests-hypothesis-based-sum-observations)用于E15题录交叉核对；本版按该读取级别引用成熟指数界来源。
- **[S13]** Persi Diaconis. *Group Representations in Probability and Statistics*. IMS,1988，[出版社记录](https://doi.org/10.1214/lnms/1215467407)。E15题录级访问，引用有限群Fourier的成熟方法归属；所需公式在本稿自含证明。
'''
t=t[:t.index('<!--priority-scope:')]+refs+'\n<!--priority-scope: E13至2026-11-10；E15于2026-11-11六条定向查询按原回执；v3新增联网检索0；全球优先权待核。-->\n'
(OUT/'CRYPTOANALYSIS_DRAFT.md').write_text(t,encoding='utf-8')
(OUT/'evidence/MANUSCRIPT_REVISION.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),t.splitlines(True),fromfile=str(OLD/'CRYPTOANALYSIS_DRAFT.md'),tofile=str(OUT/'CRYPTOANALYSIS_DRAFT.md'))),encoding='utf-8')
blocks=[]
a=old.splitlines(True);b=t.splitlines(True)
for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
 if tag!='equal':blocks.append(dict(op=tag,v2_2_lines=[i+1,j],v3_lines=[k+1,l],old_sha256=sh(''.join(a[i:j])),new_sha256=sh(''.join(b[k:l]))))
dump(OUT/'evidence/MANUSCRIPT_PATCH_LEDGER.json',dict(schema='frodo-fi-v3/targeted-author-patch/1',authority='Current user explicitly authorizes C1-C6 adoption, three-profile unification, exact parameter/endpoint contracts and handoff; historical sources remain read-only',ARS_scope='Inline targeted-revision/source-integrity principles; deterministic exact replacements and diff, with no ARS schema authorization certificate claimed',baseline=rec(OLD/'CRYPTOANALYSIS_DRAFT.md'),target=rec(OUT/'CRYPTOANALYSIS_DRAFT.md'),operations=ops,changed_blocks=blocks,unchanged_appendix_A=old.split('## 附录A')[1].split('## 附录B')[0]==t.split('## 附录A')[1].split('## 附录B')[0],unchanged_attack_sections_3_to_6=old[old.index('## 3. '):old.index('## 7. ')]==t[t.index('## 3. '):t.index('## 7. ')]))

# Retain historical fields with explicit origin; introduce canonical v3 selectors.
m=copy.deepcopy(oldm);m['schema']='frodo-fi-claim-evidence-matrix/v3';m['version']='v3';m['date_asia_shanghai']='2026-11-11'
m['inherited_v2_2_identity']=m['identity'];m['identity']=identity;m['inherited_action_counts_v2_2']=m['action_counts']
m['action_counts']=dict(author_generator_copy_runs=1,author_verifier_copy_runs=1,author_checks=3194,review_reconstruction_copy_runs=1,review_named_comparisons=9196,source_event_relation_copy_runs=1,source_event_convolution_coefficients=[1281,769],cryptographic_samples=0,Monte_Carlo_runs=0,LWE_solver_runs=0,candidate_mechanism_implementations=0,historical_script_executions=0,new_web_searches=0,author_contacts=0,new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,formal_proof_assistant_runs=0)
m['core_proof_status']='A CF-1 and B all three official one-update profiles integrated under frozen ideal contracts. Latest mathematical core PROVED_UNDER_STATED_MODEL; C1-C6 adopted in v3. Human cryptographic review, actual author artifacts, exact FI reduction and global priority retain separate external conditions.'
m['manuscripts']='CRYPTOANALYSIS_DRAFT.md; REVISION_AND_READINESS.md; HUMAN_REVIEW_ENTRY.md'
m['official_profile_results']=profiles
m['canonical_probability_selector']='official_profile_results.<n>.<fixed_A|uniform_Setup>; legacy640 probability_results and fixed_A_probability_results retained as scoped historical payloads'
m['parametric_criterion']=dict(domain='n,D,mbar,k>=1; q=2^D;0<=B<=D;finite symmetric integer chi;FI printed domain additionally8 divides n',pi0='|D_correct|/q',Ck_first_definition='sum(pi0^j,j=0..k-1)',F='pi0^k+Ck*Z',U_J='(1-delta)*min(1,F,pi0+Z)+delta',L_J='(1-delta)*max(0,pi0-Z)^k',U_S='(1-delta)*min(1,pi0+Z)+delta',L_S='(1-delta)*max(0,pi0-Z)',conditioning='[max(0,(L-alpha)/(1-alpha)),min(1,U/(1-alpha))],alpha<1; full K uses row upper',endpoints=dict(pi0_zero='Exact success0,Ck1',pi0_one='Exact success1,Ck=k by finite sum',k_one='C1=1;row=coordinate',delta_one='Generic[0,1],exact pi endpoints retained',Z_ge_pi0='Generic Jensen lower0',F_ge_one='UJ=1;F-1=Ck*(Z-(1-pi0)),so pi0+Z>=1;Uraw>=1',B_zero='D_correct=full group,pi0=1',B_eq_D='D_correct={0},pi0=1/q',alpha_one='Need separate positive denominator',empty_sizes='k0/n0/D0 outside algorithm theorem;empty row may be defined separately'),full_PGF='g_H(z)=max_a E_chi[z^wt_D(a+X modq)]',cost='Full translation certificate costs at least q-shift enumeration; q=2^D. No universal polynomial-in-D enumeration claim.')
m['frozen_models']['OFFICIAL_ONE_UPDATE_PARAMETRIC']=dict(contract='Same A across two generations, pre-coins fixed message/row, exact raw chi coordinate/call product law conditional on A, Ord_n/Tensor matching, one honest unfiltered TG/Upd, official half-up Decode',profiles={n:p['parameters'] for n,p in profiles.items()},A_quantifiers=['EVERY_PRE_FIXED_A','UNIFORM_FULL_MATRIX_SETUP_AVERAGE_ONLY'],public_seed='Each relevant public-seed conditional experiment must obey entire frozen contract')
def source(id,files,**fields):m['source_registry'][id]=dict(files=[rec(x) for x in files],**fields)
source('V22',[OLD/x for x in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md','MANIFEST.json']],scope='Read-only v3 baseline; old attack, LWE and640 proof scopes retained')
source('E15',[PROFILE/x for x in ['PARAMETRIC_CORRECTNESS_BOUND.md','PROFILE_RESULTS_AND_SCOPE.md','OFFICIAL_PROFILE_CERTIFICATES.json','VERDICT.json','evidence/PUBLIC_PRECEDENT_SEARCH_RECEIPT.json']],identity='INFORMED_PARAMETRIC_PROBABILITY_RESEARCH_AND_DETERMINISTIC_FINITE_CERTIFICATE_CHECK',scope='Parametric proof, exact976/1344 instances, prior6-query receipt and mature-method bibliographic scope')
source('E16',[REVIEW/x for x in ['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md','REVIEW_VERDICT.json','INPUT_AND_REVIEW_PROVENANCE.json','MANIFEST.json','evidence/INDEPENDENT_RECOMPUTATION.json','evidence/AUTHOR_REPLAY_RESULT.json','evidence/PGF_FULL_COVERAGE_976.json','evidence/PGF_FULL_COVERAGE_1344.json','evidence/PGF_SHIFT_TO_REP_976.u16le','evidence/PGF_SHIFT_TO_REP_1344.u16le']],identity=review['identity']['status'],identity_record=review['identity'],core_status=review['core_mathematical_verdict'],historical_adoption_status=review['manuscript_adoption_status'],historical_adoption_status_preserved=True,v3_adoption='C1-C6_CLOSED',finite_validation=review['finite_validation'])
source('E17',[OUT/x for x in ['evidence/REPLAY_EXECUTION.json','certificates/UNIFIED_RESULT_SELECTORS.json','certificates/OFFICIAL_PROFILE_CERTIFICATES.json','certificates/review/evidence/INDEPENDENT_RECOMPUTATION.json','certificates/review/evidence/HISTORICAL_EVENT_RELATIONS.json']],identity=identity['status'],scope='Current byte-identical scalar copies replayed3194+9196; exact historical source-event convolutions; no new independent mathematical review')
m['source_registry']['S12']=dict(title='Chernoff1952, A Measure of Asymptotic Efficiency for Tests of a Hypothesis Based on the Sum of Observations',DOI='10.1214/aoms/1177729330',reading_scope='Bibliographic-only source check inherited from E15 receipt; DOI open failure retained; self-contained inequalities in manuscript')
m['source_registry']['S13']=dict(title='Diaconis1988, Group Representations in Probability and Statistics',DOI='10.1214/lnms/1215467407',reading_scope='Bibliographic-only publisher record inherited from E15; finite-group identities proved in manuscript')
m['source_registry_inheritance_note']='Historical source records retain their original semantic/execution scopes. Current reading and replay are in E15-E17; all adopted path/hash nodes checked. No new primary-source network retrieval or human review.'
claims={x['id']:x for x in m['claims']}
claims['C25a']['manuscript_location']='§7.3的640均匀Setup行、附录D、附录G.1'
claims['C29']['manuscript_location']='§7.3的640固定A行、附录E、附录G.1'
claims['C25b'].update(claim='Remaining depth/reuse/exact-full-message and software questions',precise_object='More updates, token reuse/selection, exact cross-row full64 probability and actual software;976/1344 frozen one-update reliability now proved',manuscript_location='§7.4–7.5、§10.4',limitations='No extrapolation beyond the three one-update ideal contracts; previous976/1344 one-update pending status superseded by C45-C50',source_ids=claims['C25b']['source_ids']+['E15','E16'])
claims['C25d'].update(claim='High-error reliability of all three official one-update ideal profiles',precise_object='640/976/1344 with separate fixed-A and uniform-Setup quantifiers',quantifiers='Every pre-fixed legal128/192/256-bit message; fixed-A errors>=99.4956640%,92.1979375%,79.3884688%;uniform-Setup errors>=99.9969655%,98.2862369%,91.7186557%;same displays under I',dependencies=['C25a','C29','C45','C46','C47','C48','C49','C50'],manuscript_location='§7.3–7.4、附录D–G',source_ids=claims['C25d']['source_ids']+['E15','E16'])
claims['C25p']['manuscript_location']='§2、§6.2、§7.2–7.5、附录D–G';claims['C25p']['precise_object']='Explicit three-profile A quantifiers;finite-sum Ck/endpoints;64/nu/n-power80;B0+t_maxW'
claims['C25c']['manuscript_location']='§7.5、§10.4';claims['C25c']['precise_object']='Authenticated author UE code/config, exact conditional secret-noise law, formulas/filtering/Ord and machine arithmetic for all6 reported profiles'
claims['C25c']['limitations']='All three mathematical numeric profiles covered; actual6 author mappings UNRESOLVED, WAITING_FOR_AUTHOR_ARTIFACT;message-checked author UE traces0'
claims['C36']['manuscript_location']='§7.5、附录F.11';claims['C36']['limitations']='This claim is the inherited640 public-seed corollary; all-three extension is C51. Public-A distribution responsibility removed for fixed-A numbers only.'
claims['C37']['manuscript_location']='§7.5、§10.4、人工入口';claims['C27']['source_ids']+=['E15','E16','E17']
def add(id,claim,loc,obj,quant,assumptions,deps,sources,lim,status='PROVED_UNDER_STATED_MODEL',dist=None):
 m['claims'].append(dict(id=id,claim=claim,manuscript_location=loc,precise_object=obj,quantifiers=quant,assumptions=assumptions,dependencies=deps,source_ids=sources,evidence_status=status,limitations=lim,semantic_distribution_inputs=dist or [],review_identity_and_scope='E16 actual AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW, prior positive reviews visible; E17 current informed author integration and scalar-copy replay; exact backend IDs null; new human/cross-model/blind/formal/independent-error-process certifications0'))
contract=['A fixed before all relevant raw chi coins, same A across two generations;conditional exact raw-coordinate/call product law','Pre-coins fixed message/row;Ord_n matched to Tensor_D;S/E n-by-k;one honest unfiltered TG/Upd;half-up Decode']
add('C39','Parameterized mixed-row criterion and clipped upper','§7.2、附录F.1–F.5','p_row=E[p(V)^k],Ck finite sum,F=pi^k+CkZ,UJ=(1-delta)min(1,F,pi+Z)+delta','Every fixed A and each good raw environment;generic finite symmetric chi',contract+['B-measurable good event;bad mass<=delta;each good environment E|p-pi|<=Z'],['C02'],['E15','E16'],'A nontrivial bound requires an actual instance Z;no universal high-error claim')
add('C40','All endpoint, coordinate and Jensen cases','§7.2端点表、附录F.4/F.12','pi0/1,k1,delta1,Z>=pi,F>=1,B0/BD,alpha1 and excluded empty sizes','Finite-sum Ck used at all pi;local-good-environment Jensen and scalar bounds',contract,['C39'],['E15','E16'],'Legacy640 lower is a valid weaker global-Jensen certificate;row lower remains row event')
add('C41','True residual, two layers,2n coefficient law and all-frequency mechanism','附录F.1–F.4、F.9–F.10','Raw column packets and true weighted T_B;Dt difference law;E|Phi|<=Dt^n','Every supported raw environment under each pre-fixed A',contract,['C02','C39'],['E15','E16'],'No conditioning on public outputs/rank/success;wraps retained')
add('C42','All-translation bit-weight PGF and finite cost','§7.3、附录F.8、G.2–G.3','gH(z)=max_a E[z^wtD(a+X modq)]','First fix A,u,then maximize each translation,then average u;bothD16 profiles enumerateall65536 shifts',contract,['C41'],['E15','E16','E17'],'q-linear enumeration is exponential inD;mathematical criterion conditional on certified Z is distinct from finite certificate cost',dist=['chi976','chi1344'])
add('C43','976 full shift-map and maximum certificate','附录F.8、G.2','65536 shifts,1484 representatives,unique maximizer4,z33/40,H1477','Every shift maps to an explicit17-coordinate mass vector;all representatives compared with nonnegative exact gaps',contract,['C42','C10_976'],['E15','E16','E17'],'D16 exact finite certificate;H inclusive tail<=2^-40',dist=['chi976'])
add('C44','1344 full shift-map, maximum and parity certificate','附录F.7–F.9、G.2','65536 shifts,1000 representatives,max2,z9/10,H1644;theta1/16384','Official correctedCDF,actual even/odd32770/32766;all maps/representatives compared',contract,['C42','C10_1344'],['S10','E15','E16','E17'],'No fair-parity replacement in uniform-Setup or Nyquist accounting',dist=['chi1344'])
for n,ids in [('976',('C45','C46','C47')),('1344',('C48','C49','C50'))]:
 p=cert['profiles'][n];fa=p['fixed_A']['display'];un=p['uniform_Setup']['display'];dist=['chi'+n]
 add(ids[0],n+' fixed-A one-update reliability','§7.3、附录F、G.1',f'official_profile_results.{n}.fixed_A',f'Every pre-fixed A and pre-coins fixed legal{p["parameters"]["message_bits"]}-bit message:full correct<={fa["row_full_upper"]},error>={fa["full_error_percent_lower"]}%;row/scalar intervals per exact certificate',contract,['C39','C40','C41',('C43' if n=='976' else 'C44')],['E15','E16','E17'],'K subset J;one update;exact full64 success not computed;software transfer unresolved',dist=dist)
 add(ids[1],n+' uniform-Setup one-update reliability','§7.3、附录F.11、G.1',f'official_profile_results.{n}.uniform_Setup',f'Average independent uniform full-matrix A and all honest coins:full correct<={un["row_full_upper"]},error>={un["full_error_percent_lower"]}%',contract+['Independent uniform full-matrix Setup;true all-u-even probability'],[ids[0]],['E15','E16','E17'],'Tighter numbers retain their own A distribution basis;not per-seed bounds',dist=dist)
 add(ids[2],n+' initial correctness and event-ratio conditioning','附录F.5–F.6、G.1',f'official_profile_results.{n}.initial and both conditioned_on_initial objects',f'Every A:initial full failure<=2^-{p["initial"]["full_failure_power_of_two"]};all displayed updates retain endpoints conditional on I',contract,[ids[0],ids[1]],['E15','E16','E17'],'Initial PGF2n product terms,64-coordinate union;conditional proof uses event ratios after unconditional chain;full lower separate gamma witness',dist=dist)
add('C51','All-three public-seed corollary and scoped migration','§7.5、附录F.11、§10.4','Three fixed-A bounds averaged overZpub','Given every relevant public seed,the entire appropriate frozen chi/algorithm/message contract holds,then average seed;I-conditioned display endpoints survive',contract,['C36','C45','C47','C48','C50'],['E15','E16','E12'],'Public A distribution responsibility removed for fixed-A numbers;secret seeds/formulas/filtering/Ord/arithmetic still need artifact or finite loss',dist=['chi640','chi976','chi1344'])
add('C52','Latest review identity and exact replay scope','附录C/G.5、修订报告','E16 historical9196 and3194;E17 current script copies and two finite convolutions','Actual identity/exposure and numeric counts only;exact backend IDs null',[],[],['E16','E17'],'Arithmetic-code reconstruction independence does not establish model-error independence',status='VERIFIED_PROVENANCE_SCOPE')
add('C53','Stage contribution and external handoff','§10.3–10.4、人工入口','A and all-three ideal one-update results integrated;author artifacts/human judgment external','Candidate for independent cryptanalysis short paper or thesis core chapter on stated evidence',[],['C09','C25d','C51','C52'],['E12','E13','E15','E16','E17'],'No venue acceptance or global priority certification;new depths/exactfull64 are scope/precision research',status='EVIDENCE_BOUNDED_STAGE_ASSESSMENT')
claims={x['id']:x for x in m['claims']}
def closure(id,anc=()):
 assert id not in anc,(id,anc);res={id}
 for d in claims[id].get('dependencies',[]):res|=closure(d,anc+(id,))
 return res
m['main_result_dependency_audit']={name:dict(root_claim=root,transitive_claim_dependencies=sorted(closure(root)),semantic_distribution=dist,depends_on_chi976=('C10_976' in closure(root))) for name,root,dist in [('A','C09','chi640'),('B_640_fixed_A','C29','chi640'),('B_640_uniform','C25a','chi640'),('B_976_fixed_A','C45','chi976'),('B_976_uniform','C46','chi976'),('B_1344_fixed_A','C48','chi1344'),('B_1344_uniform','C49','chi1344')]}
m['implementation_model_migration']['new_fixed_A_public_A_distribution_responsibility_removed']=True
m['implementation_model_migration']['all_three_numeric_mathematical_profiles_covered']=True
for cfg in m['implementation_model_migration']['config_mappings']:
 n=str(cfg['normative_numeric_fields']['n']);cfg['result_B_fixed_A_transfer']='UNRESOLVED';cfg['result_B_uniform_Setup_transfer']='UNRESOLVED'
 cfg['numeric_reference_comparison_to_B_fixed_A']='MATHEMATICAL_PROFILE_COVERED_UNDER_IDEAL_CONTRACT'
 cfg['mathematical_profile_selector']='official_profile_results.'+n
 cfg['author_implementation_status']='UNRESOLVED';cfg['evidence_scope']='Reported names/official mathematical numeric profiles;authenticated author UE source and joint-law/arithmetic mapping remain unacquired'
m['latest_profile_review']=dict(record=rec(REVIEW/'REVIEW_VERDICT.json'),identity=review['identity'],core_verdict=review['core_mathematical_verdict'],historical_adoption_status='REPAIR_REQUIRED',current_adoption_status='C1-C6_CLOSED',historical_9196_scope=review['finite_validation'],current_replay=rec(OUT/'evidence/REPLAY_EXECUTION.json'))
m['v3_corrections']=[dict(id='C'+str(i),status='CLOSED',source='E16 CORRECTIONS_AND_MANUSCRIPT_IMPACT',current_location=loc) for i,loc in [(1,'摘要、§1、§7.3、§10'),(2,'§7.4、§10.4、附录B.2'),(3,'§7.2、附录F.4/F.12'),(4,'§2、§6.2、§7.4、附录F.1–F.2'),(5,'附录F.8–F.10、G.2–G.4'),(6,'§7.5、§10.4')]]
m['inherited_erratum_impact_by_claim_v22']=m['erratum_impact_by_claim']
m['erratum_impact_by_claim']=[dict(claim_id=x['id'],depends_on_corrected_chi976=('C10_976' in closure(x['id'])),note='INC976 correction retained;v3 976 reliability now genuinely depends on corrected chi976;CF1/640 proofs remain chi640') for x in m['claims']]
m['priority_scope']=dict(historical_application_audit_cutoff='2026-11-10',newer_inherited_profile_queries_date='2026-11-11',newer_query_count_as_recorded=6,source='E15 PUBLIC_PRECEDENT_SEARCH_RECEIPT',new_network_searches_this_revision=0,global_priority='UNRESOLVED')
m['stage_verdict']=dict(theory='THEORETICAL_RESULTS_INTEGRATED_AND_READY_FOR_HUMAN_CRYPTOGRAPHIC_REVIEW',author_software='WAITING_FOR_AUTHOR_ARTIFACT',contribution='Construction-specific source-hiding cryptanalysis and three-official-profile one-update reliability analysis, with parameterized proof/certificates and exact-assumption audit',publication_readiness='Substantive independent short-paper/thesis-core candidate;human cryptographic contribution and proof judgment pending',external_reopen='Authenticated author UE artifact/config and message-checked trace;human3-question review;exact FI reduction/predecessor versions or same-object precedent')
dump(OUT/'CLAIM_EVIDENCE_MATRIX.json',m)
print(json.dumps(dict(draft_bytes=(OUT/'CRYPTOANALYSIS_DRAFT.md').stat().st_size,claims=len(m['claims']),profiles=list(profiles),targeted_patch_blocks=len(blocks),latest_corrections_closed=6),ensure_ascii=False))
