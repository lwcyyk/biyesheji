from pathlib import Path
import hashlib
import json
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from content import SECTIONS, SOURCES

ROOT=Path('D:/毕业设计')
SOURCE_ROOT=ROOT/'research_main_innovation/main_topic_selection'
OUTPUT=ROOT/'探索进展与创新方向_2026-11-09'
DEST=OUTPUT/'AI智能体授权研究探索进展与创新方向_2026-11-09.docx'
source_records=[]
source_ids={}

def register(key):
    if key not in source_ids:
        title,relative=SOURCES[key]
        path=ROOT/relative[6:] if relative.startswith('@root/') else SOURCE_ROOT/relative
        raw=path.read_bytes()
        sid=f'S{len(source_records)+1:02d}'
        source_ids[key]=sid
        source_records.append({'id':sid,'title':title,'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)})
    return source_ids[key]

def resolve(text):
    return re.sub(r'\{ref:([^}]+)\}',lambda m:'['+register(m.group(1))+']',text)

doc=Document()
section=doc.sections[0]
section.page_height=Cm(29.7)
section.page_width=Cm(21)
section.top_margin=Cm(2.3)
section.bottom_margin=Cm(2.2)
section.left_margin=Cm(2.35)
section.right_margin=Cm(2.35)
section.header_distance=Cm(1.0)
section.footer_distance=Cm(1.0)

for style in doc.styles:
    for border in list(style.element.findall('.//'+qn('w:pBdr'))):
        border.getparent().remove(border)
    if style.type in (1,2):
        style.font.name='Calibri'
        style.font.color.rgb=RGBColor(0,0,0)
        props=style.element.get_or_add_rPr()
        fonts=props.find(qn('w:rFonts'))
        if fonts is None:
            fonts=OxmlElement('w:rFonts')
            props.insert(0,fonts)
        fonts.set(qn('w:eastAsia'),'宋体')
        for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
            fonts.attrib.pop(qn('w:'+key),None)

normal=doc.styles['Normal']
normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.3
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name,size,before,after in [('Title',25,0,14),('Subtitle',15,0,12),('Heading 1',18,17,10),('Heading 2',13,13,7),('TOC Heading',18,0,12)]:
    style=doc.styles[name]
    style.font.size=Pt(size)
    style.font.bold=name!='Subtitle'
    style.font.italic=False
    style.paragraph_format.space_before=Pt(before)
    style.paragraph_format.space_after=Pt(after)
    style.paragraph_format.keep_with_next=True
    style.element.get_or_add_rPr().find(qn('w:rFonts')).set(qn('w:eastAsia'),'黑体')
for name in ['Header','Footer']:
    doc.styles[name].font.size=Pt(9)
header=section.header.paragraphs[0]
header.text='AI智能体授权研究  探索进展与创新方向'
header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer=section.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
section.different_first_page_header_footer=True

def field(paragraph,instruction,cached=''):
    for field_type in ['begin','separate','end']:
        run=OxmlElement('w:r')
        element=OxmlElement('w:fldChar')
        element.set(qn('w:fldCharType'),field_type)
        run.append(element)
        paragraph._p.append(run)
        if field_type=='begin':
            run=OxmlElement('w:r')
            element=OxmlElement('w:instrText')
            element.set(qn('xml:space'),'preserve')
            element.text=instruction
            run.append(element)
            paragraph._p.append(run)
        elif field_type=='separate':
            paragraph.add_run(cached)

footer.add_run('第 ')
field(footer,' PAGE ','1')
footer.add_run(' 页')

def add_paragraph(text,style=None):
    paragraph=doc.add_paragraph(style=style)
    text=resolve(text)
    position=0
    for match in re.finditer(r'\^([A-Za-z0-9]+)',text):
        paragraph.add_run(text[position:match.start()])
        run=paragraph.add_run(match.group(1))
        run.font.superscript=True
        position=match.end()
    paragraph.add_run(text[position:])
    if text.endswith(('。以下式给出当前界。','定义。')):
        paragraph.paragraph_format.keep_with_next=True
    return paragraph

def add_table(rows):
    columns=len(rows[0])
    widths={2:[4.4,11.9],3:[3.65,6.5,6.15]}[columns]
    table=doc.add_table(rows=0,cols=columns)
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    table.autofit=False
    for column,width in zip(table.columns,widths):
        column.width=Cm(width)
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        border=OxmlElement('w:'+side)
        for attr,value in [('val','single'),('sz','4'),('color','D9D9D9')]:
            border.set(qn('w:'+attr),value)
        borders.append(border)
    table._tbl.tblPr.append(borders)
    for index,values in enumerate(rows):
        row=table.add_row()
        row_props=row._tr.get_or_add_trPr()
        row_props.append(OxmlElement('w:cantSplit'))
        if index==0:
            row_props.append(OxmlElement('w:tblHeader'))
        for cell,text,width in zip(row.cells,values,widths):
            cell.width=Cm(width)
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props=cell._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for side,value in [('top',95),('bottom',95),('left',115),('right',115)]:
                element=OxmlElement('w:'+side)
                element.set(qn('w:w'),str(value))
                element.set(qn('w:type'),'dxa')
                margins.append(element)
            props.append(margins)
            if index==0:
                shade=OxmlElement('w:shd')
                shade.set(qn('w:fill'),'E7E6E6')
                props.append(shade)
            paragraph=cell.paragraphs[0]
            paragraph.paragraph_format.line_spacing=1.15
            paragraph.paragraph_format.space_after=Pt(0)
            paragraph.paragraph_format.keep_with_next=index==0
            run=paragraph.add_run(resolve(text))
            run.font.size=Pt(9.5)
            run.bold=index==0
    doc.add_paragraph().paragraph_format.space_after=Pt(0)

def math_run(text):
    run=OxmlElement('m:r')
    element=OxmlElement('m:t')
    element.text=text
    run.append(element)
    return run

def math_script(base,value,kind):
    script=OxmlElement('m:s'+kind.title())
    expression=OxmlElement('m:e')
    expression.append(math_run(base))
    part=OxmlElement('m:'+kind)
    part.append(math_run(value))
    script.extend([expression,part])
    return script

def add_equation(key):
    equations={
        'QUERY_BOUND':[math_run('⌈d / '),math_script('K','η','sub'),math_run('⌉ ≤ Q(d,η) ≤ ⌈d / '),math_script('k','η','sub'),math_run('⌉')],
        'QUERY_ORDER':[math_run('Q(d,η) = Θ(1+dη)    0 ≤ η < 1')],
        'T3_BOUND':[math_script('2','O(L log(L+2) + Lr log(Lr+2))','sup'),math_run(' · poly(mn+qL)')],
    }
    paragraph=doc.add_paragraph()
    paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before=Pt(5)
    paragraph.paragraph_format.space_after=Pt(8)
    paragraph.paragraph_format.keep_with_next=True
    container=OxmlElement('m:oMathPara')
    equation=OxmlElement('m:oMath')
    equation.extend(equations[key])
    container.append(equation)
    paragraph._p.append(container)

def add_blocks(body):
    lines=body.splitlines()
    index=0
    paragraph_lines=[]
    def flush():
        if paragraph_lines:
            add_paragraph('\n'.join(paragraph_lines))
            paragraph_lines.clear()
    while index<len(lines):
        line=lines[index].strip()
        if not line:
            flush()
        elif line.startswith('## '):
            flush()
            doc.add_heading(line[3:],2)
        elif line.startswith('@math '):
            flush()
            add_equation(line.split()[1])
        elif line.startswith('|'):
            flush()
            rows=[]
            while index<len(lines) and lines[index].strip().startswith('|'):
                rows.append([item.strip() for item in lines[index].strip().strip('|').split('|')])
                index+=1
            add_table(rows)
            continue
        else:
            paragraph_lines.append(line)
        index+=1
    flush()

def add_link(paragraph,label,path):
    link=OxmlElement('w:hyperlink')
    link.set(qn('r:id'),paragraph.part.relate_to(path.as_uri(),RT.HYPERLINK,is_external=True))
    run=OxmlElement('w:r')
    props=OxmlElement('w:rPr')
    size=OxmlElement('w:sz')
    size.set(qn('w:val'),'18')
    props.append(size)
    color=OxmlElement('w:color')
    color.set(qn('w:val'),'000000')
    props.append(color)
    run.append(props)
    text=OxmlElement('w:t')
    text.text=label.replace('/','/\u200b').replace('_','_\u200b')
    run.append(text)
    link.append(run)
    paragraph._p.append(link)

doc.add_paragraph('AI智能体授权研究',style='Title')
doc.add_paragraph('探索进展与创新方向',style='Subtitle')
doc.add_paragraph('候选命题与未来两年研究计划',style='Subtitle')
add_paragraph('整理日期  2026年11月9日\n展望窗口  2026年11月至2028年11月')
add_paragraph('近期研究形成25项候选方向，并在授权询问、主动撤销隐私和语义保持上取得限定数学进展。本报告将这些结果接到具体用户场景、潜在主贡献、强基线和两年工作责任。')
doc.add_heading('阅读入口',2)
add_paragraph('了解当前进度可先读第1章。\n比较创新方向可读第3至8章的25项方向卡。\n核查数学进展可读第9章。\n讨论研究投入可读第10至12章。\n回查依据可使用附录中的原始文稿链接。')
add_paragraph('当前研究采用知情模型辅助文献分析与纸面推导。发表优先权、外部领域复核和实际用户收益按各方向的证据继续核验。')
doc.add_page_break()
doc.add_paragraph('目录',style='TOC Heading')
field(doc.add_paragraph(),' TOC \\o "1-1" \\h \\z \\u ','目录更新后显示')
doc.add_page_break()
for title,body in SECTIONS:
    doc.add_heading(title,1)
    add_blocks(body)

doc.add_page_break()
doc.add_heading('附录 研究来源与回查入口',1)
add_paragraph('编号对应正文引用。下列资料记录了实际取得的论文、规范、产品文档、核读范围和纸面推导。原文URL、版本与页码可在各目录的来源记录中继续回查。T表示D:/毕业设计/research_main_innovation/main_topic_selection，R表示D:/毕业设计。')
for record in source_records:
    paragraph=doc.add_paragraph()
    paragraph.paragraph_format.keep_with_next=True
    paragraph.paragraph_format.space_after=Pt(3)
    run=paragraph.add_run('['+record['id']+'] '+record['title'])
    run.bold=True
    run.font.size=Pt(10)
    path=Path(record['path'])
    label='T/'+str(path.relative_to(SOURCE_ROOT)).replace('\\','/') if path.is_relative_to(SOURCE_ROOT) else 'R/'+str(path.relative_to(ROOT)).replace('\\','/')
    paragraph=doc.add_paragraph()
    paragraph.paragraph_format.keep_with_next=True
    paragraph.paragraph_format.space_after=Pt(2)
    add_link(paragraph,label,path)
    paragraph=doc.add_paragraph('SHA256 '+record['sha256'][:16]+'…')
    paragraph.paragraph_format.space_after=Pt(9)
    for run in paragraph.runs:
        run.font.size=Pt(8)

doc.core_properties.title='AI智能体授权研究探索进展与创新方向'
doc.core_properties.subject='25项候选方向的研究进展 潜在贡献与两年计划'
doc.core_properties.author='研究者与模型辅助整理'
doc.core_properties.keywords='AI智能体 授权 隐私 研究进展 创新方向'
doc.save(DEST)
(OUTPUT/'_build/source_manifest.json').write_text(json.dumps(source_records,ensure_ascii=False,indent=2),encoding='utf-8')
full='\n'.join(paragraph.text for paragraph in doc.paragraphs)
assert '{ref:' not in full
assert '不是' not in full and '而是' not in full
assert '；' not in full and ';' not in full
assert '：' not in full
summary={'output':str(DEST),'chapters':len(SECTIONS),'candidate_directions':25,'source_count':len(source_records),'paragraph_characters':len(full),'tables':len(doc.tables)}
(OUTPUT/'_build/build_check.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
