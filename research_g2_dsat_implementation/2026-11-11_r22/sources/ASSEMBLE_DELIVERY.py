"""R22 read-only evidence assembly and reporting. No application imports/tests."""
import ast
import datetime
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(r'D:\毕业设计');BASE=ROOT/'research_g2_dsat_implementation';OUT=BASE/'2026-11-11_r22'
R21=BASE/'2026-11-11_r21';RUNTIME=BASE/'2026-11-11_r22_d1b1_closure_offline';PROJECT=ROOT/'auth-lifecycle'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,d):
    (OUT/n).write_text(d.strip()+'\n' if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lock=load(OUT/'R22_FILE_LOCK.json');pre=load(OUT/'sources/PRECHECK_LOCK.json');scope=load(OUT/'R22_SCOPE_LOCK.json')
history=load(RUNTIME/'TEST_RUNS.json')
all_runs=[load(x['path']) for x in history['runs']]
latest={}
for r in all_runs:latest[r['suite']]=r
selected=[latest[s] for s in ['new54','r19_24','legacy44'] if s in latest]
counts={s:sum(r['counts'][s] for r in selected) for s in ['PASS','FAIL','ERROR','SKIP','BLOCKED','NOT_RUN']}
new=latest['new54'];newroot=Path(new['run']);first=load(RUNTIME/'new54_001/RESULTS.json')
same_code=all(r['code']==lock['executed_code'] for r in selected)
raw_complete=len(selected)==3 and counts=={'PASS':122,'FAIL':0,'ERROR':0,'SKIP':0,'BLOCKED':0,'NOT_RUN':0}
complete=raw_complete and same_code and all(r['passed'] for r in selected)
receipt=load(OUT/'ADDITIONAL_APPROVAL_RECEIPT.json') if (OUT/'ADDITIONAL_APPROVAL_RECEIPT.json').exists() else None
additional_approved=receipt is not None and receipt.get('approved') is True
used=len(list(RUNTIME.glob('SUITE_INVOCATION_*.json')))

# Every historical result remains byte-fixed, including the first54 error.
put('R22_TEST_RUNS.json',{'schema':'r22-all-runs/1','runs':history['runs'],'direct_suite_invocations':used,
    'original_budget':3,'approved_budget':4 if additional_approved else 3,'automatic_reruns':0,
    'additional_approval':str(OUT/'ADDITIONAL_APPROVAL_RECEIPT.json') if additional_approved else None,
    'wrapper_failure':str(OUT/'sources/COMMAND_WRAPPER_FAILURE_001.json'),'wrapper_failure_started_Python':False,
    'first54_counts':first['counts'],'first54_error_id':'F24','history_deleted':False})
case_rows=[{**c,'suite':r['suite'],'executed_version_code':r['code']} for r in selected for c in r['cases']]
put('R22_ACTUAL_RESULTS.json',{'schema':'r22-combined-results/1','TOTAL':122,'counts':counts,'selected_cases':case_rows,
    'selected_results':[{'path':str(Path(r['run'])/'RESULTS.json'),'sha256':sha(Path(r['run'])/'RESULTS.json')} for r in selected],
    'same_final_code_version':same_code,'all122_contract_accepted':complete,
    'critical_original_blockers':{i:{'latest54_status':next(c['status'] for c in new['cases'] if c['id']==i),
        'independent_process_evidence':True,'full_current_version_qualification':complete} for i in ['F23','F26','T45']},
    'first_failure_preserved':True,'additional_run_pending':not complete and not additional_approved,
    'R21_historical_120_added_to_current_counts':False})

first_witness=load(newroot/'CROSS_FIRST_WITNESS.json');replay=load(newroot/'CROSS_REPLAY_WITNESS.json')
consumptions=[];invalid=[]
for path in sorted(newroot.rglob('start_consumption_*.jsonl')):
    raw=path.read_bytes();rows=[]
    try:
        assert raw.endswith(b'\n') and 0<len(raw)<=16384
        previous=None
        for i,line in enumerate(raw.splitlines()):
            value=json.loads(line);p=value['payload']
            assert p['seq']==i and value['digest']==hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
            if previous is not None:assert p['previous']==previous
            previous=value['digest'];rows.append(p)
        consumptions.append({'path':str(path),'sha256':sha(path),'states':[x['state'] for x in rows],
            'latest':rows[-1],'P2':False})
    except Exception:invalid.append({'path':str(path),'classification':'RECOVERY_REQUIRED'})
effects=[p for p in newroot.rglob('start_effect_*.json')]
witness={'schema':'r22-cross-process-witnesses/1','evidence_code':new['code'],
    'first_actor':first_witness,'second_actor':replay,'actors_distinct':first_witness['actor']['pid']!=replay['actor']['pid'],
    'first_actor_exited_before_second_admission':replay['first_owner_exit_record']['exit_recorded'],
    'owned_processes':new['owned_children'],
    'F23':{'source':'X01 actual independent actor','rejected':first_witness['probes']},
    'F26':{'source':'X02 actual second actor plus F24 durable concurrent actors','replays':replay['replays'],'aliases':replay['aliases']},
    'T45':{'successful':first_witness['first_start'],'claimed_before_crash':replay['claimed_failure'],
        'startup_ACK_deliberately_withheld':not first_witness['start_ACK_observed_by_client']},
    'worker_stdout_stderr_complete':all(Path(c['result']['stdout_path']).is_file() and Path(c['result']['stderr_path']).is_file() for c in new['owned_children'])}
put('R22_CROSS_PROCESS_WITNESSES.json',witness)
put('R22_AUTHORIZATION_CONSUMPTION_AUDIT.json',{'schema':'r22-consumption-audit/1','fault_model':
    'single local Windows/NTFS host, trusted researcher/SYSTEM/runtime, intact private ACL and file identities; process crashes and interrupted writes; OS power-loss/volume rollback/malicious same-SID excluded',
    'atomic_boundary':'actual exclusive instance-file handle across validation/read/append/fsync; all mutating admission paths use it',
    'authoritative_states':['UNCLAIMED','CLAIMED','STARTED','FINISHED','UNCERTAIN'],
    'authority':'synthetic one-action startup approval from explicitly authorized R22 test bootstrap, separate from job admission; no real deployment approval issued',
    'bindings':['authorization_id','approved_action','environment_id','run_id','root physical identity','instance_id','source/config digests','OS SID','Python image/hash/version','assigned epoch','singleton scope','budget1','original receipt digest'],
    'invariants':[
        'UNCLAIMED can only transition to CLAIMED under the held native lease',
        'claim append is flushed and fsynced before Store/Host/listener allocation',
        'no transition returns to UNCLAIMED; valid spent or damaged/ambiguous state cannot re-admit',
        'effect receipt uses exclusive create per grant; consumed and successfully started are distinct',
        'display/issuer/client aliases do not select a different authoritative consumption key',
        'Status observes history and verified owner separately; Stop uses creator registry plus exact PID/creation/SID/epoch/event',
        'record hashes detect accidental corruption; authenticity depends on trusted private storage, not on unkeyed hashes alone'],
    'raw_consumption_files':consumptions,'invalid_current_records':invalid,'effect_files':len(effects),
    'negative_corruption_probes':replay['corruption'],'actual_world_SQL_or_key_loads_in_recovery':0,
    'current_complete_suite_qualified':complete,'real_P2':0,'real_deployment':False})

catalog=[]
for p in sorted(p for p in RUNTIME.rglob('*') if p.is_file()):
    catalog.append({'path':str(p),'bytes':p.stat().st_size,'sha256':None if p.suffix in {'.key','.pem','.pfx'} else sha(p),
                    'private_test_key':p.suffix in {'.key','.pem','.pfx'}})
totals={'file_SQLite_connections':sum(r['audit']['file_SQLite_connections'] for r in all_runs),
    'memory_connections':sum(r['audit']['memory_SQLite_connections'] for r in all_runs),
    'test_state_keys':sum(r['scope_counts'].get('test_state_keys_generated',0) for r in all_runs),
    'test_TLS_materials':sum(r['scope_counts'].get('test_TLS_material_generated',0) for r in all_runs),
    'test_SSLContext_loads':sum(r['scope_counts'].get('test_SSLContext_loads',0) for r in all_runs),
    'own_child_launches':sum(r['audit']['child_launch_attempts'] for r in all_runs),
    'own_child_forced_terminations':sum(c['result']['terminated_owned_stub'] for r in all_runs for c in r['owned_children']),
    'actual_runtime_violations':sum(len(r['audit']['unexpected_violations']) for r in all_runs),
    'actual_socket_attempts':sum(r['audit']['socket_attempts'] for r in all_runs)}
put('R22_RESOURCE_LEDGER.json',{'schema':'r22-resources/1','direct_suite_invocations':used,'aggregate_actual':totals,
    'selected_suites':[{'suite':r['suite'],'audit':r['audit'],'scope_counts':r['scope_counts'],'elapsed_ns':r['elapsed_ns'],'memory':r['memory'],
        'files_before_result':r['files_before_result_output'],'directories_before_result':r['directories_before_result_output']} for r in selected],
    'logical_current_output_bytes':sum(x['bytes'] for x in catalog),'catalog':catalog,
    'first_failure_child_observation_window':next(c['result']['elapsed_seconds'] for c in first['owned_children'] if c['facts']['pid']==97484) if any(c['facts']['pid']==97484 for c in first['owned_children']) else None,
    'first_failure_window_limit':'deferred loser cleanup recorded17.953s parent observation window; loser had exited; kernel lifetime not separately recorded, no claim that parent window is actual process lifespan',
    'wrapper_failed_outside_write_attempts':1,'wrapper_actual_outside_write':0,
    'runtime_outside_writes':sum(r['audit']['outside_writes'] for r in all_runs),
    'additional_budget_approved':additional_approved,'additional_budget_request':'ADDITIONAL_RUN_REQUEST.json',
    'physical_disk_peak_OS_thread_peak_VFS_IO':'NOT_MEASURED','real_D1B2_cost':'NOT_MEASURED'})

changes=[];diff=[];locations=[]
allowed={x['path'] for x in pre['allowed_modifications']}
for x in pre['allowed_modifications']:
    p=Path(x['path']);original=OUT/'sources/original'/(p.name+'.txt')
    before=original.read_text(encoding='utf-8');after=p.read_text(encoding='utf-8')
    assert sha(original)==x['before_sha256']
    changes.append({'path':str(p),'old_sha256':sha(original),'new_sha256':sha(p),'original':str(original)})
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='R21/'+p.name,tofile='R22/'+p.name))
    tree=ast.parse(after);entries=[]
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)):
            entries.append({'name':n.name,'line':n.lineno})
            if isinstance(n,ast.ClassDef):entries.extend({'name':n.name+'.'+q.name,'line':q.lineno} for q in n.body if isinstance(q,ast.FunctionDef))
    locations.append({'path':str(p),'sha256':sha(p),'symbols':entries})
