# SR-1证据索引、版本与实际阅读范围

取证日2026-11-07，Asia/Shanghai。主稿ID指本索引。原始网页/Markdown、获取状态、实际文件SHA-256在ACQUISITION_01–09.json和SOURCE_MANIFEST.json；历史字节在INPUT_HASHES.json。网页为持续更新版本，以下日期与hash固定本轮范围。

## 1. 本地课题及判废资产

|ID|来源与定位|实际使用|
|---|---|---|
|L01|[详细计划书2026-11-04](D:/毕业设计/面向AI智能体的认证语义感知与可撤销凭据管理方法及系统研究_详细计划书_2026-11-04.docx)：执行摘要、§§1–4、原参考R11–16/R30|从docx原XML提取阅读，保存LOCAL_PLAN_TEXT.txt；没有编辑Word或把计划目标当已实现|
|L02|[MR-1 DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_m1_profile_refinement/DECISION.md)、[Countertrace](D:/毕业设计/research_main_innovation/main_topic_selection/ae_m1_profile_refinement/REFINEMENT_OR_COUNTERTRACE.md)、[Authority](D:/毕业设计/research_main_innovation/main_topic_selection/ae_m1_profile_refinement/PROFILE_AND_AUTHORITY.md)|限定Casdoor4.25.0/CD425-M203-ORIGINAL、Local截止/known处置/A1未知仍接受、M₁未精化；不读取secret材料|
|L03|[SG-1 DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_strict_separation_gate/DECISION.md)：§§1–4|两族严格分离被强组合关闭，X-CUBE poly(N)停止；不复活旧例|
|L04|[MT-1 VALUE_AND_SCOPE](D:/毕业设计/research_main_innovation/main_topic_selection/ae_main_theorem_package/VALUE_AND_SCOPE.md)：§§3–8；[DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_main_theorem_package/DECISION.md)|完整M₁原子迁移前提/距离与真实B动作/空根费用差额|
|L05|[UR-1 MODEL](D:/毕业设计/research_main_innovation/main_topic_selection/ae_three_mode_radius4_cycle_form/MODEL_AND_EXCHANGE_LEMMA.md)：§§1–2|正常形以给定可行p/X为输入、满域/零成本、高型/原输出；未重审数学全证明|
|L06|[B4-1 DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_four_profile_radius3_cycle_form/DECISION.md)：§§1–5|四profile/r=3的β≤2及给定解转换费用；结构必要性与运行费分开|
|L07|[auth-lifecycle README](D:/毕业设计/auth-lifecycle/README.md)|现有有限/在线状态、Casdoor/对账入口与实际集成范围；本轮未执行源码|

## 2. 官方产品及网站原文

