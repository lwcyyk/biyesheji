from pathlib import Path
import json,re,collections,csv,hashlib
ROOT=Path(r'D:\毕业设计');OUT=Path(__file__).resolve().parents[1]
records=json.loads((OUT/'data/source_records.json').read_text(encoding='utf-8'))
oldcore=json.loads((OUT/'data/core_analysis.json').read_text(encoding='utf-8'))
titles={
'P19':'SAGA: A Security Architecture for Governing AI Agentic Systems',
'P20':'Universal Cross-app Attacks: Exploiting and Securing OAuth 2.0 in Integration Platforms',
'P24':'Do You Need a Receipt? Anonymous Credential Revocation at Continental Scale via Private Record Certification',
'P27':'Securing Autonomous Clinical Agents: Time-Scoped Hypergraph Delegation for Controlling Patient Data Access',
'P29':'AgentBound: Securing Execution Boundaries of AI Agents',
'P32':'AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents',
'P34':'Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions',
'P35':'AGentVLM: Access control policy generation and verification framework with language models',
'P37':'CapChain: A Capability-Token Access Control Architecture with Verifiable Provenance for Multi-Agent LLM Systems'}
for r in records:
 if r['id'] in titles:r['title']=titles[r['id']]
 if r['id']=='L12':r['reading_scope']='正文与来源索引定点核读；部分表格仅机器提取'
finalmap={r['id']:r for r in records}
for p in OUT.glob('*.md'):
 t=p.read_text(encoding='utf-8')
 for old in oldcore:
  r=finalmap[old['id']]
  if old['title']!=r['title']:t=t.replace(old['title'],r['title'])
 p.write_text(t,encoding='utf-8')
(OUT/'data/source_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')

def local_link(r):
 return '['+Path(r['local_path']).name+']('+Path(r['local_path']).as_posix()+')' if r.get('local_path') else '本次公开页面或项目已登记入口'
def reference(r):
 doi=(' DOI：`'+r['doi']+'`。') if r.get('doi') else ''
 version=(' 版本：`'+r['draft_id']+'`。') if r.get('draft_id') else ''
 return f"[{r['id']}] {r['authors']}（{r['year']}）。{r['title']}。{r['venue']}。{doi}{version} [原始入口]({r['url']})。核验：{r['verification_status']}；范围：{r['reading_scope']}。"

# Refresh the stage-one evidence record after the verification phase.
lines=['# 文献来源与证据记录','','本文件经第四阶段回溯修订。来源编号与09一致。明确事实核验、摘要级分析、未读证明和实验复现分别登记。完整结构字段见[data/source_records.json](data/source_records.json)。','']
for r in records:
 lines += [f"## {r['id']} {r['title']}",'',f"- 作者、年与渠道：{r['authors']}；{r['year']}；{r['venue']}。",f"- 来源：[公开或项目入口]({r['url']})。本地：{local_link(r)}。",f"- 标识：{r.get('doi') or r.get('arxiv_id') or r.get('draft_id') or '未额外推定DOI或arXiv标识'}。",f"- 研究问题：{r.get('problem','本次按题录、条文或项目状态定位；进一步问题分析见所引阅读范围')}。",f"- 技术方法：{r.get('method',r['reading_scope'])}。",f"- 结果：{r.get('results','该项按规范、产品声明或项目记录使用，实验数据依实际来源范围；本次新增实验为0')}。",f"- 结论：{r.get('conclusion','支持本报告明确引用范围，其他结论保留待核')}。",f"- 局限：{r['limitations']}。",f"- 阅读与核验：{r['reading_scope']}；{r['verification_status']}；{r['verification_scope']}。"]
 if r.get('sha256'):lines.append('- 文件SHA256：`'+r['sha256']+'`。')
 if r.get('preflight'):lines.append(f"- 结构：{r['preflight']}；{r['pages']}个物理页；页码和语义核验分别解释。")
 lines.append('')
