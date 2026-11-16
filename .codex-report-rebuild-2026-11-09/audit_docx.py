from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from docx import Document
import re,json,hashlib
root=Path(__file__).resolve().parent
f=root.parent/'面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_写作重构版_2026-11-09.docx'
z=ZipFile(f)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
x=E.fromstring(z.read('word/document.xml'))
styles=E.fromstring(z.read('word/styles.xml'))
anchors=set(x.xpath('//w:hyperlink/@w:anchor',namespaces=ns))
book=set(x.xpath('//w:bookmarkStart/@w:name',namespaces=ns))
t=''.join(x.xpath('//w:t/text()',namespaces=ns))
defs=set(re.findall(r'\[(R\d{2})\]',t))
assert not anchors-book,anchors-book
assert len(defs)==55
assert not x.xpath('//w:del|//w:ins|//w:commentReference',namespaces=ns)
assert not styles.xpath('//w:style[@w:styleId="Title"]//w:pBdr',namespaces=ns)
assert '待更新' not in t and '不是' not in t and '而是' not in t
assert len(x.xpath('//w:fldSimple[starts-with(@w:instr,"PAGEREF")]',namespaces=ns))==14
assert set(re.findall(r'P(?:0[1-9]|1[0-8])',t))=={f'P{i:02d}' for i in range(1,19)}
d=Document(f)
assert len(d.tables)==10
summary={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
 'tables':len(d.tables),'references':len(defs),'internal_links':len(anchors),
 'bookmarks':len(book),'external_links':len([r for r in d.part.rels.values() if r.is_external]),'checks':'PASS'}
(root/'docx_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
