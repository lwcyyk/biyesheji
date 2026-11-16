# 来源、定位与执行记录

日期2026-11-05，AW-EVIDENCE-1。四项初筛、一个深入对象。来源文件的URL/获取状态见RETRIEVAL_*.json，内容哈希最终见SOURCE_MANIFEST.json。历史继承文件及其哈希见INHERITED_INPUTS.json；历史目录未改动。

## 1. 初筛对象及阅读范围

|ID|公开来源|版本/阅读范围|证据等级|
|---|---|---|---|
|TB|[sierra-research/tau-bench](https://github.com/sierra-research/tau-bench)|官方README、完整源归档索引；选定retail政策/任务/工具/运行器及一条历史记录深入，commit `59a200c6d575d595120f1cb70fea53cef0632f6b`|作者提供的模拟基准运行和公开fixtures|
|T2|[sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)|main README、src/tau2/orchestrator/README.md和domains/README.md，均保存内容哈希；精确commit未取得|当前框架说明。旧τ²、后续τ³、当前README的τ-bench2.0命名与版本分别保留，未把它当作2025论文原版本|
|AD|[ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo)|main README，含论文/结果站链接、运行示例与用户任务/攻击配置入口。未深入任务及原始结果|公开基准介绍；原始trace取得状态为未取得|
|TP|[temporalio/samples-python](https://github.com/temporalio/samples-python)|main README及样本入口列表；未取得实际workflow history|规范示例，不能当作实际生产运行|

前三项README原始URL均为其官方raw.githubusercontent.com入口，第四项同样来自官方repo。未选的三个对象只提供初筛级事实；尚未完成对其全代码/全数据的覆盖审查。

## 2. τ-bench论文

**τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains**，Shunyu Yao、Noah Shinn、Pedram Razavi、Karthik Narasimhan，arXiv2406.12045v1，2024-06-17；本轮使用50页作者稿。[元数据](https://arxiv.org/abs/2406.12045) [全文](https://arxiv.org/pdf/2406.12045)

本地tau_bench_paper.pdf，SHA256 `0ce66a1763d698c61bb311c3c874bf593d1e9a5bfff11bb35f6f72b981f6da56`。结构预检PASS，sidecar与正文页标保留。提取有旋转文本警告；本轮没有依靠旋转图页数字作性能结论。

实读范围为摘要、§1中模拟/真实领域的区分、§2环境/工具/政策/用户及hidden state/任务可见性、§3生成过程相关段。PDF p1为摘要，§2主要在pp4–5，§3生成描述在pp5–6。后续性能及50页全部附录未作为已全面核验材料。论文用于确认模拟性质、组件语义和评估口径，实际事件以原始JSON为准。

## 3. 深入对象的源码定位

归档文件tau_bench.zip SHA256 `94d58500e85c5b5790b2afb2af41639977dd8b23f1a0699a78508d4b77216762`，ZIP注释给出commit，索引129条。原归档完整保留；非historical/few-shot源码及fixture摘录在tau_bench_snapshot，未导入/执行任何benchmark模块。

以下路径均在`sources/tau_bench_snapshot/`下：

|路径/函数|定位及事实|
|---|---|
|README.md|开头任务过时警告、Historical trajectories、模拟用户/工具说明；分发快照不能作为最新任务版本|
|tau_bench/envs/retail/data/readme.md|Mock Data Generation及LM/程序/人工生成说明，确定数据性质|
|tau_bench/envs/retail/wiki.md|用户识别、一用户、明确确认、一次一个tool、收齐item和一次性规则；Exchange delivered order段|
|tau_bench/envs/retail/tools/exchange_delivered_order_items.py:11–73|invoke；20–25状态守卫；27–35旧item多重数/长度；37–49variant/availability/价格；53–64付款及gift-card条件；66–73写入exchange metadata并返回|
|同文件:76–130|get_info公开数组参数、描述中的明确确认及一次性说明。函数不接收签名批准/代次字段|
|tau_bench/envs/retail/tools/get_user_details.py|返回已有user JSON；本身不是OAuth身份认证协议|
|tau_bench/envs/retail/tools/get_order_details.py|只读返回订单；被省略显示的其他订单查询未修改目标订单|
|tau_bench/envs/retail/data/__init__.py:11–23|每次load_data从三个JSON加载新dict|
|tau_bench/envs/retail/env.py:23–46|选择task split并构造MockRetailDomainEnv，绑定data loader与工具/政策|
|tau_bench/envs/base.py:58–84|Env.data及reset重新装入数据|
|同文件:90–119|step同步invoke并返回；没有该切片中的外部业务HTTP/分布式提交|
|同文件:124起|calculate_reward主要比较reference最终DB hash；不能把reward作为所有授权政策的证书|
|tau_bench/agents/tool_calling_agent.py:29–81|solve的messages、同步step、收到结果后再进入下一步|
|同文件:86–98|message_to_action选择首个tool call|
|tau_bench/run.py:66–114|_run为每个task建立isolated_env，ThreadPoolExecutor并发的是episode；checkpoint lock并非跨任务批准/业务锁|

全部行号绑定该分发commit。历史执行commit未记录，所以源码用于当前可核对模型及兼容解释，不伪装成历史精确环境锁。

## 4. 原始轨迹与选择

原始成员`historical_trajectories/gpt-4o-retail.json`按原字节复制为`raw/author_tau_bench/gpt-4o-retail.json`，哈希见SELECTED_SOURCE_BINDING.json。文件含460条记录，深入选择数组`/0`，task_id0/trial0/作者reward1.0。提取的完整元素文件为task0_trial0_full_record.json，属于可读提取件，原始字节文件另存。

|JSON Pointer前缀/0|含义及本轮使用|
|---|---|
|/traj/0/content|嵌入policy，历史合同首要来源，与当前wiki逐字匹配|
|/traj/3–5|提供姓名/zip、查找user_id及返回；模拟身份识别|
|/traj/8–9|读取user信息，包括订单列表/付款引用|
|/traj/18–19|目标订单及delivered/owner/old items/prices|
|/traj/21、23|第二目标及键盘回退偏好|
|/traj/22|原订单、项目和付款的提案上下文|
|/traj/24–27|两个产品查询及返回，包含最终选择的available variant/价格|
|/traj/28–31|最小后缀：具体提案、明确同意、批量请求、成功返回|
|/traj/32–33|agent业务叙述及用户结束；未作真实物流/退款效果证明|
|/info/task|私有user instruction及reference actions，仅供用户模拟/评分与源核对，禁止给在线基线作oracle|
|/info/reward_info|作者评分字段；本轮未重新运行/验证评分器|

版本比对只读进行。原始Task/Action构造通过ast读取字面量，未eval/import。模式规范化限于annotator、默认outputs及arguments/kwargs，不改变目标/用户/动作参数。用户地址province/state差异如实保留；本合同有关的name/email/orders/payment_methods相同。

benchmark的visibility是论文协议和LLM消息边界。Python程序持有Env/info.task，所以它并非进程级秘密隔离；本轮明确区分合法方法输入与源审计/评分数据。

## 5. 理论来源复用及适用界

复用main_question_reset/sources中的Balegas等2015 bounded counter、Bailis等2014 I-confluence全文/原定位。本轮只使用既有定义/定理范围：副本状态与权利前提、I-confluence的定性条件。没有将框架的表达能力说成任意政策判定或最优协调算法的高效保证。

批量更新命题W为本轮纸面推导，范围为一个顺序状态权威、已规范化并确认的参数、现有batch接口、无故障输入。成本只证明C_mut=1，未证明完整自然语言episode调用数最优。paper/SPLIT_CALL_COUNTERFACTUAL.json为未执行反事实，独立于raw作者记录。

## 6. 获取限制与运行纪律

GitHub连接器的两个tree只读请求均返回MCP传输错误，转用官方raw/codeload公开来源。τ²主分支归档超过本轮70MiB采集上限而停止，未写出不完整ZIP；branch API返回403 rate limit。它们限制该对象本轮证据完整度，无法据此推断其算法或数据性质。

没有发送issue/邮件、没有运行模型或benchmark、没有服务/账户/客户端变更。paper切片及合同JSON由文档提取/注释生成，没有实现候选机制、保护策略或求解器。采集源、原始轨迹、纸面反事实在目录中分开。

## 7. 复核资产

SELECTED_SOURCE_BINDING.json绑定成员/commit/哈希；VERSION_CONSISTENCY.json保留模式与地址差异；OBSERVED_FIXTURE_CONSISTENCY.json保留逐条原始比较结果；COST_LEDGER.json只记录可观察数量和缺项。ARITHMETIC_CHECKS.json是价格及调用数的算术核对，未执行业务工具。DOCUMENT_VALIDATION.json记录最终文档、源指针、哈希和执行状态检查。
