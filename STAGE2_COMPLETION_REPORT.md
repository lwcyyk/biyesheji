# VPass第二阶段完成报告

> 命名迁移说明：本报告记录 2026-07-31 的 Stage 2 事实，当时使用的 VDNS-PM 为 VPass 旧名。文中当前代码路径和展示名已对齐 VPass；Stage 2 当时的测试数量和结果保留历史口径。

日期：2026-07-31  
文档版本：2.1.0  
当前阶段：G6研究原型集成  
协议状态：Stage 1设计冻结 + ADR-018补正  
G7：未达成

## 1. 修改的代码模块

本阶段完成以下研究原型模块：

1. `internal/finalorder`：单节点最终序接口、候选、冲突集合、显式裁决、Ed25519回执、确定性CBOR和研究检查点；
2. SQLite v8：Authority恢复快照、候选/回执/裁决/检查点、E0～E5证据和撤销三层投影；
3. credential/site：统一CanonicalOrigin、重定向重新授权、多Origin显式策略、E0～E5状态与耐久恢复；
4. device：`KnownCredentialSet`、`FutureAccessBlockedSet`、`RemediationRequiredSet`和四态修复；
5. resolver：L3最终序回执/冲突校验、完整失败投影清空、独立层错误；
6. `internal/adapters/researchsync`：真实localhost HTTP对象/manifest同步、分批、分页、幂等、重试和故障视图；
7. 本地客户端接口：OpenAPI 2.1.0对齐、E0～E5、稳定501边界、移除合成L1～L5成功；
8. 追踪与覆盖：动态任务统计、baseline重建和22项API机器覆盖生成器。

## 2. P0/P1完成情况

| 任务 | 状态 | 结果 |
|---|---|---|
| P0-1版本/合同/baseline/任务统计 | COMPLETE | 2.1.0合同通过；旧v2.0.0摘要保留；当前36项摘要真实重算；任务动态统计23项 |
| P0-2研究Final Order Authority | COMPLETE（研究范围） | 单调序、前序、冲突、幂等、签名、SQLite恢复和`RESEARCH_ADAPTER`标签 |
| P0-3跨设备冲突 | COMPLETE（研究范围） | 2/3设备多分支进入CONFLICTED；隐藏分支不改变可信状态；用户裁决产生新版本 |
| P0-4 E0～E5 | COMPLETE（允许边界） | 领域/API/SQLite已迁移；真实E4 Connector仍NOT_IMPLEMENTED |
| P0-5设备撤销三层 | PARTIAL | 领域集合和状态规则完成；完整API/UI/真实站点编排未完成 |
| P0-6 CanonicalOrigin | COMPLETE | Go/扩展共享向量、iframe、重定向、HTTP降级和多Origin策略通过 |
| P1-1 L1～L5 | COMPLETE（核心） | 每层正负测试、回执、冲突、失败投影清空；API组合为PARTIAL |
| P1-2 HTTP同步 | COMPLETE（研究适配器） | 真实localhost HTTP与10k批次；生产云NOT_IMPLEMENTED |
| P1-3 OpenAPI覆盖 | COMPLETE（核对） | Stage 2当时为13 COMPLETE、7 PARTIAL、2 NOT_IMPLEMENTED；VPass迁移新增1个legacy路径操作，当前合同共23项 |

## 3. 新增和强化的测试

- Final Order：2/3设备、同base多分支、同版本异descriptor、隐藏分支、重复/乱序、显式裁决、失败分支返回、CAS崩溃边界、SQLite重启、回执/checkpoint篡改；
- 网站确认：E0～E5矩阵、Mock E4、严格E3、页面/响应不确定、明确失败、MFA、策略拒绝、SQLite每个主要状态close/reopen；
- 撤销：最终序前后操作、拒绝新代际、旧密文/已知密码残余风险、部分失败和Pending/Unknown不安全；
- Origin：HTTP/HTTPS、大小写、默认/非默认端口、IPv4/v6、IDN、尾随点、子域、localhost、iframe、重定向、extension/非法/超长输入；
- L1～L5：身份、能力、动态状态、ProofBundle/树/anchor、离线缓存和高风险策略；完整流程与Merkle语义分离；
- HTTP同步：10k分批、对象hash、manifest cursor、网络中断、延迟、重试、重复、部分响应、旧manifest、隐藏分支、大小限制；
- API：Stage 2原始22项operation覆盖、secret schema、幂等、CAS、cursor、PARTIAL/501边界；当前23项合同另增legacy路径兼容测试；
- fuzz：Origin、CBOR、ProofBundle、manifest、状态转换和strict JSON。

## 4. 验证结果

| 命令/检查 | 结果 |
|---|---|
| `GOPATH=/home/lwc/go go test ./... -count=1` | PASS |
| `GOPATH=/home/lwc/go go vet ./...` | PASS |
| `GOPATH=/home/lwc/go go test -race ./... -count=1` | PASS，0 race report |
| `npm test`（browser extension） | 13/13 PASS |
| Python回归 | 6/6 PASS |
| trace | 43 FR、30 NFR、21 AC、23 tasks，PASS |
| baseline | `spec-001-v2.1.0-stage2-g6`，36 artifacts，PASS |
| 6个fuzz目标 | PASS |
| govulncheck v1.6.0 | 0可达、0已导入包；1个未调用模块finding |

没有删除失败测试。实现过程中新增的逐状态SQLite恢复测试发现并修复了v2.1证据决策名与数据库约束不一致问题。

## 5. 已闭环协议问题

