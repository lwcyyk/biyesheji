from pathlib import Path
import json,re,collections,hashlib
OUT=Path(__file__).resolve().parents[1];ROOT=Path(r'D:\毕业设计')
records=json.loads((OUT/'data/source_records.json').read_text(encoding='utf-8'))
def alltext(obj):
 if isinstance(obj,dict):
  if obj.get('type')=='text':yield obj.get('text','')
  else:
   for v in obj.values():yield from alltext(v)
 elif isinstance(obj,list):
  for v in obj:yield from alltext(v)
web=[]
for fn in ['web_evidence_batches.json','metadata_web_batch.json','draft_cn_web_batch.json','verification_extra_web.json','verification_fields_web.json','verification_exact_web.json']:
 web.extend(alltext(json.loads((OUT/'data'/fn).read_text(encoding='utf-8'))))
sections=[s for t in web for s in t.split('\n--------------------------------------------------------------------------------\n')]
clean=lambda s:re.sub(r'【\d+†([^】]+)】',r'\1',s)
changes=[]
for r in records:
 r['full_text_validation']='未进行全文证明审查或实验复现'
 if r['id'].startswith('P'):
  hits=[s for s in sections if r.get('url') and r['url'] in s[:600]]
  r['web_record_status']='有可读主来源或检索记录' if any('Total lines:'in s and 'Internal Error'not in s and 'Access Denied'not in s for s in hits) else '现场入口受限或仅本地原件；保留核验范围'
  for s in hits:
   m=re.search(r'L\d+: # Title:(.+)',s)
   if m:r['title_original']=r['title'];r['title']=clean(m[1].strip())
   m=re.search(r'L\d+: Authors:(.+)',s)
   if m:r['authors']=clean(m[1].strip())
  r['verification_status']='已核验' if r.get('deep_analysis') else '部分核验'
  r['verification_scope']='已核验仅表示本次所引题录和定点事实；完整理论及实验复现未执行' if r.get('deep_analysis') else '本地摘要或首页匹配；完整机制、条件和未读结果保持待核'
  if r['id']=='P24':r['reading_scope']='物理页2、5、7的摘要与相关片段';r['evidence_locator']='物理页2、5、7'
  if r['id']=='P29':r['reading_scope']='物理页1、4、6的相关片段';r['evidence_locator']='物理页1、4、6'
  if r.get('arxiv_id'):r['doi']=r.get('doi') or '10.48550/arXiv.'+re.sub(r'v\d+$','',r['arxiv_id'])
 if r['id'] in ['L14','L15']:r['reading_scope']='全文';r['verification_scope']='核对文档字段、命题范围和来源状态；未重跑原生实验'
