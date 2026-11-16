from pathlib import Path
import json,hashlib
import pypdfium2 as pdfium
BASE=Path(__file__).resolve().parent;out=BASE/'qa_final';out.mkdir(exist_ok=True)
old=Path('D:/毕业设计/研究/算法机制重构与原创性验证_2026-11-03/working/qa')
pdf=pdfium.PdfDocument(str(BASE/'merged_qa.pdf'));pages=[]
for i,page in enumerate(pdf):
 path=out/f'page-{i+1:02}.png';page.render(scale=1.6).to_pil().save(path)
 text=page.get_textpage().get_text_range();(out/f'page-{i+1:02}.txt').write_text(text,encoding='utf-8')
 ref=old/path.name;identical=ref.exists() and hashlib.sha256(ref.read_bytes()).digest()==hashlib.sha256(path.read_bytes()).digest()
 pages.append({'page':i+1,'characters':len(text),'image':str(path),'identical_to_previously_reviewed_v1_0':identical})
(out/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pages),'unchanged_old_pages':[x['page'] for x in pages if x['identical_to_previously_reviewed_v1_0']],'review_pages':[x['page'] for x in pages if not x['identical_to_previously_reviewed_v1_0']],'characters':[x['characters'] for x in pages]}))
