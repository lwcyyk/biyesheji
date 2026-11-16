# DCL-R3：授权入口与NativeCreationCut

2026-11-10。固定源码同NC审计。输入范围：所列OAuth、session及管理路径；其他grant/恢复/管理员入口若未纳入实际部署目录，完整截止结论保持UNKNOWN。

## 1. 入口矩阵

|入口/分支|客户端/用户材料与secret|GrantTypes/scope/原生状态|创建/控制与泄露调用|
|---|---|---|---|
|access_token统一入口|client_id及对应grant材料；Secret要求由分支决定|token_oauth.go:75–81查GrantTypes；各分支查scope/状态|可发行/刷新；两个刷新入口均需纳入目录|
|专用refresh_token|client_id、RT；ValidateOAuth(true)，后由checkRefreshClientSecret判secret；DPoP按原绑定|controllers/token.go:471–477；refresh:563只验grant_type字面值，未执行统一入口的GrantTypes守卫；scope不得扩张、RT/用户/cert等检查|RT泄露且其他前提满足时可创建子行；只关闭统一入口留下此路径|
|password grant|client_id、用户名/密码，另查MFA/登录政策；该分支未以client_secret作为密码登录必需条件|统一入口grant允许；token_oauth.go:290–342查scope和身份|已泄露密码可重新登录；撤销某RT不撤销密码|
|authorization_code兑换|client_id、有效code；无PKCE通常须正确secret；有PKCE验证code_verifier且允许省secret，已给secret仍要匹配|token_oauth.go:169–286查app/resource/code时效，claimAuthorizationCode作单次CAS|此CAS只约束code兑换，不能自动赋予RT刷新CAS|
|RT刷新：存储GrantType在认证列表|RT及当前secret（或ValidateClientAssertion形成对应认证状态），DPoP另查|checkRefreshClientSecret:776–787；列表含authorization_code/token-exchange|secret轮换可阻断之后尚未通过检查的相应分支；已缓存app/secret的旧调用仍单列|
|RT刷新：存储GrantType不在列表且省secret|client_id、RT、必要DPoP；secret可空|同函数直接通过secret检查；其他RT/JWT/app/user/scope检查仍执行|password来源RT属于可省secret的冻结路径；仅轮换client_secret不足以截止|
|RFC7009 revoke|client_id、token/hint，必要secret按记录grant/PKCE条件|核匹配行app归属；unknown/已inactive兼容200|期限化行与同RT哈希当前行；不终态化在途handler|
|introspect|ValidateOAuth(false)要求对应客户端认证；token/hint|DB行、ExpiresIn、JWT/user/app等|只读当前活性，不能产生刷新已被尝试或未来创建截止证据|
|Session/UserInfo|header AT或Cookie/session身份；header路径有DPoP约束|AT行与期限/user/app；Cookie另含session及旧token检查|UserInfo为读取；登录会话可能参与后续授权码/新登录，须按实际目录建边；退出某session不等于全账户关闭|
|Session/GetAccount缺Token分支|已通过RequireSignedInUser与路由权限、GetSessionToken为空|controllers/account.go:701–761；object/token_oauth.go:1026–1040、584–625|GetAccessTokenByUser→GetTokenByUserWithAuth→AddToken，可新建AT/RT/ID行；该条件分支不能按HTTP GET一概当成只读|

精确字段修订：名义OAuth grant与数据库Token.GrantType分开。getUserGrantToken:367–382未填写GrantType，初始password路径可保持空串；统一出口更新也未把它改成password。GetOAuthCode:530–548初始未填，authorization_code兑换在提供非空secret时才赋值authorization_code（283–284）；public PKCE分支可保留空串。refresh继承原记录GrantType。secret判定必须读实际字段和路径，禁止仅凭名义grant标题推断。

GetAccount为本轮从会话使用链新定位的条件创建入口；本轮未执行该分支，实际可达性依鉴权和session状态。它不改变UserInfo只读结论。CD25-BOUND若已用固定可信适配器排除此入口，可引用该强制限制；CD25-LEAK持AT/Cookie能绕行时必须把它纳入能力图或给出不可达证据。

## 2. 定义

给定Provider版本p、退役来源范围r、接受入口集合E、环境/权限合同A与因果前沿b，定义：

`NativeCreationCut(p,r,E,A,b) ⇔ 对每条与b前观察一致且满足A的延伸τ，b之后没有在E内新提交的、由r的历史/派生/在途能力支持的原生材料单位。`

提交点在本例取Token Insert成功产生原生行。生成JWT字符串、客户端收到回复、Q本地撤回各用自己的事件。定义覆盖已发未到与已读有效副本，不把它们从延伸集合中删去。若声明的是“禁止新授权接受”，须另命名并选该接受方实际LP。

## 3. 必要条件与充分条件

必要性是相对允许动作和环境而言：只要还存在一个可执行的入口＋足够历史材料，或一个已通过全部检查且可继续Insert的handler，环境就能选择它，强CreationCut失败。NC1/2给出了后一类见证。BFT/批准修改不改变这些原生接受输入。

三类可核充分方案：

1. **原生原子栅栏**：所有入口在最后创建提交处核退役epoch/父状态，并与截止同域串行；覆盖全部历史/派生能力及在途执行。指定Casdoor接口尚未提供本项目所需的通用版本。
2. **完整入口禁止＋排空**：先强制阻断全部未来入口，原生执行器再提供覆盖所有先前接纳调用的终止/完成收据；随后处置其全部已创建单位。只封客户端出口或只等本地超时不足以排空服务端已接收工作。
3. **有限效果饱和**：全部可能创建调用有可信上界S_i、每次效果上界U_i，已可靠归属互异单位L=ΣS_iU_i；禁止新调用/重开。由计数排除未来额外单位。该方案可在旧handler未证明退出时成立，仍要求无未计旁路。M3/M4/M6仅支撑其原受信范围。

需要进一步得到C_native时，全部已产生材料还须在每个声明接受路径失效；得到C_effect时，还须处理已接受异步载体的未来禁止效果。CreationCut本身不抹去既有Bearer。

## 4. 操作组合的裁决

|组合|CreationCut裁决|附加边界|
|---|---|---|
|改Q批准/owner|不足|旧password/RT/handler仍有原生路径|
|只旋转secret|不足或分支条件性|可省secret的记录分支继续；已通过认证的handler仍可能Insert|
|撤销父RT并读回inactive|不足|NC1；轮换子行可能异哈希且未被覆盖|
|停用user/app|可阻断部分后续新检查，完整cut仍待证|旧handler可能已取得有效user/app副本；连带B及外部RP分别审查|
|关闭一个refresh路由|不足|另一路由、password、code/session等仍可能存在|
|全部入口强制关闭＋可信原生排空＋完整处置|条件充分|权限、入口完整性与排空真实性须出证；目前缺相应部署证据|
|全部未来创建受控＋S/U/L饱和＋材料处置|条件充分于登记scope|恶意域持可重用秘密时S_bypass可能TOP；Q额度不能替代其上界|
|固定等待“一小时”|证据不足|已检查调用可能延后Insert并取得新寿命；时钟/最大执行延迟/禁止再派生需独立依据|

对共享RT或同user/app的B，所有截止/处置动作还要通过保留支持检查；动作可用性由真实权限确定。当前完整G拥有同样接口、观察及计数论证，以上分类未产生候选独占保证。
