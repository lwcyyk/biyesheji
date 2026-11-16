"""Document consistency, source preservation and deterministic seal; no cryptographic run."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re
BASE=Path(r'D:\毕业设计')
OUT=BASE/'crypto_fi_research_manuscript_v2_2'
OLD=BASE/'crypto_fi_research_manuscript_v2_1'
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def q(x):return F(int(x['numerator']),int(x['denominator']))
def check(name,ok):
 checks.append({'id':name,'passed':bool(ok)})
 assert ok,name
def payload_hash(obj):
 x=dict(obj);x.pop('payload_sha256',None)
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

m=load(OUT/'CLAIM_EVIDENCE_MATRIX.json')
oldm=load(OLD/'CLAIM_EVIDENCE_MATRIX.json')
c=load(OUT/'FINITE_CERTIFICATES.json')
r=load(OUT/'evidence/RECOMPUTED_CERTIFICATES.json')
execs=load(OUT/'evidence/REPLAY_EXECUTION.json')
patch=load(OUT/'evidence/MANUSCRIPT_PATCH_LEDGER.json')
draft=(OUT/'CRYPTOANALYSIS_DRAFT.md').read_text(encoding='utf-8')
ready=(OUT/'REVISION_AND_READINESS.md').read_text(encoding='utf-8')
human=(OUT/'HUMAN_REVIEW_ENTRY.md').read_text(encoding='utf-8')
check('version_v22',m['version']=='v2.2' and '研究稿v2.2' in draft)
check('unchanged_appendix_A',patch['unchanged_appendix_A'])
check('unchanged_appendix_D',patch['unchanged_appendix_D'])
check('CF1_model_exactly_retained',m['frozen_models']['CF1']==oldm['frozen_models']['CF1'])
check('old_uniform_model_exactly_retained',m['frozen_models']['640_ONE_UPDATE']==oldm['frozen_models']['640_ONE_UPDATE'])
oldprob=dict(oldm['probability_results']);nowprob=dict(m['probability_results'])
nowprob.pop('model_id');nowprob.pop('scope_note')
check('old_uniform_probability_payload_retained',oldprob==nowprob)
check('fixed_certificate_byte_equal_original',(OUT/'FINITE_CERTIFICATES.json').read_bytes()==(BASE/'crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json').read_bytes())
check('review_result_byte_equal_original',(OUT/'evidence/RECOMPUTED_CERTIFICATES.json').read_bytes()==(BASE/'crypto_fi_640_fixed_A_review/evidence/RECOMPUTED_CERTIFICATES.json').read_bytes())
check('replayed385_passed',r['check_count']==385 and r['all_passed'] and len(r['checks'])==385 and all(x['pass'] for x in r['checks']))
check('H_tail_exponent73',c['environment']['H']['certificate']['exponent']==73==r['H_tail']['exponent'])
check('R2_tail_exponent27',c['environment']['R2']['certificate']['exponent']==27==r['R2_tail']['exponent'])
check('initial_coordinate_exponent138',c['initial']['coordinate_tail_certificate']['exponent']==138==r['initial']['tail']['exponent'])
src=(BASE/'crypto_fi_640_fixed_A_correctness/evidence/compute_fixed_A.py').read_text(encoding='utf-8')
dst=(OUT/'certificates/compute_fixed_A.py').read_text(encoding='utf-8')
expected=src.replace("assert hc['exponent']>=70","assert hc['exponent']>=73\nassert (hn << 73) <= hd  # Direct acceptance threshold adopted in v2.2.")
check('author_copy_only_H73_hardening',expected==dst)
check('H73_direct_acceptance',"assert hc['exponent']>=73" in dst and 'assert (hn << 73) <= hd' in dst)
src=(BASE/'crypto_fi_640_fixed_A_review/evidence/recompute_certificates.py').read_text(encoding='utf-8')
dst=(OUT/'certificates/recompute_certificates.py').read_text(encoding='utf-8')
check('review_copy_only_new_input_path',dst==src.replace("SRC = OUT.parent / 'crypto_fi_640_fixed_A_correctness'","SRC = OUT  # Verify the regenerated v2.2 certificate."))
check('review_copy_direct_H73',"tail_check('H', hn, hd, 73," in dst)
check('current_runs_exactly_two',len(execs['runs'])==2 and all(x['exit_code']==0 for x in execs['runs']))
for i,x in enumerate(execs['runs']):
 for k in ['script','source','output']:
  check(f'execution_fingerprint_{i}_{k}',rec(Path(x[k]['path']))==x[k])
 if isinstance(x.get('input'),dict) and 'path' in x['input']:check('execution_input_fingerprint',rec(Path(x['input']['path']))==x['input'])
check('mass_matches_machine',c['chi']['mass_zero_and_each_sign']==m['fixed_A_probability_results']['exact_certificate']['chi']['mass_zero_and_each_sign'])
check('all49_nu_masses',len(c['nu']['mass'])==49 and sum(c['nu']['mass'].values())==2**32)
groups=c['frequency_groups'];covered=[t for g in groups for t in range(g['range'][0],g['range'][1]+1)]
check('complete_frequency_partition',covered==list(range(1,16385)))
check('new_high_rho',q(groups[-1]['rho'])==F(16156100186665515949,18446744073709551616))
Z=q(c['Z']);delta=q(c['environment']['adopted_delta']);U=q(c['row_and_full_correct_upper']);L=q(c['row_lower_Jensen'])
check('new_delta_2pow26',delta==F(1,2**26))
check('new_Z_exact',Z==F(4559006261671696450341,1208925819614629174706176))
check('U_formula_consistency',U==(1-delta)*(F(1,4**8)+F(21845,16384)*Z)+delta)
check('L_formula_consistency',L==((1-delta)*(F(1,4)-Z))**8)
aI=F(1,2**132);Uc=q(c['initial_correct_conditioned_row_and_full_upper']);Lc=q(c['initial_correct_conditioned_row_lower'])
check('initial_conditioning_upper',Uc==U/(1-aI))
check('initial_conditioning_lower',Lc==(L-aI)/(1-aI))
check('outward_new_upper',U<=Uc<=F('0.005043360'))
check('outward_new_lower',F('0.0000135117')<=Lc<=L)
check('new_full_error_endpoint',1-F('0.005043360')==F('0.994956640'))
check('fixed_A_machine_model',m['fixed_A_probability_results']['model_id']==m['frozen_models']['640_FIXED_A_ONE_UPDATE']['label'])
check('uniform_machine_model',m['probability_results']['model_id']==m['frozen_models']['640_ONE_UPDATE']['label'])
check('each_model_has_own_selector',m['probability_results_by_model']['UNIFORM_SETUP']['result_selector']!=m['probability_results_by_model']['EVERY_PREFIXED_A']['result_selector'])
for doc_name,text in [('draft',draft),('readiness',ready),('human',human)]:
 check(doc_name+'_two_upper_endpoints','0.000030345' in text and '0.005043360' in text)
 check(doc_name+'_two_error_endpoints','99.9969655%' in text and '99.4956640%' in text)
 check(doc_name+'_new_row_lower','0.0000135117' in text)
 check(doc_name+'_initial_failure','2^-132' in text)
 check(doc_name+'_waiting_status','WAITING_FOR_AUTHOR_ARTIFACT' in text)
 check(doc_name+'_zero_replacement_char','\ufffd' not in text)
 check(doc_name+'_no_prohibited_binary_construction',not re.search(r'不是[^。\n]{0,300}而是',text))
check('draft_fixed_theorem_all_conditions',all(v in draft.split('**命题640-FA。**',1)[1].split('**证明概要。**',1)[0] for v in ['n=640','D=15','q=32768','m̄=n̄=8','B=2','全部相关原始χ','给定A后','独立乘积律','两代共用A','128位消息','预先指定行','未筛选','平局向上']))
check('no_stale_public_A_responsibility','可靠性的H重量证书则使用真正均匀A，公开seed展开A需另证对应环境概率' not in draft)
check('body_event_inclusion', 'K⊆J' in draft and '行下界L的对象为J' in draft)
check('explicit_conditional_event_ratios',r'\frac{L-a_I}{1-a_I}' in draft and r'\frac{U}{1-a_I}' in draft)
check('appendixE_five_FA_sections',all('FA'+str(k) in draft.split('## 附录E')[1] for k in range(1,6)))
check('appendixE_condition_release_ledger','解除条件台账' in draft and '每个固定A保持同常数' in draft)
check('reproduction_entry_v22','v2.2' in human and '附录E.1–E.2' in human and '附录E.3–E.4' in human and 'E.5–E.9' in human)
check('human_three_decisive_questions',all('H'+str(k)+'：' in human for k in (1,2,3)))
check('same_math_method_attribution','公开矩阵量词扩展及迁移前提缩减' in draft and '经典' in draft)

tables=load(OLD/'evidence/DISTRIBUTION_TABLES.json');table_results=[]
for name,v in tables['profiles'].items():
 match=re.search(r'^\| '+name+r' \| ([0-9,]+) \|$',draft,re.M)
 check('display_table_present_'+name,match is not None)
 row=[int(z) for z in match.group(1).split(',')]
 cdf=v['cdf'];derived=[2*(cdf[0]+1)]+[cdf[j]-cdf[j-1] for j in range(1,len(cdf))]
 check('display_CDF_certificate_mass_'+name,row==derived==v['official_mass']==v['mass_zero_then_each_signed_value'])
 w={x:row[abs(x)] for x in range(-v['s'],v['s']+1)}
 check('table_total_'+name,sum(w.values())==65536)
 check('table_support_'+name,all(z>0 for z in w.values()) and len(w)==2*v['s']+1)
 check('table_symmetry_'+name,all(w[x]==w[-x] for x in w))
 check('table_parity_'+name,sum(w[x] for x in w if x%2==0)==v['even_numerator'] and sum(w[x] for x in w if x%2)==v['odd_numerator'])
 table_results.append({'n':name,'display_mass':row,'source_table':rec(OLD/'evidence/DISTRIBUTION_TABLES.json'),'CDF_derived_mass':derived,'current_scope':'Display/CDF-formula/historical certificate-input comparison only; no full convolution replay in v2.2'})
write(OUT/'evidence/DISPLAY_TABLE_RECHECK.json',{'profiles':table_results,'full_976_replay_this_round':False,'prior_full976_replay':'v2.1 E9; retained by source fingerprints'})

claim_map={v['id']:v for v in m['claims']}
check('claim_ids_unique',len(claim_map)==len(m['claims'])==46)
for id,cclaim in claim_map.items():
 check('claim_dependencies_exist_'+id,all(d in claim_map for d in cclaim.get('dependencies',[])))
 check('claim_sources_exist_'+id,all(s in m['source_registry'] for s in cclaim.get('source_ids',[])))
def closure(id,ancestors=()):
 assert id not in ancestors,('cycle',ancestors,id)
 result={id}
 for dep in claim_map[id].get('dependencies',[]):result.update(closure(dep,ancestors+(id,)))
 return result
for name,v in m['main_result_dependency_audit'].items():
 ids=closure(v['root_claim'])
 check('dependency_closure_'+name,ids==set(v['transitive_claim_dependencies']))
 check('no976_dependency_'+name,'C10_976' not in ids)
check('new_claims_registered',all('C'+str(i) in claim_map for i in range(29,39)))
check('new_fixed_A_claim_scope','Every A fixed before' in str(claim_map['C29']['assumptions']))
check('H73_claim_registered','2^-73' in claim_map['C30']['quantifiers'])
check('public_seed_claim_registered',not m['implementation_model_migration']['new_fixed_A_public_A_distribution_responsibility_removed']==False)
check('all6_author_mappings_unresolved',len(m['implementation_model_migration']['config_mappings'])==6 and all(v['result_B_fixed_A_transfer']=='UNRESOLVED' for v in m['implementation_model_migration']['config_mappings']))
check('author_trace_zero',m['implementation_model_migration']['author_UE_message_checked_traces']==0)
check('review_exact_identity',m['fixed_A_review_identity']['status']=='AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW')
check('review_exact_backend_null',m['fixed_A_review_identity']['exact_backend_model_id'] is None)
check('current_backend_null',m['identity']['exact_backend_model_id'] is None)
check('current_no_new_independent_reviews',m['identity']['new_independent_reviews']==0)
check('every_correction_closed',all(re.search(r'\| '+re.escape(id)+r' \|.*CLOSED',ready) for id in m['v2_2_correction_ids']))

# Check all literal local links and bind old/new link targets to actual bytes.
linked={}
for name in ['CRYPTOANALYSIS_DRAFT.md','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md','evidence/appendix_E.md']:
 p=OUT/name
 # Displayed TeX such as [1-(1-p)^n](1-epsilon) is a product, not a file link.
 link_text=re.sub(r'\\\[.*?\\\]','',p.read_text(encoding='utf-8'),flags=re.S)
 for dest in re.findall(r'\]\(([^\n)]+)\)',link_text):
  dest=dest.strip('<>')
  if dest.startswith(('https://','http://','#')):continue
  target=Path(dest)
  if not target.is_absolute():target=p.parent/target
  target=target.resolve()
  if target==OUT/'MANIFEST.json':continue
  check('local_link_'+name+'_'+str(len(linked)),target.is_file())
  linked[str(target)]=rec(target)
write(OUT/'evidence/LINKED_SOURCE_FINGERPRINTS.json',{'scope':'Literal local Markdown targets excluding not-yet-written manifest; current bytes, separate from initial historical snapshot','files':sorted(linked.values(),key=lambda x:x['path'])})

seals=[]
for p in [OLD/'MANIFEST.json',BASE/'crypto_fi_author_implementation_audit/VERDICT.json']:
 x=load(p);ok=payload_hash(x)==x['payload_sha256']
 check('historical_canonical_seal_'+p.parent.name,ok)
 seals.append({'file':rec(p),'payload_sha256':x['payload_sha256'],'canonical_payload_matched':ok})
snapshot=load(OUT/'evidence/INPUT_SNAPSHOT.json')
changes=[]
for item in snapshot['files']:
 now=rec(Path(item['path']))
 if now!=item:changes.append({'before':item,'after':now})
check('all338_historical_files_unchanged',not changes and len(snapshot['files'])==338)
recheck={'schema':'frodo-fi-v22/input-recheck/1','historical_file_count':len(snapshot['files']),'all_unchanged':not changes,'changes':changes}
write(OUT/'evidence/INPUT_RECHECK.json',recheck)
finger=load(OUT/'evidence/INPUT_FINGERPRINT_CHECK.json')
check('1789_embedded_fingerprints_matched',finger['records_checked']==1789 and finger['all_matched'])
for name in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md']:
 check('required_payload_exists_'+name,(OUT/name).is_file() and (OUT/name).stat().st_size>0)
qa={'schema':'frodo-fi-v22/document-qa/1','date_asia_shanghai':'2026-11-11','check_count':len(checks),'all_passed':True,'checks':checks,'scope':'Consistency, source bindings, targeted arithmetic endpoint comparisons and historical preservation. The mathematical385-check replay is a separately recorded execution; this QA provides no independent cryptographic-review certificate.','local_link_targets_checked':len(linked),'historical_files_unchanged':338}
write(OUT/'evidence/DOCUMENT_QA.json',qa)
manifest={'schema':'frodo-fi-manuscript-manifest/v2.2','version':'v2.2','date_asia_shanghai':'2026-11-11','sealed_at_asia_shanghai':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'status':'SEALED_V2_2_FIXED_A_INTEGRATED_H73_REPLAYED','root':str(OUT),'required_deliverables':['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md','MANIFEST.json'],'identity':m['identity'],'scope':'Informed author revision, proof integration and deterministic finite mathematics. No candidate cryptographic mechanism implemented. Historical inputs read-only.','frozen_models':m['frozen_models'],'probability_results_by_model':m['probability_results_by_model'],'fixed_A_results':{k:v for k,v in m['fixed_A_probability_results'].items() if k!='exact_certificate'},'main_result_dependency_audit':m['main_result_dependency_audit'],'implementation_model_migration':m['implementation_model_migration'],'review_record':{'historical_review':rec(BASE/'crypto_fi_640_fixed_A_review/REVIEW_VERDICT.json'),'identity':m['fixed_A_review_identity'],'original_check_count':385,'current_replay_check_count':385,'current_replay_record':rec(OUT/'evidence/REPLAY_EXECUTION.json')},'correction_status':[{'id':id,'status':'CLOSED','table':'REVISION_AND_READINESS.md §2'} for id in m['v2_2_correction_ids']],'input_integrity':{'direct_file_count':snapshot['direct_file_count'],'unique_historical_file_count':len(snapshot['files']),'embedded_fingerprint_records':finger['records_checked'],'all_reference_fingerprints_matched':True,'all_historical_bytes_unchanged':True,'snapshot':rec(OUT/'evidence/INPUT_SNAPSHOT.json'),'embedded_check':rec(OUT/'evidence/INPUT_FINGERPRINT_CHECK.json'),'final_recheck':rec(OUT/'evidence/INPUT_RECHECK.json')},'historical_inputs_read_only':True,'historical_writes':0,'inherited_canonical_seals':seals,'arithmetic_entrypoints':[rec(OUT/'certificates/compute_fixed_A.py'),rec(OUT/'certificates/recompute_certificates.py')],'qa':{'document_check_count':len(checks),'all_passed':True,'file':rec(OUT/'evidence/DOCUMENT_QA.json'),'finite385_check_replay':'Separately recorded; no double-counted independent-review claim'},'readiness':'READY_FOR_HUMAN_CRYPTOGRAPHIC_REVIEW_WITH_EXTERNAL_ITEMS','external_evidence_pending':['Authenticated author UE commit/archive and640 config; conditional secret-noise law, formulas/filtering/Ord/arithmetic and a message-checked trace','Full FI Lemma6.8/LWE reduction with exact sample and auxiliary-view contract; fixed n/3n premise remains unresolved','Version-authenticated Nishimaki2024 extended Lemma5.7 and CJL original-PDF correspondence','Human cryptographic review and global application priority; fixed-A extension has no new literature search this round'],'next_external_input':'Paper/author/institution-authenticated UE artifact plus source-mapped640 randomness/arithmetic configuration and one honest unfiltered original/initial/updated-message comparison trace','adopted_application_priority':m['adopted_publication_impact_audit'],'current_new_priority_searches':0,'action_counts':m['action_counts'],'INC976':{'status':'CLOSED_IN_V2_1_RETAINED','full_convolution_replayed_current_round':False,'three_display_rows_currently_checked_against_CDF_formula_and_historical_inputs':True,'A_BU_BFA_have_no976_dependency':True},'files_exclude_manifest_itself':True,'files':[rec(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'MANIFEST.json'],'manifest_integrity_definition':'SHA256 of canonical UTF8 JSON omitting payload_sha256; json.dumps(ensure_ascii=False,sort_keys=True,separators=(comma,colon)). File-byte hash is distinct.'}
manifest['payload_sha256']=payload_hash(manifest)
write(OUT/'MANIFEST.json',manifest)
assert (OUT/'MANIFEST.json').is_file()
assert payload_hash(load(OUT/'MANIFEST.json'))==manifest['payload_sha256']
assert all(rec(Path(x['path']))==x for x in manifest['files'])
print(json.dumps({'status':manifest['status'],'document_QA_checks':len(checks),'all_passed':True,'scalar_checks_replayed':385,'historical_files_unchanged':338,'sealed_payload_files':len(manifest['files']),'manifest':rec(OUT/'MANIFEST.json'),'payload_sha256':manifest['payload_sha256']},ensure_ascii=False))
