# H2宿主挂载与身份

## 1. 实际生命周期及缺口

`services.serve`先读取角色secure配置并创建transport EventLog；Authority分支构造Store；随后建立Handler、ThreadingHTTPServer、TLS、ready文件并进入serve_forever。[C02:277–349] Store引用保存在serve的局部变量implementation中。

Store构造本身会mkdir、打开rw连接、设置WAL/PRAGMA、可能migration/genesis，并写marker/config。[C01:47–91] **注册H2组件应在已有Store构造成功之后、Handler闭包形成之前完成，接收同一对象引用；注册阶段源SQL/key/read_state调用数均为0。**

现有Controller持有Client而非Store。Controller构造自动recover，写日志/缓存；cli.request构造Laboratory并加载多角色配置。它们的原生命周期不能直接作为首次H2执行命令。[C02:42–79；C07；C04:105–125]

将新代码部署到现有Authority通常需要独立的服务生命周期操作。当前进程没有热挂载入口，本方案不使用调试器注入。**离线激活代码通过、部署/重启获批、P1运行取证和P2一次读，分别推进。** 新增注册函数自身无初始化副作用，不代表整个serve启动无副作用。实际部署只面向已存在且确认Schema2/marker/状态行的测试库；若无法排除自动迁移或genesis，部署激活保持阻塞。相关启动SQL/文件写入不能并入P2的一读许可。

## 2. 三路线比较与唯一选择

| 路线 | 结果 |
|---|---|
| A：扩展旧recover/call | recover旧投影缺原请求校验材料；普通call会统一更新a/event。需改变旧响应和分派语义，未选择。 |
| B：新独立管理服务/监听器 | 增加进程、秘密配置和生命周期，超出首次最小目标，未选择。 |
| **C：复用既有TLS/Bearer/RPC骨架与R12适配器** | 在Authority Handler加专用只读分支，直接传认证身份给受限内部宿主；保持旧分派不变。唯一推荐。 |

专用分支操作名沿用H1的`staging_read_metadata`，在旧`implementation.call`之前路由。它只接受独立配置的最小管理读取身份；现有广权限controller token和Agent身份默认无该operation许可。管理身份的配置名仅为拟议角色，实际值未取得。

## 3. 调用图与逐节点责任

| 节点 / 源码 | 输入、身份及权限 | 秘密 / 副作用 / 状态 |
|---|---|---|
| 当前Controller.Client [C02:48–56] | controller服务级Bearer；原用户身份只在Controller内部可见 | 持服务token；旧RPC、日志；已存在，尚无H2转发 |
| 既有Client [C03:106–144] | 受信loopback TLS、配置Bearer、operation/payload | 内存持token；TLS/network；可复用传输，当前目标URL未知 |
| Authority Handler认证 [C02:301–316] | Bearer compare_digest、operation白名单、strict JSON | 正文只作为数据；transport日志；已实现服务角色认证，实际部署待P1 |
| **拟议H2专用分支** [C02:317前] | 直接使用匹配的identity及独立权限；正文仅授权/许可/scope引用 | 不向旧call分派；不接受自报actor/grant/path；未实现 |
| **拟议Registration与ReadSession** | 宿主发行的对象绑定Store/connection/lock、进程epoch、批准manifest和精确scope | 注册无SQL/key；一次会话尝试闸门；未实现 |
| **拟议BoundedAuthorityReader** | 已批准的唯一Store引用；固定查询、16MiB界、Schema2 | 最多一次世界行SELECT、一次既有cipher/key解码；未实现 |
| R12公开适配器 [C05:417–468] | proxy reader、真实宿主context、scope、limits | Authority域内原请求验证和净化；本地Native缺口保持；已有代码 |
| H1宿主策略/摘要 [C06:84–467] | 原许可/范围/错误/白名单 | 需最小来源接口与真实计量适配；当前只支持合成 |
| **拟议管理调用工具** | 读取经批准的专用最小凭据与manifest，最多调用一次 | 输出仅管理摘要，禁止全状态/秘密；工具未存在，命令不可执行 |

首次调用工具直接复用与Controller相同的Client传输封装，作为独立管理请求发起者。现有Controller业务代码本轮方案保持原样；把用户/Agent透传到此管理入口属于以后单独的委托授权工作。当前真实Controller链的缺环明确保留，不能以合成Controller测试代替。

## 4. 最小文件级差异（本轮均未修改）

工程根`D:/毕业设计/auth-lifecycle`。

