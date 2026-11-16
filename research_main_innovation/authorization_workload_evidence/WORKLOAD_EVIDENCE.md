# 授权工作负载取证

版本AW-EVIDENCE-1，2026-11-05。目标为核实实际任务约束和执行拓扑，沿用K1标量额度及K2私有取位核心的覆盖裁决。公开材料只读；本轮benchmark执行、模型调用、原生服务调用、真实账户操作和候选机制实现均为0。使用academic-research-suite的来源核验流程。[来源清单](sources/READING_LOG.md)

## 1. 最多四项初筛及选择

|对象|已取得资料、版本与来源|证据类别|适用性和缺口|
|---|---|---|---|
|τ-bench，sierra-research/tau-bench|官方main归档，commit `59a200c6d575d595120f1cb70fea53cef0632f6b`；README、任务/政策/工具源码、historical_trajectories|**作者提供的基准运行，业务环境与用户均为模拟**|政策、对话、调用/返回和目标任务同时具备；选择该项深入。README已警告任务过时，本轮只对冻结历史版本作结论|
|τ²-bench及同仓库后续版本，sierra-research/tau2-bench|main README、orchestrator/domains说明的内容哈希快照|规范/框架说明；本轮未取得一条完整运行|旧仓库称后续为τ³，当前README称τ-bench2.0；不能把2025论文名直接绑定当前main。归档超过本轮70MiB采集上限，branch API403，精确commit未取得。只用于初筛|
|AgentDojo，ethz-spylab/agentdojo|官方main README内容哈希快照，含NeurIPS2024引用与结果入口|公开基准介绍；原始结果本轮未取得|有用户任务和安全评价需求；此阅读范围尚未确认独立执行器、共享批准或断连合同，未深入|
|Temporal Python SDK Samples|temporalio/samples-python main README内容哈希快照|**规范示例集合**|列出并行活动、resource_pool、消息与agent集成；未取得该样本的批准政策或作者实际history。样本说明无法替代部署和失败域证据|

三项未选对象只完成上述范围的筛查。没有据此断言它们全部缺少多执行器场景。公开GET来源、哈希及获取限制见sources/RETRIEVAL_*.json。

## 2. 深入对象与可复核版本

