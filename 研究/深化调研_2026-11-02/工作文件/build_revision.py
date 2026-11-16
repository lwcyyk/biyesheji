from pathlib import Path
from copy import deepcopy
import json,re,hashlib
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(r'D:\毕业设计')
WORK=ROOT/'研究'/'深化调研_2026-11-02'/'工作文件'
OUT=ROOT/'硕士研究深化增补_AI数字主体与密码管理器_v2.14_系统调研增强版.docx'
sources=json.loads((WORK/'sources.json').read_text(encoding='utf-8'))
doc=Document(ROOT/'硕士研究深化增补_AI数字主体与密码管理器_v2.13.docx')
oldparas=list(doc.paragraphs)

def font_style(s,font='宋体',size=11,bold=False):
    s.font.name='Times New Roman';s.font.size=Pt(size);s.font.bold=bold;s.font.color.rgb=RGBColor(0,0,0)
    s.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),font)

for name,size,font,bold in [('Research Body',11,'宋体',False),('Research H1',16,'黑体',True),('Research H2',12,'黑体',True),('Research Title',23,'黑体',True),('Research Small',9,'宋体',False),('Research Note',10,'宋体',False),('Research Table',10,'宋体',False)]:
    s=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    s.base_style=doc.styles['Normal'];font_style(s,font,size,bold)
    pf=s.paragraph_format;pf.space_after=Pt(6);pf.line_spacing=1.35
    if name in ['Research H1','Research H2','Research Title']:
        pf.keep_with_next=True;pf.space_before=Pt(10);pf.space_after=Pt(9)
    if name=='Research H1':
        pf.page_break_before=False
        lvl=OxmlElement('w:outlineLvl');lvl.set(qn('w:val'),'0');s.element.get_or_add_pPr().append(lvl)
    if name=='Research H2':
        lvl=OxmlElement('w:outlineLvl');lvl.set(qn('w:val'),'1');s.element.get_or_add_pPr().append(lvl)
    if name=='Research Note':
        pf.space_before=Pt(5);pf.space_after=Pt(7)
    if name in ['Research Small','Research Table']:
        pf.line_spacing=1.15;pf.space_after=Pt(3)

def para(text='',style='Research Body'):
    p=doc.add_paragraph(text,style);return p

def link(p,label,url):
    rid=p.part.relate_to(url,RT.HYPERLINK,is_external=True)
    el=OxmlElement('w:hyperlink');el.set(qn('r:id'),rid)
    r=OxmlElement('w:r');rp=OxmlElement('w:rPr')
    c=OxmlElement('w:color');c.set(qn('w:val'),'245B78');rp.append(c)
    u=OxmlElement('w:u');u.set(qn('w:val'),'single');rp.append(u);r.append(rp)
    t=OxmlElement('w:t');t.text=label;r.append(t);el.append(r);p._p.append(el)

def note_after(p,text):
    n=para('v2.14增补　'+text,'Research Note');p._p.addnext(n._p)
    pp=n._p.get_or_add_pPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F2F5F7');pp.append(shade)

# Retain the v2.13 technical narrative and evidence tables, and make provenance explicit.
for p in oldparas:
    for r in p.runs:
        r.text=r.text.replace('本轮','v2.13阶段').replace('v2.13阶段阶段','v2.13阶段')
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:r.text=r.text.replace('本轮','v2.13阶段')
oldparas[3].text='以下主体保留v2.13的两项研究和方法叙述；其v2.12基线与代码来源为原稿记载。用户决定目标与授权，AI组织活动，密码管理器提供账户身份与凭据基础。v2.14新增调研、接口优化与实验规约见第11至20章。[L1]'
oldparas[8].text='来源说明：[D212]与[E213]为v2.13原稿的历史材料与运行记录，本轮未取得对应完整实验包；[R1]至[R7]沿用原公开来源；[N01]至[N37]为本版新增来源。文献报告、条件分析、研究提案和实际运行不得互相替代。'
oldparas[98].text='[E213] 原稿登记hand​off.py、run_v213.py、14个继承源码、run1/run2、回归结果及哈希清单。本次在当前文件夹和研究.zip中未找到对应完整包，故保留为原稿报告，未作本轮复现。'
oldparas[98].text=oldparas[98].text.replace('\u200b','')
notes={
14:'最新近邻包括SUDP v4、Progent v3、FORGE v4和CapLease。秘密托管、扩权检查及持久授权预算分别已有先例；具体版本及能力映射见第12章。[N02–N05]',
24:'同账户不等于同权限，不同token不等于独立授权。替代路径的政策相关依赖需要服务证据或可信登记；信息不足时应报告独立性未建立。见第15章。[R1][R4]',
34:'建议将批准事件、任务代次、执行预算和凭据版本纳入统一契约；这是领域接口优化提案，不能倒填为v2.13已实现的功能。见第15至16章。[N04][N05]',
45:'恢复状态需分成持久授权账本、可恢复见证、可重随机化预计算和一次性掩码。CS03历史隐私方向作为研究二的密码学子问题，适用条件见第14至16章。[L2]',
59:'补充的预算不增生P5和状态分类一致P6均为待验证目标。系统并发安全、完整转录隐私与远端效果唯一性使用不同证明条件。见第16章。[N05][L2]',
73:'本版未新增上述缺项的实现或实验。加密备份完整性也不自动提供防回滚新鲜度；需要独立可信下界。见第15章。[N25]',
81:'主对照须为正确持久工作流，并获得同等凭据、批准、幂等接口和服务增强能力；密码学对照须包括全量新掩码及已有安全预计算。见第18章。[N05][N17]',
102:'本版完成公开来源核验与系统性综合，未改变上述实证边界。候选增量、停止条件和来源台账见第17至20章。'
}
for idx,txt in notes.items():note_after(oldparas[idx],txt)

