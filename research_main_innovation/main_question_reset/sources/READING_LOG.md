# MQ-RESET-2来源、版本、定位与证据等级

日期2026-11-06。当前主文稿版本MQ-RESET-2；旧MQ-RESET-1主文件和旧READING_LOG均按原字节保存在round_MQ_RESET_1_snapshot。新旧输出不混计。本轮沿用academic-research-suite的来源核对流程，全部研究阶段在当前会话内执行；没有调用新研究子代理。

## 1. 约束与输入继承

已确认范围为“允许相关理论方向，以精确问题和先例差异为准”。本轮公开原文、纸面推导和已有结果分析获得授权。正式主要贡献类型、周期、硬件、数据与导师验收待确认。机制实现仍需严格分离。

以下五份指定文件按原路径完整获取，并围绕当前问题核读其结论、范围和进入条件；路径/哈希见MQ2_INPUT_BINDING.json：

- prediction_rematerialization_screen/FINAL_DECISION.md：已覆盖子族、一般DAG未决和实际接口边界。
- prediction_rematerialization_screen/SAME_MODEL_PRIOR_ART.md：paging、闭包缓存、黑pebbling及metric映射的条件。
- ci02_cost_problem_screen/NOVELTY_DECISION.md：整份驻留与SC/MC归约；Q-next的历史状态。
- ci01_policy_regression/FINAL_DECISION.json：完整离线链的一项普通实现缺陷、最小修复和部署限制。
- workspace_asset_review_2026-11-04/REPORT.md：十二类资产、CS03历史证据与已归档机制。

同时复用main_topic_selection/TOPIC_DECISION.md、FIRST_PROOF_ATTEMPT.md和sources/READING_LOG.md中的最新A-E及已写出的手工证明。原M_r公理、重数工具和原生缺口分别核读R3 MATH_REVIEW与NATIVE_PREMISES。新引理没有升级旧实验/数字的证据级别。

## 2. 最新计划书和当前源码

根目录实际发现的最新详细计划书为《面向AI智能体的认证语义感知与可撤销凭据管理方法及系统研究_详细计划书_2026-11-04.docx》，v1.0。以word/document.xml文本节点直接提取至LATEST_PROPOSAL_MQ2.txt，按DOCX原段落序号标记[Pn]。重点核读§3.1整体问题/验收、§4.1 L/R/E及保留、§4.3资源目标、§5.4抽象保持和§11流程/预算。计划书表达需求和拟建能力，不能代替部署记录。

当前源码根为`D:/毕业设计/auth-lifecycle/src/auth_lifecycle/`。源字节冻结在project_source_mq2下的`*.py.txt`中，仅作已有源码副本，没有修改或执行研究内核。

|入口|函数与行号|本轮观察及边界|
|---|---|---|
|a/candidate.py|Shield:15–38；solve:41起|相同赢集约束下选择策略；源码入口不能单独支持新的效率主张|
|a/bridge.py|Feedback:16起；get:20–75|调用B搜索和冲突检查，区分固定配置冲突与联合观察不可行；不重开AB2/AB3|
|b/search.py|solve:7–36|完整有限catalog任务子集配置搜索、独立checker和节点界；未将它等同于M_r任意重绑|
|b/engine.py|resources:12起；actions:57起；available:73起；preserves:83；goal:87；plan:93–121|登记根效果域、撤销/关闭/gate动作、前缀保留；静态目录合法流程|
|b/_kernel.py|native_units:8–12；configuration:15–43；live:46–52；final:55–62；menu:65–76；transition:80–96|原始解释器核对账户、权限、批准、预算与前缀保留；菜单没有任意任务原子重绑|
|b/model.py|prepare:23起|schema与预算/路径输入检查|
|online_state/storage.py|AuthorityStore:46起；grant:161；admit:197–225；revoke:284–307|task/account/audience/generation绑定与权威状态；符合性不由源码阅读独自证明|
|online_state/protocol.py|normalized_request:54起|请求的rid、handle、task、account、audience、generation及operation投影，当前白名单范围|
|experiment/planning.py|35–63|继承已知契约单路径/空probe profile边界，无新查询困难被激活|

夹具`examples/b/shared_root_conflict.json`、`mixed_alternatives.json`按原字节复用，已读取任务、synthetic_grant、效果域、停止/保留、批准与预算。证据类别为PROJECT_SYNTHETIC_FIXTURE；本轮没有把它们描述成生产执行或作者基准。

R3 NATIVE_PREMISES.md §2–3对任意目的根资格、原子支持转换、旧支持退役及在途闭包的缺口继续有效。其待授权测试协议仅被阅读，本轮没有执行协议。

## 3. 直接学术近邻

PDF在theory_2026_11_06中原样复用，相关结构预检sidecar与字节哈希绑定；复制文件路径不同不改变hash对应。结构PASS仅用于页锚完整性。全文阅读声明限于下表，研究者本人阅读状态为unknown。

