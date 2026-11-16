# 最小宿主接线与分阶段验收计划

当前完成 H0。以下 H1/H2 均为提案；源码修改、项目测试和真实调用尚未执行。

## 1. 分阶段文件计划

工程根 `D:/毕业设计/auth-lifecycle`。

| 文件 / 当前函数 | H1拟议工作 | 权限、输入输出与副作用 | 验收 / 版本 |
|---|---|---|---|
| **新增** `src/auth_lifecycle/online_state/dsat_authority_read_host.py` | 内部 `AuthorityReadHost`、宿主身份/permit接口、singleton tuple守卫、最小摘要 | 接受已注册reader与宿主策略；不创建数据库/服务，不加载key；只通过R12读一次；允许宿主临时permit计数 | H01–H24；新增独立宿主摘要合同 |
| **新增** `tests/test_dsat_authority_read_host.py` | 专用离线身份/策略/reader/connection替身 | 手写合成状态、RLock及transaction flag；外部身份发行使用替身 | 仅新24项，无旧测试重跑 |
| **新增子树** `tests/fixtures/dsat_authority_read_host/` | 合成scope、permit、状态及canary | 全新命名与输入，R12夹具原字节保留 | 文件摘要与可公开sink扫描 |
| **新增** `scripts/run_dsat_authority_read_host_tests.py` | 限定新测试发现、离线审计、结果与hash记录 | 审计禁止SQLite连接、网络、服务、子进程、private/runtime访问及输出根外写入；-B | 120秒软预算；每次新run保留失败 |
| `storage.py` / read_state | H1保持原字节；宿主传入替身协议 | 实际源码保证及key/execute行为通过H0审查，H1不构造Store | 实际Store适配仍待H2 |
| `services.py` / serve、Controller.call | H1保持原字节；不挂HTTP路由/管理回调 | H2需要另审Authority内部调用挂载点，不能借现有CLI启动取得引用 | 部署激活差异当前未批准 |
| `dsat_authority_read.py` / 公开适配器与类型 | H1原字节复用 | 使用公开适配器，不调用私有_project，不修改Schema | R12 SHA保持 |
| protocol.py / migration / S1/S2/S3-A | H1全部原字节保留 | 仅复用R12已有纯规范函数；无求解/提交 | 原结果和下游资格门沿用 |
| H1运行与审计输出 | 新根 `D:/毕业设计/research_g2_dsat_implementation/2026-11-11_r13_h1_offline/` | 只保存合成输入hash、新源码快照、结果和净化日志 | 本轮未创建；报告根与执行根区分 |

H1是可复用内部守卫组件的离线接线。实际管理身份认证提供者、Authority进程内调用入口和部署注入仍为H2前置责任。新模块不把自己发行的类型或布尔标签称为真实身份认证。

### H1 精确执行命令（拟议，文件尚未建立）

```powershell
& 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_read_host_tests.py'
```

当前执行次数0。使用已批准隔离解释器，无新增依赖。H1 runner只导入新宿主、原R12适配器及其纯规范依赖、新专用测试；Storage/Services/Provider/实验启动器均不导入或实例化。现有 115/46/33 项、整仓和Native测试不在命令发现范围。范围内新文件允许最小修复与重新运行，全部失败run保留，单次新suite最多120秒且每轮仅24项。真实key/SQLite运行费用继续NOT_MEASURED。

## 2. H1 冻结24项

全部当前为 `NOT_RUN`、executed=false。

