from pathlib import Path
import json,re,hashlib
from docx import Document
from docx.shared import Pt,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(r'D:\毕业设计')
TASK=ROOT/'研究'/'研究空白与创新融合_2026-11-02'
WORK=TASK/'工作文件'
BASE=ROOT/'硕士研究深化增补_AI数字主体与密码管理器_v2.14_系统调研增强版.docx'
OUT=ROOT/'硕士研究深化增补_AI数字主体与密码管理器_v2.15_研究空白与创新融合版.docx'
source_hash=hashlib.sha256(BASE.read_bytes()).hexdigest()
doc=Document(BASE)
sources=json.loads((WORK/'new_sources.json').read_text(encoding='utf-8'))
for s in sources:
    if s['id']=='G18':s['authors']='Fan Zhang et al.'

def para(text='',style='Research Body'):
    return doc.add_paragraph(text,style)
def after(p,text):
    n=para(text,'Research Note');p._p.addnext(n._p)
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F2F5F7');n._p.get_or_add_pPr().append(shade)

ps=list(doc.paragraphs)
ps[0].text='认证契约获取与凭据生命周期配置'
ps[1].text='硕士研究深化增补 v2.15'
ps[2].text='研究空白挖掘与创新候选融合版'
ps[4].text='本版以v2.14及其保留的v2.13主体为基础，审查新对话中的A至E路线。建议优先检验A认证契约安全获取与B生命周期约束凭据配置，保留原安全执行和恢复后端，CS03作为有明确隐私需求时的密码学支撑。此为候选重构，未认定原创性或正式冻结选题。'
ps[5].text='新增重点是7类研究缺口、8项潜在设计缺陷、统一的观察条件策略规约，以及A1、B1、AB1三张可证伪贡献卡。查新已确认：无reset学习、安全屏障及动态账户策略均有先例；可能增量须落到核验副作用、后续处置可实现性和配置驱动的补证方法。'
ps[6].text='本轮新增18项公开来源登记和有限构造性检查：16453个终止需求族的分区枚举与小型策略反例。它们不代表真实网站、AI任务或完整协议实验。v2.13及CS03的旧结果仍按原稿报告登记，原算法附件缺失的边界不变。'
ps[8].text='建议先读第21至27章的空白审计、形式化修正、方法候选与实施合并；第28章列本轮证据和G01至G18来源。前20部分保留既有技术依据与N01至N37文献，在相关章节加入本版衔接说明。历史定位与当前候选方向分别标注，避免把新目标倒填成已实现能力。'
ps[9].text='本地来源　L1为v2.13；L2为CS03；L3为v2.14及其研究目录材料；L4为本轮粘贴对话；F215为本轮有限构造性检查。所有原文件保持原样。'

