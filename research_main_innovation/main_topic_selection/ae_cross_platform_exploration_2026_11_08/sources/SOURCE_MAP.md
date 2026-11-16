# 来源与实际核读范围

2026-11-08，Asia/Shanghai。获取时间以 UTC 保存在各 .retrieval.json。原始响应和文件哈希见 SOURCE_MANIFEST.json。

## 1. 新取得的官方记录

### Efficient Proofs of Software Exploitability for Real-world Processors

作者为 Matthew Green、Mathias Hall-Andersen、Eric Hennenfent、Gabriel Kaptchuk、Benjamin Perez、Gijs Van Laer。

取得 IACR 2022/1223 独立官方记录并核读完整摘要。记录标注 Published elsewhere、PoPETs，接收记录日期为 2022-09-15。摘要描述针对 MSP430 二进制生成非交互零知识漏洞可利用性证明，并使用 Microcorruption 练习作展示。

本轮只据此确认零知识证明漏洞存在和隐藏利用见证已有直接先例。具体构造、证明与性能尚未核读。[官方记录](https://eprint.iacr.org/2022/1223)

### Reparo

取得 arXiv 2610.41800v1 官方题录与摘要。作者为 Ayesha Binte Mostofa、Gehao Zhang、Sam Stern、Juan Zhai、Pubali Datta。原记录首次提交日期为 2026-10-30。

摘要涉及从仓库证据合成、修复和验证访问控制政策，使用官方语言验证工具、模型生成的行为 oracle 与抽样人工评估。本轮确认相关自动化已有近邻，完整模型、实验与证明尚未核读。作者报告的统计验证不作为本项目全称正确性的证据。[官方记录](https://arxiv.org/abs/2610.41800)

## 2. 检索级材料

IACR 的零知识与漏洞检索还定位到 ZEE200、ZEE、Sealed-Glass Proofs 等线索，当前为搜索页摘要范围。

私密分布式约束检索取得 14 项结果，按题名筛选，并查看了 A Privacy Preserving Collusion Secure DCOP Algorithm（1905.09013）和 Privacy of Existence of Secrets（1902.05943）的官方搜索摘要。它们为共同授权中的私密约束求解提供直接查新入口，算法与定理未展开。[1905.09013](https://arxiv.org/abs/1905.09013) [1902.05943](https://arxiv.org/abs/1902.05943)

multi-party consent conflict 的查询返回空结果，按该入口的实际结果记录。该结果不承担首次性证明。

## 3. 复用来源

复用 ae_agent_collaboration_ideas_2026_11_08 中的 PREFERENCE_QUERY_NOTE.md，以及已取得的《Delegating Authorization to Misaligned Agents》arXiv 2609.15803v1。源定理和上轮阅读范围见该目录的 PRIOR_ART_AND_STATUS.md 与 SOURCE_MANIFEST.json。

本轮 d 维结果由原有限结果与真诚审核语义、上轮二维例和标准零空间论证组合得到。没有将其描述为源论文已经给出的询问定理，也没有作独占原创性判断。

## 4. 获取失败与恢复

本轮部分 Python urllib 请求返回 TLS EOF。随后使用普通 PowerShell HTTPS 取得了 IACR 独立记录、Reparo 独立记录，以及 joint consent、private constraints 的检索页。相关失败记录保留，成功响应另存。

首次 private bug report 查询与 ZEE 独立记录未取得可读响应，当前对应材料仅保留线索或未取得状态。没有依据缺失正文补写其定理。

## 5. 过程归属

本轮为模型辅助探索和纸面证明。新材料以摘要和官方记录为主，全文先例覆盖继续待核。

代码操作仅用于来源获取、HTML 提取、哈希与文档检查。没有运行候选机制、参考实现、求解器或数学穷尽程序。外部数学核验待取得。
