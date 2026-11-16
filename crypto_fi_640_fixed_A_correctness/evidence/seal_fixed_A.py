"""Integrity, source-scope, and deterministic certificate QA; no crypto execution."""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
    b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def frac(x):return F(int(x['numerator']),int(x['denominator']))

inputs=set()
for name in ['crypto_fi_research_manuscript_v2_1','crypto_fi_640_correctness_audit','crypto_fi_640_joint_correctness']:
    inputs.update(p for p in (BASE/name).rglob('*') if p.is_file())
inputs.add(BASE/'crypto_fi_author_implementation_audit/IMPLEMENTATION_MODEL_MAPPING.md')
for folder in [BASE/'crypto_fi_640_probability_review',BASE/'crypto_fi_640_probability_review/review_01a1c4ed']:
    for name in ['MATHEMATICAL_REVIEW.md','CORRECTIONS_AND_MANUSCRIPT_IMPACT.md','REVIEW_VERDICT.json','INPUT_AND_REVIEW_PROVENANCE.json']:
        inputs.add(folder/name)
records=[rec(p) for p in sorted(inputs)]
lockpath=ROOT/'evidence/INPUT_LOCK.json'
if lockpath.exists():
    old=read(lockpath)
    assert old['files']==records,'Historical input changed after local lock'
else:
    save(lockpath,dict(schema='fi640-fixed-A/input-lock/1',date_asia_shanghai='2026-11-10',
        snapshot_scope='Historical directories and supplemental review/source records; file integrity, not a full-read attestation',
        snapshot_phase='After initial reads and before final delivery validation; no historical writes performed',
        files=records))

# Verify every reachable path/sha256 tuple in the frozen manifests.
referenced=[]
def visit(x):
    if isinstance(x,dict):
        if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str):
            p=Path(x['path'])
            if p.is_file():
                rr=rec(p)
                assert rr['sha256']==x['sha256'],str(p)
                if 'bytes' in x:assert rr['bytes']==x['bytes'],str(p)
                referenced.append(str(p))
        for v in x.values():visit(v)
    elif isinstance(x,list):
        for v in x:visit(v)
for p in [BASE/'crypto_fi_research_manuscript_v2_1/MANIFEST.json',
          BASE/'crypto_fi_640_correctness_audit/evidence/DELIVERY_MANIFEST.json',
          BASE/'crypto_fi_640_joint_correctness/evidence/DELIVERY_MANIFEST.json']:
    visit(read(p))

sources=[]
for p,scope,expected in [
    (BASE/'crypto_fi_640_joint_correctness/sources/FI_journal_20261110.pdf',
     'Hash-matched primary images PDF12 and14 visually inspected this round; Setup/KG/Enc/Dec/TG/Upd',
     'bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4'),
    (BASE/'crypto_fi_640_joint_correctness/sources/articlev08.tex',
     'Printed TG/Upd lines633-652 and residual/correctness surrounding lines680-700; additional algorithm locators searched',
     '16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b'),
    (BASE/'crypto_fi_640_joint_correctness/sources/official_frodo_2021.pdf',
     'Hash-matched original images PDF10 ties upward and PDF25 Tables3/4 visually inspected this round; text counterparts checked',
     '5c3440b311c7ee4fba8b9a12e0ff567eb75c29fef66843f3eecc16f137164f7d')]:
    rr=rec(p);assert rr['sha256']==expected
    sources.append(dict(file=rr,read_scope=scope))

c=read(ROOT/'FINITE_CERTIFICATES.json')
old_single=read(BASE/'crypto_fi_640_correctness_audit/evidence/SCALAR_CERTIFICATES.json')
old_joint=read(BASE/'crypto_fi_640_joint_correctness/evidence/JOINT_SCALAR_CERTIFICATES.json')
assert c['chi']['mass_zero_and_each_sign']==old_single['masses_zero_and_each_signed_point']==old_joint['masses_zero_and_each_sign']
assert c['nu']['mass']==old_joint['difference_mass']
assert frac(c['chi']['max_atom'])==F(1161,8192)
assert c['environment']['H']['certificate']['exponent']==73
assert c['environment']['R2']['certificate']['exponent']==27
assert frac(c['environment']['adopted_delta'])==F(1,2**26)
Z=frac(c['Z']);delta=frac(c['environment']['adopted_delta'])
U=frac(c['row_and_full_correct_upper']);L=frac(c['row_lower_Jensen'])
assert U==(1-delta)*(F(1,4**8)+F(21845,16384)*Z)+delta
assert L==((1-delta)*(F(1,4)-Z))**8
assert frac(c['initial_correct_conditioned_row_and_full_upper'])==U/(1-F(1,2**132))
assert U<=F('0.005043360') and frac(c['initial_correct_conditioned_row_and_full_upper'])<=F('0.005043360')
assert F('0.0000135117')<=frac(c['initial_correct_conditioned_row_lower'])
assert F('0.005043360')<F(1,4)
assert F(c['full_error_outward_lower'])==1-F(c['row_and_full_outward_upper'])
assert c['initial']['coordinate_tail_certificate']['exponent']>=138
assert c['uncharged_truncation_loss']==0 and c['cryptographic_samples_generated']==0

