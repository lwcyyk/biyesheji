# 自主开户方向的新增原文与覆盖核查

2026-11-07，ENO-2。证据来自本轮公开获取及定点原文阅读。上一轮关于自主开户主线的推荐偏早，本轮依据新增材料收缩其贡献定位。

## 1. 新增来源改变了哪些判断

|拟研究内容|新增直接来源|本轮判断|
|---|---|---|
|新取得账户、凭证或服务的授权激活|Runtime Authorization for Resources Acquired by AI Agents，arXiv 2609.14744v2|有明确的模型、前提和安全定理，属于强近邻|
|跨控制层保持身份、授权与操作绑定|CONTINUITY，arXiv 2609.05269v1|已有assume–guarantee合同及端到端组合安全定理|
|账户接管后旧会话、备用身份继续生效|USENIX Security 2022账户预劫持论文|攻击与纵深防御已有正式发表结果|
|AgentID登录key的查询、更新与撤销|AgentMail官方Sign-In与Permissions正文|来源缺口已补齐，基线能力增强|
|身份提供方故障时的独立管理入口|Microsoft Entra emergency access官方指南|独立紧急账户是成熟基线|
|密码与passkey跨凭证管理器迁移|FIDO Credential Exchange官方概述|已有标准化方向，协议全文核查列入后续责任|

本轮研究判断围绕这些来源的实际保证。已发表结果、预印本、官方规范和产品文档在来源表中保留各自身份。

## 2. 新取得的论文

### 2.1 Runtime Authorization for Resources Acquired by AI Agents

作者为Genliang Zhu与Chu Wang，题名为Runtime Authorization for Resources Acquired by AI Agents，arXiv 2609.14744v2，PDF标注2026-09-18，共55页。

本轮核读摘要、§1.3–1.4、§2.3–3.4、Table 2、§4.6–4.8及§9.4–11。第7页Table 2已完整视觉复核。原稿的全部证明依赖链仍可在后续定点核验时展开。

原文把资源取得后的激活单独建模，覆盖账户、凭证、服务、计算资源和新主体。§4.8给出隔离、授权支撑、非放大、拆单一致性、崩溃恢复、退款及epoch等条件性安全结果。前提包含完整中介、可靠身份归一化、完整能力解析、持久事务、provider结果查询和效果线性化。

