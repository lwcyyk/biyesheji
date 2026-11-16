from pathlib import Path
import json,hashlib,statistics,re
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
BASE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
analysis=read(BASE/'结果分析.json');main=read(BASE/'runs/final02/summary.json');rows=read(BASE/'runs/final02/rows.json')
smt=read(BASE/'runs/smt02/summary.json');components=read(BASE/'runs/components01/summary.json');secondary=read(BASE/'runs/secondary01/summary.json');mech=read(BASE/'runs/mechanisms01/summary.json');independent=read(BASE/'runs/acquisition_reference01/summary.json')
assert all(x['pass'] for x in [main,smt,components,secondary,mech,independent])
old=read(Path('D:/毕业设计/研究/主线研究论证深化_2026-11-03/文献核验表.json'))['sources']
sources=[]
for id in ['L01','L02','L04','L06','L07','L08','L09']:
 s=dict(next(x for x in old if x['id']==id));s['read_scope']=s['read_scope'].replace('；工件另列L11','');s['reading_status']='INHERITED_VERIFIED_READING; no new full-text claim';sources.append(s)
def src(i,title,year,url,doi,scope,note):
 sources.append(dict(id=i,title=title,year=year,url=url,doi=doi,read_scope=scope,reading_status='THIS_STAGE_TARGETED_VERIFICATION',note=note))
src('N01','Near Optimal Bayesian Active Learning for Decision Making',2014,'https://proceedings.mlr.press/v33/javdani14.html',None,'原文§2、§3.1—3.4，重叠决策区域、HEC、Theorem 1','DRD/高阶超边已有直接先例；原文主要是先验加权期望目标，不将其保证移植到有状态最坏分支模型。')
src('N02','Logic-based Benders decomposition',2003,'https://link.springer.com/article/10.1007/s10107-003-0375-9','10.1007/s10107-003-0375-9','出版页摘要与元数据；全文订阅受限','推理对偶与逻辑割已有；当前单元分层搜索不冒称完整LBBD实现。')
src('N03','Logic-Based Benders Decomposition: Theory and Applications',2024,'https://link.springer.com/book/10.1007/978-3-031-45039-6','10.1007/978-3-031-45039-6','官方概览和目录；未通读专著','分解、branch-and-check与决策图组合已有背景。')
src('N04','Solving logic-based benders decomposition master problems with constraint programming and domain-independent dynamic programming',2025,'https://link.springer.com/article/10.1007/s10601-025-09382-1','10.1007/s10601-025-09382-1','官方摘要、数据与代码入口；全文订阅受限','CP/DIDP主问题和割编码已有近期研究；未运行其工件。')
src('N05','Introducing Automatically Derived Subproblem Relaxations in a Logic-Based Benders Decomposition Solver',2026,'https://link.springer.com/chapter/10.1007/978-3-032-27242-3_26','10.1007/978-3-032-27242-3_26','出版摘要与元数据；全文订阅受限','自动子问题松弛及有效不等式已存在；不能仅以生成必要条件为新原理。')
src('N06','Multi-Cost-Bounded Reachability Analysis of POMDPs',2025,'https://proceedings.mlr.press/v286/bork25a.html',None,'机构原文§1与§2附近；Storm工件说明 DOI 10.5281/zenodo.15642233','多维硬成本界、成本可观察性和状态展开已有方法；本轮未复现Storm工件。')
src('N07','Using Adaptive Sequences for Learning Non-Resettable FSMs',2019,'https://proceedings.mlr.press/v93/groz19a.html',None,'PMLR摘要、作者和年份；会议2018，论文集2019','无reset本身不构成空白；账户副作用外包络不能从FSM结果自动得到。')
src('N08','Program Synthesis By Sketching',2008,'https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-176.html',None,'作者机构技术报告摘要及CEGIS定位','候选生成—反例验证循环不是本项目首创。')
src('N09','Action Selection for MDPs: Anytime AO* Versus UCT',2012,'https://ojs.aaai.org/index.php/AAAI/article/view/8369','10.1609/aaai.v26i1.8369','官方摘要和卷期；AAAI 26为2012，网页迁移发布日期显示2021；arXiv上传2019','AND/OR上下界和anytime搜索有先例；不混淆会议年份、网页发布日期和预印本时间。')
dump(BASE/'来源记录.json',{'sources':sources,'search_scope':'targeted adverse novelty search, not exhaustive systematic review','unverified':['RAG 2026 readable full text remains unavailable','LBBD 2003/2025/2026 full text not obtained','commercial CP/DIDP artifact speed not reproduced'],'own_review':'same assistant, not independent peer review'})

