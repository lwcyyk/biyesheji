# 可信注册与会话总量门

## 实际接线

serve新增仅限可信进程调用的keyword `authority_mount_ticket=None`。Authority Store构造完成后调用mount_authority_host，再建立Handler；默认None立即返回，源对象属性亦无需访问。旧CLI没有新增可启用的参数，配置正文不能发行ticket。

ActivationIssuer.authorize_offline属于可信内部测试/宿主API。它生成进程内opaque ticket，注册表绑定issuer/epoch、scope/grant/rid、管理身份、策略、源引用和有效期。普通字符串、dict、裸LOCAL及未登记的同类型对象均被拒绝。对象不具跨进程密码学认证含义；有任意Python执行权限的代码仍在可信域内。

mount捕获同一Store的connection、lock，建立BoundedAuthorityReader窄视图并传入原H1宿主。来源替换、ticket版本/有效期、issuer退役和epoch变化在读前检查；注册不构造Store、不执行SQL/key/decode、不创建日志或服务。

真实Handler仍使用原配置Bearer/operation门；新读取分支将私有header/config交给authenticate_authority_peer，再把登记的AuthenticatedRpcContext交受限dispatch。旧controller/Agent身份即使有广权限也不自动匹配专用管理身份。新核心在合成上下文下执行，实际Handler只静态核对，RUNTIME_IMPORT_REFINEMENT_GAP保持。

## 会话定义与修复

实现中的本地会话命名空间为：

`K=(持有的connection对象, authorization_id, process_epoch, canonical scope)`。

connection是获准Store来源的对象身份，连同Store/lock绑定核验；显示source_ref、issuer对象和permit对象均无法重置K。该定义对应本轮固定来源的进程内合同，未声称已识别同一磁盘数据库的所有连接或持久genesis。

run_002的A09显示：仅将claimed放在一个Registration内，可通过另建issuer并换显示来源别名再挂载，得到第二次SELECT。原结果中的issuer_recreation_escape保存status=STAGING_READY_WITH_GAPS、同授权ref和total_source_selects=2。

修复增加进程级受锁命名空间注册表：同K仅注册一次，强持有connection对象避免id复用；4096项封顶。即使新issuer发行新ticket，第二次同K挂载也会拒绝。命名空间保留到进程结束；没有自动删除/恢复/重置入口。

## 至多一次的论证

1. 在进程级锁内检查并保留K，故同K最多存在一份已准入Registration。
2. 每份Registration共用原policy RLock。全部合法permit在同一claimed标志上竞争，claim原子地将false变为true，后续路径无反向赋值。
3. 权限和来源先检查；连接处于活动事务时先拒绝。合法入场占槽后，配额、源、key、decode、返回、日志和超时失败均不恢复槽。
4. reader仅接受当前inflight拥有线程，reader_started只允许一次false→true；回调重入无法产生第二个SELECT。
5. 结束只清理inflight与观测值，保留claimed/reader_started/命名空间。因此换permit、重复请求、新客户端或同源重新挂载均不能增加读取。

A09三线程持3张permit，结果1 ready/2 replay，SELECT/key/decode各1；之后新permit、旧permit和新issuer均被拒绝。A13回调重入拒绝；A18新CLI Invocation重连仍replay；A14异常/超时不rearm。

## 撤回与重启范围

ticket及policy epoch/有效期入场核验，出域前再核当前权限。源内发生撤回时，已发生费用保持，业务数据被丢弃。纯内存epoch退役使旧ticket/permit失效，旧ticket不能自动挂载；默认客户端无真实执行路径。

此处没有跨崩溃持久claim簿。新进程内的真实epoch来源、批准票据发行、旧授权失效、唯一Store与DB身份仍需部署/P1/P2固定。可信内部显式重批与远程请求自行重开分别管理，任何字符串标签本身都不提供批准。

## 计量

最终27份成功Registration，23次permit发行、19次permit消费/会话claim、18次read_state/SELECT API尝试、17次SELECT成功、14次key spy、13次decode spy。一次已占槽因额度不足而源读0；一次源遥测故障在SQL前失败。各session的计数与业务结果分别保存在SESSION_GATE_AUDIT。这组统计只属于新A1侧，原H1回归的替身计数在原始H1_details和独立汇总中保存，两个口径不混合。

真实身份、证据来源/当前性、typed O/o、Native资格和全局COMPLETE继续保持原缺口。
