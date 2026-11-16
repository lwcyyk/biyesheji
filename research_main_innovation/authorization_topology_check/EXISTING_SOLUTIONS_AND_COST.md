# 成熟方案、处理过程与成本

版本AT-CHECK-1。本轮以可执行规格L1开展比较，实测延迟保持未知。事件均在MINIMAL_WORKFLOW.json标为源码推导，raw/RUN_STATUS.json记录未运行。候选与基线获得相同Temporal接口、历史、Task Queue、批准输入及外部服务条件。

## 1. R：现成的持久中央互斥/工作流状态机

本例的完整基线就是已存在的Pool协调者与ResourcePoolClient。它处理的是可归还的具名资源锁，包含跨Activity持有及跨run续持；没有多维消费约束、多个审批权威或任意图匹配参数。[SOURCE：AcquireRequest只有workflow_id；pool的FIFO/first-free实现]

成熟中央锁/状态机方法与这份具体实现的全交错正确性分别登记。之后若发现通知顺序、重发或取消分支需普通修正，仍应在相同接口/权威下审查；本轮未给出并验证源码缺陷，也未把未审计分支当作新协议需求。

### 1.1 最小争用/失败切片

边界保留starter中的另一个resource_a及其持有者U0；resource_b空闲。选U1（首个Activity完成后注入失败）、U2（正常两Activity）构成一个源码允许的调度：

|事件|基线动作|必须等待的位置|已有状态/接口|
|---|---|---|---|
|R1|U1向pool发acquire|等待pool处理及grant|现成Signal、waiters|
|R2|pool选择b并发送grant，随后登记holder/key|Signal await返回；使用者等待grant到达|现成外部Workflow Signal、资源map|
|R3|U2发acquire，但a/b均被占用|等待资源释放，不能自行创造permit|FIFO queue|
|R4|U1首个use_resource正常完成|等待Activity结果|Activity completion|
|R5|显式抛FailWorkflowException，finally发送release(k1)|等待release处理|已有async context finally|
|R6|pool清空b，给U2发送新key的grant|同R2|release-key查找和相同调度循环|
|R7|U2用同一b完成两次Activity|逐次等待完成|已有ResourceUserWorkflow|
|R8|U2 finally归还b|等待pool接收|相同release接口|

这是可执行示例的规格切片，未作为实际history。它保留“占有—等待—完成后失败归还—另一执行者继续”的非平凡条件。R2的发送/登记顺序按源码保留；全体可能交错的实现正确性另需SDK级审查，未由该切片证明。

### 1.2 基线为何足以处理声明的合同

在合法合作式使用和消息/Activity完成前提下，经典中央锁状态机的规则为：空闲资源才产生一次分配；匹配key的合法释放回到空闲；等待者由唯一分配循环选择。当前成功规格路径使用这组规则。U1的失败发生在Activity完成后，所以finally无需猜测未决外部效果，即可发送归还。[SOURCE/DERIVED]

跨continue-as-new的资格保持由已有detach/reattach对象完成：旧run设置detached，finally跳过release；新run用相同resource/key继续，最终一次释放。pool自身CAN携带resources/waiters，并从holder重建key map。这是持久工作流/锁状态传递的现成功能，未产生新协议。

必须区分资源模型的互斥与物理效果围栏。若引入不可停止的外部工作，标准基线应等到所声明的停止/完成依据成立再释放，或使用资源端fencing。SDK具有不同Activity cancellation mode，但请求取消或超时不能代替真实效果完成。本样例没有那个外部资源合同，不能据它自动推广，也无法用该缺失证明新理论。[SOURCE：锁caveat、SDK取消API；DERIVED范围]

### 1.3 源码可推出的费用

对N个成功获得资源且最终显式释放的使用者，无应用级重发时，现有协议产生N个acquire、N个grant和N个release，即3N个**逻辑Signal**。它们经Temporal服务和Workflow tasks实现，不能当成3N个物理RPC或实际网络延迟下界。

最小切片为6个逻辑Signal、3个成功Activity attempt。全部starter的名义路径为：1次pool start、4次user start、12个逻辑Signal、9次use_resource（U0跨CAN共4次，U1失败前1次，U2/U3各2次）、U0一次CAN、最后一次pool terminate。pool自身若触发CAN及基础服务消息成本另计。均为程序路径计数，未采样。[SOURCE/DERIVED：starter.py、ResourceUserWorkflow.run]

资源map/key map及等候队列的控制状态为O(R+W)条目，另加ID/key字节、各run history及CAN序列化。当前找空闲资源为O(R)扫描，`list.pop(0)`可移动O(W)元素。普通free-list/deque等数据结构可同等交给强基线；这种工程优化无法作为新算法差距。[SOURCE/DERIVED]

