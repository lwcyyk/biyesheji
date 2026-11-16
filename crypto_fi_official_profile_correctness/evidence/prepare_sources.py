"""Read-only provenance and source-page extraction; writes only beside this script."""
from pathlib import Path
import hashlib, json, subprocess, sys
import fitz

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[1]
sys.stdout.reconfigure(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
roots = [BASE / s for s in ('crypto_fi_research_manuscript_v2_2',
         'crypto_fi_640_fixed_A_correctness', 'crypto_fi_640_fixed_A_review')]
extra = [BASE / 'crypto_fi_research_manuscript_v2_1' / s for s in
         ('ERRATUM_AND_CERTIFICATE_AUDIT.md', 'evidence/DISTRIBUTION_TABLES.json',
          'evidence/replay_976_and_check_tables.py')]
extra += [BASE / 'crypto_fi_research_manuscript_v1/sources/articlev08.tex']
files = sorted(set(p for r in roots for p in r.rglob('*') if p.is_file()) | set(extra))
snap = [{'path':str(p), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in files]
(OUT/'INPUT_SNAPSHOT.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
preflight = Path('C:/Users/a1887/.codex/skills/academic-research-suite/ars/scripts/pdf_read_preflight.py')
records=[]
for tag, path, pages in [
 ('official_2021', BASE/'crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf', [10,15,16,25]),
 ('official_2023', BASE/'crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf', [8,15,16]),
 ('FI', BASE/'crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf', [12,14,15])]:
 result=subprocess.run([sys.executable,str(preflight),str(path)],capture_output=True,check=True)
 pf=json.loads(result.stdout.decode('utf-8',errors='replace'))
 assert pf['verdict']=='PASS' and pf['sha256']==sha(path)
 (OUT/f'{tag}_PREFLIGHT.json').write_text(json.dumps(pf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with fitz.open(path) as pdf:
  for page in pages:
   pg=pdf[page-1]
   png=OUT/f'{tag}_p{page}.png'
   pg.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(png)
   (OUT/f'{tag}_p{page}.txt').write_text(pg.get_text(),encoding='utf-8')
   records.append(dict(tag=tag,path=str(path),sha256=sha(path),page=page,
       page_count=len(pdf),png=str(png),png_sha256=sha(png)))
(OUT/'SOURCE_PAGES.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Frozen',len(snap),'historical input files; extracted',len(records),'source pages.')