# Front matter is built using the original document's package and moved to the front.
before=list(doc.element.body)
front=[]
def fp(text,style='Research Body'):
    p=para(text,style);front.append(p._p);return p
font_style(doc.styles['Title'],'黑体',23,True)
for border in doc.styles['Title'].element.xpath('.//w:pBdr'):
    border.getparent().remove(border)
fp('AI 数字主体的凭据交接与恢复安全','Title')
fp('硕士研究深化增补 v2.14','Research H2')
fp('以v2.13为主体的系统性学术调研与密码学优化建议','Research Body')
fp('研究与检索日期　2026年11月2日　Asia/Shanghai','Research Small')
fp('本版保留原有“可检查身份策略”和“安全核验与恢复”两项研究，将密码学参考材料中的历史隐私与受限刷新纳入恢复研究。重点新增近五年论文、规范及开源方案的机制比较，并把已有先例、条件推论、候选贡献和待完成实验分开。')
fp('主要判断是：秘密保管、任务授权、持久消费、撤销生效和证明状态恢复属于不同安全层次。下一步应围绕统一操作契约、真实执行点与可检查恢复状态建立证据；不能用一个“安全密码管理器”标签替代这些条件。')
fp('本轮交付是文献与研究设计增强版。原稿记载的14个开发案例、3处进程退出和CS03运行结果均保留其历史归属；当前目录缺少相应实验包，本轮未重新运行，不新增性能或安全优势结论。')
fp('阅读顺序','Research H2')
fp('前10部分保留v2.13方法主体，并在相关位置加入v2.14说明。第11至14章给出检索方法、发展脉络和技术方案；第15至18章给出接口、证明义务、研究缺口和实验方案；第19章汇总修订，第20章给出37条新增来源与读取范围。')
fp('本地来源　L1为v2.13主文档；L2为CS03；L3为研究目录中的2026年10月16日综合报告与研究点r2修订。原文件保持不变。','Research Small')
p=fp('');p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
for el in front:doc.element.body.remove(el)
for el in reversed(front):doc.element.body.insert(0,el)

def add_table(rows):
    t=doc.add_table(rows=1,cols=len(rows[0]));t.autofit=False
    widths={2:[4.0,13.0],3:[3.2,6.0,7.8],4:[3.4,4.0,6.2,3.4]}[len(rows[0])]
    for i,w in enumerate(widths):t.columns[i].width=Cm(w)
    for i,txt in enumerate(rows[0]):t.rows[0].cells[i].text=txt
    for values in rows[1:]:
        for c,txt in zip(t.add_row().cells,values):c.text=txt
    for j,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();ns=OxmlElement('w:cantSplit');trpr.append(ns)
        if j==0:
            head=OxmlElement('w:tblHeader');trpr.append(head)
        for i,c in enumerate(row.cells):
            c.width=Cm(widths[i]);tcpr=c._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'80');e.set(qn('w:type'),'dxa');margins.append(e)
            tcpr.append(margins)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DDE7ED' if j==0 else ('F5F7F8' if j%2==0 else 'FFFFFF'));tcpr.append(shade)
            for p in c.paragraphs:
                p.style=doc.styles['Research Table']
                if j==0:
                    p.paragraph_format.keep_with_next=True
                    for r in p.runs:r.bold=True
    p=para('');p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1
    return t

def mr(text):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
def sub(a,b):
    e=OxmlElement('m:sSub');base=OxmlElement('m:e');base.append(mr(a));ss=OxmlElement('m:sub');ss.append(mr(b));e.extend([base,ss]);return e
def eq(parts):
    p=para();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    op=OxmlElement('m:oMathPara');o=OxmlElement('m:oMath')
    for part in parts:o.append(mr(part) if isinstance(part,str) else part)
    op.append(o);p._p.append(op)

