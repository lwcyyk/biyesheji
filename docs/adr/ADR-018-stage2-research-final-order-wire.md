# ADR-018：第二阶段研究型最终序回执线格式

- 状态：Accepted
- 日期：2026-07-31
- 追踪：P0-001、P0-002、P0-007；FR-020、FR-030～034；AC-004、AC-006～010
- 补充：ADR-004、ADR-012、ADR-013

## 背景

Stage 1要求第二阶段实现可持久化、可验证的单节点 Final Order Authority。原`protocol-registry.md`中的示意CDDL没有包含CredentialID和研究适配器标签，也没有明确签名载荷与派生摘要的边界。若直接按示意结构实现，回执无法在同一Namespace内精确绑定凭据，也容易被误写为生产共识证明。

## 决策

第二阶段新增`ResearchSingleNodeFinalOrderAuthority`，部署标签固定为：

```text
RESEARCH_ADAPTER
NO_MULTI_NODE_CONSENSUS
NO_BYZANTINE_FAULT_TOLERANCE
```

`FinalOrderReceipt`使用确定性CBOR。签名载荷必须绑定：

- CP-2域、协议ID和协议版本；
- Suite ID与`RESEARCH_ADAPTER`；
- NamespaceID和CredentialID；
- 被排序候选对象摘要；
- 单调`finalSequence`；
- 前一已排序对象摘要；
- Authority key ID和key generation。

线对象只携带签名载荷和Ed25519签名。`receiptDigest`由域分离前缀、确定性签名载荷和签名派生，不在签名载荷中自引用。解析只负责确定性CBOR和字段约束，信任判断必须另行调用签名验证并使用接收设备已信任的Authority公钥。

Authority检测同一base descriptor上的不同候选后必须保留全部分支并把状态设为`CONFLICTED`。Authority不按到达时间选择密码。用户裁决产生引用完整候选集合的新版本与新回执，历史分支不删除。

单节点Authority签发的回执提供研究原型内的确定性排序。回执进入透明日志及本地策略要求的可信检查点前仍是provisional。Authority自身签发的研究检查点只能证明该单节点视图可恢复，不能证明多节点共识、拜占庭容错或生产链最终性。

## 后果

- Resolver L3验证回执签名、Authority key、Namespace、CredentialID、对象摘要和最终序；L4/L5仍不可省略。
- SQLite v8保存候选、回执、冲突裁决、研究检查点和带CAS revision的恢复快照。
- 生产Final Order Authority未来必须使用独立部署标签、信任根和协议升级，不能把本适配器原样改名。
- Stage 1示意CDDL由本ADR补正，规范、代码、迁移和测试以本ADR后的完整结构为准。
