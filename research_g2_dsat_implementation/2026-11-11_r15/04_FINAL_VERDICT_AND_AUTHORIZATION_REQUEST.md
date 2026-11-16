# R15最终裁决与授权申请

本轮完成H2_PREFLIGHT_ONLY，工程源码修改、项目测试、进程/数据库/key/真实RPC访问均为0。四份报告和七份主JSON固定实例/身份/秘密/挂载/命令/授权边界，历史材料原字节保持。

**当前可以审批的是最小挂载代码的离线实施范围。P1/P2仍为待补运行目标的模板，真实H2命令尚未存在。** 下一项优先任务为下述A1，符合本轮附件“缺少入口时先最小宿主激活并离线验证”的要求。

## 状态

| 状态 | 实际判定 |
|---|---|
| H1_IMPLEMENTED / H1_SYNTHETIC_TESTS_PASSED | true，继承R14的合成范围 |
| H2_HOST_ACTIVATION_SPEC_READY | true，仅文件/权限/来源/次数和测试规格 |
| H2_INSTANCE_IDENTIFIED / H2_CALLER_IDENTIFIED / H2_SCOPE_LOCKED | false，各字段UNRESOLVED |
| H2_SECRET_BOUNDARY_APPROVED | false，key及整行解码均待独立批准 |
| H2_COMMAND_LOCK_READY | false，actual入口和argv为null |
| H2_ENTRYPOINT_MISSING / H2_RUNTIME_METADATA_PENDING | true |
| P1_READY_FOR_AUTHORIZATION | false，尚无指定运行环境、PID/根目录/元数据范围；模板已备 |
| P2_READY_FOR_AUTHORIZATION | false，入口、实例、身份、scope、解码及命令条件未齐 |
| H2_AUTHORIZATION_PENDING / REAL_AUTHORITY_READ_NOT_RUN | true |
| S3B2_NOT_AUTHORIZED / S5_NOT_AUTHORIZED | true |

CALLER_IDENTITY_UNRESOLVED、READ_SCOPE_UNRESOLVED、TARGET_SCOPE_PENDING、SOURCE_OR_REFINEMENT_GAP、TYPED_O_NOT_IMPLEMENTED和O_REVISION_NOT_IMPLEMENTED持续保留。

## 十四问

| 问题 | 回答 |
|---|---|
| Q1 H1如何挂载serve？ | Store构造成功后、Handler形成前，将同一Store引用交受信Registration工厂；注册无SQL/key，专用RPC分支直接使用认证identity。部署启动仍有独立副作用。 |
| Q2 为什么合成注册不能直用？ | H1限定SYNTHETIC_ONLY，来源身份是宿主前提，SQL计数固定0；许可只限单permit，实际实例/权限/key/全局次数尚缺。 |
| Q3 最小文件？ | 两个现有文件services.py和H1 host受控修改；新增activation模块、最小client、新测试/runner和fixture子树，共七目标。storage/R12/protocol/migration保持。 |
| Q4 可复用真实入口？ | 有内部read_state和旧recover，但缺适配的scope/身份/挂载；没有安全可执行H2触发入口。选复用RPC骨架的新专用分支，绕开旧call。 |
| Q5 实例如何唯一认证？ | 未来绑定已批OS/部署身份、PID/创建时点/新epoch、加载版本、DB位置及文件/连接观察；目前全部运行值未取得。持久DB genesis身份仍缺，authority_instance保持null。 |
| Q6 谁读取什么？ | 管理actor和独立staging_read_metadata/历史读取权、精确scope/grant/rid均未指定；不选择生产账户。 |
| Q7 key/解码授权？ | 指定现有Authority进程对既有key文件至多一次读取尝试，并显式批准整行瞬时解码；全状态只留Authority域。少量输出不自动授予该权。 |
| Q8 费用如何计入？ | primary一次世界SELECT和同语句Schema元数据观察、operations最多+1、key/decode各≤1；票据/客户端凭据/日志/网络/锁/内存另计。启动不并入P2。 |
| Q9 单次许可额外保证？ | P2会话级总槽，所有新permit共用；绑定当前进程epoch和授权ID；错误/超时不rearm；重启后旧授权失效并重新审批。 |
| Q10 无额外读取如何验证？ | 固定无DML路径、同连接total_changes属性前后值及源计量；只核调用自身无写入。独立前后世界hash仍未知；额外读需单独4语句预算。 |
| Q11 精确真实命令存在？ | 否。command_executable=false、H2_ENTRYPOINT_MISSING；argv=null。候选client文件尚未创建，现有cli参数不冒用。 |
| Q12 最小下一动作？ | A1七目标离线实施/验收；20项新用例＋原H1 24项必要回归，均先取得独立批准。 |
| Q13 能否申请P1/P2？ | 当前仅提供模板。P1须先指定环境/PID/元数据文件；P2须全部12门齐备。现阶段优先A1，实际运行接触仍关闭。 |
| Q14 独立门？ | B2持久typed O/o/CAS/迁移/旧writer覆盖，S5原生实验和全源/持续失活/后代/接受路径/AS异步/COMPLETE条件全部保持。 |

## A1最小离线实施申请（当前approved=false）

