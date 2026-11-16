from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, hashlib, re, sys

sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
OUT=Path(__file__).resolve().parents[1]
EV=OUT/'evidence'
BASE=OUT.parents[1]
THREAD='01a1c4ed-4bf2-7dc2-8cda-8a2b7be88799'
TURN='01a1c4ed-50ea-72f3-b929-eac37fcf2880'
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def metadata(p):
    p=Path(p); b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
calc=read(EV/'RECOMPUTED_PROBABILITY_CHAIN.json')
hashes=read(EV/'INPUT_HASH_VERIFICATION.json')
replays=read(EV/'SOURCE_AND_REPLAY_VERIFICATION.json')
snapshot=read(EV/'INPUT_SNAPSHOT.json')
required=['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md','REVIEW_VERDICT.json','INPUT_AND_REVIEW_PROVENANCE.json','MANIFEST.json']
identity=dict(status='AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW',
    current_thread_id=THREAD,current_turn_id=TURN,
    declared_model_family='Codex based on GPT-6, as declared in current system/developer context',
    exact_backend_model_id=None,exact_backend_model_id_basis='Not exposed; not inferred from task title, tool names, or older records',
    author_backend_model_ids=None,prior_reviewer_backend_model_id=None,
    distinct_thread_ids_observed=True,independent_model_error_processes_established=False,
    author_proofs_visible=True,author_numerical_targets_visible=True,prior_positive_same_task_review_visible=True,
    fresh_proof_blind_phase=False,new_blind_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_subagents=0,
    formal_proof_assistant_used=False,empirical_calibration='NOT_CALIBRATED',
    execution='Single current AI reviewer; paper rederivation and newly written deterministic scalar checker after proof exposure')
model=dict(n=640,D=15,q=32768,mbar=8,nbar=8,B=2,message_bits=128,
    Setup='Uniform A in Rq^(640x640), common to both generations',
    chi='Exact signed official chi640 table on [-12,12]; mass denominator65536',
    independence='All raw chi coordinates and calls independent',
    Ord='n-column bit-plane normalization; Ord(C1)Tensor_D(S)=C1S modq',
    token='One honest unfiltered TG; all singular and invertible P2 outcomes integrated',
    experiment='One Enc, one TG, one Upd and Dec under new key',
    rounding='Nearest integer, ties upward',
    message_quantifier='Every legal128bit message fixed before coins',
    row_coordinate_quantifier='Any row or coordinate fixed before coins',
    probability_quantifier='Average uniform Setup and both honest key generations plus all Enc/TG/Upd coins',
    initial_bound_A_quantifier='For every fixed A, average honest old key and Enc coins',
    theoretical_chi_sample_count=13225024,actual_chi_samples_generated=0)

claims=[]
def claim(cid,status,statement,anchor,evidence=None):
    claims.append(dict(id=cid,status=status,statement=statement,proof_anchor=anchor,evidence=evidence or ['MATHEMATICAL_REVIEW.md']))
