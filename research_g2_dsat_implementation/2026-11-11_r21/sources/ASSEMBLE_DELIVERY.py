"""R21 evidence/report assembly. No application imports or project tests."""
import ast
import datetime
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(r"D:\毕业设计");PROJECT=ROOT/"auth-lifecycle"
BASE=ROOT/"research_g2_dsat_implementation";OUT=BASE/"2026-11-11_r21"
R20=BASE/"2026-11-11_r20";RUNS=BASE/"2026-11-11_r21_d1b1_offline"

def load(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,d):
    text=d.strip()+"\n" if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+"\n"
    (OUT/n).write_text(text,encoding="utf-8")

lock=load(OUT/"D1B1_FILE_LOCK.json");pre=load(OUT/"sources/PRECHECK_LOCK.json")
final=[load(RUNS/(s+"_002")/"RESULTS.json") for s in ["new52","r19_24","legacy44"]]
new,oldD,oldAH=final
history=load(RUNS/"TEST_RUNS.json")
all_results=[load(x['path']) for x in history['runs']]
assert len(history["runs"])==6
assert all(r["passed"] for r in final)
assert all(r["code"]==lock["executed_code"] for r in final)
assert all(sha(x["path"])==x["sha256"] for x in lock["executed_code"])
mods={x["path"] for x in pre["allowed_modifications"]}
protection=[{"path":x["path"],"before_sha256":x["sha256"],"after_sha256":sha(x["path"]),
             "authorized_modify":x["path"] in mods} for x in pre["protected_files"]]
assert all(x["authorized_modify"] or x["before_sha256"]==x["after_sha256"] for x in protection)
put("sources/INTEGRITY_POSTCHECK.json",{"schema":"r21-integrity/1","rows":protection,
    "R20_original_protected":1133,"original_group_unchanged":1130,"R20_and_other_extra_protected":25,
    "total_unique_protected":1158,"allowed_modified":3,"other_unchanged":1155})

# Preserve exactly what each test driver reported; acceptance audit is separate.
raw_counts={x:sum(r["counts"][x] for r in final) for x in ["PASS","FAIL","ERROR","SKIP","BLOCKED","NOT_RUN"]}
blocked={"F23":"stale-marker classification tested; restart entry does not yet consume/check old operation journals",
         "F26":"same-process authorization replay tested; persistent cross-process startup approval responsibility unresolved",
         "T45":"spent start retained in current context; independent-process admission/spending not implemented"}
rows=[]
for r in final:
    for c in r["cases"]:
        rows.append({**c,"suite":r["suite"],"raw_execution_status":c["status"],
            "contract_acceptance_status":"BLOCKED" if c["id"] in blocked else c["status"],
            "acceptance_reason":blocked.get(c["id"],"frozen bounded test expectation observed")})
acceptance={x:sum(c["contract_acceptance_status"]==x for c in rows) for x in raw_counts}
put("D1B1_ACTUAL_RESULTS.json",{"schema":"r21-combined-actual-results/1","TOTAL":120,
    "raw_execution_counts":raw_counts,"contract_acceptance_counts":acceptance,"cases":rows,
    "raw_results":[{"path":str(RUNS/(r["suite"]+"_002")/"RESULTS.json"),"sha256":sha(RUNS/(r["suite"]+"_002")/"RESULTS.json")} for r in final],
    "final_satisfied_checks":sum(len(c["checks"]) for r in final for c in r["details"]),
    "full_frozen_contract_accepted":False,"audit_blockers":blocked,
    "reason_counts_differ":"unit runners returned120 PASS; final source/coverage audit withholds three stronger cross-process obligations; original run files unchanged",
    "R19_historical_passes_added_to_current_count":False,"new_deployment_executed":False})
put("D1B1_TEST_RUNS.json",{**history,"direct_invocations":6,"per_suite_invocations":2,
    "distinct_final_ids":120,"all_executed_case_occurrences":240,"observed_test_failures":0,
    "second_trio_reason":"informed source-review refinements; all first-trio tests passed; original IDs/assertions retained",
    "additional_project_test_invocations_authorized":0,
    "history_note":"R21 contains no failed or early-aborted actual suite invocation"})
faults=load(R20/"D1B_FAILURE_AND_CLEANUP_MATRIX.json")["rows"]
details={x["id"]:x for x in new["details"]}
coverage=[]
for f in faults:
    d=details[f["id"]]
    grade="SIMULATED_CONTROL_BOUNDARY_WITH_REAL_WINDOWS_OWNER"
    if f["id"] in {"F08","F09","F14"}:grade="REAL_TEMP_SQLITE_AND_INJECTED_CHECKPOINT_FAILURE"
    if f["id"] in {"F19","F22","F24"}:grade="REAL_OWNED_WINDOWS_STUB_PROCESS_AND_LOCK"
    if f["id"]=="F13":grade="REAL_TEMP_TLS_MATERIAL_WITH_SIMULATED_LISTENER_FAILURE"
    if f["id"]=="F25":grade="REAL_NEW_ENCRYPTED_TEST_DB_COPY_AND_FILE_ID_CHECK"
    coverage.append({**f,"original_frozen_status":f["status"],"execution_status":"PASS",
        "status":"BLOCKED" if f["id"] in blocked else "PASS",
        "contract_acceptance_status":"BLOCKED" if f["id"] in blocked else "PASS",
        "blocker":blocked.get(f["id"]),"evidence_grade":grade,"actual_checks":len(d["checks"]),
        "detail_locator":str(RUNS/"new52_002/RESULTS.json")+"#/details/"+str(list(details).index(f["id"])),
        "actual_observations":d["observations"],"resources":d["resource_ledgers"]})
