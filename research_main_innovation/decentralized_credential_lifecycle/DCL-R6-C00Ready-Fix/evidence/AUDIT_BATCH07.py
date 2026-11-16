"""Read only existing batch07 source/logs; no live query and no secret ticket parsing."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

E=Path(__file__).resolve().parent
ROOT=E.parent.parent
B=ROOT/'DCL-R6-batch07'
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch07\native_snapshot')
F=N.parent/'FROZEN_BOOTCONTINUITY'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=(F/'src/boot_continuity.py').read_text(encoding='utf-8');tree=ast.parse(s)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='service_confirmed')
condition=next(n for n in fn.body if isinstance(n,ast.If) and isinstance(n.test,ast.BoolOp) and isinstance(n.test.op,ast.Or))
assert len(condition.test.values)==8
events=[json.loads(x) for x in (B/'evidence/windows_entry.stdout.raw').read_text().splitlines() if x.strip()]
assert len(events)==34
internal=load(B/'evidence/INTERNAL_COMMANDS.json')['commands'];assert len(internal)==15
for r in internal:
    for name in ['stdout','stderr']:assert sha(B/r[name+'_file'])==r[name+'_sha256']
journal=load(B/'evidence/JOURNAL_SUMMARY.json');assert len(journal['records'])==7
cap=load(N/'inputs/root_private/boot/capability.json')
fields=['Uid','Gid','Groups','CapEff','NoNewPrivs','LimitAS','LimitASSoft','ControlGroup']
wants=[[999],[989],[989],0,1,'1073741824','1073741824','/dclr6batch07.slice/dclr6batch07-c00.service']
rows=[]
for i,(name,w,expr) in enumerate(zip(fields,wants,condition.test.values),1):
    rows.append({'check_id':'CR-%02d'%i,'field':name,'source_file':'src/boot_continuity.py',
      'function':'service_confirmed','source_line':expr.lineno,'rejection_expression':ast.get_source_segment(s,expr),
      'expected':w,'observed':None,'read_time':None,'process_identity':None,'state_phase':'UNRECORDED_C00_RECHECK',
      'historical_result':'NOT_SAMPLED','evidence_source':'/proc/MainPID/status' if i<=5 else 'systemd show C00 service',
      'evidence_disposition':'C00_FAILED_FIELD_UNRESOLVED; requested properties/source known, actual failed-time values absent',
      'error':'Aggregate rejection only; later OR terms may not have been evaluated'})
with zipfile.ZipFile(B/'BATCH07_EVIDENCE.zip') as z:
    m=json.loads(z.read('OUTPUT_MANIFEST.json'))
    for r in m['files']:assert hashlib.sha256(z.read(r['archive_path'])).hexdigest()==r['sha256']
    entries=len(z.namelist())
dump('EIGHT_FIELD_HISTORICAL_AUDIT.json',{'schema':'CR-eight-historical/1','fields':rows,
 'overall':'C00_FAILED_FIELD_UNRESOLVED','direct_MATCH':0,'direct_MISMATCH':0,'unrecorded':8,
 'short_circuit':'Original OR could stop at first true mismatch; no per-term evaluation witness',
 'not_in_original_eight':['MainPID','ActiveState','SubState','TasksMax','actual /proc limits','actual /proc cgroup'],
 'source_sha256':sha(F/'src/boot_continuity.py'),'events_verified':34,'inner_stream_pairs_verified':15,
 'journal_verified':7,'batch07_archive_entries_verified':entries,'archive_sha256':sha(B/'BATCH07_EVIDENCE.zip'),
 'sealed_sha256_only':cap['sha256'],'secret_ticket_value_copied':False})
timeline=[]
for r in events:
    timeline.append({'event':r['event'],'sample':r['sample'],'identity':r['identity'],'argv':r.get('argv'),
                     'exit_code':r.get('exit_code'),'source':'batch07 windows_entry.stdout.raw'})
dump('BATCH07_FAILURE_TIMELINE.json',{'schema':'CR-historical-timeline/1','BC_events':timeline,
 'journal_clock':'MONOTONIC microseconds; separate from native BOOTTIME','journal':journal['records'],
 'state':load(N/'inputs/batch_state.json'),'closed':load(N/'inputs/CLOSED.json'),
 'resource_accounting':load(B/'evidence/RESOURCE_ACCOUNTING.json'),
 'causal_assessment':'Readiness gap confirmed in source; race supported, exact cause remains unresolved'})
print(json.dumps({'real_fields':8,'historical_failed_field':'UNRESOLVED','events':34,'inner_streams':15,'journal':7,'archive_entries':entries,'native_calls':0}))
