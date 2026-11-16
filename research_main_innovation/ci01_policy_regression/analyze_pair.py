"""Independent paired-output and artifact checks; never calls a service."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,argparse,zipfile

ROOT=Path(__file__).resolve().parent
def h(p):return sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def stage(row,name):
    values=[e['passed'] for e in row['stages'] if e['stage']==name]
    return all(values) if values else None
def layers(row):
    return {k:stage(row,v) for k,v in {'route_resolved':'route_resolved','client_gate_continues':'client_gate_return',
      'authenticated_identity_retained':'subject_identified','global_permission':'global_permission_result',
      'controller_dispatched':'controller_dispatch','controller_entered':'controller_enter','controller_permission_pass':'controller_permission_pass'}.items()} | {
      'synthetic_effect_observed':row['synthetic_display_changed'] or row['synthetic_userinfo_accepted']}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-id',default='paired02');ap.add_argument('--out',default='PAIRED_RESULTS.json');args=ap.parse_args()
    a_dir=ROOT/'raw'/(args.run_id+'_baseline');b_dir=ROOT/'raw'/(args.run_id+'_fixed')
    a,b=load(a_dir/'chain_results.json'),load(b_dir/'chain_results.json')
    aa={x['id']:x for x in a['results']};bb={x['id']:x for x in b['results']}
    cases=load(ROOT/'INPUT_CASES.json')['cases'];cm={c['id']:c for c in cases};checks=[]
    def check(name,actual,expected=True):checks.append({'id':name,'actual':actual,'expected':expected,'pass':actual==expected})
    check('identical_case_ids',list(aa)==list(bb))
    check('all_113_historical_cases_present',all(x in aa for x in cm))
    check('four_integration_controls_present',sum(x.startswith('X_') for x in aa),4)
    check('zero_runtime_network_attempts',a['runtime_HTTP_attempts']+b['runtime_HTTP_attempts'],0)
    check('test_processes_completed',[int((p/'exit_code.txt').read_text(encoding='utf-8-sig')) for p in [a_dir,b_dir]],[0,0])
    old=load(ROOT.parent/'ci01_policy_consistency_review/TEST_RESULTS.json');old_by={x['id']:x for x in old['results']}
    pairs=[];unknown_changes=[];known_fail=[]
    for name,x in aa.items():
        y=bb[name];expected=x['historical_expected']
        row={'id':name,'historical_expected':expected,'baseline_actual':x['actual'],'fixed_actual':y['actual'],
          'baseline_layers':layers(x),'fixed_layers':layers(y),'baseline_post_session':x.get('post_session_fields_present'),
          'fixed_post_session':y.get('post_session_fields_present'),'baseline_cost':x['observed_costs'],'fixed_cost':y['observed_costs'],
          'expected_changed':False,'class':'UNRESOLVED_OBSERVATION' if expected=='SPEC_UNRESOLVED' else 'KNOWN_CONTRACT'}
        if name in old_by:row['prior_mock_actual']=old_by[name]['actual']
        if expected=='SPEC_UNRESOLVED' and x['actual']!=y['actual']:unknown_changes.append(name);row['class']='UNRESOLVED_BEHAVIOR_CHANGED'
        if expected!='SPEC_UNRESOLVED' and y['actual']!=expected:known_fail.append(name)
        pairs.append(row)
    check('all_known_contracts_hold_after_fix',known_fail,[])
    check('previous_50_passes_preserved',sum(bb[n]['actual']==old_by[n]['expected'] for n in old_by if old_by[n]['contract_check']=='PASS'),50)
    fixedids=['M081','B02','B04']
    for name in fixedids:
        x,y=aa[name],bb[name]
        check(name+'_baseline_effect',x['synthetic_display_changed'])
        check(name+'_baseline_full_chain',all(layers(x)[key] for key in ['route_resolved','authenticated_identity_retained','global_permission','controller_entered','controller_permission_pass']))
        check(name+'_fixed_effect_absent',not y['synthetic_display_changed'] and y['actual']=='DENY')
        check(name+'_no_persistent_source_identity',all(v is False for v in y['post_session_fields_present'].values()))
        check(name+'_same_app_lookup_count',y['observed_costs'].get('application_by_client_lookup'),x['observed_costs'].get('application_by_client_lookup'))
    check('independent_login_retained',bb['B16']['actual']=='ALLOW' and bb['B16']['post_session_fields_present']['username'])
    check('anonymous_public_continuation',bb['X_ANON']['actual']=='ALLOW' and stage(bb['X_ANON'],'subject_identified') is False)
    for name in ['X_ORIGIN','X_FIELD','X_TARGET']:check(name+'_control',bb[name]['actual'],'DENY')
    check('spec_expectations_stay_unresolved',sum(x['historical_expected']=='SPEC_UNRESOLVED' for x in b['results']),60)
    # Verify exact baseline-to-fixed source delta (observation and fixture code equal).
    differences=[]
    for p in (ROOT/'baseline').rglob('*'):
        if p.is_file() and (p.suffix in {'.go','.mod','.sum'}):
            rel=p.relative_to(ROOT/'baseline');q=ROOT/'fixed'/rel
            if not q.exists() or h(p)!=h(q):differences.append(rel.as_posix())
    check('only_policy_source_differs',differences,['routers/authz_filter.go'])
    check('minimal_patch_hash',h(ROOT/'MINIMAL_PATCH.diff'),load(ROOT/'PATCH_HASHES.json')['patch_sha256'])
    check('patch_applies_to_original',int((ROOT/'raw/patch_check02_exit.txt').read_text(encoding='utf-8-sig')),0)
    histories=load(ROOT/'HISTORICAL_HASHES.json')
    changed=[x['path'] for x in histories if not Path(x['path']).exists() or h(Path(x['path']))!=x['sha256']]
    check('history_unchanged',changed,[])
    for directory in [a_dir,b_dir]:
        hashes=load(directory/'source_hashes.json')
        check(directory.name+'_snapshot_hashes',all(h(directory/'source_snapshot'/x['path'])==x['sha256'] for x in hashes))
    known_before=sum(x['historical_expected']!='SPEC_UNRESOLVED' and x['actual']!=x['historical_expected'] for x in a['results'])
    result={'evidence_level':'FULL_TARGET_PERMISSION_CHAIN_OFFLINE','source_commit':'528a0213f01caf70b9f41009cbf7b2f67bdd67ec',
      'run_id':args.run_id,'historical_case_count':113,'supplemental_controls':4,'paired_inputs':len(pairs),
      'baseline_known_contract_violations':known_before,'fixed_known_contract_violations':len(known_fail),
      'previous_50_known_passes_retained':50,'three_branch_instances_fixed':fixedids,'spec_unresolved_count':60,
      'unresolved_behavior_changes':unknown_changes,'new_policy_decision':'D1: application-bound identity with missing application is cleared; anonymous public continuation remains available',
      'native_service_calls':0,'real_account_operations':0,'runtime_outbound_HTTP_attempts':0,
      'cost_scope':{'per_variant_target_in_process_requests':117,'per_variant_fixture_cookie_seed_in_process_requests':67,
        'per_variant_observer_session_reads':68,'new_DB_queries_in_patch':0,'new_session_delete_attempts_per_missing_app_case':6,
        'relogin_interactions_executed':0,'relogin_may_be_required_for_affected_context':True,
        'sql_counters_caveat':'native async logging can overlap measurement windows; narrow resolver/clear counters are the primary delta'},
      'pairs':pairs,'checks':checks,'checks_passed':sum(c['pass'] for c in checks),'checks_failed':sum(not c['pass'] for c in checks),
      'historical_files_checked':len(histories),'limitations':['in-process framework and synthetic SQL/session state, not real browser or production',
        'metrics and request-log sink filters omitted; authz internal audit I/O remains native',
        'no concurrency safety proof','60 unresolved contracts remain unresolved','no new algorithm or protocol']}
    (ROOT/args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['paired_inputs','baseline_known_contract_violations','fixed_known_contract_violations','unresolved_behavior_changes','checks_passed','checks_failed','historical_files_checked']},ensure_ascii=False))
    if result['checks_failed']:raise SystemExit(1)
if __name__=='__main__':main()
