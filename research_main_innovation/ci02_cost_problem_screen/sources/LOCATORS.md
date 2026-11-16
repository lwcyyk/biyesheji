# 原文定位与实际阅读范围

日期为2026-11-05。数字的证据类型采用AUTHOR_REPORTED（作者报告）、AUTHOR_REMEASURED_BASELINE（Vega作者重测其他实现）、DERIVED（本文计算）和NOT_REPORTED（已读来源未给出）。本轮进行了公开资料整理和算术核对。

## 来源定位

|ID|来源与版本|定位/实际阅读范围|用途|
|---|---|---|---|
|V1|Kaviani、Setty，Vega本地19页PDF，SHA256 `2893026c8c8dc4db4da724869873119b3c4834406913c33f8200a210ae3ba8a4`|摘要、§1.2、§2、§7、§8、§9及参考实现链接|功能、预计算和性能|
|V1-F10|[Vega PDF](vega.pdf)|PDF第15页Figure 10，已渲染并目视核对[图页](vega_fig10.png)|1920 byte MSO全表；线程数、阶段时间、proof/pk/vk|
|V1-EVAL|同V1|PDF第14页§8、§8.1；第15页各阶段正文|Azure F16as v7、16 vCPUs/64GB RAM、mock device及阶段定义|
|V1-MEM|同V1|PDF第15页Peak memory段|MC约100 MB预计算、562 MB在线峰值；该段线程数未给|
|V1-SIZE|同V1|PDF第15页§8.2、Figure 10；第16页Figure 11|密钥/证明大小、长度趋势；图10的SC vk=6587 kB，§8.2正文泛称pk/vk均6588 kB，保留差异|
|V1-SMALL|同V1|PDF第1页摘要|896-byte凭据的62 ms/17 ms/83 kB；该条线程条件未单列|
|V2|[官方prepare](https://microsoft.github.io/vega-prover/mc/prep.html)，本地vega_prep.html/txt|Input and output、Shared witness、Precommitted states、Prover-internal caches、Rerandomization per proof|私有预计算结构、复用、缓存有效性；复用此前取得的网页快照|
|V3|[官方prove](https://microsoft.github.io/vega-prover/mc/prove.html)，本轮网页快照|Ordered pipeline 1–12|每次重随机化、检查、fold/sum-check/PCS及返回state；文本vega_prove.txt|
|V4|[官方scope](https://microsoft.github.io/vega-prover/spec/scope.html)，本轮快照|Canonical engine、Proof bytes and determinism、Out of scope|T256/Keccak/Hyrax与内部缓存边界；不提供具体实现性能承诺|
|V5|[Vega作者项目](https://github.com/microsoft/vega-prover)，README本轮main快照|Performance、References及bench说明|S&P2026作者标注、Rust、SHA-only bench输入及阶段；与图10的版本关联未报告|
|V6|[MSR页面](https://www.microsoft.com/en-us/research/publication/vega-low-latency-zero-knowledge-proofs-over-existing-credentials/)，含BibTeX快照|题名/作者/May2026/BibTeX|BibTeX类型为unpublished，项目README标注IEEE S&P2026；本轮未取得IEEE DOI|
|C1|[Crescent ePrint元数据](https://eprint.iacr.org/2024/2013)|全文元数据、摘要、History与Publication info|Preprint；2024-12-13 received、2025-03-26 revised；PDF端点403|
|C2|[Crescent作者项目](https://github.com/microsoft/crescent-credentials)，README version 1.0/main快照|Setting up、命令阶段、Selective Disclosure、Range proofs、Device-Bound Credentials|zksetup/prove/show/verify语义和复用|
|C3|[Crescent setup README](https://github.com/microsoft/crescent-credentials/blob/main/circuit_setup/README.md)|依赖、Sample JWT/mDL、Running Setup、Troubleshooting|Circom v2.1.6；setup适用issuer/proof specification；编译内存警告不是实测峰值|
|C4|[MSR Crescent页面](https://www.microsoft.com/en-us/research/publication/crescent-stronger-privacy-for-existing-credentials/)，含BibTeX|作者/日期/摘要|页面November2024、项目December2024、ePrint接收日期不同；精确书目按ePrint记录|
|L1|Frigo、shelat，CIC Vol3 No1，44页[出版方PDF](longfellow_cic.pdf)，DOI [10.62056/a3qjmpgxq](https://doi.org/10.62056/a3qjmpgxq)|摘要、§1、方法概述、§5及§6性能、参数和相关说明|正式期刊版本；PDF结构预检PASS见longfellow_cic_preflight.json|
|L1-HW|同L1|PDF第29–30页§5 Evaluation|硬件、单线程、手机热节流控制、128-bit hash参数、Ligero约110-bit参数|
|L1-ECDSA|同L1|PDF第35页Table 11、§5.3|1/2/3签名微基准；与完整凭据展示分开|
|L1-TOY|同L1|PDF第37–38页§6.1、Table 12|183-byte玩具凭据；原表proof size单位写为kb|
|L1-MDOC|同L1|PDF第38页Alg10、第39页Table13和相邻正文|表13声明≤2231 bytes；Alg10写2551-byte witness。记录输入界差异；按表13标注其数据|
|L2|[Longfellow ePrint元数据](https://eprint.iacr.org/2024/2010)|摘要、History、Publication info|初稿2024-12-12；2026-04-27 last of 2 revisions，说明CIC2026版本；ePrint PDF403|
|L3|[官方benchmarks](https://longfellow-zk.github.io/longfellow-zk/docs/benchmarks/)|Mac M4 FFT/SHA/ECDSA及页面时间|2025-10-17修改；[提交7906304](https://github.com/longfellow-zk/longfellow-zk/commit/790630406916ef9f87cf8e8334283ea6f22db0f3)，原Markdown已取得|
|L4|[Longfellow项目](https://github.com/google/longfellow-zk)，README本轮main快照|Overview、Specifications、Requirements、bench命令|C++工具链依赖；当前V1/V2说明与CIC参数另列，未用于重写论文数据|

## 阅读与获取限制

Crescent全文PDF返回403，本轮阅读C1–C4与Vega的共同评测。Crescent数值在主表中全部标为Vega作者重测，不能归为Crescent原论文原生硬件实验。NOT_REPORTED对该工作仅指已取得来源范围，原PDF是否报告相关字段保留未核实。

Longfellow ePrint PDF403后，从官方出版方取得CIC全文。CIC文章HTML入口有URLError，卷期目录和正式PDF可用；DOI与作者见PDF第1页。当前Longfellow README、2025 benchmark页与2026论文各有版本标记。

公开搜索连接器出现MCP传输错误，后续使用官方作者、项目和出版方HTTPS来源。vega/mc/proving.html为错误路径404，已按prepare页面链接取得mc/prove.html。Longfellow benchmark的_index.md路径404，已按网页View page source取得benchmarks.md的固定提交。

PDF读取工具的输出路径模式在Windows受POSIX dirfd要求限制。改用同一现有预检工具的stdout模式保存结果，Longfellow结构预检PASS。Poppler提供pdfinfo/pdftoppm；本机无pdftotext，文本由pypdf提取。Vega图10已可视核验。所有受限动作与资料摘要另见各RETRIEVAL_*.json。

## 来源完整性

REUSED_INPUTS.json保存复用来源的原始路径与SHA256。新取得资料的URL、时间、状态与SHA256分别见RETRIEVAL_LOG.json、RETRIEVAL_PAPERS.json、RETRIEVAL_ADDITIONAL.json、RETRIEVAL_BENCHMARKS.json和RETRIEVAL_CIC.json。VEGA_FIGURE10_TRANSCRIPTION.json是原表转录，DERIVED_COSTS.json保存本文算术模型，二者证据类型分开。
