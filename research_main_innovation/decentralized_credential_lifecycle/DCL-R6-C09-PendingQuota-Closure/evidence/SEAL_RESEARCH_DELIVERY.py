"""Administrative research delivery only; no native/admin runtime seal invocation."""
from RESEARCH_AUDIT import ROOT, OLD, OUT, E, RUNTIME, read, write, row, sha
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
import zipfile
from datetime import datetime, timezone

tick=time.perf_counter()
assert not (E/'DELIVERY_CHECK.json').exists(), 'Seal once; finalized receipts are immutable'
for n in ['evidence/SECOND_PASS_REVIEW.json','proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json']:
    assert (OUT/n).is_file()
qpath=OUT/'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json';qhash=sha(qpath)
assert qhash==read(E/'FINAL_PROPOSAL_BINDING.json')['proposal']['sha256']

# Preserve the read inputs as new research copies. Historical originals stay untouched.
prior=[]
for base,names in [
 (OLD,['FINAL_DECISION.md','C09_PENDING_PRODUCER_AUDIT.md','C09_PENDING_RECORD_BOUND.md','C09_PENDING_BYTE_BOUND.md',
       'C09_PENDING_COUNTEREXAMPLES.md','EVIDENCE_TOTAL_BYTE_BOUND.md','ARCHIVE_WORK_COMPLEXITY.md',
       'EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.md','MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md','C09BOUND_MANIFEST.json',
       'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json','proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json',
       'evidence/COUNT_SCOPE_COVERAGE_REVIEW.json','evidence/GLOBAL_JOURNAL_BYTE_MODEL.json','evidence/ZIP_BOUND_ALGEBRA.json']),
 (ROOT/'DCL-R6-EvidenceContract-Closure',['FINAL_DECISION.md']),
 (ROOT/'DCL-R6-FullChain-AdmissionFix',['FINAL_DECISION.md']),
 (ROOT/'DCL-R6-CalDiag',['CALDIAG_FINAL_DECISION.md'])]:
    for name in names:
        p=base/name;dest=E/'PRIOR_INPUT_COPIES'/base.name/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,dest);assert sha(p)==sha(dest)
        prior.append({'original':row(p),'copy':str(dest)})
write('PRIOR_INPUT_COPY_LOCK.json',{'files':prior})

gates={
 'PQ-1':{'status':'PROVED','scope':'all native producers in frozen closed caller set'},
 'PQ-2':{'status':'CONDITIONAL_PROVED','scope':'v2 slot injection invariant; current source COUNTEREXAMPLE'},
 'PQ-3':{'status':'PARTIAL','scope':'main345148 conditionally proved; PENDING_BYTE_BOUND_PARTIAL'},
 'PQ-4':{'status':'UNRESOLVED','scope':'CLOSE_RESERVE_BOUND_UNRESOLVED; minimal marker subgroup only'},
 'PQ-5':{'status':'PARTIAL','scope':'12 static interleavings; current quota implementation/native fault tests absent'},
 'PQ-6':{'status':'PARTIAL','scope':'count set deltas and layered bytes; full capacity/work unresolved'},
 'PQ-7':{'status':'PARTIAL','scope':'logical approve/reject text ready; whole close/capacity approval BLOCKED'}}
write('FINAL_DECISION.json',{'schema':'DCL-C09PQ-STATIC-DECISION/1','client_date':'2026-11-16','timezone':'Asia/Shanghai',
 'overall':'C09_MAIN_BOUND_CONDITIONAL_CLOSE_RESERVE_UNRESOLVED_CAPACITY_NOT_READY',
 'gates':gates,'quota_proposal_sha256':qhash,'effective':False,'approved':False,
 'current_source_pending_bound':'ABSENT_RESOURCE_QUOTA_WITH_REPRESENTATION_CAVEAT',
 'historical_PENDING':17,'main_attempts_proposed':256,'main_rows_proposed':263,'main_bytes_proposed':345148,
 'local_minimal_subgroup_bytes_proposed':350166,'full_close_bytes':None,'full_raw_bytes':None,
 'CLOSE_RESERVE':'CLOSE_RESERVE_BOUND_UNRESOLVED','capacity':'CAPACITY_CONTRACT_NOT_READY',
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','RESOURCE_GATE_PASS':'NOT_OBTAINED',
 'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED',
 'T0':None,'deadline':None,'R':None,'runtime_source_edits':0,'new_mechanism_implementation':0,
 'WSL_calls':0,'native_faults':0,'dynamic_tests':0,'model_runs':0})
