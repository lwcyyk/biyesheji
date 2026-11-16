"""Independent artifact audit. No HTTP, DB, native-service or policy execution."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import argparse,json,shutil,subprocess

ROOT=Path(__file__).resolve().parent
def h(p):return sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',default='offline02');parser.add_argument('--out',default='TEST_RESULTS.json');args=parser.parse_args()
    raw=(ROOT/'raw'/args.run).resolve()
    if not raw.is_relative_to(ROOT/'raw'):raise ValueError('invalid run')
    cases=load(raw/'cases.json');results=load(raw/'results.json')
    ids=[x['id'] for x in cases];rids=[x['id'] for x in results]
    checks=[]
    def check(name,value):checks.append({'id':name,'pass':bool(value)})
    check('one_result_per_case',ids==rids and len(ids)==len(set(ids)))
    extracts=load(ROOT/'SOURCE_EXTRACTS.json')
    for e in extracts:
        src=ROOT/'sources/frozen'/e['source'];out=ROOT/'offline'/e['output'];chunk=out.read_bytes()[e['output_byte_offset']:e['output_byte_offset']+e['bytes']]
        check('verbatim_'+e['source']+'_'+e['declaration'],h(src)==e['source_sha256'] and sha256(chunk).hexdigest()==e['segment_sha256'] and chunk in src.read_bytes())
    inputs=load(ROOT/'INPUT_HASHES.json')
    changed=[x['path'] for x in inputs if not Path(x['path']).exists() or h(Path(x['path']))!=x['sha256']]
    check('all_historical_inputs_unchanged',not changed)
    supplementary=load(ROOT/'SUPPLEMENTAL_INPUTS.json')
    check('supplementary_source_unchanged',all(h(Path(x['path']))==x['sha256'] and h(ROOT/x['snapshot'])==x['sha256'] for x in supplementary))
    lines=[json.loads(x) for x in (raw/'go-test.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.startswith('{')]
    mismatches=[x for x in results if x['contract_check']=='POLICY_MISMATCH']
    go_fails=[x['Test'].split('/')[-1] for x in lines if x.get('Action')=='fail' and x.get('Test','').startswith('TestPolicyMatrix/')]
    check('go_failures_match_contract_mismatches',sorted(go_fails)==sorted(x['id'] for x in mismatches))
    check('all_synthetic_matrix_cells_recorded',sum(x['id'].startswith('M') for x in cases)==96)
    check('no_synthetic_secret_or_real_user',[x for x in cases if 'password' in x or 'token' in x]==[])
    controls={x['Test']:x['Action'] for x in lines if x.get('Test') in {'TestConversionAttributePreservation','TestIndependentLoginClearsTokenBinding'} and x['Action'] in {'pass','fail'}}
    check('two_conversion_controls_pass',len(controls)==2 and set(controls.values())=={'pass'})
    snapshot=raw/'source_snapshot_final';snapshot.mkdir(exist_ok=True)
    hashes=[]
    for p in sorted((ROOT/'offline').rglob('*')):
        if p.is_file() and p.suffix in {'.go','.mod'}:
            rel=p.relative_to(ROOT);q=snapshot/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
            hashes.append({'source':str(rel),'snapshot':str(q.relative_to(raw)),'sha256':h(p)})
    for name in ['SOURCE_EXTRACTS.json','REVIEW_SCOPE.md','run_offline.ps1','audit_offline.py']:
        p=ROOT/name;q=snapshot/name;shutil.copyfile(p,q);hashes.append({'source':name,'snapshot':str(q.relative_to(raw)),'sha256':h(p)})
    (raw/'source_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    by_check=Counter(x['contract_check'] for x in results)
    go_version=subprocess.check_output([r'C:\Program Files\Go\bin\go.exe','version'],text=True,encoding='utf-8').strip()
    report={'stage':'authentication context and access policy consistency review','evidence_kind':'SYNTHETIC_OFFLINE_FUNCTION_TEST',
      'run':args.run,'native_HTTP_requests':0,'real_account_or_application_mutations':0,'new_protection_mechanisms':0,
      'compiled_verbatim_declarations':len(extracts),'test_scope':'extracted original functions with in-memory dependencies and an explicit downstream self-policy mock',
      'matrix_cells':96,'boundary_cases':len(cases)-96,'case_count':len(cases),'contract_results':dict(by_check),
      'actual_decisions':dict(Counter(x['actual'] for x in results)),'mismatch_case_ids':[x['id'] for x in mismatches],
      'distinct_source_branch_findings':1,'conversion_controls':controls,
      'go_test_exit_code':int((raw/'exit_code.txt').read_text(encoding='utf-8-sig').strip()),
      'toolchain':{'executed':go_version,'upstream_declared_go':'1.26.0','upstream_declared_toolchain':'go1.26.10','entire_upstream_build':'NOT_RUN','external_modules':[],'network_dependencies':'GOPROXY=off; GOSUMDB=off; GOTOOLCHAIN=local'},
      'artifact_checks':checks,'artifact_checks_passed':sum(x['pass'] for x in checks),'artifact_checks_failed':sum(not x['pass'] for x in checks),
      'historical_files_checked':len(inputs),'changed_historical_files':changed,
      'results':results,'limits':['ALLOW is an isolated harness result; no real edit request or resource write',
       'actual Beego middleware/session serialization, Casbin policy and HTTP deployment omitted',
       'missing source fields are fault-injected; normal-path reachability unproved',
       'three mismatch cases instantiate one nil-application branch; no independent-platform replication',
       '60 SPEC_UNRESOLVED observations are not counted as verified product contracts']}
    target=(ROOT/args.out).resolve()
    if not target.is_relative_to(ROOT):raise ValueError('invalid output')
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'OFFLINE_CASES.json').write_text(json.dumps({'synthetic_only':True,'operation_mapping':{'edit_display_name':'/api/update-user','read_userinfo':'/api/userinfo'},
      'fixture_model':{'subject':'fixture/alice','AT':'synthetic-at in an in-memory token map, not a JWT','live_token_created_time':'wall clock now minus 60 seconds','live_token_expires_in':3600,'expired_token_created_time':'2000-01-01T00:00:00Z','expired_session_data':{'ExpireTime':1},'source_missing_fault':'remove aud and signinTokenId after authentication','downstream_permission':'explicit mock allows fixture/alice to edit self; no mutation is implemented'},'cases':cases},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['case_count','contract_results','mismatch_case_ids','go_test_exit_code','artifact_checks_passed','artifact_checks_failed']},ensure_ascii=False))
    if report['artifact_checks_failed']:raise SystemExit(1)

if __name__=='__main__':main()
