"""Independent M6 rules: read-only authority and scorer-only audit decryption."""
import argparse
import base64
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.online_state.native_http import private_http_records, budget_path


def load(path):return json.loads(Path(path).read_text())
def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()


def score(root, synthetic=False):
    root=Path(root);trusted=root/"trusted";out=load(trusted/"runner/outcome.json")
    checks=[];accesses=[]
    def check(name,condition,category="security"):
        checks.append({"name":name,"pass":bool(condition),"category":category})
    def res(value):return value.get("result",{})
    def denied(value):return value.get("reached") is True and res(value).get("status")=="REJECTED"
    def success(value):return value.get("reached") is True and res(value).get("status")=="RESULT_AVAILABLE"
    if out["status"]!="OBSERVED":
        result={"status":out["status"],"checks":[],"scenario":out["scenario"],"reason":out.get("safe_reason")}
        (root/"scorer_private/result.json").write_text(json.dumps(result));return result
    profile=load(trusted/"secure/native_profile.json");batch=Path(profile["batch"])
    policy=load(batch/"BUDGET_AND_AUTHORIZATION.json");lock=load(root/"ENVIRONMENT_LOCK.json")
    setup=load(root/"SETUP_CONTROLS.json")["identities"]
    db=trusted/"authority/authority.db";key=trusted/"secure/authority.key"
    accesses += [{"path":str(db),"mode":"sqlite_read_only"},{"path":str(key),"mode":"scorer_authority_decryption"},
                 {"path":str(batch/"scorer_secret/http-audit-private.pem"),"mode":"scorer_private_audit_decryption"}]
    with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as c:
        version,raw=c.execute('SELECT version,ciphertext FROM authority_state WHERE id=1').fetchone()
        events=[{"version":v,"operation":op,**json.loads(p)} for v,op,p in c.execute('SELECT version,operation,projection FROM authority_events ORDER BY version')]
    state=json.loads(AESGCM(key.read_bytes()).decrypt(raw[:12],raw[12:],b'auth-lifecycle/online-state/schema-1'))
    private=private_http_records(batch)
    own=[r for r in private if r['actor']==profile['actor']['name']]
    check('audit_private_decryption_positive',len(own)>0,'availability')
    check('audit_one_way_configuration',policy['audit_mode']=='sealed_to_scorer' and not (batch/'secure/http.key').exists())
    check('native_mode_matches_batch',synthetic==(policy.get('execution_domain')=='SYNTHETIC_ZERO_NATIVE_PREFLIGHT'))
    for n in ('A','B','R_probe'):
        token=setup[n]['token'];role='R' if n=='R_probe' else n
        check(role+'_actual_primary_token',token['token_type']==1 and token['elevated']==0 and token['user']==lock['owner_sid']
              and token['integrity']==('S-1-16-8192' if role=='R' else 'S-1-16-4096')
              and lock['restricting_sids'][role] in {r['sid'] for r in token['restricting_sids']} and bool(token.get('default_dacl')))
        check(role+'_own_workspace_control',setup[n]['own_read_write'],'availability')
    check('object_dacls_frozen',all(p.get('object_sddl') for p in lock['processes']))
    service_metadata=[load(p) for p in (trusted/'control').glob('*_isolation.json')]
    check('all_service_boots_use_R_token',len(service_metadata)>=3 and all(
        m['token']['integrity']=='S-1-16-8192' and m['token']['token_type']==1 and m['token'].get('default_dacl')
        and lock['restricting_sids']['R'] in {s['sid'] for s in m['token']['restricting_sids']} for m in service_metadata))
    permitted_environment={'SYSTEMROOT','TEMP','TMP','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','PYTHONPATH'}
    check('service_environment_allowlist',all({k.upper() for k in m['environment']}<=permitted_environment for m in service_metadata))
    p=out['permission_precheck']
    # The synthetic preflight may expose a legacy ACL gap; it records that gap
    # separately and cannot authorize a real batch until the gate passes.
    check('existing_and_new_private_targets_exist',all(p['targets_exist'].values()),'evidence')
    check('credential_permission_gate',p['gate_pass'],'environment')
    check('R_read_positive',all(rows and rows[0].get('allowed') for rows in p['R_positive'].values()),'availability')
    check('A_issue_and_B_issue',success(out['A_issue']) and success(out['B_issue']),'availability')
    check('B_final_resource_positive',success(out['B_after']),'availability')
    check('old_A_local_release_denied',out['ack']['status']=='LOCAL_REVOKE_COMMITTED' and denied(out['A_after_ack']))
    check('commit_sequence',[e['version'] for e in events]==list(range(1,version+1)))
    revoked=set();releases={};safe=True
    for e in events:
        r=e['result']
        if e['operation']=='revoke' and r['status']=='LOCAL_REVOKE_COMMITTED':revoked.add(r['grant_id'])
        if e['operation']=='release' and r.get('send'):
            req=next(x for x in e['state']['requests'] if x['rid']==r['rid'])
            safe &= req['origin']['grant_id'] not in revoked and req['release_version']==e['version']
            releases[req['attempt_id']]=req
    check('no_release_after_revoke_commit',safe)
    for grant in state['grants'].values():
        reqs=[r for r in state['requests'].values() if r['origin']['grant_id']==grant['grant_id']]
        check('budget_'+grant['task'],sum(r['attempt_id'] is not None for r in reqs)==grant['spent'] and
              sum(r['phase']=='QUEUED' for r in reqs)==grant['reserved'] and grant['spent']+grant['reserved']<=grant['limit'])
        check('source_'+grant['task'],all(all(r['origin'][k]==grant[k] for k in r['origin']) and
              hashlib.sha256(canonical({'caller':r['origin']['caller'],'request':r['request']})).hexdigest()==r['digest'] for r in reqs))
    with sqlite3.connect('file:'+str(budget_path(batch,policy))+'?mode=ro',uri=True) as c:
        sends=[dict(zip(('seq','operation','attempt_id','rid','digest'),row)) for row in c.execute(
            "SELECT seq,operation,attempt_id,rid,request_digest FROM requests WHERE category='method' AND actor=? AND operation IN ('issue','refresh')",(profile['actor']['name'],))]
    check('each_send_has_original_durable_release',all(s['attempt_id'] in releases and s['rid']==releases[s['attempt_id']]['rid'] and s['digest']==releases[s['attempt_id']]['digest'] for s in sends))
    check('no_creation_auto_retry',all(n==1 for n in Counter(s['attempt_id'] for s in sends).values()))
    inbox=trusted/'provider/native_inbox.jsonl';journal=trusted/'provider/identifier_receipts.jsonl'
    if out['scenario']=='M6-01':
        check('actual_parse_error_is_safe_rejection',denied(out['parse_error']))
        for task in ('A','B'):
            status=res(out[task+'_status'])
            check(task+'_status_scope',status.get('status')=='RECOVERED' and all(g['caller']=='agent'+task for g in status['approvals'])
                  and all(r['origin']['caller']=='agent'+task for r in status['requests']))
        check('inbox_and_journal_enabled_and_exist',profile['durable_inbox'] is True and profile['identifier_journal'] is True and inbox.exists() and journal.exists())
        received=[]
        if inbox.exists():
            for line in inbox.read_bytes().splitlines():
                blob=base64.b64decode(line);received.append(json.loads(AESGCM((trusted/'secure/provider.key').read_bytes()).decrypt(blob[:12],blob[12:],b'native-inbox-v1')))
        check('real_material_in_authority_and_inbox',all(state['requests'][rid]['result_material']['native']['access_token'] and
              any(x['rid']==rid and x['material']==state['requests'][rid]['result_material'] for x in received) for rid in ('A0','A1','B0')))
        check('seven_actual_read_denials',len(out['file_reads'])==7 and all(x.get('allowed') is False and x.get('winerror')==5 for x in out['file_reads']))
        check('three_actual_write_denials',len(out['file_writes'])==3 and all(x.get('allowed') is False and x.get('winerror')==5 for x in out['file_writes']))
        sensitive=[x for x in out['process_attacks']['processes'] if x['operation']!='QUERY_LIMITED']
        check('trusted_process_access_denied',len(sensitive)==18 and all(not x['allowed'] and x['winerror']==5 for x in sensitive))
        check('B_handle_rejected_for_A',denied(out['B_handle_attack']))
        check('six_role_attacks_reached_and_denied',len(out['role_attacks'])==6 and all(denied(x) for x in out['role_attacks']))
        check('R_cannot_read_private_response',len(out['R_private_evidence_denial'])==1 and
              out['R_private_evidence_denial'][0].get('allowed') is False and out['R_private_evidence_denial'][0].get('winerror')==5)
        check('known_A_disposition',all(r.get('status')=='KNOWN_UNIT_INACTIVE' for r in out['disposals'].values()) and
              all(state['requests'][rid]['phase']=='DISPOSED' for rid in ('A0','A1')))
        closure='KNOWN_MATERIALS_DISPOSED'
    else:
        check('no_identifier_or_inbox',not profile['durable_inbox'] and not profile['identifier_journal'] and not inbox.exists() and not journal.exists())
        pre=out['pre_query_inputs'];target=next(r for r in pre['runtime_projection']['requests'] if r['rid']=='A1')
        check('pending_unknown_before_query',target['phase']=='DISPATCHED_UNKNOWN' and pre['lookup']['status']=='UNKNOWN')
        if not synthetic:
            refresh=next(r for r in own if r['category']=='method' and r['operation']=='refresh')
            body=refresh['response']['body'];claims=json.loads(base64.urlsafe_b64decode(body['access_token'].split('.')[1]+'=='))
            values=[body['access_token'],body['refresh_token'],claims['jti'],claims['jti'].split('/')[-1]]
            check('pre_query_no_A1_identifiers',all(v.encode() not in canonical(pre) for v in values))
        check('A_alive_across_old_cache_recovery',out['A_alive_during_recovery'])
        check('both_unknown_during_authority_outage',res(out['A_outage']).get('status')=='UNKNOWN' and res(out['B_outage']).get('status')=='UNKNOWN')
        check('outage_does_not_admit_or_spend','A_outage' not in state['requests'] and 'B_outage' not in state['requests'])
        process_events=[json.loads(s) for s in (trusted/'control/processes.jsonl').read_text().splitlines()]
        stop_index=next((i for i,e in enumerate(process_events) if e['event']=='terminated_and_waited' and e['child_pid']==out['fault_pid']),None)
        check('old_instance_exit_precedes_new_instance',stop_index is not None and any(
            e['event']=='started_restricted' and e.get('role')=='controller' and e['child_pid']!=out['fault_pid'] for e in process_events[stop_index+1:]))
        check('B_creation_pause_and_existing_resource',denied(out['B_creation_paused']) and success(out['B_inside_window']))
        receipt=out['closure'].get('receipt',{})
        spec=importlib.util.spec_from_file_location('independent_closure',Path(__file__).with_name('check_reconciliation_receipt.py'))
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        verdict=checker.check(receipt)
        check('independent_closure_receipt',verdict['status']!='INVALID')
        check('closure_committed',state['reconciliation_windows'][profile['actor']['id']]['receipt']==receipt)
        closure=receipt.get('claim','UNKNOWN')
        if closure=='CLOSED':
            check('enumeration_evidence_origin',receipt['evidence_origin']=='AUTHORIZED_SCOPE_ENUMERATION' and receipt['remaining_creation_bound']==0)
            check('closed_obligation_removed','A1' not in out['final_state']['obligations'])
        else:check('unknown_obligation_retained','A1' in out['final_state']['obligations'])
    if not synthetic:
        final=load(trusted/'scorer/final_native.json')
        check('independent_native_B_accepts',any(r['rid']=='B0' and r['accepted'] is True for r in final['rows']))
        a=[r for r in final['rows'] if r['rid'] in {'A0','A1'}]
        if closure in {'CLOSED','KNOWN_MATERIALS_DISPOSED'}:
            check('independent_native_A_rejects',len(a)==2 and all(r['accepted'] is False and r.get('refresh_rejected') is True for r in a))
    # Full secret set comes from private audit and decrypted authoritative state.
    secrets_to_scan=[]
    for record in private:
        form=record.get('form') or {};payload=record.get('payload') or {};body=record['response'].get('body') or {}
        for field in ('password','client_secret','token','refresh_token'):
            if isinstance(form.get(field),str):secrets_to_scan.append(form[field])
        if isinstance(payload,dict) and isinstance(payload.get('password'),str):secrets_to_scan.append(payload['password'])
        if isinstance(body,dict):
            for field in ('access_token','refresh_token','id_token','clientSecret'):
                if isinstance(body.get(field),str):secrets_to_scan.append(body[field])
    for role in ('controller','authority','provider'):
        cfg=load(trusted/('secure/'+role+'.json'))
        secrets_to_scan += list(cfg['identities'].values())
    private_key=(batch/'scorer_secret/http-audit-private.pem').read_bytes()
    forbidden=[v.encode() for v in secrets_to_scan if v]+[key.read_bytes(),key.read_bytes().hex().encode(),base64.b64encode(key.read_bytes()),private_key]
    files=[trusted/'runner/outcome.json',root/'ENVIRONMENT_LOCK.json']
    for folder in ('runner','controller','control','provider','authority','scorer'):
        files += [p for p in (trusted/folder).rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.txt','.stderr'} and p.name!='native_inbox.jsonl']
    files += list((root/'agents/A/out').glob('*.json'))+list((root/'agents/B/out').glob('*.json'))
    leaks=[]
    for path in files:
        data=path.read_bytes()
        if any(secret in data for secret in forbidden):leaks.append(str(path))
    check('responses_errors_logs_no_actual_secret',not leaks)
    agent_file_leaks=[]
    for n in ('A','B'):
        own_cap=load(root/('agents/'+n+'/config.json'))['capability'].encode()
        for path in (root/('agents/'+n)).rglob('*'):
            if path.is_file() and path.suffix in {'.json','.txt'}:
                data=path.read_bytes()
                if any(secret in data for secret in forbidden if secret!=own_cap):agent_file_leaks.append(str(path))
    check('agent_readable_workspace_no_other_secrets',not agent_file_leaks)
    # Current batch owns every recorded process; cleanup is checked separately
    # after the case exits, keeping pre-cleanup B evidence intact.
    cleanup=load(root/'CLEANUP.json')
    check('all_owned_processes_terminated',all(p.get('terminated_and_waited') for p in cleanup['processes']),'cleanup')
    bad=[c for c in checks if not c['pass']]
    status='SAFETY_FAILURE' if any(c['category']=='security' for c in bad) else 'INCONCLUSIVE' if bad else ('PASS_CLOSED' if closure=='CLOSED' else 'PASS_KNOWN_DISPOSAL')
    result={'scenario':out['scenario'],'status':status,'checks':checks,'closure':closure,'remaining_obligations':out['final_state']['obligations'],
            'leak_paths':leaks+agent_file_leaks,'read_paths':accesses,'synthetic':synthetic}
    (root/'scorer_private/result.json').write_text(json.dumps(result,indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--synthetic',action='store_true');a=p.parse_args()
    result=score(a.case,a.synthetic);print(json.dumps({'status':result['status'],'failed':[x for x in result.get('checks',[]) if not x['pass']]}))
    raise SystemExit(2 if result['status']=='SAFETY_FAILURE' else 0)
