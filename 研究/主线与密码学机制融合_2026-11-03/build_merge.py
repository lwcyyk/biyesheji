from pathlib import Path
from copy import deepcopy
import json,hashlib,re
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

BASE=Path(__file__).resolve().parent
MAIN=Path('D:/毕业设计/研究/算法机制重构与原创性验证_2026-11-03')
CR=Path('D:/毕业设计/研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1')
SRC=MAIN/'A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert read(BASE/'checks/run02/summary.json')['pass']
mapping=[
dict(id='Crypto-C1',role='关系位置冲突界',retained='ε_S+η_j≥1；同一模拟器δ误差时2δ+η_j≥1',main_use='解释某类线性诊断无法同时完美隐藏幅值并保留相关位置',cannot_infer='B配置全局无解、原生认证失败或全部支持位置必须消失',status='CONDITIONAL_MANUAL_PROOF; PRIORITY_NOT_ESTABLISHED'),
dict(id='Crypto-C2',role='一般允许族可用性',retained='r自由选择时，可行当且仅当每个允许支持独立；仅保留活跃列',main_use='在采用线性诊断之前审查公开模型是否适用',cannot_infer='固定r可行、实际秘密支持合规或来源真实',status='CONDITIONAL_MANUAL_PROOF; CLASSICAL_COMPONENTS'),
dict(id='Crypto-C3',role='完整独立族下的分布与资源',retained='有效矩阵联合块群不变；最小行数max d_j及GL轨道熵下界',main_use='附属数学刻画及简单独立分块负控制',cannot_infer='所有协议最优、端到端省成本、拟阵分量等于原生G',status='CONDITIONAL_MANUAL_PROOF; PRIORITY_UNRESOLVED'),
dict(id='Crypto-C4',role='公开代数证书',retained='绑定预期profile；独立算术、支持族、回路和左逆核验',main_use='未来M07证据解释和M08独立核对的辅助输入',cannot_infer='服务事实真实性、批准授予或自动执行资格',status='FINITE_IMPLEMENTED; PUBLIC_MODEL_ONLY'),
dict(id='Crypto-Gate',role='私密结构合规及支持输出参考',retained='固定残差后判定成员资格；获准profile接受时输出支持',main_use='A的一种候选诊断观察，须另有来源/作用域与Post语义',cannot_infer='认证成功、只有party0见输出、零整体成本或恶意安全部署',status='HONEST_LOCAL_MPC_REFERENCE_ONLY'),
]
dump(BASE/'主线与密码学机制映射.json',{'version':'integration-draft/1.1','algorithm_objectives':['A','B','AB'],'crypto_is_auxiliary_not_fourth_algorithm_claim':True,'items':mapping,'CCT':'optional protected execution protocol proposal; not implemented by this gate','CS03':'historical affine transcript analysis; not replaced or verified by C1-C3'})
interface={
 'name':'PublicDiagnosticEvidence','version':'integration-draft/1.1','status':'SPEC_ONLY_NOT_INSTALLED','authorizes_execution':False,
 'request_fields':['request_id','attempt_id','task_account_service_scope','query_principal','epoch','approval_ref_and_version','remaining_request_compute_and_disclosure_budgets','check_ids','residual_function_version','input_commitment_ref','field_representation','dictionary_digest','expected_profile_digest','complete_support_policy_digest','support_premise_mode','source_relation_evidence_ref','leakage_profile','all_output_recipients','cancellation_and_cleanup_policy'],
 'support_premise_modes':{'SOURCE_BOUND':'independently verified source guarantees the declared support family','PRIVATE_GATE':'a fixed authenticated residual is checked for membership; this does not itself attest its service origin'},
 'response_fields':['source_status','algebra_verification_status','mathematical_conclusion','gate_status','diagnostic_status','support_if_authorized','certificate_and_scope','observation_time','received_time','consumed_external_requests','consumed_compute','openings_and_disclosures','unresolved_obligations','authorizes_execution'],
 'verification_boundaries':['expected_profile comes from trusted caller configuration, not a replacement bundled with an untrusted certificate','content digest is not a service signature or freshness guarantee','source references are identifiers until checked by an external source mechanism','small GF3/GF4 certificate implementation does not verify GF(2^128) production algebra'],
 'outcome_rules':[
  {'case':'source unknown, public certificate verified','evidence_status':'UNKNOWN','A_semantics':'retain uncertainty; no automatic model deletion','execute':False},
  {'case':'gate rejects support family','evidence_status':'REJECTED_DIAGNOSTIC_DOMAIN','A_semantics':'not proof of authentication failure or B impossibility','execute':False},
  {'case':'protocol aborts after a service request may have happened','evidence_status':'ABORTED','A_semantics':'include all possible service effects and retain charged budgets/obligations','execute':False},
  {'case':'certified diagnostic result including empty support','evidence_status':'COMPLETED_DIAGNOSTIC','A_semantics':'only mapped registered check facts at the attested scope/time; independent planning still required','execute':False}],
 'invalidations':['account/service/principal change','approval withdrawal','budget changes','profile/dictionary/field/residual changes','epoch or source freshness failure','input not fixed before disclosure','mask reuse','recipient or leakage change'],
 'not_implemented':['source attestation verifier','A/B/AB runtime adapter','persistent disclosure budget','malicious protocol or recovery implementation']}
