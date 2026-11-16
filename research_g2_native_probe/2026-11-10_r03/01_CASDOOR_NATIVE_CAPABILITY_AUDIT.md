# 真实 Casdoor 能力、权限与观察审计

版本与证据分类见 00；所有判断限锁定源码和历史固定 profile。

## 1. 三层观察边界

1. **原生服务响应**：可能包含 AT/RT/ID Token、Token 行、JWT claims、内省字段。
2. **可信适配器内部**：验签后保存 material、access_ref/refresh_ref、native identifier；可选持久 inbox 和 identifier journal。journal 只覆盖已经收到且验过的结果。
3. **Controller 调用者投影**：C01:24—26 只给 rid、digest、origin、phase、attempt_id、release_version。代理当前得不到 Token 字符串或内部 refresh_ref；新诊断投影需要单独设计并批准。

只读 API 的返回值可能含秘密。GET 属性只表示该操作的数据足迹，账户范围和泄露费用仍须审查。以下 Caller/Approval 同时受 AS 授权与本地 RPC/批次范围约束。

## 2. 七项接口

### Introspect

`POST /api/login/oauth/introspect`，G01:634—757；由获准 client 携 client 身份和 AT/RT、type hint 发起。账户/应用、JWT/记录及用户有效性检查以该路径为准。可信结果证明**查询时指定材料在声明内省路径的 active 判断**，并可给 sub、aud、iss、jti、expiry 等。

S：读 Token 与用户，不创建 Token；失败/超时不给可靠 inactive。`active=false` 可由缺记录、到期、失活或用户状态等造成；该结果无法单独定位原因、证明执行过刷新或证明无迟到子代。返回没有本地 grant/task/rid/attempt/generation/parent 绑定。

权限/成本：client 凭据与指定 Token 使用批准；每次 HTTP 机会收费。C04 允许 method 调用，但 C03 的普通 perform 仅 issue/refresh/userinfo，独立内省尚无通用 Controller 操作；dispose 中固定调用 AT 内省。不能将原生存在升级为公共接线完备。

### UserInfo

`GET /api/userinfo`，AT Bearer；固定 H01 是 fresh、cookie-free、HTTP 200 且 sub 正确的接受合同。C03:99—111 支持此路径，账户/client 由 material 和 profile 验证。结果证明这一次请求的接受，未来请求、离线 RP、浏览器 cookie 和业务效果需各自合同。

G12:63—91先查AT hash对应记录，再查记录有效期和用户状态；缺行时拒绝。G11:781—803经已登录用户上下文输出UserInfo。因此正常轮换删除父记录对该cookie-free路径有直接影响；07及费用中的跳过父处置仅依此类声明路径，不能据源码中“旧AT可继续使用”的注释扩大到全部RP行为。

S/D：不新建 Token；查询仍有访问日志、速率/共享机会消耗。网络异常、解析错误或 sub 不符保留不确定性。B 需要当前 gB、同 origin 的已知 source_rid 和剩余预算。

### get-token

`GET /api/get-token?id=owner/name`，G01:80—100、G04 主键查询。AS 校验组织访问，global admin 分支另计；当前 NativeHTTP 使用获准 client Basic 与已验证标识，读取权限以部署策略为前提。

返回 Token 行可核 owner/name、organization、application、user、AT/RT hash/材料、时间等。**行没有本地任务或父子来源字段。** 密码发行未设置 SessionId，刷新继承已有值；相同空 SessionId 对来源没有识别力。

C03:151—190 的现有点读 helper 还要求唯一可信标识和一个 refresh 机会；组织/应用校验写死 `l1-study/app-l1-0`。UNKNOWN Issue 即使留下标识，当前 SQL 的 operation='refresh' 也会使此路径停在 UNKNOWN。组织改成 M6 新值时也须修订规格，不能跨版本宣布 helper 通用可用。

每次一次机会；找不到行仅证明该读时点，仍可能有已通过检查的旧创建者。

### get-tokens

`GET /api/get-tokens`，G01:37—70。授权组织范围、owner、分页和 field/value 由路由与模型决定（G09、G10）。field/value 的 LIKE 子串过滤不构成账户级读取权限边界。当前 Python 发组织等值单页查询，再按账户/application 选取，**读取整个组织的批准必须先具备**。

count 与 Find 分开执行；count 不是同一事务快照证明。H01 的 complete 依赖：单页足够的上界、授权宇宙、排除外部写入、固定发送/来源清单等。C05 的 collection_complete、origin_bound 是不同结论。

