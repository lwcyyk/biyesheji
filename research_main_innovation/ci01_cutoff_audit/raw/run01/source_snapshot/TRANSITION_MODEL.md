# 源码约束的最小转移规格（采样前冻结）

## Material Passport

阶段：CI-01 可枚举派生材料的选择性截止能力核验。初始规格日期：2026-11-05。证据类型：纸面规格及冻结源码推导；采样结果另存 raw。研究对象为 Casdoor 4.25.0，commit `528a0213f01caf70b9f41009cbf7b2f67bdd67ec`。来源根 S 为 `D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/`。候选机制实现门保持关闭。

## 合同与时点

当前批准 A:g0 停止、B:g1 继续由可信且最新输入固定。A 持有自身 AT、RT、公开 client_id，可以直连两个原生刷新入口；密码、客户端 secret、B 材料与管理会话保存在可信操作者处。secret 持有者、完全托管者分别属于其他 profile。恢复与回滚新鲜度留作后续依赖。

截止请求时点 c 是控制方停止意图；完成承诺 q 是控制方已取得所有所需终态依据的时点。API ack 只确认所调用的原生操作。区分五个谓词：K（已知清单失效）；P（c 前全部 A 材料失效）；N（q 后无法由 A 旧支持产生在声明资源路径有效的后代）；R（q 后新发起的声明资源请求均拒绝 A 闭包）；B（整个声明区间内 B 的获准路径持续可用）。q 前已通过服务器接受点的请求可迟到响应，额外 drain 合同需要额外证据。

主资源 R_bearer 是无 Cookie、仅 Bearer AT 的 `/api/userinfo`，以及两个 refresh 入口的有效新材料获取。扩展资源 R_cookie 另包含 AT URL 参数建立的 Cookie-only `/api/userinfo`。离线 JWT、其他 RP、ID token 的登录路径属于独立资源合同。完整 A 后代闭包必须与获准攻击接口集合一起定义；扩大接口集后重新审计。

B 保持以原生效果不交叠、无外部配置变更、期限覆盖区间为前提。离散检查支持所测切点，连续性由限定转移模型条件性论证。若 B 需要续期，调用、批准和等待都计费。用户/账户相同与批准来源相同分别判断。

## 状态

`s=(time, apps, userActive, records, cookies, pending, localOrigins, approvals, budget)`。
记录包含 id、app、user、AT、RT/hash、expires_in、created_time、RT.exp、sessionId、grantType。pending 保存每请求已经读取的旧记录、应用与用户快照及程序计数器。localOrigins 为可信来源账本，原生记录没有任务批准代次或父记录字段。方法观察是获准 API 返回及自身记录；评分器 DB 内容保持独立。UNKNOWN 保留待决，预算耗尽给 INCONCLUSIVE；本轮采样器不输出规划器 IMPOSSIBLE。

## 微步骤与定位

|转移|守卫与效果|冻结源码定位|
|---|---|---|
|F0|读取应用；通用 access_token 入口检查 grantTypes；专用 refresh_token 入口 ValidateOAuth(true)|S/controllers/token.go:444–485；S/object/token_oauth.go:27–121|
|F1|按 RT hash 取一条记录，缺失/失效拒绝，校验 client、resource、secret、DPoP|S/object/token_oauth_util.go:585–630；S/object/token.go:GetTokenByRefreshToken|
|F2|验证 RT JWT 期限，取用户并检查 active；保存本次读取结果|S/object/token_oauth_util.go:632–703；S/object/token_jwt.go:815–854|
|F3|生成子 AT/RT；非轮换时 RT 值保留为父值|S/object/token_oauth_util.go:705–717；S/object/token_jwt.go:634–640|
|F4|插入子记录，继承 sessionId；插入前无父状态/应用状态/会话截止代次重检|S/object/token_oauth_util.go:719–741|
|F5|轮换开则删除父记录；轮换关保留父；随后返回|S/object/token_oauth_util.go:752–769|
|V0|按句柄查行；未知值/其他应用/已失效行的成功返回均不能证明派生族关闭|S/object/token_oauth_util.go:RevokeToken|
|V1/V2|选定行 expires_in=0；再将相同 RT hash 的活跃行置0，保留两个更新间插入窗口|S/object/token_oauth_util.go:ExpireToken|
|E0/E1|count 与 offset/limit SELECT 是独立调用；页间可以插入删除；默认 created_time 排序|S/controllers/token.go:37–70；S/object/ormer_session.go:GetSession|
|S0/S1|按 session/user/app 范围置0，再销毁/删除会话；已读取的刷新仍可继续 F3–F5|S/object/session.go；S/object/token.go:282–333|
|D|管理员删除本轮新建应用；删除语句本身只删 application 行|S/object/application.go:598–612；S/controllers/application.go:DeleteApplication|
|U|Bearer 读 token/期限/user/app；app 缺失拒绝，随后生成本请求的 userinfo|S/routers/auto_signin_filter.go:63–131；S/controllers/account.go:781–803|
|C|AT 查询参数可以持久化 session；Cookie 路径检查源 token，app=nil 的动态会话检查允许继续|S/routers/auto_signin_filter.go:50–61,134；S/routers/base.go:255–273；S/routers/authz_filter.go:647–675|

非轮换 RT hash 有多个匹配行，Get 未指定排序；纸面模型保留所有可能匹配行。删除应用可阻止后来的 Bearer/app 读取及新刷新应用读取；D 前通过检查的旧请求和 Cookie 路径分别处理。grantTypes 移除只覆盖检查该字段的入口。内部函数的存在不自动成为方法接口。

## 输入族与调度

F_closed：停止新派发后没有新增 A 操作，完整登记的在途结果有限且最终可归属；稳定枚举范围内记录最终停止插入/删除/改序，A/B 撤销效果互不交叠。可枚举句柄和来源正确性分别要求。若其他 B 请求会改变同一分页范围，先取得同一 SELECT 的完整结果或提供排序稳定/范围隔离条件。

F_active：A 可直接刷新，控制方只能使用本 profile 冻结接口，B 持续可用。基准包括同应用轮换、同应用非轮换、独立会话、独立应用、完全托管等不同配置机会。两个方法获得同样权限、信息、批准、单位预算与等待预算。

默认每个开始的请求最终结束，弱公平、非 Zeno、有限并发上限 C；这些条件不提供统一墙钟时延。声称时间界时另假设每请求相关验证至插入/完成的延迟 ≤ δ、服务器时钟可靠、AT 最大有效期 L_A。任意长度轮换轨迹需每轮在 RT.exp 前完成下一次验证、正的生命周期、总时间随轮数发散；只在控制策略逐项追赶且无持久截止时给出条件族，保留控制方每轮完成的事件。

## 采样前明确的命题

T1：无在途刷新时，非轮换同 RT 的多个 AT 可由一次撤销共同失效且 B 独立 RT 保留。

T2：移除应用 refresh_token grant 后，两个刷新入口的结果可能分歧。

T3：独立应用 A 删除后，A 的新 Bearer/refresh 请求拒绝、B 保留；既有 AT-derived Cookie 可能仍有效。广义截止由两类资源分别裁定。

T4：稳定 name 升序也无法避免页间删除导致 offset 漏项；失效记录仍参加列表。

T5：非轮换 RT 的 exp 固定；轮换 RT 的期限按本次生成时间更新。有限 expiry 的源约束可由 JWT 字段与源码核对，长时间原生等待实验本轮可免除。

T1–T5 的取证仅包装现有 API。有限交错检查只验证以上已声明的转移命题，输出标记 PAPER_MODEL_CHECK，不实现截止机制。
