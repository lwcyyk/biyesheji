"""Administrative research package/integrity receipt. Never invokes runtime seal.

Only this new delivery and four authorized prepend-only navigation files write.
"""
from AUDIT_INPUTS import ROOT, PREV, BOUND, OUT, E, RUNTIME, ISOLATED, NAV, save, read, sha, row, cp
from pathlib import Path
import hashlib
import json
import re
import zipfile
from datetime import datetime,timezone
import time

tick=time.perf_counter()
assert not (E/'DELIVERY_CHECK.json').exists(), 'Finalized receipt is immutable'
review=read(E/'SECOND_ARITHMETIC_REVIEW.json');assert review['status']=='PASS_ADMINISTRATIVE_RESEARCH_CHECKS_ONLY'
bindings=read(E/'PROPOSAL_BINDINGS.json')
for k in ['capacity','close','MR_original_rule','PENDING_original_v2']:
    r=bindings[k];assert sha(r['path'])==r['sha256']

required_inputs=[
 (PREV,'FINAL_DECISION.md'),(PREV,'C09_RECORD_COUNT_BOUND_PROOF.md'),(PREV,'C09_TOTAL_BYTE_BOUND_PROOF.md'),
 (PREV,'C09_OVERFLOW_AND_CLOSE_RESERVE.md'),(PREV,'C09_CONCURRENCY_AND_CRASH_ANALYSIS.md'),(PREV,'C09_WORK_COMPLEXITY_BOUND.md'),
 (PREV,'CAPACITY_CONTRACT_FINAL_PROPOSAL.md'),(PREV,'CONTRACT_APPROVAL_CHECKLIST.md'),
 (BOUND,'FINAL_DECISION.md'),(ROOT/'DCL-R6-EvidenceContract-Closure','FINAL_DECISION.md'),
 (ROOT/'DCL-R6-FullChain-AdmissionFix','FINAL_DECISION.md'),
 (PREV,'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json'),(PREV,'evidence/QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json'),
 (PREV,'evidence/HISTORICAL_RECHECK.json'),(BOUND,'evidence/COUNT_SCOPE_COVERAGE_REVIEW.json'),
 (BOUND,'evidence/GLOBAL_JOURNAL_BYTE_MODEL.json'),(BOUND,'evidence/TOTAL_BYTE_FAMILY_AUDIT.json'),
 (BOUND,'MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md'),(BOUND,'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'),
 (ROOT/'DCL-R6-FullChain-AdmissionFix','maintenance/archive_oracle.py'),
 (ROOT/'DCL-R6-FullChain-AdmissionFix','maintenance/archive_check.py')]
copied=[]
for base,n in required_inputs:
    p=base/n;q=E/'PRIOR_INPUT_COPIES'/base.name/n;cp(p,q);assert sha(p)==sha(q)
    copied.append({'original':row(p),'copy':str(q)})
save('COPIED_INPUT_LOCK.json',{'files':copied,'required_initial_reports':11,'target_imports':0})
h=read(PREV/'evidence/HISTORICAL_RECHECK.json');assert h['pending']==17 and h['rows']==24
assert h['c09_source_sha256']==sha(RUNTIME/'src/c09_handoff.py')
for r in h['originals']:assert sha(r['path'])==r['sha256']
save('HISTORICAL_C09_INHERITANCE.json',{'scope':'historical CalDiag C09 bytes and original logs only; no current MR/resource qualification',
 'pending':17,'rows':24,'bytes':27144,'c09_source_sha256':h['c09_source_sha256'],
 'originals_rechecked':8,'journal_appends_in_pending_interval':h['global_journal_rows_during_pending'],
 'new_runs':0,'prior_receipt':row(PREV/'evidence/HISTORICAL_RECHECK.json')})

decision=read(E/'FINAL_GATE_DECISIONS.json')
save('FINAL_MACHINE_DECISION.json',{
 'schema':'DCL-CLOSE-RESERVE-STATIC-DECISION/1','client_date':'2026-11-16','timezone':'Asia/Shanghai',
 'overall':'CLOSE_SOURCE_CORE_COUNTS_CONDITIONAL_FULL_VOLUME_AND_WORK_UNRESOLVED',
 'gates':decision['gates'],'final_answers_count':20,'producer_families':36,
 'close_status':'CLOSE_RESERVE_UNRESOLVED','legacy_close_status':'CLOSE_RESERVE_BOUND_UNRESOLVED',
 'N_core_attempts_H0':160,'N_core_paths_no_staging':54,'N_close_max':None,'B_close_max':None,
 'main_bound_proposed':345148,'previous_local_subset_proposed':350166,'B_C09_total':None,
 'COUNT_BOUND_PROVED':'CONDITIONAL_OLD_FROZEN_SCOPE','BYTE_BOUND_PROVED':'NOT_OBTAINED_FOR_FULL_RESOURCE_CONTRACT',
 'WORK_BOUND_PROVED':'CONDITIONAL_ACCEPTED_INPUT_ORACLE_ONLY','WALL_TIME_BOUND':'UNRESOLVED',
 'capacity':'CAPACITY_CONTRACT_NOT_READY','capacity_approved':False,'capacity_effective':False,
 'new_capacity_values_selected':False,'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','T0':None,'deadline':None,'R':None,
 'runtime_implementation_edits':0,'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'F1_runs':0,'F4_runs':0,
 'research_tools':'hash/AST/JSON grammar/report/archiving only; no protocol implementations or runtime imports'})

