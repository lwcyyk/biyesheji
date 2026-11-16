from pathlib import Path
import json
import pypdfium2 as pdfium
from PIL import Image,ImageOps,ImageDraw
base=Path('D:/毕业设计/研究成果总报告_2026-11-08/_build')
out=base/'pages';out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(base/'report_qa.pdf')
data=[]
for i,p in enumerate(pdf):
    im=p.render(scale=1.65).to_pil().convert('RGB')
    im.save(out/f'page-{i+1:02}.png')
    tx=p.get_textpage().get_text_range()
    data.append({'page':i+1,'text':tx,'characters':len(tx)})
(base/'page_text.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for start in range(0,len(pdf),9):
    sheet=Image.new('RGB',(900,1320),'#dddddd');draw=ImageDraw.Draw(sheet)
    for j in range(start,min(start+9,len(pdf))):
        im=Image.open(out/f'page-{j+1:02}.png');im.thumbnail((290,402))
        x=(j-start)%3*300+(300-im.width)//2;y=(j-start)//3*440+24
        sheet.paste(im,(x,y));draw.text((x,y-17),str(j+1),fill='black')
    sheet.save(out/f'overview-{start//9+1}.png')
print('pages',len(pdf))
for d in data:
    lines=[x for x in d['text'].splitlines() if x.strip()]
    print(d['page'],d['characters'],' | '.join(lines[:3]),' LAST ', ' | '.join(lines[-3:])[:120])