write('TASK_STEP_RECEIPT.json',{'mode':'STATIC_ANALYSIS_ONLY','steps':[
 {'step':i,'subject':subject,'artifact':name,'status':status} for i,subject,name,status in [
 (1,'latest reports and full previous ZIP','PREVIOUS_ZIP_FULL_VERIFICATION.json','PROVED'),
 (2,'all PENDING producers','STATIC_PRODUCER_CENSUS.json','PROVED'),
 (3,'256 observation semantics','../C09_OBSERVATION_SEMANTICS.md','CONDITIONAL_PROVED'),
 (4,'263 native row composition','../C09_RECORD_COUNT_BOUND_PROOF.md','CONDITIONAL_PROVED'),
 (5,'17 historical rows','HISTORICAL_RECHECK.json','PROVED'),
 (6,'concurrency/replay/crash/recovery','CRASH_AND_CONCURRENCY_MATRIX.json','PARTIAL'),
 (7,'345148 field derivation','RECORD_BYTE_ALGEBRA.json','CONDITIONAL_PROVED'),
 (8,'STOP/CLOSED after exhaustion','../C09_OVERFLOW_AND_CLOSE_RESERVE.md','UNRESOLVED'),
 (9,'native/admin required inputs','../FULL_EVIDENCE_BYTE_RECALCULATION.md','PARTIAL'),
 (10,'log work and resource bounds','WORK_BOUND_RECALCULATION.json','PARTIAL'),
 (11,'complete evidence bytes','CAPACITY_RECALCULATION.json','UNRESOLVED'),
 (12,'strict existing draft assessment','../CONTRACT_APPROVAL_CHECKLIST.md','PARTIAL'),
 (13,'minimal unclosed counterexamples','CRASH_AND_CONCURRENCY_MATRIX.json','PROVED'),
 (14,'generic G comparison','GENERAL_METHOD_COMPARISON.json','PROVED'),
 (15,'final pending approval draft','../CAPACITY_CONTRACT_FINAL_PROPOSAL.md','PARTIAL'),
 (16,'independent MR contract status','../MR_CROSS_INSTANCE_STATUS.md','PROVED'),
 (17,'decision and next action','../FINAL_DECISION.md','PROVED')]]})
