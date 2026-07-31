# VDNS-PM 研究设计与实验方案

| 属性 | 值 |
|---|---|
| 版本 | `2.1.0` |
| 当前阶段 | G6研究原型集成；G7冻结未达成 |
| 论文题目 | 基于VDNS的可验证密码生命周期管理与隐私审计方法研究 |
| 核心对象 | 完整密码管理器的生命周期与不可信云同步 |
| 增强对象 | 隐私审计、SCOPE-ZK 和最小影响修复 |

> 第一阶段审计要求所有贡献主张区分目标协议和当前实现。Final Order Authority、多节点共识、真实网络同步、真实网站connector和SCOPE-ZK尚未完成；历史实验的逐样本数据不完整。

## 1. 研究定位

本研究不再以“密码泄露后的集合证明”定义整个系统，而研究完整密码管理器在多设备、不可信云和动态撤销下的控制完整性。泄露分析只作为最后一组增强实验。

核心研究问题为：

> 如何让每台设备在不暴露密码、网站和账号关系的前提下，独立验证凭据的当前版本、操作主体、授权状态、撤销状态和透明历史，并使本地保存值与目标网站真实状态保持一致？

研究对象包含密码生成、字段加密、Origin 路由、自动填充、多设备同步、版本更新、网站确认、设备加入/撤销、恢复、VDNS 解析、透明日志和隐私审计。

## 2. 贡献主张

### C1：VDNS 可验证密码生命周期解析

传统同步查询返回密文对象；本方案返回 `State + Principal + Authorization + Version + Audit + Proof`。设备本地执行 L1～L5 后才下载和解密对象。

### C2：名称空间授权的凭据操作主体

DeviceOperationCredential 把设备签名扩展为带操作、scope、有效序、发行 counter、撤销引用和根链的资格证明，回答“签名者当时是否有权做这件事”。

### C3：不可信云上的可验证多设备同步

云只分发密文和候选索引，current version 由 VDNS descriptor 与透明检查点确定。设备拒绝旧版、错误 hash、错误 scope 和同版本冲突伪装。

### C4：生命周期与真实网站确认绑定

本地候选只有在 SITE_CONFIRMED 或符合策略的 USER_CONFIRMED 后才能成为 ACTIVE(v+1)。网站成功而本地尚未全局提交时，通过耐久新密码和独立恢复状态避免锁号。

### C5：周期隔离的隐私使用审计

Epoch 密钥和加密事件支持重复/历史/异常分析，公开层不形成稳定密码复用标签。

### C6：可选泄露—修复一致性

SCOPE-ZK 在事故活动内证明影响集合和 Completed/Pending 划分；其不可用不影响日常密码管理。

## 3. 研究假设

| 假设 | 对照 | 主要指标 | 支持条件 | 证伪条件 |
|---|---|---|---|---|
| H1 VDNS 解析能阻止云回滚/替换 | 仅云版本索引、仅对象 hash、完整 L1～L5 | 攻击接受率、误拒率、验证延迟 | 所有预设旧版/替换为 0 接受，合法输入无误拒 | 任一攻击对象被填充或 current state 被替换 |
| H2 设备能力+最终序能阻止撤销后操作 | 仅签名、墙钟撤销、完整方案 | 撤销后接受率、传播延迟 | 最终撤销序后接受率为 0 | 回填 observedAt 可绕过撤销 |
| H3 网站确认状态机降低密码失配/锁号 | 直接覆盖、两阶段但无耐久、完整状态机 | 密码丢失、错误激活、人工恢复次数 | 各崩溃点密码丢失和错误激活为 0 | 网站已改密后本地只剩旧密码 |
| H4 字段级模型降低更新开销 | 整 Envelope 重加密、字段级 | 写入字节、延迟、无关字段变化 | 只改密码时无关字段变化为 0 | 任一无关字段 ciphertext/wrapped key 改变 |
| H5 Epoch 审计在保留分析能力时减少公开链接 | 稳定标签、无标签、Epoch 方案 | precision/recall、跨 Epoch 链接率、开销 | 真值集可恢复，公开稳定链接不存在 | 公开投影可直接关联相同密码 |
| H6 可选响应精确限制修改范围 | 手工批量轮换、通用 zkVM、SCOPE-ZK | 证明时间/大小、越界修改、ChangedSet | 只有 Completed 项变化，无关字段不变 | Pending/Failed 被计入改变或越界项变化 |

