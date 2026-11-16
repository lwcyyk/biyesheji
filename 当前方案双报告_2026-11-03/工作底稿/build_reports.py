from pathlib import Path
import sys,os,re,json,csv,hashlib,math
from xml.sax.saxutils import escape
from PIL import Image,ImageDraw,ImageFont
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import report_data as data
import survey_text,technical_text
OUT=data.OUT;W=data.WORK;FIG=W/'figures';FIG.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'deps'))
from latex2mathml.converter import convert as latex_convert
from lxml import etree
from math_defs import equations
from late_updates import apply as apply_late_updates
apply_late_updates(data,survey_text.blocks,technical_text.blocks,equations)
MML_XSL=etree.XSLT(etree.parse(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'))
def font(size,bold=False):return ImageFont.truetype(r'C:\Windows\Fonts\msyhbd.ttc' if bold else r'C:\Windows\Fonts\msyh.ttc',size)
def diagram(key,nodes,edges,size=(1400,650),legend=''):
 im=Image.new('RGB',size,'white');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{size[0]}" height="{size[1]}" viewBox="0 0 {size[0]} {size[1]}">','<rect width="100%" height="100%" fill="white"/>']
 # Nodes: id,x,y,w,h,label
 pos={n[0]:n for n in nodes}
 for src,dst,dash in edges:
  _,x,y,w,h,_=pos[src];_,xx,yy,ww,hh,_=pos[dst]
  if key=='architecture' and src=='c' and dst=='x':
   pts=[(895,225),(940,225),(940,552),(880,552)]
   for aa,bb in zip(pts,pts[1:]):
    dist=math.dist(aa,bb);steps=max(1,int(dist/12))
    for kk in range(0,steps,2):dr.line((aa[0]+(bb[0]-aa[0])*kk/steps,aa[1]+(bb[1]-aa[1])*kk/steps,aa[0]+(bb[0]-aa[0])*min(kk+1,steps)/steps,aa[1]+(bb[1]-aa[1])*min(kk+1,steps)/steps),fill='#314957',width=3)
   dr.polygon([(880,552),(893,546),(893,558)],fill='#314957')
   svg.append('<path d="M895 225 L940 225 L940 552 L880 552" fill="none" stroke="#314957" stroke-width="3" stroke-dasharray="10 7"/><polygon points="880,552 893,546 893,558" fill="#314957"/>')
   continue
  if yy>y+h:a=(x+w/2,y+h);b=(xx+ww/2,yy)
  elif xx>x+w:a=(x+w,y+h/2);b=(xx,yy+hh/2)
  elif x>xx+ww:a=(x,y+h/2);b=(xx+ww,yy+hh/2)
  else:a=(x+w/2,y);b=(xx+ww/2,yy+hh)
  if dash:
   dist=math.dist(a,b);steps=max(1,int(dist/12))
   for k in range(0,steps,2):dr.line((a[0]+(b[0]-a[0])*k/steps,a[1]+(b[1]-a[1])*k/steps,a[0]+(b[0]-a[0])*min(k+1,steps)/steps,a[1]+(b[1]-a[1])*min(k+1,steps)/steps),fill='#506778',width=3)
  else:dr.line([a,b],fill='#314957',width=3)
  ang=math.atan2(b[1]-a[1],b[0]-a[0]);tri=[b,(b[0]-13*math.cos(ang-.45),b[1]-13*math.sin(ang-.45)),(b[0]-13*math.cos(ang+.45),b[1]-13*math.sin(ang+.45))]
  dr.polygon(tri,fill='#314957')
  svg.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="#314957" stroke-width="3" fill="none"'+(' stroke-dasharray="10 7"' if dash else '')+'/>')
  svg.append('<polygon points="'+ ' '.join(f'{v[0]},{v[1]}' for v in tri)+'" fill="#314957"/>')
 for _,x,y,w,h,label in nodes:
  dr.rounded_rectangle((x,y,x+w,y+h),radius=9,fill='#f5f7f8',outline='#677783',width=2)
  svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#f5f7f8" stroke="#677783" stroke-width="2"/>')
  lines=label.split('\n');ft=font(27);top=y+(h-36*len(lines))/2
  for j,line in enumerate(lines):
   box=dr.textbbox((0,0),line,font=ft);tx=x+(w-(box[2]-box[0]))/2;ty=top+j*36
   dr.text((tx,ty),line,font=ft,fill='black')
   svg.append(f'<text x="{x+w/2}" y="{ty+28}" text-anchor="middle" font-family="Microsoft YaHei, sans-serif" font-size="27">{escape(line)}</text>')
 if legend:
  dr.text((35,size[1]-48),legend,font=font(23),fill='#333333')
  svg.append(f'<text x="35" y="{size[1]-20}" font-family="Microsoft YaHei,sans-serif" font-size="23">{escape(legend)}</text>')
 svg.append('</svg>');im.save(FIG/(key+'.png'));(FIG/(key+'.svg')).write_text('\n'.join(svg),encoding='utf-8')
diagram('evidence',[
('a',40,40,370,105,'文档提出\n问题与设计意图'),('b',515,40,370,105,'源码实现\n函数与调用关系'),('c',990,40,370,105,'有限运行\n输入·命令·哈希'),
('d',70,270,350,110,'条件数学论证\n前提与量词'),('e',525,270,350,110,'原生保持与组合\n需要独立证据'),('f',980,270,350,110,'贡献与效用判断\n先例·强对照·范围')],[('a','b',True),('b','c',False),('c','e',True),('d','e',True),('e','f',True)],(1400,475),'虚线：需要额外证明或验证，不允许由上一层自动提升。')
diagram('architecture',[
('u',70,30,380,90,'用户 / M03\n批准·撤回'),('i',950,30,380,90,'AI / M04\n业务提案与受限工具'),
('c',505,175,390,100,'M10 协调与状态\n完整产品仍待实现'),
('a',50,330,360,100,'M05 A\n安全契约获取'),('b',520,330,360,100,'M06 B / AB\n配置·反馈'),('k',990,330,360,100,'M07 / M08\n证据解释·独立检查'),
('x',520,500,360,105,'M02 / M09\n凭据与受控执行'),('q',50,500,360,105,'密码学辅助\n拟议诊断接口'),('e',990,500,360,105,'M11 / M12\n展示·独立评价')],[('u','c',False),('i','c',False),('c','a',False),('c','b',False),('c','k',False),('a','b',False),('b','k',False),('c','x',True),('q','k',True),('k','e',True)],(1400,705),'模块责任沿用原编号；实线为有限逻辑关系，虚线为尚待产品化/集成的边界。')
diagram('abflow',[
('s',50,60,320,105,'统一K / 批准 / 预算\n状态·义务·剩余步'),
('b',540,60,320,105,'B条件配置检查\n或静态区域下界'),
('a',1030,60,320,105,'A选择安全核验\n反馈不授予权限'),
('w',1030,285,320,105,'共同W与独立检查\n全部可见后继'),
('e',540,285,320,105,'受控派发 / 观察\n失败与费用保留'),
('p',50,285,320,105,'Post保守合并\n义务·epoch同步')],[('s','b',False),('b','a',False),('a','w',False),('w','e',False),('e','p',False),('p','s',False)],(1400,490),'AB1排序；AB2静态下界；v1.2 AB3已有传递实现，证书scope缺口尚阻塞验收。')
diagram('crypto',[
('r',45,55,350,100,'给定共享密钥与记录\n两条 AES-128-GCM'),
('f',525,55,350,100,'AES / GHASH关系\ntag差与claim差'),
('d',1005,55,350,100,'rowspace2\n历史实际接入'),
('s',45,295,350,100,'seed-repair2\n两故障独立原型'),
('g',525,295,350,100,'秘密支持gate\n合成残差参考'),
('a',1005,295,350,100,'A / B / AB\n尚无辅助调用链')],[('r','f',False),('f','d',False),('f','s',True),('g','d',True),('d','a',True)],(1400,505),'实线：已定位调用；虚线：接口或组合提案，不能挪用旧实验结果。')
diagram('interface',[
('s',40,50,310,110,'来源与上下文\nsource_status'),
('m',545,50,310,110,'公开模型 / 证书\nalgebra_status'),
('g',1050,50,310,110,'输入固定 / gate\nsupport前提'),
('d',545,280,310,110,'限定诊断输出\n接收者与泄漏'),
('a',40,280,310,110,'M07映射观察\nM08重新检查'),
('u',1050,280,310,110,'未知 / 中止 / 拒绝\n保留成本和义务')],[('s','m',True),('m','g',True),('g','d',True),('d','a',True),('g','u',True)],(1400,500),'整个主线桥接仍为拟议；authorizes_execution 固定为 false。')

def setfont(run,size=None,bold=None,east='宋体'):
 run.font.name='Times New Roman'
 run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),east)
 if size:run.font.size=Pt(size)
 if bold is not None:run.bold=bold
 run.font.color.rgb=RGBColor(0,0,0)
