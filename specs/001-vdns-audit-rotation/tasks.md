# VDNS-PM 第二阶段实施任务清单

| 属性 | 值 |
|---|---|
| 基线 | Spec 001 v2.1.0 / Stage 1协议设计冻结 |
| 当前阶段 | G6研究原型集成；G7未达成 |
| 生成日期 | 2026-07-31 |
| 状态来源 | `docs/reviews/stage1-completion-audit.md` |
| 优先级 | P0协议正确性；P1安全实现；P2测试与故障恢复；P3性能和工程优化 |

历史v2.0.0清单把97项全部标为完成，无法反映第一阶段审计发现。本清单替代该完成口径。任务只有在代码、负向测试、验收证据和论文声明同步后才能关闭。文档存在不等于实现完成。

## Stage 2执行状态

| Stage 1任务 | Stage 2结果 | 说明 |
|---|---|---|
| P0-001 | COMPLETE（研究适配器范围） | 单节点Authority、签名回执、幂等、SQLite恢复和检查点已实现；生产共识仍`NOT_IMPLEMENTED` |
| P0-002 | COMPLETE（研究适配器范围） | 2/3设备分支、隐藏分支、乱序、重试、裁决和崩溃边界已有测试；多进程试验留第三阶段 |
| P0-003 | COMPLETE（允许的边界内） | E0～E5、SQLite v2.1投影、API和状态机已迁移；真实E4 Connector仍`NOT_IMPLEMENTED` |
| P0-004 | PARTIAL | 三层领域模型、集合和状态规则已实现；完整API/UI/网站修复编排未闭环 |
| P0-005 | COMPLETE | Go、扩展和共享向量覆盖规范化、iframe、重定向、降级和显式多Origin策略 |
| P0-006 | PARTIAL | L4/L5已有检查点与分叉拒绝；新设备带外初始检查点的产品流程未完成 |
| P0-007 | COMPLETE | OpenAPI 2.1.0、Evidence/FinalOrder线格式、SQLite v8、动态任务统计和真实baseline迁移已对齐 |
| P1-001～004 | PARTIAL/NOT_IMPLEMENTED | 属于平台安全存储、真实浏览器、真实E4和外部复核，仍需后续阶段 |
| P2-001～005 | NOT_IMPLEMENTED | 第三阶段证据与实验任务，不用本阶段定向测试冒充 |
| P3-001～004 | PARTIAL/NOT_IMPLEMENTED | 已建立分离基准和HTTP试验台，最终优化与E1～E8尚未执行 |

## P0 协议正确性

### P0-001 实现 Final Order Authority 与排序回执

- **问题：** 当前`finalSequence`由调用方提供，单机日志只检查单调性，没有权威生产者或可验证终局。
- **涉及模块：** `internal/protocol`、`internal/transparency`、`internal/anchor`、`internal/resolver`、SQLite迁移、OpenAPI。
- **验收条件：** 普通调用方不能自报最终序；Authority对对象摘要、前序、Namespace、序号和key generation签署回执；同序双摘要触发finding；检查点前标记provisional，高风险写不把它当final。
- **需要增加的测试：** 伪造回执、重复序号、前序错、Authority换代、同序分叉、检查点前撤销/写入竞争、重启恢复。
- **对应论文章节：** 第三章VDNS架构、第五章生命周期协议、第七章安全分析。

### P0-002 修正跨设备CAS与冲突终局

- **问题：** 本地CAS不能阻止设备A/B分别生成`v2-A/v2-B`，旧文档误写成全局唯一。
- **涉及模块：** credential aggregate、SQLite conflict repository、sync acceptance、resolver L3、local API。
- **验收条件：** 双设备同base不同候选全部保留并进入CONFLICTED；云端、墙钟和到达顺序不能自动选择；显式`CONFLICT_RESOLVE`引用全部候选并经最终序后更新accepted。
- **需要增加的测试：** 两个独立SQLite进程并发、离线重连、候选缺失、恶意云只返回一支、裁决重放、裁决后旧分支回滚。
- **对应论文章节：** 第四章多设备同步、第五章版本与冲突、第七章因果一致性。

