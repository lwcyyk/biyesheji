from pathlib import Path
import json,re,hashlib,collections
ROOT=Path(r'D:\毕业设计');OUT=Path(__file__).resolve().parents[1]
catalog=json.loads((OUT/'data/pdf_catalog.json').read_text(encoding='utf-8'))
core={s['paper_id']:s for s in catalog if 'paper_id'in s}
# Fields are evidence summaries for document authoring, not candidate mechanisms.
data='''
P01|SUDP Secret-Use Delegation Protocol for Agentic Systems|Yu 等|2026|arXiv v4|身份与秘密托管|受损请求方使用用户秘密|规范化操作 新鲜认证许可 托管方代用|作者报告亚毫秒协议开销；七性质中六项由协议承担，内存保密依赖硬件组合|认证器、托管方、规范化与端到端通道进入可信基础
P02|Beyond OAuth Task-Scoped Authorization for AI Agents via Natural Language Slices|Sharma 等|2026|arXiv v2|任务授权|操作数与运行时值超出简单 scope|逐服务任务切片 签名 envelope 绑定值来源|AuthBench 100 个良性任务获准，634 个对抗调用阻断|任务无歧义、权威服务数据和可用 API；事务争议在作者范围外
P03|Authorization Revocation for Long-Running AI Agents Root-Scoped Quiescence under Delegation and Asynchronous Execution|Zhu 与 Wang|2026|arXiv v1|撤销与效果|授权根撤回后仍有异步能力|root-epoch 围栏 独立支持重绑定 通道守恒与前沿证书|provider-free 17/17 轨迹符合登记，检查器拒绝 44/44 语义变异|登记 sink 与 carrier、提供方围栏和完整证据；业务完成与回滚各需其他条件
P04|ResidualAuth What Authorization State Must Language Agents Preserve under Revocable Delegation|Choi 等|2026|arXiv v2|授权状态|相同权限对撤销后的决定不足|以全部未来序列等价定义残余状态及信息下界|四个模型的可信当前决定诊断为 15–16/16 对，256-token 摘录为 0–2/16 对|限声明委托规则；信息访问、状态维护和信息使用分别有责任
P05|AID-Guard Stateful Authorization for Delegated Agent Effects|Tong 等|2026|arXiv v1|撤销与效果|准入到提交及重试可能扩张一次批准|提交复核 原预约保留 终态或带围栏的无效果证明 单一后继|210 次 Stripe 契约试验符合登记；40 个后继时序、30 个竞态和10个恢复时序未见重复效果；严格清单降低效用|D0 完整效果路径、可信宿主与线性化状态；非原子批次需拆分
P06|Authorization Closure Graph Minimal Repair for LLM Agents with Evolving User Instructions|Wang 等|2026|arXiv v1|授权状态|用户修改指令后的选择性失效|Authority Evidence Derived 版本化 DAG 依赖闭包 最小修复|作者在两个自然任务和三个模型上比较动作安全与任务成功|依赖与规则需正确给定，执行前核对版本；修复最小性限定相应语义
P07|Demystifying the InSecurity of OAuth-based Account Linking in Connector Ecosystems|Luo 等|2026|IEEE S&P|连接与绑定|连接器账户与应用用户或租户错绑|架构分类 OASIS 扫描 COSF 与跨租户分析|当前作者稿为40家COSF风险及8家OaaS的额外威胁，按各自分母记录|厂商和版本限定；当前修复状态另核验
P08|Verifying Account Ecosystems With Graph Transformations|Murphy 与 Radomirović|2026|IEEE EuroS&P|形式化与规划|动态账户和恢复依赖|Resource Access Graph 图重写 CTL GROOVE|Apple SDP 案例中识别限制并模型验证改进|图规则与真实平台之间需可靠映射
P09|Near Optimal Bayesian Active Learning for Decision Making|Javdani 等|2014|AISTATS PMLR33|形式化与规划|为决定选择测试|重叠决策区域 Hyperedge Cutting|模型下竞争保证与比较学习、机器人定位评价|贝叶斯测试合同；有副作用核验与动态义务需额外建模
P10|Safe Reinforcement Learning via Shielding under Partial Observability|Carr 等|2023|AAAI|形式化与规划|部分可观测环境的安全探索|可能状态与 shield 限制动作，并与深度RL组合|作者在稀疏奖励场景报告安全性和学习性能|安全性质与部分环境模型正确性是前提
P11|Multi-Cost-Bounded Reachability Analysis of POMDPs|Bork 等|2025|UAI PMLR286|形式化与规划|多项实际累积费用受限时的可达性|cost-epoch 展开 区分代价可见条件|正式题录286卷355–387页；有算法与实证|概率可达目标与用户的最坏情形合同需映射
P12|Tactics for Account Access Graphs|Arnaboldi 等|2024|ESORICS2023论文集|形式化与规划|账户访问关系随动作演化|状态转移 性质断言与 tactics|移动账户与银行应用攻击防御案例|会议年份2023与论文集年份2024分别登记
P13|Defeating Prompt Injections by Design|Debenedetti 等|2025|arXiv v2|信息流与执行|外部数据污染控制和参数|特权规划与隔离解析 能力标签 解释器检查|AgentDojo 安全完成77%，未防御84%；这些是任务完成指标|策略覆盖、工具实现和解释器在可信基础中
P14|DECO Liberating Web Data Using Decentralized Oracles for TLS|Zhang 等|2020|CCS扩展版v4|私密证据|向第三方证明 TLS 数据来源|交互式 TLS 取数与零知识性质证明|展示金融、匿名凭据和价格歧视应用|来源真实性和服务行为解释分别成立
P15|Lightweight Authentication of Web Data via Garble-Then-Prove|Xie 等|2024|USENIX Security|私密证据|降低 Web 数据认证开销|garble-then-prove 与认证载荷转换|作者报告相对前作通信14倍改善；实例与网络条件需保留|TLS版本、载荷、网络和比较实现需同条件
P16|Privacy-preserving policy evaluation in multi-party access control|Sheikhalishahi 等|2021|Journal of Computer Security29(6)|私密证据|共同裁决时保护各方政策|同态加密与安全函数求值实现|作者给出计算和通信实验|参与方、协作、泄漏和中止前提各自固定
P17|Heartbeat-Bound Hierarchical Credentials Cryptographic Revocation for AI Agent Swarms|Deochake|2026|arXiv v1|撤销与效果|停父代理后的子代理残留资格|父心跳新鲜度 层级凭据 缓存公钥及时钟|作者报告0.26 ms认证、0.71%任务开销；窗口有显式上界|父心跳私钥外泄需要在线更新公钥；安全enclave和时钟偏差前提
P18|API Secrets Should Never Become Tokens in the LLMs Vocabulary A Threat Analysis of API Credential Handling in LLM Agent Systems and an Empirical Evaluation of a Vault-Mediated Execution Boundary|Kenney 等|2026|arXiv v1|身份与秘密托管|密钥进入上下文及复制点|模型选择连接标识 可信边界注入认证|16个探针、7个控制域符合期望，同时保留连接头配置失败|有限黑盒不可观测性证据；最小权限和动作批准另行保证
P19|SAGA A Security Architecture for Governing AI Agentic Systems|Syros 等|2026|NDSS|身份与秘密托管|代理发现通信和用户持续控制|Provider注册 身份归属 Access Contact Policy与受控通信|存在实现与评价；具体分母和性能待核|治理服务、代理注册和通信中介的覆盖条件
P20|Universal Cross-app Attacks Exploiting and Securing OAuth 2.0 in Integration Platforms|Luo 等|2025|USENIX Security|连接与绑定|集成平台未区分应用导致跨应用攻击|COAT CORF 与 COVScan 黑盒测量|18个平台中11个COAT、另5个CORF，按论文测试版本解释|OAuth协议正确性与平台应用上下文分别检查
P21|Towards Automating Data Access Permissions in AI Agents|Wu 等|2026|IEEE S&P；预印本2511.17959|偏好与最小权限|频繁数据权限决定的用户负担|用户研究 通信上下文特征 权限预测助手|作者报告总体85.1%、高置信94.4%预测准确率|预测误差与实际授权保证分别计量；用户群和上下文范围待核
P22|Position AI Agents Need Authenticated Delegation|South 等|2025|ICML Position PMLR267|身份与秘密托管|代理代表主体的可认证委托|OAuth OIDC扩展与权限翻译路线|立场论文和研究路线图|观点与实现验证区分，体系建议按提案引用
P23|The Task Shield Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents|Jia 等|2025|ACL Long Papers|任务授权|外部指令使动作偏离用户目标|逐指令与工具调用的任务贡献检查|GPT-4o AgentDojo：ASR2.07%、任务效用69.79%|模型和攻击设置限定；模型判断与形式保证区分
P24|Do You Need a Receipt Anonymous Credential Revocation at Continental Scale via Private Record Certification|EdalatNejad 等|2026|USENIX Security|私密证据|匿名凭据撤销的查询隐私与大规模成本|PRC将PIR和MPC结合，对数据库记录认证|作者报告十亿级凭据亚秒PRC及每百万请求每服务器2.5美元在线成本|数据库与权威参与假设、离线成本、部署费用另核；匿名凭据与OAuth令牌需区分
P25|Prompts Dont Protect Architectural Enforcement via MCP Proxy for LLM Tool Access Control|Uppala|2026|EMNLP Industry|信息流与执行|提示词约束下仍可选越权工具|ABAC代理过滤发现与调用|200任务、3模型；作者将受控代理UIR0%界定为结构路径性质|所有调用须经代理，身份属性和策略正确；旁路另验
P26|Towards Verifiably Safe Tool Use for LLM Agents|Doshi 等|2026|ICSE NIER|信息流与执行|系统安全需求到工具强制的桥接|STPA导出危害规格 能力标签MCP|研究流程与框架提案；本地页含2018及DOI占位模板|正式DOI已定位，局部设计和部署验证范围分开
P27|Securing Autonomous Clinical Agents Time-Scoped Hypergraph Delegation for Controlling Patient Data Access|Karim 等|2026|IEEE ICDH|任务授权|临床多代理权限扩散|NGAC超图 限时衰减 相同轨迹重放SEPI|合成EHR五代理、39载荷；作者报告相对RBAC75%、所实现Macaroon65.2%的加权半径改善|合成工作流和基线实现限定；成熟Macaroon的一般能力另核
P28|Protocols and Formal Models for Delegated Authorisation with Server-Side Secrecy|Snyman 等|2025|ACM ASIA CCS|私密证据|对加密资源进行受限委托|APEX协议族 RAD密码学安全模型|形式证明与OAuth集成实现|服务端加密资源与密钥信任合同，完整成本待核
P29|AgentBound Securing Execution Boundaries of AI Agents|Bühler 等|2026|FSE Proc ACM Software Engineering|信息流与执行|MCP服务器的宿主资源权限|声明式manifest 源码策略生成 宿主边界执行|296个MCP服务器，策略生成80.9%准确率|策略生成误差、宿主执行覆盖与未覆盖威胁分别报告
P30|Securing Agents With Tracked Capabilities|Odersky 等|2026|ACM CAIS|信息流与执行|模型生成代码的资源与信息流|Scala3 capture checking capability-safe子语言及安全harness|作者报告任务性能和阻止不安全行为的实验|禁用unchecked、反射等逃逸；底层工具与LLM无状态保证需实现
P31|When Lower Privileges Suffice Investigating Over-Privileged Tool Selection in LLM Agents|Yang 等|2026|Findings EMNLP|偏好与最小权限|有足够低权限工具时仍升级|ToolPrivBench 初次选择与故障升级 训练缓解|8个领域和5类风险模式；具体百分比待核|暂态失败、可用工具和充分性判断需固定
P32|AgentSpec Customizable Runtime Enforcement for Safe and Reliable LLM Agents|Wang 等|2026|ICSE|信息流与执行|可定制运行时安全规则|触发器 谓词与执行动作DSL|作者报告代码域超90%阻止；生成规则与手写规则分别评价|规则覆盖、语言解释与模型生成质量是前提
P33|Audience Injection Attacks A New Class of Attacks on Web-Based Authorization and Authentication Standards|Hosseyni 等|2026|IEEE S&P|连接与绑定|多端点的客户端断言audience混淆|协议安全分析 规范协作修订|影响多种OAuth/OIDC组合；正式页205–222|具体端点与断言验证合同；当前修复需看RFC10070
P34|Model Context Protocol MCP Landscape Security Threats and Future Research Directions|Hou 等|2025/2026|本地2025预印本；另有正式ACM记录|评测与综述|MCP生命周期攻击面分类|4阶段16活动 4类攻击者16场景|公开分类与案例及项目仓库|本地占位DOI与正式版本分开，完整版本差异待核
P35|AGentVLM Access control policy generation and verification framework with language models|Jayasundara 等|2026|Journal of Information Security and Applications|偏好与最小权限|自然语言访问需求到复杂政策|本地小模型 目的条件抽取 政策反馈|NLACP识别F1 90.6%，政策生成F1 80.6%|文本生成质量与已执行政策安全分别计量
P36|Evaluating Privilege Usage of Agents with Real-World Tools|Zhang 等|2026|FSE Companion|评测与综述|真实工具权限使用的可测性|GrantBox沙箱 真实权限工具注入评测|作者选定场景平均攻击成功率84.80%|受控攻击分布；与AgentDojo或MCPTox指标不可直接排名
P37|CapChain A Capability-Token Access Control Architecture with Verifiable Provenance for Multi-Agent LLM Systems|Choong 等|2026|Applied Sciences|信息流与执行|多代理共享状态的字段传播|能力token provenance日志 capability-aware reducer|150条件中Salient层redactor触发4.67%|4.67%是拦截器触发率，泄漏阻止率需独立评价
P38|MCPTox A Benchmark for Tool Poisoning on Real-World MCP Servers|Wang 等|2026|AAAI；本地题名含Attack|评测与综述|工具元数据中的投毒|45服务器353工具1348案例20模型|作者报告o1-mini ASR72.8%，最高拒绝率低于3%|元数据、输出注入及真实执行效果分别观察；版本差异保留
P39|ProbGuard Proactive Runtime Monitoring for LLM Agent Safety via Probabilistic Prediction|Wang 等|2026|ASE标注稿 arXiv2508.00500v4|信息流与执行|提前预测长程危险|符号抽象 学习DTMC 风险阈值 PAC式分析|重提示减少65.37%不安全行为，保留基线80.4%完成；更严停机有更大效用代价|数据分布和抽象假设；正式DOI占位待核
P40|Delegated Authorization for Agents Constrained to Semantic Task-to-Scope Matching|El Helou 等|2025|arXiv2510.26702v1|任务授权|将任务匹配到最小scope|授权服务器语义检查 ASTRA数据|作者显示多scope任务的能力与限制|语义匹配准确率和服务真实强制分别评价
P41|Hybrid Inspection and Task-Based Access Control in Zero-Trust Agentic AI|El Helou 等|2026|arXiv2605.02682v1|任务授权|多轮任务及不可信中间应用|CASA拦截 五种确定性控制 多轮任务提取与匹配|扩展ASTRA及初始多轮实验|确定性完整性与模型语义判断分别承担保证
P42|Towards Elastic Least Privilege for Agent Planning|Parkinson 等|2026|arXiv2610.40981v1|偏好与最小权限|动态权限与确认负担|用户包络 租约 补充预算 价格对规划器可见|研究议程与示例模型，实践实现效果仍开放|实施和有效性属于作者明确开放问题
P43|Progent Securing AI Agents with Privilege Control|Shi 等|2025|arXiv2504.11703v3|任务授权|动态政策更新与隐性扩权|工具及参数符号规则 每调用确定性检查 SMT判断收缩或扩张|AgentDojo与ASB实验；支持LangChain等框架|初始政策与扩权批准可信，SMT覆盖的表达语言和所有路径需固定
P44|The Irreversibility Budget Fleet-Level Risk Accounting and Admission Control for Agent Operating Systems|Mohammadi 与 Bindschaedler|2026|arXiv2609.00275v1|授权状态|局部合法动作累计超出共享风险|主体跨代理剩余风险账户 边际效果准入|受控研究局部门控最高48倍超额；正确计价下预算保持|保守且依赖感知的定价是作者核心开放问题
P45|Intent-Governed Tool Authorization for AI Agents|Zhu 与 Wang|2026|arXiv2606.22916v4|任务授权|宽凭据与当前请求的效果差异|短期意图证书 收窄manifest payload效果界 draft preflight|176合成任务306端到端试验及36外部子集；无已完成不安全效果仍有0.0909–0.2727未执行不安全草稿|证书忠实度、效果界和静态政策；草稿接受与实际执行分别记录
'''
known_urls={
'P07':'https://mobitec.ie.cuhk.edu.hk/connector-oauth-security/', 'P08':'https://doi.org/10.1109/EuroSP68448.2026.00038','P09':'https://proceedings.mlr.press/v33/javdani14.html','P10':'https://arxiv.org/abs/2204.00755v2','P11':'https://proceedings.mlr.press/v286/bork25a.html','P12':'https://doi.org/10.1007/978-3-031-51479-1_23','P14':'https://arxiv.org/abs/1909.00938v4','P15':'https://www.usenix.org/conference/usenixsecurity24/presentation/xie-xiang','P16':'https://doi.org/10.3233/JCS-200007','P19':'https://doi.org/10.14722/ndss.2026.230869','P20':'https://www.usenix.org/conference/usenixsecurity25/presentation/luo-kaixuan','P21':'https://arxiv.org/abs/2511.17959','P22':'https://proceedings.mlr.press/v267/south25a.html','P23':'https://aclanthology.org/2025.acl-long.1435/','P24':'https://www.usenix.org/conference/usenixsecurity26/presentation/edalatnejad','P26':'https://arxiv.org/abs/2601.08012','P27':'https://doi.org/10.1109/ICDH72779.2026.00047','P31':'https://aclanthology.org/search/?q=When%20Lower%20Privileges%20Suffice','P33':'https://www.sec.uni-stuttgart.de/institute/team/Hosseyni/','P34':'https://arxiv.org/abs/2503.23278','P38':'https://ojs.aaai.org/index.php/AAAI/article/view/40895'}
deep_pages={'P01':[1,6],'P02':[1,4],'P03':[1,8],'P04':[1,4],'P05':[1,3],'P06':[1,4],'P07':[1,4],'P13':[1,4],'P17':[1,6],'P24':[2,5],'P29':[1,4],'P30':[1,4],'P43':[1,3],'P45':[1,4]}
records=[]
for line in data.strip().splitlines():
 a=line.split('|');assert len(a)==10,(len(a),a)
 key,title,author,year,venue,category,problem,method,result,limits=a;s=core[key]
 own=[v for v in s['arxiv_ids'] if not v.startswith('2026.')]
 url=known_urls.get(key) or ('https://arxiv.org/abs/'+own[0] if own else ('https://doi.org/'+s['doi_candidates'][0] if s['doi_candidates'] else ''))
 records.append({'id':key,'title':title,'authors':author,'year':year,'venue':venue,'url':url,'doi':next((v.rstrip('.,') for v in s['doi_candidates'] if 'nnnn'not in v and 'XXXX'not in v),''),'arxiv_id':own[0] if own else '', 'local_path':s['path'],'sha256':s['sha256'],'pages':s['pages'],'preflight':s['preflight']['verdict'],'category':category,'problem':problem,'method':method,'results':result,'conclusion':method+'为该限定问题提供已有方案或分析基础。','limitations':limits,'reading_scope':('首页或摘要与物理页'+','.join(map(str,deep_pages[key]))+'的定点片段') if key in deep_pages else '首页或摘要；封面文献另读第二页','deep_analysis':key in deep_pages,'verification_status':'部分核验','verification_scope':'本地文件匹配与所列片段；公开题录和具体事实分项核对，完整证明及实验复现另列','evidence_locator':'物理页'+','.join(map(str,deep_pages.get(key,[2] if key in ['P08','P15','P16','P20','P24'] else [1])))})