dump(BASE/'PublicDiagnosticEvidence_接口增补.json',interface)
progress={'version':'merged-progress/1.1','mainline_metrics_unchanged':True,'original_H_A_H_B_H_AB':'NOT_TESTED','crypto_dimensions':{'mathematics':'manual self-contained proofs under declared conditions; no external/proof-assistant verification','priority':'classical components; exact C3 priority unresolved','construction':'conditional ideal/model arguments; source and composition incomplete','implementation':'finite public checks and honest local MPC references','end_to_end_value':'NOT_ESTABLISHED'},'new_gates':[{'id':'HC-SOURCE','condition':'a verified real source guarantees the declared support family, or an efficient membership method preserves the original success domain','status':'NOT_SATISFIED'},{'id':'HC-FAIR','condition':'same success domain, leakage, recipient set, safety parameter, preprocessing, retry and failure policy','status':'REQUIRED_NOT_FROZEN'},{'id':'HC-COST','condition':'complete costs improve over independent blocks and gate-then-direct-support, not only rows or entropy','status':'NOT_ESTABLISHED'},{'id':'HC-PRIOR','condition':'close cited full-text/version gaps and exact C3 reductions','status':'UNRESOLVED'}],'decision':'retain theory/certificates/gate reference; do not expand structure-optimized MPC in this merge'}
dump(BASE/'最新研究进展登记.json',progress)

blocks=[]
def h(t):blocks.append(('h',t))
def p(t):blocks.append(('p',t))
def eq(t):blocks.append(('eq',t))
def tab(headers,rows,widths):blocks.append(('table',headers,rows,widths))
def link(label,url):blocks.append(('link',label,url))

h('13 密码学机制融合结论与证据层次')
p('本融合版以第1—12节的A/B/AB最新算法进展为主体，纳入structural-audit-r1的结构化私密诊断结果。主线仍追求三项可独立归因的算法贡献；Crypto-C1—C4和gate作为辅助密码学研究，不将同一诊断收益重复计为A、B、AB及第四项创新。原算法、实验分母、阈值和历史结果均保持。')
p('合并的是受限模型中的数学刻画、公开证书检查、私密结构合规参考及其负结果。C1—C3的手工证明、优先权、实现安全和完整成本是不同判断。现有证据不支持强独立密码学原创性，也不支持结构层优于简单独立分块或逐项私密零判断；本次不扩大结构优化MPC、不接入真实撤销。该结论不排除未来找到更强机制。')
tab(['层次','纳入最新进展的内容','保留的限制'],[
['数学','修正量词和观察模型后的Crypto-C1—C3自包含手工论证','无证明助手或外部数学复核；不是全体诊断协议下界'],
['优先权','经典工具及逐命题映射，完整C3优先权未决','独立推导不等于文献首次；未取全文不得猜测覆盖'],
['构造','声明模型中的掩码与gate理想功能','实际来源、组合、恶意实现安全未完成'],
['实现','小域公开检查、证书攻击测试、本地诚实MPC参考','不等同真实服务、生产域证书或恶意部署验证'],
['成本','保留强负控制及完整开销缺口','新增秘密乘法为0不等于总成本为0'],
],[.75,3.0,2.85])
p('本次完整阅读了审计REPORT、PROOFS、PRIOR_ART、DECISION、REPRODUCIBILITY、接口与证书审计说明，并重点核对profile、编译/检查及gate源码。旧文献的详细阅读范围沿审计台账保留，不冒称本次重新通读。Arithmetic Sketching及ePrint 2026/946的官方元数据再次核实；后者当前仍标Preprint，未据相关期刊标识提升版本证据。')

