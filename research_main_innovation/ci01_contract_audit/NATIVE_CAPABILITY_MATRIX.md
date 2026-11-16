# 原生能力、权限与代价

本轮冻结Casdoor 4.25.0，实际运行文件与既有发行ZIP中的casdoor.exe摘要一致。公开源码固定于提交528a0213f01caf70b9f41009cbf7b2f67bdd67ec。源码推导以该版本对应关系为前提，完整可复现构建证明仍待补齐。[实测环境锁](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/environment.lock.json)

|源码标识|位置与相关函数|
|---|---|
|S1|object/token_oauth_util.go，RefreshToken、RevokeToken、ExpireToken。[源码](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token_oauth_util.go)|
|S2|controllers/token.go，RefreshToken、RevokeToken、IntrospectToken。[源码](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/controllers/token.go)|
|S3|routers/auto_signin_filter.go、controllers/account.go，Bearer准入与GetUserinfo。[过滤器](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/auto_signin_filter.go) [接口](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/controllers/account.go)|
|S4|object/user.go，isUserAccessRevoked、terminateUserAccess、DeleteUser。[源码](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/user.go)|
|S5|object/token.go，Token、GetTokenByRefreshToken、GetTokenByTokenValue。[源码](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token.go)|
|S6|routers/session_provider.go，skipSessionPersistence与lazySessionStore。[源码](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/session_provider.go)|
|S7|object/token_oauth.go，password grant发行路径。[源码](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/object/token_oauth.go)|
|E1|run01，307条原始事件、29个独立接受检查、两个新建用户。[原始日志](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/http_and_events.jsonl)|
|S8|authz/authz.go的IsAllowed及routers/authz_filter.go的organizationParamObject。[授权规则](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/authz__authz.go) [对象作用域](D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/routers/authz_filter.go)|
|E2|C01两步无client_secret刷新与父撤销。[原始记录](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run02_secretless/http_and_events.jsonl)|
|E3|C02普通Bearer与应用Basic凭据的同范围只读查询。[原始记录](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run03_listing/http_and_events.jsonl)|

## 能力审计

|前提或能力|提供者与接口|证据|代价|分类|结论|
|---|---|---|---|---|---|
|为当前账户发行新材料|AS password grant|S7及E1的A0/B0/B1实际发行|每次1个原生HTTP请求，另需密码及客户端资格|已有原生能力|同账户可取得不同token记录，任务批准代次未进入原生参数|
|刷新既有RT|AS refresh_token|S1创建新Token，轮换开启时删除旧Token，E1 seq166—168|每次1请求，产生新的AT/RT及处置工作|已有原生能力|本轮新后代A1与A0具有不同原生记录|
|持有RT而缺少client_secret仍刷新|当前password grant profile|S1 checkRefreshClientSecret及E2两次200，无Authorization头和client_secret字段|每次1请求，仍产生新的处置义务|已有原生能力|保管client_secret不能单独构成此类RT的发行围栏|
|撤销已知材料对应记录|AS revoke|S1按token值查记录，ExpireToken置expires_in=0，并处理同refresh_token_hash记录|每次1请求|已有原生能力|正常A0与已知A1撤销后，其AT/RT检查均拒绝|
|通过已消耗旧RT定位整个后代族|当前token-specific revoke|S1轮换后旧记录删除，未知token可返回200，E1 seq173之后A1仍接受|现接口没有可核实的族查询/族撤销句柄|需要提供方改造|若要求该接口单次保证完整派生族失效，所需持久谱系/族状态在本profile中缺失|
|新鲜资源准入|GET /api/userinfo，Bearer且无Cookie|S3检查token记录、过期、用户状态，E1真实200/401与sub匹配|每次1资源HTTP请求|已有原生能力|支持该特定资源路径上的接受结论|
|只凭离线JWT判断撤销|既有签名/issuer/audience/期限检查|E1所有29次签名检查通过，其中多项在线已拒绝|本地验证，无原生HTTP|当前证据不足|签名有效性不能提供当前撤销新鲜度|
|使旧任务无法借新批准发行|当前批准存储与可信客户端入口|原生参数不含任务/批准代次，取证仅记录实验g0/g1|至少维护任务—批准映射，每次发行前检查，持久性另计|可由现有客户端机制实现|属于强组合的客户端责任，当前实验未验收其部署|
|恢复后抵抗旧有效批准快照|独立近期锚点或防回滚存储|旧快照双历史纸面控制，当前无该控制器实现|可信单调状态，或恢复时独立新鲜查询/见证|需要额外可信组件|本机AS的同账户认证不能代替本地任务批准新鲜度|
|原子改换支持且同步关闭旧支持|原生任务级rebind|S1/S7仅提供刷新与发行，实验B1是独立发行|当前没有对应原子接口实测|当前证据不足|A8不能由B1登录成功推定|
|同一发行请求的重试返回同一结果|password grant的操作幂等|S7生成新记录，A0/B0/B1使用同类输入而记录不同，未见调用者提供的幂等键|需要受信客户端账本，跨AS提交还需可对账结果或原生幂等接口|需要提供方改造|完整受控幂等契约尚不能由当前发行端点实例化|
|结果丢失后证明无效果并阻止迟到提交|提供方terminal lookup/no-effect/delivery fence|已查操作未提供与调用者attempt绑定的终态或fence收据|增加提供方协议，或保留未决，或采用范围更大的处置|需要提供方改造|AID-Guard的安全后继条件当前缺少原生支撑|
|全测试账户强制下线|管理API isForbidden=true及删除用户|S4调用ExpireTokenByUser与会话清理，E1清理后全部已知材料在线拒绝|每账户2个变更请求＋1个删除确认|已有原生能力|本轮作为终点后清理。若用于中途收尾，会影响B持续可用|
|枚举本次用户token记录|GET get-tokens，应用client_id/secret的Basic认证|S8及E3，普通Bearer未获数据，应用凭据返回A1/B0的AT与RT句柄|每页至少1请求、O(n)输出，应用凭据及管理动作批准|已有原生能力|无需额外built-in/admin口令即可进行已测查询。原运行者批准集合仍需明确扩展，评分数据保持隔离|