H1～H4 是论文主结论，H5 是辅助创新，H6 是增强创新。即使 H6 工程实现受限，H1～H5 和完整密码管理主路径仍构成独立可评价系统。

## 4. 形式化对象与性质

### 4.1 当前版本安全

对设备 d 的可信检查点 `cp`、Credential `c` 和候选对象 `o`：

```text
AcceptObject(d,c,o,cp)
  ⇒ Hash(o)=Descriptor(c,cp).activeEnvelopeHash
  ∧ Version(o)=Descriptor(c,cp).activeVersion
  ∧ VerifyL1..L5(c,cp)=ACCEPT/allowed-degraded-read
```

新写入不能使用 degraded-read 例外。

### 4.2 授权安全

```text
AcceptedEvent(e)
  ⇒ SignatureValid(e.device)
  ∧ RootChainValid(e.credential)
  ∧ CapabilityAllows(e.operation,e.credentialId)
  ∧ e.finalSequence < RevokedAt(e.device)
```

`observedAt` 不参与最后一个不等式。

### 4.3 网站状态一致性

```text
Active(c,v+1)
  ⇒ LocalCiphertextDurable(c,v+1)
  ∧ SiteEvidence(c,v+1) ≥ PolicyThreshold
  ∧ DescriptorAccepted(c,v+1)
```

### 4.4 最小字段更新

对不在更新集合 U 的字段 f：

```text
f ∉ U ⇒
  CipherDigest(v,f)=CipherDigest(v+1,f)
  ∧ WrappedKeyDigest(v,f)=WrappedKeyDigest(v+1,f)
```

### 4.5 事故活动的局部关系

只有用户发起事故快照后才定义：

```text
A = Exposure(Snapshot, Incident)
A = C ˙∪ P
C ⊆ F
ChangedSet = C
```

AffectedRoot 只绑定输入/输出字节；语义正确性依赖证明系统、输入完整性和验证策略。

## 5. 实验平台与可复现性

### 5.1 固定环境字段

每次实验输出：git commit、protocol/suite、Go/Node/浏览器版本、OS、CPU、逻辑核、内存、存储类型、编译 flags、数据集版本、非安全 seed、预热次数、正式重复次数、开始/结束时间、ProviderKind 和原始结果 digest。

业务数据可用固定 seed 生成；密钥/nonce 的生产代码仍必须调用 CSPRNG。实验适配器在输出中标为 TEST_ONLY、SIMULATED、ANVIL 或 REAL，不混称。

### 5.2 数据集

| 数据集 | 规模 | 内容 |
|---|---:|---|
| D1 Daily-Small | 100 凭据、2 设备 | 常用站点策略、同域多账号、6 字段 |
| D2 Daily-Medium | 10,000 凭据、5 设备 | RouteMap、版本历史、增量同步 |
| D3 Daily-Large | 100,000 凭据、10 设备 | 查询、初始同步、对象规模 |
| D4 Log | 100k/1m 叶 | 合法追加、坏包含、双视图、回滚 |
| D5 Audit | 100,000 事件、12 Epoch | 重复、异常、陈旧、历史改密真值 |
| D6 Incident | 100/1k/10k 影响候选 | Completed/Pending/Failed、越界动作 |

Origin 和账号使用合成域名/值，不使用真实用户数据。密码按生成器策略产生，实验输出不打印密码。

## 6. E1 解锁、胶囊、加入与恢复

### 方法

- 在三类资源档位校准 Argon2id，分别运行正确/错误密码、错误 DeviceSecret、复制另一设备胶囊、篡改参数/tag；
- 运行已有设备批准和 RecoverySecret 恢复；
- 检查只凭主密码+云端 capsule 不能恢复；
- 记录锁定/超时后的内存句柄行为和 secret scan。

### 指标

P50/P95/P99 解锁时间、峰值 RSS、错误输入拒绝率、跨设备胶囊拒绝率、恢复成功率、活动 secret handle 数、日志秘密命中数。

