from pathlib import Path
import json, re, sys
from copy import deepcopy
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_论证重构版_v2_2026-11-04.docx'
OUTPUT = ROOT.parent / '面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_写作重构版_2026-11-09.docx'
body = (ROOT / 'report_body.txt').read_text(encoding='utf-8')
body = body.replace('普通工作流和 RPA', '普通工作流和机器人流程自动化（RPA）')
body = body.replace('决策区域判定 DRD', '决策区域判定（Decision Region Determination，DRD）')
body = body.replace('多成本有界 POMDP 研究', '多成本有界部分可观测马尔可夫决策过程（POMDP）研究')
body = body.replace('经 TLS 取得的数据', '经传输层安全协议（TLS）取得的数据')
body = body.replace('离线 JWT 的签名', '离线 JSON Web Token（JWT）的签名')
body = body.replace('SMT 及相同预处理', 'SMT 求解及相同预处理')

refs = {}
for line in (ROOT / 'source_extract.txt').read_text(encoding='utf-8').splitlines():
    m = re.match(r'\[P\] Normal \| \[(R\d{2})\] (.*)', line)
    if m:
        text = m[2]
        url = re.search(r'https?://\S+', text)
        if url:
            refs[m[1]] = {'text': text[:url.start()].strip(), 'url': url[0]}

refs.update({
 'R46': {'text': 'Wang, Q., et al. (2026). Authorization Closure Graph: Minimal Repair for LLM Agents with Evolving User Instructions. arXiv:2609.32428v1，预印本。', 'url': 'https://arxiv.org/abs/2609.32428v1'},
 'R47': {'text': 'Luo, K., Wang, X., Fung, P. H. A., & Lau, W. C. (2026). Demystifying the (In)Security of OAuth-based Account Linking in Connector Ecosystems. IEEE Symposium on Security and Privacy, 2327–2346. DOI 10.1109/SP63933.2026.00128.', 'url': 'https://mobitec.ie.cuhk.edu.hk/connector-oauth-security/'},
 'R48': {'text': 'Murphy, F., & Radomirović, S. (2026). Verifying Account Ecosystems With Graph Transformations. IEEE EuroS&P, 470–490. DOI 10.1109/EuroSP68448.2026.00038.', 'url': 'https://pure.hw.ac.uk/ws/portalfiles/portal/173709309/Verifying_Account_Ecosystems_AAM.pdf'},
 'R49': {'text': 'Zhang, F., Maram, D., Malvai, H., Goldfeder, S., & Juels, A. (2020). DECO: Liberating Web Data Using Decentralized Oracles for TLS. CCS 2020，扩展版 arXiv:1909.00938v4. DOI 10.1145/3372297.3417239.', 'url': 'https://arxiv.org/abs/1909.00938v4'},
 'R50': {'text': 'Xie, X., Yang, K., Wang, X., & Yu, Y. (2024). Lightweight Authentication of Web Data via Garble-Then-Prove. USENIX Security 2024.', 'url': 'https://www.usenix.org/conference/usenixsecurity24/presentation/xie-xiang'},
 'R51': {'text': 'Sheikhalishahi, M., Stork, I., & Zannone, N. (2021). Privacy-preserving policy evaluation in multi-party access control. Journal of Computer Security, 29(6), 613–650. DOI 10.3233/JCS-200007.', 'url': 'https://doi.org/10.3233/JCS-200007'},
 'R52': {'text': 'Deochake, S. (2026). Heartbeat-Bound Hierarchical Credentials: Cryptographic Revocation for AI Agent Swarms. arXiv:2605.20704v1，预印本。', 'url': 'https://arxiv.org/abs/2605.20704v1'},
 'R53': {'text': "Kenney, P., Ahmadi, H., Lusson, D., Nguyen, D., & Gill, G. (2026). API Secrets Should Never Become Tokens in the LLM's Vocabulary: A Threat Analysis of API Credential Handling in LLM Agent Systems and an Empirical Evaluation of a Vault-Mediated Execution Boundary. arXiv:2609.33371，预印本。", 'url': 'https://arxiv.org/abs/2609.33371'},
 'R54': {'text': 'Chen, M., & Su, L. (2026). OAuth 2.0 Agent Authorization Explicit Revocation. draft-chen-oauth-agent-revocation-01，2026-10-30，个人 Internet-Draft，进行中的工作。', 'url': 'https://datatracker.ietf.org/doc/html/draft-chen-oauth-agent-revocation-01'},
 'R55': {'text': 'Asor, R. (2026). Verifiable Attenuated Delegation for AI Agent Chains. draft-asor-wimse-agent-delegation-chain-03，2026-10-27，个人 Internet-Draft，进行中的工作。', 'url': 'https://datatracker.ietf.org/doc/html/draft-asor-wimse-agent-delegation-chain-03'},
})
refs['R07']['text'] = '1Password. (持续更新). Machine and AI Agent Credential Management. 原稿记录页面状态为 public preview，状态日期为 2026-11-04。'
refs['R24']['text'] = 'McGuinness, K. (2026). Mission-Bound Authorization for OAuth 2.0. draft-mcguinness-oauth-mission-02，2026-11-02，个人 Internet-Draft，进行中的工作。'
refs['R31']['text'] = 'Carr, S., Jansen, N., Junges, S., & Topcu, U. (2023). Safe Reinforcement Learning via Shielding under Partial Observability. AAAI. DOI 10.1609/aaai.v37i12.26723. 作者预印本 arXiv:2204.00755v2。'
refs['R31']['url'] = 'https://arxiv.org/abs/2204.00755v2'
for key in ['R20','R37','R39','R40','R41','R45']:
    refs[key]['text'] = refs[key]['text'].replace('本次核对', '原稿定位')