put("D1B1_FAILURE_COVERAGE.json",{"schema":"r21-failure-coverage/1","TOTAL":28,"raw_executed":28,
    "raw_PASS":28,"full_contract_PASS":26,"full_contract_BLOCKED":2,"rows":coverage,
    "actual_Authority_service_crashes":0,"native_power_loss_tests":0})

all_runtime_files=[p for p in RUNS.rglob('*') if p.is_file()]
private_suffixes={".key",".pem",".pfx"}
catalog=[]
for p in sorted(all_runtime_files):
    row={"path":str(p),"bytes":p.stat().st_size}
    if p.suffix.lower() in private_suffixes:row.update(kind="OWNED_TEMPORARY_TEST_KEY",sha256=None,hash_policy="private test key contents/hash omitted")
    else:row.update(kind="OWNED_TEST_OR_EVIDENCE",sha256=sha(p))
    catalog.append(row)
case_costs={c["id"]:c["elapsed_ns"] for r in final for c in r["details"]}
maps={"C_source_validation":["F03","T31"],"C_identity":["F02","T32","T39","T41"],
    "C_initialization":["F07","F08","F09","T34"],"C_database":["F14","T35","T50"],
    "C_key":["F10","F11","T34"],"C_tls":["F12","F13","T36"],"C_logging":["F14","T49"],
    "C_host":["F15","T38"],"C_listener":["F16","F17","F18","T40"],
    "C_shutdown":["F20","F21","T42"],"C_recovery":["F22","F23","F25","T43","T44"],
    "C_cleanup":["F06","F19","T37"],"C_retry":["F26","F27","F28","T45","T46"]}
costs={k:{"case_ids":v,"inclusive_case_ns":sum(case_costs[x] for x in v),"meaning":"overlapping case-level coverage proxy; no isolated production component benchmark"} for k,v in maps.items()}
timer_sums={}
for d in new["details"]:
    for ledger in d["resource_ledgers"]:
        for k,v in ledger["cost_ns"].items():timer_sums[k]=timer_sums.get(k,0)+v
resource={"schema":"r21-resource-ledger/1","measurement_scope":"owned offline tests; application attempts/SQL native calls distinguished",
    "final_suites":[{"suite":r["suite"],"audit":r["audit"],"scope_counts":r["scope_counts"],"memory":r["memory"],"elapsed_ns":r["elapsed_ns"]} for r in final],
    "final_new52_SQL":{"execute_attempts":75,"execute_returned":73,"execute_failures":2,"failure_meaning":"one deliberate ATTACH authorizer denial and one access to an already-closed connection",
        "explicit_rollback_calls":1,"initializer_normal_wrappers":15,"strict_constructor_normal_wrappers":7,
        "composed_normal_boot_bound":22,"single_real_production_boot_measured":False,"VFS_internal_operations":"NOT_MEASURED"},
    "final_new52_own_children":new["owned_children"],"final_child_exit_codes":[x["result"]["exit_code"] for x in new["owned_children"]],
    "lock_conflict_evidence":[{"id":"F24","asserted_conflicts":1,"basis":"two actual child results checked as LOCKED/CONFLICT"},{"id":"T39","asserted_conflicts":1,"basis":"parent re-open denied while inherited child handle held"}],
    "actual_seed_function_failure_records":sum(e['event']=='seed_failed' for d in new['details'] for q in d['resource_ledgers'] for e in q['events']),
    "injected_cleanup_failure_records":sum(e.get('errors',0) for d in new['details'] for q in d['resource_ledgers'] for e in q['events'] if e['event']=='owned_cleanup'),
    "recovery_classification_verified_case_ids":["F22","F23","F25","T43","T44","T52"],
    "actual_recovery_restart_operations":0,
    "child_window_sum_seconds":sum(x["result"]["elapsed_seconds"] for x in new["owned_children"]),
    "all_runs_totals":{"owned_test_child_launches":sum(x['audit']['child_launch_attempts'] for x in all_results),
        "file_SQLite_connections":sum(x['audit']['file_SQLite_connections'] for x in all_results),
        "R19_memory_connections":sum(x['audit']['memory_SQLite_connections'] for x in all_results if x['suite']=='r19_24'),
        "legacy_memory_connections":sum(x['audit']['memory_SQLite_connections'] for x in all_results if x['suite']=='legacy44'),
        "temporary_state_key_generations":sum(x['scope_counts'].get('test_state_keys_generated',0) for x in all_results),
        "temporary_TLS_key_certificate_generations":sum(x['scope_counts'].get('test_TLS_material_generated',0) for x in all_results),
        "test_SSLContext_load_calls":sum(x['scope_counts'].get('test_SSLContext_loads',0) for x in all_results),
        "direct_suite_processes":len(all_results),"owned_child_forced_terminations":sum(c['result']['terminated_owned_stub'] for x in all_results for c in x['owned_children'])},
    "final_new52_limits":{"file_connections_cap":104,"per_case_connections_cap":2,"children_cap":8,"concurrent_children_cap":2,
        "temporary_state_key_cap":2,"temporary_TLS_generation_cap":2,"SSLContext_load_cap":2,"private_directory_cap":64,"file_path_cap":512,"output_byte_cap":67108864},
    "inclusive_suite_total_ns":sum(r["elapsed_ns"] for r in final),"case_cost_categories":costs,"partial_core_call_timers_ns":timer_sums,
    "logical_current_output_bytes":sum(x["bytes"] for x in catalog),"logical_current_file_paths":len(catalog),"runtime_catalog":catalog,
    "physical_allocation_peak_and_VFS_IO":"NOT_MEASURED","old_suite_peak_memory":"NOT_MEASURED",
    "measurement_limits":"main-entry clock to result construction; excludes interpreter startup/top-level imports and trailing result/index flush; ledger timers cover selected calls; case categories overlap",
    "real_D1B2_costs":"NOT_MEASURED","real_deployment_P1_P2_RPC_native_operations":0}