h('14 可保留的密码学结果与严格边界')
p('固定GF(q)，q>2；公开字典V和允许支持族F；活跃列A是F中支持的并集。秘密线性掩码M与支持及幅值独立，单次执行默认不复用。对固定S，幅值能在各位置独立遍历全部非零域元素；观察是带位置标签的掩码列。该模型保护“给定支持后的幅值”，不会自动隐藏支持或账户关联，也不是未标记syndrome的恢复算法。')
eq('Y_S(a) = (a_i Mv_i)_{i∈S}')
p('Crypto-C1：若S内存在非零系数关系，则关系中的每个位置j满足下式。它不要求支持S中所有其他位置也被抹除；模拟器误差为δ时必须用三角不等式得到系数2。')
eq('ε_S + η_j ≥ 1,     2δ + η_j ≥ 1')
p('其中η是该位置被抹除的概率，ε是同支持不同幅值输出的最大总变差距离。该结论可用作线性诊断模型的不可能性见证；不否定非线性MPC，也不表示B的凭据配置无解。GF(2)的非零幅值只有1，受约束幅值或输入相关掩码也不满足原量词，不能沿用该证书。')
p('Crypto-C2：行数r自由选择时，完美幅值隐藏且活跃位置不抹除的线性掩码存在，当且仅当每个允许支持均线性独立。这不是给定r的完整判据。空允许族在存在性命题中可为空真，但运行gate必须恒拒绝；仅含空支持的族可采用零行。未出现列不自动承担保留义务。')
p('Crypto-C3进一步要求F恰好等于活跃字典的全部独立集。设W的分量秩为d₁至dₕ，B为分量分组的列基，L为左逆。刻画作用于有效矩阵Z=MB；当环境维度大于有效维度时，不可省略左逆或直接使用B的逆。')
eq('Γ = ∏_j GL_{d_j}(GF(q)),     r_{min} = max_j d_j')
eq('H_{ent}(M) ≥ ∑_j log₂ |GL_{d_j}(GF(q))|')
p('完美隐私对应Z联合分布对完整块群直积不变；无抹除要求每块以概率1满列秩。给定全部块列空间的元组后，frame分布为乘积均匀；列空间本身仍可相关。匹配构造在各块独立均匀采样GL矩阵并嵌入公共输出空间，等效于简单独立分块。活跃宇宙为空时取零行、空积和空和。行数和Shannon熵最优，不等于随机种子、秘密乘法、通信或恢复开销最优。')
p('记号统一：H_ent是熵，H_dec是主线决策步界；拟阵分量数h、掩码行数r与原生撤销单元G分别记录。线性独立不能替代原生撤销独立。两个代数分量可能对应同一个账户根，因此h=2不能推出G=2。一般允许族也不能直接套用Crypto-C3的行数或熵界。完整证明及反例保留在原PROOFS.md，不在融合中改写为已获同行确认。')

