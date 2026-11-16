"""Create review metadata and deterministic artifact QA only inside review output."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT/'evidence'
BASE = ROOT.parent
SRC = BASE/'crypto_fi_640_fixed_A_correctness'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, value):
    assert p.resolve().is_relative_to(ROOT.resolve())
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def fingerprint(p):
    b = p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def main():
    calc = read(EV/'RECOMPUTED_CERTIFICATES.json')
    assert calc['all_passed'] and calc['check_count'] == 385
    snapshot = read(EV/'INPUT_SNAPSHOT.json')
    refs = read(EV/'EMBEDDED_FINGERPRINT_CHECK.json')
    # Final read-only check includes every uniquely fingerprinted reference target.
    universe = {x['path']: x for x in snapshot['files']}
    for item in refs['records']:
        v = item['target']
        universe[v['path']] = v
    changes = [p for p,item in universe.items() if fingerprint(Path(p)) != item]
    assert not changes, changes
    recheck = {'schema':'fi640-fixed-A-review/input-recheck/1',
               'direct_historical_files_rechecked':len(snapshot['files']),
               'historical_files_rechecked_including_references':len(universe),
               'historical_inputs_unchanged':True,'changes':[]}
    write(EV/'INPUT_RECHECK.json', recheck)
    for fn in ['FI_PREFLIGHT.json','OFFICIAL_PREFLIGHT.json']:
        assert read(EV/fn)['verdict'] == 'PASS'
    identity = {
        'status':'AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW',
        'operator':'One current Codex AI reviewer; targeted mathematical audit, no simulated panel',
        'current_thread_id':'01a1c652-ba78-71a0-b293-a09d61f26039',
        'current_turn_id':'01a1c652-c18f-7f81-abf9-d4622bc71aac',
        'thread_id_basis':'CODEX_THREAD_ID and one successful local read_thread response',
        'declared_model_family':'Codex based on GPT-6, as stated by the current developer context',
        'exact_backend_model_id':None, 'exact_weights_version':None,
        'author_backend_model_ids':None,'prior_review_backend_model_ids':None,
        'model_id_basis':'Not exposed; not inferred from filenames, task title, or tool labels',
        'author_proof_visible':True,'numerical_targets_visible':True,
        'prior_same_task_positive_reviews_visible':True,
        'fresh_proof_blind_phase':False,
        'independent_model_error_processes_established':False,
        'author_current_same_model_or_raw_session_continuity':'UNDETERMINED from available author-side identifiers',
        'new_author_proof_visible_targeted_AI_reviews':1,
        'new_human_reviews':0,'new_cross_model_reviews':0,'new_blind_reviews':0,
        'new_independent_model_reviews':0,'new_subagents':0,
        'formal_proof_assistant_used':False,'empirical_calibration':'NOT_CALIBRATED',
        'criteria_binding':'User-defined FA1-FA5 and stated frozen model; no venue-fit assessment'}
    reading = [
        ('crypto_fi_640_fixed_A_correctness/FIXED_A_MODEL_AND_TARGET.md','Full semantic read'),
        ('crypto_fi_640_fixed_A_correctness/PROOF_OR_OBSTRUCTION.md','Full semantic read; some sections returned twice'),
        ('crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json','Full content read and structured arithmetic comparison'),
        ('crypto_fi_640_fixed_A_correctness/VERDICT.json','Full semantic read, including embedded prior-review scope'),
        ('crypto_fi_640_fixed_A_correctness/evidence/compute_fixed_A.py','Full code read; original execution count zero'),
        ('crypto_fi_640_fixed_A_correctness/evidence/INPUT_LOCK.json','Full record read; every listed fingerprint checked'),
        ('crypto_fi_640_fixed_A_correctness/evidence/DELIVERY_MANIFEST.json','Full read and fingerprint check'),
        ('crypto_fi_640_fixed_A_correctness/evidence/READING_AND_SCOPE_RECORD.json','First 95 lines plus targeted thread/history searches; JSON machine parsed'),
        ('crypto_fi_640_fixed_A_correctness/evidence/seal_fixed_A.py','Targeted rg excerpts only; hash checked; zero execution'),
        ('crypto_fi_640_joint_correctness/CONDITIONAL_STRUCTURE.md','Full semantic read'),
        ('crypto_fi_640_probability_review/MATHEMATICAL_REVIEW.md','First 70 lines, including verdict, provenance, model and residual start'),
        ('crypto_fi_640_probability_review/review_01a1c4ed/MATHEMATICAL_REVIEW.md','First 150 lines, including verdict, provenance, residual, envelopes'),
        ('crypto_fi_640_correctness_audit/sources/articlev08.tex','L491-550 and L549-706; algorithms, Ord/Tensor, residual and Theorem6.3'),
        ('crypto_fi_640_correctness_audit/sources/FI_journal_20261110.pdf','New structural preflight PASS; new source rendering and visual read of PDF12/14'),
        ('crypto_fi_640_correctness_audit/sources/official_frodo_2021.pdf','New structural preflight PASS; new source rendering and visual read of PDF10/25'),
    ]
    for fn in ['FI_journal_20261110_p12','FI_journal_20261110_p14','official_frodo_2021_p10','official_frodo_2021_p25']:
        reading.append(('crypto_fi_640_correctness_audit/evidence/'+fn+'.txt','Full source-page text read'))
        reading.append(('crypto_fi_640_correctness_audit/evidence/'+fn+'.png','Visually inspected frozen page image; later source PDF rerender also inspected'))
    provenance = {
        'schema':'fi640-fixed-A-review/provenance/1','date_asia_shanghai':'2026-11-11',
        'identity':identity,
        'actual_history_scope':{
            'current_conversation_visible':True,'injected_memory_summary_visible':True,
            'current_thread_tool_reads':1,'read_response_turn_count':1,'read_response_has_more':False,
            'raw_earlier_author_threads_retrieved':0,'raw_prior_review_threads_retrieved':0,
            'prior_review_history_claims':'Taken only as file-attributed statements; no new raw-history attestation',
            'source':fingerprint(EV/'CURRENT_THREAD_OBSERVATION.json')},
        'user_part_seven_received_ending':'公共变量Z先决定A=g(Z)。若给定每个Z值后，后续原始χ仍满足声明',
        'part_seven_handling':'Reviewed the complete conditional public-seed implication already written in the supplied model section5',
        'read_scope':[{'file':fingerprint(BASE/p),'scope':scope} for p,scope in reading],
        'hash_only_or_machine_parse_scope':'All remaining snapshot/reference files: fingerprint or JSON structure checks; no full semantic-read claim',
        'input_integrity':{
            'direct_snapshot_file_count':len(snapshot['files']),
            'embedded_records_verified':refs['records_checked'],
            'unique_historical_files_final_rechecked':len(universe),
            'all_reference_fingerprints_matched':True,'historical_writes':0,
            'snapshot':fingerprint(EV/'INPUT_SNAPSHOT.json'),
            'reference_checks':fingerprint(EV/'EMBEDDED_FINGERPRINT_CHECK.json'),
            'final_recheck':fingerprint(EV/'INPUT_RECHECK.json')},
        'pdf_preflight':{
            'FI':read(EV/'FI_PREFLIGHT.json'),'official':read(EV/'OFFICIAL_PREFLIGHT.json'),
            'initial_output_binding_attempts':2,
            'initial_output_binding_error':'Windows: anchored sidecar output requires POSIX dirfd operations',
            'successful_method':'Run preflight without --output; save stdout under the review directory',
            'new_source_page_rendering':fingerprint(EV/'SOURCE_PAGE_RENDERING.json'),
            'new_source_pages_visually_inspected':['FI PDF12','FI PDF14','official PDF10','official PDF25']},
        'verification':{
            'scalar_checker':fingerprint(EV/'recompute_certificates.py'),
            'recomputed_result':fingerprint(EV/'RECOMPUTED_CERTIFICATES.json'),
            'unique_scalar_checks':385,'new_scalar_checker_runs':2,
            'author_compute_script_runs':0,'author_code_imported':False,
            'implementation_constraint':'No candidate mechanism implementation; only proof arithmetic and source-integrity verification'},
        'actions':{'matrices_keys_tokens_ciphertexts_sampled':0,'cryptographic_mechanisms_implemented':0,
                   'attack_prototypes':0,'LWE_solvers':0,'Monte_Carlo_runs':0,
                   'author_contacts':0,'external_messages':0,'external_research_network_requests':0,
                   'local_app_read_thread_calls':1,'workspace_dependencies_lookup_calls':1,'subagents':0}}
    write(ROOT/'INPUT_AND_REVIEW_PROVENANCE.json',provenance)
    endpoints = calc['endpoints']
    verdict = {
        'schema':'fi640-fixed-A-review/verdict/1','date_asia_shanghai':'2026-11-11',
        'status':'PROVED_UNDER_STATED_MODEL','identity':identity,
        'frozen_model':{'n':640,'D':15,'q':32768,'mbar':8,'nbar':8,'B':2,
                        'A':'Every matrix fixed before all relevant raw chi draws; shared across generations',
                        'chi':'Exact official chi640; conditional coordinate/call product law',
                        'message':'Every pre-coins fixed legal128-bit message',
                        'Ord':'n-column bit-plane normalization matching Tensor_D',
                        'token':'One honest unfiltered TG and Upd; every P2 rank retained',
                        'decode':'Nearest integer, ties upward'},
        'claims':[{'id':x,'status':'PROVED_UNDER_STATED_MODEL'} for x in
                  ['FA1','FA2','FA3','FA4','FA5','INITIAL_FIXED_A_PGF','INITIAL_CORRECT_CONDITIONING','CONDITIONAL_PUBLIC_SEED_MIGRATION']],
        'results':{'row_outward_interval':['0.0000135117','0.005043360'],
                   'full_correct_upper':'0.005043360','full_error_lower':'0.994956640',
                   'full_error_percent_lower':'99.4956640%',
                   'initial_full_correct_lower':'1-2^-132 for every fixed A',
                   'same_displayed_endpoints_conditioned_on_initial_full_correct':True,
                   'row_lower_applies_to':'Specified eight-coordinate row event J',
                   'full_upper_basis':'Pointwise K subset J; no cross-row independence premise',
                   'full_message_exact_probability_computed':False,
                   'exact_certified_bounds':endpoints},
        'finite_verification':{'checks':385,'all_passed':True,'H_tail_exponent':73,
                               'R2_tail_exponent':27,'initial_single_coordinate_tail_exponent':138,
                               'bad_environment_budget':'2^-26',
                               'frequency_representatives':16384,'negative_frequencies':'Paired; Nyquist double-counted conservatively',
                               'nu_support':'Every d=-24,...,24 with exact mass',
                               'uncharged_truncation_loss':0,'dyadic_slack_already_in_Z':'<2^-41'},
        'symbolic_A_cases':['zero','identity','explicit low-inner-dimension factorization A=XY','rank-one outer product'],
        'open_core_mathematical_gaps':[],
        'nonblocking_hardening':[{'id':'E1','source':'evidence/compute_fixed_A.py:60',
                                 'finding':'Author H exponent assertion >=70 is weaker than the claimed >=73',
                                 'recomputed_exponent':73,'suggestion':'Use >=73 in future checker revision',
                                 'current_endpoint_impact':0,'historical_file_modified':False}],
        'public_seed':{'status':'PROVED_UNDER_STATED_CONDITIONAL_LAW',
                       'A_generator_uniformity_prg_entropy_assumption_needed_for_this_reliability_bound':False,
                       'required':'Given each supported public seed, all later raw chi coordinates/calls obey the exact product law and the frozen algorithm',
                       'author_program_status':'WAITING_FOR_AUTHOR_ARTIFACT'},
        'theorem63_scope':'The printed sufficient premise fails for official640; this result concerns probabilities outside that premise',
        'input_integrity':provenance['input_integrity'],
        'provenance':fingerprint(ROOT/'INPUT_AND_REVIEW_PROVENANCE.json'),
        'report':fingerprint(ROOT/'MATHEMATICAL_REVIEW.md'),
        'required_deliverables':['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md',
                                 'INPUT_AND_REVIEW_PROVENANCE.json','REVIEW_VERDICT.json']}
    write(ROOT/'REVIEW_VERDICT.json',verdict)
    badlinks, forbidden, controls, table_errors = [], [], [], []
    for p in ROOT.glob('*.md'):
        t = p.read_text(encoding='utf-8')
        if re.search('不是[^\n。]*而是',t):
            forbidden.append(str(p))
        if any(ord(c)<32 and c not in '\n\r\t' for c in t):
            controls.append(str(p))
        for target in re.findall(r'\]\((D:/[^)\n]+)\)',t):
            if not Path(target).exists():
                badlinks.append({'source':str(p),'target':target})
        current = []
        for line in t.splitlines()+['']:
            if (line.startswith('| ') or line.startswith('|---')) and line.endswith('|'):
                current.append(line.count('|'))
            elif current:
                if len(set(current)) != 1:
                    table_errors.append(str(p))
                current = []
    json_checked = []
    for p in ROOT.rglob('*.json'):
        if p.name in ['DELIVERY_MANIFEST.json','DOCUMENT_QA.json']:
            continue
        read(p)
        json_checked.append(str(p))
    qa = {'schema':'fi640-fixed-A-review/document-qa/1','date_asia_shanghai':'2026-11-11',
          'json_files_parsed':json_checked,'broken_links':badlinks,'forbidden_style':forbidden,
          'unexpected_control_characters':controls,'markdown_table_errors':table_errors,
          'scalar_checks_passed':385,'historical_inputs_unchanged':len(universe),
          'embedded_fingerprints_matched':refs['records_checked'],'pdf_structure':'PASS/PASS',
          'rendered_source_pages_visually_inspected':4,
          'no_historical_writes_observed':True}
    assert not badlinks and not forbidden and not controls and not table_errors, qa
    write(EV/'DOCUMENT_QA.json',qa)
    files = [fingerprint(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='DELIVERY_MANIFEST.json']
    write(EV/'DELIVERY_MANIFEST.json',{'schema':'fi640-fixed-A-review/delivery-manifest/1',
          'date_asia_shanghai':'2026-11-11','status':'SEALED_TARGETED_REVIEW_COMPLETE',
          'excludes_self':True,'files':files})
    print(json.dumps({'status':verdict['status'],'scalar_checks':385,
                       'historical_files_unchanged':len(universe),
                       'embedded_fingerprints_matched':refs['records_checked'],
                       'delivery_manifest_entries':len(files),'QA':'PASS'},ensure_ascii=False))

if __name__ == '__main__':
    main()