put("D1B1_RESOURCE_LEDGER.json",resource)

# Actual textual diffs and semantic preservation checks.
diff=[];semantic={};changed=[]
for x in lock["targets"]:
    p=Path(x["path"])
    if p.suffix!='.py':continue
    after=p.read_text(encoding='utf-8');before=''
    if x["before_sha256"]:
        original=OUT/'sources/original'/(p.name+'.txt');before=original.read_text(encoding='utf-8')
        changed.append({"path":str(p),"before_sha256":x["before_sha256"],"after_sha256":sha(p),"original_snapshot":str(original),"snapshot_sha256":sha(original)})
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+p.name,tofile='after/'+p.name))
    if p.name=='storage.py':
        b=next(n for n in ast.parse(before).body if isinstance(n,ast.ClassDef) and n.name=='AuthorityStore')
        a=next(n for n in ast.parse(after).body if isinstance(n,ast.ClassDef) and n.name=='AuthorityStore')
        dump=lambda n:ast.dump(n,include_attributes=False)
        semantic['storage_business_methods_unchanged']={n.name:dump(n)==dump(next(v for v in a.body if isinstance(v,ast.FunctionDef) and v.name==n.name)) for n in b.body if isinstance(n,ast.FunctionDef) and n.name!='__init__'}
    if p.name=='services.py':
        for name in ['SingleActive','Controller','FakeProvider']:
            find=lambda text:next(n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name==name)
            semantic[name+'_AST_unchanged']=ast.dump(find(before),include_attributes=False)==ast.dump(find(after),include_attributes=False)
put('sources/CODE.diff',''.join(diff))
put('CODE_DIFF.json',{'schema':'r21-code-diff/1','modified':changed,'new_python':[x for x in lock['executed_code'] if x['path'] not in mods],
    'fixture_files':lock['inputs'],'semantic_preservation':semantic,'actual_existing_modifications':3,'other_protected_unchanged':1155,
    'diff':'sources/CODE.diff','old_locks_modified':False})
commands={op:{'actual_script':str(PROJECT/'scripts/run_h2_authority_service.py'),'script_sha256':sha(PROJECT/'scripts/run_h2_authority_service.py'),
    'supported_arguments':['--manifest PATH','--mode offline','--operation '+op,'--approval-ref R21_RECEIPT','--result OWNED_NEW_PATH (optional)'],
    'executed_in_process_driver':True,'real_deployment_command_executable':False,'actual_D1B2_argv':None,
    'execution_boundary':'same-process trusted test scope; independent process resumption not implemented; recover can classify a persisted receipt',
    'D1B2_AUTHORIZED':False,'P1_P2_AUTHORIZED':False} for op in ['prepare','initialize','start','status','stop','recover']}
put('D1B1_COMMAND_LOCK.json',{'schema':'r21-offline-command-lock/1','offline_parser_implemented':True,'operations':commands,
    'actual_test_commands':[{'executable':r['executable'],'argv_interpreter':r['argv_interpreter'],'suite':r['suite']} for r in final],
    'D1B2_actual_argv':None,'D1B2_command_executable':False,'D1B2_authorized':False,
    'blockers':['real deployment admission factory absent','native bounded network adapter/owned supervisor incomplete','cross-process operation approval/spending unresolved','actual deployment SID/source snapshot/key/TLS/DB and exact start-stop argv need independent approval']})
