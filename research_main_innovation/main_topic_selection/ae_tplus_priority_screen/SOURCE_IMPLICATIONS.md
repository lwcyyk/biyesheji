# T+逐来源蕴含：既有结论与本轮差异

版本 TP-1，2026-11-07。全文来源、哈希与实际范围见sources/SOURCE_MANIFEST.json、READING_LOG.md。原数学状态保持TRANSFER_PROVED_PROJECT_T3_DEPENDENT；本文只作优先权检验。

## 1. 总表

|来源/路径|已有结论|T+本轮新增检验|局部裁决|
|---|---|---|---|
|COL2020 Definition 2 / Theorem 3|最大Hamming半径、逐坐标关系、有序中心；随机PTAS及旧精确组合已核读|R_t=Q[:,Ω_t]直接给A/B模型；偏移d_x不是未知中心选择下的τ_i(p)|MODEL_EXPRESSION_COVERED限A/B；完整C为PARTIAL_OVERLAP|
|COL2020 Partition Center⋆ / IP(6)|给定分簇、每点偏移、关系精确；近似/小精确分支已有费用|已给定行标签时可令d_x=τ_i(p_i)，行标签未定时这个值没有源接口|RESTRICTED_DOMAIN_COVERAGE限固定赋值；一般C桥接MAPPING_UNRESOLVED|
|FS21 Theorem 4 / Lemmas 10–12|总编辑预算、逐坐标关系、代表与超图枚举|Ω在点方向/坐标方向不同；标签禁用在对偶关系可表达，但局部预算和τ=1保留责任|PARTIAL_OVERLAP|
|NF25 / KKM20|完整ILP和M相关精确包络已完成|域计入列型；固定标签后预算为0/1；未知标签的big-M/预算行数仍按输入增长|PARTIAL_OVERLAP；若干承诺域RESTRICTED_DOMAIN_COVERAGE|
|FHS14关联作者修订稿|矩阵划分、列表定义、固定模板split算法、二部障碍|采用修订n^{O(k+ℓ)}有利界；源主算法非列表且没有未知单侧编辑|PARTIAL_OVERLAP；完整包装MAPPING_UNRESOLVED|
|BK2024 v2|完整0/1关系、∅-CSP、确定性结构归约|精确区分⋆/∅；给定掩码可编码，选择未知掩码未付费|MODEL_EXPRESSION_COVERED限固定不确定位置基底；完整T+为PARTIAL_OVERLAP|

没有一行得到一般T+的STANDARD_COROLLARY_COVERAGE或SAME_PARAMETER_FPT_WITH_WEAKER_BOUND。后者必须先有完整同参数算法；仅有固定模板多项式或总预算算法不够。

## 2. COL2020：域已经在原模型内

准确版本：Fomin、Golovach、Panolan、Simonov，Low-Rank Binary Matrix Approximation in Column-Sum Norm，APPROX/RANDOM2020，LIPIcs176，32:1–32:18，DOI10.4230/LIPIcs.APPROX/RANDOM.2020.32；相关遗漏证明复用2019v1。本文定点重读正式pp5、10–14。

### 2.1 A/B模型的完整映射

每个T+行视作源v维点，源k=K₀；每个坐标关系

\[
R_t=\{(Q[p,\ell])_{p\in[K_0]}:\ell\in\Omega_t\}.
\]

Ω全域为A，任意Ω为B。源合法tuple逐坐标保存一个允许原模式preimage，反向恢复η；最大点半径就是最大逐行半径。重复及闲置中心均保持，读取/展开/原K输出为固定多项式。

因此B的逐坐标域模型已经由源Definition 2（32:5）表达。它不是本轮新模型字段。

### 2.2 精确阈值与参数

Theorem 3（32:5）给随机(1+ε)近似，时间v^{O(1)}M^{O((K₀/ε)^4)}，成功概率≥1−2M⁻²。半径1取ε=1/4，成功事件中的整数半径<2，即≤1。完整验收排除错误YES；概率放大仍有失败概率。

