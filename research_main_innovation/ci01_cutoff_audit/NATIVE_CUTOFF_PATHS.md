# 原生截止路径审计

## Material Passport

源码S=`D:/毕业设计/research_main_innovation/ci01_cutoff_audit/sources/casdoor-v4.25.0/`，版本与摘要见[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)及[补充清单](ADDITIONAL_SOURCES.json)。本地新采样E=`raw/run01/http_and_events.jsonl`，历史采样H=`D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/`。全部推导保留非原子边界，数据库隔离不补成跨HTTP事务。

## 接口—效果—代价

|路径|入口/权限及授权流程|实际作用范围|并发与迟到插入|对B、成本、信任|证据|
|---|---|---|---|---|---|
|轮换password刷新|POST `/api/login/oauth/refresh_token`；也可用access_token grant_type=refresh_token；client_id+RT，secret可省略|新增AT/RT行后删除父；SessionId从父继承|父读取/用户验证、插入、父删除分开；已读取快照可继续|1请求，1新材料组；B另行不受此删除影响|S/object/token_oauth_util.go:562–787；H/run02_secretless；C11专用入口|
|非轮换刷新/同hash撤销|应用disableRefreshRotation=true；同上刷新；revoke(token)|子行保留原RT字符串和RT自身exp；ExpireToken先更新定位行，再更新相同hash活跃行|批量更新后仍可能插入同hash行；重复RT查找未指定排序，命中旧失效行会提前返回|F_closed下每A共享组1次撤销；B不同hash保持；无需新增服务组件|S/object/token_oauth_util.go:351–393,713–769；C10实测|
|逐记录管理删除|POST `/api/delete-token`，管理/获准应用权限需具体映射；本轮用管理会话|按owner/name/organization删除指定行|已经读取的刷新快照仍可插入子行|每行1请求；附加管理权限同等赋予强对照；不自动解决后代来源|S/controllers/token.go:159以后；S/object/token.go:267–273；C12实际可用|
|按session关闭|POST `/api/delete-session[?sessionId=...]`，管理作用域；或本人logout/sso-logout|非空sid匹配行置0，再删除/销毁会话；缺失session时有早返回分支|refresh校验没有sid存在性检查；先读取后插入可产生迟到行；再调用删除可能找不到session|B须另一独立sid；登录/批准/session单位及等待计入；原password sid为空|S/controllers/session.go:136–159；S/object/session.go:DeleteSession/DeleteSessionId；S/object/token.go:293–333。新原生会话实验未跑|
|用户范围失效|update-user isForbidden=true；delete-user；本人sso-logout默认all|该user的token与会话；禁用还在后续user检查拒绝|已读用户快照可能先插入，后续资源用户检查仍拒绝；全用户logout只做行失效则保留竞态|同账户B受损；本轮用户禁用在区间结束后作清理|S/object/user.go:terminateUserAccess；S/controllers/account.go:577–691；run01清理|
|应用范围行失效|内部ExpireTokenByUserAndApplication，经HandleLoggedIn的exclusive signin/maxSessions条件调用|该用户该应用当前行|新登录/刷新插入和范围更新分离；新登录自身在范围更新后发行|同应用B受影响；启用排他登录是新profile，增加登录调用与批准|S/controllers/auth.go:202–205。缺少独立通用expire-app端点，内部函数不计获准接口|
|移除refresh grant|POST update-application，更改新应用grantTypes|access_token总入口检查grant列表|专用refresh_token入口直接调用RefreshToken；C11确认仍刷新成功|1配置变更＋读回；同应用B刷新也受配置约束；覆盖全部入口的前提未满足|S/object/token_oauth.go:75–121；S/controllers/token.go:444–485；E/C11|
|删除独立A应用|POST `/api/delete-application`，body owner/name/organization，管理权限|删除application行；Bearer准入和新刷新需要当前application；token行仍在|D前读取Application的刷新可迟到插入；D后新Bearer仍查app；已有Cookie另走分支|两个应用至少两份配置/授权支持；B另应用保留；禁止退休标识再用；删除权限计入双方|S/object/application.go:598–612；S/routers/auto_signin_filter.go:112–120；E/C11|
|轮换secret|update-application clientSecret，管理权限|只覆盖校验该secret的请求；authorization_code/token-exchange刷新需要secret|已验证请求仍可继续，原password省secret路径继续可用|共享secret改变会影响B；若声称完全中介需覆盖所有材料|S/object/token_oauth_util.go:772–787；未新测secret轮换|
|期限限制|应用ExpireInHours/RefreshExpireInHours，创建/更新获准配置|AT以生成时间签名exp；userinfo还使用CreatedTime+ExpiresIn；轮换RT从本次生成时间续期；非轮换保留原RT.exp|RT验证至CreatedTime/插入之间延迟需要计入；无额外请求时限难给统一完成界|等待E+δ+L_A，B续期另计；0回退AT期限，负期限不作为有用保留配置|S/object/token_jwt.go:634–640；S/util/time.go:61–66；C10固定RT字段观测|

