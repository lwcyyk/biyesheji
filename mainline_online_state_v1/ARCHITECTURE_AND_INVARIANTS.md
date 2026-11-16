# ONLINE_TRUSTED_STATE_V1 工程实例

本轮实例化已确认的 G1/G3 组合。运行入口为 `auth-lifecycle/scripts/online_state.py`，运行层位于 `src/auth_lifecycle/online_state/`。密码学辅助线状态为 FROZEN。本轮新增的是成熟组件的集成与有限恢复验证。

## 入口映射与选型

| 层次 | 入口 | 实际责任 |
|---|---|---|
| L0 有界控制 | BoundedController.step | 有限知识状态、剩余步数和参考检查 |
| 实验批准/预算 | experiment.journal.Gate.call | 既有实验方法批准、请求计数与未知结果记录 |
| 原生适配 | experiment.providers.Casdoor/Keycloak | 既有原生调用，本轮执行次数为 0 |
| 持久运行层 | online_state.services.Controller.call | 调用者鉴别后的句柄请求、批准、派发、返回、撤回及恢复 |
| 当前状态权威 | online_state.storage.AuthorityStore.call | 原子事务、预算、pending、来源和材料持久登记 |
| 假 provider | online_state.services.FakeProvider | 合成材料、持久效果、受控迟到与精确结果查询 |
| 本地验收 | online_state.acceptance | 真进程故障、单活重启和限额执行 |
| 独立评分 | scripts/score_online_state.py | 独立读取 SQL/效果证据，核对不变量与秘密交付 |

本机可用 Python 3.12.14、SQLite 3.53.1、cryptography 50.0.2。PostgreSQL 工具未出现在所查 PATH，Docker daemon pipe 不可用。本轮选用独立进程托管 SQLite，并以 TLS RPC 暴露受限的事务方法。环境锁给出实际版本、配置与源码哈希。该选型适合两任务的小规模原型。

## 进程、目录与信任

每条轨迹有三个服务进程和一个运行者进程。评分器在服务退出以后启动，采用独立读路径。

| 目录 | 内容 | 故障与权限 |
|---|---|---|
| secure/ | AES 密钥、TLS 私钥、服务能力凭据、controller.lock | Windows DACL 授予当前测试用户和 SYSTEM。控制器回滚范围之外 |
| authority/ | SQLite DB、WAL、事务事件、数据库操作日志 | 权威进程独占应用连接，控制器通过 RPC 访问 |
| provider/ | 加密结果、效果真值 | 假 provider 持久保存。运行者通过已知尝试的 lookup 接口取得结果 |
| cache/view.json | 仅供展示的版本/数量提示 | 唯一被旧快照恢复覆盖的文件，恢复入口始终查询权威 |
| controller/ | 安全投影日志与故障屏障 | 原始材料只在可信进程内存中使用 |
| runner/ | 合同可见调用与结果 | 运行者按预定场景执行，额外真值不进入决策 |
| scorer/ | 离线检查结果及访问路径 | 可读取权威密文和私钥、provider 真值/加密结果，权限用途明确登记 |

同机、同一可信 OS 用户是本轮的实验前提。HTTP 层将用户、agentA、agentB、controller、adapter 和故障夹具分别绑定高熵能力凭据。R 根据凭据派生 caller，代理正文只能提交句柄和用途字段。进程代码与故障夹具可信。恶意同 OS 用户、主机管理员、硬件失效和权威自身恶意回滚的部署验证另行登记。

所有出站 RPC 使用固定的 127.0.0.1 随机测试端口、固定证书信任和 TLS。环境代理和重定向关闭。原生测试端口被客户端拒绝。原生 Casdoor/Keycloak 适配器未进入本轮服务入口。

单活由 secure/controller.lock 的 OS 文件锁控制，进程死亡释放该锁。恢复程序先 kill 并 wait 旧活动进程，再启动新进程。缓存恢复仅写经过路径范围校验的 cache/view.json。多主机多活需要进一步的接纳者协调合同。

## 事务、迁移与秘密存储

迁移文件为 online_state/migration.sql，user_version 为 1。数据库有一行 AES-GCM 加密应用状态，以及独立的安全投影事件表。应用状态包括 grants、requests、grant_ops、revoke_ops。应用变化和事件在同一事务提交。

每次写使用 `BEGIN IMMEDIATE`，服务内 RLock 串行化访问。连接启用 WAL、synchronous=FULL、busy_timeout=5000、wal_autocheckpoint=1000，并读回关键配置。恢复通过一个 SELECT 读取完整状态快照。不同阶段的状态变更依据事务 version 排序，客户端时间只用于其可观察的延迟。

