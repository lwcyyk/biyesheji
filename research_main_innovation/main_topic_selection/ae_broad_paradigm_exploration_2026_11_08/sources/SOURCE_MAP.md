# 来源、实际范围与证据等级

用户侧记录日期为 2026-11-08，Asia/Shanghai。网络获取时间以各 .retrieval.json 内的 UTC 时间保存，文件哈希汇总于 SOURCE_MANIFEST.json。

## 1. 本轮阅读层级

本轮属于广度探索。取得并核读 13 份论文的官方摘要和题录页面，以及 4 项官方规范或产品文档的相关段落。论文全文和全部定理、实验尚未展开。摘要中的性能与用户研究结果按作者报告登记，主稿没有将其作为本项目复现结果。

检索结果还提供多人隐私、纵向交互、可移植代理和资源攻击的其他来源线索。原始搜索页面与提取结果已保存，未显示或未核读的条目不计入阅读范围。

## 2. 论文来源

|标识|题名与主要作者|本轮用途与范围|
|---|---|---|
|S01，2606.09908|IDP-Bench，Ayana Hussain 等|官方摘要和题录，确认 LLM 多人相互依赖隐私已有研究|
|S02，2609.28537|Privacy Leakage Through AI-mediated Analysis of Smartphone Data，Sarah Radway 等|官方摘要和题录，确认从获准数据推断额外敏感信息的直接研究|
|S03，2606.02668|What You Approve Is What Executes，Xiaoqi Weng|官方摘要和题录，批准呈现与执行绑定的近邻，作者说明了原型假设与限制|
|S04，2609.33910|When Consent Outlives Context，Zhihao Zhang 等|官方摘要和题录，持久批准与原上下文分离的近邻|
|S05，2603.04815|EchoGuard，Ratna Kandala 等|官方摘要和题录，纵向操控识别的框架与验证设想，按议程层级使用|
|S06，2606.05449|Insurance of Agentic AI，Quanyan Zhu|官方摘要和题录，代理风险、承保和责任组合框架|
|S07，2607.11999|Underwriting the Agent Economy，Cristian Trout 等|官方摘要和题录，AI 保险基础设施议程，预测性数字没有作为已发生事实使用|
|S08，2510.20007|zk-Agreements，To-Wen Liu、Matthew Green|官方摘要和题录，私密合同、2PC 与链上执行组合。页面的条件式会议说明没有被视为已接收证明|
|S09，2303.00533|Towards a Privacy-Preserving Dispute Resolution Protocol on Ethereum，Andrea Gangemi、Aida Manzano Kharman|官方摘要和题录，私密争议解决的直接近邻|
|S10，2609.00546|Runtime-Independent Persistent Agents，Zhenyu Zhao、Roy Zhao|官方摘要和题录，运行时、模型与宿主切换的机械连续性，原摘要限定了行为等价与外部效果保证|
|S11，2609.05339|Does Your Agent's Memory Survive a Model Upgrade，Ankit Goyal、Jaideep Ray|官方摘要和题录，受控记忆迁移研究及来源材料保留问题|
|S12，2606.14517|From Shield to Target，Yuguang Zhou 等|官方摘要和题录，安全审查模型的资源耗尽问题|
|S13，2601.10955|Beyond Max Tokens，Kaiyu Zhou 等|官方摘要和题录，多轮工具链造成的资源放大问题|

独立官方页面均保存为 abs_编号.html，并提取为同名 txt。元数据位于 PAPER_RECORDS.json，原始 citation_date 与页面版本记录保持其含义。它们不自动等同于正式发表日期。

来源入口如下。

- [S01](https://arxiv.org/abs/2606.09908) [S02](https://arxiv.org/abs/2609.28537)
- [S03](https://arxiv.org/abs/2606.02668) [S04](https://arxiv.org/abs/2609.33910) [S05](https://arxiv.org/abs/2603.04815)
- [S06](https://arxiv.org/abs/2606.05449) [S07](https://arxiv.org/abs/2607.11999)
- [S08](https://arxiv.org/abs/2510.20007) [S09](https://arxiv.org/abs/2303.00533)
- [S10](https://arxiv.org/abs/2609.00546) [S11](https://arxiv.org/abs/2609.05339)
- [S12](https://arxiv.org/abs/2606.14517) [S13](https://arxiv.org/abs/2601.10955)

## 3. 官方规范与产品文档

|来源|实际范围|证据范围|
|---|---|---|
|W3C ODRL Information Model 2.2|相关概念、§2.7 Policy Rule Composition、§2.10 Policy Conflict Strategy、Privacy Considerations|政策、职责、组合与冲突已有表达基础，具体联合推断强制执行需另证|
|Solid Protocol|摘要、文档状态、互操作与访问控制相关段落|外部存储的许可访问与互操作基础。页面明确为 Solid Community Group 报告|
|ERC-4337|验证流程相关段落、Validation Rules Rationale、Reputation Rationale、安全考虑|验证 DoS、验证规则、质押与节流等强基线。当前文档明确质押在该处用于 Sybil 成本，其机制没有 slashing|
|UMA Optimistic Oracle v3|官方索引与示例入口说明|保险合约、数据断言和争议处理存在产品文档入口，完整安全协议与费用未核读|

对应入口为 [ODRL](https://www.w3.org/TR/odrl-model/)、[Solid](https://solidproject.org/TR/protocol)、[ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)、[UMA](https://docs.uma.xyz/developers/optimistic-oracle-v3)。

## 4. 其他发现级材料

Interdependent Privacy 查询还定位到 IDPFilter、Modeling interdependent privacy threats，以及 2017 年云应用多人隐私研究。当前核读为搜索页官方摘要。它们对“首次发现共享数据影响他人”的宽泛主张构成直接先例线索。

CONCORD 的官方搜索摘要讨论助手之间的隐私感知上下文交换，本轮作为多方协作线索。其他未展开条目保持发现级状态。

## 5. 检索方法与限制

公开检索围绕 inference consent、agent consent、agent liability、privacy dispute blockchain、agent portability、LLM denial of service、interdependent privacy、AI manipulation autonomy。每项检索仅覆盖实际返回的页面，部分查询有后续分页。

题名筛选用于快速定位六个研究对象，选定的 13 项进一步取得独立 arXiv 官方记录。论文摘要提供概念和范围信息，同级保证需要回到全文。

本轮没有进行全数据库穷尽检索，全球首次保持待核。用户原目录与既有综述的版本身份保留。

## 6. 本地材料复用

复用 ae_scenario_reanchoring 的场景和平台边界裁决，补读 ae_two_year_research_outlook 的研究展望与计划相关部分。它们帮助区分已知基础能力、真实接口前提和新假说。

现有 T3、私密授权、分离门等结论按原范围管理。旧稿中的单路线优先级属于旧阶段记录，本轮采用新的并列探索安排。

## 7. 过程归属

候选生成、摘要核查、来源比较和手工例均由当前模型辅助完成。外部研究者意见待取得。哈希和文档检查固定来源版本，未承担学术原创性或数学正确性认证。

本轮代码操作限于文档下载、HTML 提取、来源记录、哈希和交付检查。机制实现状态为未开始。