def L(n):return '['+n+']('+str(OUT/n).replace('\\','/')+')'
prefix=('## DCL-R6-C09-CloseReserve-Closure 静态审查（2026-11-16）\n\n'
 '**关闭保留量仍未闭合，完整容量NOT_READY。** 已枚举36类关闭/退出/封存/行政生产者和204个相关调用点；'
 '冻结scope关闭核心≤160＋H次生产尝试、54个稳定路径粗界，均非完整关闭配额。'
 'ABI/schema条件下ABORTING237、关闭委托260、waitpid1223/565；其余R/T/E/V、终态复核、原始流和行政派生字节仍需闭合。'
 '345148主日志及350166局部集合只保留各自原待批条件。\n\n'
 'CLOSED之后可有有限已有角色的close_attempt/stop_event/result；一般API重复调用族与旧冻结次数域分开。'
 'EIO时本进程HALTED、共享取消、真实退出/组空和证据完整性分别取证；缺父waitpid或持久证据保留UNKNOWN。'
 'COUNT_BOUND旧scope条件性保持；完整BYTE/WORK和300秒保证未取得。\n\n'
 'CAPACITY_CONTRACT_NOT_READY；CLOSE_RESERVE_UNRESOLVED；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。'
 '现行256/257及64运行源/输入保持；本轮实现/WSL/动态/真实故障/F1/F4均0，T0/R=null。'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 +L('FINAL_DECISION.md')+' · '+L('CLOSE_RESERVE_BOUND_PROOF.md')+' · '+L('UNRESOLVED_BOUND_CHECKLIST.md')+' · '+L('EVIDENCE_INDEX.md')+'\n\n'
 '下文逐字节保留前序导航。\n\n---\n\n')
nav=read(E/'NAV_BASELINE.json')['files']
for r in nav:
    p=Path(r['path']);old=Path(r['copy']).read_bytes()
    assert p.read_bytes()==old and sha(r['copy'])==r['sha256']
    p.write_bytes(prefix.encode('utf-8')+old)

prior=read(E/'ALL_PRIOR_BASELINE.json')['files'];assert len(prior)==10174
bad=[]
for r in prior:
    p=Path(r['path'])
    if not p.is_file() or p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:bad.append(str(p))