- 本地CAS与全局冲突语义分离；
- 单节点研究Authority成为`finalSequence`生产者并签发回执；
- 冲突不按同步存储返回、到达顺序或墙钟自动选支；
- E0～E5进入协议、领域、数据库和API；
- Mock E4不能冒充真实站点；
- 候选在网站调用前耐久，UNKNOWN不删除候选；
- 撤销三层和旧密码不可收回边界进入领域模型；
- CanonicalOrigin在扩展/本地安全客户端/RouteMap/OriginBinding使用同一规则；
- L1～L5失败不暴露部分成功投影；
- 网络同步经过真实HTTP且继续视同步存储层为不可信；
- Stage 2原始22项API完成状态有机器可读结论；命名迁移后当前合同为23项。

## 6. 仍为NOT_IMPLEMENTED

- 生产多节点/BFT Final Order Authority；
- 真实公网或生产云；
- 真实网站E4 Connector；
- SCOPE-ZK；
- 平台OS key store/硬件边界；
- 生产浏览器自动化与移动端；
- 最终E1～E8实验；
- G7冻结。

## 7. 仍为UNVERIFIED或PARTIAL

- 撤销三层完整API/UI/外部网站修复：PARTIAL；
- 新设备可信初始检查点完整产品流程：PARTIAL；
- local API的sync/device/audit为排队或研究组合边界：PARTIAL；
- 多进程双Agent/双SQLite网络冲突试验：UNVERIFIED；
- 外部密码学和安全审计：UNVERIFIED；
- 最终论文性能数值与E1～E8：UNVERIFIED；
- G7历史8/8故障、7/7恢复和最终性能声明不能由本阶段测试替代。

## 8. 是否可以进入第三阶段

可以进入第三阶段的“实验与证据冻结准备”，理由是核心研究协议可运行、合同/测试/race通过、研究适配器边界明确。项目不能进入G7或生产发布。第三阶段必须先完成多进程组合、原始实验数据管线、声明—证据绑定和固定环境重测。

## 9. 变更文件

### 协议、文档与基线

- `docs/VPass研究生毕业设计开发报告.md`
- `docs/adr/README.md`
- `docs/adr/ADR-018-stage2-research-final-order-wire.md`
- `specs/001-vdns-audit-rotation/spec.md`
- `specs/001-vdns-audit-rotation/tasks.md`
- `specs/001-vdns-audit-rotation/protocol-registry.md`
- `specs/001-vdns-audit-rotation/security.md`
- `specs/001-vdns-audit-rotation/data-model.md`
- `specs/001-vdns-audit-rotation/contracts/openapi.json`
- `specs/001-vdns-audit-rotation/contracts/api-review.md`
- `specs/001-vdns-audit-rotation/canonical-origin-vectors.json`
- `specs/001-vdns-audit-rotation/BASELINE.md`
- `specs/001-vdns-audit-rotation/BASELINE.json`
- `specs/001-vdns-audit-rotation/BASELINE-v2.0.0.json`
- `migrations/README.md`

### Final Order、Resolver与撤销

- `internal/finalorder/domain/model.go`
- `internal/finalorder/ports/store.go`
- `internal/finalorder/application/authority.go`
- `internal/finalorder/application/authority_test.go`
- `internal/adapters/outbound/sqlite/final_order_store.go`
- `internal/resolver/domain/model.go`
- `internal/resolver/application/layers.go`
- `internal/resolver/application/resolver.go`
- `internal/resolver/application/layers_test.go`
- `internal/device/domain/revocation.go`
- `internal/device/domain/revocation_test.go`

### 网站确认、Origin与协议枚举

- `internal/protocol/registry.go`
- `internal/protocol/registry_test.go`
- `internal/site/domain/connector.go`
- `internal/site/application/change.go`
- `internal/site/application/change_test.go`
- `internal/adapters/outbound/mocksite/connector.go`
- `internal/adapters/outbound/sqlite/site_change_repository.go`
- `internal/adapters/outbound/sqlite/site_change_repository_test.go`
- `internal/credential/domain/aggregate_test.go`
- `internal/credential/domain/version_test.go`
- `internal/credential/domain/origin.go`
- `internal/credential/domain/origin_test.go`
- `internal/credential/domain/autofill_origin.go`
- `internal/credential/domain/autofill_origin_test.go`
- `apps/browser-extension/lib/origin.js`
- `apps/browser-extension/tests/origin.test.mjs`
- `apps/browser-extension/popup/popup.js`
- `tests/e2e/daily_mocksite_test.go`

### SQLite、HTTP同步与本地API

- `migrations/0008_stage2_protocol_closure.sql`
- `migrations/tests/0008_constraints.sql`
- `migrations/embed.go`
- `internal/adapters/outbound/sqlite/database.go`
- `internal/adapters/outbound/sqlite/database_test.go`
- `internal/adapters/researchsync/http_adapter.go`
- `internal/adapters/researchsync/http_adapter_test.go`
- `internal/localapi/application/local_secure_client.go`
- `internal/localapi/application/local_secure_client_test.go`
- `internal/adapters/inbound/httpapi/handler.go`
- `internal/adapters/inbound/httpapi/handler_test.go`
- `tests/contract/openapi_local_api_test.go`

### 追踪、审计与证据

- `scripts/check_spec_trace.py`
- `scripts/tests/test_check_spec_trace.py`
- `scripts/generate_api_coverage.py`
- `scripts/tests/test_generate_api_coverage.py`
- `docs/reviews/stage2-code-audit.md`
- `docs/reviews/stage2-api-coverage.md`
- `docs/reviews/stage2-security-status.md`
- `docs/reviews/stage2-remaining-gaps.md`
- `test-results/stage2/test-summary.json`
- `test-results/stage2/api-coverage.json`
- `test-results/stage2/race-summary.json`
- `test-results/stage2/fuzz-summary.json`
- `test-results/stage2/security-scan.json`
- `test-results/stage2/integration-summary.json`
- `STAGE2_COMPLETION_REPORT.md`
