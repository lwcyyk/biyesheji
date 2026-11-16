"""Source and document sealing for the scalar correctness audit; no crypto code."""
from pathlib import Path
import hashlib
import json
import re
import sys
from fractions import Fraction as F

sys.stdout.reconfigure(encoding="utf-8")
BASE=Path(r"D:\毕业设计")
ROOT=BASE/"crypto_fi_640_correctness_audit"
SRC=ROOT/"sources"
EV=ROOT/"evidence"
OLD=BASE/"crypto_fi_research_manuscript_v1"


def readj(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def writej(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def pin(p):
    p=Path(p)
    return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def rational(v):return F(int(v['numerator']),int(v['denominator']))


lock=readj(EV/'INPUT_LOCK.json')
assert lock['payload_matches'] and lock['all_files_match']
for x in lock['files']:assert pin(x['path'])['sha256']==x['sha256']
assert pin(lock['manifest']['path'])['sha256']==lock['manifest']['sha256']
cert=readj(EV/'SCALAR_CERTIFICATES.json')
assert cert['mass_denominator']==65536 and cert['parity_mass_numerators']==[32768,32768]
assert cert['environment']['budget_verified'] and cert['single_coordinate']['outward_rounding_checked']
assert rational(cert['single_coordinate']['exact_upper'])<=F(2500946,10**7)
assert F(2499054,10**7)<=rational(cert['single_coordinate']['exact_lower'])
assert rational(cert['tie_boundary_mass_upper'])<=F(613,10**7)
assert cert['initial_encryption']['single_failure']['exponent']==138
assert cert['initial_encryption']['full_failure_upper']=='2^-132'

identity=dict(status='INFORMED_PROBABILITY_AND_FINITE_PARAMETER_AUDIT',
              prior_derivations_and_reviews_visible=True,new_independent_reviews=0,
              human_reviews=0,new_subagents=0,formal_proof_assistant=False,
              exact_runtime_model_id=None)
actions=dict(protection_mechanism_implementations=0,LWE_solvers=0,
             cryptographic_attack_prototypes=0,matrices_keys_tokens_ciphertexts_sampled=0,
             large_cryptographic_experiments=0,project_test_reruns=0,
             native_AS_RP_requests=0,author_contacts=0,messages_or_emails=0,
             network_retrievals=0,private_material_decryptions=0,
             deterministic_scalar_script_executions=4,
             scope='Exact finite scalar PGFs, moments, rational envelopes, large integer comparisons and PDF/hash processing only')
sources=[]
for name,scope in [
    ('FI_journal_20261110.pdf','Current original images PDF12 Enc/Decode,14 TG/Upd,15 residual/Theorem6.3; source data copied from manuscript frozen journal/v4'),
    ('official_frodo_2021.pdf','Current original images PDF10 nearest-tie rule,15 Encode/Decode,16 Sample/SampleMatrix,25 exact chi640 and parameters'),
    ('articlev08.tex','Current text locators493/496,553-560,580-590,633-653,669-699; used for type/sampling/formula anchors'),
    ('PARAMETER_CERTIFICATES.json','Byte identity/copy and historical source context; current moments and probabilities use official chi640 table directly')]:
    sources.append(dict(pin(SRC/name),reading_scope=scope,
                        original_file=pin(OLD/'sources'/name)))

record=dict(schema='fi640-correctness/source-and-computation/1',date_asia_shanghai='2026-11-10',
            identity=identity,skills=['academic-research-suite: scoped theoretical/source audit','pdf: read-only structural and original-image inspection'],
            task='Official640 one honest update correctness under ideal independent chi640',
            primary_input_files=[pin(OLD/n) for n in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVIEW_RESPONSE_AND_READINESS.md','MANIFEST.json']],
            input_manifest_byte_sha256=lock['manifest_byte_sha256'],
            input_manifest_canonical_payload_verified=True,declared_manifest_file_records_verified=len(lock['files']),
            historical_inputs_modified=False,
            semantic_scope=dict(manuscript='Full file obtained, known from prior authoring; current focus sections2,6,7 and scope/correctness statements',
                claim_matrix='JSON parsed; source registry and C08,C10,C25 inspected',
                review_response='Repair/readiness and model/source boundaries read; no new review status inherited for current probability proof',
                manifest='Canonical payload and all26 file byte records verified'),
            primary_sources=sources,
            source_version=dict(doi='10.46298/fi.14425',arxiv='2410.03948v4',
                PDF_sha256=pin(SRC/'FI_journal_20261110.pdf')['sha256'],
                current_round_new_download=False,source_download_date='2026-11-10 prior manuscript task',
                original_source_URL='https://fi.episciences.org/17222/pdf',
                target='Printed formulas with inherited explicit Ord_n bit-plane type normalization'),
            preflights=[readj(EV/'FI_journal_20261110_preflight.json'),readj(EV/'official_frodo_2021_preflight.json')],
            sampling_contract=dict(n=640,D=15,q=32768,mbar=8,nbar=8,B=2,
                message_bits=128,chi='Exact finite signed chi640',
                coordinate_and_call_independence=True,A='Uniform Zq^(640x640), common old/new',
                token='One honest unfiltered TG; singular and invertible P2 both integrated',
                no_sampling_failures='Exact16bit finite-table sampling; no reject/truncate branch'),
            proof_dependencies=dict(residual='MODEL_AND_RESIDUAL sections2-5, FI PDF12/14/15',
                conditional_sigma_field='All old-side latent data, A, underlying new S/E and R fixed; all raw TG matrices left independent',
                characteristic_identity='exp(2pi*i*t*eta0/q)*G(t)^w*product_i G(t*r_i)',
                H_distribution='Uniform A plus an odd parent U0 component -> uniform parent first row ->9600 fair bits',
                modular_decoding='Finite group Fourier on all32768 residues, D={-4096,...,4095}; no integer no-wrap approximation',
                full_message='Intersection implies selected coordinate; rare event U0=F0=R=0 supplies lower; no coordinate product rule'),
            computation=dict(script=pin(EV/'compute_scalar_certificates.py'),result=pin(EV/'SCALAR_CERTIFICATES.json'),
                arithmetic='Python exact arbitrary-precision integer and Fraction. All decisive comparisons rational/integer; no floating-point acceptance test',
                pi_interval=['157/50','22/7'],
                exponential='Positive Taylor sum0..24 proves exp(C)>5300; e>2 covers remaining ranges',
                conditional_Fourier_ranges=[[1,7],[8,85],[86,1024],[1025,16384]],
                no_unbounded_frequency_tail=True,
                bad_event_budget='2^-22 including all charged environment events',
                initial_PGF='Full25point chi and625 product terms; exact tilt21/20;64-coordinate union',
                decimal_rounding='Outward endpoints compared exactly as rational integers over10^7',
                numerical_output_precision='Exact fractions retained; displayed floats/timing are diagnostic only',
                scalar_binary_certificate_semantics='Largest exponent comparison refers to rational Chernoff envelope, not a lower bound on actual failure probability',
                preliminary_rejected_candidate='Initial w4000/environment budget2^-24 was not certified by integer comparison; no certificate adopted. Final w4500, budget2^-22, Fourier constants fully rechecked.',
                matrix_simulations=0,Monte_Carlo_trials=0,Gaussian_approximations_used_for_certification=False),
            quantifiers=dict(message='Every fixed128bit message; correctness event under shared random coins is message-independent with half-up rule',
                probability='Average uniform Setup and honest keys/Enc/TG/Upd randomness',
                conditional='Every latent environment satisfying good event, averaging only remaining raw TG coins',
                initial_correct_condition='Additional Frechet bounds certified; same outward endpoints still valid when initial full message was correct',
                not_claimed=['Same rate for each fixed A/key/token','Independent64 message coordinates','Actual author program or public-seed law mapping']),
            independent_review_status='Current new conditional-Fourier/correctness proof pending independent review; prior reviews did not cover it',
            priority_scope='Mature characteristic-function/Fourier/Chernoff tools. Existing target/version/source-hiding priority evidence retained; no new global priority search for this correctness result.',
            manuscript_impact=dict(C25='Official640 one-update ideal configuration now certified high-error; full joint probability remains bounded broadly',
                C08_C09='CF-1 common-correct security result unchanged',C10='Affine-support probability certificate unchanged',
                source_game='Algebraic provenance distinguisher remains legal; disclose unreliable640 configuration',
                actual_implementation='Code/config, Ord, A seed, noise joint law and arithmetic/rounding mapping pending'),
            action_counts=actions)
writej(ROOT/'SOURCE_AND_COMPUTATION_RECORD.json',record)

verdict=dict(schema='fi640-correctness/verdict/1',date_asia_shanghai='2026-11-10',
             overall='CERTIFIED_HIGH_ONE_UPDATE_DECRYPTION_ERROR_IN_IDEAL_PRINTED_640',
             overall_chinese='官方640参数与理想独立采样下，FI打印算法一次诚实更新的高解密错误率已认证',
             identity=identity,proof_status='INFORMED_PAPER_PROOF_AND_EXACT_SCALAR_CERTIFICATES',
             independent_review_pending=True,
             model=dict(n=640,D=15,q=32768,mbar=8,nbar=8,B=2,chi='exact chi640',
                        A='uniform Setup',Ord='n-column bit-plane normalization',
                        tokens='honest TG, unfiltered, all P2 ranks',rounding='nearest ties upwards'),
             initial=dict(single_coordinate_correct_lower='1-2^-138',full128bit_correct_lower='1-2^-132',
                          A_scope='every fixed A; average honest old key and Enc coins',
                          method='Exact finite-product PGF Chernoff, no Gaussian approximation'),
             one_update_single_coordinate=dict(correct_lower=cert['single_coordinate']['exact_lower'],
                correct_upper=cert['single_coordinate']['exact_upper'],outward_decimal_interval=['0.2499054','0.2500946'],
                exact_error_budget='1/10600+2^-46+2^-22',
                scope='Any coordinate fixed before sampling and fixed message; average all honest experiment randomness'),
             one_update_full_message=dict(correct_lower='(1161/8192)^15360 > 2^-46080',
                correct_upper=cert['single_coordinate']['exact_upper'],outward_correct_upper='0.2500946',
                error_probability_lower='0.7499054',
                exact_joint_probability_computed=False,
                interpretation='Upper bound sufficient to reject high-reliability one-update correctness; not a full-message point estimate near1/4',
                independence_of_coordinates_assumed=False),
             condition_initial_full_correct=dict(same_outward_coordinate_interval=True,same_outward_full_upper=True,
                proof='(L-a)/(1-a),U/(1-a), a=2^-132; exact endpoint comparisons; no independence assumed'),
             key_derivation='Conditional exact characteristic function plus good-environment small/high-frequency envelopes controls modular decoded mass',
             ledger=dict(environment_failure_upper='2^-22',conditional_decoding_error_from_uniform_upper='1/10600+2^-46',
                all_Fourier_frequencies_accounted=True,unaccounted_sampling_or_truncation_loss=0,
                characteristic_conditioning_excludes_token_rank=True),
             tie_scope=dict(canonical='Official half-up rule supported by source',
                boundary_mass_upper='0.00006130',any_other_nearest_tie_rule_coordinate_enclosure=['0.2498441','0.2501559']),
             theorem_scope=dict(FI_Theorem6_3='Its sufficient noise premise is not met by this finite configuration; this is not a counterexample with that premise satisfied',
                finite_configuration='Now actual high-error probability certified, stronger than mere failure of sufficient worst-case bound',
                Theorem6_9='Separate conditional security-premise audit unchanged',
                CF1='Unchanged common-correct family',
                actual_author_software='Not measured or identified as equivalent by this audit'),
             minimal_remaining_questions=['Independent rederivation of current conditional Fourier and exact scalar certificate chain',
                'Tighter64-coordinate joint correctness bounds under shared H/token/key randomness',
                'Author exact code/config and publicA/noise seed/arithmetic mapping'],
             application_priority='Specific-object correctness result; global novelty not established in this round',
             action_counts=actions,
             deliverables=['MODEL_AND_RESIDUAL.md','CERTIFIED_CORRECTNESS_BOUNDS.md','SOURCE_AND_COMPUTATION_RECORD.json','VERDICT.json'])
writej(ROOT/'VERDICT.json',verdict)

qa=dict(input_manifest_and_26_records_unchanged=True,json_errors=[],broken_local_links=[],forbidden_style=[],
        source_PDF_preflights_PASS=True,scalar_certificates_passed=True)
for name in ['MODEL_AND_RESIDUAL.md','CERTIFIED_CORRECTNESS_BOUNDS.md']:
    txt=(ROOT/name).read_text(encoding='utf-8')
    if re.search('不是.{0,80}而是',txt):qa['forbidden_style'].append(name)
    cleaned=re.sub(r'`[^`]*`','',txt);cleaned=re.sub(r'\\\[.*?\\\]','',cleaned,flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)',cleaned):
        if not target.startswith(('http:','https:')) and not (ROOT/target).resolve().exists():qa['broken_local_links'].append(dict(file=name,target=target))
for p in list(ROOT.glob('*.json'))+list(SRC.glob('*.json'))+list(EV.glob('*.json')):
    if p.name=='DELIVERY_MANIFEST.json':continue
    try:readj(p)
    except Exception as e:qa['json_errors'].append(dict(path=str(p),error=str(e)))
assert not qa['json_errors'] and not qa['broken_local_links'] and not qa['forbidden_style']
for x in lock['files']:assert pin(x['path'])['sha256']==x['sha256']
assert pin(lock['manifest']['path'])['sha256']==lock['manifest']['sha256']
writej(EV/'DOCUMENT_QA.json',qa)
files=[pin(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='DELIVERY_MANIFEST.json']
manifest=dict(schema='fi640-correctness/delivery-manifest/1',date_asia_shanghai='2026-11-10',
              status='COMPLETE_WITH_DECLARED_MODEL_AND_INFORMED_REVIEW_STATUS',
              deliverables=verdict['deliverables'],files_exclude_this_manifest=True,files=files,qa=qa)
writej(EV/'DELIVERY_MANIFEST.json',manifest)
print(json.dumps(qa,ensure_ascii=False))
print('Four deliverables, source/computation record and scalar certificates sealed.')