draft_dir=ROOT/'关键论文与可行性核查_2026-11-04/标准草案'
drafts=[]
for i,p in enumerate(sorted(draft_dir.glob('*.txt')),1):
 t=p.read_text(encoding='utf-8-sig',errors='replace');m=re.search(r'draft-[a-z0-9-]+-\d\d',p.name)
 drafts.append({'id':f'D{i:02d}','title':p.stem,'authors':'见原文头部','year':'2026','venue':'Internet-Draft，具体个人或工作组状态以Datatracker为准','url':'https://datatracker.ietf.org/doc/html/'+p.stem,'local_path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'problem':'代理委托、来源证据、会话绑定或撤销','method':'草案定义的记录、字段与验证要求','results':'协议提案，部署结果须另核','conclusion':'作为对应接口的强先例候选','limitations':'草案状态与规范性要求尚需官方题录核对','reading_scope':'标题与摘要定位','verification_status':'部分核验','category':'标准与协议','header_excerpt':t[:1800]})
local_specs=[
('L01','最新系统范围修订','research_main_innovation/main_topic_selection/ae_multi_attempt_revocation_review_2026_11_09/RESEARCH_DECISION_R2.json','全文'),
('L02','区块链辅助候选与最强组合','research_main_innovation/main_topic_selection/ae_blockchain_auxiliary_review_2026_11_09/CANDIDATES_AND_DECISION.json','全文'),
('L03','半径一列表模板主定理','research_main_innovation/main_topic_selection/ae_main_theorem_package/MAIN_THEOREM.md','全文'),
('L04','严格分离门裁决','research_main_innovation/main_topic_selection/ae_strict_separation_gate/DECISION.md','全文'),
('L05','有界误差授权询问定理','research_main_innovation/main_topic_selection/ae_robust_consent_exploration_2026_11_08/ROBUST_QUERY_THEOREM.md','全文'),
('L06','授权询问直接前作比较','research_main_innovation/main_topic_selection/ae_robust_consent_exploration_2026_11_08/PRIOR_ART_COMPARISON.md','全文'),
('L07','FI原游戏密码分析裁决','crypto_fi_original_game_decision/FINAL_THEOREM_AND_CONTRIBUTION.md','已读所列正文范围'),
('L08','持久层闭合状态','mainline_research_closure_v1/VERDICT.md','全文'),
('L09','原生校准结果','auth-lifecycle/docs/experiments/RESULTS.md','本会话前轮全文复用'),
('L10','v1.2反方审查','research_v12/REVIEW.md','本会话前轮全文复用'),
('L11','研究历程总报告','研究成果总报告_2026-11-08/AI智能体授权与凭证管理研究历程及成果总报告_2026-11-08.docx','正文定点与章节索引'),
('L12','探索进展与创新方向','探索进展与创新方向_2026-11-09/AI智能体授权研究探索进展与创新方向_2026-11-09.docx','正文和来源索引，表格另作提取'),
('L13','学位论文证据映射','thesis_draft/THESIS_MAP.md','全文'),
('L14','多尝试模型与案例','research_main_innovation/main_topic_selection/ae_multi_attempt_revocation_review_2026_11_09/PAPER_MODEL_AND_CASES.json','待定点读取'),
('L15','多尝试来源覆盖','research_main_innovation/main_topic_selection/ae_multi_attempt_revocation_review_2026_11_09/SOURCE_AND_COVERAGE.json','待定点读取'),
]
locals=[]
for key,title,rel,scope in local_specs:
 p=ROOT/rel
 locals.append({'id':key,'title':title,'authors':'项目研究记录','year':'2026','venue':'本地研究工件','url':p.as_posix(),'local_path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reading_scope':scope,'verification_status':'部分核验','limitations':'记录状态与当前独立证明或实验复现分别评价','category':'本地证据'})
allr=records+drafts+locals
(OUT/'data/source_records.json').write_text(json.dumps(allr,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'data/core_analysis.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 文献来源与证据记录','','本文件记录阶段一取得的来源与研究内容。题录、被引用事实、完整证明、实验复现分别核验。P 为45篇核心论文，D为8份本地草案，L为当前研究工件；09登记最终统一清单。','', '## 来源与证据字段','']
for r in allr:
 lines += [f"### {r['id']} {r['title']}",'',f"- 作者与时间：{r['authors']}，{r['year']}。载体：{r['venue']}。",f"- 文件：[本地来源]({Path(r['local_path']).as_posix()})。SHA256：`{r['sha256']}`。",f"- 公开入口：{r.get('url') or '待核验'}。",f"- 阅读范围：{r['reading_scope']}。核验状态：{r['verification_status']}。"]
 for field,label in [('problem','研究问题'),('method','技术方法'),('results','结果与条件'),('conclusion','研究结论'),('limitations','限制')]:
  if field in r:lines.append(f"- {label}：{r[field]}。")
 if 'preflight'in r:lines.append(f"- 结构预检：{r['preflight']}；物理页共{r['pages']}页。结构通过与语义读取分别评价。")
 lines.append('')
lines+=['## 机器目录与阅读责任','','[完整PDF目录](data/pdf_catalog.json)包括241个不同字节来源和107份重复副本。45篇核心PDF均通过本次ARS结构预检。两个外围文件解析失败，保留为输入缺陷，具体路径和错误见目录；它们退出本次实质结论。机器全文提取保持来源字节和物理页，实际引用只覆盖明确记录的片段。','', '## 初始论断与证据对应','','| 论断 | 证据 | 定位与范围 |','|---|---|---|','| 课题当前以全生命周期系统为主线 | [L01] | thesis_mainline 与 supersedes |','| 区块链定位为辅助证据核验 | [L01]、[L02] | auxiliary_candidate 与 candidates |','| 原生验收与算法运行桥接有各自状态 | [L08]、[L09] | 算法连接状态与成本分母 |','| T+的精细界和严格实例分开 | [L03]、[L04] | 主定理与实现门逐项 |','| 授权询问量级依赖特定误差合同 | [L05]、[L06] | 定理和直接前作对照 |','| FI为特定发表对象的条件明确分析 | [L07] | 对象、模型、概率与作者实现责任 |','']
(OUT/'03_文献来源与证据记录.md').write_text('\n'.join(lines),encoding='utf-8')
print('Saved stage 1:',len(records),'papers',len(drafts),'drafts',len(locals),'local evidence records')
