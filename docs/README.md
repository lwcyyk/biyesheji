# VDNS-PM 文档入口

当前项目指导基线为 **VDNS-PM v2.0.0 / G0.2**。

建议阅读顺序：

1. [研究生毕业设计开发报告](VDNS研究生毕业设计开发报告.md)：项目定位、总体设计、实施与论文结构；
2. [Spec 001](../specs/001-vdns-audit-rotation/spec.md)：规范性 FR/NFR/AC；
3. [实施计划](../specs/001-vdns-audit-rotation/plan.md) 与 [任务清单](../specs/001-vdns-audit-rotation/tasks.md)：开发顺序和完成定义；
4. [安全规范](../specs/001-vdns-audit-rotation/security.md)、[协议注册表](../specs/001-vdns-audit-rotation/protocol-registry.md) 和 [数据模型](../specs/001-vdns-audit-rotation/data-model.md)：实现边界；
5. [OpenAPI](../specs/001-vdns-audit-rotation/contracts/openapi.json) 与 [API 评审](../specs/001-vdns-audit-rotation/contracts/api-review.md)：本地接口合同；
6. [研究方案](../specs/001-vdns-audit-rotation/research.md)：假设、实验和论文结论边界；
7. [ADR 索引](adr/README.md) 与 [G0.2 基线记录](../specs/001-vdns-audit-rotation/BASELINE.md)：设计决定和变更纪律。

仓库根目录的 `VDNS_可验证凭据操作审计与最小影响轮换系统白皮书_最终方案稿.docx` 是 v1 课题演进的历史输入，不再是当前规范性指导。遇到冲突时以 Spec v2、ADR-011 和协议注册表为准。

当前代码仍包含 v1.0.1 原型实现。它可以复用，但只有完成 `tasks.md` 中的 v2 迁移任务并通过相应验收后，才可标记为 `VDNS-PM/2` 合规。