h('15 必须改变合并方案的三项负结果')
p('第一，Crypto-C3的达到下界构造与简单独立分块等效。因此可保留分布刻画和必要条件，却不能把同一构造另命名为优于分块的算法。后续对照必须提供同样的公开字典、结构前提、独立随机性与预处理。')
p('第二，拟议字典V=[e₁,e₁,e₂,e₂]的完整独立族要求每记录至多一项失败；原认证定位契约允许任意最多两项失败。同一记录的tag和claim同时失败在原历史样例已经出现，来源绑定并未排除它。本次独立按支持集合计算并交原公开gate解释器核对GF(4)的全部256个输入：原域接受67，限制域接受49，丢失18个原本应处理的输入，例如(1,1,0,0)。这18个是有限代数枚举计数，不是现实失败率。')
p('第三，通用gate已经计算了各坐标的秘密零标志。若同一成功范围与泄漏契约允许输出支持，接受后直接打开这些标志即可完成定位。原日志中两profile都没有新增秘密乘法；结构掩码层还需另付采样、乘法和检查费用。不能用减少掩码行数代替端到端成本分析。')
tab(['旧参考批次','秘密乘法triples','通信MB','party0轮次'],[
['gate 原最多两失败','8480','331.380','4435'],
['gate后直接支持 原域','8480','331.383','4484'],
['gate 限制族','8416','328.923','4435'],
['gate后直接支持 限制族','8416','328.924','4470'],
],[2.7,1.4,1.2,1.3])
p('每行是原审计中8例一批的开发测量，本次仅复核日志和哈希。相同profile内新增秘密乘法为0，但开值仍分别增加约0.003/0.001 MB通信及49/35轮。不同profile接受范围不同，不以更低通信或更高拒绝获得表面优势。编译、SSL、预处理、内存、失败和恢复必须另纳入总成本；原内存和恢复测量未完成。')

h('16 面向A B AB的证据接口和成本契约')
p('接入位置为M07证据解释与M08独立核对的辅助输入，接口提案仍称PublicDiagnosticEvidence。调用链必须是：有来源依据的检查项及作用域，固定的残差函数和输入，明确的域与字典，可信支持前提或私密gate，限定输出，再由主线解释为观察。证书固定authorizes_execution=false，不能生成批准、配置安全标签或撤销命令。当前接口是规格增补，未安装进auth-lifecycle。')
tab(['主线对象','允许利用的结果','不能直接推出'],[
['A','来源、查询者、epoch匹配的诊断观察及成本；纳入完整Post','空支持即认证成功；REJECTED即无失败；MPC中止等于外部未执行'],
['B','经审定语义映射的事实；公开模型适用或不适用的说明','代数分量等于G；线性掩码不可行等于配置无解'],
['AB','诊断是否消除具体配置分歧、后续清理及计算代价','将密码学编码修复直接称为配置冲突反馈收益'],
],[.55,3.3,2.75])
p('请求绑定任务/账户/服务、查询者、批准版本、剩余请求/计算与披露预算、检查项和残差版本、固定输入引用、域表示、字典与完整支持策略摘要、来源关系、泄漏profile及所有接收者。expected_profile须来自调用方可信配置，不能采信攻击者与证书一起替换的版本。SHA-256只绑定内容，不证明来源或新鲜度。')
p('支持前提使用SOURCE_BOUND（可信来源保证）和PRIVATE_GATE（固定残差的私密合规检查）命名，避免将原审计的路径A/B与主线研究A/B混淆；两种前提都不能省略实际服务来源与账户作用域的核验。')
p('响应分别保留source_status、algebra_verification_status、mathematical_conclusion、gate_status和diagnostic_status。来源UNKNOWN而公开证书VERIFIED时仍不能取得服务事实。gate拒绝只表示超出声明诊断成功域；公开模型的INFEASIBLE_IN_DECLARED_MASK_CLASS也只否定指定掩码类。这些标签不自动覆盖A/B的UNKNOWN、INCONCLUSIVE或界内IMPOSSIBLE。')
p('若MPC在真实核验后中止，A的后继仍须包含所有允许的已生效/未生效状态、已创建会话及未知句柄，预算不退款，义务不消失。收到支持为空仅说明固定检查在绑定时点的结果，不是未检查权限或未来生命周期的保证。批准撤回、epoch变化、源关系撤销、残差/域/字典/策略或接收者变更均使旧证据不能直接复用。')
p('成本分账：外部认证请求继续进入Q及原C_Q，原生单元进入G及原C_G；秘密乘法、预处理、开值/泄漏次数、轮次、字节、CPU和内存另列。披露预算是拟议附加资源，不暗改原成本函数。一次抽象诊断动作可以有多轮MPC，H_dec不自动等于协议轮数或墙钟时长；A/B/AB所有方法必须取得相同诊断接口、成功域、泄漏和批准预算。')
p('本轮复核还显示：把一个未认证的来源标签放入自洽公开profile，代数检查仍可能返回VERIFIED，但runtime_support_verified和authorizes_execution均为false。这是设计边界而非来源真实性测试通过。调用方不得把字段名称或“verified=true”再提升为可信原生事实。')

