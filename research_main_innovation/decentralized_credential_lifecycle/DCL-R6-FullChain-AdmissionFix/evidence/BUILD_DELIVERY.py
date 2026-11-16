"""Freeze the review version and write the authorized static findings."""
from pathlib import Path
import ast,difflib,hashlib,json
from datetime import datetime,timezone
O=Path(__file__).resolve().parent.parent;P=O.parent;E=O/'evidence';S=E/'FROZEN_RA_ORIGINALS'
VERSION='FullChainAdmission-static-1/review-1'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def text(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(x.strip()+'\n')
passport=f'Material Passport：DCL-R6-FullChain-AdmissionFix；{VERSION}；2026-11-13；HOST_STATIC_REVIEW_ONLY。'
tail='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。'
def doc(n,title,body):text(n,f'# {title}\n\n{passport}\n\n{body}\n\n{tail}')
catalog=read(E/'EVIDENCE_CATALOG.json');w=read(E/'EXPANDED_FULLCHAIN_LOWER_WITNESS.json')
checks=read(E/'HOST_ATTEMPT_R2/HOST_CHECK_SUMMARY.json');final=read(E/'FINAL_COMPONENT_CHECKS.json')
hist=read(E/'HISTORY_BASELINE.json');base=read(E/'SOURCE_BASELINE_LOCK.json')
input_dir=O/'proposals';input_dir.mkdir(exist_ok=True)
capacity={'schema':'FC-CAPACITY-REVISION-PROPOSAL/1','version':VERSION,'status':'UNSELECTED_REQUIRED_MAXIMUM_MISSING',
 'runtime_enabled':False,'selected_new_admin_files':None,'selected_new_native_members':None,
 'legacy':{'admin_original_files':256,'native_members':257,'admin_final_zip_members_upper':271,
 'admin_host_sidecars':10,'admin_source_lock_sidecars':4,'admin_manifest':1},
 'proved_full_calibration_lower':887,'proved_full_with_models_lower':1082,'proved_native_members_lower':1083,
 'full_success_manifest_available':False,'full_filename_cardinality_upper':None,
 'preserved':{'admin_bytes':33554432,'native_uncompressed_bytes':33554432,'native_compressed_bytes':33554432,
 'manifest_bytes':4194304,'journal_bytes':33554432,'journal_line':32768,'read_seconds':5,'admin_seconds':30,
 'RLIMIT_AS':1073741824,'TasksMax':4,'global_visits':1000000,'calibration_visits':100000,'wall':1800,'calibration_seconds':300},
 'selection_rule':'Close all producer/cardinality/error/temp/metadata bounds; choose exact maximum necessary files plus explicit native/admin sidecars; bind to scope/source/input hashes.',
 'legacy_preservation':'Existing ra01 bytes and old readers remain frozen; new profile only after a complete bounded cardinality proof and concrete revision acceptance.',
 'novel_mechanism':False,'separation_status':'COVERED_BY_G_STANDARD_ZIP_MANIFEST_MAINTENANCE'}
save('proposals/CAPACITY_CONTRACT_REVISION.json',capacity)
native={'schema':'MR-NATIVE-CLOSURE-PROPOSAL/1','source_revision':VERSION,'runtime_enabled':False,
 'scope':'MR_RECOVERY_DIAGNOSTIC_ONLY','batch_id':None,'boot_id':None,'unit_argv':None,
 'fault_exit':79,'scheduler_exit':78,'prepaid_visits':512,'max_manager_samples':64,'fault_observation_seconds':5,
 'fault_unit_suffix':'mr-native-fault.service','worker_uid':999,'worker_gid':989,
 'control':'Dedicated service under current payload slice; original C10 properties; one current A namespace only',
 'current_authorization':'STATIC_ONLY; no runtime receipt, unit, batch, T0, budget or nonce',
 'required_true_flags':['MR_native_fault_explicitly_approved','ManagerRecovery_diagnostic_explicitly_approved','Diagnostic_auto_close_injection_explicitly_approved'],
 'required_evidence':['current invocation/PID/boot/start/exit79','failed_set exact one-unit delta','unreviewed failure rejection',
 'current boot/unit/invocation raw journal','STOP/CLOSED','Root child waitpid78','budget hashes stable','roles/group empty','native archive verification','admin archive verification'],
 'no_fault_retries':True,'closes_current_A':True,'permits_F1_F4':False,
 'standalone_old_diagnostic_78_is_sufficient':False,'fault_runtime_status':'UNRUN','snapshot_oracle_status':'HOST_SHAPED_FIXTURES_ONLY',
 'integration_status':'Concrete MR guard hook proposal only; add source/input bindings and frozen caller wiring before native admission'}
save('proposals/MR_NATIVE_CLOSURE_CONTRACT.json',native)
life={'schema':'FC-MR-LIFECYCLE-DECISION/1','status':'MR_NATIVE_CLOSURE_LIFECYCLE_CONFLICT',
 'contradictory_requirements':['Native exception test closes the same main batch','CLOSED is absorbing and budget/deadline immutable',
 'Current B requires exception evidence in current batch before resource gate','B continues F1/F4 in the same batch'],
 'independent_instance_authorized_now':False,'cross_instance_admission_authorized_now':False,
 'request_only_revision':{'A':'Independent one-shot native diagnostic batch, permanently closes, no models',
 'B':'New identity with its own C00-C12/C09/MR64/current recovery/S34/gate18/runtime/source/budget/time evidence',
 'A_to_B':'Optional implementation-qualification certificate only, if explicitly approved; source/input/runtime/fault-model hashes and exact A closed originals verified. No A runtime authority/receipt/budget/T0 transfer.',
 'historical_failed_A_unit':'Only exact A InvocationID/PID/exit/boot/closed proof may enter read-only historical classification after specific review; never reset-failed or wildcard allowlist'},
 'B_release':False,'required_user_decision':'Explicitly accept a changed cross-instance evidence rule or authorize a separately bounded subordinate instance design after trust/budget/identity/stop analysis.'}
save('proposals/LIFECYCLE_CONTRACT_REVISION.json',life)
plan={'schema':'FC-EXECUTION-LOCK-PROPOSAL/1','version':VERSION,'status':'NO_EXECUTABLE_LOCK_ISSUED','runtime_enabled':False,
 'A':{'active_argv':None,'batch_id':None,'source_root':None,'receipt':None,'readiness':'STATIC_COMPONENTS_ONLY_CAPACITY_AND_INTEGRATION_PENDING'},
 'B':{'active_argv':None,'batch_id':None,'receipt':None,'readiness':'BLOCKED_MR_LIFECYCLE_AND_CAPACITY'},
 'unchanged_limits':[1000000,1800,1740,1073741824,4],'calibration':[100000,300],'TCB_preT0':120,
 'base_static_manifest_sha256':sha(S/'inputs/static_manifest.json'),'base_execution_lock_sha256':sha(S/'inputs/execution_lock.json'),
 'required_pre_execution':['Final integrated source hash and contracts','Selected exact count maximum within fixed byte/time/resource bounds',
 'Final argv/new namespace/current runtime and boot qualification','Current explicit dynamic authority',
 'For B: approved lifecycle/evidence-recognition rule plus exact A evidence if used'],
 'F1_F4_business_changed':False,'budget_core_changed':False,'C09_changed':False,'RootIPC_permissions_changed':False}
save('proposals/EXECUTION_LOCK_PROPOSAL.json',plan)
resource={'schema':'FC-RESOURCE-REVIEW/1','version':VERSION,'actual_global_visits_consumed':0,'actual_T0':None,'actual_R':None,
 'unchanged_frozen_calibration_hard':68498,'MR_proposed_prepaid':512,'MR_only_conditional_upper':69010,
 'host_check_jobs':79,'host_job_equation':'27 archive +6 exact old checker guards +10 old MR pure predicates +21 new MR oracle fixtures +15 guard-deletion mutants =79',
 'future_driver_unimplemented':True,'proposed_per_job_prepaid':32,'proposed_per_job_root_oracle':1,'proposed_suite_entry':1,
 'conditional_extra_suite':2608,'conditional_joint_visit_estimate':71618,'conditional_margin_to_100000':28382,
 'proposed_visit_estimate_is_final_proof':False,'actual_new_formal_hard_bound':None,
 'unresolved':['Exact full producer maximum/cardinality including errors/temp files','Final archive work limits and final test input count/size',
 'Runtime billing driver integration and final source-locked fee policy','Cross-instance native evidence rule','300s complete calibration time','Python allocation/RSS proof for selected capacity'],
 'unchanged_contract':capacity['preserved'],'global_wall_seconds':1800,'stop_relative':1740,'preT0_TCB_seconds':120,
 'native_new_payload_processes_peak':1,'native_new_persistent_root_roles':0,'new_systemd_unit':'one dedicated fault service under current slice, proposal only',
 'archive_FD_envelope':'source/archive FD plus one member stream, sequential; OS/interpreter internal FD count needs native audit',
 'archive_index_work':'EOCD checked before ZipFile; central-directory bytes <=1582*N; per-name<=1024B; extra/comment<=256B',
 'archive_stream_work':'64KiB subject /32KiB reference; total raw <=32MiB; two complete reads when both checkers used',
 'archive_python_memory':'O(N) index/rows plus <=4MiB manifest and bounded chunks; exact object overhead UNRESOLVED',
 'disk_envelope':'Existing runtime originals, native compressed ZIP and administrative copy each retain own fixed32MiB limit; no proof that every full trajectory fits aggregate admin32MiB',
 'time_status':'UNRESOLVED; host parser check time does not establish native300s/5s/30s guarantees'}
save('evidence/RESOURCE_RECALCULATION.json',resource)
# Concrete proposed hook; it is stored as review text and never applied.
old=(S/'src/guard.py').read_text(encoding='utf-8-sig')
needle="if c=='C10' and a['scope']=='MR_RECOVERY_DIAGNOSTIC_ONLY':return M.diagnostic_marker(sys.modules[__name__])"
assert needle in old
replacement="if c=='C10' and a['scope']=='MR_RECOVERY_DIAGNOSTIC_ONLY':\n                import mr_native_entry\n                return mr_native_entry.run(sys.modules[__name__],trusted(SOURCE.parent/'inputs/mr_native_closure_contract.json'))"
new=old.replace(needle,replacement)
text('evidence/PROPOSED_MR_HOOK.patch',''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='frozen/src/guard.py',tofile='proposed/src/guard.py')))
diff=[]
for p in sorted((O/'maintenance').glob('*.py')):
 diff.extend(difflib.unified_diff([],p.read_text(encoding='utf-8').splitlines(True),fromfile='/dev/null',tofile='maintenance/'+p.name))
