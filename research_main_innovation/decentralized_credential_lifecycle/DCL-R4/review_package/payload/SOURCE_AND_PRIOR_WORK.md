# 来源核验与原创性审计

版本提示：本文件主体保留DCL-R1的来源记录。DCL-R2新增精确核读范围、SC-A2A出版信息与抓取缺口见 DIRECT_PRIOR_WORK_COMPARISON.md；R1旧字节已存revisions/DCL-R1。更新不会把早期题录/摘要核验改写为当时已读全文。

检索日期：2026-11-09，Asia/Shanghai。研究范围截至当日可取得的公开材料。本文为有目的的近邻审查；系统性文献综述及全球优先权排除仍待完成。

## 1. 核验口径

P=同行评审正式论文/会议记录；A=官方标准/官方技术文档；D=公开预印本/个人草案；L=仅线索。级别描述来源成熟度，具体结论由已读内容承担。论文自述实验与证明均按作者报告引用，本轮复现实验为 0。作者/厂商利益关系在各自源类型中披露，独立 COI 调查尚待完成。

evidence/web/web01–web18.json 保存工具返回的检索片段、正文定位、URL 及失败记录。内容读取是分段的；网页可变版本以实际返回为准。web10 部分跨调用 ref 定位返回了与请求不同的 URL，相关结果按返回 URL 识别，未用作请求对象的阅读证据；后续 web11 使用绝对 URL 重取。文献摘要、实际章节、机器证明与本项目保证各自分列。

## 2. 用户指定的直接近邻

### P01 Horcrux