routes=[
{'object':'A','id':'A2','mechanism':'完整后续成本的有界AND/OR搜索；共享乐观下界剪枝','status':'IMPLEMENTED_AND_TESTED','selection':'作为完整求知成本候选和可执行基准保留；通用BB已能覆盖，不登记原创性成立'},
{'object':'A','id':'A3','mechanism':'保留观察、资源、义务与配置G的后续行为签名商键及策略回译','status':'IMPLEMENTED_SECOND_ROUTE_PROBE','selection':'已实际运行；三诊断均无quotient hit，暂不扩大部署；需更弱且可证明的决策保持抽象'},
{'object':'B','id':'B2','mechanism':'原生单元基数分层＋覆盖/远端停止与保留分离松弛＋下界证书','status':'IMPLEMENTED_AND_TESTED','selection':'证书机制可用；当前总体计算慢于通用BB，保留为下界/反例工件'},
{'object':'B','id':'B3','mechanism':'按原生资源耦合分组件，组合各场景预算前沿；耦合时回退B2','status':'IMPLEMENTED_SECOND_ROUTE','selection':'20输入均与R-B一致；3输入分解、其余回退；下一轮检验组件宽度与前沿规模'},
{'object':'AB','id':'AB2','mechanism':'静态决策区域松弛产生查询成本下界，加入同一联合搜索','status':'IMPLEMENTED_AND_TESTED','selection':'静态下界健全性有条件论证和50次残余参考核对；本批无净收益'},
{'object':'AB','id':'AB3','mechanism':'将高阶配置核心通过有副作用的转换关系映射到后继约束，按需精化动态前沿','status':'SPEC_ONLY_NOT_IMPLEMENTED','selection':'静态下界失效反例已运行；下一步需证明转换保持而非简单搬用旧核心'},
]
dump(BASE/'候选路线与筛选.json',{'routes':routes,'research_goal':'three independently attributable algorithmic advantages remains active as a research objective','not_a_claim_of_success':True})

pseudocode={
'A2':'''输入：完整有限认证模型，当前 K、r，固定 B 选择规则，共享预算
1. 编译并审计全部观察、效果、批准、费用与义务；空 K 返回 UNKNOWN。
2. 由共同 W_r 排除无安全完成后继的动作；保持所有允许观察分支。
3. A 模式：若存在可完成的共同配置，按原 G/字典序规则固定配置动作。
4. 计算公开的单世界、最有利结果松弛下界；所有对照可使用它。
5. 按下界顺序完整求值首个动作，取得当前合法策略上界 U。
6. 对其余动作做 min–max 后续成本搜索；仅在已证明下界≥U时剪枝。
7. 缓存完整上下文及 r；独立核验最终原始策略与全部源轨迹。
8. 共享周期预算耗尽返回 INCONCLUSIVE，不交付未检查策略。''',
'A3':'''1. 对具体节点和剩余 r 递归计算严格后续签名。
2. 签名含账户、批准、预算、能力、义务、原生配置G及动作—观察后继。
3. 用结构相等的签名集合构成信念缓存键；不靠哈希碰撞假设判等。
4. 命中时把代表策略按真实可见观察回译到当前原始信念。
5. 逐动作/终态检查回译，再交原独立检查器及源评分器。
6. 构造、比较、回译成本全部计量；无命中也保留负结果。''',
'B2':'''1. 验证原生效果分区及原输入约束；任务标签/token数量不代替G。
2. 共同快捷路径：检查全部单单元候选；若有合法G=1交付，以空域覆盖割证明下界。
3. 对单元集合 U 检查覆盖及逐场景原生停止/保留的乐观可分离性。
4. 独立检查全部低于所报下界的排除证书；保留批准、预算、动作和模型摘要。
5. 按 |U| 递增，仅枚举资源恰为 U 的配置；原计划器和检查器核验交付。
6. 在找到最优基数层后完成该层的字典序比较；不进入更高层。
7. 截断报告 INCONCLUSIVE 与已有检查交付；LB、UB及差距分列。
8. 松弛下界不足以证明整体无解时，明确证书只证明下界。''',
'B3':'''1. 将共享原生单元、隔离环境或有价创建环境的任务连成耦合图。
2. 单组件时回退 B2；零价共享broker仅具有任务独立门控时可跨组件。
3. 各组件枚举配置及不可逆停止动作集合，得到每场景请求/批准/步数前沿。
4. 同配置内去掉资源支配的计划；不随意删除同G但不同字典序的配置。
5. 按组件组合前沿，以全局批准、请求、隔离数和H剪去超额组合。
6. 合并配置与动作，原独立检查器逐前缀核验；按原G/字典序选优。
7. 独立R-B验证有限输入；当前未导出通用分解最优性机器证明。''',
'AB2':'''1. 与关闭版本共享 A 搜索、B 目录接口、目标、W、缓存及所有动作。
2. 只有反馈开关打开时，尝试建立“静态查询”资格证明。
3. 要求无故障、无当前义务、未配置、费用一致；查询不改变世界/批准/会话。
4. 独立核对每个条件世界的配置可行区域；查询只按观察划分 K。
5. 计算进入任一共同配置区域的最小最坏查询成本 D(K)。
6. 用 spent + D(K) + min_world tail 作下界，与公共下界取最大。
7. 证书检查或资格条件不满足时回退公共下界，绝不沿用静态割排除动态策略。
8. 只改变有界联合搜索的剪枝/顺序；完全求解时应与R-J同最优Q。''',
'AB3_SPEC_ONLY':'''目标：对有状态核验后的配置核心建立可检查的传递规则。
1. 从当前配置约束提取核心及其依赖的状态/批准/预算/义务条件。
2. 对每个允许观察，计算转换关系上的前像/后像，而非只删除世界标签。
3. 仅当可检查模拟关系证明约束仍有效时复用；否则展开对应B子问题。
4. 维护覆盖全部策略的下界与可执行策略上界；差距未闭合不报最优。
5. 这是待证明规格，尚未实现；不得作为本轮运行优势。'''
}
(BASE/'算法伪代码.txt').write_text('\n\n'.join(k+'\n'+v for k,v in pseudocode.items()),encoding='utf-8')

