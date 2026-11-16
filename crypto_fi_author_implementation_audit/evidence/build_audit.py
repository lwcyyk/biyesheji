"""Public-source/static provenance audit and reproduction specification authoring.
No downloaded cryptographic module is imported or executed.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,re,sys,tarfile
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_author_implementation_audit';EV=OUT/'evidence';SRC=OUT/'sources';V=BASE/'crypto_fi_research_manuscript_v2_1';P=BASE/'crypto_fi_publication_impact_audit'
def read(p):return Path(p).read_text('utf-8-sig')
def jd(p):return json.loads(read(p))
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def rec(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def link(p,label=None,line=None):return '['+(label or Path(p).name)+']('+str(p).replace('\\','/')+((':'+str(line)) if line else '')+')'
def unpack(r):
    sc=r.get('structuredContent',{})
    return json.loads(sc['content'])

current=unpack(jd(EV/'upstream_commit.json')['result'])
history=unpack(jd(EV/'upstream_detail_1.json')['result']['value'])[0]
releases=unpack(jd(EV/'upstream_detail_2.json')['result']['value'])
tree=unpack(jd(EV/'upstream_tree.json')['result'])
codefile=SRC/'upstream_frodokem_2023.py';code=read(codefile);node=ast.parse(code)
blob=hashlib.sha1(b'blob '+str(codefile.stat().st_size).encode()+b'\0'+codefile.read_bytes()).hexdigest()
expected=next(x for x in tree['tree'] if x['path']=='FrodoKEM/python3/frodokem.py')['sha']
assert blob==expected=='731cb0eae2c4cf2f01bb6ec4dc9fd7e1e322189f'
assert codefile.read_bytes()==(SRC/'upstream_frodokem_2026.py').read_bytes()
methods={x.name:dict(line=x.lineno,end_line=x.end_lineno) for x in ast.walk(node) if isinstance(x,ast.FunctionDef)}
selected=['error_distribution','D','q','n','mbar','nbar','B','len_seedA','len_seedSE','len_chi','len_salt']
paramfacts={}
for n in [640,976,1344]:
    fn=next(x for x in ast.walk(node) if isinstance(x,ast.FunctionDef) and x.name==f'setParamsFrodo{n}')
    facts={}
    for x in fn.body:
        if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Attribute) and x.targets[0].attr in selected:
            facts[x.targets[0].attr]=dict(value=ast.literal_eval(x.value),line=x.lineno)
    paramfacts[str(n)]=facts
upstream=dict(role='OFFICIAL_BASELINE_ONLY_NOT_AUTHENTICATED_AUTHOR_UE',repository='https://github.com/microsoft/PQCrypto-LWEKE',current_commit=current['sha'],current_commit_date=current['commit']['author']['date'],paper_date_bounded_path_commit=history['sha'],historical_commit_date=history['commit']['author']['date'],path='FrodoKEM/python3/frodokem.py',git_blob_sha1=blob,local_files=[rec(codefile),rec(SRC/'upstream_frodokem_2026.py')],byte_identical_two_versions=True,methods=methods,parameter_facts=paramfacts,releases=[dict(tag=x.get('tag_name'),published_at=x.get('published_at'),url=x.get('html_url')) for x in releases],tree_truncated=tree['truncated'],citation_archive_manifest_files=[x['path'] for x in tree['tree'] if re.search(r'citation|\.zenodo|codemeta',x['path'],re.I)],code_imports_or_executions=0)
dump(EV/'UPSTREAM_STATIC_FACTS.json',upstream)

routes=[
 dict(id='R01',basis='Target DOI/arXiv from frozen paper; current publisher export is an explicit metadata link',url='https://fi.episciences.org/17222/jsonv2',result='Current version4, same arXiv links and PDF resource; no software artifact relation in visible export',state='CHECKED_NO_AUTHOR_UE_LINK_LOCATED',receipts=['web_01.json','web_04.json','web_05.json','ARCHIVE_AND_IDENTITY_METADATA.json'],reopen='A new publisher relation, supplement, software DOI or versioned artifact link'),
 dict(id='R02',basis='Four public arXiv source packages acquired and sealed in prior publication audit',url='https://arxiv.org/abs/2410.03948',result='Reuse four-package inventory; v4 contains6 typesetting files. Current Code/Data anchors name general services, without paper-specific code URL',state='CHECKED_TYPESSETTING_ONLY',receipts=['ARXIV_CODE_LINKS.json','web_01.json','web_08.json'],reopen='New source package, arXiv comment or paper-specific artifact URL'),
 dict(id='R03',basis='Target full author name/email plus WAT official contact page and primary JTIT ORCID link',url='https://www.wcy.wat.edu.pl/pl/instytuty/imk/kontakt',result='Mariusz name and paper email match official institution; JTIT1581 explicitly links ORCID0000-0002-6314-4381. DBLP labels its own ORCID mapping inferred/pending',state='IDENTITY_LINKED_CODE_OWNERSHIP_UNRESOLVED',receipts=['web_01.json','web_02.json','web_03.json'],reopen='Author/institution/ORCID explicitly linked software repository'),
 dict(id='R04',basis='Official WAT staff page hyperlink58 identifies a specific institutional author profile',url='https://repo.bg.wat.edu.pl/info/author/WAT839fd48da58147e29ba6d882b5bbf563',result='Staff-link author page403; repository root timeout; targeted indexed queries did not yield target artifact',state='ACCESS_LIMITED',receipts=['web_04.json','web_05.json','web_07.json'],reopen='Normal public access or lawful institutional export with all external artifact links'),
 dict(id='R05',basis='Primary journal verified ORCID; narrower person endpoint follows full record timeout',url='https://orcid.org/0000-0002-6314-4381',result='Webpage needsJavaScript; public record request timeout; person API tool unavailable and direct TLS EOF. Researcher website fields not obtained',state='ACCESS_LIMITED_FIELDS_UNKNOWN',receipts=['web_02.json','web_04.json','INITIAL_PUBLIC_RETRIEVAL.json','ARCHIVE_AND_IDENTITY_METADATA.json'],reopen='Public person/record export or accessible researcher-url list for this exact ORCID'),
 dict(id='R06',basis='Target coauthor name/email and DBLP coauthor link124',url='https://dblp.org/pid/394/4071.html',result='Coauthor/paper relation visible. No author-specific ORCID was displayed. Institution staff list did not containPrabucka; linked WAT profile news403, indexed academic-profile lead limited',state='AUTHOR_UE_LINK_UNRESOLVED',receipts=['web_02.json','web_03.json','web_04.json','web_06.json'],reopen='Paper/institution-author profile with explicit software link or researcher identifier'),
 dict(id='R07',basis='Publisher names Central European Conference on Cryptology2024; official2025 site links2024 host; participant university lists exact conference-program URL',url='https://cecc2024.wat.edu.pl/conference-program',result='2024 root502 and program URL inaccessible. Similar acronym European Interdisciplinary Cybersecurity Conference was excluded as another event',state='ACCESS_LIMITED',receipts=['web_04.json','web_05.json','web_06.json','web_07.json','web_08.json','web_09.json'],reopen='Lawful2024 program/abstract/supplement archive with target title and outbound links'),
 dict(id='R08',basis='Original paper funding identifier DOB/002/RON/ID1/2018 resolves exact project ISSIP-PKI',url='https://www.wcy.wat.edu.pl/wydzial/badania-rozwoj/projekty-badawcze',result='Official WAT and KenBIT project pages confirm project/institution relation; visible pages supply no target UE release. Funding relation alone provides no code attribution',state='CHECKED_PROJECT_LINK_ONLY',receipts=['web_04.json','web_05.json','web_06.json'],reopen='Project deliverable explicitly naming target paper, repository/version and code'),
 dict(id='R09',basis='Target DOI/arXiv/title and source-linked author identity permit archive metadata queries',url='https://zenodo.org/',result='Exact indexed archive queries did not locate target artifact; Zenodo web/API inaccessible or TLS EOF; DataCite API TLS EOF. Archive totals not obtained',state='INDEX_SCOPE_CHECKED_API_ACCESS_LIMITED',receipts=['web_01.json','web_03.json','web_04.json','web_08.json','ARCHIVE_AND_IDENTITY_METADATA.json'],reopen='Archive record DOI/ID, author-linked upload, or restored normal API access'),
 dict(id='R10',basis='Verified paper/WAT email identifiers plus author/title',url='https://github.com/',result='Two exact email queries returnedempty; title+coauthor returnedRSS records. Prior exact arXiv/UE.TG searches and issue queries reused. Codeberg search reportedrobots block',state='CHECKED_NO_AUTHENTICATED_CANDIDATE',receipts=['identity_code_query_0.json','identity_code_query_1.json','identity_code_query_2.json','web_07.json'],reopen='Explicit author/paper/institution link identifying repository owner and immutable version'),
 dict(id='R11',basis='Official Frodo project code link in previously sealed primary reading; original paper claims basis on official reference implementation',url='https://github.com/microsoft/PQCrypto-LWEKE',result='Pinned official baseline current commit and paper-date-bounded Python blob match exactly; release and full tree inspected; selected blob has noTG/Upd/Ord/Tensor methods',state='AUTHENTICATED_UPSTREAM_BASELINE_ONLY',receipts=['upstream_commit.json','upstream_tree.json','upstream_detail_0.json','upstream_detail_1.json','upstream_detail_2.json','upstream_historical_file.json','UPSTREAM_STATIC_FACTS.json'],reopen='Authenticated author fork/patch/adapter explains UE extension, versions/config and timing driver'),
 dict(id='R12',basis='Current arXiv Code/Data anchors explicitly name CatalyzeX/alphaXiv services',url='https://arxiv.org/abs/2410.03948',result='Anchors point to general services; paper-title code-finder query did not locate an associated author implementation in returned results',state='CHECKED_GENERIC_SERVICE_LINKS_ONLY',receipts=['ARXIV_CODE_LINKS.json','web_08.json'],reopen='Paper-specific code-finder record with independently verified author association')]
for x in routes:
    x['receipt_files']=[rec(EV/p) for p in x.pop('receipts')]
    x['recorded_at_asia_shanghai']=datetime.now(timezone(timedelta(hours=8))).isoformat()
dump(EV/'PUBLIC_ROUTE_LEDGER.json',dict(schema='fi-author-implementation/public-route-ledger/1',cutoff='2026-11-10 Asia/Shanghai',routes=routes,scope='Bounded discovered public routes, plus precise access gaps; not a global nonexistence assertion'))

webqueries=[]
for p in sorted(EV.glob('web_*.json')):
    d=jd(p);webqueries.append(dict(receipt=rec(p),route_basis=d['route_basis'],queries=[q['q'] for q in d['request'].get('system2_search_query',[])],retrieved_at_UTC=d['retrieved_at_UTC']))
dump(EV/'SEARCH_AND_RETRIEVAL_SCOPE.json',dict(web_calls=len(webqueries),new_web_query_count=sum(len(x['queries']) for x in webqueries),batches=webqueries,new_identity_code_queries=3,inherited_publication_audit_search=rec(P/'evidence/SEARCH_LEDGER.json'),raw_public_HTTP_batches=[rec(EV/f) for f in ['INITIAL_PUBLIC_RETRIEVAL.json','ARCHIVE_AND_IDENTITY_METADATA.json']],no_error_interpreted_as_zero_hit=True))

config=[]
for n in [640,976,1344]:
    f=paramfacts[str(n)]
    for primitive in ['AES','SHAKE']:
        config.append(dict(name=f'FrodoPKE-{n}-{primitive}',reported_in_paper='PDF21 Table1(AES) orTable2(SHAKE)',normative_numeric_fields={k:f[k]['value'] for k in ['n','D','q','mbar','nbar','B']},author_source_location=None,author_config_export=None,author_implementation_status='UNRESOLVED',result_A_transfer='UNRESOLVED',result_B_transfer='UNRESOLVED',numeric_reference_comparison_to_A='DIFFERS:fixed official profile vs growingCF1; higher profiles also use anotherchi',numeric_reference_comparison_to_B=('MAPPED_NUMERIC_SUBFIELDS_ONLY' if n==640 else 'DIFFERS:resultB is fixed640'),evidence_scope='Reported variant and official baseline parameters only; no source-certified author UE configuration'))

provenance=r'''
# 作者实现公开溯源与模型迁移核查：来源取证

2026-11-10，Asia/Shanghai。身份：**INFORMED_PUBLIC_ARTIFACT_PROVENANCE_AND_STATIC_MODEL_TRANSFER_AUDIT**。本轮以 **WAITING_FOR_AUTHOR_ARTIFACT** 完成来源取证和模型对应裁决：实际检查的公开路线尚未取得可认证的作者UE实现、配置或更新后消息比对轨迹。公开可访问记录、索引未命中和访问错误分别登记，作者工件是否存在于其它位置保持未知。

## 1. 固定研究对象与历史输入

目标为Mariusz Jurkiewicz、Kamila Prabucka的FI论文，DOI [10.46298/fi.14425](https://doi.org/10.46298/fi.14425)，arXiv:2410.03948v4。当前期刊JSON导出仍登记version4，关联v2/v3预印本及v4 PDF，未在该导出发现软件工件关系。当前arXiv页面仍列v1–v4。采用已封存的23页期刊/v4 PDF，SHA256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`；本轮没有重新下载该PDF。

原论文PDF20–22与Table1/2报告Python、NumPy及基于官方参考实现，配置为640/976/1344各AES/SHAKE共六组，计时操作为KG、Enc、Dec、TG、Upd共五类，100次独立运行用于计时。更新后消息比对的实际流程、成功分母、深度和原日志仍缺认证材料。

读取v2.1的版本、勘误与依赖记录，并复用发表影响审计的原声明映射、软件缺项、31条检索查询与源包清单。v2.1的INC976已闭合；A/B均使用χ640，其完整模型与既有数学状态保持。起始快照覆盖两个指定目录144个历史文件，规范化封存载荷分别核验；结束时再次核对。

## 2. 作者身份和代码归属的认证边界

| 线索 | 原始/可追溯依据 | 当前支持 |
|---|---|---|
| Mariusz Jurkiewicz | 目标PDF1的全名/机构邮箱；WAT官方IMK联系页相同姓名与邮箱 | 作者与机构联系对应 |
| ORCID0000-0002-6314-4381 | JTIT原始文章1581明确把Mariusz/WAT链接到该ORCID | 有原始期刊支持的研究者标识；DBLP自身另标推断/待验证 |
| WAT作者记录 | 官方员工页把Jurkiewicz明确链接至WAT839fd48da58147e29ba6d882b5bbf563 | 机构作者页链接获认证；页面内容403，外链列表未取得 |
| Kamila Prabucka | 目标PDF1的全名/机构邮箱；目标与同作者DBLP记录相连 | 目标作者关系明确；本轮未取得专属ORCID或代码主页认证 |
| 同名账号 | 需作者、论文或机构的显式外链或可验证声明 | 名字或搜索关键词匹配只形成待核线索；本轮未形成已认证的作者代码候选 |

ORCID网页需要JavaScript，完整record请求超时，person接口工具不可访问且直接请求TLS EOF。故其researcher-urls内容保持未知。WAT员工名录未显示Prabucka不承担任职状态判断。第三方索引中的其它姓名拼写不覆盖目标原文的全名。

## 3. 新增公开路线及结果

ROUTE_TABLE

每条路线的定位依据、原始URL、获取时间、工具原始返回及重开输入见PUBLIC_ROUTE_LEDGER。新增28条网页查询分布在9次调用；新做3条以机构邮箱/作者关系为依据的GitHub代码查询。旧题名、arXiv、UE.TG和issue检索按原回执复用。批次合并返回不被拆成虚构的逐查询零命中数字。

具体受阻包括：机构作者页403、出版库根页超时、ORCID公开API超时/TLS错误、CECC2024根页502和program不可访问、Zenodo/DataCite API TLS错误、Codeberg robots限制。Crossref本轮直接请求超时；使用已封存Crossref记录，并以本轮取得的期刊JSON导出交叉定位。Zenodo/DataCite总命中数保持未知。可访问的项目页面显示ISSIP-PKI及WAT关系，未提供目标UE发布；资助关系本身不认证代码归属。

会议名依据期刊专刊和官方后续会议的历史链接，明确为Central European Conference on Cryptology2024，区别于同缩写的Cybersecurity会议。后发现的conference-program路径亦已单独尝试。源包、机构/项目、关联工件、归档和身份代码线索的当前可用分支已处理；恢复访问或新工件链接将重开相应路线。

## 4. 已取得的代码：官方上游参照

本轮认证的代码归属为Microsoft PQCrypto-LWEKE官方Frodo基础仓库，其关联依据来自官方Frodo项目的代码链接和既有原始来源记录。该角色按上游参照登记，作者UE归属另有专门证据门槛。

| 项目 | 固定证据 |
|---|---|
| 当前仓库commit | `e1edeb3af1fae0d5727683bd2f5465280ec2437a`，提交时间2026-09-15T16:08:15Z |
| 首次预印本日期之前的所选文件最后提交 | `6f92cb7bb5e1a060c8b40913a003ed0aa63bd080`，2023-08-26T02:50:12Z；查询until=2024-10-04T22:16:20Z |
| 文件 | FrodoKEM/python3/frodokem.py，31329字节；两commit下该文件逐字节相同 |
| Git blob SHA1 | `731cb0eae2c4cf2f01bb6ec4dc9fd7e1e322189f`，本地按Git blob编码复核 |
| SHA256 | `61f38e04fa99605489f596f6c62275fc7e7d03052d0dd507cacdb606ef69a15e` |
| release | 可见v1.0发布于2024-11-27T23:27:34Z；属于上游发布 |
| 引用/归档清单 | 固定完整树返回truncated=false，未见名称匹配CITATION、.zenodo或codemeta的文件 |

固定文件标记CC0-1.0、Created by Douglas Stebila。其函数包括KEM、基础矩阵/采样/编解码，未定义TG、Upd、Ord或Tensor。其内部矩阵例程使用Python列表/int，论文作者报告的NumPy UE改写仍需取得。历史文件相同证明这个上游blob在论文之前已存在；它不认证作者究竟采用哪个版本、改写或驱动。未导入或执行下载代码，未安装其依赖。

静态对应的文件/行号见IMPLEMENTATION_MODEL_MAPPING，commit、tree、release、原始文件和哈希见UPSTREAM_STATIC_FACTS及原始GitHub回执。上游公开issue35的CDF勘误已在v2.1认证，既有issue检索也未提供作者UE关联工件。

## 5. 取证裁决和最小补交

**可认证作者UE源码、六组配置、运行入口和带消息比对的真实运行记录，当前取得数均为0。** 这是本轮取证状态。作者曾报告实现与计时；现有材料不足以把该实现身份认证到一个可读取的版本。

最小补交材料为：

1. 作者、论文或机构明确关联到目标DOI的仓库/归档链接；或可认证声明与代码包SHA256。版本须可固定到commit、tag解析的commit或归档版本。
2. 包含Setup/KeyGen、Enc、TG、Upd、Dec、Ord/Tensor、六配置与计时driver的完整源文件，附依赖版本和实际入口/命令。
3. 一组640参数导出及随机性/算术说明，配一条未按结果筛选、具有原消息及初始/更新后消息比对的完整轨迹。六配置全部映射及原性能数字核准还需各配置与原计时日志。

获得后按MINIMAL_REPRODUCTION_SPEC的来源认证→参数/随机性/算法/位序/算术静态对应→入口冻结→单轨迹记录→分母与模型裁决顺序核验。本轮未联系作者、发送消息或运行UE。既有理论结果和应用优先权状态保持原范围。
'''
route_table='| 路线 | 新定位依据 | 结果/状态 | 重开条件 |\n|---|---|---|---|\n'
shorts={
 'R01':('期刊/DOI导出','当前JSON仅见预印本/PDF关系','新增软件或补充工件关系'),
 'R02':('arXiv关联工件/四版源包','旧源包排版材料；当前代码锚点为通用服务','paper-specific代码或新源包'),
 'R03':('WAT/JTIT身份链','作者机构与ORCID线索成立，代码归属未闭合','作者/机构显式代码外链'),
 'R04':('机构员工页链接的精确作者ID','作者记录403、库根超时','正常访问或合法导出'),
 'R05':('确切ORCID的公开record/person','JS/API访问未完成，网站字段未知','公开record/person导出'),
 'R06':('目标 coauthor及机构公开资料','未取得专属代码/ORCID链接','作者学术主页/标识链接'),
 'R07':('精确会议名称及官方历史链接','CECC2024根502/program不可访问','2024程序/摘要/补充材料归档'),
 'R08':('原论文资助编号→ISSIP-PKI','官方项目关系可核，未见目标UE发布','明确目标论文的项目工件'),
 'R09':('DOI/ID/作者→公开归档','索引未定位；Zenodo/DataCite访问错误','归档ID、DOI或恢复访问'),
 'R10':('机构邮箱及题名+作者代码查询','空返回或RSS；没有认证代码候选','明确仓库owner及论文关联'),
 'R11':('官方Frodo上游历史/发布','上游文件已固定；UE扩展仍缺','作者fork/patch/driver'),
 'R12':('arXiv代码发现服务锚点','仅通用服务链接及有界检索','可核的paper-specific记录')}
for x in routes:
    a,b,c=shorts[x['id']];route_table+=f'| {x["id"]} {a} | {x["basis"]} | {b} | {c} |\n'
provenance=provenance.replace('ROUTE_TABLE',route_table.strip()).replace('PUBLIC_ROUTE_LEDGER',link(EV/'PUBLIC_ROUTE_LEDGER.json')).replace('UPSTREAM_STATIC_FACTS',link(EV/'UPSTREAM_STATIC_FACTS.json')).replace('IMPLEMENTATION_MODEL_MAPPING',link(OUT/'IMPLEMENTATION_MODEL_MAPPING.md')).replace('MINIMAL_REPRODUCTION_SPEC',link(OUT/'MINIMAL_REPRODUCTION_SPEC.md'))

mapping=r'''
# 作者实现与v2.1模型：静态对应和迁移条件

2026-11-10。总体状态：**WAITING_FOR_AUTHOR_ARTIFACT**。作者UE源文件与配置未取得，六组作者配置的整体静态映射均为**UNRESOLVED**。以下将论文报告、已取得的上游局部事实和条件迁移论证分别登记。上游Frodo文件的局部MAPPED/DIFFERS状态仅覆盖该上游代码。

## 1. 冻结理论对象

**A。** CF-1：λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8、B=2、独立精确χ640，既定Ord，最长n次逐样本正确；原游戏≤3n+1次调用、Δ→1。公开A先固定，攻击逐个A成立。

**B。** n=640、D=15、q=32768、m̄=n̄=8、B=2；均匀Setup、独立χ640、同一A、既定Ord、一次诚实未筛选TG/Upd、最近整数平局向上；每个抽样前固定合法128位消息。初始完整正确≥1−2^-132，更新完整错误≥99.9969655%，初始正确条件下显示下界保持。更新概率平均全部诚实币与均匀Setup。

MAPPED表示该行给定范围有具体源位置和相符证据；DIFFERS表示该范围有可定位差异；UNRESOLVED表示材料或迁移论证尚缺。多个数值子项相符只支持相应子项。

## 2. 六种报告配置的裁决

| 报告配置 | 官方数值参照(n,D,q,m̄,n̄,B) | 作者源位置/配置文件 | 对A整体迁移 | 对B整体迁移 |
|---|---|---|---|---|
| 640-AES | (640,15,32768,8,8,2) | 未取得；论文PDF21 Table1仅给名称/计时 | UNRESOLVED | UNRESOLVED |
| 640-SHAKE | 同上 | 未取得；论文PDF21 Table2 | UNRESOLVED | UNRESOLVED |
| 976-AES | (976,16,65536,8,8,3) | 未取得；论文PDF21 Table1 | UNRESOLVED | UNRESOLVED |
| 976-SHAKE | 同上 | 未取得；论文PDF21 Table2 | UNRESOLVED | UNRESOLVED |
| 1344-AES | (1344,16,65536,8,8,4) | 未取得；论文PDF21 Table1 | UNRESOLVED | UNRESOLVED |
| 1344-SHAKE | 同上 | 未取得；论文PDF21 Table2 | UNRESOLVED | UNRESOLVED |

在**规范参数比较**层面，640的六个数值子项与B相符；976/1344与固定640命题B的参数范围DIFFERS。六组固定官方数值均不同于A要求的增长D/q族，且976/1344还使用其它χ表。例如CF-1取n=640时D=80，区别于标准640的15。这里比较的是已知数值范围，作者程序是否允许扩展参数仍为UNRESOLVED。它们也不能替代CF-1的参数化实现。

## 3. 已取得上游文件的局部静态事实

代码位置均指固定blob `731cb0eae2c4cf2f01bb6ec4dc9fd7e1e322189f` 的上游Python文件，分别在2023和当前commit下取得，字节相同。当前版本与归属见来源报告。

| 类别 | 源位置 | 实际静态行为 | 对定理条件的局部判断 |
|---|---|---|---|
| 六变体分派 | L20–47 | 固定640/976/1344×AES/SHAKE六分支 | MAPPED到上游变体名称；CF-1族支持DIFFERS |
| 参数/χ | L49–164 | 三组n/D/q/m̄/n̄/B、正确质量表；lenχ=16 | 640数值与B子项MAPPED；作者UE采用情况UNRESOLVED |
| 随机源与seed | L26、457–477、505–535 | secrets字节源；KeyGen切分seed；SHAKE(0x5F∥seedSE)采S/E；Encaps用pkh/μ/salt导出seed，再以0x96展开 | 秘密seed展开与精确iid数学采样DIFFERS；需要明确计算/随机预言机迁移 |
| A | L420–455、466–470、540–541 | AES128/SHAKE128从128位seedA生成矩阵；每次KEM KeyGen生成自己的seedA | 均匀全矩阵Setup及UE跨代复用并未由此认证；上游KeyGen不能单独给UE同一A合同 |
| 采样器 | L210–219、389–418 | 从质量生成CDF；t=r>>1，严格t>T，符号位r mod2，分片逐项采样 | 若输入16位字独立均匀，表采样器子项MAPPED；seed扩展输入的联合律仍须另证 |
| 基础环运算 | L221–252 | 内部列表/Python int乘加后%q | 在内部整数调用链按目标环计算；作者报告的NumPy dtype未取得 |
| 编码/舍入 | L295–311、322–351，关键L339 | floor(K·2^B/q+0.5) mod2^B | 对标准三组规范模代表，半向上子项MAPPED；一般增长D另需数值论证 |
| 打包 | L353–387 | 逐坐标D位、每坐标高位先输出，unpack反向恢复 | 是序列化位序；UE Ord/Tensor未定义，不能直接认证gadget |
| UE层 | 全文件AST函数清单 | 公开接口为KEM KeyGen/Encaps/Decaps；无TG、Upd、Ord/Tensor | 作者UE四块与更新式整体UNRESOLVED |
| 验证与计时 | L568–662 | KEM Decaps包含再加密一致性检查；该文件无UE计时driver | 静态可执行检查不等于实跑证据，更不认证更新后消息比对 |

该上游的seedSE长度为256/384/512位，且含salt；2021规范与其它版本可能有不同seed参数。源文件头还保留“TBD,2020”说明，精确版本按commit/blob认证。论文未给作者采用的上游commit，因此这些长度、函数和行号均不赋给作者UE程序。完整静态字段由UPSTREAM_STATIC_FACTS记录，下载代码执行次数为0。

## 4. 作者UE逐项对应仍需取得的源位置

| 条件组 | 作者源位置 | 必需事实/判据 |
|---|---|---|
| 参数 | null | 六配置实际导出、χ/CDF版本、更新上限、是否支持CF-1增长参数 |
| 随机性 | null | A生成/跨代复用，KeyGen/Enc/TG/Upd的每条seed来源、长度、域前缀、切片和重复输入；公开与秘密seed分开 |
| 算法 | null | P₁/Q₁/P₂/Q₂形状与公式、R、额外噪声、拒绝筛选、重试、失败路径 |
| 位展开 | null | Ord实际输入列数和位序、Tensor行序、H·Tensor(S)=C₁S；一致置换的显式对应 |
| 算术 | null | 每个矩阵dtype、提升/截断、累加、取模/符号扩展、编码/packing/Decode舍入；底层库和机器语义 |
| 计时和正确性 | null | 五操作入口、预处理/缓存、随机性/打包是否计时、运行次数、原消息生成、初始及更新后Dec比对和异常分母 |

## 5. 分布迁移：需要的具体引理

**A的公开A与秘密噪声。** A的固定A定理允许对任意先确定A的分布平均；若实际噪声在给定公开seed/A后仍满足声明的独立χ合同，公开seed生成A本身无需均匀性。但r̂恢复的代数事实与β界分别核账：Y=HP₁+RP₂且P₂可逆时恢复R是逐样本事实；真实fresh、可逆概率及停止放大依赖噪声联合律，单个CDF边缘相符不能替代该联合律。

若能证明实际第b分支的目标攻击输出概率与理想模型之差≤η_b，则

\[
\Delta_{code}\ge\Delta_{ideal}-\eta_0-\eta_1.
\]

此处η可来自适用于相关可测输出的统计耦合，或明确的计算混合。种子必须独立/域分离，实际被暴露字段、重复输入、调用次数和损失均要入账。模型迁移所需的PRG/XOF条件与原FI完整LWE归约各有不同证明责任。

**B的均匀Setup。** 128位seed通过确定性生成器输出A，其像大小≤2^128；R_q^(640×640)有2^6144000个元素。因此A边缘律与真正均匀全矩阵的统计距离至少

\[
1-2^{128-6144000}=1-2^{-6143872}.
\]

所以该seed模型需要其它迁移路径。若可靠性事件可严格写成只通过矩阵A起作用、其余币独立的高效可测函数，可建立相应边缘生成器的计算/随机预言机混合。包含公开seed的完整视图另需注意：检查A=Gen(seedA)即可辨认与独立(seedA,均匀A)的关系，普通不暴露seed的PRG断言无法直接认证这个联合视图。实际代码是否满足所需的函数分解正是静态核查内容。

秘密seed扩展也与精确iid表律不同。若κ位seed确定性生成N个χ样本，其输出像≤2^κ；理想iid law最大原子为a^N，故像在理想law下质量≤min(1,2^κa^N)。这些熵/支撑界说明必须标明模型，不能从“每点用同一采样表”推出完整独立性。新鲜均匀seed、互异域输入及理想XOF可通过互异输入输出独立性和碰撞损失论证；具体SHAKE/AES则需要相应明确假设与有限损失。

**B的条件事件。** 记理想完整成功上界U_*与初始失败预算a_I=2^-132。若适用迁移给出实际完整成功概率≤U_*+η_E、初始正确概率≥1−a_I−η_I，则在分母为正时

\[
\Pr_{code}(E_m\mid I)\le\frac{U_*+\eta_E}{1-a_I-\eta_I}.
\]

保持显示上界0.000030345需核准右侧≤该值。只有渐近“可忽略”措辞还不足以固定640实例的相同十进制端点。一次输出或字段比对仅支持该代码/配置/币的事实，概率和条件化仍需上述输入合同或迁移界。

## 6. 位序与机器算术的纸面判据

**一致行置换。** 若H′=HΠ，Tensor′=Π^-1Tensor，且(P₁′,Q₁′)=Π^-1(P₁,Q₁)，则H′P₁′=HP₁、H′Q₁′=HQ₁；iid原始U/F/G行在固定置换下同分布。这样的匹配重排保留声明结论。只改Ord而未匹配Tensor/token行序，则gadget等式需重新核验。

**固定字宽回绕。** 若已证明每步整数加、减、乘都按2^w回绕，且D≤w，则2^D整除2^w，自然投影Z/2^w→Z/2^D为环同态。故先回绕再mod2^D与精确整数运算后mod2^D相同，即使矩阵累加超过字宽。此论证要求实际操作具有该语义，且除法、比较、位提取或浮点转换前的代表处理相容。D>w时2^w与0在机器环相同、在目标环不同，这条迁移不成立。C/C++未定义的有符号溢出、饱和/检查溢出、浮点矩阵乘法等均需各自判据。

因此，仅凭“NumPy可能溢出”不能判定作者环计算错误；也不能在缺dtype/后端证据时认证其相容。上游所见内部Python int链没有固定字宽回绕。CF-1的D随n增长，固定w实现还需参数范围或多精度证明。

**标准参数舍入。** 上游L339在规范输入0≤K<q、D≤16、B≤4时，K·2^B<2^20是精确整数，除以2^D及加1/2均为短二进制有理数；binary64可精确表示，floor给平局向上。该范围证明不自动覆盖任意增长D或未规范化中间输入。作者若使用原生round/NumPy round等平局规则，须按真实边界事件重新对应；仅函数名称类似不足以保持B的行级和逐消息概率接口。

## 7. 能改变适用范围的最小程序差异

| 待核差异（非实际发现） | 对应最小影响 |
|---|---|
| 固定D/q、χ976或χ1344 | 超出A的增长族/χ640；976/1344也超出B的固定640命题 |
| A在两代重新生成 | B的同一A残差与H分布推导需重新对应；A也须核其准确公开仿射式 |
| 复用秘密seed/相同XOF输入/相关切片 | 独立性及可逆/选择概率界需要新联合论证 |
| 按P₂秩、初始正确或输出结果筛选/重试 | 改变B的诚实未筛选分母；A的预算和选择条件也需对应 |
| Y额外加噪或P₂形状改变 | A的精确逆像/支撑接受事件可能改变，需分析实际公式 |
| Ord与Tensor/token行序不相配 | gadget抵消与实际残差改变；一致置换则按上一节处理 |
| D>w且截断、非环相容算术或不相同舍入 | 改变目标环/解码事件，需要精确数值或误差界 |
| 调用KEM Encaps/Decaps及其FO检查而非论文PKE/UE接口 | 消息、随机性和失败语义改变，需要对应真实API |

这些是收到工件后的判定分支，当前未归因给作者。它们说明哪些外部材料能扩大、缩小或改变现有结论的实现适用范围；两个理想打印模型的已登记数学结果继续保持。
'''
mapping=mapping.replace('UPSTREAM_STATIC_FACTS',link(EV/'UPSTREAM_STATIC_FACTS.json'))
mapping+='\n\n静态参照文件：'+link(codefile,'固定上游Python文件')+'；实际函数行号清单：'+link(EV/'UPSTREAM_STATIC_FACTS.json')+'；v2.1完整命题：'+link(V/'CRYPTOANALYSIS_DRAFT.md')+'。\n'

spec=r'''
# 最小复现规格：作者UE的Enc→TG→Upd→Dec轨迹

2026-11-10。规格状态：**PREPARED_ENTRYPOINT_PENDING_AUTHOR_ARTIFACT**。实际作者UE执行状态：**NOT_EXECUTED**。本规格准备材料与判据；本轮运行轨迹、正确率估计和性能重现次数均为0。

## 1. 最小外部包及入口

接收一份经作者/论文/机构明确关联目标DOI的不可变代码包或commit，包含UE driver、六配置和依赖说明。来源认证需同时满足：可验证论文关联、不可变版本/完整源码哈希、实际含TG/Upd/Ord/Tensor及调用driver。只有官方Frodo基础库或同名账号时，状态保持UNRESOLVED。

目前作者入口文件、callable和CLI argv均未取得，登记为null。收到后把真实位置写成entrypoints中的文件路径、行号、函数签名或原样argv；本规格没有假定作者提供任何自造CLI选项。来源核验可记录git commit、dirty状态、包SHA256、Python/NumPy/依赖与BLAS/平台版本，源码改动应有单独patch与哈希。

## 2. 固定输入与模型标签

最小第一条为报告640-AES或640-SHAKE之一，参数完整导出n=640、D=15、q=32768、m̄=n̄=8、B=2及χ640/CDF。选择一个在抽样前固定的128位合法消息，例如全零16字节；记录原始bytes、bit顺序和位长。A的生成方式必须实际标明为全矩阵均匀、AES seed、SHAKE seed或其它，不把它们合成一个标签。

976/1344各消息长度按ℓ=B·m̄·n̄导出，通常为192/256位；六配置分别记录。CF-1另需要参数化入口、χ640及随λ增长的D/q证明；单个标准640运行只提供一个有限配置的轨迹。程序支持范围在静态核查后再赋MAPPED/DIFFERS。

随机性规格至少列出Setup、old/new KeyGen、Enc、TG每块U/F/G、Upd R对应的源位置、seed来源/长度、域前缀、XOF输入、输出长度、切片区间、重复/共享关系和调用顺序。可重放材料需提供合成seed/输入字或完整可重现熵轨迹及生成器版本；只有哈希时记录为观察轨迹，不能登记逐币可重放。

## 3. 运行前的静态接收判据

| 顺序 | 要核验的明确条件 | 通过/差异的记录 |
|---|---|---|
| S0 来源 | 作者/机构/论文链接绑定版本，文件哈希匹配 | AUTHENTICATED或UNRESOLVED；缺关联先补证据 |
| S1 参数 | 六配置、CDF/PMF、深度、常量与输出长度导出 | 字段级MAPPED/DIFFERS并附源行 |
| S2 随机性 | A跨代合同，seed独立/复用/域/切片和XOF模型 | 精确law、需统计耦合、需计算混合或UNRESOLVED |
| S3 算法/位序 | TG四块、Upd、形状、额外项、重试，Ord/Tensor匹配 | 逐式映射与置换证据；缺项明确定位 |
| S4 算术 | dtype、每次提升/回绕/取模、符号、编码/packing/舍入 | 环同态或误差证明；条件范围明确 |
| S5 driver | 五操作计时边界、缓存/预处理、消息断言和失败日志 | 代码可执行检查与历史运行证据分别登记 |

上述步骤只做静态对应和材料准备，当前均未执行作者程序。字段齐备后，运行计划可由研究者按其授权范围实施，并保留原始工件。

## 4. 单条轨迹的操作顺序

1. 冻结artifact、依赖、参数、消息及seed规格，生成run_id和配置哈希；公布本条选定的目标模型标签和偏差项。
2. 执行真实Setup，再生成old/new两代key；记录代次、对象ID、A生成/缓存策略及逻辑矩阵A的同一性。若每次KeyGen自生成A，保留两份标识并按实际差异处理。
3. Enc_old(M)取得父密文；用old key解密并记录initial_message、initial_equal与初始异常。为观察未筛选实验，初始比对结果只作记录，后续按预先固定计划继续；若作者driver本身拒绝，则保留该分支与分母。
4. 对old→new调用一次真实TG，记录四块shape、dtype、逻辑/序列化哈希、token_id、key IDs。若内含重试，每一次尝试都保留编号、原因、筛选谓词与接受结果。
5. Upd(token,parent)生成子密文，记录其父ID、新key代次、R生成规格、shape与哈希。一次正常调用的语义与内部循环分别记录。
6. Dec_new(child)记录updated_message、updated_equal、异常/⊥。消息比较发生在正确性记录中；计时窗口是否包括该比较单独标明。
7. 保存按序事件、stdout/stderr/退出状态、原样命令和环境，计算工件清单哈希；使用相同代码/配置/币重放时，分别比对逻辑矩阵与序列化输出，并登记差异。

密文/key/token哈希的规范化需写明shape、模数、行列顺序、整数代表、字节宽度与大小端；同时保留实际序列化哈希。只有哈希相同仅支持采用的序列化下对象身份，通用算法/联合分布仍由静态映射判断。

## 5. 预期证据格式

至少四类文件：artifact_and_environment.json、parameters_and_randomness.json、trace.jsonl、result_and_timing.json，另附原日志和文件清单。每个字段应由实际值填充；待补字段用null并保留状态。以下为**未执行模板**的结构摘要：

```json
{
  "execution_status": "NOT_EXECUTED",
  "paper_doi": "10.46298/fi.14425",
  "artifact": {"authenticated_link": null, "commit_or_archive": null, "sha256": null, "dirty_patch_sha256": null},
  "entrypoints": {"setup": null, "keygen": null, "enc": null, "tg": null, "upd": null, "dec": null, "argv_exact": null},
  "parameters": {"variant": null, "n": null, "D": null, "q": null, "mbar": null, "nbar": null, "B": null, "chi_cdf": null, "max_depth": null},
  "randomness": {"A_generation": null, "cross_generation_A_reuse": null, "seed_manifest": null, "replay_material": null, "call_order": null},
  "arithmetic": {"dtypes": null, "overflow_semantics": null, "modulo_locations": null, "negative_representation": null, "Ord_Tensor_order": null, "rounding": null, "packing": null},
  "objects": {"old_key_id": null, "new_key_id": null, "token_id": null, "parent_id": null, "child_id": null},
  "messages": {"original_hex": null, "bit_length": null, "initial_hex": null, "updated_hex": null, "initial_equal": null, "updated_equal": null},
  "failures": {"initial_error": null, "tg_attempts": null, "filters": null, "retries": null, "update_error": null, "decode_error": null},
  "denominators": {"planned_attempts": null, "initial_correct": null, "completed_updates": null, "all_correct": null, "abort_or_exception": null, "per_operation_timed_calls": null},
  "timing": {"clock": null, "units": null, "operation_windows": null, "preprocessing_and_cache": null, "verification_inside_window": null},
  "model_mapping": {"result_A": "UNRESOLVED", "result_B": "UNRESOLVED", "deviations_and_transfer_bounds": null}
}
```

trace.jsonl每行包含sequence、operation、source_ref、input_object_ids、output_object_ids、key_epoch、seed_domain_ref、retry_index、filter_reason、timing_window和结果状态。原消息、两个解密结果与比较布尔值必须实际记录，不能仅以“程序返回0”替代。

## 6. 正确率与计时的分母

最小轨迹N=1时，只登记一个配置和一组币的行为见证。以后若做统计，先固定计划attempt数，保留全部初始错误、TG/Upd/Dec异常、拒绝与重试。总体全消息正确率以预先定义的全部attempt为分母；程序异常的处理规则与模型事件另列。完成更新数、有效输出数、指定行/坐标分母同时报告，不能通过丢弃异常改变实验。

先完成总体记录，再按initial_equal分组给条件正确率；条件分母为initial_correct，分组包含其中全部最终成功、失败及异常记录。B的单次成功仍是允许事件，单次失败也不能推出其概率下界。分布/采样或筛选差异仍需迁移论证。

计时分别保留N_KG、N_Enc、N_Dec_initial、N_Dec_updated、N_TG、N_Upd；包含A生成、seed抽取、打包、内存分配、预热/缓存或消息验证的范围逐项写明。最小轨迹包含两代KG、一次Enc/TG/Upd以及两次不同用途的Dec，可分别记录而不混合。原论文100次是计时运行口径，重现其均值/标准差还需相同测量边界、硬件/库环境和独立原日志。

## 7. 取得工件后的模型裁决顺序

先填写字段级MAPPED/DIFFERS/UNRESOLVED和确切源行，再填写配置整体状态。A需参数族、公开仿射关系、可逆/噪声与停止预算；B需固定640、A及噪声联合律、未筛选一次更新和舍入。对seed模型使用明确统计耦合或计算引理，保存有限损失；对初始正确条件化使用事件/比率范围。字段或单条输出相符时，结论止于相应范围。

本轮可执行作者入口仍为null，实际消息比对轨迹和率/耗时执行证据均未取得。最能改变当前实现适用裁决的材料是一份可认证作者UE版本，加上完整静态配置/随机性/算术映射及一条消息比对轨迹；来源和静态合同决定如何使用v2.1定理，单次轨迹认证实际代码路径。
'''

for name,text in [('PUBLIC_ARTIFACT_PROVENANCE.md',provenance),('IMPLEMENTATION_MODEL_MAPPING.md',mapping),('MINIMAL_REPRODUCTION_SPEC.md',spec)]:
    (OUT/name).write_text(text.strip()+'\n','utf-8')

verdict=dict(schema='fi-author-implementation-audit/verdict/1',stage='作者实现公开溯源与模型迁移核查',date_asia_shanghai='2026-11-10',status='WAITING_FOR_AUTHOR_ARTIFACT',completion='SOURCE_FORENSICS_AND_MODEL_CORRESPONDENCE_VERDICT_COMPLETE_WITH_DISCLOSED_GAPS',identity=dict(status='INFORMED_PUBLIC_ARTIFACT_PROVENANCE_AND_STATIC_MODEL_TRANSFER_AUDIT',author_proofs_prior_reviews_and_search_results_visible=True,exact_backend_model_id=None,new_independent_mathematical_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_subagents=0),
 target=dict(doi='10.46298/fi.14425',arxiv='2410.03948v4',authors=['Mariusz Jurkiewicz','Kamila Prabucka'],current_publisher_export=rec(SRC/'publisher_export.json'),paper_PDF_sha256='bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4',reported_variants=[x['name'] for x in config],reported_operations=['KG','Enc','Dec','TG','Upd'],reported_timing_run_count=100),
 authenticated_author_UE_artifact_obtained=False,author_UE_artifact_exists_elsewhere=None,authenticated_author_UE_source_files=[],author_configs_fully_statically_mapped=0,author_config_mappings=config,
 public_author_identity=dict(mariusz=dict(paper_affiliation_email_matches_official_WAT=True,ORCID='0000-0002-6314-4381',ORCID_basis='Primary JTIT1581 link plus institution/name; DBLP separately flags inferred verificationpending',institution_profile_id='WAT839fd48da58147e29ba6d882b5bbf563',profile_access='403',ORCID_public_person_fields_obtained=False),kamila=dict(paper_affiliation_email_known=True,DBLP='394/4071',dedicated_ORCID_certified=None,author_code_homepage_certified=None),same_name_account_is_sufficient_for_code_attribution=False),
 upstream_baseline=upstream,upstream_code_is_author_UE=False,
 actual_execution=dict(author_UE_runs=0,upstream_crypto_code_runs=0,downloaded_crypto_modules_imported=0,dependencies_installed=0,message_checked_author_UE_traces_acquired=0,reported_post_update_check='NOT_REPORTED_IN_PAPER; actual execution unresolved',KEM_reencrypt_check_seen_statically_in_upstream=True,UE_check_execution_certified_by_that_KEM_code=False),
 mapping_differences=dict(observed_upstream_only=['Fixed official parameter profiles rather thanCF1 growth','Seed-generatedA rather than uniform full matrix','SecretSHAKE streams rather than exact iid raw words','KEM keygen chooses its ownA; noUE same-globalA contract','NoTG/Upd/Ord/Tensor methods in acquired blob'],potential_author_differences_requiring_source=['SharedA across generations','Seed/domain/slice reuse','Extranoise orP2shape','Rank/initial/final-output screening and retry','Gadget row mismatch','Non-ring-compatible arithmetic or rounding','KEM versusPKE/UE call path'],not_attributed_to_author_without_evidence=True),
 paper_transfer_analysis=dict(A_fixed_A_can_average_public_matrix_distribution_if_conditional_noise_contract_holds=True,A_algebraic_inverse_and_real_fresh_probability_proofs_are_distinct=True,B_seed128_A_statistical_distance_lower='1-2^-6143872',seed_A_full_view_exposure_caveat=True,secret_seed_expansion_requires_joint_law_lemma=True,arithmetic_wrap_lemma='If every step is defined modulo2^w andD<=w, projection toZ/(2^D) preserves add/sub/mul; bit/compare/division/float/undefined overflow separately checked',B_conditioned_success_transfer='(U_star+eta_E)/(1-2^-132-eta_I) when denominator positive; same decimal endpoint requires concrete bound',numeric_field_or_single_trace_does_not_establish_joint_distribution=True),
 reproduction_spec=dict(status='PREPARED_ENTRYPOINT_PENDING_AUTHOR_ARTIFACT',author_entrypoint=None,author_argv=None,template_is_not_execution_record=True,required_files=['artifact_and_environment.json','parameters_and_randomness.json','trace.jsonl','result_and_timing.json','raw logs and hash manifest'],planned_first_trace='Fixed-message640 Enc->TG->Upd->Dec with initial andupdated comparisons; full seed/arithmetic and retry records',correctness_and_timing_denominators_separate=True),
 minimal_external_submission=['Paper/author/institution authenticated repository or archive plus immutable version/hash','Complete UE source/driver and six config exports with dependencies','A andsecret-noise generation/domain/slice plusOrd/arithmetic/rounding specification','One unfiltered message-checked640 trace and exactentrypoint; full original100-run logs needed for performance-table reproduction'],
 next_most_decisive_evidence='An authenticated author UE commit/archive plus source-mapped640 config/randomness/arithmetic and one message-checkedEnc->TG->Upd->Dec trace',
 public_route_state=dict(route_ledger=rec(EV/'PUBLIC_ROUTE_LEDGER.json'),routes_count=len(routes),search_scope=rec(EV/'SEARCH_AND_RETRIEVAL_SCOPE.json'),all_discovered_accessible_branches_checked=True,access_limited_branches_with_reopen_conditions=True,global_nonexistence_asserted=False),
 inherited_theory=dict(manifest=rec(V/'MANIFEST.json'),A_andB_models=jd(V/'CLAIM_EVIDENCE_MATRIX.json')['frozen_models'],INC976_closed=True,mathematical_results_changed=False,FI_full_LWE_reduction_and_human_review_still_external=True,application_priority_state='Prior2026-11-10 search-bounded candidates/global priority unresolved; current work is artifact provenance'),
 action_counts=dict(new_web_queries=sum(len(x['queries']) for x in webqueries),web_tool_calls=len(webqueries),new_identity_code_searches=3,upstream_GitHub_read_calls=6,raw_public_HTTP_requests=8,cryptographic_implementations_created=0,attack_or_LWE_runs=0,matrices_keys_tokens_ciphertexts_generated=0,large_crypto_experiments=0,native_AS_RP_requests=0,account_operations=0,author_contacts=0,messages_or_emails_sent=0,new_subagents=0),
 required_deliverables=['PUBLIC_ARTIFACT_PROVENANCE.md','IMPLEMENTATION_MODEL_MAPPING.md','MINIMAL_REPRODUCTION_SPEC.md','VERDICT.json'],seal_state='PENDING_FINAL_QA')
dump(OUT/'VERDICT.json',verdict)
print(json.dumps(dict(status=verdict['status'],core=[rec(OUT/x) for x in verdict['required_deliverables']],routes=len(routes),web_queries=verdict['action_counts']['new_web_queries'],author_configs_mapped=0),ensure_ascii=False))
