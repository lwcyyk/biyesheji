"""Integrity/source and document bookkeeping, no cryptographic implementation."""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计')
ROOT=BASE/'crypto_fi_640_joint_correctness'
SRC=ROOT/'sources'
EV=ROOT/'evidence'
OLD=BASE/'crypto_fi_640_correctness_audit'


def readj(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def writej(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):
    p=Path(p)
    return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def ratio(x):return F(int(x['numerator']),int(x['denominator']))


lock=readj(EV/'INPUT_LOCK.json')
assert len(lock['records'])==30
for x in lock['records']:
    p=Path(x['path']);assert pin(p)['sha256']==x['sha256'] and p.stat().st_size==x['bytes']
oldverdict=readj(OLD/'VERDICT.json')
assert oldverdict['independent_review_pending'] is True
cert=readj(EV/'JOINT_SCALAR_CERTIFICATES.json')
assert cert['upper_comparison_verified'] and cert['strict_improvement_over_old_0_2500946']
assert cert['all16384_positive_frequencies_covered'] and cert['initial_correct_condition_same_endpoints']
assert sum(g['count'] for g in cert['frequency_groups'])==16384
upper=ratio(cert['unconditional_row_upper'])
lower=ratio(cert['unconditional_row_lower_Jensen'])
assert ratio(cert['Z'])<F(1,4)
assert F(152532,10**10)<=lower<=upper<=F(30345,10**9)
assert F(30345,10**9)<F(1,32768)
assert ratio(cert['initial_correct_conditioned_upper'])<=F(30345,10**9)
assert F(152532,10**10)<=ratio(cert['initial_correct_conditioned_lower'])

identity=dict(status='INFORMED_JOINT_PROBABILITY_DERIVATION',
              previous_results_visible=True,new_independent_reviews=0,human_reviews=0,
              new_subagents=0,formal_proof_assistant=False,exact_runtime_model_id=None)
actions=dict(cryptographic_protection_implementations=0,LWE_solvers=0,attack_prototypes=0,
             matrices_keys_tokens_ciphertexts_sampled=0,large_crypto_experiments=0,
             native_AS_RP_requests=0,author_contacts=0,messages_or_emails=0,
             network_retrievals=0,project_test_reruns=0,deterministic_scalar_script_runs=2,
             scalar_scope='625chi-difference products; finite exponential envelopes; rational/dyadic powers and integer comparisons; two base Chernoff envelopes')
sources=[]
for name,scope in [
    ('FI_journal_20261110.pdf','Current source images PDF12 KeyGen/Enc/Decode and14 TG/Upd via hash-matched inherited render; frozen journal/v4'),
    ('articlev08.tex','Current TG/Upd/residual/Ord text locators; original model field correspondence'),
    ('official_frodo_2021.pdf','Current original images PDF10 nearest ties upward,25 exact chi640 and official640; prior AlgorithmSampleMatrix coordinate product contract also explicitly fixed by user')]:
    assert pin(SRC/name)['sha256']==pin(OLD/'sources'/name)['sha256']
    sources.append(dict(copy=pin(SRC/name),origin=pin(OLD/'sources'/name),reading_scope=scope))
assert pin(SRC/'INHERITED_SCALAR_CERTIFICATES.json')['sha256']==pin(OLD/'evidence/SCALAR_CERTIFICATES.json')['sha256']

record=dict(schema='fi640-joint/source-and-computation/1',date_asia_shanghai='2026-11-10',
            identity=identity,skills=['academic-research-suite: inline source/paper mathematics audit','pdf: hash-matched primary-image inspection'],
            primary_inputs=[pin(OLD/n) for n in ['MODEL_AND_RESIDUAL.md','CERTIFIED_CORRECTNESS_BOUNDS.md','SOURCE_AND_COMPUTATION_RECORD.json','VERDICT.json']],
            historical_input_record_count=30,historical_input_lock=pin(EV/'INPUT_LOCK.json'),
            all_historical_bytes_unchanged=True,primary_sources=sources,
            source_identity=dict(doi='10.46298/fi.14425',arxiv='2410.03948v4',
                journal_PDF_sha256=pin(SRC/'FI_journal_20261110.pdf')['sha256'],
                current_round_network_download=False,
                structural_preflight_reused='Inherited PASS sidecars for identical PDF byte hashes, all input records reverified'),
            model=dict(n=640,D=15,q=32768,mbar=8,nbar=8,B=2,chi='Exact finite chi640',
                A='Uniform Setup, shared old/new',Ord='n-column bit-plane normalization',
                TG='One honest unfiltered token; no rejection or conditioning on invertibility',
                samples='Every chi coordinate and call independent',rounding='Official nearest integer ties upward'),
            inherited_review_status=dict(single_coordinate_proof='Pending independent mathematics review, as recorded in old VERDICT',
                initial_full_correctness='Inherited informed proof and exact scalar certificate >=1-2^-132; used only for final conditioning corollary',
                new_joint_proof='Informed paper derivation and exact scalar certificates, independent review pending'),
            proof_chain=[
                dict(id='J1',claim='Given V, eight residual coordinates iid',anchor='CONDITIONAL_STRUCTURE sections2-4',
                     reason='Remaining key/G column packets disjoint and product-chi given all shared raw coefficients'),
                dict(id='J2',claim='Conditional characteristic function matches candidate',anchor='CONDITIONAL_STRUCTURE section5',
                     reason='Combine shared new-key appearances into a,b before factoring; remaining individual chi variables independent'),
                dict(id='J3',claim='Given base B, 1280 a/b coefficients iid T_B',anchor='CONDITIONAL_STRUCTURE section6',
                     reason='Distinct raw U/F columns; h,r fixed; original unfiltered coin law retained'),
                dict(id='J4',claim='Absolute Fourier first moment bound',anchor='JOINT_PROBABILITY_BOUND sections2-5',
                     reason='Cauchy-Schwarz and exact chi-difference identity; all frequencies enclosed'),
                dict(id='J5',claim='E p(V)^8 bound',anchor='JOINT_PROBABILITY_BOUND section6',
                     reason='Pointwise chord inequality, then conditional expectation and charged bad base environments'),
                dict(id='J6',claim='Full message and initial-correct conditioned bounds',anchor='JOINT_PROBABILITY_BOUND section7',
                     reason='Event inclusion and Frechet ratio bounds, no new independence after initial conditioning')],
            conditioning=dict(V='sigma(A,U0,F0,U1,F1,U2,F2,R)',
                base_B='sigma(A,U0,F0,R)',remaining_given_V='Old/new S/E and G0/G1/G2, independent by output columns',
                base_good_event='Parent u has an odd component,w>=4500,sum r_i^2>=3500',
                event_measurability='Base good event B-measurable; excludes keys/G and also UF being integrated in Fourier moment step',
                rank_nuance='P2 and rank are V-measurable; outer average unfiltered. At B stage UF and rank have not been conditioned on.',
                no_cross_row_independence_claim=True),
            computation=dict(script=pin(EV/'compute_joint_certificates.py'),certificate=pin(EV/'JOINT_SCALAR_CERTIFICATES.json'),
                exact_probability_laws='Full25point chi mass and49point difference law from625weighted pairs',
                base_environment='Rechecked exact rational Chernoff envelopes; bad mass <=2^-25',
                coefficient_integration='True weighted-sum law psi(s)^w*product psi(s*r_i); no Gaussian/coefficient-size truncation',
                frequency_groups=[[1,1],[2,3],[4,7],[8,15],[16,63],[64,16384]],
                negative_frequencies='Paired; Nyquist conservatively counted twice',
                difference_subset_handling='Unused difference masses kept with unit CF bound, no discarded probability',
                arithmetic='Exact Fraction/integer. exp(-x) bounded by reciprocal positive Taylor0..24, then64bit upward ceiling; power640 then80bit upward ceiling.',
                aggregate_dyadic_rounding_slack=cert['explicit_dyadic_rounding_slack'],
                aggregate_slack_scope='Already contained in computed Z, not added twice; below2^-49',
                pi_bounds=['157/50','22/7'],
                displays='Float printouts are explanatory, never comparison criteria',
                new_unconditional_bound_does_not_use_old_single_coordinate_numeric_interval=True),
            result=dict(row_interval=['0.0000152532','0.000030345'],
                full_message_correct_upper='0.000030345',full_message_error_lower='0.999969655',
                initial_correct_condition_same_outward_bounds=True,old_full_upper='0.2500946',
                strict_improvement_exactly_verified=True,exact_row_or_full_probability_computed=False),
            scopes=dict(message='Every fixed legal128bit message; row fixed before coins',
                probability='Average uniform Setup and all honest old/new key,Enc,TG,Upd coins',
                conditional_iid='Given V only; not extended to given V and initial-correct I',
                actual_author_software='Still requires exact code/config, A/noise seed law and arithmetic mapping',
                deeper_updates_or_other_parameters='Not analyzed this round'),
            review_priority=['J1 column-packet conditioning','J3 true a/b conditional law and unfiltered outer average','J4-J5 absolute-Fourier to eighth moment and exact rounding chain'],
            priority_claim='Mature Fourier/Cauchy-Schwarz/chord/Jensen tools; no generic method or global application priority claimed',
            action_counts=actions)
writej(ROOT/'SOURCE_AND_COMPUTATION_RECORD.json',record)

verdict=dict(schema='fi640-joint/verdict/1',date_asia_shanghai='2026-11-10',
             status='NEW_STRICT_JOINT_BOUND_PROVED_IN_STATED_MODEL',
             status_chinese='同行8坐标条件独立结构与新联合概率上界成立；严格加强完整消息旧上界',
             identity=identity,new_independent_review_pending=True,
             fixed_model=record['model'],
             conditional_structure=dict(V=record['conditioning']['V'],residuals_iid_given_V=True,
                formula='p_row=E[p(V)^8]',characteristic_candidate_verified=True,
                a_b_iid_given_base_B=True,token_generated_once=True,
                rank_handling=record['conditioning']['rank_nuance']),
             row=dict(correct_lower=cert['unconditional_row_lower_Jensen'],
                correct_upper=cert['unconditional_row_upper'],
                outward_interval=['0.0000152532','0.000030345'],
                uniform_independent_reference='4^-8=1/65536',
                upper_less_than_twice_uniform_reference=True,exact_probability_computed=False),
             full_message=dict(correct_upper=cert['unconditional_row_upper'],
                outward_correct_upper='0.000030345',error_lower='0.999969655',error_percent_lower='99.9969655%',
                inherited_nonemptiness_correct_lower='(1161/8192)^15360',
                relation='All64coordinates correct implies first8coordinate row correct',
                row_bound_not_raised_to_eighth_power=True,exact_probability_computed=False),
             conditional_initial_correct=dict(initial_correct_lower='1-2^-132',
                row_upper=cert['initial_correct_conditioned_upper'],
                row_lower=cert['initial_correct_conditioned_lower'],
                same_displayed_row_interval=True,same_displayed_full_message_upper=True,
                method='First unconditional joint analysis, then event/Frechet ratios',
                conditional_independence_after_I_assumed=False),
             certificate_chain=dict(base_bad_upper='2^-25',Z=cert['Z'],
                chord_slope='21845/16384',good_base_row_upper=cert['good_environment_row_upper'],
                full_formula='U=(1-delta_B)*(4^-8+C8*Z)+delta_B',
                all_nonzero_frequencies_enclosed=True,unaccounted_probability_or_truncation_loss=0,
                arithmetic='Exact rational/integers with directed dyadic upper envelopes'),
             improvement=dict(old_full_correct_upper='0.2500946',new_full_correct_upper='0.000030345',
                same_model_and_parameters=True,strict_exact_comparison=True),
             unreviewed_dependencies=[dict(claim=x['id'],status='PAPER_PROOF_SUPPLIED_INFORMED_INDEPENDENT_REVIEW_PENDING') for x in record['proof_chain']],
             core_mathematical_gap_currently_registered=False,
             remaining_precision_obstructions=['Chord uses full p in[0,1], retaining conservative rare-large-p contribution',
                'Cauchy-Schwarz and discarded CF factors plus uniform decode-coefficient norm are upper-bound slack',
                'Shared keys/G across ciphertext rows require a new joint argument for all64coordinates'],
             next_decision_changing_math='Control true64coordinate event with shared keys and TG; no row-product assumption',
             external_implementation_mapping_pending=True,
             action_counts=actions,
             deliverables=['CONDITIONAL_STRUCTURE.md','JOINT_PROBABILITY_BOUND.md','SOURCE_AND_COMPUTATION_RECORD.json','VERDICT.json'])
writej(ROOT/'VERDICT.json',verdict)

qa=dict(input_records_unchanged=30,source_copy_hashes_match=True,scalar_certificates_passed=True,
        json_errors=[],broken_links=[],forbidden_style=[])
for name in ['CONDITIONAL_STRUCTURE.md','JOINT_PROBABILITY_BOUND.md']:
    txt=(ROOT/name).read_text(encoding='utf-8')
    if re.search('不是.{0,80}而是',txt):qa['forbidden_style'].append(name)
    clean=re.sub(r'`[^`]*`','',txt);clean=re.sub(r'\\\[.*?\\\]','',clean,flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)',clean):
        if not target.startswith(('http:','https:')) and not (ROOT/target).resolve().exists():qa['broken_links'].append(dict(file=name,target=target))
for p in list(ROOT.glob('*.json'))+list(EV.glob('*.json'))+list(SRC.glob('*.json')):
    if p.name=='DELIVERY_MANIFEST.json':continue
    try:readj(p)
    except Exception as e:qa['json_errors'].append(dict(path=str(p),error=str(e)))
assert not qa['json_errors'] and not qa['broken_links'] and not qa['forbidden_style']
for x in lock['records']:assert pin(x['path'])['sha256']==x['sha256']
writej(EV/'DOCUMENT_QA.json',qa)
files=[pin(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='DELIVERY_MANIFEST.json']
manifest=dict(schema='fi640-joint/delivery-manifest/1',date_asia_shanghai='2026-11-10',
              status='COMPLETE_WITH_EXPLICIT_INFORMED_REVIEW_SCOPE',
              deliverables=verdict['deliverables'],files_exclude_this_manifest=True,files=files,qa=qa)
writej(EV/'DELIVERY_MANIFEST.json',manifest)
print(json.dumps(qa,ensure_ascii=False))
print('Four joint-correctness deliverables sealed.')