for key in ['R25','R26','R27','R28','R29','R34','R43','R44','R46','R52','R53']:
    match = re.search(r'arXiv:(\d{4}\.\d+)', refs[key]['text'])
    if match:
        refs[key]['text'] += ' DOI 10.48550/arXiv.' + match[1] + '。'

used_refs = sorted(set(re.findall(r'R\d{2}', body)))
assert set(used_refs) <= set(refs), set(used_refs)-set(refs)
assert '不是' not in body and '而是' not in body
assert body.count('@table ') == body.count('@endtable')

doc = Document()
section = doc.sections[0]
source_section = Document(SOURCE).sections[0]
section.page_width, section.page_height = source_section.page_width, source_section.page_height
section.top_margin = Cm(2.25)
section.bottom_margin = Cm(2.15)
section.left_margin = Cm(2.4)
section.right_margin = Cm(2.25)
section.header_distance, section.footer_distance = Cm(1.0), Cm(1.0)
section.different_first_page_header_footer = True
content_width = section.page_width-section.left_margin-section.right_margin
WIDTH_CM = content_width/360000

def font(style, size, east='宋体', bold=False):
    style.font.name = 'Times New Roman'
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0,0,0)
    pr = style.element.get_or_add_rPr()
    rfonts = pr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts=OxmlElement('w:rFonts'); pr.append(rfonts)
    for attr, val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia',east)]:
        rfonts.set(qn('w:'+attr),val)
    for name in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
        rfonts.attrib.pop(qn('w:'+name),None)
    col = pr.find(qn('w:color'))
    if col is not None:
        for attr in ['themeColor','themeTint','themeShade']:
            col.attrib.pop(qn('w:'+attr),None)

