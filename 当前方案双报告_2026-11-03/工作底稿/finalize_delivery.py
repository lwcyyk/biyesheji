from pathlib import Path
import json,hashlib,csv,zipfile,re,shutil
from pypdf import PdfReader
from lxml import etree
import report_data as d
O=d.OUT;W=d.WORK
# Read the actual exported final tables; report_data alone predates the frozen increment.
d.evidence=json.loads((O/'当前实现与证据状态表.json').read_text(encoding='utf-8'))
d.refs=json.loads((O/'文献核验表.json').read_text(encoding='utf-8'))
d.conflicts=json.loads((O/'关键矛盾及处理记录.json').read_text(encoding='utf-8'))
d.contributions=json.loads((O/'贡献主张—先例—证据—限制对应表.json').read_text(encoding='utf-8'))
d.next_items=json.loads((O/'未完成项及下一阶段进入条件.json').read_text(encoding='utf-8'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
old=json.loads((W/'增量一轮已逐页审阅哈希.json').read_text(encoding='utf-8'))
docs=[];pages=[]
for key,file in [('survey','当前方案_系统性调研报告_2026-11-03.docx'),('technical','当前方案_研究与技术方案报告书_2026-11-03.docx')]:
 pdf=W/'qa'/f'{key}.pdf';reader=PdfReader(pdf);n=len(reader.pages)
 for i,page in enumerate(reader.pages,1):
  image=W/'qa'/f'{key}-{i:02}.png';digest=h(image)
  pages.append({'document':file,'page':i,'png':str(image.relative_to(O)),'sha256':digest,'visual_review':'已逐页打开图像审阅；最终修订后内容变化页重新审阅，其余图像哈希一致','matches_previous_review':old.get(image.name)==digest,'layout':'未发现截断、重叠、缺字、孤立表头或空白页','formula':'原生OMML公式按页核对；无公式页不适用','references':'编号/出处可读；不等同外部来源全部全文复核','text_characters':len(page.extract_text() or '')})
 docs.append({'file':file,'sha256':h(O/file),'pages':n,'reviewed_pages':n,'pdf_sha256':h(pdf)})
qa={'date':'2026-11-03','renderer_attempt':'render_docx.py已执行但失败：soffice.exe不在PATH；失败日志保留','actual_renderer':'Microsoft Word COM，文档只读打开、Fields.Update、Repaginate、ExportAsFixedFormat；bundled Poppler pdftoppm 110dpi','render_warnings':['Poppler报告Symbol/ArialUnicode显示字体警告；最终逐页未发现对应缺字。'],'authoring':'bundled Python/python-docx；latex2mathml 3.81.1 + Microsoft MML2OMML.xsl；31条原生可编辑OMML','corrections':['移除默认Title蓝线和Subtitle斜体','修复求和/乘积空操作数','表头与首数据行同页','移除由分页段落产生的空白页','重画M10到执行器连线以避免经过B','Post使用严格存在量词集合定义','纳入冻结增量后重新审阅；压缩附录段距避免仅两条证据占一页'],'documents':docs,'pages':pages,'limits':'本机Word渲染核验；其他Office/字体环境可能重新分页。非数学形式化证明。'}
save(O/'文档核验记录.json',qa)
same=sum(x['matches_previous_review'] for x in pages)
(O/'文档核验记录.txt').write_text(f'文档核验记录 2026-11-03\n\n调研报告{docs[0]["pages"]}页，方案报告{docs[1]["pages"]}页，共{len(pages)}页。全部逐页打开PNG核查；最终{len(pages)-same}个变化页重核，其余{same}页图像哈希与此前逐页审阅一致。\n实际排版：Microsoft Word COM只读导出PDF；bundled Poppler 110dpi渲染。\n常规render_docx.py因缺少soffice.exe失败，未声称它通过。日志保留于工作底稿/renderer_attempt.log。\nPoppler报告Symbol/ArialUnicode显示字体警告；逐页未见缺字、截断和重叠。\n已修正：Title默认蓝线、公式求和/乘积空占位、孤立表头、多余空白页、架构连线及Post集合表示；增量后重排附录。\n31条公式为可编辑OMML，含分数和上下标。结构检查未发现无效E/R编号、段落边框、空求和操作数。\n本检查不等于数学证明或一般Word跨环境一致性保证。逐页图像、哈希和页码详见同名JSON。\n',encoding='utf-8')
# Summarize missing references, including the D0 source named in SRS.
missing=[
{'item':'v2.13完整运行包','reference':'handoff.py、run_v213.py、E213','status':'在递归文件与历史ZIP/限定嵌套ZIP检索未找到','impact':'14案例及3处退出仅历史文档记载'},
{'item':'CS03完整运行包','reference':'run_models.py、run_local_separator.py、run_balanced_history.py及D01—D03结果','status':'未找到','impact':'32768/324/48/96不并入当前验证'},
{'item':'前序密码学设计','reference':'V5.1、CS01、CS02原件','status':'未找到原件','impact':'不能独立复核完整协议'},
{'item':'四阶段源附件','reference':'schemas、sql/001_initial.sql、traceability、DOT/SVG源','status':'指定目录只有DOCX；限定历史包未找到源附件','impact':'正文附录可读不等于独立源包'},
{'item':'SRS引用D0','reference':'硕士毕业论文_A+B技术方案设计_v1.0.docx','status':'当前递归索引未发现该准确文件名','impact':'只按SRS引用登记，不作为本轮直接读取原件'},
{'item':'RAG全文','reference':'R11机构AAM','status':'本轮下载403；仅原始摘要/题录','impact':'不能排除其完整能力覆盖'},
{'item':'Nissim–Weinreb全文','reference':'R34','status':'出版社题录/摘要可得；PDF未取得','impact':'522—541已纠正，精确先例归约仍未决'},
{'item':'随机化多项式与共享解码','reference':'R27/R28本地PDF','status':'已找到；11/43页结构预检PASS，关键章节选读','impact':'不再列全文缺失；完整优先权仍须归约'},
{'item':'冻结增量后的变化','reference':'research_v12后续dev02等；截点2026-11-03 18:03:39 Asia/Shanghai','status':'不在本轮894项增量快照内；不称全局缺失','impact':'新结论须另立来源/哈希审计；dev01的4文件哈希与冻结源码不同'},
{'item':'r3/r4一般论证与优先权','reference':'双行非均匀核、表示分离、六弧极值','status':'报告/源码/manifest已读取；10份有限精确证书本轮通过','impact':'一般归约、唯一性与域嵌入仍为手工推导；精确先例覆盖未闭合'},
{'item':'q-polymatroid新版全文','reference':'R45 arXiv v2 2026-10-08','status':'本轮核验原始摘要和题录；原r3的v1选读不能替代v2','impact':'不作完整先例排除或理论包含性定论'}]
save(O/'资料缺失与核验限制.json',missing)
with (O/'资料缺失与核验限制.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=missing[0]);wr.writeheader();wr.writerows(missing)
# Public audit receipts delivered without raw secrets or third-party papers.
audit=O/'核验附件';audit.mkdir(exist_ok=True)
for name in ['索引最终统计.json','历史清单最终核对.json','原始结果再统计.json','本轮原始资料保持核对.json','文档结构检查.json','本轮公开证书检查.json','本轮MPC历史日志离线重核.json','本轮离线单元检查.log','嵌套压缩包引用检索.json','paper1_preflight.json','paper2_preflight.json','docx提取目录.csv','去重阅读映射.json']:
 shutil.copyfile(W/name,audit/name)
# Include algorithms' current symbols and dependency graph for source claims.
for name in ['自写源码符号索引.json','源码导入依赖索引.json','索引最终统计_含增量.json','增量快照清单.json','增量来源哈希核对.json','冻结增量最终保持核对.json','增量v12原始行重核.json','增量v12源码版本差异.json','增量密码学证书独立重核.json','新增AB3证书scope反例.json']:shutil.copyfile(W/name,audit/name)
for name in ['audit_increment.py','index_increment.py','audit_final.py','verify_evidence.py','render_word.ps1','renderer_attempt.log']:shutil.copyfile(W/name,audit/name)
# Retain editable vector diagrams alongside the Word artifacts.
figs=O/'可编辑图示';figs.mkdir(exist_ok=True)
for p in (W/'figures').glob('*.svg'):shutil.copyfile(p,figs/p.name)
# Typed evidence status columns, multiple statuses can coexist.
matrix=[]
for e in d.evidence:
 s=e['status'];matrix.append({'id':e['id'],'claim':e['claim'],'document_proposed':'原材料已提出' if '文档提出' in s else '由源码/结果/本轮审计登记，见来源','source_implemented':'是' if '源码已实现' in s else ('源码存在但未建立结果' if '源码存在' in s else '未据此认定'),'finite_validation':'有历史或本轮有限证据' if '已运行有限' in s else '未据此建立','conditional_math':'有条件推导' if '条件性数学论证' in s else '非本条证明结论','general_proof':'一般论证待完成或待独立复核' if '一般证明' in s else ('有手工条件论证；不等同一般实现证明' if '条件性数学论证' in s else '非本条证明结论'),'native_scope':e['scope'] if '原生' in s else '未据此确认原生部署','integration':'尚未集成' if '尚未集成' in s else '按证据范围，不代表完整产品','future_only':'是（限定该条版本）' if '仅为未来计划' in s else '否/分层状态','negative_or_narrowed':'是' if '收缩' in s or '反例' in s else '见限制','missing_or_unverified':'是' if '缺失' in s or '资料不足' in s else '见限制','source':e['source_path'],'source_sha256':e['source_sha256'],'locator':e['locator'],'result':e['result'],'scope':e['scope'],'limitation':e['limitation']})
with (O/'证据分层登记矩阵.csv').open('w',encoding='utf-8-sig',newline='') as f:
 for row,e in zip(matrix,d.evidence):
  s=e['status']
  row['native_validation']='未验证（相应产品）' if '原生实现未验证' in s else ('已有限验证（限定范围）' if '原生实现已验证' in s or '原生MPC已验证' in s else '不据此确认原生实现')
 wr=csv.DictWriter(f,fieldnames=matrix[0]);wr.writeheader();wr.writerows(matrix)
readme=f'''交付说明 2026-11-03

正式报告
1. 当前方案_系统性调研报告_2026-11-03.docx（{docs[0]['pages']}页）
2. 当前方案_研究与技术方案报告书_2026-11-03.docx（{docs[1]['pages']}页）
两份独立可读，共用47条外部文献和41项项目证据编号。正文分别侧重先例/空白与规格/实现/验证。
证据范围：初始全目录审计及2026年11月3日18:03:39（Asia/Shanghai）固定的894项新增资料。截点后持续变化的开发目录未并入核验。

配套证据
资料索引与来源哈希清单.csv：10607条目；9402项公开可读哈希；7354组不同内容；运行秘密仅元数据。
当前实现与证据状态表.csv/json：41项能力与主张。
关键矛盾及处理记录.csv/json：20项冲突，不覆盖原件。
文献核验表.csv/json与统一参考文献.bib：47条，实际阅读范围和限制逐条登记。
贡献主张—先例—证据—限制对应表.csv/json：15项。
未完成项及下一阶段进入条件.csv/json：15项。
原需求编号与实现映射.csv：37项原编号。
证据分层登记矩阵.csv：非互斥的分层状态。
资料缺失与核验限制.csv/json；历史压缩包成员索引.csv。
核验附件：本轮原始保持、历史清单/原始数据重核、96项离线测试、32个既有MPC场景离线重核、10份新增精确证书检查、688条开发结果重计、AB3范围反例与PDF预检等。

主要结论
有限A/B/AB内核、新研究原型和多项密码学参考已存在；A4/B4/AB3已形成源码和开发记录。独立算法优势、正式统计支持、完整产品与密码学主线接入尚未建立。
本轮复现AB3证书scope反例：control无解时，含probe的联合可行策略仍被接受为control-only证书。它是公共证书合同缺陷，不等于已证明原生越权；原代码未改，列为N06验收阻塞。
dev01共70输入、688方法行，决定性参考比较未见状态/值差异；其中4份注册源码哈希与冻结代码不同，不能用于宣称当前全部源码通过；后续dev02不在本轮快照内。
原负控制和反例保留：A等效条件、6/6和8/6、B共享子域等效/枚举补齐、AB投影敏感、R-J等效或更好。
AES前端实际接rowspace2；seed-repair未重跑前端。r1已有秘密支持gate参考，但不是结构优化全流程或主线集成。
结构定理带全部受限前提；匹配构造与独立分块等效；主动安全底座运行不等于完成恶意安全审计。
新增r3/r4给出双行非均匀核、同拟阵不同表示的最优隐私差异、六弧关联结构的条件极值与核边缘唯一性。10份有限有理数证书检查通过；一般核归约、对偶提升、域嵌入及优先权仍需独立审定，尚无恶意采样/部署净成本证据。
本地新增的两篇论文全文已选读，旧缺口更新；RAG和Nissim–Weinreb全文及部分历史实验/四阶段源附件仍缺。

本轮实际工作
递归资料索引、核心文档/关键源码/原始数据和哈希核对、外部一手来源选读、96项离线单元测试、32个历史MPC场景离线解析、公开证书检查与GF4计数；另核对688行、10份有理数证书及AB3范围反例。
没有启动原生服务、账户探索、新MPC或确认性实验。此前原始保持复核的5586项公开研究文件全部一致；最终894项冻结增量复核全部一致。该结论不声称外部持续开发目录此后未改变。
文档由本机Word排版，Poppler逐页渲染并检查{len(pages)}页，31条主要公式为可编辑OMML。常规render_docx.py缺LibreOffice失败，替代过程如实登记。
工作底稿保留生成脚本、可编辑SVG、内部PDF/PNG和提取文本。压缩交付包不含运行秘密、第三方依赖或论文全文。
可编辑图示目录提供5份SVG；核验附件另含实际审计脚本与Word替代渲染脚本，供审阅执行范围。

阅读规则
Rxx为文献编号；需求R01—R04在需求上下文中保持原编号。Exx为项目证据；Kxx为本轮矛盾处理；Nxx下一阶段台账不重编号原需求。
“已实现”“有限验证”“条件推导”“原生验证”“尚未集成”“未来计划”可同时出现在不同层面，不相互替代。
'''
(O/'交付说明.txt').write_text(readme,encoding='utf-8')
# Final public delivery manifests and ZIP.
files=[p for p in O.iterdir() if p.is_file() and p.suffix!='.zip' and p.name!='交付文件哈希.json']
files+=list(audit.iterdir())+list(figs.iterdir())
manifest=[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(files)]
save(O/'交付文件哈希.json',{'date':'2026-11-03','files':manifest})
zip_path=O/'当前方案双报告与证据附件_2026-11-03.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[O/'交付文件哈希.json']:z.write(p,str(p.relative_to(O)))
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
print(json.dumps({'documents':docs,'evidence':len(d.evidence),'literature':len(d.refs),'conflicts':len(d.conflicts),'zip':str(zip_path),'zip_bytes':zip_path.stat().st_size,'public_files':len(files)+1},ensure_ascii=False,indent=2))