write('CAPACITY_AND_MR_STATUS.json',{'capacity':{'status':'CAPACITY_CONTRACT_NOT_READY','selected_new_caps':None,
 'old_admin_files_guard':256,'old_native_member_guard':257,'guards_changed':False,'approved':False,'effective':False},
 'MR':{'status':'PROPOSED_NOT_EFFECTIVE','rule_sha256':sha(OLD/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'),
 'approved':False,'effective':False,'approved_pairs':[],'A_identity':None,'B_identity':None}})

# Prepend only; preserve original bytes of each navigation file as a suffix.
nav=read(E/'NAV_BASELINE.json')['files']
def L(name):return '['+name+']('+str(OUT/name).replace('\\','/')+')'
prefix=(
 '## DCL-R6-C09-PendingQuota-Closure 静态审查（2026-11-16）\n\n'
 '**345148主日志条件证明完成；完整关闭保留量与容量未决。** '
 '256次准入尝试＋六stage＋ACK1推出263行；冻结源码仍保留PENDING重复反例，历史17条已直接核对原始导出锁。'
 'v2待批cursor1198/更新522，主日志与声明的cursor/首错/STOP/CLOSED及失败staging局部保留界350166，'
 '写量971216/durability1316仅针对该有界调用子合同；stop_result/MR/seal/admin及跨角色EIO传播仍需闭合。\n\n'
 'CLOSE_RESERVE_BOUND_UNRESOLVED；CAPACITY_CONTRACT_NOT_READY；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。'
 '现行256/257守卫及64运行源/输入原字节保持；本轮实现/WSL/动态/真实故障/F1/F4均0，T0/R=null。'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 +L('FINAL_DECISION.md')+' · '+L('C09_TOTAL_BYTE_BOUND_PROOF.md')+' · '+L('CONTRACT_APPROVAL_CHECKLIST.md')+' · '+L('EVIDENCE_INDEX.md')+'\n\n'
 '下文完整保留前序导航字节。\n\n---\n\n')
for r in nav:
    p=Path(r['path']);old=Path(r['copy']).read_bytes();current=p.read_bytes()
    assert sha(r['copy'])==r['sha256'] and current==old, str(p)
    p.write_bytes(prefix.encode('utf-8')+old)

history=read(E/'HISTORY_BASELINE_9867.json')['files'];hist_errors=[]
for r in history:
    p=Path(r['path'])
    if not p.is_file() or p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:hist_errors.append(str(p))
assert not hist_errors,hist_errors
oldbase=read(E/'PREVIOUS_DELIVERY_BASELINE.json')['files']
assert len(oldbase)==160
prior_errors=[r['path'] for r in oldbase if not Path(r['path']).is_file() or sha(r['path'])!=r['sha256']]
assert not prior_errors,prior_errors
frozen=read(E/'FROZEN_SOURCE_LOCK.json')['files']
for r in frozen:assert sha(r['path'])==sha(r['copy'])==r['sha256']
for r in read(E/'PRIOR_OBJECT_LOCK.json')['files']:assert sha(r['path'])==r['sha256']
native_root=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
expected={r['path'] for r in history+oldbase}
current={str(p) for base in [ROOT,native_root] for p in base.rglob('*')
         if p.is_file() and not p.is_relative_to(OUT) and not (p.parent==ROOT and p.name in {Path(r['path']).name for r in nav})}
extra=sorted(current-expected);missing=sorted(expected-current);assert not extra and not missing,(extra,missing)
mis=read(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
miserr=[r['relative'] for r in mis['files'] if sha(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']]
assert len(mis['files'])==47 and not miserr
nav_check=[]
for r in nav:
    old=Path(r['copy']).read_bytes();new=Path(r['path']).read_bytes();assert new.endswith(old)
    nav_check.append({'path':r['path'],'original_suffix_sha256':r['sha256'],'suffix_preserved':True,'new_sha256':sha(r['path'])})
write('FINAL_IMMUTABILITY_CHECK.json',{'history_files':len(history),'historical_mismatches':hist_errors,
 'previous_delivery_files':len(oldbase),'previous_delivery_mismatches':prior_errors,'runtime_objects':len(frozen),
 'prior_review_objects':8,'prior_contract_review_objects':21,'mispath_objects':47,'mispath_errors':miserr,
 'new_files_outside_new_delivery':extra,'missing_old_files':missing,'navigation':nav_check})

# Recheck all links and JSON, then construct a non-self-referential research archive.
links=0;linkerr=[];json_count=0
for p in OUT.rglob('*.json'):read(p);json_count+=1
for p in OUT.glob('*.md'):
    text=p.read_text(encoding='utf-8');assert '不是' not in text
    for target in re.findall(r'\]\(([^)]+)\)',text):
        links+=1;target=re.sub(r':\d+$','',target.strip('<>'))
        if not Path(target).exists() and target!=str(E/'DELIVERY_CHECK.json').replace('\\','/'):
            linkerr.append({'report':p.name,'target':target})
assert not linkerr,linkerr
manifest_path=OUT/'PQUOTA_MANIFEST.json';archive=OUT/'PQUOTA_EVIDENCE.zip'
excluded={'PQUOTA_MANIFEST.json','PQUOTA_EVIDENCE.zip','PQUOTA_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
files=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.relative_to(OUT).as_posix() not in excluded:
        files.append({'relative':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'schema':'DCL-C09PQ-RESEARCH-MANIFEST/1','client_date':'2026-11-16','status':'STATIC_RESEARCH_DELIVERY_ONLY',
 'scope':'Reports, frozen read inputs, byte algebra and proposed contracts; no runtime seal or executable deployment lock',
 'files':files,'excluded':sorted(excluded),'interpreter_cache_excluded':True}
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for r in files:z.write(OUT/r['relative'],r['relative'])
    z.write(manifest_path,manifest_path.name)
with zipfile.ZipFile(archive) as z:
    names=z.namelist();assert len(names)==len(set(names))==len(files)+1
    assert set(names)=={r['relative'] for r in files}|{manifest_path.name}
    assert z.read(manifest_path.name)==manifest_path.read_bytes()
    for r in files:
        data=z.read(r['relative']);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
archive_hash=sha(archive)
(OUT/'PQUOTA_EVIDENCE.zip.sha256').write_text(archive_hash+'  PQUOTA_EVIDENCE.zip\n',encoding='ascii')
write('DELIVERY_CHECK.json',{'schema':'DCL-C09PQ-DELIVERY/1','client_date':'2026-11-16','timezone':'Asia/Shanghai',
 'status':'PASS_ADMINISTRATIVE_RESEARCH_DELIVERY_ONLY','overall':read(E/'FINAL_DECISION.json')['overall'],'PQ':gates,
 'specified_reports':14,'additional_reports':2,'index':1,'historical_files':len(history),'historical_mismatches':hist_errors,
 'previous_delivery_files_unchanged':len(oldbase),'frozen_runtime_objects_unchanged':64,'prior_maintenance_objects_unchanged':8,
 'prior_contract_review_objects_unchanged':21,'mispath_files_unchanged':47,'nav_original_suffixes_preserved':4,
 'new_files_outside_new_delivery':extra,'historical_native_PENDING':17,'historical_raw_originals_rechecked':8,
 'previous_zip_fully_read_members':157,'main_limit_proposed':345148,'main_records_proposed':263,'attempts_proposed':256,
 'cursor_bytes_proposed':1198,'cursor_updates_proposed':522,'local_retained_bytes_proposed':350166,
 'local_write_bytes_proposed':971216,'local_fsync_attempts_proposed':1316,
 'quota_proposal_sha256':qhash,'quota_approved':False,'quota_effective':False,
 'capacity':'CAPACITY_CONTRACT_NOT_READY','CLOSE_RESERVE':'CLOSE_RESERVE_BOUND_UNRESOLVED',
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','old_guards':'256/257_UNCHANGED',
 'runtime_source_edits':0,'logger_or_quota_implementation':0,'budget_core_edits':0,'packager_gate_MR_edits':0,
 'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'F1_runs':0,'F4_runs':0,'T0':None,'deadline':None,'R':None,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED',
 'native_seal':'NOT_APPLICABLE_NO_RUNTIME','administrative_runtime_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','JSON_parsed':json_count,'links_checked':links,'link_errors':linkerr,
 'manifest_rows':len(files),'ZIP_entries':len(names),'manifest_sha256':sha(manifest_path),
 'ZIP_sha256':archive_hash,'ZIP_bytes':archive.stat().st_size,'receipt_excluded_from_manifest_and_zip':True,
 'utc_recorded':datetime.now(timezone.utc).isoformat(),'research_admin_elapsed_seconds':time.perf_counter()-tick})
print(json.dumps({'delivery':'PASS_RESEARCH_ONLY','historic':len(history),'previous':len(oldbase),'source':64,
 'reports':14,'archive_files':len(files),'ZIP_entries':len(names),'ZIP_bytes':archive.stat().st_size,
 'ZIP_sha256':archive_hash,'quota_sha256':qhash,'links_checked':links,'runtime_runs':0},ensure_ascii=False))
