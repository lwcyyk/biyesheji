# VPass 文档入口

当前项目指导基线为 **VPass Spec 2.1.0 / G6 研究原型集成**，Stage 1 协议设计已冻结，G7 未达成。

建议阅读顺序：

1. [README](../README.md)：当前定位、完成状态、快速演示和已知边界；
2. [Stage 2完成报告](../STAGE2_COMPLETION_REPORT.md)与[Stage 2代码审计](reviews/stage2-code-audit.md)：当前代码基线；
3. [研究生毕业设计开发报告](VPass研究生毕业设计开发报告.md)：总体设计、实现与论文结构；
4. [Spec 001](../specs/001-vdns-audit-rotation/spec.md)：规范性 FR/NFR/AC；
5. [安全规范](../specs/001-vdns-audit-rotation/security.md)、[协议注册表](../specs/001-vdns-audit-rotation/protocol-registry.md)和[数据模型](../specs/001-vdns-audit-rotation/data-model.md)：安全、wire 与持久化边界；
6. [OpenAPI](../specs/001-vdns-audit-rotation/contracts/openapi.json)与[API覆盖审计](reviews/stage2-api-coverage.md)：本地客户端接口合同；
7. [ADR索引](adr/README.md)：决策和变更纪律；
8. [VPass命名迁移](migrations/vpass-naming-migration.md)：新旧名称、旧数据和 legacy wire 兼容策略；
9. [研究生毕业论文](论文/VPass研究生毕业论文.md)与[答辩六问回答](答辩/VPass项目介绍六问回答.md)：学术与答辩材料。

仓库根目录的 `VDNS_可验证凭据操作审计与最小影响轮换系统白皮书_最终方案稿.docx` 是 v1 课题演进的历史输入，不再是当前规范性指导。`test-results/`、历史 Stage 报告、旧 baseline 和旧 ADR 中的 VDNS-PM 是 VPass 旧名，为保留历史证据不改写。
