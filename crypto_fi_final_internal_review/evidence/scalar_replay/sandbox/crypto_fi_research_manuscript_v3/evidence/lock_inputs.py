"""Read-only historical fingerprint lock for the explicitly requested v3 integration."""
from pathlib import Path
import hashlib,json
BASE=Path(r'D:\毕业设计'); OUT=BASE/'crypto_fi_research_manuscript_v3'
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def nodes(x,loc='$'):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str):yield loc,x
  for k,v in x.items():yield from nodes(v,loc+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from nodes(v,loc+f'[{i}]')
paths=set()
for name in ['crypto_fi_research_manuscript_v2_2','crypto_fi_official_profile_correctness','crypto_fi_official_profile_review']:
 paths.update(p.resolve() for p in (BASE/name).rglob('*') if p.is_file())
for name in ['crypto_fi_author_implementation_audit/IMPLEMENTATION_MODEL_MAPPING.md','crypto_fi_author_implementation_audit/VERDICT.json','crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md','crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json']:
 paths.add((BASE/name).resolve())
cache={};records={};refs=[]
def cached(p):
 p=p.resolve();k=str(p)
 if k not in cache:cache[k]=rec(p)
 return cache[k]
for p in sorted(paths):
 records[str(p)]=cached(p)
 if p.suffix.lower()!='.json':continue
 x=json.loads(p.read_text(encoding='utf-8-sig'))
 for loc,r in nodes(x):
  t=Path(r['path'])
  if not t.is_absolute():
   candidates=[parent/t for parent in [p.parent,*p.parents] if parent==BASE or BASE in parent.parents]
   existing=[z.resolve() for z in candidates if z.is_file()]
   matches=[z for z in existing if cached(z)['sha256'].lower()==r['sha256'].lower()]
   assert matches,(p,loc,r,existing)
   t=matches[0]
  actual=cached(t)
  matched=actual['sha256'].lower()==r['sha256'].lower() and ('bytes' not in r or actual['bytes']==r['bytes'])
  assert matched,(p,loc,r,actual)
  refs.append(dict(source=str(p),locator=loc,target=actual,matched=True));records[actual['path']]=actual
snapshot=dict(schema='frodo-fi-v3/input-snapshot/1',date_asia_shanghai='2026-11-11',direct_file_count=len(paths),unique_historical_file_count=len(records),reading_scope='Relevant v2.2 manuscript/core JSON, latest parametric proof/scope/review/corrections, exact certificate fields and scripts; prior proofs/source-page reading scopes inherited. Hashing does not imply semantic reading.',files=sorted(records.values(),key=lambda r:r['path']))
dump(OUT/'evidence/INPUT_SNAPSHOT.json',snapshot)
dump(OUT/'evidence/INPUT_FINGERPRINT_CHECK.json',dict(records_checked=len(refs),all_matched=True,records=refs))
print(json.dumps(dict(direct_files=len(paths),unique_historical_files=len(records),embedded_fingerprint_records=len(refs),all_matched=True)))