text('evidence/ACTUAL_ADDITIONS.patch',''.join(diff))
protected=[]
for r in base['files']:
 p=Path(base['source'])/r['relative'];protected.append({'relative':r['relative'],'same_bytes':sha(p)==r['sha256'],'sha256':sha(p)})
assert all(r['same_bytes'] for r in protected)
save('evidence/PROTECTED_SEMANTICS_CHECK.json',{'all_64_originals_unchanged':True,'files':protected,
 'D1_D2_changed':False,'five_business_bytes_changed':False,'budget_core_changed':False,'RootIPC_changed':False,'C09_changed':False,
 'C00Ready_Boot_PreT0_PT_PF_TR_runtime_bytes_changed':False,'MR_classifier_changed':False,'native_hook_applied':False})
gates={'FC-1':{'status':'PASS_STATIC','meaning':'Old count conjunction proved unsatisfiable; lawful versioned route documented; new cap unselected'},
 'FC-2':{'status':'PARTIAL','meaning':'Existing byte originals preserved; conventional archive checks and independent oracle passed host tests; no full capacity/ native equivalence proof'},
 'FC-3':{'status':'PARTIAL','meaning':'Native A entry and independent snapshot/data oracle plus guard hook proposal prepared; integration and current native evidence pending'},
 'FC-4':{'status':'UNRESOLVED','meaning':'Same-batch close/continue conflict formally registered; separate-instance/evidence-recognition change needs explicit authority'},
 'FC-5':{'status':'PARTIAL','meaning':'Old bound68498 retained, native proposal512, conditional71618 model documented; final new bound and byte/time/memory proof incomplete'},
 'FC-6':{'status':'PARTIAL','meaning':'Static review artifact hashes frozen; no final integrated executable lock or dynamic receipt'}}
