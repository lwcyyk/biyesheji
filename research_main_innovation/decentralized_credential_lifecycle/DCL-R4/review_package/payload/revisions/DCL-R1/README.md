# 去中心化凭据生命周期：D1 / D2 研究交付

日期：2026-11-09，Asia/Shanghai。版本：DCL-R1（含多轮纸面设计、自我反驳与修订）。主课题：面向用户与 AI 智能体的全生命周期密码与凭据管理系统。

本目录给出条件协议、联合配置模型、反例、强通用组合覆盖构造及后续验证设计。当前具有可审查的技术规格；严格优势实例、机器证明和外部独立复核仍待取得。实现门保持关闭。

建议阅读顺序：

1. [当前裁决](CURRENT_VERDICT.md)与[现状审查](CURRENT_STATE_AUDIT.md)。
2. [分离声明与实现门](SEPARATION_GATE.md)、[最强适用组合 G](BASELINE_G.md)。
3. [D1 协议](D1/PROTOCOL_SPEC.md)、[安全性质与证明](D1/SECURITY_PROPERTIES.md)、[反例](D1/PROOFS_AND_COUNTEREXAMPLES.md)。
4. [D2 模型](D2/CONFIGURATION_MODEL.md)、[算法及证书](D2/ALGORITHM_AND_CERTIFICATES.md)、[正确性](D2/CORRECTNESS_AND_PROOFS.md)。
5. [集成架构](JOINT/INTEGRATED_ARCHITECTURE.md)、[组合证明责任](JOINT/COMPOSITION_PROOF_OBLIGATIONS.md)。
6. [先例核验](SOURCE_AND_PRIOR_WORK.md)、[验证计划](EVALUATION_PLAN.md)、[下一步](NEXT_ACTION.md)。

evidence/INPUT_MANIFEST.json 固定 33 份本地输入的 SHA-256；evidence/web/ 保存本轮 18 批公开检索及正文定位结果，public_sources/ 保存 Crossref 元数据。哈希承担版本识别；语义与证明由正文中的论证承担。检索资料按实际取得范围使用，全文未核验项保留缺口。

本轮活动：源码与既有证据只读检查、公开资料检索、手工状态轨迹、条件证明、研究文档整理。新增机制代码、求解器实验、历史测试重跑、原生账号操作和外部发送均为 0。所有研究推导由当前对话内知情模型辅助完成；外部独立评审尚待取得。