overrides={
'P07':{'title':'Demystifying the (In)Security of OAuth-based Account Linking in Connector Ecosystems','doi':'10.1109/SP63933.2026.00128'},
'P12':{'doi':'10.1007/978-3-031-51479-1_23'},
'P14':{'title':'DECO: Liberating Web Data Using Decentralized Oracles for TLS','doi':'10.1145/3372297.3417239'},
'P19':{'url':'https://www.ndss-symposium.org/ndss-paper/saga-a-security-architecture-for-governing-ai-agentic-systems/'},
'P22':{'title':'Position: AI Agents Need Authenticated Delegation'},
'P23':{'title':'The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents','doi':'10.18653/v1/2025.acl-long.1435'},
'P26':{'doi':'10.1145/3786582.3786839','venue':'ICSE 2026 NIER；本地模板字段与正式题录分列'},
'P31':{'url':'https://aclanthology.org/2026.findings-emnlp.2059/','title':'When Lower Privileges Suffice: Investigating Over-Privileged Tool Selection in LLM Agents'},
'P33':{'doi':'10.1109/SP63933.2026.00116','title':'Audience Injection Attacks: A New Class of Attacks on Web-Based Authorization and Authentication Standards'},
'P34':{'doi':'10.1145/3796519','venue':'本地2025预印本；2026正式DOI定位，版本差异未完整比对'},
'P38':{'doi':'10.1609/aaai.v40i42.40895','title':'MCPTox: A Benchmark for Tool Poisoning on Real-World MCP Servers'},
'P39':{'doi':'10.1145/3832783.3837413','venue':'ASE 2026；本地arXiv2508.00500v4与正式题录分列'},
'P43':{'year':'2025；所用v3修订于2026-05-14'},
}
author_map={
'P07':'Kaixuan Luo, Xianbo Wang, Pui Ho Adonis Fung, Wing Cheong Lau',
'P08':'Fergus Murphy, Saša Radomirović',
'P09':'Shervin Javdani, Yuxin Chen, Amin Karbasi, Andreas Krause, J. Andrew Bagnell, Siddhartha Srinivasa',
'P10':'Steven Carr, Nils Jansen, Sebastian Junges, Ufuk Topcu',
'P11':'Alexander Bork, Joost-Pieter Katoen, Tim Quatmann, Svenja Stein',
'P12':'Luca Arnaboldi, David Aspinall, Christina Kolb, Saša Radomirović',
'P14':'Fan Zhang, Deepak Maram, Harjasleen Malvai, Steven Goldfeder, Ari Juels',
'P15':'Xiang Xie, Kang Yang, Xiao Wang, Yu Yu',
'P16':'Mohammad Sheikhalishahi, I. Stork, Nicola Zannone',
'P19':'Georgios Syros, Anshuman Suri, Jacob Ginesin, Cristina Nita-Rotaru, Alina Oprea',
'P20':'Kaixuan Luo, Xianbo Wang, Pui Ho Adonis Fung, Wing Cheong Lau, Julien Lecomte',
'P22':'Tobin South, Samuele Marro, Thomas Hardjono, Robert Mahari, Cedric Deslandes Whitney, Alan Chan, Alex Pentland',
'P23':'Feiran Jia, Tong Wu, Xin Qin, Anna Squicciarini',
'P24':'Kasra EdalatNejad, Sebastian Faust, Jonas Hofmann, Philipp-Florens Lehwalder, Thomas Schneider',
'P27':'Hassan Karim, Sai Sitharaman, Deepti Gupta, Danda B. Rawat',
'P28':'Jean Snyman, Chris Culnane, Ioana Boureanu, Gerault David（按本地首页顺序登记）',
'P29':'Christoph Bühler, Matteo Biagiola, Luca Di Grazia, Guido Salvaneschi',
'P30':'Martin Odersky, Yaoyu Zhao, Yichen Xu, Oliver Bračevac, Cao Nguyen Pham',
'P31':'Kaiyue Yang, Yuyan Bu, Jingwei Yi, Yuchi Wang, Biyu Zhou, Juntao Dai, Songlin Hu, Yaodong Yang',
'P32':'Haoyu Wang, Christopher M. Poskitt, Jun Sun',
'P33':'Pedram Hosseyni, Ralf Küsters, Tim Würtele',
'P34':'Xinyi Hou, Yanjie Zhao, Shenao Wang, Haoyu Wang',
'P35':'Sakuna Harinda Jayasundara, Nalin Asanka Gamagedara Arachchilage, Giovanni Russello',
'P37':'Tuck Wai Choong, Wen-Bin Hsieh, Jenq-Shiou Leu',
'P38':'Zhiqiang Wang, Yichao Gao, Yanting Wang, Suyuan Liu, Haifeng Sun, Haoran Cheng, Guanquan Shi, Haohua Du, Xiang-Yang Li',
}
# Full given names not established by a primary record remain initials.
author_map['P08']='F. Murphy, S. Radomirović'
author_map['P16']='M. Sheikhalishahi, I. Stork, N. Zannone'
for r in records:
 key=r['id']
 if key in overrides:
  changes.append({'id':key,'before':{k:r.get(k,'') for k in overrides[key]},'after':overrides[key]});r.update(overrides[key])
 if key in author_map:r['authors']=author_map[key]
draft_names=[('Verifiable Attenuated Delegation for AI Agent Chains','Rafael Asor'),('OAuth 2.0 Agent Authorization Explicit Revocation','Meiling Chen, Li Su'),('Authorization Evidence and Audit Trail for OAuth 2.0 Access Tokens','Dapeng Liu, Judy Zhu, S. Krishnan, Aaron Parecki'),('Mission-Bound Authorization for OAuth 2.0','Karl McGuinness'),('Binding Agent Dialogs to WIMSE and OAuth Credentials','T. Reddy, Z. Sarker'),('Credential Delegation Protocol for AI Agents in Multi-System Environments','Kieran Sweeney'),('Evidence Binding for AI Agent Credentials','Shameer Thaha, Shaibi Shamsudeen'),('Revocation Closure and Authority Epochs for Agent Delegation','Deonté Watts')]
for r in records:
 if r['id'].startswith('D'):
  t,a=draft_names[int(r['id'][1:])-1];r['draft_id']=r['title'];r['title']=t;r['authors']=a;r['venue']='个人Internet-Draft；进行中的工作' if r['id']!='D05' else 'Internet-Draft；已读正文，工作组采纳状态待核'