cards=[
dict(object='A',problem='有副作用核验的完整合法求知成本',core='A2后续成本搜索；A3决策保持表示探索',nearest=['N09','L02','L06'],mature_parts=['AND/OR搜索','可采纳下界','缓存','严格行为等价'],technical_increment='将发行/清理/剩余批准预算纳入实际后继和代价，细化早配置策略类；尚非已确立原创机制',proof='A策略类内完备/最坏Q最优；商键回译保持条件',metric='完整C_Q、U、求解CPU/内存',baselines=['全后续性质启发式','通用同下界BB','独立受限A参考','R-J'],scope='登记有限模型、可靠原子configure',failure='通用BB同成本；A3构造开销且零命中',evidence='有限模型实证＋条件论证；原创性未建立'),
dict(object='B',problem='原生撤销结构下最小G配置的求解成本',core='B2分离松弛证书与单元层；B3组件预算前沿',nearest=['N02','N03','N04','N05'],mature_parts=['分支定界','组合枚举','资源前沿','约束求解'],technical_increment='具体原生停止/保留必要条件和可检查LB；零价共享broker分解条件',proof='必要割健全；固定模型可分组件合并保持；一般实现未机器证明',metric='同最优G的总求解时间/内存、LB/UB与差距',baselines=['原B','原B-B','同割通用BB','R-B','Z3 Optimize'],scope='独立原生效果分区、不可逆停止、确定setup',failure='耦合图单组件；前沿爆炸；B2松弛预处理超过收益',evidence='20输入与多参考一致；未证总体速度或原创优势'),
dict(object='AB',problem='信息获取与配置承诺之间的净协同',core='AB2静态DRD下界；AB3有状态核心传递规格',nearest=['N01','L06','L02','N06'],mature_parts=['DRD/HEC','联合规划','下界剪枝'],technical_increment='静态资格守卫与最坏查询下界＋最小尾成本的安全组合',proof='资格成立时下界可采纳；动态失效必须回退',metric='仅切换协同开关后的C_Q、U、额外求解开销',baselines=['AB_OFF同一联合搜索','通用DRD适配','R-J'],scope='AB2静态子域；其余回退',failure='所有完整最优Q相同；本批证书构造更慢；动态查询不适用',evidence='50残余下界核对、343关系矩阵、开关配对；独立原创增量未成立')]
dump(BASE/'贡献卡.json',{'cards':cards,'status':'ORIGINALITY_CANDIDATES_NOT_ESTABLISHED','goal_preserved':True})

blocks=[]
def h(t,l=1):blocks.append(('h',l,t))
def p(t):blocks.append(('p',t))
def eq(t):blocks.append(('eq',t))
def table(headers,rows,widths):blocks.append(('table',headers,rows,widths))
def code(t):blocks.append(('code',t))

h('本轮结果与研究目标')
p('本轮继续以A的安全求知效率、B的配置求解效率和AB的独立联合增量为三个算法贡献目标，未将目标改为普通系统整合。已实现A2、A3探索原型、B2、B3及AB2，并增加直接Z3优化对照、独立受限A精确参考和证书检查。已有负结果用于筛掉不充分机制，而不推导所有未来算法都无优势。')
p('实际结果仍不足以确认三个原创优势。A2在一个W0诊断中由6次请求降到5次，但通用同语义精确搜索也能做到；A3三个诊断未产生商键命中。B2/B3给出与精确参考一致的G，B2在本批整体更慢。AB2的静态下界有效，却没有降低完整最优Q，额外计算较大。因此本稿的“突破”是探索目标和候选构造，不是已取得原创性认证。')
p('本轮主结果为40个输入、260次方法运行；另外执行A3的12次路线检查、B3的20次分解检查、Z3的20次对照、20次独立A参考，以及343个三世界关系矩阵与具名安全反例。它们相互重叠，不合计为独立统计样本。原H-A/H-B/H-AB及建议阈值均保持NOT_TESTED。')

