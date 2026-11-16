"""Administrative extraction/reporting of startup failure. No target logic replay."""
from pathlib import Path
import hashlib
import json

E=Path(__file__).resolve().parent;O=E.parent
R=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch10\native_snapshot')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def report(name,text):(O/name).write_text(text.strip()+'\n',encoding='utf-8')
audit=load(E/'POSTRUN_AUDIT.json');entry=load(E/'ACTIVE_ENTRY_RETURN.json');auth=load(E/'AUTHORIZATION_RECEIPT_LOCK.json')
first=load(R/'inputs/root_private/boot/mr_first_failure.json');close=load(R/'inputs/root_private/boot/mr_close_state.json')
stop=load(R/'out/STOP_REQUEST.json');closed=load(R/'inputs/CLOSED.json');child=load(R/'inputs/root_private/boot/child_initial.json')
waits=[load(p) for p in (R/'inputs/root_private').glob('waitpid_*.json')];assert len(waits)==1;wait=waits[0]
stop_results=[load(p) for p in (R/'inputs').glob('stop_result_*.json')];assert len(stop_results)==1;physical=stop_results[0]
attempts=[json.loads(line) for line in (R/'inputs/root_private/boot/mr_close_attempts.jsonl').read_text().splitlines()]
events=[]
for line in (E/'windows_entry.stdout.raw').read_text(encoding='utf-8',errors='replace').splitlines():
    try:d=json.loads(line)
    except ValueError:continue
    if 'event' in d:events.append(d)
begin=next(d for d in events if d['event']=='PREFLIGHT_BEGIN')['sample']['boottime']
qualified=next(d for d in events if d['event']=='PREFLIGHT_QUALIFIED')['sample']['boottime']
verified=next(d for d in events if d['event']=='ENTRY_VERIFIED')['sample']['boottime']
boot=first['sample']['boot_id']
assert first['error']=='IPC_STATE_MISSING' and first['window'] is None and first['expected_diagnostic'] is False
assert not audit['batch_state_exists'] and not audit['budget_counter_exists'] and not audit['budget_journal_exists']
assert audit['closed_marker_exists'] and audit['STOP_REQUEST_exists'] and not audit['native_seal_exists']
assert not audit['payload_processes'] and not audit['root_role_processes'] and not audit['parent_cgroup_exists']
assert wait['exit_code']==125 and wait['raw_wait_status']==32000
failed=(E/'FAILED_UNITS.stdout.raw').read_text(encoding='utf-8');unit_names=[line.replace('●','').split()[0] for line in failed.splitlines() if line.replace('●','').split()]
previews=[d['review'] for d in events if d['event']=='MR_PREFLIGHT_REVIEW'];assert all(d['units']==['mnt-e.mount'] for d in previews)
bookends={'preflight_begin':begin,'preflight_qualified':qualified,'entry_verified':verified,'child_initial':child['sample']['boottime'],
    'failure_interval':[child['sample']['boottime'],stop['boottime']],'STOP_record_sample':stop['boottime'],'first_failure_sample':first['sample']['boottime'],
    'CLOSED_record_sample':closed['boottime'],'parent_stop_return_sample':physical['sample']['boottime'],
    'child_wait_sample':wait['sample']['boottime'],'cleanup_UNKNOWN_sample':close['sample']['boottime'],
    'seal_error_sample':load(R/'inputs/SEAL_ERROR.json')['sample']['boottime'],
    'host_elapsed_seconds':entry['host_elapsed_seconds'],'STOP_to_CLOSED_record_samples':closed['boottime']-stop['boottime'],
    'STOP_to_parent_stop_return':physical['sample']['boottime']-stop['boottime'],
    'STOP_to_child_wait':wait['sample']['boottime']-stop['boottime'],'Root_owner':next(d for d in events if d['event']=='ENTRY_VERIFIED')['identity'],
    'scheduler':child['child'],'run_boot_id':boot,'T0':None}
