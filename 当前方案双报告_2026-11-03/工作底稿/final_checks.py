from pathlib import Path
import csv,json,hashlib,re,zipfile
from lxml import etree
from pypdf import PdfReader
import report_data as d
O=d.OUT;W=d.WORK;R=d.ROOT
index=list(csv.DictReader((O/'资料索引与来源哈希清单.csv').open(encoding='utf-8-sig')))
# Initial preservation receipt is retained unchanged. Project work continued externally;
# the final incremental evidence is verified against the explicitly frozen byte copy.
record=json.loads((W/'本轮原始资料保持核对.json').read_text(encoding='utf-8'))
snapshot=json.loads((W/'增量快照清单.json').read_text(encoding='utf-8'))
checked=0;errors=[]
for x in snapshot['files']:
 p=O/x['snapshot'];checked+=1
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:errors.append(x['path'])
(W/'冻结增量最终保持核对.json').write_text(json.dumps({'cutoff':snapshot['captured_at_utc'],'checked':checked,'matched':checked-len(errors),'mismatches':errors},ensure_ascii=False,indent=2),encoding='utf-8')
assert not errors
# Source needs preserve prior numbering and original text; status note separate.
cross=json.loads((R/'研究/当前与四阶段及密码学融合_2026-11-02/需求与实现映射.json').read_text(encoding='utf-8'))
req=[]
for x in cross['requirements']:
 req.append({'id':x['id'],'original_text':x['original_text'],'source_locator':x['source_locator'],'modules':'/'.join(x['modules']),'interfaces':'/'.join(x['interfaces']),'historical_mapping_status':x['status'],'current_product_acceptance':'NOT_ACCEPTED','audit_interpretation':x['integration_note'],'current_evidence':'参见E01—E21；算法新增原型不自动关闭产品验收'})
with (O/'原需求编号与实现映射.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=req[0]);wr.writeheader();wr.writerows(req)
# Formal artifact structural check
artifacts=[]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
for p in O.glob('*.docx'):
 with zipfile.ZipFile(p) as z:
  root=etree.fromstring(z.read('word/document.xml'));styles=etree.fromstring(z.read('word/styles.xml'))
  text=''.join(root.xpath('//w:t/text()|//m:t/text()',namespaces=ns))
  refs={int(x) for x in re.findall(r'R(\d\d)',text)};evs={int(x) for x in re.findall(r'E(\d\d)',text)}
  artifacts.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'characters':len(text),'equations':len(root.xpath('//m:oMath',namespaces=ns)),'math_fractions':len(root.xpath('//m:f',namespaces=ns)),'math_scripts':len(root.xpath('//m:sSub|//m:sSup|//m:sSubSup',namespaces=ns)),'tables':len(root.xpath('//w:tbl',namespaces=ns)),'images':len(root.xpath('//w:drawing',namespaces=ns)),'invalid_R_ids':sorted(refs-set(range(1,48))),'invalid_E_ids':sorted(evs-set(range(1,42))),'paragraph_borders':len(root.xpath('//w:pBdr',namespaces=ns))+len(styles.xpath('//w:pBdr',namespaces=ns)),'empty_nary_operands':len(root.xpath('//m:nary/m:e[not(.//m:t)]',namespaces=ns))})
  (W/(p.stem+'_最终正文.txt')).write_text(text,encoding='utf-8')
(W/'文档结构检查.json').write_text(json.dumps(artifacts,ensure_ascii=False,indent=2),encoding='utf-8')
# Extract rendered page text as mechanical aid, not substitute for visual inspection.
for name in ['survey','technical']:
 p=W/'qa'/f'{name}.pdf'
 if p.exists():
  reader=PdfReader(p);rows=[]
  for i,page in enumerate(reader.pages,1):
   t=page.extract_text() or '';(W/'qa'/f'{name}-{i:02}.txt').write_text(t,encoding='utf-8');rows.append({'page':i,'characters':len(t),'replacement_chars':t.count('\ufffd')})
  (W/'qa'/f'{name}_text_checks.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'initial_preservation':record,'frozen_increment':{'checked':checked,'mismatches':errors},'documents':artifacts,'requirements':len(req)},ensure_ascii=False,indent=2))

