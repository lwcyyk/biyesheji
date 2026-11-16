from pathlib import Path
import json
import pypdfium2 as pdfium
BASE=Path(__file__).resolve().parent
out=BASE/'qa_final';out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(BASE/'report_qa.pdf'));rows=[]
for i,page in enumerate(pdf):
 im=page.render(scale=1.6).to_pil();path=out/f'page-{i+1:02}.png';im.save(path)
 text=page.get_textpage().get_text_range();(out/f'page-{i+1:02}.txt').write_text(text,encoding='utf-8')
 rows.append({'page':i+1,'characters':len(text),'image':str(path)})
(out/'pages.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Pages:',len(rows));print('Characters per page:',[x['characters'] for x in rows])
