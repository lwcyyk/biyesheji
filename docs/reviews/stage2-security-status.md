# Stage 2安全状态

日期：2026-07-31  
结论：本阶段安全门禁通过，结论限定于当前工作区快照和本次工具范围。

## 1. 已验证安全属性

| 属性 | 证据 | 结果 |
|---|---|---|
| 最终序回执不可篡改 | Ed25519回执/检查点及L3负向测试 | PASS |
| 冲突不静默选支 | 2/3设备、乱序、隐藏分支、裁决测试 | PASS |
| E0～E2不激活 | protocol/site/local API矩阵 | PASS |
| Mock E4不冒充真实站点 | Connector trust kind与review测试 | PASS |
| UNKNOWN/候选可恢复 | SQLite逐状态close/reopen | PASS |
| 撤销不声称收回旧密码 | 三层模型与残余风险测试 | PASS |
| Origin精确绑定 | 共享向量、iframe、重定向、降级攻击 | PASS |
| L1～L5失败关闭 | 分层错误、投影清空、高风险策略 | PASS |
| 不可信HTTP同步 | hash、旧manifest、缺失/替换/隐藏分支 | PASS |
| JSON秘密边界 | OpenAPI扫描、strict decoder、扩展合同 | PASS |
| 数据竞争 | 全仓`go test -race` | 0 report |

## 2. 漏洞扫描

命令：

```text
GOPATH=/home/lwc/go go run golang.org/x/vuln/cmd/govulncheck@v1.6.0 -show verbose ./...
```

结果：

- 59个根包、15个模块和Go 1.25.12标准库被扫描；
- 可达漏洞：0；
- 已导入包漏洞：0；
- required module finding：1；
- finding为`GO-2026-5932`，位于`golang.org/x/crypto/openpgp`，当前代码没有导入或调用，且无修复版本。

允许的准确声明是：

> 本次govulncheck快照发现0个可达漏洞和0个已导入包漏洞，并发现1个未调用的模块级finding。

不得简化为“所有依赖漏洞为0”。

## 3. Fuzz

短时定向fuzz覆盖CanonicalOrigin、确定性CBOR、ProofBundle、manifest、状态转换和HTTP严格JSON。6个目标均PASS，执行数保存在`test-results/stage2/fuzz-summary.json`。短时fuzz不替代长期持续fuzz、渗透测试或第三方密码学审计。

## 4. 研究适配器边界

- `ResearchSingleNodeFinalOrderAuthority`没有多节点共识和BFT；
- `RESEARCH_HTTP_SYNC_ADAPTER`没有生产认证、租户隔离、公网TLS运维和高可用；
- Mock Site没有真实网站证明能力；
- Anvil/模拟checkpoint没有生产链最终性；
- local agent仅在注入真实Verifier后返回L1～L5结果；
- 撤销设备已知旧密码仍可能在外部网站有效。

## 5. 未完成安全工作

平台OS key store、真实浏览器/Native Messaging攻击测试、真实E4 trust registry、生产共识、独立安全复核和长期fuzz仍为`NOT_IMPLEMENTED`或`UNVERIFIED`。上述能力不阻止进入第三阶段实验准备，但阻止G7和生产声明。
