"""Read-only fingerprint audit and local copies for v2.2 finite-scalar replay."""
from pathlib import Path
import hashlib,json,platform
from datetime import datetime
from zoneinfo import ZoneInfo
BASE=Path(r'D:\毕业设计')
OUT=BASE/'crypto_fi_research_manuscript_v2_2'
def record(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def nodes(x,loc='$'):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str):yield loc,x
  for k,v in x.items():yield from nodes(v,loc+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from nodes(v,loc+f'[{i}]')
def main():
 paths=set()
 for name in ['crypto_fi_research_manuscript_v2_1','crypto_fi_640_fixed_A_correctness','crypto_fi_640_fixed_A_review','crypto_fi_author_implementation_audit']:
  paths.update(p.resolve() for p in (BASE/name).rglob('*') if p.is_file())
 cache={}; refs=[]; all_records={}
 def measured(p):
  p=p.resolve()
  if str(p) not in cache:cache[str(p)]=record(p)
  return cache[str(p)]
 for p in sorted(paths):
  all_records[str(p)]=measured(p)
  if p.suffix.lower()!='.json':continue
  x=json.loads(p.read_text(encoding='utf-8-sig'))
  for loc,r in nodes(x):
   t=Path(r['path']);t=t if t.is_absolute() else p.parent/t
   got=measured(t);matched=got['sha256'].lower()==r['sha256'].lower() and ('bytes' not in r or got['bytes']==r['bytes'])
   refs.append({'source':str(p),'locator':loc,'target':got,'matched':matched})
   assert matched,refs[-1]
   all_records[got['path']]=got
 write(OUT/'evidence/INPUT_SNAPSHOT.json',{'schema':'frodo-fi-v22/input-snapshot/1','date_asia_shanghai':'2026-11-11','direct_file_count':len(paths),'all_historical_file_count':len(all_records),'reading_scope':'Whole relevant proof/review/model mapping and selected v2.1 sections; hashing and JSON parsing do not imply semantic reading','files':list(sorted(all_records.values(),key=lambda r:r['path']))})
 write(OUT/'evidence/INPUT_FINGERPRINT_CHECK.json',{'schema':'frodo-fi-v22/input-fingerprint-check/1','records_checked':len(refs),'all_matched':True,'records':refs})
 copies=[]
 src=BASE/'crypto_fi_640_fixed_A_correctness/evidence/compute_fixed_A.py'
 s=src.read_text(encoding='utf-8');assert s.count("assert hc['exponent']>=70")==1
 s=s.replace("assert hc['exponent']>=70","assert hc['exponent']>=73\nassert (hn << 73) <= hd  # Direct acceptance threshold adopted in v2.2.")
 dst=OUT/'certificates/compute_fixed_A.py';dst.write_text(s,encoding='utf-8')
 copies.append({'source':record(src),'destination':record(dst),'changes':['H exponent threshold 70 -> 73','Direct integer acceptance (hn << 73) <= hd'],'output':'../FINITE_CERTIFICATES.json','all_other_source_text_preserved':True})
 src=BASE/'crypto_fi_640_fixed_A_review/evidence/recompute_certificates.py';s=src.read_text(encoding='utf-8')
 assert s.count("SRC = OUT.parent / 'crypto_fi_640_fixed_A_correctness'")==1
 s=s.replace("SRC = OUT.parent / 'crypto_fi_640_fixed_A_correctness'","SRC = OUT  # Verify the regenerated v2.2 certificate.")
 dst=OUT/'certificates/recompute_certificates.py';dst.write_text(s,encoding='utf-8')
 copies.append({'source':record(src),'destination':record(dst),'changes':['Read regenerated v2.2 FINITE_CERTIFICATES.json; mathematics and 385 checks preserved'],'output':'../evidence/RECOMPUTED_CERTIFICATES.json'})
 write(OUT/'evidence/SCRIPT_COPY_AND_HARDENING.json',{'scope':'Deterministic scalar calculation only; no candidate cryptographic mechanism implementation','copies':copies,'python_version':platform.python_version(),'historical_script_execution_count':0,'historical_writes':0})
 print(json.dumps({'direct_files':len(paths),'unique_locked_files':len(all_records),'embedded_fingerprint_records':len(refs),'all_matched':True,'script_copies':len(copies)}))
if __name__=='__main__':main()
