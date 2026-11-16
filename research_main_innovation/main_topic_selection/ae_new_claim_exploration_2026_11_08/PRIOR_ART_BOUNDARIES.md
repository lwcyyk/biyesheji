# 先例边界与“没人做过”的当前证据

2026-11-08。当前对话内知情模型辅助核查。结论均限定到实际读取范围。

## 1. 本轮查新的准确状态

目前没有一条候选取得足以标注“全球从未有人做过”的证据。本轮从大议题推进到三个具体命题，并取得相关原文进行定点核读。

|候选|已经确认的已有基础|仍可探索的准确责任|当前状态|
|---|---|---|---|
|撤销预算规划|安全中断、有限状态规划和恢复语义已有基础|异构服务的预算内恢复策略、可靠抽象与完整组合费用|SPECIFIC_CLAIM_CANDIDATE|
|授权前提验证|完整性信息流、背书和认证应用已有直接理论|真实工具的可写状态与授权依赖的可靠推导及作用域保持|KNOWN_FORMAL_CORE_WITH_MAPPING_QUESTION|
|第三方私密异议|旁观者隐私、同意恢复、匿名凭证和私密计算已有基础|资格证据获取、处理范围、派生对象和滥用抵抗的联合协议|SPECIFIC_CLAIM_CANDIDATE|

这些状态使候选继续可研究，同时避免把已有基础本身申报为创新。

## 2. 新增原文与实际阅读

### Dynamic Safe Interruptibility for Decentralized Multi-Agent Reinforcement Learning

所读文件为 arXiv 1704.02882v2，2017-05-22，共 13 页。实际核读 PDF 第 1、4–5 页及定理位置索引，第 4 页完成图像复核。

§3 的 interruption scheme 包含给定的中断策略。Dynamic safe interruptibility 的条件涉及探索和学习更新对中断的依赖。该结果为候选提供重要先例，调用前需保持其状态可观察性、有限状态和学习模型假设。

本轮候选需要核验真实服务的停止状态、响应前提、恢复费用与任务策略。两个合同尚未完成相互归约。另有反应式综合、可控性与安全屏蔽等直接方法需要后续原文映射。[原文](https://arxiv.org/abs/1704.02882)

### Nonmalleable Information Flow Control

所读技术报告为 arXiv 1708.08596v2，2017-08-31，共 39 页。实际核读 PDF 第 1、3、8、22 页，其他页用于章节和定理定位，第 8 页完成图像复核。

报告提出 nonmalleable information flow 与 transparent endorsement，并给出类型系统。§8.2 涉及 HTTP Basic Authentication。它使“用信息流完整性约束授权前提”的宽泛主张具有直接先例。

后续必须进一步核对所有相关定理、证明和可适用的已有实现。当前新责任限定在工具语义、影响关系与部署前提的可靠映射。[原文](https://arxiv.org/abs/1708.08596)

### MIRAGE

所读文件为 arXiv 2609.24537v1，2026-09-21，共 16 页。实际核读 PDF 第 1、3–4、6–7 页与第 13–14 页相关参考文献，第 4 页完成图像复核。

§3.1–3.4 明确可信采集边界、TTP 与受保护区域范围。§4.3 描述身份匹配与作用域恢复，同时说明身份登记、通知和同意政策沿用前作。它已经覆盖旁观者保护与同意恢复的宏观思路。

论文直接引用的 SITARA、BystandAR、LensCap 和 Aragorn 是后续资格、同意与采集接口核查的重要原文。本轮没有取得这些论文的完整核读结论。[原文](https://arxiv.org/abs/2609.24537)

## 3. 摘要级近邻

本轮还通过公开搜索记录查看以下摘要。

- Matoi，arXiv 2610.21394，涉及后果证据复用、当前执行资格与持久发生记录。
- Attacker Control and Impact for Confidentiality and Integrity，arXiv 1107.5594，涉及 checked endorsement 与 robust integrity。
- When Assisting One Disempowers Another，arXiv 2511.04177，涉及用户代理对旁观者行动能力的影响。
- Full Provenance on the COSS Causal Axis，arXiv 2611.07164，以及 Beyond Proof of Possession，arXiv 2611.07159，涉及事件、因果历史和关系授权。搜索记录标注首次提交为 2026-11-04，早于本轮日期。

上述材料按摘要级证据使用，完整命题范围与证明尚待核读。

## 4. 检索覆盖

本轮查询围绕 agent revocation planning、safely interruptible、authorization causal、bystander consent、bystander credential、zero knowledge consent、robust endorsement information flow 及 objection privacy proof。

精确关键词缺少结果时，继续使用概念近邻与引用链。比如 bystander credential 返回空结果，MIRAGE 仍展示了与身份、同意和私密恢复直接相关的已有方案。该过程说明关键词命中范围与学术首次性需要分开判断。

所有原始页面、提取结果和响应时间保存在 sources。本轮没有进行全数据库穷尽检索。

## 5. 对“从未有人提出”的可核验替代陈述

未来若完成查新，可使用类似以下的限定表述。

> 在明确列出的原文、版本与模型范围内，尚未定位到能够给出该完整保证与费用的定理或标准组合。

采用这类表述之前，仍需完成相关原文与桥接推导。本轮尚未完成这一步。

## 6. 证据与实现状态

三份 PDF 的结构 preflight 均为 PASS，页数一致，warnings 为空。该检查只承担版本和页码取证。

论文阅读、命题形成与手工检查有模型辅助参与，外部领域读者意见待取得。机制实现未开始，代码操作限于资料获取与文档取证。
