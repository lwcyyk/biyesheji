"""Produce formal review data and twelve reports. No runtime mechanism code."""
from pathlib import Path
import hashlib,json,collections
O=Path(__file__).resolve().parent.parent;P=O.parent;E=O/'evidence'
def j(n):return json.loads((E/n).read_bytes())
def save(n,x):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def text(n,s):
 with(O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
C=j('FINAL_COUNT_CLOSURE_CALCULATION.json');G=j('FINAL_EVIDENCE_DEPENDENCY_GRAPH.json');K=C['raw_nonarchive_upper'];assert K==4450
oldG=G.copy();G['nodes']=list(G['nodes']);G['edges']=list(G['edges'])
# Family schemas represent optional cardinality slots. They are not additional
# physical files on top of the 1,082 witness leaves.
family_records=[]
for f in C['families']:
 i='FAMILY_'+f['id'];dep=['PROGRAM_BYTES','STATIC_INPUTS','FORMAL_ADMISSION' if f['id']=='MODEL_FILES' else 'T0_AND_CAL_LEDGER_PREFIX']
 r={'evidence_id':i,'producer':f['id'],'source_path':'<ROOT>/'+f['id']+'/<frozen-pattern-or-temporary-slot>',
 'content_hash':None,'evidence_type':'bounded_evidence_family_schema','required_by':'Complete source-derived namespace envelope',
 'verification_rule':f['basis'],'storage_requirement':'Preserve every produced original; schema slots do not assert file existence',
 'retention_requirement':'Original bytes/paths/types/hashes retained; no deletion from classification','dependency_ids':dep,
 'max_cardinality':f['count'],'family_member_paths':f.get('paths'),'contract_scope':'STATIC_UPPER_SCHEMA_NOT_RUNTIME_OBJECT'}
 family_records.append(r);G['nodes'].append(r);G['edges'].extend([[d,i] for d in dep])
G['schema_cardinality_is_additional_files']=False
ids={n['evidence_id'] for n in G['nodes']};adj={i:[] for i in ids};indegree={i:0 for i in ids}
for a,b in G['edges']:assert a in ids and b in ids;adj[a].append(b);indegree[b]+=1
queue=collections.deque(i for i in ids if indegree[i]==0);order=[]
while queue:
 a=queue.popleft();order.append(a)
 for b in adj[a]:
  indegree[b]-=1
  if not indegree[b]:queue.append(b)
assert len(order)==len(ids)
G['topological_order']=order;G['acyclic']=True
save('evidence/EVIDENCE_GRAPH_DELIVERY.json',G)
save('evidence/EVIDENCE_FAMILY_SCHEMAS.json',{'families':family_records,'physical_upper_sum':sum(r['max_cardinality'] for r in family_records),
 'schema_nodes_are_not_extra_files':True,'leaf_hashes_unrun':True})

current=['boot_id','execution_lock','systemd unit instances/InvocationIDs','UID/GID/groups','runtime/ELF/map identity',
 'budget counter/intent/journal health','T0/deadline/stop_at','WORK/C00','real C09 ACK/waitpid/fresh classification',
 'normal ManagerRecovery health and current supervision','RLIMIT_AS/TasksMax/cgroup restrictions','current independent stop source and closure preconditions',
 'C00-C12/BC/IPC/C09H/MR64/PT/PF/TR/RA/S34/gate18 as current contract requires','current original-byte rechecks and all other resource-gate mandatory fields']
requirements=[
 ('R01','POLICY_AUTHORITY','Current explicit user approval of this exact rule digest plus a separate fresh authorization for target B'),
 ('R02','A_UNIQUE_NATIVE_ORIGIN','Distinct A batch/boot/InvocationID/PID/source lock; actual unit exit79 and raw journal/query events, never a simulation flag alone'),
 ('R03','SOURCE_PAIR_RELATION','A/B exact artifact locks both explicitly reviewed; security-relevant code has identical projected AST under a closed, per-node namespace-only map'),
 ('R04','SAME_BOOT_TCB','A.boot==B.boot; exact kernel/systemd/Python/loader/libc/libm/TCB fingerprints and effective sandbox contract match; actual B refreshed'),
 ('R05','FAULT_SCOPE','Only dedicated current service failure -> unreviewed failed-unit detection -> main A automatic close with Root/stopper otherwise available'),
 ('R06','PRIMARY_AUTOMATIC_CLOSE','A STOP/CLOSED/role exits/group empty/budget and deadline preservation confirmed; fallback/manual cleanup alone cannot satisfy this class'),
 ('R07','INDEPENDENT_RAW_ORACLE','Named independent checker hashes and re-evaluation of immutable raw originals; shared parser/TCB assumptions disclosed'),
 ('R08','SEALED_ARTIFACTS','A native and administrative seals completed and separately verified; missing/partial/UNKNOWN status refuses the capability-observation class'),
 ('R09','POSTSEAL_CERTIFICATE','Certificate written after A seals, outside both sealed preimages; commits both archive/manifest hashes and actual oracle result'),
 ('R10','TARGET_B_USE_BINDING','One predeclared B batch/boot/lock + fresh use nonce + approval digest + certificate hash. Use spec precedes B receipt; realized record follows receipt'),
 ('R11','CURRENT_B_PROOFS','Every listed current-instance obligation is independently checked by B; A approval cannot grant B WORK/RESOURCE_GATE or change budgets'),
 ('R12','INVALIDATION','Boot, source, TCB, fault scope, approval or target/use mismatch invalidates; no wildcard new target or indefinite cached admission'),
 ('R13','FRESH_OPERATOR_AUTH','Current B direct user authority pins certificate/policy/use-spec hashes; withdrawn or superseded authority rejects; no unproved monotonic registry assumption'),
 ('R14','EVIDENCE_COMPLETE','Every required raw/member/source artifact available and bound; missing/extra/substituted/cross-version files reject')]
attacks=[
 ('old_version_replay','R03/R10/R12','Reject different exact artifact pair, projected security core, rule digest or target lock'),
 ('fake_abnormal_close','R02/R06/R07','Reject claimed FAIL/PASS without current native event and automatic STOP/CLOSED/exits'),
 ('simulation_as_native','R02/R05','Reject MR-SIMULATION/1 or host-shaped data without raw OS provenance'),
 ('wrong_source','R03','Reject uncontrolled normalization, changed guard/operator/constant/call graph or missing pair review'),
 ('wrong_boot_batch','R02/R04/R10','Reject mismatched A identity, different current boot or wrong B target'),
 ('fault_not_triggered','R02/R05','Reject normal exit, wrong status/code/InvocationID/PID or missing matching journal event'),
 ('exit_unconfirmed','R06/R07','Reject missing waitpid/role/current cgroup emptiness facts or caller_exit_pending unclosed'),
 ('fallback_only','R06','Keep FALLBACK_CLEANUP_ONLY/UNKNOWN; reject primary automatic capability class'),
 ('partial_seal','R08/R14','Reject absent member/manifest, byte/hash/type/path mismatch or unresolved archive status'),
 ('shared_checker_error','R07','Disclose same-parser common-mode TCB; require rule independence plus independent raw review. Avoid universal independence claims'),
 ('missing_replaced_file','R14','Reject absent original, wrong digest/path, member set mismatch or forged content-to-identity relation'),
 ('budget_window_transfer','R11','Reject A counter/T0/deadline/receipt used as B current resource facts'),
 ('stale_B_current_state','R04/R11','Reject stale C00/real C09/current supervisor/state regardless of valid A certificate'),
 ('use_nonce_replay','R10/R13','Reject duplicate B activation or a use record outside exact freshly authorized target; no new free window'),
 ('certificate_self_hash_cycle','R09/R10','Reject contract requiring certificate inside its own earlier archive or receipt/use-record mutual hashes')]
projection={'status':'PENDING_ARTIFACT_PAIR_REVIEW','algorithm_implementation':'NOT_IMPLEMENTED',
 'required_equal':['MR classify/health/abort/stop/supervision logic','budget and durable C09 protocol semantics','RootIPC permission/ownership rules',
 'PreT0/PT/PF/TR active/terminal policies','resource caps, file/type/hash limits, runtime pins and fault scope'],
 'only_candidate_differences':['Explicit namespace literals at individually listed AST node coordinates for batch/root/service/control/authorization filenames'],
 'must_not_ignore':['Versions','guard branches/operators/calls','numerical resource/safety constants','UID/GID/modes/ACL flags','runtime digests','fault exit expectations','test/qualification requirements'],
 'mapping_record':['file','AST_coordinate','old_literal_sha256','new_literal_sha256','namespace_role','A_artifact_sha256','B_artifact_sha256','review_authority'],
 'unsafe_alternatives_rejected':['Blind text replacement','Ignore all strings','Version label equality without bytes','Accept arbitrary digest chosen by certificate producer'],
 'current_approved_pairs':[],'reason':'Batch identity and fixed namespace are currently embedded in sources; whole-package byte equality is impossible across two fresh namespaces without an explicit reviewed relation.'}
rule={'schema':'MR-CROSS-INSTANCE-OBSERVATION-RULE/1-DRAFT','version':'EvidenceContract-Closure/review-1','user_approved':False,
 'runtime_enabled':False,'recommendation':'APPROVE_RECOMMENDED_CONDITIONAL_RULE_ONLY','evidence_usable_now':False,
 'only_admitted_class':'OBSERVED_IMPLEMENTATION_RESPONSE_FOR_ONE_NATIVE_SERVICE_FAILURE_SCENARIO',
 'conclusion_strength':'A particular native A trace was accepted under the locked assumptions; no universal future-instance shutdown theorem',
 'same_boot_required':True,'one_target_B_only':True,'source_projection':projection,'requirements':[{'id':i,'name':n,'predicate':p} for i,n,p in requirements],
 'current_B_obligations':current,'forbidden_promotions':['B shutdown already occurred','All B supervisors are healthy','B budget is safe','B current resources valid',
 'B real C09 passed','B RESOURCE_GATE_PASS','A budget/deadline/authorization transfers to B'],
 'validity':'Exact approved artifact pair, scenario, runtime/sandbox TCB and same boot, one fresh B use authorization; any relevant change/refusal/revocation invalidates',
 'certificate_location':'Outside A ROOT and outside A native/admin archive preimages, after final A read-only verification',
 'qualification_effect':'Only replaces the strengthened same-instance abnormal-scenario evidence obligation if explicitly approved; all current-instance checks and independent budget windows remain mandatory',
 'formal_effect':'Environmental evidence assumption, not D1/D2 proof, current execution safety proof, cryptographic claim or original architectural separation'}
save('proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json',rule)
save('proposals/SOURCE_PAIR_REVIEW_REQUIREMENTS.json',projection)
save('proposals/ATTACK_REJECTION_MATRIX.json',{'attacks':[{'attack':a,'requirements':r,'rejection':x} for a,r,x in attacks],
 'execution_status':'DESIGN_ONLY_NO_NEW_ATTACK_TESTS_RUN','pending_test_inputs':'Freeze after rule approval and implementation review; historical15 mutants do not prove this future rule'})
certificate={'schema':'MR-OBSERVED-NATIVE-CAPABILITY/1-DRAFT','produced':False,'runtime_authority':False,
 'fields':['policy_digest','A_unique_identity','A_source_execution_input_locks','A_projected_core_and_review_reference','A_runtime_and_effective_sandbox_fingerprints',
 'A_boot','fault_scenario_and_unit_InvocationID_PID','raw_fault_log_query_hashes','STOP_CLOSED_and_role_waitpid_refs','budget_before_after_and_original_window',
 'native_manifest_and_zip_hashes','admin_manifest_and_zip_hashes','postexit_cleanup_verdict','independent_oracle_program_and_result_hashes',
 'retained_unknowns_and_conditional_provenance','scenario_scope','creation_observation'],
 'preconditions':['A actually CLOSED','Native and admin artifacts independently verified','Primary automatic path confirmed','Post-exit caller/stopper exits confirmed'],
 'B_use_spec_fields':['certificate_hash','rule_hash','reviewed_artifact_pair_hash','target_B_batch_id','target_B_boot_id','target_B_execution_lock','fresh_use_nonce','purpose'],
 'no_hash_cycle_order':['A native seal','A administrative seal','A post-seal certificate','B use_spec','B authorization receipt binding use_spec hash','B realized use record binding authorization hash','B current gate evaluation'],
 'missing_fields_fail_closed':True,'ready_for_issue':False}
save('proposals/MR_CERTIFICATE_AND_USE_SCHEMA.json',certificate)
save('proposals/CAPACITY_CONTRACT_DRAFT.json',{'schema':'DCL-EVIDENCE-CAPACITY/2-DRAFT','effective':False,'user_approved':False,
 'closed_world_count_envelope':{'raw_nonarchive':4450,'native_members':4451,'admin_runtime_originals':4452,'admin_final_members':4467},
 'derivation_sha256':hashlib.sha256((E/'FINAL_COUNT_CLOSURE_CALCULATION.json').read_bytes()).hexdigest(),
 'old_guards_preserved':{'admin_runtime_originals':256,'native_members':257},
 'unchanged_byte_and_time_limits':{'native_uncompressed':33554432,'native_compressed':33554432,'admin_runtime_bytes':33554432,'manifest':4194304,
 'terminal_read_seconds':5,'post_exit_admin_seconds':30,'calibration_seconds':300,'global_seconds':1800},
 'activation_blockers':['Raw C09 pending append record/byte/work quota unresolved','Aggregate raw/admin bytes and single-file bounds not derived','Full IO/decompression/memory proof and new-source/current-lock integration not established',
 'New explicit user approval required for any numeric guard update'],
 'status':'COUNT_FORMULA_CLOSED_CONDITIONALLY_VOLUME_AND_WORK_UNRESOLVED','new_packaging_code':False})
V={'baseline_frozen_calibration':68498,'baseline_version':'RuntimeAdapt-static-1/r1','actual_new_visits':0,'T0':None,'deadline':None,'R':None,
 'proposed_A_bound_if_existing_prefix_plus512_integrated':69010,'A_approval':'NOT_GRANTED','A_window':'independent new authorized T0_A/deadline_A/R_A; no A-to-B ledger merge',
 'new_B_bound_formula':'68498 + V_cert_current_verification + V_new_volume_work_checks + V_added_native_test_oracles - provably shared prepayments',
 'new_B_numerical_bound':None,'prior_71618':'Prior AdmissionFix estimate conditional on unintegrated79-job32+1 fee plan; not a frozen valid bound for this rule',
 'source_pending_append_quota':None,'raw_byte_upper':None,'single_file_global_upper':None,'accepted_artifact_uncompressed_cap':33554432,
 'bounded_individual_examples':{'counter':24,'C03_shared':16777216,'readiness_row_max':131072,'readiness_rows_max':602,'manifest_accept_max':4194304},
 'readiness_independent_rows_byte_bound':602*131072,'archive_verifier_conditional_work':'O(K + B); K<=4450 and B<=32MiB only for admitted artifacts; two archive scans<=64MiB plus raw cross-checks. Does not bound uncapped native builder input or C09 log production.',
 'all_resource_caps':{'global_visits':1000000,'calibration_visits':100000,'global_seconds':1800,'calibration_seconds':300,'TCB_preT0':120,'stop_relative':1740,'AS_bytes':1073741824,'parent_tasks':4},
 'time_guarantee':'UNRESOLVED','reason':'No finite record quota for pending C09 log; no locked fee policy for pending rule; no new native execution authorized'}
save('evidence/RESOURCE_AND_WORK_MODEL.json',V)
save('evidence/SOURCE_PROOF_REVIEW_NOTES.json',{'final_raw_upper':4450,'scope':'Conservative manual source proof checked by arithmetic/AST/hash analysis; not full formal verification of CPython/kernel execution',
 'review_adjustments':[{'draft':4378,'delta':48,'basis':'Allow an intent temp retained under mutant_retained and recreated at original path'},
 {'delta':24,'basis':'Include G.atomic rendezvous temp files for two concurrent scenarios'}],
 'count_vs_bytes_counterexample':'602 readiness rows times131072 permits78,905,344 bytes before all other files; individual caps do not imply aggregate32MiB fit',
 'normal_and_failure_schemas':'Union envelopes; unused branches/slots conservative, no physical duplicate removal or double counted leaf promoted to extra slot',
 'source_loop_volume_obstruction':'C09 pending log append has no step/record/byte counter; time alone lacks a frozen minimum operation time.',
 'source_missing_export':'Separate full current boot/unit journal export is lock-described but not a ROOT automatic producer. A concrete read-only export plan must declare its fixed files and byte/work bound; convenience research reports never reopen native seal.'})

passport='Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。'
tail='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。'
def doc(n,title,s):text(n,f'# {title}\n\n{passport}\n\n{s}\n\n{tail}')
doc('EVIDENCE_DEPENDENCY_GRAPH.md','证据依赖图与对象分类','''
阶段/版本敏感的交付图共1142个对象/族节点，拓扑排序通过。1082个计划输出叶保持content_hash=null；16个有界族节点表达可选槽位，未额外加算为物理文件。完整记录提供evidence_id、producer、source_path、content_hash、evidence_type、required_by、verification_rule、storage/retention_requirement和dependency_ids。

```mermaid
flowchart LR
 S[源码与静态输入] --> L[manifest与执行锁]
 L --> R[当批运行身份与原始事实]
 R --> Q[当批校准与资格证明]
 Q --> F[正式模型输出]
 F --> T[终态只读审查]
 T --> N[native manifest与ZIP]
 N --> A[行政审查与ZIP]
 A --> Z[最终收据]
 Z --> C[封存外的事后证书]
 C --> U[新B的use_spec与独立授权]
 U --> B[B当批检查及待批准的限定承认]
```

图中通用封存次序用于说明层级。实际机器图将旧完整正常轨迹、异常前缀替代轨迹、独立MR专项A和待批准B分别标注scope；专项A在C10后关闭，依赖图没有要求A先生成F1/F4。失败前缀仅保留已产生原件，未运行后续测试继续UNRUN，不能据此取得资源门。

|类别|对象|合同地位|
|---|---|---|
|原生原始事实|boot/InvocationID/PID、ACK/waitpid、实际单位与STOP/CLOSED、预算字节、角色/组状态、原始日志|当批强制原件；跨实例仅限拟批准的特定故障观察|
|测试输入与身份|冻结程序/输入、manifest/锁、授权、激活与当前票据|强制身份绑定；新旧实例保持区分|
|独立验证结果|MR/IPC/BC/S34/gate/模型输出|可确定性重算的部分仍按现合同保留；反例轨迹字节具有单独保全责任|
|manifest/完整性证明|native/admin清单、成员hash、包hash|强制完整性集合；排除自己的hash前像|
|行政审查报告|post-exit审查、调用/关闭说明、研究报告|正式post-exit输出与便阅材料分别标注；研究报告位于运行收集目录之外|
|归档封存元数据|native/admin ZIP、最终收据、拟议事后证书|逐层产生；后层不写回前层sealed preimage|

历史TR-A2、旧失败与UNKNOWN保留原身份，当前计划叶未借用其摘要。全量journal外部导出还需固定生成计划/边界；当前自动ROOT生产者与锁中的命令描述分别列示。

[完整机器图](evidence/EVIDENCE_GRAPH_DELIVERY.json) · [族槽位与边界](evidence/EVIDENCE_FAMILY_SCHEMAS.json)。''')
doc('EVIDENCE_RECURSION_AUDIT.md','递归、自摘要与封存层级审查','''
现行冻结收集边界没有形成自动扩张的证据递归。guard.seal收集ROOT常规原件并按文件名排除EVIDENCE_MANIFEST.json/EVIDENCE.zip，随后加入manifest一次；行政快照和报告写在ROOT之外，host manifest不收集其自身、最终ZIP或含该ZIP摘要的最终收据。额外研究报告也位于收集前像之外。

三条最小潜在环需要在合同中显式阻断：

1. 事后MR证书→native manifest→native ZIP→事后MR证书。触发条件：验收器要求先看到native/admin seal，同时证书被要求在创建该native包之前进入ROOT。新oracle的from_snapshot需要事后admin证明；其未接入入口，当前属于接线风险，未作为已发生动态循环。
2. 最终行政收据→admin manifest→admin ZIP→最终行政收据。触发条件：把包含admin ZIP hash的最终收据纳入同一个ZIP。现有层级已经切断。
3. B授权收据↔B最终use record。触发条件：授权绑定use record hash，use record又绑定该授权hash。草案采用独立use_spec→授权收据→实际use record，顺序单向。

机器图按文件的阶段版本区分预算前缀/终态预算、pre-native review/post-seal review，避免将原地更新的同一文件名误当成自引用hash。模型中的可重算报告与用户便阅报告不反向增加更早的必需集合。证据分类不会删除原件。

每个环都有明确触发条款和切断位置。将环反复展开不会产生有效的无限文件要求；它首先构成不可同时满足的hash/先后约束。固定点由分层集合求得，包内嵌已有ZIP只按当前层一个成员计数，内部完整性仍逐件核验。

[候选最小环与拓扑顺序](evidence/EVIDENCE_GRAPH_DELIVERY.json) · [源行证据](evidence/SOURCE_EXCERPTS.json)。''')
rows='\n'.join(f"|{f['id']}|{f['count']}|{f['basis']}|" for f in C['families'])
doc('EVIDENCE_COUNT_CLOSURE_PROOF.md','数量闭包与保守上界证明',f'''
在锁定程序/输入、受控ROOT封闭写入域、Restart=no、一次激活/最多一次C09恢复、固定演员/线程和首错展开的前提下，得到保守源级包络：K≤4450。该值由以下互斥路径族及临时对象族相加推导，当前运行未产生这些文件。

|路径族|槽位上界|来源|
|---|---:|---|
{rows}
|合计K|4450|保守联合包络，未声称为可同时达到的最小精确最大值|

源级封闭性：固定目标的覆盖写增加文件内容版本，不增加成员；G.atomic的临时名由目标＋固定PID/TID决定；S34最多48个实际actor。intent临时件移入mutant_retained后可在原路径重建，因此每actor计当前intent、保留intent、fact三个槽位。G.atomic另计并发rendezvous的12个目标及其临时件，避免遗漏。Root随机临时名按有界调用次数计，未按随机值空间臆造容量。

关闭调用展开：C_abort≤2×3＋2×4＋2=16（两个scheduler每个最多fail/两层异常；两个协调阶段每个最多四层关闭责任；external两层）；abort内部无递归abort。C_stop≤16＋4＋1＋1＋1=23；动态stop_event/result每次≤2，共46；STOP/CLOSED/first_failure/close_state/external_closing为最多5个固定异常目标，已在固定族计入。C_seal_attempt≤1＋2＋2＋1＋1=7。随机BC临时件341及Root publish临时件96按这些调用配额逐项界定。未成功停止/未确认回收继续UNKNOWN，文件上界本身不推导关闭成功。

1082的构成逐项为312回归raw＋238 C09H事件/oracle＋56 IPC raw＋40 BC raw＋170个S34最低原件＋71个预算异常原件＋195模型输入/输出。1083再加入一个native manifest。该下界去重后1082条路径互异；后来增加的上界族只为尚未覆盖的文件类型、可选分支和临时件提供包络，图中schema节点不再作为额外文件计入。

层级固定点：以K表示排除native manifest/ZIP的运行原件，native ZIP成员=K＋1；native封存后行政运行原件=K＋2；行政最终ZIP再加10 host侧件、4 source lock及1 manifest，为K＋17。故完整成功轨迹：原件1082≤K≤4450，native成员1083…4451，行政导出原件1084…4452，行政ZIP成员1099…4467。原用户1082行政下界仍成立，精细层级表达揭示额外两份native封存文件。

现有256/257接受集合中的完整成功轨迹为空；上述区间描述源产物/拟议容量包络，未声称旧守卫接受。全范围、额外外部写入者或自动重试若改变，当前上界失去适用性，需重算。新增测试集合J时按新增固定目标、actor/临时对象、Root调用上界和封存侧件作并集，再求相同分层固定点；同路径更新不重复加算。

字节/工作量仍为EVIDENCE_MAX_BOUND_UNRESOLVED：C09 PENDING退出见证循环反复向一个固定日志追加记录，源码没有记录数/字节配额，访问上限也未给此循环收费。固定时间截止没有提供单操作最短耗时公理。故可构造任意n次PENDING的合同模型前缀，文件数恒定而日志字节/读验工作增长；此处未声称物理机器能在固定时间实际完成任意n。

602条就绪记录各≤131072，独立逐条上限组合已允许78905344字节，高于32MiB；实际是否达到该组合待测，单项cap无法推出总量保证。完整RAW单文件/总字节/构建与验收期限继续未闭合。4450属于带明确前提的人工源级证明，算式/AST/hash已核对，尚无CPython/内核完整语义机械证明。

[最终算式与S34逐job表](evidence/FINAL_COUNT_CLOSURE_CALCULATION.json) · [原始1082路径](evidence/HISTORICAL_REFERENCES/DCL-R6-FullChain-AdmissionFix/evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json) · [待闭合日志规则](evidence/FINITE_FIXED_POINT.json)。''')
doc('ADMIN_NATIVE_CAPACITY_CONTRACT.md','容量合同草案与生效边界','''
版本DCL-EVIDENCE-CAPACITY/2-DRAFT仅供批准审查；effective=false。旧admin256/native257守卫和所有旧64份运行源码保持原字节。

|对象|推导包络|现行界|状态|
|---|---:|---|---|
|pre-native运行原件|4450|无独立统一count字段|源模型上界|
|native ZIP成员|4451|257|拟议数量合同字段，尚未生效|
|行政导出运行原件|4452|256|拟议数量合同字段，尚未生效|
|最终行政ZIP成员|4467|旧256＋14＋1=271|包括native两文件和host/source侧件|
|解压/压缩/导出字节|原32MiB分别保留|32MiB|源总量保证未闭合|
|manifest、终态读取、行政期限|4MiB、5秒、30秒保持|同左|完整工作量保证未闭合|

新数量字段的来源为固定源/输入及临时件、异常展开公式，已避免任意选择2048/4096。它们属于保守包络，不会自动更新执行合同。需要先补齐raw日志及聚合字节/内存/时间义务，再取得具体版本的新明确授权。

原件路径/类型/权限/身份/hash、逐成员独立读取、重复/缺失/多余成员拒绝、跨批次替换拒绝、部分包UNKNOWN/FAIL和压缩资源界全部保留。新count不能作为放宽字节或期限的依据。原生seal的证明责任、CLOSED拒绝与只读接口保持。

32MiB接受界仅约束被接受的归档；当前native构建器在生成清单前遍历/散列ROOT，未统一限制所有输入文件字节。因此接受上限不能循环用作所有源产物的生成上界。

[可供明确批准的容量草案](proposals/CAPACITY_CONTRACT_DRAFT.json)。''')
doc('EVIDENCE_CAPACITY_OPTIONS.md','C1与C2工程方案比较','''
|项目|C1：版本化数量上限|C2：标准归档分段|
|---|---|---|
|证据字节|逐原件保留现行路径与hash|逐原件保留，根manifest绑定有序完整分段及各自清单|
|完整集合|整包成员集合＝完整manifest集合|分段ID集合必须与根manifest完全相等，任一缺段/重复/额外段拒绝|
|独立oracle|读取全部原件及每个包成员|读取所有分段和全部成员，跨段路径唯一、分段hash/全局原件hash都匹配|
|资源|固定总字节和总工作量，修改count须批准|逐段界与所有段总量/工作量同时限制，避免分段放大总许可|
|当前工程变动|原格式容量字段、相应读验/导出界及版本绑定|需要新的分段组织合同/清单与读验接线，当前合同尚未承认|
|当前建议|优先；数量包络已有，字节/工作量仍待闭合|备选标准工程方案；当前只做规则比较|

C2可采用现成标准ZIP/tar＋版本化根manifest，属于COVERED_BY_G。当前严格分离实例仍为0；没有新封装代码、研究候选机制或未经批准的分段承认实现。

C2的完整性证明以集合等式为核心：根清单确定必需原件集合E和完整分段集合S；每段的hash/成员清单与根绑定，oracle验证分段索引双射及所有原件hash；缺任一s∈S或任一e∈E均拒绝。只提交部分段无法形成该等式。包内包的嵌套不解除最内层逐件验证责任。

分段只改变组织方式，不能约束当前未计量的C09日志生成，也不能把每段32MiB误读为总量扩容；当前raw字节与封存期限缺口对C1/C2共同适用。新count/分段规则均需另行明确批准后才可能实施。''')
doc('MR_LIFECYCLE_CONFLICT_PROOF.md','MR生命周期最小冲突证明','''
结论分两层：**MR_LIFECYCLE_CONFLICT_PROVED**适用于“同一主批次原生异常关闭必须先于资源门和F1/F4”的强化验收合同；仅根据当前冻结M.formal_gate代码，结论为**MR_LIFECYCLE_CONFLICT_NOT_ESTABLISHED**，因为代码尚未强制要求原生异常关闭证书，存在覆盖缺口。

最小不可满足条件为四条：故障测试使B进入CLOSED；CLOSED吸收；Gate(B)要求该故障已在B发生；F1/F4要求Gate后B仍WORK。最小轨迹WORK(B)→原生异常→CLOSED(B)→Gate前提中WORK被拒绝→F1/F4无法进入。删除任一条件可以构造不同合同，但会改变当前要求。

有限合同模型穷举严格状态关系，FORMAL不可达。它是本轮静态逻辑状态探索，没有导入运行程序、运行F1/F4或建立实际T0。当前源码正常MR64与真实C09恢复的前置关系也已核对，避免将后来增加的研究验收条件误记成旧代码已经实现的条件。

保持严格同实例合同的方案A无法达到完整目标；可以只执行异常关闭专项并保留模型UNRUN。把异常关闭移到模型之后会改变资格门先决次序；只关闭专用worker、不关闭主批次，会改变所验收的主关闭性质；重新激活CLOSED或合并预算亦不属于现合同合法方案。共享预算的嵌套实例需要新的隔离/停止/证据合同，当前尚未授权。

方案B仅在明确批准限定跨实例条款后，分离A的故障能力观察与B的当前工作资格；A保持CLOSED，B独立新窗口。该顺序在抽象合同模型有条件可满足，实际原生证据仍未产生。

[状态模型与最小条件](evidence/LIFECYCLE_FORMAL_MODEL.json)。''')
attack_table='\n'.join(f'|{a}|{r}|{x}|' for a,r,x in attacks)
doc('MR_CROSS_INSTANCE_TRUST_MODEL.md','跨实例承认的信任与攻击边界',f'''
唯一候选承认类别为：相同受审实现及声明故障模型下，独立A实际观察到的一次原生服务异常处理能力。其事实强度为特定轨迹接受；有限测试不推出所有后续实例都能成功关闭。

TCB继续包含受信kernel/systemd/Root、源码与授权存储、现有包数据库/密钥环及无并发特权更新前提；GNU libc2.39/Ubuntu8.12来源条件与缺独立.deb payload再现原样保留。候选规则限定A/B同boot，关键binary/loader/maps/配置必须由B重新核验。Root恶意伪造与未声明的TCB失效超出原信任模型。

跨namespace的whole-source hash必然可能不同，不能只比较版本名。草案要求精确A/B artifact pair和按AST坐标逐项审阅的namespace字面量映射；所有安全分支、数字界、UID/GID/权限、运行时pin、故障/测试要求必须保持。禁止忽略全部字符串或盲目替换路径。当前approved_pairs=[]，实际等价证明未完成，证书当前不可用。

独立oracle重读原字节，来源靠Root绑定、原始单位实例事件、前后预算及真实退出相关联；生产者自报PASS不构成原生来源。现有archive主体与参考均依赖zipfile，存在共同parser TCB；现有15变异只证明已运行主机夹具，当前规则的攻击测试仍为设计状态。

|攻击|条件|明确拒绝|
|---|---|---|
{attack_table}

撤销/新鲜性采用窄范围策略：同boot、单个预声明B、当前直接用户授权固定CA/rule/use_spec摘要和nonce；新版本/新boot/新TCB/新目标需重新审阅。草案没有声称已经部署防回滚注册表或无限期证书缓存。

[逐条攻击矩阵](proposals/ATTACK_REJECTION_MATRIX.json) · [源码对关系约束](proposals/SOURCE_PAIR_REVIEW_REQUIREMENTS.json)。''')
conditions='\n'.join(f'|{i}|{n}|{p}|' for i,n,p in requirements)
current_list='\n'.join('- '+s for s in current)
doc('MR_CROSS_INSTANCE_ADMISSION_PROPOSAL.md','限定跨实例承认合同草案',f'''
**DRAFT / PENDING_USER_APPROVAL / runtime_enabled=false。** 本轮只有规则设计权限，草案没有改变当前资格门。

候选推导规则：Approved(rule) ∧ NativeObserved(A,scenario) ∧ PrimaryAutoClosed(A) ∧ SealedAndRechecked(A) ∧ ReviewedSourcePair(A,B) ∧ SameBootEquivalentTCB(A,B) ∧ ExactFreshUse(B) ⇒ ApplicableObservedImplementationScenario(A→B)。该结论仅用于替代强化验收中的那一项异常场景观察义务；B的WORK、当前监督、预算、C09及RESOURCE_GATE均需要各自前提。

|条款|名称|正式前提|
|---|---|---|
{conditions}

始终由B当批重新证明：

{current_list}

事后证书C_A在A native/admin封存和原始复核后，写在两者hash前像外；随后生成独立use_spec，固定C_A、rule、artifact-pair和B身份/boot/执行锁/nonce；B授权收据固定use_spec hash；最后实际use record绑定授权hash。任何缺值或逆向自hash均拒绝。当前证书、nonce、B身份与授权收据均未签发。

A新增failed单位的后续只读分类只能依赖精确A单位/InvocationID/PID/boot/退出及CLOSED原件hash；禁止reset-failed、广泛白名单或把A的故障状态授为B监督职责。实际实现仍须在明确批准后单独审查。

[完整机器规则](proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json) · [证书及use记录顺序](proposals/MR_CERTIFICATE_AND_USE_SCHEMA.json)。''')
doc('MR_CROSS_INSTANCE_ADMISSION_APPROVAL.md','待用户明确批准的合同文本','''
建议裁决：**APPROVE_RECOMMENDED**，范围仅限下列带先决条件的规则草案。该建议与用户批准、实现许可、动态执行许可及实际证书可用性分别登记；当前user_approved=false。

1. 原合同：B当批完成身份/运行时/资源、正常C09/ManagerRecovery及全部强制校准；强化验收还要求同批先完成主关闭异常场景再进入F1/F4。四条生命周期条件共同形成冲突。
2. 拟修订的唯一条款：允许独立A已实际完成并经原始字节复核的“专用原生服务故障→未审查失败识别→主A自动安全关闭”观察，作为B该有限实现能力观察项的条件性依据。其他资格条款保持。
3. 仅承认一个明确scenario、一个精确受审artifact pair、同一boot/等价关键TCB及一个预声明B。A未实际触发、未确认退出/组空、主自动路径失败、native/admin不完整或必需UNKNOWN均拒绝该类承认。
4. B必须重新证明当前boot、锁、单位、UID/GID、binary/maps、budget/T0/deadline/WORK、C00、真实C09、正常MR、当前监督/停止前提及所有原有C/S/门/资源强制项。A任何窗口、收据和预算均不转移。
5. A/B源锁均精确绑定。仅逐AST节点审阅的namespace字面量差异可以进入对应关系，安全控制流/数值/权限/pin/故障要求保持。approved_pairs表填实且经明确审核后方可应用，当前表为空。
6. 保留既有Root/kernel/systemd/存储与条件性运行时来源TCB；如无法接受这些前提则规则不可用。哈希不替代来源证明，主机合成数据不构成原生事件。
7. 所有当前必需raw/query/journal/ACK/退出/预算/关闭/封存及独立oracle程序和结果字节均需可取得。C_A在A封存后生成于其前像外，固定native/admin两个包及其manifest hash；不可为了取得证书回写旧包。
8. 当前B直接用户授权固定rule/CA/use_spec摘要及新nonce，现有once/新鲜namespace约束继续适用。任一撤销、版本/boot/TCB/fault scope/目标/锁变化使承认失效；未知撤销状态拒绝。当前没有部署额外防回滚注册表。
9. 攻击验收至少覆盖旧版本/旧boot重放、伪造原生事件、未触发、错误身份/InvocationID、缺退出、fallback-only、部分seal、checker共同错误、缺/换文件、预算转移与use重放。逐项拒绝规则见附件，测试当前尚未执行。
10. 资格门影响仅限经批准替换该强化的异常观察项，并增加CA适用性检查。RESOURCE_GATE仍由B全部当批条件合取决定。D1/D2语义、F1/F4有限域、PASS_BOUNDED条件和原创性裁决保持。
11. 规则本身记录有限经验性能力观察及其适用假设；不构成B关闭已发生、任意故障必定关闭或未来实例安全的无条件证明。
12. 额外行为需分别明确授权：实际gate/证据承认代码适配；最终源/合同/argv锁；修改4452/4451等容量字段；独立A动态注入/封存；新B完整校准与条件F1/F4。批准本文草案不会自动授权这些执行。
13. 生效前未决项：源码等价pair实填、raw日志/字节/工作量合同闭合、独立A真实验收、当前B精确使用授权、未来承认器的独立安全审查。当前这些前提尚未全部具备，任何实际证书均不可登记为已有效。
14. 本文的批准对象为与MR_CROSS_INSTANCE_RULE_DRAFT.json绑定的有限规则，实施与使用继续受以上先决条件约束。用户明确批准文字应引用该规则版本及最终交付中的SHA-256；本轮没有代用户勾选或生成批准回执。

待批准文本：

> 我批准MR-CROSS-INSTANCE-OBSERVATION-RULE/1-DRAFT所列的限定同boot、单目标B、精确受审源码对及原生场景观察承认原则，并保留全部当前B独立资格要求。此批准仅允许后续提交具体实现/执行申请；实际适配、容量变更、MR注入和F1/F4仍需按精确工件与范围另行明确授权。

当前记录：**PENDING_USER_APPROVAL**；证书适用性：**NOT_USABLE_NOW**。

[规则附件](proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json) · [攻击拒绝条件](proposals/ATTACK_REJECTION_MATRIX.json) · [源码pair要求](proposals/SOURCE_PAIR_REVIEW_REQUIREMENTS.json)。''')
doc('RESOURCE_AND_TIME_RECALCULATION.md','访问、字节及时间责任重算','''
已冻结范围的校准硬界仍为68,498，实际本轮访问消耗0，T0/deadline/R均null。MR专项A若将旧前缀与新入口512预付集成，保守申请估计69,010；目前A源码/额度/执行批准尚未形成最终锁。A与B各有独立审计账和唯一窗口，不做预算合并或余额转移。

新B的正确公式为V_B=68,498＋V_当前证书验证＋V_新增字节工作检查＋V_新增oracle－已经证明共享的预付。新增规则尚无实现与收费合同，V_B数值保持UNRESOLVED。旧AdmissionFix的71,618仅为未接入79-job方案的条件估算，当前没有把它继承为新版本硬界。

源级数量包络K=4450已计算；raw总字节、通用单文件字节及端到端验证/构建工作量上界仍为EVIDENCE_MAX_BOUND_UNRESOLVED。具体源规则为C09退出见证PENDING循环的未计数append。另有602条readiness各131072字节的组合上界78,905,344字节，说明单记录界无法推出aggregate32MiB。

已明确的单项包括counter24字节、C03共享文件16MiB、readiness单条128KiB、接受的manifest≤4MiB、接受的native压缩/总解压及admin导出各≤32MiB。对已被这些字节守卫接受的输入，逐件checker工作量为O(K+B)，两个包扫描最多64MiB另加raw核对；该条件式界仅覆盖已接受输入的读验工作，构建输入和日志生成仍需独立上界。

总访问1,000,000、软校准100,000、总1800秒、软校准300秒、pre-T0 TCB120、提前1740、每进程AS1GiB及父TasksMax4全部保持。完整300秒、终态5秒、行政30秒的满足性继续UNRESOLVED；当前数量证明与主机逻辑状态探索不能替代原生时延/内存证书。

后续有限静态工作应为C09日志重复观察及外部原始journal导出补数值化record/byte/work责任、审查其安全停止边界和计费；本轮没有修改ACK协议、日志产生程序或预算核心。

[机器算式](evidence/RESOURCE_AND_WORK_MODEL.json) · [源循环证据](evidence/FINITE_FIXED_POINT.json)。''')
doc('NEXT_EXECUTION_DECISION.md','后续合同与执行方案裁决','''
当前优先级：继续有限静态字节/工作量责任补齐，同时可供用户审阅限定MR合同草案。当前尚不进入专项动态验收或完整校准。

方案A：保持严格同实例异常先决合同。完整目标在四条生命周期条件下不可满足；可单独完成MR异常关闭验收并保持F1/F4未运行。尾部异常测试或只关worker属于不同合同/性质，需明确变更后再评估。

方案B：仅在用户明确批准新规则后准备适配。完整依赖顺序为：独立A原生故障→自动STOP/CLOSED/真实退出与组空→native/admin封存→独立原件复核→封存外C_A→精确A/B源码关系及同boot TCB审查→新B use_spec和独立授权/一次性认领→B当前身份/资源与C00–C09→真实C09/正常MR→C10–C12/S34/负向门/原始重算→检查已批准CA适用性→所有资源条件合取→F1→F4→关闭。

这是一份设计阶段可满足的执行依赖方案。A/B当前真实身份、argv、动态nonce与回执未签发，待容量/字节/工作量、源码pair与收费证明闭合后再填入独立执行申请；旧batch14和旧授权不复用。

明确先决批准分开：一是限定证据承认条款；二是之后具体gate适配实现范围；三是固定字节/时间边界下的版本化容量字段；四是精确A动态授权；五是精确B完整校准及条件F1/F4授权。本轮静态任务未授予这些操作。

任何源/输入/TCB/测试集合变化都触发计数及证据闭包重算。全局failed状态保持只读实例审查，无reset-failed/无关单位操作；A的新增failed单位仅按固定关闭原件供后续精确历史分类。''')
answers=[
 ('行政证据能否形成有限最大上界','封闭冻结ROOT的源级保守原件上界4452（含native两文件）；前提与人工源证明范围明确。整体raw字节/工作量尚未闭合。'),
 ('Native成员能否形成有限最大上界','同前提下4451；与完整成功下界1083区分，旧257不变。'),
 ('证据递归依赖','现有分层收集无自动递归；识别3条条件性最小自摘要环，草案按封存外证书和use_spec顺序切断。'),
 ('1082/1083构成','312+238+56+40+170+71+195=1082；native再加manifest1。'),
 ('256/257为何无法满足','必需互异路径已超限；完整成功轨迹在旧count接受集合中为空。'),
 ('最小容量修订','C1原格式版本化count草案：raw4450/native4451/admin原件4452/admin ZIP4467；待字节/工作量闭合及新明确批准。'),
 ('是否保留全部安全证据','分类和草案均要求原始字节/路径/hash/来源及独立重放；当前无删除、去重或封装实现。'),
 ('MR同批冲突是否成立','对异常关闭作为同主批次前置条件的强化合同成立；旧代码只强制MR64/正常恢复，旧代码自身冲突未建立。'),
 ('无需跨实例承认的合法方案','严格同主批次先关后正式工作目标无解；只做MR专项合法，F1/F4继续UNRUN。尾测/子实例需新合同。'),
 ('跨实例安全前提','R01–R14：原生/主自动关闭/封存oracle、精确source pair、同boot TCB、单B授权nonce、原件集合及全部B当前检查。'),
 ('始终当批重证的事实','B的boot/锁/单位/UID/运行时/budget/T0/WORK/C00/真实C09/正常MR/监督停止前提/全部资源资格。'),
 ('需批准精确条款','只替代强化的有限异常场景观察项；不转移运行资格/窗口/预算；完整待批准文本已交付且当前未生效。'),
 ('最新访问和时间上界','旧68,498有效于旧范围；新B为带新增项的公式，数值UNRESOLVED；A条件估计69,010；300秒及字节工作量未决。'),
 ('下一步','继续静态数值化日志/aggregate工作量合同；可并行审阅MR原则草案；当前动态与F1/F4保持关闭。')]
table='\n'.join(f'|{i}|{q}|{a}|' for i,(q,a) in enumerate(answers,1))
doc('FINAL_DECISION.md','EvidenceContract-Closure最终裁决',f'''
**COUNT_ENVELOPE_CONDITIONALLY_CLOSED；VOLUME_AND_WORK_UNRESOLVED；MR_RULE_DRAFT_PENDING_APPROVAL。** 本轮得到有限且可审查的数量公式，补齐证据层级和MR待批准条款；完整动态准入继续关闭。

固定受控写入域内K≤4450，native成员≤4451，行政导出原件≤4452，行政ZIP≤4467。该保守包络来自实际源码/固定测试/actor/临时件/异常展开配额，没有任意选择大整数，旧256/257保持原字节。原始字节和工作量仍缺C09 PENDING append等数值责任，因此没有宣称完整容量与时间准入已经通过。

交付DAG1142节点拓扑检查无环，三条潜在自摘要环的触发条件与切断次序已列明。MR同实例最小冲突在强化验收前提下证明；旧M.formal_gate没有异常证书强制项，原代码范围的结论相应保留。限定跨实例规则建议APPROVE_RECOMMENDED，但当前user_approved=false、runtime_enabled=false、artifact-pair表为空、实际证书不可用。

|序号|最终问题|答复|
|---:|---|---|
{table}

本轮仅运行主机源/合同图和逻辑状态分析；冻结64份程序/输入及8份上轮审查对象逐字节保持。新runtime代码、封装代码和跨实例gate实现0，WSL/服务/真实故障/资源校准/F1/F4/新动态测试均0，T0/deadline/R=null。历史观察与UNKNOWN继续保留。

已交付12份要求报告、机器图/固定点/最终数量表、源片段、正式规则/攻击/源码对/证书与use顺序草案和资源模型。[完整索引](EVIDENCE_INDEX.md) · [最终机器裁决](evidence/FINAL_REVIEW_DECISION.json) · [交付核验](evidence/DELIVERY_CHECK.json)。''')
save('evidence/FINAL_REVIEW_DECISION.json',{'overall':'COUNT_ENVELOPE_CONDITIONALLY_CLOSED_VOLUME_WORK_UNRESOLVED_RULE_PENDING_APPROVAL',
 'date':'2026-11-14','count_upper':{'pre_native_raw':4450,'native_members':4451,'admin_originals':4452,'admin_final_members':4467},
 'bound_scope':'Frozen closed-world source/first-failure prefix, manual source proof; not least maximum or measured native trace',
 'raw_byte_upper':'EVIDENCE_MAX_BOUND_UNRESOLVED','single_file_global_bound':'UNRESOLVED','end_to_end_work':'UNRESOLVED','DAG_acyclic':True,'DAG_nodes':len(G['nodes']),
 'MR_strict_contract':'MR_LIFECYCLE_CONFLICT_PROVED','MR_unstrengthened_code':'MR_LIFECYCLE_CONFLICT_NOT_ESTABLISHED',
 'MR_recommendation':'APPROVE_RECOMMENDED_CONDITIONAL_RULE_ONLY','user_approved':False,'runtime_enabled':False,'certificate_usable_now':False,
 'production_guard_changes':0,'runtime_source_edits':0,'packaging_implementation':0,'cross_gate_implementation':0,'WSL_calls':0,'dynamic_tests':0,
 'T0':None,'deadline':None,'R':None,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE',
 'PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'})
reports=sorted(p.name for p in O.glob('*.md'));assert len(reports)==12
text('EVIDENCE_INDEX.md','# EvidenceContract-Closure证据索引\n\n'+passport+'\n\n'+ '\n'.join(f'- [{n}]({n})' for n in reports)+'''

- [交付DAG及全部依赖字段](evidence/EVIDENCE_GRAPH_DELIVERY.json)
- [族schema与基数](evidence/EVIDENCE_FAMILY_SCHEMAS.json)
- [最终4450数量计算](evidence/FINAL_COUNT_CLOSURE_CALCULATION.json)
- [固定点与C09源规则](evidence/FINITE_FIXED_POINT.json)
- [源证明审查备注](evidence/SOURCE_PROOF_REVIEW_NOTES.json)
- [逻辑生命周期模型](evidence/LIFECYCLE_FORMAL_MODEL.json)
- [精确原源/审查组件核验](evidence/SOURCE_AND_REVIEW_CHECK.json)
- [源行片段](evidence/SOURCE_EXCERPTS.json)
- [限定MR规则草案](proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json)
- [容量草案](proposals/CAPACITY_CONTRACT_DRAFT.json)
- [最终裁决](evidence/FINAL_REVIEW_DECISION.json)
- [历史前态](evidence/HISTORY_BASELINE.json)
- [历史后态](evidence/HISTORY_AFTER_CHECK.json)
- [交付核验](evidence/DELIVERY_CHECK.json)
- [研究manifest](EVIDENCECONTRACT_MANIFEST.json)
- [研究ZIP](EVIDENCECONTRACT_EVIDENCE.zip)
- [ZIP SHA-256](EVIDENCECONTRACT_EVIDENCE.zip.sha256)

分析初稿与最终修订分别保留；交付结论只引用FINAL_COUNT_CLOSURE_CALCULATION和EVIDENCE_GRAPH_DELIVERY。研究归档独立于native/admin运行封存，DELIVERY_CHECK独立链接包摘要以避免自摘要循环。
''')
prefix=('## DCL-R6-EvidenceContract-Closure 合同审查增量（2026-11-14）\n\n'
 '**数量包络有条件闭合，字节/工作量未决，MR规则待批准。** 源级保守K4450/native4451/admin原件4452/admin ZIP4467，固定测试/actor/临时件/异常责任逐项推导；DAG1142节点拓扑无环。C09 PENDING重复日志只有deadline、缺record/byte/work配额，完整32MiB/300秒/封存期限仍未闭合。强化的同实例异常先决合同存在MR生命周期冲突；同boot单B/精确源码对的有限场景承认草案建议批准，当前user_approved=false且不可使用。\n\n'
 '旧256/257及64份运行源、8份审查工件保持，封装/跨实例gate实现和动态测试0，T0/deadline/R=null。RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。下一步继续静态日志/aggregate工作量合同，并可审阅MR原则草案。\n\n'
 '[最终裁决](DCL-R6-EvidenceContract-Closure/FINAL_DECISION.md) · [数量证明](DCL-R6-EvidenceContract-Closure/EVIDENCE_COUNT_CLOSURE_PROOF.md) · [待批准文本](DCL-R6-EvidenceContract-Closure/MR_CROSS_INSTANCE_ADMISSION_APPROVAL.md) · [索引](DCL-R6-EvidenceContract-Closure/EVIDENCE_INDEX.md)\n\n'
 '以下逐字节保留先前记录。\n\n---\n\n').encode()
for n in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
 original=(E/'NAV_ORIGINALS'/n).read_bytes();assert(P/n).read_bytes()==original;(P/n).write_bytes(prefix+original)
print(json.dumps({'reports':12,'graph_nodes':len(G['nodes']),'raw_upper':4450,'rule_approved':False,'runtime_changes':0}))
