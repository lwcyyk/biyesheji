# 来源与阅读记录

2026-11-07。本轮通过官方提案页面、arXiv、IACR 记录及既有本地原文开展候选导向查新。精确获取时间、URL 和原始哈希见各 .retrieval.json，汇总见 SOURCE_MANIFEST.json。

## 1. 官方协议页面

|记录|实际读取范围|支持的判断|
|---|---|---|
|ERC-8004 官方页面，当日快照，页面标为 Draft|Abstract、Motivation、Identity Registry 相关段落、Security Considerations|身份、声誉、独立验证登记已有提案，支付与具体信任机制按页面范围处理|
|ERC-7710 官方页面，当日快照|Abstract、Motivation、Specification、Rationale、Security Considerations|委托兑换接口、权限检查、批处理原子性要求及撤销等已有机制|
|ERC-7715 官方页面，当日快照|权限请求、响应、撤销、查询、兑换与安全章节|有界自动执行与权限请求、撤销 API 已有提案，具体强制执行由钱包与管理器实现|

来源为 [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004)、[ERC-7710](https://ercs.ethereum.org/ERCS/erc-7710)、[ERC-7715](https://ercs.ethereum.org/ERCS/erc-7715)。页面中的接口或示例代码按原文阅读，本轮没有运行或改造。

## 2. 已取得的论文正文

|本地文件|身份与实际版本|页数|本轮核读范围|
|---|---|---|---|
|vera.pdf|Lifei Liu、Haoran Yu、Xiaochong Jiang，VERA，arXiv 2608.30091v1，2026-08-30|8|PDF 1、3–4、7 页，其他页作标题和定位检索，3 页公式图像复核|
|crset.pdf|Felix Hoops、Jonas Gebele、Florian Matthes，CRSet，arXiv 2501.17089v3，2025-09-17|17|PDF 1、5、10–12、15 页，其他页作章节定位|
|pop_authority.pdf|Genliang Zhu、Chu Wang，Authorization for Self-Modifying AI Agent Populations，arXiv 2610.00347v1，2026-09-29|41|PDF 1 页摘要及引言，全文标题、定理与附录位置索引，完整定理审计待开展|
|ebft.pdf|Jun He、Deying Yu，The Honest Quorum Problem，arXiv 2607.16109v1，2026-07-17|26|PDF 1、9–10、18–19 页完整定点阅读，11–12、14 页相关阈值与运行阶段段落，其他页作标题索引|

四份均按实际公开版本绑定。正文取得与独立证明认证分别登记。作者报告的实验数值和全称保证按其实际假设使用。

### VERA 的直接责任

Definition 2–4、Lemma 1 位于 PDF 第 3 页，给出路径有效性、OR 授权及精确边撤销目标。第 4 页包含 observed-prefix exactness。第 7 页说明 survivor witness、邻接完整性与 roster 完整性，Limitations 进一步区分 OR 政策、传播时延和隐私范围。本轮用其确认多父节点撤销语义已有先例。[原始记录](https://arxiv.org/abs/2608.30091)

### CRSet 的直接责任

§3.2 与 §5 讨论发行者活动和凭证出示活动隐私，并定义 chosen count indistinguishability。所读机制通过填充与发布方式处理相应泄漏。其 Theorem 1 和 proof sketch 按作者原模型登记。本轮未完成密码学独立审计，也未将其发行者计数隐私直接等同于整个委托图隐私。[原始记录](https://arxiv.org/abs/2501.17089)

### 分叉权限的直接责任

已核读摘要明确涵盖替换、分叉、回滚、祖先撤销和生命周期消耗守恒，采用单父 generation forest。定理编号在 PDF 第 15 页，完整证明从附录第 34 页起。本轮据此关闭“首次提出分叉后的权限守恒”这一概念主张，细粒度模型覆盖仍需对应证明。[原始记录](https://arxiv.org/abs/2610.00347)

### EBFT 的直接责任

Theorem 5.2–5.4 讨论纯签名投票信息、共因错误及外部语义依据的限制，Theorem 6.1–6.4 给出声明概率事件和静态对手下的阈值条件。§10.2–10.6 明确指出分布漂移、未知共因、标签误差与自适应选择的限制。本轮将相关宏观构想归入已公开先例。[原始记录](https://arxiv.org/abs/2607.16109)

## 3. IACR 的关键来源与版本警示

### Practical Delegatable Attribute-Based Anonymous Credentials with Chainable Revocation

作者为 Min Xie、Peichen Ju、Yanqi Zhao、Man Ho Au、Zoe Lin Jiang、Junbin Fang、Yong Yu、Xuan Wang。已取得 IACR 2024/610 官方页面完整摘要、题录、版本声明及 DOI 关联。

页面明确说明该早期版本含错误，正式与完整版本已发表在 IEEE TIFS，附录在支持材料中。DOI 为 10.1109/TIFS.2025.3587182。页面最近修订日期为 2025-08-04，并将所列旧版本标为 withdraw。

PDF 入口返回 403。DOI 正常入口返回 HTTP 202 空响应，保存的响应文件为 0 字节。当前没有取得可核读的正式正文及附录。主稿只据官方记录登记匿名委托、细粒度属性和链式撤销的先例，参数定理待正式版核读。[官方版本说明](https://eprint.iacr.org/2024/610) [正式 DOI](https://doi.org/10.1109/TIFS.2025.3587182)

### Delegatable Anonymous Credentials from Legacy Credentials using Recursive zk-SNARKs

作者为 Leandro Rometsch、Philipp-Florens Lehwalder、Sebastian Faust、Stefan Schulte。已取得 IACR 2026/1855 完整摘要与题录。页面记录 received 2026-09-01、approved 2026-09-03，状态为 Preprint。

摘要声称可在 legacy JWT/ECDSA 基础上提供匿名委托、选择性属性披露与深度无关的凭证大小，并报告递归证明原型。PDF 入口返回 403，定理假设、撤销支持和完整费用尚未核读。[官方记录](https://eprint.iacr.org/2026/1855)

IACR 检索还定位到 2008/428 的 Delegatable Anonymous Credentials 及多个后续方案，当前用于历史先例发现。它们表明隐藏委托链和匿名委托具有长期文献基础。

## 4. 复用的本地原文

复用 ae_paradigm_exploration 中的 Cordon_2606_17573.pdf 与 Atomix_2602_14849.pdf，以及既有来源记录。本轮补读 Cordon PDF 2、4–6 页的效果、授权义务与补偿段落，Atomix PDF 1–3 页的补偿、适配器及进度边界段落。

这些材料为“撤销后受限清理授权”候选提供强事务基线。其原目录与字节保留，哈希在本轮清单中登记。[Cordon](https://arxiv.org/abs/2606.17573) [Atomix](https://arxiv.org/abs/2602.14849)

## 5. 检索范围与失败记录

本轮查询涵盖 agent、delegation、blockchain、revocation、zero-knowledge、accountability、correlated consensus、fail-prone quorum、cleanup capability 等组合。每次成功响应保存原始 HTML 与请求记录，选定结果另有提取文本或 JSON。分页查询按实际取得页面的范围处理。

原文筛选以具体模型和参数接近程度为依据。较宽查询发现了与初始构想直接相近的论文，候选随之收缩。检索空结果用于记录对应入口的返回情况。

网络搜索连接器本轮返回 transport error，随后使用普通公开入口继续。DBLP 请求返回反自动化挑战页，HTTP 200 仅表示收到页面，已按内容获取失败登记。IACR 记录页正常可读，两个 PDF 返回 403。DOI 空响应没有提供可核读的正式正文。

## 6. 取证与独立性

四份新增 PDF 均完成结构 preflight，页数一致，warnings 为空。该检查限文件结构与页码取证。VERA 第 3 页已经页面图像复核。

全部候选生成、公式核查与纸面证明均由当前模型辅助完成。外部数学和密码学读者意见待取得。来源下载、提取、哈希与文档检查属于取证工作，机制实现状态为未开始。
