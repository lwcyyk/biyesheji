# 第3章 认证生命周期的有限形式化

## 3.1 控制目标与可信边界

本章沿用L、R、E三类停止语义。L约束受控入口的新准入，R约束声明原生范围与接受路径，E约束声明效果域的后续提交。保留目标要求指定任务在适用执行前缀仍有合法支持。有限B模型直接处理Local/Native目标，广义E依赖效果路径和提供方契约。[系统规约](D:/毕业设计/thesis_draft/sources/technical_report.txt) [并发契约](D:/毕业设计/research_recipe_r2/CONCURRENT_CONTRACTS.md)

四阶段设计把账户、秘密保管、批准、规划、执行、证据和持久协调分为逻辑职责。现有L0研究内核实现其中有限模型与检查部分，可信UI、跨端恢复和完整事务库仍属于设计层。论文按这种层次区分模型公理与部署事实。[四阶段映射P0117—P0198](D:/毕业设计/thesis_draft/sources/technical_report.txt)

## 3.2 信息状态与保守更新

设有限模型M由候选服务语义m、外部状态s和显式结果边组成。信息状态为z=(K,h,boundary)，K⊆{(m,s)}。每个具体节点记录账户、事实、批准、资源预算、能力和严格义务，h为剩余决策步。策略只依据可见观察分支，同一可见历史下使用共同动作。[模型定义](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

对动作a及可见结果o，更新采用全部相容后继的并集。[观察更新定义](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

\[
Post(K,a,o)=\{(m',s')\mid\exists(m,s)\in K,\ (m,s)\xrightarrow{a,o}(m',s')\}.
\]

响应丢失可同时保留已生效和未生效、已创建和未创建等分支。已登记的外部语义变化通过跨世界边进入后继，未登记观察触发边界状态并停止发放完成保证。[更新规则](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

## 3.3 副作用、前置条件与终态

probe产生新的持久能力c时，L0规约要求目标节点登记close:c严格义务。未知句柄继续保留可能效果，只有具备批准和声明覆盖能力的动作才可结清。非探测动作产生的长期保留能力是否需要关闭，由任务目标决定。[义务规则](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [未知句柄说明](D:/毕业设计/thesis_draft/sources/technical_report.txt)

Pre(K,a)要求K非空且所有可能节点安全，账户、批准和前置事实满足，每种资源余额足够，原生独立性具有登记依据，每个节点均至少存在一个后继。Terminal要求boundary为假，K非空，全部可能节点满足目标账户、安全与目标事实，并且严格义务为空。[Pre与Terminal](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

## 3.4 有界可完成区域

以W₀=Terminal为基例，后续区域由下式递推。[有界递推](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

\[
W_{h+1}=W_0\cup\{K\mid\exists a,\ Pre(K,a),\ Obs(K,a)\ne\varnothing,
\ \forall o\in Obs(K,a),\ Post(K,a,o)\in W_h\}.
\]

非终态中每次实际派发均消耗一个决策步，包括零请求费用的动作。允许菜单只保留全部后继进入W_{h−1}的动作。stay→s与finish→done共存时，可以在步界充足时先stay，但h=1只能finish，从而阻止无界滞留。[递推与stay反例](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

**条件性完成命题。** 若真实可能状态始终被K覆盖，动作前置和观察转换被忠实模拟，批准预算保守、副作用义务完整、回译真实可执行且终态反映真实目标，则从W_h出发按允许菜单继续执行，至多h个模型动作后达到目标并结清严格义务。证明按h归纳，基例由Terminal，归纳步由全部后继进入W_{h−1}。驱动器继续执行及操作返回属于前提，墙钟时间另有语义。[H-S论证](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [抽象保持条件](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md)

该有限终态表达声明时点的目标。若R或E需要未来持续保证，还须加入派生闭包、围栏或相应稳定性条件。已有并发分析采用有限安全不变集检查这些条件，相关共有原理归于既有工作。[并发终态补充](D:/毕业设计/research_recipe_r2/CONCURRENT_CONTRACTS.md) [R15](D:/毕业设计/thesis_draft/sources/quiescence.txt)

## 3.5 多世界证书与结论类型

P₁={a,b}、P₂={b,c}、P₃={a,c}两两相交而整体无共同计划，说明初始冲突核心需要支持任意有限世界子集。正策略选择一个获准动作并覆盖每个观察，反证对每个注册动作给出前置阻断或可达坏观察。证书同时绑定模型、K、界、动作宇宙、批准、预算和约束引用。[协议与反例](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md)

`no_common_immediate_completion`只支持当前一步共同完成失败，`bounded_policy_impossible`支持给定H内全部获准可观察策略失败。adaptive_probe可同时具有前者证书和两步成功策略。核心最小性保持not_claimed，未完成检查返回INCONCLUSIVE。[作用域定义](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md)

|结果|论文解释|
|---|---|
|FEASIBLE|具有完整界内观察策略，执行完成需另有运行证据|
|IMPOSSIBLE|给定模型、动作和步界内已穷尽反证|
|INCONCLUSIVE|搜索或检查限额耗尽|
|UNKNOWN|空K、非法输入或可观察模型外边界|

已声明的观察字符串UNKNOWN或response-lost仍可进入保守更新，与求解器状态UNKNOWN分别使用。[结果类型](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

## 3.6 抽象保持与实现限制

具体表到抽象表的关系分别检查状态覆盖、前置保持、观察相容、副作用覆盖、批准预算保守、终态反映和可执行回译。L0已实现有限关系检查与策略回译，真实服务到具体表的完整符合性、Python一般精化及部署隔离仍待证据。哈希绑定内容，来源真实性和授权有效性由外部可信链承担。[七组保持条件](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md) [可信输入](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)
