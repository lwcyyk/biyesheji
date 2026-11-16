"""Freeze hash DAG and an unapproved planned batch13; no runtime creation."""
from pathlib import Path
import hashlib,json,shutil
E=Path(__file__).resolve().parent;B=E.parent.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=load(W/'inputs/static_manifest.json');l=load(W/'inputs/execution_lock.json')
def totals(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ('full_calibration_hard','full_calibration_hard_visits','calibration_hard_bound','calibration_hard_visit_upper_bound','calibration_total_max_visits','new_calibration_hard') and v==66770:obj[k]=67730
            elif k in ('normal_minimal_hard','normal_minimal_visits_hard') and v==2689:obj[k]=3649
            elif k=='normal_minimal_completed' and v==1907:obj[k]=2588
            else:totals(v)
    elif isinstance(obj,list):
        for v in obj:totals(v)
totals(m);totals(l)
for obj in [m,l]:obj['freeze_revision']=1;obj['export_lock_revision']='TR-r1'
m['profile_approval']='TERMINAL_READ_HOST_STATIC_ONLY; future native deployment/read/seal/test requires independent authorization'
m['input_binding_scope']='batch13-r1; unchanged PT64/PF48 jobs plus TR40; minimal stageA scope only when explicitly approved'
m['terminal_delta']={'jobs':40,'safe':32,'mutants':8,'completed_visits':681,'hard_visits':960,'normal_minimal_completed':2588,
 'normal_minimal_hard':3649,'full_calibration_hard':67730,'readonly_seconds':5,'shared_lock_seconds':2,'shared_attempts':512,
 'journal_bytes':33554432,'journal_line_bytes':32768,'native_archive_entries':257,'native_uncompressed_bytes':33554432,'runtime_grants':False,'dynamic_status':'UNRUN'}
m['source_hashes']={p.name:h(p) for p in sorted((W/'src').glob('*.py'))}
for p in sorted((W/'inputs').iterdir()):
    if p.is_file() and p.name not in ('static_manifest.json','execution_lock.json'):m['bound_inputs']['inputs/'+p.name]=h(p)
for rel,digest in m['bound_inputs'].items():
    key=Path(rel).stem+'_sha256'
    if key in m or key=='terminal_contract_sha256':m[key]=digest
put(W/'inputs/static_manifest.json',m)
for key in list(l):
    if key.endswith('_sha256') and key in m:l[key]=m[key]
l['static_manifest_sha256']=h(W/'inputs/static_manifest.json');l['windows_entry_sha256']=h(W/'host/windows_entry.py')
l['startup_host_finalizer_sha256']=h(W/'host/startup_finalize.py');l['terminal_contract_sha256']=h(W/'inputs/terminal_contract.json')
l['authorization_receipt_required_fields']=list(dict.fromkeys(l['authorization_receipt_required_fields']+['terminal_contract_sha256','TerminalRead_diagnostic_explicitly_approved']))
l['terminal_limits']=m['terminal_delta']
l['terminal_schedule']=['C00','PT64','PF48','TR40','CLOSED and original waitpid/stopper closure','readonly terminal evidence','strict active-check denial after CLOSED','native archive','unchanged automatic administrative finalizer']
l['phase_A_diagnostic']={'scope':'PT_STARTUP_DIAGNOSTIC_ONLY','mode':'NORMAL_START','through':'C00/PT64/PF48/TR40 then close/read/native/admin','models_allowed':False,'automatic_retry':False,'new_time_window':False}
l['phase_A_modes']['NORMAL_START']='Fresh prewindow/runtime/C00/PT64/PF48/TR40; close; terminal readonly review and original native seal; unchanged automatic admin. No MR/C09/full C/S/gates/models'
l['phase_A_identity_rule']='NORMAL_START only for planned batch13-r1. Any second mode or later phase needs a new independent frozen identity/lock/approval'
l['startup_schedule'][-1]='PT64 then PF48 then TR40 then minimal close, readonly/native/admin; no subsequent chain under this request'
index=l['calibration_schedule'].index('PF48');l['calibration_schedule'].insert(index+1,'TR40')
l['phase_B']='REQUEST_ONLY: first resolve required terminal native evidence and current qualification; new identity/digests and explicit authorization required for MR/C09/full chain/models'
put(W/'inputs/execution_lock.json',l)
rows=[{'relative':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(W.rglob('*')) if p.is_file()]
assert len(rows)==59 and sum(r['relative'].endswith('.py') for r in rows)==41
put(E/'STATIC_WORKSPACE_LOCK.json',{'version':'TerminalRead-static-1/r1','host':str(W),'planned_linux':'/var/lib/dcl-r6/tr01',
 'planned_runtime':'/var/lib/dcl-r6/batch13','files':rows,'source_only':True,'new_native_entities_created':False})
template=load(B/'DCL-R6-PTA-PhaseFinalizer-Fix/evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
template.update(batch_id='batch13',static_revision='TerminalRead-static-1/r1',status='TEMPLATE_UNAPPROVED',authorization_text_sha256=None,
 static_manifest_sha256=h(W/'inputs/static_manifest.json'),execution_lock_sha256=h(W/'inputs/execution_lock.json'),
 terminal_contract_sha256=h(W/'inputs/terminal_contract.json'),TerminalRead_diagnostic_explicitly_approved=False)
for key in template:
    if key.endswith('_sha256') and key in m:template[key]=m[key]
for key in template:
    if key.endswith('_explicitly_approved'):template[key]=False
put(E/'PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json',template)
shutil.copytree(W,E/'SOURCE_FINAL_R1')
r=load(E/'STATIC_RESULT.json');r.update(manifest_sha256=h(W/'inputs/static_manifest.json'),execution_lock_sha256=h(W/'inputs/execution_lock.json'))
put(E/'STATIC_RESULT.json',r)
print(json.dumps({'version':r['version'],'files':59,'programs':41,'Linux_files':57,'manifest':r['manifest_sha256'],'execution_lock':r['execution_lock_sha256'],'minimal_completed':2588,'minimal_hard':3649,'full_hard':67730,'receipt_created':False},ensure_ascii=False))
