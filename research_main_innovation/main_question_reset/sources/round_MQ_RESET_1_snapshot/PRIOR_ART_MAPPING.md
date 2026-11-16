# 直接先例、原文模型与淘汰映射

版本MQ-RESET-1，2026-11-05。原文及实际阅读定位见sources/READING_LOG.md。没有以检索未命中推断新颖性，也没有把第三方性能报告当作本轮复现。

## 1. K1的两项直接研究近邻

### B15：bounded counter与escrow

**Extending Eventually Consistent Cloud Databases for Enforcing Numeric Invariants**，Valter Balegas、Diogo Serra、Sérgio Duarte、Carla Ferreira、Rodrigo Rodrigues、Nuno Preguiça、Marc Shapiro、Mahsa Najafzadeh，2015；本轮使用arXiv1503.09052v1（2015-03-31），11页。[作者原文](https://arxiv.org/pdf/1503.09052)

核读摘要、§II模型/假设、§II-D、§III算法/正确性与优化、相关实现限制。原文将counter与下界的差分解为消费权利，权利在副本间分配；本地足够时消费，否则可取得权利或拒绝。矩阵R记录本地产生/转移，向量U记录消费，merge逐项max；localRights把已产生/收到的权利减去转出和已消费。它明确支持上界型不变量的对应形式。[SOURCE：PDF pp2–5]

副本可信，模型允许crash并从未损坏的持久内存恢复；它不保证恶意副本无法凭空修改自己的权利。每副本本地更新串行化、单调字段和持久状态是可用性/正确性前提。本文候选中“恶意代理”局限在可信执行器之外，因而可直接继承这个副本信任层次。[SOURCE/MODEL]

|原文变量/动作|本项目K1|成本对应|
|---|---|---|
|counter剩余值/数值界|共同批准剩余名额/零下界|单位消费对应一次准入|
|replica|可信执行器的额度管理副本|副本数n及每副本状态|
|localRights|本节点当前可消费权利|可消费范围和本地拒绝条件|
|decrement(n)|预留/消费n个名额|计数/持久化；实际provider调用另计|
|transfer(n,j)|把未消费额度转给执行器j|控制通信、等待、失败处理|
|merge max|合并单调消费/转移记录|状态或增量传输费|

在同一可信执行器、状态及转移接口下，这个映射保留消费可行域和费用类型。给候选一条免费全局额度查询或可信硬件共享计数，会同时给基线该能力。当前没有新协议差距。[DERIVED]

### I14：协调必要性及I-confluence

**Coordination Avoidance in Database Systems (Extended Version)**，Peter Bailis、Alan Fekete、Michael J. Franklin、Ali Ghodsi、Joseph M. Hellerstein、Ion Stoica，2014；arXiv1402.2237v4（2014-10-30），17页。[作者原文](https://arxiv.org/pdf/1402.2237)

核读§3系统合同、Definitions2–6、§4.2 Theorem1及AppendixB关键证明。原文对特定事务/不变量给出：全局I-valid系统具备无协调、事务可用和收敛，当且仅当事务I-confluent。事务可用性要求在本地不违反不变量且事务自身不选择abort时完成，避免用永久拒绝获得表面安全。[SOURCE]

K1取数据库为准入ID集合、merge为并、I为集合大小<=Q。最小Q=1分叉{r1}/{r2}各自合法、并后非法，直接成为Definition6反例。本文D1的独立轨迹合成是该协调边界的具体化；固定权利额度则改变允许事务前提，属于已有escrow路径。[DERIVED]

**K1先例裁决。** 标量额度、可信持久副本及独立本地消费的模型已覆盖。给更多代理、签名批准或换用OAuth术语，尚未改变这个归属。区分签名授权内容与全局消费状态具有系统设计价值，其原理属于已知结果。

## 2. K2的直接接口与协议近邻

### W25：群体列表、压缩与缓存

**Bitstring Status List v1.0: Privacy-preserving status information for Verifiable Credentials**，W3C Recommendation，2025-05-15；本轮使用[固定推荐版本](https://www.w3.org/TR/2025/REC-vc-bitstring-status-list-20250515/)，已取得canonical TR网页。核读§2.1–2.2数据模型、§3算法、§6隐私，尤其bitstring长度、关联及verifier caching。[SOURCE]

它以状态列表URI/index、GZIP及群体列表减少一凭据一URL的跟踪风险，说明地理请求、群体大小与关联问题。它提供的是规定模型的群体隐私，无法直接推出整个网络/验证过程不可链接。索引隐私候选必须把URI/cohort等泄漏纳入共同合同。[SOURCE/DERIVED]

### T26：JWT/SD-JWT/mdoc状态列表接口

**Token Status List (TSL)**，Tobias Looker、Paul Bastian、Carsten Bormann；`draft-ietf-oauth-status-list-21`，2026-06-21，拟Standards Track的Internet-Draft，非正式RFC。[固定原文](https://www.ietf.org/archive/id/draft-ietf-oauth-status-list-21.txt)

核读§4–8状态结构/接口/验证规则、§12.1–12.3隐私、§13.4/§13.7列表大小与更新/缓存。§8.1默认HTTP GET取得Status List Token，允许双方约定其他分发；§8.2要求优先使用token中的exp/ttl。§12明确群体隐私与传输大小的关系，并讨论唯一URI、IP及外部托管等侧信息。[SOURCE]

这与K2的实际需求同源，也构成强基线。以现有GET和不带index的共同URI下载整表，无需新增密码协议即可隐藏列表内的查询位置；合法缓存可复用。服务器支持PIR须新增接口/执行能力，双方共同计入。[DERIVED]

### P23：已有单服务器计算PIR及预处理收益

**One Server for the Price of Two: Simple and Fast Single-Server Private Information Retrieval**，Alexandra Henzinger、Matthew M. Hong、Henry Corrigan-Gibbs、Sarah Meiklejohn、Vinod Vaikuntanathan，USENIX Security2023，18页出版方PDF。[原文](https://www.usenix.org/system/files/usenixsecurity23-henzinger.pdf)

核读摘要、§1–3模型/定义、§4–5构造及成本、§8相关参数边界。算法显式为Setup(db)、Query(i)、Answer(db,hint_s,q)、Recover(st,hint_c,a)。安全为基于LWE的计算查询隐私，正确性允许明确误差；其定义保证忠实执行的取位正确性，不能直接充当恶意提供者的标准列表真实性保证。[SOURCE]

SimplePIR在方形N记录模型、固定参数下，公开预处理服务器费2nN模运算，客户端hint为n√N个域元素；每次查询上传/下载各√N元素，服务器2N模运算。原文实现使用n=2^10、q=2^32并给出具体误差/安全参数。DoublePIR已有递归减小hint的构造，完整评价需同时保留。[SOURCE：§4 InformalTheorem4.1/Remark4.1、§5]

作者在1GB数据库报告SimplePIR hint121MB、每查询总通信242KB；DoublePIR hint16MB、每查询345KB。单位按原文，§3将MB/GB定义为2^20/2^30 bytes。这些是作者报告，硬件/输入/复用次数与实际状态列表不同；本文未拿它们作本项目性能结论。[AUTHOR_REPORTED]

|对照项|G-list|G-PIR|
|---|---|---|
|功能|取得列表并本地取位、验证签名/有效期|取得指定记录；完整状态真实性需另作映射|
|查询隐私|同cohort全表获取不含index；保留URI/IP/时间泄漏|计算查询隐私；保留其参数与参与方模型|
|预处理|下载、压缩/解压、验证后可缓存|原文Setup和hint可复用，更新单列|
|接口|已有HTTP GET|新增PIR server及客户端协议|
|强度比较|可实现零错误取位；版本/接受遵循标准|计算隐私、正确性误差及HBC/忠实执行范围单列|

**K2裁决。** 索引隐藏核心由既有群体列表/PIR覆盖；单服务器完美无hint目标还受D2边界。端到端状态认证、版本及主动恶意响应映射尚需实际协议与接口，当前未据此认定为新空缺。两套标准与P23均为已实读直接近邻，覆盖角色分别登记。

## 3. 未取得来源及后续工作纪律

Spiral的准确题名和作者由P23参考文献可确认，但本轮作者PDF入口证书验证失败，其他获取尝试未成功，故未做其构造覆盖判断。ePrint编号探测未取得内容，不能据此确认版本。经典PIR原始作者页面/候选PDF也未取得，D2因此以自含计数证明和P23引用脉络登记，不声称完成全部PIR优先权审计。[获取日志sources/RETRIEVAL03.json]

本轮没有以2014/2015论文中的“未来工作”直接认定2026仍开放。所裁决的基本合同已有原文构造/定理；后续改进不会使其变成本项目的新主张。若要转向拜占庭权利、动态多维批准、可验证PIR或更新优化，需要重新提出有外部依据的精确问题，当前尚未保留这些作为额外候选。

## 4. 七项淘汰动作总表

|动作|K1|K2|
|---|---|---|
|成熟模型归约|准入集合/不变量与escrow数值权利|私有索引读取及公开状态群体列表|
|同模型参数化结果|I-confluence充要框架；bounded counter的n副本状态/优化|PIR的N/安全参数/hint/查询成本；完美无hint计数界|
|通用预处理|预分配权利、批量补充和本地计数已开放|列表缓存、PIR预处理与hint复用已开放|
|普通实现维护|合并批准组、统一权威事务可作为工程|标准字段、签名/ttl验证为规范维护|
|额外信息/信任|共享实时权威、可信不可回滚状态均计入|PIR服务、HBC/恶意模型、额外服务器不串谋均计入|
|合法功能变化|本地quota自治与任意节点全额度区分|列表内index隐私与完整匿名/真实性区分|
|实际操作粒度|集中式预算存在；分布式复制需新增能力|GET有公开标准；现项目TSL/PIR接口未实测/未实现|

决定性推导保持上述条件，当前两项均未通过严格分离门。