put('sources/CODE.diff',''.join(diff));put('sources/SOURCE_LOCATIONS.json',locations)
unapproved=[x['path'] for x in pre['protected'] if x['path'] not in allowed and sha(x['path'])!=x['sha256']]
assert not unapproved
put('R22_CODE_DIFF.json',{'schema':'r22-code-diff/1','modified_files':changes,'modified_count':5,'fixture_append':str(PROJECT/'tests/fixtures/dsat_authority_live_lifecycle/R22_SUPPLEMENTAL_CASES.json'),
    'fixture_inputs':lock['inputs'],'protected_count':len(pre['protected']),'unchanged_except5':len(pre['protected'])-5,'unapproved_changes':unapproved,
    'services_storage_launcher_unchanged':True,'old_history_locks_logs_unchanged':True,'diff':'sources/CODE.diff'})

head='执行日期按原始UTC记录及本地时间核对；目录名沿用研究者冻结的2026-11-11。过程：本对话内知情模型辅助工程实现、真实离线运行及源码复核；外部核验待取得。\n\n'
overall='D1B1_OFFLINE_CONTRACT_COMPLETE' if complete else 'D1B1_PARTIAL_IMPLEMENTATION'
result_text='122 PASS，FAIL/ERROR/SKIP/BLOCKED/NOT_RUN均0' if complete else f"{counts['PASS']} PASS、{counts['ERROR']} ERROR（原始记录保留，修复后的54项尚未完整验收）"
put('01_IMPLEMENTATION_SUMMARY.md','# G2-R22补充实现摘要\n\n'+head+f'当前裁决：**{overall}**。当前选定122项执行结果：**{result_text}**。\n\n'+r'''
严格修改原五个Python文件：live、lifecycle、Windows provider、新test、新runner；在原fixture子树追加R22_SUPPLEMENTAL_CASES.json。services.py、storage.py、launcher及其他源码保持。六目标锁见R22_SCOPE_LOCK.json。

资源准备/初始化与运行所有权分开。独立进程从持久instance、seed descriptor、marker和单动作批准重新接纳；启动前在实际OS独占锁内校验并持久消费。消费、启动成功、资源停止和拥有进程退出分别表示。

真实独立进程见证覆盖旧marker/epoch、已消费重放、崩溃后CLAIMED、别名、截断/缺失/损坏记录。F24强化为两真实进程争用同一动作批准，T41验证跨进程有界Status/Stop，P2总额0。

首轮54项53 PASS、F24一项ERROR：败者已退出，stdin.close刷新时报OSError22。已有最小修复，只在精确拥有子进程已退出时接纳该关闭结果。完整失败及修复前快照保留。

D1-A24和A1/H1 44已实际重跑通过。额外重跑以ADDITIONAL_RUN_REQUEST和实际独立批准为准；未得到批准时三次上限保持。任何已完成追加运行均在R22_TEST_RUNS列出。

所有执行均为本轮新临时对象和测试子进程。真实Authority服务、正式部署根、网络监听/RPC、生产DB/key、P1/P2/S3-B2/S5均未开放。
''')
put('02_CROSS_PROCESS_ADMISSION.md','# 跨进程启动接纳\n\n'+head+r'''
持久instance绑定environment/run、根volume/file-ID、instance ID、source/config摘要、singleton scope；seed descriptor单列真实新测试SQLite或模拟持久种子类型。没有可信descriptor的既有DB和缺失/矛盾marker进入恢复。

Prepare取得实例lease后创建/校验持久资源和独立合成启动批准。Initialize只建立/校验seed descriptor并标为SEED_READY。Start的新进程重新读全部元组，不反序列化旧Python对象。`_CLI_LOOPS`只保存当前进程拥有的运行引用，持久事实另行读取。

真实离线supervisor入口是固定的拥有worker协议：取得同实例锁、核验动作批准、持久claim、构造合成Store/Host/Handler/listener、发布STARTED，关闭资源后发布FINISHED，锁最后释放。worker可持有受信Event，另一个受控进程精确请求停止。普通shell没有获得后台服务启动资格；真实native服务和生产issuer仍闭合待审。

X01在父进程完成prepare/initialize后，由独立P1真正接纳A；A成功并停止后，P1对K先claim再以退出码73异常退出。X02由另一个P2在P1退出已被创建者记录之后重读相同文件，拒绝A/K及四类显示别名。PID、创建FILETIME、SID、image、退出码、原始stdout/stderr和文件摘要均保留。

F23读取X01独立进程拒绝stale marker、wrong config/origin、unowned resources、truncation、old epoch等结果。F26读取X02持久重放及别名结果。T45分辨A的consumed+started与K的consumed+未started。

Status将历史phase、消费状态与实际owner liveness分开；活体结论使用本轮创建登记和精确PID/创建时点/SID/image句柄。Stop只信号相符epoch的受控Event，创建时点或epoch不符即拒绝。进程退出后使用创建者EXITED记录表达已确认退出，单独旧marker无法宣布运行。

Recover为只读分类，SQL、key-load、world-decrypt、自动start和旧批准重开均0。真实key/DB内容一致性、native currentness、typed O/o和global COMPLETE保持原缺口。
''')
put('03_DURABLE_START_AUTHORIZATION.md','# 持久一次性动作批准\n\n'+head+r'''
测试作业Scope只证明进入本轮受控环境；Start另需`r22-one-shot-start/1`动作批准。其字段绑定authorization_id、START_OFFLINE_SUPERVISOR、environment/run/root/instance、source/config、SID、Python路径/hash/version、assigned epoch、scope、预算1及原批准记录digest。它来自研究者已批准的合成测试bootstrap，无法转化为真实部署许可。

权威消费文件按authorization ID规范索引。初始UNCLAIMED只发布一次；grant已存在而slot缺失时进入RECOVERY_REQUIRED。显示issuer/source/client别名与display不改变权威索引。

允许状态边为UNCLAIMED→CLAIMED→STARTED→FINISHED，以及CLAIMED/STARTED→UNCERTAIN。没有回到UNCLAIMED的边。每行包含seq、grant digest、epoch、owner、previous digest、effect count；严格UTF8/JSON、行结尾、大小、顺序和链完整性均核验。

原子边界为同物理实例的Win32独占文件handle，覆盖读取、校验、append、flush/fsync和效果前置判断。所有消费入口持有该lease；readonly Status可观察历史但不能消费。CLAIMED记录刷新并回读成功后才分配Store/Host/listener。effect receipt按批准唯一文件独占创建，效果至多1。

在诚实受控写者模型下，两个进程在同实例锁上串行；首个在UNCLAIMED状态成功claim，后续只见spent或不确定状态，均无法第二次建立效果。已写但ACK丢失仍保留CLAIMED/STARTED。append截断、missing slot、broken chain或unknown marker使接纳关闭，后续恢复无法免费发放机会。

边界前提：单机Windows/NTFS、可信研究者/SYSTEM/运行时、私有DACL及完整文件身份、正常OS下的进程崩溃。哈希链检查意外损坏，真实性依赖可信存储；恶意同SID、管理员篡改、卷回滚、介质故障和断电持久性尚未验证。

完整形式审计和实际slot状态在R22_AUTHORIZATION_CONSUMPTION_AUDIT.json。此次结论为限定模型内的离线工程保证，未推出分布式一致性或新算法优势。
''')
put('04_FAILURE_AND_RECOVERY_RESULTS.md','# 失败、恢复与见证结果\n\n'+head+r'''
R21的三项阻塞分别由实际独立进程数据补证。X01/X02的原始文件及拥有进程信息见R22_CROSS_PROCESS_WITNESSES.json，完整authoritative journal保留于当前new54 run。

- 首次有效A由P1产生一个效果，关闭后FINISHED。
- P1对K先持久CLAIMED，随后真实异常退出；K的效果0，新的P2仍拒绝重放。
- P2对同A改变issuer/source/client/display均REPLAY。
- 缺slot、truncated slot、invalid previous chain，以及prepare/initialize入口读取损坏状态均RECOVERY_REQUIRED。
- F24实际两个进程竞争同A，仅一个接纳；其败者退出时暴露stdio关闭错误，已保留ERROR。
- T41实际owner Event停止，错误PID创建时点/旧epoch安全拒绝，退出后Status使用创建者退出记录。

首轮F24 OSError22来自拥有竞争败者已退出后的BufferedWriter.close。最小修复要求`process.poll() is not None`才接纳BrokenPipe/OSError，存活peer异常继续RECOVERY_REQUIRED。修复未改动授权消费算法。是否已补跑以R22_TEST_RUNS和最终源版本哈希为准。

首轮败者的亲本回收观察窗口约17.953s，因错误推迟到suite末尾回收；它已经退出。该值无法作为内核实际存活时长，内核寿命当轮未独立记录。保留此计量缺项，额外run有记录时独立报告。

还有一次PowerShell stderr路径误写，shell在Python启动前报错。该路径未创建、suite没有启动，实际suite槽位仍为两次。包装错误及一次越界写尝试在COMMAND_WRAPPER_FAILURE_001登记；实际越界写为0。它不计作已运行suite，也未被删除。

实际Authority崩溃、真实TLS握手、生产WAL/AS凭据状态和断电试验均未执行。
''')
rows='\n'.join(f"| {r['suite']} / {Path(r['run']).name} | {r['counts']['PASS']} | {r['counts']['ERROR']} | {r['elapsed_ns']} |" for r in selected)
put('05_TEST_RESULTS_AND_COST.md','# 测试与费用\n\n'+head+f'当前选定结果：{result_text}。总计划122；原始记录及历史轮次保持。\n\n'+r'''
| suite/run | PASS | ERROR | main窗口ns |
|---|---:|---:|---:|
'''+rows+r'''

每次实际main启动先独占登记SUITE_INVOCATION槽，包括预检失败。原上限3；只有独立批准文件与请求/研究者回复摘要匹配时，才允许第4次且仅new54。自动重跑始终0。

同一54项中的8个拥有worker单列记录，不伪装为额外suite。X01/X02是新实际执行数据，原R21通过数未计入本轮。

单次new54上限：子进程8/并发2、单个10s/总窗口60s、文件SQLite104/每case2、state测试key2、TLS材料2、SSLContext2、目录64、文件路径512、输出64MiB、线程峰值4/创建16。追加run的累计扩展必须另批。

首轮new54实测：文件SQLite12、state key2、TLS材料1、SSLContext2、worker8、私有目录56、run内目录57、结果前文件368、源码计量观察窗口32.586s、新域峰值working set55,070,720B。stdout和stderr均有完整路径。SQL execute90次（返回88、预期失败2），显式rollback1；VFS内部次数未测。

SQL新增15次来自F14改为合法新库初始化后注入metrics故障；其2连接仍在case上限内。旧24内存1、旧44内存18，分别≤8/32。真实服务/生产DB/key/RPC/P2为0。

修复前后源码、计量和子进程结果分别记录。main计时从入口至构造RESULTS，解释器启动、部分顶层导入和结果尾部落盘未隔离；物理磁盘峰值、OS线程峰值、VFS写放大及D1-B2费用均NOT_MEASURED。

完整调用、资源和逻辑文件字节见R22_RESOURCE_LEDGER.json。旧D24保持原策略，通过测试Path provider把物理I/O映射到本轮输出，原runtime/旧断言保持原字节。
''')
put('06_CODE_DIFF_AND_INTEGRITY.md','# 五文件差异与历史完整性\n\n'+head+f"本轮保护清单{len(pre['protected'])}个唯一文件，其中5个获准修改单列，其余{len(pre['protected'])-5}个保持。\n\n"+r'''
允许修改的五文件原字节在sources/original；old/new SHA和实际diff见R22_CODE_DIFF.json、sources/CODE.diff。原fixture四文件保持，仅追加R22_SUPPLEMENTAL_CASES.json。services/storage/launcher和旧回归测试/runner、R20/R21资料及SOURCE_LOCK保持。

首轮54的8份源码快照保留；PIPE_CLOSE_FIX.diff单列实际修复。后续run以其各自RESULTS.code绑定真实版本，不能把旧版本见证直接改名为当前版本全量验收。

源码定位在sources/SOURCE_LOCATIONS.json。R22_FILE_LOCK当前源码须与最终所选结果逐一比较；是否完全一致在R22_ACTUAL_RESULTS.same_final_code_version表达。

秘密扫描覆盖公开报告、JSON、日志、code_snapshot和diff；专用test key和DB是受限测试资源。值不进入公开证据，key hash省略。历史失败和包装错误均保留。

哈希固定版本，不提供数学独立性。当前实现和复核均为知情模型辅助过程，外部独立审查待取得。
''')
put('07_FINAL_VERDICT_AND_NEXT_STEP.md','# 最终裁决与下一步\n\n'+head+f'当前状态：**{overall}**。当前结果：**{result_text}**。\n\n'+r'''
R22已实现持久跨进程实例接纳与单动作消费。F23/F26/T45的实际见证已有；最终是否登记当前版本全部PASS，仍以全部122项及同版本检查为依据。首轮F24 ERROR未被业务拒绝或历史通过覆盖。

| 问题 | 回答 |
|---|---|
| Q1 六目标？ | 五个Python文件受控修改、原fixture子树追加，代码已落地，最终验收按当前结果。 |
| Q2 仅批准文件？ | 是；services/storage/launcher及旧测试、历史资料保持，差异逐项固定。 |
| Q3 prepare/init跨进程start？ | 父进程持久准备后独立P1重新校验、消费并启动offline supervisor，实际见证已保存。 |
| Q4 marker身份？ | environment/run/root物理身份/instance/source/config/SID/runtime/epoch/phase及记录完整性核对，异常保守拒绝。 |
| Q5 相同授权第二进程？ | P1退出后P2重读A/K均REPLAY，原消费与效果保留。 |
| Q6 并发唯一？ | F24两真实进程仅一个消费/效果；清理错误独立记录，完整通过仍须对应最终run。 |
| Q7 issuer/别名/旧epoch？ | 四类显示别名不改变消费索引，旧epoch拒绝，当前句柄/原文件身份核验保持。 |
| Q8 失败/ACK丢失？ | CLAIMED已支付与STARTED成功分开；真实claim后退出和刻意不发送start ACK不重开。 |
| Q9 Status/Stop/Recover？ | 历史/活体/创建者退出分开，Stop验证精确owner+epoch+Event，Recover只分类且无SQL/key/自动start。 |
| Q10 三阻塞？ | 首轮三项及X01/X02已通过实际跨进程断言；当前版本全量资格以追加验收状态和哈希核对为准。 |
| Q11 122统计？ | 见本稿开头及R22_ACTUAL_RESULTS，首轮ERROR完整保留。 |
| Q12 三次预算？ | 原授权3次按独占槽严格执行；第4次仅在独立明确追加批准后允许，自动重跑0。 |
| Q13 历史/真实访问？ | 历史保持；运行audit实际越界/网络/真实业务访问0，shell包装另有一次未落地越界路径尝试。 |
| Q14 B2还缺？ | 生产live issuer、原生有界网络adapter与真实shell后台宿主、指定部署SID/ACL、冻结source/config/DB-key-TLS、精确start/stop命令及独立执行批准。 |

本轮限定模型为可信单机正常OS/NTFS下进程故障和受控actor；未验证断电、恶意同SID、卷回滚、完整原生服务及AS凭据语义。批准发行器为明确的合成动作版本，无法自动授予真实部署。

若当前122项和三个条件均已通过，唯一下一步为D1-B2最终准入审查，先闭合上述明确代码/平台/命令责任再请求执行许可。若追加重跑尚待批准，唯一下一步是审批ADDITIONAL_RUN_REQUEST中的一组54项，保持当前代码与原始失败记录；没有按时间默许。

真实部署、P1/P2、S3-B2/S5继续闭合。A/B/AB独立算法创新资格、严格分离门、COL2026暂停和FS23延期沿用。
''')
statuses=['D1B1_SUPPLEMENT_IMPLEMENTED','D1B2_AUTHORIZATION_PENDING','REAL_DEPLOYMENT_NOT_RUN','P1A_NOT_AUTHORIZED','P1B_NOT_AUTHORIZED','P2_NOT_AUTHORIZED','S3B2_NOT_AUTHORIZED','S5_NOT_AUTHORIZED','SOURCE_OR_REFINEMENT_GAP']
if complete:statuses+=['CROSS_PROCESS_START_ADMISSION_VERIFIED','DURABLE_START_AUTHORIZATION_VERIFIED','F23_FULL_CONTRACT_PASSED','F26_FULL_CONTRACT_PASSED','T45_FULL_CONTRACT_PASSED','R22_122_TESTS_PASSED','D1B1_OFFLINE_CONTRACT_COMPLETE']
else:statuses+=['D1B1_PARTIAL_IMPLEMENTATION']
put('FINAL_STATUS.json',{'schema':'r22-final-status/1','overall':overall,'statuses':statuses,'counts':counts,
    'same_code_version':same_code,'additional_approval_pending':not complete and not additional_approved,
    'original_suite_budget':3,'additional_explicit_approval':additional_approved,'direct_invocations':used,
    'real_deployment':False,'full_power_loss_or_hostile_same_SID_guarantee':False})