def link(par,text,url):
 rel=par.part.relate_to(url,RT.HYPERLINK,is_external=True);el=OxmlElement('w:hyperlink');el.set(qn('r:id'),rel)
 rr=OxmlElement('w:r');pr=OxmlElement('w:rPr');col=OxmlElement('w:color');col.set(qn('w:val'),'1E4057');pr.append(col)
 sz=OxmlElement('w:sz');sz.set(qn('w:val'),'18');pr.append(sz);rr.append(pr);tt=OxmlElement('w:t');tt.text=text;rr.append(tt);el.append(rr);par._p.append(el)
def add_math(doc,text,num,kind,latex_override=None):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(9)
 latex=latex_override or equations[kind][num-1]
 om=MML_XSL(etree.fromstring(latex_convert(latex).encode('utf-8'))).getroot()
 for rr in om.xpath('.//m:r',namespaces={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}):
  pr=OxmlElement('w:rPr');fonts=OxmlElement('w:rFonts');fonts.set(qn('w:ascii'),'Cambria Math');fonts.set(qn('w:hAnsi'),'Cambria Math');fonts.set(qn('w:eastAsia'),'宋体');pr.append(fonts)
  sz=OxmlElement('w:sz');sz.set(qn('w:val'),'20' if len(latex)>165 else '22');pr.append(sz);rr.insert(0,pr)
 p._p.append(om)
 setfont(p.add_run(f'  （{num}）'),9)
