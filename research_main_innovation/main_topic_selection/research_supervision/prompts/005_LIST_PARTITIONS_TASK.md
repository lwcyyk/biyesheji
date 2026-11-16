[AUTO-RESEARCH-LP-005]
请执行“List Partitions (2003) 到 List-B/T+ 的定理级覆盖裁决”。

用户已授权监督对话审查并自动续接。监督核读EL-1，支持ETH_ORDER_TIGHTNESS_WITH_POSITIVE_RADIUS的纸面证据定位：归约、真正半径1及参数计费闭合；源ETH和项目归约责任保持分别登记。这个结果不自动解决优先权或严格代价分离。

本轮只关闭一项明确先例路径，避免再次泛化研究范围或重做T+数学证明。

一、读取与版本处理

读取：
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_priority_screen\NORMALIZED_THEOREM.md
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_priority_screen\MODEL_REDUCTION_AUDIT.md
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_priority_screen\sources\READING_LOG.md
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_eth_lower_bound\DECISION.md

主要原文已有本地文件：
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_priority_screen\sources\FP_ListPartitions_author.ps

题录线索：
Feder、Hell、Klein、Motwani，
List Partitions，
SIAM Journal on Discrete Mathematics 16(3):449–478，2003。
作者原入口：https://theory.stanford.edu/~tomas/partitions.ps

先核实题名、作者全名、发表年份、DOI与版本身份。优先从已取得PS生成可读副本，保留PS原字节、哈希、转换命令和页码对应。文档格式转换属于取证，不构造候选求解器。
使用可用文档工具处理，记录结构检查及关键页目视范围。公开稿与正式版本的关系按实际证据限定；可读公开正文足以形成该版本的局部判断，不因另一个排版版本缺失无限等待。

正文已有关键前作/修订的依赖时，仅追加最必要的一项相关工作；例如已取得的Two Algorithms for General List Matrix Partitions原始PS。新增阅读须说明它会改变哪条蕴含。COL2026继续暂停。

二、冻结准确的目标

T+按全局模式数w给出确定性精确
2^{O(w log(w+2))}poly(N)。

本轮通过TP-1已证标准gadget重点检查List-B：
- 二元模板Q，K个行角色、w个列模式；
- 每个输入行有允许标签列表Lambda_i；
- 每列有模式域Omega_t；
- 每行使用一个全串固定标签；
- 每行Hamming距离至多1；
- 允许空角色、重复预测角色；
- 模板与列表均为输入；
- 输入次数统一，全部原有序中心和见证可恢复。

T+→List-B只增加一个模式、复制标签；行列表的存在是正式前提。列表外禁用可反向编码成成本2。因此完整适用的List-B参数结果可转到T+。

三、提取原文真正提供的算法

按原文逐一定义：
矩阵条目的0/1/*语义；
列表及角色使用条件；
模板为固定常量还是输入；
允许的输入图类；
源参数与统一/非统一常数；
编辑、忽略关系或不满足约束是否存在；
全局预算、局部预算或其他稀疏条件；
决策、构造及恢复。

优先阅读可能支持目标的算法定理及证明。准确记录其标准步骤、分支数量、输入指数、模板依赖和调用的前置结果。使用对来源最有利的适用保证。

源论文若提供“固定模板多项式”，还需检查指数是否随模板增长：
f(D)N^c才给D-FPT；
N^{g(D)}是相应XP；
代D=K0+w、K0≤2^w后分别写出真实函数。
固定常数不可静默变成可变参数。

四、完成两层实际覆盖检查

层一：无编辑基底
令所有行距离必须为0，给出到原文模型的双向映射。左右类型列表、A中的0和1、原角色/模式ID及闲置角色都保持。
这层可以采用标准零误差处理，但其覆盖范围须明确。

层二：真实逐行一次错误
恢复每行半径1，检查原文算法或其已证明引理能否处理未知错误位置，并在小模式侧w上保持时间界。

至少实际核对：
1. 源稀疏—稠密、列表或约束消除步骤是否能吸收单侧错误预算；若“稀疏”只描述源图类或块内结构，说明其与未知编辑的准确关系。
2. 固定错误掩码的List-B已能表达，未知掩码的生成/定位由哪条原定理承担。
3. 新增gadget是否保持每个原行最多一次错误，而未引入列侧预算或把局部预算相加。
4. 模板大小与w、K0的依赖；输入左行数M不得偷偷进入参数指数。
5. 行标签列表、完整0关系或一行固定角色如果被弱化，给小型合法反例。
6. 若要调用PR-C3或T+选择掩码/模式边界，将其登记为项目算法依赖，不算公开覆盖。

若源定理只解决精确识别，本轮可给出这一确定的直接适用边界；进一步包装只评估明确写出的路线，避免声称所有可能归约均不存在。

五、用已有上下界做交叉核验

EL-1已经在tau=0、满域、K=O(w²)、YES最优半径1的子域给出ETH条件下界。
如果某次源代入得到2^{o(w log w)}poly(N)，优先检查归约方向、固定模板常数、局部预算和图类承诺，而非立即宣告文献或T+错误。

反过来，共同ETH下界本身不会否定来源给2^{O(w log w)}poly(N)覆盖。没有严格速度分离时如实保留实现门。

当前论文主命题可以定位为“条件匹配上下界的参数定理候选”；本轮只增加具体先例判断，全球优先权和已暂停来源风险继续单列。

六、裁决和最小充分证据

局部来源裁决：
LP_STANDARD_COROLLARY_COVERS_TPLUS
LP_SAME_PARAMETER_FPT_WEAKER_BOUND
LP_EXACT_BASE_ONLY
LP_PROMISED_DOMAIN_ONLY
LP_MAPPING_UNRESOLVED
LP_SOURCE_UNRESOLVED

每一项附原文位置、参数代入、已完成证明与缺失引理。给完整T+覆盖前，应真正形成端到端算法和费用；较慢已知上界不承担必要代价。

本轮结束时同时回答：
- 该指定来源威胁是否已在列明路径上关闭；
- 剩余原创候选究竟是首次w-FPT、精细依赖改善，还是仅项目独立重推；
- 还有哪项具体未核读定理可能改变这一判断，以及其威胁依据；
- 下一项动作应如何推进主贡献资格，而不是重复已经完成的同式代入。

若没有新具体定理线索，允许建议转入“主定理与证明整合、适用价值及反方审查”，带完整优先权限制；无需为了延长查新再生成没有数学指向的论文名单。机制实现仍独立受原门槛约束。

七、交付与固定边界

新目录：
D:\毕业设计\research_main_innovation\main_topic_selection\ae_tplus_list_partitions_check\

主要四份：
SOURCE_AND_THEOREMS.md
LIST_B_IMPLICATION.md
COVERAGE_OR_OBSTRUCTION.md
DECISION.md

sources存原文副本、转换/读取定位、版本、哈希及实际例子。历史文件保持原字节。
所有新机制代码、求解器、数学穷尽程序、正式实验和真实服务操作保持未开始。候选进入实现前仍需具体输入族、固定度量、最强适用G、同等能力、必要代价、候选上界、严格差距实例和判废条件。

过程如实登记为当前对话内知情模型辅助核读和纸面推导。正常完成本轮后提交裁决和四份入口，由监督流程审查续接。
