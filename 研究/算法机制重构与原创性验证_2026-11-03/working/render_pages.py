from pathlib import Path
import json,pypdfium2 as pdfium
BASE=Path(__file__).resolve().parent;out=BASE/'qa';out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(BASE/'report_qa.pdf'));pages=[]
for i,page in enumerate(pdf):
 im=page.render(scale=1.6).to_pil();path=out/f'page-{i+1:02}.png';im.save(path);tx=page.get_textpage().get_text_range();(out/f'page-{i+1:02}.txt').write_text(tx,encoding='utf-8');pages.append({'page':i+1,'characters':len(tx),'path':str(path)})
(out/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8');print('Pages:',len(pages));print([x['characters'] for x in pages])
