# 来源、版本、定位与实际阅读范围

日期：2026-11-05。范围为公开接口、原有算法和纸面性能问题。来源文件保存在本目录，历史输入哈希见INPUT_HASHES.json，新获取记录见RETRIEVAL01/02/03.json。本轮来源归档哈希另见SOURCE_MANIFEST.json。

## 1. 证据与来源ID

|ID|准确来源/链接|版本绑定|本轮实际阅读及定位|
|---|---|---|---|
|V-PAPER|Darya Kaviani、Srinath Setty，*Vega: Low-Latency Zero-Knowledge Proofs over Existing Credentials*；[作者页面](https://www.microsoft.com/en-us/research/publication/vega-low-latency-zero-knowledge-proofs-over-existing-credentials/)、[ePrint 2025/2094](https://eprint.iacr.org/2025/2094)|本地vega.pdf，19页，SHA256 `2893026c8c8dc4db4da724869873119b3c4834406913c33f8200a210ae3ba8a4`；作者项目标记S&P2026，出版方DOI本轮未核|继承前轮摘要、§1.2、§2、§7–9/Fig10–11阅读；本轮重点重读§1.2复用划分、§8–8.2评估/阶段/参数，PDF p14–15。逐段读取范围限于所列部分|
|V-PREP|[官方prepare说明](https://microsoft.github.io/vega-prover/mc/prep.html)|复用vega_prep.html/txt网页快照，文档页面提交未取得|Input/output、Shared witness、Precommitted states、Prover-internal caches、Rerandomization per proof，文本约180–216行；与固定源码交叉检查|
|V-PROVE|[官方prove说明](https://microsoft.github.io/vega-prover/mc/prove.html)|vega_prove.html/txt快照|入口签名、ordered pipeline、cache检查、返回state|
|V-SCOPE|[官方scope](https://microsoft.github.io/vega-prover/spec/scope.html)|vega_scope.html/txt快照|canonical engine、verifier/public IO、proof bytes、internal cache与conformance边界；性能特征排除于该规范之外|
|V-CODE|[微软官方源仓库固定提交](https://github.com/microsoft/vega-prover/tree/c0ee259053cd12eaf43ed71b5cde375452b3ee4d)|官方归档vega_source.zip注释给出提交；SHA256 `71142dd893c350c80f4a03fda278e86c62a660645fffb9aefd246d61d108c810`|仅提取/读取预处理依赖及高层接口；构建和运行0。src/vega_mc_zkp.rs：562–588底层无缓存重算；1349–1365 state；1393–1476 setup；1482–1607 prepare；1614–1670 rerandomize/check；1770–1784 cache复制；2107返回；2111–2132 verify/精确步骤绑定|
|V-TRAIT|同V-CODE，src/traits/circuit.rs|同一提交|19–52：public_values/shared/precommitted/challenges/synthesize的划分|
|R1CS|同V-CODE，src/bellpepper/r1cs.rs|同一提交|292–301 state；306–355 shared；359–408 precommitted；411–467 online；568–601 rerandomization|
|YOUNG|Neal E. Young，*On-Line File Caching*，Algorithmica 33，371–383，2002；[原文](https://arxiv.org/pdf/cs/0205033)、[元数据](https://arxiv.org/abs/cs/0205033)|14页作者PDF；SHA256 `f6669db6a6313f180f3585e04e7c45eb0d662496b508270ad0aabbbb05d20421`；arXiv存档2002版本|摘要、§1模型、p3 Figure1 Landlord与脚注1、p4 Theorem1、§2竞争性证明。松竞争性部分未作完整重推，未用于本轮结论|
|CHECKMATE|Paras Jain、Ajay Jain、Aniruddha Nrusimha、Amir Gholami、Pieter Abbeel、Kurt Keutzer、Ion Stoica、Joseph E. Gonzalez；*Checkmate: Breaking the Memory Wall with Optimal Tensor Rematerialization*，MLSys2020；[原文](https://arxiv.org/pdf/1910.02653)|本次arXiv下载PDF，15页；SHA256 `8355cc2ecac072863fde2542585f8da0be30924e6181d9b05a36a63b22a1f694`；存档版本见PDF和metadata快照|摘要及§4.1–4.10：p4 DAG/T=n、p5峰值/依赖、p6目标(9)/frontier、p7成本与求解开销；§5只读本轮涉及的求解边界，性能全表未复核|
|DTR|Marisa Kirisame、Steven Lyubomirsky、Altan Haan、Jennifer Brennan、Mike He、Jared Roesch、Tianqi Chen、Zachary Tatlock；*Dynamic Tensor Rematerialization*，ICLR2021；[原文](https://arxiv.org/pdf/2006.09616)|31页作者PDF；SHA256 `a3b6b6d229a1b21b9c67aee2cb17612837796ca192f79d8741509b752ba0a8b2`；PDF标记ICLR2021|摘要、§2在线机制、p4 §3/Theorems3.1–3.2及证明概要、p9 §7未来工作；附录相关位置仅定位，未声称完整核验所有附录证明|
|PRED-CACHE|Thodoris Lykouris、Sergei Vassilvitskii；*Competitive Caching with Machine Learned Advice*，ICML2018，PMLR80；[原文](https://proceedings.mlr.press/v80/lykouris18a/lykouris18a.pdf)、[出版页面](https://proceedings.mlr.press/v80/lykouris18a.html)|10页出版方PDF；SHA256 `e0e33540bdadc221c9418798e1251070c83e071804c9bbb57385d14048645db5`|摘要、§2 paging/建议模型、§3 Predictive Marker及Theorem2，PDF p6；本轮引用稳健O(log k)及建议误差相关性质，未把其定理推广到依赖DAG|

V-PAPER的实际阶段时间属于`AUTHOR_REPORTED`。C1和Q2的算术属于`DERIVED_CONDITIONAL`；C2/C3及Q-next最小实例属于`SYNTHETIC`。成熟文献定理属于`PUBLISHED_RESULT`，本轮归约属于`DERIVED`。有限实验、外部数学复核均未进行。

## 2. 定理使用边界

- Young：正整数size、固定非负retrieval cost；容量h/k及未来信息明确。脚注1已提出把变化文件当作新文件，前提是有变化通知。竞争界适用于检索费，策略CPU和临时内存分别计。
- Checkmate：固定DAG与已知费用的离线规划；T=n及frontier限制影响原可行域。对重复服务目标采用额外时间展开或有限状态模型时，需要独立可行性映射；本轮保留为纸面表示。
- DTR：Theorem3.1为单位时间/空间的线性网络；Theorem3.2的离线对照允许重排。这两个定理无法直接充当任意异质DAG、同序列对照的保证。
- Predictive Marker：单位大小/费用paging，有next-use建议；Theorem2使用总loss及spread函数给误差相关界，并受4H_k约束。本文只使用已读的定性保证和原模型边界。

## 3. 获取与阅读限制

官方Vega GitHub tree API返回403，改用公开官方归档并以ZIP注释固定提交。Young作者站一次连接失败、PDF入口404；arXiv原文取得成功。DTR首次获取URLError，后一次公开原文取得成功。详见RETRIEVAL01–03.json。

公开搜索连接器在本阶段再次出现`Transport send error / HTTP request failed`，查询为`"learning augmented" "rematerialization"`及`"dependency" "caching" "predictions" algorithm`。检索结果未取得，未形成广泛的当前先例覆盖判断。仅用已取得的原文支持具体命题。该限制无法支持“找不到先例”式优先权判断。

本地PDF预检为结构性检查，vega/Young/Checkmate/DTR/Predictive Marker均有对应`*_preflight.json`，后四项PASS。来源文字带`[PDF_PAGE n]`页标；不把结构预检当作语义正确性检查。Vega图10图页从历史目录复用，前轮已目视核验，本轮对照原PDF提取表文与转录。

继承的LOCATORS.md来自前轮文献表，覆盖Crescent/Longfellow等较宽范围，其未复制附件仍在`D:\毕业设计\research_main_innovation\ci02_cost_literature_review\sources\`。本轮主文稿使用本READING_LOG及已实际保留的文件作为直接定位，不把前轮未取得全文改写为已核读。

## 4. 可复核路径

原码摘录在`vega_code/`，官方ZIP完整保留。API_SCAN.json为归档内Rust文本检索记录，SOURCE_MANIFEST.json为本目录来源文件的大小与SHA256。COST_CHECKS.json仅进行算术核对，未执行任何候选算法或证明协议。历史输入哈希另存INPUT_HASHES.json。所有新增文件位于本阶段目录。