eqs={
'affine':lambda:eq([sub('V','b'),' = ',sub('t','b'),' + ',sub('M','b'),sub('r','b'),',     ',sub('S','b'),' = im(',sub('M','b'),')']),
'feasibility':lambda:eq(['Δ = ',sub('t','1'),' − ',sub('t','0'),',   D = ',sub('S','0'),' + ',sub('S','1'),' + ⟨Δ⟩,   W = P ∩ D']),
'optimum':lambda:(eq([sub('S','0'),' + W = D  ∧  ',sub('S','1'),' + W = D']),eq([sub('r','min'),' = dim D − min(dim ',sub('S','0'),', dim ',sub('S','1'),')'])),
'prefix':lambda:eq(['TV((',sub('P','0'),', ',sub('F','0'),'), (',sub('P','1'),', ',sub('F','1'),')) ≥ TV(',sub('P','0'),', ',sub('P','1'),')'])
}

def refs():
    for s in sources:
        p=para(f"[{s['id']}] {s['authors']} {s['title']}. {s['year']}. {s['venue']}.",'Research Small')
        p.paragraph_format.keep_with_next=True
        p=para('','Research Small');link(p,'原文或官方入口',s['url'])
        if s.get('doi'):p.add_run('　DOI: '+s['doi'])
        if s.get('code'):
            p.add_run('　');link(p,'实现或项目文档',s['code'])
        if s.get('extra_url'):
            p.add_run('　');link(p,'官方预计算说明',s['extra_url'])
        p=para('类型：'+s['kind']+'。阅读范围：'+s['read']+'。','Research Small')
        p=para('用途与边界：'+s['use']+'　访问日期：2026-11-02。','Research Small')
        p.paragraph_format.space_after=Pt(8)

lines=(WORK/'supplement.txt').read_text(encoding='utf-8').splitlines();i=0
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
        if line.startswith('# 11 ') or line.startswith('# 20 '):p.paragraph_format.page_break_before=True
    elif line.startswith('## '):para(line[3:],'Research H2')
    elif line.startswith('{EQ '):eqs[line[4:-1]]()
    elif line=='{REFERENCES}':refs()
    else:para(line)
    i+=1

# Original A4 geometry is the visual authority. Use restrained formatting for the addendum.
for sec in doc.sections:
    sec.header_distance=Cm(0.8);sec.footer_distance=Cm(0.8)
    for p in sec.header.paragraphs:
        if p.text:p.text='AI数字主体与密码管理器　v2.14研究增补';p.style=doc.styles['Research Small']
    for p in sec.footer.paragraphs:
        for r in p.runs:r.text=r.text.replace('2026-10-29','2026-11-02')
for p in doc.paragraphs:
    if re.match(r'^\d{2} /',p.text):p.paragraph_format.keep_with_next=True
for t in doc.tables:
    for p in t.rows[0].cells[0].paragraphs:p.paragraph_format.keep_with_next=True
    for cell in t.rows[0].cells:
        for p in cell.paragraphs:p.paragraph_format.keep_with_next=True
doc.core_properties.title='AI数字主体的凭据交接与恢复安全 v2.14'
doc.core_properties.subject='以v2.13为主体的系统性学术调研与密码学优化'
doc.core_properties.comments='保留原版本；本轮未进行算法实验复现。'
doc.save(OUT)

ledger={'date':'2026-11-02','timezone':'Asia/Shanghai','focus_window':['2021-11-02','2026-11-02'],'new_sources':sources,'old_public_sources':'v2.13原R1至R7及链接保留于DOCX','local_sources':[str(ROOT/'硕士研究深化增补_AI数字主体与密码管理器_v2.13.docx'),str(ROOT/'CS03_密码学贡献重构与历史隐私刷新_2026-10-23.docx')],'verification_scope':'存在性和所列读取范围核验；不是全篇定理验证或代码复现'}
(ROOT/'研究'/'深化调研_2026-11-02'/'文献核验台账.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
bib=[]
for s in sources:
    bibauthor=s['authors'].replace(' et al.',' and others').replace(', ',' and ').replace('，',' and ')
    fields=[f"  title = {{{s['title']}}}",f"  author = {{{bibauthor}}}",f"  url = {{{s['url']}}}",f"  note = {{{s['venue']}; accessed 2026-11-02; {s['read']}}}"]
    m=re.search(r'\d{4}',s['year'])
    if m:fields.append('  year = {'+m.group()+'}')
    if s.get('doi'):fields.append('  doi = {'+s['doi']+'}')
    bib.append('@misc{'+s['id']+',\n'+',\n'.join(fields)+'\n}')
(ROOT/'研究'/'深化调研_2026-11-02'/'新增参考文献.bib').write_text('\n\n'.join(bib)+'\n',encoding='utf-8')
manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in ledger['local_sources'] for p in [Path(p)]}
manifest[str(OUT)]=hashlib.sha256(OUT.read_bytes()).hexdigest()
(WORK/'sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),'sources':len(sources),'bytes':OUT.stat().st_size},ensure_ascii=False))
