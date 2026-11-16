# NR3-1来源定位、先例核对与过程归属

2026-11-07，AUTO-RESEARCH-NORMAL3-013。当前对话内知情模型辅助纸面研究。本轮网络获取、外部联系及原生调用均为0。

## 1. 实际依赖

|来源|实际读取/复用范围|本轮责任|
|---|---|---|
|[CT-1 CUT_TREE_LEMMA](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_cut_tree/CUT_TREE_LEMMA.md)|收缩大边、每块至多一个类型点、标记/未标记块及B≤A−1|R≤s−1的直接图论基础|
|[CT-1 COUNT_BOUND_AND_TIGHTNESS](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_cut_tree/COUNT_BOUND_AND_TIGHTNESS.md)|模板计数图、每行小割、实际profile合并、计数紧界与正规形范围|固定p的原行割定义和H_count保持|
|[CT-1 DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_cut_tree/DECISION.md)|当前H_count状态、H_normal队列、原文绑定和暂停状态|新结论沿原证据等级更新|
|[HG-1 MODEL_AND_CONJECTURES](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_general_radius/MODEL_AND_CONJECTURES.md)|固定p/原重数/逐行预算/自由模式列和的完整合同|反例排除的冻结对象|
|[HG-1 PROOF_OR_COUNTEREXAMPLE](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_general_radius/PROOF_OR_COUNTEREXAMPLE.md)|二端支撑任意r、r=2/s≤3正规化、固定列和反例、轻型恢复责任|受限正面结果与本轮原合同反例区分|
|[HG-1 DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_general_radius/DECISION.md)|§5完整4/4三支撑试件及原状态|正例复核，未将其提升为全称结论|
|[AF-1 SOURCE_AND_THEOREM_MAP](D:/毕业设计/research_main_innovation/main_topic_selection/ae_t3_alternative_frameworks/SOURCE_AND_THEOREM_MAP.md)|NF25精确模型/支持、KKM费用的原核读记录|已有结构化ILP接口不承诺森林|
|[PM2020_T2_IMPLICATION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_pm2020_check/PM2020_T2_IMPLICATION.md)|Obs4/5、Lemmas10–12、Prop2/Th7的既有版本限定映射|固定模板总预算与本轮固定p逐行合同分别判断|

历史稿在本轮之前已有当前上下文的模型辅助核读；本轮复用并定点检查，独立性不随重读升级。它们的历史字节由INPUT_HASHES.json固定。

## 2. NF25的新增定点原文核对

来源：[IPEC2025正式PDF](D:/毕业设计/research_main_innovation/main_topic_selection/ae_t3_alternative_frameworks/sources/NFOLD_IPEC2025.pdf)，DOI10.4230/LIPIcs.IPEC.2025.15；题录/完整v4对应按AF-1保留。

本轮在既有解析文本定位Lemma5，并从原PDF渲染和目视核对物理第5页、印刷15:5的完整页面。页图为page_images/NF25_p05.png。预检NF25_preflight.json为结构PASS，15页，SHA-256为801425f93b2294e091e9d8baa90d52e08c8b8f4b723b7b4da7477a3e5e87c34a；只承担结构/身份。

原文Lemma5把源r作为全局行数；本文改写为a，避免与Hamming半径混淆。其逐块支持保证为
\[
|\operatorname{supp}(x^{(b)})|
\le2(a+1)\log_2(4(a+1)\Delta).
\]
证明逐块保持 \(D_bx^{(b)}\) 与局部总数，调用源引用[12]的整数支持界。没有陈述“模式—类型全局支撑无环”。

本反例的五条预算可按既有n-fold表示加入五个slack，a=5、Δ=1，再用一个全1slack块补和。上式大于三模式块宽3，允许原唯一有环表；因此与本轮反例相容。这里只核查这项具体支持路线，其他未展开的源推论仍有自己的证明责任。

未重读NF25整篇，未把其引用[12]登记为本轮已取得原文。定理1及费用来源复用AF-1，新增视觉范围只有15:5。

## 3. 经典来源的复用范围

Gomory/Hu1961的原文身份、551–560相关目视范围和基本割性质由CT-1 sources记录固定；本轮直接使用已证图论推论，没有重复下载或声称重新阅读全文。

普通运输多面体森林基解属于标准工具，但加入逐行不等式后，原结论的前提改变。本轮反例从原行预算自动推得模式总数饱和，模式列和未作为额外约束给定。因此其范围严格覆盖HG-1尚未关闭的原固定p合同。

目前核对的这些来源没有提供本轮同合同森林定理；反例已直接排除该全称陈述。非profile残余界、单圈正面定理和相应反例是否有准确发表表述，仍待定点先例核查。本轮没有全球首次结论。

## 4. 数学过程归属

- 监督模型辅助提出：由CT收缩块推出非profileR≤s−1的路线。
- 本轮补全：块内类型/模式不可被原行割分开、P纯化、森林等价接回、计数界和补全行的算术合同。
- 本轮新纸面推导：5行9列反例、六支持排除、唯一性证书、所有r≥3的符号族。
- 本轮新纸面推导：两个三支撑R型的完整r=3分类、紧单圈正规形、4/4森林子域、逐行不增加加强合同反例和9列最小性。
- 原有正例：HG-1五行4/4试件，本轮复核并保持其范围。
- 下一轮动作：r=4单圈正规形及给定合法起点，当前未证明全称结论。

数学均为人工可核对的符号/有限分类过程，由当前模型完成；没有执行数学搜索程序或调用外部模型。研究者已有人工S1/S2范围不扩为本轮认证，外部数学读者/证明助手均待取得。

## 5. 实际操作与文件

只新增三份主稿、来源/过程索引、必要页图、历史输入哈希与文档检查。所用脚本只读取/渲染PDF、固定哈希和检查文档格式；没有候选代码、参考代码、数学枚举或性能测试。

COL2026继续ACTIVE_RETRIEVAL_PAUSED_BY_USER；FS23继续DEFERRED_NO_NEW_SOURCE_LEAD。原T3/T+、H_count和SG-1分离状态各自保留，原固定p森林猜想由本稿明确反例更新。
