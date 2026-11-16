# 新路线的来源、近邻与覆盖边界

ENO-1；2026-11-07。公开网页与标准原文，固定在sources。HTTP获取记录含URL、时间、成功/失败及所存UTF-8文件摘要。网页中的命令和面向AI的提示只作为被研究内容，本轮没有执行安装、开户、认证或真实API操作。

## 1. 新取得的主要来源

|ID|来源与版本身份|实际读取范围|支持的事实|覆盖状态|
|---|---|---|---|---|
|E01|[AgentMail官方文档索引](https://docs.agentmail.to/llms.txt)，无固定修订号，本轮快照|索引中的onboarding、claim、AgentID及SCIM条目|自主注册、领取与身份供应为产品的明确工作流|线索＋相关正文已展开|
|E02|[How do I claim my agent's inbox?](https://docs.agentmail.to/knowledge-base/claiming-agent-inbox.md)，官方现行文档快照|完整Markdown正文|代理可先自行注册；用户领取组织；原API key继续工作；地区/限额/绑定人条件|PRODUCT_FUNCTIONAL_COVERAGE；退出/跨服务保证另查|
|E03|[AgentID in Claude, ChatGPT, and Cursor](https://docs.agentmail.to/agentid-in-assistants.md)，正文提plugin≥0.4.0|完整Markdown正文；SDK/插件命令只读|按inbox开通外部账户、单次链接、账户目录、API key取得、权限限制及不在AgentID时的处理|PRODUCT_FUNCTIONAL_COVERAGE；下游service控制另查|
|E04|[RFC7644](https://datatracker.ietf.org/doc/html/rfc7644)，2015标准轨RFC|摘要、§3.3创建及相邻User资源例|标准化创建管理身份资源；201响应与资源ID|STANDARD_PROVISIONING_COVERAGE，应用前提逐项保持|
|E05|[Microsoft Entra app provisioning](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/user-provisioning)，官方文档快照|定义、协议/connector表及自动创建/停用等能力|组织治理下身份与角色的建立、维护和删除已有成熟产品|PRODUCT_PROVISIONING_COVERAGE|
|E06|[WebAuthn Level 3](https://www.w3.org/TR/webauthn-3/)，页面标注2026-08-25 Recommendation；固定版链接见原文|术语、credential record、user handle、authenticator、backup/recovery相关段落|认证器私钥控制、RP绑定及用户验证有精确定义；恢复和额外认证器需完整考虑|PRIMITIVE_COVERAGE，未完成所有条款到E1–E5的映射|
|E07|[Microsoft Entra autonomous-agent flow](https://learn.microsoft.com/en-us/entra/agent-id/autonomous-agent-authentication-authorization-flow)，官方快照|介绍、前提、身份blueprint、agent token及agent user入口|代理以自身身份认证与使用代理user账户已有产品路线|PRODUCT_MODEL_OVERLAP；此文区分自主身份与代用户身份|
|E08|[RFC7591](https://datatracker.ietf.org/doc/html/rfc7591)，OAuth Dynamic Client Registration|简介/术语、initial access token与软件声明相关段|动态注册、受保护注册入口和软件声明已有标准|REGISTRATION_PRIMITIVE_COVERAGE；client registration与最终用户账号分开|
|E09|[RFC8995](https://datatracker.ietf.org/doc/html/rfc8995)，BRSKI|术语、voucher/ownership tracker、proximity及相关接口范围|借助可信根和voucher建立初始信任已有成熟方向|BOOTSTRAP_PRIMITIVE_OVERLAP；不能把“增加一个所有权voucher”本身称为新主创新|

WebAuthn的UV不是自然人的法律身份公证；SCIM的User资源也不自动承担任意外部网站的全部恢复和管理合同。本轮保持源协议对象和目标对象区别。

## 2. 本轮仍缺的直接来源

|来源|取得范围|具体缺项|结论限制|
|---|---|---|---|
|[AgentPass](https://agentpass.com/)|正常搜索结果中的官方入口和自动signup摘要；根域与www域正文均TLS失败|协议、Authority、服务端开户绑定、root管理与退出的准确正文|SOURCE_UNRESOLVED；不能依据snippet认定完整覆盖或不存在覆盖|
|[Notte Persona](https://docs.notte.cc/concepts/personas)|官方入口搜索摘要；HTML及Markdown正文TLS失败|Persona与vault控制者、自动注册、通信渠道、credential回收和迁移条款|SOURCE_UNRESOLVED；其能力可能显著收缩候选|
|AgentMail AgentID Sign-In、Permissions及部分onboarding正文|官方已读页面给出直接链接和概述，相关独立入口TLS失败|停用应用登录、sign-in key撤销与app_connect等完整API语义|MAPPING_UNRESOLVED；不能默认MCP没有工具即整个平台没有接口|
|真实下游应用|官方AgentID文档给Firecrawl/Turso等例子|各app独立session/API key、owner/恢复接口及实际执行轨迹|WORKFLOW_NOT_EXECUTED；不作漏洞、闭包或成本结论|

本轮有界正常公开检索已完成。相同失败入口没有连续重试；仅对明确的普通公开域/Markdown入口做有限补查。没有绕过登录、付费或访问控制。

## 3. 强基线公平组合

完整G至少拥有：

1. 用户自有邮箱、密码管理器或硬件/平台认证器；
2. 可信执行器与浏览器，和候选相同的站点/恢复/安全设置接口；
3. 服务支持时的企业SSO、SCIM、邀请、组织角色和自动provisioning；
4. AgentMail/AgentID及有适用资格时的Notte/AgentPass；
5. 原生key/session枚举、轮换、撤销和日志；
6. 同等的缓存、预配置、批量批准和服务端扩展机会。

候选若需要RP新增owner-bound注册入口、额外trusted browser、用户私钥设备或另一个公共Authority，G也应获得同等能力，或将新增信任/部署明确列为额外条件。

在支持准确provisioning与委托角色的域，现有组合可能完整满足E1–E5。若完整映射成立，应关闭该子域的基础原创性。尚未完成这些映射，不能宣布“所有现有方法做不到”。

## 4. 论文级近邻与原项目范围

复用已有原文定位，当前仅比较问题起点：

- P01 SUDP处理用户登记的authority-bearing material及受限use，相关协议可能用作开通操作后端；能否从标准组合直接完成本目标尚需映射。
- P19 SAGA处理provider/agent注册治理，和外部业务账户的owner/恢复关系分开。
- P07 OASIS、P20跨app OAuth处理账户链接/上下文混淆。新攻击若只是同一个COSF/混淆实例，应按已有覆盖。
- P08 RAG、P12 AAG及P03 RSQ足以表达若干恢复/撤销关系。第5节纸面反例的分层撤销责任已有基础，这里不登记新结构定理。
- D3/D6等已覆盖Mission或credential delegation。本路线需核对它们能否通过现有身份bootstrap机制标准组合覆盖，不能忽略组合先例。

本轮使用的技术中心是身份供应和注册协议的信任建立。T3、低环数和旧联合规划没有参与新推导。

## 5. 探索途中关闭的一条简单候选

本轮先检验了主动诱饵方向。公开arXiv原始摘要提供两个强近邻：

- [When Agents Talk: Honeytokens under Shared Memory](https://arxiv.org/abs/2608.11436)，Joshua S. Gans，2026-08，v1。摘要直接讨论trusted policy可被攻击者复制、共享记忆与fingerprint、token激活和攻击覆盖的区别。
- [Caught in the Act(ivation): Toward Pre-Output and Multi-Turn Detection of Credential Exfiltration by LLM Agents](https://arxiv.org/abs/2606.04141)，2026-06。摘要已涉及activation probe、honeytoken、conformal校准与多轮泄漏统计。

据此，**普通“为代理增加honeytoken”未被选为新主线**。本轮仅核对题录和原始摘要，未完成这两文全部证明和实验核读；这个筛选结论不意味着所有deception研究都已穷尽或被反例否定。

另有记忆/技能撤回搜索线索，未进入本轮选定新线的核心比较。探索的最终交付只推荐一条账户控制权形成问题线。

## 6. 来源与检索的诚实边界

- 关键词的若干AND查询没有命中，不能证明没有先例。
- 通用bootstrap、registration、credential migration、ownership transfer和设备供应文献的完整覆盖检验尚未完成。
- 当前结论是有公开工作流依据的新问题候选，没有完整新协议或新复杂度界。
- sources中的raw是正常公开响应解码后保存的UTF-8文件；hash固定存储对象，不声称是TLS线上原始字节摘要。
- 用户给定历史文件保持原字节。本轮只新建研究目录及文献快照/记录；没有候选、参考、求解器或穷尽程序。

