"""Cross-document/certificate consistency and historical-byte preservation seal."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re,struct
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_research_manuscript_v3';OLD=BASE/'crypto_fi_research_manuscript_v2_2'
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def rd(v):return F(int(v['numerator']),int(v['denominator']))
def ck(tag,condition):
 checks.append(dict(id=tag,passed=bool(condition)))
 assert condition,tag
def canonical(x):
 x=dict(x);x.pop('payload_sha256',None)
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

m=load(OUT/'CLAIM_EVIDENCE_MATRIX.json');p=load(OUT/'certificates/UNIFIED_RESULT_SELECTORS.json')['profiles']
cert=load(OUT/'certificates/OFFICIAL_PROFILE_CERTIFICATES.json');replay=load(OUT/'evidence/REPLAY_EXECUTION.json')
patch=load(OUT/'evidence/MANUSCRIPT_PATCH_LEDGER.json')
texts={name:(OUT/name).read_text(encoding='utf-8') for name in ['CRYPTOANALYSIS_DRAFT.md','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md']}
draft=texts['CRYPTOANALYSIS_DRAFT.md']
expected={'640':dict(D=15,q=32768,B=2,bits=128,alpha=132,coord=138,fa='0.005043360',faerr='99.4956640',un='0.000030345',unerr='99.9969655'),
          '976':dict(D=16,q=65536,B=3,bits=192,alpha=193,coord=199,fa='0.078020625',faerr='92.1979375',un='0.017137631',unerr='98.2862369'),
          '1344':dict(D=16,q=65536,B=4,bits=256,alpha=246,coord=252,fa='0.206115312',faerr='79.3884688',un='0.082813443',unerr='91.7186557')}
ck('version_v3',m['version']=='v3' and '研究稿v3' in draft)
ck('attack_sections_3_to_6_unchanged',patch['unchanged_attack_sections_3_to_6'])
ck('appendix_A_unchanged',patch['unchanged_appendix_A'])
ck('unified_selector_payload_matches_matrix',p==m['official_profile_results'])
ck('three_profiles',set(p)==set(expected))
for n,e in expected.items():
 par=p[n]['parameters'];initial=p[n]['initial'];pi=F(1,2**e['B']);alpha=F(1,2**e['alpha'])
 ck(n+'/parameters',(par['n'],par['D'],par['q'],par['B'],par['mbar'],par['nbar'],par['message_bits'])==(int(n),e['D'],e['q'],e['B'],8,8,e['bits']))
 ck(n+'/initial_powers',initial['full_failure_power']==e['alpha'] and initial['coordinate_failure_power']==e['coord'] and e['coord']-6==e['alpha'])
 for mode,display,error,averages in [('fixed_A',e['fa'],e['faerr'],False),('uniform_Setup',e['un'],e['unerr'],True)]:
  v=p[n][mode];upper=rd(v['full_correct_upper']);conditional=rd(v['conditioned_on_initial']['full_correct_upper']);Z=rd(v['Z']);delta=rd(v['adopted_delta'])
  C=sum(pi**j for j in range(8));f=pi**8+C*Z;UJ=(1-delta)*min(F(1),f,pi+Z)+delta
  ck(n+'/'+mode+'/A_quantifier',v['averages_A']==averages)
  ck(n+'/'+mode+'/upper_formula',upper==UJ)
  ck(n+'/'+mode+'/row_to_full',upper==rd(v['row_correct_upper']))
  ck(n+'/'+mode+'/I_conditioning',conditional==min(F(1),upper/(1-alpha)))
  ck(n+'/'+mode+'/outward_endpoint',upper<=conditional<=F(display)==F(v['display']['row_full_upper']))
  ck(n+'/'+mode+'/error_percent',100*(1-F(display))==F(error)==F(v['display']['full_error_percent_lower'].rstrip('%')))
  lower=rd(v['row_correct_lower']);clower=rd(v['conditioned_on_initial']['row_correct_lower'])
  ck(n+'/'+mode+'/row_lower_conditioning',clower==max(F(0),(lower-alpha)/(1-alpha)))
  ck(n+'/'+mode+'/row_display_lower',F(v['display']['row_lower'])<=clower<=lower)
  if n!='640':
   ck(n+'/'+mode+'/local_Jensen',lower==(1-delta)*max(F(0),pi-Z)**8)
   ck(n+'/'+mode+'/all_frequencies',[t for g in v['frequency_groups'] for t in range(g['range'][0],g['range'][1]+1)]==list(range(1,32769)))
   ck(n+'/'+mode+'/all_difference_mass_accounted',v['unused_difference_mass_upper']==1 and v['uncharged_truncation_loss']==0)
   ck(n+'/'+mode+'/directed_slack',rd(v['dyadic_slack_already_in_Z'])<F(1,2**41))
   ck(n+'/'+mode+'/scalar_I_display',F(v['display']['scalar_lower'])<=rd(v['conditioned_on_initial']['scalar_correct_lower']) and rd(v['conditioned_on_initial']['scalar_correct_upper'])<=F(v['display']['scalar_upper']))
  else:
   ck(n+'/'+mode+'/legacy_Jensen_lower_valid',lower<=((1-delta)*max(F(0),pi-Z)**8))
   if mode=='uniform_Setup':
    ck('640/uniform/legacy_scalar_exact_ratios',rd(v['conditioned_on_initial']['scalar_correct_lower'])==(rd(v['scalar_correct_lower'])-alpha)/(1-alpha) and rd(v['conditioned_on_initial']['scalar_correct_upper'])==rd(v['scalar_correct_upper'])/(1-alpha))
    ck('640/uniform/scalar_display_survives_I',F(v['display']['scalar_lower'])<=rd(v['conditioned_on_initial']['scalar_correct_lower']) and rd(v['conditioned_on_initial']['scalar_correct_upper'])<=F(v['display']['scalar_upper']))
 for name,text in texts.items():
  ck(n+'/'+name+'/all_six_requested_endpoints',all(s in text for s in [e['fa'],e['faerr']+'%',e['un'],e['unerr']+'%',f'2^-{e["alpha"]}']))
  ck(n+'/'+name+'/message_length',str(e['bits']) in text)

# Meaningful endpoint consistency: the identity determines F>=1 exactly.
for k in [1,2,8]:
 for pi in [F(0),F(1,16),F(1,8),F(1,4),F(1,2),F(1)]:
  C=sum(pi**j for j in range(k))
  for Z in [F(0),F(1,100),pi,1-pi,F(1),F(2)]:
   f=pi**k+C*Z
   assert f-1==C*(Z-(1-pi))
   if f>=1:assert min(F(1),f,pi+Z)==1
ck('parametric_F_endpoint_identity_and_U1',True)
for word in ['π₀=0','π₀=1','k=1','δ=1','Z≥π₀','F≥1','B=0','B=D','α=1']:
 ck('explicit_endpoint_'+word,word in draft)
ck('finite_sum_first_Ck',draft.index('C_k(\\pi_0):=\\sum')<draft.index('C_k=(1−π₀^k)/(1−π₀)'))
ck('parametric_upper_exact_form',r'\min\{1,F,\pi_0+Z\}' in draft)
ck('conditional_ratios_clipped',r'\max\{0,(L_E-\alpha)/(1-\alpha)\}' in draft)
ck('full_event_containment_and_separate_lower','K⊆J' in draft and 'γ_n=a₀^(24n)' in draft)
ck('no_false_F_ge_one_improvement','其值可能小于1' not in draft and 'UJ=1' in m['parametric_criterion']['endpoints']['F_ge_one'])
ck('correct_two_layer_and_product_power','2n个系数' in draft and 'D_t^n' in draft)
ck('all_source_theorem63_numbers',all(str(z) in draft for z in [22649448960,32387837760,13265908992,27434188800,10404495360]))
ck('new_depth_research_scoped','一次更新定理的诚实父合同分别核准' in draft)
ck('no_stale9761344_pending','976/1344的更新解码可靠性、更深更新' not in draft and '976的解码可靠性仍属于' not in draft)

tables=load(BASE/'crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json');display_binding=[]
fa640=load(OUT/'certificates/640_FIXED_A_CERTIFICATES.json')
for n,table in tables['profiles'].items():
 line=re.search(r'^\| '+n+r' \| ([0-9,]+) \|$',draft,re.M)
 ck(n+'/display_row_present',line is not None)
 shown=[int(v) for v in line[1].split(',')];cdf=table['cdf']
 derived=[2*(cdf[0]+1)]+[cdf[i]-cdf[i-1] for i in range(1,len(cdf))]
 certmass=fa640['chi']['mass_zero_and_each_sign'] if n=='640' else cert['profiles'][n]['distribution']['mass_zero_then_each_sign']
 ck(n+'/display_equals_CDF_equals_certificate_input',shown==derived==certmass==table['official_mass'])
 mass={x:shown[abs(x)] for x in range(-table['s'],table['s']+1)}
 ck(n+'/normalized_symmetric_support',sum(mass.values())==65536 and all(mass[x]==mass[-x]>0 for x in mass))
 ck(n+'/true_parity',sum(v for x,v in mass.items() if x%2==0)==table['even_numerator'] and sum(v for x,v in mass.items() if x%2)==table['odd_numerator'])
 display_binding.append(dict(profile=n,display_mass=shown,cdf=cdf,derived_mass=derived,certificate_input=certmass,normalization=65536,even=table['even_numerator'],odd=table['odd_numerator'],source=rec(BASE/'crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json')))
dump(OUT/'evidence/DISPLAY_TABLE_BINDING.json',dict(profiles=display_binding,scope='Actual v3 displayed rows compared to pinned official-CDF formula and certificate input;new976/1344 sampler/reliability replay in separate execution record'))

for n,repcount,maximum,H,R2 in [('976',1484,4,1477,3669),('1344',1000,2,1644,2030)]:
 root=OUT/'certificates/review/evidence';doc=load(root/f'PGF_FULL_COVERAGE_{n}.json');mapfile=root/f'PGF_SHIFT_TO_REP_{n}.u16le';raw=mapfile.read_bytes()
 ids=list(struct.unpack('<'+'H'*65536,raw));records=doc['representative_records'];count=Counter(ids)
 ck(n+'/65536_shift_map_bytes',len(raw)==131072 and len(ids)==65536 and hashlib.sha256(raw).hexdigest()==doc['map_sha256'])
 ck(n+'/complete_representatives',len(records)==repcount==doc['representatives'] and set(ids)==set(range(repcount)))
 ck(n+'/exact_all_rep_gaps',all(int(r['gap_to_max_numerator'])>=0 and int(r['pgf_common_numerator'])+int(r['gap_to_max_numerator'])==int(doc['maximum_common_numerator']) and sum(r['weight_mass'])==65536 and count[r['id']]==r['shift_count'] for r in records))
 ck(n+'/unique_max_shift',doc['maximizing_shifts']==[maximum] and [a for a,rid in enumerate(ids) if records[rid]['gap_to_max_numerator']=='0']==[maximum])
 env=cert['profiles'][n]['environment']
 ck(n+'/H_threshold_and_tail',env['fixed_A_H']['threshold']==H and env['fixed_A_H']['tail_certificate']['exponent']>=40)
 ck(n+'/R2_threshold_and_tail',env['R2']['threshold']==R2 and env['R2']['tail_certificate']['exponent']>=40)
 ck(n+'/maximum_witness_vector',records[ids[maximum]]['weight_mass']==env['fixed_A_H']['witness_weight_mass'])
 ck(n+'/q_dependent_cost_disclosed','q=2^D' in draft and '关于D的通用多项式算法' in draft)
 if n=='1344':ck('1344/corrected_CDF_and_actual_theta',cert['profiles'][n]['distribution']['cdf']==[9142,23462,30338,32361,32725,32765,32767] and rd(cert['profiles'][n]['distribution']['psi_at_nyquist'])==F(1,16384))

ck('replay_all4_exit0',len(replay['runs'])==4 and all(x['exit_code']==0 for x in replay['runs']))
ck('whole_author_certificate_identical',replay['whole_author_certificate_byte_identical'] and (OUT/'certificates/OFFICIAL_PROFILE_CERTIFICATES.json').read_bytes()==(BASE/'crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json').read_bytes())
ck('9196_replay_arithmetic_matches',replay['review_named_arithmetic_comparisons']==9196 and replay['review_result_stable_payload_equal'])
ck('3194_author_checks',replay['author_check_summary']['check_count']==3194 and replay['author_check_summary']['status']=='PASS')
for i,r in enumerate(replay['runs']):
 ck(f'replay_run_{i}_script_hash',rec(Path(r['script']['path']))==r['script'])
 ck(f'replay_run_{i}_log_hash',rec(Path(r['log']['path']))==r['log'])
for i,c in enumerate(replay['script_and_input_copies']):
 ck(f'copy_{i}_binding',rec(Path(c['source']['path']))==c['source'] and rec(Path(c['copy']['path']))==c['copy'] and c['source']['sha256']==c['copy']['sha256'])
relations=load(OUT/'certificates/review/evidence/HISTORICAL_EVENT_RELATIONS.json')
ck('epsilon_events_and_full_convolutions',relations['status']=='PASS' and [x['complete_64fold_coefficients'] for x in relations['profiles']]==[1281,769] and [x['certified_exponent'] for x in relations['profiles']]==[1118,1532])
ck('historical_script_runs0',replay['historical_script_executions']==0)

claimmap={v['id']:v for v in m['claims']}
ck('61_unique_claims',len(claimmap)==len(m['claims'])==61)
def closure(id,anc=()):
 assert id not in anc,('cycle',id,anc)
 s={id}
 for d in claimmap[id].get('dependencies',[]):s|=closure(d,anc+(id,))
 return s
for id,c in claimmap.items():
 ck('claim_'+id+'_dependencies',all(d in claimmap for d in c.get('dependencies',[])))
 ck('claim_'+id+'_sources',all(s in m['source_registry'] for s in c.get('source_ids',[])))
 closure(id)
for name,v in m['main_result_dependency_audit'].items():
 ck(name+'/closure',closure(v['root_claim'])==set(v['transitive_claim_dependencies']))
ck('CF1_and640_no976_dependency',all(not v['depends_on_chi976'] for k,v in m['main_result_dependency_audit'].items() if k=='A' or '640' in k))
ck('976_reliability_uses_corrected_mass',all(v['depends_on_chi976'] for k,v in m['main_result_dependency_audit'].items() if '976' in k))
ck('all6_C1_to_C6_closed',len(m['v3_corrections'])==6 and all(v['status']=='CLOSED' for v in m['v3_corrections']))
for v in m['v3_corrections']:
 ck('readiness_closed_'+v['id'],bool(re.search(r'\| '+v['id']+r' \|.*CLOSED',texts['REVISION_AND_READINESS.md'])))
ck('latest_review_identity_exact',m['latest_profile_review']['identity']['status']=='AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW')
ck('latest_prior_reviews_visible',m['latest_profile_review']['identity']['prior_positive_reviews_visible'])
ck('exact_backend_null',m['latest_profile_review']['identity']['exact_backend_model_id'] is None and m['identity']['exact_backend_model_id'] is None)
ck('no_model_independence_inflation',not m['latest_profile_review']['identity']['independence_of_model_error_processes_established'] and not m['identity']['model_error_process_independence_established'])
ck('all6_author_programs_unresolved',len(m['implementation_model_migration']['config_mappings'])==6 and all(v['author_implementation_status']=='UNRESOLVED' and v['result_B_fixed_A_transfer']=='UNRESOLVED' and v['result_B_uniform_Setup_transfer']=='UNRESOLVED' for v in m['implementation_model_migration']['config_mappings']))
ck('all3_mathematical_profiles_covered',m['implementation_model_migration']['all_three_numeric_mathematical_profiles_covered'])
ck('author_trace0',m['implementation_model_migration']['author_UE_message_checked_traces']==0)
ck('human3_questions',all('H'+str(i)+'：' in texts['HUMAN_REVIEW_ENTRY.md'] for i in [1,2,3]))
ck('stage_has_specific_external_reopen',all(s in texts['REVISION_AND_READINESS.md'] for s in ['认证','UE工件','消息','人工','六配置','更多更新深度']))

linked={}
for name,text in texts.items():
 ck(name+'/unicode_integrity','\ufffd' not in text)
 ck(name+'/user_style',not re.search(r'不是[^。\n]{0,300}而是',text))
 ck(name+'/waiting_state','WAITING_FOR_AUTHOR_ARTIFACT' in text)
 linktext=re.sub(r'\\\[.*?\\\]','',text,flags=re.S)
 for dest in re.findall(r'\]\(([^\n)]+)\)',linktext):
  dest=dest.strip('<>')
  if dest.startswith(('https://','http://','#')):continue
  target=Path(dest)
  if not target.is_absolute():target=OUT/target
  target=target.resolve()
  if target==OUT/'MANIFEST.json':continue
  ck('local_link_'+name+'_'+str(len(linked)),target.is_file())
  linked[str(target)]=rec(target)
tags=re.findall(r'\\tag\{([^}]+)\}',draft)
ck('equation_tags_unique',len(tags)==len(set(tags)))
dump(OUT/'evidence/LINKED_SOURCE_FINGERPRINTS.json',dict(scope='All literal local Markdown targets in the3 prose deliverables excluding self-manifest;math blocks excluded',files=sorted(linked.values(),key=lambda x:x['path'])))

snap=load(OUT/'evidence/INPUT_SNAPSHOT.json');changed=[]
for r in snap['files']:
 now=rec(Path(r['path']))
 if now!=r:changed.append(dict(before=r,after=now))
ck('all472_historical_inputs_unchanged',len(snap['files'])==472 and not changed)
dump(OUT/'evidence/FINAL_INPUT_RECHECK.json',dict(unique_historical_files=472,all_bytes_unchanged=not changed,changes=changed))
finger=load(OUT/'evidence/INPUT_FINGERPRINT_CHECK.json')
ck('2930_embedded_fingerprints',finger['records_checked']==2930 and finger['all_matched'])
inherited=[]
for path in [OLD/'MANIFEST.json',BASE/'crypto_fi_official_profile_review/MANIFEST.json']:
 v=load(path);ok=canonical(v)==v['payload_sha256'];ck('inherited_payload_seal_'+path.parent.name,ok)
 inherited.append(dict(file=rec(path),payload_sha256=v['payload_sha256'],matched=ok))
for name in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md']:
 ck('required_payload_'+name,(OUT/name).is_file() and (OUT/name).stat().st_size>0)
qa=dict(schema='frodo-fi-v3/document-certificate-qa/1',date_asia_shanghai='2026-11-11',all_passed=True,check_count=len(checks),checks=checks,scope='Cross-document/model/endpoint/source-binding consistency and final historical preservation;separate from mathematical9196 and3194 script replays. No new independent cryptographic review.',historical_files_unchanged=472,linked_local_targets=len(linked))
dump(OUT/'evidence/DOCUMENT_QA.json',qa)
manifest=dict(schema='frodo-fi-manuscript-manifest/v3',version='v3',date_asia_shanghai='2026-11-11',sealed_at_asia_shanghai=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),status='SEALED_V3_THREE_OFFICIAL_PROFILES_C1_C6_CLOSED',root=str(OUT),required_deliverables=['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVISION_AND_READINESS.md','HUMAN_REVIEW_ENTRY.md','MANIFEST.json'],identity=m['identity'],scope='Author revision,parametric proof integration,source verification,deterministic finite mathematics and stage handoff. Historical sources read-only.',stage_verdict=m['stage_verdict'],correction_status=m['v3_corrections'],parametric_criterion=m['parametric_criterion'],official_profile_result_selector=rec(OUT/'certificates/UNIFIED_RESULT_SELECTORS.json'),official_profile_summary={n:dict(parameters=v['parameters'],initial=v['initial']['full_failure_power'],fixed_A_display=v['fixed_A']['display'],uniform_Setup_display=v['uniform_Setup']['display'],all_update_displays_survive_initial_correct_conditioning=True) for n,v in p.items()},main_result_dependency_audit=m['main_result_dependency_audit'],latest_review_identity=m['latest_profile_review']['identity'],latest_review_historical_adoption_state='REPAIR_REQUIRED preserved at E16;C1-C6 applied in this version',actual_replay=rec(OUT/'evidence/REPLAY_EXECUTION.json'),action_counts=m['action_counts'],author_program_state='WAITING_FOR_AUTHOR_ARTIFACT',author_configs_mapped=0,message_checked_author_UE_traces=0,priority_scope=m['priority_scope'],input_integrity=dict(direct_files=137,embedded_records=2930,unique_historical_files=472,all_matched=True,all_historical_bytes_unchanged=True,snapshot=rec(OUT/'evidence/INPUT_SNAPSHOT.json'),embedded_checks=rec(OUT/'evidence/INPUT_FINGERPRINT_CHECK.json'),final_check=rec(OUT/'evidence/FINAL_INPUT_RECHECK.json')),inherited_seals=inherited,qa=dict(all_passed=True,check_count=len(checks),file=rec(OUT/'evidence/DOCUMENT_QA.json')),external_handoff=dict(most_decisive_real_software_input='Authenticated author UE immutable artifact plus source-mapped selected profile and one honest unfiltered Enc/TG/Upd/Dec original/initial/updated-message comparison trace',most_decisive_human_input='H1 original game/CF1;H2 parameterized probability and3 finite certificates;H3 exact FI conditional security/actual software/ contribution judgment',other_reopen_materials=['Six configs and original100-run5-operation logs','Version/date/hash-authenticated Nishimaki2024 extendedLemma5.7 and CJL originalPDF correspondence','Same-object complete precedent with verifiable public date']),historical_inputs_read_only=True,historical_writes=0,files_exclude_manifest_itself=True,files=[rec(f) for f in sorted(OUT.rglob('*')) if f.is_file() and f!=OUT/'MANIFEST.json'],manifest_integrity_definition='SHA256 of canonical UTF8 JSON excluding payload_sha256;ensure_ascii=False,sort_keys=True,separators=(comma,colon). File-byte hash distinct.')
manifest['payload_sha256']=canonical(manifest);dump(OUT/'MANIFEST.json',manifest)
assert canonical(load(OUT/'MANIFEST.json'))==manifest['payload_sha256']
assert all(rec(Path(x['path']))==x for x in manifest['files'])
assert all((OUT/name).is_file() for name in manifest['required_deliverables'])
print(json.dumps(dict(status=manifest['status'],document_checks=len(checks),author_replay_checks=3194,review_replay_comparisons=9196,all_passed=True,historical_files_unchanged=472,sealed_payload_files=len(manifest['files']),manifest=rec(OUT/'MANIFEST.json'),payload_sha256=manifest['payload_sha256']),ensure_ascii=False))
