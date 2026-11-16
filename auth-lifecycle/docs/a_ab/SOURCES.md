# 一手依据与归属边界

## 当前研究规约

已复查本地《硕士研究_v2.15_创新性验证与假设驱动研究报告.docx》的 H-A（§5.2）、H-AB（§5.4）、义务机制消融（§5.5）以及 §6.1/6.3。原提取文本在 `docs/audit/v215_report_extracted.txt`。没有修改原 DOCX 或假设登记表，也没有将建议阈值改为已通过结果。

H-A 要求同固定 B、同批准和目标；H-AB 要求只关闭具体配置分歧反馈，且设置同目标联合规划参考。开发验证沿用这些设计约束，尚不使用其中的正式阈值作统计判定。

## B-A 测试选择原理

Robert D. Nowak, **The Geometry of Generalized Binary Search**, 2011, IEEE Transactions on Information Theory 57(12), 7893–7906。

- DOI：[10.1109/TIT.2011.2169298](https://doi.org/10.1109/TIT.2011.2169298)
- [作者原文入口](https://nowak.ece.wisc.edu/GBS_arxiv_v3.pdf)
- [arXiv 原文记录，2009 初稿](https://arxiv.org/abs/0910.4397)

本轮核对范围为出版社元数据/摘要及作者正文检索到的算法引入；不是全文定理逐式复核。该工作描述按查询平衡剩余假设的成熟 GBS 规则。本实现将它用于任务性质版本空间，并加入费用、多结果、已登记不确定转换和共用 W 约束；这些适配不继承原文特定几何条件下的复杂度或噪声定理。

v2.15 已登记的性质导向 black-box checking 与部分可观测 shielding 工作仍构成研究背景；本轮没有新增其完整复现，也不把本地实现误写为其官方工件。
