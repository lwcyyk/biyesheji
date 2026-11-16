"""Local field/prose/payload consistency and archival sealing only."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re
B=Path(r'D:\毕业设计');O=B/'crypto_fi_adopted_release_v3_1';V=B/'crypto_fi_research_manuscript_v3';R=B/'crypto_fi_final_internal_review'
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def rd(x):return F(int(x['numerator']),int(x['denominator']))
def ck(id,truth):
 checks.append(dict(id=id,passed=bool(truth)));assert truth,id
def canonical(x):
 x=dict(x);x.pop('payload_sha256',None)
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
def pointer(x,p):
 for s in p.strip('/').split('/'):
  s=s.replace('~1','/').replace('~0','~');x=x[int(s)] if isinstance(x,list) else x[s]
 return x

m=load(O/'CLAIM_EVIDENCE_MATRIX.json');old=load(V/'CLAIM_EVIDENCE_MATRIX.json');prov=load(R/'REVIEW_PROVENANCE.json');local=load(R/'evidence/LOCAL_SCOPE_CORRECTIONS.json')
claims={x['id']:x for x in m['claims']};prior={x['id']:x for x in old['claims']}
ck('version_and_formal_status',m['version']=='v3.1' and m['adoption_record']['status']=='PASS_WITHIN_STATED_SCOPE')
ck('61_claims_retained',len(claims)==len(m['claims'])==61 and set(claims)==set(prior))
for entry in local['corrections']:
 for i,x in enumerate(entry['changes']):
  ck(entry['id']+'/old_source_'+str(i),pointer(old,x['json_pointer'])==x['old'])
  ck(entry['id']+'/exact_adoption_'+str(i),pointer(m,x['json_pointer'])==x['adopted'])
ck('L1_all3_frozen_contracts','cover640/976/1344' in claims['C25b']['assumptions'][0])
ck('L1_separate_remaining_scope',set(claims['C25b']['remaining_scope'])=={'official_profile_depths','filtering_selection_reuse','exact_full64','software'})
ck('L1_CF1_correctness_not_marked_pending','CF-1 correctness throughn updates is already proved' in claims['C25b']['remaining_scope']['official_profile_depths'])
ck('L1_pending_status_only_for_new_questions',claims['C25b']['evidence_status']=='UNRESOLVED' and 'fixed640 and one update' not in str(claims['C25b']['assumptions']))
ck('L2_proved_model_status',claims['C25d']['evidence_status']=='PROVED_UNDER_STATED_MODEL')
ck('L2_all3_distribution_inputs',claims['C25d']['semantic_distribution_inputs']==['chi640','chi976','chi1344'])
ck('L2_all6_model_selectors',len(claims['C25d']['semantic_input_selectors'])==6 and all(pointer(m,'/'+x.replace('.','/')) for x in claims['C25d']['semantic_input_selectors']))
ck('L2_no640_only_limitation','finite640 behavior' not in claims['C25d']['limitations'] and 'Three separate finite' in claims['C25d']['limitations'])
ck('L2_source_theorem63_relationship',claims['C25d']['theorem63_relation']['profiles']=={'640':dict(W_print=22649448960,right_numerator=4096),'976':dict(W_print=32387837760,right_numerator=4096),'1344':dict(W_print=13265908992,right_numerator=2048)})
for n,v in claims['C25d']['theorem63_relation']['profiles'].items():ck(n+'/sufficient_premise_unmet_at_all_integerT_ge1',v['W_print']>v['right_numerator'])
ck('L2_software_retained',m['stage_verdict']['author_software']=='WAITING_FOR_AUTHOR_ARTIFACT')
ck('L3_actual_time_chain',[v['id'] for v in m['priority_scope']['timeline']]==['E3','E13','E15'] and [v.get('through',v.get('registered')) for v in m['priority_scope']['timeline']]==['2026-11-08','2026-11-10','2026-11-11'])
ck('L3_top_level_latest_receipt_date',m['priority_search_cutoff']=='2026-11-11' and 'registered receipt date only' in m['priority_search_cutoff_basis'])
ck('L3_metadata_check_date_retained',m['new_metadata_check_date']==old['new_metadata_check_date']=='2026-11-10')
ck('L3_final_and_current_new_searches0',m['priority_scope']['final_internal_review_new_live_priority_searches']==m['priority_scope']['new_network_searches_this_revision']==prov['action_counts']['new_live_priority_searches']==0)
ck('L3_global_first_unestablished',claims['C24']['evidence_status']==m['priority_scope']['global_priority']=='SEARCH_BOUNDED_APPLICATION_CANDIDATE' and not m['priority_scope']['global_first_established'])
ck('review_identity_exact',m['adoption_record']['review_type']==prov['review_type']=='SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE')
ck('reviewer_and_exposure_exact',m['adoption_record']['reviewer']==prov['reviewer'] and m['adoption_record']['exposure']==prov['exposure'])
ck('exact_model_and_turn_null',all(prov['reviewer'][k] is None for k in ['exact_backend_model_id','exact_weights_version','turn_id']))
ck('no_new_independence_or_certifications',not prov['reviewer']['model_error_process_independence_established'] and not prov['exposure']['fresh_proof_blind_review'] and all(prov['action_counts'][k]==0 for k in ['new_human_reviews','new_cross_model_reviews','new_blind_reviews','proof_assistant_checks','new_independent_error_process_certifications']))
ck('current_is_adoption_not_new_review',m['identity']['new_comprehensive_internal_reviews']==0 and m['action_counts']['new_scalar_script_replays']==0)
ck('same_final_accepted_scope',m['adoption_record']['review_scope']==prov['scope'])
for k in ['frozen_models','official_profile_results','parametric_criterion','probability_results','fixed_A_probability_results','main_result_dependency_audit']:
 ck('unchanged_math_'+k,m[k]==old[k])
patch=load(O/'evidence/MANUSCRIPT_PATCH_LEDGER.json')
ck('same_theory_sections_2_to_9',patch['theorem_sections_2_to_9_unchanged_after_link_normalization'])
ck('same_proof_appendices',all(patch['proof_appendices_unchanged_after_link_normalization'].values()))
archive=load(O/'evidence/CERTIFICATE_ARCHIVE.json')
ck('21_archived_math_files',len(archive['files'])==21 and not archive['mathematical_payload_changed'])
for i,x in enumerate(archive['files']):
 ck(f'archive_{i}_source_and_copy_hash',rec(Path(x['source']['path']))==x['source'] and rec(Path(x['archive']['path']))==x['archive'] and x['source']['sha256']==x['archive']['sha256'])
selectors=load(O/'certificates/UNIFIED_RESULT_SELECTORS.json')
ck('profiles_equal_matrix_and_passed_source',selectors['profiles']==m['official_profile_results']==old['official_profile_results'])
binding=load(O/'evidence/THESIS_NUMERIC_BINDING.json')
ck('six_data_driven_endpoint_cases',len(binding['six_endpoint_comparisons'])==6 and all(v['validated_by_exact_rational_comparison'] for v in binding['six_endpoint_comparisons']))
for v in binding['six_endpoint_comparisons']:
 n=v['profile'];mode=v['mode'];p=selectors['profiles'][n];target=p[mode];alpha=F(1,2**p['initial']['full_failure_power']);U=rd(v['exact_upper']);UC=rd(v['exact_conditional_upper']);d=F(v['display_upper'])
 ck(n+'/'+mode+'/original_and_conditional_exact',U==rd(target['full_correct_upper']) and UC==min(F(1),U/(1-alpha))==rd(target['conditioned_on_initial']['full_correct_upper']))
 ck(n+'/'+mode+'/outward_and_percent',U<=UC<=d and F(v['display_error_percent'].rstrip('%'))==100*(1-d))
for id,c in claims.items():
 ck('claim_'+id+'/dependencies',all(x in claims for x in c.get('dependencies',[])))
 ck('claim_'+id+'/sources',all(x in m['source_registry'] for x in c.get('source_ids',[])))
ck('actual_author_configs_still_unresolved',all(x['author_implementation_status']=='UNRESOLVED' for x in m['implementation_model_migration']['config_mappings']) and m['implementation_model_migration']['author_UE_message_checked_traces']==0)
ck('strict_gap_gate_explicit',len(m['candidate_mechanism_implementation_gate']['before_implementation'])==5 and m['candidate_mechanism_implementation_gate']['current_new_candidate_implementations']==0)

texts={f:(O/f).read_text(encoding='utf-8') for f in ['CRYPTOANALYSIS_DRAFT.md','THESIS_ADOPTION.md','RELEASE_NOTES.md']}
thesis=texts['THESIS_ADOPTION.md'];notes=texts['RELEASE_NOTES.md'];draft=texts['CRYPTOANALYSIS_DRAFT.md']
ck('8_thesis_sections',all('## '+str(i)+'. ' in thesis for i in range(1,9)))
ck('thesis_data_driven_tables',binding['parameter_table'].strip() in thesis and binding['reliability_table'].strip() in thesis)
ck('same_approved_core_contribution',binding['core_contribution'] in thesis)
ck('thesis_A_complete_parameters',all(s in thesis for s in ['λ≥2','n=8λ','D=8⌈log₂n⌉','q=2^D','m̄=n̄=8','B=2','T=t_max=n','最长n次','3n+1','Δ_n']))
ck('thesis_B_contract_and_conditioning',all(s in thesis for s in ['两代共用A','全部原始χ坐标及调用','诚实未筛选','官方最近整数平局向上Decode','条件于相应I','128','192','256']))
ck('thesis_methods_attributed',all(s in thesis for s in ['Klooß','Arora','Fourier','Chernoff','成熟来源']))
ck('thesis_business_scope_real_contract',all(s in thesis for s in ['G1-2026-11-09-r01','LIMITED_NATIVE_PROTOTYPE','SOURCE_OR_REFINEMENT_GAP','独立密码分析章节及组件选用案例','AT/RT','严格差距']))
ck('notes_old_new_and_source',all(s in notes for s in ['Current proof fixed640 and one update','COUNTEREXAMPLE_FOUND','PROVED_UNDER_STATED_MODEL','L1','L2','L3','LOCAL_SCOPE_ADOPTION.json','MATRIX_ADOPTION_PATCH.json']))
ck('notes_specific_reopen_conditions',all(s in notes for s in ['满足冻结合同的数学反例','正式修订','日期可核的直接先例','认证作者UE工件','完整参数化归约','新业务需求与游戏映射']))
ck('notes_strict_instance_gate','至少一个' in notes and '必须承担更高代价' in notes)
for name,s in texts.items():
 ck(name+'/formal_status','PASS_WITHIN_STATED_SCOPE' in s and m['stage_verdict']['passed_result_name'] in s)
 ck(name+'/identity',prov['review_type'] in s)
 ck(name+'/priority_chain',all(d in s for d in ['2026-11-08','2026-11-10','2026-11-11']))
 ck(name+'/zero_search_disclosure',('新增' in s and '检索' in s and '0' in s))
 ck(name+'/utf8_and_user_style','\ufffd' not in s and not re.search(r'不是[^。\n]{0,300}而是',s))
 for n,p in selectors['profiles'].items():
  ck(name+'/'+n+'/numeric_endpoints',all(x in s for x in [p['fixed_A']['display']['row_full_upper'],p['uniform_Setup']['display']['row_full_upper'],p['fixed_A']['display']['full_error_percent_lower'].rstrip('%')+'%',p['uniform_Setup']['display']['full_error_percent_lower'].rstrip('%')+'%',f"2^-{p['initial']['full_failure_power']}"]))
links={}
for name,s in texts.items():
 s=re.sub(r'\\\[.*?\\\]','',s,flags=re.S)
 for dest in re.findall(r'\]\(([^\n)]+)\)',s):
  dest=dest.strip('<>')
  if dest.startswith(('https://','http://','#')):continue
  target=Path(dest)
  if not target.is_absolute():target=O/target
  target=target.resolve()
  if target==O/'MANIFEST.json':continue
  ck('local_link_'+name+'_'+str(len(links)),target.is_file())
  links[str(target)]=rec(target)
dump(O/'evidence/LINKED_SOURCE_FINGERPRINTS.json',dict(files=sorted(links.values(),key=lambda r:r['path']),scope='Actual local Markdown targets;self-manifest deferred until seal'))
snap=load(O/'evidence/INPUT_SNAPSHOT.json');changed=[]
for r in snap['files']:
 now=rec(Path(r['path']))
 if now!=r:changed.append(dict(before=r,after=now))
ck('836_historical_files_unchanged',len(snap['files'])==836 and not changed)
dump(O/'evidence/FINAL_INPUT_RECHECK.json',dict(unique_historical_files=836,all_bytes_unchanged=not changed,changes=changed))
fprints=load(O/'evidence/INPUT_FINGERPRINT_CHECK.json')
ck('4100_embedded_fingerprints_matched',fprints['records_checked']==4100 and fprints['all_matched'])
for x in fprints['inherited_canonical_seals']:
 ck('inherited_canonical_seal_'+Path(x['file']['path']).parent.name,canonical(load(Path(x['file']['path'])))==x['payload_sha256'])
for name in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','THESIS_ADOPTION.md','RELEASE_NOTES.md']:
 ck('required_payload_'+name,(O/name).is_file() and (O/name).stat().st_size>0)
qa=dict(schema='frodo-fi-v31/local-adoption-qa/1',date_asia_shanghai='2026-11-11',all_passed=True,check_count=len(checks),checks=checks,scope='Exact L1-L3 application,unchanged theorem/model/probability payloads,thesis source/endpoint consistency,provenance and archival byte checks. No new comprehensive mathematical review or historical scalar replay.',six_endpoint_comparisons=6,historical_files_unchanged=836)
dump(O/'evidence/DOCUMENT_QA.json',qa)
manifest=dict(schema='frodo-fi-adopted-release-manifest/v3.1',version='v3.1',date_asia_shanghai='2026-11-11',sealed_at_asia_shanghai=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),status='ADOPTED_V3_1_AND_ARCHIVED',adoption_verdict='PASS_WITHIN_STATED_SCOPE',passed_result_name=m['stage_verdict']['passed_result_name'],root=str(O),required_deliverables=['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','THESIS_ADOPTION.md','RELEASE_NOTES.md','MANIFEST.json'],current_identity=m['identity'],final_review_record=m['adoption_record'],correction_status=m['v3_1_corrections'],local_old_new_adoption=rec(O/'evidence/LOCAL_SCOPE_ADOPTION.json'),matrix_patch=rec(O/'evidence/MATRIX_ADOPTION_PATCH.json'),manuscript_patch=rec(O/'evidence/MANUSCRIPT_PATCH_LEDGER.json'),mathematical_payload_unchanged=True,certificate_archive=rec(O/'evidence/CERTIFICATE_ARCHIVE.json'),thesis_numeric_binding=rec(O/'evidence/THESIS_NUMERIC_BINDING.json'),official_result_selector=rec(O/'certificates/UNIFIED_RESULT_SELECTORS.json'),priority_scope=m['priority_scope'],stage_verdict=m['stage_verdict'],candidate_mechanism_implementation_gate=m['candidate_mechanism_implementation_gate'],action_counts=m['action_counts'],input_integrity=dict(direct_files=snap['direct_file_count'],unique_historical_files=836,embedded_fingerprint_records=4100,all_matched=True,all_historical_bytes_unchanged=True,snapshot=rec(O/'evidence/INPUT_SNAPSHOT.json'),embedded_checks=rec(O/'evidence/INPUT_FINGERPRINT_CHECK.json'),final_recheck=rec(O/'evidence/FINAL_INPUT_RECHECK.json')),inherited_seals=fprints['inherited_canonical_seals'],qa=dict(all_passed=True,check_count=len(checks),file=rec(O/'evidence/DOCUMENT_QA.json')),historical_inputs_read_only=True,historical_writes=0,files_exclude_manifest_itself=True,files=[rec(p) for p in sorted(O.rglob('*')) if p.is_file() and p!=O/'MANIFEST.json'],payload_hash_rule='SHA256 of canonical UTF8 JSON excluding payload_sha256;ensure_ascii=False,sort_keys=True,separators=(comma,colon). File-byte hash is distinct.')
manifest['payload_sha256']=canonical(manifest);dump(O/'MANIFEST.json',manifest)
assert all((O/name).is_file() for name in manifest['required_deliverables'])
assert canonical(load(O/'MANIFEST.json'))==manifest['payload_sha256']
assert all(rec(Path(x['path']))==x for x in manifest['files'])
print(json.dumps(dict(status=manifest['status'],adoption_verdict=manifest['adoption_verdict'],checks=len(checks),all_passed=True,L1_L2_L3='CLOSED',historical_files_unchanged=836,archived_certificate_files=21,sealed_payload_files=len(manifest['files']),manifest=rec(O/'MANIFEST.json')),ensure_ascii=False))
