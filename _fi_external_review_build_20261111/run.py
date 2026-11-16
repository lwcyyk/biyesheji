"""Public deterministic scalar replay. Python 3.11+, standard library only.

All historical sources are read from this package. Every write targets a new
external work directory. Run with --output ABSOLUTE_NEW_DIRECTORY.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys,time
from datetime import datetime,timezone

sys.set_int_max_str_digits(0)
PACKAGE=Path(__file__).resolve().parents[1]
FROZEN=PACKAGE/'frozen'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fingerprints(root):
 return {p.relative_to(root).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(root.rglob('*')) if p.is_file()}
def rf(x):return F(int(x['numerator']),int(x['denominator']))
def fraction(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def compare_json(actual,expected,allowed=None):
 """Exact recursive comparison with a closed JSON-pointer metadata allowlist."""
 a,b=load(actual),load(expected);allowed=allowed or {};differences=[];visited=[]
 def walk(x,y,p=''):
  if p in allowed:
   kind=allowed[p]
   if kind=='clock':assert isinstance(x,(int,float)) and x>=0 and isinstance(y,(int,float))
   elif kind=='script_sha256':assert x==sha(ACTIVE_SCRIPT) and re.fullmatch('[0-9a-f]{64}',y)
   elif kind=='map_path':assert Path(x).resolve().is_relative_to(SANDBOX) and Path(x).is_file()
   elif kind=='python_version':assert isinstance(x,str) and x==platform.python_version() and isinstance(y,str)
   else:raise AssertionError(('unknown comparison exception',p,kind))
   differences.append(dict(pointer=p,rule=kind,actual=x,frozen=y));visited.append(p);return
  assert type(x)==type(y),(p,type(x),type(y))
  if isinstance(x,dict):
   assert x.keys()==y.keys(),(p,x.keys()^y.keys())
   for k in x:walk(x[k],y[k],p+'/'+k.replace('~','~0').replace('/','~1'))
  elif isinstance(x,list):
   assert len(x)==len(y),(p,len(x),len(y))
   for i,(xx,yy) in enumerate(zip(x,y)):walk(xx,yy,p+'/'+str(i))
  else:assert x==y,(p,str(x)[:300],str(y)[:300])
 walk(a,b);assert set(visited)==set(allowed),(visited,allowed)
 return dict(generated=str(actual),frozen=expected.relative_to(PACKAGE).as_posix(),complete_mathematical_payload_equal=True,metadata_comparisons=differences,actual_sha256=sha(actual),frozen_sha256=sha(expected),byte_equal=actual.read_bytes()==expected.read_bytes())

def main():
 global SANDBOX,ACTIVE_SCRIPT
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',required=True,help='New absolute external work directory; must not exist')
 args=parser.parse_args();work=Path(args.output).expanduser()
 assert work.is_absolute(),'--output must be absolute'
 work=work.resolve()
 assert not work.exists(),'Choose a new output directory'
 assert not work.is_relative_to(PACKAGE) and not PACKAGE.is_relative_to(work),'Output must be outside package'
 before=fingerprints(PACKAGE)
 # Verify the sealed payload before execution. MANIFEST intentionally excludes itself.
 manifest=load(PACKAGE/'MANIFEST.json')
 assert manifest['self_exclusion']==['MANIFEST.json']
 assert set(before)-{'MANIFEST.json'}=={x['path'] for x in manifest['files']}
 for item in manifest['files']:assert before[item['path']]==dict(bytes=item['bytes'],sha256=item['sha256']),item['path']
 work.mkdir(parents=True);SANDBOX=work/'sandbox';shutil.copytree(FROZEN,SANDBOX)
 dump(work/'INPUT_FINGERPRINTS_BEFORE.json',before)
 source_map=load(PACKAGE/'provenance/PATH_MAP.json')
 origin={e['original_path'].replace('\\','/').casefold():e['relative_origin'] for e in source_map['entries']}
 # The unchanged verifier follows these explicit file records. Retain file identities.
 metadata_rewrites=[]
 for rel in ['crypto_fi_official_profile_correctness/evidence/INPUT_SNAPSHOT.json','crypto_fi_official_profile_correctness/evidence/SOURCE_PAGES.json']:
  x=load(SANDBOX/rel)
  for item in x:
   for key in ['path','png']:
    if key in item:
     old=item[key];target=origin.get(old.replace('\\','/').casefold())
     if target:
      item[key]=str(SANDBOX/target);metadata_rewrites.append(dict(file=rel,key=key,source=old,sandbox=item[key]))
     elif key=='path':raise AssertionError(('unbundled verifier input',old))
  dump(SANDBOX/rel,x)
 adapters=load(PACKAGE/'provenance/SCRIPT_ADAPTATIONS.json')
 for item in adapters['adapters']:
  name=item['source'].removeprefix('frozen/')
  shutil.copyfile(PACKAGE/item['adapted'],SANDBOX/name)
 env=os.environ.copy();env['FRODO_FI_SANDBOX']=str(SANDBOX)
 scripts=[
 ('author_compute','crypto_fi_official_profile_correctness/evidence/compute_profile_certificates.py'),
 ('author_verify','crypto_fi_official_profile_correctness/evidence/verify_profile_certificates.py'),
 ('review_976_1344','crypto_fi_official_profile_review/evidence/recompute_review.py'),
 ('source_event_976_1344','crypto_fi_official_profile_review/evidence/verify_historical_relations.py'),
 ('fixed_A_640','crypto_fi_640_fixed_A_review/evidence/recompute_certificates.py'),
 ('uniform_Setup_640','crypto_fi_640_probability_review/review_01a1c4ed/evidence/recompute_probability_chain.py'),
 ('A_all_convolutions','crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/math_verify.py'),
 ]
 runs=[];comparisons=[]
 for tag,rel in scripts:
  ACTIVE_SCRIPT=SANDBOX/rel
  audit=work/'logs'/(tag+'.file_opens.jsonl');audit.parent.mkdir(exist_ok=True)
  command=[sys.executable,'-I','-S','-B','-X','utf8',str(PACKAGE/'replay/scalar_launcher.py'),str(ACTIVE_SCRIPT),str(audit)]
  start=time.perf_counter();r=subprocess.run(command,cwd=work,env=env,capture_output=True,text=True,encoding='utf-8',timeout=600)
  log=work/'logs'/(tag+'.log');log.parent.mkdir(exist_ok=True);log.write_text(r.stdout+'\nSTDERR:\n'+r.stderr,encoding='utf-8')
  opens=[json.loads(line) for line in audit.read_text(encoding='utf-8').splitlines()]
  assert opens and all(x['allowed'] for x in opens),(tag,'file-open audit')
  runs.append(dict(tag=tag,command=command,cwd=str(work),script_sha256=sha(ACTIVE_SCRIPT),seconds=time.perf_counter()-start,exit_code=r.returncode,log=str(log),file_open_audit=str(audit),data_opens_outside_work=0,file_open_count=len(opens)))
  assert r.returncode==0,(tag,r.returncode,r.stdout[-2000:],r.stderr[-2000:])
  print(tag,'PASS',flush=True)
  if tag=='author_compute':
   comparisons.append(compare_json(SANDBOX/'crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json',FROZEN/'crypto_fi_research_manuscript_v3/certificates/OFFICIAL_PROFILE_CERTIFICATES.json'))
   assert comparisons[-1]['byte_equal']
  elif tag=='author_verify':
   comparisons.append(compare_json(SANDBOX/'crypto_fi_official_profile_correctness/evidence/CERTIFICATE_CHECK.json',FROZEN/'crypto_fi_research_manuscript_v3/certificates/author/crypto_fi_official_profile_correctness/evidence/CERTIFICATE_CHECK.json'))
  elif tag=='review_976_1344':
   allow={'/script_sha256':'script_sha256','/seconds':'clock'}
   for n in ['976','1344']:
    allow['/profiles/'+n+'/H/enumeration_seconds']='clock';allow['/profiles/'+n+'/total_seconds']='clock'
   comparisons.append(compare_json(SANDBOX/'crypto_fi_official_profile_review/evidence/INDEPENDENT_RECOMPUTATION.json',FROZEN/'crypto_fi_research_manuscript_v3/certificates/review/evidence/INDEPENDENT_RECOMPUTATION.json',allow))
   for n in ['976','1344']:
    base='crypto_fi_official_profile_review/evidence/';v3='crypto_fi_research_manuscript_v3/certificates/review/evidence/'
    comparisons.append(compare_json(SANDBOX/(base+'PGF_FULL_COVERAGE_'+n+'.json'),FROZEN/(v3+'PGF_FULL_COVERAGE_'+n+'.json'),{'/map_path':'map_path'}))
    a=SANDBOX/(base+'PGF_SHIFT_TO_REP_'+n+'.u16le');b=FROZEN/(v3+'PGF_SHIFT_TO_REP_'+n+'.u16le')
    assert a.read_bytes()==b.read_bytes() and a.stat().st_size==131072
    comparisons.append(dict(binary_map=n,bytes=a.stat().st_size,sha256=sha(a),byte_equal=True))
  elif tag=='source_event_976_1344':
   comparisons.append(compare_json(SANDBOX/'crypto_fi_official_profile_review/evidence/HISTORICAL_EVENT_RELATIONS.json',FROZEN/'crypto_fi_research_manuscript_v3/certificates/review/evidence/HISTORICAL_EVENT_RELATIONS.json'))
  elif tag=='fixed_A_640':
   comparisons.append(compare_json(SANDBOX/'crypto_fi_640_fixed_A_review/evidence/RECOMPUTED_CERTIFICATES.json',FROZEN/'crypto_fi_640_fixed_A_review/evidence/RECOMPUTED_CERTIFICATES.json',{'/python':'python_version'}))
  elif tag=='uniform_Setup_640':
   comparisons.append(compare_json(SANDBOX/'crypto_fi_640_probability_review/review_01a1c4ed/evidence/RECOMPUTED_PROBABILITY_CHAIN.json',FROZEN/'crypto_fi_research_manuscript_v3/certificates/640_UNIFORM_RESULTS.json'))
  elif tag=='A_all_convolutions':
   comparisons.append(compare_json(SANDBOX/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/exact_certificates.json',FROZEN/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/exact_certificates.json'))
 # Whole frozen convolution coefficient arrays are bound by exact integer-array digests.
 result=load(SANDBOX/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/exact_certificates.json');convolution_checks=[]
 for n,s in [('640',12),('976',10),('1344',6)]:
  source=FROZEN/('crypto_fi_research_manuscript_v1/sources/chi_'+n+'_64fold_coefficients.json');c=load(source);coeff=list(map(int,c['coefficients']))
  digest=hashlib.sha256(json.dumps(coeff,separators=(',',':')).encode()).hexdigest()
  assert digest==result[n]['coefficients_sha256'] and len(coeff)==128*s+1 and c['offset']==-64*s and int(c['denominator'])==65536**64 and sum(coeff)==65536**64
  convolution_checks.append(dict(n=int(n),all_integer_coefficients=len(coeff),exact_integer_array_sha256=digest,all_coefficients_equal=True))
 c640=load(FROZEN/'crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json');mu=F(max(map(int,c640['coefficients'])),65536**64);a0=F(1161,8192)
 assert 25*mu<F(1,2)
 import math
 n=128;eps=math.comb(n,63)*a0**(n-63)+(25*mu)**n
 assert eps<=F(1,2**59)
 assert 8*(288*n+12+n*(288*n*n*56+3456*n*n+12*n*56+144*n))<2**56
 dump(work/'A_EXTRA_CHECKS.json',dict(status='PASS',convolutions=convolution_checks,a0=fraction(a0),mu64=fraction(mu),gamma=fraction(25*mu),gamma_less_than_one_half=True,CF1_n128=dict(D=56,query_bound=385,epsilon_upper='2^-59',gap_lower_expression='1-(3/4)^128-2^-59',correctness_strict=True),scope='Finite arithmetic accompanying the symbolic CF-1 theorem and original-game proof'))
 # Bind all six selector endpoints to the actual regenerated scalar payloads.
 selectors=load(FROZEN/'crypto_fi_research_manuscript_v3/certificates/UNIFIED_RESULT_SELECTORS.json')['profiles'];bindings=[]
 for n,p in selectors.items():
  alpha=F(1,2**p['initial']['full_failure_power'])
  for mode in ['fixed_A','uniform_Setup']:
   chosen=p[mode]
   if n=='640':
    if mode=='fixed_A':
     r=load(SANDBOX/'crypto_fi_640_fixed_A_review/evidence/RECOMPUTED_CERTIFICATES.json');u=rf(r['endpoints']['row_and_full_correct_upper']['exact']);uc=rf(r['endpoints']['initial_correct_conditioned_row_and_full_upper']['exact']);z=rf(r['endpoints']['Z']['exact'])
    else:
     r=load(SANDBOX/'crypto_fi_640_probability_review/review_01a1c4ed/evidence/RECOMPUTED_PROBABILITY_CHAIN.json');u=rf(r['joint']['U']['exact']);uc=rf(r['conditional_initial_correct']['row_upper']['exact']);z=rf(r['joint']['Z']['exact'])
   else:
    r=load(SANDBOX/'crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json')['profiles'][n][mode];u=rf(r['full_correct_upper']);uc=rf(r['conditioned_on_initial']['full_correct_upper']);z=rf(r['Z'])
   assert u==rf(chosen['full_correct_upper']) and uc==rf(chosen['conditioned_on_initial']['full_correct_upper']) and uc==u/(1-alpha) and z==rf(chosen['Z'])
   assert uc<=F(chosen['display']['row_full_upper'])
   bindings.append(dict(n=int(n),mode=mode,U=fraction(u),U_conditioned=fraction(uc),display_upper=chosen['display']['row_full_upper'],all_equal=True))
 dump(work/'UNIFIED_SELECTOR_BINDINGS.json',dict(status='PASS',six_endpoints=bindings))
 after=fingerprints(PACKAGE);dump(work/'INPUT_FINGERPRINTS_AFTER.json',after)
 assert before==after,'Package input bytes changed'
 report=dict(schema='fi-external-review/replay-result/1',status='PASS',started_environment=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),external_packages=[]),package=str(PACKAGE),invocation_cwd=str(Path.cwd()),output=str(work),sandbox=str(SANDBOX),completed_at_utc=datetime.now(timezone.utc).isoformat(),runs=runs,comparisons=comparisons,metadata_rewrites=metadata_rewrites,all_mathematical_payloads_equal=True,whole_package_inputs_unchanged=True,all_scalar_file_opens_confined_to_work_or_python_runtime=True,package_file_count=len(before),complete_convolution_checks=convolution_checks,unified_selector_bindings=str(work/'UNIFIED_SELECTOR_BINDINGS.json'),coverage=['All three exact CDF laws and all 65536 scalar sampler inputs per law','A chi640 full convolution, gamma<1/2, epsilon640 and CF1 n128 finite endpoint','Three sizes and both A quantifiers, all displayed endpoints','976/1344 all 65536 shift ids, all representatives and exact maxima','Full frequency groups, directed arithmetic, initial PGFs and conditional endpoints'],candidate_mechanism_implementations=0,cryptographic_samples=0,new_human_reviews=0,scope='Deterministic scalar replay and portable-file integrity; symbolic proofs and source interpretation remain H1/H2 human questions')
 dump(work/'REPLAY_RESULT.json',report)
 print(json.dumps(dict(status='PASS',scripts=len(runs),comparison_artifacts=len(comparisons),package_input_files=len(before),all_mathematical_payloads_equal=True,inputs_unchanged=True,result=str(work/'REPLAY_RESULT.json')),ensure_ascii=False))

if __name__=='__main__':main()
