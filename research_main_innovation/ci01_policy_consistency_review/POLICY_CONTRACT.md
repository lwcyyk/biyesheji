# 权限契约与证据等级

## Material Passport

阶段：CI-01 认证上下文与访问控制策略的一致性审计。日期2026-11-05。方法：原生函数原样提取、内存依赖和合成夹具；本轮认证服务HTTP请求为0，真实账户/应用变更为0。辅助分析使用academic-research-suite证据核验流程，无外部同行评审。范围见[REVIEW_SCOPE.md](REVIEW_SCOPE.md)。

冻结Casdoor源码提交为`528a0213f01caf70b9f41009cbf7b2f67bdd67ec`（v4.25.0）。源码快照位于本目录`sources/frozen/`，原路径、函数、行号见[SOURCE_LOCATIONS.md](SOURCE_LOCATIONS.md)。公开文档取得于本轮，属于当时网站版本；其与冻结源码相同的限制逐项对应，其他版本差异保持独立。

## 已可靠确认的限制

**R_CLIENT_BOUND。** 公开官方文档“Dynamic client registration / What a registered client is and may do”明确限定用户经动态客户端取得的token及附带session可调用的API。冻结源码`routers/authz_filter.go:628–635,645–676,691–699`实现同一限制；`Application.IsDynamicClient`在`object/user_util.go:1165–1167`把`dcr`及`cimd`标签都识别为动态客户端。此处的限制来自客户端类别和原生API策略，普通`scope=openid`本身不构成“禁止全部账户管理API”的通用证明。[官方文档](https://github.com/casdoor/casdoor-website/blob/master/docs/application/dynamic-client-registration.md#security-model) [取得原文](sources/public/doc_dynamic.md)

允许集为`/api/userinfo`、`/api/user`、`/api/mcp`、`/api/login/oauth`和`/api/server/`前缀。目标`edit_display_name`映射到策略键`/api/update-user`，该键在允许集之外。携带token的请求会被拒绝；仅带其派生Cookie的请求则清除该受限身份并按匿名请求继续。匿名继续与获得受保护操作权限分别判断。

**R_CROSS_ORG_BOUND。** `routers/authz_filter.go:637–643,701–707`还限制来自其他组织应用的token会话，允许集较小；`/api/mcp`与`/api/server/`在该集合之外。应用属于`built-in`、主体为空或应用型主体时，跨组织判断有显式例外。`built-in`例外只影响该项判断；带`dcr`标记时仍接受动态客户端限制。此项以源码及公开修复记录为依据，本轮未取得同等细化的独立产品文档保证。

**客户端凭据与用户AT分开。** 文档对`app-dcr`客户端凭据还规定一套登录流程权限。当前测试仅使用合成用户AT及其会话，不把客户端secret、Basic管理身份或注册管理token加入夹具。`object.IsAppUser`的例外属于另一主体类型。[文档security-model段](sources/public/doc_dynamic.md) [源码](sources/frozen/object/user_util.go)

## 会话与权限属性

|属性|建立位置|实际用途与边界|
|---|---|---|
|`username`|AutoSigninFilter→setSessionUser，base.go:231–241|用户身份；身份相同不自动提供同样客户端权限|
|`requestCredentialUser`|setSessionUser；authz_filter.go:175|当前请求附带凭据的标记，区分直接拒绝与Cookie清除；属于请求上下文|
|`signinTokenId`|setSessionSigninToken，base.go:243–253|Cookie源token绑定；来源撤销/过期检查依赖它|
|`scope`|setSessionOidc，base.go:296–305|保存在会话中；当前客户端API允许集函数没有读取它|
|`aud`|同上；值来自查询到的`Application.ClientId`|重新取得应用并判断dcr/cimd或跨组织条件；与JWT的resource audience分别解释|
|`Tags`、`Organization`|当前应用记录|受限类型/组织依赖即时应用查询；Cookie没有单独保存这些限制属性|
|`SessionData.ExpireTime`|上游会话属性；getUsername读取|本轮用合成值1表示已过期，源码清除身份；实际会话中间件生命周期另证|

Bearer头路径调用skipSessionPersistence，属性用于本请求；AT查询参数路径可以建立持久会话。转换通过原生setter保存username、scope、aud及源token ID。测试直接调用这些原生函数核对了字段；实际Cookie序列化/文件存储没有执行。`setSessionSigninToken`对已独立登录的同用户且原先无token绑定存在保留分支，应结合独立认证来源解释。[AutoSigninFilter:50–61,112–130](sources/frozen/routers/auto_signin_filter.go) [session_provider.go:173以后](sources/frozen/routers/session_provider.go)

## 预期规则登记

|规则ID|预期与适用域|依据层级|
|---|---|---|
|R_CLIENT_BOUND|源于DCR/CIMD且未取得独立新认证的会话，不能获得edit_display_name权限|官方限制＋冻结源码同义注释/允许集|
|R_CROSS_ORG_BOUND|具有跨组织限制的会话保留相应API上界|源码注释及实际谓词|
|R_NO_NEW_AUTHORITY|合成转换后只移除应用记录，没有调用独立登录setter；源token及身份绑定仍在，禁止管理API的原约束继续用于判定|R_CLIENT_BOUND/R_CROSS_ORG_BOUND的条件性保持要求；夹具事件序列证明未加入新授权。它不规定删除应用后所有公开/允许操作必须怎样响应|
|R_BEARER_APP_LOOKUP|Bearer AT查到token而查不到其应用时拒绝|AutoSigninFilter:112–120显式分支|
|R_SOURCE_ENDS_SESSION|已绑定的源token撤销、过期或缺失时，清除token建立的会话身份|base.go:255–284；官方token文档说明撤销/过期终止其会话；缺失行的处理由源码给出|
|R_SESSION_EXPIRY|SessionData期限已过时不保留认证用户身份|authz_filter.go:getUsername:140–173；官方session lifecycle段|
|R_LOOKUP_ERROR|应用/源token查询错误进入拒绝路径|checkDynamicClientSession及AutoSigninFilter错误分支|
|R_INDEPENDENT_LOGIN|在明确独立认证的前提下，SetSessionUsername清除旧scope/aud/token绑定；后续权限依据新的登录|controllers/base.go:285–296；前提为合成声明，未运行真实登录|
|R_BUILTIN_EXCEPTION|普通built-in应用不因组织差异被此局部规则限制|authz_filter.go:701–707；仍受其他策略约束|
|R_CLIENT_ALLOWLIST_OR_REGULAR_FALLTHROUGH|允许API或普通客户端通过这一局部门槛|isClientSessionApiAllowed；“通过”不单独保证控制器授权|
|M_SELF_POLICY|合成下游策略允许fixture/alice编辑自己的抽象显示名；匿名拒绝|明确的mock前提，属于测试配置，未当成产品全局保证|
|U_APPLICATION_LIFECYCLE|普通应用删除、DisableSignin对全部存量会话/允许API的统一效果|SPEC_UNRESOLVED。所读文档未给覆盖此矩阵的完整合同|
|U_SOURCE_LOSS|aud/来源字段损坏或被删除后的产品统一处理|SPEC_UNRESOLVED；损坏由测试注入，其正常路径可达性未证明|

停用在本轮特指`Application.DisableSignin=true`。`object/check.go:682–687`在登录准入检查中拒绝该配置；当前两个局部token/session函数没有使用这一字段。将它解释为“立即撤销所有既有授权”仍缺依据。动态客户端的管理API上界可独立适用，其他停用单元格保留未决。

## 结论与规范边界

已确认的策略保持要求足以判定M081/B02/B04的局部不一致：完整源绑定、有效会话、无新认证的条件下，应用查询为空使受限身份继续进入下游。完整应用存在时的Bearer拒绝与Cookie匿名继续具有相同的受保护操作结果，属于预期的上下文差异。

缺失应用后的具体错误码、是否同时销毁全部会话、普通客户端授权如何保留，以及来源字段损坏如何处置，仍需产品规范进一步明确。60格/边界观察使用SPEC_UNRESOLVED，不计为已验证产品契约。

官方scope文档说明服务需要检查相应scope；本轮只审查客户端类型API约束。JWT签名/issuer/audience验证、其他RP以及token的`resource`绑定未被本矩阵全面审计。[scope文档](sources/public/doc_scopes.md) [token文档](sources/public/doc_token.md)