put('EXECUTION_TIMELINE.json',bookends)
put('MANAGER_EVENT_ACTUAL.json',{'component':'systemd failed-unit manager','preflight_observations':previews,'postrun_failed_units':unit_names,
    'current_batch_service_exit_events':[],'current_C06_C07_C09_not_started':True,'historical_closed_unit_branch_exercised':False,
    'baseline_mnt_e_handling':'Accepted under frozen read-only rule; no reset performed','actual_error_component':'RootIPC runtime checkpoint called from initial MR query before state creation',
    'UNREVIEWED_MANAGER_FAILURE_exercised':False,'RECOVERY_HEALTH_PASS':False,'recovery_status':'UNRUN_STARTUP_FAILED_PRE_T0'})
put('AUTOMATIC_CLOSURE_ACTUAL.json',{'trigger':'IPC_STATE_MISSING before T0','STOP_auto':stop,'CLOSED_auto':closed,'first_failure':first,
    'attempts':attempts,'internal_result':'UNKNOWN','physical_parent_stop_result':physical,'parent_stop_source':'Frozen coordinator sees STOP_REQUEST and invokes stop_tree(COORDINATOR_STOP_REQUEST)',
    'abort_fallbacks_attempted':['systemctl stop current slice','systemctl kill current slice'],'abort_fallback_outcome':'TimeoutExpired entries; exact successful-return details absent',
    'independent_external_stop_service_started':False,'manual_cleanup_used':False,'caller_cleanup_second_command':False,
    'final_all_roles_empty':True,'Payload_never_started':True,'active_Payload_recovery_proved':False,
    'native_seal':False,'native_seal_error':load(R/'inputs/SEAL_ERROR.json'),'automatic_closure_verdict':'PARTIAL_PREWINDOW_STOP_OBSERVED; CLEANUP_UNKNOWN; SEAL_FAILED_PRE_T0'})
put('REGRESSION_ACTUAL.json',{'declared_jobs':64,'declared_mutants':8,'executed':0,'accepted':0,'mutants_executed':0,'mutants_detected':0,
    'status':'UNRUN_STARTUP_FAILED_PRE_T0','counts_are_not_MUTATION_NOT_DETECTED':True,'raw_MR_cases_present':len(list((R/'inputs/root_private/boot').glob('mr_case_*.json'))),
    'MR_QUALIFICATION_exists':(R/'inputs/MR_QUALIFICATION.json').exists(),'native_diagnostic_marker_exists':(R/'inputs/root_private/boot/mr_diag_injection.json').exists()})
put('FIRST_FAILURE.json',{'status':'STARTUP_FAILED_PRE_T0','primary_error':'IPC_STATE_MISSING','raw_exception':'AdmissionBlocked','source_chain':['guard._launcher_work health(initial)','manager_recovery.health','failed_set/query(record=True)','guard.root_checkpoint(default allow_uninitialized=False)','root_ipc.checkpoint requires inputs/batch_state.json'],
    'cause':'Initial read-only manager health query precedes state creation but uses active-runtime checkpoint',
    'secondary_gaps':['No runtime deadline before T0; abort records DEADLINE_UNKNOWN and emergency subprocess timeouts','guard.seal/Boot before_seal assumes runtime state exists; native seal fails on absent state'],
    'source_repaired':False,'retry':False,'protocol_counterexample':False,'first_error_preserved':True})
result={'status':'STARTUP_FAILED_PRE_T0','version':'ManagerRecovery-static-1/r5','batch_id':'batch10','scope':'MR_RECOVERY_DIAGNOSTIC_ONLY',
    'A1':'UNRUN_STARTUP_FAILED_PRE_T0','A2':'PARTIAL_AUTOMATIC_STOP; CLEANUP_UNKNOWN; NATIVE_SEAL_FAILED','A3':{'executed':0,'accepted':0,'mutants_detected':0},
    'A4':'No T0/counter/journal; startup host elapsed2.0633844s; roles exited','A5':'NOT_READY_NEW_STATIC_FIX_REQUIRED',
    'preflight':'PREFLIGHT_PASS','same_PID_exec':'PASS','C00':'UNRUN','C09':'UNRUN','MR64':'UNRUN','RECOVERY_HEALTH_PASS':False,
    'T0':None,'deadline':None,'R':None,'counter_created':False,'CLOSED':True,'STOP_REQUEST':True,'manual_cleanup':False,
    'native_seal':False,'final_roles_empty':True,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE',
    'PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','test_retries':0,'source_repairs':0,'next_batch_created':False,
    'time_feasibility':'TIME_FEASIBILITY_UNRESOLVED_NO_CALIBRATION'}
