# 初始化、TLS 与资源预算

全部数值为未来申请上限或静态调用推导。实际费用 NOT_MEASURED，D1-B1/D1-B2 全部 NOT_RUN。完整路径、资源与费用字段在 `D1B_RESOURCE_BUDGET.json`。

## 新实例准备与跨文件发布

本实例只使用已确认的一个 grant 和一个 QUEUED issue。scope、请求规范化和 digest 复用 R19 已读规则，handle/material 重新生成专用合成值。limit=1、reserved=1、spent=0，attempt/release/result 为空。历史两行明确标记 synthetic preparation，保留它与实际 AS 发行或正常业务事件历史的区别。

按以下顺序准备：

1. 验证批准 source/config/OS/父目录，独占新根及实例锁；先记录创建意图与 UUID。
2. 建立私有目录、源快照、配置和所有权记录；已有目标保持原样并安全停止。
3. 生成新的 32 字节 state key，独占写入、flush/readback 一次后用于一次 AES-GCM 加密；生成独立 TLS key/certificate。秘密值只存在受控内存和 private 文件。
4. 规范 seed 在内存构造，以既有 nonce12/ciphertext+tag 和 schema-1 AAD 加密。新 SQLite 两表按 Schema2 准备。
5. DB 事务提交后，持久发布 seed receipt，再进入 SEED_READY。键、数据库和 JSON 文件无法构成同一个 SQLite 原子事务；中途失败保留 pending 状态，进入 RECOVERY_REQUIRED。
6. 另一次有界 start 操作消费启动许可，创建唯一子进程；子进程严格打开预置 Schema2，构造 Store 一次、绑定 Dormant、加载 TLS、创建 listener。

`authority/initialized` 是现有 Store marker，单独存在时无法证明整个部署成功。外层 `config/initialization_receipt.json`、生命周期与实际文件身份共同约束后续启动。新 strict ctor 拒绝 schema 0/1、缺少状态行和 genesis/migration 回退。

## SQLite 完整调用计费

初始化连接 1，Store 连接 1；初始化连接关闭后才创建 Store，最大同时连接 1。准备器显式事务 1。

| 次序 | 初始化调用 |
|---:|---|
| 1–2 | `PRAGMA page_size=4096`；读取有效 page_size |
| 3 | `PRAGMA max_page_count=2048` |
| 4 | `PRAGMA journal_mode=DELETE`，核对返回 |
| 5–6 | `PRAGMA synchronous=FULL`；读取有效 synchronous |
| 7 | `PRAGMA busy_timeout=0` |
| 8 | `BEGIN IMMEDIATE` |
| 9–10 | 创建 authority_state 与 authority_events，列定义采用既有 Schema |
| 11 | `PRAGMA user_version=2` |
| 12 | 插入唯一 version2 加密 state 行 |
| 13–14 | 分别插入两条明确标记的合成准备事件 |
| 15 | `COMMIT` |

未来 strict Store 正常路径 7 次：user_version 先读且必须为 2；journal_mode=WAL；synchronous=FULL；读取 synchronous；busy_timeout=5000；wal_autocheckpoint=1000；只读 `SELECT version FROM authority_state WHERE id=1`。这是对当前 ctor 的局部重排，保证严格检查在库配置修改之前。原默认路径和业务方法保持。

正常合计 **22 次 SQL wrapper 调用**，失败清理至多申请一次 rollback，因此全路径上限申请 **23 次**。事务失败路径和构造失败路径相互按实际阶段计费，重复清理不再次执行 rollback。构造后禁止业务分派，P2=0，故无后续世界状态 SELECT、解密或应用 DML。

上述包含新库有界元数据与写入。独立 P1b 两 PRAGMA 查询保持未授权，本轮无法用启动预算额外执行 P1b。Store 的版本列查询也按一次实际 SQL 计费。

内部 SQLite journal/WAL/SHM 创建、fsync、自动 checkpoint 与关闭时写入属于 VFS 行为，其次数/字节 NOT_MEASURED。显式事务数无法替代内部事务/锁次数。保留三个允许伴随路径，禁止主动删除 WAL/SHM 或通过手动 checkpoint 修复。

## 目录、文件与持久资源

固定目录 14 个，包括根及 config/authority/secure/logs/runtime/evidence/tmp/control/artifacts 和固定源子目录。父目录 `D:\毕业设计\h2_test_runtime` 若缺失，B2 申请中额外允许创建一次并设置可信 DACL；停止后保留。

固定持久文件最多 26、源文件最多 64、SQLite 伴随文件至多 3、同时临时文件至多 3，根内最大路径数申请为 **96**。具体文件名已经逐项列入 JSON。源清单超出 64 文件或 2 MiB 时，停止并修订申请。

正常停止保留数据库、密钥、配置、源码快照和审计。自动删除仅限确证为本次创建、已经关闭的白名单临时文件，至多 3 个；持久文件自动删除额为 0。外部失败证据目录另申请至多 4 文件、1 MiB，避免根内日志故障时证据完全失落。

