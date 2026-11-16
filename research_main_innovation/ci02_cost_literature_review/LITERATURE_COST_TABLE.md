# 凭据证明系统的预计算复用与成本事实表

本表区分作者报告、Vega作者对基线的重测、本文计算和待测字段。整理日期为2026-11-05，使用academic-research-suite的来源核验流程。原文定位、版本、实际阅读范围和获取状态汇总于sources。[定位清单](sources/LOCATORS.md)

`NOT_REPORTED`表示本行列明的已读来源未给出相应值。Crescent全文获取受限时附`FULL_TEXT_UNAVAILABLE`，保留原论文是否另有报告的未决状态。密钥大小、私有预计算缓存大小、在线峰值内存各用独立字段。

## 1. 文献与版本

|工作|准确题名、作者与年份|发表状态和本轮使用版本|原文及实际阅读|
|---|---|---|---|
|Vega|**Vega: Low-Latency Zero-Knowledge Proofs over Existing Credentials**；Darya Kaviani、Srinath Setty；2026作者版本，ePrint编号2025/2094|本地19页作者PDF；项目README标注IEEE S&P2026，PDF附PC meta-review。MSR BibTeX类型为unpublished；IEEE出版方DOI未核。报告时间数据绑定本地PDF的SHA256|摘要、§1.2、§2、§7–9、Figures10–11；官方prepare/prove/scope及README。[作者页面](https://www.microsoft.com/en-us/research/publication/vega-low-latency-zero-knowledge-proofs-over-existing-credentials/) [本地全文](sources/vega.pdf) [V1–V6定位](sources/LOCATORS.md)|
|Crescent|**Crescent: Stronger Privacy for Existing Credentials**；Christian Paquin、Guru-Vamsi Policharla、Greg Zaverucha；2024|ePrint2024/2013明确为Preprint/Draft，2024-12-13 received，2025-03-26 revised。MSR页面November2024、项目README December2024存在日期差异。README自标version1.0|摘要/元数据、官方README、setup接口文档已读；PDF端点403。数值使用Vega重测并注明来源。[ePrint](https://eprint.iacr.org/2024/2013) [官方项目](https://github.com/microsoft/crescent-credentials) [C1–C4定位](sources/LOCATORS.md)|
|Longfellow|**Anonymous Credentials from ECDSA**；Matteo Frigo、abhi shelat；初稿2024，正式CIC版本2026|IACR Communications in Cryptology Vol3 No1，44页，DOI10.62056/a3qjmpgxq。PDF received2025-10-08、accepted2025-12-02；ePrint2024/2010另标2026-04-27修订|正式PDF摘要、方法概述、§5–6、参数和性能表；官方README、2025 benchmark页。当前库版本、CIC论文、Vega重测分别保存。[DOI](https://doi.org/10.62056/a3qjmpgxq) [出版方PDF](sources/longfellow_cic.pdf) [L1–L4定位](sources/LOCATORS.md)|

## 2. 功能、阶段与复用语义

|项目|Vega|Crescent|Longfellow|
|---|---|---|---|
|具体功能|对既有签名凭据作隐藏属性证明；论文mDL示例含issuer签名、设备nonce签名、有效期和年龄条件|既有JWT/mDL的选择性披露、unlinkable show、有效期与设备绑定；按参数集启用|既有ECDSA签名的PoK、SHA256与CBOR处理，组合为MDOC展示；另有签名单项及玩具凭据实验|
|方案/参数|SC与MC；MC使用重复SHA256 step和core。官方规格选T256/Keccak/Hyrax；论文签名场景P-256|rs256、rs256-sd、rs256-db、mdl1；Groth16预处理与show组合；circuit-specific trusted setup|sumcheck＋Ligero、Reed–Solomon编码；CIC full-MDOC使用two-field优化；透明setup|
|阶段命名对应|setup→初始化S；prep_prove→每凭据预计算P；prove→在线O；verify→V|zksetup及circuit setup→S；**prove→每凭据P**，存入client state；**show→在线O**；verify→V|Vega重测列Setup/Prove/Verify，Precompute为“—”；CIC按组成原语及完整展示分别计时|
|预计算工作|静态凭据的shared/precommitted witness及承诺；可选step矩阵向量积、小整数表示与纠正位置缓存|创建凭据的Groth16证明和client state，供后续反复show；setup脚本先生成R1CS及参数|Vega评测配置未使用每凭据离线预计算；CIC方法包含FFT卷积核变换等公共/算术预处理，适用成本另看具体算法|
|复用对象|prepared step/core、shared witness及重随机化后的状态；公用密钥和固定形状参数|同一凭据的client state，show/verify可重复；某issuer/proof specification的setup产物|同一参数的公共设置、算法表及实现预处理按各接口复用；每凭据缓存收益数值NOT_REPORTED|
|每次新做|prepared state重随机化、动态witness、step folding、sum-check、ZK mask fold、PCS opening与序列化|新的unlinkable show、按当前展示规格选择披露/范围证明；设备绑定时取得当前challenge对应签名|签名/哈希/解析等所选电路的证明和验证；完整展示执行Alg10对应关系|
|失效/兼容边界|step数量须匹配；活动matvec缓存的step public values变化时拒绝；新凭据需其对应prepared state；新结构/密钥需兼容配置|新凭据需对应client state；setup文档适用域为issuer/proof specification。reveal_digest等配置影响circuit setup；同一支持列表内调整revealed可在show阶段进行|NOT_REPORTED完整缓存失效契约。文中公共算术预计算和每凭据状态的边界不能由“Precompute —”一项替代|
|动态输入变化|论文明确把当前日期、设备签名等列在线输入；仅凭这些输入变化无法推定全部预计算失效|当前时间、可支持的披露选择和presentation_message属于展示流程；具体重建费用NOT_REPORTED|MDOC公开输入含issuer key、属性/值、liveness transcript及时间；具体缓存重建费用NOT_REPORTED|

上述阶段语义分别来自Vega §2/§8及prepare/prove文档、Crescent官方流程、Longfellow方法及§5–6。源码版本与本轮网页快照对应关系见来源清单。[V2–V4、C2–C3、L1定位](sources/LOCATORS.md)

## 3. 同一Vega评测中的完整数字

以下全部为Vega作者Figure10报告的**1920 byte MSO**比较。Vega行属于AUTHOR_REPORTED，Crescent/Longfellow行属于AUTHOR_REMEASURED_BASELINE。硬件为Azure Standard F16as v7，16 vCPUs、64 GB RAM、West US3；设备签名由mock device提供。时间原单位ms，大小原单位kB。[V1-F10表与图页](sources/vega_fig10.png) [V1-EVAL定位](sources/LOCATORS.md)

|方案|线程|Setup ms|Precompute ms|Prove/在线 ms|Verify ms|Proof kB|pk kB|vk kB|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|Crescent|16|106158|25653|182|89|16|710565|1|
|Longfellow|1|5590|—|501|244|325|202|202|
|Vega SC|1|726|351|325|127|91|6588|6587|
|Vega SC|2|660|250|231|79|91|6588|6587|
|Vega SC|4|630|209|187|54|91|6588|6587|
|Vega SC|8|618|165|161|43|91|6588|6587|
|Vega SC|16|606|158|155|40|91|6588|6587|
|Vega MC|1|210|390|237|57|108|464|464|
|Vega MC|2|122|209|159|36|108|464|464|
|Vega MC|4|80|118|105|25|108|464|464|
|Vega MC|8|61|84|92|23|108|464|464|
|Vega MC|16|51|65|92|23|108|464|464|

原表Longfellow的“—”是本评测缺少每凭据预计算阶段。其公共setup仍有5590 ms成本。转录数据另存JSON，便于逐行回查。[原表转录](sources/VEGA_FIGURE10_TRANSCRIPTION.json)

Vega MC的预计算峰值约100 MB、在线峰值约562 MB；原文该段未单列线程数。896-byte凭据的摘要数字为Prove62 ms、Verify17 ms、Proof83 kB，线程条件在该条未单列。Figure10的SC vk为6587 kB，§8.2正文泛称两种key均6588 kB，本表采用图10并记录差异。[V1-MEM、V1-SMALL、V1-SIZE定位](sources/LOCATORS.md)

## 4. Longfellow原论文与官方微基准

### 4.1 完整MDOC展示

CIC论文Table13报告age-over-18的MDOC证明，表题输入界为**MSO at most2231 bytes**，单核单线程。Alg10的witness描述出现2551-byte MSO，两处输入界存在差异，本表保留表13的标签。[L1-MDOC定位](sources/LOCATORS.md)

|硬件标签|Prover ms|Verifier ms|Proof/缓存/峰值内存|
|---|---:|---:|---|
|amd_64|526|252|NOT_REPORTED，针对本表的完整MDOC行|
|cloud|589|286|NOT_REPORTED，同上|
|Pixel9|931|508|NOT_REPORTED，同上|
|iPhone15+|437|229|NOT_REPORTED，同上|
|Mac M4 Air|294|142|NOT_REPORTED，同上|

硬件分别为Ryzen9 7950X、Google Cloud c4-highcpu-8（Xeon Platinum8581C、约3.2GHz、16gb RAM）、TensorG4 Cortex-X4、A16 Bionic、M4 Air。手机实验在性能核运行并间隔执行以减少热节流。论文以SHA256给出128-bit计算参数，Ligero使用rate1/7、132 openings，描述为约110-bit安全。编译器版本、该表重复次数/统计量、完整MDOC峰值内存为NOT_REPORTED。[L1-HW定位](sources/LOCATORS.md)

### 4.2 不同功能的单独记录

|记录|输入/功能|原单位数字|证据与条件|
|---|---|---|---|
|CIC Table11，M4 Air|给定消息摘要/公钥，证明1份ECDSA签名知识|Total ZK20.4 ms，Verifier14.3 ms|AUTHOR_REPORTED，单线程；完整凭据的哈希/解析/有效期另计。Table11另给2/3签名数据。[L1-ECDSA](sources/LOCATORS.md)|
|CIC Table12，M4 Air|183-byte玩具凭据，固定位置属性、设备绑定/时间检查|Prover223 ms|AUTHOR_REPORTED；该表Proof size写为291 **kb**，未擅自改为kB或bits。完整MDOC使用另一电路。[L1-TOY](sources/LOCATORS.md)|
|官方benchmarks，Mac M4|1签名PoK|Prover16713685 ns，CPU16713667 ns，42 iterations；Verifier10365617 ns，CPU10365627 ns，67 iterations|AUTHOR_REPORTED，页面2025-10-17，固定提交7906304；该页具体M4机型和协议V1/V2未单列。[原文Markdown](sources/longfellow_benchmarks.md)|
|同官方页|SHA256原像知识，最多32 blocks|125226342 ns，CPU125226400 ns，5 iterations|AUTHOR_REPORTED；为SHA子功能，额外费用需完整展示关系确定。[官方页面](https://longfellow-zk.github.io/longfellow-zk/docs/benchmarks/)|

## 5. 缓存、初始化、故障与软件信息

|字段|Vega|Crescent|Longfellow|
|---|---|---|---|
|私有缓存大小|NOT_REPORTED；文档列ps_step/ps_core及可选matvec等字段|NOT_REPORTED，FULL_TEXT_UNAVAILABLE；client state含可复用Groth16凭据证明及相关数据|NOT_REPORTED完整每凭据缓存字段/大小|
|峰值内存|MC约100 MB/562 MB，分别预计算/在线；SC NOT_REPORTED|NOT_REPORTED，FULL_TEXT_UNAVAILABLE|本轮所读完整MDOC性能表NOT_REPORTED；机器16gb RAM属于硬件容量|
|安装、编译、密钥分发/加载|NOT_REPORTED独立费用；图10Setup为每circuit配置的key生成阶段|setup README描述R1CS编译/参数生成；完整安装/编译/传输时间NOT_REPORTED；示例OOM日志未作为峰值测量|NOT_REPORTED；图10Setup与原论文不同硬件/功能另列|
|缓存未命中/重建|NOT_REPORTED；文档给拒绝条件，未给重建计时|NOT_REPORTED，FULL_TEXT_UNAVAILABLE|NOT_REPORTED|
|失败与重试|NOT_REPORTED；stale cache和step数量不匹配会拒绝；失败后的state保留/重试时延未明确报告|NOT_REPORTED，FULL_TEXT_UNAVAILABLE|NOT_REPORTED|
|重随机化独立费用|NOT_REPORTED独立计时；属于每次prove管线|NOT_REPORTED独立计时；fresh unlinkable show属于在线阶段|NOT_REPORTED独立费用|
|设备签名费用|Vega比较使用mock device；真实安全元件调用与往返费用NOT_REPORTED|官方demo在软件中生成设备密钥；硬件调用费用NOT_REPORTED|完整关系含设备签名，硬件取签名是否计入各时延需继续对齐|
|软件与版本|Rust、spartan2、bellpepper扩展、RustCrypto、Hyrax；图10对应commit/编译器版本NOT_REPORTED|官方库version1.0；Rust/Cargo，setup文档指定Circom v2.1.6，Circomlib子模块；Vega评测基线commit/编译器NOT_REPORTED|C++；CIC与官方页面为单线程。官方构建依赖CMake/OpenSSL/zstd/clang等；CIC编译器版本及Vega重测commit NOT_REPORTED|
|版本绑定|论文固定PDF＋现有prepare快照＋本轮文档快照，各自哈希|ePrint元数据/README/setup文档；原PDF未取得|CIC正式PDF＋ePrint元数据＋2025固定benchmark文档＋当前README，各自版本分别保存|

source中的README命令和协议阶段用于解释公开接口，所有费用均依其实际来源报告。本轮所得论文数据与现有接口尚有版本关联缺口，比较时使用下一份文稿的条件清单。[可比性分析](COMPARABILITY_ANALYSIS.md)