| 路径 | 拟议最小变化 |
|---|---|
| **修改** src/auth_lifecycle/online_state/services.py | Authority构造成功后可选注册；专用Handler分支接收真实identity；只读分支日志失败固定码/无回退；默认关闭；Controller和Provider逻辑原样。 |
| **修改** src/auth_lifecycle/online_state/dsat_authority_read_host.py | 增加受信来源Registration接口和audit事实输入；保留默认合成路径、旧许可/summary Schema及finally计费；拒绝“仅source_kind字符串”的真实注册。 |
| **新增** src/auth_lifecycle/online_state/dsat_authority_host_activation.py | 注册来源对象、真实reader窄视图、会话总量闸门、指定rid核验、元数据/权限票据检查；复用既有Store.cipher/AAD解码能力及R12。 |
| **新增** scripts/read_dsat_authority_once.py | 最小管理客户端；只读指定manifest/专用凭据、Client一次调用、白名单输出；禁止Laboratory/serve/init。 |
| **新增** tests/test_dsat_authority_host_activation.py | 20项A01–A20离线用例；合成RPC/身份/codec，必要时仅自建`:memory:` SQLite核固定SQL。 |
| **新增** scripts/run_dsat_authority_activation_tests.py | 限定新20项＋必要的原H1 24项回归，严格资源/文件/网络边界。 |
| **新增子树** tests/fixtures/dsat_authority_host_activation/ | 纯合成注册/票据/codec输入。 |

以上七目标只申请未来离线代码开发与验收。storage.py、protocol.py、R12模块、migration及旧研究/结果保持原字节。当前H1 venv未发现常规cryptography包目录，实际导入可用性未测；A1不导入services/storage/materials。通过AST核对services挂载点，实际受限dispatch和注册核心置于仅依赖标准库/R12的activation模块，由替身执行。服务定义的实际导入/启动验证需指定具备可选依赖的Authority环境后另批，禁止以模块stub冒充真实密码学导入通过。

新客户端只依赖纯Client和摘要类型，可继续使用H1解释器；这不确定Authority服务端应使用哪一环境。P1须分别固定两端解释器/库版本。pyproject的声明不是已安装或已部署证明。

## 5. 真实注册的必要条件

Registration由Authority宿主工厂在可信配置域内发行，绑定：Store/connection/lock的对象同一性、现有codec/AAD合同、规范数据库位置、加载版本、实际进程身份/创建时点、每次启动新生成的epoch、P2授权ID、当前读取策略、field mask和预算。正文中的路径、mode、认证/来源标志只能被拒绝。

实际source_kind采用已有R12枚举`LOCAL_AUTHORITY_HOST`，只能由上述已审对象选择。它表示来源模式，仍保留UNVERIFIED的Native/部署字段。生产路径不会通过把SYNTHETIC_ONLY字符串改名取得资格。

已有库缺持久authority_instance；PID、epoch、locator和路径hash分别作本次部署定位，`authority_instance=null`继续保留。实例确认依赖批准的OS/部署信任与加载事实，不能获得跨恢复/复制库的持久genesis证明。[C01:21,47–120；C05:390–409]

## 6. 身份、授权与全局一读

scope五项为account/audience/task/caller/generation；origin在此基础上加grant_id共六项；请求绑定五元为rid、digest、完整origin、attempt_id、release_version。[C05:18,248–309] 这些对象分别管理，不能省略origin中的grant或将业务caller等同管理actor。

P2预先指定一个精确tuple、一个grant、一个已知rid。digest/attempt/release若尚无可信历史记录，可在获准的唯一快照内核验并固定，不暗中增加发现读取；当前连rid和tuple也未取得。已撤回业务grant的历史读取须独立的历史查看权，管理读取不会创建新grant或恢复业务许可。

当前secure配置在serve启动时读入，文件变化不会自动更新内存权限。拟议入口需额外核验独立P2元数据票据的当前版本/有效期/启用状态，权限变化/撤回时拒绝后续入场。票据无Bearer/key，仅含受批范围和引用；其文件访问在03预算单列。来源身份先认证，再读授权元数据，最后才允许接触世界行/key。

**会话总闸门位于issue_permit之前**，同一P2授权在同一运行epoch只允许一次已授权尝试；并发请求和重新申请新permit共用该闸门。资格不符先拒绝，合法入场后任何预算/源/网络/输出失败均不自动恢复额度。客户端无应用重试；底层可能的重复传输也由服务端总闸门限制。

会话绑定实际PID/创建时点/每启动新epoch；崩溃、重启、重新注册或权限票据更换后，旧P2授权失效，需重新核验/申请，禁止根据文件旧标签自动rearm。此首次方案不声称实现跨崩溃持久幂等簿。若研究者要求同一授权恢复重试，则需另审持久claim协议与额外写入。

策略锁顺序保持session/policy→reader，读前和出域前核当前授权；撤回后的结果处理沿授权检查点的历史观察语义，不承诺网络交付瞬间或已取得数据的回收。服务内任意Python执行、文件/数据库管理员继续属于可信域。
