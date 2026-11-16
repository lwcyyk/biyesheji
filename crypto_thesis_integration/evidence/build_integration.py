"""Compose an adopted cryptanalysis chapter and unapplied, source-bound thesis patches."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
B=Path(r'D:\毕业设计');O=B/'crypto_thesis_integration';C=B/'crypto_fi_adopted_release_v3_1';T=B/'thesis_draft'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sh(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
adopt=(C/'THESIS_ADOPTION.md').read_text(encoding='utf-8');m=load(C/'CLAIM_EVIDENCE_MATRIX.json');selectors=load(C/'certificates/UNIFIED_RESULT_SELECTORS.json')
assert selectors['profiles']==m['official_profile_results']
registry=load(O/'evidence/SOURCE_REGISTRY.json')['sources'];discovery=load(O/'evidence/MASTER_DISCOVERY.json')
proof_url=(C/'CRYPTOANALYSIS_DRAFT.md').as_posix()
def between(a,b):return adopt[adopt.index(a):adopt.index(b,adopt.index(a))]
a=between('### 3.1 定理A：','### 3.2 定理B：')
b=between('### 3.2 定理B：','## 4. 三组可靠性结果')
results=between('## 4. 三组可靠性结果','## 5. 已有方法与具体对象增量')
methods=between('## 5. 已有方法与具体对象增量','## 6. 适用范围与局限')
scope=between('## 6. 适用范围与局限','## 7. 本章小结')
summary=between('## 7. 本章小结','## 8. 与主任务的关系')
references=between('原始公开对象、方法来源与工程材料：','内部采用依据为')
reuse=[]
def reuse_block(key,text,oldheading,newheading,extra=()):
 out=text.replace(oldheading,newheading,1)
 for x,y in extra:out=out.replace(x,y)
 out=out.replace('完整证明见采用稿','完整证明见[正式采用稿]('+proof_url+')')
 reuse.append(dict(id=key,source=rec(C/'THESIS_ADOPTION.md'),source_heading=oldheading,source_text_sha256=sh(text),target_heading=newheading,adopted_text_sha256=sh(out),adopted_text=out,scope='Text/heading/cross-reference adaptation;theorems,numerical endpoints and model contract retained'))
 return out
pa=reuse_block('THEOREM_A',a,'### 3.1 定理A：','## X.3 定理FI-A：')
pb=reuse_block('THEOREM_B',b,'### 3.2 定理B：','### X.4.1 定理FI-B：', [('定理A所述','定理FI-A所述'),('第4节','X.4.2节')])
pr=reuse_block('RESULTS',results,'## 4. 三组可靠性结果','### X.4.2 三组可靠性结果')
pm=reuse_block('METHODS',methods,'## 5. 已有方法与具体对象增量','## X.5 已有方法与具体对象增量')
ps=reuse_block('SCOPE',scope,'## 6. 适用范围与局限','## X.6 源条件定理评价与适用范围')
pq=reuse_block('SUMMARY',summary,'## 7. 本章小结','## X.8 本章小结')
chapter=r'''# 第X章 已发表UE组件的来源隐藏与有限参数可靠性分析

整合稿，2026-11-11。章号X待当前权威主稿绑定；按已确认历史七章骨架，建议本章为第7章，原讨论/结论顺延为第8章。本章内容已可采用。本章内[1—6]沿用正式采用文本的局部参考编号，装配时与全篇按DOI去重合并。

## X.1 与主论文研究问题的衔接

前述系统与实证章节围绕用户及AI智能体的凭据保管、受控使用、刷新、撤回和恢复，区分本地准入、指定原生材料失效与未来业务效果。真实接口证据说明这些判断必须绑定具体主体、来源、时点、权限和接受路径。密码组件的算法名称或更新接口同样需要这样的范围核准：代理能否观察更新来源，更新后消息能否可靠解密，条件安全定理究竟依赖何种参数和采样前提。

本章据此提出独立组件研究子问题RQ-C：对凭据生命周期中考虑采用的可更新加密构造，如何核准其来源隐藏目标、有限参数可靠性和证明适用边界？研究对象为FI已发表的FrodoPKE型UE构造[1]。本章采用“具体发表构造的来源隐藏密码分析、有限参数可靠性分析及证明范围审计”的贡献定位，分别给出共同正确族的原游戏攻击和三组官方参数的一步概率结论。

本章与主系统具有组件选型和安全目标检查的方法联系。所核主系统实现使用AES-GCM应用状态、可信Controller和原生认证接口；UE/FI接线及业务fresh/update来源隐藏需求尚未建立。原系统实验和本章数学实验各用自己的对象、权限与证据链。后续讨论章将汇总这两条链的已成立结果、部署限制和外部材料条件。

## X.2 精确对象、算法与威胁模型

冻结对象为Jurkiewicz–Prabucka论文，DOI10.46298/fi.14425，期刊/arXiv:2410.03948v4打印算法。期刊PDF SHA256为`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。本章使用正式采用版v3.1，ADOPTED_V3_1_AND_ARCHIVED、PASS_WITHIN_STATED_SCOPE。

令R_q=Z/(2^D)，两代公钥B_e=AS_e+E_e，S_e/E_e为n×8。初始密文C₁=U₀A+F₀、C₂=U₀B_old+G₀+Encode(M)，其中U₀/F₀及Upd的R为8×n，G₀为8×8。TG公开token由四块组成：

\[
\begin{aligned}
P_1&=U_1A+F_1,&Q_1&=U_1B_{new}+G_1-\operatorname{Tensor}_D(S_{old}),\\
P_2&=U_2A+F_2,&Q_2&=U_2B_{new}+G_2.
\end{aligned}
\]

U₁/F₁为nD×n、G₁为nD×8；U₂/F₂为n×n、G₂为n×8。置H=Ord_n(C₁)，Upd输出C′₁=HP₁+RP₂、C′₂=C₂+HQ₁+RQ₂。Ord按实际n列的D位0/1位平面展开并匹配Tensor_D，使H·Tensor_D(S)=C₁S modq。全部原始小量按各组精确χ独立采样；A、消息及指定行/坐标的固定时序在各定理中列明。

来源隐藏实验沿原rand-ind-eu-cpa游戏，比较同一消息的fresh Enc和登记父的更新。攻击者取得公开token并选择合法查询，不取得秘密钥匙；最短轨迹为Enc₀(M)→Next→Corr(token,1)→Challenge₁(M,C)，挑战后结束。输出为来源猜测，Δ是两分支输出概率差；它与明文或密钥恢复是不同的安全事件。

可靠性实验则生成两代诚实钥匙，执行Enc_old→一次诚实未筛选TG→Upd→Dec_new，比较完整消息。所有P₂秩按诚实质量计入，采用官方最近整数平局向上Decode。固定A与均匀全矩阵Setup分别量化；实际程序的公开A生成器、秘密seed展开和机器语义各需对应。

'''+pa+r'''
**证明要点与对象增量。** P₂可逆时由公开关系恢复候选R并检查有限支持。真实fresh界固定A/P₂与适当原始环境，保留F₁随机性以完成独立列卷积。多轮停止仅看P₂并支付真实轮换预算，保留所选父/F₁的合同。逐样本正确性计入初始噪声B₀及最长n次增量，得到B₀+nW<q/8。源游戏权限、真实fresh分布与共同正确性是该具体对象命题的关键，而非仅对均匀行作支持计数。

## X.4 三组官方参数的一次更新可靠性

'''+pb+pr+r'''
### X.4.3 真实依赖与条件化的证明要点

代入打印公式后，真实更新残差包含初始项与所有token项：

\[
N=U_0E_{old}-F_0S_{old}+G_0
+(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2\pmod q.
\]

令𝓑=σ(A,U₀,F₀,R)、V=σ(𝓑,U₁,F₁,U₂,F₂)，π₀=|𝓓|/q。在V层剩余列包条件iid，外层仍保留共享钥匙和token依赖；在𝓑层有真实2n系数律。若好事件坏质量≤δ，每个好环境内E|p(V)−π₀|≤Z，定义C_k=Σ₀^(k−1)π₀^j、F=π₀^k+C_kZ，则行上界为(1−δ)min{1,F,π₀+Z}+δ，Jensen用于下界。完整消息K⊆J给单侧上界，行下界继续绑定J。

976/1344采用g_H(z)=max_a Eχ[z^wt_D(a+X modq)]。先固定A,u，对独立父坐标平移取共同最大PGF后再平均u；各枚举65536平移，1484/1000个完整向量代表，唯一最大平移4/2，H阈值1477/1644的含边界尾≤2^-40。其余环境、差值质量、全部频率和每指数64位→精确ν加权→n次幂80位上包分别计账；1344使用真实奇偶偏差。q=2^D的有限枚举成本与参数化数学判据分开声明。

初始单坐标的有限PGF为Aχ(z)Bχ(z)^(2n)，64坐标并集给各自α。所有无条件联合分析完成后，再以[max{0,(L−α)/(1−α)},min{1,U/(1−α)}]限制于初始完整正确事件I；给定I后的列包独立性并未被额外假设。完整消息正下界另由全部行U₀=F₀=R=0事件承担。精确分数、映射和舍入细节沿正式采用稿附录D—G复核。

'''+pm+ps+r'''
## X.7 与真实系统的联系及当前保证

| 证据链 | 已有事实 | 本章的适用联系 |
|---|---|---|
| 生命周期系统 | G1-r01记录批准、来源、预算、托管、原生刷新及恢复；r02/r03细化源合同和保守表示 | 这些操作支持提出组件检查问题，真实源精化与业务保证仍由系统合同承担 |
| 当前工程接续 | DCL-R6-batch05资源门失败、F1/F4未运行；G2-R17保留A1合成范围验收而H2真实读取未运行 | 已有局部工程事实和未结责任分别列示，本章定理不使用它们作密码学前提 |
| FI数学研究 | 冻结算法/游戏、精确独立χ、条件证明/有限证书及单一AI内部验收 | 形成可直接采用的独立理论章节和候选组件选型案例 |

当前所核持久存储以AES-GCM加密应用状态；原生refresh指向AS的材料创建/轮换。FI公开四块矩阵token、业务服务能力/任务句柄、AT/RT和审计公钥保持各自权限与观察语义。协议均含“token”或“更新”字样并不构成接口映射。主系统记录origin/attempt/version的需求已经存在；是否需要对某类外部密文观察者隐藏fresh/update来源，应先成为明确业务需求，再建立实际状态、泄露和游戏权限的保持证明。

因此，本章贡献用于具体发表构造的安全分析和组件核准。若未来拟采用该UE构造，需要认证作者工件、参数、秘密噪声联合律、Ord/算术与真实调用轨迹；若要推导业务收益或系统失效，还需对应的需求和保持映射。当前论文把系统保证与组件理论分层陈述。

'''+pq+r'''
与前述系统和实证章节合并时，本章增加一条已采用的理论证据链；总讨论应分别汇总系统合同/实际保证和FI算法/游戏/采样结论。原算法成本优势、D1/D2部署资格、资源门及整体优先权继续采用各自最新裁决。

## 本章引文与采用溯源

'''+references+r'''
系统联系采用[G1实际架构](D:/毕业设计/research_g1_lifecycle_contract/2026-11-09_r01/01_ACTUAL_ARCHITECTURE_AUDIT.md)、[G1-r03交接](D:/毕业设计/research_g1_lifecycle_contract/2026-11-10_r03/08_G1_R03_VERDICT_AND_G2_HANDOFF.md)、[DCL-batch05](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch05/BATCH05_FINAL_DECISION.md)及[G2-R17](D:/毕业设计/research_g2_dsat_implementation/2026-11-11_r17/05_FINAL_VERDICT_AND_AUTHORIZATION_REQUEST.md)的各自范围；本轮当前源检索只承担登记范围中的发现与存储定位。

数学采用依据为[正式采用稿v3.1](D:/毕业设计/crypto_fi_adopted_release_v3_1/CRYPTOANALYSIS_DRAFT.md)、[主张矩阵](D:/毕业设计/crypto_fi_adopted_release_v3_1/CLAIM_EVIDENCE_MATRIX.json)、[统一选择器](D:/毕业设计/crypto_fi_adopted_release_v3_1/certificates/UNIFIED_RESULT_SELECTORS.json)及[最终内部裁决](D:/毕业设计/crypto_fi_final_internal_review/FINAL_INTERNAL_DECISION.md)。本轮只适配章节、研究问题与创新措辞，新增数学审阅、标量重放和系统实验均为0；复用段落及指纹见evidence/CHAPTER_REUSE_MAP.json。
'''
(O/'INTEGRATED_CRYPTO_CHAPTER.md').write_text(chapter,encoding='utf-8')
dump(O/'evidence/CHAPTER_REUSE_MAP.json',dict(source=rec(C/'THESIS_ADOPTION.md'),target=rec(O/'INTEGRATED_CRYPTO_CHAPTER.md'),blocks=reuse,chapter_number='X_PENDING_MASTER_BINDING',new_mathematical_claims=0))

# Explicitly unapplied insertions, guarded by actual historical file hashes and anchors.
plan=(O/'THESIS_INTEGRATION_PLAN.md').read_text(encoding='utf-8')
def para_after(label):return plan.split(label,1)[1].split('\n\n',1)[0].strip()
abstract=para_after('**摘要插入段：**');contrib=para_after('**绪论贡献段：**');chapter_summary=para_after('**章节小结段：**');conclusion=para_after('**总论文结论增补段：**')
patches=[]
def operation(id,file,anchor,op,new,old=None):
 p=T/'chapters'/file;s=p.read_text(encoding='utf-8');needle=old if old is not None else anchor
 assert s.count(needle)==1,(id,s.count(needle))
 line=s[:s.index(needle)].count('\n')+1
 patches.append(dict(id=id,status='PROPOSED_NOT_APPLIED',baseline=rec(p),anchor=anchor,baseline_line=line,operation=op,old_text=old,new_text=new,requires='Bind authoritative current master andrebase exact anchors before application'))
patches.append(dict(id='P0',status='CONTENT_READY_MASTER_LOCATION_PENDING',baseline=None,operation='insert_into_authoritative_abstract',new_text=abstract,pending_fields=['abstract_location','authoritative_master_sha256']))
operation('P1','00_CONTRIBUTIONS.md','## 与近邻工作的分工','insert_before','## 新增独立密码分析贡献\n\n'+contrib+'\n\n')
contribution_base=(T/'chapters/00_CONTRIBUTIONS.md').read_text(encoding='utf-8')
old_position=next(x for x in contribution_base.split('\n\n') if x.startswith('本文围绕AI代理使用凭据后'))
operation('P1B','00_CONTRIBUTIONS.md','本文围绕AI代理使用凭据后','replace_exact_paragraph','系统部分沿用其确认的条件性资源理论、原生前提测量和后续G1/DCL/G2合同/工程范围，原H-A/H-B/H-AB成本优势保持原裁决。全论文另纳入已正式采用的FI独立密码分析章节，形成具体发表构造的来源隐藏密码分析、有限参数可靠性分析及证明范围审计；两条证据链分别使用其模型、参数、实现或实验依据。',old_position)
rq='在原有三项问题之外，新增独立组件研究子问题RQ-C：对凭据生命周期中考虑采用的可更新加密构造，如何核准其来源隐藏目标、有限参数更新可靠性与条件安全前提？本子问题采用FI已发表构造作为具体对象，业务UE接线与来源隐藏需求仍按实际材料另核。\n\n'
operation('P2','01_INTRODUCTION.md','## 1.3 方法与贡献','insert_before',rq)
intro=(T/'chapters/01_INTRODUCTION.md').read_text(encoding='utf-8')
old_contrib=next(x for x in intro.split('\n\n') if x.startswith('贡献由问题形式化、条件性资源谱'))
operation('P2B','01_INTRODUCTION.md','贡献由问题形式化、条件性资源谱','replace_exact_paragraph','系统部分的三类贡献为问题形式化、条件性资源谱及验证与实证资产，分别保留其原生符合性、优先权和后续工程范围。本轮另增加已采用的独立FI密码分析贡献，以冻结算法、原游戏和精确采样合同下的定理与证书为证据。四类内容分别列明成熟基础、具体增量及状态，不把工程通过作为独立算法优势。',old_contrib)
structure=next(x for x in intro.split('\n\n') if x.startswith('第2章整理近邻及负结果'))
operation('P3','01_INTRODUCTION.md','第2章整理近邻及负结果','replace_exact_paragraph','第2章整理近邻及负结果，第3章建立系统与真实合同，第4章给出条件性资源理论，第5章说明验证与实现，第6章呈现原生实证及更新的工程边界；独立密码分析章放在实证之后、讨论与结论之前。按历史骨架建议新增第7章并将原第7章顺延为第8章，最终编号依权威主稿确认。',structure)
scope_old=next(x for x in intro.split('\n\n') if x.startswith('当前论文采用可靠原子配置'))
scope_new='原有资源模型和有限验证继续采用其确认的条件范围。G1/DCL/G2系统接续按各自最新裁决更新，已有有限工程和原生测量保留历史分母。早期密码学成本/结构支线按原阶段归档；FI独立密码分析已正式采用v3.1，作为新增理论章节纳入。实际业务密码学接线、H-A/H-B/H-AB成本优势及完整部署仍按对应证据评价。'
operation('P3B','01_INTRODUCTION.md','当前论文采用可靠原子配置','replace_exact_paragraph',scope_new,scope_old)
related=(T/'chapters/02_RELATED_WORK.md').read_text(encoding='utf-8')
oldcrypto=next(x for x in related.split('\n\n') if x.startswith('密码学支线已有条件性代数刻画'))
newcrypto='早期密码学结构/成本支线按其历史裁决归档。此后对FI已发表UE构造的来源隐藏密码分析、三参数一次更新可靠性与证明范围审计，已在v3.1以PASS_WITHIN_STATED_SCOPE正式采用，作为独立章节接入。KLR公开一致性、官方Frodo有限分布与成熟概率/Fourier方法保留来源归属；全球首次按有界检索候选登记。各支线按自己的对象、模型和版本评价。'
operation('P4','02_RELATED_WORK.md','密码学支线已有条件性代数刻画','replace_exact_paragraph',newcrypto,oldcrypto)
operation('P5','06_EMPIRICAL.md','## 6.9 本章小结','append_to_section_end','\n\n本章提供原生接口与模型前提的版本限定证据。下一章转向候选UE组件的算法、原游戏及理想采样模型，独立分析其来源隐藏和更新解码可靠性；该理论案例与当前系统的原生刷新链分别保持对象与证据边界。')
patches.append(dict(id='P6',status='CONTENT_READY_NUMBER_PENDING',operation='insert_new_chapter_between_implementation_empirical_and_discussion',new_file=rec(O/'INTEGRATED_CRYPTO_CHAPTER.md'),historical_before=rec(T/'chapters/07_DISCUSSION.md'),historical_after=rec(T/'chapters/06_EMPIRICAL.md'),suggested_new_chapter=7,suggested_old_discussion_new_chapter=8,actual_chapter_number=None))
discussion=(T/'chapters/07_DISCUSSION.md').read_text(encoding='utf-8')
operation('P7H','07_DISCUSSION.md','## 7.1 当前论文的三条支持链','replace_exact_heading','## 7.1 当前论文的分层证据链','## 7.1 当前论文的三条支持链')
old_chains=next(x for x in discussion.split('\n\n') if x.startswith('本文以认证生命周期问题形式化'))
operation('P7','07_DISCUSSION.md','本文以认证生命周期问题形式化','replace_exact_paragraph','系统部分以认证生命周期形式化、M_r条件资源谱及版本限定验证/实证组织三条支持链，G1/DCL/G2后续结论按其实际范围更新。新增FI密码分析作为独立第四条证据链：冻结算法/游戏与采样合同→自含证明及有限证书→单一AI内部验收及v3.1采用。系统部署与组件理论分别汇总，真实业务游戏映射保持待证。',old_chains)
old_conclusion=next(x for x in discussion.split('\n\n') if x.startswith('本研究在明确的认证生命周期模型'))
new_conclusion=old_conclusion.replace('本研究在明确','系统部分在明确',1).replace('论文以条件性资源理论和原生前提测量','该系统部分以条件性资源理论和原生前提测量')+'\n\n'+conclusion
operation('P7B','07_DISCUSSION.md','本研究在明确的认证生命周期模型','replace_exact_paragraph',new_conclusion,old_conclusion)
patches.append(dict(id='P8',status='BIBLIOGRAPHY_BINDING_PENDING',operation='merge_local_crypto_references_by_DOI',local_source=rec(C/'THESIS_ADOPTION.md'),local_reference_numbers=[1,2,3,4,5,6],old_reference_scheme='R/M identifiers inhistorical baseline',global_map=None,requirements=['Reuse already registered DOI records','Bind final chapter/theorem/table numbers','Retain bibliographic reading/version scope andmissing predecessor status']))
patches.append(dict(id='P9',status='SYSTEM_SYNC_REQUIRED_BEFORE_FULL_MASTER_CLAIM',operation='versioned_system_status_update',target_sections=['system model','implementation andvalidation','empirical status','discussion limitations'],required_current_sources=[registry[x] for x in ['G1_R03','DCL_R5','B05','G2_R16','G2_R17']],note='No automatic proof/status upgrade. Keep M1-M6 andold576 calibration version/denominator;DCL resource gate andG2 actual runtime gaps remain explicit.'))
dump(O/'evidence/INSERTION_PATCHES.json',dict(authority='User permits standalone chapter andper-position plan when current whole master cannot be confirmed',current_master='CURRENT_MASTER_UNCONFIRMED',historical_base_date='2026-11-04',patches=patches,original_files_modified=False,not_a_formal_new_whole_master=True))
numeric=[]
for n,p in selectors['profiles'].items():
 for mode in ['fixed_A','uniform_Setup']:
  v=p[mode];U=F(v['display']['row_full_upper']);pct=F(v['display']['full_error_percent_lower'].rstrip('%'))
  assert 100*(1-U)==pct
  numeric.append(dict(n=n,mode=mode,selector=f'profiles.{n}.{mode}',parameters=p['parameters'],initial_full_failure_power=p['initial']['full_failure_power'],display=v['display'],source=rec(C/'certificates/UNIFIED_RESULT_SELECTORS.json')))
dump(O/'evidence/NUMERIC_BINDING.json',dict(all_profiles_equal_adopted_matrix=True,source_matrix=rec(C/'CLAIM_EVIDENCE_MATRIX.json'),source_selector=rec(C/'certificates/UNIFIED_RESULT_SELECTORS.json'),six_model_rows=numeric,new_scalar_replays=0))
status=dict(schema='crypto-thesis-integration/status/1',date_asia_shanghai='2026-11-11',status='COMPLETE_AS_STANDALONE_CHAPTER_AND_ANCHORED_INSERTION_PLAN',stage_complete=True,current_identity=dict(status='INFORMED_AUTHOR_THESIS_INTEGRATION_AND_CLAIM_ALIGNMENT',declared_model_family='Codex based on GPT-6 per visible developer context',exact_backend_model_id=None,exact_weights_version=None,new_mathematical_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,formal_proof_assistant_checks=0,model_error_process_independence_established=False),required_deliverables=['THESIS_INTEGRATION_PLAN.md','INTEGRATED_CRYPTO_CHAPTER.md','DEFENSE_CLAIM_CARD.md','INTEGRATION_STATUS.json'],adopted_crypto=dict(status='ADOPTED_V3_1_AND_ARCHIVED',verdict='PASS_WITHIN_STATED_SCOPE',contribution_phrase='具体发表构造的来源隐藏密码分析、有限参数可靠性分析及证明范围审计',manifest=rec(C/'MANIFEST.json'),final_review_type=m['adoption_record']['review_type'],final_review_model=m['adoption_record']['reviewer'],final_review_exposure=m['adoption_record']['exposure'],new_review_in_this_integration=False),main_manuscript_authority=dict(status='CURRENT_MASTER_UNCONFIRMED',historical_skeleton=registry['THESIS_MAP'],historical_confirmation=registry['THESIS_SCOPE'],historical_date='2026-11-04',historical_chapter_count=7,historical_title=discovery['historical_title'],current_research_topic=discovery['current_research_topic'],current_topic_basis=discovery['current_topic_basis'],whole_current_master_path=None,whole_current_master_sha256=None,registered_thesis_title=None,actual_final_chapter_number=None,suggested_chapter_in_historical_skeleton=7,suggested_old_discussion_number=8,pending_fields=discovery['pending_fields'],search_scope='Specified main navigation/handoffs,historicalthesis_draft and2026-11-06 patch,relevant laterG1/DCL/G2 decisions,andtitle/heading discovery ofthetwo2026-11-09 surveyDOCX candidates;no authority inferred frommtime'),placement=dict(kind='INDEPENDENT_THEORETICAL_CHAPTER_WITH_COMPONENT_SECURITY_CASE_ROLE',before='discussion andconclusion',after='system implementation/empirical evaluation',chapter_number_in_delivered_text='X',not_business_UE_deployment_proof=True),two_evidence_chains=dict(system='Contracts,versioned implementation,historical/native/profile andcurrent resource results ->scope-limited system guarantees',crypto='Frozen FI algorithm/game,Ord andprecise joint law ->theorems/finite certificates ->single-AI final review andadoptedv3.1'),current_mainline=dict(navigation=registry['NAV'],DCL_latest_decision=registry['B05'],DCL_version='DCL-R6-batch05',DCL_state=dict(batch='CLOSED',resource_gate='RESOURCE_GATE_FAILED',C00_C08_pass=9,C09H=dict(total=34,pass_count=28,mutation_detected=6),actual_C09='FAIL_ENTRY_PERMISSION / NOT_EXERCISED_HANDOFF',F1_F4='UNRUN_RESOURCE_GATE',PASS_BOUNDED=0,strict_separation_instances=0,implementation_gate='CLOSED'),G1_progress=[registry[x] for x in ['G1_R01','G1_R02','G1_R03']],G1_end_to_end='SOURCE_OR_REFINEMENT_GAP',G1_independent_novelty='ANALYSIS_ONLY',G2_latest=registry['G2_R17'],G2_local_A1_scope='Trusted registration/session-read gate,synthetic identities/in-memorySQLite;not FI theoremA or generic query-selector novelty',G2_A1_implemented_with_synthetic_acceptance=True,G2_H2_environment_locked=False,G2_real_authority_read='NOT_RUN',M_r_scope='Conditional mathematical result,priority nearest-neighbor unresolved,native atomic-rebinding conformity unresolved'),system_crypto_relation=dict(actual_reviewed_storage='AES-GCM application snapshot',UE_FI_integration='NOT_ESTABLISHED_IN_REVIEWED_CHAIN',literal_search_receipt=rec(O/'evidence/BOUNDED_UE_SOURCE_SEARCH.json'),fresh_update_hiding_business_requirement='NOT_ESTABLISHED;may be proposed withobserver/leakage/benefit',FI_token_to_business_handle_or_AT_RT_mapping='NOT_ESTABLISHED',established_connection='Candidate-component selection,safety-goal/model/parameter checking andindependent theory chapter',new_business_mapping_needed=['Explicit business source-hiding requirement','Actual UE code/configuration andconditional randomness/arithmetic correspondence','Key/token/ciphertext/observer permissions mapped tobusiness state','Observation/operation/scope preserving reduction orrefinement']),innovation_structure=dict(levels=['Lifecycle contracts andscope audits','Conditional resource theory withpriority/native limits','Versioned engineering andempirical assets','Conditional D1/D2 specification anddeployment obligations','Adopted independent FI cryptanalysis'],independent_generic_algorithm_advantage='NOT_ESTABLISHED bythese integration materials',overall_global_novelty='NOT_ESTABLISHED_AS_A_SINGLE_UNCONDITIONAL_SYSTEM_OR_ALGORITHM_CLAIM'),unapplied_insertion_plan=rec(O/'evidence/INSERTION_PATCHES.json'),next_binding_input='Author/supervisor-confirmed whole manuscript path,version/hash,outline andregisteredtitle;then bind chapter andbibliography andapplyexact guarded patches',future_substantive_inputs=['Authenticated author UE artifact andmessage-checked trace','Dated same-object directprecedent orcontract-respecting mathematical counterexample','Exact parameterized FI reduction/predecessor version','New business requirement andgame-preserving mapping','Strict higher-cost strongest-baseline instance beforecandidate protective mechanism implementation'],candidate_mechanism_gate='Concrete input family,fixedmetric,strongestsame-capability general baseline,predictedstrictgap,andatleastoneinstance proving baseline necessarily higher cost beforeimplementation',actions=dict(original_main_manuscript_writes=0,historical_input_writes=0,system_modules_imported_or_executed=0,system_tests_rerun=0,native_AS_RP_requests=0,model_searches=0,cryptographic_samples=0,scalar_certificate_replays=0,author_UE_runs=0,candidate_mechanism_implementations=0,new_web_priority_searches=0,external_contacts=0),input_snapshot=rec(O/'evidence/INPUT_SNAPSHOT.json'),source_registry=rec(O/'evidence/SOURCE_REGISTRY.json'),seal_state='AWAITING_FINAL_CONSISTENCY_AND_HASH_SEAL')
dump(O/'INTEGRATION_STATUS.json',status)
print(json.dumps(dict(chapter_bytes=(O/'INTEGRATED_CRYPTO_CHAPTER.md').stat().st_size,reused_blocks=len(reuse),patches=len(patches),current_master=status['main_manuscript_authority']['status'],theorem_models_and_endpoints_preserved=True),ensure_ascii=False))
