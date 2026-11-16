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

| 路线 | 新定位依据 | 结果/状态 | 重开条件 |
|---|---|---|---|
| R01 期刊/DOI导出 | Target DOI/arXiv from frozen paper; current publisher export is an explicit metadata link | 当前JSON仅见预印本/PDF关系 | 新增软件或补充工件关系 |
| R02 arXiv关联工件/四版源包 | Four public arXiv source packages acquired and sealed in prior publication audit | 旧源包排版材料；当前代码锚点为通用服务 | paper-specific代码或新源包 |
| R03 WAT/JTIT身份链 | Target full author name/email plus WAT official contact page and primary JTIT ORCID link | 作者机构与ORCID线索成立，代码归属未闭合 | 作者/机构显式代码外链 |
| R04 机构员工页链接的精确作者ID | Official WAT staff page hyperlink58 identifies a specific institutional author profile | 作者记录403、库根超时 | 正常访问或合法导出 |
| R05 确切ORCID的公开record/person | Primary journal verified ORCID; narrower person endpoint follows full record timeout | JS/API访问未完成，网站字段未知 | 公开record/person导出 |
| R06 目标 coauthor及机构公开资料 | Target coauthor name/email and DBLP coauthor link124 | 未取得专属代码/ORCID链接 | 作者学术主页/标识链接 |
| R07 精确会议名称及官方历史链接 | Publisher names Central European Conference on Cryptology2024; official2025 site links2024 host; participant university lists exact conference-program URL | CECC2024根502/program不可访问 | 2024程序/摘要/补充材料归档 |
| R08 原论文资助编号→ISSIP-PKI | Original paper funding identifier DOB/002/RON/ID1/2018 resolves exact project ISSIP-PKI | 官方项目关系可核，未见目标UE发布 | 明确目标论文的项目工件 |
| R09 DOI/ID/作者→公开归档 | Target DOI/arXiv/title and source-linked author identity permit archive metadata queries | 索引未定位；Zenodo/DataCite访问错误 | 归档ID、DOI或恢复访问 |
| R10 机构邮箱及题名+作者代码查询 | Verified paper/WAT email identifiers plus author/title | 空返回或RSS；没有认证代码候选 | 明确仓库owner及论文关联 |
| R11 官方Frodo上游历史/发布 | Official Frodo project code link in previously sealed primary reading; original paper claims basis on official reference implementation | 上游文件已固定；UE扩展仍缺 | 作者fork/patch/driver |
| R12 arXiv代码发现服务锚点 | Current arXiv Code/Data anchors explicitly name CatalyzeX/alphaXiv services | 仅通用服务链接及有界检索 | 可核的paper-specific记录 |

每条路线的定位依据、原始URL、获取时间、工具原始返回及重开输入见[PUBLIC_ROUTE_LEDGER.json](D:/毕业设计/crypto_fi_author_implementation_audit/evidence/PUBLIC_ROUTE_LEDGER.json)。新增28条网页查询分布在9次调用；新做3条以机构邮箱/作者关系为依据的GitHub代码查询。旧题名、arXiv、UE.TG和issue检索按原回执复用。批次合并返回不被拆成虚构的逐查询零命中数字。

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

静态对应的文件/行号见[IMPLEMENTATION_MODEL_MAPPING.md](D:/毕业设计/crypto_fi_author_implementation_audit/IMPLEMENTATION_MODEL_MAPPING.md)，commit、tree、release、原始文件和哈希见[UPSTREAM_STATIC_FACTS.json](D:/毕业设计/crypto_fi_author_implementation_audit/evidence/UPSTREAM_STATIC_FACTS.json)及原始GitHub回执。上游公开issue35的CDF勘误已在v2.1认证，既有issue检索也未提供作者UE关联工件。

## 5. 取证裁决和最小补交

**可认证作者UE源码、六组配置、运行入口和带消息比对的真实运行记录，当前取得数均为0。** 这是本轮取证状态。作者曾报告实现与计时；现有材料不足以把该实现身份认证到一个可读取的版本。

最小补交材料为：

1. 作者、论文或机构明确关联到目标DOI的仓库/归档链接；或可认证声明与代码包SHA256。版本须可固定到commit、tag解析的commit或归档版本。
2. 包含Setup/KeyGen、Enc、TG、Upd、Dec、Ord/Tensor、六配置与计时driver的完整源文件，附依赖版本和实际入口/命令。
3. 一组640参数导出及随机性/算术说明，配一条未按结果筛选、具有原消息及初始/更新后消息比对的完整轨迹。六配置全部映射及原性能数字核准还需各配置与原计时日志。

获得后按[MINIMAL_REPRODUCTION_SPEC.md](D:/毕业设计/crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md)的来源认证→参数/随机性/算法/位序/算术静态对应→入口冻结→单轨迹记录→分母与模型裁决顺序核验。本轮未联系作者、发送消息或运行UE。既有理论结果和应用优先权状态保持原范围。
