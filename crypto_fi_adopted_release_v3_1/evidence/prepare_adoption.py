"""Read-only historical lock and byte-identical certificate archive for v3.1 adoption."""
from pathlib import Path
import hashlib,json
B=Path(r'D:\毕业设计');O=B/'crypto_fi_adopted_release_v3_1';V=B/'crypto_fi_research_manuscript_v3';R=B/'crypto_fi_final_internal_review'
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def nodes(x,loc='$'):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str):yield loc,x
  for k,v in x.items():yield from nodes(v,loc+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from nodes(v,loc+f'[{i}]')
paths={p.resolve() for p in V.rglob('*') if p.is_file()}
paths.update((R/x).resolve() for x in ['FINAL_INTERNAL_DECISION.md','REVIEW_PROVENANCE.json','MANIFEST.json','evidence/LOCAL_SCOPE_CORRECTIONS.json','evidence/FINAL_SCALAR_CHECKS.json','evidence/scalar_replay/REPLAY_RESULT.json'])
paths.update((B/x).resolve() for x in ['research_g1_lifecycle_contract/2026-11-09_r01/08_G1_VERDICT_AND_MAINLINE_HANDOFF.md','crypto_fi_original_game_decision/APPLICATION_PRIORITY_AUDIT.md','crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md','crypto_fi_official_profile_correctness/PARAMETRIC_CORRECTNESS_BOUND.md','crypto_fi_official_profile_correctness/evidence/PUBLIC_PRECEDENT_SEARCH_RECEIPT.json'])
cache={};locked={};refs=[]
def measured(p):
 p=p.resolve();k=str(p)
 if k not in cache:cache[k]=rec(p)
 return cache[k]
for p in sorted(paths):
 locked[str(p)]=measured(p)
 if p.suffix.lower()!='.json':continue
 x=json.loads(p.read_text(encoding='utf-8-sig'))
 for loc,r in nodes(x):
  q=Path(r['path'])
  if not q.is_absolute():
   cand=[(parent/q).resolve() for parent in [p.parent,*p.parents] if parent==B or B in parent.parents]
   found=[q for q in cand if q.is_file() and measured(q)['sha256'].lower()==r['sha256'].lower()]
   assert found,(str(p),loc,r);q=found[0]
  now=measured(q);ok=now['sha256'].lower()==r['sha256'].lower() and ('bytes' not in r or now['bytes']==r['bytes'])
  assert ok,(str(p),loc,r,now)
  locked[now['path']]=now;refs.append(dict(source=str(p),locator=loc,target=now,matched=True))
seals=[]
for p in [V/'MANIFEST.json',R/'MANIFEST.json']:
 x=json.loads(p.read_text(encoding='utf-8-sig'));old=x.pop('payload_sha256')
 got=hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
 assert got==old
 seals.append(dict(file=rec(p),payload_sha256=old,canonical_payload_matched=True))
dump(O/'evidence/INPUT_SNAPSHOT.json',dict(schema='frodo-fi-adopted-v31/input-snapshot/1',date_asia_shanghai='2026-11-11',direct_file_count=len(paths),unique_historical_file_count=len(locked),files=sorted(locked.values(),key=lambda r:r['path']),scope='All v3 files, specified final-review inputs and adopted scalar/provenance/priority/business sources;bytes/JSON parsing do not attest new full semantic review'))
dump(O/'evidence/INPUT_FINGERPRINT_CHECK.json',dict(records_checked=len(refs),all_matched=True,records=refs,inherited_canonical_seals=seals))
copies=[]
for p in sorted((V/'certificates').rglob('*')):
 if p.is_file():
  q=O/'certificates'/p.relative_to(V/'certificates');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
  copies.append(dict(source=rec(p),archive=rec(q),byte_identical=True))
dump(O/'evidence/CERTIFICATE_ARCHIVE.json',dict(scope='Frozen v3 certificate tree copied byte-for-byte;no scalar generators/verifiers executed during adoption;internal historical path strings retained',files=copies,mathematical_payload_changed=False,new_scalar_replays=0))
print(json.dumps(dict(direct_files=len(paths),unique_historical_files=len(locked),embedded_fingerprint_records=len(refs),all_matched=True,canonical_seals_matched=len(seals),certificate_files_archived=len(copies))))
