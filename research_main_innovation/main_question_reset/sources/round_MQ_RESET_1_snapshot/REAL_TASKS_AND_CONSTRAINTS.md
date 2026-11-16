# 有依据的实际任务与本轮约束

版本MQ-RESET-1，2026-11-05。目标为高强度主创新筛选。本轮仅进行文献、源码与纸面研究，候选机制实现、原生服务调用、真实账户操作及新性能采样均为0。使用academic-research-suite的来源核验流程。`SOURCE`为文献/规范/源码事实，`DERIVED`为本轮推导，`MODEL`为明确增加的条件，`UNRESOLVED`为待核项。定位及哈希见[sources/READING_LOG.md](sources/READING_LOG.md)。

## 1. 继承裁决及实际入口

|资产|本轮准确继承|依据|
|---|---|---|
|prepared state与SC/MC|整份状态驻留、固定条件下的成本选择已有成熟归约|ci02_cost_problem_screen/NOVELTY_DECISION.md|
|预测重物化|外部请求预测已修正；一般DAG参数化界仍为具体未决，细粒度凭据接口尚缺|prediction_rematerialization_screen/FINAL_DECISION.md、SAME_MODEL_PRIOR_ART.md|
|CI-01权限缺陷|固定提交上的一项完整离线实现缺陷及最小修复；作为支撑案例归档|ci01_policy_regression/FINAL_DECISION.json；保留部署/并发/首次披露未核状态|
|七项旧机制|A2/A3/B2/B3/AB2/AB3重放/B4继续淘汰|research_secret_recipe/REPORT.md §1.2|
|资源谱|保留条件性资源理论资产；相同能力通用方法资源最优相同|workspace_asset_review报告及research_novelty_review/GAP_CARDS.md|
|CS03|原代码/原始转录缺失状态维持；运行数字仅为历史报告记载|workspace_asset_review/REPORT.md、既有搜索记录；本轮未重复检索|

最新定位到的详细计划书为根目录《面向AI智能体的认证语义感知与可撤销凭据管理方法及系统研究_详细计划书_2026-11-04.docx》，v1.0。直接提取的文本保存在sources/LATEST_PROPOSAL.txt；原件哈希已冻结。它写明批准、资源/接收方、请求预算、`charged+reserved<=limit`及SC1双代理读文档/提交摘要流程，完整系统仍分已实现与拟实现。[SOURCE：计划书§4、§11.1、§11.3]

|源码入口|实际内容及本轮阅读|能支持什么|
|---|---|---|
|auth-lifecycle/src/auth_lifecycle/a/candidate.py|Shield与solve，读取模型/信念/后继并调用Feedback|有限模型算法入口，不能据入口名称推定新基线差距|
|…/b/engine.py|resources/setup/available/preserves/goal/plan|配置和停止—保留的有限枚举/搜索语义|
|…/a/bridge.py|Feedback，调用B搜索及冲突检查|AB配置反馈入口；旧机制裁决保持|
|…/experiment/planning.py:35–63|`known-contract-single-path/v1`、`query_needed_profile=False`、单registered世界与空probes|原生绑定的已知契约profile；无法当作新观察困难已激活|
|…/experiment/journal.py:58–105|Gate用进程内锁核对准许集和累计预算，发送前计费|已有集中式请求预算门，不具有分布式配额协议的实证结论|
|…/online_state/storage.py:190–225|grant保存limit/reserved/spent；admit核对绑定、去重、资格与预算，再增加reserved|已有权威状态中的每grant额度预留；未从此推定跨服务共享额度已实现|

完整路径、函数行号及哈希另见sources。各入口只读，未执行历史测试。

## 2. 任务T1：一次批准下的多执行器共同额度

**需要方与流程。** 同一用户让两个代理调用资料/笔记或其他工具。用户希望共同批准“总共至多Q次获准发送”，执行器可位于两个进程或管理节点；网络分区时希望有权的执行器仍可工作。计划书已经存在多个代理和预算；RFC9396进一步说明结构化授权可携带细粒度操作参数，但它并不自动提供全局可消费计数器。[SOURCE：计划书§4/§11；RFC9396 §1–2；当前Gate/AuthorityStore]