official='''
O01|National Institute of Standards and Technology|2025|Digital Identity Guidelines Authentication and Authenticator Management|NIST SP800-63B-4|https://pages.nist.gov/800-63-4/sp800-63b.html|认证因素与会话相关规定
O02|Bitwarden|持续更新|Bitwarden Security Whitepaper|官方产品文档|https://bitwarden.com/help/bitwarden-security-white-paper/|客户端加密、密钥管理与共享保护
O03|FIDO Alliance|持续更新|Passkeys|官方技术说明|https://fidoalliance.org/passkeys/|公钥凭据、同步与设备绑定
O04|T. Lodderstedt, S. Dronia, M. Scurtescu|2013|OAuth 2.0 Token Revocation|RFC7009|https://www.rfc-editor.org/rfc/rfc7009.html|摘要与第2节，令牌及适用关联材料失效
O05|J. Richer|2015|OAuth 2.0 Token Introspection|RFC7662|https://www.rfc-editor.org/rfc/rfc7662.html|令牌状态与上下文查询
O06|T. Lodderstedt, J. Richer, B. Campbell|2023|OAuth 2.0 Rich Authorization Requests|RFC9396|https://www.rfc-editor.org/rfc/rfc9396.html|authorization_details细粒度表达
O07|T. Lodderstedt, J. Bradley, A. Labunets, D. Fett|2025|Best Current Practice for OAuth 2.0 Security|RFC9700|https://www.rfc-editor.org/rfc/rfc9700.html|OAuth安全最佳实践
O08|1Password|2026|About the Security of 1Password for Agents|官方安全说明|https://support.1password.com/1password-for-agents-security/|Accepted risks与保证范围
O09|E. Oyibo|2026|How to Give AI Agents Access to User Accounts without Exposing OAuth Tokens|Nango官方教程|https://nango.dev/blog/how-to-give-ai-agents-access-to-user-accounts-without-exposing-oauth-tokens|Agent Sessions工具、连接、终止与过期
O10|Google|持续更新|Using OAuth 2.0 for Web Server Applications|官方开发文档|https://developers.google.com/identity/protocols/oauth2/web-server|撤销及关联授权说明
O11|Microsoft|持续更新|user revokeSignInSessions|Microsoft Graph v1.0|https://learn.microsoft.com/en-us/graph/api/user-revokesigninsessions?view=graph-rest-1.0|刷新令牌、Cookie和传播延迟
O12|H. Birkholz, A. Delignat-Lavaud, C. Fournet, Y. Deshpande, S. Lasker|2026|An Architecture for Trustworthy and Transparent Digital Supply Chains|RFC9943 SCITT|https://www.rfc-editor.org/rfc/rfc9943.html|第5至7节及9.1至9.3，透明记录、真实性和选择性提交边界
O13|B. Laurie, E. Messeri, R. Stradling|2021|Certificate Transparency Version 2.0|RFC9162 Experimental|https://www.rfc-editor.org/rfc/rfc9162.html|Merkle包含与一致性证明；实验性RFC
O14|Ramesh Rampertab|2026|Replayable Authority Histories for Auditing Automated Agents|个人Internet-Draft00|https://datatracker.ietf.org/doc/html/draft-rampertab-audit-agent-authority-history-00|摘要、第9至12节定位，历史、未决责任及可选零知识证明
O15|HashiCorp|持续更新|Lease Renew and Revoke|Vault官方文档|https://developer.hashicorp.com/vault/docs/concepts/lease|动态秘密租约与撤销
O16|Amazon Web Services|持续更新|Obtain Credentials|AgentCore官方文档|https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/obtain-credentials.html|工作负载与用户身份用于凭据取得
O17|Microsoft|2026|Agent Identities Service Principals and Applications|Entra Agent ID官方文档|https://learn.microsoft.com/en-us/entra/agent-id/agent-service-principals|蓝图、sponsor与代理审计
O18|Alibaba Cloud|2026|What Is Agent Identity|官方产品文档|https://www.alibabacloud.com/help/en/agentidentity/what-is-agent-identity|工作负载身份、Token Vault和取得策略
'''
for line in official.strip().splitlines():
 key,a,y,t,v,u,l=line.split('|')
 records.append({'id':key,'title':t,'authors':a,'year':y,'venue':v,'url':u,'local_path':'','reading_scope':l,'verification_status':'已核验' if key in ['O04','O08','O09','O11','O12','O13','O14','O16','O17','O18'] else '部分核验','verification_scope':'本次使用的条文、产品声明或来源定位；非部署实测','limitations':'规定或产品声明的范围，实际部署另验','category':'官方规范与工程文档'})
