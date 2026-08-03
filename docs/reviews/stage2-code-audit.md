# Stage 2代码审计

> 本审计的当前展示名为 VPass；Stage 2 证据中的 VDNS-PM 是旧名。数量结论保留 2026-07-31 原始口径，命名迁移后的当前 API 口径单独注明。

审计日期：2026-07-31  
基线：Spec 001 v2.1.0 / G6研究原型集成  
结论：核心研究协议已形成可运行闭环，G7未达成。

## 1. P0/P1完成度

| 任务 | 主要代码 | 主要验证 | 状态 | 边界 |
|---|---|---|---|---|
| OpenAPI 2.1.0与baseline | contract tests、动态trace、v2.1 baseline | 合同、baseline、6项Python回归 | COMPLETE | baseline不等于发布或G7 |
| 研究型Final Order Authority | `internal/finalorder`、SQLite snapshot store | 2/3设备、幂等、乱序、回执、重启 | COMPLETE | `RESEARCH_ADAPTER`，无BFT/多节点共识 |
| 跨设备冲突 | candidate branch、conflict set、explicit resolution | 隐藏分支、失败分支回归、裁决新版本 | COMPLETE | 研究Authority内闭环，多进程试验待第三阶段 |
| E0～E5 | protocol/site/local API/SQLite v2.1 | 六级矩阵、Mock E4、严格E3、UNKNOWN/REVIEW | COMPLETE | 真实E4 Connector为NOT_IMPLEMENTED |
| 网站改密故障恢复 | site coordinator、SQLite attempt repository | 丢响应、失败/MFA/策略、每个主要状态close/reopen | COMPLETE | Mock Site不是公网网站 |
| 撤销三层语义 | `internal/device/domain/revocation.go`、SQLite v8表 | 最终序、代际隔离、旧密码残余风险、四态修复 | PARTIAL | 完整API/UI/实际站点修复编排未接入 |
| CanonicalOrigin | Go/扩展统一模块、共享JSON向量 | IDN、端口、IPv4/v6、iframe、重定向、降级 | COMPLETE | 真实浏览器自动化待后续 |
| 五层可信状态验证 | resolver、FinalOrderReceipt L3校验 | 各层负向矩阵、失败投影清空、100k完整流程 | COMPLETE | API需注入实际Verifier；未配置时501 |
| HTTP同步 | `internal/adapters/researchsync` | localhost、10k批次、分页、重试、故障矩阵 | COMPLETE | `RESEARCH_HTTP_SYNC_ADAPTER`，非生产同步存储 |
| `/api/v2`覆盖 | handler/本地安全客户端/coverage generator | Stage 2原始22项；当前23项，新增legacy路径操作 | COMPLETE（核对） | 当前13 COMPLETE、8 PARTIAL、2 NOT_IMPLEMENTED |

## 2. 关键实现结论

### Final Order与冲突

`ResearchSingleNodeFinalOrderAuthority`提供`SubmitCandidate`、`AssignFinalSequence`、`GetFinalizedState`、`GetConflictSet`、`ResolveConflict`和`GetTrustedCheckpoint`。候选摘要、base descriptor、幂等键、回执、冲突集合和用户裁决均可持久化。共同前序上的多个候选使状态进入`CONFLICTED`，到达顺序和同步存储视图不能自动选支。用户裁决产生新版本与新最终序，旧分支保留。

ADR-018冻结确定性CBOR回执。L3可要求校验Authority公钥、key ID/generation、Namespace、CredentialID、ordered digest和序号。研究Authority恢复检查点只证明单节点视图可恢复，不能代替L4透明日志检查点。

### E0～E5与耐久状态

E0/E1进入`UNKNOWN`，E2进入`REVIEW_REQUIRED`，E3只有显式严格策略可激活，E4在没有真实信任Connector时不可激活，E5按用户确认策略激活且不称为网站证明。SQLite v8用`evidence_schema=2`隔离新枚举，legacy值没有v2.1投影时拒绝读取。`MOCK_SITE_E4`为安全默认值。

候选在网站调用前由存储端证明字段和descriptor对象已耐久。主成功、重试、未知、review和abort路径在每个主要转换后关闭并重开SQLite验证恢复。超时或响应丢失不会删除唯一候选。

### 五层可信状态验证

解析器保留独立层错误码：

- L1：根链、Namespace、设备/事件/descriptor签名、key generation；
- L2：operation、scope、有效序、issuance counter和状态引用；
- L3：撤销、代际、设备counter、前序、版本、生命周期、冲突与最终序回执；
- L4：ProofBundle、树头、包含、一致性和checkpoint/anchor；
- L5：操作风险、离线缓存年龄、pending anchor和用户review。

任何失败只返回层错误与最终Verdict，身份、授权、状态、版本和审计投影全部清空。高风险写不走离线降级。本地客户端接口不再合成五层成功结果。

## 3. 测试结果

| 检查 | 结果 |
|---|---|
| `go test ./... -count=1` | PASS |
| `go vet ./...` | PASS |
| `go test -race ./... -count=1` | PASS，0 race report |
| 浏览器扩展Node测试 | 13/13 PASS |
| Python trace/API覆盖回归 | 6/6 PASS |
| 6个关键fuzz目标 | PASS |
| govulncheck | 0可达、0已导入包漏洞；1个未调用模块级finding |

原始范围与限制见`test-results/stage2/`。这些结果属于`UNIT_TEST`或`LOCAL_INTEGRATION`，不升级为最终E1～E8实验。

## 4. 仍未闭环

- 生产多节点/BFT Final Order Authority：NOT_IMPLEMENTED；
- 真实公网/生产同步存储：NOT_IMPLEMENTED；
- 真实E4 Connector与信任注册：NOT_IMPLEMENTED；
- SCOPE-ZK：NOT_IMPLEMENTED；
- 平台OS安全存储与真实浏览器自动化：PARTIAL/NOT_IMPLEMENTED；
- 新设备可信初始检查点完整产品流程：PARTIAL；
- 撤销三层在API/UI/真实站点修复中的端到端组合：PARTIAL；
- 最终E1～E8冻结数据与G7声明：UNVERIFIED。
