# 枚举完整性与来源能力

## Material Passport

证据：冻结Casdoor源码、上阶段run03_listing权限见证、本轮C12与官方SQLite隔离说明。源码根为本目录`sources/casdoor-v4.25.0/`；实现的行级定位见[转移表](TRANSITION_MODEL.md)。枚举可见性、来源正确性和截止新鲜度各自审计。

## 原生列表的准确语义

|问题|核查结果|依据与限制|
|---|---|---|
|过滤|owner精确条件；organization作为Token条件；field/value使用LIKE `%value%`|object/ormer_session.go:GetSession。调用方应检查每行实际组织/用户；字符串匹配不能直接当任务标签|
|分页|Limit+Offset；count与data独立调用；页间无共享事务句柄|controllers/token.go:37–70；object/token.go:GetPaginationTokens|
|排序|默认created_time降序，时间并列无额外键；显式name+ascend可在固定owner内给唯一全序|排序参数是ascend。稳定全序只解决并列问题，页间变更仍会移动offset|
|失效行|默认包括expires_in=0记录|C12撤销后列表仍有1条失效记录；其余自然期限也需客户端解释|
|未分页|省略pageSize或p走GetTokens(owner,organization)，field/value在该分支不使用|一次SELECT可取授权范围全量；只有获准读取整个组织时适用，输出/隐私成本另计|
|一致性|data的一个SELECT在适当SQLite隔离前提下得到该语句的结果；响应中的count和多页缺少共同快照|本轮没有将普通列表升级成可验证服务端快照；实际驱动/连接设置的全证明待补|
|游标/版本|所查接口未提供稳定游标、事务版本、完整水位或终态标记|两次相同清单只支持两次观察，之间或之后仍可发生派生|
|方法权限|历史普通用户Bearer查询业务status=error；应用Basic可读取同组织新用户列表；本轮再次用新应用B的Basic查询|具体权限来自原生authz规则和批准范围；管理员清理权限不自动进入方法能力|

SQLite的一条读事务可以有稳定视图，跨HTTP的count/SELECT和多页没有凭空获得共同读事务。C12已在真实API、唯一name排序、三个本轮新记录中验证页间删除漏项。[C12日志](raw/run01/http_and_events.jsonl) [SQLite官方说明](https://sqlite.org/isolation.html) [取得文本](sources/sqlite_isolation.html)

## 最小漏项与重复例

唯一升序列表[a,b,c]，pageSize=1。第1页返回a，其他操作删除a；第2页offset=1从[b,c]返回c，b仍存在且整个两页遍历漏掉b。本轮使用API delete-token完成该删除，属于可达原生操作。轮换refresh也会删除父行并插入子行，但其随机键位置需要另按实际顺序分析，当前C12没有把管理删除冒充刷新插入实验。

另一纸面例：第1页a后，在前缀插入0，[0,a,b,c]的第2页再次返回a，产生重复。若持续前插，offset遍历可能一直追赶；固定有限记录、停止修改并从第1页完整重扫，则可恢复完整性。失效置0本身不删除行或改变name排序；在name排序且筛选不含expiresIn时，收集后撤销不会引入上述删除位移。若方法改用delete-token，应先完整收集，或采用有证明的重新扫描方式。

## 可证明的完整枚举条件

E-stable：方法已知获准枚举域Q；Q有限，存在可知的静止时点d；d后直到扫描结束，Q的成员、匹配字段、排序键固定；排序在owner内唯一；HTTP均终态成功。此时令n=|Q|、页长p，扫描第1至ceil(n/p)页（或再空页确认）完整包含Q。证明为固定有序序列的相邻不交切片覆盖；count可在静止期间准确使用。页面完成并不说明Q以外的来源或d之后仍可派生的域已经关闭。

E-one：获准使用全量接口，或已知可信上界N且单页容量≥N，则data中的一个SELECT覆盖该语句读视图内的Q；仍需独立保证此后无新增A材料，或随后所有新增均被持久范围守卫拒绝。单次返回两个句柄及count相等均无法单独提供该保证。

B在扫描范围内刷新也可能改变行。F_closed只约束A时，需要进一步隔离A的查询域、让B在扫描期间维持现有材料、使用单SELECT范围，或为跨页修改提供另一个完整性证明；这些条件均计入双方。当前接口没有水位可消除该依赖。

## 原生来源字段与可信账本

|原生信息|可证明的关系|本地账本仍需提供|
|---|---|---|
|owner/organization/user/application|记录身份及应用范围；经原生执行形成的资源支持域|任务A/B、批准代次、用途及停止策略|
|Name、AT/RT/hash|当前行和精确句柄；非轮换同RT hash关系|轮换后父子来源、丢响应attempt到行的归属|
|SessionId|某些授权流程的原生会话归属，刷新继承|任务和批准与session的受信绑定；原password记录为空|
|GrantType、Scope、Resource、DPoPJkt|所记录发行类型及受限授权参数|同字段下不同任务的来源；某些profile字段可辅助区分，需单独证明|
|Code/CodeIsUsed、CreatedTime|代码状态和粗时间信息|原子任务提交号、完整序号、批准撤回顺序；时钟同值/并发不能补齐因果|

对P1，已知初始A RT且无可产生不同RT的新授权路径，hash相等可用于该组归属。对P0，若任务批准的发行响应/pending关系完全丢失，相同账户与应用下的两条记录可分别对应“第1条属A、第2条属B”和交换标签的两段历史。枚举视图相同而选择性停止动作不同；缺少区分信息时保留UNKNOWN。该双历史是经典来源不可区分实例，其他可区分字段存在时需重新检查前提。

本轮方法可用的列表权限在profile中明确授权；C12以列表结果选择删除第1条，属于取证调度操作。接受评分与清理SQL只进入观察者日志；取证逻辑未借评分结果为任何候选算法发完成承诺。同进程分流仍弱于进程/主体隔离，已登记限制。