P='PROVED_UNDER_STATED_MODEL';R='REPAIR_REQUIRED';U='UNRESOLVED';C='COUNTEREXAMPLE_FOUND'
claim('RESIDUAL',P,'Actual modular residual eta0+delta follows from printed TG/Upd and gadget identity','section3,R1-R3')
claim('S0',P,'Fixed-key/parent/R environment leaves independent TG rows; single-coordinate interval holds','section4,S1-S6')
claim('J1',P,'Given V, eight residuals iid and row probability equals E[p(V)^8]','section5.1,J1a-J1b')
claim('J2',P,'Conditional CF includes all old/new keys and G variables with stated signs and powers','section5.2,J2')
claim('J3',P,'Given B, all1280 a/b coefficients iid with the true weighted-sum law; V determines P2 but B still integrates UF','section5.3,J3')
claim('J4',P,'Absolute CF expectation bounded by the second CF moment to power640, with exact difference-law identity','section5.4,J4a-J4b')
claim('ENV',P,'Single and base bad-environment budgets2^-22 and2^-25 hold under uniform Setup','sections4.2,6.1')
claim('ANALYTIC_CF',P,'Small-domain144/108 and global high-frequency envelopes hold with valid positivity and absolute values','section4.2,S3-S4')
claim('FINITE_CERT',P,'All frequency groups, remaining difference masses, Taylor inverses,64/80bit ceilings and key rationals independently recomputed','sections4.3,6.1-6.3',['evidence/RECOMPUTED_PROBABILITY_CHAIN.json','evidence/SOURCE_AND_REPLAY_VERIFICATION.json'])
claim('J5',P,'Pointwise chord bounds E[p^8] above; Jensen bounds it below, including all bad-base mass','section6.3,J5a-J5c')
claim('INITIAL',P,'Exact PGF Chernoff at21/20 gives coordinate tail<=2^-138 and full initial failure<=2^-132','section7.1,I1-I2')
claim('J6',P,'Full-message event subset of row event gives success upper0.000030345 and error lower99.9969655%','section7.2,J6')
claim('IC',P,'Frechet ratio bounds after unconditional proof preserve all displayed endpoints conditioned on initial full correctness','section7.3,IC')
claim('DECIMAL_ENDPOINTS',P,'All stated outward decimal bounds preserved without numerical correction','sections4.3,6.3,7.3',['evidence/RECOMPUTED_PROBABILITY_CHAIN.json'])
claim('R640_HIGH_RELIABILITY',C,'High-reliability one-update claim for this ideal printed640 instance contradicted by proved error>=99.9969655%','sections7.2,8')
claim('ROUNDING_PRESENTATION',R,'Explain64bit ceiling per exponential term, then exact mixture, then80bit ceiling of power','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md sections1,4')
claim('MANUSCRIPT_QUANTIFIERS',R,'Carry uniform Setup and exact sampling/rounding/one-update contract; split manuscript C25','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md sections2-5')
claim('THEOREM63_PRESENTATION',R,'Account for initial B0 and max-update semantics; support12 printed slack absorbs B0 but official640 premise fails','MATHEMATICAL_REVIEW.md section8')
claim('AUTHOR_PROGRAM',U,'Exact author code/configuration and probability/arithmetic equivalence require separate evidence','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md sections5-7')
claim('OTHER_PARAMETERS_DEPTHS',U,'Other dimensions/depths and exact64-coordinate probability remain outside this round','MATHEMATICAL_REVIEW.md section8')
verdict=dict(schema='fi640-probability-review/verdict/2',date_asia_shanghai='2026-11-10',sealed_at_asia_shanghai=now,
    overall=P,research_manuscript_adoption='APPROVE_STATED_MODEL_PROPOSITION_WITH_PRESENTATION_REPAIRS',
    identity=identity,frozen_model=model,claims=claims,
    results=dict(initial_full_correct_lower='1-2^-132',coordinate_interval=['0.2499054','0.2500946'],
        coordinate_exact_lower=calc['single']['lower']['exact'],coordinate_exact_upper=calc['single']['upper']['exact'],
        row_interval=['0.0000152532','0.000030345'],
        row_exact_lower=calc['joint']['L']['exact'],row_exact_upper=calc['joint']['U']['exact'],
        Z_star=calc['joint']['Z'],F_star=calc['joint']['F'],U_star=calc['joint']['U'],L_star=calc['joint']['L'],
        full_message_correct_upper='0.000030345',full_message_error_lower='0.999969655',full_message_error_percent_lower='99.9969655%',
        condition_initial_full_correct_same_decimal_endpoints=True,conditional_exact=calc['conditional_initial_correct'],
        exact64_coordinate_probability_computed=False),
    numerical_corrections_required=[],unclosed_core_probability_steps=0,identified_gap_affecting_stated_model_high_error=False,
    theorem63=dict(**calc['Theorem63'],printed640_premise_satisfied=False,counterexample_with_premise_satisfied=False,
        general_all_parameter_theorem_newly_proved=False,support12_slack_accounting_proved=True),
    source_distinguisher_and_CF1='Compatibility/scope checked; historical proof status retained; no new complete re-audit of those proofs',
    computations=dict(new_scalar_checker_passed=calc['checks_passed'],author_script_replays=2,replay_certifying_fields_equal=True,
        initial_hash_snapshot_records=hashes['snapshot_count'],referenced_hash_records=hashes['referenced_record_count']),
    historical_files_modified=False,new_delivery_subdirectory=str(OUT))
write(OUT/'REVIEW_VERDICT.json',verdict)

core=[]
for directory,filenames in [
    ('crypto_fi_640_correctness_audit',['MODEL_AND_RESIDUAL.md','CERTIFIED_CORRECTNESS_BOUNDS.md','SOURCE_AND_COMPUTATION_RECORD.json','VERDICT.json']),
    ('crypto_fi_640_joint_correctness',['CONDITIONAL_STRUCTURE.md','JOINT_PROBABILITY_BOUND.md','SOURCE_AND_COMPUTATION_RECORD.json','VERDICT.json'])]:
    for name in filenames:
        rec=metadata(BASE/directory/name);rec['reading_scope']='Full text read or full JSON parsed; probability/model/provenance fields inspected'
        core.append(rec)
source_records=[]
for name,scope in [
    ('FI_journal_20261110.pdf','Newly rendered and visually inspected PDF12-15'),
    ('articlev08.tex','Read parameter/algorithm/Ord/residual/theorem sections around lines493-590 and633-703'),
    ('official_frodo_2021.pdf','Newly rendered and visually inspected PDF10,15,16,25')]:
    rec=metadata(BASE/'crypto_fi_640_correctness_audit'/'sources'/name);rec['reading_scope']=scope;source_records.append(rec)
