[AUTO-RESEARCH-TPLUS-003]
请执行“T+规范化主命题与跨表述先例蕴含核查”。

用户已授权监督对话审查后自动续接。监督核读TT-1，当前支持TRANSFER_PROVED_PROJECT_T3_DEPENDENT的证据定位；一般SC已在项目依赖下闭合。接下来集中判断这份精确理论结果的发表增量，避免继续扩张指数猜想或重复迁移审查。

一、冻结对象与已有证据

读取：
D:\毕业设计\research_main_innovation\main_topic_selection\ae_sc_t3_transfer\ 下四份主稿；
D:\毕业设计\research_main_innovation\main_topic_selection\ae_t3_alternative_frameworks\SOURCE_AND_THEOREM_MAP.md
D:\毕业设计\research_main_innovation\main_topic_selection\ae_t3_p26_coverage\COVERAGE_TEST.md
按需复用其余已完成覆盖稿及已取得原文。

T+：
Q∈{0,1}^{K×w}，A∈{0,1}^{M×v}；
静态坐标域Omega_t⊆[w]；
显式行标签成本tau_i(p)∈{0,1,2}；
寻找eta_t∈Omega_t及每行一个全串固定p_i，
使tau_i(p_i)+Σ_t[A_it≠Q[p_i,eta_t]]≤1。
确定性精确时间2^{O(w log(w+2))}poly(N_T)，统一固定输入次数，完整恢复模式和行标签；允许重复/闲置角色。

T+依赖项目T3/PR-C3。它覆盖原r=1及SC实际来源，但优先权未决。COL2026主动获取继续暂停。外部联系、机制代码、穷尽验证及真实服务操作保持未开始。

二、先写一份不依赖认证术语的规范定理

用可直接交给算法读者的标准记号陈述T+，包含：
输入编码、量词、参数、任意成本/域的范围、决策与见证输出、空域、确定性、时间和项目证明依赖。

同时建立三个严格包含/特化层：
A. tau全0、Omega全域：原半径1共同关系子模型；
B. tau全0、Omega可变：固定全局模式总库的逐坐标子关系；
C. 完整T+：逐行标签成本和静态域。

明确“中心标签数量K”“全局模式数w”“输入行数M”“不同输入列类型数”各自含义。对重复预测标签，解释逐行最小成本preimage；保留原输出要求。

注明主贡献候选的精确内容：按小全局模式总库计费的统一确定性精确上界。模式域或成本字段的增加本身不承担原创性，新增量需要其保持证明和先例差异。

三、已读文献仅核对新增差异

优先复用COL2020及其完整证明、FS21、KKM20/NF25已经完成的参数代入。先检查旧表是否足以判断当前层次，针对成本/域所需的新原文才补读。

对COL2020：
- 原逐坐标关系已经能表达B层的域；准确承认模型表达覆盖。
- 检查原偏移成本是按点还是按点与中心，给出准确接口映射。
- 若用近似取整、随机精确、标签包装或去随机化，复用已有完整费用，仅更新T+新增部分。
- K与w的替换、输入次数及确定性须保持实际来源保证。

对FS21：
- 总预算与逐行预算的区别继续保留；
- 只检查新的标签成本/域能否通过已有结构引理或标准组合消除原缺口；
- 已经关闭的直接总预算替换和O(wr)代表界路线保持原裁决。

对整数规划/字符串结果：
- 给强方法保留现有最小费用包络；
- 固定输入串数、固定中心数、模板宽度等参数逐项对应；
- 普通可表达性、XP和按w的FPT分别管理。

这一部分采用“已有结论＋本轮差异”的短表，避免再次全文复述已完成工作。

四、新增一条跨表述核查：列表型二部模板与单侧局部编辑

建立以下候选等价表述并给双向映射：

把A视为行侧M个对象与列侧v个对象之间的二元关系；Q为K×w模板。
每个列侧对象t选模板列eta_t∈Omega_t；
每个行侧对象i选模板行p_i；
A_it与Q[p_i,eta_t]不一致为一次修改；
行i允许的修改数为1−tau_i(p_i)，成本2标签禁用。
列侧没有逐列修改预算。

