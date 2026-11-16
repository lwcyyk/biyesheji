"""Independent M4 evidence checks, including no pre-query identifiers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.online_state.native_http import private_http_records
from auth_lifecycle.online_state.evidence_semantics import rt_inactive_or_refresh_response_rejected


def score(root):
    root=Path(root)
    outcome=json.loads((root/"runner/outcome.json").read_text())
    if outcome["status"]!="OBSERVED":
        result={"status":"ABORTED","reason":"INCOMPLETE_RUNTIME_TRACE"}
        (root/"scorer/result.json").write_text(json.dumps(result));return result
    checks=[]
    def verify(name,ok):checks.append({"name":name,"pass":bool(ok)})
    receipt=json.loads((root/"runner/closure_receipt.json").read_text())
    spec=importlib.util.spec_from_file_location('receipt_checker',Path(__file__).with_name('check_reconciliation_receipt.py'))
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    receipt_check=checker.check(receipt)
    verify('independent_receipt',receipt_check['status']!='INVALID')
    profile=json.loads((root/'secure/native_profile.json').read_text())
    batch=Path(profile['batch'])
    policy=json.loads((batch/'BUDGET_AND_AUTHORIZATION.json').read_text())
    with sqlite3.connect('file:'+str(root/'authority/authority.db')+'?mode=ro',uri=True) as con:
        sealed=con.execute('SELECT ciphertext FROM authority_state WHERE id=1').fetchone()[0]
        events=[(v,op,json.loads(p)) for v,op,p in con.execute('SELECT version,operation,projection FROM authority_events ORDER BY version')]
    state=json.loads(AESGCM((root/'secure/authority.key').read_bytes()).decrypt(sealed[:12],sealed[12:],b'auth-lifecycle/online-state/schema-1'))
    target=state['requests']['A1']
    verify('receipt_committed',state['reconciliation_windows'][target['origin']['account']]['receipt']==receipt)
    verify('target_binding',receipt['target']['attempt_id']==target['attempt_id'] and receipt['target']['request_digest']==target['digest'])
    verify('no_operational_journal_or_inbox',profile['identifier_journal'] is False and profile['durable_inbox'] is False
           and not (root/'provider/identifier_receipts.jsonl').exists() and not (root/'provider/native_inbox.jsonl').exists())
    pre=outcome['pre_query_inputs']
    prior=next(r for r in pre['runtime_projection']['requests'] if r['rid']=='A1')
    verify('recovery_projection_unknown',prior['phase']=='DISPATCHED_UNKNOWN' and pre['lookup']['status']=='UNKNOWN')
    raw=private_http_records(batch)
    refresh=[r for r in raw if r['actor']==profile['actor']['name'] and r['category']=='method' and r['operation']=='refresh']
    verify('one_refresh_send',len(refresh)==1)
    if refresh:
        body=refresh[0]['response']['body']
        claims=json.loads(__import__('base64').urlsafe_b64decode(body['access_token'].split('.')[1]+'=='))
        prior_bytes=json.dumps(pre,sort_keys=True).encode()
        verify('pre_query_projection_has_no_A1_identifiers',all(value.encode() not in prior_bytes for value in
            [body['access_token'],body['refresh_token'],claims['jti'],claims['jti'].split('/')[-1]]))
    verify('audit_sealed_to_scorer',policy['audit_mode']=='sealed_to_scorer' and not (batch/'secure/http.key').exists()
           and (batch/'scorer_secret/http-audit-private.pem').exists())
    query=receipt['evidence']['packet']['query']
    rowset=query.get('returned_records',[])
    if receipt['claim']=='CLOSED':
        verify('organization_authorized_and_complete',receipt['evidence_origin']=='AUTHORIZED_SCOPE_ENUMERATION'
               and query.get('collection_complete') is True and query.get('organization')==policy['organization'])
    if rowset:
        verify('all_rows_in_authorized_org',all(r['organization']==policy['organization'] for r in rowset))
        verify('exact_target_selection',set(query['target_unit_ids'])=={r['unit_id'] for r in rowset if r['user']==profile['actor']['name'] and r['application']==policy['application_name']})
    other={r['unit_id'] for r in rowset if r['user']!=profile['actor']['name']}
    if receipt['claim']=='CLOSED':
        verify('other_accounts_not_selected',bool(other) and not (other & set(query['candidate_unit_ids'])))
    verify('B_and_interferer_preserved',outcome['B_after']['status']=='RESULT_AVAILABLE' and outcome['interferer_preserved']['status']=='RESULT_AVAILABLE')
    initial=json.loads((root/'scorer/initial_native.json').read_text())
    final=json.loads((root/'scorer/final_native.json').read_text())
    verify('native_B_acceptance',any(r['rid']=='B0' and r['accepted'] is True for r in final['rows']))
    if receipt['claim']=='CLOSED':
        a=[r for r in final['rows'] if r['rid'].startswith('A')]
        verify('native_A_units_inactive',len(a)==2 and all(r['accepted'] is False and rt_inactive_or_refresh_response_rejected(r) for r in a))
        verify('remaining_effects_and_obligations_closed',receipt['remaining_creation_bound']==0 and 'A1' not in outcome['final_state']['obligations'])
    else:
        verify('unknown_obligation_retained','A1' in outcome['final_state']['obligations'])
    if outcome['scenario']=='M4-02':
        empty=json.loads((root/'runner/empty_receipt.json').read_text())
        first=empty['evidence']['packet']['query']
        verify('pre_send_not_falsely_closed',empty['claim']=='UNKNOWN' and empty['facts']['actual_sends']==0 and empty['remaining_creation_bound']==1)
        if first.get('collection_complete') is True:
            verify('real_native_empty_candidate_observation',first['query_kind']=='organization_equal_single_page'
                   and first['candidate_unit_ids']==[] and len(first['target_unit_ids'])==2)
    processes=[json.loads(l) for l in (root/'control/processes.jsonl').read_text().splitlines()]
    verify('all_case_processes_exited',sorted(r['child_pid'] for r in processes if r['event']=='started')==sorted(r['child_pid'] for r in processes if r['event']=='terminated_and_waited'))
    secret_values=[profile['client_secret'],profile['actor']['password']]
    for record in raw:
        if record['actor'] in policy['account_names'] and isinstance(record['response'].get('body'),dict):
            body=record['response']['body']
            secret_values += [body[k] for k in ['access_token','refresh_token','id_token'] if body.get(k)]
    leaks=[]
    for folder in ['runner','controller','control','provider','authority','scorer']:
        for path in (root/folder).rglob('*'):
            if path.is_file() and path.suffix in {'.json','.jsonl','.txt','.stderr'} and path.name!='native_inbox.jsonl':
                if any(s.encode() in path.read_bytes() for s in secret_values):leaks.append(str(path.relative_to(root)))
    verify('public_output_custody',not leaks)
    status=('PASS_CLOSED' if receipt['claim']=='CLOSED' else 'PASS_CONSERVATIVE_UNKNOWN') if all(c['pass'] for c in checks) else 'SAFETY_FAILURE'
    result={'status':status,'checks':checks,'receipt_checker':receipt_check,'closure':receipt['claim'],
            'remaining_obligations':outcome['final_state']['obligations'],'leak_paths':leaks,
            'read_scope':policy['organization'],'global_record_bound':query.get('record_upper_bound'),'returned_rows':len(rowset),
            'target_rows':len(query.get('target_unit_ids',[])),'candidates':len(query.get('candidate_unit_ids',[])),
            'observed_target_G':len({r['native_unit_ref'] for s in [initial,final] for r in s['native_units']})}
    (root/'scorer/result.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case',required=True)
    args=parser.parse_args();result=score(args.case);print(json.dumps({'status':result['status']}))
    raise SystemExit(1 if result['status']=='SAFETY_FAILURE' else 0)
