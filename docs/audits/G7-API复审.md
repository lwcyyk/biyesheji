# G7 API 设计复审

> 本文是历史 G7 准备记录，其中VDNS-PM为VPass的旧名称。当前项目仍为G6，G7未达成。

> **历史v2.0.0复审。** OpenAPI已在第一阶段更新为v2.1.0，现有实现与合同测试尚未迁移新EvidenceLevel和基线摘要，因此本文件不代表当前合同通过。

| 属性 | 结果 |
|---|---|
| 合同 | `VDNS-PM /api/v2` |
| 冻结版本 | `2.0.0` |
| 操作数 | 22 |
| 项目合同测试 | 通过 |
| 设计评分 | 86.35 / 100（B+） |
| 发布决定 | `PASS_WITH_DOCUMENTATION_DEBT` |

## 1. 复审结论

`./scripts/check-g7-api.sh` 对冻结 OpenAPI 做 `$ref` 感知解析，并验证路径参数、operationId、幂等键、分页、统一错误和 secret handle 边界。实现库存与合同匹配，冻结摘要未发生 breaking change。

第三方通用 linter 返回非零，其中 58 项“参数缺少 name”来自工具没有解引用 parameter `$ref`，已由项目测试逐个解析并判定为假阳性。工具发现的 22 个 operation 缺少长描述是真实文档债务，未被掩盖。

## 2. 一致性

- 所有资源路径使用 `/api/v2` 和复数名词；
- operationId 全局唯一；
- path 参数与模板一致；
- 写操作按冻结合同要求绑定 idempotency key；
- 分页使用受范围绑定的 opaque cursor；
- 错误响应统一解析到 `Error` schema；
- HTTP JSON 不接受主密码、网站密码、恢复秘密或字段明文。

## 3. 秘密句柄

密码生成、自动填充和安全分析的敏感输入通过 Native Messaging 在本地暂存，HTTP 只接收一次性 handle。合同测试验证：

- handle 绑定 session、Origin/operation 和上下文；
- 成功消费后不能重放；
- 过期、锁定和跨 Origin 使用失败；
- API 错误体不回显 handle 对应秘密；
- `PUBLISH_AUDIT` 不隐含 `AUDIT_ANALYZE`。

## 4. 幂等与冲突

创建、同步、生命周期写入和响应 attempt 均有稳定幂等身份。相同 key、相同请求返回既有结果；相同 key、不同请求摘要返回冲突。版本冲突不会由 HTTP 层静默执行 last-write-wins。

## 5. 分页

安全分析结果采用 HMAC 保护的 scope-bound cursor。cursor 至少绑定分析 ID、过滤器、页大小和位置；篡改、跨分析复用或改变过滤条件均拒绝。

## 6. 开放问题

1. 冻结合同中的 22 个 operation 只有 summary，没有长描述。为保持 G0.2 baseline，本阶段不直接改写冻结文件；下一协议修订应补充成功条件、幂等语义和失败恢复。
2. `SyncManifest` 类型层面允许 10k 引用，但 64 KiB 公共签名载荷要求实际分批。下一版本应明确 batch size、collection root 和完成条件。
3. 当前为本地 Agent 参考实现，没有生产反向代理、mTLS 或远程多租户速率限制，不应把本地 API 安全边界外推为互联网服务保证。

机器证据见：

- `test-results/g7/api/api-review-scorecard.json`
- `test-results/g7/api/project-contract-tests.json`
- `test-results/g7/api/third-party-linter.txt`
- `test-results/g7/api/third-party-scorecard.txt`