所以A/B有作者声明的随机精确阈值保证

\[
t\,v^{O(1)}M^{O(K_0^4)}\operatorname{poly}(N),
\]

并保留既有的代表/残余精确枚举与全部随机矩阵枚举包络。它们的完整旧推导已在ae_t3_p26_coverage/COVERAGE_TEST §§3–7固定，本轮未重复改算。

K₀≤2^w不能使M^{O(K₀⁴)}成为统一固定输入次数。随机性和输入指数责任都保留；较慢上界不构成必要下界。

### 2.3 d_x的实际接口

正式32:11的问题框Partition Center⋆输入已分簇X₁,…,X_k，并为每个点给一个非负整数d_x。32:13 IP(6)约束为

\[
\sum_{t,\rho\in R_t}\chi_i(x[t],\rho)y_{t,\rho}\le d-d_x
\quad(x\in X_i).
\]

d_x按点给定，点已固定属于中心i。它没有同时给所有候选中心一组d_{x,i}。

若T+的行标签f(i)事先给定，排除τ_i(f(i))=2后令d_x=τ_i(f(i))，该固定赋值子问题的预算、关系与恢复双向保持。源Lemma 11仍有大OPT承诺及近似/小分支条件，不能删去。

旧代表精确组合也可有利地使用固定偏移：Lemma 8允许任意给定中心，距离上界≤1；取每非空簇3个代表，额外误差≤1/2。加上已知τ后整数可行半径仍≤1，残余至多3k个坐标、每坐标≤w模式。给定f可得M^{3k}w^{3k}poly(N)的标准组合；未知f若直接枚举要再付K₀^M。

源随机分簇族Lemma 4没有在本轮取得的定义/证明中保证任意点—中心成本矩阵下仍提供合适的固定赋值。把τ_i(p)在分簇前写成d_x会丢失p依赖。MODEL_REDUCTION_AUDIT与下例给具体失败。

### 2.4 将τ替成最小点偏移会误接受

M=1、v=2、w=1、K=2，Q的两行为0/1，A=(00)，域唯一，τ=(2,0)。原问题只能用标签2，距离2而NO；取d_x=minτ=0后，源标签1零距离会接受。

这只否定该偏移替换。若通过列表/辅助坐标另行保持成本，必须补完整归约；MODEL_REDUCTION_AUDIT §3已经完成C→List-B，但普通COL2020输入缺行标签列表。

## 3. FS21：新增字段没有消除总预算缺口

准确版本：MFCS2021，LIPIcs202:14:1–14:14，DOI10.4230/LIPIcs.MFCS.2021.14及arXiv2105.03753v2；Definition 3/Theorem 4、§4证明沿用AF-1实质核读。

两个有利方向：

- 原行作为点，k=K₀、维数v。R_t已经容许Ω域子关系；但点—中心列表/成本不在该源问题框内。
- 原列作为点，k=w、维数M。原行标签是坐标关系项；τ=2禁用可从该行关系删除相应项，这是源逐坐标关系的能力。Ω则成为每个点的中心分配限制；τ=1可以借辅助模式位保留，但辅助点的固定角色与原点列表仍需证明。

Theorem 4用总预算B_total：

\[
(kB_{\rm total})^{O(kB_{\rm total})}2^{kB_{\rm total}}
(\text{点数})^{O(k)}(\text{维数})^2.
\]

形式上取B_total=M、k=w及闲置模式子集包装，仍有

\[
2^w(wM)^{O(wM)}2^{wM}v^{O(w)}M^2,
\]

且只是总预算松弛问题的费用。I_h与(00;11)、R={0}的旧反例已经否定B_total=1/M的直接替换；新成本/域没有修复它。

代表结构用总和最优坐标交换，宿主边为k-tuples、输入指数依k。本轮未新增一条从这些引理到T+固定输入次数的有效桥接。原O(wr)代表替换失败族继续按其范围归档。