h('材料继承及旧机制诊断')
p('主线论证与融合总稿沿用此前完整阅读并再次提取核对；阶段一需求全文核对，阶段二至四按工作流、模块、算法、约束与接口重点阅读，未声称逐行审计SQL附录。读取范围、文档哈希及缺失项见material_passport.json。D01—D15逐条保留原解释和本轮处理，不覆盖原规格。独立Schema/SQL源附件与CS03旧运行附件仍未取得。')
p('新工件全部位于独立研究目录，auth-lifecycle保留为只读依赖。原代码、原生预实验、两份研究报告和四阶段文档的2970项保护清单未发生变化。用户决定目标和批准、AI组织业务、密码管理器受控执行、服务实现原生认证的分工不变；本轮没有新增产品业务，也未执行生产账户操作。')
table(['旧机制','等价或失败条件','已有反例','突破结构与新机制'],[
['A1即时缩减','等有效成本时与B-A排序相同','6对6；8对6；核验创建会话','比较整个后续策略；A2完整Q与A3保持抽象'],
['B完整枚举','规则遗漏可被通用枚举补齐','034/084被回退求解','利用原生资源参数/组件；B2必要割、B3前沿'],
['AB世界对排序','收益可能只是裁掉无关性质','投影诊断5对4，R-J同为4','从排序转为可采纳界；AB2高阶区域，AB3状态传递'],
],[1.1,1.85,1.5,2.15])
p('A的不同初始动作不直接算优势；B不要求精确算法得到比另一精确算法更低的G；AB不把早配置规则解除的效果重复记为反馈收益。三组比较分别固定B和安全执行、固定知识与能力、固定A/B与联合策略空间。')

h('问题定义及公平计算条件')
p('沿用有限可能状态K、剩余决策步r、批准、共享请求/批准预算、配置、真实停止效果及会话义务。查询观察与真实状态变化分开；响应丢失不能假定未执行。W₀只接受目标达到且严格义务为空的非空状态集合，所有允许后继进入少一步的可完成域。H为决策步，不是墙钟时间。')
eq('V(K,r) = min_a max_o [ c(a) + V(Post(K,a,o),r−1) ]')
p('上式表示剩余请求成本；实现采用cap减剩余余额的累计总Q，与本轮固定价格和全分支模型等价。选择域始终经过同一W检查。A2保留固定B的早承诺规则：一旦存在获准且能完成的共同配置，就按原G/字典序选择并配置；AB的开/关版本均允许继续查询与现在配置竞争。因策略类不同，A2与联合最优的差距不能算成反馈开关的收益。')
p('联合R-J/AB在本研究档内最小化最坏Q，不一般按G优先优化。本批重点Q比较的配置G相同；若以后出现G不同的策略，必须单列或预先建立同G比较档，不能把较多原生授权换来的Q减少混入原H-B或声称固定B目标已经完整保持。')
p('任务依赖采用保守恒等投影，完整保留目标、前置、观察、转换、批准、预算与义务；不再仅用当前谓词删除状态。性质基线用后续动作—观察签名而非仅当前scope。此选择可能过保守，但不会以隐藏真实世界创建理想投影。通用精确BB/DP仍是必需强对照，性质启发式只是补充。')
p('所有方法取得同一输入、动作库、故障、预算和假设集合。A/AB共享安全核、菜单缓存和单世界乐观下界；B通用BB取得相同分离松弛和G=1快捷路径。候选专用证书、签名构造、编译、审计与独立交付检查均进入对应计量。R-I/R-J、源评分器及原B检查器的共享schema/内核如实披露，不称完全独立实现。')