save('evidence/STATIC_GATE_DECISIONS.json',gates)
review_files=[]
for p in sorted(list((O/'maintenance').glob('*.py'))+list((O/'proposals').glob('*.json'))):
 review_files.append({'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
save('evidence/STATIC_REVIEW_LOCK.json',{'version':VERSION,'scope':'REVIEW_COMPONENTS_AND_CONTRACT_PROPOSALS_ONLY','runtime_enabled':False,
 'base_source':base['source'],'base_files':64,'base_lock_sha256':sha(E/'SOURCE_BASELINE_LOCK.json'),'files':review_files,
 'new_execution_lock':'NOT_ISSUED','new_runtime_namespace':None,'receipt':None,'revision_semantics':'Unintegrated static review; no runtime pass claim'})
save('evidence/FINAL_STATIC_DECISION.json',{'version':VERSION,'overall':'PARTIAL_STATIC_REPAIR_REVIEW_ONLY',
 'old_count_contract':'EVIDENCE_COUNT_CONTRACT_UNSAT','lifecycle':'MR_NATIVE_CLOSURE_LIFECYCLE_CONFLICT','gates':gates,
 'runtime_cap_raised':False,'actual_frozen_runtime_source_edits':0,'new_review_components':4,'native_hook_applied':False,
 'WSL_calls':0,'service_starts':0,'native_faults':0,'native_entry_imports':0,'F1_F4_imports':0,'T0':None,'deadline':None,'R':None,
 'dynamic_retries':0,'host_collection_UTF8_error':1,'host_fixture_iterations_preserved':2,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'})

doc('EVIDENCE_COUNT_CONTRADICTION.md','证据数量约束的结构性冲突','''
**EVIDENCE_COUNT_CONTRACT_UNSAT。** 在现有逐件原件/逐成员ZIP合同及完整链输入下，全部必需证据与256/257同时满足的解集为空。

|证据层|确定数量|证据意义|
|---|---:|---|
|TR-A2真实native manifest|233原件/234成员|既有最小路径的确切实际数量|
|TR-A2真实行政manifest|249行/250成员|235个运行文件＋10个host侧件＋4个source lock＋manifest|
|FullChain-B原证明|至少312原件/313成员|六组C00后回归，最小缺口56|
|本轮扩展校准证明|至少887原件/888成员|增加C09H238、IPC56、BC40、S34最少170、ledger71|
|含完整F1/F4轨迹|至少1082原件/1083成员|另加195个模型输入/输出；最低缺口826|

312＋238＋56＋40＋170＋71=887；887＋195=1082。全部路径互异；额外输入、票据、锁、结果、时序、registry、快照、错误/临时文件、原生包与manifest开销尚未计入。1082/1083继续作为下界，完整实际数及最大必要数保持UNKNOWN。

实际manifest逐项核验已完成。新的完整运行尚未存在，其sha256/size字段均null。依据本轮“新上限应依据完整manifest的实际最大必要数量”“禁止任意设定过大的宽松上限”，当前材料不足以选定生产新上限。把313或1083直接用作上限将遗漏后续必需文件。

[794条原清单](evidence/EVIDENCE_CATALOG.json) · [1082条扩展路径](evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json) · [261个源写入/读取/路径调用站点](evidence/PRODUCER_SITE_CENSUS.json)。源站点清点含读操作与别名，需沿语义调用路径闭合其基数；清点本身未充当完整上界。''')

doc('ADMIN_EVIDENCE_CONTRACT_AUDIT.md','行政证据合同审计','''
256来自startup_contract.json的admin_max_files，同时由startup_lifecycle.post_exit_export:496–503的逐文件导出计数和host/startup_finalize.finalize再次强制检查。它限制运行原件导出工作量/元数据内存与行政格式容量；独立的32MiB总字节界及30秒alarm保护仍生效。它具有安全与资源边界意义。

256约束作用于导出的运行文件。最终host ZIP另加入10份固定host侧件、4份源锁和1份manifest，因此原配置下行政ZIP总成员上界为271，而非256。TR-A2实际235＋14＋1=250已由两份真实manifest核对。

原代码逐件复制、记录相对路径/字节/摘要，再逐件打包。未发现允许删除必需原件或将完整审计对象视为等价汇总的现行承认规则。相同摘要仅说明内容相同，路径/批次/来源身份仍具有独立证明责任。

本次授权覆盖维护性版本化合同修订；既有合同未附加“256必须另行批准”的独立条款。当前停止上限实装的依据是精确最大必要数量与资源证明缺失，保持本轮明确限制。当前生产源与256硬界原字节保留。

[容量修订提案](proposals/CAPACITY_CONTRACT_REVISION.json) · [真实行政manifest](evidence/ACTUAL_ADMIN_MANIFEST.json) · [实际旧guard AST边界结果](evidence/HOST_ATTEMPT_R2/ACTUAL_FROZEN_CHECKER_RESULTS.json)。''')

doc('NATIVE_ZIP_LIMIT_AUDIT.md','Native ZIP上限及相关检查器','''
257来自terminal_contract.native_archive_members及terminal_evidence._native_artifact的len(names)>257分支。guard.seal逐件记录ROOT原件并增加out/EVIDENCE_MANIFEST.json，形成一件原件对应一ZIP成员的实际格式。重复/缺失/多余成员、原件摘要和总解压32MiB构成原证明责任。

相关依赖还包括startup_lifecycle.post_exit_export中的原生包审查、host行政finalizer、终态_reader5秒界、manifest4MiB、journal32MiB与32768字节行界。旧post-exit包审查只按declared逐件比hash，完整成员集合/类型检查责任主要位于终态_reader；新维护组件尚未接入，弱项未登记成已修复。

新增常规archive_check在ZipFile创建索引前读取固定EOCD并限制中央目录大小，随后拒绝目录穿越、反斜杠/drive路径、Unicode规范化冲突、重复manifest键/路径、重复成员、symlink/FIFO、加密/不支持方法、缺/多成员、字节/摘要/权限不匹配及部分归档。流式读取保持32MiB总界，无文件解压写入。archive_oracle使用独立代码重算这些义务。

该组件支持原native dict manifest与行政list manifest，原manifest字节逐件验证。真实TR-A2的234成员native与250成员行政包均通过新组件及独立oracle的主机只读复核。Zip/文件来源与Linux实际权限仍依赖原Root绑定/metadata守卫，当前原生行为未运行。

[旧格式兼容与最终组件检查](evidence/FINAL_COMPONENT_CHECKS.json) · [维护检查器](maintenance/archive_check.py) · [独立oracle](maintenance/archive_oracle.py)。''')

doc('EVIDENCE_CAPACITY_REPAIR_OPTIONS.md','容量修复方案与选择边界','''
|方案|所需条件|当前判断|
|---|---|---|
|A：原格式版本化容量|完整生产者最大清单、精确N与元数据开销、固定字节/内存/时间证明；旧版本规则保留|优先采用；合同提案已形成，生产N尚未选定|
|B：无损表示优化|合同承认逐件恢复/身份/hash等价，并有独立逐件oracle与重放证明|通用ZIP/tar/内容寻址清单已覆盖；COVERED_BY_G|

选A的可审查变更面为容量合同、相关reader/exporter/host边界及版本绑定。当前完整数量最大值尚未闭合；新admin_files/native_members字段均null、runtime_enabled=false。旧64份源及上限保持冻结。

方案B属于现成通用归档方法G的覆盖范围。当前没有可构造的严格分离实例，未引入新编码、归并机制或候选协议实现。新增代码承担通用验证基础设施维护与专项测试职责。

必要修订程序：闭合261个站点的可达输出基数，包括失败/临时文件/动态退出记录；把校准与模型完整最大清单和字节上界绑定scope；明确host14侧件与各manifest/native ZIP嵌套开销；选择精确版本化N；保留旧配置可复核；最后集成和重新冻结。当前只读组件验证的cap313明确标为最低见证测试边界，未成为生产提案N。

[版本化合同提案](proposals/CAPACITY_CONTRACT_REVISION.json) · [完整约束证明](EVIDENCE_COUNT_CONTRADICTION.md)。''')

doc('EVIDENCE_PRESERVATION_PROOF.md','原件保全与独立校验边界',f'''
旧ra01的64/64份实际文件与最终锁逐字节相同，D1/D2、五业务、预算核心、RootIPC权限、C09 ACK、C00Ready、Boot、PreT0/PT/PF、TerminalRead及既有MR分类均保持原字节。新代码限于4份独立维护/验收组件，MR hook只保存为审查patch。

TR-A2真实native233条与行政249条manifest均按现存原始文件重新计算SHA，FullChain-B证据ZIP122文件/123成员逐项验证。新增主机fixture写在本轮目录，源输入与历史运行账保持只读。历史基线{len(hist['files'])}份文件与四份导航原件已保存，交付时执行前后摘要核对。

证据清单区分ACTUAL_HISTORICAL_FILE与STATIC_PATH_WITNESS。相同历史摘要只建立内容等价候选组，当前删除/去重/跨批次替换0。计划文件的未知SHA/字节保持null，独立校验字段标记仅路径静态证明。

新增archive组件保持逐成员检查，额外拒绝多种非法表示；它未改变现有终态work_allowed、CLOSED吸收性或native_ready义务。原生环境与权限/退出/封存行为继续UNRUN，主机检查无法授予这些性质。

[64份保全核验](evidence/PROTECTED_SEMANTICS_CHECK.json) · [实际新增diff](evidence/ACTUAL_ADDITIONS.patch) · [未应用MR hook](evidence/PROPOSED_MR_HOOK.patch)。''')

doc('EVIDENCE_NEGATIVE_REGRESSION.md','容量及故障负向专项检查','''
主机检查实际完成：27项新归档解析器用例、3项旧native函数边界、3项旧admin guard边界、10项原MR纯判据、21项新MR数据oracle用例；7项归档guard删除变异与8项MR义务删除变异实际检出。最终归档组件支持list manifest后，27项用例、7项变异及2份真实历史归档再次核对。

|覆盖|实际执行与结果|
|---|---|
|行政256/257/312|实际旧guard AST：接受256，拒绝257/312|
|native257/258/313|实际旧_native_artifact：257验证成功；258/313拒绝|
|测试cap313边界|维护组件及独立oracle：313接受、314拒绝；该cap仅为夹具边界|
|原件/manifest/ZIP完整性|缺项、多余、错误hash、重复JSON/成员、权限、路径穿越/反斜杠/drive、Unicode、symlink/FIFO、压缩方法/加密、膨胀声明、中央目录异常、部分ZIP均拒绝|
|MR义务|错误身份/boot/InvocationID、正常退出冒充故障、历史单位、未审查接受、查询/日志缺失、STOP/CLOSED/组空/角色退出缺失、预算变化、窗口重置、fallback/manual冒充、native/admin未完成及waitpid错误均拒绝|

旧函数由实际AST原文提取后执行；文件FD适配器只指向主机夹具，Linux uid/gid/ACL/锁/期限接口未模拟为已通过。MR数据夹具外层明确HOST_MR_ORACLE_FIXTURE，内层原生声明只是被验证输入字段，真实systemd/进程事件数0。

两个主机开发迭代保留：R1预算变异夹具意外共享before/after对象，改为各自deepcopy；R2路径变异仍被Windows ZIP名称规范化后的MEMBER_SET挡住，改用drive路径隔离目标guard。原始脚本、夹具和失败说明保留。初次行政收集还有一处GBK读取UTF-8错误，通过仅续作未完成AST收集修正。以上均为主机开发记录，原生重跑0。

最终变异通过实际AST删除特定guard后执行，再由独立oracle拒绝同一输入；最终检查使用固定PASS路径0。完整新容量精确N尚未确定，针对该N/N+1的资格测试继续PENDING_CONTRACT。

[最终主机汇总](evidence/HOST_ATTEMPT_R2/HOST_CHECK_SUMMARY.json) · [归档用例](evidence/HOST_ATTEMPT_R2/ARCHIVE_HOST_RESULTS.json) · [MR用例](evidence/HOST_ATTEMPT_R2/MR_HOST_RESULTS.json) · [两类变异](evidence/HOST_ATTEMPT_R2/MUTATION_HOST_RESULTS.json) · [MR变异](evidence/HOST_ATTEMPT_R2/MR_MUTATION_HOST_RESULTS.json)。''')

doc('MR_NATIVE_CLOSURE_SCOPE_AUDIT.md','MR原生异常关闭覆盖审计','''
MR64原驱动origin=MR-SIMULATION/1，覆盖分类、STOP/CLOSED模型、幂等和UNKNOWN有限夹具。C06/C07/C09提供真实指定故障与期望退出审查；旧C10后diagnostic_marker只让Root scheduler返回78，尚不足以证明新受控systemd未审查失败的完整关闭链。

维护入口run(G,contract)为独立A准备一个当前前缀mr-native-fault.service，复用C10的User/Group/slice/AS/TasksMax/NoNewPrivileges等全部现有sandbox属性。专用worker在当前cgroup内输出boot/PID原始日志后实际exit79。Root先取得active PID/InvocationID，再核failed与相同InvocationID/exit时间，failed集合只允许多出该单位，调用既有historical拒绝规则取得MR_UNREVIEWED_MANAGER_FAILURE。

原生记录保存于既有Root私有BC.Store，RootIPC policy与权限规则保持原字节。测试预付512，随后验证预算保持，写真实来源记录和旧诊断marker，再沿原M.fail/abort→STOP→CLOSED→pidfd/waitpid→native/admin封存。分类函数没有新白名单或跳过分支。原生异常只能终止A。

入口的授权位、合同摘要、runtime_enabled、scope、版本、精确argv和C10结果均须匹配；当前合同runtime_enabled=false、unit_argv=null、批次/nonce/回执均未签发，hook尚未应用。worker主函数与原生模块导入0，只有AST/compile检查。

[专项入口审查稿](maintenance/mr_native_entry.py) · [合同提案](proposals/MR_NATIVE_CLOSURE_CONTRACT.json) · [未应用hook](evidence/PROPOSED_MR_HOOK.patch)。''')

doc('MR_NATIVE_CLOSURE_LIFECYCLE.md','MR关闭与完整链生命周期冲突','''
**MR_NATIVE_CLOSURE_LIFECYCLE_CONFLICT。** 当前要求同时包含：异常测试关闭主批次A；CLOSED吸收且T0/预算保持；B资格要求当前批次异常关闭证据；同一批次继续F1/F4。前三项成立后继续工作资格终止，与第四项矛盾。

现行M.formal_gate只读取当前root/binding的MR_QUALIFICATION和MR_RECOVERY_REVIEW；旧阶段A/B申请允许B另建身份，却明确A已关闭窗口没有可复用运行资格。当前完整合同没有授予跨批次异常关闭PASS的承认规则。

本轮仅创建主机审查材料，独立原生实例0、预算/启动窗口0。专项A设计关闭其本身；测试完成后继续保持CLOSED。独立子实例共享主预算、嵌套stop责任及扩展证据承认均尚未获得第七节要求的明确批准。

具体修订申请为：允许先行A作为相同冻结实现/运行时/故障模型的“实现级异常关闭证据”；B核对A精确源/合同/hash/boot/InvocationID/关闭原件和封存，只采纳该有限实现证据，同时B自行重做当前C00–C12/C09/MR64/恢复/S34/门18/资源/预算。A的T0、R、收据和RESOURCE_GATE均不向B转移。此规则只有取得明确授权并实际集成后才生效。

A新增failed单位的后续只读审查需固定A的精确事件/关闭摘要，既有无关单位保持原样。当前未放宽任何资格门，B_release=false。

[精确矛盾与修订提案](proposals/LIFECYCLE_CONTRACT_REVISION.json)。''')

doc('MR_NATIVE_CLOSURE_TEST_PLAN.md','MR原生异常关闭专项A测试计划','''
未来A前置：完成生产容量最大清单、选定版本合同、集成入口与补充合同摘要、重新冻结源码/argv/新身份，获得独立动态授权；复核既有条件性glibc来源和当前boot。当前所有动态步骤UNRUN。

冻结依赖拟为：单会话/PreT0/WORK/C00→PT/PF/TR/RA/Ready/MR64→C01–C08→C09H/IPC/BC→真实C09及ManagerRecovery→C10→本批专用fault单位→未审查失败拒绝→自动关闭。A不进入C11/C12/S34/门18/F1/F4。

1. 验证当前scope/版本/合同/argv/专用单位空状态、独立Stop责任及C10 PASS，预付512；旧账不改写。
2. 专用单位仅复用当前Payload sandbox，worker输出当前boot/PID后exit79；Root最多64次采样、5秒观察。丢失live身份/查询超时/原始journal缺失即首次失败关闭，重试0。
3. 核对InvocationID、ExecMainPID、ExecMainCode/Status、时间、failed集合精确增量及既有未审查拒绝。保存原始查询stdout/stderr和journal。
4. 记录原始单位/预算/窗口后沿原M.abort自动STOP/CLOSED，协调者waitpid见证scheduler78，Root/独立停止器分别保存责任及错误。
5. 事后独立oracle从真实快照读取mr_native_case/first_failure/close/CLOSED/STOP/registry/waitpid及预算字节，核预算摘要、原始计数、身份与时间。原生和行政包需各自逐成员检查、相互绑定；caller自身退出另由外部只读审查。
6. 自动主路径、外部停止兜底、自动行政、后备归档和CLEANUP_UNKNOWN分别裁决；人工关闭/缺源/丢Root均禁止登记主路径成功。

新增oracle的data API已跑21个主机夹具；from_snapshot文件API与真实systemd/封存路径仍待原生准入。其admin独立包核验标记是明确外部前提，当前自动行政衔接尚未实现，未登记为PASS。

[入口](maintenance/mr_native_entry.py) · [独立oracle](maintenance/mr_native_oracle.py) · [动态前提](NEXT_DYNAMIC_AUTHORIZATION.md)。''')

doc('FULLCHAIN_RESOURCE_RECALCULATION.md','访问、容量与期限重新核算','''
实际全局访问消耗0，T0/deadline/R均null。既有冻结可达完整校准硬界68,498保持；新增原生入口代码固定预付512，因此仅该入口集成时条件界69,010。原生独立检查工作须包含在这笔预付范围内，否则重新核算。

拟将79项主机检查移入未来受控回归时，若最终计费合同明确每job预付32＋Root oracle1、driver入口1，则额外1＋79×33=2,608，合计条件估计71,618，距100,000余28,382。当前收费driver未集成、精确新容量N对应输入/工作量尚未闭合，故actual_new_formal_hard_bound=null；71,618仅供申请估算，完整新上界UNRESOLVED。

79=27新archive＋6旧guard＋10旧MR纯判据＋21新MRoracle＋15变异。两份历史包只读兼容检查单列，历史通过不充当新批回归。当前主机解析/静态测试属于明确授权的无业务检查，预算账创建0。

固定资源：校准100,000/300秒、全批1,000,000/1800秒、提前1740、pre-T0 TCB120、AS1GiB/进程、父TasksMax4。专用fault worker仅在C10结束后占用同父slice一个进程，不增加持久Root角色。

维护archive读取的中央目录预界为1582×N字节（46头＋1024名称＋256extra＋256comment），manifest≤4MiB，流式块64KiB/32KiB，总解压/压缩各32MiB，顺序打开一成员。Python对象常数与RSS峰值尚无原生证书，保持O(N)分析及UNRESOLVED。FD为archive源与一个成员流的顺序包络，解释器内部FD仍待审计。

磁盘包括原件、native ZIP和行政副本；原admin32MiB计数包含native ZIP，不能仅由每个归档32MiB推导整体可容纳。新N还需验证这一字节义务。ZIP构建、两次独立读验、5秒终态读取、30秒行政及完整300秒均保持UNRESOLVED，主机小夹具耗时不能充当原生保证。

[机器算式与未决项](evidence/RESOURCE_RECALCULATION.json)。''')

gate_table='\n'.join(f"|{k}|{v['status']}|{v['meaning']}|" for k,v in gates.items())
doc('STATIC_VERIFICATION_RESULTS.md','静态验收结果',f'''
|验收门|结果|证据范围|
|---|---|---|
{gate_table}

旧源64份全部摘要保持；新4组件通过Python3.12文法及主机内存compile；原五业务导入/运行0。归档新组件及独立oracle真实读取字节，旧native/admin守卫使用实际AST片段，MR原判据使用实际纯函数。Linux权限/期限适配器的排除边界已登记。

27＋6＋10＋21=64个基础主机检查、15个变异均已核验。最终支持行政list格式后重核27项、7归档变异和2份历史包。没有借用历史数据授予当前动态PASS。

source version仅冻结维护组件/合同审查稿，原运行包保持RuntimeAdapt-static-1/r1。当前生产容量未提高、MR hook未应用、新完整执行锁/收据/部署未签发。研究结论为PARTIAL_STATIC_REPAIR_REVIEW_ONLY。

[最终组件检查](evidence/FINAL_COMPONENT_CHECKS.json) · [机器门裁决](evidence/STATIC_GATE_DECISIONS.json) · [首次开发迭代记录](evidence/HOST_ATTEMPT_R2/HOST_ITERATION_RECORD.json)。''')

doc('SOURCE_AND_INPUT_LOCK.md','源码与输入审查锁',f'''
静态版本{VERSION}冻结4个新维护组件和4个合同/执行提案，逐件摘要见[STATIC_REVIEW_LOCK](evidence/STATIC_REVIEW_LOCK.json)。这是一份主机审查锁，runtime_enabled=false；当前没有可激活的新执行锁。

原ra01最终64文件保持，manifest SHA `{sha(S/'inputs/static_manifest.json')}`；原execution_lock SHA `{sha(S/'inputs/execution_lock.json')}`。全部旧程序/输入副本保存，旧命令只作为不可复用的历史引用。

新组件：archive_check、archive_oracle、mr_native_entry、mr_native_oracle。实际新增patch与未应用MR guard patch分别保存。原TerminalRead活动/终态policy、预算核心/RootIPC权限/C09/Boot/PreT0/PT/PF/MR分类均通过整文件摘要保持验证。

新admin/native生产N、原生A的batch/source/boot/argv、runtime receipt和nonce均未签发。A的entry属于可审查代码组件；实际集成需源/合同hash绑定、门检查、完整argv和资源证明闭合。B的生命周期规则尚待明确批准，release=false。

[实际新增diff](evidence/ACTUAL_ADDITIONS.patch) · [MR hook提案](evidence/PROPOSED_MR_HOOK.patch) · [原源锁](evidence/SOURCE_BASELINE_LOCK.json) · [执行锁提案](proposals/EXECUTION_LOCK_PROPOSAL.json)。''')

doc('NEXT_DYNAMIC_AUTHORIZATION.md','两个后续执行申请及必要合同决定','''
**REQUEST_ONLY；当前两方案均不能启动。** 本轮只有静态与主机检查授权，主动WSL/故障/模型执行均0。

方案A：MR原生异常关闭专项。申请对象限定新的独立A身份，当前批次自己的T0/预算/boot/source/输入/argv及专用fault unit；执行到真实C09/恢复/C10后，故障79→既有未审查拒绝→自动关闭→scheduler78/waitpid→预算保持→native/admin分别复核，随后永久CLOSED，模型0。总/软期限与AS/TasksMax保持原界，原生预付512已给出。当前容量精确N、完整集成锁与自动事后oracle衔接仍待完成，因此active argv和批准位保持null/false。

方案B：完整资源资格与条件F1/F4。只有容量最大清单/资源证明/执行锁完成，且MR生命周期合同获得明确决定后才可提交可执行申请。当前B_release=false。

需要明确批准的具体规则修订：允许先行A的真实原生异常关闭原件，作为同一冻结实现及运行时/故障模型的有限实现资格证据；B独立验证全部源/输入/原始hash、A单位InvocationID/boot/关闭/native/admin证据，同时B仍当批完成正常C09/恢复/MR64/C00–C12/S34/门18/账健康。A的运行窗口与RESOURCE_GATE不转移。现行合同下跨实例承认尚未生效。

如果继续要求异常关闭与F1/F4同时属于B本身，需另行授权并审查受同预算监督的专用隔离子实例，包括stop、父子预算、角色峰值和证据承认；当前未创建该实例。两种路线都保留首个关键失败即关闭、无免费窗口、无CLOSED恢复与无旧收据复用。

容量方面当前授权已允许维护性版本化修订；继续缺少完整最大清单和字节/内存/时间证明，提交的N均为待证明值。任何后续动态申请须将具体N、精确argv、hash和当前身份填实，禁止运行时临时放宽。

[A具体合同](proposals/MR_NATIVE_CLOSURE_CONTRACT.json) · [B生命周期修订](proposals/LIFECYCLE_CONTRACT_REVISION.json) · [容量修订](proposals/CAPACITY_CONTRACT_REVISION.json)。''')

doc('FINAL_DECISION.md','FullChain-AdmissionFix最终裁决',f'''
**PARTIAL_STATIC_REPAIR_REVIEW_ONLY。** 本轮完成更强的数量不可满足证明、4份维护/原生验收审查组件、真实解析器/旧守卫负向检查、15个实际命中的guard变异和两个后续执行方案。完整动态准入继续关闭。

原312/313下界成立；本轮已证明完整校准至少887份原件，含F1/F4至少1082份、native至少1083成员。实际成功完整manifest和最大必要数量尚未形成，因此按本轮明确规则保留256/257原守卫，新生产容量N保持未选定。原生异常关闭与同批继续工作之间的矛盾登记为MR_NATIVE_CLOSURE_LIFECYCLE_CONFLICT，跨实例证据承认修订等待明确授权。

|验收门|结果|说明|
|---|---|---|
{gate_table}

主机检查64项、变异15项完成；最终兼容复核27项/7归档变异及2份真实历史包通过。旧64份运行源无修改；新增组件仅主机审查，MR入口未导入/未接线；WSL/服务/真实注入/预算建立/模型/原生重跑均0，T0/deadline/R=null。主机收集与测试开发的已知失败迭代原样保留，最终用例和变异记录单独冻结。

已完成14份要求报告、完整锁/提案/diff、实际与计划证据清单和资源说明。本轮成果使缺口可定位、可审查；**完整生产上限、原生集成、生命周期承认和最终资源证明尚待闭合，未宣称解除全部阻断。**

静态版本{VERSION}只表示审查工件冻结。下一步先闭合容量最大清单与资源/集成证明，并决定A→B有限证据承认合同；随后才能签发独立动态申请。[证据索引](EVIDENCE_INDEX.md) · [机器裁决](evidence/FINAL_STATIC_DECISION.json) · [交付核验](evidence/DELIVERY_CHECK.json)。''')

reports=sorted(p.name for p in O.glob('*.md'));assert len(reports)==14
text('EVIDENCE_INDEX.md','# FullChainAdmission静态证据索引\n\n'+passport+'\n\n'+ '\n'.join(f'- [{n}]({n})' for n in reports)+'''

- [794条实际/计划分层清单](evidence/EVIDENCE_CATALOG.json)
- [1082条扩展必需路径](evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json)
- [261个源路径站点](evidence/PRODUCER_SITE_CENSUS.json)
- [最终维护组件核验](evidence/FINAL_COMPONENT_CHECKS.json)
- [64基础主机检查/15变异汇总](evidence/HOST_ATTEMPT_R2/HOST_CHECK_SUMMARY.json)
- [原件保全核验](evidence/PROTECTED_SEMANTICS_CHECK.json)
- [审查锁](evidence/STATIC_REVIEW_LOCK.json)
- [最终机器裁决](evidence/FINAL_STATIC_DECISION.json)
- [历史前态](evidence/HISTORY_BASELINE.json)
- [历史后态](evidence/HISTORY_AFTER_CHECK.json)
- [交付核验](evidence/DELIVERY_CHECK.json)
- [研究包manifest](ADMISSIONFIX_MANIFEST.json)
- [研究证据ZIP](ADMISSIONFIX_EVIDENCE.zip)
- [ZIP SHA-256](ADMISSIONFIX_EVIDENCE.zip.sha256)

研究ZIP独立于native/admin运行封存。最终DELIVERY_CHECK自排除，完成后链接研究ZIP摘要；旧原件及失败迭代保持。
''')
prefix=('## DCL-R6-FullChain-AdmissionFix 静态审查增量（2026-11-13）\n\n'
 '**PARTIAL_STATIC_REPAIR_REVIEW_ONLY。** 校准必需原件下界887，含模型1082/native1083；完整最大清单尚未闭合，256/257生产守卫保持。4个维护/原生验收组件与MR hook审查稿形成，64基础主机检查/15变异完成，原生动态UNRUN。MR同批异常关闭与继续F1/F4的冲突已登记，A→B实现级证据承认需明确合同决定。旧64文件冻结，WSL/服务/故障/模型/预算/动态重跑0，T0/R=null。\n\n'
 '静态版本FullChainAdmission-static-1/review-1，执行锁/新生产容量/动态身份均未签发。RESOURCE_GATE_PASS=NOT_OBTAINED；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[最终裁决](DCL-R6-FullChain-AdmissionFix/FINAL_DECISION.md) · [数量矛盾](DCL-R6-FullChain-AdmissionFix/EVIDENCE_COUNT_CONTRADICTION.md) · [后续方案](DCL-R6-FullChain-AdmissionFix/NEXT_DYNAMIC_AUTHORIZATION.md) · [索引](DCL-R6-FullChain-AdmissionFix/EVIDENCE_INDEX.md)\n\n'
 '以下逐字节保留先前记录。\n\n---\n\n').encode()
for n in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
 original=(E/'NAV_ORIGINALS'/n).read_bytes();assert (P/n).read_bytes()==original;(P/n).write_bytes(prefix+original)
print(json.dumps({'reports':len(reports),'review_objects':len(review_files),'production_source_edits':0,'overall':'PARTIAL_STATIC_REPAIR_REVIEW_ONLY'}))