FS23期刊版本仍为原SOURCE_UNRESOLVED，当前MFCS/v2结论不代替其未读正文。

## 4. NF25/KKM20：域和混合预算的公平包络

来源与正式定理定位完全复用AF-1：NF25 Theorem 1 / Lemma 12；KKM20 Theorem 1 / Corollary 2。本轮保留旧/新两侧最小包络，不把某个较慢上界当作G必要代价。

### 固定行标签

设f(i)给定，r_i=1−τ_i(f(i))∈{0,1}；r_i<0直接拒绝。类型按(A[:,t],Ω_t)共同分组，数为T_Ω，允许同型分配多个模式：

\[
\sum_{\ell\in\Omega_a}X_{a\ell}=\mu_a,\quad
\sum_{a,\ell}[a_i\ne Q[f(i),\ell]]X_{a\ell}+e_i=r_i.
\]

用一个全1slack块令Σe_i+e₀=Σr_i。a=M、ν=T_Ω+1、Δ=1，回到已证明的精确n-fold结构。若所有r_i=0可直接逐列匹配处理。

未知标签枚举后的完整适用保证为

\[
K_0^M\min\{((T_\Omega+1)M)^{O(M)},2^{O(M^2\log(M+2))}\}\operatorname{poly}(N).
\]

源所需域/角色/输出均保持；M仍为输入量。

### 标签也作为变量

排除τ=2标签，r_{ip}=1−τ_i(p)。每个(i,p)的条件约束可写

\[
D_{ip}(X)+(v-r_{ip})z_{ip}+e_{ip}=v.
\]

每行一个one-hot标签块、每域列型一个计数块，再加slack块，是精确有限表示。全局行数至多MK₀，系数至多max(1,v)，块数T_Ω+M+1；源时间的指数仍有MK₀。它没有给完整w-FPT。

## 5. 保留的强特例与标准处理

- 预先固定K₀：半径1的中心邻域枚举可处理τ和逐坐标R_t，时间[K₀(v+1)+1]^{O(K₀)}poly(N)，见SC-1完整证明。K₀变为输入时恢复真实指数。
- 全部允许标签都只剩零距离（τ∈{1,2}）：不同输入列型≤w，枚举模式到列型/未用标记并检查列表/域，是标准F(w)poly(N)识别；不需PR-C3。
- 所有完整模式候选仍可用w^v显式枚举；小v、固定w或特殊关系族享用各自更强保证。
- 重复模式、成本感知标签合并、域感知类型及原输出恢复对双方同等开放。

这些特例不提供一般正半径、增长K₀/模式库下的必要代价分离。

## 6. 本轮新图来源与版本限制

深读的新工作共两项：

1. FHS的Matrix Partitions of Split Graphs：12页v2及13页作者修订稿；新时间差异采用修订稿。DOI/期刊身份已绑定，VOR正文未读。
2. Barsukov–Kanté，Generalisations of Matrix Partitions: Complexity and Obstructions：21页arXiv v2及其附录，DOI元数据绑定TCS2024；VOR正文未读。

相关定义、定理及实际归约已在MODEL_REDUCTION_AUDIT §§4–7逐项检验。普通保边、固定∅掩码、克隆而局部预算不变等具体路径有明确失败；没有把这些局部失败提升为所有归约不可能。

出版方XML标准视图HTTP200仅为题录；FULL视图HTTP401认证错误。没有API key，也没有绕过访问控制。精读依据是实际取得且关联的公开全文。

## 7. 结论范围

本轮已核读版本/路径没有形成一般T+的已发表同参数FPT或精细界推导。它支持“参数化候选待核”的局部定位；全球优先权和暂停/未读来源风险保留。

如果后续取得真正适用的局部编辑算法，参数若是K₀+w，应先代入K₀≤2^w并写出函数；输入指数依模板时登记XP。调用项目PR-C3/TT-1的组合登记为项目来源。