new=[
{'id':'N01','title':'Threshold group testing','authors':'Peter Damaschke','year':'2006','venue':'General Theory of Information Transfer and Combinatorics，LNCS4123，707–718','url':'https://research.chalmers.se/en/publication/24449','reading_scope':'机构题录与原始摘要；完整定理与证明待取得','method':'阈值间允许任意回答的群测','limitations':'目标为集合恢复并允许由阈值差限定的错误；与一比特安全判定的完整归约仍待核'},
{'id':'N02','title':'Updates to OAuth 2.0 JSON Web Token (JWT) Client Authentication and Assertion-Based Authorization Grants','authors':'M. B. Jones, B. Campbell, C. Mortimore, F. Skokan','year':'2026','venue':'RFC10070，November2026，Standards Track','url':'https://www.rfc-editor.org/rfc/rfc10070.html','reading_scope':'第1、4至6节相关条款','method':'收紧客户端认证JWT的audience及显式类型说明','limitations':'客户端认证与授权授予两种用途分开；迁移兼容性按第6节处理'},
{'id':'N03','title':'Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud','authors':'Arnar Birgisson, Joe Gibbs Politz, Úlfar Erlingsson, Ankur Taly, Michael Vrable, Mark Lentczner','year':'2014','venue':'NDSS2014','url':'https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/','reading_scope':'作者机构题录与摘要，会议入口交叉核对','method':'链式MAC与衰减性caveats','limitations':'P27中具体基线实现与Macaroon一般能力分别比较，完整协议映射待核'}]
for r in new:r.update({'local_path':'','verification_status':'已核验' if r['id']=='N02' else '部分核验','verification_scope':'本次明确阅读范围','category':'本次定向补充'});records.append(r)
src=json.loads((ROOT/'research_main_innovation/main_topic_selection/ae_multi_attempt_revocation_review_2026_11_09/SOURCE_AND_COVERAGE.json').read_text(encoding='utf-8'))
for i,s in enumerate(src['sources'][:4],1):
 records.append({'id':f'CN{i:02d}','title':s['title'],'authors':'、'.join(s['authors']),'year':re.search(r'20\d\d',s['publication'])[0],'venue':s['publication'],'doi':s.get('doi',''),'url':s['url'],'local_path':'','reading_scope':('本次官方题录与摘要；原文章节范围复用L15：'+s['read_scope']) if i<4 else '仅原登记题录线索','verification_status':'待核验' if i==4 else '部分核验','verification_scope':'来源和所列范围，部分历史章节尚未本轮独立重读','limitations':s.get('limits','按原登记范围使用'),'category':'国内相关研究'})
q=next(r for r in json.loads((OUT/'data/pdf_catalog.json').read_text(encoding='utf-8')) if '2410.03948v4' in r.get('first_page',''))
records.append({'id':'Q01','title':'Unidirectional Key Update in Updatable Encryption, Revisited','authors':'Mariusz Jurkiewicz, Kamila Prabucka','year':'2025','venue':'Fundamenta Informaticae194(4)，Article4；arXiv2410.03948v4','doi':'10.46298/fi.14425','url':'https://arxiv.org/abs/2410.03948v4','local_path':q['path'],'sha256':q['sha256'],'reading_scope':'本次首页与版本定位；原游戏分析取自L07','verification_status':'部分核验','verification_scope':'题录、版本和本地源匹配；攻击证明本轮未独立重证','limitations':'期刊打印算法、独立采样与作者实现分别有证据责任','category':'密码学支线原始对象'})
for r in records:
 if r['id']=='L14':r['reading_scope']='全文，包括C1至C7、P1至P4与E1至E7'
 if r['id']=='L15':r['reading_scope']='全文，包括来源、覆盖与失败下载记录'
 r.setdefault('doi','');r.setdefault('arxiv_id','');r.setdefault('verification_scope','按本次实际读取范围，未重跑实验或外部证明审查')
