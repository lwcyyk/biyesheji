"""Local sealing utility. Excludes only MANIFEST.json; ZIP stays outside package."""
from pathlib import Path
import hashlib,json,zipfile,sys
B=Path(r'D:\毕业设计');O=B/'crypto_fi_external_review_package'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 files=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.rglob('*')) if p.is_file() and p!=O/'MANIFEST.json']
 m=dict(schema='fi-external-review/manifest/1',version='Frodo-FI-v3-external-review-2026-11-11',date_asia_shanghai='2026-11-11',identity='INFORMED_HANDOFF_ASSEMBLY_AND_DETERMINISTIC_SCALAR_REPLAY',declared_model_family='Codex based on GPT-6',exact_backend_model_id=None,exact_weights_version=None,new_human_reviews=0,new_independent_model_reviews=0,new_cross_model_reviews=0,candidate_mechanism_implementations=0,self_exclusion=['MANIFEST.json'],self_hash=None,self_hash_rule='No manifest self-hash. Hash every other package file by relative path; ZIP SHA256 and sidecar are outside package. PORTABILITY_REPORT is included.',files=files)
 (O/'MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 z=B/'crypto_fi_external_review_package.zip'
 with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as f:
  for p in sorted(O.rglob('*')):
   if p.is_file():f.write(p,p.relative_to(O).as_posix())
 (B/'crypto_fi_external_review_package.zip.sha256').write_text(sha(z)+'  '+z.name+'\n',encoding='ascii')
 print(json.dumps(dict(files=len(files)+1,archive=str(z),archive_bytes=z.stat().st_size,sha256=sha(z)),ensure_ascii=False))
if __name__=='__main__':main()