“需要提供方改造”针对当前冻结接口下的特定保证。某个更弱保证可以有同接口替代路径，替代关系见下表。尚未调用或映射的原生接口保持独立状态。

## 同接口与扩展能力下的替代

|目标缺口|替代方案|资源与信任增加|适用结论|
|---|---|---|---|
|迟到结果尚未交付|等待已登记请求完成，收到A1后撤销其RT|本例额外1个方法revoke请求，另存1项pending记录和来源映射|已实测该实例终点成功，等待期间保持未决|
|有限多个在途结果|可信客户端登记全部pending，停止新A发行，交付后逐个撤销|O(m)待处理记录，至多每个成功结果1次撤销，另计核验请求|条件性纸面充分性，前提包括清单完整和结果最终可取得|
|丢失未知后代句柄|应用凭据枚举，结合已知合法材料清单寻找待处置记录|管理动作批准、O(n)列表、逐项处置及来源判定，当前应用凭据已有所需原生权限|枚举能力已测。丢响应恢复决策未实现，记录自身缺少任务代次时仍需可信来源账本|
|无法逐族定位|全账户禁用，随后按新批准恢复B|中断B，至少禁用/恢复管理动作及B新发行，具体时间待测|不满足本轮B持续可用合同，属于另一合同|
|原生不识别任务根|可信客户端从初始时刻保管RT等可再授权材料，并检查当前批准|每次调用检查，持久批准与pending账本，恢复时可信新鲜度|既有中介机制可承担。已泄漏RT的当前对手仍可无secret刷新，原有泄漏需另行处置|
|对手可绕过客户端继续派生|AS持久family/root代次，发行提交及资源准入检查同一退役状态|原生记录字段、持久原子状态、每次相关准入检查|需要提供方能力或更强中介覆盖，已有根范围理论有对应前提|
|声明目标允许等待到期|等待全部相关材料到期，且无续期/再发行路径|期限约束与等待成本，需完整后代和RT期限界|当前有界即时收尾不能免费使用此替代|
|需要原生会话范围|使用能够建立独立原生会话的其他授权流程，并映射会话处置|额外登录/批准、会话隔离及提供方接口核验|源码存在按session ID过期token的函数。本次password记录的session ID为空，另一流程的并发闭包和B保持仍待实测|

## 本轮实际费用与清理

主见证与正常控制使用117次本机HTTP。两个源码驱动补充分别使用50次和32次，累计199次。其中方法24次、独立测量140次、配置/建户20次、清理15次，均在初始分类预算内。测量包括44次AT内省、44次RT内省、44次userinfo、6次发现文档/JWKS及2次权限查询。另有22次采样数据库查询、4次清理后只读核对和44次本地签名检查。[逐操作计费](D:/毕业设计/research_main_innovation/ci01_contract_audit/COST_ACCOUNTING.json)

四个新建用户均已删除，14组已知AT/RT对在各自清理后全部内省false且userinfo拒绝。运行后应用配置读回一致。JWT离线签名在采样窗口仍通过，其期限及线下复制不由本轮在线清理改变。新采样账户和原始结果均与历史批次分离。[主批次](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/result.json) [无secret补充](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run02_secretless/result.json) [权限补充](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run03_listing/result.json) [独立核对](D:/毕业设计/research_main_innovation/ci01_contract_audit/EVIDENCE_AUDIT.json)

费用统计覆盖采样器发往原生服务的请求，提供方内部数据库工作及回调网络流量尚未逐项计量。若强对照把本轮测量接口用于执行选择或发放承诺，相应请求应计入它的方法费用。当前199次属于取证总账，不能用作候选与基线的性能比。

清理后只读核对还发现四个测试用户名下合计保留10条token记录，expires_in均为0，session_id均为空。这些行按原生策略失效留存，清理结论使用在线不可接受性与用户删除状态。[清理后记录](D:/毕业设计/research_main_innovation/ci01_contract_audit/POST_CLEANUP_DB.json)

表中原生能力不足的结论限定于冻结操作与已审查接口。C02已经说明，当前凭据可能拥有比原方法使用范围更广的原生权限。更广管理配置能否给出兼容B持续可用的原子族围栏，尚未完成穷尽性审计。
