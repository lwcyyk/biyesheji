# 最小代码实施、测试与命令规格

本轮工程修改、项目测试与部署均为 0。以下是待独立批准的 D1-B1 范围。函数名为拟议接口，当前原码中缺失的入口一律登记 ENTRYPOINT_NOT_IMPLEMENTED。

## 九个精确逻辑目标

| 目标 | 动作 | 最小责任 |
|---|---|---|
| `src/auth_lifecycle/online_state/services.py` | 修改 | 保留原默认/offline路径；为LiveContext增加受控分支和延迟bind的同步listener工厂；统一全阶段资源所有权 |
| `src/auth_lifecycle/online_state/storage.py` | 修改 | 可选 bootstrap_context，strict Schema2、ctor连接即时登记/异常关闭、有界metrics；默认路径与业务方法保持 |
| `scripts/run_h2_authority_service.py` | 修改 | 保留现offline argv；实现六操作及受控内部child入口，生产导入置于接纳之后 |
| `src/auth_lifecycle/online_state/dsat_authority_live.py` | 新增 | 部署issuer、opaque LiveContext、source/OS/epoch绑定、Dormant固定拒绝 |
| `src/auth_lifecycle/online_state/dsat_authority_lifecycle.py` | 新增 | 所有权栈、seed初始化、阶段账本、start/stop/recover、计费 |
| `src/auth_lifecycle/online_state/dsat_windows_runtime.py` | 新增 | 惰性Win32 self/child句柄、SID/DACL/file-ID、独占锁、显式句柄交接与stop Event |
| `tests/test_dsat_authority_live_lifecycle.py` | 新增 | 新52项测试 |
| `scripts/run_dsat_authority_live_lifecycle_tests.py` | 新增 | 新runner、分域旧类兼容、独立源码差异映射和输出防护 |
| `tests/fixtures/dsat_authority_live_lifecycle/` | 新增子树 | 新合成合同/故障输入与公开向量 |

这对应 3 个既有文件修改、5 个新增 Python 文件、1 个新 fixture 树。逐文件原 SHA、目标函数、测试责任见 `D1B_SOURCE_AND_FILE_LOCK.json`。变更前保存原字节，新差异映射写入新记录。超出九目标时停止该增量并申请补充范围。

R19 `dsat_authority_runtime.py`、现 P1a inspector、R16 A1、H1、protocol/materials、旧测试和 migration 保持原字节。P2的真实管理接纳和激活 API 延期，当前live issuer只承担部署身份。原 `AuthorityStore` 的 grant/admit/release/record/recover 等业务方法不纳入本次变更。

## 接口与依赖方向

launcher 严格解析操作 → 核验独立批准来源与预期 source/config → Windows provider 获取自身/拥有对象的事实 → lifecycle 持有资源 → LiveDeploymentIssuer 创建部署context → strict Store构造一次 → Dormant绑定 → bounded TLS listener → 有界退出。

准备器可以复用 R19 规范 seed 构造、既有 canonical/digest/AAD/Schema 列定义；文件 SQLite 与新 key/TLS 准备使用新的明确代码。`lab.initialize`、`Laboratory`、旧 `cli init/serve` 和旧 stop/kill 均不作后门调用。生产模块的 import 与真实资源动作分别纳入审计。

## D1-B1测试：计划120项，当前执行0

新增 **52项**：F01–F28对应完整故障矩阵，T29–T52覆盖入口/权限、来源/OS、SQL与预算、句柄交接、TLS决策、清理、stop/recover、会话/epoch、兼容和秘密输出。

另外原 R19 24 项及 A1/H1 44 项复用原测试类，共计划 120 项。它们的历史分母、测试文件和旧runner保持。新runner使用独立来源锁和获准差异映射，避免修改旧SOURCE_LOCK或让旧预检接受未经解释的storage变更。

| suite域 | 拟用解释器 | 资源域 |
|---|---|---|
| new52 | 已确认base Python | 新临时合成文件/SQLite/Win32替身或拥有对象；网络0 |
| r19_24 | 同base Python | 原公开AES向量＋受控内存SQLite；services仅AST |
| legacy44 | 既有R07隔离venv Python | 保持原A17无crypto/services/storage/materials导入断言 |

专用输出候选：`D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r21_d1b1_offline`。此路径当前未创建。每次suite输出独立目录，保留所有失败、argv、输入/源码哈希与版本。

