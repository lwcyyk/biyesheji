from pathlib import Path
import json
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw

BASE=Path(__file__).resolve().parents[1]
pdfpath=BASE/'工作文件/融合总稿_版面核验.pdf'
out=BASE/'工作文件/版面核验'
out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(pdfpath))
pages=[]
for i,page in enumerate(pdf):
 im=page.render(scale=1.6).to_pil().convert('RGB')
 path=out/f'page-{i+1:02}.png';im.save(path)
 txt=page.get_textpage().get_text_range()
 (out/f'page-{i+1:02}.txt').write_text(txt,encoding='utf-8')
 pages.append({'page':i+1,'width':im.width,'height':im.height,'characters':len(txt),'file':str(path)})
for start in range(0,len(pages),4):
 sheet=Image.new('RGB',(1000,1340),'#E6E6E6');draw=ImageDraw.Draw(sheet)
 for offset,x in enumerate(pages[start:start+4]):
  im=Image.open(x['file']);im.thumbnail((480,620))
  xpos=10+(offset%2)*500;ypos=32+(offset//2)*670
  sheet.paste(im,(xpos,ypos));draw.text((xpos,ypos-22),f"Page {x['page']}",fill='black')
 sheet.save(out/f'sheet-{start//4+1:02}.png')
(out/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pages),'details':pages},ensure_ascii=False))