**可调用接口与信息。** 当前源码已有本地批准/预算状态、准入和provider派发入口。集中式原型可继续使用一个权威门。跨独立执行器的额度分配/转移RPC、全局批准组标识和副本状态是拟新增工程能力，须同等给强基线。仅添加OAuth JSON字段无法强迫已有资源端维护共享历史。[SOURCE/MODEL]

**冻结合同。** 计数对象为不同请求ID的授权准入/发送名额，单位成本1；重复业务效果、实际扣款金额及丢响应后的Exactly-once另属合同，当前不纳入。所有对外使用均经过可信执行器，代理可恶意提出过量请求，却无直接可绕行的Bearer/密码。批准为可信且当前有效，副本持久状态不回滚，可信执行器非Byzantine。[MODEL]

**约束。** `Σ admitted_i<=Q`；同一批准范围、主体、接收方和代次不被扩大。分区期间没有跨执行器消息或额外共享实时权威输入。可选的可用性目标须区分“在已分配本地额度内可用”与“任一执行器都能在其他执行器闲置时用尽全部Q”。[MODEL]

**已有正确方法与代价。** 集中式门逐次做权威预留；同进程可为一次本地事务，远端权威部署时增加控制面RPC。Escrow预先分配不相交的消费权利，额度内无需同步；权利不足时转移、等待或拒绝。代价在于状态、权利分配不均及转移通信，属于实际可用性/延迟问题。[SOURCE：Balegas2015 §II–III；当前源码]

这一任务技术内容为可消费授权的复制与协调，区别于CI-01恢复/撤销、CI-02证明历史、CI-03联合观察隐私，也区别于缓存调度。其重要性有依据，先例距离仍需通过本轮映射裁决。

## 3. 任务T2：凭据/令牌状态检查的索引隐私与更新费用

**需要方与流程。** 代理或服务代表用户呈示JWT/SD-JWT/VC/mdoc时，验证方需要检查撤销/挂起状态，同时希望状态发布者无法从查询得知具体凭据。W3C Bitstring Status List v1.0以及IETF Token Status List -21都明确说明这种跟踪风险及列表规模—隐私—传输权衡。[SOURCE：W3C2025 §6；TSL21 §12.1–12.2/§13.4]

**公开现成接口。** 状态引用给出列表URI和index；TSL21默认HTTP GET返回Status List Token，验证方验证保护、字段、期限及状态位；`exp/ttl`优先于HTTP缓存头。W3C使用压缩bitstring及群体列表。一个列表下载后可在有效期内支持多个本地状态查询。[SOURCE：TSL21 §6/§8/§13.7；W3C §2/§3/§6.3]

**当前项目对应。** 现有Keycloak/Casdoor适配器主要调用发行、刷新、撤销、内省；本轮没有证据表明它们已经提供TSL/PIR接口。该任务具有公开规范依据，与凭据生命周期有关，项目应用需要额外状态发布/验证适配。无法把角色受限active响应直接改写为公开状态位。[SOURCE：CAPABILITIES.md、planning.py；UNRESOLVED：原生TSL支持]

**可见信息与隐私约束。** 列表/issuer/cohort、快照版本、请求时间及网络端点作为公开泄漏固定；隐藏列表内index。身份匿名、跨列表关联及全流量模式另属目标。新鲜度限定为接受满足明确`exp/ttl`的版本，严格“全球最新”需要独立新鲜来源。客户端已有缓存和hint必须计费。[MODEL]

**已有正确方法与代价。** 基线G-list为下载同一群体列表、验证、缓存并本地查询。若启用PIR，基线同等取得服务器计算接口、预处理、hint和密码学假设。SimplePIR/DoublePIR已处理这种私有索引获取；其预处理、更新与在线成本需完整保留。原有HTTP GET无法免费执行PIR。[SOURCE：W3C/TSL21；SimplePIR2023 §3–5]

**为什么值得检查。** 大群体、高频状态更新或冷客户端可能产生实际带宽/服务器负担；小列表、压缩及多次复用可能使整表下载更便宜。当前项目尚无这类负载数据，无法仅由公开GB级PIR性能推定收益。[SOURCE/待测]

## 4. 选题限制

本轮只保留T1/T2并形成两个主问题候选。后续文稿先执行成熟模型与能力公平性检查。新增接口、可信持久状态、密码学参数或合法功能变化都单列，候选实现门继续关闭。
