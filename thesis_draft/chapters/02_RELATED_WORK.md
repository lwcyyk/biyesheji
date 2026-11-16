# 第2章 相关工作与先例边界

## 2.1 比较对象与证据口径

认证生命周期研究涉及授权表达、秘密托管、执行时控制、撤销后状态、配置资源和模型符合性。本文按这些问题层次比较已有工作。双报告的R01—R47编号继续使用，新增文献接续编号，十项重点近邻采用M01—M10作为矩阵索引。原文取得、选读范围和版本差异均记录在文献表中。[底座调研](D:/毕业设计/thesis_draft/sources/survey_report.txt) [统一书目](D:/毕业设计/thesis_draft/REFERENCES.md)

比较以明确的输入、动作、计量对象和量词为单位。例如，图中缺失要求的最小基数、未来授权监测的最少存储位数和初始凭据配置的最少撤销根数分别对应不同优化问题。两项新取得近邻的正式命题约束本文的贡献表述，其实验性能仅作为作者报告保留。[定点核查](D:/毕业设计/thesis_draft/OVERLAP_CHECK_FINAL.md)

## 2.2 部分可观测规划、安全屏障与有界完成

部分可观测规划以可见历史确定信息状态，统一处理信息获取和控制。Carr等研究部分可观测条件下的安全屏障，相关有界可达性和多成本POMDP工作提供安全动作约束、有限期限与资源约束的通用基础。本文的W_h递推采用这些已有思想，在领域状态中显式加入认证核验所产生的材料、批准变化、预算消耗和严格处置义务。[R01—R04、R37的既有核验](D:/毕业设计/当前方案双报告_2026-11-03/文献核验表.json) [领域递推](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

Rivest—Schapire的homing sequence学习、Black Box Checking以及学习与屏障组合工作表明，无reset和性质导向信息获取已有研究基础。本项目A接收审定的有限候选语义集合，承担保守更新与安全选择。真实服务是否落入该候选集合，仍需原生来源和抽象保持证据。[R04—R06调研](D:/毕业设计/thesis_draft/sources/survey_report.txt) [具体到抽象关系](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md)

## 2.3 性质导向取证与配置冲突

GBS、ECD/EC²和DRD分别研究假设区分、决定等价类与重叠决策区域。DRD已经使用高阶关系处理多个假设整体缺少共同决策的问题。本文的三世界例用于检验实现是否遗漏高阶冲突，其贡献落在证书作用域与检查规约。B-A是项目实现的性质计数选择器，原报告已限定其与完整GBS理论的对应程度。[R07—R09及基线审查](D:/毕业设计/thesis_draft/sources/survey_report.txt) [三世界证书](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md)

认证补证同时具有观察和状态转换效果。AB反馈可以改变查询排序，但配置分歧本身并不授予执行权限，动作仍须满足批准、预算与W_h条件。当前没有共同配置与所有观察策略都无法完成是不同命题，证书必须携带对应的初始K、动作范围和决策界。[AB接口说明](D:/毕业设计/thesis_draft/sources/technical_report.txt) [证书两种作用域](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md)

## 2.4 十项重点近邻矩阵

下表的“机制”是论文组织分类，包含系统、协议、形式模型和立场论文。每项工作按实际类型引用，已有理论均进入比较。[书目与阅读登记](D:/毕业设计/thesis_draft/REFERENCES.md)

|索引与R编号|工作与版本|主要对象及与本文的关系|阅读层次与证据|
|---|---|---|---|
|M01 / R48|Authorization Closure Graph，2026 v1|版本化授权依赖、选择性更新、依赖最小修复。覆盖局部修复最小性，M_r根数谱另行刻画|§3、Proposition 1—2、Appendix A，[全文](D:/毕业设计/thesis_draft/sources/acg.txt)|
|M02 / R49|ResidualAuth，2026 v2|残余授权语言、状态数与信息下界。直接解释当前权限相同而未来撤销不同|§3—5、Appendix A/L.2/O.2，[全文](D:/毕业设计/thesis_draft/sources/residualauth.txt)|
|M03 / R15|Root-Scoped Quiescence，2026 v1|根代次、在途载体、提交围栏与独立支持重绑。已有并发闭包理论|本轮摘要与引言，沿用R2章节核验，[全文](D:/毕业设计/thesis_draft/sources/quiescence.txt)|
|M04 / R14|AID-Guard，2026 v1|授权至提交效果、未知结果与后继操作约束|本轮摘要与引言，[全文](D:/毕业设计/thesis_draft/sources/aid_guard.txt)|
|M05 / R13|SUDP，2026 v4|请求者、用户批准和保管者之间的秘密使用委托|本轮摘要与引言，[全文](D:/毕业设计/thesis_draft/sources/sudp.txt)|
|M06 / R50|PAuth，Beyond OAuth，2026 v2|自然语言任务切片与带来源的操作参数授权|摘要与引言，[全文](D:/毕业设计/thesis_draft/sources/pauth.txt)|
|M07 / R51|Heartbeat-Bound Hierarchical Credentials，2026 v1|心跳新鲜性约束下的层级凭据撤销窗口|摘要与引言，[全文](D:/毕业设计/thesis_draft/sources/heartbeat.txt)|
|M08 / R52|API Secrets…Vault-Mediated Execution Boundary，2026 v1|模型选择连接器，可信边界供应认证秘密|摘要与引言，[全文](D:/毕业设计/thesis_draft/sources/vault_execution.txt)|
|M09 / R12|Position: AI Agents Need Authenticated Delegation，ICML 2025|连接代理委托、可审计责任链与现有身份基础设施的立场论文|PMLR题录和摘要，[官方快照](D:/毕业设计/thesis_draft/sources/icml_delegation_metadata.txt)|
|M10 / R11|Verifying Account Ecosystems With Graph Transformations，EuroS&P 2026|RAG图重写与CTL分析动态账户生态|机构摘要与题录，全文覆盖未决，[来源](D:/毕业设计/thesis_draft/sources/rag.txt)|

### 2.4.1 两项逐命题对照

ACG的最小修复前沿由当前缺失要求在无条件INHERIT关系中的极小元素组成。Proposition 1证明任何具有相同依赖覆盖的请求集合都包含该前沿，因而给出最小基数。它固定候选动作和当前图状态，原文同时限定该结果对完整交互总轮数的含义。本文的g_r则先选择一个覆盖全部首次停止请求的共同根配置，再为每个请求选择重绑与整根撤销计划。两者的选择变量和量词顺序有实质差别。[R48 §3.2、Appendix A.2](D:/毕业设计/thesis_draft/sources/acg.txt) [M_r定义](D:/毕业设计/research_recipe_r2/THEOREMS.md)

ResidualAuth用ρ(h)刻画授权历史的全部合法延续，给出同传递闭包内的未来状态分离以及存储下界。该认识直接限制了只保存当前active状态的认证抽象。其形式核心中的Clean(G)是授权图更新后的规范化，实验probe是未来更新与查询的诊断。本文另把认证式核验产生的会话与未知材料记为严格义务，并在统一可见策略中计入其处置批准、费用与所有结果分支。所核命题未覆盖这一具体规划规约，W_h的通用原理仍采用既有有界可达性。[R49 §3—5、Appendix A与L.2](D:/毕业设计/thesis_draft/sources/residualauth.txt) [本项目规格](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

这两项定点核查保留完整资源谱的数学陈述，并收缩关于依赖维护、未来敏感授权和最小修复的一般原创措辞。各命题的覆盖、未覆盖及版本边界见单独矩阵，整体优先权继续维持近邻未决。[完整覆盖矩阵](D:/毕业设计/thesis_draft/OVERLAP_CHECK_FINAL.md)

### 2.4.2 其余八项的机制归类

**Root-Scoped Quiescence。** 该工作以根代次和接收端围栏处理委托、异步载体及独立支持重绑，并给出条件性组合结果。本文沿用其关于未来效果闭包的认识，用OAuth轨迹定位原生前提，并单独研究固定重绑预算下的根资源谱。[R15](D:/毕业设计/thesis_draft/sources/quiescence.txt)

**AID-Guard。** 该工作把批准请求绑定到提供方提交，在结果不明时保留预留，并限制重试与后继操作。本文借其区分准入、效果和恢复前提，把丢响应和剩余处置工作纳入有限模型，现有规划宏的原生符合性仍需证据。[R14](D:/毕业设计/thesis_draft/sources/aid_guard.txt)

**SUDP。** 该协议由请求者提出规范化操作、用户批准、保管者执行秘密使用，研究秘密保密和授权完整性。本文将此类机制作为可信执行边界的近邻，配置问题仍需核对原生撤销单位、目标根资格以及生命周期终态。[R13](D:/毕业设计/thesis_draft/sources/sudp.txt)

**PAuth。** 本轮取得的v2题名为Beyond OAuth，使用自然语言任务切片和签名封装关联操作参数及来源。其重点是具体操作对任务的忠实性。本文承认任务精确授权先例，将问题收敛到获准接口下的认证效果、停止粒度和资源配置。[R50](D:/毕业设计/thesis_draft/sources/pauth.txt)

**Heartbeat-Bound。** 该工作把后代凭据有效性与父节点心跳新鲜性联系起来，撤销窗口结论依赖时钟偏差、验证策略及密钥保护等条件。本文把这类机制作为可能具有更强停止契约的输入，既有双平台数据按实际接口解释。[R51](D:/毕业设计/thesis_draft/sources/heartbeat.txt)

**API Secrets保险库代理。** 该工作研究模型上下文与秘密使用边界，报告保险库介导的受控黑盒测量及错误连接器配置的负例。本文与其共享秘密托管动机，测量重心放在原生撤销、观察语境和未来处置前提。[R52](D:/毕业设计/thesis_draft/sources/vault_execution.txt)

**ICML委托认证。** South等的立场论文主张可认证、可审计的代理委托，并讨论OAuth、OpenID Connect和代理专属凭据的衔接。本文以其说明基础设施背景，进一步给出有限问题规格、受限资源定理和版本限定的撤销行为数据。[R12](D:/毕业设计/thesis_draft/sources/icml_delegation_metadata.txt)

**RAG。** Murphy与Radomirović通过资源访问图、图重写和CTL分析动态账户生态。本文采用其动态图表达作为直接近邻。当前取得范围为机构题录和摘要，具体能力排除保留未决，配置理论仍须明确本身的计量目标和前提。[R11](D:/毕业设计/thesis_draft/sources/rag.txt)

## 2.5 资源谱的数学近邻

Fomin等的categorical clustering已以多数Hamming代价求固定簇中心。把任务停止矩阵按列分到根后，根终态标签与该工具直接相关。本文距离还要求非平凡请求同时存在两类可用根，并对每一请求分别约束移动数。Hamming范数中心文献又说明最大距离预算已有先例，因此完整谱的候选增量集中在共同初始配置、独立根计费和每个参数值的匹配构造。[R53—R54核查](D:/毕业设计/research_recipe_r3/PRIORITY_AUDIT_R3.md) [资源谱](D:/毕业设计/research_recipe_r2/THEOREMS.md)

约束聚类、分区距离和组合重配置提供成员分组、硬约束与一步变化的通用框架。角色挖掘与密码化动态访问控制则分别涉及授权覆盖资源和撤销更新费用。这些文献的原有目标与M_r有不同边界，R3已登记12项全文的读取范围及尚未关闭的分支。定点核查结束后，这份较广优先权台账继续有效。[R55—R64及未决项](D:/毕业设计/research_recipe_r3/PRIORITY_AUDIT_R3.md)

## 2.6 已排除机制与负结果

|机制|历史审查结果|论文中的保留位置|
|---|---|---|
|A2完整后续成本搜索|同下界通用分支定界复现|完整成本和公平对照的设计依据|
|A3商键缓存|三个历史诊断零命中|压缩前提与失败记录|
|B2原生分离割|通用同预处理等效|领域约束编码|
|B3组件前沿|20输入中17例回退|适用结构与计算开销限制|
|AB2区域查询界|通用DRD/HEC覆盖|决策区域先例及静态条件|
|AB3证书重放|通用重放同机制，另有scope反例|检查器合同和审计记录|
|B4路径类压缩|通用同等价关系预处理复现|受限保持性质与工程规约|

该表来自四缝审查和双报告冻结记录。四条进一步分离靶声明也全部淘汰，留下的动态重绑结果以资源刻画定理保留。[负结果原始审查](D:/毕业设计/research_secret_recipe/REPORT.md) [v1.2证据边界](D:/毕业设计/thesis_draft/sources/technical_report.txt)

密码学支线已有条件性代数刻画、有限证书和本地参考执行，结构分块等效、成功域缩减以及通用gate直接输出支持等结果限制了其完整成本主张。本文将其作为已归档的辅助研究背景，主线贡献计数采用前述三项。[密码学审计素材](D:/毕业设计/thesis_draft/sources/survey_report.txt) [当前论文范围](D:/毕业设计/thesis_draft/TASK_SCOPE.md)

## 2.7 本章小结

已有工作分别承担任务授权、秘密代用、执行效果控制、撤销闭包与授权状态理论。本文在这些前提之上组织认证生命周期规格、M_r完整资源谱和原生语义证据。相关工作中的理论贡献均予承认，差异按具体命题而非系统名称判断，当前总体优先权保留近邻未决。[定点结论](D:/毕业设计/thesis_draft/OVERLAP_CHECK_FINAL.md) [贡献定位](D:/毕业设计/research_recipe_r3/VERDICT.md)
