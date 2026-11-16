from pathlib import Path
import sys, json, re, subprocess
from PIL import Image, ImageOps, ImageDraw, ImageFont
root=Path(__file__).resolve().parent
rd=root/sys.argv[1]
pdf=next(rd.glob('*.pdf'))
from pypdf import PdfReader
pages=[p.extract_text() for p in PdfReader(pdf).pages]
data='\f'.join(pages)
headings=json.loads((root/'headings.json').read_text(encoding='utf-8'))
normal=lambda s:re.sub(r'\s+','',s)
found={}
for i,txt in enumerate(pages):
    if i<3:continue
    for h in headings:
        if h not in found and normal(h) in normal(txt):found[h]=i+1
assert len(found)==len(headings),(found,headings)
old=json.loads((root/'toc_pages.json').read_text(encoding='utf-8'))
(root/'toc_pages.json').write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf-8')
(rd/'page_text.txt').write_text(data,encoding='utf-8')
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',20)
for start in range(1,len(pages)+1,6):
    sheet=Image.new('RGB',(1200,1740),'#DDE0E2')
    draw=ImageDraw.Draw(sheet)
    for offset in range(6):
        n=start+offset
        if n>len(pages):break
        im=Image.open(rd/f'page-{n}.png').convert('RGB')
        im.thumbnail((575,815))
        x=(offset%2)*600+(600-im.width)//2
        y=(offset//2)*580+28
        im.thumbnail((575,540))
        x=(offset%2)*600+(600-im.width)//2
        sheet.paste(im,(x,y))
        draw.text(((offset%2)*600+12,(offset//2)*580+2),str(n),font=font,fill='black')
    sheet.save(rd/f'contact-{start}.png')
summary={'pages':len(pages),'heading_pages':found,'toc_changed':old!=found,'sparse_pages':[i+1 for i,t in enumerate(pages) if len(normal(t))<100],'tail_chars':len(normal(pages[-1]))}
(rd/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
