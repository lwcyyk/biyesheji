import bootstrap
import json
import pypdfium2 as pdfium
from pypdf import PdfReader
def main():
    p=bootstrap.ROOT/'qa/report.pdf';doc=pdfium.PdfDocument(str(p));texts=PdfReader(p)
    rows=[]
    for i,page in enumerate(doc):
        image=page.render(scale=1.5).to_pil();out=p.parent/f'page-{i+1:02d}.png';image.save(out)
        text=texts.pages[i].extract_text() or '';rows.append({'page':i+1,'text_characters':len(text),'last_lines':text.splitlines()[-4:]})
    (p.parent/'render_log.json').write_text(json.dumps({'pages':len(doc),'renderer':'fresh hidden Word COM read-only PDF export + PDFium 108dpi','bundled_renderer':'FAILED: soffice.exe unavailable; no user LibreOffice used','pages_data':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    print('pages',len(doc));print(json.dumps(rows,ensure_ascii=False))
if __name__=='__main__':main()