h('A的两条路线及完整算法')
p('A2把核验价值定义为完整合法后续策略的成本，消除“立即减少最多签名”与“完成任务最省成本”之间的混淆。其数学机制是有界AND/OR值搜索，不单独主张新搜索理论。公共下界放松可见性和不利结果：每个条件状态允许选择最有利结果及最优动作，再对当前可能状态取最大。这不会高于统一可观察策略的最坏成本。')
code(pseudocode['A2'])
p('A2的剪枝只在已有完整可执行上界后使用下界；相等下界可剪除同Q的另一路策略，但不宣称同时最小化其他资源。有限r递减保证终止；在足够计算资源下，它在声明的早承诺策略类内完备且最小化最坏Q。证明由r归纳和可采纳界的上下界关系给出；Python一般正确性仍未机器证明。新增独立受限A参考用原始参考解释器构造全图，再实施同一早承诺规则，20输入与A2一致。')
p('令N为具体节点数、A为动作数、O为结果数。最坏信念状态数为指数级，记为M；A2及公共安全核的粗略上界为O(MAO)，空间O(M＋策略输出)，M可达H乘2的N次方量级。剪枝只影响实际展开，不改变指数最坏界。节点、下界与参考核验开销都必须计入。')
p('A3是另一机制路线：尝试用严格后续行为等价替代原始信念缓存键。签名保留资源、义务、未来观察/转换及配置G，命中后回译策略并检查原始模型。它采用通用等价/商化思想，不能因加上认证字段就声称首创。')
code(pseudocode['A3'])
p('A3已在重复语义、无压缩空间和有副作用三个输入上运行，所有回译策略合法，Q与参考相同，但quotient_hits均为0。当前实现仅商化缓存键，未建立完整商图；构造和结构比较开销保留。理想的共享签名DAG可按节点/边构建，当前嵌套tuple的比较与哈希成本需另计，不能套用未实现的线性复杂度。')
p('筛选结果：A2作为完整成本的可执行机制保留；A3未取得表示收益，下一项更有区分力的工作是弱于完整迹等价、却保持所有合法决策和代价界的抽象。它必须与通用抽象/精化同条件比较，并证明不会漏掉批准或后置义务；不再把普通缓存当成创新。')

h('B的原生单元下界与分层搜索')
p('主要目标仍为最小g(C)，其中g由原生撤销效果分区计算。B2先考虑原生单元集合U，再考虑恰好使用U的路径配置，避免把大量路径名字直接当作相互独立资源。对每个U建立两个乐观必要条件：各任务有合法账户/scope的支持路径；各停止场景存在获准原生撤销集合，使每个远端停止任务至少有一条可选择的路径被切断，而每个保留任务至少有一条可选择路径不被切断。')
eq('LB = min { |U| : Cover(U) ∧ Separate(U) }')
p('Separate允许不同场景选择不同配置，忽略本地停止、数值预算和部分顺序条件，因而是原问题的放松。任一真正可行配置都满足这些必要条件；若一个U在放松中都失败，就可安全排除。不能反过来把放松可行当成完整交付可行。最终计划仍由原检查器逐前缀核验。')
code(pseudocode['B2'])
p('独立下界检查器不调用B2生成器；它从原始任务、grant、效果分区和批准重新枚举低于LB的单元域与撤销集合。证书绑定模型摘要、世界作用域、批准、预算、动作及约束引用。LB=UB时得到该有限实例的可检查最优性界；若证书只覆盖下界，不得将它扩写为所有配置无解。截断保留INCONCLUSIVE。')
p('本批15个可行B输入均有LB=UB，另外5个输入无解；均与原B、R-B及直接Z3编码一致。不是新算法使最优G低于精确参考。所有共享代理达到G=1的负控制使用共同快捷路径，不增加探测或新授权。')
p('若u为单元数、p为路径数、s为场景数，分离预处理的粗略最坏代价含随3的u次方、s和p的乘积增长的项，后续还可能枚举多个U下的路径子集，最坏仍指数级。证书大小可随2的u次方增长。当前B2的瓶颈恰是预处理和重复候选检查，并未因换成原生单元表示自动变快。')

h('B的第二路线及成熟优化对照')
p('B3从另一结构入手：按共享原生单元、共享隔离环境或有价创建环境连接任务，独立组件内枚举配置与各场景的资源前沿，再在全局预算下组合。零价共享broker仅有任务独立门控时允许跨组件；有共享原生根或整环境关闭影响时必须合并组件。单组件输入回退B2，不擅自删掉耦合。')
code(pseudocode['B3'])
p('正确性条件：组件之间没有未计入接口的原生效果或有价创建共享，目标可按任务分解，原模型停止动作不可逆。此时局部合法计划的全局合并保持目标；最终保留路径也在每个前缀存活，且各场景费用和步数可相加。全局预算仍用组合前沿检查。不能把多个场景分别可行推为连续停止组合可行。')
p('B3保留同G的不同配置，而不是凭局部字典序随意删除：排序集合并集可能改变前缀关系。对同一配置，才去除资源向量受支配的计划。最坏代价包含各组件枚举及前沿笛卡尔积，预算数值还带来伪多项式维度；本轮没有建立“仅以组件宽度为参数”的固定参数可解定理。')
p('B3在全部20个B输入上与独立R-B的最优G和字典序配置一致；3个独立结构输入实际分解，其余17个回退。该结果建立了可运行分解路线，并未建立总体速度或原创优势。下一轮应冻结逐步增加组件接口宽度与前沿规模的输入族，比较通用分解/DIDP而非仅比较平坦枚举。')
p('额外实现了Z3 Optimize 4.15.4.0直接编码：选择路径、已用grant/环境/原生单元、各场景撤销与门控、停止/保留及预算均进入约束；以G和排序配置列表为词典序目标。不可逆停止下，最终保留路径存在可推出任何停止前缀均保留，因此动作集合能回译为原模型中的合法序列。所有SAT交付再过原独立检查器。20个输入状态、最优G和配置均与R-B一致。Z3的UNSAT结果未导出通用证明证书，不能替代本系统一般安全证明。')