数据库初始化 page 上限对应逻辑 DB 8 MiB，单 state ciphertext 至多 16 KiB；全套逻辑内容预算 16 MiB。该预算用于有界输入和写入接纳。磁盘实际分配、SQLite 写放大及操作系统 I/O 另行计量；当前文稿没有给出未实现的硬磁盘配额保证。

## 秘密与恢复

state key 生成/写入/readback 各一次，AES 加密一次、解密零次；Store 预置路径 cipher 调用零次。TLS 申请一个新 RSA2048 key、一个签名证书及一次 `SSLContext.load_cert_chain`。OpenSSL 内部文件读取、密钥副本和内核 I/O 次数须实测，应用调用次数单列。

Python 与 OpenSSL 无法保证所有秘密副本被安全擦除。实现责任为缩短明文存活、去除不必要引用、关闭文件和进程，日志始终只含用途引用/错误类别。密钥原值、密钥 hash、PEM 私钥和完整 state 均排除在公开证据之外。

密钥已落盘而 DB 初始化失败时保留 private 材料与 pending 记录；禁止自动重新生成并覆盖。正常停止保留 key。首轮 recover 仅按受信来源、文件 ID、长度/用途记录分类，**不加载 state key、不查询 DB、不解密**。因此恢复后“密码学验证 key 与 DB 内容匹配”继续登记未验证；需要该结论时，另行申请明确的验证读取预算。该限制防止恢复入口吸收 P2 责任。

## TLS、RPC 与线程预算

证书为新本地测试证书，SAN 包含 IP `127.0.0.1`，有效期至多 24h，客户端只信任该私有测试证书；系统信任库修改额 0。固定 endpoint 使用 IP 地址，证书与 URL 地址必须一致。TLS 最低 1.2，加载证书成功后才 bind，冲突立即停止。

bootstrap 配置 `identities={}`、`permissions={}`，管理身份只保留逻辑 scope 名称；本阶段可用管理 token 数为 0。TLS 提供服务端通道身份，RPC 权限仍在独立默认拒绝门。测试的一条业务请求在 Store 分派之前拒绝。OS 受控 stop Event 承担停止通知，HTTP 暂无管理激活操作。

live 分支拟采用同步 `HTTPServer` 有界轮询，应用工作线程 1；原 ThreadingHTTPServer 默认路径保留。标准库/原生库额外 OS 线程若出现，必须作为实测事实登记，当前 application-thread 上限无法替代整个 OS 线程数证明。

固定 listener bind/listen 各一次、连接 accept 总上限 3、同时 accepted 连接 1、部署方客户端连接至多 2、HTTP 请求至多 2。TLS handshake 和请求分别至多 2s；接受的 socket 立即登记拥有权，再执行带超时的 TLS handshake。请求体至多 1024B、响应至多 4096B，限制头部大小/头部读取时间并拒绝 keep-alive 无限复用。无 controller/provider/native 连接。

Windows live factory 必须在 bind 前设置 `SO_EXCLUSIVEADDRUSE`，关闭 `allow_reuse_address`。平台无法提供该合同则拒绝启动。总连接额包含外部到达的连接；本地恶意请求可能耗尽额度，当前承诺为安全关闭，服务可用性在该攻击条件下保持待研究。

服务 lease 至多 60s，启动 Ready 窗口 10s，停止窗口 5s，完整 B2 回合至多 120s。新启动自动重试 0。预算耗尽或日志错误触发关闭接纳与清理，无法确认完全停止时报告 RECOVERY_REQUIRED。

这些时间是受控API及观察的deadline。底层文件系统阻塞或不可中断I/O可能超时；默认强制终止额0，因此实际进程退出时间需要实测，无法承诺任意故障下硬限时退出。超时记录保留UNKNOWN/RECOVERY_REQUIRED，锁和资源归属继续按实际事实处理。

## 日志和成本

结构化逻辑 append 申请最多 170 次：lifecycle32＋ownership128＋database_ops8＋transport2；单条最多 2048B，合计预算 512KiB，stdout/stderr 各至多 64KiB。bounded sink 必须在调用 EventLog.emit 前检查计数与字段，外部 traceback 默认只保留固定类别。源代码中的旧 EventLog 自身没有这些全部预算，需要新 owned wrapper 承担 live 限额。

所有成本类别、attempt/success 和失败损失分别计量：preflight/source/identity/initialize/database/Store/key/TLS/host/listener/logging/shutdown/recovery/cleanup/retry。C_initialize 与 C_initialization 为别名，C_host 与 C_host_registration 为别名，listener 是 network 子项。汇总避免重复求和；R19 耗时仅作为历史离线事实。

JSON的 `phase_accounting` 对每个阶段分别列出最大操作、最坏持久资源、潜在失败损失及计量方式。源验证包含至多两遍摘要核对及一次复制读取，有限源清单在B1后冻结，读取费用完整计入。