def add_table(doc,title,heads,rows):
 cap=doc.add_paragraph(title,'Caption');cap.paragraph_format.keep_with_next=True
 table=doc.add_table(rows=1,cols=len(heads));table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
 total=16.6
 if len(heads)==3:weights=[.19,.38,.43]
 elif len(heads)==4:weights=[.13,.28,.29,.30]
 else:weights=[1/len(heads)]*len(heads)
 for i,head in enumerate(heads):table.rows[0].cells[i].text=head
 for row in rows:
  cells=table.add_row().cells
  for i,x in enumerate(row):cells[i].text=str(x)
 for ri,row in enumerate(table.rows):
  trpr=row._tr.get_or_add_trPr()
  cant=OxmlElement('w:cantSplit');trpr.append(cant)
  if ri==0:
   repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  for ci,cell in enumerate(row.cells):
   cell.width=Cm(total*weights[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcp=cell._tc.get_or_add_tcPr()
   borders=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   tcp.append(borders)
   margin=OxmlElement('w:tcMar')
   for side,val in [('top','70'),('bottom','70'),('left','80'),('right','80')]:
    x=OxmlElement('w:'+side);x.set(qn('w:w'),val);x.set(qn('w:type'),'dxa');margin.append(x)
   tcp.append(margin)
   shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E7EDF1' if ri==0 else 'FFFFFF');tcp.append(shade)
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.15
    if ri==0:p.paragraph_format.keep_with_next=True
    for run in p.runs:setfont(run,9.5,ri==0)
 doc.add_paragraph('来源：本轮依据项目源码、原始结果和所引文献整理。具体范围见正文及证据台账。','SourceNote')
def setup():
 d=Document();sec=d.sections[0];sec.page_height=Cm(29.7);sec.page_width=Cm(21)
 sec.top_margin=Cm(2.15);sec.bottom_margin=Cm(2);sec.left_margin=Cm(2.2);sec.right_margin=Cm(2.2)
 sec.header_distance=Cm(.8);sec.footer_distance=Cm(.8)
 styles=d.styles
 for name,size,east in [('Normal',11,'宋体'),('Title',25,'黑体'),('Subtitle',12,'宋体'),('Heading 1',16,'黑体'),('Heading 2',12.5,'黑体'),('Heading 3',11,'黑体'),('Caption',10,'宋体')]:
  st=styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st.font.italic=False;st.font.underline=False
  st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),east)
  st.paragraph_format.space_after=Pt(7)
  if name.startswith('Heading'):st.paragraph_format.space_before=Pt(14);st.paragraph_format.keep_with_next=True
 styles['Normal'].paragraph_format.line_spacing=1.35
 for name,size in [('SourceNote',8.5),('CodeBlock',9.5),('Reference',9.5)]:
  st=styles.add_style(name,1);st.base_style=styles['Normal'];st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
  st.paragraph_format.line_spacing=1.15;st.paragraph_format.space_after=Pt(5)
 styles['CodeBlock'].font.name='Consolas'
 styles['Reference'].paragraph_format.line_spacing=1.10
 styles['Reference'].paragraph_format.space_after=Pt(3)
 foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
 field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
 d.core_properties.author='';d.core_properties.last_modified_by='';d.core_properties.subject='AI代理认证语义与凭据生命周期研究'
 return d