这项结果压缩了“新账户先隔离，再检查归属与权限，最后激活”的概念空间。用户在原运行商永久失效后的独立恢复能力，仍需在新增故障模型中单独推导。原文§10明确登记了部署前提和可用性边界。[原始记录](https://arxiv.org/abs/2609.14744)

### 2.2 CONTINUITY

Chris Zheng与Geng Yang，CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls，arXiv 2609.05269v1，共20页。PDF封面日期为2026-09-05，arXiv标注提交日期为2026-09-04。

本轮核读摘要、§3.3–3.5、§5.3–5.5、§9.6–12和附录起始证明说明。第7页组合条件和定理已视觉复核。

Theorem 1在C1–C7及密码学假设下给出端到端组合安全。其条件包括认证起点、合同兼容、上下文保持、权限约束、操作绑定、最终状态检查和完整中介。§12把可信根供应、实现精化和具体provider语义列为独立责任。

因此，“为多层授权加签名证据和组合合同”的一般方案已有强先例。新主张需要落在尚待建立的注册、恢复或特定协议保证上。[原始记录](https://arxiv.org/abs/2609.05269)

### 2.3 Pre-hijacked accounts

Avinash Sudhodanan与Andrew Paverd，Pre-hijacked accounts: An Empirical Study of Security Failures in User Account Creation on the Web，USENIX Security 2022，正文1795–1813页，所取PDF含会议封面共19页。

本轮核读摘要、§2.2–3、§4.2–4.4及§6.1–6.3。第16页的防御与自动测试讨论已视觉复核。

论文讨论了旧会话、额外身份和待确认邮箱变更等五类账户预劫持攻击，报告其分析的75个服务中至少35个存在一类问题。§6.2提出标识验证、结束旧会话及token、处理待确认变更、核对保留的外部身份等防御。

这些历史实验数字仅对应原论文的时间和样本。将攻击执行者换成代理，需要进一步证明新增条件和危害。[正式来源](https://www.usenix.org/conference/usenixsecurity22/presentation/sudhodanan)

## 3. AgentID来源缺口的补读结果

已取得AgentID Sign-In与Permissions完整Markdown正文。权限是scope与显式许可的交集，子key创建受父key有效权限限制。Sign-In文档提供公钥型登录key的查询、更新和撤销接口，说明创建它的bearer key与登录key具有独立生命周期。应用会话由应用管理，正文也列出对应生效边界。

这些接口扩大了可公平比较的基线范围。单系统领取、账户目录、登录key管理和按应用限制应进入组合覆盖推导。[Sign-In](https://docs.agentmail.to/agentid-sign-in.md) [Permissions](https://docs.agentmail.to/permissions.md)

上一轮的两服务纸面例继续承担合同检查作用。当前官方文档已明确若干独立生命周期，研究贡献需要进一步落实到新的协议责任或用户收益。

## 4. 恢复与迁移的额外强基线

### 4.1 独立紧急访问

Microsoft Entra官方指南建议配置独立的紧急管理账户，采用与正常账户不同的认证方式，并使其依赖独立于可能故障的联合身份提供方。指南包含维护、监控和定期验证要求。

因此，预设备用入口与独立恢复凭证应作为既有方案。候选需要计入备用入口的创建、保管、检测及维护成本。[官方指南](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access)

### 4.2 凭证交换

FIDO官方概述说明Credential Exchange规范处理凭证管理器之间的安全迁移，包含密码与passkey。此次阅读范围为官方概述和规范下载入口。具体版本、支持对象及迁移后的副本处置责任，列为定点全文核查项。[官方概述](https://fidoalliance.org/specifications-credential-exchange-specifications/)

将现有凭证搬到用户端的基础功能已有强标准化近邻。恢复原账户、撤销旧持有方以及服务端接管语义，需要结合对应服务接口映射。

## 5. 完成的标准组合推导

考虑k个账户，每个账户满足以下条件。

1. 用户具有独立于代理运行商的管理或恢复入口。
2. 代理持有的全部有效认证入口可以被用户枚举，或由服务提供覆盖完整的统一失效操作。
3. 代理角色无法删除用户的独立恢复入口。
4. 用户具有独立保存的服务地址、账户标识及必要恢复资料。
5. 目标服务和用户恢复设施可用，通信最终完成。

组合现成方案可先验证用户入口，再结束代理的认证入口，核对结果，最后向新代理签发所需权限。

对条件1、3、4，原代理运行商失效后用户仍有一条合法的恢复路径。条件2保证旧代理的全部认证入口进入处置范围。条件5保证这些有限步骤能够完成。新代理的权限由恢复后的用户独立授予。

若账户a的代理认证入口数量为d_a，这条组合给出O(k＋Σd_a)级别的逻辑管理操作上界，分页按返回规模计入，物理重试和服务延迟另计。该式描述完整信息及服务调用成功条件下的可行操作量。通用方法的必要代价仍需独立证明。

这个子域已经有标准组合解。该推导是本轮的纸面整合，用于收缩研究范围。

## 6. 当前仍有责任的目标

进一步的问题可加入以下故障条件。

- 原代理运行商永久不可用，用户仍需恢复原账户和业务数据。
- 创建或交接在任意协议阶段中断，某些provider已完成动作，另一些仍未确认。
- 代理可能保留早期材料，恢复过程需要阻止其重新取得管理权。
- 用户使用新设备，恢复资料的可达性和真实性需要得到保障。
- 各服务提供不同的恢复、角色和撤销能力。

本轮已核读结果尚未形成这组合同的完整覆盖链。紧急访问、备份、SCIM、标准邀请、凭证交换及原生安全接口都应向强基线开放。新贡献仍需通过该组合的挑战。

## 7. 获取与阅读限制

|项目|本轮状态|
|---|---|
|3份新增PDF|全文取得，结构预检PASS，相关章节定点核读，3页视觉核查|
|AgentID Sign-In及Permissions|全文取得并读取相关能力与生命周期说明|
|AgentPass|官方GitHub项目识别为clerk/agentpass，homepage关联agentpass.com。网站连接关闭，GitHub内容接口遇公开API限额|
|Notte|官方项目识别为nottelabs/notte，具体Persona文档本轮仍有获取缺口|
|搜索连接器与GitHub连接器|传输故障，使用正常公开HTTP补充取得可读来源|
|FIDO Credential Exchange|官方概述取得，规范逐条覆盖待核|
|预印本优先权|按公开版本比较，发表状态及后续版本另核|
|真实工作流|本轮为文档与纸面分析，生产验证证据待取得|

获取记录保存在sources/RETRIEVAL_*.json。下载PDF的SHA-256及实际阅读范围保存在来源清单。GitHub限额出现后，仓库内容核读登记为待补。

本轮对协议的组合能力和条件性推导进行核查。通用安全证明的完整重验、真实用户研究和实现测试列入后续工作包。