h('17 与CCT及CS03的分层关系')
tab(['支线','研究对象','本次合并关系'],[
['结构化私密诊断','带位置掩码列的幅值隐私、支持合规及受限输出','作为理论与证据辅助；不负责远端停止或真实来源'],
['CCT','输入凭据到后继凭据的受保护转换及证据材料绑定','仍是可选执行后端候选；本次gate没有实现该目标'],
['CS03','历史仿射公开视图的区分与允许刷新','保留原适用域；C1—C3单次定理不提供跨会话刷新证明'],
],[1.15,2.65,2.8])
p('审计MPC参考的reveal面向两个计算方。只有party0打印日志不代表party1无法取得支持。若未来CCT要求只向可信协调器披露，则当前参考的接收者集合不匹配，不能原样复用并声称同泄漏安全；必须重新设计输出及证明组合。正常随机MASCOT参考运行也不等于该部署已经经过恶意行为、侧信道和断连恢复审计。')
p('小域证书实现只覆盖GF(3)/GF(4)、环境维数1—4及列数0—8；GF(2^128)gate没有被这些证书核验。不同域表示的同名整数不自动是保持运算的嵌入，生产域的字典、左逆及独立族须在实际域中重新核验。GF(2^128)域大小也不等于128位统计安全；原参考参数为-S 40。')
p('输入必须在任何成员资格位或诊断输出前固定，掩码与输入独立且默认每次新采样。收到拒绝后改输入或改策略重试，会形成新的披露，须重新核对批准和预算。单次“只泄漏一位”的结论不能直接组合为多次查询安全，更不能由CS03的局部仿射检查替代整个MPC/TLS转录证明。')

h('18 最新研究进展及继续开发门槛')
p('A2/A3、B2/B3、AB2的最新原型和正反结果继续有效：完整成本方法有局部改善但通用参考也能达到；B的下界和组件分解可检查而无总体加速证据；AB静态界有效但本批无净收益。密码学审计没有补足这些算法的原创性证据，也不降低继续探索三项算法贡献的目标。')
tab(['研究对象','本版保留的成果','未解决的关键问题'],[
['A B AB','原40输入260次主比较、独立参考和机制反例，成本/阈值不改','弱决策保持抽象、组件前沿压缩、有状态核心传递及真实映射'],
['Crypto-C1—C3','受限观察模型的手工刻画与边界反例','完整C3优先权、一般族固定行数、近似隐私和跨次组合'],
['Crypto-C4与gate','公开证书修复、小域核验、诚实本地参考','来源真实性、生产域证书、恶意实现和完整成本'],
['CCT与CS03','既有候选问题与适用域保留','与诊断接收者/泄漏/恢复的可证明组合尚未建立'],
],[1.25,2.75,2.6])
p('开发门槛按因果顺序设置：先补齐未决原始文献和C3精确归约；再取得非人为的可信结构来源，或提出不依赖逐项零判断且不缩小原成功域的合规方法；随后在同泄漏、接收者、安全参数、预处理和失败策略下，与独立分块及gate后直接支持输出比较完整成本。门槛未满足前，保留理论、证书和参考，不扩大结构优化MPC。')
p('新增HC-SOURCE、HC-FAIR、HC-COST、HC-PRIOR只用于登记进入条件，均未判定通过；原H-S与H-A/H-B/H-AB分开保留。实际收益必须包括来源采集、gate、采样、检查、开值、重试、清理与恢复，不能因优化后的域更窄或只统计成功者而成立。')