| ID | 场景 | 验收条件 |
|---|---|---|
| H01 | 合法内部注册 | reader对象、producer/locator/epoch与permit绑定一致 |
| H02 | 缺真实认证输入 | 在读源前拒绝；替身只模拟宿主已认证事实 |
| H03 | 自报trusted/admin/source_confirmed | 正文无法发行权限，源读取0 |
| H04 | permit过期或权限已撤回 | 当前策略拒绝，源读取0 |
| H05 | 精确singleton tuple | 仅获准account/audience/task/caller/generation可读取 |
| H06 | 跨account/audience | 拒绝且源读取0 |
| H07 | 跨task/caller/generation | 分别拒绝且无外scope标识出口 |
| H08 | tuple集合展平 | 两个获准tuple的混合交叉tuple拒绝 |
| H09 | 正文grant/rid/字段/path注入 | 未支持的选择器或字段拒绝；scope合同完整保留 |
| H10 | 正常锁与一次读 | policy→reader.RLock顺序、允许重入、B1源读1次 |
| H11 | 危险入口陷阱 | 构造器/旧call/SQL/服务/Provider调用0 |
| H12 | 读取配额 | 一读+6余量门，边界不足时拒绝且重试0 |
| H13 | 源异常含秘密 | 固定码、无异常字符串/cause/局部变量出口 |
| H14 | connection在事务中 | 源读取前拒绝；COMMIT/ROLLBACK均0 |
| H15 | Schema/源合同 | 可信登记的legacy合同可处理；未知合同安全拒绝，无迁移 |
| H16 | 整行解码域与摘要 | 源可含多个scope的合成秘密，最小摘要无行/原请求/材料 |
| H17 | 全部输出sink | 正常/错误/repr/JSON/日志/缓存/序列化的canary扫描 |
| H18 | 世界与临时控制状态 | 世界/a/event/phase/预算不变；permit消耗和读遥测单列 |
| H19 | 读取与策略撤回排序 | 撤回先提交则拒绝；读取先授权则仅生成历史摘要；无越权复用 |
| H20 | 重放/第二次使用 | 已使用permit再次调用拒绝，源读取0 |
| H21 | reader/epoch置换 | 相同a/数据在另一对象或host epoch拒绝 |
| H22 | 输出/记录上界 | 超限整体拒绝，无半份成功结果；拒绝输出自身也受界 |
| H23 | 业务撤回与管理读取分离 | 明确历史读取许可下可读inactive grant；业务active不自动授予读取权 |
| H24 | 资格与费用 | native/global/math固定关闭，读/锁/投影/序列化费用明示；S1/S2/S3/B2调用0 |

测试H19采用线程/受控替身调度，保持纯离线且不启动服务。H14的connection仅为暴露in_transaction标志的替身，H15登记仅为合成源元数据；这两项真实运行性质须在H2再验。

## 3. H2 首次真实验收最小方案

推荐方案仍为03稿的C：Authority宿主内部已初始化reader。首次只输出 **管理摘要**，不向Agent输出。

### 冻结输入与输出

| 项目 | 计划 / 当前缺项 |
|---|---|
| 测试环境、Authority实例、DB绝对路径 | 均null，须研究者指定；本轮未猜测或搜索运行库 |
| 宿主进程、加载源码/二进制、SQLite/crypto版本 | 当前锁定源码；运行PID、加载路径/构建、解释器与库版本待部署事实 |
| 调用者/权限 | 本机管理主体、已验证认证事实、独立staging_read_metadata、当前permit版本；真实值null |
| 作用域 | 一个精确account/audience/task/caller/generation tuple；实际值null；至少一条已有规范请求，以便核验原请求绑定 |
| 允许内部读取 | 最多16MiB的单份完整加密state及一次整行解密；scope外明文仅短暂留Authority可信域，禁止导出 |
| 最小key权限 | 现有Authority身份对既有key文件的read；B1复用cipher一次，禁止拷贝、独立hash、打印或发给Controller/Agent |
| B1内部上界 | output_bytes=65536、scoped_records=32、write_headroom=6；超限整体拒绝 |
| 最终摘要 | ≤4096字节，白名单见下；完整B1对象内存内消亡，无公开缓存 |
| 调用/SQL/key | B1最多1次；只读验证SQL总数最多4；key读取最多1；自动重试0；有限额度预留4+6 |
| 日志/证据 | 新获准目录内至多1份摘要、1份计数审计、1份授权/版本清单，合计≤65536字节；既有SQL遥测最多4条单列 |
| 时限 | 10秒软期限；阻塞后不杀Authority，不重试；记录真实经过时间 |
| 源状态观察 | 原a/有界密文/event count/max/total_changes比较均在可信域；只导出相等判定及计数；外部writer变化时INCONCLUSIVE |
| 退出清理 | 释放本次锁与临时对象，不关闭既有连接、停止服务、删WAL/SHM、改key或撤回grant；失败记录同样净化 |
| 命令/调用入口 | **null / BLOCKED_NO_INTERNAL_INVOCATION_ENTRY**；没有现成可安全执行命令；H1后需冻结管理回调、挂载差异、激活和精确触发命令 |

### 摘要字段白名单（拟议 dsat-host-read-summary/1）

`schema`、`execution_ref`、`status`、`authority_revision`、`authority_instance=null`、`obligation_revision=null`、`snapshot_digest`（内部B1内容摘要）、`read_scope_ref`（受批非秘密引用）、`observed_at`（monotonic下/上界与epoch）、`source_contract`、`source_binding_status`、`missing_fields`（固定码）、`native_currentness_status="UNPROVEN"`、`math_ready=false`、`current_native_eligible=false`、`global_complete=false`、`authority_write_action="NONE"`、`audit`（有限计数/相等判定）。

