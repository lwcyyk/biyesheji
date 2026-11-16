"""Explicit reviewed runtime contract and RA32 input construction; no system mutation."""
from pathlib import Path
import copy,json,hashlib
E=Path(__file__).resolve().parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
def load(name):return json.loads((E/name).read_bytes())
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=load('RUNTIME_DISCOVERY.json');p=load('PROVENANCE_AUDIT.json');a=load('ELF_ABI_AUDIT.json');x=load('PLATFORM_EXPORT.json');decision=load('PROVENANCE_DECISION.json')
assert decision['static_baseline_admissible'] and not a['unresolved_needed'] and not a['missing_versions']
components=[]
for row in d['artifacts'][:3]:
    elf=a['three_components'][row['path']];assert elf['sha256']==row['sha256']
    components.append({'artifact_id':Path(row['path']).name,'path':row['path'],'resolved':row['resolved'],'is_symlink':False,
        'sha256':row['sha256'],'bytes':row['bytes'],'mode':row['mode'],'build_id':elf['build_id'],'elf_class':'ELF64','machine':62,
        'package':'libc6','package_version':'2.39-0ubuntu8.12','architecture':'amd64'})
identity={'schema':'RUNTIME-IDENTITY-CONTRACT/1','profile':'GLIBC-UBU24-2.39-8.12/1','source_revision':'RuntimeAdapt-static-1/r1','batch_id':'batch14',
    'components':components,'aliases':x['aliases'],'packages':{'libc6':{'version':'2.39-0ubuntu8.12','architecture':'amd64'},'libc-bin':{'version':'2.39-0ubuntu8.12','architecture':'amd64'}},
    'installed_catalogs':x['catalogs'],'python':{'path':'/usr/bin/python3.12','version':'3.12.3','sha256':a['python']['sha256'],'interpreter':a['python']['interpreter']},
    'provenance':{'classification':decision['classification'],'assumptions':decision['trust_assumptions'],'limitations':decision['limitations'],
        'keyring_sha256':p['keyring']['sha256'],'signed_indices':[{'release_sha256':r['release_sha256'],'index_sha256':r['index_sha256'],'index_bytes':r['index_bytes'],'package_stanzas':r['packages']} for r in p['repositories']]},
    'static_ABI_necessary_conditions':{'ELF_seed_count':a['frozen_ELF_seed_count'],'objects':a['resolved_ELF_objects'],'unresolved_needed':0,'missing_versions':0},
    'read_seconds':5,'loader_overrides_allowed':False,'silent_relock':False,'runtime_authority':'NONE','dynamic_status':'UNRUN',
    'remaining_execution_identity_boundary':'Checks current disk and process maps at explicit points. No filesystem-to-exec atomicity or immunity to privileged replacement after check.'}
put(W/'inputs/runtime_identity_contract.json',identity)
def facts(**kw):
    f=dict(digests=True,paths=True,build_ids=True,packages=True,symbols=True,preload_absent=True,read_ok=True,fresh=True,batch_binding=True,silent_relock=False,purpose='IDENTITY_ONLY',closed=False);f.update(kw);return f
safe=[('new_three_match',facts()),('loader_path',facts()),('coherent_package',facts()),('python_needed',facts()),('package_identity',facts()),
 ('mixed_loader',facts(digests=False)),('single_digest_change',facts(digests=False)),('symlink_change',facts(paths=False)),('package_file_mismatch',facts(packages=False)),
 ('build_id_change',facts(build_ids=False)),('search_path_change',facts(preload_absent=False)),('provenance_missing',facts(packages=False)),('read_failure',facts(read_ok=False)),
 ('post_preflight_replace',facts(fresh=False)),('auto_relock',facts(silent_relock=True)),('missing_digest',facts(digests=False)),('version_only',facts(digests=False)),
 ('cross_batch',facts(batch_binding=False)),('closed_work',facts(purpose='WORK',closed=True)),('missing_symbol',facts(symbols=False)),
 ('active_identity',facts(purpose='WORK')),('admin_after_close',facts(purpose='IDENTITY_ONLY',closed=True)),('current_mapping_match',facts()),('fresh_query_required',facts(fresh=False))]
assert len(safe)==24
jobs=[{'case_id':'RA_SAFE_'+name,'mutant':None,'expected_violation':None,'allowed_violations':[],'frames':[f]} for name,f in safe]
pairs=[('missing_digest_pass','IDENTITY_BYPASS','missing_digest'),('alias_change_pass','IDENTITY_BYPASS','symlink_change'),('package_change_pass','IDENTITY_BYPASS','package_file_mismatch'),
 ('build_id_pass','IDENTITY_BYPASS','build_id_change'),('loader_override_pass','IDENTITY_BYPASS','search_path_change'),('stale_mapping_pass','IDENTITY_BYPASS','post_preflight_replace'),
 ('cross_batch_pass','IDENTITY_BYPASS','cross_batch'),('silent_relock_pass','SILENT_RELOCK','auto_relock')]
by_name=dict(safe)
for mutant,violation,control in pairs:jobs.append({'case_id':'RA_MUTANT_'+mutant,'mutant':mutant,'expected_violation':violation,'allowed_violations':[violation],
    'safe_control':'RA_SAFE_'+control,'frames':[copy.deepcopy(by_name[control])]})
assert len(jobs)==32 and sum(bool(j['mutant']) for j in jobs)==8
put(W/'inputs/runtime_regression_contract.json',{'schema':'RA-REGRESSION/1','version':'RuntimeAdapt-static-1/r1','batch_id':'batch14','origin':'RA-SIMULATION/1',
    'jobs':jobs,'driver_prepay':16,'completed_visits':545,'hard_visits':768,'max_frames':3,'dynamic_status':'UNRUN',
    'scope':'Synthetic identity decision/negative observations; system ELF/files never modified. Actual disk/process checks require new native A2 receipts.'})
print(json.dumps({'identity_components':3,'packages':2,'regression_jobs':32,'mutants':8,'completed':545,'hard':768,'source_runtime_relock':'explicit only; no native activation'},ensure_ascii=False))