font(doc.styles['Normal'],11)
normal=doc.styles['Normal'].paragraph_format
normal.line_spacing=1.32; normal.space_after=Pt(6); normal.first_line_indent=Pt(22)
normal.widow_control=True
font(doc.styles['Title'],23,'黑体',True)
font(doc.styles['Subtitle'],13,'黑体')
doc.styles['Subtitle'].font.italic=False
for s in doc.styles:
    for border in list(s.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
for name,size in [('Heading 1',16),('Heading 2',12.5),('Heading 3',11.5)]:
    s=doc.styles[name]; font(s,size,'黑体',True)
    p=s.paragraph_format; p.first_line_indent=Pt(0); p.space_before=Pt(16 if name=='Heading 1' else 10)
    p.space_after=Pt(8 if name=='Heading 1' else 5); p.keep_with_next=True
font(doc.styles['Caption'],10,'宋体')
cap=doc.styles['Caption'].paragraph_format
cap.first_line_indent=Pt(0); cap.space_before=Pt(7);cap.space_after=Pt(5);cap.keep_with_next=True
for name in ['Header','Footer']:
    font(doc.styles[name],9,'宋体'); doc.styles[name].paragraph_format.first_line_indent=Pt(0)
for stname in ['Reference','TOC Entry','Cover Meta']:
    if stname not in doc.styles:
        doc.styles.add_style(stname,1)
font(doc.styles['Reference'],10,'宋体')
rpf=doc.styles['Reference'].paragraph_format
rpf.first_line_indent=Cm(-0.83);rpf.left_indent=Cm(0.83);rpf.line_spacing=1.12;rpf.space_after=Pt(5)
rpf.keep_together=True
font(doc.styles['TOC Entry'],11,'宋体')
tpf=doc.styles['TOC Entry'].paragraph_format
tpf.first_line_indent=Pt(0);tpf.space_after=Pt(10);tpf.line_spacing=1.15
tpf.tab_stops.add_tab_stop(content_width,WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
font(doc.styles['Cover Meta'],11,'宋体')
doc.styles['Cover Meta'].paragraph_format.first_line_indent=Pt(0)

settings=doc.settings.element
compat=settings.find(qn('w:compat'))
if compat is None: compat=OxmlElement('w:compat');settings.append(compat)
upd=OxmlElement('w:updateFields');upd.set(qn('w:val'),'true');settings.append(upd)

hp=section.header.paragraphs[0]
hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
hp.add_run('AI 智能体认证语义与凭据管理调研报告')
fp=section.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE')
fr=OxmlElement('w:r');ft=OxmlElement('w:t');ft.text='1';fr.append(ft);fld.append(fr);fp._p.append(fld)

bookmark_counter=1
def bookmark(p,name):
    global bookmark_counter
    a=OxmlElement('w:bookmarkStart');a.set(qn('w:id'),str(bookmark_counter));a.set(qn('w:name'),name)
    b=OxmlElement('w:bookmarkEnd');b.set(qn('w:id'),str(bookmark_counter))
    p._p.insert(0,a);p._p.append(b);bookmark_counter+=1

def hyperlink(p,text,target=None,anchor=None,size=None,external=False):
    h=OxmlElement('w:hyperlink')
    if external:
        h.set(qn('r:id'),p.part.relate_to(target,RT.HYPERLINK,is_external=True))
    elif anchor:
        h.set(qn('w:anchor'),anchor)
    r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    fonts=OxmlElement('w:rFonts')
    fonts.set(qn('w:ascii'),'Times New Roman');fonts.set(qn('w:hAnsi'),'Times New Roman');fonts.set(qn('w:eastAsia'),'宋体');pr.append(fonts)
    col=OxmlElement('w:color');col.set(qn('w:val'),'24445B' if external else '000000');pr.append(col)
    if external:
        u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u)
    if size:
        sz=OxmlElement('w:sz');sz.set(qn('w:val'),str(int(size*2)));pr.append(sz)
    r.append(pr);t=OxmlElement('w:t');t.text=text;t.set(qn('xml:space'),'preserve');r.append(t);h.append(r);p._p.append(h)

def rich(p,text):
    pos=0
    for m in re.finditer(r'\[(?:R\d{2}|L\d{2})(?:，(?:R\d{2}|L\d{2}))*\]',text):
        p.add_run(text[pos:m.start()]);p.add_run('[')
        keys=m[0][1:-1].split('，')
        for i,key in enumerate(keys):
            if i:p.add_run('，')
            hyperlink(p,key,anchor=('REF_' if key.startswith('R') else 'LOC_')+key)
        p.add_run(']');pos=m.end()
    p.add_run(text[pos:])

def paragraph(text,style=None):
    follows_table=doc.element.body[-2].tag==qn('w:tbl')
    p=doc.add_paragraph(style=style)
    if follows_table:p.paragraph_format.space_before=Pt(6)
    p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p,text)
    m=re.match(r'\[(L\d{2})\]',text)
    if m:bookmark(p,'LOC_'+m[1])
    return p

def table(caption,lines):
    paragraph(caption,'Caption')
    rows=[[v.strip() for v in l.split('|')] for l in lines]
    n=len(rows[0]); assert all(len(r)==n for r in rows),caption
    widths={2:[3.35,12.95],3:[3.2,5.2,7.9],5:[4.7,3.1,3.1,2.5,2.9]}[n]
    widths=[x/sum(widths)*WIDTH_CM for x in widths]
    t=doc.add_table(rows=0,cols=n);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    pr=t._tbl.tblPr
    layout=OxmlElement('w:tblLayout');layout.set(qn('w:type'),'fixed');pr.append(layout)
    bw=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');bw.append(e)
    pr.append(bw)
    for i,width in enumerate(widths):t.columns[i].width=Cm(width)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        trpr=t.rows[-1]._tr.get_or_add_trPr()
        cant=OxmlElement('w:cantSplit');trpr.append(cant)
        if ri==0:
            repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
        for ci,value in enumerate(row):
            c=cells[ci];c.width=Cm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=c._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for key,val in [('top','90'),('bottom','90'),('left','105'),('right','105')]:
                e=OxmlElement('w:'+key);e.set(qn('w:w'),val);e.set(qn('w:type'),'dxa');margins.append(e)
            tcpr.append(margins)
            fill=OxmlElement('w:shd');fill.set(qn('w:fill'),'E8EDF1' if ri==0 else ('F7F8F9' if ri%2==0 else 'FFFFFF'));tcpr.append(fill)
            p=c.paragraphs[0];p.paragraph_format.first_line_indent=Pt(0)
            p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.2
            if len(rows)<=6 and ri<len(rows)-1:
                p.paragraph_format.keep_with_next=True
            if len(rows)>6 and ri==len(rows)-2:
                p.paragraph_format.keep_with_next=True
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER if ri==0 or (n==5 and ci>0) else WD_ALIGN_PARAGRAPH.LEFT
            r=p.add_run(value);r.font.size=Pt(10.5);r.font.bold=(ri==0)
            if ri==0:r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'黑体') if r._element.get_or_add_rPr().rFonts is not None else None

