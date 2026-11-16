# 查新边界与当前结论

2026-11-08。当前对话内模型辅助发散与知情核读。

## 1. 逐项判断

|构想|已经确认的先例|本轮形成的更具体责任|状态|
|---|---|---|---|
|账户与权限清单隐私|观察最小化、隐藏技能、权限过滤发现、私密规划|允许任务交互中的完整清单隐私、主动探测与任务完成性|HYPOTHESIS_REQUIRING_MAPPING|
|模型能力变化后的授权认证|推断隐私、模型评估、政策改变后的工件治理、增量验证|区分模型无关保证和能力相关保证，形成可靠的保留或失效证据|HYPOTHESIS_REQUIRING_MAPPING|
|任务经验的复用许可|联邦技能、persona skill 风险、技能封装和撤销|可释放抽象、受限技能导出、作用域及完整效用与费用|HYPOTHESIS_REQUIRING_MAPPING|
|分级私密诊断|AWS 受控诊断解码、Google Cloud 权限感知排障|跨服务联合原因与最小修复信息的保证|BASIC_MECHANISM_HAS_DIRECT_PRECEDENT|

四项都没有达到“全球首次”的证据等级。候选中的具体增强命题继续开放。

## 2. 本轮正文核读

### MINIM

取得 arXiv 2606.13949v1，2026-06-11，共 17 页。核读 PDF 第 1–3、8 页，其他页作章节定位，第 8 页完成图像复核。

§2–4 以可信本地 broker、结构化观察、敏感度与任务必要性预测为基础。威胁模型采用 honest-but-curious 远端代理。PDF 第 8 页明确将主动对手和长时程累计隐私列入边界，并提出未来的时序隐私核算。

因此，任务相关的本地观察最小化已有直接先例。候选要比较其主动交互、账户状态和完整会话保证。不能从本文的限定范围推断其他方法都缺少相应保证。[原文](https://arxiv.org/abs/2606.13949)

### Skill-as-API

取得 arXiv 2609.01677v1，2026-09-01，共 5 页。核读 PDF 第 1–4 页，第 2 页完成图像复核。

§3.1 给出只公开 schema view 的封装，§3.4 对隐藏及不存在技能使用同一错误字符串。原文也明确讨论输出泄漏、时间侧信道、跨步输入污染和 schema 推断等剩余范围。

“技能实现没有被直接序列化发送”与所有输出、时间和调用结果的语义保密分别承担证明责任。本轮只按其实际结构与声明范围比较。[原文](https://arxiv.org/abs/2609.01677)

## 3. 官方规范与产品核查

|来源|实际读取|本轮判断|
|---|---|---|
|AWS DecodeAuthorizationMessage|说明、专门权限、返回内容和错误|诊断详情受专门权限控制已有产品先例|
|Google Cloud Policy Troubleshooter|策略可见性、所需权限、Unknown 范围|排障能力与策略读取权限绑定已有产品先例|
|RFC 6749|§5.2 Error Response|一个错误码可覆盖多个具体原因，另有可选描述与 URI|
|RFC 9807|摘要、§6.3.2.2 相关内容、§10.9|OPAQUE 对客户端枚举及假响应作出明确说明，注册流另有边界|

RFC 9807 为 IRTF Informational 文档，按 CFRG 协议文档身份登记。其原文明确区分自身状态与 IETF 标准。

## 4. 摘要级先例

本轮还核读以下公开摘要，完整命题与证明尚待取得。

- Privacy Preserving Multi-Agent Planning with Provable Guarantees，arXiv 1810.13354，提出搜索算法的精确安全计算概念与 Secure-MAFS 证明。
- Zero-Trust Authorization and Discovery for Enterprise MCP，arXiv 2609.22573，涉及权限过滤可见性与调用强制一致性。
- FederatedSkill，arXiv 2606.03143，采用语义技能差分进行跨用户技能演化。
- AntiSkillBench，arXiv 2608.03700，研究 persona skill 的隐私与冒用风险。
- Change-Provenant Supervision，arXiv 2609.28574，区分登记依赖与独立当前合同复核。
- OBLIVION，arXiv 2608.08264，研究通过残余载体重建已撤销技能。
- AgentHeal，arXiv 2610.39234，涉及访问障碍下的目标保持恢复。

这些来源支持近邻识别。它们的作者实验结果没有转化为本项目的性能证据。

## 5. 检索范围

检索词覆盖 agent credential metadata、policy privacy planning、model upgrade privacy、consent model upgrade、agent skill privacy、workflow unlearning、authentication error privacy、authentication diagnostic 及 privacy multi-agent planning。

其中 consent model upgrade 的精确组合返回空结果。相关推断隐私、政策变化和增量验证仍有明确先例，因此该空结果只记录本次入口的返回范围。

原始页面、摘要提取和获取记录均位于 sources。部分查询有分页，本轮范围限实际取得和查看的页面。

## 6. 下一阶段的并列问题

1. 清单隐私候选应与私密规划、MPC 和本地观察抽象做完整合同映射。
2. 能力变化候选应建立准确的模型相关假设，再核验标准增量验证是否足够。
3. 技能复用候选应对受限导出语言与信息流、程序切片、联邦技能方法逐项比较。
4. 私密诊断候选应把 AWS、Google Cloud 的现成能力组合后，再检查跨服务和最小披露是否仍有新增责任。

本轮保留四条探索路线。创新资格与实现资格各自需要后续证据。
