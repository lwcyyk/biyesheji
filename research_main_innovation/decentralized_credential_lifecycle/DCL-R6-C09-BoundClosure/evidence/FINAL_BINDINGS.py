"""Freeze final approval data and source-side audit references only."""
from pathlib import Path
import ast,hashlib,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence'
def j(p):return json.loads(p.read_bytes())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,x):
 with(E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
surround=[
 {'producer':'manager_recovery.event','file':'manager_recovery.py','line':51,'sink_line':59,'process':'Root supervisor/recovery roles','target':'inputs/root_private/boot/mr_events.jsonl',
 'repeat':'Multiple queries/reviews, controlled separately by frozen calls/credits; no native PENDING append','variable':'raw query/error/identity facts; row write cap32768','fsync':True,'uniqueness':'Append events; lock fixed, not unique record key'},
 {'producer':'guard.request_stop','file':'guard.py','line':545,'sink_line':546,'process':'Frozen authorized Root/payload failure contexts','target':'out/STOP_REQUEST.json',
 'repeat':'Fixed marker path; M.abort preserves first existing marker','variable':'reason/stamp; generic helper has no universal text cap','fsync':True,'uniqueness':'One path, overwrite/preserve rules distinct'},
 {'producer':'guard.stop_tree','file':'guard.py','line':749,'sink_line':769,'process':'Root stop responsibility','target':'CLOSED.json and stop_event/result_<pid>_<time>.json',
 'repeat':'Bounded wrapper calls, not a pending logger','variable':'CG snapshots and closure errors','fsync':True,'uniqueness':'CLOSED fixed; extra stop outputs timestamped'},
 {'producer':'manager_recovery.abort','file':'manager_recovery.py','line':317,'sink_line':396,'process':'Root scheduler/coordinator/external stop','target':'mr_first_failure/close_state/close_attempts',
 'repeat':'Failure wrappers can append after markers; no C09 event() call','variable':'Error[:2048], budget hashes, role/error arrays; not every close row has MR event rowcap','fsync':True,'uniqueness':'First failure exclusive; close-state overwrite and bounded attempt log'},
 {'producer':'guard._launcher_impl waitpid','file':'guard.py','line':1225,'other_line':1255,'process':'Direct Root parent coordinator','target':'inputs/root_private/waitpid_<child>.json',
 'repeat':'At most initial/resume child witness paths','variable':'Raw wait status/state/samples','fsync':True,'uniqueness':'Per child identity'},
 {'producer':'H.coordinator_witness','file':'c09_handoff.py','line':309,'process':'Root coordinator','target':'inputs/c09_exit_witness.json',
 'repeat':'Existing witness must match exactly or reject','variable':'Exit/window/identity','fsync':True,'uniqueness':'One C09 witness; no direct native event call'},
 {'producer':'guard.seal','file':'guard.py','line':1018,'sink_lines':[1023,1024],'process':'Native sealer owner or approved external tail','target':'terminal review/native manifest/native ZIP',
 'repeat':'Single-sealer/frozen terminal obligations; failed/partial evidence stays explicit','variable':'All actual originals, not a bounded PENDING producer','fsync':'Existing source-specific guarantees','uniqueness':'Manifest/ZIP excluded from own original collection'},
 {'producer':'native/admin errors','file':'guard.py','line':1149,'other_lines':[1275,823],'process':'Frozen failure/finally roles','target':'SEAL_ERROR.json or stderr',
 'repeat':'Bounded error sites; no handoff recursive call','variable':'repr(exc)/traceback/prints may lack common byte cap','fsync':'File vsstderr rules differ','uniqueness':'Fixed error file or stdout stream'},
 {'producer':'post_exit_export','file':'startup_lifecycle.py','line':490,'other_line':503,'process':'Read-only administrative Root helper after active entry','target':'CONTROL/STARTUP_NATIVE_AUDIT.json/startup_snapshot',
 'repeat':'Current one post-exit plan; no source test/budget/role activation','variable':'/proc/system-state/quiescence/export arrays; ambient process count not bounded by Payload TasksMax4',
 'fsync':'Existing administrative record/copy rules','uniqueness':'Snapshot must be fresh, control outside native ROOT'},
]
for r in surround:r['source_sha256']=h(E/'FROZEN_RA_ORIGINALS/src'/r['file'])
put('SURROUNDING_PRODUCER_SITES.json',{'sites':surround,'native_pending_direct_sites':1,'scope':'Concrete surrounding writers, not conflated with C09-native event sources','new_execution':0})
tests=[
 '255 pending plus one verified check: preserve every row, allow once handoff if all original checks pass',
 '256 pending: preserve the full last row then safe close; no257th classify/append',
 '128/1322 row schema exact bounds and a1323-byte invalid row rejected before append; no silent raw truncation',
 'Per-type reserved345148 and off-by-one total bytes; fixed956/334 metadata and failed staging retained',
 'Wrong batch/boot/handoff/source/policy/cursor generation; missing or corrupted cursor never reset',
 'Reservation persisted then crash before append burns credit; append short write/fsync failure remains uncertain',
 'Initial/bind/reserve/poison/emergency persistence failures and last in-flight STOP timing',
 'Native ACK/commit/waitpid/fresh receiver proof unchanged; no global R change after handoff counter snapshot',
 'Shared-producer serialization/lock order; no recursive stop_tree while lifecycle lock held',
 'Quota exhaustion before coordinator scheduling is a declared resource/liveness stop, never forged success',
 'Primary close failure, external fallback and UNKNOWN classified separately; original T0/deadline preserved',
 'New metadata/test count/bytes/visits delta computed before any capacity request',
]
put('FUTURE_VALIDATION_OBLIGATIONS.json',{'status':'DESIGN_ONLY_NOT_EXECUTED','cases':tests,'new_test_code':0,'native_tests':0})
qfile=O/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json';q=j(qfile)
assert q['pending_record_max']==256 and q['pending_max_successful_handoff']==255 and q['all_C09_native_rows_max']==263
assert q['failure_record_schema']['reason'] in q['allowed_failure_codes'] and q['total_quota_evidence_max_bytes']==348684
quota_hash=h(qfile);mr=O/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json';mr_hash=h(mr)
checklist=O/'CONTRACT_APPROVAL_CHECKLIST.md';s=checklist.read_text(encoding='utf-8')
append=f'''\n日志配额政策附件SHA-256：`{quota_hash}`。可独立表达的决定如下：

> 批准日志政策：我批准C09-PENDING-QUOTA-CONTRACT/1-DRAFT及其摘要中的数值、原件保全和fail-closed原则。后续最小静态维护/实现/测试仍须按具体源码与执行锁另行授权；本次决定不批准容量扩容、动态故障或F1/F4。

> 拒绝日志政策：我拒绝上述配额参数或政策，当前日志逻辑及全部守卫保持；继续研究其他明确的有限工作量合同。

MR规则附件SHA-256：`{mr_hash}`。其独立批准/拒绝文本见[最终MR条款](MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md)。容量项目仍NOT_READY；其他任何一项获批均不代替容量证明。当前没有记录用户作出其中任一决定。
'''
s=s.replace('\nRESOURCE_GATE_PASS=NOT_OBTAINED',append+'\nRESOURCE_GATE_PASS=NOT_OBTAINED');checklist.write_text(s,encoding='utf-8')
workp=E/'WORK_MEMORY_FD_MODEL.json';work=j(workp)
work['ambient_system_state_caveat']='Administrative /proc scans and systemd responses include ambient environment, not only current slice. TasksMax4 provides no bound on global process count or all response lengths; no new environment-scale bound assumed.'
workp.write_text(json.dumps(work,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
put('FINAL_APPROVAL_BINDINGS.json',{'date':'2026-11-15','quota_rule_sha256':quota_hash,'MR_final_rule_sha256':mr_hash,
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','quota_effective':False,'capacity':'CAPACITY_CONTRACT_NOT_READY',
 'user_approval_received':False,'approval_receipt_issued':False,'new_runtime_programs':0,'new_dynamic_tests':0})
print(json.dumps({'quota_sha256':quota_hash,'MR_sha256':mr_hash,'approval_effective':False,'new_programs':0}))
