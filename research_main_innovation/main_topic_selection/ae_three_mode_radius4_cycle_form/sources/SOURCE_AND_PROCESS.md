# UR-1来源、过程与阅读范围

2026-11-07。三profile半径4验收及统一半径交换证明。当前对话内知情模型辅助纸面研究。

## 1. 完整读取和定点复用

|来源|本轮实际范围|使用|
|---|---|---|
|[NR3-1 RESIDUAL_REDUCTION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_three_mode_radius3_normal_form/RESIDUAL_REDUCTION.md)|全文|任意r的非profileR≤s−1、P纯化、固定p合同和行补全|
|[NR3-1 PROOF_OR_COUNTEREXAMPLE](D:/毕业设计/research_main_innovation/main_topic_selection/ae_three_mode_radius3_normal_form/PROOF_OR_COUNTEREXAMPLE.md)|全文|唯一单环反例族、原r=3分类/单圈结果、4/4子域、完整恢复边界|
|[NR3-1 DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_three_mode_radius3_normal_form/DECISION.md)|全文|原r=4待证对象、正例和优先权/实现状态|
|[CT-1 CUT_TREE_LEMMA](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_cut_tree/CUT_TREE_LEMMA.md)|已有证明复用，重点大边收缩/标记块及B≤A−1|残余数量基础；本轮没有重复获取或全文重读1961 PDF|
|[CT-1 COUNT_BOUND_AND_TIGHTNESS](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_cut_tree/COUNT_BOUND_AND_TIGHTNESS.md)|已有模板归约/实际profile量词复用|原高型阈值与计数状态保持|
|[HG-1 PROOF_OR_COUNTEREXAMPLE](D:/毕业设计/research_main_innovation/main_topic_selection/ae_heavy_type_general_radius/PROOF_OR_COUNTEREXAMPLE.md)|定点重读二端/r=2三profile森林证明；§7.1圈方向的既有记录复用|r=2强森林保证及标准循环操作来源|
|[AF-1 SOURCE_AND_THEOREM_MAP](D:/毕业设计/research_main_innovation/main_topic_selection/ae_t3_alternative_frameworks/SOURCE_AND_THEOREM_MAP.md)|已有源定理/版本记录复用，不登记新的原文精读|通用支持/求解器结果与本轮正规形分别判断|

主稿没有把历史T3、割树或NF25的复用变成新的独立外部核读。历史输入字节及哈希见INPUT_HASHES.json。

## 2. 三种责任

### 标准循环工具

EX为2×2运输循环：同型加减相抵，同模式加减相抵，整数非负步长取被减两项之最小值。这是标准代数事实，本稿逐项展开；HG-1 §7.1已写出一般圈方向及逐行预算可能相反的例子。

本轮没有绑定这一工具最早发表文献，亦未把行/列和保持包装为原创性。一般循环工具自身不保证所有附加预算单调。

### 已有割树残余计数

CT-1所依经典GH来源为Gomory/Hu1961，原p556 Lemma2及p560基本割定义/存在性；具体原文/页图/哈希在CT-1 sources。NR3-1进一步证明非profile型只能处于未标记块，因此R≤s−1。

该链在本轮作为已有结构引理使用，X/p保持给定解量词；没有运行割树找未知标签。

统一上界不调用NR3-1针对r=3的有限分类，也不调用完整T3求解器。它只依赖残余计数、P纯化及本轮EX证明；旧r=3分类现在可视为其特例回归。紧性另复用原反例族。

### 本轮预算方向证明

用户本次消息给出待核的S/D与方向路线，过程按模型辅助线索转交登记。本轮完成：

- 任意r的四类行公式；
- 同位正负/全正/全负的严格高重数矛盾；
- 不同增减位置的四类选择；
- D变化为±2ε，00/11保持、实际10/01单调；
- 补全回原行、常量行、轻型保留、原ID与全部中心恢复；
- r=4两项手工回归及统一r紧性；
- 后续四profile/r=3两环唯一表起点，作为另列参数范围的手工材料。

统一结论的原文优先权未在本轮完成。已核读通用支持定理、经典循环以及割树残余分别是工具，不自动构成整项预算单调正规形的已发表覆盖证据。

## 3. 手工材料与全称证明

- 全称EX证明：MODEL_AND_EXCHANGE_LEMMA §§3–6；给定真实约束标记，不使用未知解oracle。
- 全称正规化/恢复：PROOF_OR_COUNTEREXAMPLE §§1–2、6–7。
- r=4正例：该稿§3，完整A/Q/p/计数/中心，错误(3,4,3,4,4)→(3,4,3,2,2)。
- r=4下界：该稿§4，完整12列实例，唯一计数β=1。
- 每r≥3下界：该稿§5复用原NR3-1符号族，原重数不变，逐行预算强制唯一表。
- 下一范围起点：DECISION §6，s=4/r=3、三个4重型，唯一表β=2；未据此宣称四profile的全称2上界。

手算例只承担各例核验；统一上界依赖前述全称证明。没有执行数学搜索或穷尽程序。

## 4. 原ID、轻型和费用口径

实际profile合并只为高型选原代表ID。它只保证给定p的预测相同，原Q仍完整保存；原未选标签的中心词可以变化，但全部原标签按序输出。

给定原η时，轻型坐标逐一不动。只有计数表时，其计数逐项不动，恢复的型内排列保持所有行错误。输出费用包括完整K中心、模式ID和原p。空输入时按实际输出长度收费。

原未知标签求解、经典割树、给定解正规化、通用求解器和严格实现门各有独立责任。没有从多项式正规化推出新的T3未知解算法。

## 5. 独立性及实际操作

当前模型已接触原T3/NR3构造和证明，并接收本次具体交换线索，属于知情模型辅助复核。原始路线的AI参与、研究者组织及既有人工S1/S2核读范围沿已校正记录；没有新增外部数学读者或证明助手证据。

本轮仅原稿读取、纸面数学及文档取证。候选代码、参考代码、数学枚举程序、实验、原生请求、外部联系均0。COL2026暂停、FS23缺少新正文入口的状态保持，两个来源请求均0。

OUTPUT_CHECK.json只核验主稿存在性、格式/链接及历史字节，不能视作数学认证。