选择`historical_trajectories/gpt-4o-retail.json`的数组元素`/0`，字段`task_id=0`、`trial=0`、作者报告`reward=1.0`。原文件共460条分发记录；本轮只深入这一条，未据此估计成功率。[SOURCE：raw/author_tau_bench/gpt-4o-retail.json#/0]

源码归档SHA256为`94d58500e85c5b5790b2afb2af41639977dd8b23f1a0699a78508d4b77216762`，其ZIP注释绑定上述commit。原始轨迹按字节保存于raw/author_tau_bench；选中元素另存为方便阅读的full_record。来源绑定见[sources/SELECTED_SOURCE_BINDING.json](sources/SELECTED_SOURCE_BINDING.json)。

**版本限制。** 历史运行未记录其执行commit、模型精确构建、时间戳或环境锁。当前分发commit是归档版本，无法称为历史执行版本。逐项检查结果为：

- 轨迹嵌入的完整system policy与冻结源码wiki逐字一致。
- task0任务语义在去除annotator、补齐默认outputs、按旧`arguments`/`kwargs`模式规范化后匹配；原始结构差异保持记录。
- 目标订单和两份产品的观察返回与冻结fixtures一致。
- 用户记录存在`address.province`/`address.state`结构差异；本合同所需姓名、付款方式和订单集合一致。未篡改原始记录消除差异。

[SOURCE_READ/只读比对：sources/VERSION_CONSISTENCY.json、OBSERVED_FIXTURE_CONSISTENCY.json]

研究合同以**轨迹内政策和实际返回**为首要依据；冻结代码用于核对兼容的调用语义。未执行重放、重新评分或工具函数调用。

## 3. 模拟性质与参与方

τ-bench论文摘要和§2明确将用户定义为LM模拟者，工具为Python数据库API；仓库data/readme说明fixture由人工设计、LM和程序生成。姓名、地址和付款引用属于公开mock数据，不能写成生产客户或真实交易。[SOURCE：tau_bench_paper.pdf §2/§3；snapshot/tau_bench/envs/retail/data/readme.md]

|问题|实际证据与判断|
|---|---|
|谁执行有状态工具|本记录有一个assistant执行者；user为对话模拟者，未作为第二个工具执行者|
|状态在哪里|当前代码`Env.data`集中保存orders/products/users；工具直接读写这一字典。历史物理主机未记录|
|谁调度|`ToolCallingAgent.solve`逐次调用`Env.step`，只取一个tool_call；`Env.step`同步invoke。政策也要求一次一个工具|
|max_concurrency是否共享批准|`tau_bench/run.py:_run`为每个任务创建`isolated_env`；loader重新读取JSON。并发的是独立benchmark episode，无法据此认定共同消费同一订单/批准|
|批准由谁产生|模拟用户在对话中明确同意两项替代选择；无签名Approval对象、代次、独立授权服务器或分布式批准账本|
|批准覆盖什么|同一订单的一次批量换货请求，包含键盘与温控器两个目标；付款上下文来自此前同一对话|
|是否存在独立故障域/自治要求|未记录且规范未提出。一次一个工具的明确要求，与本轮欲寻找的断连自治输入不同|
|协调/等待费用|有需求澄清及最终确认的对话往返；工具同步返回。原始记录无墙钟，无法量化网络等待/分区或协调延迟|

当前环境是状态权威/调用调度器，并非已实现所有自然语言授权政策的强制安全PEP。工具函数检查状态、商品及付款条件，却不接收确认凭证；对话确认与一用户政策主要是agent遵守义务。这是benchmark模型边界，未据此提出生产安全缺陷。[SOURCE：exchange工具签名、Env.step、paper §2]

## 4. 有来源的实际合同

目标订单O1已delivered。用户希望同时替换键盘和温控器，并给出键盘选项的回退偏好。政策要求先识别用户、只服务同一用户、说明操作并取得明确确认、收齐待换货项目后一次调用。工具要求旧项目存在、数组长度相同、每项替代来自同产品且available、付款方式属于订单主人；成功将状态改为`exchange requested`。[SOURCE：嵌入政策/0/traj/0；消息19/21/23/25/27/29/30/31；工具源码20–73]

|检查类别|证据状态|
|---|---|
|多维可消费额度|未确认；产品选项多属性不等于多维额度。gift-card余额条件存在于规范，但本记录用credit card，未触发该分支|
|同对象仅一次操作|顺序模型中，成功exchange后该接口的delivered守卫阻止再次成功。无法扩展成跨副本全局互斥保证|
|跨服务联合条件|未确认；商品、订单、用户/付款记录属于同一mock环境，未出现独立银行/仓储服务提交|
|前后顺序|确认：识别/查询/收齐项目/提出选项/明确同意/更新|
|预留、取消、归还|exchange接口没有prepare/commit/abort/撤销exchange；其他cancel_pending_order不适用于该已送达订单。无本次实际退款或归还证据|
|分阶段批准|有对话澄清和最终同意；未确认正式批准阶段或代次协议|
|条件消费权限|delivered、匹配可用变体、合法付款方式等条件确认；不据此推定通用额度协议|
|同时完成要求|确认：两个目标都在一个exchange请求和接受记录中出现|

合同谓词、逐项来源和未知范围保存在[CONTRACT_AND_TRACE.json](CONTRACT_AND_TRACE.json)。本轮提取的是可核对子合同；作者reward无法证明所有自然语言政策、价格披露充分性或真实部署授权均已正确。

## 5. 最小轨迹切片与投影

切片边界继承消息0–27中已经实际取得的观察：用户ID、目标订单delivered/owner/items、付款引用、两份商品目录、用户偏好及付款上下文。隐藏任务instruction、reference actions、完整fixtures与评分hash不给运行者当作免费信息。[SOURCE：paper §2；源码Agent.messages；JSON visibility字段]

这里的信息边界属于benchmark协议和LLM消息组织。Python外层程序持有Env及info.task，源码没有建立进程级秘密隔离；本轮源核对可读取这些字段，规划比较则禁止把它们用作oracle。未把评估协议的可见性约定写成真实部署访问控制保证。

|事件|源消息索引|实际内容/作用|
|---|---:|---|
|E28|28|agent提出两个具体替代选项；结合消息22保留原订单/付款上下文|
|E29|29|模拟用户明确同意这两个选项|
|E30|30|一个exchange_delivered_order_items调用，两个旧item和两个新item同批提交|
|E31|31|成功返回：exchange requested，两个目标均在metadata中，价格差−16.63|

保留E28/E29是为核对批准范围和顺序；保留E30是为核对批量参数/计量；保留E31是为核对接受结果。删掉任一事件会失去相应证据。消息28前的只读订单搜索在投影边界中保留已得信息和全部9次工具费用，没有当作免费查询删除。

这个切片保留“共同确认后一次性批量提出两个换货目标”的约束。它不声称保持完整自然语言任务的全策略空间、最优对话成本或任意故障语义。[DERIVED，限定投影]

## 6. 结果与计量阶段

完整记录有34条message、10次逻辑工具请求：9只读、1更新。切片只剩1更新，前缀9次仍计费。模拟用户共有7条message，其中最终具体选项的明确确认在消息29；这不等于7次正式授权。[只读计数：sources/COST_LEDGER.json]

请求由assistant的tool_call提出；guard成功及字段变化由返回与源码支持。记录没有独立admission、server线性化时间或网络send事件；不能把这些阶段各加一次请求。最终状态是**换货申请已记录**。商品最终交付、原商品退回、银行退款及邮件送达均未观察。assistant消息32的业务叙述也无法替代这些效果证据。

作者字段`reward=1.0`表示其评分结果；当前代码主要比较reference最终数据库状态，未单独验证每项对话政策。费用中的`user_cost`原字段保留，但记录没有完整成本/单位，未用于性能结论。工具、模型的墙钟和底层重试次数为NOT_REPORTED。

10次是agent轨迹中的逻辑工具请求。评分器内部重放reference等后台计算不属于这10次；当前代码包含这类评分调用，历史记录没有独立费用账本，完整benchmark计算成本保持未报告。

原始作者数据位于raw/author_tau_bench；“拆成两个调用会怎样”仅为纸面反事实，单独保存在paper/SPLIT_CALL_COUNTERFACTUAL.json。它未混入实测轨迹。