def create(title,blocks,filename):
 d=setup();p=d.add_paragraph(title,'Title');p.paragraph_format.space_before=Pt(95);p.paragraph_format.space_after=Pt(26)
 d.add_paragraph('面向AI代理的认证语义安全识别与\n可撤销性驱动凭据配置方法研究','Subtitle')
 d.add_paragraph('资料审计与关键来源核验基础上的正式报告')
 d.add_paragraph('2026年11月3日  ·  Asia/Shanghai')
 d.add_paragraph('研究根目录：D:\\毕业设计')
 d.add_paragraph('版本：本轮独立报告 v1.0\n证据截止：2026年11月3日18:03:39（Asia/Shanghai）\n适用用途：硕士毕业设计研究审阅与后续实施依据')
 d.add_paragraph('结论层次：规范提出、源码实现、有限验证、条件证明、原生保持与创新性分别登记。原始材料保持不变。')
 d.add_page_break()
 d.add_heading('阅读导航',level=1)
 for block in blocks:
  if block[0]=='h1':d.add_paragraph(block[1])
 d.add_paragraph('附录A  关键项目证据定位\n附录B  统一参考文献\n附录C  本轮审计与使用说明')
 d.add_paragraph('引用约定：Rxx为两报告共享的外部文献；Exx为配套证据状态表；Kxx为矛盾处理记录。正文中的“拟议”不属于已经集成的软件能力。')
 d.add_page_break();eqnum=0
 for b in blocks:
  if b[0]=='h1':d.add_heading(b[1],1)
  elif b[0]=='h2':d.add_heading(b[1],2)
  elif b[0]=='p':
   pp=d.add_paragraph(b[1]);pp.paragraph_format.first_line_indent=Cm(.74)
  elif b[0]=='eq':eqnum+=1;add_math(d,b[1],eqnum,'survey' if '系统性' in filename else 'technical')
  elif b[0]=='eq_extra':add_math(d,'',str(eqnum)+'a','technical',b[1])
  elif b[0]=='table':add_table(d,b[1],b[2],b[3])
  elif b[0]=='code':
   pp=d.add_paragraph(b[1],'Caption');pp.paragraph_format.keep_with_next=True
   for line in b[2].splitlines():d.add_paragraph(line,'CodeBlock')
  elif b[0]=='figure':
   pp=d.add_paragraph();pp.alignment=WD_ALIGN_PARAGRAPH.CENTER;pp.paragraph_format.keep_with_next=True
   run=pp.add_run();run.add_picture(str(FIG/(b[1]+'.png')),width=Cm(16.5))
   d.add_paragraph(b[2],'Caption');d.add_paragraph(b[3],'SourceNote')
 app=d.add_heading('附录A 关键项目证据定位',1);app.paragraph_format.page_break_before=True
 d.add_paragraph('下表路径均相对D:\\毕业设计。状态完整字段、源码SHA-256、适用范围与限制见同目录《当前实现与证据状态表》；报告中的编号在本表独立可追踪。')
 # Paragraphs instead of multi-page wide path tables.
 for e in data.evidence:
  pp=d.add_paragraph(style='Reference');setfont(pp.add_run(e['id']+'  '+e['claim']+'。'),9.5,True)
  pp.add_run(e['source_path'].replace('/','\\')+'；'+e['locator']+'。状态：'+e['status']+'。')
 app=d.add_heading('附录B 统一参考文献',1);app.paragraph_format.page_break_before=True
 d.add_paragraph('两报告使用同一编号体系。实际选读范围、失败访问和版本限制见文献核验表；引用不表示本轮通读或复现全部论文。')
 for r in data.refs:
  pp=d.add_paragraph(style='Reference');pp.add_run(f"[{r['id']}] {r['authors']}. {r['title']}. {r['year']}. {r['type']}.")
  if r['doi']:pp.add_run(' DOI: '+r['doi']+'.')
  pp.add_run(' ');link(pp,'原文或官方入口',r['url'])
 d.add_heading('附录C 本轮审计与使用说明',1)
 d.add_paragraph('本轮新建独立交付目录，不覆盖旧版。递归索引、去重映射、源码符号/导入索引、原始数据重新计数、哈希差异、离线测试与文献PDF预检保存在工作底稿。历史运行与本轮重核分开，未运行原生服务、账户探索、MPC或确认性实验。')
 d.add_paragraph('保密处理：运行时密钥、令牌、密码、Player-Data及账户数据库不进入正文和配套普通日志；相关条目只保留必要路径/分类。公开哈希说明字节身份，不证明来源真实、学术优先权或实现安全。')
 d.add_paragraph('文献缺口更新：本地Randomizing_polynomials…pdf与3-3-4.pdf已取得并选读关键章节；Nissim–Weinreb页码按出版社更正为522—541。RAG及Nissim–Weinreb全文仍未取得；旧失败记录保留。')
 d.add_paragraph('Word公式为原生OMML，可直接编辑。图的可编辑SVG和PNG在工作底稿figures中；图表均为本轮整理，未复制外部论文图。渲染工具、逐页检查结果和限制以《文档核验记录》为准。')
 for root in [d.styles.element,d.element]:
  for border in root.xpath('.//w:pBdr'):border.getparent().remove(border)
 d.save(OUT/filename)
 return {'file':filename,'blocks':len(blocks),'equations':eqnum,'tables':len(d.tables),'inline_figures':len(d.inline_shapes),'paragraphs':len(d.paragraphs)}
if __name__=='__main__':
 data.export()
 res=[create('当前方案系统性调研报告',survey_text.blocks,'当前方案_系统性调研报告_2026-11-03.docx'),
      create('当前方案研究与技术方案报告书',technical_text.blocks,'当前方案_研究与技术方案报告书_2026-11-03.docx')]
 (W/'authoring_summary.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(res,ensure_ascii=False,indent=2))

