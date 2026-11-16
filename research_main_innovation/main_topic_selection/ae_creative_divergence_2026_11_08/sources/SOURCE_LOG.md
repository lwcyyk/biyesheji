# 来源与实际阅读范围

用户侧日期为 2026-11-08，Asia/Shanghai。原始获取时间采用 UTC 保存于各 .retrieval.json，哈希汇总于 SOURCE_MANIFEST.json。

## 正文

|文件|实际版本|页数|实际核读|
|---|---|---|---|
|minim.pdf|arXiv 2606.13949v1，2026-06-11|17|PDF 1–3、8 页与章节定位，8 页图像复核|
|skill_api.pdf|arXiv 2609.01677v1，2026-09-01|5|PDF 1–4 页，2 页图像复核|

MINIM 的论文记录标注 ICML 2026 接收，当前固定文件为上述 arXiv 版本。Skill-as-API 的 PDF 标有 KDD 2026 Workshop，当前未另行绑定出版社正式文件。两者按已取得版本使用。

两份 PDF 结构预检均为 PASS，页数一致，warnings 为空。完整数学独立审查与实验复现待取得。

## 官方文档

- AWS STS DecodeAuthorizationMessage，读取功能说明、专门权限、输出与错误。原文说明授权失败详情可能包含请求者无权查看的信息，解码需要 sts:DecodeAuthorizationMessage 权限。当前候选的基础机制由此取得直接产品先例。[文档](https://docs.aws.amazon.com/STS/latest/APIReference/API_DecodeAuthorizationMessage.html)
- Google Cloud Policy Troubleshooter，读取可见策略与排障权限段落。原文说明依据调用者有权查看的策略进行分析，并记录缺少相关策略权限时的 Unknown。[文档](https://cloud.google.com/policy-intelligence/docs/troubleshoot-access)
- RFC 6749，读取 §5.2 的错误类型、可选描述与 error_uri。invalid_grant 汇集多种原因。[文档](https://www.rfc-editor.org/rfc/rfc6749.html#section-5.2)
- RFC 9807，读取摘要、§6.3.2.2 的相关假响应内容和 §10.9 Client Enumeration。记录其 IRTF Informational 身份及注册流的不同范围。[文档](https://www.rfc-editor.org/rfc/rfc9807.html#section-10.9)

上述接口只作资料读取，本轮没有调用账户服务或执行诊断操作。

## 摘要级材料

本轮检索和查看摘要涉及以下直接近邻。

|arXiv|来源|作用|
|---|---|---|
|2609.22573|Zero-Trust Authorization and Discovery for Enterprise MCP|工具可见性与调用权限|
|2609.33371|API Secrets Should Never Become Tokens in the LLM's Vocabulary|凭证托管执行边界|
|1810.13354|Privacy Preserving Multi-Agent Planning with Provable Guarantees|私密搜索与规划的形式化先例|
|2606.03143|FederatedSkill|跨用户语义技能差分|
|2608.03700|When Agents Learn to Be You|persona skill 隐私与冒用风险|
|2609.28574|Change-Provenant Supervision|学习工件在政策改变后的再验证|
|2608.08264|OBLIVION|撤销技能的残余重建|
|2610.39234|AgentHeal|访问障碍下的目标保持恢复|

这些来源的完整定理映射和性能费用尚未核读。之前已取得的 Priva-See 摘要记录作为推断隐私背景复用。

## 检索与归属

本轮先保存 IDEAS_BEFORE_SEARCH.md，再开展针对性检索。模型在生成时已接触项目历史和一般知识，该顺序不能证明独立发明或公开优先权。

搜索限实际读取页面，部分查询有后续分页。精确查询未命中只记录该入口结果。本文没有用关键词空结果确认全球首次。

网络工具使用普通公开入口与默认 TLS 验证。脚本只负责下载、文本提取、结构检查、渲染、哈希及文稿检查。机制实现、参考实现、求解器与数学穷尽程序未开始。
