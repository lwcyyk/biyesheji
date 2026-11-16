from pathlib import Path
from datetime import datetime,timezone,timedelta
from fractions import Fraction
import hashlib,json,re,sys
sys.set_int_max_str_digits(0)
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_publication_impact_audit';EV=OUT/'evidence';SRC=OUT/'sources';V2=BASE/'crypto_fi_research_manuscript_v2'
def read(p):return Path(p).read_text('utf-8-sig')
def jd(p):return json.loads(read(p))
def rec(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def mdlink(p,label=None):return f'[{label or Path(p).name}]({str(p).replace(chr(92),"/")})'
def write(name,s):(OUT/name).write_text(s.strip()+'\n','utf-8')

matrix=jd(V2/'CLAIM_EVIDENCE_MATRIX.json');vm=jd(V2/'MANIFEST.json');vh=vm.pop('payload_sha256')
assert hashlib.sha256(json.dumps(vm,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==vh
for x in vm['files']:
    a=rec(V2/x['path']);assert a['bytes']==x['bytes'] and a['sha256']==x['sha256']

# Replay exact fingerprint records actually used in the source/proof-entry mapping.
refchecks=[]
def walk(x):
    if isinstance(x,dict):
        if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str) and len(x['sha256'])==64:
            p=Path(x['path'])
            if p.is_absolute():
                a=rec(p) if p.is_file() else None
                refchecks.append(dict(path=str(p),expected_sha256=x['sha256'],expected_bytes=x.get('bytes'),actual=a,match=a is not None and a['sha256']==x['sha256'] and ('bytes' not in x or x['bytes']==a['bytes'])))
        for v in x.values():walk(v)
    elif isinstance(x,list):
        for v in x:walk(v)
for k in ['S1','S2','S3','E1','E2','E3','E7','E8']:walk(matrix['source_registry'][k])
assert all(x['match'] for x in refchecks)
dump(EV/'INPUT_FINGERPRINT_VERIFICATION.json',dict(v2_manifest_canonical_payload_match=True,v2_three_sealed_file_hashes_match=True,reference_records=refchecks,record_count=len(refchecks),all_match=True,semantic_read_scope='v2 claims and supplied proof/response context; target current/historical versions and source audit; E1/E2/E7/E8 identities and proof pointers inherited with byte verification; no fresh independent mathematical review'))

source_records=[]
def source(sid,title,public_date,version,path,url,scope,grade='PRIMARY_FULL_TEXT'):
    r=dict(id=sid,title=title,public_date=public_date,version=version,url=url,reading_scope=scope,evidence_grade=grade,recorded_at_asia_shanghai=datetime.now(timezone(timedelta(hours=8))).isoformat())
    if path:r['local_file']=rec(path)
    source_records.append(r);return r
source('O4','FI期刊/arXiv v4','arXiv v4:2025-12-29; journal online:2026-01-11; PDF volume year:2025','23-page current publisher PDF byte-identical to arXiv2410.03948v4',SRC/'arxiv_v4.pdf','https://fi.episciences.org/17222/pdf','Full PDF text, source TeX, pp2,9-15,19-22 claim scope; new images visually inspected pp11,13,14,15,19,20,21; old images/game readings retained through matching hashes')
for v,date in [(1,'2024-10-04'),(2,'2024-10-08'),(3,'2025-08-09')]:
    source('O'+str(v),'FI历史公开版本',date,f'arXiv2410.03948v{v}',SRC/f'arxiv_v{v}.pdf',f'https://arxiv.org/abs/2410.03948v{v}','Full text extracted; TG/Upd source blocks normalized and compared, theorem/parameter/implementation paragraphs and tables scoped-read; no new full original-game proof audit')
source('F21','FrodoKEM官方2021规范','2021-06-04','59-page2021-06-04 frozen specification',BASE/'crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf','https://frodokem.org/files/FrodoKEM-specification-20210604.pdf','PDF10 half-up,14 D<=16,18-19 exact PKE residual and failure convolution,25 Tables3/4; parameter table newly rendered and visually read')
source('F23','FrodoKEM官方2023提案','2023-03-14','21 physical PDF pages; printed AnnexA pp11-12',SRC/'official_frodo_2023.pdf','https://frodokem.org/files/FrodoKEM-standard_proposal-20230314.pdf','AnnexA TablesA.1/A.3/A.4:640 numeric and chi/CDF match2021; seed/salt version differences; source citation does not identify an author software commit')
source('KLR','Klooß–Lehmann–Rupp2019','2019 EUROCRYPT; exact first-preprint day not newly verified','71-page institution author version',BASE/'crypto_fi_research_manuscript_v1/sources/KLR2019.pdf','https://orbilu.uni.lu/bitstream/10993/50226/1/Publikation_UE_Eurocrypt_2019.pdf','PDF17 Def11,27 Def14,44 AppB.2; exact definitions/formulas compared; PDF44 newly rendered and visually read; website handle timeout recorded')
source('N','Nishimaki前驱','received2021-03-02; latest revision2024-04-19; note dated2024-04-18','ePrint2021/221 landing page; exact extended PDF unavailable',None,'https://eprint.iacr.org/2021/221','Primary abstract and revision note; source PDF403 in both web and direct fetch. Exact Lemma5.7 remains unresolved; obfuscation retraction note applies to its named construction', 'PRIMARY_METADATA_AND_ABSTRACT_PDF_UNAVAILABLE')
source('LC','Lattice Codes for Lattice-Based PKE','README modified date returned:2023-07-16; exact paper initial date not newly verified','Pinned README commit e577f664353a6ea8b679815c314a8e3f04264657',None,'https://github.com/shx-lyu/lattice-codes-for-pke/blob/e577f664353a6ea8b679815c314a8e3f04264657/README.md','Full author repository README read; base-PKE lattice coding and rounded-continuous-Gaussian simulation; paper full-text formulas not adopted','AUTHOR_REPOSITORY_README_ONLY')
source('UHE','Liu等CSS2022混合UE','2022-09-29','Springer publisher abstract; pp71-85; DOI10.1007/978-3-031-18067-5_6',None,'https://link.springer.com/chapter/10.1007/978-3-031-18067-5_6','Primary abstract:REACT+iO+puncturable PRF; publisher full text requires subscription; no formula-complete exclusion asserted','PRIMARY_ABSTRACT_FULL_TEXT_UNAVAILABLE')
source('GH','官方Frodo参考仓库','current default branch viewed2026-11-10; author UE commit unspecified','microsoft/PQCrypto-LWEKE directory listing; FrodoKEM tree4f337a3ee6945cc8e9949a8ddba34f51d88325d9',None,'https://github.com/microsoft/PQCrypto-LWEKE','Official base implementation existence and current tree; full author UE program not located. Repository response retained in github_fetch_1.json','PRIMARY_REPOSITORY_LISTING')
acquisition=jd(EV/'PUBLIC_ACQUISITION.json')
for r in source_records:
    if r['id'] in ['O1','O2','O3','O4']:
        a=next(x for x in acquisition if x['name']==f'arxiv_v{r["id"][1:]}.pdf')
        r['retrieved_at_asia_shanghai']=a['retrieved_at_asia_shanghai']
        r['retrieval_record']='evidence/PUBLIC_ACQUISITION.json'
    elif r['id']=='F23':
        a=jd(EV/'OFFICIAL2023_CORRECTED_ACQUISITION.json');r['retrieved_at_asia_shanghai']=a['retrieved_at_asia_shanghai'];r['retrieval_record']='evidence/OFFICIAL2023_CORRECTED_ACQUISITION.json'
    elif r['id']=='F21':
        r['retrieval_record']='Historical frozen local bytes; primary online text reopened in evidence/web_06.json; first network acquisition timestamp not newly reconstructed'
        r['current_online_retrieval_time_UTC']=jd(EV/'web_06.json')['retrieved_at']
    elif r['id']=='KLR':r['retrieval_record']='Historical acquisition/source audit dated2026-11-08; current scoped reread and hash verification; first acquisition seconds not registered here'
    else:
        mapping={'N':'web_05.json','LC':'github_fetch_3.json','UHE':'web_08.json','GH':'github_fetch_1.json'}
        f=mapping[r['id']];r['retrieval_record']='evidence/'+f;r['current_online_retrieval_time_UTC']=jd(EV/f)['retrieved_at']
dump(EV/'SOURCE_LEDGER.json',source_records)

# The web tool merges query results within a call. Keep exact query batches without inventing per-query zero counts.
queries01=['"Unidirectional Key Update in Updatable Encryption, Revisited" correctness implementation','"2410.03948" erratum OR correction OR github','"10.46298/fi.14425"']
searches=[dict(receipt='evidence/web_01.json',queries=queries01,retrieved_date_asia_shanghai='2026-11-10',result_shape='Merged batch; exact initial tool output retained')]
for p in sorted(EV.glob('web_*.json')):
    if p.name=='web_01.json':continue
    d=jd(p);q=d['query'].get('system2_search_query',[])
    searches.append(dict(receipt='evidence/'+p.name,queries=[x['q'] for x in q],retrieved_at=d['retrieved_at'],open_and_click=d['query'].get('open',[])+d['query'].get('click',[]),result_shape='Merged batch; keyword absence interpreted only within returned source scope'))
assert sum(len(s['queries']) for s in searches)==31
dump(EV/'SEARCH_LEDGER.json',dict(cutoff_asia_shanghai='2026-11-10',web_query_count=31,web_calls=9,query_batches=searches,github_code_searches=['2410.03948','FrodoPKE','Unidirectional Key Update','FrodoPKE UE.TG'],github_issue_searches=['is:issue "2410.03948"','is:issue "Unidirectional Key Update in Updatable Encryption"'],limitations=['Web ranking/index coverage is bounded, not exhaustive','S2 metadata429; no retry or zero-citation inference from that error','Nishimaki extended PDF403','UHE publisher abstract only','No global-publication-priority attestation']))

original=r'''
# 两项主结果的应用优先权与发表影响核查：原声明与参数映射

2026-11-10，Asia/Shanghai。身份：**INFORMED_APPLICATION_PRIORITY_AND_ORIGINAL_CLAIM_AUDIT（知情应用优先权与原论文声明审计）**。本轮阅读既有作者证明与AI审阅后进行来源和命题比较，新增独立数学审阅计数为0。

本轮裁决绑定期刊 DOI [10.46298/fi.14425](https://doi.org/10.46298/fi.14425) 的当前23页文件，与 arXiv:2410.03948v4 逐字节相同。结果A评价声明合同中的来源隐藏安全；结果B已经支持该具体640有限配置的一步可靠性失败。作者性能表对应的实际程序仍需版本、配置和联合采样证据。

## 1. 输入和版本身份

v2四份文件及其规范化封存载荷核验通过，实际使用的历史指纹逐项对照。正文与证明继续从v2只读引用。完整指纹和当前来源记录见本目录VERDICT与evidence/INPUT_FINGERPRINT_VERIFICATION.json、SOURCE_LEDGER.json。字节核验与语义阅读分别登记。

| 公开对象 | 公开时间 | 实际取得与比较 | 与本轮结论的关系 |
|---|---|---|---|
| arXiv v1 | 2024-10-04 22:16:20 UTC | 17页PDF和6文件源包 | TG/Upd活跃源块与v4去空白后相同；Theorem4.3在PDF11，4.9在15；实现/表在15–16 |
| arXiv v2 | 2024-10-08 14:26:09 UTC | 17页PDF和5文件源包 | 同样的TG/Upd核心；Theorem4.3在PDF10，4.9在15；表在15–16 |
| arXiv v3 | 2025-08-09 00:32:48 UTC | 23页PDF和7文件源包 | 核心更新块相同；Theorem6.3在15，6.9在20；表在21 |
| arXiv v4 | 2025-12-29 13:10:25 UTC | 23页PDF和6文件源包 | 本轮主对象；articlev08.tex与v1研究稿冻结源字节相同 |
| 当前期刊 | 在线2026-01-11；接受2025-08-08；PDF卷年2025 | 2026-11-10重新获取 | PDF哈希与v4相同；当前落地页未列新增勘误链接 |

v4/期刊PDF SHA256：`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。TeX：`16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b`。版本日期来自arXiv原始版本表，获取时间和所有下载哈希见evidence/PUBLIC_ACQUISITION.json。源块比较只认证所列活跃代码块的文本身份；各版完整游戏与安全证明仍按其版本分别审计。

## 2. 两项冻结结果

**A（共同正确族中的来源隐藏攻击）。** FI打印算法配Ord列数规范化及独立χ640；λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，T=t_max=n。对每个先固定A、所有合法消息和支持内诚实随机样本，初始加密及最长n次更新逐样本正确。原rand-ind-eu-cpa游戏存在合法PPT攻击，调用≤3n+1，Δ≥1−(3/4)^n−ε_n=1−negl(λ)，故Δ→1。难度假设数量为0；条件安全定理前件另按§6评价。

**B（640一次更新可靠性）。** 固定n=640、D=15、q=32768、m̄=n̄=8、B=2；均匀Setup、全部原始χ640坐标/调用独立、既定Ord、一次诚实未筛选TG/Upd及最近整数平局向上。任意抽样前固定合法128位消息：初始完整正确率≥1−2^-132；更新后指定坐标正确率∈[0.2499054,0.2500946]，指定行全正确率∈[0.0000152532,0.000030345]，完整正确率≤0.000030345、错误率≥99.9969655%。条件于初始完整正确后，更新显示界保持。更新概率平均均匀Setup及全部诚实币；初始界还逐固定A成立。

## 3. 原论文声明对应表

以下采用精确公式和短语作原文锚点，其余内容为定位明确的中文转述。页码均为当前23页PDF的物理页码，恰与印刷页码相同；源行号指本轮取得的articlev08.tex。

| ID | 原文锚点及位置 | 算法、参数和前提 | A/B能够直接评价的部分 | 剩余证据与范围 |
|---|---|---|---|---|
| O01 | p2：Pr[UE.Dec(k_e2,ct_e2)≠m]≤negl(n) | 对消息、连续更新链定义UE正确性；正确性和安全性分别定义 | B刻画一个明确有限配置的一步高错误行为；A的族自身正确 | 单个固定n=640的数值界只承担具体配置评价；任意渐近正确性族的全称反驳另需相应族命题 |
| O02 | p11/TeX493：D∈Z>0，q=2^D，B∈{0,…,D}，n,m̄,n̄>0，8整除n | 打印参数域没有在此写D≤16；χ为小支持对称表 | CF-1满足这些明写类型及维度条件；固定25点χ640符合表分布描述 | 官方2021 API p14另写D≤16，CF-1属于打印域的扩展参数模型；LWE困难前件与成员资格分别核准 |
| O03 | pp11–12/TeX496–499：Sχ={−s,…,s}、反CDF及Frodo.SampleMatrix | 引用[1]2021、[2]2023；打印的χ矩阵记号 | χ640的精确边缘律与v2一致，A/B均携带独立采样合同 | 实际seed复用/域分离、跨矩阵联合律需代码或明确随机带说明 |
| O04 | p12/TeX509–520：A←R_q^(n×n)，B=AS+E | 打印Setup均匀A、两代共用A | B的H重量二项律与此平均模型对应；A逐固定A成立 | 官方AES/SHAKE使用128位seed展开A；实际软件分布与真正均匀A的迁移需单列 |
| O05 | p12/TeX557–560：ec(k)=kq/2^B，dc(c)=⌊c2^B/q⌉ mod2^B | 引用官方编解码 | B正确集合为{−4096,…,4095} mod32768；消息标签平移相容 | 软件舍入、整数表示、取模与打包要与规范对应 |
| O06 | p13/TeX580–590：Ord域为m̄×n̄，Tensor域为n×n̄；Remark6.1：Ord(C)Tensor_D(S)=CS | Upd实际调用Ord(C₁)，C₁有n列；TG第一块有nD行 | 最小列数重载给v2模型；一致位序重排保持A/B | 字面域在n≠n̄时类型不相容；行为变化的解释需要另一份精确定义，见§5 |
| O07 | p14/TeX633–653：P₂=U₂A+F₂，Y=HP₁+RP₂ | P₂为n×n，完整token公开；Upd仅新采R←χ | A可逆分支恢复r̂=(y−HP₁)P₂^-1并检验Sχ^n；B直接使用真实更新残差 | 未筛选TG是B合同；实际程序重试、额外噪声等均需映射 |
| O08 | p15/TeX669–703：W_print<q/(T2^(B+1))，随后短句“then the scheme is correct” | W_print=2(n²Ds³+n²s³)+nDs+ns²；T称最大epochs | B的640实例对任意整数T≥1均在前提之外；A另有完整逐样本证明 | 初始B₀与更新计数需完整计账，见§6；前提成立的源条件句保持其范围 |
| O09 | p19/TeX872–877：LWE assumption⇒Eq(6)；援引Nishimaki Lemma5.7，省略证明 | 精确样本数、秘密先验、辅助视图和时间损失未展开 | A的公开事件定位相邻端点障碍；v2保留H_rich/H_fixed分支 | 扩展版原图403，需完整参数化归约；两个源对象的引用继承尚待逐式认证 |
| O10 | p20/TeX882–886：“Under the LWE assumption”；Adv≤negl(n) | Theorem6.9，backward-leak uni-directional rand-ind-eu-cpa | A直接给同一游戏的构造级区分事实 | 非空困难前件下的条件定理反驳资格另需精确H，见§6 |
| O11 | pp20–21、Tables1/2、TeX893–959 | AES/SHAKE×640/976/1344；KG、Enc、Dec、TG、Upd的均值/标准差 | B说明标准640数值配打印iid/均匀模型需要严肃可靠性解释 | 表格未给D/B/CDF/config/代码版本；Dec输入的来源和更新后比对流程未报告 |
| O12 | pp20–22/TeX961–963：Python、NumPy及“100 independent test runs” | 作者称基于官方参考实现，100次用于计时 | 可确认实现语言与报告的计时范围 | 程序、命令、环境、随机带、成功/失败分母与日志仍缺；100次计时不等同100次更新解密验证 |
| O13 | p3：constant-size ciphertexts and keys；pp20–22部署适用性论述 | 尺寸相对更新深度保持；实用性还依赖正确性/安全性 | A/B使安全与可靠性前提成为必要核查项 | A/B并未改变所列矩阵尺寸；原始耗时数字本身没有被本轮推翻 |

源文件、PDF与图像均在本目录sources/evidence中。源包README只配置TeX编译入口和编译器。作者/资助说明、文末引用与各公开源包中，未定位作者UE仓库、运行命令或配置文件；这个观察限于实际取得材料和所列检索。

## 4. 640采用程度与性能表的准确含义

**采用程度。** 论文明确把UE测试标为FrodoPKE-640等六种变体，并测试TG和Upd。D=15、q=32768、B=2、m̄=n̄=8及χ640精确表由其引用的2021规范Table3/4（PDF25）对应；2023公开提案AnnexA TablesA.1/A.3（PDF15、印刷11）给相同640核心数值和质量。FI正文和性能表没有逐项重印这组配置。因此“作者明确测试640名称”已核准；“原性能程序逐项采用当前冻结分布与算术”仍需实物对应。

| 操作 | AES640：均值 / 标准差（秒） | SHAKE640：均值 / 标准差（秒） | 表内验证信息 |
|---|---:|---:|---|
| KG | 0.0198 / 0.0006 | 0.0198 / 0.0004 | 耗时 |
| Enc | 0.0218 / 0.0011 | 0.0218 / 0.0002 | 耗时 |
| Dec | 0.0003 / 0.00001 | 0.0002 / 0.00001 | 记为Dec(k_e,ct_e)，未交代ct_e的生成轨迹 |
| TG | 6.3251 / 0.2018 | 6.3118 / 0.0649 | 耗时 |
| Upd | 0.1224 / 0.0057 | 0.1214 / 0.0012 | 耗时 |

Tables1/2同页还列976/1344。正文报告100次独立计时运行，未报告消息比对断言、更新后的解密成功数、失败数、置信界或链深度。最准确判断为**更新后解密验证未报告**；实际是否执行过该检查仍需代码或日志。耗时测量可以在成功和失败输出上发生，因此B直接挑战的是这些配置作为可靠UE实例的解释，作者耗时数据的真实性和准确性继续需要其测量工件评价。

**T及失败预算。** Theorem6.3保留符号T，安全证明也用轮换范围；实现段没有给具体最大更新次数、可接受失败预算或多次更新的失败曲线。100是计时运行次数。对固定640，源充分式对T≥1均不满足；B已经给一步错误率下界。对更多更新深度及其它配置分别保留研究责任。

**作者软件的最小对应材料。** 一份可定位的commit/压缩包和依赖锁、六配置参数导出、运行命令及机器环境；Setup的A生成/复用合同；KeyGen/Enc/TG/Upd各随机流的seed长度、域分离和切片；Ord/Tensor顺序；矩阵整数dtype、溢出与取模位置；Decode平局/打包；筛选/拒绝/重试/失败处理；一条含消息相等断言的Enc→TG→Upd→Dec调用轨迹及100次原始计时日志。每项缺失的影响在VERDICT.software_mapping登记。此处只准备证据清单，外部消息发送为0。

## 5. Ord解释的稳定性与边界

1. **实际列数重载。** 把Ord_t的域写为m̄×t，原逐位规则按t应用，Upd取t=n。它同时满足nD行token、Tensor和Remark6.1，属于v2透明携带的最小类型规范化。
2. **位平面、逐元素或反位序的一致重排。** 对固定置换矩阵Π，令H′=HΠ，(P₁′,Q₁′)=Π^-1(P₁,Q₁)，Tensor′=Π^-1Tensor。则H′P₁′=HP₁、H′Q₁′=HQ₁。原始U/F/G行iid，重排保持联合律；H重量也保持。因此两项结果对这一类一致规范化稳定。
3. **字面m̄×n̄域。** n=640、n̄=8时无法直接应用于C₁；维度检查已经需要一个额外定义。它只给出类型缺项，不能提供另一份同类型、同分布、已正确的640算法。
4. **有符号数字展开、截断列、额外噪声、重试或改变token形状。** 这些行为改变H、抽样或算法。公开仿射恢复在相同Y=HP₁+RP₂关系下仍可分析，但v2的反集中和可靠性数字必须按新模型重新证明。当前源文给的是D位0/1展开；D位代表与标准模代表的一致转换属于第一/二类。

本轮纸面置换论证只建立上述限定等价类，作者实际Ord仍需程序对应。所有影响表随规范化标签引用。

## 6. 两个条件定理的准确评价

**Theorem6.3。** 完整充分式应计B₀+t_maxW<q/2^(B+1)，其中B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²。s=12、合法维度/编码合同、整数n,D≥1、T≥1且0≤t_max≤T时，W_print−W=3168n²D≥B₀，所以打印的更松充分界若满足前提可吸收初始项。640下B₀=184332、W=3185256960、W_print=22649448960，而q/8=4096。本轮B评价的是充分前提之外的具体高错误行为。CF-1由自己的完整证明承担正确性；其有限例n=128、D=56、T=128也满足源较松充分前提，核账见evidence/SCALAR_SOURCE_ACCOUNTING.json。

**Theorem6.9。** 参数域成员资格、构造攻击和困难性前件逐项区分。CF-1属于FI明写打印域；结果A给原游戏区分事实。若H取精确χ640的丰富同秘密新独立样本困难性，v2附录A已给成熟代数算法使该前件失效。若H限定固定n/3n样本，其真实性、同预算算法以及FI完整模拟归约继续待证；更宽Gaussian也需到精确表/完整UE视图的迁移。当前最强措辞为：构造级来源隐藏结论及命名端点存在已证明障碍，非空困难前件下条件蕴含为假的资格另行核准。论文p20的量子安全/部署论述需要该精确归约和实际实例对应支持。

## 7. 本轮发现的旁支呈现差异

v2附录B的χ976分子序列把±5…±9列为1131、426、138、38、8；2021 Table3和2023 TableA.3原图/文本为1101、396、118、29、6。前者按零点一次、正负各一次总和为65718，分母写65536，无法作为该分母下归一化概率表。旧PARAMETER_CERTIFICATES.json的976 source_cdf为[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767]，从它导出的质量与官方表相符；64重系数文件的总质量也等于所存分母。

此处登记为**INC976：已确认的v2附录转录修正**。本轮未重算976卷积或重审其全部概率证书。结果A、B均只使用χ640，当前两个主结果的输入与裁决保持。v2历史字节保留，后续作者版本应更正该行及其重放说明。

2023引用另有书目精度问题：FI文末[2]登记1–59页，官网所列2023-03-14提案实际21个PDF页；本轮只以明确版本的表核准640参数，不据页数差异替作者判定其所用软件版本。
'''

impact=r'''
# 两项主结果的应用优先权与发表影响裁决

2026-11-10，Asia/Shanghai。身份：知情应用优先权与原论文声明审计。**A、B在本轮实际核读与公开检索范围内均保留具体新对象应用候选地位；相同FI对象、完整等价命题的公开直接先例尚未定位。** 这是一项检索有界的应用判断，全球首次与本项目公开发表优先权仍待独立证据。

本轮沿用v2的数学状态和精确模型，新增工作为公开版本、声明、代码线索、先例与影响比较。方法、对象贡献、条件安全前件及作者性能实例分别评价。原论文声明的逐条位置见ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md；本目录VERDICT固化输入、检索与交付字节。

## 1. 检索范围与时间界

复用截至2026-11-08的APPLICATION_PRIORITY_AUDIT及四份原始检索回执；本轮新增31条公开网页检索查询，覆盖题名、DOI、arXiv、作者、修订/勘误/公开讨论、Frodo型UE错误/噪声/正确性、公开token/仿射支撑/来源隐藏、代码、论文及学位材料。另做4条GitHub代码查询、2条格式正确的issue查询；初次issue请求422后按服务要求修正。所有实际查询及原始返回在evidence/SEARCH_LEDGER.json和web_01…09.json、github_*.json保存，截止2026-11-10。

| 路线 | 本轮实际观察 | 证据含义 |
|---|---|---|
| 出版社、arXiv原始记录 | 公开版本仍为v1–v4，期刊当前PDF=v4；页面未列新增勘误链接 | 只认证所见版本与页面状态 |
| 版本PDF/源包 | 4版PDF、4版源包均取得；TG/Upd活跃源块去空白后相同 | 算法核心沿版本保留；完整游戏/证明分别定位 |
| OpenAlex DOI记录 | cited_by_count=0，updated_date=2026-11-07 | 该数据库这一记录的索引状态 |
| Crossref DOI记录 | is-referenced-by-count=0；update-to未返回；关联预印本版本可见 | 登记的引用与更新字段，覆盖面另有边界 |
| Semantic Scholar | 429限流；保留错误回执 | 该路线未完成；其引用数与引用全文状态保持未知 |
| GitHub arXiv/题名/算法查询 | 返回RSS归档、基础PKE或异对象材料；FrodoPKE UE.TG返回空；两个issue精确查询total_count=0 | 未在所查默认分支/词法issue范围定位作者UE代码或同题攻击；全平台不存在代码的断言仍缺证据 |
| 搜索聚合、AI摘要与转引 | 多数返回原文转载和二手概述 | 仅作发现线索；其新颖性判断和重复转引不作为证明 |

查询批次的网页结果由工具合并返回。本报告保留批次与原始条目，不为每个查询虚构独立的零命中数字。精确数字查询未返回目标证明，同样只承担当前返回范围的观察。数据库引用数、搜索未命中与原文未取得具有不同含义。

## 2. 最强已核原始近邻与完整命题覆盖

| 来源及定位 | 同一构造/权限/事件 | 对A的覆盖 | 对B的覆盖 | 裁决和重开材料 |
|---|---|---|---|---|
| KLR2019，71页作者稿PDF17 Def11、27 Def14、44 AppB.2 | 确定性公开token一致性和概率重加密分布匹配；发表于FI之前 | 覆盖思想和攻击骨架：已知token下检验公开可测更新像；FI方阵逆使检验高效。未给FI原游戏、真实fresh、CF-1或3n+1预算命题 | 没有FI640的TG残差、联合列包或一步高错误下界 | **最强已核方法近邻**；同对象完整结果覆盖尚未建立 |
| 官方Frodo2021 §2.2.7，PDF18–19及Tables3/4 p25 | 基础PKE残差S′E+E″−E′S；精确有限产品律/卷积及全消息并集 | 精确χ表、采样和成熟分布工具已有来源 | 覆盖B的初始残差与成熟失败概率方法；未包含FI的TG/Upd、随机系数和行八阶混合矩 | **B的最强计算方法先例**；其基础PKE失败率无法直接给FI更新失败下界 |
| FI自身v1–v4 Theorem4.3/6.3 | 相同更新递推与W_print充分上界 | 已有噪声递推工具；CF-1需给同族完整正确性与预算 | 充分上界超过半宽只使判据失效，不能从中推出失败概率下界；源码四版均未给当前B命题 | 同对象先有正确性充分分析；**当前高错误概率结论尚无直接覆盖** |
| Nishimaki ePrint2021/221，最新2024-04-19 | 同研究链的LWE UE；FI援引其Lemma5.7 | 历史定点转录记录较长随机向量/不同矩阵接口；完整源图与映射当前缺失 | 未取得可核读的相同640一次更新概率命题 | **潜在同链先例的逐式覆盖未决**。最小材料为2024扩展版PDF、Lemma5.7及构造/参数邻文，附公开日期与哈希 |
| Lyu等作者代码README，固定commit e577f…，ePrint2022/874线索 | 基础FrodoPKE的格编码与AWGN近似/rounded Gaussian模拟 | README没有FI token或原游戏轨迹 | README研究改变编码的基础PKE DFR，采样也不同；未提供相同FI更新命题 | **作者README级筛选**；论文完整公式未核读，保留该层级，不作全文覆盖裁决 |
| Liu等CSS2022，DOI10.1007/978-3-031-18067-5_6，出版社摘要 | REACT+iO+puncturable PRF的混合UE；2022-09-29公开 | 摘要对象与当前FI公开矩阵token不同 | 摘要未给640一次诚实更新失败概率 | **原始摘要级近邻**。正文订阅受限，完整公式比较待合法全文；摘要差异只支持当前筛选 |
| FrodoKEM故障/侧信道/key-mismatch搜索线索 | 依赖故障、侧信道或不同解密反馈接口 | 权限与同一诚实原游戏尚无等价映射 | 改变密钥误差的攻击实验与诚实TG/Upd有不同输入族 | 作为发现线索排出当前直接证据集；若取得同算法同权限命题则重开 |

旧PRE/残差平均近邻的实读与权限比较沿用2026-11-08审计：腐化接收方秘密、隐藏token或同父重复输出与A的零Key、单挑战轨迹分别核账。本轮未为它们新增全文审阅认证。

## 3. 逐式迁移检验

**KLR到A。** KLR Def14给固定sp、old/new钥匙、token及密文的decrypt-then-encrypt与ReEnc分布相同要求。AppB.2展示公开token下，确定性重加密结果可用于发现不相容的混合替换。令FI公开上下文w=(父第一行h、P₁、P₂)，在P₂可逆时定义

\[
E_w=\{y:(y-hP_1)P_2^{-1}\in\mathcal S^n\}.
\]

这是成熟仿射代数对公开一致性思路的直接实例化。真实update必通过；独立均匀行通过概率为(25/q)^n。结果A的比较端是**真实fresh Enc**，它与token共享A；其概率不能由均匀行计数替代。v2用父低重量界、保留F₁的独立列卷积、逐固定P₂条件界给β≤αε_n，再证明P₂-only停止的付费放大。KLR固定上下文分布定义也没有直接给当前四查询的合法性和CF-1共同正确性。因此思想与骨架已有明确归属，完整FI对象命题仍包含实际新增的参数与概率工作。

**基础Frodo到B。** 官方规范的初始误差η₀=U₀E_old−F₀S_old+G₀对A消去。FI额外产生

\[
\delta=(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2.
\]

不能把该误差简单当成更多独立XY项：H与父币相关，新钥匙在多个项和行间共享。B分别固定单坐标环境F及同行环境V；在较小B环境下积分真实1280个a/b系数，使用绝对Fourier矩、差值律、全频率包络和点态弦线。行上界经事件包含推出完整上界，条件于初始正确再使用事件比率。精确有限分布、Fourier、Chernoff、Cauchy–Schwarz、Jensen和有向算术均属经典工具；本轮对象增量为把它们用于该残差及其真实依赖，给出严格有限数值。初始规范、粗最坏界和Gaussian近似均未单独达到B的完整命题。

## 4. A的应用与影响裁决

**已核准对象内容。** 在期刊/v4打印算法、列数规范化和iid χ640下，原游戏合法且无需Key腐化的高效支撑区分；逐固定A/P₂的真实fresh界；真实轮换预算内放大；同一CF-1族的最长n次逐样本正确性。来源、权限与参数的具体匹配构成对象贡献。

**成熟覆盖。** 公开token一致性和分布匹配归属KLR，矩阵逆、支撑成员检查、卷积收缩、并集、二元秩及停止放大各有成熟基础。当前证据支持具体密码分析应用，通用技术首创和相对所有成熟方法的资源分离均另需证明。

**对原文影响。** A对源rand-ind-eu-cpa构造级来源隐藏声明形成直接障碍；它同时展示正确性与来源隐藏失败可在同一打印参数族出现。Theorem6.9的条件逻辑继续采用v2精确审计：H_rich在CF-1已失效；H_fixed和完整归约未认证。常量尺寸关系、基础FrodoPKE/KEM的安全声明、明文恢复能力和实际软件破坏分别有自己的证据责任。

**允许的最强措辞。** “我们给出FI期刊/v4打印构造在明确Ord与独立采样合同下的原游戏来源隐藏攻击，并在同一逐样本正确族上用≤3n+1次调用得到Δ→1；在截至2026-11-10的实际核读与定向检索范围内，未定位相同构造、权限和完整命题的公开直接先例。”

**最小改变材料。** 带可核公开时间、完整同对象攻击/直接推导的原文；改变游戏或更新公式的正式版本；对Ord合同、F₁保留或停止条件的具体反例；精确可用LWE归约及其真实困难前件。

## 5. B的应用与影响裁决

**已核准对象内容。** 官方640核心数值可由原论文引用对应；对打印均匀Setup及独立精确χ模型，近乎全正确的初始消息经过一次诚实未筛选更新后，完整错误率≥99.9969655%，初始正确条件下保持该显示下界。该结论直接支持**该具体有限配置的一步可靠性失败**。

**成熟覆盖。** 原FI有更新误差递推与充分最坏界，基础Frodo有初始PKE精确卷积失败分析。二者尚未提供当前同行混合矩、完整消息上界或同一条件化数值。当前贡献为具体有限模型可靠性密码分析与认证概率，工具归属按经典方法登记。

**对原文影响。** 640不满足Theorem6.3打印前提，B评价前提之外的具体行为。原文p2使用渐近negl(n)定义；单个有限n的错误下界本身不能裁定任意渐近族。性能段明确测试640/TG/Upd，却未报告更新后消息比对、成功分母或深度预算。B使“标准640配该打印机制构成可靠实用UE”的解释需要更正或配置解释。原始耗时数据是否准确、作者程序是否具有同一错误率，需代码/日志和分布算术对应。

**允许的最强措辞。** “FI打印算法配官方640数值参数，在均匀Setup、iid χ640、既定Ord、一次未筛选诚实TG/Upd和官方舍入模型下，初始完整正确率≥1−2^-132，更新完整错误率≥99.9969655%，且初始正确条件下显示下界保持。当前公开性能报告缺少把实测程序与这一模型逐项对应的工件。”

**最小改变材料。** 已日期认证且同算法/参数/联合律的一步高错误命题；指出当前列包/特征函数/有向证书的具体错误；作者完整commit/config/随机带/整数与舍入证据；明确修改后的参数或算法及其新正确性证明。

## 6. 当前贡献层级与下一步

当前最强统一定位为：**对已发表Frodo型UE的构造级来源隐藏密码分析及具体640配置可靠性分析，并附条件安全前提与发表声明范围审计。** 两个主结果各自有精确对象、量词、纸面证明与有限证书，具备独立密码分析短文或毕业论文核心研究章节的实质内容。通用新方法、全球优先权、标准FrodoKEM被攻破、作者软件实测失败和期刊接收均有独立的证据门槛。

最高价值的外部输入是作者UE实现的准确版本及一条有消息比对的完整调用轨迹；它决定性能表与B之间的迁移。最高价值的人工数学复核为HUMAN_REVIEW_ENTRY的三个明确问题。Nishimaki扩展版Lemma5.7与构造邻文可补齐先例/继承链；S2限流解除后可补其引用图。本轮无需为已完成的有限可靠性下界扩大采样或实现攻击。

旁支INC976已确认需在后续作者版本修正；它不进入A/B。本轮完成条件为在可复核范围内形成上述应用与影响裁决，受阻来源均给重开输入，历史材料保留原字节。
'''

human=r'''
# 人工密码学审阅入口：Frodo-FI两项主结果

2026-11-10。请以**公开打印算法与明确模型中的两个命题**为审阅对象。本入口自含命题、最短轨迹及证明责任；全文证明和有限证书通过末表直接访问。当前申请的是领域判断与数学复核，已有AI记录的身份和曝光在§5列明。

## 1. 目标版本与最小原始规范

目标为Jurkiewicz–Prabucka，DOI10.46298/fi.14425，当前期刊PDF与arXiv:2410.03948v4相同，23页，SHA256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。原文pp9–11为游戏，12为Setup/Enc/Dec，13为Ord/Tensor，14为TG/Upd，15为正确性充分定理，19–20为Lemma6.8/Theorem6.9，20–22为实现声明与性能表。官方2021规范PDF10给平局向上，14给D≤16的接口，18–19给基础残差/失败方法，25给χ640与参数。

冻结规范化：Ord_t对实际t列做D位0/1分解；Upd取t=n，位平面顺序与Tensor_D(S)=[S;2S;…;2^(D−1)S]相配，Ord_n(C₁)Tensor_D(S)=C₁S modq。源域写m̄×n̄与Upd输入m̄×n之间有类型缺项。相配的固定行置换保持两项结果；改变数字展开、形状或采样需单独定义。

## 2. 两项待审命题

**A。** λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，χ=精确χ640，T=t_max=n。所有原始χ条目和调用独立；A在其后采样前任意固定。最长n次诚实更新对所有消息和支持内样本逐样本正确。原rand-ind-eu-cpa攻击只用Enc、Next、token腐化及一次Challenge，最多3n+1次调用，Δ≥1−(3/4)^n−ε_n=1−negl(λ)。这是打印一般参数模型；官方D≤16 API和作者实际程序另行对应。

**B。** 固定n=640、D=15、q=32768、m̄=n̄=8、B=2。A均匀Setup，两代共用；所有原始χ640坐标和调用独立，一次Enc、一次诚实未筛选TG、一次Upd，Decode最近整数平局向上。任意预先固定合法128位消息、预先指定坐标/行：Pr(I)≥1−2^-132；Pr(E_c)∈[0.2499054,0.2500946]；Pr(E_r)∈[0.0000152532,0.000030345]；Pr(E_m)≤0.000030345，Pr(E_m^c)≥99.9969655%。条件于I后这些更新显示界保持。更新概率对均匀Setup和全部诚实币平均；初始界逐固定A成立。

χ640的0与每个正/负点质量分子为[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]，分母65536；0只计一次。负数用声明的模代表处理，理想表由16个独立均匀位精确抽样。

## 3. 最短攻击与A的证明节点

在epoch0和phase0开始，固定消息M：Enc₀(M)取得完整诚实父C；Next到1；Corr(token,1)取得((P₁,Q₁),(P₂,Q₂))；Challenge₁(M,C)取得fresh或update。立即输出，Key/Dec/普通Upd/随机带请求及挑战后Next均为0。

取父第一行的h=Ord_n(c)及挑战第一行y。P₂可逆时算r̂=(y−hP₁)P₂^-1，属于Sχ^n则猜update；P₂奇异时公平猜测。真实update精确恢复r。空Key泄露使K*=∅，终局K*∩C*=∅；同消息和登记父满足挑战权限。

定理1的关键是**固定A、P₂以及父/H、U₁、fresh y时保留F₁随机**。记w为h的Hamming重量，μ_j=‖χ^{*j}‖∞为模群卷积峰值。逐列有hF₁=y−hU₁A−rP₂；高重量时每列卷积峰值≤μ_w0，枚举固定r只用于并集分析。n≥64时取w₀=64、h_support=25、a=maxχ=1161/8192，给

\[
\epsilon_n=\min\{1,\binom n{63}a^{n-63}+(25\mu_{64})^n\},
\quad\beta\le\alpha\epsilon_n.
\]

该ε_n式用于n≥64；n<64按v2置ε_n=1。首个可逆边界的停止只读P₂，每轮重做一份诚实父，支付真实轮换预算；条件于完整P₂序列后所选父/F₁仍有相同抽样律。χ640奇偶各半给α=p_n=∏_(i=1)^n(1−2^-i)>1/4。γ=25μ₆₄<1/2使ε_n可忽略，k=n即得A。共同正确性由B₀+nW<q/8承担，B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²，s=12。

## 4. B的概率链与应保留的依赖

更新残差为η₀+δ modq，η₀=U₀E_old−F₀S_old+G₀，δ=(HU₁+RU₂)E_new−(HF₁+RF₂)S_new+HG₁+RG₂。正确集合为D={−4096,…,4095} mod32768，逐消息标签一致。

单坐标先固定两代钥匙、父侧币及R的环境F，保留独立TG行：Φ_F(t)=ζ^(tη₀)G(t)^w∏_iG(tr_i)。坏环境<2^-22，全频率给1/4±(1/10600+2^-46+2^-22)。均匀Setup在u含奇数时使uA+f逐列均匀，H的9600位公平独立；这是B更新概率的A量词依据。

行级改用V=σ(A,U₀,F₀,U₁,F₁,U₂,F₂,R)。钥匙/G的8个列包此时iid，故p_row=E[p(V)^8]。在B_env=σ(A,U₀,F₀,R)下，a=hU₁+rU₂和b=hF₁+rF₂的1280系数有真实共同律T=Σ_(ℓ=1)^wX_ℓ+Σ_ir_iY_i modq。先合并共享钥匙系数，再对每个特征函数因子取模，得

\[
E[|\Phi_V(t)|\mid B_{env}]\le(E_T|\psi(tT)|^2)^{640},\quad
E_T|\psi(tT)|^2=\sum_{d=-24}^{24}\nu_d\varphi_B(td).
\]

全部rank在原始U/F外层积分；未改善的ν质量用单位包络保留。全部频率1–16384按1、2–3、4–7、8–15、16–63、64–16384覆盖，负频率配对，Nyquist保守计费。每个指数的Taylor倒数包络先向上取64位，再精确ν加权，最后对640次幂向上取80位。

\[
Z_*={27303052442598203493\over2417851639229258349412352},\quad\delta_B=2^{-25},
\]
\[
L_*=[(1-\delta_B)(1/4-Z_*)]^8,\quad
U_*=(1-\delta_B)[4^{-8}+(21845/16384)Z_*]+\delta_B.
\]

行下界来自Jensen，上界来自逐点弦线。完整事件E_m⊆E_r给完整消息上界；全零U₀/F₀/R事件另给完整非空性下界，行下界保持自己的事件范围。初始PGF Aχ(z)Bχ(z)^1280在z=21/20处给单坐标尾≤2^-138，64坐标并集给Pr(I^c)≤a_I=2^-132。无条件联合链完成后，用(L−a_I)/(1−a_I)与U/(1−a_I)限定I，条件显示端点保持；给定V和I的列独立性无需额外假定。

## 5. 现有AI复核身份

| 记录 | 实际身份/曝光 | 范围与计算 |
|---|---|---|
| ROUND-005旧攻击复核 | 一名AI的两阶段流程；phase1未见作者推导，phase2同审阅者读稿比对 | 固定A、选择、有限表与CF-1按各自封存范围沿用 |
| 精确LWE复核 | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 作者证明可见；丰富/固定样本与环上线性化范围；v2修正已落实 |
| 640首轮，01a1c4d6… | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 两份作者证明可见；375项总检查含100条引用指纹，作者脚本副本重放 |
| 640补充轮，01a1c4ed… | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 作者与前轮通过结论均可见；303项标量检查，两作者脚本副本重放 |
| v2作者整合及本轮审计 | 知情作者整合；知情应用/原声明审计 | v2重放303项；本轮不新增独立概率证明认证 |

两次概率审阅记录的精确后端型号均为null，所声明家族为GPT-6或Codex基于GPT-6；不同会话仅表明不同调用上下文，模型错误过程独立性未认证。新增人工、跨模型、盲审和证明助手认证均为0。检查计数记录执行范围，方法优先权与数学充分性由具体证明承担。

## 6. 三个最有决定性的人工问题

| 问题 | 最小输入 | 请判断的明确命题及改变后果 |
|---|---|---|
| H1：A是否为同一原游戏内的共同正确族攻击？ | 目标pp9–15；v2 §§2–6与附录B的640卷积证书；本入口§§1–3 | Ord列数规范化是否准确保持源对象；四查询/空Key终局是否合法；固定P₂后F₁保留与P₂-only停止是否足以支持所列优势，并与CF-1全样本正确性同合同。任何反例应指出具体输入、条件化或原游戏行 |
| H2：B的真实联合概率链是否完整？ | 目标pp12–15；官方规范10/25；v2 §7.2和附录D；两份作者标量证书及补充轮重算证书 | 同行列包、1280系数律、全频率绝对矩/弦线、坏质量、64/80位上取整、事件包含与I条件化能否严格推出完整错误≥99.9969655%，且保持均匀Setup量词。请给通过范围或具体失效式 |
| H3：哪些源条件安全声明能被严格评价？ | 目标pp19–20 Lemma6.8/Theorem6.9；v2 §§8–9及附录A；另需2024版Nishimaki Lemma5.7与构造/参数邻文 | 源归约究竟对应哪个(n,m,q,χ、秘密先验、辅助视图、时间、PPT/QPT)前提；能否给与CF-1匹配且已认证的非空困难前提。若仅能恢复H_rich，应将前件失效与构造攻击分别登记；若为H_fixed，须给足参数化模拟 |

H3所需前驱PDF当前403；可先审H1/H2，H3在取得带版本/公开日期/哈希的合法全文后完成。作者实际性能对象的判断另需commit/config/随机带和更新后消息比对轨迹，本入口不把缺失程序当作已实测的失败。

## 7. 直接阅读入口与文件分工

LINK_TABLE

原始阅读顺序为目标算法/游戏→命题A或B→对应完整证明→有限证书。人工审阅无需重读本项目业务系统材料。应用优先权的检索范围与缺项见同目录APPLICATION_PRIORITY_AND_IMPACT.md。旁支INC976仅涉及v2附录B的976显示表，两个主结果均使用χ640；当前历史文件保持只读。
'''
links=[
 ('目标期刊/v4',SRC/'arxiv_v4.pdf','原始游戏、算法、定理与性能表'),
 ('官方2021规范',BASE/'crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf','舍入、χ640、参数及基础正确性'),
 ('完整研究稿v2',V2/'CRYPTOANALYSIS_DRAFT.md','A：§§2–6、附录B；B：§7.2、附录D；LWE：§§8–9、附录A'),
 ('机器主张v2',V2/'CLAIM_EVIDENCE_MATRIX.json','C08/C09、C25a/C25d及完整精确概率证书'),
 ('640卷积证书',BASE/'crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json','A的完整64重整数系数'),
 ('作者单坐标证书',BASE/'crypto_fi_640_correctness_audit/evidence/SCALAR_CERTIFICATES.json','B初始PGF、坏环境、单坐标整数比较'),
 ('作者联合证书',BASE/'crypto_fi_640_joint_correctness/evidence/JOINT_SCALAR_CERTIFICATES.json','B的ν、全部频率、R/Q及L/U分数'),
 ('首轮概率审阅',BASE/'crypto_fi_640_probability_review/MATHEMATICAL_REVIEW.md','作者证明可见的完整概率链'),
 ('补充概率审阅',BASE/'crypto_fi_640_probability_review/review_01a1c4ed/MATHEMATICAL_REVIEW.md','作者与前轮审阅可见的完整链及呈现修正'),
 ('补充轮重算证书',BASE/'crypto_fi_640_probability_review/review_01a1c4ed/evidence/RECOMPUTED_PROBABILITY_CHAIN.json','303项检查与全部精确分数'),
 ('补充轮标量脚本',BASE/'crypto_fi_640_probability_review/review_01a1c4ed/evidence/recompute_probability_chain.py','确定性有限数学；阅读或复制重放均可，历史目录保持只读'),
 ('精确LWE审阅',BASE/'crypto_fi_lwe_independent_review/MATHEMATICAL_REVIEW.md','H_rich/H_fixed与环上线性化的已登记范围')]
table='| 材料 | 入口 | 用途 |\n|---|---|---|\n'
for label,p,purpose in links:table+=f'| {label} | {mdlink(p)} | {purpose} |\n'
human=human.replace('LINK_TABLE',table.strip())

source_links='''

## 来源与复核记录入口

'''
for r in source_records:
    source_links+=f'- **{r["id"]}**：[{r["title"]}]({r["url"]})。版本：{r["version"]}；公开时间：{r["public_date"]}。'
    if 'local_file' in r:source_links+=' 本地：'+mdlink(r['local_file']['path'])+'。'
    source_links+='\n'
source_links+='\n每项具体支持位置、获取时间、阅读等级及SHA256见 '+mdlink(EV/'SOURCE_LEDGER.json')+'；实际检索输入与原始返回见 '+mdlink(EV/'SEARCH_LEDGER.json')+'。\n'
write('ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md',original+source_links)
write('APPLICATION_PRIORITY_AND_IMPACT.md',impact+source_links)
write('HUMAN_REVIEW_ENTRY.md',human)

# Source-accounting checks are arithmetic of printed constants, not cryptographic experiments.
counts=[]
for n,D,T in [(640,15,1),(128,56,128)]:
    s=12;B0=2*n*s*s+s;W=2*n*n*D*s*s+2*n*n*s**3+n*D*s+n*s*s;Wp=2*(n*n*D*s**3+n*n*s**3)+n*D*s+n*s*s
    counts.append(dict(n=n,D=D,T=T,B=2,B0=B0,W=W,W_print=Wp,initial_plus_T_updates=B0+T*W,printed_T_update_bound=T*Wp,halfwidth=2**D//8,printed_sufficient_premise_satisfied=T*Wp<2**D//8))
official976=[11278,10277,7774,4882,2545,1101,396,118,29,6,1];display976=[11278,10277,7774,4882,2545,1131,426,138,38,8,1]
cert=jd(BASE/'crypto_fi_research_manuscript_v1/sources/PARAMETER_CERTIFICATES.json');cdf=next(x for x in cert['profiles'] if x['profile']=='976')['source_cdf']
derived=[2*(cdf[0]+1)]+[cdf[i]-cdf[i-1] for i in range(1,len(cdf))]
assert derived==official976
coeff=jd(BASE/'crypto_fi_research_manuscript_v1/sources/chi_976_64fold_coefficients.json')
dump(EV/'SCALAR_SOURCE_ACCOUNTING.json',dict(scope='Printed constant accounting and source-transcription check only',source_conditions=counts,incidental976=dict(v2_display_mass=display976,v2_display_total=display976[0]+2*sum(display976[1:]),official_mass=official976,official_total=official976[0]+2*sum(official976[1:]),historical_certificate_source_cdf=cdf,cdf_derived_matches_official=True,coefficient_total_matches_its_denominator=sum(map(int,coeff['coefficients']))==int(coeff['denominator']),full976_convolution_not_recomputed=True,main_A_B_chi640_unchanged=True)))

verdict={
 'schema':'fi-publication-impact-audit/verdict/1',
 'stage':'两项主结果的应用优先权与发表影响核查',
 'date_asia_shanghai':'2026-11-10',
 'status':'DRAFT_PENDING_FINAL_SOURCE_AND_DOCUMENT_QA',
 'identity':{'status':'INFORMED_APPLICATION_PRIORITY_AND_ORIGINAL_CLAIM_AUDIT','author_proofs_and_prior_reviews_visible':True,'declared_runtime_family':'Codex based on GPT-6 (visible declaration)','exact_backend_model_id':None,'new_independent_mathematical_reviews':0,'new_human_reviews':0,'new_cross_model_reviews':0,'new_blind_reviews':0,'new_subagents':0,'formal_proof_assistant':False},
 'frozen_input_files':[rec(V2/x) for x in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVIEW_RESPONSE_AND_READINESS.md','MANIFEST.json']],
 'v2_manifest_payload_verified':vh,
 'frozen_results':matrix['frozen_models'],
 'result_A':{'status':'SEARCH_BOUNDED_CONCRETE_OBJECT_APPLICATION_CANDIDATE','exact_same_FI_complete_public_precedent_located':False,'strongest_verified_method_precedent':'KLR2019 Def11/14 and AppB.2; mature affine inversion/support/convolution/rank/stopping tools','new_object_content':['FI original-game legality with zero Key and single challenge','fixed-A/fixed-P2 real-fresh anti-concentration','paid P2-only first-invertible amplification','same CF1 parameters with pointwise correctness and <=3n+1 calls Delta->1'],'parameter_scope':'FI printed general D>0 domain, explicit Ord normalization and iid chi640; extended relative to official D<=16 API','conditional_Theorem69':'H_rich false in CF1 by existing exact LWE audit; H_fixed and parameterized source reduction unresolved; nonempty-hardness-premise refutation unestablished','global_first_established':False,'public_priority_established_by_local_hashes':False},
 'result_B':{'status':'SEARCH_BOUNDED_CONCRETE_CONFIGURATION_RELIABILITY_RESULT','exact_same_FI_complete_public_precedent_located':False,'strongest_verified_method_precedent':'Official Frodo2021 section2.2.7 exact basic-PKE failure/convolution; FI Theorem6.3 residual recursion','initial_full_correct_lower':'1-2^-132','updated_full_error_percent_lower':'99.9969655%','conditioned_initial_correct_same_displayed_lower':True,'one_update_reliability_failure_supported_under_frozen_model':True,'Theorem63_premise_satisfied_at640':False,'premise_satisfied_counterexample_claimed':False,'one_finite_n_decides_all_asymptotic_correctness_families':False,'author_software_error_rate_certified':False,'timing_numbers_refuted':False,'global_first_established':False},
 'original_claim_summary':{'640_named_for_UE_TG_Upd':True,'D15_B2_chi640_correspondence':'Via cited official2021 Tables3/4 and2023 TablesA1/A3; not explicit run-config printout','performance_operations':['KG','Enc','Dec','TG','Upd'],'performance_variants':['640-AES','976-AES','1344-AES','640-SHAKE','976-SHAKE','1344-SHAKE'],'performance_run_count_reported':100,'post_update_decryption_comparison':'NOT_REPORTED; whether actually executed unresolved','numerical_max_update_count':'NOT_REPORTED','UE_decryption_failure_budget':'NOT_REPORTED','author_UE_source_or_run_commands_in_four_source_packages':False,'official_base_Frodo_repo_exists':True},
 'software_mapping':[
  {'missing':'Exact author UE commit/archive and dependencies/config','impact':'Bind timing tables to actual algorithm/version'},
  {'missing':'A generation and cross-generation reuse','impact':'Uniform-Setup B versus seed-expanded public-A law; A fixed-A theorem retained'},
  {'missing':'Secret-noise seed lengths/domain separation/stream slices/reuse','impact':'Preserve joint iid contract or prove bounded probability transfer'},
  {'missing':'Ord/Tensor and dtype/overflow/modulo/packing/rounding','impact':'Bind residual and decoding events'},
  {'missing':'Rank screening/retry/additional randomness/failure handling','impact':'Bind honest unfiltered law'},
  {'missing':'Enc-TG-Upd-Dec message comparison trace and raw100-run logs/depth','impact':'Establish measured correctness denominator and reproducible performance'}],
 'priority_scope':{'new_web_queries':31,'web_calls':9,'github_code_queries':4,'successful_issue_queries':2,'cutoff':'2026-11-10 Asia/Shanghai','historical_search_cutoff':'2026-11-08','no_hit_is_bounded_observation':True,'database_counts_not_priority_proofs':True,'full_text_gaps_not_treated_as_exclusions':True},
 'access_limits':[
  {'source':'Nishimaki ePrint2021/221 current PDF','state':'403_FORBIDDEN','reopen_input':'Legally accessible2024-04-19 extended PDF with Lemma5.7, construction and parameter neighbors, date and byte hash'},
  {'source':'Semantic Scholar ARXIV:2410.03948 metadata','state':'429_RATE_LIMITED','reopen_input':'Normal rate-limit expiry or authorized access; then fetch citation metadata/full originals, no bypass'},
  {'source':'CSS2022 UHE chapter full text','state':'PUBLISHER_SUBSCRIPTION_PREVIEW_ONLY','reopen_input':'Lawful author/institutional full text or supplied excerpt with version/page context'},
  {'source':'Lattice-codes PKE paper','state':'AUTHOR_PINNED_README_SCREENED_FULL_FORMULAS_NOT_READ','reopen_input':'Original paper if an explicit FI-equivalent update/error proposition is alleged'}],
 'incidental_finding':{'id':'INC976','status':'CONFIRMED_V2_APPENDIX_B_TRANSCRIPTION_REPAIR','v2_display_total':65718,'stated_denominator':65536,'official_and_certificate_CDF_match':True,'main_results_use_only_chi640':True,'historical_v2_edited':False,'next_action':'Correct the976 display mass and replay wording in a subsequent author version; full976 certificate audit separate'},
 'contribution_level':'Concrete published-construction source-hiding cryptanalysis plus finite-configuration reliability analysis and conditional-proof-scope audit; candidate standalone cryptanalysis short paper or thesis core chapter; generic method/global priority/human certification separate',
 'human_questions':['H1 same-object Ord/game/fixed-P2/stopping/common-correctness resultA','H2 true coefficient law/Fourier moments/full-message and conditional resultB','H3 exact source LWE premise/parameterized reduction and conditional theorem qualification'],
 'next_highest_value_external_input':'Exact author UE commit/config/randomness-and-arithmetic contract plus one message-checked Enc->TG->Upd->Dec trace',
 'action_counts':{'mechanism_implementations':0,'attack_prototype_runs':0,'LWE_solver_runs':0,'matrices_keys_tokens_ciphertexts_sampled':0,'large_crypto_experiments':0,'native_AS_RP_requests':0,'author_contacts':0,'emails_or_messages_sent':0,'external_model_calls':0,'new_subagents':0,'known_probability_script_replays_this_stage':0},
 'required_deliverables':['ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md','APPLICATION_PRIORITY_AND_IMPACT.md','HUMAN_REVIEW_ENTRY.md','VERDICT.json'],
 'evidence_entrypoints':['evidence/SOURCE_LEDGER.json','evidence/SEARCH_LEDGER.json','evidence/PUBLIC_ACQUISITION.json','evidence/INPUT_FINGERPRINT_VERIFICATION.json','evidence/VERSION_AND_SOURCE_COMPARISON.json','evidence/SCALAR_SOURCE_ACCOUNTING.json'],
}
dump(OUT/'VERDICT.json',verdict)
print(json.dumps({'core_files':[rec(OUT/x) for x in verdict['required_deliverables']],'input_fingerprint_records':len(refchecks),'web_queries':31},ensure_ascii=False))