### P0-003 迁移E0～E5网站证据等级

- **问题：** 代码仍使用`LOGIN_INFERRED/USER_CONFIRMED/SITE_CONFIRMED`旧值，和v2.1.0冻结规范不一致。
- **涉及模块：** `internal/protocol/registry.go`、credential/site/audit、local API、HTTP handler、SQLite、扩展、OpenAPI。
- **验收条件：** E0/E1/E2永不激活；E3只有严格策略可激活；E4验证站点信任和签名；E5明确为用户声明；旧对象通过schema version显式迁移或拒绝，不能重解释。
- **需要增加的测试：** 六级正负矩阵、旧枚举迁移、页面成功误报、重登录跨Origin/重定向、过期/重放站点回执、用户确认签名与权限。
- **对应论文章节：** 第五章网站确认、第七章状态一致性、第八章E4。

### P0-004 落实设备撤销三层状态

- **问题：** 控制面撤销、秘密代际隔离和网站凭据修复当前只在不同模块中分散表达。
- **涉及模块：** device、rotation、remediation、resolver、SQLite、API/UI。
- **验收条件：** 三层有独立状态和证据；控制面最终化后拒绝未来操作；g+1只发给活动设备；外部凭据逐项确认；UI明确旧密码不可收回。
- **需要增加的测试：** 撤销与操作竞争、代际中断恢复、部分设备离线、外部修复部分失败、旧明文仍可用的残余风险展示。
- **对应论文章节：** 第四章设备与恢复、第五章撤销、第七章安全边界。

### P0-005 完成CanonicalOrigin与重定向规则

- **问题：** 现有代码覆盖IDN、大小写、端口和iframe，缺少重定向后重新授权的完整闭环。
- **涉及模块：** credential origin、autofill authorization、browser extension、Native Messaging、secret handle。
- **验收条件：** 精确scheme/host/port、Punycode、子域隔离、top-frame、iframe默认拒绝全部一致；每次重定向后重算Origin；旧handle跨Origin失败；HTTP降级不携带秘密。
- **需要增加的测试：** 同/跨子域重定向、HTTPS→HTTP、端口变化、IDN同形、嵌套iframe、页面伪报Origin、重定向后handle重放。
- **对应论文章节：** 第四章RouteMap与自动填充、第七章Origin安全。

### P0-006 实现可信初始检查点与分叉处置

- **问题：** 新设备如何得到第一份可信检查点、日志分叉后如何停止/恢复高风险操作尚未落到代码。
- **涉及模块：** enrollment、recovery、resolver L4/L5、monitor、checkpoint store。
- **验收条件：** 仅已有设备、恢复承诺或带外核对可引入高风险信任；云端TOFU只能只读受限；分叉触发REVIEW/REJECT并保留证据；恢复需要用户选择或治理回执。
- **需要增加的测试：** 恶意首个检查点、旧恢复检查点、相同高度双根、gossip证据导入、离线读取、高风险写失败关闭。
- **对应论文章节：** 第三章信任模型、第五章L4/L5、第七章透明历史。

### P0-007 对齐规范、线格式、迁移和API

- **问题：** v2.1.0新增EvidenceLevel和FinalOrderReceipt，当前Go常量、迁移、KAT和API实现尚不一致。
- **涉及模块：** protocol registry、migrations、OpenAPI、contract tests、all consumers。
- **验收条件：** 注册表、Go枚举、CBOR、SQLite、OpenAPI、扩展和论文使用同一语义；产生新KAT；legacy对象有明确导入/拒绝策略；breaking change记录完整。
- **需要增加的测试：** 固定向量、错误宽度/枚举、legacy导入、跨版本重放、OpenAPI实现一致性。
- **对应论文章节：** 第四/五章实现、第八章API评估。

## P1 安全实现

### P1-001 接入设备秘密与私钥的安全存储

- **问题：** DeviceSecret和私钥机制已实现，生产OS key store/硬件边界未实现。
- **涉及模块：** platform、cryptokit、local agent、设备初始化。
- **验收条件：** Linux/macOS/Windows至少选择一个目标平台实现受保护存储；导出默认禁止；锁定销毁句柄；不可用时明确降级或拒绝。
- **需要增加的测试：** 权限、进程重启、锁屏、备份误包含、key store拒绝和降级提示。
- **对应论文章节：** 第四章本地密码学、第七章残余风险。