h('AB的决策区域下界与动态边界')
p('AB2开启与关闭版本使用同一联合策略空间，均允许probe/configure/stop/cleanup竞争；仅是否构建和使用DRD证书下界不同。解除A的早承诺后从5次请求降到4次，是普通联合规划可以解释的效果，不归入AB反馈增量。')
p('把每个配置映射为在该条件世界中可完成的区域R_C。区域来自逐世界假设诊断，不是隐藏真实世界。先要求严格静态资格：所有查询在配置前、结果确定、不改变世界/批准/会话；当前无配置或未决会话；故障表为空且已付请求数一致。区域的逐世界可行性由R-I独立复核；允许使用乐观区域，因为它只提供下界。')
eq('D(K) = 0,  if ∃C : K ⊆ R_C')
eq('D(K) = min_q [ c(q) + max_o D(K_o) ],  otherwise')
eq('h(K) = max(h_{public}(K), spent + D(K) + min_m tail(m))')
p('查询只考虑严格缩小当前集合的划分，因而D的递归终止。h可采纳的理由是：任何完成策略至少支付进入某一共同配置区域的查询成本，随后至少支付所有可能世界中最小的控制尾成本。这里必须取min tail，不能把两个可能在不同分支达到的最大值直接相加。数值预算、剩余步数和统一停止策略的额外限制未全部进入区域，放松使下界更低而非更高。')
code(pseudocode['AB2'])
p('对三世界P₁={a,b}、P₂={b,c}、P₃={a,c}，两两相容但整体不在任何配置区域。穷尽三世界三计划的343个非空关系矩阵，发现6个这种高阶冲突排列。一个合成认证模型实例中，公共完美信息下界为3，加入必要补证后下界为4，独立精确参考也为4。高阶关系确有内容，但DRD/HEC原文已明确处理重叠区域和高阶超边[N01]，不能称采用超图本身为首创。')
p('本轮还构造了同一可见标签下核验把候选世界转换为同一语义的例子。它可以通过真实状态变化恢复共同配置，无须将原世界逐个区分。静态DRD资格守卫在该例停用下界，回退公共搜索。这既是实现检查，也是AB3所需新机制的边界：要通过转换关系传递约束，而不是只删除世界标签。')
code(pseudocode['AB3_SPEC_ONLY'])
p('AB3仍是待证明、未实现的路线；已完成的是使它成为必要研究问题的动态反例。下一步应检验有状态核心的前像/后像传递是否在同等增量缓存和求解条件下减少B调用，并把无效核心重新验证成本计入。已有联合规划、CEGIS和增量约束推理仍可能覆盖它；这正是新的反向查新任务。')

h('原创性查新与路线筛选')
table(['候选','最接近先例','改变的技术环节','目前判断'],[
['A2','AND/OR、POMDP界搜索 [L02,N09]','以完整发行/处置尾成本替代即时评分','通用同下界BB完全复现；非独立新原理'],
['A3','行为等价与抽象保持','把义务、预算和配置G纳入可回译商键','尚无命中；仍属通用商化路线'],
['B2','分支定界、逻辑割 [N02—05]','原生停止/保留的可检查必要条件','领域割有效；原创性及效率未建立'],
['B3','资源分解与前沿DP [N03—04]','零价门控例外与原生效应耦合条件','实现了分解；需对成熟分解求证增量'],
['AB2','ECD、DRD/HEC [L06,N01]','静态资格、最坏查询下界与尾成本组合','通用DRD适配复现；本批无净收益'],
['AB3','联合规划、CEGIS、子问题松弛 [N05—06,N08]','动态转换下的核心传递及按需精化','尚未证明和实现，不提前认定空白'],
],[.65,1.7,2.15,2.1])
p('本轮补查2024—2026年的逻辑型分解、自动松弛及多成本POMDP工作。近期研究已经覆盖通用割、子问题松弛与多维资源展开，不能将“加预算”“用SMT”“生成证书”单独作为贡献。无reset学习也已有成熟路线[N07]。账户图方面沿用已读Tactics和RAG的已核实摘要；RAG可读全文仍未取得，不声称它缺少本研究某项能力。')
p('未运行的先例工件包括Storm多成本分析、CP/DIDP/LBBD作者实验包和商用CP；本轮真正运行的成熟工具为固定版本Z3。原文、摘要和工件说明的阅读范围在来源记录中分别标注。原创性评价由同一代理进行，不冒称外部独立同行审定。')

