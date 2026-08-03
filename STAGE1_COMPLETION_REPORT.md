# VDNS-PM 第一阶段完成报告

> 本文为历史阶段记录，其中VDNS-PM为VPass的旧名称。

| 属性 | 结论 |
|---|---|
| 完成日期 | 2026-07-31 |
| 文档版本 | 2.1.0 |
| 当前阶段 | G6研究原型集成 |
| 协议状态 | 第一阶段设计冻结 |
| G7状态 | 未达成 |
| Git身份 | 当前工作区没有Git元数据，未提供或伪造commit SHA |

## 1. 检查范围

已检查：

- `docs/VDNS研究生毕业设计开发报告.md`；
- `docs/论文/VDNS-PM研究生毕业论文.md`；
- Spec、plan、research、protocol registry、security、data model、tasks和历史baseline；
- ADR-001～011及ADR索引；
- `/api/v2` OpenAPI、API评审和合同测试；
- `internal/`下密码学、凭据、设备、站点、同步、VDNS resolver、透明日志、Monitor、审计、暴露和修复模块；
- `apps/browser-extension`、`apps/native-host`、`cmd/`；
- migrations 0001～0007及约束测试；
- `experiments/g7/`的数据集、schema、AC映射；
- `test-results/g3`～`g7`中的性能、故障、恢复、密码学、API和安全证据；
- 顶层测试、演示、实验、恢复和发布脚本。

仓库没有`services/`目录。文档中的服务名称是逻辑部署边界，当前代码采用Go模块化单体和研究适配器。

## 2. 当前真实完成度

仓库已有可运行研究原型，密码学、RouteMap、字段加密、密码生成、SQLite/outbox、生命周期、Mock Site、同步接受、L1～L5、Merkle、Monitor、隐私审计和本地修复基线均有代码与测试。当前工作树在文档变更前通过：

- `go test ./...`；
- `go vet ./...`；
- `go test -race ./internal/... ./tests/...`；
- 浏览器扩展10/10测试；
- 10万叶本地完整L1～L5测试，101次调用P95为2.302853 ms。

真实阶段判定为G6。G7没有达成，主要原因是Final Order Authority未实现、跨设备CAS终局不闭合、代码仍是旧证据枚举、同步没有真实网络、实验缺逐样本原始数据、SCOPE-ZK未实现。

详细完成度表见`docs/reviews/stage1-completion-audit.md`。

## 3. 开发报告与论文冲突

审计前开发报告是v2.0.0/G0.2开发指导，论文声称仓库G7冻结。两者已统一为v2.1.0/G6，并明确Stage 1设计冻结不等于实现完成。

已纠正的论文口径：

- 10k同步614.70 ms改为本地100×100 manifest构造/签名/验证，不含网络和对象传输；
- 16.79 μs改为百万叶Merkle包含证明验证，不代表完整L1～L5；
- 8/8改为本地适配器/协议故障回归，不称部署系统全栈；
- 7/7改为自动测试演练，不称真实灾备；
- H1～H6说明弱化项是`TEST_ONLY_DECISION_MODEL`；
- 漏洞0说明为2026-07-22历史扫描快照，当前状态`UNVERIFIED`；
- Mock Site不代表真实网站；
- 设备撤销不能回收旧密码；
- SCOPE-ZK明确为`NOT_IMPLEMENTED`。

## 4. 已修改的规范

核心规范已统一为v2.1.0，并冻结以下设计：

1. VDNS是可验证凭据状态解析控制平面，不是传统DNS；根授权中心治理，各设备和Monitor分布式验证；当前无多节点共识。
2. 本地CAS只提供本机事务原子性；跨设备`v2-A/v2-B`进入CONFLICTED，最终选择需要显式裁决和排序回执。
3. 网站证据固定为E0～E5；E0～E2禁止激活，E3条件激活，E4/E5按各自信任语义处理。
4. 设备撤销拆成控制面撤销、秘密代际隔离、外部凭据修复。
5. CanonicalOrigin固定scheme、IDNA/Punycode host、端口、子域、iframe、top-frame、HTTP/HTTPS和重定向规则。
6. Final Order Authority产生`FinalOrderReceipt`；检查点前为provisional；分叉失败关闭；新设备必须获得可信初始检查点。
7. 实验声明按MODEL到PRODUCTION分级，必须保存逐样本数据，不得用微基准冒充端到端。

新增ADR-012～017记录上述决策。OpenAPI已更新E0～E5目标枚举。

## 5. 缺少证据的论文声明

下列内容仍为`UNVERIFIED`：

- 仓库已经达到G7研究原型冻结；
- E1～E8均保存真实逐样本原始结果；
- 10k性能代表真实网络同步；
- G7 E5微秒值代表完整L1～L5；
- 8/8代表部署系统全栈故障注入；
- H1～H6弱化方案均有实际代码实现；
- Mock Site证明真实网站改密；
- 22项OpenAPI已与v2.1.0实现完全一致；
- 2026-07-31当前可达漏洞为0；
- 单机Monitor证据证明生产多观察者网络已经部署。

下列内容为`NOT_IMPLEMENTED`：

