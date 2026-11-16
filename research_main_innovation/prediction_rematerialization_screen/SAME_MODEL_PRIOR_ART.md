# 同模型先例：逐项映射与定理裁决

版本：PR-SCREEN-1，2026-11-05。原文、版本哈希、定位及实读范围见[sources/READING_LOG.md](sources/READING_LOG.md)。`SOURCE`表示已读来源结果，`DERIVED`表示本轮映射；检索未命中和目录缺项只作为查找记录。

## 1. 发现与阅读范围

复用DTR、Checkmate、Young和LV2018全文。本轮取得并实读关键模型/定理：Dallot等2024 *Dependency-Aware Online Caching*；Jiang–Panigrahi–Sun的 *Online Algorithms for Weighted Paging with Predictions*（使用2020作者稿）；Bansal等 *Learning-Augmented Weighted Paging*（SODA2022，使用arXiv作者稿）；Antoniadis等2020 *Online metric algorithms with untrusted predictions*；Nordström2013黑pebbling定义；Yu等2017 LRC的依赖与缓存语义。[SOURCE]

ALPS公开目录归档固定提交`286e29d1fcf950cfef04d00404e117f0996412dd`，扫描450条论文记录，用于发现上述加权/metric近邻。目录中的摘要及“没有匹配标题”均未用作完整覆盖证据。公开搜索连接器传输失败；DBLP返回机器人验证页面；Bing有与查询不符的结果、Google未给可读结果。arXiv标题检索和官方目录归档可用。获取限制与查询逐项存入sources。[检索记录]

## 2. 同模型矩阵

|工作|图、大小与费用|请求/执行顺序；峰值规则|预测及误差|一致性/稳健性/资源增广|计算复杂度及可用范围|
|---|---|---|---|---|---|
|M-PRP，本轮规格|已知生成DAG；异质s_v/c_v|外部请求固定顺序；父及新输出同时驻留；祖先之后可逐出|当前输出的next-arrival；η1或ηw|待证；双方B相同|只提出纸面规格|
|DTR，ICLR2021|在线随执行记录依赖；定理用单位time/space线性网络|在线不能重排；Theorem3.2离线对照可重排；运行时pin住正在使用依赖|无预测定理；§7提利用过去batch|Thm3.1：B=Ω(√N)时O(N)计算；Thm3.2有Ω(N/B)差距，比较类不同|现成在线启发式；一般图metadata及递归成本另计|
|Checkmate，MLSys2020|已知静态DAG，M_v/C_v|离线拓扑/阶段规划；T=n，frontier-advancing可行域；模型显式核算allocation峰值|无建议接口|原文离线规划可行域内求解；无PRP稳健界|MILP，§4/§5说明求解限制；算法规划费应计入|
|Dallot等，INFOCOM2024|已知任意DAG；单位item及fetch费|固定外部请求；**始终驻留全部依赖闭包**；每对象依赖数<=k−1|无预测|无bypass：2H_min(k,ℓ)随机竞争，上界对oblivious adversary；有H_min(k,ℓ)下界；同容量|Bucketing维护桶及图关系；仅原文可行域继承保证，复杂度未被本文提升为每请求常数|
|LV2018，ICML|无依赖、单位页/费用|固定外部序列，paging容量k|当前页next-arrival；loss/spread与η1|Predictive Marker的误差相关保证受4H_k约束；同容量|Alg1可直接用于单位原子bundle；一般图恢复费不在原定理中|
|BC2022，SODA|无依赖、单位页，ℓ个生成/加载权重类|固定外部序列，容量k|当前页next-arrival；ηw，另有加权surprise ε|完美预测：确定性ℓ、随机O(logℓ)；错误时有退化至O(k)/O(logk)的组合界；同容量|全局class分配+class内Belady/rank方法；随机算法分析复杂，本文未完整重推|
|JPS2020作者稿|无依赖、单位页、任意正权重|固定外部顺序；deterministic构造/随机oblivious分布分开|PRP；另研究更强SPRP预测整段中间请求|PRP完美时仍Ω(k)/Ω(logk)；SPRP有2竞争算法|§2给下界构造，§4给强信息算法；对手和接口需保留|
|Antoniadis等，ICML2020|metric states，服务成本函数|固定任务顺序；移动距离为对称度量|预测参考离线方法的状态；η=Σdist(p_t,o_t)|Thm1/2给robustification；随机版本接近1+ε并有O(D/ε)加项|需可用的基线及metric；状态数/预测获取费另计|
|Nordström2013，Definition2.10|DAG、单位pebbles；本文只用黑pebbles|父全在场时放置；可任意移除；单sink完成合同|无预测|给经典时间/空间模型；不提供本轮PRP界|经典状态规划基座，非新算法|
|LRC，2017作者稿|计算DAG/数据块；实际Spark缓存|依赖用于生成/计算，不要求永久闭包|未计算子块的reference count，经验策略|实证比较，无本轮误差竞争定理|应用近邻；refcount与真实未来内部调用分别解释|