h('实际验证与完整分母')
table(['验证块','实际范围','结果与解释'],[
['主比较','20个A/AB输入×8方法；20个B输入×5方法','260运行；独立可行性/交付及参考值一致'],
['W0模型子域','A/AB 18输入，B 20输入；H≤3','保留不可行和空K，不以成功子集替换分母'],
['另行扩展','A/AB H=4和5，各1输入','单列；不得替代W0'],
['第二路线','A3 3输入×4方法；B3 20输入','A3无命中；B3三例分解其余回退'],
['成熟求解器','Z3直接编码全部20个B输入','G/配置/状态与R-B一致'],
['独立残余核对','20个受限A参考；50个AB下界','均符合声明策略类或可采纳关系'],
['机制反例','343关系矩阵、动态守卫、证书篡改、义务遗漏、限额','均符合预期；故意不安全版本被拒绝'],
],[1.25,2.55,2.8])
p('主比较里，A2与性质启发式在18个W0输入中有1例完整Q更低，其余成本相同；H4/H5两例也更低，必须单列。A2与通用同下界BB全部20例同Q。B2与通用BB、原B、R-B全部20例同结果/最优G；旧规则B-B在3个可行例中没有规则内方案，通用枚举与Z3均已补齐。AB开关全部20例同Q，同通用DRD/R-J一致。')
g=analysis['groups'];display=[]
for key,label in [('A2/W0','A2'),('BA_PROPERTY/W0','性质启发式'),('AB_OFF/W0','AB关闭'),('AB_ON/W0','AB开启'),('B2/W0','B2'),('GENERIC_BB/W0','通用B定界'),('R-B/W0','R-B')]:
 v=g[key];display.append([label,str(v['N']),str(v['complete']),f"{v['mean_failure_penalty_cost']:.4f}",f"{v['mean_wall']:.4f}",f"{v['p95_wall_nearest_rank']:.4f}"])
table(['方法','N','完成','平均惩罚成本','平均秒','样本p95秒'],display,[1.25,.35,.5,1.6,1.4,1.5])
p('上表A/AB为C_Q，B为C_G，不能跨行比较单位。A/AB每方法的W0结果是15次可行完成、2次界内不可行和1次UNKNOWN；B2/通用B/R-B为15次可行、5次不可行。主批没有TIMEOUT或INCONCLUSIVE，但单独限额诊断确实返回INCONCLUSIVE。所有未完成均按原共同cap+1计入描述成本，未删除未知或拒绝。')
p(f"以全部20个A输入描述，AB开启/关闭的总墙钟比为{analysis['comparisons']['AB_ON/AB_OFF']['time_ratio_sum_all']:.3f}；B2/通用BB为{analysis['comparisons']['B2/GENERIC_BB']['time_ratio_sum_all']:.3f}。这些值表示本批额外构造开销，不能作总体效应估计或显著性结论。候选有更强下界，并不自动意味着运行更快。")
p('每个测量worker实际设置4个逻辑CPU亲和性和8GiB进程内存上限；30秒共同周期从输入处理贯穿编译、审计、求解与检查，子调用不重置，父进程另有32秒含启动的看门狗。每行记录实际CPU、峰值工作集及守卫是否成功。机器不是独占的4个物理核；只测模型worker，没有两服务/真实AI完整部署，所以不能宣称完整W0验收通过，尤其未测1000次本地准入p95。')
p('final01和二路线worker部分重叠，最终计时采用final02；两次260个运行的语义结果及策略完全一致，时间和内存不要求相同。此为同一开发输入的重复执行，不是新独立家族。SMT首次库加载另记，smt02统一把已初始化求解器作为周期入口；smt01保留。所有源码快照、实际命令、状态、政策、费用和工作计数可复查。')

h('三项独立归因及原生语义映射')
p('A比较只改变求知选择/表示，固定B目录接口与配置后控制。研发审查发现早期性质基线的配置后控制也是贪心，故在0.2中统一为相同精确尾策略，旧dev01原样保留。B比较固定全部知识和能力，只替换配置求解器；AB比较固定同一联合策略空间和A/B接口，仅切换DRD界。')
p('当前A/AB使用B2Select目录适配器，对已经通过共同W检查的配置按当前K的原生G与字典序选择；没有在每个联合节点运行完整B2/B3配置搜索。因此本轮不能把B2/B3的独立计算改进声称已经传导到完整AB系统。这是必要的耦合边界，下一阶段须把全B2/B3成本接入后再作真正2×2×2归因。现有三组比较仍能分别否定即时启发式、配置搜索与静态界的宽泛主张。')
p('F1对应原生授权/撤销效果分区；B2的分离割只有在此契约真实时才有实际意义。F2对应实际账户及材料接受，不能由元数据名字推断。F3对应核验新会话、未知句柄和清理可用性；A2将这些代价加入状态，AB2则对改变它们的查询停用静态界。Q2认证成功不能证明F1，active/client_id/sid或两个token不能自行证明独立撤销。')
p('本轮输入中的verified与evidence是合成声明，不是原生调查新证据。V-Q、V-R保持未关闭；可靠原子configure的一步可能包含多个真实请求，不能把其结论推广到真实发行微步骤、迟到请求及并发恢复。CCT、MPC-TLS与CS03保持可选支线，不为A/B/AB提供虚构的接口或创新证明。')