真实account/task/caller/grant/rid、原请求摘要、opaque材料引用、原生标识、DB/key路径、认证凭据、完整原请求和整份state全部留在内部。`source_binding_status`仅在至少一条获准请求实际核验成功后为 MATCHED；scope为空时为 NOT_APPLICABLE_EMPTY_SCOPE，不能据此记原请求验证通过。

最终摘要采用独立schema，R12原schema/digest保持原义。缺可靠UTC时保留monotonic域；epoch为运行观察标识，稳定authority_instance保持null。`read_scope_ref`须指向管理域中已经批准的tuple，标签自身只承担关联作用。

完整嵌套白名单以 `sources/HOST_SUMMARY_SCHEMA_PROPOSED.json` 固定，属于待实施规格。audit 仅允许：source_sql_count、source_read_count、source_operations_delta、key_read_count、key_count_basis、bound_request_count、world_row_unchanged、authority_events_count_unchanged、authority_events_max_unchanged、connection_total_changes_unchanged、observed_sql_schema_version、secret_scan_status、elapsed_ns、deadline_exceeded、permit_consumed。未知或未测量值保持null；key_count_basis区分固定代码路径上界与独立实测。仅凭预期一次cipher调用，key_read_count仍为null，不能填作实测1。

### H2 14项真实验收计划

全部当前为 `NOT_RUN`。首次一调用可观察的检查与后续需要额外场景/授权的检查分别登记。

| ID | 实际需要验证 | 首次单调用能力 |
|---|---|---|
| R01 | 宿主/管理主体的认证链 | 必需，部署事实＋受信上下文 |
| R02 | 当前读取权与精确tuple | 必需，当前策略核验；真实输入待指定 |
| R03 | 实际加载源码和受锁read路径 | 必需，批准的加载事实与安全调用计数 |
| R04 | 无构造/初始化/迁移 | 必需，路径审计和已初始化引用 |
| R05 | 无本次世界版本递增 | 首次前后观察；外部变化时INCONCLUSIVE |
| R06 | 无本次新Authority历史event | 首次计数/最大版本/总变更及无DML；非恶意部署前提 |
| R07 | 真实净化摘要与所有出口 | 必需，真实sink白名单；范围外零导出 |
| R08 | 实际错误输出安全 | 真实失败若自然出现可观察；主动故障注入另批 |
| R09 | 旧Schema1/2兼容及未知拒绝 | 首次仅当前库；其它版本新样本另批，无migration |
| R10 | 实际权限不足时读取前拒绝 | 真实负向调用另批；首次正向调用无法覆盖 |
| R11 | 原请求来源绑定 | 首次须已有至少1条正确请求；不创建或修复请求 |
| R12 | 当前局部revision配对 | 首次a/W/B1一致；“当前”限语句快照点 |
| R13 | 与并发写入、撤回、迟到结果的关系 | 首次安静窗口只给实际观察；主动并发/更多调用另批 |
| R14 | 最小key读取及秘密边界 | 首次现有cipher一次，无新key副本；ACL/使用许可必需 |

首次验收成功并不等于14项全面PASS。R08/R09扩展/R10/R13主动并发需要各自测试样本和调用预算；机器表保留所有未执行项。

## 4. 继续阻塞的能力

生产typed O、独立o、生产CAS、B2写回、Schema migration、旧writer fence、原生持续失活、完整创建前沿、C_effect和全局COMPLETE全部BLOCKED。R11的B15/B27/B28原ID、原合同与R12结果保持原样，未纳入H1执行分母。

## 5. 成本与停止条件

设整行密文及解码状态规模为S，相关记录数G/R/D/W、选定条数k、选定原请求总长度J。读取/JSON解码至少O(S)，扫描过滤O(G+R+D+W+J)，排序O(k log k)，序列化和闭合Schema检查按输出长度计。R12在锁内完成投影、摘要和最终序列化，锁持有时间包含这些成本。[S05:433–461] 输出界无法代替输入S的界，宿主策略和整行解码费用均须计入。

H2增加最多4次SQL遥测fsync、一次key访问、有界密文比较、策略/reader锁等待及最小审计写。真实时延、内存倍数和文件系统副作用均NOT_MEASURED，R12的0.7639秒离线总耗时仅属替身测试。

停止条件：身份或scope缺失、源指针/epoch/哈希不匹配、旧路径/新端点需要超范围修改、残留事务、输入/输出/配额越界、未知Schema、key访问未经批准、绑定不符、日志出口不可控、需要真实服务/网络或测试越界。出现失败时保存最小固定码，既有世界和服务继续保持；超出H1四个新路径或H2锁定授权需要重新审定。