|ID|实际来源URL/章节|版本与核读结论|
|---|---|---|
|P01|[1Password for Agents](https://support.1password.com/1password-for-agents/)：Before you begin、How 1Password fills your logins|Published 2026-11-04；app≥8.12.42；US Individual/Families、Personal/Private；30天批准/网站自行管session；raw OP_AGENTS_RETRY|
|P02|[Security of 1Password for Agents](https://support.1password.com/1password-for-agents-security/)：Security/Authorization model、Accepted risks|Published 2026-11-03；enclave/扩展交付；信任agent developer及环境；登录后行为不在PM承诺内；raw OP_AGENT_SECURITY_NEW|
|P03|[Create an access request](https://www.1password.dev/agentic-autofill/partners/access-requests.md)：Batch、request字段、Write text、response|Partner preview；version2、1–5项、goal/reason为说明、keywords只排序、其他字段忽略；明确发票用例；同连接请求可跨browser session；OP_ACCESS_NEW.raw|
|P04|[Approval](https://www.1password.dev/agentic-autofill/partners/approval.md)：What person sees、Read grants、How long a grant lasts|30天、可复用、不绑chat session；配置寿命planned；entryId匹配及额外项处理；OP_APPROVAL_NEW.raw|
|P05|[Store keys and tokens](https://www.1password.dev/agentic-autofill/partners/keys-and-tokens.md)：Hold as one secret、Give each browser session|Partner preview；没有更窄session key，AT/key在browser内存，RT/backend；AT15min、connection约90d；OP_KEYS_NEW.raw|
|P06|[Disconnect](https://www.1password.dev/agentic-autofill/partners/disconnect.md)：What revocation does、What isn't available yet|v1alpha1/oauth-integrations/self:revoke；整连接/所有login，单登录尚不可用；OP_DISCONNECT.raw|
|P07|[Browserbase Agentic Autofill](https://docs.browserbase.com/integrations/1password/agentic-autofill.md)：Prerequisites、Connect user、Request/approve/fill、Expected output、ZDR|Extension API v1/request v2；合作方Business注册与独立US个人用户；填充时暂停读页；after-fill另验登录；录制/日志与下载/Context分列；BB_AUTOFILL.md|
|P08|[Browserbase Contexts](https://docs.browserbase.com/platform/browser/core-features/contexts.md)：默认目录、stored data、merge cookies、delete|默认每session全新；可cookies()/addCookies()导出/导入；持久化同步异步、Context删除限制未来session；BB_CONTEXTS.md|
|P09|[Manage session](https://docs.browserbase.com/platform/browser/getting-started/manage-browser-session.md)：Session termination/status|终态COMPLETED/TIMED_OUT/ERROR，脚本崩溃断连可COMPLETED，非业务完成；BB_SESSIONS.md|
|P10|[Update Session](https://docs.browserbase.com/reference/api/update-a-session.md)：Closing/OpenAPI；[Create](https://docs.browserbase.com/reference/api/create-a-session.md)|API v1；REQUEST_RELEASE请求结束，200请求成功、返回真实status；BB_UPDATE_SESSION.raw/BB_CREATE_SESSION.raw|
|P11|[Allowed Domains](https://docs.browserbase.com/platform/browser/security/allowed-domains.md)：Limitations|实验性；只top-frame、不拦iframe或XHR等；BB_DOMAINS.md|
|P12|[Navigation policies](https://docs.browserbase.com/platform/browser/security/navigation-policies.md)：What checks、Service workers、Edit/disable/delete|比P11覆盖iframe/popup/redirect，但不检查fetch/XHR/WebSocket；已启动session保持旧策略；BB_NAV_POLICIES.raw|
|P13|[SDKs](https://www.1password.dev/sdks)、[Connect](https://www.1password.dev/connect)、[Credential Broker](https://www.1password.dev/brokered-access.md)|SDK v0 vendor称production可用但频繁更新；Connect私有REST；Broker public preview OIDC工作负载验证/日志；OP_SDK.html/OP_CONNECT.html/OP_BROKER.md|
|P14|[1Password for NVIDIA OpenShell](https://www.1password.dev/environments/nvidia-openshell.md)：How works、provider配置、TTL|Beta；秘密custody转交gateway、沙箱placeholder、host/port/read-write/TTL；停止替换不证明已派生网站cookie关闭；OP_OPENSHELL.raw|
|P15|[GitHub payment/billing info](https://docs.github.com/en/billing/how-tos/set-up-payment/manage-payment-info#viewing-payment-history)|当前官方billing UI，个人/组织owner/billing manager；下载Receipt/Invoice；GH_PAYMENT_INFO.raw|
|P16|[GitHub sessions](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/viewing-and-managing-your-sessions)|现有Revoke web session UI；未给本轮测得传播时限或全世系证明；GH_SESSIONS_NEW.raw|
|P17|[GitHub OAuth scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)|建议更细GitHub Apps；已读scope不提供本轮已核的单月Invoice操作链；GH_OAUTH_SCOPES.raw|
|P18|[Cloudflare invoices](https://developers.cloudflare.com/billing/manage/invoices/)，[Markdown](https://developers.cloudflare.com/billing/manage/invoices/index.md)|Last updated 2026-09-29；自助Billing→Invoices and documents→download；企业invoice由accounting提供；CF_INVOICE_MD.raw|
|P19|[Cloudflare billing permissions](https://developers.cloudflare.com/billing/understand/billing-permissions/index.md)|Last updated 2026-05-04；Billing角色也可支付/改支付方式；API Billing Read/Edit；CF_PERMISSIONS.raw|
|P20|[CF User billing history](https://developers.cloudflare.com/api/resources/user/subresources/billing/subresources/history/methods/list/)|GET/user/billing/history，Deprecated，接受Billing Read/Write；JSON为billing history，未由本页建立PDF下载完整链；CF_API_BILLING.raw|
|P21|[Regular autofill behavior](https://support.1password.com/autofill-behavior/)|普通URL建议/填充匹配包括子域及相关站点设置；不把该页自动等同Agentic全部匹配规则；OP_AUTOFILL.html|

源组P13只证明各自官方能力，不把SDK原文取密、enclave填充和OIDC机器取密混为一个接口。P01消费页与P06 partner preview关于从1Password内断开的UI状态分歧保留；不能择一推导未核的单项撤销。

未取得可绑定的真实已安装SDK/extension二进制，产品部署成本/兼容性依实际准入后确认。这里固定的是文档版本、API字段和已给最低app版本。

## 3. 标准原文

|ID|来源/定位|作用|
|---|---|---|
|S01|[RFC7009](https://www.rfc-editor.org/rfc/rfc7009.txt)，2013-08，§2、§2.1、§2.2/Implementation Note|refresh撤销MUST/access SHOULD；关联域随AS政策；200也可为invalid token；传播延迟/已有材料/opaque token等边界；不对无关网站cookie自动生效|
|S02|[RFC9700](https://www.rfc-editor.org/rfc/rfc9700.txt)，2025-01，§2.4及token protection相关段|新OAuth客户端不应采用ROPC；不把网站表单密码登录混同该grant；PKCE/发行保护按实际实现|

RFC7009的目标是客户端在相应AS撤销token。1Password本轮实际backend API是P06的连接撤销，范围以其具体合同为准；两个来源不互换。

RFC的初次提取副本被统一为LF换行，原传输字节hash和提取文件hash因此不同。完整原字节已通过普通公开GET另存RFC7009.original.txt/RFC9700.original.txt，SHA与初次下载记录完全一致；ACQUISITION_09固定此恢复。语义定位可用提取文本，原文身份以original文件为准。

## 4. 本地公开预印本：版本及实际阅读

|ID|实际原文/版本|本轮范围与限制|
|---|---|---|
|W01|[SUDP PDF](D:/毕业设计/thesis_draft/sources/sudp.pdf)，arXiv2604.24920v4，2026-10-21，21页；SHA c5e41b345da3308c57b443fed9f8c91686627ebddfba6914a864f91ba2e833bc|§III/Definitions1–3、adversary/properties的已有文本和物理p1/p3图；明确CRC/CMC、custodian和派生可重用权力；未重审全部proof/实验；旧计划v3不当v4|
|W02|[Root-Scoped Quiescence PDF](D:/毕业设计/thesis_draft/sources/quiescence.pdf)，arXiv2609.21284v1，2026-09-18，39页；SHA 9c00c4fc6f5a112b5551ba94f843df468d6056e522e0b3325180e824ac4c0b95|已有文本intro、§3/Table2、§10.3–10.5；实际图p1、9、31、32；完整fence/manifest条件和opaque边界；未独立复核全定理/作者17轨迹|
|W03|[PAuth PDF](D:/毕业设计/thesis_draft/sources/pauth.pdf)，arXiv2603.17170v2，2026-08-25；首题Beyond OAuth: Task-Scoped Authorization for AI Agents via Natural Language Slices|首页/intro文本及p1整页图；每server NL slice/签名envelope前提；旧计划简称非当前完整题名；未核全证明/性能|

三项均按预印本登记，不升级为同行评审发表。当前arXiv页面请求TLS失败，本轮使用已取得的本地实际原文，没有宣称最新线上版本和全部后续工作已穷尽。

三个PDF预检各为结构PASS，页数/hash与实际文件关联；物理页图在page_images。首渲染批次有3条字体类型/嵌入字体不匹配警告，未按文件单独归因；所用页图已目视可读，解析/结构PASS不承担数学认证。没有复制全文到主稿。

## 5. 获取与研究边界

联网连接器本次为后端传输错误。Python正常HTTP部分成功、部分TLS EOF；随后正常PowerShell HTTP取得关键官网。所有失败保留实际状态：旧GitHub/CF路径404不推导功能不存在，OpenAI入口403未作为内容来源。GetMyInvoices官网TLS失败，未据产品名判其端到端覆盖。

所有读取为公开文档或本地已授权材料。没有访问真实账单URL、提交登录/撤销、解密本地凭据或查询在线AS。原文中的安装/调用示例均作为资料读取，没有执行。

本轮主结论限上述实际取得来源：任务有依据、C_exec标准组合可达、强化Native依赖实际接口/信任，尚无合格主创新差距。检索未穷尽商业产品；更强同合同产品只会进一步加强基线，仍应据实际原文/轨迹更新。

历史数学来源限制、COL2026暂停与FS23延期保持，两项请求均0。来源文件完整性检查、工作轨迹纸面分析、实际产品验收和学术优先权各自登记。

