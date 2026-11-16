# EL-1原文及定位记录

日期2026-11-07，Asia/Shanghai。模型辅助原文阅读与纸面证明，知情口径。原始路线/监督建议已提供；当前阶段不计输入隔离或外部数学复核。

## 主来源

CFGKMPSo2017_author_JACM.pdf：22页作者公开JACM排版副本，内部首页/页脚/DOI/印刷页码完整。结构预检PASS，作用域STRUCTURE_ONLY。正文符号读取采用pypdf，关键公式回到整页图核对。

实际阅读：

- 物理p1/印刷18:1：题名、七作者、DOI、ACM引文、页数、初步会议版本声明。
- p4：普通Subgraph Isomorphism的保边单射定义；其他应用只作背景定位。
- pp6–8：Theorems1.1/1.2/1.3、简单无向图定义、ETH问题框、Proposition2.1/Lemma2.2。
- pp9–12：Lemmas3.1/3.2全部相关着色/分桶构造及证明；Lemma3.3开头。
- pp12–14：Lemma3.3列表同态归约、大小界及双向证明。
- pp14–17：Lemma3.4锚gadget、Claims3.5–3.8、规模和投影恢复证明。
- pp17–18：Theorem4.1的参数代入和指数预算；4.2/4.3局部单射对应段落亦已读，但本轮下界只使用普通子图。
- p19：Theorem4.4及完整原像大小OR归约、Theorem4.5。
- pp20–22：仅参考文献/后续问题及收稿信息定位，没有其他应用的完整证明复核。

Theorem1.3、4.4/4.5、ETH问题框、Lemma3.3/3.4、Theorem4.1代入的整页图已目视检查。RENDER_LOG.json列出p1、7、8、12、14、18、19。

## 版本对照

CFGKMPSo2016_arxiv_v1.pdf：arXiv1602.05016v1、2016-02-16、23页，预检PASS。实际只读p1、p6、pp18–19及相关编号定位。Theorems3/6/7与正式1.3/4.4/4.5对照；总图阶与每图阶的差别均记录。没有声称完整23页均已数学核读。

arxiv1602.05016.html：题录、版本号、作者、摘要、公开PDF入口。未把同题同作者或摘要相同单独当作正式版逐字关联证明；正式定理依据作者公开JACM副本内部身份。

early_subgraph_candidate_abs.html：arXiv1504.02876，The Hardness of Subgraph Isomorphism，2015-04-11，三位作者。只读条目元数据及摘要；旧弱界按摘要宣称登记，正文未读、不承担EL-A的源证明。

JACM2017_doi_metadata.json：DOI内容协商题录。article-number为空；文章18的身份来自PDF。在线/印刷日期分别2017-06-16/2017-06-30。题录元数据不代替数学正文。

## 既有项目工具

TP-1 DECISION/NORMALIZED_THEOREM、RC-1 INTERFACE_LEMMAS的L4/H及TT-1合同和计费已读取/复用，冻结于INPUT_MANIFEST。复用读取及当前知情重读不形成新的独立审查者。

RC-1重数事实在当前归约中重新给出全称证明；T3/PR-C3不用于下界映射。上界来源继续按TT-1/TP-1实际证明口径管理。

COL2026请求数0，暂停状态保持。未增加外部作者意见、研究者人工阅读全文声明、形式化验证或可执行数学测试。