### 判定

错误输入和跨设备复制接受率为 0，正确恢复为 100%，日志秘密命中为 0；解锁 P95 符合记录参数目标。

## 7. E2 日常密码管理

### 方法

完成注册/生成/创建/再次访问/解析/解密/填充全流程；对 D1～D3 测量 RouteMap、字段解密和端到端延迟；加入同域多账号、IDN、默认端口、恶意 iframe、错误 CredentialID 和 OriginBinding 篡改。

### 指标

生成延迟、创建延迟、RouteMap P50/P95/P99、单字段解密、缓存命中/未命中填充、错误 Origin 接受率、链/VRF/SCOPE 调用次数。

### 判定

缓存命中自动填充 P95 ≤100 ms；10k RouteMap P95 ≤5 ms；单字段解密 P95 ≤10 ms；错误 Origin 接受为 0；普通填充链/VRF/SCOPE 调用为 0。

## 8. E3 多设备同步与不可信云

### 攻击矩阵

| 场景 | 云行为 | 预期 |
|---|---|---|
| 正常增量 | 返回 VDNS current object | 接受 |
| 回滚 | current v2 时返回 v1 | 拒绝 ROLLBACK |
| 替换 | 返回其他 Credential object | 拒绝 digest/context |
| 同版本冲突 | v2 不同 descriptor | CONFLICT/REVIEW |
| 删除 | 缺失 current object | 明确不可用，不回退 |
| 重排 | 先返回后继、延迟前驱 | 等待/补齐，不跳过因果 |
| 离线恢复 | 使用已验证缓存 | 有限 DEGRADED read |

记录双设备和 5/10 设备初始/增量同步延迟、对象吞吐、冲突率、攻击接受率、缓存可用率和恢复时间。

## 9. E4 生命周期与网站确认

Mock Site 提供成功、明确失败、策略拒绝、MFA、连接中断、响应丢失和查询状态。对候选生成、对象 fsync、事务提交、请求发出、站点成功、回执持久化、descriptor 发布和 accepted CAS 每个点注入崩溃。

指标为密码丢失次数、旧密码错误填充次数、新密码错误激活次数、UNKNOWN 次数、自动恢复时间、人工确认次数和状态机非法边命中。目标是密码丢失/错误激活/错误回退均为 0。

## 10. E5 VDNS 与透明日志

分别破坏 L1 签名/根链、L2 capability/scope、L3 revoke/counter/predecessor/version、L4 inclusion/consistency/tree head/anchor、L5 缓存和风险策略。对 D4 测验证时延、proof bytes、hash 次数和 Monitor 发现时间。

目标：所有预置攻击产生对应 Verdict；合法输入无误拒；100k 叶 L1～L5 P95 ≤25 ms；1m 叶 inclusion proof 不超过 32 个 hash 加固定元数据；同 tree size 异根和回滚发现率 100%。

## 11. E6 撤销与新秘密代际

设备在 final sequence s 被撤销后，尝试回填 observedAt、重放旧 capability、使用旧 counter、提交新版本和请求 g+1 envelope。对照墙钟撤销与 final-sequence 撤销。

指标：s 后操作接受率、撤销传播延迟、错误 envelope 分发数、剩余设备 g+1 解封成功率、历史 g 对象读取成功率。目标是撤销后接受和错误分发均为 0，同时合法剩余设备和合法历史读取可用。

## 12. E7 隐私审计

在 D5 中预置同密码重复、历史复用、异常设备、长期未更新、回滚和冲突真值。比较稳定公开标签、无审计标签和 Epoch 加密见证。

指标：各风险 precision/recall、100k 扫描时延/内存、事件写入开销、公开字段秘密扫描、同密码跨 Epoch 公开链接成功率、padding/批量带宽。强证据真值 precision/recall 目标为 1；公开稳定标签命中为 0；扫描时间 ≤5 s。

本实验不宣称隐藏全局观察者可见的访问时间、大小和 IP 元数据；报告必须列出残余链接面。

## 13. E8 可选事故响应