## 扩展路径的闭包检查

**AT→Cookie。** Bearer头调用触发skipSessionPersistence；accessToken/access_token查询参数走可持久化会话路径。Cookie-only请求通过clearSessionOfRevokedToken检查源token的行与期限；checkDynamicClientSession在app=nil时继续。C11中当前源AT建立Cookie、删除A应用后，Bearer拒绝且Cookie userinfo仍返回同一用户。删除应用单动作只覆盖特定路径。[S/routers/auto_signin_filter.go:50–61,134；S/routers/base.go:255–273；S/routers/authz_filter.go:647–675；E/C11]

Cookie清除需要源token失效/删除、会话处置或到期等现有能力。只要所有Cookie仍绑定已知源token且没有跨路径再授权，逐源处置可以覆盖；Cookie建立之前/之后跨应用授权的完整闭包仍须单独核验。C11没有尝试修改账户、建立用户新秘密或换取其他应用材料，因而本轮不把这些可能性写成实测攻击。

**授权码、PKCE及token exchange。** authorization_code在IsGrantTypeValid中直接允许；去掉grant列表项不等于禁用整个授权流程。代码交换在存在PKCE时允许省略client_secret；code本身有使用标记及相关前提。refresh的secret规则根据记录的GrantType处理。常规token exchange需要调用方secret，federated credential分支更早分流。是否有已可达代码/PKCE/联邦凭据，需要按实际账户能力冻结，当前没有对全接口建立不可达证明。[S/object/token_oauth_util.go:254–263,772–787；S/object/token_oauth.go:169–246,815–969]

**动态注册及其他再发行。** object/oauth_dcr.go:73–92按组织DcrPolicy检查。config01实际读取l1-study为disabled，本组织新增DCR客户端路径据此关闭。当前模板guest/sign-up关闭，用户密码、验证渠道和私钥属于可信方，A没有这些初始能力；服务内是否可由现有会话改变这些能力尚未完整审计。device_code由控制器完成额外验证后分派，源分派函数本身不能当成对手免费新授权。完整SSO/浏览器认证、其他RP和离线JWT保持独立范围。

## 本轮可核实的反例与成功

C10撤销前四个AT均接受，撤销后A0/A1/A2拒绝、B0接受，旧A RT刷新拒绝；三个A AT共享同一RT与RT.exp。C11去掉refresh grant后总入口返回unsupported_grant_type，专用入口发行新pair；删除A应用后两刷新入口拒绝，Bearer拒绝，Cookie仍接受，B保持。C12在name升序下页间删除导致一个仍存在的行漏出遍历，撤销后该失效行仍在列表。这些均由离线检查器从事件投影重算。[独立核对](EVIDENCE_AUDIT.json)

长期RT期限终止、服务端强制暂停竞态、独立原生session profile及完整派生闭包尚无新运行证据。历史199 HTTP与52/576原生结果维持原始版本范围，不并入本轮88 HTTP。