h('19 本次核验与可复查索引')
p('本次执行25项整合断言，并按两种契约核对GF(4)全部256个输入的公开gate输出；完成两次确定性重放。它们不是新的MPC实验，更不与旧898、70、21条断言和32个MPC场景相加。旧1016个群恒等式实例、538个gate输入也保持各自口径。')
p('另用独立的离线解析脚本，从合成fixture推导预期gate及支持输出，重新核对旧32个场景及四批退出状态。未启动任何MPC进程；旧输出重新核对不等于新增32次执行，也不证明恶意参与方安全。')
p('核对了原审计清单中107项公开源码/报告/日志、源码快照摘要、8个MPC原日志哈希、9组确定性重放、10份指定原件及14项明确旧哈希。104项Player-Data密钥、预处理缓存与WSL链接不在本次公开复核和再分发范围。旧523项仅有存在性声明的历史条目不被升级为全量哈希证明。原算法、最新原型、密码学审计和历史结果均未覆盖。')
p('《主线与密码学机制映射.json》列出可用结论和禁止推论；《PublicDiagnosticEvidence_接口增补.json》为未安装的规范提案；《最新研究进展登记.json》保存五维判断和门槛；checks目录保存本次实际结果。源报告与完整证明保留在原审计目录，以下链接用于核查，不代表本次重做一般证明或同行审查。')
for label,name in [('原审计报告','REPORT.md'),('完整手工证明与边界','PROOFS.md'),('先例映射与未决项','PRIOR_ART.md'),('门槛与反方审查','DECISION.md'),('原实验复现和成本','REPRODUCIBILITY.md')]:link(label,str(CR/name))
p('[CR1] Boneh等，Arithmetic Sketching，CRYPTO 2023，DOI 10.1007/978-3-031-38557-5_6。审计已读指定构造与证明；本次复核官方元数据和摘要，不宣称重新通读。')
link('Arithmetic Sketching 原文与出版信息','https://link.springer.com/chapter/10.1007/978-3-031-38557-5_6')
p('[CR2] Giorgi、Laguillaumie、Ottow、Vergnaud，Constant-Round Secure Distributed Decoding and HQC Threshold Decryption，2026，ePrint 2026/946。本次复核标题、作者、摘要与Preprint状态；全文和精确覆盖仍未决。')
link('ePrint 2026/946','https://eprint.iacr.org/2026/946')
p('其他经典来源及未取全文的Nissim–Weinreb 2006、Ishai–Kushilevitz 2000均按原PRIOR_ART.md保留阅读范围。此版没有把摘要核验、有限实现或同一助手的审阅写成优先权确认。')

dump(BASE/'working/appendix_blocks.json',blocks)
doc=Document(SRC)
edited=[]
for idx,para in enumerate(doc.paragraphs):
 oldtext=para.text
 if oldtext=='机制重构 候选路线与可检查的有限验证':para.text='机制重构与结构化私密诊断融合'
 elif oldtext.startswith('研究报告 v1.0'):para.text='研究融合版 v1.1   2026年11月3日'
 elif oldtext=='保留原算法与历史证据\n已执行离线诊断和确定性重放\n正式经验假设仍未判定':
  para.text='第1至12节保留v1.0算法阶段内容与结果\n本次密码学融合见第13至19节\n正式经验假设仍未判定'
 if oldtext!=para.text:edited.append({'paragraph_index':idx,'before':oldtext,'after':para.text})
def mr(t):
 r=OxmlElement('m:r');pr=OxmlElement('m:rPr');v=OxmlElement('m:sty');v.set(qn('m:val'),'p');pr.append(v);r.append(pr);x=OxmlElement('m:t');x.text=t;r.append(x);return r