supplement_paths=[PROJECT/'src/auth_lifecycle/online_state'/n for n in ['dsat_authority_live.py','dsat_authority_lifecycle.py','dsat_windows_runtime.py']]+[PROJECT/'tests/test_dsat_authority_live_lifecycle.py',PROJECT/'scripts/run_dsat_authority_live_lifecycle_tests.py',PROJECT/'tests/fixtures/dsat_authority_live_lifecycle']
put('SUPPLEMENTAL_AUTHORIZATION_REQUEST.json',{'schema':'r21-supplemental-request/1','approved':False,'executed':False,
    'purpose':'close F23/F26/T45 persistent start-admission obligations with owned independent-process evidence',
    'targets':[{'path':str(p),'before_sha256':sha(p) if p.is_file() else None,'action':'MODIFY_EXISTING' if p.is_file() else 'ADD_FIXTURE_WITHIN_EXISTING_SUBTREE'} for p in supplement_paths],
    'current_code_frozen_unchanged':True,'requested_next_record':str(BASE/'2026-11-11_r22_d1b1_closure'),
    'requested_test_output':str(BASE/'2026-11-11_r22_d1b1_closure_offline'),
    'code_responsibilities':['read bounded persisted marker/start-claim state before re-admission; malformed/ambiguous state refuses',
        'bind a distinct one-shot startup approval to full instance/source/config/OS/epoch tuple; trusted job test scope alone is not the one-shot grant',
        'exclusive durable start-consumption before any Store/supervisor creation; uncertain consumption stays spent',
        'add finite owned worker admission protocol and two independent-process supplement cases X01/X02; preserve current52 IDs and all old test sources'],
    'future_tests':{'new_domain':54,'R19':24,'legacy':44,'total':122,'direct_invocations':3,'automatic_rerun':0,
        'fault_witnesses':['X01 stale marker and old epoch refuse independent-process re-admission','X02 previously consumed startup grant refuses independent-process replay'],
        'caps_per_new_domain':{'own_children':8,'concurrent_children':2,'child_seconds_each':10,'child_seconds_total':60,
            'file_SQLite_connections':104,'per_case_connections':2,'state_test_keys':2,'TLS_test_materials':2,'SSLContext_loads':2,
            'private_directories':64,'file_paths':512,'logical_output_bytes':67108864,'test_threads_peak':4,'threads_created':16},
        'R19_memory_connections':8,'legacy_memory_connections':32},
    'closed':['real deployment directory','network/socket/TLS handshake','actual Authority/Controller/Provider/Casdoor service','P1/P2','S3B2/S5','new dependencies','old locks/tests mutation'],
    'success_means':'specific three blocked obligations may be reconsidered; standalone six-operation supervisor/native deployment adapter remains separately reviewed',
    'permission_reason':'R20 per-suite repair-rerun allowance used; R21 inherits stricter caps; additional code validation needs a distinct explicit scope'})

