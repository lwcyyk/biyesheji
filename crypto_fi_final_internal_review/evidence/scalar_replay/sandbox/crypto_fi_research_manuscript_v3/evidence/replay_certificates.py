"""Replay frozen scalar arithmetic only, with byte-identical script copies in v3."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,subprocess,sys,time
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_research_manuscript_v3'
AUTHOR=BASE/'crypto_fi_official_profile_correctness';REVIEW=BASE/'crypto_fi_official_profile_review'
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
copies=[]
def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
 copies.append(dict(source=rec(src),copy=rec(dst),byte_identical=True));return dst
aroot=OUT/'certificates/author/crypto_fi_official_profile_correctness'
rroot=OUT/'certificates/review'
for name in ['compute_profile_certificates.py','verify_profile_certificates.py','INPUT_SNAPSHOT.json','SOURCE_PAGES.json']:
 cp(AUTHOR/'evidence'/name,aroot/'evidence'/name)
for rel in ['crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json','crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json']:
 cp(BASE/rel,OUT/'certificates/author'/rel)
for name in ['recompute_review.py','verify_historical_relations.py']:
 cp(REVIEW/'evidence'/name,rroot/'evidence'/name)
runs=[]
for tag,script in [('author_compute',aroot/'evidence/compute_profile_certificates.py'),('author_verify',aroot/'evidence/verify_profile_certificates.py'),('review_reconstruct',rroot/'evidence/recompute_review.py'),('source_event_relations',rroot/'evidence/verify_historical_relations.py')]:
 start=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat();t=time.perf_counter()
 r=subprocess.run([sys.executable,'-X','utf8',str(script)],capture_output=True,text=True,encoding='utf-8',cwd=OUT)
 log=OUT/'evidence'/f'{tag}.log';log.write_text(r.stdout+('\nSTDERR:\n'+r.stderr if r.stderr else ''),encoding='utf-8')
 runs.append(dict(tag=tag,command=[sys.executable,'-X','utf8',str(script)],script=rec(script),started_at_asia_shanghai=start,elapsed_seconds=time.perf_counter()-t,exit_code=r.returncode,log=rec(log)))
 assert r.returncode==0,(tag,r.stdout,r.stderr)
 print(tag,'PASS',flush=True)
generated=aroot/'OFFICIAL_PROFILE_CERTIFICATES.json'
assert generated.read_bytes()==(AUTHOR/'OFFICIAL_PROFILE_CERTIFICATES.json').read_bytes()
cp(generated,OUT/'certificates/OFFICIAL_PROFILE_CERTIFICATES.json')
for name,src in [('640_FIXED_A_CERTIFICATES.json',BASE/'crypto_fi_research_manuscript_v2_2/FINITE_CERTIFICATES.json'),('640_UNIFORM_RESULTS.json',BASE/'crypto_fi_640_probability_review/review_01a1c4ed/evidence/RECOMPUTED_PROBABILITY_CHAIN.json')]:
 cp(src,OUT/'certificates'/name)
review_result=load(rroot/'evidence/INDEPENDENT_RECOMPUTATION.json');old_review=load(REVIEW/'evidence/INDEPENDENT_RECOMPUTATION.json')
def stable(x):
 if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if k not in ['seconds','total_seconds','enumeration_seconds']}
 if isinstance(x,list):return [stable(v) for v in x]
 return x
assert stable(review_result)==stable(old_review)
assert review_result['check_count']==9196 and review_result['status']=='PASS'
pgf=[]
for n in [976,1344]:
 m=rroot/f'evidence/PGF_SHIFT_TO_REP_{n}.u16le';oldmap=REVIEW/f'evidence/PGF_SHIFT_TO_REP_{n}.u16le'
 assert m.read_bytes()==oldmap.read_bytes()
 doc=load(rroot/f'evidence/PGF_FULL_COVERAGE_{n}.json');original=load(REVIEW/f'evidence/PGF_FULL_COVERAGE_{n}.json')
 doc.pop('map_path');original.pop('map_path');assert doc==original
 pgf.append(dict(n=n,translation_map=rec(m),representative_certificate=rec(rroot/f'evidence/PGF_FULL_COVERAGE_{n}.json'),all_map_bytes_and_representatives_match_historical=True))
verify=load(aroot/'evidence/CERTIFICATE_CHECK.json')
relations=load(rroot/'evidence/HISTORICAL_EVENT_RELATIONS.json')
assert relations==load(REVIEW/'evidence/HISTORICAL_EVENT_RELATIONS.json')
dump(OUT/'evidence/REPLAY_EXECUTION.json',dict(schema='frodo-fi-v3/scalar-replay/1',date_asia_shanghai='2026-11-11',identity='INFORMED_AUTHOR_REVISION_PARAMETRIC_PROOF_INTEGRATION_AND_STAGE_HANDOFF',scope='Byte-identical scalar-script copies; no new mathematical review or model independence attestation',script_and_input_copies=copies,runs=runs,whole_author_certificate_byte_identical=True,author_check_result=rec(aroot/'evidence/CERTIFICATE_CHECK.json'),author_check_summary={k:v for k,v in verify.items() if not isinstance(v,(dict,list))},review_result=rec(rroot/'evidence/INDEPENDENT_RECOMPUTATION.json'),review_named_arithmetic_comparisons=9196,review_result_stable_payload_equal=True,comparison_excluded_clock_keys=['seconds','total_seconds','enumeration_seconds'],full_translation_maps=pgf,source_event_relation_result=rec(rroot/'evidence/HISTORICAL_EVENT_RELATIONS.json'),source_event_convolutions_replayed=[1281,769],cryptographic_samples=0,Monte_Carlo_runs=0,candidate_mechanism_implementations=0,new_independent_reviews=0,historical_script_executions=0))
print(json.dumps(dict(status='PASS',author_verify_summary={k:v for k,v in verify.items() if k in ['check_count','checks_passed','status']},review_comparisons=9196,author_certificate_byte_equal=True,all_65536_shift_maps_match=True),ensure_ascii=False))