new52每次调用申请最多64个测试子目录、512个测试文件、64MiB输出；文件SQLite连接总额104、内存连接16、每case至多2。公开AES测试向量可写入明确拥有的测试文件；另申请至多2个临时测试state key、2套临时测试TLS key/certificate及2次SSLContext加载，用于核验已有crypto/x509/SSL文件兼容性。它们限专用输出树private子目录，真实服务密钥生成保持0，bind/accept/handshake使用替身且实际socket额0。临时测试密钥只作测试输入，日志不输出原值，失败时保留受限private证据。

Windows适配测试允许对自身及最多8次拥有的合成stub子进程查询SID/创建时点/image、使用新临时文件DACL/文件ID/锁/Event。子进程同时至多2、单个10s、aggregate等待预算60s；应用测试线程同时至多4、总创建16。后台stub隐藏窗口，严格命令和输出路径，网络0，无真实Authority角色。测试本身使用真实Win32锁/句柄能力时须显式记录证据范围。

每suite软时限300s，最多申请一次范围内修复重跑，三域完整调用总额最多6次；每次预算独立计，所有记录追加。R19域内存连接额8，legacy域32。预算耗尽或出现部署根/服务/网络访问立即停止，保留失败证据。

若全部获准修复重跑额度均使用，累计stub子进程上限16次、文件SQLite连接208次、三域内存连接分别32/16/64次，临时测试state key/TLS key-cert/SSLContext加载各4次；六次suite输出统一上限384MiB。每次预算与累计预算同时检查。

上述全部属于待批B1测试权限。它没有包含部署根创建、真实服务、P1/P2、S3-B2或S5。

## D1-B2验收：计划12项，当前执行0

B201–B212覆盖新根与source、指定SID与实例、初始化预算、新key/TLS/seed来源、单回环TLS、Dormant和一次被拒绝请求、单Store/epoch、最小Ready凭据、graceful stop、零越界访问、日志计费和完整运行记录。

实际部署仅申请一次新实例初始化与启动、至多2个TLS客户端连接和一次受拒绝业务请求、随后安全停止。B1的28故障注入留在隔离测试域；B2无真实破坏性故障注入。P2总量门在B2只验证默认关闭和源读0；真实一次读的运行验收属于随后独立P2。

部署最小Ready/退出凭据只验证自身拥有子进程的生命周期和受限TLS接纳。它不替代P1a外部进程/来源/endpoint完整核验。P1a/P1b/P2均继续独立。

## 六操作命令合同

| 语义操作 | 目标与副作用 | 未来成功判断 |
|---|---|---|
| prepare | 已批 source/config/OS检查、独占新根/源快照，数据库/key/socket0 | 新根所有权和来源记录完整 |
| initialize | 新私有key/TLS、一次加密seed事务；Store/socket0 | DB提交和seed receipt完整，进入SEED_READY |
| start | 持锁claim一次许可、唯一owned child、新epoch、Store/Dormant/TLS | child精确句柄与有限Ready/TLS事实；启动次数1 |
| status | 只读自身状态记录 | 附观察时点的record结果；缺信息UNKNOWN，不声称活体证明 |
| stop | 精确实例/epoch stop Event，等待退出，持久数据保留 | exact child退出和stop receipt；超时RECOVERY_REQUIRED |
| recover | 静态所有权/阶段分类 | 有限诊断；SQL/key/decrypt/repair/start0 |

拟议入口由已确认Python、审查后的 `scripts/run_h2_authority_service.py` 以及独立operation/approval manifest组成。操作、manifest、approval_ref和result采用严格参数合同；root/port/scope来自批准记录，CLI无法扩大。prepare之后的操作应使用固定artifact脚本与源码摘要，禁止工作区漂移。

当前脚本只支持 `--manifest PATH [--mode offline]`，六操作parser及内部child入口尚未实现。`D1B_COMMAND_LOCK.json` 对每项保存拟议参数Schema、具体脚本候选、固定根/端口、次数/时限和拒绝原因；**actual_argv=null、command_executable=false、blocker=ENTRYPOINT_NOT_IMPLEMENTED**。本稿未给出可被误运行的虚构启动命令。

B1完成后才依据真实parser与源码生成准确start/stop/recover argv，填入新的批准来源、SID、source/config摘要及全部I/O预算。服务身份、TLS引用和父子进程继承handle清单必须同时固定；未经支持的参数不能通过命令锁获得权限。
