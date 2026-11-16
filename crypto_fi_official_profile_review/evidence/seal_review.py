"""Build provenance/verdict, audit all historical bytes, then seal the package."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json, hashlib, os, stat, re, platform, sys
R=Path(__file__).resolve().parents[1]; E=R/'evidence'; B=Path('D:/毕业设计')
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p): return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
history=rd(E/'INPUT_SNAPSHOT.json')+rd(E/'ADDITIONAL_INPUT_SNAPSHOT.json')
unique={x['path']:x for x in history}; mismatches=[]
for x in unique.values():
 p=Path(x['path'])
 if not p.exists() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']: mismatches.append(x['path'])
assert not mismatches,mismatches
integrity=dict(status='PASS',unique_historical_files=len(unique),all_historical_bytes_preserved=True,
 mismatches=[],baseline_scope='Initial intake before replay plus three additional relation inputs before their recomputation',
 checked_at_asia_shanghai=now)
dump(E/'FINAL_INPUT_HASH_CHECK.json',integrity)
calc=rd(E/'INDEPENDENT_RECOMPUTATION.json'); replay=rd(E/'AUTHOR_REPLAY_RESULT.json'); rel=rd(E/'HISTORICAL_EVENT_RELATIONS.json')
assert calc['status']==replay['status']==rel['status']=='PASS'
assert calc['script_sha256']==sha(E/'recompute_review.py')
assert replay['entire_certificate_byte_identical']
authorcheck=rd(E/'author_replay/crypto_fi_official_profile_correctness/evidence/CERTIFICATE_CHECK.json')
assert authorcheck['check_count']==3194 and authorcheck['status']=='PASS'
claims=[
 ('R1_TRUE_RESIDUAL','PROVED_UNDER_STATED_MODEL','§3'),
 ('R2_TWO_RAW_COIN_ENVIRONMENTS','PROVED_UNDER_STATED_MODEL','§4'),
 ('R3_CONDITIONAL_IID_COLUMN_PACKETS_AND_ROW_MOMENT','PROVED_UNDER_STATED_MODEL','§4'),
 ('R4_TRUE_2N_COEFFICIENT_LAW','PROVED_UNDER_STATED_MODEL','§4'),
 ('R5_ABSOLUTE_FOURIER_MOMENT_D_TO_N','PROVED_UNDER_STATED_MODEL','§4'),
 ('R6_EXACT_DIFFERENCE_LAW_IDENTITY','PROVED_UNDER_STATED_MODEL','§4'),
 ('P_PARAMETRIC_RAW_AND_CLIPPED_CRITERIA','PROVED_UNDER_STATED_MODEL','§5'),
 ('P_ENDPOINTS_AND_ACTUAL_PARAMETER_DOMAIN','PROVED_UNDER_STATED_MODEL','§5'),
 ('P_JENSEN_AND_SCALAR_INTERVALS','PROVED_UNDER_STATED_MODEL','§5'),
 ('D_OFFICIAL_CDF_SAMPLER_MOMENTS_PARITY','PROVED_UNDER_STATED_MODEL','§6'),
 ('D_COMMON_DECODE_SET_AND_PI0','PROVED_UNDER_STATED_MODEL','§5'),
 ('H_ALL_65536_TRANSLATIONS_AND_REPRESENTATIVE_COVERAGE','PROVED_UNDER_STATED_MODEL','§7'),
 ('H_FIXED_A_PGF_AND_INCLUSIVE_TAILS','PROVED_UNDER_STATED_MODEL','§7'),
 ('E_R2_TAILS_AND_BAD_BUDGETS','PROVED_UNDER_STATED_MODEL','§8'),
 ('F_POSITIVITY_SMALL_DOMAINS_SUBGROUPS_NYQUIST','PROVED_UNDER_STATED_MODEL','§8'),
 ('F_ALL_FREQUENCIES_64_AND_80_BIT_UPWARD_CHAIN','PROVED_UNDER_STATED_MODEL','§8'),
 ('U_976_EVERY_FIXED_A','PROVED_UNDER_STATED_MODEL','§9'),
 ('U_1344_EVERY_FIXED_A','PROVED_UNDER_STATED_MODEL','§9'),
 ('U_976_UNIFORM_FULL_MATRIX_SETUP','PROVED_UNDER_STATED_MODEL','§9'),
 ('U_1344_UNIFORM_FULL_MATRIX_SETUP','PROVED_UNDER_STATED_MODEL','§9'),
 ('I_INITIAL_PGF_AND_64_COORDINATE_UNION','PROVED_UNDER_STATED_MODEL','§10'),
 ('C_EVENT_CONTAINMENT_AND_INITIAL_CORRECT_CONDITIONING','PROVED_UNDER_STATED_MODEL','§10'),
 ('C_PUBLIC_SEED_FIXED_A_AVERAGING','PROVED_UNDER_STATED_MODEL','§9'),
 ('T_THEOREM63_PREMISE_AND_PARAMETER_SUBSTITUTION','PROVED_UNDER_STATED_MODEL','§11'),
 ('T_SOURCE_EVENT_CERTIFICATE_AND_640_CF1_RELATIONS','PROVED_UNDER_STATED_MODEL','§11'),
 ('M_STALE_MANUSCRIPT_SCOPE_AND_PRESENTATION','REPAIR_REQUIRED','§11 and CORRECTIONS_AND_MANUSCRIPT_IMPACT.md §§1–7'),
 ('SW_AUTHOR_UE_ARTIFACT_SAMPLING_AND_MACHINE_MAP','UNRESOLVED','§12'),
 ('Q_EXACT_FULL_MESSAGE_SUCCESS_PROBABILITY','UNRESOLVED','§§1,10'),
 ('Q_DEEPER_UPDATES_GLOBAL_PRIORITY_AND_GENERAL_ASYMPTOTIC_HIGH_ERROR','UNRESOLVED','§§11–12')]
identity=dict(status='AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW',
 operator='One current Codex AI context; user-defined targeted mathematical review; no simulated panel',
 chat_id='01a1c8ef-6688-7b71-9943-f98a9c3ff068',turn_id='01a1c8ef-6c33-7431-9127-f813014a0c5a',
 id_basis='CODEX_THREAD_ID plus successful read_thread response',declared_model_family='Codex based on GPT-6 per developer context',
 exact_backend_model_id=None,exact_weights_version=None,author_exact_backend_model_id=None,prior_review_exact_backend_model_ids=None,
 model_id_basis='These exact identities were not exposed by the accessed session and provenance records',
 author_proof_visible=True,numerical_targets_visible=True,prior_positive_reviews_visible=True,
 actual_current_author_thread_ids_differ=True,author_current_raw_context_continuity='UNDETERMINED',
 independence_of_model_error_processes_established=False,new_author_proof_visible_targeted_AI_reviews=1,
 new_independent_model_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,
 new_subagents=0,new_formal_proof_assistant_checks=0,calibration='NOT_CALIBRATED',
 skill_adaptation='ARS review integrity/source/read-only discipline used inline for this user-specified mathematical audit; no journal panel or venue-fit claims')
provenance=dict(schema='fi-official-profile-review/provenance/1',date_asia_shanghai='2026-11-11',identity=identity,
 scope=dict(authorized='Paper mathematics, primary specifications, deterministic finite distributions and interval arithmetic',
  historical_inputs='Read-only',new_output_root=str(R),candidate_mechanisms_implemented=0,
  cryptographic_samples=0,monte_carlo_runs=0,LWE_solver_runs=0,author_UE_runs=0,author_contacts=0,external_service_experiments=0,
  external_model_uploads=0,public_GitHub_read_calls=1,thread_read_calls=3,thread_list_calls=1),
 conversation_access=[
  dict(thread_id=identity['chat_id'],title='复核Frodo-FI参数化可靠性',turns_requested=1,receipt='evidence/CURRENT_THREAD_SNAPSHOT.json',scope='Current in-progress turn item summaries; tool outputs excluded by request'),
  dict(thread_id='01a1c8d5-6c65-73e3-ba03-e114f01b3b8a',title='认证976与1344配置可靠性',turns_requested=1,receipt='evidence/AUTHOR_PROFILE_THREAD_SNAPSHOT.json',scope='One completed author turn, including visible final targets and execution-item summaries'),
  dict(thread_id='01a1c652-ba78-71a0-b293-a09d61f26039',title='复核 Frodo640 固定矩阵结论',turns_requested=1,receipt='evidence/PRIOR_FIXED_A_REVIEW_THREAD_SNAPSHOT.json',scope='One completed prior-review turn and final; item previews include truncation')],
 transcript_limit='Tool-returned summaries/items only; no assertion of full raw-history access or backend identity',
 semantic_access=[
  dict(path=str(B/'crypto_fi_official_profile_correctness/PARAMETRIC_CORRECTNESS_BOUND.md'),level='Complete proof text read'),
  dict(path=str(B/'crypto_fi_official_profile_correctness/PROFILE_RESULTS_AND_SCOPE.md'),level='Complete results and scope text read, including separately returned ending'),
  dict(path=str(B/'crypto_fi_official_profile_correctness/VERDICT.json'),level='Verdict and scope read'),
  dict(path=str(B/'crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json'),level='Complete structural parse; all distributions, PGF, analytic, spectral, initial and endpoint fields used and cross-checked'),
  dict(path=str(B/'crypto_fi_official_profile_correctness/evidence/compute_profile_certificates.py'),level='Full source read; unmodified copy replayed'),
  dict(path=str(B/'crypto_fi_official_profile_correctness/evidence/verify_profile_certificates.py'),level='Full source read; unmodified copy replayed'),
  dict(path=str(B/'crypto_fi_official_profile_correctness/evidence'),level='Source pages, reading and execution records, original check results, erratum receipt; fingerprinting of other files is separately scoped'),
  dict(path=str(B/'crypto_fi_research_manuscript_v1/sources/articlev08.tex'),level='Targeted primary parameter/algorithms/Ord/Tensor/Theorem6.3 text, approximately lines489–708'),
  dict(path=str(B/'crypto_fi_640_fixed_A_correctness/PROOF_OR_OBSTRUCTION.md'),level='Targeted fixed-A conditional proof and PGF sections; finite criterion C/U specialized exactly'),
  dict(path=str(B/'crypto_fi_640_fixed_A_review/REVIEW_VERDICT.json'),level='Identity, contract, claims, numerical results and limitations'),
  dict(path=str(B/'crypto_fi_640_probability_review/review_01a1c4ed/MATHEMATICAL_REVIEW.md'),level='Targeted identity, uniform-Setup contract, source, residual and probability chain sections'),
  dict(path=str(B/'crypto_fi_lwe_independent_review/REVIEW_VERDICT.json'),level='CF-1 claim outcomes and unresolved sample/reduction responsibilities'),
  dict(path=str(B/'crypto_fi_research_manuscript_v2_2/CRYPTOANALYSIS_DRAFT.md'),level='Targeted abstract, §§6–8/10, distribution/certificate and disclosure sections, plus line searches for scope replacement'),
  dict(path=str(B/'crypto_fi_author_implementation_audit/VERDICT.json'),level='Authenticated artifact status, six static-mapping entries, source identity, action counts and transfer fields'),
  dict(path=str(B/'crypto_fi_research_manuscript_v1/sources/PARAMETER_CERTIFICATES.json'),level='976/1344 source-event data parsed; full convolution/epsilon independently rebuilt'),
  dict(path=str(B/'crypto_fi_research_manuscript_v2_1/evidence/chi_976_64fold_coefficients.json'),level='All1281 coefficients reconstructed and matched'),
  dict(path=str(B/'crypto_fi_research_manuscript_v1/sources/chi_1344_64fold_coefficients.json'),level='All769 coefficients reconstructed and matched')],
 pdf_access=dict(structural_preflight='All PASS: 2021=59 pages,2023=21 pages,FI=23 pages',
  extracted_and_rendered_pages=rd(E/'SOURCE_PAGES.json'),
  visually_inspected=['official_2021_p16','official_2021_p25','official_2023_p16','FI_p12','FI_p14'],
  other_listed_pages='Text extraction and/or TeX cross-reading only'),
 memory_access=[dict(path='C:/Users/a1887/.codex/memories_v2/rollout_summaries/2026-11-10T10-07-28-GAn7-frodo640_probability_chain_mathematical_review.md',use='Historical route and scope; actual owning sources reread'),
  dict(path='C:/Users/a1887/.codex/memories_v2/rollout_summaries/2026-11-10T05-50-41-SueU-cf1_bounded_error_lwe_targeted_mathematical_review.md',use='Historical CF-1 interface boundaries; verdict owning source reread')],
 determinism=dict(new_checker=str(E/'recompute_review.py'),author_scripts_imported_by_new_checker=False,
  repeated_arithmetic_is_not_new_review=True,named_comparisons=calc['check_count'],
  independent_exponential_certificate='32/33 degree alternating exp(-y), y<=1/16,192-bit interval repeated squaring',
  source_event_checks='Full64-fold scalar convolution of976 and1344 plus epsilon exact exponent'),
 author_replay=replay,history_integrity=integrity,
 execution_issues=[dict(stage='Initial PDF preflight capture',issue='Child Python stdout used host encoding; UTF-8 decode failed',
  resolution='Set child PYTHONIOENCODING=utf-8 and reran intake; all three source preflights PASS',mathematical_model_changed=False)],
 runtime=dict(python=sys.version,platform=platform.platform(),timezone='Asia/Shanghai'),
 fingerprinting_is_distinct_from_semantic_reading=True)
dump(R/'INPUT_AND_REVIEW_PROVENANCE.json',provenance)
profiles={}
for n,p in calc['profiles'].items():
 profiles[n]=dict(parameters=p['parameters'],status='PROVED_UNDER_STATED_MODEL',
  fixed_A=dict(full_correct_upper=p['modes']['fixed_A']['display']['row_full_upper'],full_error_lower=p['modes']['fixed_A']['display']['full_error_lower'],
   full_error_percent_lower=p['modes']['fixed_A']['display']['full_error_percent_lower']),
  uniform_full_matrix_Setup=dict(full_correct_upper=p['modes']['uniform_Setup']['display']['row_full_upper'],full_error_lower=p['modes']['uniform_Setup']['display']['full_error_lower'],
   full_error_percent_lower=p['modes']['uniform_Setup']['display']['full_error_percent_lower']),
  initial_full_failure_upper_power_of_two=(193 if n=='976' else 246),initial_coordinate_failure_upper_power_of_two=(199 if n=='976' else 252),
  same_update_display_endpoints_conditioned_on_initial_full_correct=True,
  full_translation_PGF=dict(complete=True,translations=65536,representatives=p['H']['representatives'],maximizing_shifts=p['H']['maximizing_shifts'],
   maximum_weight_mass=p['H']['maximizing_weight_mass'],inclusive_H_tail_upper_power_of_two=40),
  full_message_exact_probability_computed=False,author_software_applicability='UNRESOLVED')
verdict=dict(schema='fi-official-profile-targeted-mathematical-review/verdict/1',
 date_asia_shanghai='2026-11-11',completion='SEALED_COMPLETE',core_mathematical_verdict='PROVED_UNDER_STATED_MODEL',
 manuscript_adoption_status='REPAIR_REQUIRED',repairs_supplied=True,
 identity=identity,allowed_claim_verdicts=['PROVED_UNDER_STATED_MODEL','REPAIR_REQUIRED','COUNTEREXAMPLE_FOUND','UNRESOLVED'],
 claims=[dict(id=i,status=s,anchor='MATHEMATICAL_REVIEW.md '+a) for i,s,a in claims],profiles=profiles,
 final_answers=dict(parametric_criterion='PROVED_UNDER_STATED_MODEL including stated endpoints',
  full_translation_PGF='Complete: both65536 shifts, all representative vectors compared exactly, full shift-to-representative maps retained',
  fixed_A_and_uniform_Setup_bounds='All four displayed bounds proved under their separate A quantifiers',
  initial_and_conditioned_endpoints='Both initial failure bounds proved; all requested update displays survive conditioning',
  manuscript_adoption='Parameterized criterion, full PGF certification, two finite-profile theorems, uniform-Setup corollaries, initial/conditional bounds and exact scope replacements supplied',
  clear_gap_affecting_model_high_error=False,software_and_broader_claims='Unresolved outside the stated ideal experiment'),
 no_counterexample_to_submitted_core_propositions_found=True,identified_open_core_proof_steps=0,
 source_theorem63=dict(left976=32387837760,right976_at_T1=4096,left1344=13265908992,right1344_at_T1=2048,
  premise_satisfied_for_official_profiles_and_integer_T_at_least1=False,conditional_theorem_refuted_by_these_profiles=False),
 finite_validation=dict(independent_reconstruction_named_comparisons=calc['check_count'],author_replay_checks=authorcheck['check_count'],
  whole_author_certificate_byte_identical=True,new_source_event_convolutions=[1281,769],history_integrity=integrity),
 required_deliverables=['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md','REVIEW_VERDICT.json','INPUT_AND_REVIEW_PROVENANCE.json','MANIFEST.json'],
 historical_inputs_modified=0,seal_time_asia_shanghai=now)
dump(R/'REVIEW_VERDICT.json',verdict)
# Artifact QA: table widths, banned contrast construction and unresolved placeholders.
qa=[]
for p in R.glob('*.md'):
 txt=p.read_text(encoding='utf-8')
 assert not re.search('不是[^\n。]{0,100}而是',txt),p
 assert not any(ord(c)<32 and c not in '\r\n\t' for c in txt),p
 width=None
 for line in txt.splitlines():
  if line.startswith('|'):
   w=len(re.split(r'(?<!\\)\|',line))-2
   if width is None: width=w
   assert w==width,(p.name,line,width,w)
  else: width=None
 assert 'TODO' not in txt and 'TBD' not in txt
 qa.append(dict(file=p.name,bytes=p.stat().st_size,table_widths_consistent=True,control_characters=False))
for n in [976,1344]:
 cov=rd(E/f'PGF_FULL_COVERAGE_{n}.json'); mp=Path(cov['map_path'])
 assert mp.stat().st_size==131072 and sha(mp)==cov['map_sha256']
 assert all(int(x['gap_to_max_numerator'])>=0 for x in cov['representative_records'])
assert all((R/f).is_file() for f in verdict['required_deliverables'] if f!='MANIFEST.json')
dump(E/'FINAL_QA.json',dict(status='PASS',markdown=qa,check_count=calc['check_count'],author_replay_status='PASS',
 coverage_maps_bound=True,history_integrity=integrity,all_five_deliverables_accounted_for=True))
# Final manifest lists every other package file; self hash is over canonical payload without the self-hash field.
manifest=dict(schema='fi-official-profile-review/manifest/1',completion='SEALED_COMPLETE',sealed_at_asia_shanghai=now,
 output_root=str(R),historical_integrity=integrity,
 files=[dict(relative_path=p.relative_to(R).as_posix(),**info(p)) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='MANIFEST.json'],
 self_integrity='payload_sha256 is SHA256 of UTF-8 JSON sorted keys,ensure_ascii=False,separators=(comma,colon), excluding payload_sha256',
 readonly_policy='All deliverable files marked Windows read-only after the manifest bytes are written; metadata is outside byte hashes')
canonical=json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
manifest['payload_sha256']=hashlib.sha256(canonical).hexdigest(); dump(R/'MANIFEST.json',manifest)
for p in R.rglob('*'):
 if p.is_file(): os.chmod(p,stat.S_IREAD)
assert all(sha(Path(x['path']))==x['sha256'] and Path(x['path']).stat().st_size==x['bytes'] for x in manifest['files'])
print('SEALED_COMPLETE;',len(manifest['files']),'hashed files;',len(unique),'historical inputs unchanged; all five deliverables present.')
print('MANIFEST_SHA256',sha(R/'MANIFEST.json'))