### P1-002 强化本地Agent与扩展进程边界

- **问题：** 研究原型已有InstallToken、nonce和handle，仍需真实浏览器/Native Messaging环境验证。
- **涉及模块：** `cmd/vdns-local-agent`、httpapi、nativemessaging、browser extension。
- **验收条件：** Host/CORS/extension ID/CSRF/Origin全部独立验证；secret不进入HTTP普通JSON、日志、命令行或持久前端存储；真实浏览器完成日常闭环。
- **需要增加的测试：** 跨扩展调用、恶意网页直连、nonce重放、handle过期、并发消费、浏览器重启。
- **对应论文章节：** 第三章信任边界、第四章自动填充、第八章实现。

### P1-003 建立真实Connector信任注册

- **问题：** 当前只有Mock Site，E4缺少真实签发者治理和密钥轮换。
- **涉及模块：** site connector ports、trust registry、resolver L5、API/UI。
- **验收条件：** connector身份、Origin范围、key generation、有效期、撤销和nonce绑定可验证；Mock与真实Provider标签不可混淆。
- **需要增加的测试：** 错Origin、错key、旧generation、回执重放、connector撤销、部分站点失败。
- **对应论文章节：** 第五章网站确认、第七章伪造威胁。

### P1-004 密钥生命周期与第三方安全复核准备

- **问题：** 内部测试通过不能替代独立密码学/安全审计。
- **涉及模块：** cryptokit、protocol、SBOM、threat model、runbook。
- **验收条件：** 密钥生成/存储/轮换/销毁清单完整；KAT和域分离表可复核；所有研究适配器有风险标签；形成外部审计包。
- **需要增加的测试：** 跨域重放总矩阵、内存/日志秘密扫描、异常退出清理、依赖升级回归。
- **对应论文章节：** 第七章安全性与限制。

### P1-005 完整L1～L5与最终序回执闭环

- **问题：** 本地API曾返回合成的五层成功字符串，L3只信任调用方提供的序号，失败结果还可能保留前几层投影。
- **涉及模块：** `internal/resolver/application`、`internal/resolver/domain`、`internal/finalorder`、local API composition。
- **验收条件：** L1～L5逐层验证并返回独立错误码；L3可强制验证Authority回执；冲突进入REVIEW；失败清空身份、授权、状态和审计投影；未配置完整Verifier的API明确返回不可用。
- **需要增加的测试：** 五层各自成功/失败、回执篡改、已知冲突、离线缓存过期、高风险写不降级、失败投影清空、100k叶完整流程与Merkle微基准分名。
- **对应论文章节：** 第五章VDNS验证、第七章安全分析、第八章性能方法。
- **Stage 2状态：** COMPLETE（研究原型）；第三阶段重新冻结性能数据。

### P1-006 研究型HTTP同步适配器

- **问题：** 内存函数调用不能证明网络传输、超时、分页、重试和请求限制行为。
- **涉及模块：** `internal/adapters/researchsync`、sync domain、localhost集成测试。
- **验收条件：** 真实HTTP完成内容寻址对象/manifest上传下载、分批、cursor、幂等、重试和大小限制；可模拟回滚、替换、对象损坏和隐藏分支；部署标签固定为`RESEARCH_HTTP_SYNC_ADAPTER`。
- **需要增加的测试：** 10k对象分批、网络中断、延迟/超时、重复上传、部分响应、hash不匹配、旧manifest和隐藏分支。
- **对应论文章节：** 第四章同步协议、第八章网络化试验方法。
- **Stage 2状态：** COMPLETE（localhost研究适配器）；公网与生产云`NOT_IMPLEMENTED`。

### P1-007 OpenAPI实现覆盖与能力边界