# Preserve the actual inherited review identity and scope.
reviews=[]
for folder in [BASE/'crypto_fi_640_probability_review',BASE/'crypto_fi_640_probability_review/review_01a1c4ed']:
    p=folder/'REVIEW_VERDICT.json';j=read(p)
    reviews.append(dict(file=rec(p),status=j.get('core_status',j.get('overall')),
        identity=j['identity'],scope='Uniform-Setup residual, single-coordinate, J1-J6 and initial PGF; not this new fixed-A extension'))

m=read(BASE/'crypto_fi_research_manuscript_v2_1/CLAIM_EVIDENCE_MATRIX.json')
selected_claims=[x for x in m['claims'] if x.get('id') in ['C01','C02','C25a','C25b','C25c','C25d','C25p','C25r']]
save(ROOT/'evidence/READING_AND_SCOPE_RECORD.json',dict(
    schema='fi640-fixed-A/reading-scope/1',date_asia_shanghai='2026-11-10',
    primary_sources=sources,pdf_structural_preflight='Inherited PASS sidecars for identical PDF byte hashes',
    current_visual_pages=['FI PDF12','FI PDF14','official2021 PDF10','official2021 PDF25'],
    manuscript_scope='v2.1 abstract/model,640 proposition,AppendixD and review/source registry; selected C01/C02/C25 claims and frozen model metadata',
    manuscript_selected_claims=selected_claims,manuscript_model=m['frozen_models'],
    inherited_reviews=reviews,
    current_review_status='Informed paper derivation and deterministic finite certificates; new independent review pending',
    mapping_scope='Entire IMPLEMENTATION_MODEL_MAPPING.md read, especially sections3-7; WAITING_FOR_AUTHOR_ARTIFACT retained',
    inherited_files_integrity_count=len(records),
    verified_referenced_manifest_records=len(referenced),
    full_read_of_all_hashed_files_claimed=False,
    new_network_requests=0,new_global_priority_search=False))