lines+=['## 论断与证据对应','','| 论断 | 核心来源 | 明确定位与解释 |','|---|---|---|','| 当前主线为全生命周期系统，链为辅助 | [L01]、[L02] | thesis_mainline、supersedes、auxiliary_candidate |','| 模型与原生接受具有不同验证责任 | [P03]、[P05]、[L08] | 原生前提、D0、算法连接状态 |','| 来源歧义在可靠容量合同下仍可关闭 | [L14] | C1–C7、P1–P3、E1；流为强基线 |','| E2相同观察形成共同信息障碍 | [L14] | 四个固定处置集合穷尽；链锚定无法新增源事实 |','| 数学精细界与严格代价实例分开 | [L03]、[L04] | 主定理、两族判废与实现门 |','| 查询界依赖特定归一化与误差 | [L05]、[L06]、[N01] | 定理、先例对照、群测摘要范围 |','| JWT客户端认证有新版audience要求 | [N02]、[P33] | RFC10070第4、5节与攻击对象 |','| 来源承诺保留声明真实性及完整性责任 | [O12]、[O14] | RFC9943第9.2、9.3及草案第12节 |','']
(OUT/'03_文献来源与证据记录.md').write_text('\n'.join(lines),encoding='utf-8')

reftext=['# 参考文献与来源清单','','全套采用统一前缀编号与作者年题录。P为45篇核心论文，D为8份草案，L为15项项目证据，O为18项官方资料，N为3项定向补充，CN为4项国内来源或线索，Q为1项密码学对象。共94项。','', '已核验指本次明确使用的题录与事实，完整理论证明和实验复现另列；部分核验保留具体范围；待核验条目仅作为线索。正文中的数值均按作者报告或项目记录解释。','']
for r in records:
 reftext += [f"## {r['id']}",'',reference(r),'',f"- 本地位置：{local_link(r)}。",f"- 核验范围：{r['verification_scope']}。",f"- 限制：{r['limitations']}。"]
 if r.get('sha256'):reftext.append('- SHA256：`'+r['sha256']+'`。')
 reftext.append('')
(OUT/'09_参考文献与来源清单.md').write_text('\n'.join(reftext),encoding='utf-8')

# A conservative content-reading ledger; metadata enumeration is not a full read.
ledger=[]
for r in records:
 if not r.get('local_path'):continue
 p=Path(r['local_path'])
 ledger.append({'source_id':r['id'],'path':str(p),'sha256':r.get('sha256') or hashlib.sha256(p.read_bytes()).hexdigest(),'scope':r['reading_scope'],'mode':'同会话前轮已读复用' if r['id'] in ['L09','L10'] else '本轮内容核读','level':'定点核心分析' if r.get('deep_analysis') else ('摘要或首页' if r['id'].startswith('P') or r['id']=='Q01' else '记录的正文或片段')})