header='日期：2026-11-11。范围：R21明确批准的九目标及离线合成验收。过程为本对话内模型辅助实现、实际执行与知情复核；外部独立核验待取得。\n\n'
put('01_IMPLEMENTATION_SUMMARY.md','# G2-R21实施摘要\n\n'+header+r'''
九个逻辑目标均已落地。最终三组单元运行结果为 **120 PASS，FAIL/ERROR/SKIP/BLOCKED/NOT_RUN均0**，2366条内部检查满足。交付源码审查另发现跨进程接纳责任尚未闭合：**完整合同验收为117 PASS、3 BLOCKED**，整体状态为 **D1B1_PARTIAL_IMPLEMENTATION**。

两套统计分别保留。120是本轮真实重跑的52＋24＋44，不包含R19历史通过数；3个阻塞来自F23/F26/T45的较强跨进程条件，单元runner原始输出保持原字节。

| 九目标 | 实物 |
|---|---|
| services.py | 保留旧服务；新增受控offline listener工厂、LiveContext在配置I/O前拒绝真实运行 |
| storage.py | 可选strict bootstrap路径，原默认和业务方法保持 |
| run_h2_authority_service.py | 六操作offline parser和受控分派，原D1-A参数兼容 |
| dsat_authority_live.py | opaque test issuer/context、来源/实例/epoch/同Store关联、P2固定拒绝 |
| dsat_authority_lifecycle.py | 所有权栈、真实新文件SQLite15SQL、strict Store7SQL、阶段/日志/分类恢复 |
| dsat_windows_runtime.py | 真实自有Windows SID/PID/创建时点/file-ID、私有DACL、独占锁、句柄交接、Event及stub管理 |
| test_dsat_authority_live_lifecycle.py | F01–F28/T29–T52，增强子断言保持原ID |
| run_dsat_authority_live_lifecycle_tests.py | 三域runner、固定worker协议、拒绝钩子、日志/快照/预算 |
| 新fixture树 | 原冻结计划、确认配置、公开向量副本及新合成哨兵 |

仅修改3个既有文件，新增5个Python文件及1个fixture子树。研究目录中的汇编脚本仅处理报告、哈希和JSON。源码及入口定位见D1B1_FILE_LOCK.json。

实际底层行为包括11次新临时文件SQLite连接、6个拥有的测试子进程、2个测试state key、1套TLS测试材料和2次SSLContext加载。Authority网络服务、真实RPC、P1/P2、生产库和密钥访问全部0。

本轮离线核心提供了可复现的启动/失败关闭基础。独立shell中的分阶段操作、真实部署接纳、原生有界网络适配与一次性启动批准仍须补齐，当前材料没有把它们登记为可部署成品。
''')
put('02_INSTANCE_IDENTITY_AND_SINGLE_ACTIVE.md','# 实例身份与Authority单活结果\n\n'+header+r'''
真实Win32测试核对当前测试宿主的TokenUser SID、PID、创建FILETIME、image，以及新测试目录/文件的最终路径、volume/file-ID与DACL。只处理自身和本轮创建的stub，系统进程枚举0。所测SID属于测试宿主，未来部署SID仍需单独指定。

TestScope仅由核验R21 receipt、请求原文哈希、固定Python和获批输出树的工厂创建。opaque证据/issuer/context保存在进程内registry；请求自报trusted、普通dict及未登记对象安全拒绝。源字节与已加载内部模块__file__/spec.origin均有核对，无法替代硬件内存证明或对恶意同SID代码的隔离。

实例记录把实际根file-ID、UUID、source/config摘要和singleton scope绑定。Store/connection/RLock在同一上下文中检查，替换connection和重复bind均拒绝。P2门始终关闭，新context不发行真实permit。

| 证据 | 结果及范围 |
|---|---|
| F24两个真实stub竞争同一物理lock | 恰好一个LOCKED，一个CONFLICT；都退出后可重新取得 |
| F19/F22异常退出 | 退出码73/74，OS释放拥有锁；partial receipt保留并进入分类恢复 |
| T39继承handle | 父句柄关闭后子句柄继续持锁；父重取拒绝；子退出后可重新取得 |
| T41指定process handle与Event | PID/创建时点不符拒绝，正确Event使拥有stub正常退出 |
| T45/T46同上下文重复start/Store/连接替换 | 一次槽/生命周期拒绝保持 |
| T33路径/DACL | 实际hardlink与file-ID检查；reparse属性通过显式注入检查拒绝，未创建真实junction |
| F25复制 | 真实新加密测试DB复制后，旧根/DB file-ID无法直接复用 |

Win32独占文件handle保护遵守该入口的同物理实例。旧Controller SingleActive保持，Authority新core在构造Store前取得自己的lease。SQL写锁、PID或路径单独出现时无法替代实例所有权。

最终6个stub的process/pipe handle均显式关闭，强制终止0，窗口均隐藏，环境为构造的公开白名单，继承句柄仅T39明确指定的一份。

R16原44项及D1-A24项重新执行通过，原读总量门、并发、重放、issuer/别名保护保持。新LiveContext的受保护读/permit额均0。持久防回滚/防克隆、真实P2接纳和跨进程一次性启动批准均未取得完整证明。

F26和T45的完整跨进程条件在最终合同验收中BLOCKED；它们的同进程单元断言实际通过。具体源码轨迹见07稿，避免把进程内registry提升为持久批准账本。
''')
put('03_LIFECYCLE_AND_RESOURCE_OWNERSHIP.md','# 生命周期与资源所有权\n\n'+header+r'''
实现NEW→PREFLIGHTED→RESOURCES_RESERVED→INITIALIZING→SEED_READY→STORE_READY→HOST_DORMANT→LISTENER_READY→SERVICE_READY→STOPPING→STOPPED，以及FAILED/RECOVERY_REQUIRED。转移除次序外，还检查前置事实；phase为只读属性，CLI无法提交任意phase。

Scope把目录和文件操作限定到当前R21 run。新实例记录及有界JSONL阶段日志在测试目录持久保存，start_claim在Store构造前写入。该日志当前用于证据，重启入口尚未将它变成完整消费/重放判定，F23/F26/T45据此保留阻塞。

OwnedResources按获取次序登记强引用和creator scope，退出逆序关闭。Store connection在ctor返回前即登记，schema/metrics/marker/config失败均由内外层幂等关闭。connect_owned在row_factory/authorizer/trace配置失败时也会关闭已打开连接。strict bootstrap使用时再次核验lease，过期锁在SQL前拒绝。

默认与原业务方法保持：strict路径只接受新Schema2/version2，禁止genesis/migration。初始化正常15次SQL，strict ctor正常7次；两者作为函数和同一新DB的前后阶段分别实际验证。22为组合正常调用推导，完整生产boot尚未执行。

失败关闭先retire context，再关闭listener/connection/lock；一个closer抛错后继续其余closer，primary与cleanup错误分开。listener只有明确登记的替身，server_close替代未运行loop上的shutdown等待。持久DB/key/审计自动删除0。

正常stop可重复；close异常保留RECOVERY_REQUIRED并保持已消耗状态。超时、丢失ACK和partial marker只能恢复无权限记录。recover只读元数据和文件身份，SQL/key-load/decrypt/start/repair均0；key_DB_content_verified始终false，来源一致与密码学内容一致分别管理。

六操作在同一受控driver进程中实际执行并保存receipt。跨独立进程的initialize/start/status/stop需要拥有同一监督进程的控制接线，当前没有该实现；新进程无法自动反序列化旧opaque对象。该收缩保护了读取权限，也限制了当前CLI实用范围。
''')
fault_table='\n'.join('| '+x['id']+' | '+x['name']+' | PASS | '+x['contract_acceptance_status']+' | '+x['evidence_grade']+' |' for x in coverage)
put('04_FAILURE_CLEANUP_AND_RECOVERY_RESULTS.md','# 故障清理与恢复证据\n\n'+header+r'''
28个冻结故障ID全部实际调用，原定义与预期保存在D1B1_FAILURE_COVERAGE.json。runner返回28 PASS；最终完整合同验收为26 PASS、2 BLOCKED（F23/F26），原因是较强跨进程入口条件未闭合。此区分保持原始运行记录。

| ID | 冻结故障 | 原始执行 | 完整合同 | 证据等级 |
|---|---|---|---|---|
'''+fault_table+r'''

F08在真实新文件SQLite事务中注入提交前故障，验证DDL回滚和一次rollback。F09在实际COMMIT之后、外层receipt之前注入故障，验证version2和两事件仍存在，外层保留RECOVERY_REQUIRED。

F14在真实Store已取得连接、第一次metrics之前注入异常；连接被捕获并实际关闭。F15–F18分别在Host/Handler/listener/Ready边界注入，验证Store及拥有listener替身全部关闭、无shutdown等待、无端口回退。

F19/F22为真实拥有stub异常退出和kernel锁释放；F24为两个真实stub竞争。它们没有启动Authority网络服务。F13生成真实临时TLS材料，网络失败使用替身。T36另以实际SSLContext加载正确材料并拒绝错误证书，真实TLS握手0。

恢复成功的准确含义为：拥有对象退出/关闭可核对，partial状态被正确分类，旧读权限保持关闭。介质断电、真实Authority崩溃、生产WAL恢复及原生凭据处理均未测试。

源级后置条件：持久文件保留、foreign closer拒绝、临时对象仅本次拥有、旧context关闭、错误不自动重新开放读槽。F23/F26的跨进程部分继续阻塞，不能以表中单元PASS替代该义务。
''')
cost_table='\n'.join('| '+k+' | '+','.join(v['case_ids'])+' | '+str(v['inclusive_case_ns'])+' |' for k,v in costs.items())
put('05_TEST_RESULTS_AND_COST.md','# 测试结果与费用\n\n'+header+r'''
最终原始执行：TOTAL120、PASS120、FAIL0、ERROR0、SKIP0、BLOCKED0、NOT_RUN0；内部检查2366（新310＋原137＋原1919）。最终完整合同验收：TOTAL120、PASS117、FAIL0、ERROR0、SKIP0、BLOCKED3、NOT_RUN0。

F23/F26/T45的单元测试通过，但更强跨进程条件仍有源级缺口。D1B1_ACTUAL_RESULTS.json同时保留raw_execution_status与contract_acceptance_status。原始RESULTS/stdout保持，验收数没有通过改写测试制造。

| 最终suite | 执行PASS | 内部检查 | elapsed ns |
|---|---:|---:|---:|
| new52_002 | 52 | 310 | 11425682200 |
| r19_24_002 | 24 | 137 | 965285700 |
| legacy44_002 | 44 | 1919 | 1127940900 |

最终suite时段合计13,518,908,800ns。时段从main内clock开始至构造结果，解释器/顶层导入、尾部结果及索引写入未单独计入；数值代表该测量窗口。

实际命令模板：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite new52
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite r19_24
& 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite legacy44
```

每个模板实际执行两次，总6次，达到R20每suite一次重跑的上限。首轮也全部通过；随后知情代码复核补强句柄关闭、lease复核、连接配置异常清理、加载来源和拒绝断言，再执行最终三组。240为含重复的用例执行次数，最终独立分母保持120。未发生测试FAIL/ERROR或early failure。全部6轮保留。

R19兼容D24采用测试Path provider：原始逻辑R19路径与准入判断保留，物理读写映射到新R21 run。原runtime源/原断言保持。这是旧策略兼容性证据，无法证明R19生产读取器直接接受R21路径。

| 最终新52资源 | 实测 | 上限/范围 |
|---|---:|---|
| 文件SQLite连接 | 11 | 104；每case至多2 |
| execute尝试/返回/失败 | 75/73/2 | 失败为主动ATTACH拒绝及访问已关闭连接 |
| 显式rollback调用 | 1 | 初始化失败清理单列 |
| state测试key生成 | 2 | 2 |
| TLS测试材料生成/SSLContext加载 | 1/2 | 2/2 |
| 拥有stub创建/强制终止 | 6/0 | 8/仅拥有对象 |
| 新工作线程＋watchdog/观察峰值 | 12＋1/4 | 16/4 |
| 私有子目录/最终前记录目录 | 21/22 | 64 |
| 成功取得实例锁 | 47 | 父测试进程计数；child另有实际锁证据 |
| 峰值working set | 51,302,400B | 实际当前测试进程，含导入及harness |

R19域内存连接1，legacy域18；两组无services/storage/materials导入，legacy无crypto导入。新52允许导入服务定义和真实测试Store，运行服务进程0。

所有轮累计：stub12、文件SQLite22、R19内存2、legacy内存36、state key4、TLS材料2、SSLContext4，均在获批累计预算内。原始执行正常不等于完整契约全部通过。

成本覆盖代理见下表；分类重叠，无法求和替代整体时段。精细ledger只计选定调用，未隔离的生成/日志fsync/平台I/O按实际局限登记。

| 类别 | 覆盖case | inclusive case ns |
|---|---|---:|
'''+cost_table+r'''

实际物理分配峰值、VFS写放大、完整OS线程峰值及旧两域内存峰值NOT_MEASURED。输出树当前逻辑文件字节和清单在D1B1_RESOURCE_LEDGER.json。真实D1-B2性能全部NOT_MEASURED。
''')
put('06_CODE_DIFF_AND_INTEGRITY.md','# 差异与历史完整性\n\n'+header+r'''
R20原保护组1133文件中，3个本轮获准修改文件单列，1130文件保持；另25个R20及补充来源文件保持。共1158个唯一来源，1155保持，3个获准修改。已有SOURCE_LOCK、原测试、fixture、失败记录、R18参数确认均保留原字节。

services/storage/launcher的原字节在sources/original，原SHA与新SHA在CODE_DIFF.json；新5个Python文件、fixture4文件和实际入口在D1B1_FILE_LOCK.json。文本差异在sources/CODE.diff。

AST检查确认storage的原业务方法及SingleActive/Controller/FakeProvider类保持。原默认服务路径保持；新接纳在配置I/O前拒绝真实运行。旧migration、protocol/materials、R16/H1/B1/S3-A/S1/S2等文件保持。

三份最终RESULTS的8文件SHA列表相同并与当前代码一致。首轮版本另存FILE_LOCK_RUN1及各run/code_snapshot；代码审查补强来源在CODE_REVIEW_REFINEMENTS.json。此前所有测试均通过，修订并非清除失败记录。

秘密扫描覆盖报告、公开JSON、日志、源码快照及diff；测试key/DB留在受限测试资源位置，公开材料不含其原值，key hash也省略。哈希仅固定版本，外部独立验证待取得。

完整复查见sources/DELIVERY_QA.json。运行期实际file/SQLite/进程/native事件与代码检查证据共同使用；审计hook无法独立观测所有原生库内部I/O，来源和文件边界另由受控provider约束。
''')
put('07_FINAL_VERDICT_AND_NEXT_STEP.md','# 最终裁决与唯一下一步\n\n'+header+r'''
**裁决：D1B1_PARTIAL_IMPLEMENTATION。** 九目标离线核心已落地，原始120项全部通过；跨进程入口和一次性启动接纳仍有具体缺口，完整合同验收为117 PASS＋3 BLOCKED。

## 源级缺口与证明范围

1. 六操作调用当前依赖同一进程的`_CLI_LOOPS`。新的CLI进程无法继续原initialize/start/stop上下文；status/recover语义也需要区分记录与拥有进程。当前只完成同进程受控driver接线。
2. `authorize_test_scope`认证本轮测试作业，`LiveDeploymentIssuer`只发行测试上下文。它们没有发行绑定一次实际部署动作的研究者批准。`_LIFECYCLE_NAMESPACES`是进程内登记；已有JSONL start_claim尚未被重新接纳流程作为持久消费依据。
3. 真实D1-B2 issuer、拥有supervisor与有界原生网络adapter尚未实现可执行闭环。现有services旧native路径仍受OFFLINE_ONLY阻断，新增listener工厂为明确标记的离线适配器。

可逐步核对的纸面轨迹（未运行额外进程）：当前driver用授权标识A完成prepare/start并写start_claim；进程退出后其registry消失；若未来另一个入口对同一run/root/A重新调用测试factory，现有prepare会读instance.json，随后仅依赖新进程namespace建立context，尚未读取并消费A的历史journal。此轨迹指出未来入口放宽前必须补齐的检查。R21实际执行命令受冻结runner限制，本轮未额外运行该轨迹，也未证明实际P2绕过；当前所有context的P2仍固定拒绝。

因此F23的完整旧marker启动接纳、F26的跨进程授权重放、T45的跨进程启动批准消耗列为BLOCKED。已实际通过的分类/同进程断言保留PASS；完整合同从它们无法推出。

## 状态

| 状态 | 登记 |
|---|---|
| D1B1_PARTIAL_IMPLEMENTATION | TRUE，完整生产/独立进程闭环未完成 |
| D1B1_SINGLE_ACTIVE_VERIFIED | 限真实自有Windows临时对象/stub与离线core |
| D1B1_INSTANCE_IDENTITY_VERIFIED_OFFLINE | 限测试宿主、根file-ID、opaque上下文与同Store |
| D1B1_LIFECYCLE_VERIFIED_OFFLINE | 限同进程模型、真实临时SQL函数与分类恢复 |
| D1B1_SESSION_GATE_REGRESSION_PASSED | 原44＋D1-A24实际重跑；新P2额0 |
| D1B1_SYNTHETIC_TESTS_PASSED | 原始runner120 PASS；完整契约117/3分别记录 |
| D1B1_FAILURE_CLEANUP_VERIFIED | 未登记完整通过；28执行、26完整接纳、2阻塞 |
| D1B1_CRASH_RECOVERY_VERIFIED | 未登记完整通过；已取得拥有stub退出/锁释放/元数据分类证据 |
| D1B2_AUTHORIZATION_PENDING / REAL_DEPLOYMENT_NOT_RUN | TRUE；还缺代码与环境准入 |
| P1A/P1B/P2/S3B2/S5_NOT_AUTHORIZED | 保持 |
| SOURCE_OR_REFINEMENT_GAP | 保持；typed O、o、native/global COMPLETE沿用原缺口 |

## Q1–Q14

| 问题 | 回答 |
|---|---|
| Q1 九目标全部实现？ | 九个文件/子树和离线core已实现；完整独立进程启动接纳仍缺，整体部分实现。 |
| Q2 单活并发/异常退出？ | 实际两个stub竞争、异常退出和handle交接通过；限定临时Windows对象。 |
| Q3 身份/OS/Store/epoch？ | 当前测试宿主真实SID/PID/创建时点/file-ID和同Store/连接/锁检查通过；未来部署身份未批准。 |
| Q4 R16一次门？ | 原44项和D1-A24重跑通过，新context P2固定拒绝；持久跨进程启动批准未闭合。 |
| Q5 初始化/所有权？ | 新文件SQLite15SQL、strict Store7SQL、连接前后异常关闭、LIFO与保留实际验证；完整生产boot未运行。 |
| Q6 SQL/key/TLS隔离？ | 文件连接11，仅新输出树；state key2/TLS材料1/SSLContext2；真实网络0。 |
| Q7 Store至listener已知异常？ | 当前离线core和strict ctor已知异常有关闭路径；真实原生有界网络分支仍缺。 |
| Q8 28故障？ | 28实际执行并返回PASS；完整跨进程义务F23/F26阻塞，完整接纳26。 |
| Q9 stop/recover/retry？ | 同进程stop幂等、失败消耗保持、recover元数据0读通过；独立进程监督接线/批准消费待补。 |
| Q10 120统计？ | 原始执行120 PASS；完整验收117 PASS、3 BLOCKED，其他0。均在结构化结果中分层。 |
| Q11 资源和费用？ | 实际六次调用在获批预算内；全部轮保留。最终suite窗口13.519s，新域峰值51,302,400B；完整物理I/O等未测。 |
| Q12 历史完整性？ | 原1133组1130保持、3单列获准；加25来源共1158，其他1155保持，原快照和实际diff齐备。 |
| Q13 真实访问均0？ | 已部署服务/生产DB/真实用户key/RPC/native为0；临时SQL/key及测试Store另有明确实测计数。 |
| Q14 B2还缺？ | 先闭合独立进程接纳、持久启动批准与拥有supervisor/原生adapter，再固定SID/source/config/DB-key-TLS/argv并单独批准；当前未具可执行B2命令。 |

## 唯一下一步

**完成独立进程部署接纳与一次性启动批准的最小补充闭环。** 保持九目标范围，先给出一次具体补丁/测试追加申请：分开prepare/initialize的持久资源与start的拥有supervisor；启动前校验完整批准tuple及持久消费/不确定态；旧marker/旧epoch/旧授权进入拒绝或RECOVERY_REQUIRED；stop只信号精确拥有进程，P2继续0。实际原生网络适配仍需用替身先核对所有权。

具体申请见SUPPLEMENTAL_AUTHORIZATION_REQUEST.json：仅修改原九目标中的5个Python文件并在原fixture子树追加输入；在新R22输出树执行54＋24＋44＝122项，新增X01/X02独立进程见证，限3次直接suite调用、额外自动重跑0。其余临时资源上限明确列入申请，真实部署/网络/P1/P2继续0。它针对上述三个阻塞，独立shell的完整supervisor/native适配仍须分开审定。

成功应使F23/F26/T45完整条件取得可重复的独立进程证据，并形成真正可审定的B2代码/argv。失败则保留具体反例与部分实现状态。当前R20每suite一次重跑额度已使用，额外项目测试需新增明确批准。

这项补充需求来自实际源码及覆盖复核。R20 TEST_PLAN把每suite修复重跑限定为一次；R21要求遵守更严格预算。本轮保留最终已测代码，未将预算外执行或未验证改动登记为完成。

A/B/AB独立创新评价和严格分离门保持。成熟接线和单元通过不产生通用方法必要代价分离。COL2026暂停、FS23延期状态沿用。
''')
statuses=['D1B1_PARTIAL_IMPLEMENTATION','D1B1_SINGLE_ACTIVE_VERIFIED','D1B1_INSTANCE_IDENTITY_VERIFIED_OFFLINE',
    'D1B1_LIFECYCLE_VERIFIED_OFFLINE','D1B1_SESSION_GATE_REGRESSION_PASSED','D1B1_SYNTHETIC_TESTS_PASSED',
    'D1B2_AUTHORIZATION_PENDING','REAL_DEPLOYMENT_NOT_RUN','P1A_NOT_AUTHORIZED','P1B_NOT_AUTHORIZED',
    'P2_NOT_AUTHORIZED','S3B2_NOT_AUTHORIZED','S5_NOT_AUTHORIZED','SOURCE_OR_REFINEMENT_GAP']