put('MRA_RESULT.json',result)
P='Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。\n\n'
report('MRA_AUTHORIZATION_AND_LOCK.md','# MR-A授权及绑定\n\n'+P+f'''本次用户明确批准有限阶段A，绑定最终r5。实际scope=MR_RECOVERY_DIAGNOSTIC_ONLY，Full=false，Manager诊断及关闭注入批准=true。冻结方案以单项C10后返回78为收尾；完整C10–C12链及阶段B、S34/门18/F1F4保持关闭。本轮在更早前言失败，C10范围没有实际触发。

manifest `e32453a883905db0089e7fd480f43283edeba2d87604407bbea55f4b14c2d395`，execution_lock `a8358f504248377340e86c5d0b79210fd18c7c3207096f9fe7c7e27e4b928c64`。46项/31程序host及45份Linux源/输入实际摘要一致，原生Python3.12.3核验通过。回执SHA `{auth['receipt_sha256']}`，原文SHA `{auth['request_sha256']}`，控制目录为ManagerRecovery-Fix/authorization/batch10-r5。申请正文一处裸r4为历史文案残留，源码/执行锁/最终摘要及本次明确版本均为r5，历史文本保持。

运行boot={boot}；Root owner PID12242/start699487跨exec，初始scheduler PID{child['child']['pid']}/start{child['child']['start_ticks']}。预检及同进程exec通过，当前窗口目录与一次认领建立；正式T0、deadline、counter/journal均未初始化。旧CalDiag及历史账保持。

[实际授权](evidence/execution_authorization.json) · [源码与范围准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [入口实际argv](evidence/ACTIVE_ENTRY_INVOCATION.json)。
''')
report('MRA_MANAGER_EVENT_RESULTS.md','# systemd manager事件结果\n\n'+P+'''冻结预检进行了3次MR_PREFLIGHT_REVIEW，实际失败单位集合均仅含mnt-e.mount，按既有基线规则接受，整个过程只读。事后failed集合仍仅mnt-e.mount，没有本批C06/C07/C09服务退出事件，历史batch09单位实例分支本次没有触发。

manager版本、当前boot、Root/权限及源/工具摘要由原生预检fresh核对，systemd查询正常返回。实际错误来自初始MR query先调用RootIPC运行态检查点，检查点要求batch_state.json存在；该文件本应在后续初始化中创建。它与过去的UNREVIEWED_MANAGER_FAILURE是不同的新初始化顺序错误。

本次未生成本批管理器退出审查证书，也没有真实C09后恢复证据。UNREVIEWED_MANAGER_FAILURE处理正确性保持UNRUN，不能用基线mnt-e被接受替代本批预期退出或异常退出验收。

[实际manager摘要](evidence/MANAGER_EVENT_ACTUAL.json) · [首次异常](evidence/FIRST_FAILURE.json)。
''')
report('MRA_RECOVERY_HEALTH_RESULTS.md','# 恢复健康动态状态\n\n'+P+'''A1=UNRUN_STARTUP_FAILED_PRE_T0。C00、C09、MR64及后续恢复均未启动；RECOVERY_HEALTH_PASS=false，含义为尚未取得该结果。

原CalDiag真实C09 PASS、T0+48.592秒和194项/41变异保持历史归属。本批对新r5只取得预检/启动身份的实际证据，初始健康检查在T0之前失败。首错为IPC_STATE_MISSING，未发生新的ACK/Receiver/退出/恢复事件，也未达到预声明的C10后返回78故障点。

修复建议应限于PRE_WINDOW与ACTIVE窗口的检查点职责：预窗只读manager查询仍核当前boot、sealed初始身份、SOURCE/receipt、STOP/CLOSED和新目录约束；运行窗建立后继续强制state/预算。不能将allow_uninitialized无差别放开到恢复或正式执行。当前源码冻结，本轮不实施修复。

[实际阶段结果](evidence/MRA_RESULT.json) · [根因链](evidence/FIRST_FAILURE.json)。
''')
report('MRA_AUTOMATIC_CLOSURE_RESULTS.md','# 自动关闭、兜底与退出\n\n'+P+f'''A2=PARTIAL_PREWINDOW_STOP_OBSERVED，r5内部结果CLEANUP_UNKNOWN，原生seal失败。本次是非预期真实启动异常；预声明的C10后故障注入未到达。

|职责|实际结果|
|---|---|
|主触发|初始scheduler在异常wrapper中自动设置HALTED并生成STOP_REQUEST|
|STOP/CLOSED|均为自动路径产生；CLOSED原因COORDINATOR_STOP_REQUEST|
|父协调器停止|观察STOP，调用原stop_tree；stop_exit={physical['stop_exit']}、empty=true|
|abort内部后备|当前slice stop/kill有尝试，记录两项TimeoutExpired；没有足够日志给出各命令完整返回|
|独立external-stop服务|尚未启动，因此该来源本次未验证|
|人工/第二条清理命令|0；仅做事后只读导出|
|r5关闭结果|两轮记录UNKNOWN，含DEADLINE_UNKNOWN/PRIMARY_CLEANUP:LimitReached/两个EXTERNAL_STOP:TimeoutExpired|
|原生封存|SEAL_ERROR=FileNotFoundError，缺batch_state；out/EVIDENCE.zip不存在|
|最终退出|scheduler直接waitpid exit125/raw32000；事后Root/Payload角色全空，父cgroup不存在|

STOP记录→CLOSED记录书签差{bookends['STOP_to_CLOSED_record_samples']:.9f}秒；STOP→父停止返回采样{bookends['STOP_to_parent_stop_return']:.9f}秒；STOP→child wait采样{bookends['STOP_to_child_wait']:.9f}秒。它们是已有书签跨度，CLOSED精确持久完成在记录采样与停止结果之间；异常指令/ABORTING瞬时转换缺独立打点。

本批Payload从未启动，现有组空证据只能说明无残留，尚不证明活动Payload回收能力。实际角色全空与producer保留UNKNOWN分别登记，不据事后观察改写旧UNKNOWN。主路径产生停止信号，父协调器既有停止路径完成关闭；原生自动seal责任仍失败。最终研究ZIP属于行政证据打包，不能充当原生自动seal通过。

[关闭实际数据](evidence/AUTOMATIC_CLOSURE_ACTUAL.json) · [退出/时间](evidence/EXECUTION_TIMELINE.json) · [原生事后审计](evidence/POSTRUN_AUDIT.json)。
''')
report('MRA_REGRESSION_RESULTS.md','# 64项回归与8项变异\n\n'+P+'''A3：冻结64项实际执行0、获接受0；8项变异实际执行0、检出0。所有结果为UNRUN_STARTUP_FAILED_PRE_T0，原始mr_case_###及MR_QUALIFICATION均未生成。

这些数量表示阶段未到达，不能登记为已运行后MUTATION_NOT_DETECTED。当前目标行为未被实际exercise，正控制/注入/独立oracle/变异效果均继续待验。原31程序、64固定输入及独立oracle保持冻结，本轮没有运行关闭后的独立重放来补数字。

READY64/RootIPC56/BC40/H34、C00–C09等前置同样尚未启动；过去CalDiag通过结果保持各自范围。当前也没有新的PASS_BOUNDED。

[机器数量](evidence/REGRESSION_ACTUAL.json) · [全部冻结输入](evidence/FROZEN_SOURCE_REFERENCE/inputs/manager_contract.json)。
''')
report('MRA_RUNTIME_AND_RESOURCE.md','# 时间、预算及资源\n\n'+P+f'''A4：启动host调用{entry['host_elapsed_seconds']:.9f}秒，exit125；T0/deadline/R=null，counter、intent、journal及Root检查预付均未创建。无预算账时保持未初始化，不能填写R=0或虚构配对事务。

预检开始→通过{qualified-begin:.9f}秒，开始→same-PID entry验证{verified-begin:.9f}秒；child wait退出在预检开始后{wait['sample']['boottime']-begin:.9f}秒。所有Native跨度来自同boot CLOCK_BOOTTIME；host perf_counter单列。完整300秒校准时间继续TIME_FEASIBILITY_UNRESOLVED_NO_CALIBRATION。

原资源合同1,000,000/1,800/300/100,000/64,082/提前1,740、AS1GiB和Payload4tasks保持。Root bootstrap自限1GiB并被初始scheduler继承；Payload服务/slice未激活，实际Payload峰值和任务高水位不适用，Root RSS峰值未采样。单位定义安装按冻结预检执行，实际资源使用资格尚未到C00。

保存22份Native常规原件及46份冻结源导出；socket/非regular对象另记元数据。STOP/CLOSED存在，原生ZIP缺失。当前所有受控角色为空、父cgroup不存在。历史6,068份文件及47误路径副本最终hash复核，旧CalDiag账38,729保持。

[真实时间书签](evidence/EXECUTION_TIMELINE.json) · [Native审计](evidence/POSTRUN_AUDIT.json) · [历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。
''')
timeline_rows=[('预检开始',begin),('预检通过',qualified),('同PID entry验证',verified),('初始child记录',child['sample']['boottime']),('STOP记录',stop['boottime']),('首错记录',first['sample']['boottime']),('CLOSED记录',closed['boottime']),('父停止结果',physical['sample']['boottime']),('child wait125',wait['sample']['boottime']),('最终UNKNOWN记录',close['sample']['boottime']),('seal错误记录',bookends['seal_error_sample'])]
report('MRA_EXECUTION_TIMELINE.md','# MR-A实际时间线\n\n'+P+'|事件|CLOCK_BOOTTIME|自预检开始秒|\n|---|---:|---:|\n'+'\n'.join(f'|{name}|{t:.9f}|{t-begin:.9f}|' for name,t in timeline_rows)+f'''

本批boot={boot}，Root12242/start699487，scheduler{child['child']['pid']}/start{child['child']['start_ticks']}。抛错发生在child记录与STOP采样之间，精确raise时点未打点。ABORTING由冻结控制流及后续CLEANUP文件见证，临时状态精确发布时刻缺独立记录。

初始化顺序为sealed认领/exec→child_admission→health(initial)→query(record=True)→root_checkpoint要求state→IPC_STATE_MISSING。后续创建T0/账的分支从未执行。自动父停止与abort尝试并发，不能把各条采样强行解释成单线程严格总序；原始每个actor/退出状态均保存。

[结构化时间线](evidence/EXECUTION_TIMELINE.json) · [原始stdout](evidence/windows_entry.stdout.raw) · [原始stderr](evidence/windows_entry.stderr.raw)。
''')
report('MRA_COUNTEREXAMPLES.md','# 首次失败与新增实现缺口\n\n'+P+'''|登记|真实观察|结论|
|---|---|---|
|MRA-INIT-1|health(initial)在T0创建前调用query(record=True)，query的root_checkpoint默认要求batch_state|启动生命周期接线缺陷，IPC_STATE_MISSING在初始phase必然拒绝|
|MRA-CLOSE-2|state/BOOT_START/STOP_ARMED都尚未建立，abort无法得到运行deadline，留下UNKNOWN及后备超时|预窗口错误关闭上下文缺少已有的启动TCB期限；不能凭空造运行窗|
|MRA-SEAL-3|seal/Boot before_seal依赖不存在的batch_state，记录FileNotFoundError|预窗口封存分支缺口，原生自动seal未完成|

首错属于r5验证编排实现缺陷；静态检查未捕获该初始化依赖。预检manager查询正常，当前failed集合仅mnt-e，无新UNREVIEWED_MANAGER_FAILURE或C09交接错误可供裁决。原CalDiag实际通过和旧失败保持。

下一静态修复建议限于：把PRE_WINDOW只读身份/停止/boot核验与ACTIVE state检查明确分开；仅已认证初始阶段使用受限allow_uninitialized，恢复和正式执行仍要求state；预窗停止使用已绑定sealed/preflight期限与已登记Owner/child证据；预窗封存不依赖虚构T0/账，明确记录未初始化。增加对应前言故障和正向启动控制的独立fixture后重新冻结，再申请新独立有限A。

本轮源码/输入/判据/权限/上限修复0、重跑0、人工清理0、T0/预算重置0、自动下一批0。当前batch10已有CLOSED/一次认领事实，后续保持关闭，不能以缺T0为由重用同一目录或回执。

[首错链](evidence/FIRST_FAILURE.json) · [关闭原件](evidence/AUTOMATIC_CLOSURE_ACTUAL.json)。
''')
answers=[('1 批次启动','新身份/单会话/一次认领/exec成立，正式预算运行窗未建立'),('2 预检/C00/C09','PREFLIGHT_PASS；C00/C09 UNRUN'),('3 failed集合','三次预检和事后仅mnt-e.mount，按冻结基线接受'),('4 UNREVIEWED处理','当前退出实例未产生；该修复验收UNRUN'),('5 C09后恢复','UNRUN_STARTUP_FAILED_PRE_T0'),('6 64实际数量','执行0/接受0'),('7 8变异','执行0/检出0，保持UNRUN'),('8 自动关闭','真实非预期启动错误触发STOP/CLOSED；主关闭结果UNKNOWN，预期78故障点未到达'),('9 兜底','父协调器自动stop_tree返回0；abort内stop/kill超时；独立停止服务未启动，人工清理0'),('10 清理UNKNOWN','r5内部结果UNKNOWN保持；事后受控角色全空分别记录'),('11 停止/组空','见同boot时间书签；无活动Payload，组空回收耗时不适用'),('12 预算/时间','R/T0/deadline null；host2.0633844秒；Root RSS未测，无Payload资源高水位'),('13 新缺陷','预窗query要求state、预窗关闭期限及seal依赖缺口'),('14 300秒证据','无新校准性能数据，TIME_FEASIBILITY_UNRESOLVED_NO_CALIBRATION'),('15 后续完整链','尚不具备；先最小静态修复初始化及预窗关闭/封存，再新独立A验收')]
report('MRA_FINAL_DECISION.md','# MR-A最终裁决\n\n'+P+'''**STARTUP_FAILED_PRE_T0：预检及same-PID exec通过，r5初始健康查询触发IPC_STATE_MISSING。真实C09恢复与64项回归尚未执行。**

|最终问题|真实回答|
|---|---|
'''+ '\n'.join('|'+a+'|'+v+'|' for a,v in answers)+'''

A1=UNRUN_STARTUP_FAILED_PRE_T0；A2=PARTIAL_AUTOMATIC_STOP / CLEANUP_UNKNOWN / NATIVE_SEAL_FAILED；A3执行0、变异检出0；A4未初始化预算；A5需新的静态补缺。现有自动STOP和父协调器停止实际发生，所有受控进程最终退出，CLOSED保留；本轮没有用第二条人工清理命令替代自动关闭。原生seal缺失，当前研究ZIP只作行政证据包。

冻结入口只执行1次、返回125，Root child直接waitpid raw32000/125；预声明C10后返回78注入尚未发生。Source46、输入和权限保持原样，现场修复/重跑/新窗口/自动下一批均0。历史6,068份文件、误路径47及旧CalDiag38,729账保持。

RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]，D1/D2原条件、强G、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持。资源资格、模型正确性和原创性继续分别裁决。

[首次反例及下一修复](MRA_COUNTEREXAMPLES.md) · [自动关闭结果](MRA_AUTOMATIC_CLOSURE_RESULTS.md) · [时间/资源](MRA_RUNTIME_AND_RESOURCE.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('README.md','''# DCL-R6-MR-A

batch10-r5真实有限A，STARTUP_FAILED_PRE_T0。预检/exec通过，初始健康查询遇IPC_STATE_MISSING；T0/R未初始化，C00/C09/MR64均未到达。自动STOP/CLOSED与父停止已观察，r5内部UNKNOWN、原生seal失败，事后角色全空。模型保持未运行。

[最终裁决](MRA_FINAL_DECISION.md) · [新缺口](MRA_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md)。
''')
print(json.dumps({'status':result['status'],'boot':boot,'T0':None,'R':None,'STOP_to_CLOSED_samples':bookends['STOP_to_CLOSED_record_samples'],
 'STOP_to_parent_stop_return':bookends['STOP_to_parent_stop_return'],'MR_executed':0,'manual_cleanup':False,'native_seal':False,'roles_empty':True},ensure_ascii=False))
