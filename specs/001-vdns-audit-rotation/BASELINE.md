# Spec 001 v2.1.0 VPass命名迁移基线

| 属性 | 值 |
|---|---|
| 基线标识 | `spec-001-v2.1.0-vpass-naming-g6` |
| 日期 | 2026-08-03 |
| 文档版本 | 2.1.0 |
| 实现阶段 | G6研究原型集成 |
| 协议状态 | Stage 1设计冻结 + ADR-018线格式补正 + ADR-019命名兼容 |
| G7 | 未达成 |
| 校验 | `scripts/check_spec_trace.py`、`scripts/check_spec_baseline.py`和合同测试 |

`BASELINE.json`中的摘要由当前文件真实字节重新计算。它冻结VPass命名迁移后的Spec 2.1.0、当前接口合同和legacy兼容边界，不能证明代码为生产系统，也不能证明G7实验完成。`tasks.md`仅归一化任务复选框状态，任务文本和验收语义仍参与摘要。

## 迁移历史

| 文件 | 基线 | 状态 |
|---|---|---|
| `BASELINE-v1.0.0.json` | `spec-001-v1.0.0-g0` | 历史 |
| `BASELINE-v1.0.1.json` | `spec-001-v1.0.1-g0.1` | 历史 |
| `BASELINE-v2.0.0.json` | `spec-001-v2.0.0-g0.2` | 历史；保留旧摘要和`historicalStatus`迁移标记 |
| `BASELINE-v2.1.0-stage2-g6.json` | `spec-001-v2.1.0-stage2-g6` | 历史；完整保留Stage 2结束摘要 |
| `BASELINE.json` | `spec-001-v2.1.0-vpass-naming-g6` | 当前 |

v2.0.0和Stage 2摘要不再与当前OpenAPI和规范匹配，这是显式命名与合同迁移结果。旧文件不删除、不覆写为新值，也不用于声称当前代码完成。

## 当前冻结内容

1. VPass是当前唯一产品展示名；可验证状态控制层定义为私有凭据状态的可验证控制平面，不是传统DNS。
2. `ResearchSingleNodeFinalOrderAuthority`及回执按ADR-018冻结为研究适配器，没有生产共识或拜占庭容错。
3. 本地CAS不提供全局唯一版本；同base多候选进入`CONFLICTED`并由用户显式裁决。
4. E0～E5已进入代码、SQLite v8和OpenAPI；Mock E4不能激活，真实E4 Connector未实现。
5. 设备撤销分为控制面、秘密代际隔离和外部凭据修复；旧密码不可收回。
6. CanonicalOrigin采用精确scheme/host/port规则，重定向重新授权，iframe默认拒绝，多Origin必须显式配置。
7. 完整L1～L5与Merkle微基准分开命名；Stage 2定向测试不是最终G7实验数据。
8. localhost同步部署标签为`RESEARCH_HTTP_SYNC_ADAPTER`，不外推为公网或生产同步存储。
9. SCOPE-ZK、真实E4、生产共识、生产同步存储和最终E1～E8仍保持`NOT_IMPLEMENTED`或`UNVERIFIED`。
10. `VDNS-PM/2`、`VDNS-PM-CP-2`、旧API路径/头字段和旧Native Messaging主机名仅作为legacy兼容读取；新展示标签为`VPass/2`。

## 变更流程

安全语义、线格式、枚举、ID宽度、KDF/AAD、状态边、公开字段或完成声明变化必须新增ADR或显式基线修订。每次修订需重新计算真实摘要，运行合同、trace、Go测试、race/fuzz及可用的安全扫描，并保存原始命令状态。缺少工具或报告时继续标记`UNVERIFIED`。
