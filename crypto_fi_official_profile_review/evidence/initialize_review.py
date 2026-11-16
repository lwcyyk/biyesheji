"""Read-only source intake and contained author-script replay preparation."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, os
from datetime import datetime, timezone, timedelta
import fitz

BASE=Path('D:/毕业设计')
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence'
E.mkdir(parents=True,exist_ok=True)
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=BASE/'crypto_fi_official_profile_correctness'
paths={p for p in src.rglob('*') if p.is_file()}
for ent in json.loads((src/'evidence/INPUT_SNAPSHOT.json').read_text(encoding='utf-8')):
 paths.add(Path(ent['path']))
for name in ['crypto_fi_640_probability_review/review_01a1c4ed','crypto_fi_640_fixed_A_review','crypto_fi_lwe_independent_review']:
 paths.update(p for p in (BASE/name).glob('*.md'))
 paths.update(p for p in (BASE/name).glob('*.json'))
for name in ['crypto_fi_author_implementation_audit/VERDICT.json','crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md']:
 paths.add(BASE/name)
sources=[('official_2021',BASE/'crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf',[10,15,16,25]),
 ('official_2023',BASE/'crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf',[8,15,16]),
 ('FI',BASE/'crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf',[12,13,14,15])]
paths.update(p for _,p,_ in sources)
snap=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(paths)]
write(E/'INPUT_SNAPSHOT.json',snap)
write(E/'SESSION_INTAKE.json',dict(date=datetime.now(timezone(timedelta(hours=8))).isoformat(),
 chat_id=os.environ.get('CODEX_THREAD_ID'),identity='AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW',
 declared_family='Codex based on GPT-6 (developer declaration)',exact_backend_model_id=None,
 exact_weight_version=None,author_proof_visible=True,historical_reviews_visible=True,
 new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,
 formal_proof_assistant_runs=0,calibration='NOT_CALIBRATED',
 scope='Paper mathematics, primary specifications and deterministic finite distributions/interval arithmetic; no candidate mechanism implementation',
 historical_baseline='After initial read-only intake and before replay or independent computations',
 fingerprinting_does_not_imply_semantic_reading=True))
rb=E/'author_replay'
for name in ['compute_profile_certificates.py','verify_profile_certificates.py','INPUT_SNAPSHOT.json','SOURCE_PAGES.json']:
 dst=rb/'crypto_fi_official_profile_correctness/evidence'/name
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src/'evidence'/name,dst)
for rel in ['crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json','crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json']:
 dst=rb/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(BASE/rel,dst)
preflight=Path('C:/Users/a1887/.codex/skills/academic-research-suite/ars/scripts/pdf_read_preflight.py')
records=[]
for tag,p,pages in sources:
 run=subprocess.run([sys.executable,str(preflight),str(p)],capture_output=True,
  env={**os.environ,'PYTHONIOENCODING':'utf-8'})
 (E/f'{tag}_PREFLIGHT.stdout.json').write_bytes(run.stdout)
 (E/f'{tag}_PREFLIGHT.stderr.txt').write_bytes(run.stderr)
 pf=json.loads(run.stdout.decode('utf-8')); assert run.returncode==0 and pf['verdict']=='PASS'
 assert pf['sha256']==digest(p)
 with fitz.open(p) as pdf:
  for page in pages:
   text=pdf[page-1].get_text(); txt=E/f'{tag}_p{page}.txt'; txt.write_text(text,encoding='utf-8')
   png=E/f'{tag}_p{page}.png'; pdf[page-1].get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(png)
   records.append(dict(tag=tag,path=str(p),sha256=digest(p),physical_pdf_page=page,
    pages=len(pdf),text_path=str(txt),png_path=str(png),text_sha256=digest(txt),png_sha256=digest(png)))
write(E/'SOURCE_PAGES.json',records)
print('Source intake:',len(snap),'fingerprints;',len(records),'PDF pages; all preflights PASS.')
