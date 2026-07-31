# ADR-017：实验声明与证据要求

- 状态：Accepted
- 日期：2026-07-31
- 追踪：NFR-MNT-003～004、NFR-PERF-001～008；AC-019～021

## 背景

历史G7材料混合了微基准、定向测试、决策模型、Mock Site和本地适配器。汇总统计没有保存全部逐次原始样本，导致部分结论无法独立复算。

## 决策

每项实验声明必须标注证据等级：

```text
MODEL
UNIT_TEST
LOCAL_INTEGRATION
MULTI_PROCESS_LOCAL
NETWORKED_TESTBED
PUBLIC_TESTNET
PRODUCTION
```

强等级不得由弱等级替代。具体规则：

- Merkle包含证明耗时不得写成完整L1～L5耗时；
- 本地manifest构造/签名/验证不得写成网络同步；
- Mock Site不得写成真实网站；
- Anvil/模拟锚定不得写成生产区块链共识；
- 定向Go测试故障矩阵不得写成部署系统全栈故障；
- 恢复单元/集成测试不得写成真实灾备切换；
- `TEST_ONLY_DECISION_MODEL`不得写成弱化生产实现；
- 未配置provider的时间、大小、内存必须为`null/UNAVAILABLE`。

性能实验至少保存：

- 环境、工具链、工作树标识、数据集版本和摘要；
- 预热、重复次数、固定非安全seed和命令；
- 每次测量的原始值，不只保存P50/P95/P99；
- 错误、超时、失败样本和退出码；
- 指标计算脚本版本和单位；
- 明确包含/不包含的步骤。

“当前漏洞为0”只对记录的扫描器、数据库时间、依赖快照和工作树成立。后续修改后必须重跑，历史扫描只能称快照。

## 后果

- 历史`test-results/g7`保留，不改写；不满足新规则的声明标为`UNVERIFIED`。
- 第二阶段建立新证据schema和claim-evidence map。
- G7门禁必须先验证声明口径，再验证命令退出码。