put('FINAL_STATUS.json',{'schema':'r21-final-status/1','overall':'D1B1_PARTIAL_IMPLEMENTATION','statuses':statuses,
    'raw_execution_counts':raw_counts,'full_contract_counts':acceptance,'blocked_obligations':blocked,
    'final_checks':2366,'full_production_or_cross_process_qualification':False,'real_deployment':False,'additional_tests_authorized_now':0})
put('SOURCE_LOCK.json',{'schema':'r21-source-lock/1','request':pre['request'],'approval_receipt_sha256':sha(OUT/'APPROVAL_RECEIPT.json'),
    'file_lock_sha256':sha(OUT/'D1B1_FILE_LOCK.json'),'supplemental_request':{'path':str(OUT/'SUPPLEMENTAL_AUTHORIZATION_REQUEST.json'),'sha256':sha(OUT/'SUPPLEMENTAL_AUTHORIZATION_REQUEST.json')},
    'R20_source_lock':{'path':str(R20/'SOURCE_LOCK.json'),'sha256':sha(R20/'SOURCE_LOCK.json')},'precheck':'sources/PRECHECK_LOCK.json','protected_unique':1158,
    'allowed_modified':changed,'executed_code':lock['executed_code'],'inputs':lock['inputs'],
    'final_results':[{'path':str(RUNS/(r['suite']+'_002')/'RESULTS.json'),'sha256':sha(RUNS/(r['suite']+'_002')/'RESULTS.json')} for r in final],
    'all_test_runs':history['runs'],'process_evidence':'D1B1_RESOURCE_LEDGER.json','test_path_projection':'R19 compatibilityD24 logical policy retained,physicalR21 namespace; test-only provider',
    'acceptance_audit':'117 accepted/3 blocked distinct from raw120 PASS','process':'informed model-assisted implementation/execution/audit; external verification pending',
    'real_deployment_P1_P2':False,'self_hash_policy':'final DELIVERY_QA manifest includes this file, excludes QA itself'})
print(json.dumps({'reports':7,'raw_PASS':120,'contract_PASS':117,'contract_BLOCKED':3,'fault_executed':28,'project_tests_in_this_assembly':0}))
