# 强通用方法、原文映射与完整成本

2026-11-05。本文为定向核查，共使用 2 篇前轮已取得的状态连续性/历史一致性全文、5 篇本轮新取得的直接后续全文，以及 2 份本地原生撤销近邻文本。读取范围按下表登记，覆盖判断基于正文。本文采用单一研究流程的资料与论证审查，尚无外部独立评审。

本轮新文献检索/获取共 13 次公共 HTTP 请求，分为 3 次元数据检索和 10 次定向获取；均收到响应体。元数据命中与题名识别逐项判断，HTTP 成功本身只说明响应取得。原始请求台账位于 evidence/SEARCH_01.json、RETRIEVAL_01.json、RETRIEVAL_02.json、RETRIEVAL_03.json。原生服务请求为 0。该分母支持本轮限定覆盖分析，范围外优先权保持开放。

## 1. 原文定位与变量映射

`L*.txt` 的行号绑定本轮提取文件；PDF 页码指含封面在内的文件页。5 篇新增 PDF 的结构预检均 PASS。Memoir 沿用前轮 PASS；SUNDR 结构预检 UNAVAILABLE，采用已核读章节及文本行号，PDF 页码保持未核准。

| 编号、原始来源与版本 | 实际读取位置 | 原文结论、映射与用途 |
|---|---|---|
| M：Parno 等，*Memoir: Practical State Continuity for Protected Modules*，IEEE S&P 2011；[DOI](https://doi.org/10.1109/SP.2011.38)，[作者机构全文](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/memoir.pdf) | P_memoir.txt §II.B；§III.A–C，386–442、505–642、642–822；重点 Fig.6 | 确定性受保护模块、认证快照、请求历史摘要和安全重放。模块映射 R 的本地状态机；快照映射批准/pending/消费状态。Basic 每次请求更新 NVRAM。Opt 用 PCR、guard bit、ExtensionSecret 与关机 checkpoint 节省 NVRAM；保证 checkpoint 需要 UPS/可靠硬件路径。内部重放只证明本地确定性语义，外部 OAuth 重试另需合同 |
| S：Li 等，*Secure Untrusted Data Repository (SUNDR)*，OSDI 2004；[官方全文](https://www.usenix.org/legacy/events/osdi04/tech/full_papers/li_j/li_j.pdf) | P_sundr.txt §3.2，316–341；§3.3.2，459–476 | 服务器可隐藏另一个用户已完成的更新；分叉一致性限制可伪造历史。在线可信一致性服务可增强保证；版本结构可缓存/增量传输。用户历史映射多个授权/恢复参与者。单独 SUNDR 不能支撑全局最新撤回；加入同条件权威后继续作为强组合 |
| L1：Brandenburger、Cachin、Lorenz、Kapitza，*Rollback and Forking Detection for Trusted Execution Environments Using Lightweight Collective Memory*，DSN 2017；[DOI](https://doi.org/10.1109/DSN.2017.45)，[arXiv 全文](https://arxiv.org/pdf/1701.00981)，本地稿标注 2017-06-20 | L1_lcm.txt §2.1–2.3，97–192；§3.2，241–297；§4.2.3，392–403；§4.5–4.6.1，507–542 | 所有客户端正确且相互信任；客户端必须把序号/历史哈希恢复自稳定存储。operation stability 与 majority stability 各有定义。把每客户端常量状态移至用户/恢复端仍需计费。旧代理 A 具有恶意能力时，不能直接把 A 当作原模型的可信客户端。多数稳定等待和刷新通知也影响 ACK 与 B |
| L6：Matetic 等，*ROTE: Rollback Protection for Trusted Execution*，USENIX Security 2017；[官方页面](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/matetic)，[全文](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-matetic.pdf) | L6_rote.txt §2.1–2.2，238–330；§2.5–3.1，412–508；§4.2–4.5，625–698、795–854；PDF pp.4–9 | 通过辅助 enclave 的分布式计数维护当前性。原文辅助节点数 n=f+2u+1，本文避免符号冲突，改记 a=f+2z+1；z 为允许不可达节点数。更新有 echo/返回 echo/final ACK；重启要求所有辅助节点重新建会话。降低本地慢计数器依赖，同时增加可信节点、消息、故障域与恢复等待 |
| L7：Hartono、Brito、Fetzer，*CRISP: Confidentiality, Rollback, and Integrity Storage Protection for Confidential Cloud-Native Computing*，IEEE CLOUD 2024；[DOI](https://doi.org/10.1109/CLOUD62652.2024.00026)，[全文](https://arxiv.org/pdf/2408.06822) | L7_crisp.txt §III.A–C，265–432；PDF pp.3–4，尤其 354–364、393–427 | 每个 fsync 对应计数器/存储认证更新；乐观批处理先 ACK，之后防回滚保护才完成；Checker 阻塞至 promised local value 已被 stable counter 覆盖。撤回成功响应应置于该 barrier 以后。故通用基线同时拥有批处理和强应用 ACK，无需限定成逐操作同步写 |
| L10：Angel 等，*Nimble: Rollback Protection for Confidential Cloud Services*，OSDI 2023；[官方页面](https://www.usenix.org/conference/osdi23/presentation/angel)，[全文](https://www.usenix.org/system/files/osdi23-angel.pdf) | L10_nimble.txt §3.1–3.2，282–430；§4，449–534；§5.1 开头，545–565；§9.1，1444–1480；PDF pp.4–7、15 | append 绑定 ledger label、state、expected index；read_latest 回执绑定新 nonce；大状态可留普通存储，仅摘要进账本。远端 endorsers 保存受保护易失尾部并以多数签名回执认证。多数永久丢失时保持安全但失去活性；新建旧快照实例不能自动延续原来最新状态。对应在线权威强基线的完整原文例证 |
| L8：Burke 等，*It’s a Feature, Not a Bug: Secure and Auditable State Rollback for Confidential Cloud Applications*（REBOUND），IEEE S&P 2026；[DOI](https://doi.org/10.1109/SP63933.2026.00148)，[arXiv 全文](https://arxiv.org/pdf/2511.13641)，版本固定以本地 SHA 为准 | L8_rollback.txt §2.1，153–209；§4.1，528–555；§4.3，698–757；§4.4–5 开头，821–889；PDF pp.2、5、7–8 | 最新 authoritative root 绑定硬件计数器，多份历史/策略认证字典共同封存；intent/completion 记录、原子 seal 和恢复 counter 规则。直接覆盖“统一新鲜根绑定策略与历史”的一般组合思路。§4.4 将若干恢复策略细节留给未来工作，§5 标为 informal analysis；本轮按该强度使用，不将其升级为已复核的一般密码学定理 |

Memoir/SUNDR 的本地路径位于前轮 `crypto_recovery_function_2026-11-05/sources/`，哈希见本轮 INPUT_MANIFEST.json；新增全文哈希见 NEW_SOURCES.json。页码/行号只证明可定位读取，结构预检与数学证明分别登记。

两份原生近邻属于外部效果层的条件参照：

- Root-Scoped Quiescence，本地 `D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P03_全文.txt`，§3.4 Table 2、A8/A9、Theorem 5 与附录证明（453–459、741–746、1848–1874）。其 crash-safe monotonicity 明确要求持久排序、精确重试与恢复保持 fence/epoch。原文把这些作为前提；本轮考察这些前提的标准实现成本。
- AID-Guard，同目录 P05_全文.txt，§II.C TCB（246–255），§IV 假设与 P2 的原生条件沿前轮核读记录。线性化 authority store、rollback-detecting time 和 provider 原生约束需要实例化。上述原文不证明本项目生产配置已经具备相应能力。

## 2. G1：可信当前数据库＋事务＋来源账本＋持久 pending

**适用条件。** 数据库的“可信”包含当前性及恢复保证。若攻击者能回滚数据库全部磁盘而缺少外部锚点，应转入 G2/G3/G5。R 的用户认证、来源接纳和串行化逻辑可信。

**组合。** 用一个事务提交批准变化、预算/消费与 pending；外发前保留原请求摘要。结果归属原请求，重试通过相同键与摘要去重。撤回与接纳共用一个序列化顺序。数据库 WAL/组提交保证 ACK 与恢复的一致边界。

**成本。** 对 b 个提交组，至少有相应逻辑 durable commits；具体引擎每组可能有多次物理写，故只用 `Θ(b)` 描述满足条件的普通组提交上界。业务写入字节为 `O(uℓ)` 加 WAL、索引和复制开销；存储 `O((n+m)ℓ)` 加保留历史。恢复可用最近 checkpoint 加 `d_h` 增量；冷启动完整状态读为 `O((n+m)ℓ+d_h)`，也允许延迟加载。没有协议必要性要求每次完整重读所有审批。撤回 ACK 等待所属组的持久确认；B 可用性取决于数据库和调度。

**当前缺证。** 生产持久状态机、原子接纳、崩溃恢复和真实 ACK/B 时限尚未验收。当前实验日志 flush 不能直接充任这项契约。

## 3. G2：Memoir-Basic、Memoir-Opt 与受保护锚点

**Basic 映射。** R 的纯本地状态转换作为确定性模块请求；认证用户输入和时间等作为明确输入。把 b 个合法提交组编码成 b 个复合状态转换，可沿用相同 ACK 边界。每组保护历史摘要，普通存储保存快照和请求。安全重放重建相同本地结果。

**Basic 成本。** 请求组相关 NVRAM 写 `O(b)`，锚点 `O(λ)` 字节，此外初始化/恢复及底层原子性操作逐项计入；普通快照/WAL、状态读取与 MAC/哈希计费。原论文整状态序列化会有 `O(b|S|)` 的直接版本成本；强对照允许接入成熟增量认证存储，不能把整状态复制当作所有通用方法的下界。

**Opt 成本与界限。** 在可靠 shutdown-checkpoint 合同 C 下，初始化及每次 boot/checkpoint 有常数 NVRAM 写，合计 `O(c+1)`（c 覆盖相应重启），仍有 `O(b)` PCR 历史更新、普通存储及 UPS/SMI/硬件资源。突然破坏性断电绕过 checkpoint 时，guard bit 与 ExtensionSecret 支撑拒绝旧状态；合法 B 的有界恢复需额外保证。不能将该拒绝行为算作模型 O 下的完整活性。

**跨组件义务。** 保护最小语义状态是基线可用优化：可丢缓存和可重建数据分别处理，配额/消费/pending 的安全相关部分需保持。确定性本地重放不能凭空保证原生 refresh 幂等，也不能将未知外部结果重复派发为同一个原生效果。

## 4. G3：在线当前权威、缓存、增量恢复

**最简单组合。** 可信权威持久接受带版本的状态变化。R 在恢复时发送新挑战，核验绑定请求、身份、版本、状态摘要的认证答复，再读普通存储中匹配的状态。更新采用预期版本/CAS 或事务。缓存可减少重复读，但需要单写者持有期、协调的撤回失效通知、租约或接纳点权威验证。

新 nonce 使旧答复无法冒充本次权威答复；当前性来自权威读取其真实当前状态的保证。签名旧状态与 nonce 的组合若由可回滚进程生成，仍缺当前性来源。

**具体强实例 Nimble。** 原文 §3 给出状态签名＋位置、append(expected_index)、read_latest(nonce)，§3.2 已允许普通存储存大状态、账本存摘要并恢复中断 append。多控制器还需正确的应用更新/CAS 与资格消费串行化。账户/任务/代次是已认证业务状态的字段，独立加字段不构成协议创新。

**成本。** 用 `w_N` 表示在线权威更新交互数、`q_N` 表示新鲜读/租约/失效交互数。正常成功路径的简单批量版本有 `w_N=b`；其中 c0 次恢复失去有效缓存时，每次一次新鲜读，恢复部分为 `q_N=c0≤c`。失败重试、日常多写者、租约和失效交互另加，实际总量可高于这些正常路径值。本文未建立通用 `Ω(c)` 下界。摘要版控制消息为 `O((w_N+q_N)λ)` 加业务绑定，状态传输为增量/所需数据大小。

可信数据库权威承担当中的 durable commits。Nimble 原文以 a 个 endorsers 的受保护易失尾部、普通账本存储和多数回执实现：直接计费为 `O(a)` 节点通信/回执验证因子与 `O(aλ)` 尾部可信内存（每 ledger）；初始化、远程证明、重配置、灾难恢复再加。正常核心操作的次数可按 b 和 q_N 计，具体物理通信与存储后端需实例化。多数 endorsers 永久丢失时，原安全身份下恢复活性丧失；可用区/运维和外部灾难 checkpoint 均须计费。

**当前缺证。** 真实权威部署、访问限制、缓存/撤回协调、在线预算及 B 时限未确认。线上调用带来的时间和请求成本属于整个系统账本。

## 5. G4：SUNDR 类历史与分叉一致性

**直接能力。** 签名版本结构、哈希和历史比较可认证客户端所见历史，限制可隐藏的分叉。允许缓存、版本差分和批处理。

**边界及增强。** 在 A 更新后离线、B 随后恢复的例子中，孤立 B 的旧历史可以与未发生更新的世界一致；严格最新撤回仍需可信一致性服务、跨客户端新鲜通信或保护 checkpoint。SUNDR §3.2 已明确给出在线增强路径。增强后成本并入 G3 或 G5。

LCM 使用每客户端常量序号/哈希状态，服务端维护每客户端信息。客户端需持久恢复自身记录；majority stable 与所有客户端最新可见分别定义。强 ACK 若等待稳定，需计入其他客户端的消息、等待和可达条件。该优化只适用于其可信客户端假设可实现的部署。

**资源。** 设 h 为客户端数、v 为改变版本结构数，增量传输可依 v 而非每次全部历史计费。客户端持久状态总量至少按实际各端记录列出；客户端写次数随确认其本地历史的操作数计。本文不对所有 fork-consistency 协议给统一最优阶数。单独 fork consistency 对本轮强当前性合同属于功能不足，增强组合属于条件覆盖。

## 6. G5：认证数据结构、批处理、单调资源

**认证树＋当前根。** 受保护当前根为 `O(λ)` 字节，把 n 项批准和 m 项 pending 放入认证字典；平衡树的单项路径验证/更新为 `O(log N)` 哈希，批量与多重证明可减少共享路径。普通存储保存条目、节点及所需历史。当前根的不可回滚提交、崩溃原子性及获取当前根的成本仍由 G1/G2/G3 承担。哈希树单独认证提交内容，不提供当前根的新鲜性。

**CRISP 的同合同用法。** 允许乐观内部 fsync 及批量计数器更新；应用撤回 ACK 在 Checker 确认保护覆盖之后发出。b 个提交组使用 `O(b)` 计数器更新，`O(u)` 业务变更/哈希工作，实际磁盘写字节按变更集计。恢复验证计数器与认证存储；仅检测到不一致而停机时，还需恢复正确数据才能恢复 B。普通 fsync 早 ACK 的窗口版本单独登记，不能拿其较弱承诺和强候选比较。

**ROTE。** 一次更新将计数器发至 a 个辅助节点，收 echo、返相应 echo、收 quorum final ACK，再封存本地状态；直接实现每组 `O(a)` 认证消息与 counter 元数据量。建立全互联组会话、节点重启和组表读可能有更高通信与状态开销，均单列。原文要求重启时所有辅助节点响应；其可用性边界与采用多数存活的 Nimble 分开。TEE 内存、可信节点及共享命运风险是额外资源。

**REBOUND 的相关内容。** 历史/策略/审计字典共同根＋当前计数器＋事务意图/完成记录已有直接近邻。其允许的策略回滚更宽，本项目只需保存撤回当前状态时可使用更简单状态机。原文恢复政策仍有未解决细节，本轮不给其全面部署充分性背书。Ariadne 双增量规则在该文被引用，本轮只按 REBOUND 的直接描述记录；Ariadne 原文未另行取得，涉及其必要性证明的优先权保持未决。

## 7. 覆盖结论与资格审查

| 设想 | 最强适用组合允许的优化 | 本轮结果 |
|---|---|---|
| 每项撤回独立持久更新太贵 | G1 组提交、G2 合法复合请求、G5 Checker barrier | 可合并合同内已有覆盖；顺序严格 ACK 的下界另见 INPUT_FAMILIES |
| 仅保护少量授权状态以减少可信写 | 认证字典根、最小语义状态、缓存/增量重建 | 既有优化；安全相关消费与 pending 仍计费 |
| 把当前性搬到远端 | G3 认证当前答复、Nimble/ROTE 的具体方案 | 条件覆盖；资源转移完整计入 |
| 签名来源、批准代次和迟到结果 | G1 持久 pending/来源、MAC/签名、精确重试＋G2/G3 当前性 | 条件覆盖；AS/RP 幂等及派生关闭另有前提 |
| 统一历史、策略与当前根 | G5 标准认证结构组合及 REBOUND 直接近邻 | 普通组合主张已覆盖；尚无独立密码增量 |

本轮没有选出存活候选。删除设想中的新增“密码组件”后，上表成熟组合仍能在对应条件合同中完成本地功能；可见的性能变化来自批处理、状态分解或资源转移。未建立超出这些近邻的可证明新权衡。现有数学和 PSCD 资产维持归档，其限定模型最优性独立于此处应用功能。
