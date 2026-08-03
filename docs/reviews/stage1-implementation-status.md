# VDNS-PM 第一阶段实现状态

> 本文为历史阶段记录，其中VDNS-PM为VPass的旧名称。

## 1. 当前真实完成度

当前仓库已经形成可运行的Go模块化研究原型。核心包括RootCapsule/RecoveryCapsule、字段级加密、RouteMap、密码生成、SQLite事务与outbox、凭据生命周期、Mock Site确认、同步清单接受、VDNS L1～L5本地验证、Merkle透明日志、Monitor、隐私审计、本地修复基线、浏览器扩展和本地Agent。审计前全量Go测试通过，vet、race及扩展测试通过。v2.1.0冻结后除合同包外的Go包通过；合同包因旧2.0.0版本/摘要断言产生两项预期失败，准确反映代码迁移尚未完成。

系统仍处于 G6。关键缺口集中在“全局控制面如何产生可信最终序”和“文档冻结语义如何落到代码”。这些缺口会影响撤销、跨设备CAS、冲突裁决和G7实验结论，不能用已有单机测试掩盖。

## 2. 研究适配器与生产组件

| 当前组件 | 当前性质 | 生产替换或补充要求 |
|---|---|---|
| `internal/transparency/application` | 单进程内存透明日志 | 独立持久日志、复制、见证者/gossip、访问控制和运维 |
| `memoryanchor` | 内存公告模拟器 | 可验证公告服务或生产链客户端 |
| `anvilanchor` | 本地EVM研究适配器 | 明确链、确认深度、重组处理、合约治理和监控 |
| `memorysync` | 本地同步端口适配器 | 鉴权网络服务、对象传输、重试、限流和多设备部署 |
| Mock Site | 生命周期/回执测试站点 | 真实站点connector、用户确认UX和站点信任注册 |
| 本地 L1～L5 resolver | 验证算法研究实现 | 独立解析服务可选；本地验证器仍是最终采信点 |
| 本地 finalSequence 输入 | 测试夹具/调用方字段 | Final Order Authority与签名排序回执 |
| Disabled SCOPE-ZK provider | 可选功能关闭路径 | 经审查的电路、prover、verifier和基准 |

## 3. 功能—代码—测试—证据映射摘要

| 功能族 | 代码 | 测试 | 证据结论 |
|---|---|---|---|
| 解锁、胶囊、字段密码学 | `internal/cryptokit` | KAT、变异、race | 本地研究实现闭合 |
| 路由、Origin、凭据 | `internal/credential`、SQLite | 单元、合同、E2 | 本地功能闭合；重定向规则待补 |
| 生命周期、确认 | credential/site | Mock、崩溃、UNKNOWN | 状态机闭合；真实网站未验证 |
| 设备、撤销、恢复 | device/recovery/resolver | 加入、代际、恢复演练 | 机制部分闭合；依赖未实现最终序 |
| 同步 | sync、memorysync | 回滚/替换/冲突 | 本地协议闭合；网络服务未实现 |
| VDNS/透明历史 | resolver/transparency/monitor/anchor | L1～L5、proof、fork | 本地算法闭合；多节点信任未实现 |
| 隐私审计 | audit | 能力、复用、异常、100k | 本地分析闭合；部署隐私未验证 |
| 泄露响应 | exposure/remediation | unavailable、scope、attempt | 本地基线部分完成；SCOPE-ZK未实现 |

详细逐项状态见 `docs/reviews/stage1-completion-audit.md`。

## 4. 已知限制

1. 工作区没有Git元数据，历史证据只能记录 `WORKTREE_NO_GIT`。
2. 当前没有 `services/`，文档中的服务是逻辑边界。
3. 透明日志和锚定是研究适配器，不提供生产拜占庭共识。
4. `finalSequence` 由调用方提供；当前仓库没有权威生产者。
5. 证据等级代码仍使用 `LOGIN_INFERRED/USER_CONFIRMED/SITE_CONFIRMED`旧语义。
6. Mock Site不等同于真实网站，页面成功提示不构成密码学证明。
7. 设备撤销无法回收已经复制的密码、根或历史字段明文。
8. E3性能只包含本地manifest计算，不含网络和对象传输。
9. G7 E5微基准只测Merkle包含证明；完整L1～L5需单独报告。
10. E1～E5的逐轮duration没有写入证据文件。
11. SCOPE-ZK和通用zkVM均未实现。
12. 历史漏洞扫描不能代表2026-07-31当前状态。

## 5. 协议债务

| 债务 | 风险 | 冻结处理 | 第二阶段动作 |
|---|---|---|---|
| 最终序生产者缺失 | 撤销和冲突依赖未经证明的序号 | ADR-012/013定义Final Order Authority | 实现端口、签名回执、持久化与验证 |
| 全局CAS误表述 | 两设备可分别成功写本地v2 | 明确本地CAS与全局终局分离 | 增加双分支检测、CONFLICTED和裁决 |
| 证据等级旧枚举 | 页面推断可能被当强确认 | ADR-014冻结E0～E5 | 协议/DB/API/扩展整体迁移 |
| 撤销边界混合 | 易误称“收回旧密码” | ADR-015拆为三层 | UI、API、轮换流程和测试对齐 |
| Origin规则不完整 | 子域/iframe/重定向可能越权 | ADR-016冻结规范 | 增加redirect与top-origin测试 |
| 实验证据口径混淆 | 微基准冒充端到端 | ADR-017冻结证据等级 | 输出原始样本和claim-evidence映射 |
| 10k manifest容量 | 单份对象引用超过64KiB上限 | 保持100×100历史口径 | 设计分页/分片合同和网络基准 |

## 6. 下一阶段任务

第二阶段以 `tasks.md` 中的 P0～P3 为唯一执行清单：

- P0：实现最终序权威、跨设备冲突、证据等级迁移、撤销三层和Origin规则；
- P1：强化设备秘密存储、真实connector信任、API与进程边界；
- P2：补原始实验数据、真实多进程/网络同步、故障和恢复证据；
- P3：完整L1～L5性能、网络规模、浏览器兼容和可选SCOPE-ZK研究。

G7之前仍未解决的P0是：最终序权威、跨设备双分支终局、E0～E5代码迁移、可信初始检查点和撤销竞争排序。