[SOURCE：各工作所列章节；文献全名与链接见sources/READING_LOG.md。ℓ在Dallot文中为依赖图传递闭包再对称化后的最大独立集大小；在BC2022中为权重类数，二者分开使用。]

关键定理的定量边界进一步固定如下。BC2022 §1.2中，ε为原文的加权surprise：确定性生成/检索费至多`ℓ·OPT+2ℓε`，随机版本为`O(logℓ·OPT+ℓε)`；组合既有最坏情形算法后，Theorems1.3–1.4分别给出`O(min{ℓ+ℓε/OPT,k})`与`O(min{logℓ+ℓε/OPT,logk})`竞争界。log形式按ℓ>=2使用，单权重类回到原文的无权重情形。其成本及误差均属于原paging模型。[SOURCE]

METRIC2020 Theorem1对已有α竞争的确定性基线给出`9·min{α,1+4η/OFF}`；Theorem2在直径D的metric上，对0<ε<=1/4给出随机费用上界`(1+ε)min{α,1+4η/OFF}·OFF+O(D/ε)`。这里的ε为组合算法参数，与BC2022的预测误差符号分别解释。OFF、metric和状态建议缺一不可；本轮未将它们免费替换成外部PRP及一般有向生成费用。[SOURCE/DERIVED]

## 3. 三项可审查的归约/不匹配

### 3.1 M-PRP无边子族与加权paging

令每个可管理节点为一个页，s_v=1、c_v=w_v、B=k，生成该节点只需要固定外部输入，驻留/逐出均为页动作，r_t为页请求。预测正确答案与误差按请求序号完全对应。双方空缓存、同容量、同顺序。于是缺页生成费与paging检索费逐项相同；逆向把页当作可重建原子对象即可。[DERIVED]

允许主动预取不会在这个无边、固定费用、无并行收益的**总生成费**目标中增加最低必需成本优势：可模拟原方法的虚拟驻留，把未被实际请求的预取延迟至首次需要；物理驻留可保持为虚拟驻留的子集，费用延迟支付且不增加。依赖元数据、模拟开销仍属管理费；该归一化只用于生成费边界。[DERIVED]

**继承的必要条件。** JPS2020 Theorem1.1及§2给出完美PRP下的Ω(k)确定性和Ω(logk)随机竞争下界；随机构造使用与算法币独立的分布。其权重可随k扩展。任何声称覆盖所有已知DAG、任意正费用的M-PRP算法，也需覆盖这个无边子族。因此，统一的近1或常数竞争性无法仅由η=0、已知图和相同容量推出。[SOURCE/DERIVED]

量词入口可写成原文的页族：对增长的k，取k+1个单位节点a_0,…,a_k，预算k，费用w_i=c^i（常数c>=2），请求为原文构造的、满足先前PRP答案的合法blocks。确定性构造针对确定算法选序列，随机下界使用oblivious分布；比较方维持同一外部顺序。由此转移的下界允许费用范围随k增长，无法据此断言固定权重范围或单权重类也有相同不可能性。它是既有边界的实例化，未提出新的下界。[SOURCE：JPS2020 §2.1–2.2；DERIVED映射]

BC2022进一步提供以权重类数ℓ参数化的上界：完美预测确定性ℓ、随机O(logℓ)，匹配文献相应量级的下界；ℓ=1恢复Belady情形。其原文错误量ε为class内surprise，而ηw为加权时间误差，两种量须按原定义映射。一般图的状态相关恢复费用无法只用原始c_v充当固定page weight。[SOURCE：BC2022 §1.1–1.2/Theorems1.1–1.4]

该结论排除了“增加依赖前，完美PRP已自然给出任意权重的离线最优”这一出发点。限制权重、增强预测或增加内存均会改变研究条件，需重新建立差异。[DERIVED]

### 3.2 驻留闭包与生成依赖有不同可行域