# Surgical integration into the previous research frame.
for p in ps:
    if p.text.startswith('研究一仍为“可检查身份策略”'):
        p.text='v2.14以“可检查身份策略”和“安全核验与恢复”为两项研究。v2.15在保留其执行基础的前提下，提出上游A认证契约安全获取、B生命周期约束配置的候选重构；A补足可信输入的获取，B选择首次委托前的关系与方式，原后端执行关闭和恢复。历史隐私仍是有条件的密码学支撑。详见第21至27章。[L1][L2][L4]'
    elif p.text.startswith('本研究面向AI代理通过密码管理器使用多类账户凭据的场景'):
        p.text='以下保留v2.14的研究定位作为技术依据：本研究面向AI代理通过密码管理器使用多类账户凭据，研究可检查操作契约及撤回、并发、结果未知和恢复中的条件性安全。v2.15进一步将“可信契约从何而来”和“初始配置怎样保留未来控制能力”列为候选方法问题，当前选题建议以第27.4节为准。[L1][L4]'
    elif p.text.startswith('本轮使用AI辅助资料检索、来源核对、综合分析和文档修订'):
        p.text=p.text.replace('本轮','v2.14阶段',1)
    elif p.text.startswith('本版保留原稿关于14个开发案例'):
        p.text=p.text.replace('本版','v2.14',1).replace('此次新增工作','该阶段新增工作')
    elif p.text.startswith('以下N01至N37是本版新增登记'):
        p.text='以下N01至N37为v2.14登记并在本版保留；本轮新增G01至G18见第28章。R1至R7沿用原始链接。L1为v2.13，L2为CS03，L3为v2.14及其研究目录材料；D212、E213仅代表原稿所述历史来源与实验记录，仍未取得对应完整包。'
    elif p.text.startswith('本次以v2.13的“可检查身份策略”'):
        p.text=p.text.replace('本次以','v2.14调研以',1)
    elif p.text.startswith('v2.14增补　最新近邻包括'):
        after(p,'v2.15衔接　新增G01至G18对A/B做反向查新：无reset学习、性质导向学习、安全屏障及动态账户图已有先例。第21至26章收缩宽泛创新表述。')
    elif p.text.startswith('## '):
        pass
    elif p.text.startswith('建议统一一个版本化操作契约'):
        after(p,'v2.15衔接　契约增加证据作用域、仍相容模型、失效条件与未决义务；它记录可相信的事实，不创建用户授权。见第23至24章。')
    elif p.text.startswith('建议将研究主张'):
        pass

def add_table(rows):
    t=doc.add_table(rows=1,cols=len(rows[0]));t.autofit=False
    widths={3:[3.2,6.2,7.6],4:[3.4,4.5,3.8,5.3]}[len(rows[0])]
    for i,w in enumerate(widths):t.columns[i].width=Cm(w)
    for i,x in enumerate(rows[0]):t.rows[0].cells[i].text=x
    for rr in rows[1:]:
        for c,x in zip(t.add_row().cells,rr):c.text=x
    for j,row in enumerate(t.rows):
        ns=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(ns)
        if j==0:row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for i,c in enumerate(row.cells):
            c.width=Cm(widths[i]);pr=c._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DDE7ED' if j==0 else ('F5F7F8' if j%2==0 else 'FFFFFF'));pr.append(shade)
            mar=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'80');e.set(qn('w:type'),'dxa');mar.append(e)
            pr.append(mar)
            for p in c.paragraphs:
                p.style=doc.styles['Research Table']
                if j==0:
                    p.paragraph_format.keep_with_next=True
                    for r in p.runs:r.bold=True
    para('')

def mr(text):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
def sub(a,b):
    e=OxmlElement('m:sSub');base=OxmlElement('m:e');base.append(mr(a));s=OxmlElement('m:sub');s.append(mr(b));e.extend([base,s]);return e
def sup(a,b):
    e=OxmlElement('m:sSup');base=OxmlElement('m:e');base.append(mr(a));s=OxmlElement('m:sup');s.append(mr(b));e.extend([base,s]);return e
def eq(parts):
    p=para();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;o=OxmlElement('m:oMath');op=OxmlElement('m:oMathPara')
    for e in parts:o.append(mr(e) if isinstance(e,str) else e)
    op.append(o);p._p.append(op)
def equation(name):
    if name=='knowledge':eq([sub('K','h'),' ⊆ {(m,s) : m ∈ M, s ∈ ',sub('S','m'),'} ,   z = (',sub('K','h'),', b, O, g)'])
    if name=='admissible':
        eq(['Admit(a,z) ⇒ ∀(m,s) ∈ ',sub('K','h'),': Allowed(a,m,s,b)'])
        eq(['Admit(a,z) ⇒ ∀o ∈ Obs(',sub('K','h'),',a): Post(z,a,o) ∈ W'])
    if name=='uniform':
        eq(['∀S ∈ F, ∃',sub('π','S'),', ',sub('ρ','S'),' ∈ ObsPolicy, ∀(m,s) ∈ ',sub('K','h'),','])
        eq(['∀τ ∈ Runs(m,s,x,',sub('π','S'),'): Goal(S,x,τ,',sub('ρ','S'),')'])
    if name=='signature':
        eq([sub('σ','F'),'(i) = ',sub('(1[i ∈ S])','S ∈ F')])
        eq([sup('k','*'),' = |{',sub('σ','F'),'(i) : i ∈ Tasks}|'])

