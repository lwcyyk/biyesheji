"""Local claim registry assembly; cited bytes are hashed, no service requests."""
from pathlib import Path
import hashlib
import json

BASE=Path(r'D:\毕业设计');OUT=Path(__file__).resolve().parent
rows=[]


def add(cid,text,category,scope,premises,refs,denominator,failures,level,wording,gap):
    evidence=[]
    for relative,locator in refs:
        path=BASE/relative
        evidence.append({'path':str(path),'locator':locator,'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None})
    rows.append({'id':cid,'text':text,'category':category,'quantifier_and_scope':scope,'premises':premises,
                 'evidence':evidence,'original_results_and_denominators':denominator,'counterexamples':failures,
                 'evidence_level':level,'paper_wording':wording,'missing_key_evidence':gap})


add('F01','L、R、E分别描述本地准入、声明原生接受及效果提交边界。','问题形式化','本项目声明的接口和效果域；三个目标分别判断',
 ['范围与接受路径先声明'],[('thesis_draft/chapters/03_FORMAL_MODEL.md','§1'),('thesis_draft/sources/technical_report.txt','P0037')],{},
 ['本地门关闭仍存在直接Bearer路径；资源拒绝仍可存在已提交业务效果'],'SPECIFICATION',
 '本文区分本地撤回、原生材料接受和效果提交，并为每个目标分别登记前提。',['任意业务RP及外部效果的实际契约'])
add('F02','W_h递推支持带严格义务的有界完成条件命题。','条件性理论','有限显式表、非空K、剩余决策步h；所有允许观察分支',
 ['初态覆盖','完整Post','批准/预算正确','策略继续执行','终态反映'],[('auth-lifecycle/docs/SEMANTICS.md','§3–7'),('auth-lifecycle/src/auth_lifecycle/controller.py','BoundedController.step')],{},
 ['stay自环；未建模迟到效果；把h解释为墙钟'],'CONDITIONAL_MANUAL_ARGUMENT',
 '在有限表完整覆盖执行且终态反映成立时，W_h内策略在至多h个模型决策步内完成并结清严格义务。',['真实运行层精化映射；机器证明；墙钟活性'])
add('F03','多世界策略/反证证书覆盖统一可观察策略，世界对不足以替代任意有限世界。','条件性理论','声明模型及给定h，证书检查完整终止',
 ['模型可信且完整','每个动作反驳覆盖或真实阻断'],[('auth-lifecycle/docs/CERTIFICATES.md','多世界及证书范围'),('auth-lifecycle/src/auth_lifecycle/checker.py','check_policy/check_impossibility')],{},
 ['三世界两两有解但共同无解；一步不可能不能推两步不可能'],'CONDITIONAL_ARGUMENT_AND_FINITE_TESTS',
 '提供绑定模型和查询范围的可检查证书，明确多世界与决策步界。',['通用算法新颖性；真实服务模型可信来源'])
add('T01','M_r中固定绑定最少迁移距离等于两标签错配最小值。','条件性理论','任意有限非空任务集；非平凡请求标签均出现；单次首次停止',
 ['完全目标根资格','充分容量','单任务原子交接','同步退役旧支持','付费空根'],[('research_recipe_r3/MATH_REVIEW.md','§2–3及附录'),('research_recipe_r3/BLIND_DERIVATION.md','§2')],{'finite_budget_queries':268310},
 ['单根非平凡请求距离∞；同向多数标签需修正；非原子复制/删除窗口'],'MANUAL_PROOF_WITH_SAME_MODEL_REDERIVATION',
 '在M_r公理下给出固定配置的精确迁移距离及达到执行。',['外部数学复核；真实原子重绑子域符合性'])
add('T02','固定k≥2、r≥1时资源节省谱恰为0至k−2。','条件性理论','∀固定k≥2,r≥1，∀节省s∈[0,k−2]，∃有限T,F及可变重数；共同初态∃b0∀S∃执行',
 ['M_r全部公理','首次请求','每任务移动计一单位','空备用根计G'],[('research_recipe_r3/VERDICT.md','§1–3'),('research_recipe_r3/MATH_REVIEW.md','§2–6'),('research_recipe_r3/results/expanded01/summary.json','exhaustive/spectrum')],
 {'spectrum_instances':224,'full_lower_enumeration':36,'larger_instances_lemma_based':188},
 ['固定实例大r可降至2根，与重数随实例变化的谱量词分开；至多一次与恰好一次不同'],'CONDITIONAL_MANUAL_PROOF_PRIORITY_UNRESOLVED',
 '证明M_r的完整资源节省谱，整体优先权维持近邻未决；有限核对与手工下界分别登记。',['直接近邻优先权封口；外部审阅；原生M_r符合性'])
add('T03','M6刷新、撤销与恢复尚不能直接实例化M_r原子重绑公理。','实现符合性','当前M6 profile与M_r之间的关系',
 ['以实际调用和公理逐项对应'],[('research_recipe_r3/NATIVE_PREMISES.md','公理/原生保持及P-MR-01'),('mainline_native_isolation_v1/NATIVE_ISOLATION_PROFILE.md','两个场景'),('mainline_native_isolation_v1/source_frozen/src/auth_lifecycle/online_state/native_isolation.py','run_case')],{'M6_native_samples':2},
 ['本地原子接纳不等于原生原子换根；刷新材料不等于换到另一独立根'],'MAPPING_NOT_ESTABLISHED',
 'M6补强托管和未知尝试处置证据；完全资格、逐前缀保留及同步退役的M_r映射继续单列。',['被测rebind实现与覆盖关系'])
add('A01','A1/A4、研究B/B4、AB反馈存在有限模型实现。','实现符合性','各自版本及有限模型；不混入M1—M6原生动作选择',
 ['可信源模型','相应scope/完整Post核验'],[('auth-lifecycle/src/auth_lifecycle/a/candidate.py','solve'),('research_v12/a4.py','Cells'),('research_v12/b4.py','solve/partition/expand'),('research_v12/joint.py','session/solve'),('research_v12/FORMAL.md','§2–5')],{},
 ['A4未减少完整模型编译规模；B4非零接口回退全局'],'FINITE_IMPLEMENTATION',
 '历史原型提供有限获取、配置与反馈计算；原生运行层的接线单独判断。',['持久运行层调用适配；真实未知契约查询策略激活'])
add('A02','B4零费用等语义路径按类枚举具有受限结构压缩界。','条件性理论','p路径/k等价类；同任务/授权/环境/委托且零费用',
 ['严格类等价','全局字典序展开','原完整规划器不变'],[('research_v12/FORMAL.md','§4 B-Q/B-Lex'),('research_v12/b4.py','partition/expand/check_compression'),('research_v12/REVIEW.md','第4项')],{},
 ['局部最小代表[a]并[c]输给[a,b,c]；k=p无指数压缩；通用同预处理复现'],'CONDITIONAL_STRUCTURE_RESULT_GENERIC_COVERAGE',
 '在受限输入上将配置子集枚举从2^p缩至2^k，保留全局字典序；相同通用预处理可获得该收益。',['超出通用预处理的严格差距；总体分布优势'])
add('A03','冻结v1.2 AB3检查器存在control-only作用域混用反例。','实现符合性','历史research_v12独立Checker的可行证书scope',
 ['保留历史原件'],[('research_secret_recipe/SCOPE_AUDIT.json','actual_checker_verdict=VALID/expected=INVALID/fix_status=pending'),('thesis_draft/POSTPONED_UPGRADES.md','U08')],{'registered_scope_counterexample':1},
 ['将probe策略重贴control-only标签仍被接受'],'COUNTEREXAMPLE_REPRODUCED_IN_PRIOR_AUDIT',
 'AB3历史实现的广义scope健全性主张收缩，内部生成证书的适用情况与恶意输入检查分开。',['独立修复与新源码回归；当前任务未修改算法'])
add('A04','M1—M6没有调用研究A/B/AB求解器选择动作。','实现符合性','登记的六批运行及相应冻结入口',
 ['按实际import和调用点审计'],[('mainline_native_isolation_v1/source_frozen/src/auth_lifecycle/online_state/native_isolation.py','run_case'),('mainline_agent_isolation_v1/source_frozen/src/auth_lifecycle/online_state/isolation_acceptance.py','run_scene'),('auth-lifecycle/src/auth_lifecycle/online_state/services.py','Controller.call/reconcile')],{'M1_slots':21,'M2_samples':4,'M3_samples':2,'M4_samples':2,'M5_scenarios':12,'M6_samples':2},
 ['成熟对账分支根据证据决定CLOSED，不能归为AB算法反馈收益'],'SOURCE_DERIVED_WITH_TRACE_ENTRY_BINDING',
 'M1—M6由固定验收程序发起，成熟Controller进行授权、预算、来源和对账判断。',['模型—快照适配、策略提案和反馈闭环执行证据'])
add('A05','早期576次校准存在研究B配置到原生执行的受限绑定。','有限原生实测','known-contract-single-path/v1；与当前持久运行层分开',
 ['已知单世界','原子配置投影','每任务单路径','缓存对照按原协议'],[('auth-lifecycle/src/auth_lifecycle/experiment/planning.py','plan'),('auth-lifecycle/scripts/l1_pilot.py','execute'),('auth-lifecycle/docs/experiments/RESULTS.md','§1–3')],{'method_runs':576,'pairs':288,'runs_per_method':96},
 ['query_needed_profile=false；probes={}；AB查询/具体反馈激活0'],'LIMITED_NATIVE_CALIBRATION',
 '旧校准曾使用B配置及有限策略的ok分支驱动原生调用；它不代表M1—M6采用该规划器。',['未知语义查询与AB反馈激活；持久层精化'])
add('H01','H-A/H-B/H-AB总体成本优势尚无确认性支持。','算法优势假设','现有模型/负控制和正式研究状态',
 ['不把方法标签等效当优势','失败惩罚保留'],[('auth-lifecycle/docs/experiments/RESULTS.md','三组成本比1；NOT_TESTED'),('thesis_draft/TASK_SCOPE.md','第2项'),('research_v12/REVIEW.md','主样本和通用复现')],{'calibration_runs':576,'query_activation':0,'AB_feedback_activation':0},
 ['所有六方法每96次均20完成/56拒绝/20UNKNOWN；不代表真实可行目标分布'],'NOT_ESTABLISHED',
 '正式优势假设未通过；当前论文沿用排除其总体优势主张的范围。',['已确认分布、同条件强对照、激活与完整成本证据'])
add('H02','A-E小见证存在性已给出，但目标候选枚举界未证明。','算法优势假设','TOPIC-THEORY-1临时理论策略；M_r完整需求矩阵，g/r参数',
 ['同模型同信息强基线','不把基线上界作下界'],[('research_main_innovation/main_topic_selection/TOPIC_DECISION.md','§2–6'),('research_main_innovation/main_topic_selection/FIRST_PROOF_ATTEMPT.md','结构见证与未完成步骤'),('research_main_innovation/main_topic_selection/sources/PROOF_STATUS.json','unproved/next_action')],{},
 ['直接枚举m^(g−1)n^(r(g−1))；通用FPT存在不能作新主张'],'READY_FOR_FOCUSED_PROOF_NOT_A_PROVED_ADVANTAGE',
 '已有≤g−1分离行及≤r(g−1)例外任务存在性；在目标参数界内定位候选仍是未证的唯一主攻步骤。',['2^{O(g²+gr log(gr+2))}(mn)^c定位证明或精确障碍；优先权封口'])
add('E01','双平台52次调查刻画指定profile的认证语义差异。','有限原生实测','Keycloak26.8.1/Casdoor4.25.0，各13条件×2重复',
 ['冻结版本、端点和观察路径'],[('auth-lifecycle/docs/experiments/CAPABILITIES.md','52条调查'),('auth-lifecycle/results/experiments/survey04/observations.json','rows'),('research_recipe_r3/NATIVE_PREMISES.md','旧RT/共享根/恢复分别解释')],{'observations':52,'platforms':2},
 ['旧RT撤销竞争不代表共享账户根并发关闭；离线JWT资源策略不同'],'PROFILE_BOUND_NATIVE_OBSERVATIONS',
 '两平台受控调查揭示指定接受与撤销路径差异，作为原生公理审计输入。',['完整平台类覆盖及原生M_r子域符合性'])
add('E02','M1保留20通过和1初始化中止。','实现符合性','21预登记槽；假provider，局部进程/目录故障',
 ['只续行未运行槽'],[('mainline_online_state_v1/M1_AGGREGATE.json','planned_slots/counts'),('mainline_online_state_v1/m1_batch01/results.json','ABORTED/NOT_RUN'),('mainline_online_state_v1/m1_batch01_continuation/results.json','20 PASS')],{'planned_slots':21,'pass':20,'initialization_abort':1,'native_samples':0},
 ['初始化失败不计通过；有限故障不覆盖断电/权威回滚'],'LIMITED_LOCAL_ACCEPTANCE',
 'M1的21槽中20通过、1初始化中止，安全失败0。',['主机灾难与权威自身回滚验收'])
add('E03','M2四条原生采样及评分修订/本地补核分别保留。','有限原生实测','四条各一次；旧同可信OS用户布局',
 ['原始报警保留','补核不追认为原调用'],[('mainline_native_casdoor_v1/COST_AND_RESULTS.json','original/reviewed scores'),('mainline_native_casdoor_v1/review/SCORER_CORRECTION.json','M2-03'),('mainline_native_casdoor_v1/supplement/RESULT.json','M2-04本地补核')],{'native_samples':4,'raw_PASS':3,'raw_alert':1,'reviewed_PASS':4,'HTTP':114},
 ['M2-03 A1运行态未知但评分者见其接受；M2-04原中断期接纳未执行'],'NATIVE_TRACE_AND_EXPLICIT_OFFLINE_CORRECTION',
 '原报警经离线启动顺序复核修正，原生不重采；M2-04另有零原生本地补核。',['当时未知A1关闭不由后续清理知识补写'])
add('E04','M3在预启用标识日志条件下完成精确点读关闭。','已有方法覆盖','两条受限未知创建实例',
 ['标识日志','精确点读授权','单发送/单效果','B保留'],[('mainline_native_reconciliation_v1/COST_AND_RESULTS.json','native_verdicts/73HTTP'),('mainline_native_reconciliation_v1/CAPABILITY_AND_CLOSURE_CONDITIONS.md','关闭前提')],{'native_samples':2,'PASS_CLOSED':2,'HTTP':73},
 ['标识完全丢失不在本分支；早期UNKNOWN是本地无发送信息'],'CONDITIONAL_MATURE_METHOD_COVERAGE',
 'M3验证标识点读分支，保持其标识持久记录前提。',['任意多未知来源与截止类覆盖'])
add('E05','M4专用组织授权使无标识受限实例可关闭。','已有方法覆盖','两条一次性轨迹；组织整体授权，记录上界50',
 ['新组织/应用/三账户','单页100≥50','完整来源及单效果'],[('mainline_native_unidentified_v1/COST_AND_RESULTS.json','最终98HTTP'),('mainline_native_unidentified_v1/QUERY_SCOPE_AND_AUTHORIZATION.md','授权'),('mainline_native_unidentified_v1/cleanup_repair_RESULT.json','应用组织字段修复与回读')],{'native_samples':2,'PASS_CLOSED':2,'HTTP_including_cleanup_repair':98},
 ['共享组织精确账户过滤仍未解决；初次新增候选空不排除迟到创建'],'DEPLOYMENT_CONDITIONAL_NATIVE_COVERAGE',
 '额外组织级授权、费用及清理修复作为成立条件登记。',['共享组织账户级授权；无界记录/多页一致性'])
add('E06','M5为合成provider下的独立权限域与托管通道证据。','部署权限证据','12场景各一次；登记目录/PID；Windows受限主令牌',
 ['可信OS/管理员','正向控制'],[('mainline_agent_isolation_v1/CUSTODY_ACCEPTANCE_REPORT.md','完整范围'),('mainline_agent_isolation_v1/M5_AGGREGATE.json','12 PASS/native0')],{'scenarios':12,'PASS':12,'regression_tests':141,'native_samples':0},
 ['旧环境凭据目录不在M5登记对象中；整体主机沙箱/侧信道未验收'],'FINITE_OS_PERMISSION_ACCEPTANCE',
 'M5支持登记对象的实际文件/进程/角色边界，材料为合成值。',['全局主机对象及生产浏览器状态'])
add('E07','M6两条联合轨迹支持当前原生隔离profile。','有限原生实测','单机/单活/可信在线权威/专用组织/收紧环境ACL',
 ['可信R/OS','独立审计私钥','受控写入者','指定UserInfo'],[('mainline_native_isolation_v1/ACCEPTANCE_REPORT.md','本批范围及字段口径'),('mainline_native_isolation_v1/batch01/RESULTS.json','2条/84HTTP'),('mainline_native_isolation_v1/COST_AND_RESULTS.json','各43检查/148回归')],{'native_samples':2,'PASS_KNOWN_DISPOSAL':1,'PASS_CLOSED':1,'check_items_each':43,'HTTP':84,'regression_tests':148},
 ['43检查不等于43独立采样；回归不等于原生样本'],'JOINT_PROFILE_FINITE_ACCEPTANCE',
 '当前profile取得两条联合原生与OS权限轨迹，结论限于登记合同。',['多活/跨机/灾难与任意RP效果'])
add('E08','M6的原凭据可读发现和额外ACL授权为必要部署前提。','部署权限证据','原.runtime/l1及其继承ACL；1241对象备份',
 ['可信用户/SYSTEM保留访问','历史失败不抹除'],[('mainline_native_isolation_v1/EXISTING_DEPENDENCY_PERMISSIONS.json','原权限'),('mainline_native_isolation_v1/AUTHORIZATION_ADDENDUM.json','研究者授权'),('mainline_native_isolation_v1/FINAL_ACL_REVIEW.json','公钥计划内追加R2只读')],{'ACL_objects_backed_up':1241,'native_samples':2},
 ['恢复Users读取会改变当前profile；公钥R2授权不等于私钥放宽'],'EXPLICIT_DEPLOYMENT_PREMISE',
 '原生采样前发现并在明确授权后修复环境凭据权限，原值与计划内共享公钥ACL转换均保留。',['其它未登记全局对象'])
add('E09','M6-02的CLOSED是带来源/完整性/截止前提的关闭收据。','已有方法覆盖','一个A未知刷新、B合法保留，原生单Find快照',
 ['唯一未知来源','四批准总预算40','页容量100','每发送最多一单位','其他创建者排除','已知单位处置'],[('mainline_native_isolation_v1/batch01/M6-02/trusted/runner/closure_receipt.json','facts/evidence/remaining_creation_bound'),('mainline_native_isolation_v1/NATIVE_ISOLATION_PROFILE.md','four-grants-single-Find-single-effect')],{'native_samples_supporting_this_instance':1},
 ['空列表后迟到创建；两个未知来源；多发送；每请求多效果'],'CONDITIONAL_RECEIPT_AND_NATIVE_INSTANCE',
 '在登记源模型与部署条件下，该未知尝试剩余创建上界为0并完成已知材料处置，运行态义务空。',['任意后代图/未知写入者的一般保证'])
add('E10','RT内省inactive、刷新响应拒绝、资源拒绝分别观察。','问题形式化','版本化证据读取接口；所有历史数据只读',
 ['原响应与冻结生产者定位'],[('mainline_native_isolation_v1/source_frozen/scripts/measure_native_casdoor.py','READ_ONLY_INTROSPECTION分支'),('auth-lifecycle/src/auth_lifecycle/online_state/evidence_semantics.py','normalize_material'),('auth-lifecycle/scripts/measure_native_casdoor.py','v2显式字段')],{},
 ['HTTP200撤销不自证失效；HTTP错误/缺少新材料不自证无创建效果'],'SOURCE_BOUND_SEMANTIC_CORRECTION',
 'RT内省inactive只作为该查询声明，实际刷新请求与响应单独记录；UserInfo为指定资源接受观察。',['其它接受路径与未来创建能力的独立证据'])
add('E11','原生data2是计数观察，不是页数或完整性证明。','问题形式化','Casdoor4.25.0 GetTokens及分页依赖',
 ['冻结源码与原响应对应','count/Find分别读取'],[('research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/controllers/token.go','GetTokens count/NewPaginator/ResponseOk Nums'),('mainline_research_closure_v1/sources/beego_v2.3.8_paginator.go','Nums L50–51 与 PageNums L37–41分开'),('auth-lifecycle/src/auth_lifecycle/online_state/evidence_semantics.py','normalize_query')],{},
 ['计数相同但集合变化；页容量不足遗漏'],'SOURCE_BOUND_SEMANTIC_CORRECTION',
 '旧reported_pages映射为native_reported_count，完整性另依据记录上界和单Find快照。',['通用多页一致性保证'])
add('E12','逻辑序列化字节、WAL留存大小与物理I/O分别计量。','实现符合性','M1—M6成本账本的实际指标',
 ['指标定义与缺测保留'],[('mainline_native_isolation_v1/COST_AND_RESULTS.json','logical_snapshot_bytes_written/physical NOT_MEASURED'),('mainline_online_state_v1/M1_AGGREGATE.json','指标代理口径')],{},
 ['WAL文件大小受检查点影响，不能直接作设备写入字节或fsync次数'],'MEASUREMENT_SCOPE',
 '逻辑字节与文件尺寸作为各自代理指标；未测物理写入和fsync不补成零。',['设备/文件系统层测量'])
add('C01','当前新增密码学功能需求与严格分离均未成立，辅助线冻结。','密码学原创候选','当前已确认托管/在线权威合同及审查范围',
 ['沿用研究者未确定受限披露参与方答复','不凭缺平台能力制造密码增量'],[('研究/密码学辅助_一致性核验/revisions/crypto_state_cost_review_2026-11-05/DECISION.md','条件覆盖与冻结'),('研究/密码学辅助_一致性核验/revisions/contract_decision_2026-11-05/CONTRACT_DECISION_CARD.md','ONLINE_TRUSTED_STATE_V1'),('mainline_native_isolation_v1/MAINLINE_EVIDENCE_MAP.md','冻结状态')],{'strict_separation_instances':0,'new_crypto_candidate_code_this_round':0},
 ['成熟签名/事务/当前权威覆盖；缺真实职责或同条件差距'],'FROZEN_NOT_ESTABLISHED',
 '现有密码机制承担支撑职责，当前无充分新增密码协议原创依据。',['确认需求、最强组合不足、严格差距及完整成本信任链'])
add('C02','七项淘汰机制与密码学候选B不因工程验收复活。','已有方法覆盖','已审查机制与同能力通用方法',
 ['算法研究B与密码学候选B分开'],[('research_secret_recipe/REPORT.md','§1.2 A2/A3/B2/B3/AB2/AB3/B4'),('研究/密码学辅助_一致性核验/revisions/credential_contract_2026-11-05/CRYPTO_REQUIREMENT_DECISION.md','候选B当前主线身份终止')],{},
 ['把命名、单实现低效或工程符合性包装成新颖性'],'COVERED_OR_ARCHIVED',
 '既有淘汰和归档判断保留，M1—M6只增加对应工程与部署证据。',['若重开须完整可证伪分离链'])

ledger={'schema':'mainline-claims/1','date':'2026-11-06','native_requests_this_round':0,'crypto_line':'FROZEN',
        'review_kind':'current research-process internal audit; no external independent peer review',
        'category_legend':['问题形式化','条件性理论','已有方法覆盖','实现符合性','有限原生实测','部署权限证据','算法优势假设','密码学原创候选'],
        'claims':rows}
(OUT/'CLAIMS.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# 论文主张—证据矩阵','', '机器登记以CLAIMS.json为准。以下主张类别与量词均保留；哈希一致仅支持原字节对应。','',
       '| ID | 类别 | 主张/允许表述 | 证据等级 | 关键缺项 |','|---|---|---|---|---|']
for c in rows:lines.append('| '+c['id']+' | '+c['category']+' | '+c['paper_wording']+' | '+c['evidence_level']+' | '+'；'.join(c['missing_key_evidence'])+' |')
lines+=['','最多三项论文核心贡献：F01–F03的问题及条件规格；T01–T02的M_r资源理论（优先权近邻未决）；E01–E09的分层实测与成熟组合工程证据。它们不构成三个独立算法/密码学优越性结论。','',
         '当前唯一优先动作沿用TOPIC-THEORY-1：核查/证明A-E见证候选枚举界，或给出精确障碍。算法—持久层最小接口缺口登记后暂存，不以扩平台或机制实现代替该证明门。']
(OUT/'CLAIM_EVIDENCE_MATRIX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'claims':len(rows),'categories':len(ledger['category_legend']),'native_requests':0}))
