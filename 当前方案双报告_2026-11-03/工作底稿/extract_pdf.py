from pathlib import Path
import json,subprocess,sys
from pypdf import PdfReader
R=Path(r'D:\毕业设计');W=Path(__file__).parent
paths=[R/'研究'/'Randomizing_polynomials_A_new_representation_with_applications_to_round-efficient_secure_computation.pdf',R/'研究'/'3-3-4.pdf']
for i,p in enumerate(paths):
 subprocess.run([sys.executable,'-X','utf8',r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py',str(p),'--output',str(W/f'paper{i+1}_preflight.json')],capture_output=True)
 r=PdfReader(p);text='\n'.join(f'\n[PHYSICAL_PAGE {i+1}]\n'+page.extract_text() for i,page in enumerate(r.pages));(W/f'paper{i+1}.txt').write_text(text,encoding='utf-8');print(p.name,len(r.pages),text[:1800])