(OUT/'data/source_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'data/citation_corrections.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
core={r['id']:r for r in records if r['id'].startswith('P')}
for filename in ['03_文献来源与证据记录.md','05_核心论文深度分析.md']:
 p=OUT/filename;t=p.read_text(encoding='utf-8')
 for r in core.values():
  if r.get('title_original'):t=t.replace(r['title_original'],r['title'])
 t=t.replace('完整攻击权限、可信组件与失败模型待核','完整攻击权限、可信组件与失败模型继续按对应正文范围核验')
 if filename.startswith('05'):
  t=t.replace('客户端查询撤销记录时保护索引与数据库内容，认证目标是服务器保存的记录；具体腐化和服务器假设需按协议章节继续核对。','客户端查询撤销记录时保护索引与数据库内容。物理页7采用any-trust假设，至多n−1个撤销权威受损；信道保密完整性成立。数据库复制在作者范围外，真实实时性需要能接触权威。')
  t=t.replace('物理页2,5；','物理页2,5,7；').replace('物理页1,4；[公开来源](https://doi.org/10.1145/3808103)','物理页1,4,6；[公开来源](https://doi.org/10.1145/3808103)')
 p.write_text(t,encoding='utf-8')
lines=['# 参考文献与来源清单','','## 编号与核验含义','','全套文件统一使用P、D、L、O、N、CN、Q前缀和两位序号。P为45篇核心论文，D为8份本地草案，L为15项项目证据，O为规范和工程文档，N为本次定向补充，CN为国内来源，Q为密码分析对象。题录采用作者、年、完整标题、载体及原始入口格式。','', '“已核验”只针对本次所引题录和明确事实；完整证明审查与复现实验单独登记。“部分核验”明确剩余范围。“待核验”条目保留为线索，退出主报告实质结论。','']
for r in records:
 lines += [f"## {r['id']}",'',f"[{r['id']}] {r['authors']}（{r['year']}）。{r['title']}。{r['venue']}。",'',f"- 官方或作者入口：[来源链接]({r['url']})。"]
 if r['doi']:lines.append('- DOI：`'+r['doi']+'`。')
 if r.get('draft_id'):lines.append('- 版本：`'+r['draft_id']+'`。')
 if r.get('local_path'):lines.append(f"- 原件：[本地文件]({Path(r['local_path']).as_posix()})。")
 if r.get('sha256'):lines.append('- SHA256：`'+r['sha256']+'`。')
 lines += [f"- 阅读范围：{r['reading_scope']}。",f"- 核验状态：{r['verification_status']}。{r['verification_scope']}。",f"- 限制：{r['limitations']}。",'']
stats=collections.Counter(r['verification_status'] for r in records)
(OUT/'09_参考文献与来源清单.md').write_text('\n'.join(lines),encoding='utf-8')
report='''# 文献及事实核验报告

## 方法与结论口径

逐项检查本地文件、论文身份、版本、题录和本次使用的事实。45篇核心PDF均由本次ARS结构预检给PASS，哈希与页码保存在data/pdf_catalog.json。14篇进行定点机制核验，31篇采用摘要或首页级证据。字段与来源级状态见09，机器提取与完整证明核验分别评价。

部分DOI或出版方入口返回403、不可访问或BotStopper。保留失败回执，采用可读的作者稿、官方会议记录、机构页面或已在本会话读取的同日原始来源。单个入口失败保持其访问含义。CN04完整来源仍待核，主报告仅在限制部分登记。

## 影响研究判断的核验与修正

| 项目 | 原稿或版本风险 | 本次处理与证据 |
|---|---|---|
| 当前课题 | 11月6日A-E决定与旧窄题目覆盖较新修订 | 主线采用L01的全生命周期系统，链辅助单列；L03和L04保留理论后继 |
| RFC7009 | 将其概括为只撤销孤立字符串 | 摘要与第2节包含适用关联令牌失效，[O04] |
| 草案地位 | 由正文Workgroup字段推出正式采纳 | 7份可读Datatracker明确individual；D05正文可读，采纳状态待核；8份均按Internet-Draft引用 |
| P26 | 本地首页2018、Conference17、占位DOI | arXiv2601.08012与官方ICSE2026 NIER记录匹配；正式DOI为10.1145/3786582.3786839 |
| P34 | 本地DOI nnnnnnn | 保留本地2025稿，另登记正式DOI10.1145/3796519；正式内容差异待核 |
| P39 | 本地模板DOI nnnnnnn | ASE2026与机构记录提供10.1145/3832783.3837413；本地v4和正式版分列 |
| P38 | 本地题名含Attack，正式题名省略 | 正式AAAI40(42)35811–35819，DOI10.1609/aaai.v40i42.40895，保留题名版本差异 |
| P43 | 首次提交年与v3修订年混用 | 2025首次提交，v3于2026-05-14修订，引用明确版本 |
| P07 | 早期速览写42/46且正式出处未明 | 当前本地摘要为40家COSF与8家OaaS额外威胁，正式IEEE S&P DOI已定位 |
| P11 | PMLR卷号244 | 正式题录为286卷355–387页 |
| P37 | 将4.67%解读为泄漏减少 | 原文明确为redactor gate触发率，保留实际指标 |
| P45 | 以零完成不安全效果推出零不安全权威 | 未执行草稿仍有0.0909–0.2727，不同结果分开 |
| P24 | 亚秒、大规模结果隐去信任条件 | 定点补读页7：any-trust、至多n−1受损、信道条件和复制范围外 |
| P27基线 | 将作者所测Macaroon变体外推为整个机制能力 | N03作者摘要明确支持衰减与上下文caveats；改为限定基线实现比较 |
| 本地校准 | 完成、故障触发和清理分母遗漏 | L09保留576次、A/AB激活0、156未结条件、240触发及144未到达触发点 |
| 关闭判据 | 来源有歧义就一律无法关闭 | L14 E1在容量饱和和可靠失效下允许关闭，E2才是具体共同信息障碍 |
| 链证据 | 普通锚定可证明原生事实和完整性 | O12第9.2、9.3区分声明准确性与参与完整性；L14 E2保持信息边界 |
| T3/T+ | 将显示上界差、ETH紧性写成实现优势 | L04两个族被强组合处理，严格实例仍缺 |

## 定向新增来源

新增3项独立登记来源：N01阈值群测前作、N02最新OAuth客户端断言规范、N03Macaroons基础工作。N01与N03为摘要或题录级对照，完整覆盖归约保留待核；N02实际核对第4、5节及兼容性说明。其他新增公开访问属于已有资料的题录或状态复核，不计作新论文。

N02的范围限客户端认证JWT：aud以授权服务器issuer identifier为唯一值。授权授予断言的接收方规则另有分支。显式typ属于建议，规范还讨论因旧客户端兼容而形成的迁移次序。该区别已纳入主报告。[N02]

## 国内来源与失败副本

CN01与CN03官方期刊页面匹配题录，CN02官方电子期刊页面给出作者、刊期与DOI。章节评价部分复用L15的实际范围，保留原始阅读限制。CN03本地PDF截断，网页与本地副本状态分别管理。CN04只保留原登记，完整正文待核。

PDF目录还包含一个空的GroupActions文件。两份失败副本均保持原状，其本地文本退出本次证据。机器解析出现过字体映射警告；结构PASS只验证结构，公式和语义采用已读清晰文本及规范条款，完整页面视觉与证明认证仍按实际范围登记。

## 引用一致性与剩余责任

全套来源ID映射到09和data/source_records.json。核心论文编号在各文件保持一致，标题规范化及DOI修订见data/citation_corrections.json。主报告末尾列其实际引用来源；未核线索另列。最终自动检查覆盖未定义ID、失效本地路径、占位文本、重复ID和输出数量。

本次未执行作者实验、原生认证请求、新机制实现、全数据库PRISMA检索、外部人工证明评审或第三方模型评审。已完成的是来源与事实分项核验及研究综合。剩余证明、可达性、优先权和成本证据按07与08保留。
'''
(OUT/'10_文献及事实核验报告.md').write_text(report+'\n\n来源状态统计：'+ '，'.join(f'{k}{v}项' for k,v in stats.items())+'。\n',encoding='utf-8')
(OUT/'data/verification_stats.json').write_text(json.dumps({'total_sources':len(records),'source_status_counts':dict(stats),'core_papers':45,'targeted_deep_papers':14,'supplemental_sources':3,'supplemental_papers':2,'local_drafts':8,'local_evidence':15,'public_full_text_proof_reviews':0},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sources':len(records),'status':dict(stats),'corrections':len(changes)},ensure_ascii=False))
