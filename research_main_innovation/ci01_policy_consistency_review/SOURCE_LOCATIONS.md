# 源码位置与原样提取说明

## Material Passport

冻结提交：528a0213f01caf70b9f41009cbf7b2f67bdd67ec（v4.25.0）。以下行号采用冻结原文件的一基行号；提取文件的偏移与SHA256另见SOURCE_EXTRACTS.json。30项为函数及常量/变量声明的提取数量，不能解释成30项一般性质证明。

## 编译进离线包的原样声明

|原文件与声明|行号|本轮副本|原文件SHA256|
|---|---|---|---|
|[routers/authz_filter.go::dynamicClientApis](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:630)|630–635|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::crossOrgClientApis](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:639)|639–643|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::requestCredentialUserKey](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:175)|175–175|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::checkDynamicClientSession](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:647)|647–676|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::isRestrictedClientSession](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:678)|678–689|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::isClientSessionApiAllowed](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:691)|691–699|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::isCrossOrgClient](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:701)|701–707|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::getUsername](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:140)|140–173|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::getSubject](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:195)|195–207|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/authz_filter.go::isCrossOriginCookieRequest](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go:177)|177–193|[副本](sources/frozen/routers/authz_filter.go)|`29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`|
|[routers/auto_signin_filter.go::AutoSigninFilter](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/auto_signin_filter.go:28)|28–176|[副本](sources/frozen/routers/auto_signin_filter.go)|`474a1cf52684d48dd934c054cde3611392361d80e27afe725df7b6399eafe489`|
|[routers/base.go::getSessionUser](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:222)|222–229|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/base.go::setSessionUser](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:231)|231–241|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/base.go::setSessionSigninToken](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:243)|243–253|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/base.go::setSessionOidc](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:296)|296–306|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/base.go::clearSessionOfRevokedToken](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:255)|255–273|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/base.go::clearSessionOfToken](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:276)|276–285|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/base.go::parseBearerToken](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/base.go:308)|308–322|[副本](sources/frozen/routers/base.go)|`44b136b8449f14a5c01041935337d4bf995d0c6553c5328a9bae8c670d4fda41`|
|[routers/session_provider.go::skipSessionPersistence](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/session_provider.go:160)|160–166|[副本](sources/frozen/routers/session_provider.go)|`8355235845ca5c9ff5511cd1d089b5d134b9064ca7f944ab42decfde2e221db0`|
|[object/user_util.go::IsDynamicClient](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/user_util.go:1165)|1165–1167|[副本](sources/frozen/object/user_util.go)|`664597a47c81ee1c59e096e9f2cb2acfa2c3377e76f973cd620da401969d67a1`|
|[object/user_util.go::IsAppUser](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/user_util.go:1132)|1132–1137|[副本](sources/frozen/object/user_util.go)|`664597a47c81ee1c59e096e9f2cb2acfa2c3377e76f973cd620da401969d67a1`|
|[object/token.go::SessionSigninTokenId](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token.go:26)|26–26|[副本](sources/frozen/object/token.go)|`32f9fc3bc7c24aa77071cc9de9b63b83e26163329cee7ad396a0f18273e7aa5a`|
|[object/token.go::GetId](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token.go:208)|208–210|[副本](sources/frozen/object/token.go)|`32f9fc3bc7c24aa77071cc9de9b63b83e26163329cee7ad396a0f18273e7aa5a`|
|[object/token.go::IsUserActive](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token.go:123)|123–137|[副本](sources/frozen/object/token.go)|`32f9fc3bc7c24aa77071cc9de9b63b83e26163329cee7ad396a0f18273e7aa5a`|
|[util/time.go::IsTokenExpired](D:/毕业设计/research_main_innovation/ci01_cutoff_audit/sources/casdoor-v4.25.0/util/time.go:61)|61–67|[副本](sources/frozen/util/time.go)|`59feb4914fe41a90aaeb47c4ddced862d8f13a7f54ba8b298c63ee3685d89fc9`|
|[util/string.go::GetId](D:/毕业设计/research_main_innovation/ci01_cutoff_audit/sources/casdoor-v4.25.0/util/string.go:189)|189–191|[副本](sources/frozen/util/string.go)|`b644c3a8ec3a6579150eccb67e53d55ae4a33d92fa0a2110554145155908334c`|
|[util/string.go::GetOwnerAndNameFromIdNoCheck](D:/毕业设计/research_main_innovation/ci01_cutoff_audit/sources/casdoor-v4.25.0/util/string.go:142)|142–145|[副本](sources/frozen/util/string.go)|`b644c3a8ec3a6579150eccb67e53d55ae4a33d92fa0a2110554145155908334c`|
|[util/string.go::GetOwnerAndNameFromIdWithError](D:/毕业设计/research_main_innovation/ci01_cutoff_audit/sources/casdoor-v4.25.0/util/string.go:124)|124–131|[副本](sources/frozen/util/string.go)|`b644c3a8ec3a6579150eccb67e53d55ae4a33d92fa0a2110554145155908334c`|
|[controllers/base.go::SetSessionUsername](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/controllers/base.go:286)|286–289|[副本](sources/frozen/controllers/base.go)|`48ec0abac416973d49af0abdd80cf6f4e2a282cef8776e65cb7ce7800a7cf6e6`|
|[controllers/base.go::clearSessionOidc](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/controllers/base.go:292)|292–296|[副本](sources/frozen/controllers/base.go)|`48ec0abac416973d49af0abdd80cf6f4e2a282cef8776e65cb7ce7800a7cf6e6`|