put('SOURCE_LOCK.json',{'schema':'r22-source-lock/1','request':pre['request'],'approval_receipt_sha256':sha(OUT/'APPROVAL_RECEIPT.json'),
    'parent_R21_source_lock':{'path':str(R21/'SOURCE_LOCK.json'),'sha256':sha(R21/'SOURCE_LOCK.json')},
    'scope_lock_sha256':sha(OUT/'R22_SCOPE_LOCK.json'),'file_lock_sha256':sha(OUT/'R22_FILE_LOCK.json'),
    'code':lock['executed_code'],'inputs':lock['inputs'],'original_snapshots':changes,
    'all_results':history['runs'],'additional_approval':receipt,'failure_history_preserved':True,
    'protected_unchanged_except5':len(pre['protected'])-5,'reports':[{'path':str(OUT/n),'sha256':sha(OUT/n)} for n in ['01_IMPLEMENTATION_SUMMARY.md','02_CROSS_PROCESS_ADMISSION.md','03_DURABLE_START_AUTHORIZATION.md','04_FAILURE_AND_RECOVERY_RESULTS.md','05_TEST_RESULTS_AND_COST.md','06_CODE_DIFF_AND_INTEGRITY.md','07_FINAL_VERDICT_AND_NEXT_STEP.md']],
    'process':'informed model-assisted implementation/execution/audit; external verification pending',
    'version_qualification':{'same_final_code':same_code,'all122_accepted':complete},'self_hash_policy':'DELIVERY_QA manifest excludes itself'})
print(json.dumps({'reports':7,'selected_counts':counts,'same_version':same_code,'complete':complete,'suite_calls':used,'application_tests_run_by_assembly':0}))