assert not bad,bad
expected={r['path'] for r in prior}
current={str(p) for base in [ROOT,ISOLATED] for p in base.rglob('*') if p.is_file() and not p.is_relative_to(OUT) and not(p.parent==ROOT and p.name in NAV)}
extra=sorted(current-expected);missing=sorted(expected-current);assert not extra and not missing,(extra,missing)
source=read(E/'FROZEN_SOURCE_LOCK.json')['files']
for r in source:assert sha(r['path'])==sha(r['copy'])==r['sha256']
mis=read(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
miserr=[r['relative'] for r in mis['files'] if sha(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']]
assert len(mis['files'])==47 and not miserr
nav_result=[]
for r in nav:
    assert Path(r['path']).read_bytes().endswith(Path(r['copy']).read_bytes())
    nav_result.append({'path':r['path'],'old_suffix_sha256':r['sha256'],'suffix_preserved':True,'new_sha256':sha(r['path'])})
save('FINAL_IMMUTABILITY_CHECK.json',{'all_prior':10174,'historical9867':9867,'previous_deliveries':307,
 'mismatches':bad,'extra_outside_new_delivery':extra,'missing_old_files':missing,
 'runtime_objects':64,'old_maintenance_review_objects':8,'old_contract_review_objects':21,
 'mispath_objects':47,'mispath_errors':miserr,'nav':nav_result})

jsons=0;links=0;linkerr=[]
for p in OUT.rglob('*.json'):read(p);jsons+=1
for p in OUT.glob('*.md'):
    t=p.read_text(encoding='utf-8');assert '不是' not in t
    for target in re.findall(r'\]\(([^)]+)\)',t):
        links+=1;target=re.sub(r':\d+$','',target.strip('<>'))
        if not Path(target).exists() and target!=str(E/'DELIVERY_CHECK.json').replace('\\','/'):
            linkerr.append({'report':p.name,'target':target})
assert not linkerr,linkerr

mf=OUT/'CRB_MANIFEST.json';zp=OUT/'CRB_EVIDENCE.zip'
excluded={'CRB_MANIFEST.json','CRB_EVIDENCE.zip','CRB_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
files=[]
for p in sorted(OUT.rglob('*')):
    rel=p.relative_to(OUT).as_posix()
    if p.is_file() and '__pycache__' not in p.parts and rel not in excluded:
        files.append({'relative':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'schema':'DCL-CRB-RESEARCH-MANIFEST/1','client_date':'2026-11-16',
 'status':'STATIC_RESEARCH_ARTIFACTS_ONLY','scope':'research reports, copied frozen inputs, source census and syntax algebra; no native/admin runtime seal',
 'files':files,'excluded':sorted(excluded)}
mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for r in files:z.write(OUT/r['relative'],r['relative'])
    z.write(mf,mf.name)
with zipfile.ZipFile(zp) as z:
    names=z.namelist();assert len(names)==len(set(names))==len(files)+1
    assert set(names)=={r['relative'] for r in files}|{mf.name}
    assert z.read(mf.name)==mf.read_bytes()
    for r in files:
        b=z.read(r['relative']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
zsha=sha(zp)
(OUT/'CRB_EVIDENCE.zip.sha256').write_text(zsha+'  CRB_EVIDENCE.zip\n',encoding='ascii')
save('DELIVERY_CHECK.json',{'schema':'DCL-CRB-DELIVERY/1','client_date':'2026-11-16','timezone':'Asia/Shanghai',
 'status':'PASS_ADMINISTRATIVE_RESEARCH_DELIVERY_ONLY','close_status':'CLOSE_RESERVE_UNRESOLVED',
 'capacity':'CAPACITY_CONTRACT_NOT_READY','CRB_gates':decision['gates'],'reports':13,'index':1,'final_answers':20,
 'producer_families':36,'static_relevant_call_sites':204,'core_attempt_upper_H0':160,'core_paths_upper_no_staging':54,
 'N_close_max':None,'B_close_max':None,'B_C09_total':None,'main_proposed':345148,'old_local_subset_proposed':350166,
 'conditional_ABI_schema_bounds':{'ABORTING':237,'external_closing':260,'waitpid_normal':1223,'waitpid_fallback':565},
 'historical9867_unchanged':9867,'prior_delivery_objects_unchanged':307,'all_prior_objects_unchanged':10174,
 'historical_mismatches':bad,'new_files_outside_delivery':extra,'runtime_objects_unchanged':64,
 'prior_maintenance_objects_unchanged':8,'prior_contract_review_objects_unchanged':21,'mispath_objects_unchanged':47,
 'navigation_old_byte_suffixes_preserved':4,'prior_archive_members_fully_read':301,'historic_PENDING':17,
 'capacity_draft_sha256':bindings['capacity']['sha256'],'close_draft_sha256':bindings['close']['sha256'],
 'original_pending_v2_sha256':bindings['PENDING_original_v2']['sha256'],'MR_rule_sha256':bindings['MR_original_rule']['sha256'],
 'capacity_approved':False,'close_approved':False,'any_draft_activated':False,'new_guard_values_selected':False,
 'old_guards':'256/257_UNCHANGED','MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE',
 'runtime_implementation_edits':0,'budget_core_edits':0,'logger_quota_closure_implementation':0,'native_admin_gate_MR_edits':0,
 'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'F1_runs':0,'F4_runs':0,'T0':None,'deadline':None,'R':None,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','WALL_TIME_BOUND':'UNRESOLVED',
 'native_seal':'NOT_APPLICABLE_NO_RUNTIME','administrative_runtime_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','JSON_parsed':jsons,'links_checked':links,'link_errors':linkerr,
 'manifest_files':len(files),'ZIP_members':len(names),'manifest_sha256':sha(mf),'ZIP_sha256':zsha,
 'ZIP_bytes':zp.stat().st_size,'receipt_excluded_from_preimages':True,
 'utc_recorded':datetime.now(timezone.utc).isoformat(),'research_packaging_seconds':time.perf_counter()-tick})
print(json.dumps({'delivery':'PASS_RESEARCH_ONLY','reports':13,'answers':20,'history':9867,'all_prior':10174,
 'source_objects':64,'ZIP_members':len(names),'ZIP_bytes':zp.stat().st_size,'ZIP_sha256':zsha,
 'close':'UNRESOLVED','capacity':'NOT_READY','runtime_runs':0},ensure_ascii=False))