重点核对：
- 原A的0和1关系均受模板约束；普通只要求保边的图同态可能无法表达0约束。
- 两侧角色、允许闲置和重复、模板是输入或固定常量、行侧标签列表/代价均明确。
- 普通图源的双侧局部预算、团目标、相等行列标签或固定模板前提不能默认继承。
- 所有恢复、输入膨胀及参数依赖单列。

这是用于查新的数学字典。先证明这份字典自身准确，再用它寻找已有结果。若等价表述需要增强源模型，写出增强处。

以实际核实的公开文献为准，围绕list matrix partition、bipartite template editing、one-sided locally bounded modifications、assignment-restricted Hamming radius clustering等概念进行一次有界筛选。可用当前可用搜索工具，记录检索式和渠道；不要把工具失败登记为未命中。

优先精读最多两项最可能改变T+判断的新工作及其完整证明。论文数量不是目标；找不到足够接近来源时如实记录。正式版受阻时采用有版本绑定的公开稿，来源继续缺失则换另一个可读对象。COL2026继续跳过。

五、尝试完成真正的蕴含链

对最强适用来源，给出：
原定义/定理/证明位置；
模型双向映射；
w/K/M/v与源参数字典；
预算与成本保存；
标签/模式域处理；
确定性；
完整见证恢复；
实际代入后的时间。

专门检查：
- 按模板总大小K+w的FPT，代K≤2^w后是否只给更弱的w参数上界；
- 对固定模板给多项式算法时，输入指数是否仍依模板；
- 取最小成本合并重复标签后，K是否可以依法受2^w限制且保留逐行preimage；
- 某个来源只覆盖B层时，C层是否由已有标准构造在w'=O(w)等允许参数膨胀下推出；
- 坐标填充/标签列表gadget的数量和新增模式必须计费；
- 若桥接实际调用项目PR-C3或TT-1迁移，把该环节按项目来源登记。

若某个具体标准编译失败，给最小合法输入或参数障碍；这个失败只裁决对应路线。不要把新的困难字段当作T3基础模型已经新颖的证据。

六、贡献分层与退出条件

分别登记：
MODEL_EXPRESSION_COVERED
STANDARD_COROLLARY_COVERAGE
SAME_PARAMETER_FPT_WITH_WEAKER_BOUND
RESTRICTED_DOMAIN_COVERAGE
PARTIAL_OVERLAP
SPECIFIC_MAPPING_REFUTED
MAPPING_UNRESOLVED
SOURCE_UNRESOLVED

“按w的FPT已有但指数改善待确认”与“已核读来源尚无按w的FPT推导”分开。来源给较慢上界不等于算法必要代价下界。

最终选择一个当前证据允许的整体判断：
TPLUS_COVERED_BY_PUBLISHED_RESULT
TPLUS_FINE_BOUND_CANDIDATE_PENDING_PRIORITY
TPLUS_PARAMETERIZATION_CANDIDATE_PENDING_PRIORITY
TPLUS_MAPPING_UNRESOLVED

范围必须列明已核读版本/路径，暂停来源风险继续保留。若得到完整公开覆盖，按该证据收缩相应贡献；若新增桥接本身需要实质证明，给出其独立责任和待查优先权。

本轮完成后，选一项真正能改变主贡献资格的后续动作。优先选择具体文献映射、尚未解决的下界/适用价值问题或明确的证明缺口。避免继续重复同一批已读定理的相同代入。

七、交付及约束

新目录：
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_priority_screen\

四份主稿：
NORMALIZED_THEOREM.md
SOURCE_IMPLICATIONS.md
MODEL_REDUCTION_AUDIT.md
DECISION.md

sources保存实际取得原文、版本与阅读定位；历史目录保持原字节。数学证明与先例范围如实区分，当前审查为知情模型辅助，外部复核仍待取得。

机制实现继续遵守用户门槛：具体输入族、固定度量、最强适用通用方法、同等能力、必要代价与候选上界、至少一个严格差距实例和判废条件形成前保持未开始。本轮只做纸面数学与原文核查，不扩大实验或MPC。完成后正常结束本轮，由监督流程审查续接。