|ID|题名/作者/年份/版本及原文|本轮实际重核与使用|
|---|---|---|
|COL2019|*Low-rank binary matrix approximation in column-sum norm*；Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov；2019；arXiv1904.06141v1，18页作者稿。[PDF](https://arxiv.org/pdf/1904.06141v1)|摘要、§1方法；PDF p4 Definition1坐标关系，p5有序中心正式问题/Theorem2；pp9–11 Lemma4代表串/例外坐标及使用。关键p4/p5在上一轮已有渲染目视核对，本轮沿用该字节并重核文本。没有独立重证完整PTAS|
|CAT2021|*Parameterized Complexity of Categorical Clustering with Size Constraints*；Fedor V. Fomin、Petr A. Golovach、Nidhi Purohit；2021；arXiv2104.07974v1，32页；初版WADS2021接收按首页记载。[PDF](https://arxiv.org/pdf/2104.07974v1)|摘要、§1 Theorem1/initial-cluster讨论；PDF p3重复列与容量导致拆分，§2 Observation1，p9 Observation2–3，pp10–11 Lemma3及Lemma4候选中心方法。总费用B与逐行r分开；完整DP未独立重证|
|MISS2025|*Binary k-Center with Missing Entries: Structure Leads to Tractability*；Farehe Soheil、Kirill Simonov、Tobias Friedrich；2025；arXiv2503.01445，取得PDF首页日期2025-03-04，28页；修订号未另确证。[PDF](https://arxiv.org/pdf/2503.01445)|摘要、PDF pp1–5 Theorems1.1–1.4，§2 Definition2.1与known-entry mask/图；只使用参数和可行域比较，没有把ILP联系转作A-E下界|
|HAM2019|*On Computing Centroids According to the p-Norms of Hamming Distance Vectors*；Jiehua Chen、Danny Hermelin、Manuel Sorge；2019修订；arXiv1807.06469v3，21页。[PDF](https://arxiv.org/pdf/1807.06469v3)|复用摘要/pp1–4中Closest String与p=∞的背景和定义；不把有限p的下界移作r下界|

2021的m/n与本轮A矩阵的行/列角色按各自目标核对，公式比较均明确。COL2019用的q在本轮等于2^g−2，palette大小为g；两者不合并计数。

## 4. 官方规范

RFC7009，*OAuth 2.0 Token Revocation*，Torsten Lodderstedt、Stefanie Dronia、Marius Scurtescu，2013-08，Standards Track。[官方原文](https://www.rfc-editor.org/rfc/rfc7009)。文本从ci01_cutoff_audit既有官方副本复用至rfc7009_mq2.txt。

实读§1、§2、§2.1–2.2，定位：本地行121–128关联grant范围，153–158撤销类型与请求，255–271提供方级联策略，273起成功/无效token响应。规范只在列明接口内比较，未用其证明任意提供方的全部行为。

## 5. 本轮推导的归属与状态

|内容|状态与归属|
|---|---|
|S0：同根r+1个同签名任务固定profile|R3既有重数引理的直接表达；继承工具|
|S1：gr+1保留/解恢复|本轮完整手工推论；标准饱和、鸽巢、预算工具；没有原创性确认|
|S2：gr统一截断反例及普适阈值紧性|本轮完整手工构造；只约束明确的统一删列规则；不提供一般kernel/算法下界|
|一般palette Lr+1饱和|自含通用预算论证；同等赋给强基线，不冒充COL2019已陈述定理|
|有界重数域到全部A-E的见证提升|本轮手工接口保持：恢复任务全行零误差，W和E大小不变|
|A-E目标算法界|CONJECTURE，尚未证明；完整先例状态UNRESOLVED_PRIORITY|
|实施门|CLOSED；没有具体强G必要时间下界和严格差距实例|

本轮所有数学实例为合成对象，手工给出可核对数值。没有调用穷尽枚举、SMT、模型检查器或新验证器。

## 6. 检索限制与完整性

新增三条定向查询及搜索连接器原始失败响应保存为MQ2_SEARCH_RESULT.json。连接器返回Transport send error；本轮没有取得新搜索结果。已取得论文和既有定位足以进行本轮模型/阈值证明，后续覆盖检查继续保持未完成。

上一轮arXiv429/超时记录原样放在theory_2026_11_06/RETRIEVAL_FOLLOWUP_QUERIES.json，本轮没有追加该服务请求。检索失败没有被转换成“无相关工作”的证据。

MQ2_INPUT_BINDING.json冻结原输入及原源码；MQ2_PREVIOUS_ROUND_BINDING.json绑定前版快照；MQ2_PROOF_STATUS.json登记结论边界；MQ2_DELIVERY_VALIDATION.json检查字节、JSON、链接和文档范围；SOURCE_MANIFEST_MQ2.json冻结当前交付。文档检查不能替代数学外审和文献优先权。

全部运行脚本限于文件复制、DOCX/PDF文本读取、元数据和文档完整性处理；新的算法/协议/保护机制代码为0。真实服务调用、账户操作、发布和外部消息发送均为0。
