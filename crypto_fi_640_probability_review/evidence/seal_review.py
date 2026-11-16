"""Build provenance/verdict and seal review files; historical sources stay read-only."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence'
BASE=ROOT.parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):
    p=Path(p); b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
calc=read(EV/'RECOMPUTED_CERTIFICATES.json')
lock=read(EV/'INPUT_HASH_CHECK.json')
replay=read(EV/'AUTHOR_REPLAY_COMPARISON.json')
assert calc['all_passed'] and calc['checks_passed']==375
assert all(x['match'] for x in lock['referenced_records'])
assert all(pin(x['path'])==x for x in lock['inputs'])
assert all(x['identical_all_decisive_fields'] for x in replay)
for prefix,oldroot,scriptname in [('scalar','crypto_fi_640_correctness_audit','compute_scalar_certificates.py'),('joint','crypto_fi_640_joint_correctness','compute_joint_certificates.py')]:
    assert pin(BASE/oldroot/'evidence'/scriptname)['sha256']==pin(EV/('author_'+prefix+'_replay')/'evidence'/scriptname)['sha256']

identity={
 'status':'AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW',
 'operator':'Current Codex conversation, one active reviewing agent',
 'declared_model_family':'GPT-6 (as stated in the current session instructions)',
 'exact_backend_model_id':None,
 'exact_backend_model_id_basis':'Not exposed by this session; no inferred model/version string',
 'author_rounds_exact_model_ids':None,
 'same_model_or_session_continuity_with_author_rounds':'UNDETERMINED from available records',
 'author_proofs_and_numerical_targets_visible':True,
 'proof_blind_phase_executed':False,
 'new_human_reviews':0,'new_cross_model_reviews':0,'new_subagents':0,
 'new_independent_blind_reviews':0,'formal_proof_assistant_used':False,
 'empirical_reviewer_calibration':'NOT_CALIBRATED',
 'actual_history_scope':'Current conversation and injected memory summary visible; both supplied author-round records read. Earlier raw author conversations were not retrieved.'}
model={'n':640,'D':15,'q':32768,'mbar':8,'nbar':8,'B':2,'message_bits':128,
 'setup':'A uniform in (Z/32768Z)^(640x640), shared by both generations',
 'chi':'Exact official chi640 25-point signed table',
 'independence':'All chi coordinates and calls independent; raw TG coins independent of keys and parent coins',
 'Ord':'n-column bit-plane normalization with Ord(C1)Tensor_D(S)=C1 S mod q',
 'experiment':'One honest Enc, one honest unfiltered TG, one Upd; every token rank integrated',
 'rounding':'Nearest integer, ties upward',
 'message_quantifier':'Every legal 128-bit message fixed before coins',
 'output_selection':'Coordinate/row fixed before coins',
 'probability_denominator':'Uniform Setup plus both honest key generations and all Enc/TG/Upd coins',
 'initial_A_quantifier':'Initial bound holds for every fixed A',
 'updated_A_quantifier':'Updated bounds average the uniform Setup law'}
claims=[]
def claim(i,status,statement,anchor,evidence=None):
    claims.append({'id':i,'status':status,'statement':statement,'proof_anchor':anchor,'evidence':evidence or ['MATHEMATICAL_REVIEW.md']})
P='PROVED_UNDER_STATED_MODEL'
claim('R0',P,'Printed-algorithm residual and message-independent half-up decoding event','sections 2-3')
claim('S1',P,'Given F, the remaining TG rows independently yield the exact conditional CF','section 4.1')
claim('S2',P,'Bad environment <=2^-22; full-frequency bound gives coordinate interval','sections 4.2-4.4',['MATHEMATICAL_REVIEW.md','evidence/RECOMPUTED_CERTIFICATES.json'])
for i,statement,anchor in [
 ('J1','Given V, eight key/G column packets yield iid row residuals; p_row=E p(V)^8','section 5.1'),
 ('J2','CF includes all old/new key and G terms with the stated powers/signs','section 5.2'),
 ('J3','Given B, 1280 a/b coefficients are iid with the actual weighted-sum law; all token ranks averaged','section 5.3'),
 ('J4','Absolute CF moment <=D_t^640; D_t equals exact difference-law sum; all frequencies charged','sections 5.4, 6.1-6.3'),
 ('J5','Pointwise chord gives the row upper bound; Jensen gives the lower bound','section 6.4'),
 ('J6','Full-message event inclusion and final Frechet conditioning preserve decimal endpoints','sections 7.2-7.3')]:
    claim(i,P,statement,anchor)
claim('I1',P,'Initial product-noise PGF at21/20 gives per-coordinate tail <=2^-138 and full initial failure <=2^-132','section 7.1',['MATHEMATICAL_REVIEW.md','evidence/RECOMPUTED_CERTIFICATES.json'])
claim('C1',P,'Exact laws, directed dyadics, key rational endpoints and author-script replay agree','sections 4,6,7',['evidence/RECOMPUTED_CERTIFICATES.json','evidence/AUTHOR_REPLAY_COMPARISON.json'])
claim('R640_HIGH_RELIABILITY','COUNTEREXAMPLE_FOUND','A high-reliability one-update claim for this ideal official640-parameter printed instance is contradicted by error>=99.9969655%','sections 7.2,8.4')
claim('PRESENTATION','REPAIR_REQUIRED','Clarify per-exponential64bit ceiling, uniform-Setup quantifier, manuscript C25 split and informed-review identity','CORRECTIONS_AND_MANUSCRIPT_IMPACT sections2-4',['CORRECTIONS_AND_MANUSCRIPT_IMPACT.md'])
claim('THEOREM63_PRESENTATION','REPAIR_REQUIRED','Include initial-noise accounting; printed s12 slack absorbs B0 but official640 premise still fails','section 8.3')
claim('AUTHOR_PROGRAM','UNRESOLVED','Exact author program/configuration, A/noise law and arithmetic equivalence remain unestablished','section 8.1',['CORRECTIONS_AND_MANUSCRIPT_IMPACT.md'])
claim('OTHER_CONFIGURATIONS','UNRESOLVED','Other sizes, update depths and full64-coordinate exact probability have no new determination in this review','section 8.1')

verdict={'schema':'fi640-probability-review/verdict/1','date_asia_shanghai':'2026-11-10',
 'core_status':P,'manuscript_presentation_status':'REPAIR_REQUIRED',
 'completion':'COMPLETE_PROBABILITY_CHAIN_REVIEW',
 'adoption':'Adopt the precise ideal-model proposition and proof supplied in the corrections document',
 'identity':identity,'model':model,'claims':claims,
 'results':{'initial_full_correct_lower':'1-2^-132',
   'coordinate_interval':['0.2499054','0.2500946'],
   'coordinate_exact_lower':calc['single']['lower'],'coordinate_exact_upper':calc['single']['upper'],
   'row_interval':['0.0000152532','0.000030345'],
   'row_exact_lower':calc['joint']['L'],'row_exact_upper':calc['joint']['U'],
   'full_message_correct_upper':'0.000030345','full_message_error_lower':'0.999969655',
   'full_message_error_percent_lower':'99.9969655%',
   'condition_initial_full_correct_same_displayed_bounds':True,
   'conditional_exact_endpoints':calc['conditional'],
   'exact_full_message_probability_computed':False},
 'numerical_corrections_required':[],
 'core_probability_gap_found':False,'unclosed_core_step_count':0,
 'effect_of_remaining_questions':'Sharper64-coordinate precision and actual-program mapping have separate scopes; the stated-model high-error bound is established.',
 'Theorem63':{'printed_640_premise_satisfied':False,'counterexample_with_premise_satisfied_claimed':False,**calc['theorem63_at640']},
 'existing_source_distinguisher_and_CF1':'Historical evidence scope retained; full original attacks/CF1 proofs were not newly re-audited here.',
 'method_priority':'Classical Fourier, Chernoff, Cauchy-Schwarz, convex chord and Jensen tools; no new global priority search',
 'history_modified':False}
save(ROOT/'REVIEW_VERDICT.json',verdict)

source_scopes={
 'FI_journal_20261110.pdf':{'pages_text':[12,13,14,15],'pages_original_image':[12,13,14,15],'pdfinfo_pages':23},
 'official_frodo_2021.pdf':{'pages_text':[10,15,16,25],'pages_original_image':[10,15,16,25],'pdfinfo_pages':59},
 'articlev08.tex':{'locators':['493-496','509-560','580-590','633-653','669-699']}}
source_records=[]
for name,scope in source_scopes.items():
    source_records.append({'source':pin(BASE/'crypto_fi_640_correctness_audit'/'sources'/name),'reading_scope':scope,
                           'matching_joint_copy':pin(BASE/'crypto_fi_640_joint_correctness'/'sources'/name)})
core_inputs=[x for x in lock['inputs'] if Path(x['path']).parent in [BASE/'crypto_fi_640_correctness_audit',BASE/'crypto_fi_640_joint_correctness']]
provenance={'schema':'fi640-probability-review/input-and-provenance/1','date_asia_shanghai':'2026-11-10',
 'observed_sealing_time_asia_shanghai':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'identity':identity,
 'observable_review_axes':{
  'session_history':'Current conversation + injected memory; historical source-and-computation records visible; prior raw conversations not retrieved',
  'model_identity':'Declared GPT-6-based Codex; exact serving model/weights and prior author-model continuity unavailable',
  'proof_visibility':'Targets visible in user request; full supplied derivations read before conclusions; no proof-blind phase',
  'source_exposure':'Frozen local PDFs, source TeX, eight deliverables, two scalar scripts and both exact certificates',
  'review_execution':'One reviewing process; no panel/persona-generated independent votes, humans or cross-model calls',
  'verification':'Paper rederivation plus rewritten deterministic scalar checks and isolated author-script replays; no formal proof assistant'},
 'skills_applied':[
  {'name':'academic-research-suite','path':r'C:\Users\a1887\.codex\skills\academic-research-suite\SKILL.md','scope':'User-specified targeted mathematics/source review; inline evidence discipline, no full panel or blind workflow claimed'},
  {'name':'pdf','path':r'C:\Users\a1887\.codex\plugins\cache\openai-primary-runtime\pdf\26.1026.10807\skills\pdf\SKILL.md','scope':'Read-only original-PDF extraction, rendering and visual source inspection'}],
 'frozen_model':model,'core_input_deliverables':core_inputs,
 'input_files_locked_count':len(lock['inputs']),'specified_directories_file_count':44,'extra_manuscript_files_count':4,
 'historical_referenced_byte_records_rechecked':len(lock['referenced_records']),'all_input_byte_checks_match':True,
 'input_fingerprints':lock['inputs'],'input_detail':pin(EV/'INPUT_HASH_CHECK.json'),
 'primary_sources':source_records,
 'semantic_read_scope':{
  'specified_deliverables':'All eight full core files; all probability derivations and verdict/model/provenance fields',
  'scalar_scripts':'Both full original probability scripts, formulas and output mechanisms inspected',
  'scalar_certificates':'Both parsed; all decisive scalar/group/exponential/endpoint fields recomputed and compared; whole replays compared',
  'other_historical_sidecars':'Read as input byte/reference records; hashing does not imply full mathematical or image review',
  'PARAMETER_CERTIFICATES':'Hash/reference context only; prior source-hiding convolution bounds were not rerun',
  'manuscript':'Sections2,6,7,10.3,C and relevant abstract/claims read for interfaces and exact correction locations; no full manuscript rereview',
  'claim_matrix':'C08,C09,C10,C25 read for scope; other rows not re-adjudicated',
  'readiness_report':'Read for historical identity and unresolved-scope migration'},
 'computation':{
  'rewritten_check_script':pin(EV/'review_scalar_check.py'),
  'rewritten_exact_result':pin(EV/'RECOMPUTED_CERTIFICATES.json'),
  'checks_passed_total':375,'checks_note':'Includes100 referenced-file byte checks plus arithmetic, enclosure, copy and final-integrity checks; count is not novelty or independence evidence',
  'author_replay_comparison':pin(EV/'AUTHOR_REPLAY_COMPARISON.json'),
  'author_scalar_replay_all_decisive_fields_equal':True,'author_scalar_excluded_diagnostic_field':'elapsed_seconds_display_only',
  'author_joint_replay_byte_identical_certificate':True,
  'arithmetic':'Python arbitrary-precision int/Fraction, recurrence Taylor polynomials, minimal upward dyadic ceilings; Decimal strings are display only',
  'trusted_basis':'Exact official mass table; elementary cosine/sine inequalities; rational pi enclosure; finite-group Fourier inversion; integer arithmetic',
  'probability_script_runs':{'rewritten_checker':2,'author_scalar_copy':1,'author_joint_copy':1},
  'program_sampling_count':0,'historical_scripts_executed_in_original_directories':False},
 'actions':{'protection_mechanism_implementations':0,'LWE_solver_runs':0,'attack_prototype_runs':0,
  'matrices_keys_tokens_ciphertexts_sampled':0,'Monte_Carlo_trials':0,'large_crypto_experiments':0,
  'native_AS_RP_requests':0,'author_contacts':0,'messages_or_emails':0,'network_retrievals':0,
  'external_model_uploads':0,'subagents':0,'project_test_reruns':0,
  'new_PDF_rendered_pages':8,'new_PDF_text_extracted_pages':8},
 'historical_inputs_unchanged_at_seal':True,
 'evidence_boundary':'No inferential upgrade to blind/external/human/production/priority certification; conclusions stay within the stated ideal model.'}
save(ROOT/'INPUT_AND_REVIEW_PROVENANCE.json',provenance)

# Deliverable QA: content, paths, table structure, required enums and frozen bytes.
required=['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md','REVIEW_VERDICT.json','INPUT_AND_REVIEW_PROVENANCE.json','MANIFEST.json']
json_errors=[]; broken=[]; table_errors=[]; style=[]
for p in sorted(ROOT.rglob('*.json')):
    if p.name=='MANIFEST.json': continue
    try: read(p)
    except Exception as e: json_errors.append({'file':str(p),'error':str(e)})
for p in ROOT.glob('*.md'):
    txt=p.read_text(encoding='utf-8')
    if re.search('不是.{0,100}而是',txt): style.append(p.name)
    for target in re.findall(r'\]\(([^)]+)\)',txt):
        if not target.startswith(('https://','http://')) and not (p.parent/target).exists(): broken.append({'file':p.name,'target':target})
    block=[]
    for i,line in enumerate(txt.splitlines()+[''],1):
        if line.startswith('|'): block.append((i,len(re.findall(r'(?<!\\)\|',line))))
        else:
            if block and len(set(n for _,n in block))>1: table_errors.append({'file':p.name,'counts':block})
            block=[]
allowed={'PROVED_UNDER_STATED_MODEL','REPAIR_REQUIRED','COUNTEREXAMPLE_FOUND','UNRESOLVED'}
assert all(c['status'] in allowed for c in claims)
qa={'all_required_except_manifest_present':all((ROOT/p).is_file() for p in required[:-1]),
 'json_errors':json_errors,'broken_local_links':broken,'table_structure_errors':table_errors,'forbidden_style':style,
 'all375_checks_passed':True,'two_author_replays_match':True,
 'historical48_files_unchanged':all(pin(x['path'])==x for x in lock['inputs']),
 'claim_status_counts':dict(Counter(c['status'] for c in claims))}
save(EV/'FINAL_QA.json',qa)
assert qa['all_required_except_manifest_present'] and qa['historical48_files_unchanged']
assert not json_errors and not broken and not table_errors and not style,qa
manifest={'schema':'fi640-probability-review/manifest/1','date_asia_shanghai':'2026-11-10',
 'status':'COMPLETE_SEALED','required_deliverables':required,
 'core_status':P,'review_identity':identity['status'],
 'self_exclusion':'Files list excludes MANIFEST.json; payload_sha256 hashes canonical JSON with the payload_sha256 field omitted.',
 'canonicalization':'UTF-8 json.dumps(ensure_ascii=False,sort_keys=True,separators=(comma,colon))',
 'files':[pin(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='MANIFEST.json'],
 'qa':qa}
manifest['payload_sha256']=hashlib.sha256(json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
save(ROOT/'MANIFEST.json',manifest)
# Read-back verification, without further writes after the sealed manifest.
sealed=read(ROOT/'MANIFEST.json'); payload=sealed.pop('payload_sha256')
assert hashlib.sha256(json.dumps(sealed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()==payload
assert all(pin(x['path'])==x for x in sealed['files'])
assert all((ROOT/p).is_file() for p in required)
print(json.dumps({'status':'COMPLETE_SEALED','files_excluding_manifest':len(sealed['files']),'manifest_byte_sha256':pin(ROOT/'MANIFEST.json')['sha256'],'qa':qa},ensure_ascii=False,indent=2))