verdict=dict(schema='fi640-fixed-A/verdict/1',date_asia_shanghai='2026-11-10',
    status='UNIFORM_SETUP_PREMISE_REMOVED_UNDER_EXPLICIT_IID_CHI_CONTRACT',
    identity=dict(status='INFORMED_FIXED_A_PROBABILITY_DERIVATION_AND_DETERMINISTIC_FINITE_CERTIFICATES',
        previous_author_proofs_and_reviews_visible=True,exact_runtime_model_id=None,
        new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,
        new_blind_reviews=0,new_subagents=0,formal_proof_assistant_used=False),
    mathematical_gap_currently_registered=False,new_independent_review_pending=True,
    frozen_model=dict(n=640,D=15,q=32768,mbar=8,nbar=8,B=2,
        A='Every matrix fixed before all relevant raw chi draws; common to old and new',
        chi='Exact official chi640; every coordinate and call independent after fixing A',
        token='One honest unfiltered TG; all P2 ranks',Ord='n-column bit-plane normalization',
        decode='Nearest integer ties upward',message='Every legal128bit message fixed before coins'),
    result=dict(row_outward_interval=[c['row_outward_lower'],c['row_and_full_outward_upper']],
        full_message_correct_upper=c['row_and_full_outward_upper'],
        full_message_error_lower=c['full_error_outward_lower'],
        full_message_error_percent_lower=c['full_error_percent_outward_lower'],
        exact_row_and_full_correct_upper=c['row_and_full_correct_upper'],
        initial_full_correct_lower='1-2^-132 for every fixed A',
        condition_initial_full_correct_same_decimal_endpoints=True,
        full_message_exact_probability_computed=False,
        full_message_nonempty_correct_lower='(1161/8192)^15360',
        no_cross_row_independence_assumption=True),
    proof_chain=[
        dict(id='FA1',claim='Given A,u, parent coordinates are independent chi translates; w>=L',status='Paper proof supplied'),
        dict(id='FA2',claim='H-tail<=2^-73 and R2-tail<=2^-27 uniformly in A',status='Paper proof plus exact finite comparison'),
        dict(id='FA3',claim='Conditional column iid and true1280coefficient law survive fixed A',status='Paper proof supplied; structure inherited'),
        dict(id='FA4',claim='All nonzero Fourier modes bounded using h0=450,R2>=3500 and new high rho',status='Paper proof plus exact finite comparison'),
        dict(id='FA5',claim='Absolute Fourier moment,chord,bad environment yield U; event inclusion and Frechet conditioning',status='Paper proof plus exact finite comparison')],
    probability_accounting=dict(H_bad='<=2^-73',R2_bad='<=2^-27',adopted_bad='2^-26',
        Z=c['Z'],high_frequency_rho=c['frequency_groups'][-1]['rho'],
        all_positive_frequency_representatives=16384,unused_nu_mass='Retained with unit bound',
        uncharged_truncation_loss=0,dyadic_slack_already_charged_bound='2^-41'),
    public_seed_migration=dict(
        conclusion='Any prior A law can be averaged; no uniformity/PRG/entropy premise for public A in this reliability bound',
        required='Given each public seed, later raw chi coins satisfy this exact product law; same A,printed algorithm,Ord and decode',
        secret_seed_noise_expansion='Requires independent evidence or quantitative migration',
        author_artifact_status='WAITING_FOR_AUTHOR_ARTIFACT'),
    comparison=dict(old_uniform_Setup_full_correct_upper='0.000030345',
        new_every_fixed_A_full_correct_upper='0.005043360',
        nature='Wider A quantifier; old bound remains numerically stronger on uniform Setup'),
    contribution='Specific scheme reliability range extension and public-A model migration; mature probability/Fourier tools',
    theorem63_impact='Official640 printed sufficient premise still fails; result concerns actual probability outside that premise',
    inherited_review_scope=reviews,
    minimal_author_artifact_facts=[
        'Same pre-fixed A across generations and all randomness inputs/seed domains yielding the needed conditional joint law',
        'TG/Upd/Ord/Tensor formulas and rank/rejection/retry/failure semantics',
        'Ring arithmetic,representatives,packing,and exact Decode correspondence'],
    priority_review_inputs=['FA1-FA2 fixed-A conditioning and Chernoff','FA4 global high-frequency envelope and directed rounding','FA5 eighth-moment and event conditioning'],
    next_precision_question='Stronger uniform translated-bitweight PGF or true cross-row joint event; not required for established c<1/4',
    action_counts=dict(cryptographic_protection_implementations=0,attack_prototypes=0,LWE_solvers=0,
        matrices_keys_tokens_ciphertexts_sampled=0,Monte_Carlo_runs=0,network_requests=0,
        author_contacts=0,emails_or_messages=0,subagents=0,deterministic_scalar_script_runs=2),
    inputs=dict(lock=rec(lockpath),historical_file_count=len(records),historical_writes=0,
        referenced_manifest_hash_records_verified=len(referenced)),
    certificate=rec(ROOT/'FINITE_CERTIFICATES.json'),
    required_deliverables=['FIXED_A_MODEL_AND_TARGET.md','PROOF_OR_OBSTRUCTION.md','FINITE_CERTIFICATES.json','VERDICT.json'])
save(ROOT/'VERDICT.json',verdict)

# Reserve the self-excluding manifest link before the link pass; replace with
# the completed final hash list below in this same successful execution.
manifest=ROOT/'evidence/DELIVERY_MANIFEST.json'
if not manifest.exists():
    save(manifest,dict(schema='fi640-fixed-A/delivery-manifest/1',status='SEALING'))

# Parse all delivered JSON, resolve all local links, and audit task-specific style.
errors=[];broken=[];style=[]
for p in ROOT.rglob('*.json'):
    try:read(p)
    except Exception as e:errors.append(dict(path=str(p),error=str(e)))
for p in ROOT.glob('*.md'):
    text=p.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('http:','https:','#')):continue
        target=target.strip('<>').split('#')[0]
        dest=Path(target) if re.match(r'^[A-Za-z]:',target) else p.parent/target
        if not dest.exists():broken.append(dict(file=str(p),target=target))
    if re.search('不是[^\n]{0,120}而是',text):style.append(str(p))
assert not errors and not broken and not style,(errors,broken,style)
assert [rec(p) for p in sorted(inputs)]==records
qa=dict(schema='fi640-fixed-A/document-qa/1',all_json_parsed=True,broken_links=broken,
    forbidden_style=style,historical_inputs_unchanged=len(records),
    referenced_manifest_records_verified=len(referenced),
    exact_scalar_relations_and_endpoint_checks_passed=True,
    actual_sampling_and_implementation_count=0,
    new_fixed_A_proof_has_independent_review=False)
save(ROOT/'evidence/DOCUMENT_QA.json',qa)
files=[rec(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest]
save(manifest,dict(schema='fi640-fixed-A/delivery-manifest/1',date_asia_shanghai='2026-11-10',
    status='COMPLETE_INFORMED_FIXED_A_PROOF_AND_CERTIFICATES',
    required_deliverables=verdict['required_deliverables'],excludes_self=True,files=files,qa=qa))
print('Historical inputs verified unchanged:',len(records))
print('Referenced frozen-manifest hash records verified:',len(referenced))
print('New delivery files sealed:',len(files))
print('Exact scalar relationships,decimal endpoints,JSON,links,and style: PASS')
