# 来源、版本与阅读范围

记录日期为 2026-11-07。获取时间的精确 UTC 值保存在 RETRIEVAL_01–06.json 及各新增来源的 .retrieval.json。PDF 的实际字节、SHA-256、页数及已声明的阅读范围汇总于 SOURCE_MANIFEST.json。

## 1. 已取得 PDF

|文件|作者与题名|实际版本与页数|本轮实际核读范围|承担的证据|
|---|---|---|---|---|
|CIV_2508_09288.pdf|Aayush Gupta，Can AI Keep a Secret? Contextual Integrity Verification|arXiv 2508.09288v2，2025-08-18，12 页|PDF 1–4、6–7、9–10 页及关键词定位，7、10 页图像复核|内部 trust mask 与来源认证的公开构想，形式化方向存在下述核查项|
|KIVI_2402_02750.pdf|Zirui Liu、Jiayi Yuan、Hongye Jin、Shaochen Zhong、Zhaozhuo Xu、Vladimir Braverman、Beidi Chen、Xia Hu，KIVI|arXiv 2402.02750v2，2024-07-25，15 页，PDF 标注 ICML 2024|PDF 1、3–5 页，3 页量化公式图像复核|量化公式、跨 token 的键分组、残余缓存|
|LLMbda_2602_20064.pdf|Zac Garby、Andrew D. Gordon、David Sands，The LLMbda Calculus|arXiv 2602.20064v2，2026-07-10，63 页|摘要、PDF 9 页语义、26 页限制和定点检索|代理对话 IFC、概率非干涉与模型抽象边界，完整证明审计待取得|
|SPAN_VETO_2610_15883.pdf|Mark Russinovich，What the Model Cannot See|arXiv 2610.15883v1，2026-10-11，15 页|PDF 1、3–4、8、11 页及相关标题|Proposition 1 的全通道前提、固定几何与缓存策略条件|
|StateUnlearning_2609_04875.pdf|Chao Yao、Yangbo Wei、Zhen Huang、Junhong Qian、Chenle Chen、Shaoqiang Lu、Chen Wu、Lei He，Forgetting Without Restarting|arXiv 2609.04875v1，2026-09-04，8 页|PDF 1、3–4、7 页及定点检索|执行状态遗忘、重放定理和受限黑盒模型下界|
|BatchIFC_2505_18323.pdf|Nicolas Küchler、Ivan Petrov、Conrad Grobler、Ilia Shumailov，Architectural Backdoors for Within-Batch Data Stealing and Model Inference Manipulation|arXiv 2505.18323v2，2026-03-20，13 页|PDF 1、3–8 页，8 页图像复核|动态量化信息流的直接先例，完整来源集合与优化标签传播|
|secure_compilation_full.pdf|Carmine Abate、Roberto Blanco、Deepak Garg、Cătălin Hriţcu、Marco Patrignani、Jérémy Thibault，Journey Beyond Full Abstraction|arXiv 1807.04603v6，2019-05-17，70 页|PDF 1、6–7 页完整定点阅读，其余页只作关键词定位|§3 安全编译的 hyperproperty 保持框架|
|DeepProv.pdf|Firas Ben Hmida、Abderrahmen Amich、Ata Kaboudi、Birhanu Eshete，DeepProv|arXiv 2509.26562v1，2025-09-30，18 页|PDF 1、5、7–8、12 页完整定点阅读，其他相关段落检索|推理来源图与修复动作生成已有先例，具体全称权限合同需另行映射|

BatchIFC 的首页声明获 SaTML 接收，正式 IEEE 排版版尚未独立绑定。DeepProv 的公开记录标注 ACSAC 2025，当前证据固定于上述作者公开稿。安全编译公开记录关联 CSF 2019 与 DOI 10.1109/CSF.2019.00025，本轮使用含附录的公开长版。

原文入口如下。