> 我批准R15七目标的最小宿主挂载代码开发和离线验证：仅修改D:\毕业设计\auth-lifecycle下的src\auth_lifecycle\online_state\services.py、src\auth_lifecycle\online_state\dsat_authority_read_host.py；仅新增src\auth_lifecycle\online_state\dsat_authority_host_activation.py、scripts\read_dsat_authority_once.py、tests\test_dsat_authority_host_activation.py、scripts\run_dsat_authority_activation_tests.py及tests\fixtures\dsat_authority_host_activation\。实现默认关闭的Authority内部注册/专用RPC分支、受信来源对象、一次H2会话总量门、精确tuple/grant/rid核验、有界单SELECT reader与最小管理client；真实实例、配置、凭据和P2票据仅使用合成替身。允许标准库SQLite仅在专门`:memory:`连接中核固定SQL，最多32个自有连接，禁止ATTACH、文件库、扩展加载和真实key；codec采用合成spy，既有服务/Store/EventLog/Controller/Provider构造均禁用。仅运行新A01–A20及原H01–H24必要回归，使用新限定runner和既有隔离Python/-B，无依赖安装。修改前按R15 SOURCE_LOCK保存两份旧源码快照，新基准明确登记获准修改路径，历史R13/R14的锁、批准、源码快照和结果保持原字节。旧R14 runner及其旧预检保持原样；原H1测试类由新runner受控加载，不能靠改旧锁使其通过。结果仅写入新的A1离线输出根，每run新建，保留失败/修复，单轮120秒软预算。storage.py、protocol.py、R12/migration/S1/S2/S3-A和旧测试源码保持原字节。禁止服务启动/部署/重启、运行目录/真实配置/数据库/key/账号访问、真实RPC、B2、S5和旧115/46/33或整仓测试；任何扩大范围单独申请。

拟议离线runner路径和命令在H2_HOST_ACTIVATION_PLAN/H2_AUTHORIZATION_REQUEST冻结，当前脚本尚未存在，未执行。允许`:memory:`SQLite是这个新申请的明确范围，原H1禁SQLite结论和旧运行记录保持。

### A1冻结验收责任

A01关闭注册零I/O；A02绑定Store/lock/connection；A03正文/字符串无法发行Registration；A04原合成兼容及裸LOCAL拒绝；A05真实Handler认证上下文的替身转交；A06旧controller/Agent默认拒绝；A07精确scope/grant/rid；A08当前票据/权限/有效期；A09不同permit及并发共用总槽；A10重启/epoch旧授权失效；A11界内SQL/codec等价；A12越界/缺行/Schema拒绝在key前；A13活动事务/回调重入拒绝；A14日志/key/decode/返回失败保留费用；A15无DML/旧dispatcher/原分派语义；A16全部秘密sink；A17挂载定义不启动服务；A18客户端一次调用/严格argv/无Laboratory；A19全部元数据/额度/日志成本与无自动rearm；A20未知/Native缺口及出域权限复核。

内存SQLite验证只承担SQL与接口责任；真实WAL、ACL、实际AES-GCM/key域和生产认证仍待运行取证。原H1 24项是独立回归分母，不能合并成“44个新用例”。

## P1与P2模板

**P1a元数据**：研究者指定一个环境、一个PID及少量批准的非秘密元数据文件后，核进程身份/创建时点/可执行位置、endpoint所属、加载部署记录、规范DB/key引用及挂载状态。禁止扫描全系统、读取完整命令行/环境变量/secure配置/凭据；当前未提供目标，实际命令为null。

**P1b可选Schema/WAL核验**：如非秘密启动记录不足，另批一个指定DB的只读元数据连接，最多PRAGMA user_version/journal_mode两条查询，世界行SELECT/key/解密0。须审WAL/SHM/权限与文件副作用；不使用immutable或自动初始化。此许可不自动随P1a获得。

**P2**：实例、主体、scope、DB、key/整行解码、入口、无占位符命令、会话预算、输出/日志、停止条件、运行版本12门齐备后，独立申请03稿primary一次读。完整数据和摘要仍限指定管理域。

实际部署/配置更新/重启另需生命周期授权：serve原构造器的PRAGMA、marker/config/日志和状态行存在性查询均单列，Schema2与已存在状态未能保证时停止。A1、P1和P2各自都不自动包含部署激活。

当前H1解释器环境未发现常规cryptography包目录，实际导入未测。A1保持无安装，纯activation核心/替身及`:memory:`SQL可以验证；services挂载点只作AST核对，禁止导入services/storage/materials或伪造密码学模块。实际服务导入/加载与运行环境精化仍是后继明确缺项。新A1 runner受控加载原H1测试类，使用独立授权的两文件修改映射核当前代码和旧版本快照；旧R14锁和runner保持原样。

## 唯一下一项动作

**审定并独立批准上述A1七目标、20新项＋24原H1回归的离线实施范围。** 成功将消除入口代码、真实注册接口和会话一读的工程缺口，随后仍需指定环境并完成部署/P1，再锁P2。若单读、权限、无秘密或总量门验证失败，修复或收缩挂载，维持P2阻塞。

本轮源码、历史和旧执行结果保持原字节。成熟接线工程与A/B/AB创新性分别管理，外部安全复核待取得。
