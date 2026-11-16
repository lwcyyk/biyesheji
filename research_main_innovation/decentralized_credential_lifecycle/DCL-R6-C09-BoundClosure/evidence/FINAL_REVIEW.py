"""Final mathematical/draft review; preserve every computed raw observation."""
from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence';P=O.parent
def read(p):return json.loads(p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def enc(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
qp=O/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json';q=read(qp)
# The256th computed PENDING must retain its full raw facts. Successful handoff
# still has <=255 pending plus one terminal check; failed quota path may have256.
q['pending_record_max']=256;q['pending_max_successful_handoff']=255;q['terminal_check_reserved_slots']=0
q['terminal_check_upper']=1;q['joint_count_constraint']='N_pending+N_terminal<=256; N_terminal<=1; success needs one terminal, failure may contain256 pending'
q['last_attempt']='Always append the full256th classification result within its reserved slot. If still PENDING, publish stop and a fixed exhaustion receipt; no257th classification. No computed raw facts replaced by a summary.'
q['cursor_semantics']='Counters record reserved/debited work and bytes, not claims of fully written records. Actual row count is recomputed from raw bytes.'
q['quota_file_schema']['pending_reserved']=256
failure={'schema':'C09-LOG-QUOTA-FAIL/1-DRAFT','handoff_id':'a'*64,'batch_id':'batch14','boot_id':'b'*36,
 'reason':'C09_PENDING_ALLOWANCE_EXHAUSTED','used':256,'pending_reserved':256,'boottime':0,'utc_ns':0}
Lf=len(enc(failure))+(25-1)+(20-1);assert Lf==334
q['failure_record_schema']=failure;q['failure_record_max_bytes']=Lf
q['retained_stable_objects_max_bytes']=345148+956+Lf
q['failed_staging_max_bytes']=2*956+Lf
q['total_quota_evidence_max_bytes']=q['retained_stable_objects_max_bytes']+q['failed_staging_max_bytes']
q['quota_total_write_upper']=345148+266*956+Lf
q['future_files']='Proposed local quota envelope:2 fixed objects + up to3 failed staging objects (reserve/poison/emergency); plus any changed stop/test/source effects must be recounted before integration.'
q['failed_staging_policy']='Preserve both failed cursor reservations/poison staging and the failed emergency staging; no cleanup deletion to force archive success.'
q['lock_order_requirement']='After last PENDING raw append, publish STOP/no-more-observations under current serialization, then release lifecycle lock before frozen stop_tree/abort. No nested lifecycle re-acquisition.'
q['main_log_actual_sharp_upper']=max(256*1298,255*1298+1322)+6*948+1028
assert q['main_log_actual_sharp_upper']==339028 and q['total_quota_evidence_max_bytes']==348684 and q['quota_total_write_upper']==599778
write(qp,q)
cap_p=O/'proposals/EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.json';cap=read(cap_p)
cap['pending_only_draft_limits'].update(pending_rows=256,successful_pending_rows=255,fixed_failure=Lf,failed_staging_max=2246,total_quota_retained_max=348684)
write(cap_p,cap)
work_p=E/'WORK_MEMORY_FD_MODEL.json';work=read(work_p);r=work['steps'][1]
r['input']='<=263 main slots, row<=1322; cursor<=956; emergency<=334; failed staging retained separately'
r['write']='<=345148 +266*956+334=599778'
r['complexity']='O(263*Lmax+266*Lcursor); <=798 durability attempts including2 emergency syncs and1 initial log-directory sync; stop/seal separately accounted'
write(work_p,work)
d_p=E/'FINAL_ANALYSIS_DECISION.json';d=read(d_p)
d['quota_policy'].update(pending=256,successful_pending=255,failure_bytes=334,write_upper=599778,retained_with_failed_staging=348684)
write(d_p,d)
finding_p=E/'COUNT_COVERAGE_FINDING.json';finding=read(finding_p)
finding['source_site']='manager_recovery.py:56 with locked(G,mr_events.lock)';write(finding_p,finding)
pending_notes={
 'draft_refinement':'Keep full facts for256th pending observation;255 is the successful-handoff pending bound,256 the per-batch failure-inclusive bound.',
 'staging_refinement':'Include two failed cursor writes plus one emergency staging,2246 bytes; total local quota retained upper348684. Successful/quiescent objects upper346438.',
 'new_policy_code_written':False,'runtime_failures_or_retries':0,
 'main_log_rows':263,'pending_max_all_outcomes':256,'pending_max_success':255,'classification_attempts':256,
 'raw_source_counterexample_unchanged':True,'capacity_not_ready':True}
with(E/'FINAL_MATHEMATICAL_REVIEW_NOTES.json').open('x',encoding='utf-8') as f:json.dump(pending_notes,f,ensure_ascii=False,indent=2);f.write('\n')
replacements={
 'C09_PENDING_BYTE_BOUND.md':[
 ('独立待批配额草案：256次分类尝试，最多255条PENDING，最后1槽仅供终态分类；再计6个stage＋1ACK，原生主日志最多263行。','独立待批配额草案：256次分类尝试，成功路径最多255条PENDING加1条终态分类；失败路径允许256条完整PENDING后立即关闭。所有已计算分类均保留raw facts，再计6个stage＋1ACK，主日志最多263行。'),
 ('记录实际类型上界：255×1298＋1×1322＋6×948＋1028=339028字节。','记录实际类型上界：max(256×1298,255×1298＋1322)＋6×948＋1028=339028字节。'),
 ('sidecar≤956、固定失败摘要≤333，保留对象合计≤346437。','sidecar≤956、固定失败摘要≤334，稳定对象合计≤346438；两份cursor失败staging和一份emergency失败staging再计≤2246，全部配额相关保留对象≤348684。'),
 ('第256次仍PENDING时只保存固定错误码摘要并请求关闭，不追加第256条PENDING。','第256次仍PENDING时，先完整保存该条facts/PENDING，再写固定错误码摘要并请求关闭；禁止第257次分类。摘要不会替换已计算的原始观察。')],
 'ARCHIVE_WORK_COMPLEXITY.md':[
 ('cursor956、失败333','cursor956、失败334'),('599777','599778'),('失败333','失败334'),
 ('Main slots, row','Main slots, row'),('Log append1, existing lifecycle lock1','Log append1, existing lifecycle lock1'),
 ('<=263 main slots, row<=1322; cursor<=956; fail<=333','<=263 main slots, row<=1322; cursor<=956; emergency<=334; failed staging retained separately'),
 ('<=345148 +266*956+333=599778','<=345148 +266*956+334=599778')],
 'EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.md':[
 ('256个独立分类额度，PENDING255、终态保留1、主日志263行','256个独立分类额度，成功PENDING≤255、所有路径PENDING≤256、终态分类≤1、主日志≤263行'),
 ('cursor956、单次失败摘要333','cursor956、单次失败摘要334及失败staging≤2246')],
 'CONTRACT_APPROVAL_CHECKLIST.md':[
 ('255 PENDING与最后终态槽','256总分类、成功PENDING≤255/失败含PENDING≤256，完整记录最后一次再停'),
 ('956 cursor/333失败摘要','956 cursor/334失败摘要及失败staging保留')],
 'FINAL_DECISION.md':[
 ('255 PENDING','成功≤255/全路径≤256 PENDING'),
 ('新待批政策拟255','新待批政策拟全路径256、成功255')]
}
for name,pairs in replacements.items():
 p=O/name;s=p.read_text(encoding='utf-8')
 for old,new in pairs:s=s.replace(old,new)
 p.write_text(s,encoding='utf-8')
for name in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
 p=P/name;raw=p.read_bytes();original=(E/'NAV_ORIGINALS'/name).read_bytes();assert raw.endswith(original)
 prefix=raw[:-len(original)].decode('utf-8').replace('256观察/255 PENDING/263总行','256观察/全路径≤256 PENDING（成功≤255）/263总行')
 p.write_bytes(prefix.encode('utf-8')+original)
auth=O/'EVIDENCE_TOTAL_BYTE_BOUND.md';s=auth.read_text(encoding='utf-8')
s=s.replace('|C00–C12固定二进制|','|授权/身份输入|operator_bytes对单份原文/回执读取设4MiB；source/input locks为冻结已知字节|不把可重算报告或元数据排除出完整保留集合；动态输入实际hash/长度还需当批绑定|\n|C00–C12固定二进制|')
s=s.replace('部分MR查询8192/2048','部分MR查询结果接受8192/2048（capture后检查）')
auth.write_text(s,encoding='utf-8')
print(json.dumps({'pending_all':256,'pending_success':255,'native_rows':263,'main_reserved_bytes':345148,'cursor':956,'failure':334,
 'retained_stable':346438,'retained_with_staging':348684,'write_upper':599778,'runtime_changes':0}))