## 只读追踪、未作为完整组件执行的入口

|文件|函数/范围|用途|
|---|---|---|
|[main.go](sources/frozen/main.go)|117–120，过滤器注册|认证、超时、API策略的调用顺序|
|[routers/authz_filter.go](sources/frozen/routers/authz_filter.go)|ApiFilter:520–625|策略门槛先于主体读取；后续authz与对象检查|
|[authz/authz.go](sources/frozen/authz/authz.go)|IsAllowed:161–231；userObjectApis:237以后|最终Casbin/用户/API权限，本轮下游使用mock|
|[controllers/user.go](sources/frozen/controllers/user.go)|UpdateUser:266–380及后续|抽象操作对应的真实控制器；本轮未调用|
|[object/user.go](sources/frozen/object/user.go)|userSelfColumns:894以后；FilterUserSelfColumns:926–937|display_name在self字段集合，完整业务许可另证|
|[object/check.go](sources/frozen/object/check.go)|CheckApplicationSignin:682–687相关分支|DisableSignin限制登录准入|
|[routers/session_provider.go](sources/frozen/routers/session_provider.go)|lazySessionStore::SessionRelease:143以后|持久化/ephemeral语义；本轮会话存储仅用内存mock|
|[routers/timeout_filter.go](sources/frozen/routers/timeout_filter.go)|TimeoutFilter:48以后|独立的空闲超时层，本轮未执行|
|[controllers/auth.go](sources/frozen/controllers/auth.go)|checkApplicationSignin:122–129；HandleLoggedIn:149以后|独立登录setter的调用前提|

## 测试适配边界

提取器使用Go parser的声明起止字节，保留函数体与声明文本，替换导入路径到内存依赖。原生策略函数未编辑。审核器逐段核对源文件摘要、提取片段摘要和输出字节偏移。依赖mock保存在offline/mock*，响应适配与下游self策略位于offline/routers/adapters_test.go。

测试包含原样AutoSigninFilter、主体读取及客户端门槛；token/app/user数据库查询采用内存map，session为内存对象。独立登录控制仅调用原样setter，并显式假设新认证已完成。完整Casdoor要求Go1.26.0/toolchain1.26.10；当前提取子集以本机Go1.20编译。完整产品构建与全框架依赖未运行。

审计脚本没有调用现有providers适配器；旧collect_cutoff.py仅作只读来源核对。全部输入与生成物在本目录留档，原历史文件保持原字节。
