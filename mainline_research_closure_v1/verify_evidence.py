"""Read-only historical audit. Outputs/copies stay under this closure directory.

No native HTTP object is constructed. SQLite is opened only on disposable
copies, so historical WAL/SHM read marks cannot be changed by this audit.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

BASE=Path(r'D:\毕业设计')
REPO=BASE/'auth-lifecycle'
sys.dont_write_bytecode=True
sys.path.insert(0,str(REPO/'src'))
from auth_lifecycle.online_state.evidence_semantics import normalize_material,normalize_query
from auth_lifecycle.online_state.native_http import private_http_records

ROOTS={1:BASE/'mainline_online_state_v1',2:BASE/'mainline_native_casdoor_v1',3:BASE/'mainline_native_reconciliation_v1',
       4:BASE/'mainline_native_unidentified_v1',5:BASE/'mainline_agent_isolation_v1',6:BASE/'mainline_native_isolation_v1'}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))


class Audit:
    def __init__(self,out):
        self.out=Path(out).resolve()
        if not self.out.is_relative_to(Path(__file__).resolve().parent):
            raise ValueError('AUDIT_OUTPUT_MUST_STAY_IN_RESEARCH_CLOSURE_DIRECTORY')
        self.out.mkdir(parents=True,exist_ok=True)
        self.artifacts={};self.checks=[];self.gaps=[];self.normalized=[];self.source_locks=[];self.configs=[]

    def artifact(self,p,expected=None):
        p=Path(p).resolve();key=str(p)
        if not p.is_file():
            row={'path':key,'status':'MISSING','expected_sha256':expected};self.gaps.append(row);self.artifacts[key]=row;return row
        digest=sha(p);row={'path':key,'status':'PRESENT','sha256':digest,'bytes':p.stat().st_size}
        if expected:row.update(expected_sha256=expected,hash_match=digest==expected)
        self.artifacts[key]=row
        if expected and digest!=expected:self.gaps.append({**row,'status':'HASH_MISMATCH'})
        return row

    def load(self,p):self.artifact(p);return read(p)
    def check(self,name,condition,detail=None):
        self.checks.append({'check':name,'pass':bool(condition),'detail':detail})

    def database(self,path):
        path=Path(path);token=hashlib.sha256(str(path).encode()).hexdigest()[:16]
        dest=self.out/'work'/token;dest.mkdir(parents=True,exist_ok=True)
        for suffix in ('','-wal','-shm'):
            src=Path(str(path)+suffix)
            if src.exists():self.artifact(src);shutil.copy2(src,dest/src.name)
        return sqlite3.connect(dest/path.name)

    def budget(self,stage,path):
        with self.database(path) as c:counts=dict(c.execute('SELECT category,COUNT(*) FROM requests GROUP BY category'))
        return {'stage':stage,'path':str(path),'categories':counts,'total':sum(counts.values())}

    def lock(self,path,stage):
        data=self.load(path);files=data.get('files',data.get('source_manifest',[]))
        if not isinstance(files,list):return
        roots=[d for d in ROOTS[stage].glob('source_snapshot*') if d.is_dir()]
        if (ROOTS[stage]/'source_frozen').exists():roots.append(ROOTS[stage]/'source_frozen')
        index={}
        for d in roots:
            for p in d.rglob('*'):
                if p.is_file() and (p.suffix in {'.py','.sql','.ps1'} or p.name=='pyproject.toml'):
                    index.setdefault(sha(p),[]).append(p)
        rows=[]
        for f in files:
            expected=f.get('sha256');original=f.get('relative',f.get('path',''))
            rel=f.get('relative',str(original).replace('\\','/').split('auth-lifecycle/')[-1])
            direct=[d/rel for d in roots if (d/rel).is_file() and sha(d/rel)==expected]
            candidates=direct or index.get(expected,[])
            if candidates:
                chosen=candidates[0];self.artifact(chosen,expected)
                rows.append({'registered_path':original,'archive_path':str(chosen),'sha256':expected,'status':'ARCHIVED_BYTES_MATCH'})
            else:
                p=Path(f.get('path',''))
                if not p.is_absolute():p=REPO/p
                if p.is_file() and sha(p)==expected:
                    self.artifact(p,expected);rows.append({'registered_path':original,'archive_path':str(p),'sha256':expected,'status':'CURRENT_BYTES_MATCH_ONLY'})
                else:
                    rows.append({'registered_path':original,'sha256':expected,'status':'ARCHIVE_UNRESOLVED'})
                    self.gaps.append({'kind':'SOURCE_ARCHIVE_UNRESOLVED','lock':str(path),'registered_path':original,'sha256':expected})
        self.source_locks.append({'path':str(path),'rows':rows,'scope':'matching bytes; provenance and adequacy remain separate'})

    def source_locators(self,stage,case):
        p=ROOTS[stage]
        archives=list(p.glob('source_snapshot*'))+[p/'source_frozen']
        rel='scripts/measure_native_casdoor.py'
        return [{'path':str(a/rel),'sha256':sha(a/rel)} for a in archives if (a/rel).is_file()]

    def normalize_case(self,stage,case,transport):
        case=Path(case);transport=Path(transport)
        try:records=private_http_records(transport);decrypt_status='DECRYPTED'
        except Exception as error:records=[];decrypt_status='UNAVAILABLE_'+type(error).__name__;self.gaps.append({'kind':'AUDIT_DECRYPTION_UNAVAILABLE','path':str(transport),'exception':type(error).__name__})
        with self.database(transport/('http_budget/native_budget.db' if (transport/'http_budget/native_budget.db').exists() else 'native_budget.db')) as c:
            dbrows={x[0]:{'category':x[1],'operation':x[2],'actor':x[3]} for x in c.execute('SELECT seq,category,operation,actor FROM requests')}
        profile=self.load(case/'secure/native_profile.json');actor=profile['actor']['name']
        policy=self.load(transport/'BUDGET_AND_AUTHORIZATION.json')
        label=case.parent.name if case.name=='trusted' else case.name
        rules={'actor_whitelisted':actor in policy['account_names'],
               'batch_matches':Path(profile['batch']).resolve()==transport.resolve(),
               'client_matches':profile['client_id']==policy.get('client_id','l1-client-0'),
               'provider_version':profile['version']=='4.25.0'}
        if stage==3:rules['identifier_journal_enabled']=profile.get('identifier_journal') is True
        if stage in {4,6}:
            expected=stage==6 and label=='M6-01'
            rules['inbox_mode_matches']=profile.get('durable_inbox') is expected
            rules['identifier_mode_matches']=profile.get('identifier_journal') is expected
        if stage==2 and label in {'M2-02','M2-03'}:rules['loss_boundary_inbox_mode']=profile.get('durable_inbox') is (label=='M2-02')
        self.configs.append({'stage':'M'+str(stage),'case':label,'profile':str(case/'secure/native_profile.json'),
            'profile_sha256':sha(case/'secure/native_profile.json'),'rules':rules,'pass':all(rules.values())})
        for source in sorted((case/'scorer').glob('*_native.json')):
            data=self.load(source)
            for i,row in enumerate(data.get('rows',[])):
                proof={'source_file':str(source),'source_sha256':sha(source),'json_pointer':'/rows/'+str(i),
                       'frozen_producers':self.source_locators(stage,case),'audit_decryption':decrypt_status}
                view=normalize_material(row,proof)
                # Corroborate old RT observations against the actual sealed HTTP
                # response; never export its token/form values.
                matches=[];token=None
                if row.get('userinfo_native_sequence') and row.get('refresh_ref'):
                    token=None
                    for record in records:
                        body=record['response'].get('body')
                        if record.get('actor')==actor and isinstance(body,dict) and body.get('refresh_token'):
                            ref=hashlib.sha256(json.dumps(body['refresh_token'],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
                            if ref==row['refresh_ref']:token=body['refresh_token']
                    if token:
                        for record in records:
                            form=record.get('form') or {};seq=record['sequence'];kind=dbrows.get(seq,{})
                            if (record.get('actor')==actor and seq>row['userinfo_native_sequence'] and kind.get('category') in {'measurement','cleanup'}
                                    and form.get('token')==token and form.get('token_type_hint')=='refresh_token'):
                                matches.append(record)
                if matches and view['refresh_token_introspection']['performed']:
                    found=min(matches,key=lambda x:x['sequence'])
                    active=found['response']['body'].get('active') if isinstance(found['response'].get('body'),dict) else None
                    view['refresh_token_introspection'].update(http=found['response']['http'],native_sequence=found['sequence'],
                        raw_response_active=active if type(active) is bool else None,
                        corroborated=(found['response']['http']==200 and active is view['refresh_token_introspection']['active']))
                    view['provenance']['native_http_ref']=str(transport/'secure/http'/(str(found['sequence'])+'.aes'))
                if token:
                    actual=[record for record in records if record.get('actor')==actor and record['sequence']>row.get('userinfo_native_sequence',10**12)
                        and dbrows.get(record['sequence'],{}).get('category')=='measurement'
                        and record.get('operation')=='refresh' and (record.get('form') or {}).get('refresh_token')==token]
                    if actual and view['refresh_attempt']['performed']:
                        found=min(actual,key=lambda x:x['sequence']);body=found['response'].get('body')
                        new_material=any(body.get(k) for k in ('access_token','refresh_token','id_token')) if isinstance(body,dict) else None
                        view['refresh_attempt'].update(http=found['response']['http'],native_sequence=found['sequence'],
                            new_material_in_response=new_material,response_error_present=bool(body.get('error')) if isinstance(body,dict) else None,
                            transport_error_type=found.get('error_type'))
                        view['provenance']['refresh_http_ref']=str(transport/'secure/http'/(str(found['sequence'])+'.aes'))
                self.normalized.append({'stage':'M'+str(stage),'case':str(case),'view':view})
        receipt=case/'runner/closure_receipt.json'
        if receipt.exists():
            value=self.load(receipt)
            if value.get('evidence_origin')=='AUTHORIZED_SCOPE_ENUMERATION':
                q=value['evidence']['packet']['query']
                self.normalized.append({'stage':'M'+str(stage),'case':str(case),'view':normalize_query(q,{'source_file':str(receipt),'source_sha256':sha(receipt),'json_pointer':'/evidence/packet/query'})})


def run(output,claims=None):
    a=Audit(output);stages=[]
    p=ROOTS[1];agg=a.load(p/'M1_AGGREGATE.json')
    first=a.load(p/'m1_batch01/results.json')['records'];continued=a.load(p/'m1_batch01_continuation/results.json')['records']
    slots={(x['scenario'],x['repeat']):x for x in first};replacement_ok=True
    for record in continued:
        key=(record['scenario'],record['repeat'])
        replacement_ok &= key in slots and slots[key]['status']=='NOT_RUN'
        slots[key]=record
    records=list(slots.values());a.check('M1_continuation_only_unrun_slots',replacement_ok)
    counts=dict(Counter(x['status'] for x in records));a.check('M1_21_slots_20_PASS_1_ABORTED',len(records)==21 and counts=={'ABORTED':1,'PASS':20},counts)
    stages.append({'stage':'M1','denominator':21,'observed_counts':counts,'basis':'initial abort retained, only unrun slots continued','native_HTTP':0})
    for f in (p/'ENVIRONMENT_LOCK.json',p/'ENVIRONMENT_LOCK_v2.json',p/'m1_batch01/batch_lock.json',p/'m1_batch01_continuation/batch_lock.json'):a.artifact(f)
    p=ROOTS[2];cost=a.load(p/'COST_AND_RESULTS.json');raw=a.load(p/'raw/batch01/RESULTS.json');cont=a.load(p/'raw/continuation01/RESULTS.json');correction=a.load(p/'review/SCORER_CORRECTION.json')
    rawmap={x['scenario']:x['status'] for x in raw['records']};rawmap[cont['scenario']]=cont['status']
    a.check('M2_four_samples_original_alert',len(rawmap)==4 and rawmap['M2-03']=='SAFETY_FAILURE' and list(rawmap.values()).count('PASS')==3,rawmap)
    a.check('M2_alert_reviewed_without_resampling',correction['original_case']=='M2-03' and correction['original_status']=='SAFETY_FAILURE' and correction['corrected_scoring']=='PASS' and cost['resampled_trajectories']==0)
    oldcase=p/'raw/batch01/M2-03'
    for row in correction.get('original_case_file_hashes',[]):a.artifact(oldcase/row['path'],row['sha256'])
    supplement=a.load(p/'supplement/RESULT.json')
    stages.append({'stage':'M2','denominator':4,'original_counts':dict(Counter(rawmap.values())),'reviewed_counts':cost['reviewed_scores'],
                   'raw_M2_04_outage_admission':'missing in original trace; separate local supplement, no native resampling','supplement_path':str(p/'supplement/RESULT.json'),'native_HTTP':cost['HTTP_total']})
    a.budget('M2',p/'raw/batch01/native_budget.db')
    for stage in (3,4):
        p=ROOTS[stage];r=a.load(p/'raw/batch01/RESULTS.json');cost=a.load(p/'COST_AND_RESULTS.json')
        a.check('M'+str(stage)+'_two_native_samples',len(r['records'])==2 and all(x['status']=='PASS_CLOSED' for x in r['records']))
        bd=a.budget('M'+str(stage),p/'raw/batch01/native_budget.db')
        expected=cost.get('native_HTTP_total',cost.get('HTTP_total'))
        a.check('M'+str(stage)+'_HTTP_ledger',bd['total']==expected,bd)
        if stage==4:a.artifact(p/'cleanup_repair_RESULT.json');a.artifact(p/'SOURCE_LOCK_cleanup_fix.json')
        stages.append({'stage':'M'+str(stage),'denominator':2,'counts':r['counts'],'native_HTTP':bd['total'],
                       'premise':'identifier journal and exact point read' if stage==3 else 'additional dedicated-org read authorization; cleanup repair separately retained'})
    p=ROOTS[5];r=a.load(p/'batch01/INDEPENDENT_SCORES.json');agg=a.load(p/'M5_AGGREGATE.json')
    a.check('M5_twelve_synthetic_scenarios',len(r['results'])==12 and all(x['status']=='PASS' for x in r['results']) and agg['native_requests']==0)
    stages.append({'stage':'M5','denominator':12,'counts':r['counts'],'native_HTTP':0,'provider':'synthetic'})
    p=ROOTS[6];r=a.load(p/'batch01/RESULTS.json');cost=a.load(p/'COST_AND_RESULTS.json');bd=a.budget('M6',p/'batch01/transport/http_budget/native_budget.db')
    a.check('M6_two_samples_and_84_HTTP',r['planned']==2 and len(r['records'])==2 and r['HTTP_total']==bd['total']==84)
    a.check('M6_each_43_checks',all(len(a.load(p/('batch01/'+x+'/scorer_private/result.json'))['checks'])==43 for x in ('M6-01','M6-02')))
    a.artifact(p/'AUTHORIZATION_ADDENDUM.json');a.artifact(p/'EXISTING_DEPENDENCY_PERMISSIONS.json');a.artifact(p/'FINAL_ACL_REVIEW.json')
    stages.append({'stage':'M6','denominator':2,'counts':r['counts'],'native_HTTP':84,'check_items_per_case':43,
                   'checks_are_not_native_samples':True,'initial_permission_gap':'extra researcher ACL authorization, retained before/after','shared_public_key_ACL_transition':'explicit planned R2 read grant'})
    # Immutable snapshots and locks are checked independently of current source.
    for stage,p in ROOTS.items():
        for name in ('SOURCE_LOCK.json','SOURCE_LOCK_v2.json'):
            if (p/name).exists():a.lock(p/name,stage)
        if stage==1:
            for name in ('ENVIRONMENT_LOCK.json','ENVIRONMENT_LOCK_v2.json'):a.lock(p/name,stage)
    for stage in (2,3,4):
        p=ROOTS[stage];transport=p/'raw/batch01'
        caseparents=[transport]+([p/'raw/continuation01'] if stage==2 else [])
        for parent in caseparents:
            for case in sorted(parent.glob('M'+str(stage)+'-*')):
                if case.is_dir() and (case/'secure/native_profile.json').exists():a.normalize_case(stage,case,transport)
    for case in (ROOTS[6]/'batch01').glob('M6-*'):
        if case.is_dir():a.normalize_case(6,case/'trusted',ROOTS[6]/'batch01/transport')
    material_views=[x['view'] for x in a.normalized if x['view']['schema']=='native-material-observation/2']
    a.check('legacy_RT_introspection_not_promoted_to_refresh',all(not v['refresh_attempt']['performed'] for v in material_views if v['refresh_token_introspection']['performed']))
    a.check('native_count_not_promoted_to_page_count',all(x['view']['native_reported_page_count'] is None for x in a.normalized if x['view']['schema']=='native-enumeration-observation/2'))
    a.check('profile_and_budget_configuration_correspondence',all(x['pass'] for x in a.configs),a.configs)
    # Research evidence is not pooled with native trials.
    empirical=REPO/'results/experiments/pilot02/runs.jsonl';survey=REPO/'results/experiments/survey04/observations.json'
    a.artifact(empirical);lines=[json.loads(x) for x in empirical.read_text().splitlines()]
    a.check('legacy_576_calibration_runs',len(lines)==576)
    obs=a.load(survey);observations=obs if isinstance(obs,list) else obs.get('rows',[])
    a.check('legacy_52_semantic_observations',len(observations)==52)
    r3=a.load(BASE/'research_recipe_r3/results/expanded01/summary.json')
    a.check('R3_registered_finite_counts',r3['exhaustive']['budget_queries']==268310 and r3['spectrum']['spectrum_instances']==224 and r3['spectrum']['full_lower_enumeration_instances']==36)
    missing=BASE/'硕士研究深化增补_AI数字主体与密码管理器_v2.15_研究空白与创新融合版.docx';a.artifact(missing)
    if claims:
        ledger=a.load(claims)
        for claim in ledger['claims']:
            for ref in claim['evidence']:
                row=a.artifact(ref['path'],ref.get('sha256'))
                if row['status']=='MISSING':a.gaps.append({'kind':'CLAIM_REFERENCE_MISSING','claim_id':claim['id'],'path':ref['path']})
        a.check('claim_category_and_scope_fields',all(all(k in c for k in ('id','text','category','quantifier_and_scope','premises','counterexamples','evidence_level','paper_wording','missing_key_evidence')) for c in ledger['claims']))
    dependency=Path(output).resolve().parent/'sources/beego_v2.3.8_paginator.go'
    if dependency.exists():a.artifact(dependency)
    # Original inputs are rehashed after all reads, not opened through SQLite.
    unchanged=[]
    for row in list(a.artifacts.values()):
        if row.get('sha256'):
            ok=Path(row['path']).is_file() and sha(row['path'])==row['sha256'];unchanged.append(ok)
            if not ok:a.gaps.append({'kind':'INPUT_CHANGED_DURING_AUDIT','path':row['path']})
    a.check('historical_inputs_unchanged_during_audit',all(unchanged))
    findings={'scope':'read-only artifact and registered-claim audit; no conclusion-completeness certificate',
        'verifier_sha256':sha(Path(__file__)),
        'native_requests_this_round':0,'checks':a.checks,'stages':stages,'gaps':a.gaps,
        'source_locks':a.source_locks,'configuration_correspondence':a.configs,'artifacts':list(a.artifacts.values()),'normalized_record_count':len(a.normalized),
        'code_correctness':'regression tracked separately','evidence_integrity':'GAPS_VISIBLE' if a.gaps else 'REGISTERED_CHECKS_PASS',
        'claim_sufficiency':'manual conditional judgment; not implied by checksum success'}
    for name,value in [('VALIDATION_RESULT.json',findings),('NORMALIZED_EVIDENCE.json',{'schema':'closure-evidence-views/1','records':a.normalized})]:
        (a.out/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'checks':len(a.checks),'failed_checks':[c['check'] for c in a.checks if not c['pass']],
                      'visible_gaps':len(a.gaps),'normalized':len(a.normalized),'native_requests':0}))
    return findings


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--claims');args=p.parse_args();run(args.out,args.claims)
