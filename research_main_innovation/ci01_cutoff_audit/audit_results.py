"""Offline evidence checker; does not call the collector or any service."""
from collections import Counter,defaultdict
from hashlib import sha256
import argparse,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def h(p):return sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='EVIDENCE_AUDIT.json');args=parser.parse_args()
    out=(ROOT/args.output).resolve()
    if not out.is_relative_to(ROOT):raise ValueError('outside directory')
    assertions=[]
    def check(name,actual,expected=True):
        assertions.append({'id':name,'expected':expected,'actual':actual,'pass':actual==expected})
    totals=Counter();cost_rows=[];all_events=[];raw_paths=[];sessions=[]
    for run in ['run01','config01']:
        path=ROOT/'raw'/run/'http_and_events.jsonl';raw_paths.append(path)
        events=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]
        prev='0'*64
        good=True
        for i,row in enumerate(events,1):
            body={k:v for k,v in row.items() if k!='sha256'}
            calc=sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
            good &= row['sha256']==calc and row['previous']==prev and row['seq']==i
            prev=row['sha256']
        check(run+'_hash_chain',good)
        sent=[x for x in events if x['event']=='http_sent'];received=[x for x in events if x['event']=='http_received'];unknown=[x for x in events if x['event']=='http_unknown']
        check(run+'_all_sent_accounted',sorted(x['payload']['request_id'] for x in sent)==sorted(x['payload']['request_id'] for x in received+unknown))
        counts=Counter(x['category'] for x in sent);totals.update(counts)
        result=json.loads((path.parent/'result.json').read_text(encoding='utf-8'))
        check(run+'_cost_summary',dict(counts),result['http_costs'])
        check(run+'_no_transport_unknown',len(unknown),0)
        for x in sent:cost_rows.append({'run':run,'case':x['case'],'category':x['category'],'operation':x['operation'],'path':x['payload']['path'],'request_id':x['payload']['request_id']})
        all_events.extend(events)
        src=json.loads((path.parent/'source_hashes.json').read_text(encoding='utf-8'))
        check(run+'_source_snapshot_integrity',all(h(path.parent/x['snapshot'])==x['sha256'] for x in src))
        # Explicit projection carries key names and token digests, never token values.
        check(run+'_no_serialized_jwt',re.search(r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.',path.read_text(encoding='utf-8')) is None)
        sessions.append({'run':run,'events':len(events),'sent':len(sent),'received':len(received),'unknown':len(unknown),
                         'non2xx_responses':sum(x['payload']['response'].get('http',0)>=300 for x in received),
                         'business_error_responses':sum(x['payload']['response'].get('status')=='error' for x in received),
                         'oauth_error_responses':sum(bool(x['payload']['response'].get('oauth_error')) for x in received)})
    accept=[x['payload'] for x in all_events if x['event']=='independent_acceptance']
    def observation(point,label,path='fresh_Bearer'):
        found=[x for x in accept if x['point']==point and x['label']==label and x['path']==path]
        if len(found)!=1:return 'MISSING_OR_DUPLICATED'
        return found[0]['accepted']
    for label in ['C10_A0','C10_A1','C10_A2']:
        check(label+'_initial_acceptance',observation('before_shared_hash_revoke',label))
        check(label+'_after_shared_hash_revoke',observation('after_shared_hash_revoke',label),False)
    check('C10_B_preserved',observation('after_shared_hash_revoke','C10_B0'))
    check('C11_bearer_reject',observation('after_app_delete','C11_dedicated_after_disable'),False)
    check('C11_cookie_accept',observation('after_app_delete','C11_dedicated_after_disable','cookie_only'))
    check('C11_B_preserved',observation('after_app_delete','C11_B0'))
    responses={x['operation']:x['payload']['response'] for x in all_events if x['event']=='http_received'}
    check('C11_generic_refresh_rejected',responses['refresh_C11_generic_after_disable_access_token'].get('oauth_error'),'unsupported_grant_type')
    check('C11_dedicated_refresh_issued',bool(responses['refresh_C11_dedicated_after_disable_refresh_token'].get('access_token_ref')))
    lists=[x['payload'] for x in all_events if x['event']=='scoped_listing']
    before,p1,p2,after,inactive=lists
    check('C12_offset_missed_record',before['rows'][1]['name'] not in {r['name'] for l in [p1,p2] for r in l['rows']} and before['rows'][1]['name'] in {r['name'] for r in after['rows']})
    check('C12_inactive_record_returned',any(r['expiresIn']==0 for r in inactive['rows']))
    final=[x for x in accept if x['point']=='after_fixture_cleanup']
    check('cleanup_known_AT_count',len(final),10)
    check('cleanup_known_AT_rejected',all(not x['accepted'] for x in final))
    main_result=json.loads((ROOT/'raw/run01/result.json').read_text(encoding='utf-8'))
    check('cleanup_3_users_3_apps',len(main_result['cleanup']),6)
    check('cleanup_deletions',all(x.get('deleted') for x in main_result['cleanup'].values()))
    check('cleanup_database_no_active_rows',all(x['user_rows']==0 and x['nonzero_token_rows']==0 for x in main_result['cleanup_db']))
    check('shared_app_unchanged',main_result['shared_application_unchanged'])
    history=json.loads((ROOT/'HISTORICAL_INPUT_HASHES.json').read_text(encoding='utf-8'))['files']
    mismatch=[x['path'] for x in history if not Path(x['path']).exists() or h(Path(x['path']))!=x['sha256']]
    check('historical_files_unchanged',mismatch,[])
    model=json.loads((ROOT/'checks02/results.json').read_text(encoding='utf-8'))
    check('model_no_failed_claims',model['failed'],0)
    check('model_74_schedules',model['enumerated_interleavings'],74)
    check('phase_budget',sum(totals.values())<=220)
    breakdown=defaultdict(Counter)
    for x in cost_rows:breakdown[x['run']+'/'+x['case']][x['category']]+=1
    result={'evidence_kind':'OFFLINE_RAW_RECONCILIATION','sessions':sessions,'http_costs':dict(totals),'http_total':sum(totals.values()),
       'cost_by_case':{k:dict(v) for k,v in breakdown.items()},'acceptance_observations':len(accept),
       'historical_files_verified':len(history),'assertions':assertions,'passed':sum(x['pass'] for x in assertions),'failed':sum(not x['pass'] for x in assertions),
       'checker_sha256':h(Path(__file__)),'notes':['native runs are observations, not statistical tests','hash chain is integrity bookkeeping, not independent freshness attestation','role separation is same-process data flow']}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/(out.stem+'_REQUEST_COSTS.json')).write_text(json.dumps(cost_rows,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['http_total','acceptance_observations','historical_files_verified','passed','failed']},ensure_ascii=False))
    for x in assertions:
        if not x['pass']:print(json.dumps(x,ensure_ascii=False))
    if result['failed']:raise SystemExit(1)

if __name__=='__main__':main()