Hannah Li、David Evans，*Horcrux: A Password Manager for Paranoids*。arXiv:1706.05085，v1 2017-06-15，已读 v2 2017-10-10；[论文](https://arxiv.org/abs/1706.05085)、[PDF](https://arxiv.org/pdf/1706.05085v2)、[研究原型](https://github.com/HainaLi/horcrux_password_manager)。级别 D，正式发表状态本轮未另认定。

核读：摘要、§3.2 的 account entries/item lookup、§3.3 可信客户端、§4 多 keystore 失陷与§5 凭据恢复计时片段（web05/08/11/17）。分散保管与小可信使用核心直接重叠 D2。客户端重组/使用完整秘密的信任边界与保管节点失陷边界分别存在。D1 原生请求未决责任与跨域接管完整流程尚未从该文取得。可作为托管组件，结合工作流/原生控制构成 G；其原生接口为兼容传统登录表单，目标服务语义与本项目各自建模。

### P02 WAVE

Michael P. Andersen、Sam Kumar、Moustafa AbdelBaky、Gabe Fierro、John Kolb、Hyung-Sin Kim、David E. Culler、Raluca Ada Popa，*WAVE: A Decentralized Authorization Framework with Transitive Delegation*，USENIX Security 2019。[官方题录](https://www.usenix.org/conference/usenixsecurity19/presentation/andersen)、[作者 PDF](https://www.samkumar.org/papers/wave_security2019.pdf)。级别 P。

核读：摘要、§1.2 威胁模型片段、§2 授权图片段与§6.1 commitment-based revocation（web01/08/11）。跨域传递授权、撤销与可验证存储重叠。撤销依验证者查询及其 merge deadline；已读内容也区分已撤销证明资格与既得解密能力。本项目旧 Provider bearer 和异步效果须另外控制。官方页面/PDF 入口403，作者镜像可读；其余密码构造证明尚未逐节重审。通过标准组合可承担授权图一层，完整组合覆盖由 BASELINE_G 的构造承担。

### P03 SAGA-BFT / SAGA-HYB

Matthew D. Laws、Alina Oprea、Cristina Nita-Rotaru，*Attacks and Mitigations for Distributed Governance of Agentic AI under Byzantine Adversaries*，arXiv:2605.12364v1，2026-05-12。[正文](https://arxiv.org/html/2605.12364v1)。级别 D；核读版本固定 v1，后续版本状态待核。

核读：§III-D、§IV、§V-C、§VII 目录/结构定位（web03/04/05/11）。数据库和控制器 BFT 化直接重叠 D1；原文明示 BFT 完整性与机密性风险分开。HYB 的分片异构保障按分片处理，全部设计与实验仍待完整复核。原生外部服务与本项目凭据迁移合同不同；可作协调组件，无法仅由共识推出全部历史秘密失效。

### P04 AID-Guard

Yingzhe Tong、Leyu Dai、Songhui Guo，*AID-Guard: Stateful Authorization for Delegated Agent Effects*，arXiv:2608.21159v1，2026-08-21。[题录](https://arxiv.org/abs/2608.21159)、[正文](https://arxiv.org/html/2608.21159v1)。级别 D。

核读：§II-E、§III-A–E、§IV-C 及关联实验定位（web03–06/10）。同一批准/保留预算谱系、不确定结果、原生终态截止后单继任与 D1 高度重叠。威胁模型排除失陷可信主机/中介及未登记旁路；多地区权威线性化留作独立问题。其 Provider 合同要求稳定请求身份、与效果竞争的终态化、权威终态查询及期限内迟到阻断。可与 BFT/托管组合覆盖本轮恢复规则；原生与部署证明仍需各自满足。作者实验数据仅按论文报告，全部附件/证明尚未重放。

### P05 EFFECTBOUND

Igor Santos-Grueiro，*When Does Authorization End? Effect Closure at Provider Boundaries*，arXiv:2609.02866v1，2026-09-02。[正文](https://arxiv.org/html/2609.02866v1)。级别 D。

核读：§III-A–D、§IV-A–C、附录 C-E 定位（web03–05/17）。有限隐藏状态、可执行统一控制、效果前沿、保持外部合同的修复及配置后声明保持与 D2/JOINT 直接重叠。正文区分证据不足和模型内无解，部署符合性保持外部责任。可与故障/暴露变量和通用求解组合。本文报告 Lean 检查，本轮仅读其陈述及边界，Lean 工件未运行；所有真实 Provider 完整性也未由该文自动保证。

### P06 Root-Scoped Quiescence

Genliang Zhu、Chu Wang，*Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution*，arXiv:2609.21284v1，2026-09-18。[题录](https://arxiv.org/abs/2609.21284)、[正文](https://arxiv.org/html/2609.21284v1)。级别 D。

核读：§4.1–4.3、§5.4–5.6 定位、§6.3、§9.8/10 保障边界片段（web03–06）。实际选定 AND/OR 支持、独立充分支持、载体和跨域转移守恒、sink fence 直接重叠。它的原子 rebind 必须重验独立支持，来源字段更名缺乏该效力。Provider-free 测试作用域与原生部署分开。保护 sink 的新接受与已提交业务后果分开，本项目严格 C_effect 另需处理。证明附录与所有测试尚未完整重核；可作 G 的关闭/责任组件。

### P07 SC-A2A Gateway

Hyunwoo Kim、Mpyana Mwamba Merlec、Inseong Jeon、Hoh Peter In，*SC-A2A Gateway: A Blockchain-Powered Gateway for Session Grants and Audit in Agent-to-Agent Collaboration*，IEEE Access，2026，DOI [10.1109/ACCESS.2026.3742942](https://doi.org/10.1109/ACCESS.2026.3742942)。级别 P（题录），正文读取待完成。

核验：IEEE 搜索题录/摘要片段、Crossref 完整元数据（evidence/public_sources/SC_A2A_CROSSREF.json；web04/06/08）。Crossref created=2026-10-13，published 只列2026年，精确首发日期待核。摘要表明 session grant/策略/审计与广义链协作重叠；对未决原生责任、历史披露和 D2 配置保证尚待正文。IEEE 直取418，故本轮没有作“全文完整覆盖 D1/D2”的裁决。

### P08 Seal

Mysten Labs，*Seal Design* 与 *Security Best Practices and Risk Mitigations*，2026-11-09 实时文档快照。[官方设计](https://docs.sui.io/sui-stack/seal/design)、[官方仓库最佳实践](https://github.com/MystenLabs/seal/blob/main/docs/content/SecurityBestPractices.mdx)。级别 A（厂商文档）。

核读：IBE/链上访问策略/独立 key server 与 committee 模式说明、最佳实践 fetched-keys 段（web07/11）。门限秘密发放、策略治理与 D2 重叠；官方明确已取得派生 key 继续可用，链上撤回只停止未来取 key。设计页指向新版 v2 白皮书，本轮白皮书证明未核读，部署 committee 与具体信任假设待逐项固定。传统 Provider 的已披露密码与 bearer 需要独立原生撤销。可作为 G 的加密托管组件。

### P09 Lit Protocol

Lit Protocol，*Lit Protocol Documentation*、*Chain Secured*，2026-11-09 读取的 v3 / Chipotle 文档。[当前首页](https://developer.litprotocol.com/)、[Chain Secured](https://developer.litprotocol.com/architecture/chain-secured)。级别 A（厂商文档）。

核读：首页 v3、TEE 内密钥/Actions、链上权限及版本控制/运行暂停边界（web07/08/13）。旧 Datil URL 本轮重定向到 v3；早期检索片段中的网络门限/MPC 表述单独保留，未当成 v3 部署事实。链上规则＋可信使用与 D2/联合架构重叠；具体回滚、秘密输出和当前性证明仍待核，其能力未自动封闭外部网站旧 token。可用作 G 的受保护使用组件，完整实际安全性及版本优先权待证。

## 3. 新定位及基础近邻

|ID、完整题录/链接|已核内容与重叠|威胁/原生假设、覆盖与缺口|
|---|---|---|
|P10 Arnab Mallick，*Brief Announcement: Fair Binding for Hidden-State Authorization in Byzantine SMR*，DISC2026，2026-11-02，DOI [10.4230/LIPIcs.DISC.2026.58](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.DISC.2026.58)|官方题录/摘要，7页PDF入口（web06/07/08）；hidden policy 下 reserve/use 与公平性分离|正式论文 P；为“隐藏授权＋BFT”提供直接新近邻。后续 PDF 定位不可达，证明/完整模型尚未核读；本轮 D1 保持公开可验证规则，相关差异待逐条审查|
|P11 bnb-chain/BEPs 公开项目草案，*Agent Lifecycle Protocol v0.4-draft*；[原文](https://github.com/bnb-chain/BEPs/blob/master/BAPs/assets/bap-alp/protocol.md)|§§1、2.2/2.3、5 实际正文（web14/16/17）；义务善后、六阶段迁移、epoch、会计连续性|D；文稿日期/历史 commit 首发待独立认证，个人/项目提出者身份按仓库记录；智能账户/付款场景。普通迁移组织已高度重叠；原生旧签名另行处理|
|P12 R. Rampertab，*Replayable Authority Histories for Auditing Automated Agents*，draft-rampertab-audit-agent-authority-history-00，2026-10-29；[原文](https://www.ietf.org/ietf-ftp/internet-drafts/draft-rampertab-audit-agent-authority-history-00.html)|§§8.1–8.3及相关来源/新鲜度定位（web14–17）；duties、继任和预算保持|D，个人 I-D；明确职责随角色、grants 另行批准；重叠 D1 责任转移。§9/10 整体与执行真实性尚待补读，IETF 发布平台身份与标准认可分开|
|P13 Xinming Ou、Sudhakar Govindavajhala、Andrew W. Appel，*MulVAL: A Logic-based Network Security Analyzer*，USENIX Security2005；[官方全文](https://static.usenix.org/publications/library/proceedings/sec05/tech/full_papers/ou/ou_html/index.html)|摘要、§§1–2（web09/13），有限逻辑事实/规则与多主机能力传播|P；逻辑推理为 D2/G2 基础，原生状态与任务/迁移合同由本项目给定。整体联合配置覆盖采用本目录构造，未把 MulVAL 自身描述成全部优化器|
|P14 Hector Garcia-Molina、Kenneth Salem，*Sagas*，SIGMOD1987，DOI [10.1145/38713.38742](https://doi.org/10.1145/38713.38742)|出版方/Princeton题录（web09）；事务/补偿为 G1 组件|P 题录；Princeton正文403，补偿具体证明本轮待补。对不可逆效果的“未发生”仍需原生事实|
|P15 Collin Lee、Seo Jin Park、Ankita Kejriwal、Satoshi Matsushita、John Ousterhout，*Implementing Linearizability at Large Scale and Low Latency*，SOSP2015，DOI 10.1145/2815400.2815416；[官方PDF](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/126-lee.pdf)|官方摘要、作者和DOI检索核对，定位 RIFL 的 RPC 身份、持久结果、重试与元数据迁移（web06/13/18）|P 题录/摘要。效果与完成记录共原子域的条件，任意外部 SaaS 原生 key 保留需另证；全文未逐节核读，列为组件近邻|
|P16 T. Lodderstedt、S. Dronia、M. Scurtescu，*OAuth 2.0 Token Revocation*，RFC7009，2013；[官方](https://www.rfc-editor.org/rfc/rfc7009)|摘要、§2目录/语义与已取得标准文本（web09）；token/grant 撤销|A；具体 token 波及范围与接受方传播由 Provider 决定。异步业务效果和全部旧密码路径继续单列；全篇实现条款尚未逐节重审|
|P17 D. Fett、B. Campbell、J. Bradley、T. Lodderstedt、M. Jones、D. Waite，*OAuth 2.0 Demonstrating Proof of Possession (DPoP)*，RFC9449，2023；[官方](https://www.rfc-editor.org/rfc/rfc9449)|摘要、§1（web09），AT/RT 持有者约束|A；已泄露私钥的对手仍有能力，接收方合规及密钥保护由 profile 证明。实现/测试未运行|
|P18 Sangam Das，*Distributed Authority and Execution-Finality for Multi-Agent Systems, Delegated Operations, and Cross-Domain Gateways*，draft-das-distributed-agent-authority-finality-00，2026-10-23；[IETF登记](https://datatracker.ietf.org/doc/html/draft-das-distributed-agent-authority-finality-00)|题录、摘要/目录级检索，正文很长（web14–16）|D；个人草案，正式标准地位无依据。题名与摘要强相关，机制/证明/专利自述未核验，作为补读线索，未单独承担淘汰结论|

D1/D2 的关键覆盖论证使用本项目手工构造，依靠这些来源的成熟组件定位，未要求任何单篇已经发布完整同构系统。

## 4. 国内、专利及数据库覆盖

CNKI 定向搜索取得多条 cbpt.cnki.net 门户片段，主题包括 Fabric/CP-ABE、物联网多域访问控制；万方查询未取得可用于核心裁决的相关一手正文。题名/作者不完整项继续保留在线索日志，未编造参考文献。真正的数据库站内系统检索、学位论文与全文核读尚待执行。

公开专利搜索（web08/12）定位：US7382762B2 *Method and system for distributed certificate management in ad-hoc networks*；US12695750B1 *System and method for proxy-based credential custody with distributed validation*；US20260095308A1 *Systems and methods for secret-based operation execution in a trusted execution environment*；US20220263814A1 及故障域布置相关条目。当前只取得 Google Patents 搜索片段，作者/权利要求/优先权/官方原件/法律状态尚未核验。它们作为高重叠风险线索 L，未用于专利有效性或全球排除判断。

USENIX、IEEE S&P、CCS、NDSS、ESORICS、ACSAC、FC、TDSC/TIFS、ICDCS 使用了定向组合检索；正式原文的实际读取集中在上表。arXiv、IETF、GitHub 和官方文档取得直接内容；DBLP、Semantic Scholar 只有外部索引定向查询/链接定位，站内完整检索尚未完成；Google Scholar 未做站内检索；IACR ePrint 仅取得 HiSE 检索线索，正文待核。广泛关键词触及这些来源，尚不足以声明各会场查重完成。

## 5. 对创新主张的影响

- 持久未知责任、同意图预算、单继任、支持来源与迁移的广义功能已有直接公开重叠。
- 本轮 D1 的分布式扩展可由同能力 BFT RSM/工作流/托管/原生接口组合覆盖；该判断为构造性论证。
- 本轮 D2 增加的变量可由通用闭包和知识博弈表达；“标准求解器之前缺该字段”仅说明输入模型差异。
- 静态可切断性和历史 bearer 不可能性提供清晰边界，相关经典/新近先例的独立优先权仍待审查。
- 下一轮最有价值的实证来源是具体原生接口 profile 与部署模拟；搜索未见结果继续只按检索范围记录。
