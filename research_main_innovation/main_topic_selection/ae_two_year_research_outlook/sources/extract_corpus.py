from pathlib import Path
import hashlib,json,re,subprocess,sys,logging
from datetime import datetime,timezone
from pypdf import PdfReader

root=Path(r'D:\毕业设计\关键论文与可行性核查_2026-11-04')
out=Path(__file__).parent
preflight=Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py')
records=[]
for f in sorted((root/'论文全文').glob('*.pdf')):
    slug=f.stem.split('_')[0]
    check=subprocess.run([sys.executable,str(preflight),str(f)],capture_output=True,text=True,encoding='utf-8')
    (out/(slug+'_structure.json')).write_text(check.stdout,encoding='utf-8')
    r=PdfReader(f)
    pages=[p.extract_text() or '' for p in r.pages]
    (out/(slug+'_pages.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
    (out/(slug+'_text.txt')).write_text('\n'.join(f'\n[PDF PAGE {i+1}]\n{p}' for i,p in enumerate(pages)),encoding='utf-8')
    headings=[]
    for i,p in enumerate(pages):
        for line in p.splitlines():
            if re.search(r'(?i)limitation|future work|discussion|conclusion|threat model|system model|security model|^\d+[. ]+.*(?:policy|design|protocol|evaluation|scope)',line):
                headings.append({'page':i+1,'line':line[:220]})
    rec={'id':slug,'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pages':len(pages),'metadata':{str(k):str(v) for k,v in (r.metadata or {}).items()},'headings':headings}
    records.append(rec)
    print(slug,len(pages),len(''.join(pages)),flush=True)
for f in sorted((root/'标准草案').glob('*.txt')):
    records.append({'id':f.stem,'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(out/'CORPUS_MANIFEST.json').write_text(json.dumps({'date':datetime.now(timezone.utc).isoformat(),'note':'Extraction and structural checks only; actual read scope recorded separately.','records':records},ensure_ascii=False,indent=2),encoding='utf-8')