C03:206—208 额外固定每账户两批准、预算和20、唯一未知 creator、一个发送槽和单候选。本轮 i1/i2 双未知已超其来源合同；同账户增加 gV 后，即使撤回，账户批准清单仍有第三项，2/20条件失效。原生 GET 仍可能给有用记录；现有 helper 无法据此输出原 CLOSED。

### Issue

`POST /api/login/oauth/access_token`，C04 固定 password grant；gV 的 casdoor_login、client secret、账户、scope 均须合法。G02:290—343 进行用户、scope、密码、MFA、应用签到等检查；成功生成一束 AT/RT/ID Token并 AddToken 一次（346—388）。AT/RT 与原生单位的对应复用 G1；字符串个数与撤销根数分别统计。

**共享账户副作用**：正确密码可清失败次数；密码格式可能升级；失败会增长错误次数并可能冻结；RecordUserSignin 更新登录时间/IP相关字段，UpdateUser还维护 hash/updated_time（G06—G08）。getUserGrantToken 在生成 JWT 后、AddToken 前写签到；外层 AddToken 后还调用 updateUsedByCode。因此错误响应与“无创建、无共享写入”不能等同。

CheckPassword 也可能接受组织 MasterPassword 或 LDAP 路径，成功只说明当前策略接受该材料。固定普通本地账户子域可排除这些分支，但要把前提写进规格。password 实验流程的可行性不承担生产推荐。

新 Token 的 Code 是新生成的授权码；updateUsedByCode 按 Code 更新 code_is_used/grant_type。限定非碰撞时影响新行；其真实查询范围和潜在碰撞必须保留，不能将其直接视为主键更新。

### Refresh

`POST /api/login/oauth/refresh_token`，G03:562—769，读取**所提交 RT hash 对应的行**，检查 client/application、expiry/scope/user等，生成新束，再 AddToken 一次。轮换开启时随后删除父行；关闭轮换时复用旧 RT 且保留父行。

创建后父删除错误、响应丢失或适配器验签/保存失败均可留下有效子代。父检查与子写入之间没有覆盖撤回的原子围栏。z0 的结果返回 z1 自己的材料；没有旧 i1/i2 的执行状态、来源关系或全前沿收据。

本地必须有同完整 origin 且 RESULT_AVAILABLE 的 source_rid（C01:244—250）。新 gV 无法引用 gA 的 p。每一次新 release/物理机会分别计费；多次重试不获得服务端幂等容量1。

### Revoke / dispose

`POST /api/login/oauth/revoke`，G03:351—393。选择指定材料对应行，然后 ExpireToken：先按该主键置 expires_in=0，再处理同 refresh_token_hash 的正 expiry 行。不同 RT hash 的独立性只适用于此动作；disable/delete user 等账户动作的影响更广。

不存在/不同 client 的 token 可成功返回；已失活行有早返回路径。成功响应本身无法证明所有相关行、迟到创建者或全部 RP 路径关闭。

C03 dispose 对已知 material 先做本地 JWT 验证，再最多三次原生调用：RT revoke、AT UserInfo、AT introspect。C01 只接受 QUARANTINED 材料，须先撤回 gV。前置到期校验失败可使三次调用均未发生；该失败不能自动生成 DISPOSED。仅满足 HTTP200、UserInfo明确拒绝、AT内省false才落到命名材料失活。RT刷新可用性及完整前沿仍需源合同，避免用实际Refresh作免费验证。

## 3. 权限与共享状态结论

基础 lab 中 user 有 grant/revoke/recover/deliver/status，agentA/B 有 call/status（C06）。M6 继承的 IsolationLab 将 user改为 grant/revoke/deliver/status/begin_reconciliation/reconcile/dispose，并分出 recovery身份（C07）。两者的 user 均无 call。新 verifier 身份当前未配置。

所以“管理批准→直接由管理 RPC 执行 Issue/Refresh”存在接口缺口；“管理批准给已配置 caller 的独立新 task/generation→该 caller 代发”在窗口未开、材料/范围/预算满足时具有代码级合法路径。其信任责任见02。

账户 UpdateUser 中，全用户 access 终止由 IsForbidden/IsDeleted 转变且列命中触发（G08:1315起）；通常签到时间/失败次数列本身不触发该条件。元数据变化、未来登录策略和并发覆盖风险仍需列入 frame，不能推成所有状态无副作用。

裁决：原生七类端点能力为限定 `NATIVE_INTERFACE_CONFIRMED`；通用 Controller 诊断投影、未知 Issue、多尝试来源/关闭及有界 Fence 为 `SOURCE_OR_REFINEMENT_GAP`。