h('贡献卡及下一项关键验证')
p('三项研究目标继续保留。下面列的是当前最有内容的候选与失败范围，不是三个创新已成立的结论。详细贡献卡另附，成熟组件与新增技术部分分开登记。')
table(['对象','原创机制候选','理论证据','实现状态','同条件优势证据','等价或失败范围','下一项关键验证'],[
['A','完整处置成本；决策保持抽象','策略类内最优及下界条件；商键回译检查','A2、A3原型','1个W0例6→5；通用BB亦可','通用BB覆盖；A3零命中','弱于迹等价的抽象能否保留值界并减少构造'],
['B','原生分离割；组件预算前沿','必要条件健全；分解需耦合条件','B2、B3及Z3对照','同最优G；尚无总体计算优势','预处理过重；17例单组件回退','逐步增大接口宽度，检验前沿压缩和通用DIDP'],
['AB','区域查询下界；动态核心传递','静态可采纳；动态必须回退','AB2实作；AB3待证明','开关同Q；本批更慢','通用DRD覆盖；状态变化禁用静态界','证明有状态核心传递并计入验证/失效成本'],
],[.4,1.05,1.05,.8,1.1,1.05,1.15])
p('已排除：单调改分数、完整枚举补齐、普通世界对/超图、通用缓存本身足以构成三个创新的主张。仍值得探索：认证动作对可行配置与后置义务的受限结构，是否能产生比通用抽象、分解和联合规划更便宜且可证明的算法。下一轮应先冻结结构参数和反证集合，再实现弱决策抽象、分解前沿压缩或动态核心传递中的一个具体增量；若再次等价，就精确说明原因并转向另一机制。')
p('本轮未完成：一般代码机器证明、对成熟工具全集的性能复现、完整A2×B2/B3×AB系统耦合、独立原生家族、正式统计与完整W0部署验收。原阈值不变，新计算优势只在protocol及addendum中登记为开发目标，未转成正式假设通过。')

h('来源与可复现附件')
p('规范附件包括算法伪代码、候选路线、贡献卡、D01—D15对照、协议、全部输入、原始运行、独立参考、证书检查与依赖锁。复现入口见《复现与限制说明.txt》。文件名中的v1.0表示本报告版本，不覆盖原算法版本。')
for s in sources:
 p(f"[{s['id']}] {s['title']}。{s['year']}。"+(f"DOI {s['doi']}。" if s.get('doi') else '')+f"读取范围：{s['read_scope']}。")
 blocks.append(('link',s['url']))
dump(BASE/'working/report_blocks.json',blocks)

# Reuse the already visually verified academic Word layout only, never execute the
# original report builder or write into its directory.
layout=Path('D:/毕业设计/研究/主线研究论证深化_2026-11-03/working/build_report.py').read_text(encoding='utf-8').split('# Artifact creation:')[1]
layout='# Artifact creation:'+layout
layout=layout.replace('认证语义与凭据配置研究论证深化','A B 与 AB 三项算法原创性突破及优势验证研究报告')
layout=layout.replace('A B AB 的等效边界 条件正确性与验证路线','机制重构 候选路线与可检查的有限验证')
layout=layout.replace('研究增补 v1.0','研究报告 v1.0').replace('A B AB 主线研究论证  |  条件命题与可复现反例','A B AB 算法探索  |  机制 原创性与效果分别核验')
layout=layout.replace('认证语义与凭据配置_主线研究论证深化_v1.0.docx','A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx')
layout=layout.replace("doc.add_paragraph('A B 与 AB 三项算法原创性突破及优势验证研究报告','Title')","doc.add_paragraph('A B 与 AB 三项算法\\n原创性突破及优势验证研究报告','Title')")
layout=layout.replace('par.paragraph_format.space_after=Pt(5)','par.paragraph_format.space_after=Pt(4)')
layout=layout.replace("par.paragraph_format.line_spacing=1.15\n  el=", "par.paragraph_format.line_spacing=1.15;par.paragraph_format.space_after=Pt(5)\n  el=")
layout=layout.replace("elif b[0]=='eq':", "elif b[0]=='code':\n  par=doc.add_paragraph(b[1]);par.paragraph_format.line_spacing=1.15;par.paragraph_format.keep_together=True\n  for r in par.runs:r.font.size=Pt(10)\n elif b[0]=='eq':")
layout=layout.replace("r'^\\[L\\d+\\]'", "r'^\\[(?:L|N)\\d+\\]'")
exec(compile(layout,'local_docx_layout','exec'))
