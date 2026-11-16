# 答辩问答预案

本稿用于导师审阅和答辩准备，回答沿用B版条件性口径。事实依据在各问答末尾给出，外部论文的具体能力以阅读范围为准。[论文定位](D:/毕业设计/research_recipe_r3/VERDICT.md) [本轮范围](D:/毕业设计/thesis_draft/TASK_SCOPE.md)

## 1 为什么没有H-A/H-B/H-AB正式对比实验

这三项实验原拟支持查询成本、配置成本和反馈收益的总体优势。当前论文已经移除相应优势主张，历史状态保持NOT_TESTED。现在的主张由认证领域规格、条件性资源定理和版本限定原生测量各自支撑。有限枚举与576次校准按原用途保留，未被填写为正式假设通过。若未来重新主张总体成本优势，需要恢复对应的实验与统计前提。[范围决定](D:/毕业设计/thesis_draft/TASK_SCOPE.md) [历史结果](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

## 2 是否因为结果不理想而修改了指标或挑选数据

当前改变的是论文承担的主张范围。原成本函数、失败惩罚、原始分母和负结果均保留。A的等效或更差例、B简单组合等效、AB投影敏感、R-J更低请求以及四条分离声明淘汰，均进入研究历史。论文通过缩小结论适应证据，任何未完成假设仍按原状态使用。[负结果审查](D:/毕业设计/research_secret_recipe/REPORT.md) [旧报告计量口径](D:/毕业设计/thesis_draft/sources/technical_report.txt)

## 3 本文最集中的数学贡献是什么

在M_r的一次首次请求、单任务原子重绑、完全目标资格和既有独立根计费条件下，给出固定配置最少迁移距离，并证明零预算静态退化及固定k≥2、r≥1时完整节省谱0至k−2。候选增量集中于该精确资源刻画和匹配构造，数学工具及通用搜索原理按先例引用。[定理全文](D:/毕业设计/thesis_draft/chapters/04_RESOURCE_THEORY.md) [先例记录](D:/毕业设计/research_recipe_r3/PRIORITY_AUDIT_R3.md)

## 4 通用枚举也能找到相同根数，定理还有什么意义

精确求解器在相同模型和目标下应得到相同最优值。定理直接说明整个参数域允许哪些资源值，为什么更少根不可行，以及哪些前提改变会使构造失效。其价值在结构刻画和可检查最优性边界，当前论文不以此主张独立求解效率优势。[动态与通用方法比较](D:/毕业设计/research_secret_recipe/REPORT.md) [R2理论定位](D:/毕业设计/research_recipe_r2/THEOREMS.md)

## 5 r增加为何全局最大节省仍是k−2

单根无法同时停止和保留任务，给出统一两根下界。稀疏族在一次重绑时已达到两根，因此对固定k跨全部需求族取最大节省，r≥1时界值均为k−2。固定某一实例的g_r仍可随预算改善，四任务全需求族给出4、3、2序列。两种量词分别在定理中写明。[R2 §5](D:/毕业设计/research_recipe_r2/THEOREMS.md) [量词表](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

## 6 谱是否只是一组有限样例

每个固定k、r和目标节省s都有一般构造，重类大小M=pr+1迫使任意低根配置出现超预算占据，再用一个请求导出终态冲突。有限验证仅核对具体输入与实现，数学全称性由该参数化证明承担。[完整证明](D:/毕业设计/research_recipe_r2/THEOREMS.md) [扩容范围](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

## 7 原子重绑在Keycloak或Casdoor中真的存在吗

当前已核实接口中有发行、刷新、内省、撤销和账户级管理操作，原子重绑子域尚未取得符合性证据。论文因此明确使用B版条件模型，并把目标根资格、旧支持同步退役、逐前缀可用和在途闭包列为前提。R3已有最小验证协议，执行等待研究者另行授权。[公理—操作审计](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md)

## 8 ACG已经证明minimal repair，是否覆盖本论文下界

ACG确有最小基数结果。其Proposition 1固定当前动作、图与缺失集合，证明所有同依赖覆盖集合都包含修复前沿。本文优化的是请求到来前建立的独立撤销根，并要求共同初态覆盖所有首次停止请求，再允许各请求使用预算内重绑。两者的变量、量词和代价对象均已逐项对照，所核命题未直接给出完整根节省谱。[ACG原文](D:/毕业设计/thesis_draft/sources/acg.txt) [矩阵](D:/毕业设计/thesis_draft/OVERLAP_CHECK_FINAL.md)

## 9 ResidualAuth是否已经解决未来撤销语义

该文已严格刻画未来授权语言，并给出同闭包不同未来、监测存储与信息下界。本文承认这些理论。其Clean(G)属于图更新规范化，实验probe用于未来更新和查询诊断。本文的核验动作另有批准、费用、丢响应和会话义务，目标要求在所有可见结果分支上有界清空严格义务。所核版本未覆盖这套具体规划规约，W_h通用递推仍归已有方法。[ResidualAuth原文](D:/毕业设计/thesis_draft/sources/residualauth.txt) [比较](D:/毕业设计/thesis_draft/OVERLAP_CHECK_FINAL.md)

## 10 “近邻未决”是否意味着已经确认原创

当前完成了两项定点核查，并能明确指出被比较命题的差异。R3较广近邻和全文缺口仍保留，因此整体首次性继续未决。论文采用条件性资源理论贡献的表述，工具先例和直接机制先例均引用。学位贡献是否充分，还需导师和学位评审结合完整论文判断。[优先权边界](D:/毕业设计/research_recipe_r3/PRIORITY_AUDIT_R3.md) [本轮收口](D:/毕业设计/thesis_draft/OVERLAP_CHECK_FINAL.md)

## 11 为什么W_h可以处理stay问题

无秩规则只保证每一步仍有完成策略，可能反复选择stay。W_h菜单要求每个后继进入W_{h−1}，于是剩余步减少。r=1的最后一步只能选择能够终止的动作。该结论依赖策略继续执行和模型覆盖，决策步无法强迫网络在某墙钟期限内返回。[语义与实际本地派发](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [回归定位](D:/毕业设计/auth-lifecycle/docs/VALIDATION.md)

## 12 多世界证书为何需要超过两个世界

计划集合{a,b}、{b,c}、{a,c}两两有交而总交为空，两世界反例搜索会遗漏整体冲突。证书支持任意有限初始世界核心，重新检查批准、预算、动作和全部必要观察分支。高阶冲突及不可满足证据已有通用基础，本文使用它们确保实现的量词完整。[证书规格](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md) [R09归属](D:/毕业设计/thesis_draft/sources/survey_report.txt)

## 13 AB3 scope反例到底说明什么

冻结v1.2检查器把带probe的joint策略接受为control-only证书，而该输入的control-only参考为界内不可行。它暴露的是检查器对不可信证书的动作范围约束遗漏。内部生成器只产生控制动作，与公共检查器接收任意证书的安全合同分别评价。本轮已经登记反例与修复路径，源码摘要仍对应该被审快照，修复结果尚未验收。[反例与源码逻辑](D:/毕业设计/research_secret_recipe/REPORT.md) [复现数据](D:/毕业设计/research_secret_recipe/SCOPE_AUDIT.json) [当前摘要](D:/毕业设计/thesis_draft/SOURCE_MANIFEST.json)

## 14 这个scope缺口是否推翻资源谱

资源谱基于M_r公理、固定距离和重数引理的手工证明，并由独立任务移动搜索进行有限核对。AB3 scope问题位于另一条证书执行路径，直接限制其control-only健全性。论文分别列明这两条证据链，同时保留公共检查器需要修复的事实。[资源证明](D:/毕业设计/research_recipe_r2/THEOREMS.md) [数学验证](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md) [scope审计](D:/毕业设计/research_secret_recipe/SCOPE_AUDIT.json)

## 15 两个程序一致是否已经证明安全

一致运行支持声明输入域内的行为相符。候选与R-I分开解释状态，R-I和检查器仍共享内核，实际服务也可能存在共同模型遗漏。H-S因此还要求真实覆盖、批准预算可信、所有后效和义务被表示、终态反映及动作回译成立。[独立性](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md) [抽象保持](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md)

## 16 52次调查和576次校准能得出多大范围的结论

52次是两平台×13条件×两重复，支持指定版本和profile的行为矩阵。576次来自已知契约校准，六方法各96次，查询与反馈均未激活，独立性获确认家族为0。它们保留反例、负控制和工具链证据，总体效应或竞争概率仍受样本范围限制。[调查](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [校准](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

## 17 Casdoor新AT存活能否说明共享根撤销失败

这条归档轨迹执行refresh(old_RT)与revoke(old_RT)，观测到新AT在授权方内省中活跃。共享账户根处置另有独立实验，组合并发条件尚待测。该轨迹的直接反例对象为旧RT撤销后的派生材料内省失活承诺，业务资源R、L和E分别按已取得证据判定。[调用范围与结论](D:/毕业设计/research_recipe_r2/REPORT.md) [原日志](D:/毕业设计/auth-lifecycle/results/experiments/survey04/survey-casdoor-concurrent_race-1.jsonl)

## 18 为什么要强调G与token字符串数量的区别

资源理论按独立效果单位计费。多份材料可能共享处置根，一份刷新操作也可能产生新的记录而需要重新核对根关系。当前fresh-grant profile用原生记录匹配和撤目标保兄弟的效果观察支持G，跨SSO与派生谱系的普遍映射仍待证据。[G核对](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [M_r计费](D:/毕业设计/research_recipe_r2/THEOREMS.md)

## 19 论文怎样处理原有密码学成果

密码学支线按独立归档保留，条件性代数定理、有限证书、来源和完整成本限制分别呈现。结构分块等效以及gate直接输出支持等负结果继续有效。当前学位主线的三项贡献围绕认证规格、根资源谱和原生测量，密码学工作只作辅助背景与边界说明。[底座密码学审计](D:/毕业设计/thesis_draft/sources/survey_report.txt) [当前范围](D:/毕业设计/thesis_draft/TASK_SCOPE.md)

## 20 v2.15原件缺失如何影响引用

旧摘要清单登记的研究空白与创新融合DOCX目前缺失。本文静态定理依据R2冻结重述及可定位验证资料，明确材料继承关系。恢复原件后应先比对原SHA256，再核对§25.2和首次请求边界。当前稿保留该缺口，不补造历史附件。[缺失记录](D:/毕业设计/research_recipe_r3/HISTORICAL_HASH_CHECK.json) [待完成项](D:/毕业设计/thesis_draft/POSTPONED_UPGRADES.md)