- **问题：** 仅比较22个operationId无法证明handler、领域逻辑和测试一致，且可选接口容易被误报为已实现。
- **涉及模块：** OpenAPI、httpapi、localapi、`scripts/generate_api_coverage.py`、合同测试。
- **验收条件：** 22项逐项生成机器报告；字段、错误码、Idempotency-Key、expectedVersion和cursor匹配；合成VDNS成功被移除；SCOPE-ZK/E4等未实现能力返回明确错误。
- **需要增加的测试：** operation清单、secret字段扫描、写请求头、严格JSON、分页、可选501、API覆盖生成器回归。
- **对应论文章节：** 第三章接口架构、第四/五章实现、第八章工程验证。
- **Stage 2状态：** COMPLETE（覆盖结论包含PARTIAL/NOT_IMPLEMENTED，不宣称22项全部完成）。

## P2 测试与故障恢复

### P2-001 重建实验原始数据管线

- **问题：** 历史E1～E5只保存汇总指标，无法独立复算每轮统计。
- **涉及模块：** G7 research runner、experiment schemas、claim-evidence map。
- **验收条件：** 每次测量原始值、错误、环境、命令、单位和范围进入不可变JSONL/CSV；汇总由原始值确定性生成；失败样本保留。
- **需要增加的测试：** schema校验、汇总复算、缺样本拒绝、单位混淆、篡改摘要。
- **对应论文章节：** 第八章实验方法与全部E1～E8。

### P2-002 建立真实多进程网络同步试验台

- **问题：** 当前E3只测本地manifest构造、签名和验证。
- **涉及模块：** 新sync service adapter、对象传输、两个独立Agent/SQLite实例、网络故障代理。
- **验收条件：** 报告manifest、对象上传下载、认证、重试、网络延迟和总时延；10k初始/增量分开；攻击云仍不能改变accepted状态。
- **需要增加的测试：** 丢包、乱序、重复、限速、断连、对象损坏、双设备并发。
- **对应论文章节：** 第四章同步、第八章E3。

### P2-003 升级故障注入与恢复命名

- **问题：** 历史“全栈故障”和“恢复演练”实际为定向本地Go测试。
- **涉及模块：** fault runner、recovery scripts、runbooks、evidence schema。
- **验收条件：** 旧8/8标为LOCAL_INTEGRATION；新增多进程场景才可称系统集成；每项记录注入点、观测、退出码和原始日志；恢复区分自动测试与人工操作。
- **需要增加的测试：** 服务崩溃、数据库锁、日志双视图、Authority故障、备份介质缺失、人工裁决步骤。
- **对应论文章节：** 第八章故障与恢复。

### P2-004 更新安全扫描快照

- **问题：** “当前可达漏洞为0”只由2026-07-22数据库快照支持。
- **涉及模块：** security gate、govulncheck、SBOM、license/secret scan。
- **验收条件：** 使用当前工作树和扫描数据库重跑；保存scanner/db时间和原始输出；reachable/module-only分开；任何例外有书面裁决。
- **需要增加的测试：** 扫描器失败、数据库不可达、过期快照、已知测试秘密误报处理。
- **对应论文章节：** 第八章安全工程结果。

### P2-005 建立论文声明自动核对

- **问题：** 历史门禁只验证文件/命令，不能阻止微基准或Mock证据被提升口径。
- **涉及模块：** experiments claim map、论文构建检查、Stage审计。
- **验收条件：** 每个数值和完成声明绑定证据ID、等级、数据范围和日期；弱等级不能满足强claim；UNAVAILABLE自动禁止生成数值。
- **需要增加的测试：** Merkle冒充L1～L5、local冒充network、Mock冒充site、null proof变0、历史扫描冒充current。
- **对应论文章节：** 第八章和结论。

## P3 性能和工程优化

### P3-001 分离并优化完整L1～L5与Merkle基准

- **问题：** 历史G7表只列Merkle微基准，完整L1～L5证据在另一测试中。
- **涉及模块：** resolver benchmark、transparency benchmark、experiment runner。
- **验收条件：** 两类指标独立命名、保存原始样本；100k/1m叶、不同proof大小和冷/热缓存分别报告。
- **需要增加的测试：** 各层单独失败、proof上限、缓存失效、签名key换代。
- **对应论文章节：** 第八章E5。

### P3-002 设计10k同步分片和背压

