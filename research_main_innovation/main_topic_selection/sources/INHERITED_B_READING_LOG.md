# 来源与定位记录

日期：2026-11-05。主文稿版本PR-SCREEN-1。来源类型分为作者原文/出版方原文、官方源码/接口、发现用目录、检索页面与本轮推导。所有字节哈希最终记录在SOURCE_MANIFEST.json；历史来源未修改，复用路径见REUSED_INPUTS.json。

## 1. 新取得并实读的原文

|ID|准确题名、作者、发表/版本|原文与本地文件|实际阅读/定位及使用边界|
|---|---|---|---|
|DALL2024|*Dependency-Aware Online Caching*；Julien Dallot、Amirmehdi Jafari Fesharaki、Maciej Pacut、Stefan Schmid；作者元数据标记INFOCOM2024；arXiv2401.17146，2024-01-30|[作者稿](https://arxiv.org/pdf/2401.17146)，dependency_caching.pdf，21页，SHA256 `f03a510e2a627ca9dde1932b5f5087888b5382292d461dcced5683e3d39172d3`|摘要、§1.2–1.3、PDF p5 §3模型/ℓ定义、§4.1算法、p11 Theorem6及紧邻证明、p12 Theorem7及构造部分、§5旁路模型/定理；未逐行重推完整随机证明。重点：永久驻留闭包、单位fetch、oblivious adversary；ℓ按传递闭包后对称图的最大独立集定义|
|JPS2020|*Online Algorithms for Weighted Paging with Predictions*；Zhihao Jiang、Debmalya Panigrahi、Kevin Sun；arXiv2006.09509v1，2020-06-16；目录另记ICALP2020/ACM TALG2022，后者修订稿未核|[作者稿](https://arxiv.org/pdf/2006.09509)，weighted_limits.pdf，27页，SHA256 `de2c2d0f06ae4ad4f17ec1f16645ce2746cd0cc2745f861e47b4483e393a13dc`|摘要、§1定义/Theorems1.1–1.3；PDF p3 PRP、p4 SPRP；§2下界构造与证明概要、p7 Theorem2.1、p9 Theorem2.5及oblivious分布、对应权重/blocks；§3/§4只核对更强信息的定义/结果。复杂概率论证未独立重推，按作者证明范围引用|
|BC2022|*Learning-Augmented Weighted Paging*；Nikhil Bansal、Christian Coester、Ravi Kumar、Manish Purohit、Erik Vee；SODA2022目录条目；实际使用arXiv2011.09076v2，2021-11-09|[作者稿](https://arxiv.org/pdf/2011.09076)，weighted_predictions.pdf，23页，SHA256 `748d917432ccb2872b27144a009a8c79b3e84a8e6fb79ba622998be870411586`|摘要、§1.1–1.3，PDF pp2–3；§2 rank/interface说明及§4部分成本模型；AppendixB仅定位。Theorems1.1–1.4、ηw及ε定义已对照渲染页目视核验，图片weighted_predictions_page-02/03.png。未声称完成随机算法所有证明的独立复核|
|METRIC2020|*Online metric algorithms with untrusted predictions*；Antonios Antoniadis、Christian Coester、Marek Eliás、Adam Polak、Bertrand Simon；ICML2020，PMLR119；本轮使用出版方11页版|[出版方原文](https://proceedings.mlr.press/v119/antoniadis20a/antoniadis20a.pdf)，metric_predictions.pdf，SHA256 `513bb0f887d22a98b6d25634b85633e54cc2acd95dd081ad90e65b60e2359fa1`|摘要、§1 metric/状态预测定义、PDF p2 Theorems1–3、§2框架及§3组合的相关条件；后续matching实验未核。本轮引用Theorems1–2的原假设与界，未转化成一般有向状态图定理|
|N2013|*Pebble Games, Proof Complexity, and Time-Space Trade-offs*；Jakob Nordström；LMCS9(3:15)，2013；arXiv1307.3913v3，2013-09-20|[全文](https://arxiv.org/pdf/1307.3913)，pebble_survey.pdf，63页，SHA256 `9c773f87376b96e3ad4e46acf0adc2d82b4cf378b847fe3703bddb9588dfbd34`|摘要及PDF pp14–15 Definition2.10的黑pebble规则、时间/空间/完成定义。其余证明复杂度结果未作本轮依据；该文为综述，本文未把它登记成模型最初提出文献|
|LRC2017|*LRC: Dependency-Aware Cache Management for Data Analytics Clusters*；Yinghao Yu、Wei Wang、Jun Zhang、Khaled Ben Letaief；本轮使用arXiv1703.08280v1，元数据2017-03-24|[作者稿](https://arxiv.org/pdf/1703.08280)，lrc.pdf，9页，SHA256 `0dffc1ad7ab58ef37c68a531f3c5c12b86e4e408dc20101e61486f75b88606f6`|摘要、§I/II Spark RDD、DAG与缓存语义，reference count的定义及更新说明。用于区分生成依赖与永久闭包，未使用其性能数字支持本轮主张|

上述PDF有结构预检sidecar，均PASS。提取文字中有旋转/字体警告，BC2022包含控制字符，涉及其错误量和定理公式时已用Poppler渲染pp2–3目视核对。结构PASS仅证明解析结构；语义仍限于列明阅读范围。

## 2. 复用来源及重核位置

|ID|来源|本轮重核|
|---|---|---|
|DTR|*Dynamic Tensor Rematerialization*，Kirisame等，ICLR2021；[全文](https://arxiv.org/pdf/2006.09616)，dtr.pdf/txt；原哈希见SOURCE_MANIFEST/REUSED_INPUTS|§2依赖、pin与递归重算；p4 Theorems3.1–3.2，特别是离线重排；p9 §7学习过去batch的未来工作。附录未作本轮新外部复核|
|CHECKMATE|*Checkmate: Breaking the Memory Wall with Optimal Tensor Rematerialization*，Jain等，MLSys2020；[全文](https://arxiv.org/pdf/1910.02653)，checkmate.pdf/txt|§4.1–4.10，p4 T=n、p5峰值、p6 frontier/目标、p7求解与成本。固定阶段可行域保持原样|
|YOUNG|*On-Line File Caching*，Neal E. Young，Algorithmica2002；[原文](https://arxiv.org/pdf/cs/0205033)，young_file_caching.pdf/txt|§1文件大小/固定retrieval fee，p3 Landlord/变化通知脚注，p4 Theorem1。只约束检索费|
|LV2018|*Competitive Caching with Machine Learned Advice*，Thodoris Lykouris、Sergei Vassilvitskii，ICML2018；[原文](https://proceedings.mlr.press/v80/lykouris18a/lykouris18a.pdf)，prediction_caching.pdf/txt|§2 PRP/误差、§3 Predictive Marker/Theorem2。单位页与费用；本轮保留更强BC2022作为加权子族对照|
|VEGA|微软[固定源提交](https://github.com/microsoft/vega-prover/tree/c0ee259053cd12eaf43ed71b5cde375452b3ee4d)，vega_source.zip及vega_code|vega_mc_zkp.rs 1268–1295整份keys、1349–1365私有prep、1393–1476 setup、1482–1607 prepare、1614–1670 prove/check、1770–1784临时cache复制、2107返回、2111–2132 verify；r1cs.rs 292–408/568–601；traits/circuit.rs19–52|
|V-PREP/PROVE|[prepare](https://microsoft.github.io/vega-prover/mc/prep.html)、[prove](https://microsoft.github.io/vega-prover/mc/prove.html)、[scope](https://microsoft.github.io/vega-prover/spec/scope.html)；继承网页快照|复用合同、缓存有效性、高层调用及返回对象；文档与固定源码交叉核对。内部机制不能直接当作可调用API|

原文更宽的历史阅读记录保存为PREVIOUS_READING_LOG.md。本轮主文稿仅依上述重核范围；历史未取得全文、历史运行数字或其他密码电路线索均未升级。

## 3. 检索与未决条目

公开搜索连接器查询`learning-augmented dependencies caching`、`online pebbling predictions`、`dependency-aware caching algorithm competitive`返回传输错误。HTTP公开检索/元数据的各次请求分别存于RETRIEVAL_SEARCH、RETRIEVAL_DISCOVERY、RETRIEVAL_ARXIV_SEARCH、RETRIEVAL_DISCOVERY2、RETRIEVAL_PRIMARY、RETRIEVAL_SECONDARY_PRIMARY、RETRIEVAL_THEOREMS、RETRIEVAL_METADATA.json。

DBLP两域响应为HTTP202机器人验证HTML，未继续处理验证，未将其视为论文元数据。Google未提供可读结果；Bing出现与查询无关的页面，均排除于事实证据。部分arXiv短语/标题检索因SSL EOF失败，其他标题检索可用；具体未命中无法证明不存在相关工作。ALPS前端脚本获取失败，取得其公开源归档用于目录发现。

ALPS归档commit=`286e29d1fcf950cfef04d00404e117f0996412dd`；450条papers/*.yml。针对dependency、rematerialization、pebbling、checkpoint、recomputation及缓存/metric词汇保存CATALOG_SEARCH.json，包含部分词法假阳性；目录角色仅为发现。已取得近邻的定理判断回到原论文。本轮未查得并核读一篇同时包含“一般生成DAG、外部PRP、同顺序/同容量、生成峰值规则”的完整误差定理，覆盖范围继续未决。

learning-augmented rematerialization、online pebbling with predictions、prediction-assisted checkpointing、robust online recomputation相关方向均纳入上述目录/标题/术语筛查；未取得具体匹配原文的项目保留`UNRESOLVED`，不写覆盖/未覆盖断言。DTR的2021未来工作不能单独作为2026未解决问题的证明。

## 4. 本轮推导资产与证据边界

- M-PRP外部预测及内生性反例：纸面定义/合成对象。
- 无边子族对加权paging的映射：已知模型归约，继承原文边界。
- 黑pebbling对应：可行性及限定单sink的仿射成本关系；多输出状态图为标准表示。
- 非对称闭环例：只排除同一状态空间的metric+势差直接表示。
- 三个决定性实例：手工成本与守卫核验；未运行穷尽枚举或机制实现。
- 2×2随机minimax值108/7：标准有限博弈的算术结果；附于ARITHMETIC_CHECKS.json。

候选机制、新分析算法、认证服务与真实账户操作均为0。提取、哈希和算术处理属于文档取证辅助，不具有候选调度或保护功能。