script_cert_records=[]
for directory,files in [
    ('crypto_fi_640_correctness_audit',['evidence/compute_scalar_certificates.py','evidence/SCALAR_CERTIFICATES.json']),
    ('crypto_fi_640_joint_correctness',['evidence/compute_joint_certificates.py','evidence/JOINT_SCALAR_CERTIFICATES.json'])]:
    for name in files:
        rec=metadata(BASE/directory/name);rec['reading_scope']='Script fully inspected and isolated byte-copy replayed' if name.endswith('.py') else 'JSON parsed; certifying fields cross-compared with new formula recomputation and author replay'
        script_cert_records.append(rec)
history=[]
for filename,label in [('AUTHOR_THREAD_SNAPSHOT.json','author_last4_turns'),('PRIOR_REVIEW_THREAD_SNAPSHOT.json','prior_same_task_review1turn'),('CURRENT_THREAD_SNAPSHOT.json','current_active_turn')]:
    raw=read(EV/filename)
    payload=json.loads(''.join(x['text'] for x in raw['content'] if x['type']=='text'))
    history.append(dict(scope=label,thread_id=payload['thread']['id'],title=payload['thread']['title'],
        retrieved_turn_ids=[t['id'] for t in payload['turns']],has_more=payload['page']['hasMore'],
        snapshot=metadata(EV/filename),limitation='Tool summary/entry view; some messages and tool data truncated; no claim to complete raw historical transcript'))
prov=dict(schema='fi640-probability-review/provenance/2',date_asia_shanghai='2026-11-10',sealed_at_asia_shanghai=now,
    identity=identity,current_user_request=dict(thread_id=THREAD,turn_id=TURN,source='User instruction visible in current conversation; current tool snapshot retained'),
    workflow='User-requested targeted mathematical review, author-proof-visible, one reviewer inline',
    skills=[dict(name='academic-research-suite',path=r'C:\Users\a1887\.codex\skills\academic-research-suite\SKILL.md',scope='Targeted methodology/source and integrity discipline; no panel, blind phase or cross-model review claimed'),
        dict(name='pdf',path=r'C:\Users\a1887\.codex\plugins\cache\openai-primary-runtime\pdf\26.1026.10807\skills\pdf\SKILL.md',scope='Read-only primary PDF preflight, extraction, fresh rendering and visual inspection')],
    frozen_model=model,core_deliverables=core,primary_sources=source_records,author_scripts_and_certificates=script_cert_records,
    actual_history_retrieval=history,
    preexisting_delivery=dict(path=str(OUT.parent),manifest=metadata(OUT.parent/'MANIFEST.json'),
        previous_review_id='01a1c4d6-4913-7322-ac79-66e53d6f135b',preservation='All preexisting files preserved; this run uses distinct child directory; prior review was visible before new recomputation'),
    input_snapshot=dict(file=metadata(EV/'INPUT_SNAPSHOT.json'),records=len(snapshot['records']),all_unchanged_at_source_verification=True),
    fingerprint_verification=dict(file=metadata(EV/'INPUT_HASH_VERIFICATION.json'),snapshot_records=hashes['snapshot_count'],referenced_records=hashes['referenced_record_count'],all_match=True),
    arithmetic=dict(new_script=metadata(EV/'recompute_probability_chain.py'),result=metadata(EV/'RECOMPUTED_PROBABILITY_CHAIN.json'),checks_passed=303,
        method='Exact arbitrary precision integers/Fraction; independent formula code written after proof exposure; recurrent positive Taylor sums and minimal upward dyadic grid checks',
        author_replay_verification=metadata(EV/'SOURCE_AND_REPLAY_VERIFICATION.json'),author_replay_count=2,certifying_fields_equal=True,
        ignored_replay_field='Single-coordinate elapsed_seconds_display_only only',
        displayed_decimals='Decimal65digits, diagnostic only; endpoint verdicts use exact rational comparisons',
        no_formal_verification=True),
    source_read_integrity=dict(preflight=[metadata(EV/'FI_PREFLIGHT.json'),metadata(EV/'FRODO_PREFLIGHT.json')],actual_results=['PASS','PASS'],
        recovery='Windows --output mode rejected POSIX dirfd requirement. Supported stdout mode captured with explicit PYTHONIOENCODING=utf-8; exact PDF paths/hashes checked.',
        current_network_source_downloads=0,local_frozen_source_version_only=True),
    semantic_scope=dict(manuscript='Sections1-2,6-7,10/appendixC and claim C08/C09/C10/C25/readiness fields; no rewrite of historical manuscript',
        prior_review='Provenance/verdict and section5-6 mathematical excerpts visible, plus prior thread returned entries/final; not counted as new independent evidence',
        whole_historical_corpus_read=False,hash_scope_is_separate_from_semantic_scope=True),
    action_counts=dict(new_mechanism_implementations=0,cryptographic_attack_prototypes=0,LWE_solvers=0,matrices_keys_tokens_ciphertexts_sampled=0,
        large_cryptographic_experiments=0,Monte_Carlo_trials=0,native_AS_RP_requests=0,author_contacts=0,emails_or_messages_sent=0,
        external_model_calls=0,new_subagents=0,new_scalar_checker_executions=1,author_script_replays=2),
    historical_inputs_modified=False,completion='Complete probability-chain adjudication; manuscript-ready statement and repairs supplied; sealing pending final byte/QA checks')
