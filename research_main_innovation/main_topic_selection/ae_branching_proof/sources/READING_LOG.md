# 来源、阅读范围及本轮证明归属

版本AE-BRANCH-1，2026-11-06。采用academic-research-suite的原文/推导/未决分离纪律；本轮所有证明工作在当前会话内完成，没有新子代理或外部数学审查。机制、求解器、穷尽验证器和证明助手均未执行。

## 1. 四份指定输入

|本地输入|本轮使用|
|---|---|
|main_question_reset/DECISIVE_DERIVATION.md，MQ-RESET-2|S0重数工具、S1/S2及恢复、A-E见证提升；研究者明确报告核读S1/S2|
|main_question_reset/RESEARCH_DECISION.md，MQ-RESET-2|有界重数A-E目标、强基线共享、实现门及原生条件边界|
|main_topic_selection/FIRST_PROOF_ATTEMPT.md，TOPIC-THEORY-1|固定配置距离、两根复杂度、通用bounded search和A5恢复|
|main_topic_selection/TWO_PRECISE_PROBLEMS.md，TOPIC-THEORY-1|原M_r全部量词、A-E目标、显式center关系映射；B路线不在本轮扩展|

全部按原字节复制并绑定于INPUT_BINDING.json。历史文件保持原状；新目录中的数学完成状态更新前轮“候选生成器待证明”的状态，保持版本可追溯。

研究者对S1/S2的核读只按当前消息明确范围登记于RESEARCHER_READING_ATTESTATION.json。该声明没有扩大为对本轮C1/C2、分支计数或通用形式的人工复核。

## 2. 本轮原文核查

PDF沿用已取得字节及其结构预检sidecar；三份PDF的SHA256与对应PASS记录绑定。结构PASS只约束页结构，不承担数学语义。INHERITED_READING_LOG.md原样保存前轮范围；本轮实际重核如下。

|ID|原文、版本及链接|本轮实读/使用范围|
|---|---|---|
|COL2019|Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov，*Low-rank binary matrix approximation in column-sum norm*，2019，arXiv1904.06141v1，18页作者稿。[PDF](https://arxiv.org/pdf/1904.06141v1)|摘要/§1方法、物理PDF p4 Definition1、p5正式问题/Theorem2及后续partition说明；复用pp9–11 Lemma4的前轮定位。本轮比较共同R子域、tuple中心和目标/参数；没有独立重证完整随机PTAS。2019摘要页版本快照已复用|
|BCC2018|Fedor V. Fomin、Petr A. Golovach、Daniel Lokshtanov、Fahad Panolan、Saket Saurabh，*Approximation Schemes for Low-Rank Binary Matrix Approximation Problems*，arXiv1807.07156，2018编号；取得38页，修订号未另核实。[PDF](https://arxiv.org/pdf/1807.07156)|摘要/概述；物理PDF p2 Binary Constrained Clustering定义及Theorem1，p5 k-Means例中全部关系相同/共享存储；重点区分总和目标与最大逐行预算。未将取得全文写成完整阅读全部证明|
|CAT2021|Fedor V. Fomin、Petr A. Golovach、Nidhi Purohit，*Parameterized Complexity of Categorical Clustering with Size Constraints*，2021，arXiv2104.07974v1，32页；首页注明WADS2021初版接收。[PDF](https://arxiv.org/pdf/2104.07974v1)|摘要、物理PDF p2 Theorem1/总预算；p9 Observation2–3，pp10–11 Lemma3和重复类/候选中心入口。用于预算、分拆和标准工具归属，不冒充共同小R精确界出处|

上述来源为作者稿，所列发表状态以取得稿件明确记载为限。论文内部原m/n与本轮输入行数m/任务数n分别映射。新通用定理使用q个中心及L=|R|；q与L不混为一项参数。

## 3. 本轮推导资产及状态

|编号|陈述|归属/检查状态|
|---|---|---|
|C1|固定绑定/单行每(root,bit)类截到r+1，逐处置保持≤r阈值|研究者路线，本轮完整手工证明；预算截断工具|
|C2|失败行上的分离/真实投影例外二择一|研究者提出关键引理，本轮逐任务反向证明及边界核对|
|C3|无匹配任务必在真实W错配并集|本轮完整手工证明|
|PATH|正确状态及全局W/E界、有限树可靠/完备/NO|本轮完整手工证明|
|COUNT|两类步骤交错词节点界及目标指数|研究者提供方向，本轮写出全树计数和各项成本|
|RECOVER|实际处置下的profile合并、分离行/例外恢复|继承A5工具，本轮补全成功猜测不同、空根、费用和S1情形|
|GENERIC|共同R的q^{O(L)}(L(r+1))^{O(Lr)}poly(mn)型精确界|本轮自含推广证明；独立优先权待审|

完整手工证明代表推导已逐步写出，不表示已经获得外部读者或形式化内核确认。没有调用新算法或穷尽实例来替代这些全称论证。

## 4. 反例与边界审查记录

本轮检查重复码、空根、相同完整profile、X∩E、错误投影恰好匹配其他码、同签名任务分拆、r=0、L=1、q=1、已选行失败及成功时猜测/实际标签差异。未发现违反完整引理前提的反例。

压力审查纠正了一处草稿说明：q=1、R={0,1}时中心内容仍未知，是Closest String；正式稿改为本构造的(r+1)^{O(r)}界，r=0才退化为检查全部输入串相同。该纠正针对边界解释，主分支证明及通用规模式保持成立。记录见PROOF_AUDIT.json。

存在的警示例仅否定“可匹配就是真实非例外”和“搜索W/E直接作为最终见证”等错误加强版本；完整命题和前提保存在PROPOSED_ROUTE.md及五份主稿。

## 5. 优先权核查与获取限制

本轮向公开搜索连接器提交三条定向查询：binary constrained k-center/relation/exact parameterized；binary constrained/common relation/center；binary matrix/row-wise/clustering parameterized。原始返回为Transport send error，保存PRIORITY_SEARCH_RESULT.json。

前轮arXiv429/超时记录保留于RETRIEVAL_LIMITATIONS.json，本轮没有继续受限服务的请求，也没有绕过验证或限额。已有本地原文足以支持具体模型比较和本轮推导，后续先例查证仍不完整。

因此数学状态为AE_PROVED_PENDING_PRIORITY。未授予首次性、最优性、严格资源分离或机制实现许可。若已有原文在相同关系/半径/功能/信息条件下给出同级界，需以该原文更新覆盖判断；本轮自写通用构造只属于数学结果，不是已发表先例证据。

## 6. 文档及执行纪律

INPUT_BINDING.json绑定来源，PROOF_STATUS.json分离数学/先例/实现状态，PROOF_AUDIT.json记录逐前提审查及一次边界更正，DELIVERY_VALIDATION.json记录文件哈希/JSON/链接检查，SOURCE_MANIFEST.json冻结当前交付字节。

所有执行工具仅用于复制、读取、定位、文档写入及哈希/链接检查。机制实现、新求解器/验证器、认证服务调用、真实账户操作、性能采样、外部发布及外部消息发送均为0。