- [CIV](https://arxiv.org/abs/2508.09288)
- [KIVI](https://arxiv.org/abs/2402.02750)
- [LLMbda](https://arxiv.org/abs/2602.20064)
- [Span Veto](https://arxiv.org/abs/2610.15883)
- [Execution-State Unlearning](https://arxiv.org/abs/2609.04875)
- [Batch IFC](https://arxiv.org/abs/2505.18323)
- [安全编译](https://arxiv.org/abs/1807.04603)
- [DeepProv](https://arxiv.org/abs/2509.26562)

## 2. 摘要及发现级材料

|来源|阅读层级|用途|
|---|---|---|
|Towards a General-Purpose Dynamic Information Flow Policy，arXiv 2109.08096|公开摘要|动态释放、撤销、委托与擦除已有理论线索|
|Combining Tools for Optimization and Analysis of Floating-Point Computations，arXiv 1805.02436|公开搜索结果完整摘要，正文尚待核读|Herbie/Daisy 优化与误差认证组合的直接下一步来源|
|StaticFixer，arXiv 2307.12465|公开摘要|自动信息流修复的已有工作线索|
|SEIO*、SCIO*|公开摘要|较新的安全编译与 IO 框架线索，未展开定理覆盖|

这些材料只承担所列层级的证据。后续精确调用算法或定理时，需要取得并核对相应正文与前提。

## 3. 检索范围与记录

本轮检索围绕候选依次收缩，原始 HTML 或 raw、提取文本和请求记录均保存在本目录。

- 推理内部权限，检索 information flow、attention、language、attention mask、prompt injection、noninterference。
- 状态撤销，检索 KV cache、revocation、unlearning、inference。
- 量化组合，检索 quantization 与 noninterference、prompt injection、information flow。
- 新增编译核查，检索 secure compilation 与 hyperproperties，mixed precision 与 compiler、verified，information flow 与 repair，以及 Daisy 与 numerical。

检索采用公开 arXiv 页面及已发现论文的引用线索。搜索结果按标题和摘要筛选，本文明确的主张回到 PDF 指定页核读。搜索页可能有分页，返回的单页范围记录于保存的 HTML。此轮覆盖范围限实际入口和核读文献。

两项较窄的编译关键字查询返回空结果。更宽查询取得安全编译、DeepProv 和数值工具组合线索。空结果按检索覆盖限制解释。

## 4. 重要的前提核查

### CIV 的公式方向

PDF 第 7 页给出 \(L=QK^T/\sqrt{d_k}\)，随后允许 \(M_{ij}=0\) 当 \(T_i\ge T_j\)。按该矩阵中查询为行、键为列的定义，高信任查询可读取低信任键。

PDF 第 9–10 页 Theorem 1 则在 \(T_p<T_q\) 时要求低信任位置 \(p\) 对高信任位置 \(q\) 的影响为零，并在证明中写 \(\alpha_{qp}=0\)。这与第 7 页公开公式存在方向冲突。两处已回到页面图像核对。

本轮将 CIV 用作内部权限构想的公开先例。采用其定理作为安全基础之前，需要核实掩码实现、索引约定或修订说明。当前没有作实现审计，也没有把全文的所有经验结果升级为已验证保证。

### Span Veto 的全通道前提

Proposition 1 明列全部跨位置通道与确定性、batch-invariance 前提。动态量化、共享缓存和混合器状态均需要在这些前提中核算。本轮反例作用于引入新共享通道的组合。

### Batch IFC 的证书范围

PDF 第 6 页首先给出完整来源集合分析，再说明针对每输出单用户标签的 min/max 标签优化。第 7 页明确其大规模评估证书针对所检验的固定输入维度。任意允许来源集合可采用完整标签传播思路，但其成本和实现接口需另算。

### State Unlearning 的下界范围

所读 Theorem 1 依赖确定性或固定随机性、重放观察与反事实观察一致、外部副作用可恢复等前提。Corollary 1 的重放调用下界位于黑盒 transition oracle 模型。带有白盒依赖与额外可逆状态的系统需要单独比较。

## 5. 文件取证与工具范围

所有八份 PDF 已进行结构 preflight，结果为 STRUCTURE_ONLY 范围的 PASS，页数核对一致，sidecar 中 warnings 为空。该结果用于页码定位可靠性。

初次为新增两份 PDF 调用 preflight 时使用了不适用的命令参数，工具返回 usage error。随后按实际位置参数重新执行，成功结果保存为 secure_compilation_full_structure.json 与 DeepProv_structure.json。HTML 提取遇到 bs4 缺失后使用 Python 标准库 HTMLParser 完成。上述处理属于文档读取。

已查看的渲染图为 KIVI 第 3 页、BatchIFC 第 8 页、CIV 第 7 和第 10 页。抽取页文本、完整文件保存与定点核读各有独立范围。

来源哈希用于固定本次实际文件。读者应结合版本、页码与适用前提使用。所有核读由当前模型完成，外部人工审查仍待取得。