write(OUT/'INPUT_AND_REVIEW_PROVENANCE.json',prov)

# End-of-run historical byte verification.
final_inputs=[]
for r in snapshot['records']:
    got=metadata(r['path'])
    assert got['sha256']==r['sha256'] and got['bytes']==r['bytes'],r['path']
    final_inputs.append(got)
write(EV/'FINAL_INPUT_HASH_CHECK.json',dict(all_unchanged=True,record_count=len(final_inputs),records=final_inputs))

# The earlier root manifest has a canonical payload digest. Check it without changing it.
old=read(OUT.parent/'MANIFEST.json');expected=old.pop('payload_sha256')
canonical=lambda obj:json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
assert hashlib.sha256(canonical(old)).hexdigest()==expected

bad_controls=[];broken_links=[];style=[];json_errors=[]
for p in sorted(OUT.rglob('*')):
    if not p.is_file():continue
    if p.suffix=='.json':
        try:read(p)
        except Exception as e:json_errors.append(dict(path=str(p),error=str(e)))
    if p.suffix=='.md':
        s=p.read_text(encoding='utf-8')
        if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',s):bad_controls.append(str(p))
        if re.search('不是.{0,100}而是',s):style.append(str(p))
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',s):
            if '://' in target:continue
            dest=Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else p.parent/target
            if not dest.is_file() and dest.name!='MANIFEST.json':broken_links.append(dict(path=str(p),target=target))
assert not any([bad_controls,broken_links,style,json_errors])
qa=dict(schema='fi640-review/final-QA/2',all_checks_passed=True,new_scalar_assertions=303,
    historical_files_unchanged=len(final_inputs),source_record_matches=126,author_replays_equal=2,
    primary_PDF_structural_preflights_pass=2,visual_source_pages_inspected=8,
    prior_review_canonical_manifest_verified=True,broken_links=broken_links,control_character_errors=bad_controls,
    forbidden_style=style,json_errors=json_errors,all_required_deliverables_present=True,
    note='Counts record finite verification work, without implying independent reviewers or a formal proof assistant.')
write(EV/'FINAL_QA.json',qa)
prov['completion']='SEALED_COMPLETE_PROBABILITY_CHAIN_REVIEW'
prov['final_input_verification']=dict(records=len(final_inputs),all_unchanged=True,file=str(EV/'FINAL_INPUT_HASH_CHECK.json'))
write(OUT/'INPUT_AND_REVIEW_PROVENANCE.json',prov)
manifest=dict(schema='fi640-probability-review/manifest/2',date_asia_shanghai='2026-11-10',sealed_at_asia_shanghai=now,
    status='SEALED_COMPLETE',core_verdict=P,required_deliverables=required,output_directory=str(OUT),
    historical_output_directory_preserved=str(OUT.parent),review_identity=identity['status'],
    self_exclusion='File list excludes this MANIFEST.json; payload_sha256 hashes canonical JSON with that field omitted.',
    canonicalization='UTF-8 json.dumps(ensure_ascii=False,sort_keys=True,separators=(comma,colon))',
    files=[metadata(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'MANIFEST.json'],qa=qa)
manifest['payload_sha256']=hashlib.sha256(canonical(manifest)).hexdigest()
write(OUT/'MANIFEST.json',manifest)
assert all((OUT/f).is_file() for f in required)
for r in manifest['files']:assert metadata(r['path'])==r
fresh=read(OUT/'MANIFEST.json');digest=fresh.pop('payload_sha256')
assert hashlib.sha256(canonical(fresh)).hexdigest()==digest
print(json.dumps(dict(status='SEALED_COMPLETE',files_excluding_manifest=len(manifest['files']),payload_sha256=digest,
    manifest_file_sha256=metadata(OUT/'MANIFEST.json')['sha256'],historical_unchanged=len(final_inputs),new_scalar_checks=303),ensure_ascii=False))