AES-256-GCM 使用每次新生成的 96 位 nonce，AAD 固定到 schema-1。密钥在独立 secure 目录，每次状态解密重新读取。缺少密钥、无效密文或已有权威状态缺失均保留失败/UNKNOWN。初始化标记阻止既有数据库消失后静默创建空状态。已有更高 schema 版本会拒绝加载。

该原型每次提交序列化完整应用状态，时间与写入量随状态大小增长。它提供一个清晰的事务基线，后续可按真实规模采用行级存储和成熟索引优化。其成本全部登记。

## 请求与预算语义

代理请求的精确字段为 rid、handle、task、account、audience、generation、operation、payload。payload 在本轮只接受一个有界整数 value。标识符使用长度受限的 ASCII 集合，拒绝重复 JSON 键、未知字段、浮点、布尔替代整数和非有限数。摘要覆盖由认证夹具确定的 caller 与完整规范化请求，采用排序键、无空白、ASCII JSON 和 SHA-256。

批准绑定 caller、task、account、audience、generation、允许操作集合和总预算。新批准产生独立 grant_id/handle。approval_op 的同正文重试返回原批准收据，并维持权威中的当前有效性。相同来源代次的重复创建产生冲突。

| 请求阶段 | 预算 | 外部效果责任 |
|---|---|---|
| QUEUED | reserved 加 1 | 尚未放行，可安全取消 |
| DISPATCHED_UNKNOWN | reserved 减 1，spent 加 1 | 已持久放行，可能产生外部效果 |
| RESULT_AVAILABLE | spent 保留 | 已登记且当前批准有效的结果 |
| QUARANTINED | spent 保留 | 原批准撤回后的结果，仍保留原生处置义务 |
| CANCELLED | 释放 QUEUED 的 reserved | 确定未放行的取消项 |

相同 rid 与正文返回已有状态。不同正文或 caller 使用同一 rid 产生冲突。已放行请求的重复调用返回现存状态，外发路径只在 QUEUED→DISPATCHED_UNKNOWN 的事务第一次返回 send=true 时执行。数据库提交与发送之间的崩溃因此留下未知义务。当前假 provider 的 perform 每次都记录效果，评分器能识别意外重复外发。

## 撤回、返回与恢复

撤回事务把批准置为撤回、取消其 QUEUED 项并隔离已有结果，然后提交 `LOCAL_REVOKE_COMMITTED` 收据。revoke_op 保留原始 commit_version，同操作标识重试可查询原提交结果，正文冲突产生拒绝。

放行先于撤回时，调用属于在途范围，可能在 ACK 后到达 provider。放行后预算与原来源持续保存。撤回先于放行时，当前批准检查阻止新放行。两者以权威事务序列为依据。

结果绑定 rid、请求摘要、完整 origin、attempt_id 和 release_version。材料登记与结果摘要在一个事务内完成。同结果重试幂等，不同结果产生冲突。迟到 A 结果保持 g0 来源，B.g1 独立授权 B 请求。假 provider 的 lookup 只返回已登记尝试的确定结果，缺少结果时返回 UNKNOWN，运行者不会据此自动认定无效果。

正常与管理接口均返回明确投影。原生材料只出现在批准的可信输入、权威加密状态、可信适配器内存、假 provider 加密结果和对应 TLS 传输中。未知 provider 扩展字段不会进入业务输出。日志保存状态、版本、标识、字节数和耗时，异常返回固定错误类型。

恢复先取得权威当前状态和必要密钥。缓存快照不授予调用资格。权威不可达或密钥不可用时返回 UNKNOWN。条件恢复后，B 可继续执行，即使 A 仍有独立未知或隔离义务。

## 核对的不变量与边界

1. 已承诺撤回后，同批准没有新的派发放行。
2. reserved 与 QUEUED 数量一致，spent 与已放行数量一致，合计受批准预算约束。
3. rid 正文唯一，原请求来源与返回来源一致。
4. 任一 provider 效果对应持久放行和相同尝试，未知请求保持一次外发。
5. 重复返回与状态登记中途失败维持事务一致性。
6. 旧缓存恢复使用当前权威状态，单活实例按退出/启动顺序切换。
7. B 的独立合法恢复与 A 的未决责任分别保留。
8. 公共日志、错误和管理投影通过已知合成秘密的扫描。

独立评分器直接读取 SQLite 与 provider 记录，未导入运行层模块。它复核提交序列、预算、摘要、来源、效果次数、B 完成、进程退出及秘密交付。开发测试包含合法正例和篡改来源负例。该独立性属于实现/读取路径的独立，尚无外部独立审稿。

M1 验证同机进程终止、权威进程短暂不可达和单文件旧缓存恢复。主机断电、磁盘损坏、权威数据回滚、跨主机身份与网络故障、真实代理权限隔离、真实 AS/RP 关闭均保留相应验收项。密码学创新与形式化一般证明另有证据门。
