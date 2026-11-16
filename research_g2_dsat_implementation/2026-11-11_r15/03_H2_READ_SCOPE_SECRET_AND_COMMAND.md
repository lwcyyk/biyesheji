# H2范围、秘密、副作用与命令

## 1. 当前实例与调用范围

目标环境、Authority PID/创建时点/身份、URL、DB绝对路径、实际Schema/WAL、管理主体、任务tuple、grant、rid和真实key引用均为null/UNRESOLVED。实例/身份字段的获取方式、当前证据级别分别见H2_INSTANCE_LOCK和H2_IDENTITY_AND_SCOPE_LOCK。

源码只给出相对位置关系：`approved_root/authority/authority.db`与`approved_root/secure/authority.key`。[C02:282–283] approved_root尚未确定，这两个表达式不作为已发现的真实路径。当前Python客户端候选是R14已验证的隔离解释器；Authority进程实际解释器、库版本和加载代码另待P1。

P2最小范围是一个已确认运行实例、一个独立管理读取主体、一个精确account/audience/task/caller/generation tuple、一个grant和一个已知rid。该rid的原请求digest、完整origin、attempt/release在唯一快照内核验并记录；若已有可信历史期望则同时比较。当前目标尚未指定，登记TARGET_SCOPE_PENDING，禁止自动选择账户或扫描所有Token寻找样本。

稳定数据库authority_instance和独立o当前均缺失，继续为null；本次进程/部署定位不能替代持久实例身份。

公开的全局a和计时/费用可能反映其它任务活动，管理读取许可需明确包含这类元数据观察。首期Agent无此入口，字段过滤不被提升为跨租户侧信道非干扰证明。

## 2. key与整行解密

Store持有key_path引用，cipher每次重新读32字节key，再构造AESGCM。[C01:103–108] 复用既有cipher能保持codec合同，但首次H2仍会产生一次额外key文件读取尝试，需要独立批准。

当前加密合同是12字节nonce＋AES-GCM密文/标签、固定AAD `auth-lifecycle/online-state/schema-1`、JSON明文。SQL a和Schema标记没有进入AAD；可靠性依赖批准主机/数据库及无不受控回滚的前提。使用正确key并不能排除整库旧版本回放。

一个tuple的净化仍需要在Authority域内解码整行state；该行可能包含其它账户的秘密。P2必须显式同意：指定现有Authority进程对指定DB加密行的一次瞬时完整解码，仅R12/受信reader/宿主可持有对象，最终仅获批tuple参与投影。若研究者要求解码本身也严格限于单task，当前存储格式缺少该能力，P2应收缩或保持阻塞。

密钥字节、handle、密码、AT/RT/ID Token、client secret、API key、私钥、原请求、完整state及他人资料均不导出或落临时明文。cipher对象及原始state不交Controller/Agent，异常只返回固定码；内存安全擦除、恶意同进程代码和OS管理员风险依既有可信边界处理。

## 3. 单次有界读取规格（新适配器待实现）

BoundedAuthorityReader仅暴露R12所需的read_state、原Store.lock、额度视图及空闲事务状态。注册阶段不读源。获准调用使用固定一条SQL：

```sql
SELECT version,
       length(ciphertext) AS state_bytes,
       CASE WHEN length(ciphertext) <= :ceiling
            THEN ciphertext ELSE NULL END AS ciphertext,
       (SELECT user_version FROM pragma_user_version) AS schema_version
FROM authority_state WHERE id=1
```

`:ceiling=16777216`来自受信配置，正文无权修改。世界行/版本与Schema元数据在一次SQL调用中取得；Schema元数据观察仍在预算内单列，内部SQLite页访问和实现成本不按“一条语句”忽略。

先检查行存在、Schema2、长度和非空有界密文，再用现有Store.cipher及原AAD按原方法解码，返回同一行a/W给R12。超限/未知Schema/缺行在key访问前固定拒绝，禁止重查/自动回退。新模块只复用已存在对象的execute/cipher能力，不构造Store或另开连接；storage.py原路径保持原样。

对界内且Schema匹配的状态，新投影行与原SELECT version,ciphertext取到相同配对，后续nonce切分、AAD、cipher.decrypt和JSON解码相同；因此reader结果与原read_state一致。界外输入被本次更窄准入拒绝。这个有限适配证明和实际SQL语法/绑定尚待A1离线验收；当前没有调用SQLite。

pragma表值函数的版本前提来自已保存官方SQLite文档（R13 sources/sqlite_pragma.html:310–366，特性自3.16.0加入）。实际SQLite版本/能力仍须核验，版本不满足时停止，禁止改用额外未批查询。

## 4. 输出白名单

首次P2沿用R14的`dsat-host-read-summary/1`根和audit白名单，≤4096字节；内部B1输出≤65536字节、选定记录≤32。管理者仅获schema、局部revision、快照摘要、批准scope引用、读时钟、指定请求核验状态、固定缺口及费用。真实rid/grant/task/operation/phase/legacy O留在Authority内部核验，首轮对外不扩大字段集合；它们的展示需要另外明确批准。

R12原Staging与request_verifications合同保持原义，稳定instance、o、SQL Schema源字段仍按原合同保留。新宿主audit可记录实际观察的SQL Schema、connection.total_changes相等性和计量出处；key_read_count无法独立实测时保持null，key_count_basis=PINNED_PATH_BOUND，不能把路径上界写成实测次数。