def seq(t):
 out=[];buf='';i=0
 while i<len(t):
  if t[i] in '_^' and buf:
   base=buf[-1];buf=buf[:-1]
   if buf:out.append(mr(buf))
   buf='';kind=t[i];i+=1
   if t[i]=='{':
    start=i+1;depth=1;i+=1
    while i<len(t) and depth:
     if t[i]=='{':depth+=1
     elif t[i]=='}':depth-=1
     i+=1
    value=t[start:i-1]
   else:value=t[i];i+=1
   node=OxmlElement('m:sSub' if kind=='_' else 'm:sSup');e=OxmlElement('m:e');e.append(mr(base));node.append(e);sub=OxmlElement('m:sub' if kind=='_' else 'm:sup')
   for n in seq(value):sub.append(n)
   node.append(sub);out.append(node)
  else:buf+=t[i];i+=1
 if buf:out.append(mr(buf))
 return out
for i,b in enumerate(blocks):
 if b[0]=='h':
  para=doc.add_paragraph(b[1],'Heading 1')
  if i==0:para.paragraph_format.page_break_before=True
 elif b[0]=='p':
  para=doc.add_paragraph(b[1].replace('GF(2^128)','GF(2¹²⁸)'))
  if i+1<len(blocks) and blocks[i+1][0]=='eq':para.paragraph_format.keep_with_next=True
 elif b[0]=='eq':
  para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.keep_with_next=i+1<len(blocks) and blocks[i+1][0]=='eq';om=OxmlElement('m:oMath')
  for n in seq(b[1]):om.append(n)
  para._p.append(om)
 elif b[0]=='link':
  para=doc.add_paragraph();rel=para.part.relate_to(b[2],RT.HYPERLINK,is_external=True);el=OxmlElement('w:hyperlink');el.set(qn('r:id'),rel);r=OxmlElement('w:r');rp=OxmlElement('w:rPr');c=OxmlElement('w:color');c.set(qn('w:val'),'245B78');rp.append(c);r.append(rp);t=OxmlElement('w:t');t.text=b[1];r.append(t);el.append(r);para._p.append(el)
 else:
  _,headers,rows,widths=b;table=doc.add_table(rows=1,cols=len(headers));table.autofit=False;table.alignment=WD_TABLE_ALIGNMENT.CENTER
  for col,width in zip(table.columns,widths):col.width=Inches(width)
  borders=OxmlElement('w:tblBorders')
  for edge in ['top','left','bottom','right','insideH','insideV']:
   x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'6');x.set(qn('w:color'),'D9D9D9');borders.append(x)
  table._tbl.tblPr.append(borders)
  for k,values in enumerate([headers]+rows):
   cells=table.rows[0].cells if k==0 else table.add_row().cells
   for j,(cell,value) in enumerate(zip(cells,values)):
    cell.width=Inches(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;pr=cell._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
    for edge in ['top','left','bottom','right']:
     x=OxmlElement('w:'+edge);x.set(qn('w:w'),'95');x.set(qn('w:type'),'dxa');mar.append(x)
    pr.append(mar)
    if k==0 or k%2==0:
     sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'DCE6EE' if k==0 else 'F5F7F9');pr.append(sh)
    para=cell.paragraphs[0];para.paragraph_format.line_spacing=1.15;para.paragraph_format.space_before=Pt(2);para.paragraph_format.space_after=Pt(2);para.paragraph_format.keep_with_next=k==0;para.alignment=WD_ALIGN_PARAGRAPH.CENTER if j==0 else WD_ALIGN_PARAGRAPH.LEFT;r=para.add_run(value);r.font.size=Pt(10);r.bold=k==0
   props=table.rows[k]._tr.get_or_add_trPr();props.append(OxmlElement('w:cantSplit'))
   if k==0:props.append(OxmlElement('w:tblHeader'))
  doc.add_paragraph().paragraph_format.space_after=Pt(2)
doc.core_properties.title='A B AB算法研究与结构化私密诊断融合'
doc.core_properties.version='1.1'
target=BASE/'A、B与AB三项算法研究报告_v1.1_密码学机制融合版.docx'
doc.save(target)
dump(BASE/'修改说明.json',{'base':str(SRC),'base_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'output':str(target),'edits':edited,'append_sections':[13,14,15,16,17,18,19],'original_body_tables_and_results':'preserved; no retrospective relabeling','software_changed':False})
print(json.dumps({'output':str(target),'changed_original_paragraphs':len(edited),'append_blocks':len(blocks)},ensure_ascii=False))
