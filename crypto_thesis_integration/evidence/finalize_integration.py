"""Document/source/claim consistency seal; no system or cryptographic experiment."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re
B=Path(r'D:\毕业设计');O=B/'crypto_thesis_integration';C=B/'crypto_fi_adopted_release_v3_1'
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sh(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def rd(v):return F(int(v['numerator']),int(v['denominator']))
def ck(id,truth):
 checks.append(dict(id=id,passed=bool(truth)));assert truth,id
def canonical(x):
 x=dict(x);x.pop('payload_sha256',None)
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
status=load(O/'INTEGRATION_STATUS.json');sources=load(O/'evidence/SOURCE_REGISTRY.json');snapshot=load(O/'evidence/INPUT_SNAPSHOT.json');reuse=load(O/'evidence/CHAPTER_REUSE_MAP.json');patches=load(O/'evidence/INSERTION_PATCHES.json');nb=load(O/'evidence/NUMERIC_BINDING.json')
texts={name:(O/name).read_text(encoding='utf-8') for name in ['THESIS_INTEGRATION_PLAN.md','INTEGRATED_CRYPTO_CHAPTER.md','DEFENSE_CLAIM_CARD.md']}
plan=texts['THESIS_INTEGRATION_PLAN.md'];chapter=texts['INTEGRATED_CRYPTO_CHAPTER.md'];card=texts['DEFENSE_CLAIM_CARD.md']
adopt=load(C/'MANIFEST.json');matrix=load(C/'CLAIM_EVIDENCE_MATRIX.json');selectors=load(C/'certificates/UNIFIED_RESULT_SELECTORS.json')
ck('adopted_status_retained',status['adopted_crypto']['status']=='ADOPTED_V3_1_AND_ARCHIVED' and status['adopted_crypto']['verdict']=='PASS_WITHIN_STATED_SCOPE')
ck('adopted_manifest_canonical_payload',canonical(adopt)==adopt['payload_sha256'])
for i,r in enumerate(adopt['files']):ck('adopted_payload_'+str(i),rec(Path(r['path']))==r)
ck('complete_adopted_profile_payload',selectors['profiles']==matrix['official_profile_results'])
ck('no_new_math_review',status['current_identity']['new_mathematical_reviews']==0 and not status['adopted_crypto']['new_review_in_this_integration'])
ck('exact_final_AI_identity',status['adopted_crypto']['final_review_type']=='SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE')
ck('exact_final_exposure_record',status['adopted_crypto']['final_review_exposure']==matrix['adoption_record']['exposure'])
ck('exact_backend_not_invented',status['adopted_crypto']['final_review_model']['exact_backend_model_id'] is None and status['current_identity']['exact_backend_model_id'] is None)
for r in reuse['blocks']:
 ck('reused_'+r['id']+'_source_hash',rec(Path(r['source']['path']))==r['source'])
 ck('reused_'+r['id']+'_adopted_text_hash',sh(r['adopted_text'])==r['adopted_text_sha256'])
 ck('reused_'+r['id']+'_actually_in_chapter',r['adopted_text'] in chapter)
ck('six_reused_adoption_blocks',len(reuse['blocks'])==6)
ck('chapter_X_sections_complete',all('## X.'+str(i)+' ' in chapter for i in range(1,9)))
ck('chapter_precision_and_rounding_contract',all(s in chapter for s in ['Ord_n','Tensor_D','独立乘积律','诚实未筛选','所有P₂秩','平局向上Decode','两代共用A']))
ck('chapter_shortest_original_game_trace',all(s in chapter for s in ['Enc₀(M)','Next','Corr(token,1)','Challenge₁(M,C)','挑战后结束']))
ck('chapter_CF1_parameters_and_cost',all(s in chapter for s in ['λ≥2','n=8λ','D=8⌈log₂n⌉','q=2^D','T=t_max=n','3n+1','最长n次','Δ_n']))
ck('chapter_full_true_residual',all(s in chapter for s in ['U_0E_{old}','F_0S_{old}','HU_1+RU_2','HF_1+RF_2','HG_1+RG_2']))
ck('chapter_mixed_row_and_event_containment','p_row=E[p(V)^8]' in chapter and 'K⊆J' in chapter)
ck('chapter_half_up_sets_and_source_conditions','官方最近整数平局向上Decode' in chapter and '初始完整消息已正确' in chapter)
ck('chapter_Theorem63_and_69_precise',all(s in chapter for s in ['Theorem6.3','22649448960','32387837760','13265908992','Theorem6.9','固定n/3n']))
for n,p in selectors['profiles'].items():
 ck(n+'/message_length_in_chapter',str(p['parameters']['message_bits']) in chapter)
 ck(n+'/initial_failure_in_chapter',f"2^-{p['initial']['full_failure_power']}" in chapter)
 for mode in ['fixed_A','uniform_Setup']:
  v=p[mode];alpha=F(1,2**p['initial']['full_failure_power']);U=rd(v['full_correct_upper']);UC=rd(v['conditioned_on_initial']['full_correct_upper']);disp=F(v['display']['row_full_upper'])
  ck(n+'/'+mode+'/exact_conditional_and_display',UC==min(F(1),U/(1-alpha)) and U<=UC<=disp)
  ck(n+'/'+mode+'/error_percent',F(v['display']['full_error_percent_lower'].rstrip('%'))==100*(1-disp))
  ck(n+'/'+mode+'/both_displays_in_chapter',v['display']['row_full_upper'] in chapter and v['display']['full_error_percent_lower'].rstrip('%')+'%' in chapter)
ck('numeric_binding_six_rows',len(nb['six_model_rows'])==6 and nb['all_profiles_equal_adopted_matrix'])
ck('chapter_quantifiers_distinct',all(s in chapter for s in ['逐固定A列不对A平均','独立均匀全矩阵A平均','条件于相应I']))
ck('mature_methods_attributed',all(s in chapter for s in ['Klooß','Arora','Chernoff','Diaconis','具体对象增量']))
ck('chapter_bibliography_local_not_fabricated_global','本章内[1—6]' in chapter and status['main_manuscript_authority']['actual_final_chapter_number'] is None)
ck('current_master_is_unconfirmed',status['main_manuscript_authority']['status']=='CURRENT_MASTER_UNCONFIRMED' and status['main_manuscript_authority']['whole_current_master_path'] is None)
ck('history_authority_version_and_structure',status['main_manuscript_authority']['historical_date']=='2026-11-04' and status['main_manuscript_authority']['historical_chapter_count']==7)
ck('no_latest_mtime_authority_claim','不构成全篇权威指定' in plan and 'CURRENT_MASTER_UNCONFIRMED' in plan)
ck('proposed_position_independent_chapter',status['placement']['kind']=='INDEPENDENT_THEORETICAL_CHAPTER_WITH_COMPONENT_SECURITY_CASE_ROLE' and status['placement']['after']=='system implementation/empirical evaluation')
ck('historical_7_discussion_8_suggestion',status['main_manuscript_authority']['suggested_chapter_in_historical_skeleton']==7 and status['main_manuscript_authority']['suggested_old_discussion_number']==8)
ck('research_question_added_with_scope','RQ-C' in plan and '新增研究子问题' in plan)
ck('plan_all10_slots',all('| P'+str(i)+' ' in plan for i in range(10)))
ck('plan_four_direct_prose_snippets',all(x in plan for x in ['**摘要插入段：**','**绪论贡献段：**','**章节小结段：**','**总论文结论增补段：**']))
ck('all_patches_unapplied',not patches['original_files_modified'] and patches['not_a_formal_new_whole_master'])
for p in patches['patches']:
 if p.get('baseline'):
  ck(p['id']+'/baseline_bytes_guard',rec(Path(p['baseline']['path']))==p['baseline'])
  text=Path(p['baseline']['path']).read_text(encoding='utf-8');needle=p.get('old_text') or p['anchor']
  ck(p['id']+'/unique_exact_anchor',text.count(needle)==1)
  ck(p['id']+'/line_guard',text[:text.index(needle)].count('\n')+1==p['baseline_line'])
  ck(p['id']+'/full_replacement_or_insertion_text',bool(p['new_text'].strip()))
ck('fifteen_guarded_or_pending_patches',len(patches['patches'])==15)
ck('no_three_vs_four_contribution_conflict',any(p['id']=='P2B' and p['operation']=='replace_exact_paragraph' and '四类' in p['new_text'] for p in patches['patches']))
ck('early_crypto_archive_statement_updated',any(p['id']=='P4' and '早期' in p['new_text'] and '已在v3.1' in p['new_text'] for p in patches['patches']))
ck('discussion_three_chain_heading_updated',any(p['id']=='P7H' and '分层证据链' in p['new_text'] for p in patches['patches']))
ck('latest_DCL_version_bound',status['current_mainline']['DCL_version']=='DCL-R6-batch05')
dcl=status['current_mainline']['DCL_state']
ck('latest_resource_failure_not_upgraded',dcl['resource_gate']=='RESOURCE_GATE_FAILED' and dcl['F1_F4']=='UNRUN_RESOURCE_GATE' and dcl['PASS_BOUNDED']==0 and dcl['implementation_gate']=='CLOSED')
ck('C09H_counts_not_protocol_runs',dcl['C09H']==dict(total=34,pass_count=28,mutation_detected=6) and dcl['C00_C08_pass']==9)
ck('G2_local_engineering_and_H2_separate',status['current_mainline']['G2_A1_implemented_with_synthetic_acceptance'] and not status['current_mainline']['G2_H2_environment_locked'] and status['current_mainline']['G2_real_authority_read']=='NOT_RUN')
ck('M_r_keeps_priority_native_conditions','priority nearest-neighbor unresolved' in status['current_mainline']['M_r_scope'])
ck('system_FI_mapping_not_invented',status['system_crypto_relation']['UE_FI_integration']=='NOT_ESTABLISHED_IN_REVIEWED_CHAIN' and status['system_crypto_relation']['FI_token_to_business_handle_or_AT_RT_mapping']=='NOT_ESTABLISHED')
search=load(O/'evidence/BOUNDED_UE_SOURCE_SEARCH.json')
ck('bounded_source_query_no_matches',search['exit_code']==1 and search['stdout']=='' and search['runtime_modules_imported_or_executed']==0)
ck('negative_query_scope_honest','does not prove absence' in search['interpretation'])
ck('selected_storage_is_AESGCM','AESGCM' in Path(sources['sources']['CURRENT_STORAGE']['path']).read_text(encoding='utf-8'))
ck('two_chains_in_all_docs',all(('证据链' in s and ('系统' in s or '主系统' in s)) for s in texts.values()))
ck('defense_minimum7_questions',all('### Q'+str(i)+' ' in card for i in range(1,8)))
ck('defense10_answers',all('### Q'+str(i)+' ' in card for i in range(1,11)))
claimids=['CF-I','CF-A','CF-B','CF-P','SYS-C','SYS-T','SYS-E','SYS-D','SYS-R','SYS-A1','LINK-C']
ck('all11_claim_rows_registered',all('| '+id+'：' in card for id in claimids))
ck('six_required_claim_table_fields',all(s in card for s in ['主张','新增内容','已有方法基础','证据入口','适用范围','当前状态']))
ck('strict_instance_gate_kept',all('严格' in s and '必须' in s and '代价' in s for s in [plan,card]) and 'necessarily higher cost' in status['candidate_mechanism_gate'])
ck('no_new_system_or_crypto_execution',all(v==0 for v in status['actions'].values()))
links={}
for name,s in texts.items():
 ck(name+'/encoding_and_control_characters','\ufffd' not in s and not any(ord(ch)<32 and ch not in '\r\n\t' for ch in s))
 ck(name+'/user_style',not re.search(r'不是[^。\n]{0,300}而是',s))
 ck(name+'/contribution_phrase',status['adopted_crypto']['contribution_phrase'] in s)
 s=re.sub(r'\\\[.*?\\\]','',s,flags=re.S)
 for dest in re.findall(r'\]\(([^\n)]+)\)',s):
  dest=dest.strip('<>')
  if dest.startswith(('https://','http://','#')):continue
  # Optional file-link line number is UI metadata, not part of the filesystem name.
  dest=re.sub(r':\d+$','',dest)
  p=Path(dest)
  if not p.is_absolute():p=O/p
  p=p.resolve()
  if p==O/'INTEGRATION_STATUS.json':continue
  ck('local_link_'+name+'_'+str(len(links)),p.is_file())
  links[str(p)]=rec(p)
dump(O/'evidence/LINKED_SOURCE_FINGERPRINTS.json',dict(files=sorted(links.values(),key=lambda x:x['path']),scope='All literal local links in the3 prose artifacts;line suffix anddisplay-math handled'))
changes=[]
for r in snapshot['files']:
 now=rec(Path(r['path']))
 if now!=r:changes.append(dict(before=r,after=now))
ck('238_historical_inputs_unchanged',len(snapshot['files'])==238 and not changes)
dump(O/'evidence/FINAL_INPUT_RECHECK.json',dict(files_rechecked=len(snapshot['files']),all_unchanged=not changes,changes=changes))
for name in ['THESIS_INTEGRATION_PLAN.md','INTEGRATED_CRYPTO_CHAPTER.md','DEFENSE_CLAIM_CARD.md']:
 ck('required_payload_'+name,(O/name).is_file() and (O/name).stat().st_size>0)
qa=dict(schema='crypto-thesis-integration/document-qa/1',date_asia_shanghai='2026-11-11',all_passed=True,check_count=len(checks),checks=checks,scope='Adopted-text reuse,numeric/model/claim/version consistency,unapplied insertion guards andsource byte preservation;not a new cryptographic orsystem review',historical_files_unchanged=238,local_link_targets=len(links))
dump(O/'evidence/DOCUMENT_QA.json',qa)
status['seal_state']='SEALED_COMPLETE';status['sealed_at_asia_shanghai']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
status['qa']=dict(all_passed=True,check_count=len(checks),file=rec(O/'evidence/DOCUMENT_QA.json'))
status['input_integrity']=dict(adopted_release_files_verified=len(adopt['files']),adopted_manifest_payload_hash_matched=True,historical_input_files=238,all_bytes_unchanged=True,snapshot=rec(O/'evidence/INPUT_SNAPSHOT.json'),final_recheck=rec(O/'evidence/FINAL_INPUT_RECHECK.json'))
status['math_reuse_and_data_binding']=dict(reuse_map=rec(O/'evidence/CHAPTER_REUSE_MAP.json'),numeric_binding=rec(O/'evidence/NUMERIC_BINDING.json'),all_adopted_models_and_displays_retained=True)
status['files_exclude_status_itself']=True
status['files']=[rec(p) for p in sorted(O.rglob('*')) if p.is_file() and p!=O/'INTEGRATION_STATUS.json']
status['payload_hash_rule']='SHA256 of canonical UTF8 JSON excluding payload_sha256;ensure_ascii=False,sort_keys=True,separators=(comma,colon). File-byte hash distinct.'
status['payload_sha256']=canonical(status);dump(O/'INTEGRATION_STATUS.json',status)
assert canonical(load(O/'INTEGRATION_STATUS.json'))==status['payload_sha256']
assert all(rec(Path(r['path']))==r for r in status['files'])
assert all((O/name).is_file() for name in status['required_deliverables'])
print(json.dumps(dict(status=status['status'],seal=status['seal_state'],current_master=status['main_manuscript_authority']['status'],checks=len(checks),all_passed=True,historical_files_unchanged=238,guarded_or_pending_patches=len(patches['patches']),sealed_payload_files=len(status['files']),status_file=rec(O/'INTEGRATION_STATUS.json')),ensure_ascii=False))
