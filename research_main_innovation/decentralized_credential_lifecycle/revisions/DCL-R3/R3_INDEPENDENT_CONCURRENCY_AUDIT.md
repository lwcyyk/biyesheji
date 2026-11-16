# DCL-R3：NC1 / NC2重新推导的静态复核

定稿日期：2026-11-10，Asia/Shanghai；读取跨2026-11-09—10。固定Casdoor提交528a0213f01caf70b9f41009cbf7b2f67bdd67ec。本轮从入口、ORM、约束与调度重新建链。属于同一知情对话内的不同证据链复核，外部独立研究者复核及原生新运行均为0。

## 1. 新证据及假设

Casdoor go.mod:84固定github.com/xorm-io/xorm v1.1.6。该版本[engine.go](https://raw.githubusercontent.com/xorm-io/xorm/v1.1.6/engine.go)的Engine.Insert/Get/Update/Delete分别创建并关闭session（1094–1128，网页行号从0计）；[session.go](https://raw.githubusercontent.com/xorm-io/xorm/v1.1.6/session.go)初始化tx=nil、isAutoCommit=true。Casdoor object/ormer.go:285附近建立普通xorm.Engine，未把这些调用绑定进同一刷新事务。

现存配置仅提取非秘密字段driverName=sqlite。SQLite[事务规则](https://www.sqlite.org/lang_transaction.html)允许无显式BEGIN时按语句隐式事务；[隔离规则](https://www.sqlite.org/isolation.html)串行化写事务。下列调度把写语句逐个完成，不要求两个写事务同时持锁，因此单写者约束与它相容。即使连接池仅有一个可用连接，只要前一语句结束释放连接，整个handler仍可在语句间让出执行。

main.go:112–124的过滤链、controllers/token.go、object/token*.go关键调用没有包围整个refresh/revoke的共同锁/事务；routers/session_provider.go:98–164的锁保护单次session操作，离开方法即释放。TimeoutFilter是会话闲置处理；FieldValidationFilter只约束add/update API。先让两条请求完成过滤和认证，再在AddToken之前暂停，即可避开前置处理的互斥疑问。

采用的具体条件：请求被真实权限/配置允许；数据库正常返回且无额外部署级whole-handler串行代理/触发器；有效期足够长、用户/app/cert保持有效；两个生成的随机主键不同；无额外写入者改变该例。源码到二进制符合性仍待部署证明。它们是可行历史条件，独立于“已实测该调度”。

## 2. 从源码抽取事件

路径相对固定Casdoor源码根；行号从1计。

|事件|源码|事实|
|---|---|---|
|R.read(p)|object/token_oauth_util.go:586；object/token.go:139–149|按RT哈希读父记录，结果为Go对象副本|
|R.validate(p)|refresh:594–711|检查secret、ExpiresIn、app/resource、DPoP、JWT、user等，生成新材料和随机name|
|R.insert(c)|refresh:719–738；object/token.go:256–264|新记录只含子字段；单次Engine.Insert；缺以父仍有效/未消费为条件的Insert守卫|
|R.delete(p)|refresh:754–758；object/token.go:267–273|轮换时按父PK和organization删除；调用方只检查err，忽略affected布尔值|
|V.lookup(p)|object/token_oauth_util.go:370–390|查父并验证app/secret；未知或已失效可直接成功|
|V.expire(p)|同文件:351–367|先置父ExpiresIn=0，再期限化同RT哈希的当前活动行|
|V.ack|controllers/token.go:532–543|对象函数正常返回后输出HTTP200空体|
|R.reply|controllers/token.go:477–485|刷新函数返回后写TokenWrapper；客户端可能收到或丢失|

Token的PK为(owner,name)，refresh_token_hash只是index；schema没有parent唯一约束。授权码路径另有claimAuthorizationCode CAS（object/token.go:191–197；token_oauth.go:272），它没有被refresh调用。

## 3. NC1最短见证

取轮换开启，父p有效，子c使用新RT哈希。精确暂停点选R.validate全部完成且生成材料后、R.insert之前。

|序号|刷新R|撤销V|数据库/观察|
|---|---|---|---|
|1|读p并完成全部检查；保留副本p和子材料c|尚未开始|p有效，c未插入|
|2|暂停|查p，置p.ExpiresIn=0|父失效；V的cohort更新扫不到未来c|
|3|继续暂停|V返回HTTP200，客户端收到ACK|此时c仍不存在|
|4|插入新主键、新RT哈希c|已结束|c.ExpiresIn>0；用户/app仍有效|
|5|删除p并返回c|已结束|c留存；后续fresh原生接受可查c|

偏序为 `R.read≺R.validate≺V.lookup≺V.expire≺V.ack≺R.insert≺R.delete≺R.reply`。所有必需程序顺序均满足，写语句串行。V对数据库p的修改没有改写R内存副本；R.insert之后没有回查p。后续删除失败也没有包围此前Insert的回滚代码。选所有语句成功的轨迹即可建立反例，无需依赖错误/SQLITE_BUSY。

**裁决：SOURCE_FEASIBLE，限上述正常并发/DB条件。** 更严格部署若在整个handler外提供串行化，可排除该调度，须单独出证。本轮不授予EXPERIMENT_OBSERVED标签。

V.ack证明该次已执行的期限化调用正常返回；它缺“所有已通过检查的旧调用均已排空”的收据。反例反驳的是ACK之后无新派生行的强声明，对指定旧行随后认证拒绝的较窄命题保持原范围。

## 4. NC2最短见证

|序号|刷新R1|刷新R2|数据库|
|---|---|---|---|
|1|读/检查p并生成不同name的c1|待执行|p有效|
|2|暂停|读/检查同p并生成c2|p仍有效|
|3|插入c1|暂停|p,c1|
|4|暂停|插入c2|p,c1,c2|
|5|删除p成功，返回c1|暂停|c1,c2|
|6|已完成|删除p影响0行但err=nil，返回c2|c1,c2同时存在|

必要边为各自的 `read→validate→insert→delete→reply`，再加两次read都先于第一次delete。不同子PK满足唯一性约束；两个child均不与父争同一PK。第二次Delete返回false,nil时refresh继续返回wrapper。整个例可以把所有写操作顺序执行，SQLite写锁不排除它。

**裁决：SOURCE_FEASIBLE，限上述条件。** 一调用U=1仍成立；两次实际调用的总效果界为2。以“轮换开启”推导同父全局至多一次的主张被该见证推翻。

## 5. 失败、持久与判废条件

Insert之后DPoP更新/父删除返回error时，函数直接返回错误，缺跨此前Insert的rollback；客户端错误观察保持MAY_INSERTED。数据在无掉电、数据库成功返回的运行中可持久留存；突然掉电恢复的物理落盘保证仍须检查DB配置，本文未据此扩展。

能推翻上述源码结论的新证据包括：实际编译调用链存在共同事务、whole-handler父锁、插入时父CAS/唯一约束，或所述请求被前置权限确定拒绝。当前已核固定路径没有这些约束；生产环境的额外中介保持ASSUMPTION_DEPENDENT。

强G可同样保留在途相位与义务，在真实创建截止/S-U-L饱和后对账；它也无法凭本地epoch让该源码自动回查父。该审计提供具体系统语义证据，独立协议原创性与生产漏洞认定继续待核。
