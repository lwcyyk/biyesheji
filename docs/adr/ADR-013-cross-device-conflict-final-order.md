# ADR-013：跨设备冲突与最终顺序

- 状态：Accepted
- 日期：2026-07-31
- 追踪：FR-020～026、FR-030～034；AC-004、AC-006～010
- 补充：ADR-004

## 背景

SQLite CAS只能保证一个本地数据库事务不会在同一expectedVersion上静默覆盖。设备A和设备B离线或并发时可以分别成功创建`v2-A`和`v2-B`。既有“CAS保证同版本只有一个Descriptor”的表述把本地原子性误写成全局唯一性。

## 决策

系统区分三种顺序：

1. `localCounter`：单设备单调计数，只约束该设备；
2. `provisionalSequence`：发布者或日志接收时的位置，不提供跨视图最终性；
3. `finalSequence`：Final Order Authority签发并进入受信检查点的安全顺序。

本地CAS保证：

```text
同一SQLite状态、同一expectedVersion、同一事务边界内，
最多一个accepted pointer更新成功。
```

本地CAS不保证全局只存在一个v2候选。

发现以下任一情况必须进入`CONFLICTED`：

- 同一CredentialID和base descriptor出现两个不同候选；
- 同一版本出现不同DescriptorHash；
- 两个候选都具有有效设备签名和能力，尚无可信最终选择；
- 不同日志视图为同一版本返回不同状态。

候选均保留，不按到达时间、墙钟、设备ID或云端顺序静默选择。Final Order Authority为候选分配序号并签署`FinalOrderReceipt`。检查点前的排序是provisional；进入本地信任策略要求的检查点后才可作为final。若Final Order Authority自身返回相同位置的不同摘要，Monitor产生分叉证据，本地高风险写失败关闭。

冲突裁决者是名称空间策略授权的`CONFLICT_RESOLVE`主体，通常为用户在已授权设备上的显式选择。裁决事件必须引用全部候选摘要、选中摘要、理由码、能力凭证和前一可信检查点。Final Order Authority只排序，不替用户决定哪个密码在真实网站有效。

撤销竞争按`finalSequence`比较：

```text
operation.finalSequence < revocation.finalSequence  → 可继续验证
operation.finalSequence >= revocation.finalSequence → REJECT_REVOKED
```

相同序号禁止复用。没有最终序时，撤销、加入、轮换、冲突裁决等高风险写保持PENDING或REJECT；只读仅可按L5缓存策略降级。

新设备的可信初始检查点必须来自以下之一：已有设备通过已认证通道转移、恢复胶囊绑定的检查点承诺、用户核对的带外摘要。普通云端返回值和无提示TOFU不能授权高风险写。

## 后果

- `finalSequence`不能再由普通事件调用方任意填写。
- 数据模型需要保存排序回执、branch/base摘要和冲突集合。
- 第二阶段必须增加双进程/双数据库并发测试和分叉排序测试。

