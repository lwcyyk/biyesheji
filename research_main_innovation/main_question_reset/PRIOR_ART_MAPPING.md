# 原文近邻、参数对应与覆盖范围

版本MQ-RESET-2，2026-11-06。复用已取得原文，重新核对与本轮S1/S2及A-E直接相关的定义、定理和预处理。全文取得与指定范围阅读分开记录；本轮未新增论文首次性结论。[完整版本/哈希/定位](sources/READING_LOG.md)

## 1. 最近邻COL2019：受约束二元中心

**准确来源。** Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov，*Low-rank binary matrix approximation in column-sum norm*，2019，arXiv1904.06141v1，18页作者稿。[原文](https://arxiv.org/pdf/1904.06141v1)

实读：摘要、§1三步方法、PDF p4 Definition1、p5正式问题及Theorem2、pp9–11 Lemma4及应用。关键定义页已在上一轮渲染核对；本轮重读提取文本与已保存字节，未独立重证整个随机PTAS。

**原模型与定理。** n_src条长度m_src的二元串；q个有序中心；每个坐标t有允许的q元关系R_t；目标为最大到最近中心的Hamming距离。Theorem2提供`m_src^{O(1)} n_src^{O((q/ε)^4)}`随机PTAS，成功概率至少`1−2n_src^{-2}`。

### 1.1 原M_r的精确对应

令D_g为全部非恒定g位根处置，q=|D_g|=2^g−2。对根j定义q位模式v_j=(δ_j)_{δ∈D_g}，每坐标均取R_t={v_1,…,v_g}。输入串是A的m条行、串长n。

给定f定义中心c_δ[t]=δ_{f(t)}；反向由每个坐标的允许模式唯一恢复f(t)。半径等于`max_i min_δ Σ_t[A_it≠δ_{f(t)}]`。不同v_j可由δ=e_j区分。关系表显式成本O(ng2^g)，共享表示同给基线。

允许有序中心重复/未使用、付费空根和语义恒定中心；禁止的是恒定根处置。加强“每根/每中心非空”会改变问题。该模型/目标的表达性已经被成熟框架覆盖。

### 1.2 效率及见证差别

Theorem2的输入串数/长度在本轮记号中分别为m/n。将ε取为1/[2(r+1)]可在成功事件中做整数精确阈值判断，但m的指数随q,r变化；该直接代入尚未给A-E的输入多项式指数常数。

Lemma4按q个数据簇分别取s个代表，例外坐标界为s q OPT；A-E继承的小见证按g个根profile分离，用≤g−1行、≤r(g−1)例外任务，但未知见证定位仍待解。存在性工具与候选算法效率分别判断。

## 2. 最近邻CAT2021：总预算聚类与重复列

**准确来源。** Fedor V. Fomin、Petr A. Golovach、Nidhi Purohit，*Parameterized Complexity of Categorical Clustering with Size Constraints*，2021，arXiv2104.07974v1，32页作者稿；首页注明初版获WADS2021接收。[原文](https://arxiv.org/pdf/2104.07974v1)

实读：摘要、§1特别是PDF p3的重复列/initial clusters讨论、p2 Theorem1、§2定义/Observation1、p9 Observation2–3、pp10–11 Lemma3、Lemma4候选中心列表及方法概述。§3.2全部DP及概率/枚举细节没有在本轮重新独立核验。

**原结果。** 对总Hamming费用B及字母表Σ，Capacitated Clustering在`2^{O(B log B)}|Σ|^B(mn)^{O(1)}`可解。Observation2通过B+1个不匹配列否定低总成本；Lemma3处理容量约束下重复列拆分的结构。

**精确差别。** 本轮是逐行r，总代价可随需求数m增长；代B=mr把m带入参数函数。原文无容量总和模型中同类可并的交换论证，不能直接用于每行预算：本轮10/01各3份、00两份的g=2/r=1实例必须拆分00。原文已有“重复对象可能因约束而拆分”的明确认识，故该现象/名称本身不承担原创。

**共同工具。** S0的超过预算强制相等、S1的饱和及S2的边界使用标准鸽巢/预算工具，并继承R3既有重数引理。本轮没有把这些重新列成独立新算法。

## 3. 一般关系palette已经允许同样饱和

为避免给专用方法保留额外结构，考虑COL2019的一般实例：若一组坐标在所有输入串上的位型相同，且允许关系R也相同、|R|=L，则固定半径r时保留Lr+1个坐标即可，前提仍为单位Hamming且无跨坐标约束。

给任何缩减实例的可行有序中心及每条输入串选定的覆盖中心。在Lr+1个保留坐标中，一个允许tuple至少使用r+1次。若某条输入串在其覆盖中心上的该tuple位与组的输入位不同，它会有至少r+1个错配，矛盾。故用这个tuple恢复全部删去坐标时，全部输入串对其既定覆盖中心增加0误差，关系也满足。正向删坐标只减误差。这是与S1相同的通用预算/饱和论证。[DERIVED_GENERIC_TOOL]

A中L=g，所以该通用方法直接享有gr+1预处理。由此排除“只有凭据专用方法才能发现重数阈值”的效率解释。该段给出自含证明，未将它冒充COL2019已经陈述的引理。若后续原文已给相同结论，须引用并调整归属。

## 4. 其他近邻与范围检查

|原文、版本及实读|准确使用|与A-E的关系|
|---|---|---|
|Jiehua Chen、Danny Hermelin、Manuel Sorge，*On Computing Centroids According to the p-Norms of Hamming Distance Vectors*，1807.06469v3，2019-06-28，21页；摘要、pp1–4。[原文](https://arxiv.org/pdf/1807.06469v3)|p=∞为Closest String及已知NP-hard基础|两根用公共锚消去补方向可归约该标准问题；有限p下界不转写成r下界|
|Farehe Soheil、Kirill Simonov、Tobias Friedrich，*Binary k-Center with Missing Entries: Structure Leads to Tractability*，2503.01445，PDF日期2025-03-04，28页；pp1–5、§2 Definition2.1与mask定义。[原文](https://arxiv.org/pdf/2503.01445)|Theorems1.1–1.3按known-entry图vc/fr/tw及相关参数给FPT/XP|完全已知I_N的图为K_N,N，g+r固定仍可宽度无界；其无约束中心也不强制R_g。已读定理没有经这些参数直接给A-E|
|RFC7009，*OAuth 2.0 Token Revocation*，Torsten Lodderstedt、Stefanie Dronia、Marius Scurtescu，2013-08，Standards Track；§1、§2–2.2。[官方](https://www.rfc-editor.org/rfc/rfc7009)|请求对token及相关grant/材料的处置由契约决定|支持原生停止语义与影响范围需要识别；规范没有在该接口内提供M_r任务原子重绑合同|

## 5. 强方法、可表达性与同条件效率

1. **解质量。** 通用绑定枚举与受约束中心能得到相同最优g；这可承担正确性核验。
2. **计算资源。** 比较G†组合中的最快适用分支；它共用palette、S1饱和、对称性、g=2算法和相同缓存。SAT/ILP可表达，不等于已有目标参数界；G-rel的双指数形式上界也不构成必要下界。
3. **接口/信任。** 两方若研究M_r，均被赋予相同原子迁移公理；若部署原生接口，均须承担目标资格、身份隔离、旧支持退役及并发证明。当前B静态目录与M_r没有被无证据合并。

## 6. 优先权与后续工作状态

本轮新增检索只对准逐行误差、受约束中心和重复坐标参数。公开搜索连接器返回传输错误，原始响应保存于MQ2_SEARCH_RESULT.json。上一轮arXiv后续请求的429/超时记录按原样复用，本轮没有继续该限额服务请求。

这次已取得并核读的近邻尚未经直接代入给A-E；完整后续查新仍未封口。因此本轮可登记精确证明工作对象，首次性、最优性和已确认开放状态均待审。S1/S2按初等推论归档；它们不弥补A-E的未证步骤。
