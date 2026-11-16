# 去中心化凭据生命周期：D1 / D2 研究交付 DCL-R3

定稿日期：2026-11-10，Asia/Shanghai。DCL-R3继续原研究；R1的46份工件、R2的94份活动工件分别固定在revisions/DCL-R1与revisions/DCL-R2，锁定清单在evidence/r2与evidence/r3。原33输入保留。

本阶段入口：[NC1/NC2重新推导](R3_INDEPENDENT_CONCURRENCY_AUDIT.md)、[入口与创建截止](R3_NATIVE_ENTRY_CUT_AUDIT.md)、[具体BFT重配置](D1/BFT_RECONFIGURATION_PROTOCOL.md)、[证明与部署义务](D1/PROOF_OBLIGATIONS_R3.md)、[费用语义](D2/COST_SEMANTICS_R3.md)、[组合合同](JOINT/R3_COMPOSITION_CONTRACT.md)、[两轮强G反证](R3_STRONG_G_REASSESSMENT.md)、[原创性/状态裁决](R3_NOVELTY_DECISION.md)。

R3规范优先级：上述R3合同/实例/证明限定R2的21业务转换；R2文稿和历史证据保持原版本，未将后来结论改写成过去已经验证。CONDITIONAL_PROTOCOL_COMPLETE限纸面实例；原强B前缀支持仍由D2检验，单路径暂停场景不能通过。

R2阶段入口（历史）：[Casdoor能力审计](CASDOOR_NATIVE_CONTRACT_AUDIT.md)、[全部转换与原生轨迹](NATIVE_SEMANTICS_REFINEMENT.md)、[直接先例对照](DIRECT_PRIOR_WORK_COMPARISON.md)、[强G与四项分离反驳](STRONG_G_COVERAGE_AUDIT.md)。R2当时为Gate A静态范围通过、Gate B来源缺口、Gate C协议精化待证，实现门关闭。

本目录给出条件协议、联合配置模型、反例、强通用组合覆盖构造及后续验证设计。当前具有可审查的技术规格；严格优势实例、机器证明和外部独立复核仍待取得。实现门保持关闭。

建议阅读顺序：

1. [当前裁决](CURRENT_VERDICT.md)与[现状审查](CURRENT_STATE_AUDIT.md)。
2. [分离声明与实现门](SEPARATION_GATE.md)、[最强适用组合 G](BASELINE_G.md)。
3. [D1 协议](D1/PROTOCOL_SPEC.md)、[安全性质与证明](D1/SECURITY_PROPERTIES.md)、[反例](D1/PROOFS_AND_COUNTEREXAMPLES.md)。
4. [D2 模型](D2/CONFIGURATION_MODEL.md)、[算法及证书](D2/ALGORITHM_AND_CERTIFICATES.md)、[正确性](D2/CORRECTNESS_AND_PROOFS.md)。
5. [集成架构](JOINT/INTEGRATED_ARCHITECTURE.md)、[组合证明责任](JOINT/COMPOSITION_PROOF_OBLIGATIONS.md)。
6. [先例核验](SOURCE_AND_PRIOR_WORK.md)、[验证计划](EVALUATION_PLAN.md)、[下一步](NEXT_ACTION.md)。

evidence/INPUT_MANIFEST.json 固定 33 份本地输入的 SHA-256；evidence/web/ 保存本轮 18 批公开检索及正文定位结果，public_sources/ 保存 Crossref 元数据。哈希承担版本识别；语义与证明由正文中的论证承担。检索资料按实际取得范围使用，全文未核验项保留缺口。

以上18批为R1；R2新增公开正文定位保存于evidence/r2/web，26份固定版本源码及13项18字段能力记录保存于evidence/r2/native。R2_SOURCE_INDEX.json与CLAIM_LEDGER_R2.json汇总新证据及状态；文档完整性检查不承担协议验证。

本轮活动：源码与既有证据只读检查、公开资料检索、手工状态轨迹、条件证明、研究文档整理。新增机制代码、求解器实验、历史测试重跑、原生账号操作和外部发送均为 0。所有研究推导由当前对话内知情模型辅助完成；外部独立评审尚待取得。
