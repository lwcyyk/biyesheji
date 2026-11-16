"""Seal the final internal review; hashes certify bytes and named checks only."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import platform
import re
import sys

OUT = Path(r'D:\毕业设计\crypto_fi_final_internal_review')
E = OUT / 'evidence'
PACKAGE = Path(r'D:\毕业设计\crypto_fi_external_review_package')
V3 = Path(r'D:\毕业设计\crypto_fi_research_manuscript_v3')
FROZEN = PACKAGE / 'frozen'
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def fingerprint(p):
    return {'path': str(p), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

before = read(E / 'INPUT_SNAPSHOT_BEFORE.json')
after = [fingerprint(Path(x['path'])) for x in before]
assert before == after
current = {str(p) for root in [PACKAGE, V3] for p in root.rglob('*') if p.is_file()}
assert current == {x['path'] for x in before}
dump(E / 'INPUT_SNAPSHOT_AFTER.json', after)
dump(E / 'INPUT_INTEGRITY_RESULT.json', {
    'status': 'PASS', 'files': len(before), 'all_bytes_and_hashes_equal': True,
    'added_or_removed_input_files': [], 'historical_input_writes': 0,
    'scope': 'All files in submitted portable package and original v3 directory, from first explicit snapshot through final seal',
    'snapshot_started_after_initial_entry_and_source_reads': True,
    'end_check_asia_shanghai': NOW})

matrix = read(V3 / 'CLAIM_EVIDENCE_MATRIX.json')
corrections = []
def correction(id_, claim_id, patch, reason):
    i = next(i for i, c in enumerate(matrix['claims']) if c['id'] == claim_id)
    old = matrix['claims'][i]
    corrections.append({'id': id_, 'claim_id': claim_id, 'decision_bearing': False,
                        'status': 'CLOSED_IN_FINAL_REVIEW_ADOPTION_TEXT',
                        'source': str(V3 / 'CLAIM_EVIDENCE_MATRIX.json'),
                        'changes': [{'json_pointer': '/claims/' + str(i) + '/' + k,
                                     'old': old.get(k), 'adopted': v} for k, v in patch.items()],
                        'reason': reason, 'source_manuscript_modified': False,
                        'theorems_or_numerical_endpoints_changed': False})
correction('L1', 'C25b', {
    'assumptions': ['Current proofs cover640/976/1344, each under its own frozen one-update contract; new depths, reuse/selection, exactfull64 and software transfer require their own analysis.']},
    'Inherited fixed640-only premise conflicts with updated three-profile scope of this registry row; F1-F32 and six checked endpoints settle the intended scope.')
correction('L2', 'C25d', {
    'evidence_status': 'PROVED_UNDER_STATED_MODEL',
    'assumptions': ['Each of the three profiles uses its own exact chi law, common A across two generations, matched Ord/Tensor, one honest unfiltered TG/Upd, and official half-up Decode; each A quantifier and I conditioning follow its own proof.'],
    'limitations': 'Three separate finite one-update configurations;Theorem6.3 sufficient premises unmet;actual author software transfer remains unresolved.'},
    'The row now asserts a positive high-error theorem; the inherited COUNTEREXAMPLE_FOUND tag originally addressed an interpretation of high reliability. This adoption removes ambiguity about the target of the counterexample.')
correction('L3', 'C24', {
    'quantifiers': 'Bounded source reading/search: inherited through2026-11-08 plusE13 through2026-11-10 andE15 registered2026-11-11 receipts;current final review adds0 live priority searches;global first unestablished.'},
    'Synchronizes inherited row cutoff with v3 top-level priority_scope and manuscript1.2; it adds no new search coverage.')
dump(E / 'LOCAL_SCOPE_CORRECTIONS.json', {
    'schema': 'frodo-fi-final-review/local-adoption-corrections/1',
    'status': 'THREE_NONBLOCKING_REGISTRY_CLARIFICATIONS_COMPLETED',
    'adoption_authority': 'FINAL_INTERNAL_DECISION.md section7',
    'original_sources_read_only': True, 'corrections': corrections})

read_log = []
def log(seq, phase, paths, scope, exposure=None):
    read_log.append({'sequence': seq, 'phase': phase, 'paths': [str(x) for x in paths],
                     'scope': scope, 'exposure': exposure})
log(0, 'initial_context', [],
    'User targets and six percentages; user AGENTS implementation gate; injected MEMORY_SUMMARY already visible; no rollout summaries retrieved.',
    'Prior positive historical result summaries visible before source reading; no proof-blind claim.')
log(1, 'entry_batch', [PACKAGE/'START_HERE.md', Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\SKILL.md')],
    'Entry and ARS routing read in one independent-call batch; no within-batch completion order claimed.',
    'START_HERE discloses E16, historical positive verdict summaries, arithmetic counts and author-software status.')
log(2, 'navigation', [PACKAGE/'SOURCE_GUIDE.md', PACKAGE/'REPLAY.md'],
    'Full source guide/replay instructions; relevant file inventory; ARS reviewer workflow and PDF skill; the DA role prompt was partially surfaced as a challenge checklist. User single-review specification controls execution.',
    'Further summaries visible; role-separated panel not invoked.')
log(3, 'original_FI_TeX', [FROZEN/'crypto_fi_research_manuscript_v1/sources/articlev08.tex'],
    'Game lines283-491, PKE/UE/Ord/correctness lines492-708, security and implementation lines709-963, plus preliminary introduction snippets. These source passages preceded standalone historical opinion files.')
log(4, 'draft_A_and_PDF_integrity', [V3/'CRYPTOANALYSIS_DRAFT.md'],
    'Draft sections1-5; structural preflight and new extraction of FI2021/2023 source PDFs; first explicit input snapshot taken.',
    'Author proofs and integrated historical discussion visible. Initial preflight subprocess stdout decoding failed once; fixed by explicit -X utf8 and rerun successfully; no failed result promoted.')
log(5, 'original_FI_primary', [FROZEN/'crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf'],
    'Physical PDF9-15 newly extracted text, cross-checked with TeX. Other pages completed at sequence10; visual13-15 at sequence9.')
log(6, 'draft_A_B_proofs', [V3/'CRYPTOANALYSIS_DRAFT.md'],
    'Sections6-7; AppendixF1-F32 and G; AppendixE then D; public replay scripts inspected before execution. All draft mathematical sections are covered across sequences4,6,8,11.')
log(7, 'deterministic_scalar_replay', [PACKAGE/'replay/run.py', PACKAGE/'replay/scalar_launcher.py', PACKAGE/'replay/verify_package.py'],
    'Executed only copied deterministic scalar scripts in new external sandbox; seven entries, eleven complete mathematical payload comparisons. Exact source/certificate arrays checked mechanically.',
    'Historical author/review checker code and their expected certificates visible; this is replay, not independent error-process certification.')
log(8, 'official_sources_and_scope', [FROZEN/'crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf',
    FROZEN/'crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf',
    FROZEN/'crypto_fi_official_profile_review/evidence/OFFICIAL_1344_ERRATUM_LIVE_RECEIPT.json', V3/'CRYPTOANALYSIS_DRAFT.md'],
    'Official2021 physical10,14,15,16,25;2023 physical8,15,16; frozen issue35 primary-tool receipt in full; draft8-10. Frozen receipt was read locally; no new live GitHub retrieval.')
log(9, 'visual_source_check', [E/'FI_p13.png', E/'FI_p14.png', E/'FI_p15.png', E/'FRODO2023_p16.png'],
    'Four actual rendered source images inspected through view_image. Rendering and structural checks supply reading-integrity evidence.')
log(10, 'complete_FI_text', [E/'FI_EXTRACT.txt'],
    'Physical1-8 and16-23 read in full extracted text; combined with sequence5 gives all23 physical pages, including references.')
log(11, 'remaining_draft_and_matrix', [V3/'CRYPTOANALYSIS_DRAFT.md', V3/'CLAIM_EVIDENCE_MATRIX.json'],
    'AppendixA-C and bibliography; all61 claim rows selected fields: id,claim,location,object,quantifiers,assumptions,dependencies,status,limitations; frozen_models,parametric_criterion,main_result_dependency_audit; clipped initial claim output filled by separate rows27-49 read. Evidence/path metadata were inspected selectively and mechanically, not claimed as full prose reading.',
    'Integrated author descriptions of ROUND005,LWE,E7/E8,E11/E16/E17 and their positive outcomes visible before the preliminary checkpoint.')
log(12, 'primary_nearest_precedent', [FROZEN/'crypto_fi_research_manuscript_v1/sources/KLR2019.pdf'],
    'Physical17,27,43,44,45 extracted text, after fresh structural preflight; Def11/Def14 and AppB.2 explicitly compared.')
log(13, 'pre_history_judgment', [E/'PRE_HISTORICAL_COMPARISON.md'],
    'Written before opening standalone historical mathematical opinion/verdict/comparison files. Minute-level document marker is approximate; actual file timestamp retained below.',
    'Summaries, integrated draft history and replay code already visible; current proof-blind review count remains0.')
log(14, 'historical_E16_and_AG', [FROZEN/'crypto_fi_official_profile_review/MATHEMATICAL_REVIEW.md',
    FROZEN/'crypto_fi_official_profile_review/CORRECTIONS_AND_MANUSCRIPT_IMPACT.md',
    FROZEN/'crypto_fi_research_manuscript_v1/sources/AG2011_author.pdf'],
    'E16 mathematical report and corrections read; output tail filled by separate sections9-13 reads. AG physical7,8,9,10,19 selected extracted text; some page9 output truncated, no full AG reading claimed.',
    'Full historical proof commentary and opinions now visible.')
log(15, 'historical_round005_and_verdicts', [FROZEN/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase2/FINAL_REVIEW_VERDICT.json',
    FROZEN/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase2/COMPARISON.md'],
    'Phase2 metadata, passed claims, repairs and unresolved entries; comparison selected text including D1/D2,CF1,scope; initial large output truncated, opening48 lines later reread. Phase1 derivation prose was not opened; its scalar script was replayed.')
history_roots = ['crypto_fi_lwe_independent_review','crypto_fi_640_probability_review',
                 'crypto_fi_640_probability_review/review_01a1c4ed','crypto_fi_640_fixed_A_review','crypto_fi_official_profile_review']
log(16, 'historical_targeted_comparison', [FROZEN/r/'REVIEW_VERDICT.json' for r in history_roots],
    'Structured selected identity/verdict/repair fields of all five JSON records. LWE,640 supplemental,fixed-A and E16 correction reports read in full; their historical manuscript adoption checked against current v3. Other standalone mathematical reports were not newly read in full.')
log(17, 'priority_and_software', [FROZEN/'crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md',
    FROZEN/'crypto_fi_publication_impact_audit/evidence/SEARCH_LEDGER.json',
    FROZEN/'crypto_fi_official_profile_correctness/evidence/PUBLIC_PRECEDENT_SEARCH_RECEIPT.json',
    FROZEN/'crypto_fi_author_implementation_audit/IMPLEMENTATION_MODEL_MAPPING.md',
    FROZEN/'crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md'],
    'Impact report,mapping and minimal spec full text; E13 search ledger complete; E15 raw receipt first11000 characters only. Underlying31-query raw result batches were not newly read. No new search-coverage certification.')
log(18, 'base_PKE_primary_and_exact_endpoints', [E/'FRODO2021_EXTRACT.txt', V3/'certificates/UNIFIED_RESULT_SELECTORS.json',
    V3/'certificates/OFFICIAL_PROFILE_CERTIFICATES.json', V3/'certificates/640_FIXED_A_CERTIFICATES.json',
    V3/'certificates/640_UNIFORM_RESULTS.json', V3/'MANIFEST.json'],
    'Official2021 physical18-19; structured certificate keys and selected payloads; full mathematical arrays mechanically recomputed via replay; six exact endpoints directly reconstructed with a new small audit script; G.1,entire six matrix-mode objects and selector binding checked; original/frozen core equality and43 manifest entries verified.')
extra = [Path(r'D:\毕业设计\research_g1_lifecycle_contract\2026-11-09_r01\08_G1_VERDICT_AND_MAINLINE_HANDOFF.md'),
         Path(r'D:\毕业设计\系统总体架构与研究进展_2026-11-09\总体架构与研究进展_技术说明.md'),
         Path(r'D:\毕业设计\mainline_native_isolation_v1\NATIVE_ISOLATION_PROFILE.md')]
log(19, 'business_scope', [FROZEN/'crypto_fi_research_manuscript_v1/evidence/MAINLINE_SOURCE_LOCK.json'] + extra,
    'Source lock first100 lines; G1 handoff full; architecture first95 lines and targeted rg matches including cryptography section; native profile targeted rg matches. No live system operations or new full repository audit.')
log(20, 'decision_and_seal', [OUT/'FINAL_INTERNAL_DECISION.md', E/'final_scalar_checks.py'],
    'Final decision composed, local registry adoption text supplied, all submitted input fingerprints compared, output manifest sealed.')

extra_fingerprints = [fingerprint(p) for p in extra]
dump(E/'ADDITIONAL_SOURCE_FINGERPRINTS.json', {
    'files': extra_fingerprints,
    'basis': 'Recorded after selected semantic reads; no pre-read byte snapshot claimed for these three supplementary business sources.',
    'source_writes': 0})

scalar = read(E/'FINAL_SCALAR_CHECKS.json')
replay = read(E/'scalar_replay/REPLAY_RESULT.json')
package_check = read(E/'PACKAGE_VERIFICATION.json')
assert scalar['status'] == replay['status'] == package_check['status'] == 'PASS'
provenance = {
    'schema': 'frodo-fi-final-internal-review/provenance/1',
    'date_asia_shanghai': '2026-11-11', 'sealed_at_asia_shanghai': NOW,
    'verdict': 'PASS_WITHIN_STATED_SCOPE',
    'review_type': 'SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE',
    'reviewer': {'provider': 'OpenAI', 'application': 'Codex desktop',
        'declared_model_family': 'Codex based on GPT-6 per visible developer context',
        'exact_backend_model_id': None, 'exact_weights_version': None,
        'model_identity_basis': 'Family explicitly stated in session; exact serving model not exposed; OPENAI_MODEL environment value absent.',
        'chat_id': os.environ.get('CODEX_THREAD_ID'), 'chat_id_basis': 'CODEX_THREAD_ID',
        'turn_id': None, 'human_reviewer_id': None, 'operator_contexts': 1,
        'model_error_process_independence_established': False, 'calibration': 'NOT_CALIBRATED'},
    'scope': {'result_A': 'CF-1 original-game source-hiding attack,common pointwise correctness,<=3n+1 calls,Delta->1',
              'result_B': '640/976/1344 ideal one-update reliability,each pre-fixed A and separately uniform full-matrix Setup,same displays under initial full correctness',
              'software': 'WAITING_FOR_AUTHOR_ARTIFACT', 'global_priority': 'SEARCH_BOUNDED_APPLICATION_CANDIDATE',
              'nonempty_hardness_premise_counterexample': 'UNRESOLVED',
              'business_mapping': 'SOURCE_OR_REFINEMENT_GAP; independent cryptanalysis chapter',
              'core_open_mathematical_dependencies_identified': [],
              'candidate_protective_mechanism_implementation_gate': 'Separate; concrete input family,fixed metric,strongest like-for-like baseline,predicted strict gap and at least one strict higher-cost baseline instance required'},
    'exposure': {'author_proofs_visible': True, 'targets_visible_from_start': True,
                 'historical_positive_summaries_visible_from_start': True,
                 'standalone_historical_reviews_opened_after_preliminary_judgment': True,
                 'prior_review_code_used_in_scalar_replay_before_preliminary_checkpoint': True,
                 'fresh_proof_blind_review': False, 'integrated_manuscript_contains_prior_reviews': True,
                 'memory_summary_injected': True, 'rollout_summary_files_retrieved': [],
                 'historical_chat_tools_used': False},
    'reading_order': read_log,
    'order_resolution': 'Sequence denotes actual tool-call batches/phases; no finer order inferred for independent calls batched together.',
    'first_observed_tool_clock_utc': '2026-11-11 06:36:57 UTC',
    'preliminary_checkpoint_file_timestamp_utc': datetime.fromtimestamp((E/'PRE_HISTORICAL_COMPARISON.md').stat().st_mtime, timezone.utc).isoformat(),
    'skills': ['academic-research-suite: user-defined single-AI audit; source,scope,adversarial challenge and read-only integrity guidance applied inline',
               'pdf: structural preflight,extraction and four critical rendered-page inspections'],
    'skill_execution_adaptation': 'No simulated journal panel; no subagent delegation; user explicitly specified single AI and final internal criteria.',
    'runtime': {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
                'replay_standard_library_only': True, 'pdf_reading_runtime_used_pypdf_and_pymupdf': True},
    'verification': {'seven_scalar_entries': len(replay['runs']), 'complete_payload_comparisons': len(replay['comparisons']),
                     'all_mathematical_payloads_equal': replay['all_mathematical_payloads_equal'],
                     'all_replay_data_file_opens_confined': replay['all_scalar_file_opens_confined_to_work_or_python_runtime'],
                     'package_payload_entries': package_check['manifest_file_count'], 'package_files_including_manifest': replay['package_file_count'],
                     'submitted_inputs_unchanged': True, 'submitted_input_files': len(before),
                     'direct_endpoint_reconstructions': 6, 'v3_manifest_entries': scalar['v3_manifest_entries_verified'],
                     'six_complete_matrix_selector_modes_equal': scalar['six_complete_matrix_selector_modes_equal'],
                     'symbolic_proof_evidence': 'FINAL_INTERNAL_DECISION sections3-5; finite-check counts do not replace this reasoning',
                     'integrity_evidence': 'MANIFEST and INPUT_INTEGRITY_RESULT certify named byte identities, not mathematical truth'},
    'local_adoption_clarifications': {'count': 3, 'decision_bearing': False,
                                     'file': 'evidence/LOCAL_SCOPE_CORRECTIONS.json', 'original_inputs_modified': False},
    'tooling_incidents': [{'kind': 'PDF preflight child stdout decode', 'attempt': 1,
                          'effect': 'First invocation failed before PDF result was saved; rerun with explicit UTF-8 succeeded for each PDF.',
                          'core_math_impact': 'None; failed attempt was not treated as evidence.'}],
    'action_counts': {'new_single_AI_comprehensive_reviews': 1, 'new_human_reviews': 0,
        'new_cross_model_reviews': 0, 'new_blind_reviews': 0, 'new_subagents': 0,
        'new_independent_error_process_certifications': 0, 'proof_assistant_checks': 0,
        'new_deterministic_direct_endpoint_checker': 1, 'portable_scalar_script_entries_executed': 7,
        'cryptographic_samples_generated': 0, 'monte_carlo_runs': 0, 'LWE_solver_implementations': 0,
        'candidate_mechanism_implementations': 0, 'author_UE_executions': 0,
        'new_live_priority_searches': 0, 'external_model_calls': 0,
        'author_contacts_or_messages': 0, 'native_AS_RP_requests': 0,
        'automations_created_or_resumed': 0, 'historical_input_writes': 0},
    'input_fingerprint_files': ['evidence/INPUT_SNAPSHOT_BEFORE.json', 'evidence/INPUT_SNAPSHOT_AFTER.json'],
    'required_deliverables': ['FINAL_INTERNAL_DECISION.md','REVIEW_PROVENANCE.json','MANIFEST.json'],
    'stage_complete': True}
assert provenance['reviewer']['chat_id'] == '01a1c951-f315-7fe2-8cf8-ec84f397d959'
dump(OUT/'REVIEW_PROVENANCE.json', provenance)

report = (OUT/'FINAL_INTERNAL_DECISION.md').read_text(encoding='utf-8')
assert 'PASS_WITHIN_STATED_SCOPE' in report
assert len(re.findall(r'^\| [1-8]\. ', report, re.M)) == 8
assert '不是' not in report
for pct in ['99.4956640%','92.1979375%','79.3884688%','99.9969655%','98.2862369%','91.7186557%']:
    assert pct in report
links = re.findall(r'\]\(([^)]+)\)', report)
for link in links:
    if link.startswith('1-\\'):
        continue  # Display-math multiplication after a closing square bracket.
    if link == 'MANIFEST.json':
        continue  # Created after the QA record, verified by the final readback.
    if not re.match(r'^[a-z]+://', link):
        assert (OUT/link.split('#')[0]).exists(), link
dump(E/'DELIVERY_QA.json', {'status': 'PASS', 'eight_objections_present': True,
                          'six_percentages_present': True, 'all_report_local_links_resolve': True,
                          'prohibited_sentence_pattern_absent': True,
                          'JSON_provenance_valid': True, 'submitted_inputs_unchanged': True,
                          'checked_at_asia_shanghai': NOW})

files = []
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p != OUT/'MANIFEST.json':
        x = fingerprint(p); x['path'] = p.relative_to(OUT).as_posix(); files.append(x)
manifest = {'schema': 'frodo-fi-final-internal-review/manifest/1',
            'date_asia_shanghai': '2026-11-11', 'sealed_at_asia_shanghai': NOW,
            'root': str(OUT), 'status': 'SEALED_FINAL_INTERNAL_REVIEW',
            'verdict': 'PASS_WITHIN_STATED_SCOPE', 'stage_complete': True,
            'required_deliverables': ['FINAL_INTERNAL_DECISION.md','REVIEW_PROVENANCE.json','MANIFEST.json'],
            'self_exclusion': ['MANIFEST.json'], 'files': files,
            'input_integrity': {'status': 'PASS','submitted_files': len(before),
                                'all_submitted_files_unchanged': True,
                                'additional_business_sources_have_post_read_fingerprints_only': True},
            'evidence_interpretation': 'Files certify bytes; exact scalar results certify named finite arithmetic; general mathematical conclusions follow the scoped reasoning in the decision.',
            'payload_hash_rule': 'sha256 of canonical UTF8 JSON excluding payload_sha256;ensure_ascii=False,sort_keys=True,separators=(comma,colon)'}
canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
manifest['payload_sha256'] = hashlib.sha256(canonical).hexdigest()
dump(OUT/'MANIFEST.json', manifest)
print(json.dumps({'status': 'PASS', 'verdict': provenance['verdict'], 'output_files_excluding_manifest': len(files),
                  'submitted_input_files_unchanged': len(before), 'output_manifest_sha256': fingerprint(OUT/'MANIFEST.json')['sha256']}, ensure_ascii=False))
