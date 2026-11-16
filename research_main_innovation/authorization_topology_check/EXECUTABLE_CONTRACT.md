# 可执行合同及最小切片

版本AT-CHECK-1。所有事件均为`SPEC_SOURCE_DERIVED`，不是实测history。源码commit、SDK锁及部署位置见SYSTEM_AND_AUTHORITY_MAP.md；结构化事件保存在MINIMAL_WORKFLOW.json。

## 1. R：长驻资源锁与失败归还

### 1.1 实际接口和检查位置

|接口/状态|源码定位|已有语义|
|---|---|---|
|AcquireRequest(workflow_id)|resource_pool/shared.py:7–9|请求任意可用资源；没有指定多维需求或人类Approval|
|acquire_resource Signal|pool_client/resource_pool_workflow.py:45–52|将请求加入waiters|
|get_free_resource/assign_next_resource|同文件106–125|取首个空闲资源、FIFO取等待者|
|grant Signal|同文件81–97|生成release key并通知使用者，随后登记holder/key；跨await顺序保持原代码|
|release_resource Signal|同文件54–74|matching key且有holder时清空；unknown key忽略。resource字段本身不决定释放对象|
|ResourcePoolClient context|pool_client/resource_pool_client.py:54–85|等待grant；yield期间持有锁；finally正常释放；detached时跳过释放|
|detach/reattach|shared.py数据类；client.py:68–72；resource_user_workflow.py:56–88|跨continue-as-new保留同一resource/key|
|use_resource|resource_user_workflow.py:17–27|本地日志和3秒配置sleep，无资源端验证|

资源数量不是跨人类批准的消费额度；锁归还后资源可复用。这个区别不改变已有互斥/工作流方法的适用性。[SOURCE/DERIVED]

### 1.2 来源支持的约束

在合作式客户端、唯一pool权威、正常消息处理及唯一关联key的模型内，合同包含：

- 单个资源的合作式持有区间不重叠。
- 一段持有区间覆盖同一User Workflow的两次Activity；不是每个Activity重新抽取资源。
- Activity正常结束后显式注入的Workflow失败仍通过finally发送释放。
- detach/CAN/reattach不应在两个run之间释放给其他使用者。

[SOURCE：ResourceUserWorkflow.run；ResourcePoolClient.acquire_resource；官方test对使用开始/结束、同Workflow固定resource及最终全部空闲的断言]

本轮最小切片采用starter已有的U1失败、U2等待场景：边界中resource_a由另一Workflow持有，resource_b初始可用；U1先取得b，U2进入等待；U1首个Activity**已完成**后触发FailWorkflowException，finally归还b；随后U2获得b并执行两次Activity、正常归还。具体排队顺序是源码允许的规格调度，未声称它是一次已保存的运行。

必须保留：U1持有/使用完成事件（建立占用及安全释放依据）、U2等待事件（建立争用）、失败和finally释放（建立非平凡清理）、U2后续分配（建立等待者可继续）。删掉它们会分别丢失对应约束。边界外的另一资源/Workflow不被当作免费新增能力。

### 1.3 原文前提、取消和未知结果

README明确采用真锁而非lease。文档要求避免Workflow执行/运行超时、operator terminate及永久停机等泄漏情形；源码的`_warn_when_workflow_has_timeouts`实际是告警，未强制禁止这些配置。[SOURCE：README Caveats；client.py:88–101]

Activity的start-to-close timeout与Workflow timeout分别处理。普通取消请求、超时状态或finally执行本身不足以证明外部物理效果已经停止；锁是否可归还仍依赖Activity/资源服务的完成合同。本切片只选首个Activity已经完成后注入失败，未引入“结果未知也可安全归还”的额外保证。

源码的grant在await外部Signal后登记holder，release handler可异步运行；本轮未对所有SDK调度/故障交错完成代码级证明。Acquire的逻辑重复没有应用request-id去重；重复release在已删除key后被忽略。官方正常/失败/CAN测试不等于所有交错已通过。[SOURCE/证据边界]

若部署要求对不可信或不可停止的真实Activity仍保持资源效果互斥，需要终止确认或资源端fencing等额外合同。当前use_resource模拟函数和输入schema未提供此需求，不能将该条件补入新主问题。

## 2. T：审批门与有序草稿生成

### 2.1 实际检查

`Ticket`含ticket_id/customer_email/subject/body。`ApprovalDecision`含approved/reviewer。Workflow保存一个可更新的`_approval`；Start/Update的Workflow ID提供Ticket上下文绑定。[SOURCE：activities.py数据类；workflows.py]

已确认的执行约束是：

\[
ScheduleDraft\Rightarrow ClassifyDone\land LookupDone\land
DecisionAtGate.approved\land DecisionAtGate.reviewer\ne\emptyset.
\]

条件中nonempty-reviewer依赖标准SDK的Update validator以及示例唯一赋值入口。它只保证输入形状/分支，不保证该字符串对应有权的人、批准了回复内容或包含新鲜代次。[SOURCE/DERIVED：workflows.py:47–88]

门处读到approved=False时返回declined，不调draft。后续没有发送邮件/退款阶段。多次Update可以覆盖`_approval`，而run在门处把当前decision取入局部变量；样本starter/test只发送一次decision。未提取出“撤回后即时中止已经开始的draft”合同。

### 2.2 最小来源切片

1. Start Ticket Workflow。
2. 可在triage完成之前接受一个有nonempty reviewer的批准Update；官方test就是start后立即Update。
3. classify成功，再lookup成功。
4. 读取已接受的decision；true则调draft并返回草稿，false则declined。

这保持“两项前置结果+批准共同控制后续调用”的联合条件。把批准到达限制在triage完成后、把两个前置Activity改成并行、增加多reviewer法定人数或共享金额，都缺本case源码依据。

不能删除decision，否则门永远没有满足依据；不能删除分类/账户结果，它们是DraftReplyInput的数据依赖；不能删除false分支，否则无法核对拒绝路径。独立的人类鉴别与身份授权留在外部部署条件。

### 2.3 等待、重试及效果

classify/draft设置`maximum_attempts=3`、start-to-close 60秒；OpenAI客户端`max_retries=0`，避免客户端重复重试隐藏在一个Activity attempt内。lookup为本地示例账户表，start-to-close 10秒，未设置同样的最大重试数。审批等待没有全局截止时间。[SOURCE：workflows.py:19/47–75；activities.py:71–80/108–122]

这不能推出任意故障下的固定结束时间。timeout不是实际观测时延；即使遥测span去重，也不能推出外部模型调用/业务效果Exactly-once。官方test关注span tree/replay及拒绝后不出现draft，未认证真实服务副作用。

## 3. 约束与证据分层

|问题|R|T|
|---|---|---|
|联合完成|同一资源跨两次Activity及可选CAN|分类、账户及decision共同决定draft|
|唯一性|合作式持有者排他；中央pool|一个WF审批状态门；无全局对象唯一消费|
|取消/归还|已完成Activity后失败的finally归还；termination等有caveat|无取消draft/补偿真实业务接口|
|多维额度|未提供|未提供；两个LLM调用不自动形成共享费用预算|
|独立批准主权|未提供业务Approval|reviewer字符串及部署访问权，非多个独立审批权威|
|运行证据|测试源码为L1；本轮无L2|同左；README预期trace仍为L1|

这些规格已足以进行路线判断。实测吞吐/延迟缺失保持参数，未因L2缺失继续扩张候选。
