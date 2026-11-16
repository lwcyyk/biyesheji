"""Same-agent second arithmetic route and research-artifact checks only.

No runtime imports, DCL simulations, failure tests or native checker invocation.
"""
from AUDIT_INPUTS import ROOT, PREV, BOUND, OUT, E, RUNTIME, save, read, sha
import json
import re
from pathlib import Path

def compact(x):return len(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def pretty(x):return len(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2).encode())
stamp={'boottime':0,'utc_ns':0,'boot_id':'b'*36}
ident={'pid':0,'start_ticks':0,'boot_id':'b'*36}
window={'T0':0,'deadline':0,'stop_at':0}
data=read(E/'CLOSE_SCHEMA_BYTE_ALGEBRA.json')
ref={}
ref['ABORTING']=compact({'phase':'ABORTING','first_failure_sha256':'a'*64,'sample':stamp})+43
ref['external_closing']=compact({'actor':ident,'batch_id':'batch14','sample':stamp})+9+19+43
state={'status':'AWAIT_EXPECTED_RESUME','boot_id':'b'*36,**window,'launcher_identity':ident,'resume_count':1,
 'expected_launcher_exit':None,'execution_mode':'MR_RECOVERY_DIAGNOSTIC_ONLY','coordinator_identity':ident,'mr_stop_required':False}
w={'schema':'ROOT-IPC-WAITPID/1','child':ident,'coordinator':ident,'raw_wait_status':0,'exit_code':0,'state':state,'sample':stamp}
ref['waitpid_normal']=pretty(w)+4*(9+19)+4*24+19+2*10
f={'schema':'ROOT-IPC-WAITPID/1','child':ident,'coordinator':ident,'raw_wait_status':0,'exit_code':0,'sample':stamp,'reason':'COORDINATOR_EXCEPTION'}
ref['waitpid_fallback']=pretty(f)+2*(9+19)+43+2*10
for k,v in ref.items():assert v==data[k]['constant_bytes'],(k,v,data[k])
marker={'reason':'MR_CRITICAL:C09_PENDING_ALLOWANCE_EXHAUSTED',**stamp}
assert pretty(marker)+43==data['quota_marker_fixed43']==189
assert compact({'sha256':'a'*64,'bytes':0})+19==106
assert compact({'status':'UNKNOWN','error':''})-2==29
assert compact({n:None for n in ('visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl')})-3*4==69
assert len(json.dumps('\U0001f600'*2048).encode())==24578
counts=read(E/'CLOSE_COUNT_DERIVATION.json')
assert counts['core_production_attempts']['at_A16_S23_W2_H0']==7*16+2*23+2==160
assert counts['stable_core_path_upper']['value']==5+46+1+2==54
assert read(E/'MR_CLOSE_ORACLE_COMPATIBILITY.json')['at502_total']==130912
assert read(E/'MR_CLOSE_ORACLE_COMPATIBILITY.json')['at503_coarse_total']==131136
z=read(E/'MANIFEST_ZIP_BOUND_ARITHMETIC.json')
assert z['conditional_native_manifest_upper']==247+4449*119+4450*(1534+18)+43==7436121
assert z['ZIP32_headers_at4451']==22+4451*(92+2*1535)==14074084
assert z['at_accepted_uncompressed_U32MiB_ZIP_STORED_upper']==33554432+14074084==47628516
assert z['at_accepted_U32MiB_deflate_conditional_upper']==33554432+(33554432>>12)+(33554432>>14)+(33554432>>25)+13*4451+14074084==47696620
assert z['generator_R_raw_upper'] is None
binding=read(E/'PROPOSAL_BINDINGS.json')
for k in ('capacity','close','MR_original_rule','PENDING_original_v2'):
    r=binding[k];assert sha(r['path'])==r['sha256']
for name in ('CAPACITY_REVIEW_DRAFT.json','CLOSE_RESERVE_REVIEW_DRAFT.json'):
    c=read(OUT/'proposals'/name)
    for flag in ('user_approved','effective','runtime_enabled'):assert c[flag] is False
req=['CLOSE_RECORD_PRODUCER_AUDIT.md','CLOSE_RESERVE_BOUND_PROOF.md','QUOTA_EXHAUSTION_COUNTEREXAMPLES.md',
 'C09_TOTAL_LOG_BOUND.md','PERSISTENCE_FAILURE_BOUNDARY.md','FULL_EVIDENCE_BYTE_CLOSURE.md','ARCHIVE_WORK_AND_MEMORY_BOUND.md',
 'CAPACITY_CONTRACT_APPROVAL_DRAFT.md','MR_CROSS_INSTANCE_APPROVAL_STATUS.md','GENERAL_BASELINE_AND_SEPARATION.md',
 'UNRESOLVED_BOUND_CHECKLIST.md','NEXT_STAGE_AUTHORIZATION_REQUEST.md','FINAL_DECISION.md']
assert all((OUT/n).is_file() for n in req)
answers=read(E/'FINAL_GATE_DECISIONS.json');assert [a['number'] for a in answers['final_answers']]==list(range(1,21))
assert len(answers['gates'])==7
rows=read(E/'CLOSE_PRODUCER_MATRIX.json')['rows'];assert len(rows)==36
required_fields=['producer','process','source_site','trigger','phase','maximum_count','maximum_encoded_bytes','persistence','quota_domain','required_for_close','after_closed','failure_behavior']
assert all(all(k in r for k in required_fields) for r in rows)
links=[];bad=[]
for p in OUT.glob('*.md'):
    t=p.read_text(encoding='utf-8');assert '不是' not in t,p.name
    for target in re.findall(r'\]\(([^)]+)\)',t):
        q=re.sub(r':\d+$','',target.strip('<>'))
        links.append({'from':p.name,'target':target})
        if not Path(q).exists() and q!=str(E/'DELIVERY_CHECK.json').replace('\\','/'):
            bad.append({'from':p.name,'target':q})
assert not bad,bad
save('SECOND_ARITHMETIC_REVIEW.json',{
 'provenance':'same active agent, reference JSON skeleton-delta calculations vs recursive grammar expression; no independent native oracle claim',
 'status':'PASS_ADMINISTRATIVE_RESEARCH_CHECKS_ONLY','reference_bounds':ref,'marker':189,
 'core_attempt_bound_H0':160,'core_paths_no_staging':54,'manifest_conditional_upper':7436121,
 'required_reports':len(req),'final_answers':20,'producer_families':len(rows),'links_checked':len(links),'link_errors':bad,
 'retained_caveats':['current runtime has no effective quota','160/54 are local scoped counts, not complete closing reserve',
  'R/T/E/V/terminal/admin remain unresolved','502 is a derived compatibility threshold, not a selected guard',
  'fixed-source vs extended API repeated-close family separated','interface stderr family native attainability unverified',
  'stat ctime ns uses29 character conditional ABI bound','complete closure unknown; package/check success does not grant runtime PASS'],
 'target_imports':0,'DCL_dynamic_tests':0,'mechanism_implementation':0})
print({'review':'PASS_RESEARCH_ONLY','reports':len(req),'answers':20,'links':len(links),'producer_families':36})