比较本地普通计算、通用 zkVM 和可用的 SCOPE-ZK 实现。设置不同影响规模、事件窗口和部分网站失败；尝试将未受影响凭据加入 ChangedSet、把 Pending 标为 Completed、修改无关字段和重用旧 attempt proof。

指标：证明/验证时间、proof size、峰值内存、AffectedRoot/RotationRoot 一致性、越界接受率、Completed/Pending/Failed 计数、无关字段变化字节和动作总成本。

目标：越界接受为 0，ChangedSet=Completed，部分失败不冒充成功，只更新密码时无关字段变化为 0。SCOPE-ZK 不可用时记录明确的 optional unavailable，不将 E1～E7 判为失败。

## 14. 消融实验

| 移除机制 | 预期变化 | 目的 |
|---|---|---|
| 去掉 DeviceSecret | 云 capsule 可作为主密码离线验证条件 | 说明设备绑定的价值 |
| 去掉 OriginBinding | 跨站对象替换更难在解密前绑定 | 说明填充边界 |
| 去掉 VDNS current version | 云回滚可被接受 | 验证 H1 |
| 去掉 capability | 任何有效设备签名可越权操作 | 验证 C2 |
| 墙钟代替 final sequence | 回填时间绕过撤销 | 验证 H2 |
| 新密码未先耐久 | 崩溃后可能只剩旧密码 | 验证 H3 |
| 整 Envelope 重加密 | 无关字段变化和带宽上升 | 验证 H4 |
| 稳定公开 ReuseTag | 跨 Epoch 密码关系可链接 | 验证 H5 |

## 15. 统计与报告方法

- 延迟至少预热 10 次、正式重复 30 次；高成本证明可降低次数但必须记录理由；
- 报告中位数、P95、P99、均值、标准差和 95% bootstrap 置信区间；
- 攻击接受/拒绝按二项结果报告样本数和置信区间；
- 同机配对比较优先使用配对差值；分布明显非正态时使用 Wilcoxon；
- 所有原始 JSON/CSV、生成器版本、seed、构建信息和失败样本保留；
- 结果不达目标时仍写入论文，并区分实现瓶颈、硬件限制和机制成本。

## 16. 有效性威胁

### 内部有效性

缓存、JIT/GC、磁盘 page cache、后台进程和模拟网络会影响性能。通过固定环境、预热、重复、独立冷/热缓存组和原始数据降低偏差。

### 构念有效性

“签名有效”不等于“授权有效”，“自动填充”不等于“登录成功”，“Root 被锚定”不等于“集合语义正确”，“跨 Epoch 标签变化”不等于“完全匿名”。实验指标分别对应这些性质，不使用含混总分替代。

### 外部有效性

Mock Site 不能代表所有真实网站；Anvil/模拟日志不能代表生产拜占庭网络；桌面 Argon2 参数不能直接推广到手机。论文把这些结果描述为原型机制证据，并给出真实 Connector、移动端和多日志部署的后续验证范围。

### 结论有效性

避免只展示成功路径或单次最好结果。预先冻结数据集、指标、失败标准和分析脚本；协议/阈值变化通过 ADR 和新实验版本记录。

## 17. 论文证据映射

| 章节 | 证据 |
|---|---|
| 第四章密码学存储/同步 | E1、E2、E3、KAT、篡改测试 |
| 第五章生命周期协议 | E3、E4、E6、状态机模型测试 |
| 第六章隐私审计/响应 | E7、E8、公开面秘密扫描 |
| 第七章安全分析 | H1～H6、形式化性质、负向矩阵、残余风险 |
| 第八章实现/实验 | 原始 JSON/CSV、环境、统计、消融和失败结果 |

## 18. 结论边界

若实验满足假设，允许主张：原型在定义的攻击模型和检查点假设下阻止云端回滚/替换与撤销后操作；网站确认状态机改善本地/网站一致性；字段级更新降低无关写入；Epoch 审计减少稳定公开关系。

不允许主张：系统对完全受控终端仍保密、链上锚定自动保证所有状态真实、撤销能回收历史明文、Mock Site 证明适配所有网站、Epoch 机制达到流量匿名、AffectedRoot 单独证明影响集合正确，或 SCOPE-ZK 是日常密码管理所必需。
