"""Read-only provenance and finite integration checks. No MPC/native execution.
 New records are not reclassified as the prior audit's 898/70/21/32 results.
 """
from pathlib import Path
import sys,json,hashlib,itertools,argparse
from copy import deepcopy
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent
ROOT=Path('D:/毕业设计')
CR=ROOT/'研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1'
MAIN=ROOT/'研究/算法机制重构与原创性验证_2026-11-03'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
 baseline=BASE/'保留基线.json'
 if not baseline.exists():
  files={}
  for directory in [CR,MAIN,ROOT/'auth-lifecycle/src',ROOT/'auth-lifecycle/docs',ROOT/'auth-lifecycle/experiments',ROOT/'auth-lifecycle/results']:
   for p in directory.rglob('*'):
    if any(x in p.parts for x in ['__pycache__','.deps','working','Player-Data']):continue
    if p.is_file():files[str(p)]=sha(p)
  dump(baseline,{'scope':'crypto public revision artifacts and latest mainline package excluding working/.deps/pycache/Player-Data; auth source/docs/experiments/results','files':files})
 m=read(CR/'delivery_manifest.json');checks=[]
 def check(name,expected,actual,scope='INTEGRATION_CHECK'):
  checks.append({'name':name,'expected':expected,'actual':actual,'pass':actual==expected,'scope':scope})
 check('crypto_manifest_digest', (CR/'manifest_sha256.txt').read_text().split()[0],sha(CR/'delivery_manifest.json'))
 file_checks=[{'path':r['path'],'pass':(CR/r['path']).exists() and sha(CR/r['path'])==r['sha256']} for r in m['files'] if 'Player-Data' not in Path(r['path']).parts]
 skipped=[r['path'] for r in m['files'] if 'Player-Data' in Path(r['path']).parts]
 check('crypto_public_manifest_entries',True,all(x['pass'] for x in file_checks))
 check('crypto_source_snapshot_digest',m['source_snapshot_sha256'],sha(CR/'source_snapshot.zip'))
 ten=[{'path':r['path'],'pass':sha(CR.parents[1]/r['path'])==r['expected']} for r in m['protected_ten_inputs']]
 known=[{'path':r['path'],'pass':sha(CR.parents[1]/r['path'])==r['expected']} for r in m['old_manifest_explicit_hash_checks']]
 check('ten_original_inputs',True,all(x['pass'] for x in ten))
 check('fourteen_explicit_old_hashes',True,all(x['pass'] for x in known))
 replay=[{'left':r['left'],'right':r['right'],'same':(CR/r['left']).read_bytes()==(CR/r['right']).read_bytes()} for r in m['deterministic_replay']]
 check('nine_old_deterministic_pairs',True,all(x['same'] for x in replay))
 inherited={k:read(CR/'results'/folder/'summary.json') for k,folder in [('main','dev02'),('attacks','certificate_attacks02'),('algebra','algebra02')]}
 for key,count in [('main',898),('attacks',70),('algebra',21)]:check('recorded_'+key+'_assertions',count,inherited[key]['assertion_records'],'HISTORICAL_RECORD_VERIFIED_NOT_RERUN')
 logs=read(CR/'results/gate_log_verification.json');check('recorded_MPC_scenarios',32,sum(x['verified_cases'] for x in logs['runs']),'HISTORICAL_RECORD_VERIFIED_NOT_RERUN')
 log_hash=[]
 for r in logs['runs']:
  for name,h in r['raw_logs_sha256'].items():
   path=CR/'results'/(('gate_' if r['method']=='gate' else 'release_')+r['profile'])/name
   log_hash.append({'path':str(path),'pass':sha(path)==h})
 check('MPC_raw_log_hashes',True,all(x['pass'] for x in log_hash))
 deltas=[]
 for profile in ['original','restricted']:
  a=next(x for x in logs['runs'] if x['profile']==profile and x['method']=='gate');b=next(x for x in logs['runs'] if x['profile']==profile and x['method']=='release')
  deltas.append({'profile':profile,'secret_multiplication_delta':b['triples']-a['triples'],'communication_MB_delta':b['global_data_sent_MB']-a['global_data_sent_MB'],'rounds_delta':b['party0_rounds_including_preprocessing']-a['party0_rounds_including_preprocessing'],'not_free_overall':True})
 check('recorded_extra_secret_multiplications',[0,0],[x['secret_multiplication_delta'] for x in deltas],'HISTORICAL_RECORD_VERIFIED_NOT_RERUN')
 sys.path.insert(0,str(CR));import profiles,compiler,checker,gate_reference
 original,restricted=profiles.record_profiles();counts={'original':0,'restricted':0,'lost_inputs':[]};evaluations=[]
 co=gate_reference.build(original);cr=gate_reference.build(restricted)
 for d in itertools.product(range(4),repeat=4):
  support={i for i,x in enumerate(d) if x};expected_o=len(support)<=2;expected_r=all(len(support&pair)<=1 for pair in [{0,1},{2,3}])
  ao=gate_reference.evaluate(co,d)['accepted'];ar=gate_reference.evaluate(cr,d)['accepted']
  evaluations.append({'d':d,'expected':[expected_o,expected_r],'actual':[ao,ar],'pass':ao==expected_o and ar==expected_r})
  counts['original']+=expected_o;counts['restricted']+=expected_r
  if expected_o and not expected_r:counts['lost_inputs'].append(d)
 check('GF4_support_range',[67,49,18],[counts['original'],counts['restricted'],len(counts['lost_inputs'])])
 check('256_inputs_two_gate_evaluations',True,all(x['pass'] for x in evaluations))
 cert=compiler.components(restricted);positive=checker.check(cert,restricted)
 check('public_component_certificate','VERIFIED',positive['verification_status'])
 check('math_certificate_never_authorizes',False,positive['authorizes_execution'])
 check('math_certificate_not_runtime_support',False,positive['runtime_support_verified'])
 badfamily=checker.check(compiler.components(original),original)
 check('C3_not_original_profile','MODEL_NOT_APPLICABLE',badfamily['verification_status'])
 conflict=checker.check(compiler.find_conflict(original),original)
 check('conflict_scope_only','INFEASIBLE_IN_DECLARED_MASK_CLASS',conflict['mathematical_conclusion'])
 changed=deepcopy(restricted);changed['world_ref']='changed-world'
 check('certificate_context_change','INVALID_CERTIFICATE',checker.check(cert,changed)['verification_status'])
 partial=deepcopy(restricted);partial['support_policy']['coverage']='known_subset'
 check('partial_family','INCONCLUSIVE',checker.check(compiler.components(partial),partial)['verification_status'])
 check('budget_exhaustion','INCONCLUSIVE',checker.check(cert,restricted,max_rank_checks=0)['verification_status'])
 production=deepcopy(restricted);production['field']={'q':2**128,'representation':'backend-gf2n'}
 check('small_field_not_production_certificate','OUT_OF_SCOPE',checker.check(cert,production)['verification_status'])
 # A new public profile with forged-looking reference text can still be a valid
 # mathematical instance: this explicitly demonstrates that reference text is not
 # an authenticated service fact. It must retain runtime_support_verified=False.
 labelled=deepcopy(restricted);labelled['source_refs']=['UNATTESTED_SERVICE_CLAIM'];cc=checker.check(compiler.components(labelled),labelled)
 check('source_label_is_not_attestation',['VERIFIED',False,False],[cc['verification_status'],cc['runtime_support_verified'],cc['authorizes_execution']])
 dump(out/'support_range.json',{'counts':counts,'checks':evaluations,'scope':'clear L0 finite check, not MPC'})
 dump(out/'public_certificates.json',{'original_profile':original,'restricted_profile':restricted,'positive':positive,'inapplicable':badfamily,'conflict':conflict,'unattested_reference':cc})
 dump(out/'provenance.json',{'crypto_files':file_checks,'excluded_player_data':skipped,'exclusion_reason':'MPC keys/preprocessing caches and WSL links are not reread or redistributed in this integration task','ten_inputs':ten,'fourteen_explicit_hashes':known,'replay':replay,'raw_log_hashes':log_hash,'historical_summaries':inherited,'historical_MPC':logs,'incremental_costs':deltas,'existence_only_523_not_upgraded':True})
 current=read(baseline)['files'];changes=[p for p,h in current.items() if not Path(p).exists() or sha(Path(p))!=h]
 check('retained_sources_unchanged',[],changes)
 dump(out/'summary.json',{'pass':all(x['pass'] for x in checks),'integration_assertions':len(checks),'checks':checks,'protected_files':len(current),'historical_counts_not_added_to_current':True,'MPC_executed_this_merge':False,'auth_lifecycle_modified':False,'limits':'not proof-assistant review, priority resolution, malicious MPC audit or formal H testing'})
 print(json.dumps({'pass':all(x['pass'] for x in checks),'assertions':len(checks),'protected_files':len(current),'failed':[x for x in checks if not x['pass']]},ensure_ascii=False))
if __name__=='__main__':main()
