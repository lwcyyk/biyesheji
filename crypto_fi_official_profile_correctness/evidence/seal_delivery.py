"""Final deterministic replay, document checks and delivery manifest; no historical writes."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, re, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
sys.set_int_max_str_digits(100000)
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'evidence'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(v): return F(int(v['numerator']),int(v['denominator']))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
executions=[]
for filename in ('compute_profile_certificates.py','verify_profile_certificates.py'):
 path=E/filename
 result=subprocess.run([sys.executable,'-X','utf8',str(path)],capture_output=True)
 log=result.stdout.decode('utf-8')+result.stderr.decode('utf-8')
 (E/(path.stem+'_FINAL.log')).write_text(log,encoding='utf-8')
 executions.append(dict(script=str(path),sha256=sha(path),returncode=result.returncode,
      stdout_stderr_file=path.stem+'_FINAL.log'))
 print(log,end='')
 assert result.returncode==0
write(E/'EXECUTION_RECORD.json',dict(date_asia_shanghai='2026-11-11',
 identity='Same informed AI context; scalar computation and certificate checking',
 final_replays=executions,
 earlier_observed_formatting_attempts=dict(failed_count=2,
   reason='Python4300-digit integer-to-string limit; first on tiny positive lower bound, second on biased parity probability',
   resolution='Kept astronomically small event bounds in factored form; raised integer string limit for exact parity fraction',
   probability_model_changed=False),
 random_samples=0,independent_review_claim=False))

cert=json.loads((ROOT/'OFFICIAL_PROFILE_CERTIFICATES.json').read_text(encoding='utf-8'))
checked=json.loads((E/'CERTIFICATE_CHECK.json').read_text(encoding='utf-8'))
assert checked['status']=='PASS' and checked['check_count']==3194
snap=json.loads((E/'INPUT_SNAPSHOT.json').read_text(encoding='utf-8'))
additional=[]
for rel in ('crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md',
            'crypto_fi_author_implementation_audit/VERDICT.json'):
 p=ROOT.parent/rel
 additional.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,read_level='Targeted primary status/precedent sections'))
write(E/'READING_AND_SCOPE_RECORD.json',dict(
 date_asia_shanghai='2026-11-11',identity=cert['identity'],
 declared_model_family='Codex based on GPT-6, per developer context',exact_backend_model_id=None,exact_weights_version=None,
 author_proofs_visible=True,prior_positive_reviews_visible=True,blind=False,
 new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_subagents=0,new_proof_assistant_checks=0,
 historical_direct_snapshot_count=len(snap),
 semantic_reading='Targeted v2.2 correctness/source/scope/erratum sections; fixed-A model and proof; review verdict and mathematical review; v2.1 erratum and distribution audit; original FI TeX algorithms and theorem',
 fingerprinting_is_distinct_from_semantic_reading=True,additional_historical_sources=additional,
 visual_source_pages=['official_2021_p15','official_2021_p16','official_2021_p25','official_2023_p15','official_2023_p16','FI_p12','FI_p14'],
 other_source_pages_text_read=['official_2021_p10','official_2023_p8','FI_p15'],
 PDF_structural_preflights='PASS:2021=59 pages;2023=21 pages;FI=23 pages',
 public_web_queries=6,public_web_open_requests=2,official_GitHub_comment_reads=1,
 author_contacts=0,cryptographic_samples=0,candidate_mechanism_implementations=0,
 artifact_generation='Four requested files plus finite scripts, source extracts, receipts and verification evidence; all inside new directory',
 history_write_count=0,calibration='NOT_CALIBRATED'))

profiles={}
for key,p in cert['profiles'].items():
 fixed=p['fixed_A']; uniform=p['uniform_Setup']
 assert fixed['verdict']==uniform['verdict']=='CERTIFIED_HIGH_ERROR'
 profiles[key]=dict(verdict='CERTIFIED_HIGH_ERROR',parameters=p['parameters'],
   initial_full_failure_upper=p['initial']['full_failure_upper'],
   initial_full_failure_power_of_two=p['initial']['full_failure_power_of_two'],
   every_fixed_A=dict(scalar_outward_interval=[fixed['display']['scalar_lower'],fixed['display']['scalar_upper']],
     row_outward_interval=[fixed['display']['row_lower'],fixed['display']['row_full_upper']],
     full_correct_outward_upper=fixed['display']['row_full_upper'],
     full_error_outward_lower=fixed['display']['full_error_lower'],
     full_error_percent_lower=fixed['display']['full_error_percent_lower']+'%',
     exact_certificate_selector='profiles.'+key+'.fixed_A',
     same_display_endpoints_given_initial_full_correct=True,
     positive_full_correct_lower_factorization=fixed['full_correct_lower_factorization']),
   uniform_full_matrix_Setup_average=dict(full_correct_outward_upper=uniform['display']['row_full_upper'],
     full_error_percent_lower=uniform['display']['full_error_percent_lower']+'%',
     exact_certificate_selector='profiles.'+key+'.uniform_Setup',
     same_display_endpoints_given_initial_full_correct=True),
   core_proof_bottlenecks=[],
   precision_obstacles=['Low-frequency envelope and full-interval eighth-moment chord',
     'Exact64-coordinate probability requires a cross-row joint argument'],
   author_software_applicability='WAITING_FOR_AUTHOR_ARTIFACT')
verdict=dict(schema='fi-official-profile-correctness/verdict/1',stage='参数化可靠性判据与官方976／1344配置认证',
 date_asia_shanghai='2026-11-11',identity=cert['identity'],
 completion='BOTH_PROFILES_HAVE_REVIEWABLE_STRICT_PROBABILITY_CONCLUSIONS',
 parametric_proposition=dict(status='PROVED_UNDER_STATED_MODEL',
   formula='U_row_raw=(1-delta)*(pi0^k+C_k(pi0)*Z)+delta; C_k=sum(pi0^j,j=0..k-1)',
   conditions=['FI journal/v4 raw residual with declared n-column Ord/Tensor normalization',
    'Exact independent symmetric finite chi after every pre-fixed A; same A across generations',
    'One honest unscreened TG/Upd; every P2 rank included',
    'Shared raw-coin V leaves independent identically distributed column packets',
    'B_env-measurable good event; pointwise good-environment E|p(V)-pi0|<=Z',
    'Bad probability<=delta in[0,1]; k>=1; correctly derived common decode set'],
   endpoints='pi0=0 or1 handled exactly; C_k(1)=k; F>=1 yields trivial upper; alpha<1 needed for conditioning',
   counterexample_to_stated_proposition=False,
   unrestricted_high_error_generalization='chi=delta0 is a sanity counterexample; no universal noise-free high-error claim'),
 profiles=profiles,
 new_step_beyond640_substitution='Exact full translated bit-weight PGF maximum over all65536 parent shifts, yielding H thresholds1477/1644 above n; profile-specific parity and full-frequency certification',
 contribution='Concrete finite official-profile reliability cryptanalysis and a conditional abstraction of the640 proof; classical probability tools attributed',
 mathematical_model_scope='Every pre-coins fixed legal message and A; probability averages all subsequent raw chi; printed FI algorithm and official half-up Decode',
 author_software_status='WAITING_FOR_AUTHOR_ARTIFACT',
 exact64_coordinate_success_probability_computed=False,asymptotic_family_claim=False,
 global_priority='UNRESOLVED; six new targeted queries plus cited historical bounded audit',
 new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,new_proof_assistant_checks=0,
 exact_backend_model_id=None,calibration='NOT_CALIBRATED',
 finite_verification=dict(status='PASS',checks=checked['check_count'],historical_snapshot_files=len(snap),historical_inputs_unchanged=True),
 certificate_sha256=sha(ROOT/'OFFICIAL_PROFILE_CERTIFICATES.json'),
 parametric_proof_sha256=sha(ROOT/'PARAMETRIC_CORRECTNESS_BOUND.md'),
 results_scope_sha256=sha(ROOT/'PROFILE_RESULTS_AND_SCOPE.md'),
 execution_scope=dict(cryptographic_samples=0,monte_carlo=0,LWE_solver_runs=0,author_contact=0,external_service_experiments=0,candidate_mechanism_implementations=0))
write(ROOT/'VERDICT.json',verdict)

qa=[]
def qc(label,value):
 assert value,label
 qa.append(label)
for filename in ('PARAMETRIC_CORRECTNESS_BOUND.md','PROFILE_RESULTS_AND_SCOPE.md'):
 text=(ROOT/filename).read_text(encoding='utf-8')
 qc(filename+'/requested-style', '不是' not in text)
 qc(filename+'/display-math-delimiters',text.count('\\[')==text.count('\\]'))
 qc(filename+'/code-fences',text.count('```')%2==0)
 qc(filename+'/check-count',str(checked['check_count']) in text)
 for name,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
  if target.startswith(('https://','http://')): continue
  qc(filename+'/local-link/'+target,(ROOT/target).resolve().exists())
 for key,p in profiles.items():
  qc(filename+'/'+key+'/full-correct-display',p['every_fixed_A']['full_correct_outward_upper'] in text)
  qc(filename+'/'+key+'/full-error-display',p['every_fixed_A']['full_error_percent_lower'].rstrip('%') in text)
for key,p in cert['profiles'].items():
 groups=p['fixed_A']['frequency_groups']; pi=rd(p['parameters']['pi0'])
 tail=sum((2*pi*g['count']*rd(g['R_power_n_up']) for g in groups if g['range'][0]>=8),F())
 if key=='1344': qc('1344/displayed-low-frequency-remainder',tail<F('0.0000008725'))
 high=2*pi*groups[-1]['count']*rd(groups[-1]['R_power_n_up'])
 qc(key+'/displayed-high-frequency-negligibility',high<F(1,10**19))
for item in snap+additional:
 qc('final-input-byte-check/'+item['path'],sha(Path(item['path']))==item['sha256'])
for p in ROOT.rglob('*.json'):
 json.loads(p.read_text(encoding='utf-8'))
write(E/'DOCUMENT_QA.json',dict(status='PASS',checks=qa,check_count=len(qa),
 four_requested_deliverables_present=all((ROOT/f).exists() for f in (
 'PARAMETRIC_CORRECTNESS_BOUND.md','OFFICIAL_PROFILE_CERTIFICATES.json','PROFILE_RESULTS_AND_SCOPE.md','VERDICT.json'))))
manifest=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name!='DELIVERY_MANIFEST.json':
  manifest.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)))
write(E/'DELIVERY_MANIFEST.json',dict(schema='fi-official-profile-delivery/1',date_asia_shanghai='2026-11-11',
 files=manifest,manifest_excludes_self=True,historical_inputs_unchanged=True))
print('Final document checks:',len(qa),'PASS; delivery files:',len(manifest)+1)
