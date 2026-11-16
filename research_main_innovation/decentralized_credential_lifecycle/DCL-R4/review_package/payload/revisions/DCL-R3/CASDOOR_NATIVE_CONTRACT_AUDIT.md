# Casdoor 4.25.0 原生能力审计：DCL-R2

2026-11-09，Asia/Shanghai。范围为静态源码、历史 M3/M4/M6 与本地发行文件哈希；新增原生请求和运行实验为 0。

## 1. 版本与证据

源码根 `D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0` 的 HEAD 为 `528a0213f01caf70b9f41009cbf7b2f67bdd67ec`，初始 `git status --short` 为空。官方 [v4.25.0 发布记录](https://github.com/casdoor/casdoor/releases/tag/v4.25.0) 指向 `528a021`，changelog 明列 RFC7009 撤销端点。

现存 `auth-lifecycle/.runtime/l1/dist/casdoor/casdoor.exe` SHA-256 为 `ddbab07cbe0a913e3bf3b3fbb09b0a1fa3b4abc5127c6b3156930aa77a37ad5c`，与 M6 环境锁一致。本轮读取文件，未启动/调用该服务。源码到发行二进制的可复现构建仍为 UNPROVED。

26份源码的副本和哈希位于 `evidence/r2/native/source/`、`SOURCE_LOCK.json`。下文路径/一基行号均相对该源码根。`util/time.go` 稀疏克隆对象获取失败，改核固定 commit 的[官方原文](https://raw.githubusercontent.com/casdoor/casdoor/528a0213f01caf70b9f41009cbf7b2f67bdd67ec/util/time.go)，见本轮 web04；其他缺失对象单列，空抓取文件未当成源码。

标签：SOURCE_CONFIRMED=指定源码支持；CONTRACT_ASSUMPTION=部署或环境前提；EXPERIMENT_OBSERVED=历史实际轨迹；UNVERIFIED=证据缺口；UNSUPPORTED=所审接口缺相应合同。每项操作的18字段记录见 [NATIVE_CAPABILITIES.json](evidence/r2/native/NATIVE_CAPABILITIES.json)。UNSUPPORTED 限本次审核接口及冻结 password/refresh、Bearer、非共享应用子域。

## 2. 核心调用链

|操作|路由/实现|状态、返回和保证边界|
|---|---|---|
|AT/RT 初始发行|routers/router.go:383；controllers/token.go:218–429；object/token_oauth.go:27–165、290–388|password 验证后生成随机 name/jti、插入 Token，再组装响应。getUserGrantToken:352、383；后续 DPoP/CodeIsUsed 更新仍可失败。重复请求会重新发行；本地 intent/rid 没有原生去重合同|
|刷新专用端点|router.go:384；controllers/token.go:444–485；object/token_oauth_util.go:562–769|读取父 RT→检查→生成子材料→AddToken→DPoP 更新→轮换删除父→返回。多个数据库语句独立，代码没有包围它们的同一事务/父行 CAS|
|access_token 的 refresh grant|object/token_oauth.go:116–121|进入相同 RefreshToken；审计/网络入口不同仍属于可能创建入口|
|RFC7009 revoke|router.go:386；controllers/token.go:500–543；object/token_oauth_util.go:351–393|查匹配 AT/RT 行，核 app/secret 条件，置 expires_in=0；可按相同 refresh_token_hash 扩散。未知/其他客户端/已失效行可返回空 HTTP200|
|内省|router.go:385；controllers/token.go:634–756|客户端认证、数据库匹配/ExpiresIn、JWT 验签时效、用户/应用状态。200+active=false 为当前观察；未执行刷新，也未证明所有后代关闭|
|UserInfo|controllers/account.go:781–803；routers/auto_signin_filter.go:63–131|fresh cookie-free Bearer 请求先按 AT 哈希查原生行，检查期限/用户，再查应用并设置请求身份。指定行失效后，后续新认证读取应拒绝；认证已完成的在途请求仍需单列|
|Token 点读/枚举|controllers/token.go:37–100；object/token.go:56–89、200–205；object/ormer_session.go:32–53|get-token 精确 PK；列表可分页，organization 等值而 field/value 为 LIKE。count 与 Find 分开。返回包含敏感材料，读取权限范围先成立|
|审计产生/读取|main.go:122–124；routers/record.go:120–183；object/record.go:144–206、235–268；controllers/record.go:33–75|AfterExec 建普通记录，再在 SafeGoroutine 内 webhook→Insert→audit sink；缺与 Token 插入共事务的原生完成日志。查询需 RequireAdmin，count/Find 分离|
|会话退出|controllers/account.go:401–549、577–690；object/session.go:353–377；object/token.go:291–332|按 hint/当前 session/SSO scope 处置并通知 RP。多个动作及外部通知分属步骤，缺统一跨 RP 终态/异步效果关闭|
|用户/应用/组织处置|object/user.go:1335–1422；object/application.go:598–612；object/organization.go:399–413|用户先期限化 tokens/删 sessions，再软/硬删除；app/org 删除为各自对象行删除。共同账户/应用下的 B 可能失去支持；重建/管理员改写必须纳入后续模型|

## 3. 刷新与撤销的真实细化

刷新一条调用的关键点：

`F0 到达 → F1 ValidateOAuth → F2 读取父Token(586) → F3 ExpiresIn检查(599)、app/resource/DPoP/JWT/user检查 → F4 生成随机子ID(705) → F5 AddToken(738) → F6 DPoP更新(747，可选) → F7 DeleteToken父(755，轮换时) → F8 TokenWrapper → F9 HTTP写出 → F10 客户端可能收到`。

审计从 AfterExec 触发，其 Insert 另在 goroutine 中。Token 插入成功与审计记录可见之间缺共同原子点；HTTP写出与客户端收到之间也缺必达关系。数据库正常返回的语句作为状态变化点，掉电持久性仍继承实际数据库/驱动配置，源码调用成功未独立证明物理落盘。

撤销顺序：

`V0 到达/客户端条件核验 → V1 查当前匹配行 → V2 app归属/secret/ExpiresIn判断 → V3 单行ExpiresIn=0(353) → V4 同RT哈希的正ExpiresIn行批更新(360) → V5 返回HTTP200`。

F2/F3 与 F5/F7 之间允许插入 V3/V4。刷新没有在插入子行时再次以父仍有效为条件提交；删除父行影响行数为0也未在调用方当作失败。因此原生撤销 ACK 与“所有已通过检查的创建执行结束”分开。

## 4. 精确撤销域

SOURCE_CONFIRMED：AT 和 RT 同属一个 Token 行。成功期限化该行后，内省和 fresh UserInfo 的相关数据库检查会受影响。`ExpireToken` 还对相同 `refresh_token_hash` 的当前活动行批量置0；这覆盖禁用轮换时共享 RT 的多个 AT 行。AT 撤销进入的也是同一个函数，所以波及范围以代码为准。

轮换开启时子行获得新 RT 哈希；父行随后删除。此后拿旧父 RT 调 revoke 可查不到行并返回200，子行继续存在。原生 Token schema:28–54 没有 parent_token / root_grant / 本地 intent / attempt 字段；SessionId 在 refresh:736 继承，但 password 初始发行:367–382 未设置 SessionId。它无法替代普遍任务来源关系。

password RT 的刷新可省略client_secret，见token_oauth_util.go:772–787。统一token入口:75–81与专用refresh入口:444–477在grantTypes检查上有差异，详见NC7。以客户端密钥轮换或单入口grant拒绝作为全创建能力截止，需要额外依据。

历史 M3 能力文档将“找到当前记录失效”作为简化描述，遗漏了相同RT哈希扩散这一细节。R2 修正其解释范围，历史文档/数据原字节保留。该修正不改变轮换开启 M3/M4/M6 的单次创建前提和原始验收结果。

## 5. 审计与枚举能证明什么

审计 Record.Id 为自增日志位置；它排序日志插入，跨 goroutine 可能与 Token 创建先后不同。NewRecord 会遮盖 token/password 类字段、通常清除响应 Data，并把 StatusCode 初始化为200。完整 TokenWrapper 的 request→新jti 映射和原生创建提交点没有因此自动取得。

记录写入可能滞后、失败、被保留策略清理；object/record_cleanup.go:33–76 明列正 RecordRetentionDays 删除策略，非正默认保留。Token 自身也有清理策略：object/token_cleanup.go 的缺省保留为过期后30天，并允许按组织配置。它们各自属于存储保留，不能冒充请求终态/无效果证明。

Token/Record 的一条查询结果是对应读操作的观察。一般多页读取缺稳定快照游标；count+Find 缺同事务。M4/M6 通过授权整个专用组织、记录总上界和单页容量获得一次 Find 的范围完整性，随后以来源排除及效果上界饱和解决未来创建；这些前提必须一起保留。

## 6. 历史验收精确范围

|阶段|实际支持|继续保留的条件|
|---|---|---|
|M3|两条条件关闭；预先启用标识日志，取得新jti后精确点读|响应已收到并保存标识；S=1、每调用U=1、唯一未知创建、可信发送入口、未来重试排除；完全丢失标识的旧轨迹仍UNKNOWN|
|M4|无完整inbox/标识日志，授权专用组织枚举；两条PASS_CLOSED|五批准×10上界50，pageSize100；单Find范围、唯一来源排除；首次无新增候选仍保留创建余量1|
|M6|可信单机/单活/受限进程/专用组织；两条各43检查，原生HTTP共84|四批准×10上界40；B已有材料可用，窗口暂停新创建；处置后RT只做内省，本批真实刷新探测为0|

实验支持限历史二进制与profile。M6 的 UNKNOWN→条件 CLOSED 使用可信控制入口、写入者排除及发送/效果上界，无法直接外推到“E1拿到密码并恶意直连”的跨管理域攻击模型。

## 7. 保证清单

- SOURCE_CONFIRMED：已知行/共享RT cohort 的期限化、指定数据库接受检查、每个审核刷新调用至多一次新行 Insert、普通查询与管理接口。
- CONTRACT_ASSUMPTION：源到运行符合性、所有发送者受控、发送/效果上界、来源唯一、查询授权、外部写入排除、DB持久性及时间正确性。
- UNSUPPORTED：本地 k/intent 的原生精确结果幂等、按 k 的 FINAL_NO_EFFECT 与迟到永久拒绝、任务epoch原生验证、普遍父子世系查询、全域原子效果截止。
- UNVERIFIED：任意外部 RP、Cookie 生态、业务异步后果、失陷执行域的全部历史材料范围。

静态 Gate A 的通过表示能力及映射审计可复查；强原生目标分别按 profile 成立或 MODEL_BLOCKED。