`source_sql_count`在真实适配器中明确记录调用既有execute的SQL尝试次数：至多1。若execute内部遥测失败，物理SQL可能尚未发出；该差异用计量出处和最小内审记录表达，不把尝试次数当作SQL成功数。原H1中此值0仍表示其全程未访问真实SQLite。若实施发现需要新增公共字段来表达这些差异，应升级宿主摘要版本并重新审批，避免默默改旧字段含义。

所有响应由白名单新建，errors/JSON/repr/log/cache/IPC/temp/traceback均使用固定码和批准引用。最终序列化校验后再输出，故障无部分成功前缀；摘要hash固定内容，真实性继续依赖受信宿主/通道。

## 5. 明确预算与失败费用

| 项目 | 首次P2提案上限 / 单位 |
|---|---|
| MAX_AUTHORIZED_READS | 1次H2会话授权尝试；全部新permit共用此总量 |
| 世界读取 | 1次BoundedReader调用、1次世界行SELECT尝试 |
| SQL | 1次Store.execute尝试；其中包含1次Schema元数据观察 |
| key / 完整解码 | 各至多1次尝试；长度/Schema拒绝时为0 |
| 额度 | operations增加0或1；有限额度要求读前operations+1+6≤limit |
| 授权元数据 | 服务端P2非秘密票据最多2次读取（入场/出域检查），不读完整secure配置 |
| 客户端凭据 | 专用受限调用token文件最多1次逻辑加载，需单独授权；服务端身份表复用启动时的可信配置 |
| TLS | 复用既有Client；公共CA文件1次逻辑加载，具体OS读次数依库；无新服务监听器 |
| RPC | 1次应用Client.call；无应用重试/回退；重复传输由会话闸门拒绝再次读源 |
| 遥测 | 单个预期请求至多1条源SQL日志、1条宿主审计和1条现有transport日志；异常/重复流量另记实际次数 |
| 输出/归档 | 摘要≤4KiB；≤3件最小证据，总≤64KiB；真实目录待指定并核ACL |
| 时间 | 10秒软期限；客户端超时按已可能消耗处理，保持UNKNOWN，禁止自动再读或强杀Authority |

Store.execute先operations+1，再emit/fsync，最后调用connection.execute。[C01:93–101] 遥测失败可能已扣额度而SQL尚未发出。解码、返回、摘要或网络失败均保留已发生费用；finally计费逻辑必须延续。只有权限/scope/会话/资源预检先拒绝时，世界源/key费用才为0。会话尝试槽一经合法入场即消费，额度拒绝也不会自动rearm。

新增P2票据由管理可信配置域提供，仅存范围/引用/有效期，实际读取许可和变更责任仍待指定。磁盘secure配置变更不会自动更新当前Handler，故不能把改文件当作权限已经撤回。出域前发现票据撤回时丢弃数据，历史读取费用保留；最终检查之后的撤回仍按检查点的时点语义处理。

现有transport日志在try/except之后emit，其失败当前可能阻断响应。[C02:325–330] 拟议分支须处理该失败为无数据/固定码或断连，仍保持已消费会话，禁止进入旧recover/重试。对其它流量的日志行为保持原义，无法在任意攻击流量下保证全服务仅追加三条记录。

WAL/SHM锁与读取、atime、key文件访问、遥测fsync、连接竞争、内存和序列化均有成本。复用已开连接，禁止本次构造器、migration、新连接、query_only切换、immutable绕过及checkpoint。启动/部署所需rw初始化和文件变化另在独立生命周期授权中计费。

源扫描与JSON解码按整行字节数S计费，选中记录及原请求校验再按其总长度扫描/排序；内存包含有界密文、解码bytes、完整JSON对象和输出。16MiB输入界不等于16MiB进程内存，Python对象展开和临时副本需要运行容量余量；本轮没有实测耗时、内存或硬期限保证。

## 6. 前后验证的证据边界

primary模式采用**单读、固定无DML路径**：在实例锁内记录connection.total_changes前后值与源operations，按固定代码核一次SELECT、无旧dispatcher/无写handler；返回a/W和内部净化摘要绑定同一快照。total_changes是连接属性读取，无SQL/解密。当前源代码闭包、标准表、无任意用户回调/UDF、同连接受锁使用及部署忠实是前提。

这可以支持“本次调用没有发起世界DML”；它不能单独证明其他连接没有提交，也不提供独立的前/后完整世界hash。首次输出的world_row_unchanged、event_count/max相等性保持null；connection_total_changes_unchanged可按实际观察填值，Schema按唯一查询观察填写。a为快照点观察，返回时可能已有新a，原生AS变化另独立。

R13曾列出前/后密文校验的4语句方案，本轮将其列为**额外验证选项**：若要求独立前后读，则需明确授权3次世界行SELECT（前/B1/后）、1次Schema查询、4个额度及相应日志，key/解密仍最多1次。该选项未纳入primary P2，也没有被默默执行。

## 7. 命令锁

当前`H2_COMMAND_LOCK.json`的actual_entrypoint、argv、目标实例/身份/scope/许可/证据目录均为null，`command_executable=false`、`blocker=H2_ENTRYPOINT_MISSING`。拟议scripts/read_dsat_authority_once.py尚不存在；本轮没有创造旧CLI的新参数，也没有给出可执行的真实H2命令。

只有入口及安全客户端实际实现、运行源/身份/scope/key/整行解码/激活条件获批，才生成无占位符argv并固定源码和环境版本。客户端只载入专用最小配置，禁止借cli.request/Laboratory读取全部角色配置。当前动作仅是七目标A1离线实施申请，P2执行仍需下一次独立准入。
