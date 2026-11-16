# GH1961原文核读、来源与过程

CT-1；2026-11-07。所有时间以获取JSON中的实际时点为准。本文只记录本轮实际行为，不把历史失败、搜索片段或空文本提升为原文证据。

## 1. 来源身份与获取链

R. E. Gomory、T. C. Hu，Multi-Terminal Network Flows，J. Soc. Indust. Appl. Math. 9(4)，551–570，December 1961，DOI10.1137/0109047。

1. 任务给定NYU作者PDF：本次HTTP404，记录于ACQUISITION.json。NYU主页及同URL的HTTP入口也404，各入口按实际记录保存。
2. DOI入口与Crossref所列出版方PDF本次403。Crossref题录返回200；raw crossref.json保存题名、作者、卷期、页码、1961-12、DOI及VOR链接，题录只承担身份关联。
3. 联网连接器open/search两次均发生后端传输错误，未取得可读网页；随后使用正常公开HTTP读取作者目录。Google返回JS跳转页面，Bing RSS返回无关词典条目，均未用作数学或文献覆盖证据。
4. 作者域名ralphgomory.com正常重定向至ralphgomory.org，首页明确链接Mathematics目录。
5. [作者Mathematics目录](https://ralphgomory.org/mathematics/)中精确题名“Multi-Terminal Network Flows”直接链接[此PDF](https://ralphgomory.org/wp-content/uploads/2023/02/11_flows-1.pdf)，返回200并保存为GH1961_author_public.pdf。

目录另有近名“Multi-Terminal Flows in a Network”条目，文件名为11_flows.pdf。本轮取精确题名条目的11_flows-1.pdf，并核验正文身份，没有按近似标题或同文件编号混同版本。

### 实际文件

- 大小：478841字节，以实际文件stat和下载字节数为准。
- SHA-256：e41fe0be19fe74dfcd4ef5302d3b425fae03a6c91dfa5ee78dc31dcad2b121de。
- 20页；首末印刷页551/570，与题录551–570吻合。
- 首页面上有卷9、期4、December1961、题名和两作者。论文正文为期刊排版扫描，作者公开目录关联明确；1961扫描首页没有印现代DOI，DOI由精确题录组合绑定。
- PDF元数据Title/Author为空，Creator为Canon扫描设备，创建2007、修改2011；这些是电子文件元数据，不当成发表日期。当前URL路径含2023/02也不作原出版日期。
- 没有标注Abstract的独立摘要块；p.551引言说明本文研究多终端网络流的可实现性、分析及综合。

证据文件：GH1961_ACQUISITION.json、AUTHOR_MATH_RECORD.json、author_mathematics.html、PUBLIC_ENTRY_CHECK.json、SECOND_ENTRY_CHECK.json、THIRD_ENTRY_CHECK.json和crossref.json。

## 2. 解析、页锚与视觉读取

pypdf严格模式能解析全部20页、无解析警告，但全部页文本长度为0。GH1961_text.txt只含页分隔标记，是失败的文本抽取结果，不充当正文转录。正文通过Poppler页图目视核读，没有执行OCR，也未把空文本搜索当作未出现定理的证据。

ARS pdf_read_preflight第一次使用--output在当前Windows环境报告POSIX dirfd绑定限制；改用脚本原生stdout后得到结构PASS，并原样保存GH1961_preflight.json。该侧栏的SHA与原PDF一致，声明页数/枚举页数/reader页数均为20，warnings为空。它只保证所列结构范围。

pdfinfo识别20页、非加密、扫描元数据及页尺寸；其File size显示0与实际文件不符，因此字节大小采用stat/哈希，不采用该字段。页锚还由已显示的印刷页号核对。

### 实际视觉范围

|页图|印刷页 / PDF页|核读用途|
|---|---|---|
|page_images/first.png|551 / 1|完整页面；期刊/作者身份、引言、连通/无向对称非负容量假设|
|page_images/gh-02.png|552 / 2|流值关系、路径和最大生成树论证的起点|
|page_images/gh-03.png|553 / 3|数值表示与分析问题转入；区分数值树和后续实际割构造|
|page_images/gh-04.png|554 / 4|Lemma1及最小割收缩证明、cut集合拆分|
|page_images/gh-05.png|555 / 5|Lemma1结束；迭代细分广义节点、保存原割的实际构造|
|page_images/gh-06.png|556 / 6|n−1次流计算、Lemma2的准确路径最小边值陈述|
|page_images/gh-07.png|557 / 7|构造实例中的缩图与附着位置|
|page_images/gh-08.png|558 / 8|Lemma2证明起点：每条路径边对应分离两点的实际割，给出上界|
|page_images/gh-09.png|559 / 9|构造不变量、相邻块中实现原流值的端点、证明继续|
|page_images/gh-10.png|560 / 10|Lemma2证明结束；未编号cut tree定义及存在性；基本割容量等于附着边权|
|page_images/last.png|570 / 20|尾页页码和参考文献身份；未用于图论引理的新内容推导|

部分扫描行的右沿较紧；本轮所需的模型、Lemma2显示式、cut tree定义与存在性结论可在上述整页图复核。551–560为实质核读范围；561–569没有登记为完整实质核读，570只作身份检查。原PDF本身包含全部20页。

主稿未以长引文代替核对，采用准确位置与数学重述。原文没有给本轮I/W图计数命题的直接编号；本文没有据限定阅读范围宣称全篇或全部后续文献均无该表述。

## 3. 证明与来源责任

|责任|实际归属|
|---|---|
|非负无向网络的割树存在性、基本割实际容量、路径最小边值|Gomory/Hu1961原文|
|以>r树边收缩、标记W块、未标记分量收费、全树边数|监督对话提出的模型辅助待检路线|
|原基本割提升、非负容量覆盖不等式、空/断开/孤立边界|本轮当前对话中的知情模型辅助证明补全|
|模板计数图、每行割、两高型小割、实际profile合并|监督路线在本轮完整核验并写成全称证明|
|每r下2w−1达到|HG-1原星形结构及平衡计数，本轮重新核对并接入割树账本|
|给定计数后同型展开、wr+1截断恢复|项目已有S1/RC-1工具，本轮完整保留费用/量词|
|全高型表枚举费用|本轮统一计数界＋既有截断＋标准显式枚举的推论；不调用H_normal/T3|
|数学/发表独立性|同一项目上下文的知情模型辅助；没有外部读者、证明助手或新独立审查会话|

经典工具的归属已经绑定。图论计数表述与模板推论是否已有发表先例仍待核，未使用全球首次或最优算法措辞。本轮支持的是计数极值紧性；完整求解时间和具体参考必要代价各有责任。

## 4. 历史依赖

INPUT_HASHES.json固定以下历史文件：

- ae_heavy_type_general_radius的三份主稿：原模型、H_count/H_normal、受限定理、达到构造、固定列和反例和下步试件。
- ae_r1_nfold_compilation的INTERFACE_LEMMAS及PROOF_OR_COUNTEREXAMPLE：r=1森林及达到结构的原版本。
- ae_strict_separation_gate/DECISION：原两族分离判废和实现门状态。

本轮未改历史文件。COL2026暂停、FS23无新正文入口的状态沿用，两个来源请求均为0；GH1961的正常原文获取独立登记。
