# 两项定点先例核查

核查日期为2026-11-04。比较对象为既有M_r完整资源谱和认证副作用义务约束下的有界完成规约。核查结果只关闭本次两个明确问题，总体优先权沿用R3的“近邻未决”。[研究范围](D:/毕业设计/thesis_draft/TASK_SCOPE.md) [R3优先权记录](D:/毕业设计/research_recipe_r3/PRIORITY_AUDIT_R3.md)

## 1 来源与阅读范围

|索引|题名、版本与取得方式|本轮实际读取|来源|
|---|---|---|---|
|M01 / R48|Qingzhuo Wang等，Authorization Closure Graph: Minimal Repair for LLM Agents with Evolving User Instructions，2026，arXiv 2609.32428v1。复用已有PDF并核对官方题录|22页全文已取得，重点读取§1—3.2、Proposition 1—2、Appendix A.1—A.4及修复预算实验的定义。全篇检索命题、预算与下界相关位置|[本地PDF](D:/毕业设计/thesis_draft/sources/acg.pdf) [原文](https://arxiv.org/abs/2609.32428v1)|
|M02 / R49|Moonwon Choi、Seokho Jeong、Sian Choi、Seunggeun Lee，ResidualAuth，2026，arXiv 2609.08062v2。复用已有PDF并核对官方题录|81页全文已取得，重点读取§1—5、Proposition 1—2、Theorem 1—3、Appendix A.1—A.5、L.2与O.1—O.2。存储下界的全部附录证明未逐行重证|[本地PDF](D:/毕业设计/thesis_draft/sources/residualauth.pdf) [原文](https://arxiv.org/abs/2609.08062v2)|

ResidualAuth官方题录使用“What Authorization State Must Language Agents Preserve under Revocable Delegation?”，取得PDF题头使用“What Authorization State Must Agent Systems Preserve under Revocable Delegation?”。本稿按同一arXiv标识和v2内容定位，保留题名差异。两个PDF的页树结构预检均为PASS，该结果只支持页面定位。阅读对象摘要与来源记录保存于sources目录。[官方题录快照](D:/毕业设计/thesis_draft/sources/residualauth_metadata.html) [获取记录](D:/毕业设计/thesis_draft/sources/RETRIEVAL.json) [结构预检](D:/毕业设计/thesis_draft/sources/residualauth_preflight.json)

## 2 ACG的逐命题覆盖矩阵

ACG用有限DAG记录authority、evidence和derived节点，按版本和依赖关系保留或失效先前授权。其Proposition 1具有真正的最优性内容，Appendix A.2证明修复前沿F是保持当前缺失集合依赖覆盖的唯一最小包含集合，也是唯一最小基数集合。该性质应作为既有理论引用。[R48 §3.1—3.2、Appendix A.2](D:/毕业设计/thesis_draft/sources/acg.txt)

|待核主张|ACG原文的精确结果|与本项目关系|判定与定位|
|---|---|---|---|
|授权变化需要维护依赖与版本|Definition 1、式(2)—(5)、式(9)及Appendix A.1的保留性质|直接约束本项目证据失效、共享授权及反馈复用的宽泛原创主张|已有机制与形式化覆盖。PDF正文4—6页及附录12—13页|
|“最小修复”有无下界|对固定action、固定graph和missing set M，所有满足↑S=M的S都包含F，因而其基数至少为|F||具有当前依赖覆盖问题的基数最优性，不能概括为仅有算法上界|已覆盖该类修复最小性。Proposition 1、式(12)—(14)|
|最少原生撤销根数G|上述最小化变量为S⊆M的修复要求，图中授权/证据节点由当前任务规格给定|M_r优化请求到来前共同选择的J与b₀，根可用性、独立处置与付费空根进入可行域|所核命题未覆盖。两个计数对象和量词不同|
|静态g₀=k|ACG没有以任务终止签名类及不可分割原生根定义该命题|依赖前沿的最小基数不能经变量更名推出静态根分区最优值|所核命题未覆盖。M_r对照见R2定理2|
|g_{r+1}≤g_r|ACG的r是修复过程中图更新的索引，实验另有修复交互预算|M_r的r为收到首次停止请求后至多执行的单任务重绑数|所核命题未覆盖相同模型的单调性|
|完整0…k−2资源节省谱|Proposition 1只对当前M证明唯一前沿，Proposition 2证明固定图上的单次检查终止和判定|谱要求∀k≥2、∀r≥1、每个节省值的有限需求族及所有更少根配置的排除证明|所核命题未覆盖完整谱|
|全局最少交互/整个任务保证完成|原文明确限定前沿最小性，取得证据可能产生新缺口或BLOCK，单次检查终止与整个交互终止分别声明|与有界全观察完成规约有不同目标|Appendix A.2—A.3明确限定，不能借“minimal”扩写全局成本最优|

表中ACG事实均来自同一取得版本的§3和Appendix A，M_r对照来自R2与R3冻结陈述。[ACG全文](D:/毕业设计/thesis_draft/sources/acg.txt) [资源定理](D:/毕业设计/research_recipe_r2/THEOREMS.md) [量词复核](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

**最终判定为机制近邻，且含修复最小性理论，所核命题未覆盖M_r撤销根资源谱。** 本轮可保留原谱的数学陈述，创新措辞收敛到“明确原生效果与重绑公理下的完整资源谱刻画”。依赖图、选择性失效和当前缺失要求的最小修复均归于已有工作。两种不同优化问题的区分也保留未来归约核查的空间。[R48 Appendix A.2](D:/毕业设计/thesis_draft/sources/acg.txt) [本项目定理边界](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

## 3 ResidualAuth的逐命题覆盖矩阵

ResidualAuth以合法grant/revoke/use序列的残余语言刻画授权历史。其Proposition 1、Theorem 1—3分别涉及最小监测状态、同闭包下未来状态分离、冗余委托的存储需求和信息受限错误下界。因此该文同时属于语义与理论近邻。[R49 §3—4](D:/毕业设计/thesis_draft/sources/residualauth.txt)

|待核主张|ResidualAuth原文的精确结果|与本项目关系|判定与定位|
|---|---|---|---|
|当前权限足以代表未来撤销行为|Theorem 1构造当前传递闭包相同而未来行为不同的历史族|直接覆盖“当前可达关系遗漏未来撤销所需信息”的一般认识|已有理论覆盖，PDF第4页|
|保留全部未来相关区别|ρ(h)为所有合法后续序列，Proposition 1以K_res计最少精确监测状态|约束本项目任何压缩K或证书缓存的充分性解释|已有理论覆盖。其K_res是等价类数量，与可能集合K分开|
|存储/资源下界|Theorem 2给出不同委托制度下的位数界，Theorem 3给出互信息约束下的决策错误界|计量对象为监测存储或信息，M_r计量既有独立撤销根|理论近邻，所核命题未覆盖根数节省谱|
|cleanup的含义|§3与Appendix A.4的Clean(G)删除不可达来源的授权边，作为更新后的图规范化|本项目cleanup是有批准、费用、观察与失败后继的可执行处置动作|语义对象不同，规范化规则本身未给出有费用处置义务规划|
|probe的含义|§5对保存的checkpoint执行未来更新和授权查询，评估记忆充分性|本项目probe是运行策略选取的核验，可创建会话、丢响应和新增严格义务|所核定义未覆盖认证副作用探测的完整转移规约|
|严格义务清空才允许终止|原文形式核心接受所有操作合法的前缀，use保持图不变，残余语言含空延续的定义|本项目Terminal还要求每个可能状态的严格处置义务为空|所核形式命题未覆盖该终态规则|
|W_h全观察有界完成|原文理论对象是合法语言监测，预算主要约束保留信息和实验接口|本项目判断是否存在获准动作，使全部观察后继在h−1内完成|所核命题未覆盖这一具体规划规约，通用递推另归R02/R37|
|文中出现“tool obligations”|Appendix L.2把声明goal/refusal/planning/tool obligations作为桥接实验完成端点|经验评分中的任务义务与运行语义中可创建、可处置、受预算约束的义务状态分别核对|该用词已核查，未据此认定其具有本项目W_h模型|
|原生现实符合性|Proposition 2限定selected-lineage contract下的账本—图对应，O.2列明其边界|与本项目“抽象保持需要前提”的方法论直接相关|已有条件性精化思路，本项目采用明确领域关系|

表中原文定位来自§3—5、Appendix A、L.2与O.2，项目规格定位来自SEMANTICS.md和ABSTRACTION.md。[ResidualAuth全文](D:/毕业设计/thesis_draft/sources/residualauth.txt) [本项目语义](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [抽象条件](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md)

**最终判定为语义及状态复杂度理论近邻，所核版本未覆盖本文带认证核验副作用义务的W_h完成规约。** 该结论保留领域规约贡献，同时把信念状态、有界可达性和屏障原理归于已有文献。关于授权历史必须携带未来相关区别的宽泛主张，ResidualAuth已有直接理论。[R49](D:/毕业设计/thesis_draft/sources/residualauth.txt) [本项目条件性H-S](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

上述差异属于具体状态与目标的映射边界。授权语言和状态空间框架可以承载进一步的领域扩展，本文当前没有由此得到表达能力或求解复杂度分离。两项文献分别关闭所列命题对照问题，原有通用方法归属继续有效。[已有方法归属](D:/毕业设计/research_secret_recipe/REPORT.md) [领域抽象限制](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md)

## 4 论文中保留的收口表述

两项定点核查完成后，论文保留M_r的距离、静态退化、单调性、紧界与完整谱。A/AB以领域规约、正确性边界和可复验证据呈现。ACG的修复最小性与ResidualAuth的状态下界在相关工作中明确承认，其他未决近邻沿用R3台账。由此，当前可以说明具体差异，整体首次性继续保持未决。[R3最终判定](D:/毕业设计/research_recipe_r3/VERDICT.md) [本轮定位](D:/毕业设计/thesis_draft/TASK_SCOPE.md)

本轮没有复现两篇论文的代码、性能或全部证明。PDF结构预检、关键词定位和所列章节阅读分别登记，任何未读部分继续保留其原有证据边界。[来源与版本](D:/毕业设计/thesis_draft/sources/RETRIEVAL.json)
