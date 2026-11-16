"""Hash/structure/accounting delivery checks and a local research ZIP only."""
from pathlib import Path
import hashlib
import json
import re
import sys
import time
import zipfile
from datetime import datetime, timezone

START=time.perf_counter()
P=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
O=P/'DCL-R6-FullChain-B'
E=O/'evidence'
NAV=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')

baseline=read(E/'HISTORY_BASELINE.json')['files']
history_errors=[]
for row in baseline:
    p=Path(row['path'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:history_errors.append(str(p))
expected={r['path'] for r in baseline}
current={str(p) for root in [P,I] for p in root.rglob('*') if p.is_file() and not p.is_relative_to(O) and not (root==P and p.parent==P and p.name in NAV)}
new_external_files=sorted(current-expected)
nav=[]
for name in NAV:
    original=(E/'NAV_ORIGINALS'/name).read_bytes();actual=(P/name).read_bytes()
    assert actual.endswith(original) and len(actual)>len(original)
    nav.append({'path':str(P/name),'original_sha256':hashlib.sha256(original).hexdigest(),
                'current_sha256':hashlib.sha256(actual).hexdigest(),'original_bytes_suffix_preserved':True,
                'prefix_bytes':len(actual)-len(original)})
mis=read(P/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
mis_errors=[r['relative'] for r in mis['files'] if sha(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']]
assert not history_errors and not new_external_files and not mis_errors
save(E/'HISTORY_AFTER_CHECK.json',{'status':'PASS_ADMINISTRATIVE_IMMUTABILITY','historical_files':len(baseline),
 'mismatches':history_errors,'new_files_outside_delivery':new_external_files,'navigation':nav,
 'mispath_count':len(mis['files']),'mispath_mismatches':mis_errors,'WSL_queries':0})

source=read(E/'SOURCE_LOCK_VERIFICATION.json')
source_errors=[]
for r in source['files']:
    for root in [I/'ra01',E/'FROZEN_RA_ORIGINALS']:
        p=root/r['relative']
        if sha(p)!=r['sha256'] or p.stat().st_size!=r['bytes']:source_errors.append(str(p))
assert len(source['files'])==64 and len(source['programs'])==44 and not source_errors
w=read(E/'SEAL_CAPACITY_STATIC_WITNESS.json')
assert len({r['relative'] for r in w['raw_paths']})==312
assert w['minimum_native_members']==313 and w['admin_max_files']==256 and w['native_max_members']==257
b=read(E/'RESOURCE_BOUND_INDEPENDENT.json')
assert sum(r['hard'] for r in b['parts'])==68498<=100000
assert b['RANGE_completed']==19861 and b['RANGE_using_ledger_hard']<=20000
assert b['ledger_initial']+b['ledger_reaudit_visits']==631
register=read(E/'PLANNED_CASE_REGISTER.json')['rows']
assert len(register)==525 and all(r['status']=='UNRUN_STATIC_ADMISSION' and r['begin'] is None and r['end'] is None and r['exit_status'] is None for r in register)
decision=read(E/'STATIC_DECISION.json')
assert decision['decision']=='BLOCKED_STATIC_ADMISSION'
assert all(decision[k]==0 for k in ['source_edits','WSL_calls','deployment','active_entries','model_imports','dynamic_tests','test_retries','new_visits_consumed'])
assert all(decision[k] is None for k in ['T0','deadline','R','current_boot_id','new_runtime_batch_id','new_dynamic_receipt','new_execution_lock'])

save(E/'ADMINISTRATIVE_EXECUTION_RECORD.json',{
 'scope':'Host file parsing/hash/AST/memory compile/report/archive only; no target module import, no WSL',
 'host_python':{'path':sys.executable,'version':sys.version,'sha256':sha(Path(sys.executable))},
 'commands':[{'argv':[sys.executable,str(E/'AUDIT_STATIC.py')],'result':'exit0; source64/programs44/raw312/hard68498/history9313'},
             {'argv':[sys.executable,str(E/'WRITE_REPORTS.py')],'result':'exit0; reports16/planned525/nav4/target0'},
             {'argv':[sys.executable,str(E/'SEAL_DELIVERY.py')],'result':'See DELIVERY_CHECK.json; generated only after successful checks'}],
 'frozen_reference_command':read(E/'FROZEN_RA_ORIGINALS/inputs/execution_lock.json')['launch_commands_by_scope']['CALIBRATE_S1S9_THEN_F1_F4'],
 'reference_command_executed':False,'runtime_stdout_stderr':'NOT_CREATED_NO_RUNTIME_ENTRY',
 'new_authorization_or_nonce':'NOT_ISSUED','source_or_runtime_mutations':0})

reports=sorted(p.name for p in O.glob('FULLCHAIN_*.md'))
assert len(reports)==16
assert '23|' in (O/'FULLCHAIN_FINAL_DECISION.md').read_text(encoding='utf-8')
link_errors=[];checked=0
future={'FULLCHAIN_MANIFEST.json','FULLCHAIN_EVIDENCE.zip','FULLCHAIN_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
for p in O.rglob('*.md'):
    # Historical copied prose may contain original-relative links; preserve it verbatim.
    if p.is_relative_to(E/'HISTORICAL_REFERENCES') or p.is_relative_to(E/'NAV_ORIGINALS'):continue
    s=p.read_text(encoding='utf-8-sig')
    assert '不是' not in s
    for target in re.findall(r'\]\(([^)]+)\)',s):
        if target.startswith(('http:','https:','#')):continue
        if target in future:checked+=1;continue
        target=target.split('#')[0].strip('<>')
        checked+=1
        if not (p.parent/target).exists():link_errors.append({'file':str(p),'target':target})
assert not link_errors,link_errors
json_count=0
for p in O.rglob('*.json'):read(p);json_count+=1

exclude={'FULLCHAIN_MANIFEST.json','FULLCHAIN_EVIDENCE.zip','FULLCHAIN_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
rows=[{'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in exclude]
manifest={'schema':'FULLCHAIN-STATIC-DELIVERY/1','decision':'BLOCKED_STATIC_ADMISSION',
 'scope':'Local research archive only; native/admin runtime seals are NOT_APPLICABLE',
 'excluded':sorted(exclude),'files':rows,'utc':datetime.now(timezone.utc).isoformat()}
save(O/'FULLCHAIN_MANIFEST.json',manifest)
zpath=O/'FULLCHAIN_EVIDENCE.zip'
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(O/row['relative'],row['relative'])
    z.write(O/'FULLCHAIN_MANIFEST.json','FULLCHAIN_MANIFEST.json')
stream_errors=[]
with zipfile.ZipFile(zpath) as z:
    assert len(z.namelist())==len(rows)+1==len(set(z.namelist()))
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['relative'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:stream_errors.append(row['relative'])
        assert sha(O/row['relative'])==row['sha256']
assert not stream_errors
zh=sha(zpath)
with (O/'FULLCHAIN_EVIDENCE.zip.sha256').open('x',encoding='ascii') as f:f.write(zh+'  FULLCHAIN_EVIDENCE.zip\n')
receipt={
 'schema':'FULLCHAIN-DELIVERY-CHECK/1','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY',
 'overall':'BLOCKED_STATIC_ADMISSION','reports':len(reports),'final_acceptance_answers':23,
 'source_files':64,'programs_checked':44,'source_errors':source_errors,'history_files':len(baseline),'history_mismatches':history_errors,
 'navigation_original_suffixes_preserved':4,'mispath_files':47,'mispath_mismatches':mis_errors,
 'raw_static_witness_files':312,'admin_cap':256,'native_minimum_members':313,'native_reader_cap':257,
 'calibration_hard':68498,'calibration_soft':100000,'range_bound':19861,'planned_unrun_rows':len(register),
 'WSL_calls':0,'active_entries':0,'source_edits':0,'test_retries':0,'target_imports':0,'new_budget':False,
 'T0':None,'deadline':None,'R':None,'new_runtime_batch_id':None,'RESOURCE_GATE_PASS':'NOT_OBTAINED',
 'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'native_seal':'NOT_APPLICABLE_NO_RUNTIME','automatic_admin_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED',
 'json_parsed':json_count,'links_checked':checked,'link_errors':link_errors,
 'manifest_rows':len(rows),'zip_entries':len(rows)+1,'zip_stream_errors':stream_errors,
 'manifest_sha256':sha(O/'FULLCHAIN_MANIFEST.json'),'ZIP_sha256':zh,'ZIP_bytes':zpath.stat().st_size,
 'self_excluded_from_manifest_and_zip':True,'utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-START}
save(E/'DELIVERY_CHECK.json',receipt)
print(json.dumps({k:receipt[k] for k in ['overall','reports','history_files','manifest_rows','zip_entries','ZIP_sha256','ZIP_bytes']},ensure_ascii=False))
