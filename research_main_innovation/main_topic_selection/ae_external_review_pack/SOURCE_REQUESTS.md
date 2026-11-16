# 指定来源请求与英文交接草稿

版本 ER-1，2026-11-06。所有英文文本均为**供研究者自行转交的草稿，尚未发送**。回复者可提供正常公开链接、可获授权的全文或版本确认；无需提供账户或口令。

## 1. 本轮目录复查

已对 `D:\毕业设计\research_main_innovation\main_topic_selection\` 下PDF作递归文件名、大小、修改时间与SHA256清单检查，并核对已登记来源身份及指定接收位置。见 [sources/LOCAL_SOURCE_RECHECK.json](sources/LOCAL_SOURCE_RECHECK.json)。

当前取得范围保持：COL2019的18页v1、KU同题28页作者稿、Damaschke2013正式预览433–434页。未定位到新增COL2026完整正式版/接受稿、Damaschke2013完整章或KU期刊排版版。该结论限所列目录及检查方式；本轮没有新的出版方网络获取，也没有据此推断其他公开来源不存在。

## 2. 首要请求：COL2026可绑定完整正文

**文献身份。** Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov，*Low-rank binary matrix approximation in column-sum norm*，Theoretical Computer Science，2026。

- DOI：[10.1016/j.tcs.2026.116240](https://doi.org/10.1016/j.tcs.2026.116240)。PII：S030439752600469X。
- 正常出版入口：[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S030439752600469X)。卷1086、文章116240和Open Access标记继承研究者提供的条目核读记录；原记录明确正文仍返回403，未升级为已取得全文。
- 已有：2019年[arXiv1904.06141v1](https://arxiv.org/pdf/1904.06141v1)完整稿，定义与随机PTAS已读；2026题录/摘要。相同题名和作者仅支持同工作关联，不能代替正式版差异核对。
- 需要：完整正式PDF或作者接受稿，含定义、全部相关定理、算法、证明/附录、参考文献和必要补充文件。接受稿需有可靠关联该DOI及版本身份的作者声明或机构记录。
- 将改变的判断：COL2026是否直接或经完整短推论覆盖共同显式R、L=|R|、逐行半径r及确定性T2参数界。
- 建议接收：本交接目录的 `sources/COL2026_VOR.pdf`；接受稿用 `sources/COL2026_AAM.pdf` 并附正常来源链接。原 `ae_col2026_check/sources/` 下的同名位置也继续有效。

**English draft — complete text request**

Subject: Full-text/version request: Low-rank binary matrix approximation in column-sum norm (2026)

Dear Professor,

I am checking an exact parameterized result for Binary Constrained q-Center with one common explicit relation R. Could you point me to the complete journal version or an accepted manuscript of your 2026 paper, DOI10.1016/j.tcs.2026.116240? I have read arXiv:1904.06141v1 and can access the journal entry and abstract. A version reliably linked to the DOI, including proof appendices and any relevant supplementary material, would allow a theorem-by-theorem comparison. In particular, I would like to check for exact algorithms parameterized by the common relation size and maximum Hamming radius.

Thank you for any public link or version information.

Best regards,
[Researcher name]

## 3. Damaschke2013：完整433–437页

**文献身份。** Peter Damaschke，*Cluster Editing with Locally Bounded Modifications Revisited*，IWOCA2013，LNCS8288，433–437。

- DOI：[10.1007/978-3-642-45278-9_38](https://doi.org/10.1007/978-3-642-45278-9_38)。[机构题录](https://research.chalmers.se/publication/187873)。
- 已有：出版方公开[两页预览](https://page-one.springer.com/pdf/preview/10.1007/978-3-642-45278-9_38)，对应433–434；SHA256 `e4ac89a7cfbeb8da7069871fdbdd700d87823c990b697896587f20406f375b12`。参数定义、新核大小及引言时间已目视核对。
- 精确缺项：**435–437页**，包括Lemma1剩余证明、完整核化过程与证明、个别τ、总K和簇数d的保留、恢复及随机版本细节。优先提供完整5页PDF以保留上下文。
- 2016年*Sufficient Conditions for Edit-Optimal Clusters*已取得；其首页只声明扩展2013的一节，不能补齐核化正文。
- 将改变的判断：正式章的完整算法及前提能否支持现有模型/参数桥接；当前状态是UNRESOLVED_SOURCE_OR_MAPPING。
- 建议接收：`sources/DAM2013_full_authorized.pdf`，附来源或作者版本说明。

**English draft — chapter request**

Subject: Complete chapter request: Cluster Editing with Locally Bounded Modifications Revisited

Dear Professor Damaschke,

Could you point me to a complete authorized copy of your IWOCA2013 chapter, DOI10.1007/978-3-642-45278-9_38, pp433–437? I have the publisher's preview of pp433–434 and your later paper on sufficient conditions for edit-optimal clusters. For a parameterized-algorithm comparison I need the remaining kernelization argument, especially the treatment of individual local bounds, the total edit budget, the cluster bound, and solution reconstruction. A public author manuscript or another normal full-text source would be very helpful.

Thank you.

Best regards,
[Researcher name]

## 4. 较小项：KU最终版与已读作者稿的对应

**文献身份。** Christian Komusiewicz、Johannes Uhlmann，*Cluster editing with locally bounded modifications*，Discrete Applied Mathematics160，2259–2270，2012，DOI [10.1016/j.dam.2012.05.019](https://doi.org/10.1016/j.dam.2012.05.019)。

- 已有：[研究组公开完整作者稿](https://fpt.akt.tu-berlin.de/publications/ce-bounded-degree.pdf)，28页，页脚2012-05-23、Preprint submitted to Discrete Applied Mathematics；SHA256 `ce554912f39a778d490f9c44d2a43b3620d50734d43c496596cce666c4c8683b`。§4、Theorems6/7及核化证明已经核读。
- 需要：正式2259–2270页PDF，或可靠作者/机构说明，确认作者稿§4与最终版相关结果的对应及实质修改。无需重复提供已存作者稿。
- 将改变的判断：是否有最终版新增的模型、算法、证明或定理编号变化影响覆盖比较。现有作者版按PARTIAL_OVERLAP使用。
- 建议接收：`sources/KU2012_journal_authorized.pdf`，或版本确认的链接/文本记录。

**English draft — version check**

Subject: Version correspondence for Cluster editing with locally bounded modifications

Dear Professors Komusiewicz and Uhlmann,

I have read the complete manuscript ce-bounded-degree.pdf hosted by the TU Berlin group, dated 23 May 2012. Could you confirm how its Section 4 and Theorems 6/7 correspond to the final Discrete Applied Mathematics article, DOI 10.1016/j.dam.2012.05.019? I am particularly interested in any substantive changes to the locally bounded model, the 4dt/2dt kernels, and reconstruction. A final-version link, theorem-number correspondence, or brief version confirmation would suffice for this check.

Thank you.

Best regards,
[Researcher name]

## 5. 可转交的查新询问草稿

Subject: Exact common-relation Binary Constrained q-Center: theorem identification

Dear Colleague,

Could you help identify an existing exact theorem for the following contract? The input is m binary strings of length n and one common explicit relation R⊆{0,1}ᑫ, with L=|R|. Each coordinate chooses a tuple of R; each input string chooses one fixed covering center and has at most r errors. Repeated or unused centers and unused patterns are allowed. The target is deterministic exact construction of all original ordered centers in time 2^{O(L²+Lr log(Lr+2))}poly(mn+qL).

The attached working note gives a separation-row/exception-coordinate search and its complete accounting. We would welcome either a proof defect or an exact source and theorem yielding this bound or a stronger one, including a short reduction if required. We have compared the 2019 constrained-center PTAS, the 2020 total-edit fixed-template algorithms, and the read locally bounded cluster-editing manuscript; the 2026 column-sum journal text and the final three pages of the 2013 chapter remain outstanding.

Best regards,
[Researcher name]

## 6. 接收后的最小核查顺序

记录实际来源、版本声明、页数、SHA256和读取范围；核对完整正文是否与请求身份绑定；回到定义与定理逐项映射共同R、最大逐行预算、角色使用、随机性、参数和完整输出。需要新增C2/Lr证明才能获得目标时，将该桥接责任显式保留。

外部意见应保存原答复及其作者声明的核读范围。哈希固定版本，不单独承担独立性或原创性判断。本轮没有发送上述草稿、取得外部意见或对缺页补写证明。