Dallot等§3.1规定：item存在时，它在G中可达的全部依赖item也必须存在。对一个生成链a→b→z，把依赖方向反过来仍需同时保留a/b/z。M-PRP允许生成b后释放a，再在b和z同时驻留时生成z，峰值2；闭包缓存需要3。[SOURCE/DERIVED]

因此同一对象集、同一预算下直接把生成边反向为缓存依赖边，无法保持可行域。反向也缺少普遍对应：闭包缓存可直接从slow memory读取item，M-PRP没有该固定加载原语。已读论文§1.2自己区分了“只在fetch时需要依赖”的实践模型。[SOURCE：Dallot2024 §1.2、§3.1]

这仅推翻上述直接映射，未构成所有可能编码/归约的不存在证明，更未单独建立新理论。要求本轮方法也保留完整闭包并赋予独立fetch原语时，应直接采用原有dependency caching保证。[DERIVED]

### 3.3 黑pebbling与有限状态规划

Nordström Definition2.10的黑pebble放置要求所有直接父节点在场，移除随时允许；它与单位大小、固定根条件下的生成可行性一致。原文time包含放置与移除，本文C_gen只计带权生成。单sink、空初态、末态仅sink的单位费用特例，移除次数=放置次数−1，故time=2·placements−1；可行性与该仿射成本关系明确，尚未把其单sink结论直接推广为多请求预测定理。[SOURCE/DERIVED]

一般M-PRP的已知有限序列可用状态`(t,S)`表示：合法生成边付c_v，逐出边付0，服务边要求r_(t+1)驻留并增加t。每条边核算生成瞬时内存。原语轨迹与状态路径双向对应，状态数至多(m+1)2^|V|；图构造及规划开销必须付费。该成熟最短路/pebbling表示为小实例的强精确对照，尚无多项式运行保证。[DERIVED，纸面使用]

## 4. 通用metric建议定理的接口检查

Antoniadis等预测的是某个参考OFF的状态o_t，误差是metric distance的和。若采用规范离线最优并固定打破并列的规则，其目标可独立于候选算法，但获取它需要额外信息/计算。外部next-arrival建议无法免费转换为完整OFF状态。[SOURCE/DERIVED：METRIC2020 §1]

此外，重物化状态转移一般非对称。链a→b，大小均1、预算2，生成费α,β>0。令E=空、A={a}、B={b}，允许合法中间状态，则

|最短生成转移|费用|
|---|---:|
|E→A / A→E|α / 0|
|A→B / B→A|β / α|
|E→B / B→E|α+β / 0|

闭环E→A→B→E费用α+β；反向闭环费用2α+β。若存在“同一状态空间上的对称metric距离+端点势差”的精确表示，两方向闭环应有相同费用，因势差在闭环消去，故该直接表示失败。[DERIVED]

该小例限制了把原状态生成费直接填入MTS distance的做法。其他扩展状态编码、近似失真及非metric任务系统方法仍需单独证明；它无法作为“通用方法均不能处理”的下界。原metric定理在满足metric及状态预测接口的profile中应保留全部已有收益。[DERIVED]

## 5. 覆盖裁决与未决的精确范围

|对象|判定|理由|
|---|---|---|
|原子bundle、固定大小与加载费|`REDUCIBLE_TO_KNOWN_MODEL`|Young文件缓存；单位大小带PRP时还可使用BC2022等学习增强方法|
|无依赖、单位大小、任意权重、完美PRP的普遍近最优主张|`DIRECTLY_COVERED`（已有边界）|JPS2020下界及BC2022参数化结果已处理核心信息问题|
|依赖始终同驻留且单位fetch费的profile|`DIRECTLY_COVERED`|Dallot2024对应模型及原文定理条件|
|祖先实际内部next-use作为候选无关真值|`PREDICTION_MODEL_ILL_DEFINED`|其真值随缓存决策变化；已由外部PRP修正|
|一般生成DAG+外部PRP的完整参数化误差界|覆盖范围`UNRESOLVED`；尚未授予`NONTRIVIAL_THEORETICAL_GAP`|上述四类直接映射均有范围；本轮取得来源仍未给出一篇覆盖全部条件的定理，也没有穷尽排除其他模型编码|

“最接近已读定理有条件差别”与“截至当前所有先例均未覆盖”分别登记。当前尚不足以提出新界的原创性声明。即使今后补齐一般DAG的理论空缺，应用接口门仍需独立通过。