def hyperlink(p,label,url):
    rid=p.part.relate_to(url,RT.HYPERLINK,is_external=True);h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rid);r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    color=OxmlElement('w:color');color.set(qn('w:val'),'245B78');pr.append(color);u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u);r.append(pr);t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)

def refs():
    for s in sources:
        p=para(f"[{s['id']}] {s['authors']}. {s['title']}. {s['year']}. {s['venue']}.",'Research Small');p.paragraph_format.keep_with_next=True
        p=para('','Research Small');p.paragraph_format.keep_with_next=True;hyperlink(p,'原文或官方入口',s['url'])
        if s.get('doi'):p.add_run('　DOI: '+s['doi'])
        if s.get('extra_url'):p.add_run('　');hyperlink(p,'机构研究摘要',s['extra_url'])
        if s.get('code'):p.add_run('　');hyperlink(p,'官方实现入口',s['code'])
        p=para('读取范围：'+s['read']+'。','Research Small');p.paragraph_format.keep_with_next=True
        p=para('贡献边界：'+s['boundary']+'　访问日期：2026-11-02。','Research Small');p.paragraph_format.space_after=Pt(8)

lines=(WORK/'gap_content.txt').read_text(encoding='utf-8').splitlines();i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
        add_table(rows);continue
    if line.startswith('# '):
        p=para(line[2:],'Research H1')
        if line.startswith('# 21 '):p.paragraph_format.page_break_before=True
    elif line.startswith('## '):para(line[3:],'Research H2')
    elif line.startswith('{EQ '):equation(line[4:-1])
    elif line=='{GREFERENCES}':refs()
    else:para(line)
    i+=1
for sec in doc.sections:
    for p in sec.header.paragraphs:
        for r in p.runs:r.text=r.text.replace('v2.14研究增补','v2.15研究增补')
doc.core_properties.title='认证契约获取与凭据生命周期配置 v2.15'
doc.core_properties.subject='研究空白挖掘 创新候选 与当前进展合并'
doc.core_properties.comments='候选研究重构，未确认首次性；有限构造性检查不等于真实服务实验。'
doc.save(OUT)
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==source_hash
ledger={'date':'2026-11-02','base_sha256':source_hash,'base_document':str(BASE),'output_document':str(OUT),'pasted_dialogue':r'C:\Users\a1887\.codex\attachments\e241c1b2-a824-4edb-bc36-4c83387df36f\已粘贴的文本.txt','new_sources':sources,'finite_checks':json.loads((WORK/'finite_examples.json').read_text(encoding='utf-8')),'claims':{'A1':'CANDIDATE','B1':'CANDIDATE','AB1':'CANDIDATE'},'novelty_confirmed':False,'live_service_experiment':False}
(TASK/'研究空白与来源核验台账.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
bib=[]
for s in sources:
    a=s['authors'].replace('; ',' and ').replace(' et al.',' and others')
    fields={'author':a,'title':s['title'],'year':re.search(r'\d{4}',s['year']).group(),'url':s['url'],'note':s['venue']+'; accessed 2026-11-02; '+s['read']}
    if s.get('doi'):fields['doi']=s['doi']
    bib.append('@misc{'+s['id']+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}')
(TASK/'本轮新增参考文献.bib').write_text('\n\n'.join(bib),encoding='utf-8')
print(json.dumps({'output':str(OUT),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),'new_sources':len(sources),'equations':len(doc.element.xpath('.//m:oMath'))},ensure_ascii=False))