配置的sleep(3)、10秒start-to-close及5分钟等候超时是输入参数，不是实测耗时。FIFO等待、工作流调度、任务队列、重试、持久化与网络费用分别保留符号。

README称单Pool适合长运行任务且吞吐为“几十而非几百”级请求/释放事件；它没有在本材料中提供对应硬件和测量日志。本轮登记为作者定性性能提示，无法升格为强通用方法的资源下界。

## 2. T：现成审批门与有序工作流

完整基线为一个受服务history支持的Workflow：按序取得分类和账户信息；接受一个经validator检查的decision；按当前门状态选择draft或decline。它已经是本case使用的算法/实现形式。

|阶段|成熟方案动作|等待与费用|合法功能范围|
|---|---|---|---|
|输入|Start固定Ticket Workflow|一次逻辑Start|同Ticket输入|
|前置|classify后lookup|名义2个Activity；分类1个LLM调用|保留数据依赖和原顺序|
|批准|Update validator检查nonempty reviewer，handler存decision|一次逻辑Update；批准到达可早于前置完成|同typed decision、同连接权限；不增加人类身份保证|
|门|等待decision非None，读取decision|等待可为0或无上界|不把收到批准限定为必须后置于分类|
|批准分支|draft后返回reply|名义1 Activity及1 LLM调用|生成草稿；不改变为发信/退款|
|拒绝分支|返回declined|无draft Activity|保留拒绝行为|

### 2.1 可核对的控制流论证

假定标准Update validator在接受该输入前正确执行，且按starter/test的一次decision profile运行。`_approval`初为None，只有approve handler赋值。run在两个前置Activity完成后等待并读取decision。false分支在draft前return；true分支来自已接受decision，validator对true要求reviewer非空。因此ScheduleDraft蕴含两个前置已完成、decision为true和reviewer非空。[DERIVED，源码控制流证明]

这不是通用人类审批安全定理。验证reviewer身份、内容摘要、批准代次或后续撤回，需要额外业务合同和部署检查；源码未要求这些条件。span只导出一次与真实副作用Exactly-once分别登记。

### 2.2 费用边界

批准名义路径为3个Activity、2个LLM端点调用、1个Start、1个Update及结果等待。拒绝名义路径为2个Activity、1个LLM调用。classify/draft各自最多3个Activity attempt；成功批准路径的两个LLM阶段可共发生2至6次调用尝试，实际HTTP/计费以运行日志为准。lookup没有相同显式重试上限，所以一般故障下不能给全流程固定总调用数/结束时限。[SOURCE/DERIVED]

持久状态包括Ticket、分类、账户、decision及reply/history；控制阶段数常数不代表全部存储O(1)。遥测及history输入/输出、Update、重试和外部模型费用均单列。审批本身无最大等待时间，不能把两个60秒Activity timeout相加当成端到端上界。

官方测试用mock LLM/账户Activity及内存exporter，规定批准/拒绝与replay span tree。它们提供L1可执行预期，本轮没有把这些断言写成已通过的L2结果。

## 3. 其他成熟方案的公平位置

|方法|R|T|前提/费用纪律|
|---|---|---|---|
|中央事务/权威预留|当前Pool已提供持有/等待/归还组织形式|当前Workflow已提供审批状态门|保留中央服务、history与持久化成本；不把源实现概括成跨外部服务SQL原子事务|
|标量/向量escrow|单资源权利可用已有许可/锁解释；身份及跨Activity持有仍须保留|没有共享可消费额度输入|不能把多个Activity名称当作额度维度；新增副本/权利转移不免费|
|原生工作流状态机|覆盖已列失败后归还和CAN续持|覆盖顺序、等待、true/false分支|这是具体可用的强方法，不是只有“框架能表达”的主张|
|唯一性/冲突控制|按具名资源互斥；只有一条分配run循环|只有同WF的审批状态|resource-specific task queue/slot限制只覆盖较弱per-Activity并发；要保持跨Activity/CAN同资源，需相应session/锁组合|
|幂等/预留/补偿|重复已释放key被忽略；Acquire逻辑重发未应用去重；没有真实资源补偿服务|无实际业务提交/撤销API；模型调用可能重试|未给双方添加免费的未知效果判定或外部fence|

## 4. I-confluence与计算问题的分层

1. 定性原则可以描述不变量与协调条件，沿用原文适用范围。
2. R的实际决策只是FIFO+找空闲，T是常数阶段分支；本case没有任意程序不变量判定输入。
3. 未得到最少协调点、复杂匹配或多维权利分配的新优化问题；README的“可运行任意放置代码”描述扩展能力，无法替代一个实际约束。
4. 具体代码是否正确覆盖全部异步/取消/崩溃交错仍属独立正确性审查。未取得完整证明或本轮测试结果，不据架构原则认证该实现。

因此两份声明合同在成熟方法覆盖范围内。当前没有G的严格额外代价下界、候选上界或分离实例。