# Cover uses the reference document's A4 page size and a restrained report layout.
p=doc.add_paragraph();p.paragraph_format.space_after=Pt(48)
p=doc.add_paragraph('面向 AI 智能体的\n认证语义感知与可撤销凭据管理\n调研报告','Title')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.line_spacing=1.4;p.paragraph_format.space_after=Pt(23)
p=doc.add_paragraph('研究现状 关键问题与验证路径','Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0)
for text in ['写作重构版','2026 年 11 月 9 日']:
    p=doc.add_paragraph(text,'Cover Meta');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(10)
p=doc.add_paragraph();p.paragraph_format.space_after=Pt(53)
for text in ['研究对象  双代理任务中的凭据使用与选择性撤销','资料基础  2026 年 11 月 4 日原稿及关键来源复核','报告用途  毕业设计选题与技术方案评估']:
    p=doc.add_paragraph(text,'Cover Meta');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(10)
doc.add_page_break()

parts=body.split('\n\n')
main_headings=[x[2:].strip() for x in parts if x.startswith('# ') and x.strip()!='# 摘要']
heading_ids={h:'SEC_'+str(i+1) for i,h in enumerate(main_headings)}
toc_pages=json.loads((ROOT/'toc_pages.json').read_text(encoding='utf-8')) if (ROOT/'toc_pages.json').exists() else {}

def toc():
    p=doc.add_paragraph('目录','Heading 1')
    p.paragraph_format.space_after=Pt(20)
    for h in main_headings:
        p=doc.add_paragraph(style='TOC Entry')
        hyperlink(p,h,anchor=heading_ids[h]);p.add_run('\t')
        field=OxmlElement('w:fldSimple')
        field.set(qn('w:instr'),'PAGEREF '+heading_ids[h]+' \\h')
        run=OxmlElement('w:r');value=OxmlElement('w:t')
        value.text=str(toc_pages.get(h,'待更新'));run.append(value);field.append(run);p._p.append(field)
    doc.add_page_break()

for part in parts:
    part=part.strip()
    if not part:continue
    if part.startswith('# '):
        title=part[2:].strip()
        if title=='1 研究判断与调研范围':
            doc.add_page_break();toc()
        p=doc.add_paragraph(title,'Heading 1')
        if title in ['附录 B 核心论文与草案索引','参考文献']:
            p.paragraph_format.page_break_before=True
        if title in heading_ids:bookmark(p,heading_ids[title])
    elif part.startswith('## '):
        doc.add_paragraph(part[3:].strip(),'Heading 2')
    elif part.startswith('@table '):
        ls=part.splitlines();assert ls[-1]=='@endtable'
        table(ls[0][7:],ls[1:-1])
    else:
        if re.match(r'\[L\d{2}\]',part):
            p=paragraph(part,'Reference')
            p.alignment=WD_ALIGN_PARAGRAPH.LEFT
        else:
            paragraph(part)

for key in used_refs:
    item=refs[key];text=item['text'].replace('本次核对作者预印本。','作者预印本。')
    p=doc.add_paragraph(style='Reference');bookmark(p,'REF_'+key)
    p.add_run('['+key+'] '+text+' ')
    hyperlink(p,'来源链接',target=item['url'],external=True,size=10)

props=doc.core_properties
props.title='面向 AI 智能体的认证语义感知与可撤销凭据管理调研报告'
props.subject='研究现状、问题定义、贡献边界与验证方案'
props.author='';props.last_modified_by='';props.keywords='AI 智能体 凭据管理 认证语义 选择性撤销 安全补证'
props.comments='依据指定原稿重构；不含新候选机制实现。'
doc.save(OUTPUT)
(ROOT/'headings.json').write_text(json.dumps(main_headings,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'reference_map.json').write_text(json.dumps({k:refs[k] for k in used_refs},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUTPUT),'characters':len(body),'references':len(used_refs),'tables':len(doc.tables),'headings':len(main_headings)},ensure_ascii=False))