extras=[('X01','research_main_innovation/main_topic_selection/TOPIC_DECISION.md','全文，作为有后继的11月6日历史决定'),('X02','research_main_innovation/main_topic_selection/FIRST_PROOF_ATTEMPT.md','已显示归约和证明片段；其后继以L03为准'),('X03','mainline_research_closure_v1/FINAL_STATUS.json','全文结构化状态')]
for key,rel,scope in extras:
 p=ROOT/rel
 ledger.append({'source_id':key,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':scope,'mode':'本轮内容核读','level':'历史版本或状态'})
assert len({r['path'] for r in ledger})==len(ledger)
(OUT/'data/read_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')

inv=json.loads((OUT/'data/inventory.json').read_text(encoding='utf-8'))
readby={r['path']:r for r in ledger};hashby={r['sha256']:r for r in ledger}
for row in inv:
 if row['path'] in readby:
  rr=readby[row['path']];row['analysis_status']=rr['mode']+'；'+rr['scope']
 elif row.get('sha256') in hashby:
  rr=hashby[row['sha256']];row['analysis_status']='同字节副本；按'+rr['source_id']+'归并，未重复计论文'
 elif row['extension']=='.pdf':row['analysis_status']='已清点；不同字节来源已做首页机器提取，尚未内容核读或解析失败'
(OUT/'data/inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'data/inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(inv[0]));w.writeheader();w.writerows(inv)
stats=json.loads((OUT/'data/inventory_summary.json').read_text(encoding='utf-8'))
lines=['# 现有研究资料清单','','研究根目录：`D:/毕业设计`。清点与取证日期：2026年11月9日。','',f"共清点{len(inv):,}个候选文件，逐文件位置、类型、主题、研究价值和实际读取状态见[inventory.csv](data/inventory.csv)。完整机器表同时保存为[inventory.json](data/inventory.json)。",'', '## 数量口径','', '| 项目 | 数量与含义 |','|---|---|',f"| 候选研究文件 | {len(inv):,}；包含源码、夹具和日志，按类型分别计数 |",'| PDF文件 | 348；按字节归并为241个对象，另有107份同字节副本 |','| 核心论文 | 45；1072页，均完成机器全文提取与本次结构预检 |','| 论文内容分析 | 45篇，其中14篇定点核心分析，31篇首页或摘要级 |','| 本地草案 | 8份；标题、版本与摘要范围核读 |',f"| 内容核读登记 | {len(ledger)}个研究文件，其中{sum(r['mode']=='本轮内容核读' for r in ledger)}项本轮读取，2项同会话已读复用 |",'| 新登记外部来源 | 3项：2篇直接前作和1份最新RFC；无新增论文下载 |','', '## 文件类型','', '| 类型 | 数量 |','|---|---:|']
lines += [f'| {k} | {v:,} |' for k,v in stats['kinds'].items()]
lines+=['','## 版本关系与选用依据','','| 材料族 | 关系 | 本次采用 |','|---|---|---|','| 11月4日v2、v3及计划书 | 同主题多版；版本序号与标题可见 | 作为历史设计背景，独有定义和数据经后继证据定位 |','| 11月6日A-E决定 | 当时唯一证明目标，已有后继 | 保留历史片段，当前数学状态采用MT-1与严格分离裁决 |','| 11月7日MT-1与分离裁决 | 数学界、优先权和费用分离分别登记 | 两者共同约束当前理论表述 |','| 11月8日研究历程总报告 | 综合系统、理论、密码学和负结果 | 用于历史完整性与支线范围 |','| 11月9日探索报告 | 保留25项方向及最新询问 | 采用其核心合同和方向索引 |','| 11月9日多尝试R1、R2 | R2明确修订主线和辅助层级 | 主线定位以R2为据，R1的证据和局部判据按范围保留 |','| 四阶段设计与thesis_draft | 设计、论文骨架及证据映射 | 四阶段原稿已清点，本轮经L11/L13关联，全文尚未逐件精读 |','', '## 内容核读文件','', '| 编号 | 文件 | 主题与价值 | 分析程度 |','|---|---|---|---|']
for r in ledger:
 src=finalmap.get(r['source_id'],{})
 topic=src.get('category','历史版本与状态')
 lines.append(f"| {r['source_id']} | [{Path(r['path']).relative_to(ROOT)}]({Path(r['path']).as_posix()}) | {topic} | {r['mode']}；{r['scope']} |")
lines+=['','## 去重与输入异常','','PDF/Word完全相同字节组见[duplicate_files.json](data/duplicate_files.json)。同一论文的多个版本继续按arXiv、DOI与标题关联，241个字节对象不作为独立论文数。','', '两个外围副本无法解析：GroupActions空文件、2022批量撤销论文截断。失败状态见[pdf_catalog.json](data/pdf_catalog.json)。后者的可用证据来自期刊网页及L15，原始坏副本保持原状。','', '早期清点包含Go模块缓存，识别后已从最终候选范围排除。依赖、版本库和运行环境的排除路径保存在inventory_summary.json。读取元数据、机器提取与实际内容核读严格分开。','']
(OUT/'01_现有研究资料清单.md').write_text('\n'.join(lines),encoding='utf-8')

groups={'身份与秘密托管':'身份表示与秘密托管','连接与绑定':'账户绑定与协议安全','任务授权':'任务授权与最小权限','偏好与最小权限':'任务授权与最小权限','授权状态':'授权历史 撤销与效果','撤销与效果':'授权历史 撤销与效果','信息流与执行':'执行边界与信息流','形式化与规划':'形式化与决策','私密证据':'私密证据与审计','评测与综述':'评测与系统综述'}
by=collections.defaultdict(list)
for p in oldcore:by[groups[p['category']]].append(p['id'])
maptext='| 路线 | 论文编号 |\n|---|---|\n'+'\n'.join('| '+k+' | '+'、'.join('['+i+']' for i in v)+' |' for k,v in by.items())
main=OUT/'00_完整技术调研报告.md';t=main.read_text(encoding='utf-8');t=t.replace('<!--CORE_MAP-->',maptext)
used=set(re.findall(r'\[((?:P|D|L|O|N|CN|Q)\d{2})\]',t))
assert used<=set(finalmap),used-set(finalmap)
assert len(used)==94,(len(used),set(finalmap)-used)
t=t.replace('<!--REFERENCES-->','\n\n'.join(reference(r) for r in records if r['id'] in used))
main.write_text(t,encoding='utf-8')

names=['00_完整技术调研报告.md','01_现有研究资料清单.md','02_研究问题与调研计划.md','03_文献来源与证据记录.md','04_技术分类与研究现状.md','05_核心论文深度分析.md','06_技术方案对比.md','07_现有研究局限性.md','08_研究空白与潜在研究方向.md','09_参考文献与来源清单.md','10_文献及事实核验报告.md','11_调研质量审查与执行记录.md']
q=OUT/names[-1];t=q.read_text(encoding='utf-8');t=t.replace('阶段一进行中。已保存资料清单与研究计划。后续阶段完成后在此追加真实结果、修改和剩余限制。','阶段一已保存01至03；第二阶段已保存04至06；第三阶段已保存07至08；第四阶段已保存09至10并回改来源与前序事实；随后完成主报告、中文检查和最终一致性检查。')
t+='''

## 内部反方检查与修订

范围检查确认：11月6日A-E目标已有后继，当前主线采用R2，T3/T+与FI保持各自范围。综合检查确认：静态流和k次查询基线已经达到所列子域目标，因此潜在研究责任集中到可靠映射、动态状态和完整费用。最终检查确认：链锚定只承担其声明与版本作用，源真实性、遗漏和新鲜度继续由相应合同支撑。

直接修订包括P26的模板年份与DOI、P34/P39占位DOI、P38题名版本、P43修订日期、P07分母和P11卷号；保留CapChain触发率、Intent未执行草稿、PRC any-trust及本地156项未结条件。修订记录位于data/citation_corrections.json及10。

本次确定性检查独立于研究机制：检查文件数量、来源ID、引用定义、源文件路径、哈希、模板占位和指定句式。人工判断由同一模型按预先清单分阶段完成，外部独立同行、证明助手或第三方模型审阅均未启动。该过程保持实际身份与证据范围。

## 中文检查

采用zh-tech-writing的短句、主动表达、具体事实、段落重点和中英文排版规则。技能与typography来源副本位于working/skill_refs。autocorrect命令不可用，采用手动检查与保护URL、数学、标识符后的空格整理。技术标题、原始数值和文献归属保留。

## 剩余限制

核心45篇中31篇仍为摘要或首页级，14篇深度限于已记录片段。外围241个不同PDF字节对象未全部进行内容核读。CN04正文仍待取得，两个失败副本保留。部分DOI入口现场受限，原件、作者、会议或机构记录按实际范围替代。真实部署、完整数学复核、全局优先权和严格实现分离仍需各自证据。

## 最终交付索引

'''
t+='\n'.join(f'- [{name}]({(OUT/name).as_posix()})' for name in names)+'\n'
q.write_text(t,encoding='utf-8')

# Spacing rules apply to prose, preserving source links, code and mathematics.
def normalize(text):
 stash=[]
 def protect(m):stash.append(m.group());return '\x01'+str(len(stash)-1)+'\x02'
 text=re.sub(r'```[\s\S]*?```|\$\$[\s\S]*?\$\$|`[^`\n]+`|<!--[^>]*-->|https?://[^\s)]+|\]\([^\n]+?\)',protect,text)
 text=re.sub(r'(?<=[\u3400-\u9fff])(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?=[\u3400-\u9fff])',' ',text)
 text=re.sub(r'\x01(\d+)\x02',lambda m:stash[int(m[1])],text)
 return text
for name in names:
 p=OUT/name;p.write_text(normalize(p.read_text(encoding='utf-8')),encoding='utf-8')

summary={'topic':'面向用户与AI智能体的全生命周期密码与凭据管理；区块链辅助证据核验','candidate_files':len(inv),'pdf_files':348,'unique_pdf_byte_objects':241,'core_papers_analyzed':45,'targeted_deep_papers':14,'core_pdf_pages':1072,'content_reading_records':len(ledger),'current_turn_content_reads':sum(r['mode']=='本轮内容核读' for r in ledger),'same_chat_reused_reads':2,'drafts':8,'new_sources':3,'new_papers':2,'new_standard':1,'reference_status_counts':dict(collections.Counter(r['verification_status'] for r in records)),'total_source_records':len(records),'markdown_outputs':names,'output_directory':str(OUT),'skills_used':['academic-research-suite/deep-research','ARS综合与来源方法','zh-tech-writing远程规范','pdf与ARS结构预检'],'missing_named_skills':['related-work-synthesizer','gap-finder','citation-verification'],'candidate_code_created':0,'native_auth_requests':0,'experiments_rerun':0}
(OUT/'data/execution_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