- **问题：** 单份10k引用超过64KiB签名载荷上限，当前固定为100×100。
- **涉及模块：** sync manifest、OpenAPI、network adapter、SQLite。
- **验收条件：** 分片root、顺序无关集合承诺、分页、重试和幂等语义冻结；内存有界；不完整批次不更新accepted。
- **需要增加的测试：** 边界大小、缺片、重复片、乱序、恶意超大输入、恢复继续。
- **对应论文章节：** 第四章协议、第八章E3。

### P3-003 扩展真实浏览器与设备性能矩阵

- **问题：** 当前浏览器未安装，扩展仅有Node合同/TAP和本地e2e。
- **涉及模块：** browser extension、local agent、CI/实验脚本。
- **验收条件：** 至少Chrome/Chromium真实自动化；记录解锁、解析、填充、更新UX时延；移动/低配设备作为后续分层报告。
- **需要增加的测试：** 多标签页、iframe、重定向、浏览器重启、扩展升级、离线。
- **对应论文章节：** 第八章E2与可用性。

### P3-004 可选评估SCOPE-ZK

- **问题：** 当前只有provider接口和本地修复基线，没有SCOPE-ZK实现。
- **涉及模块：** exposure provider、proof verifier、experiment E8。
- **验收条件：** 仅在引入经审查实现后报告proof time/size/memory；验证`A=C dot-union P`、`C subseteq F`和`ChangedSet=C`；功能关闭不影响日常主线。
- **需要增加的测试：** 错快照、错集合、proof篡改、部分失败、越界修改、provider不可用。
- **对应论文章节：** 第六章隐私审计与泄露响应、第八章E8。

## G7冻结门禁

G7只有在P0全部完成、P2-001/P2-004/P2-005完成、当前测试与新证据通过、论文声明不再含阻断级`UNVERIFIED`后才能进入。SCOPE-ZK仍可保持可选`NOT_IMPLEMENTED`，但E8不得声称完成证明系统对比。

## 需求与验收追踪

| 任务组 | 主要FR | 主要AC | NFR侧重 |
|---|---|---|---|
| P0-001/P0-006/P0-007 | FR-006～008、FR-021、FR-027～035 | AC-004、AC-006～010、AC-012～013、AC-016、AC-021 | COR-003～004、AVL-003、SEC-003～004、MNT-001～004、API-001～003 |
| P0-002 | FR-019～022、FR-025～026 | AC-003～004、AC-006、AC-009、AC-012 | COR-001～004、AVL-001～003 |
| P0-003/P1-003 | FR-017、FR-023～024、FR-036 | AC-002、AC-005、AC-014、AC-017 | COR-001～002、SEC-004、AVL-001 |
| P0-004 | FR-005～008、FR-027、FR-030、FR-041～043 | AC-007～009、AC-014、AC-018 | SEC-001～005、COR-004、AVL-001～003 |
| P0-005/P1-002 | FR-009～018 | AC-002～003、AC-011～016 | SEC-001～006、PERF-002～004、API-001～003 |
| P1-001/P1-004 | FR-001～008、FR-012、FR-021 | AC-001、AC-007～013、AC-020～021 | SEC-001～007、MNT-001～004 |
| P2-001/P2-005/P3-001 | FR-001～043 | AC-001～021 | 全部NFR，重点PERF-001～008、MNT-003～004 |
| P2-002/P2-003/P3-002 | FR-019～035 | AC-003～010、AC-016、AC-019～020 | COR-001～004、AVL-001～004、PERF-005～007 |
| P2-004 | FR-001～043 | AC-011～013、AC-020～021 | SEC-001～007 |
| P3-003 | FR-009～018 | AC-002、AC-015～016、AC-019～020 | PERF-001～004、AVL-002～004 |
| P3-004 | FR-039～043 | AC-014、AC-016、AC-018～021 | PERF-008、MNT-002～004 |

覆盖检查：FR-001～043、AC-001～021、全部 NFR。`check_spec_trace.py`已从当前任务标题动态统计P0～P3，拒绝缺失、重复、跳号和未知优先级，不再硬编码97个历史任务。
