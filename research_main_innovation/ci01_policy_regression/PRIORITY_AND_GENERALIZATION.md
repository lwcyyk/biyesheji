# 先例、可推广性与实例停止判定

## 精确模式

本实例中，token源仍有效、用户身份仍保存在会话，客户端权限上界却需要通过另一个Application对象取得。该对象缺失后，旧分支跳过限制而保留身份，真实全局self策略与字段许可随后允许效果。问题同时涉及依赖对象的生命周期、缺失值处理和权限组合，当前修复采用已有身份清理与匿名继续。

## 原则与论文先例

|工作|本轮核读与具体联系|覆盖判断|
|---|---|---|
|Saltzer与Schroeder，**The Protection of Information in Computer Systems**，1975，Proceedings of the IEEE；MIT作者全文[入口](https://web.mit.edu/Saltzer/www/publications/protection/)、[Basic Principles](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)|fail-safe defaults要求以许可成立为依据；complete mediation涵盖初始化、恢复、关闭及维护，并要求授权变化后更新已有检查结果|缺失限制对象后变得更宽松，以及应重新检查依赖，已有原则覆盖；不主张首创|
|MITRE [CWE-636](https://cwe.mitre.org/data/definitions/636.html)|取得官方说明；错误/失败时落入较弱保护或较宽许可状态的既有弱点类|本实例可按fail-open模式理解；这是机制归类，未授予CVE或厂商确认|
|**Verifying Account Ecosystems With Graph Transformations**，Murphy、Radomirović，EuroS&P 2026，DOI [10.1109/EuroSP68448.2026.00038](https://doi.org/10.1109/EuroSP68448.2026.00038)|既有项目全文中图转换、用户/攻击规则、完整性及可恢复访问模型|应用对象删除、会话继续、操作路径可以被既有状态模型表达；未据此推定同一具体缺陷已披露|
|**Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution**，2026，[arXiv:2609.21284v1](https://arxiv.org/abs/2609.21284v1)|既有全文Table2 A1/A4/A5/A6等对来源、载体和资源约束完整覆盖的条件|支持本例依赖必须完整表达；本轮未违反已满足其全部假设的定理|
|**AID-Guard: Stateful Authorization for Delegated Agent Effects**，2026，[arXiv:2608.21159v1](https://arxiv.org/abs/2608.21159v1)|既有全文的当前操作授权绑定及提供方效果契约|身份成立与具体操作获准应分别核验已有覆盖；本例的普通分支修正没有给出新协议增量|

后三篇采用已取得并核读的项目全文，其路径分别为`D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P08_全文.txt`、`P03_全文.txt`、`P05_全文.txt`。本轮新增公开资料保存在sources，下载状态、时间和哈希见[PUBLIC_SOURCE_LOG.json](PUBLIC_SOURCE_LOG.json)。

## 上游具体问题与修复

沿用已取得的官方patch：2026-09-27提交`dd6ed283bef4…`加入DCR token/session限制；2026-10-05 UTC提交`f3d937df3882…`恢复受限Cookie匿名继续并把客户端检查放到主体读取之前。它们直接证明同类token会话权限防线已有公开实现；原patch未明确描述本次“应用缺失且源token有效”的完整反例。[前阶段核查](../ci01_policy_consistency_review/NOVELTY_ASSESSMENT.md)

本轮定向GitHub issue/PR搜索三组：`DCR cookie`返回0项；`"deleted application"`返回22项；`"application" "session" "nil"`返回25项；去重44项，API报告incomplete_results=false。筛查标题和可见正文，保留以下近邻：

|公开记录|已描述问题|与当前实例的差别|
|---|---|---|
|[issue #4088](https://github.com/casdoor/casdoor/issues/4088)，2025，closed|数据库session删除后，某些自定义应用的Beego session仍可用|涉及session对象与会话存储同步；当前是Application权限对象缺失后跳过客户端限制|
|[issue #4092](https://github.com/casdoor/casdoor/issues/4092)，2025，closed|SSO多个应用的session处置范围未覆盖全部会话|范围覆盖/注销问题；没有在所读正文给出本次DCR nil应用→self操作链|
|[PR #4381](https://github.com/casdoor/casdoor/pull/4381)，2025，closed|提出跨应用会话删除及先处理Beego存储的修改|体现生命周期同步已有工程先例；本轮只取得检索返回的说明，未据closed状态宣称补丁已经合并或完整核读|

检索返回正文没有命中`checkDynamicClientSession`等本次精确分支标识。该结果只限定三组查询和返回资料，不构成未披露证明；评论、私有通告及所有版本历史没有穷尽。精确优先权保持未决，无“首次”声明。

## 两个限定上下文入口的源码对照

|入口|依赖对象|缺失时身份/权限|独立认证依据与解释|
|---|---|---|---|
|routers/base.go::clearSessionOfRevokedToken（原255–273）|会话中signinTokenId指向的token记录|记录缺失、失效或过期时复用clearSessionOfToken清除身份；本轮B09–B11经真实链拒绝|源ID为空可能属于独立原生登录；当前实现保留该区别。它是可复用的正确对照，身份源与限制源的角色有差异|
|routers/base.go::getUsernameByClientIdSecret（原134–168）|本次额外client凭据所指应用|应用缺失时Basic分支返回空身份，查询参数分支返回错误；未给无效Basic新增应用身份|Basic可能属于反向代理而非OAuth凭据，Cookie可具有另一独立合法来源。保护对象是新身份提取，不能一概要求清除所有独立Cookie|

二者说明缺失对象的处理应保持授权来源区分。相似nil分支本身不构成同一漏洞；同一实现的DCR/CIMD/跨组织配置也不增加漏洞数量。相邻授权页谓词及其他RP/资源路径没有被追加为新的运行对象。

## 可推广内容与主创新资格

可推广的审计问题是：身份资格、客户端限制和独立登录依据分别存在哪些对象中；删除/失效/解析失败时，是否跳过原应成立的限制。这可以形成回归检查清单与论文案例解释，但现有fail-safe defaults、complete mediation和状态转换验证已经覆盖基本原理。

当前没有定义一种方法在同样输入族、度量、接口、信任和成功范围内严格优于最强通用分析/测试方法。没有构造通用方法必须付更高代价的实例；新算法/协议候选数为0，实现门关闭。

**最终归档判断：完整离线链确认一项实现缺陷，最小普通修复覆盖已确认合同；保留为论文支撑性安全案例。** 其价值在于契约→源码→真实权限链→合成效果→修复的可复核证据链，以及三个未决兼容性变化的透明登记。当前证据不足以承担独立的高强度主创新。本实例按用户停止条件结束继续扩展。
