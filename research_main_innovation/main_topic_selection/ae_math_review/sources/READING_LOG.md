# 输入、封存、读取及复核范围

版本AE-MATH-1，2026-11-06。本轮只复核数学正确性与计算成本；没有网络文献获取、数学穷尽、证明助手或新机制实现。

## 1. 实际独立性

协调者参与过原构造、C1/C2、分支计数和恢复证明，全部采用知情口径。新审查子代理以fork_turns=none启动；未申请模型覆盖，沿用父模型配置。它首阶段只收到输入输出合同与T1/T2，没有继承当前会话证明历史。

陈述源为ae_priority_audit/THEOREM_IDENTITY.md。为防止读取该文件后续证明状态/先例章节，协调者复制其第1节合同，并把T1/T2按无机制注释的形式存为STATEMENT_ONLY.md。源字节及摘录SHA256均在INPUT_ISOLATION_PLAN.json。完整源直到首阶段封存后才复制入本目录，记录为协调者知情材料。

隔离依靠新上下文与操作纪律；共享文件系统没有技术访问沙箱。读取清单为审查者自报的文档级清单，缺少系统调用级审计。hash只固定版本，不证明训练知识来源或错误统计独立。本轮不登记为外部人工、不同模型或证明助手验证。

## 2. 第一阶段

新审查者在读陈述前写INITIAL_KNOWLEDGE，读取STATEMENT_ONLY后独立尝试。其提交的INDEPENDENT_ATTEMPT给出了支持T1/T2的自含草稿：使用带固定中心标签的见证行、逐见证格子的翻转集合、模式类细分和小冲突证书。

首阶段两稿与自报读取回执冻结于phase1_sealed，协调者重算hash后形成PHASE1_PARENT_SEAL.json。之后两稿和回执保持原字节，任何补充均写入第二阶段报告或协调者单独记录。

## 3. 第二阶段开放及核读

首阶段父级封存后，才把以下四份AE-BRANCH-1原稿按字节复制到proof_inputs_released并发出明确放行：

- BRANCHING_CONSTRUCTION.md：完整读取，115行。
- CONFLICT_DICHOTOMY_PROOF.md：完整读取，142行。
- CORRECTNESS_AND_PARAMETER_BOUND.md：完整读取，165行。
- GENERIC_FORM_AND_PRIOR_ART.md：完整读取，147行；其嵌入先例表可见，但论文链接及其他来源未打开。

原路径/副本/hash在PHASE2_RELEASE.json；原文件当前hash也由协调者验证。具体节位置索引在PROOF_SECTION_LOCATIONS.json。新审查者核验的是披露副本，没有另读原文件，不能把这一点扩写成访问原始历史全部材料。

本阶段输出PROOF_REVIEW、REVIEW_DECISION，原字节封存于phase2_sealed。它现在已接触现有证明，第二阶段属于知情对照。其第一阶段修正格子状态与原稿E/ψ模式固定状态不同，正确路径责任已逐项比较；相似或不同都没有被当作统计独立性的证明。

## 4. 发现和采用的澄清

新审查者报告D1–D6：空输入的输出成本、局部g≥2前提、t∈X\E量词、一趟行扫描的恢复计费、两种去重对象的区分，以及M_r执行语义桥接的范围外依赖。

非退化域m,n,q,L≥1的主体界保持T1/T2，没有发现该域的实质反例或需要提高参数指数的缺口。空输入字面延伸的反例已写出。协调者知情补充采用保守包装O(N_enc+q(n+1))，N_enc含实际输入/参数编码；它与正域定理分开，详见PARENT_BOUNDARY_ADDENDUM.md。

D6只披露本次隔离审查的读取范围：本轮支持数学距离子问题及W/E恢复，没有另行审查原生迁移、退役和逐前缀保留的所有前提。它不改写历史M_r理论证据等级，也不新授予部署符合性。

## 5. 不随本轮升级的状态

数学状态继续AE_PROVED_PENDING_PRIORITY，新增正确性证据为新输入上下文的重推及逐项对照。优先权仍为PRIORITY_UNRESOLVED；最优性、严格分离、外部数学读者和证明助手各自待审，机制门保持关闭。

研究者本次报告COL2026卷1086、文章116240、开放获取标签及正文403。这份更新单列为COL2026_RESEARCHER_UPDATE.json，证据类型为研究者核读的题录/摘要信息；正文未取得、P26待核状态保持。本轮没有将OA标签等同于取得数学正文。

## 6. 可追溯材料

INPUT_ISOLATION_PLAN、PHASE1_REVIEWER_RECEIPT、PHASE1_PARENT_SEAL、PHASE2_RELEASE、PHASE2_REVIEWER_RECEIPT、PHASE2_PARENT_SEAL共同记录顺序和文件摘要。REVIEW_PROTOCOL记录实际隔离边界，PARENT_KNOWLEDGE及两份协调者笔记单独标明知情来源。

DELIVERY_VALIDATION只核对源字节、两阶段封存、JSON和链接，不认证定理本身；SOURCE_MANIFEST保存当前交付摘要。全部候选代码、验证器、数学测试程序、原生认证调用和真实账户操作为0。
