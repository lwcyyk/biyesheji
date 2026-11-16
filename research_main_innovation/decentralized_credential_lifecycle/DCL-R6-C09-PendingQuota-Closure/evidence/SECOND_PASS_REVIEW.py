"""Same-agent host second pass: independent arithmetic route, not a native oracle."""
from RESEARCH_AUDIT import ROOT, OLD, OUT, E, RUNTIME, read, write, sha, row
import ast
import copy
import json
import re
from pathlib import Path

def bounded(x,path=()):
    # JSON grammar counted recursively rather than modifying a serialized template.
    if isinstance(x,dict):
        return 2+max(0,len(x)-1)+sum(len(json.dumps(k))+1+bounded(v,path+(k,)) for k,v in x.items())
    if type(x)is bool:return 5
    if x is None:return 4
    if isinstance(x,str):return len(json.dumps(x,ensure_ascii=True).encode())
    k=path[-1]
    if k in ('T0','deadline','stop_at','boottime','now','expires'):return 25
    if k in ('start_ticks','utc_ns','prepay_journal_bytes'):return 20
    if k=='pid':return 10
    if k=='witness':return 11
    return len(str(x))

m=read(E/'RECORD_BYTE_ALGEBRA.json');q=read(OUT/'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json')
c=copy.deepcopy(m['original_templates']['terminal'])
class_size=bounded(c)+1
state_size=bounded(m['original_templates']['transition'])+1
ack_size=bounded(m['original_templates']['ack'])+1
cursor_size=bounded(q['cursor_schema_width_example'])+1
failure=read(E/'QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json')['failure_schema']
failure_size=bounded(failure)+1
assert (class_size,state_size,ack_size,cursor_size,failure_size)==(1318,948,1028,1198,334)
main=sum((256*1322,6*state_size,ack_size));assert main==345148
retained=main+3*cursor_size+2*failure_size+4*189;assert retained==350166
updates=2+(256+7)+256+1;assert updates==522
writes=main+updates*cursor_size+failure_size+2*189;assert writes==971216
fsync=263+2*updates+2+1+6;assert fsync==1316
assert q['main_limits']['main_rows']==q['main_limits']['attempts']+q['main_limits']['state_events']+q['main_limits']['ACK']==263
assert q['user_approved']is False and q['runtime_enabled']is False and q['actual_instance']is None

links=[];errors=[]
for p in sorted(OUT.glob('*.md')):
    text=p.read_text(encoding='utf-8')
    assert '不是' not in text
    assert 'PROPOSED_NOT_EFFECTIVE' in text
    for target in re.findall(r'\]\(([^)]+)\)',text):
        target=target.strip('<>')
        f=re.sub(r':\d+$','',target)
        if not Path(f).exists() and not f.endswith('/evidence/DELIVERY_CHECK.json'):
            errors.append({'report':p.name,'target':target})
        links.append({'report':p.name,'target':target})
assert not errors,errors
required=['C09_PENDING_PATH_AUDIT.md','C09_OBSERVATION_SEMANTICS.md','C09_RECORD_COUNT_BOUND_PROOF.md',
 'C09_RECORD_SIZE_BOUND_PROOF.md','C09_TOTAL_BYTE_BOUND_PROOF.md','C09_OVERFLOW_AND_CLOSE_RESERVE.md',
 'C09_CONCURRENCY_AND_CRASH_ANALYSIS.md','C09_WORK_COMPLEXITY_BOUND.md','FULL_EVIDENCE_BYTE_RECALCULATION.md',
 'CAPACITY_CONTRACT_FINAL_PROPOSAL.md','MR_CROSS_INSTANCE_STATUS.md','CONTRACT_APPROVAL_CHECKLIST.md','NEXT_ACTION.md','FINAL_DECISION.md']
assert all((OUT/n).is_file() for n in required)
write('SECOND_PASS_REVIEW.json',{
 'provenance':'same active agent, host-only second arithmetic route and artifact checks; no independent native checker run',
 'method':'recursive JSON grammar token sum with explicit leaf maxima, compared to skeleton-delta derivation',
 'status':'PASS_RESEARCH_ARTIFACT_CHECKS_ONLY','classification':class_size,'stage':state_size,'ACK':ack_size,'cursor':cursor_size,
 'failure':failure_size,'main':main,'local_retained':retained,'cursor_updates':updates,'write_bytes':writes,'fsync_attempts':fsync,
 'required_reports':len(required),'all_reports':len(list(OUT.glob('*.md'))),'links_checked':len(links),'link_errors':errors,
 'review_findings_retained':['1298 is a specialized missing-witness/ACK-true row bound;1322 governs general schema',
 'full close reserve unresolved; local350166 is not all required closing/seal evidence',
 'work/staging invocation caps require cross-role enforcement especially under EIO with no marker',
 'success terminal latch permits unused VERIFIED/RESUMED stage categories only',
 'cursor1198 assumes compact encoding, not RootIPC indent2',
 'finite invocation counts do not prove wall-time or complete CPython memory/FD limits'],
 'target_imports':0,'runtime_runs':0,'implementation_edits':0})
print({'same_agent_second_pass':'PASS','required_reports':len(required),'links':len(links),'unresolved_close_retained':True})