- Final Order Authority和生产/多节点最终性；
- SCOPE-ZK电路、prover、verifier及proof性能；
- 生产多节点VDNS共识；
- 真实网络sync service；
- 受信真实网站E4 connector。

## 6. 已在设计层解决的问题

- 明确了VDNS各角色、中心治理和分布式验证边界；
- 纠正了“本地CAS保证全球唯一”的错误表述；
- 建立E0～E5确认证据等级，页面提示不再称网站证明；
- 固定撤销三层边界和旧密码残余风险；
- 固定CanonicalOrigin及重定向后重新授权；
- 定义最终序生产者、provisional/final边界、分叉处理和初始检查点；
- 固定实验证据等级和声明规则；
- 将所有第二阶段工作改写为可验收的P0～P3任务。

这些属于协议设计冻结。相应代码未自动完成。

## 7. 第二阶段代码任务

P0协议正确性：

- Final Order Authority与FinalOrderReceipt；
- 跨设备冲突集合和显式终局；
- E0～E5全栈迁移；
- 撤销三层状态；
- CanonicalOrigin重定向闭环；
- 可信初始检查点与分叉处置；
- 线格式、迁移、OpenAPI和实现对齐。

P1安全实现：

- OS安全存储；
- 真实Native Messaging/浏览器边界；
- connector信任注册；
- 密钥生命周期与外部审计准备。

P2测试与恢复：

- 原始实验数据管线；
- 多进程网络同步试验台；
- 故障/恢复证据升级；
- 当前安全扫描；
- 论文声明自动核对。

P3工程优化：

- 分离完整L1～L5和Merkle基准；
- 10k同步分片/背压；
- 真实浏览器/设备矩阵；
- 可选SCOPE-ZK研究。

每项问题、模块、验收条件、测试和论文章节见`specs/001-vdns-audit-rotation/tasks.md`。

## 8. 仍未解决的P0

1. 没有代码实现Final Order Authority，`finalSequence`仍可由调用方/夹具提供。
2. 两个独立设备数据库的本地CAS可同时成功，冲突终局未实现。
3. Go、SQLite、扩展和handler仍使用v2.0.0旧EvidenceLevel。
4. 新设备可信初始检查点未形成实现闭环。
5. 撤销事件与设备操作的排序竞争缺少真实排序回执。
6. v2.1.0 OpenAPI已经改变，旧合同测试仍硬编码2.0.0和旧baseline摘要。
7. 旧规范追踪脚本仍硬编码97个`T-Gx-xxx`任务，不能识别新的P0～P3清单。

最后一项已经由当前合同测试真实暴露：

```text
TestFrozenOpenAPIOperationsMatchImplementation:
  OpenAPI version="2.1.0"
TestG7OpenAPIReferencesResolveAndOperationsAreUnique:
  OpenAPI changed without an explicit baseline amendment
```

本阶段没有修改业务代码或测试来制造绿色结果，也没有伪造新baseline hash。该差异由第二阶段P0-007解决。

`./scripts/check-spec-trace.sh`也真实报告旧任务格式/历史baseline不匹配。新任务清单已经包含FR-001～043、AC-001～021和全部NFR追踪，第二阶段需要更新检查器结构后再创建真实v2.1.0不可变基线。

## 9. 变更文件

新增：

- `STAGE1_COMPLETION_REPORT.md`
- `docs/reviews/stage1-completion-audit.md`
- `docs/reviews/stage1-version-alignment.md`
- `docs/reviews/stage1-implementation-status.md`
- `docs/adr/ADR-012-vdns-deployment-trust-model.md`
- `docs/adr/ADR-013-cross-device-conflict-final-order.md`
- `docs/adr/ADR-014-site-confirmation-evidence-levels.md`
- `docs/adr/ADR-015-device-revocation-boundary.md`
- `docs/adr/ADR-016-canonical-origin.md`
- `docs/adr/ADR-017-experiment-claims-evidence.md`

更新：

- `README.md`
- `docs/VDNS研究生毕业设计开发报告.md`
- `docs/论文/VDNS-PM研究生毕业论文.md`
- `docs/adr/README.md`
- `docs/adr/ADR-004-final-ordering.md`
- `docs/adr/ADR-007-anvil-research-adapter.md`
- `docs/G3阶段实施记录.md`
- `docs/G7阶段实施记录.md`
- `docs/提交前检查表.md`
- `docs/audits/G7-API复审.md`
- `docs/audits/G7密码学与协议审计.md`
- `docs/security/G7供应链审计.md`
- `docs/security/G7威胁模型与安全审计.md`
- `specs/001-vdns-audit-rotation/spec.md`
- `specs/001-vdns-audit-rotation/plan.md`
- `specs/001-vdns-audit-rotation/research.md`
- `specs/001-vdns-audit-rotation/protocol-registry.md`
- `specs/001-vdns-audit-rotation/security.md`
- `specs/001-vdns-audit-rotation/data-model.md`
- `specs/001-vdns-audit-rotation/tasks.md`
- `specs/001-vdns-audit-rotation/BASELINE.md`
- `specs/001-vdns-audit-rotation/contracts/openapi.json`
- `specs/001-vdns-audit-rotation/contracts/api-review.md`

未修改`internal/`、`apps/`、`migrations/`和历史`test-results/`中的业务实现或证据数据。
