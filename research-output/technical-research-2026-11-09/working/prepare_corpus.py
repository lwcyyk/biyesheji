from pathlib import Path
from pypdf import PdfReader
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table
import json,re,hashlib,collections,importlib.util,sys
ROOT=Path(r'D:\毕业设计');OUT=Path(__file__).resolve().parents[1]
(OUT/'data/pdf_extracts').mkdir(exist_ok=True)
rows=json.loads((OUT/'data/inventory.json').read_text(encoding='utf-8'))
rows.sort(key=lambda r:('关键论文与可行性核查_2026-11-04\\论文全文' not in r['path'],r['path']))
cache_path=OUT/'data/pdf_catalog.json'
cached={r['sha256']:r for r in json.loads(cache_path.read_text(encoding='utf-8'))} if cache_path.exists() else {}
spec=importlib.util.spec_from_file_location('ars_pdf_preflight',r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py')
sys.path.insert(0,str(Path(spec.origin).parent))
preflight=importlib.util.module_from_spec(spec);sys.modules[spec.name]=preflight;spec.loader.exec_module(preflight)
sources=[];seen={}
for row in rows:
 if row['extension']!='.pdf':continue
 path=Path(row['path']);sha=row['sha256']
 if sha in seen:
  sources[seen[sha]]['duplicate_paths'].append(str(path));continue
 r={'id':f'PDF{len(sources)+1:03d}','path':str(path),'sha256':sha,'duplicate_paths':[],'extraction_status':'未提取','review_status':'待核验'}
 core=path.parent.name=='论文全文' and path.parent.parent.name=='关键论文与可行性核查_2026-11-04'
 if not core and sha in cached:
  r.update({k:v for k,v in cached[sha].items() if k not in {'id','path','duplicate_paths','paper_id','extract_path'}})
  seen[sha]=len(sources);sources.append(r);continue
 try:
  d=PdfReader(path,strict=False);r['pages']=len(d.pages);r['title_metadata']=str((d.metadata or {}).get('/Title',''))
  text=d.pages[0].extract_text() or '';r['first_page']=text;r['arxiv_ids']=list(dict.fromkeys(re.findall(r'\b\d{4}\.\d{4,5}(?:v\d+)?\b',text)))
  r['doi_candidates']=list(dict.fromkeys(re.findall(r'10\.\d{4,9}/[^\s<>]+',text)))
  r['extraction_status']='首页已机器提取'
  if core:
   r['paper_id']=path.name.split('_')[0];full=[];blank=[]
   for i,p in enumerate(d.pages):
    t=p.extract_text() or '';full.append({'physical_page':i+1,'text':t})
    if len(t.strip())<50:blank.append(i+1)
   target=OUT/'data/pdf_extracts'/f"{r['paper_id']}.json"
   target.write_text(json.dumps(full,ensure_ascii=False,indent=2),encoding='utf-8')
   r['extraction_status']='全文已机器提取';r['extract_path']=str(target);r['sparse_text_pages']=blank
   r['integrity']='pypdf页树枚举成功；页面语义与版式待按引用核读'
   r['preflight']=preflight.run_preflight(path)
 except Exception as e:r['error']=str(e)
 seen[sha]=len(sources);sources.append(r)
(OUT/'data/pdf_catalog.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
for key,p in [('latest1',ROOT/'探索进展与创新方向_2026-11-09/AI智能体授权研究探索进展与创新方向_2026-11-09.docx'),('latest2',ROOT/'研究成果总报告_2026-11-08/AI智能体授权与凭证管理研究历程及成果总报告_2026-11-08.docx')]:
 d=Document(p);lines=[];i=0
 for e in d.element.body:
  if e.tag==qn('w:p'):
   i+=1;pp=Paragraph(e,d);lines.append(f'P{i:04d} [{pp.style.name}] {pp.text}')
  elif e.tag==qn('w:tbl'):
   lines.append('[TABLE]');lines.extend(' | '.join(c.text.replace('\n',' / ') for c in r.cells) for r in Table(e,d).rows);lines.append('[/TABLE]')
 (OUT/'working'/f'{key}_blocks.txt').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'unique_pdf_bytes':len(sources),'pdf_copies':sum(len(s['duplicate_paths']) for s in sources),'core_papers':sum('paper_id' in s for s in sources),'core_pages':sum(s.get('pages',0) for s in sources if 'paper_id' in s),'failures':[{'path':s['path'],'error':s['error']} for s in sources if 'error'in s]},ensure_ascii=False,indent=2))
