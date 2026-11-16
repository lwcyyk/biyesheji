# r5 一般定理优先权核验

核验日期为2026-11-04，时区Asia/Shanghai。本报告采用academic-research-suite的原文核对与命题映射流程。查新对象为r5的GENERAL_THEOREM.md，连同其引用的GLOBAL_EXTREMA.md。作者自己的证明、实验通过状态及完成声明均按待审材料处理。

## 1. 当前判定

| 主张 | 战役判定 | 本轮依据与处置 |
|---|---|---|
| S1 双行掩码最优模拟误差闭式 | **存疑** | 已读原文提供随机矩阵不变性与相邻隐私界。r5中具体minimax目标、硬无抹除约束、割线覆盖量及匹配对偶的直接先例仍待完整检索 |
| S2 最优核边缘分布唯一性 | **存疑** | 轨道内均匀化已有来源。跨全部基的唯一核权重、最优秩2及严格互补条件的优先权仍待核对 |
| S3 同一U₍₃,ₙ₎不同表示的严格误差分离 | **存疑** | 同一拟阵具有不同表示已见Oxley的具体实例。r5新增的δ*差值与T单调性继续作为单独查新对象 |
| S4 全局极值族 | **存疑，几何子项已有覆盖** | 偶阶Q+2弧的存在性已被书籍中的明确结论覆盖。T=0的特定存在性参数、给定二次曲线参数化及隐私全局端点的原始来源映射仍待补全 |
| S5 低故障完美隐私与三故障最坏性 | **覆盖，按直接推论降级** | 本报告给出从IK00的矩阵随机化不变性及统计距离后处理性质到S5的完整代入。三故障对应的具体数值仍归S1审查 |

**强独立原创性建议口径为暂缓确认。** 当前可报告限定模型的理论候选及本报告已经定位的先例。外部数据库检索和前向引文集合仍处于待完成状态。

本轮交付属于访问受阻条件下的优先权判定报告。S1—S4的“存疑”记录了尚待完成的核验项目。S5的降级依据来自实际阅读的原文及可检查推导。

## 2. 判定口径

“覆盖”用于原文直接陈述目标结论，或能够写出完整变量代入和直接推导的情形。报告另记覆盖的具体子项。

“未发现覆盖”要求同时报告实际完成的检索域、关键词和引文集合。它始终是带检索边界的结论。

“存疑”用于全文、版本、引文集合或命题映射仍有关键缺口的情形。摘要与书目级记录仅用于排队获取原文。

本轮对外部检索取得的有效结果数为0，因此S1—S4采用“存疑”。五份本地原文的核对结论在下文逐条登记。

## 3. 固定待查主张

共同模型采用F=GF(q)、n≥5、q≥16n²、V∈F^{3×n}任意三列独立、全部|S|≤3支持、任意独立非零幅值、输入独立M∈F^{2×3}及所有Mvᵢ以概率1非零。观察为Y_S(a)=MV_Sdiag(a)，误差为max_S inf_QS max_a TV(Law(Y_S(a)),Q_S)。

| 子项 | 精确内容 | 需要匹配的要素 |
|---|---|---|
| S1a | 全体合法掩码分布上的minimax闭式 | 任意幅值、同一P服务全部支持、秩混合、硬无抹除、TV模拟半径 |
| S1b | 割线并集高密度和其余点低密度达到界 | 分布本身及匹配下界，两者同时成立 |
| S2a | 最优掩码以概率1秩2 | 覆盖允许秩1/2混合的可行域 |
| S2b | 核边缘分布唯一 | 逐点核概率唯一，frame条件分布另行登记 |
| S3a | 同一列拟阵具有不同表示 | 区分带标签表示、射影等价和允许的列重标记 |
| S3b | 同域、同支持族、同模型的δ*严格不同 | 指定两个表示及精确差值 |
| S3c | δ*随T严格增加 | 固定n,q，T=Σ_K C(r_K−1,2) |
| S4a | q大于明确阈值时T=0存在 | 次数界、坏事件数、域特征及q阈值 |
| S4b | n=Q+2的偶阶构造达到T上界 | 实际弧、割线外点指数及域嵌入 |
| S4c | 同一域上的全局最佳/最差δ* | 将几何端点与S1、S3关联 |
| S5a | 规范均匀frame构造对|S|≤2完美隐藏幅值 | 条件rank分布、非零列和幅值缩放不变性 |
| S5b | 最坏值可在|S|=3达到 | 所有小支持可扩充成允许基，TV投影性质 |

U、N、O、D、Z依r5定义。待查闭式为δ*=(n−3)D/[(q−1)Z]。这项登记用于冻结查新对象，数学正确性审稿另行进行。

## 4. 原文来源登记与变量映射

### P01 Ishai–Kushilevitz 2000

Yuval Ishai、Eyal Kushilevitz，*Randomizing Polynomials: A New Representation with Applications to Round-Efficient Secure Computation*，FOCS 2000，印刷页294–304。本地文件为会议Extended Abstract版，共11页。DOI和会议年份已从PDF元数据及首页核对。全文逐页读完，印刷页298–299另作图像核对。一般域Theorem5.8在此版本采用证明草图，Lemma A.1的证明在该版本省略。原文入口为[DOI](https://doi.org/10.1109/SFCS.2000.892118)。

| 阅读位置 | 原文结论 | 与r5的对应 | 判定用途 |
|---|---|---|---|
| §2，印刷296页 | 统计距离的半L1及区分优势定义 | SD对应TV | S5b投影推论 |
| Definition2.1，296页 | 输出分布只依赖函数值的随机多项式定义 | f(x)可取支持功能作概念映射，r对应随机种子 | 定义层背景 |
| Example2.4，297页 | 随机线性组合隐藏非零输入的具体幅值 | 非零残差与均匀乘法/线性随机化 | S5a的背景 |
| Lemma3.3及证明，298–299页 | 同秩矩阵经独立均匀双边矩阵随机化后同分布 | 原文矩阵M对应待隐藏线性对象，R₁/R₂对应随机基变换。r5的M则是掩码，两者角色分别记录 | S5a的群不变性依据 |
| Lemma3.4、Theorem3.5，299页 | 不同秩可区分及degree-3随机化构造 | 涉及正确性和多项式次数 | S1候选映射需补充全部模型条件 |
| §4、Theorem4.1、附录，299–300及303–304页 | 保密随机种子与组合模拟 | r5实际协议的随机量与完整视图要求 | 协议基线与作用域 |
| §5及Theorem5.7/5.8，300–304页 | degree-2随机多项式的表达能力限制 | r5允许任意相关掩码分布，其采样器次数另需定义 | S1/S2待核对的模型差异 |

原文随机输入在有限域上均匀，主要研究函数随机化的多项式次数与通信轮次。r5的目标是带无抹除约束的矩阵分布minimax问题。把r5代入其次数下界还需要给出采样器的多项式表示。当前可落地的直接推论是第5节所述S5。

### P02 Giorgi等 2026期刊版

Pascal Giorgi、Fabien Laguillaumie、Lucas Ottow、Damien Vergnaud，*Constant-Round Secure Distributed Decoding and HQC Threshold Decryption*，IACR Communications in Cryptology 3(3)，2026，43页。使用用户提供的期刊PDF。与ePrint2026/946分别登记版本。入口为[期刊DOI](https://doi.org/10.62056/ay4fvu7sf)和[ePrint记录](https://eprint.iacr.org/2026/946)。

| 本轮重读位置 | 原文内容 | 变量对应 | 本轮用途 |
|---|---|---|---|
| §2.2，图1，6–7页 | ABB、秘密随机量、内积原语及通信计费 | [x]对应共享残差，原语对应实现底座 | 固定通用基线能力 |
| §2.3，表1及7–9页 | GenInv、ZeroTest、MatInv和TraceMul | 均匀非零因子、零判断、矩阵盲化 | 既有实现支撑 |
| §4.2，图5、Protocol8、Theorem3，20、22页 | 共享Padé，隐藏所选系统及可解性 | f对应syndrome，(r,t)对应求解结果 | 共享求解先例 |
| §6.2，图8、Protocol14、Theorem7，32–33页 | 秘密错误定位、错误幅值恢复及域检查 | e对应残差，错误位置集合对应S，σ对应定位多项式 | 强参考功能 |
| §7.2，表4–6，36–37页 | 成本估算及依赖分享底座的口径 | 安全乘法/内积成本对应协议资源 | 同底座成本核对 |
| References，38–43页 | 55条参考文献 | 后向引用分母55 | 完整书目登记，见附录A |

该文以共享结果和其ABB理想功能为目标。r5的公开带标签幅值观察、2×3掩码优化和δ*闭式仍需要独立变量归约。图8还明确允许非法子域输入泄漏yᵢ^{q′}−yᵢ并中止。公平比较需统一该输入域与泄漏契约。当前这些具体协议结论可以作为基线，S1—S4的优先权继续保持存疑。

### P03 Oxley 2011

James Oxley，*Matroid Theory*，第二版，2011，ISBN9780198566946。本地PDF为722页。已核对版次和源文件哈希，阅读§6.3印刷176–178页及§6.5印刷201–202页。读取的公开版本来自[书籍PDF](https://www.math.ens.psl.eu/~benoist/refs/Oxley.pdf)。

| 阅读位置 | 已有结论 | 变量对应 | 子项处置 |
|---|---|---|---|
| §6.3，6.3.1–6.3.7及Proposition6.3.12 | 行变换、列缩放、标签及域自同构下的表示等价 | 书中A对应V，X对应公开行变换，Y对应列缩放 | 等价表示规范化归入背景 |
| Example6.3.9，177页 | U₍₃,₅₎在GF5的多种带标签非等价表示 | 两个A对应同一列拟阵的两个V | S3a已有覆盖 |
| Problem6.5.19和Table6.1，201页 | n弧、U₍r,n₎可表示性和MDS码的对应，r=3且Q偶时可达Q+2点 | r=3，书中q取r5子域Q，n=Q+2 | S4b的弧存在性已有覆盖 |

Example6.3.9处理表示等价性，r5的误差函数尚需另行映射。Table6.1明确给出Q+2弧的既有存在性，并追溯Bose1947、Bush1952、Segre1955等结果。r5中具体二次曲线参数化的原始出处仍列入PI补取队列。

### P04 低秩加性掩码的相邻理论

Alejandro Cohen、Rafael G. L. D’Oliveira、Alex Sprintson，*Low-Rank Masking for Single-Server Matrix Multiplication*，arXiv:2609.18876v1，2026-09-16。本轮读取此前保存的原始HTML，复核§2.1–2.5、Theorem3–5及§3证明。来源入口为[arXiv全文](https://arxiv.org/html/2609.18876v1)。

| 原文变量/条件 | r5变量/条件 | 归约状态 |
|---|---|---|
| A+K的加性掩码 | MV_Sdiag(a)的乘法观察 | 需给出保持函数、观察与约束的变换 |
| 多个结果使用均匀消息A | 对所有非零幅值取最坏值 | 输入量词待匹配 |
| maximal correlation及其上下界 | 到共同模拟器的最坏TV | 指标转换及紧性待建立 |
| rank(K)约束 | M的行数及Mvᵢ硬非零约束 | 可行域待对应 |

这份全文明确说明低秩掩码的统计隐私已有成熟的上下界问题。其已读命题与r5之间的完整归约尚待建立，因此保留为S1/S2的重要相邻来源。

### P05 稀疏插值中的零点界和特征边界

Zhiwei Hao、Erich L. Kaltofen、Lihong Zhi，*Numerical Sparsity Determination and Early Termination*，ISSAC2016，DOI10.1145/2930889.2930924。读取本地8页原文的§4.1，印刷252–253页，特别是式(31)–(36)及Theorem4.1。来源为[DOI](https://doi.org/10.1145/2930889.2930924)。

该段对非零行列式多项式应用DeMillo–Lipton/Schwartz–Zippel零点界，并讨论特征2下非零性前提。对应r5 S4a时，变量应替换为仿射点坐标，坏事件多项式应分别证明非零，再按次数2和4进行联合界。方法层已有直接先例。r5的特定坏事件集合和常数R_n仍按具体代入记录，原始零点界论文及有限几何近邻待补取。

### H类历史来源线索

以下记录保留前轮阅读位置。本轮的在线复取失败，它们的引文集合尚待完整核验。

| 编号 | 来源 | 历史读取位置 | r5映射 | 当前状态 |
|---|---|---|---|---|
| H01 | Boneh等，Arithmetic Sketching，CRYPTO2023，DOI10.1007/978-3-031-38557-5_6 | Definition17、Construction21、Theorem22、Corollary23及参考[33]/[34] | 语言成员资格、Hankel随机化，对应稀疏gate及秩盲化背景 | 全部参考与被引集合待完成 |
| H02 | Orbanz，Global optimality under amenable symmetry constraints，2024，arXiv:2402.07613v2 | §1式(1)–(2)及有限群平均 | 概率分布Q、凸风险和幅值群对应模拟器对称化 | 具体r5极值归约待补充 |
| H03 | Byrne等，A q-Polymatroid Framework for Information Leakage in Secure Linear Network Coding，2026，arXiv:2601.07567v1 | 定理14、命题17、定理18等 | 嵌套码、子空间条件rank和熵对应拟阵/泄漏近邻 | matroid-port及其引用链待完成 |
| H04 | Boyle/Gilboa/Ishai，Function Secret Sharing: Improvements and Extensions，CCS2016，DOI10.1145/2976749.2978429 | 旧报告登记完整版本Claim4.5 | 线性草图核验对应通用基线 | 本轮原文复取待完成 |

## 5. S5的可检查降级推导

### S5a 低故障幅值隐私

取r5规范构造的两个位置i,j。它们的割线上有q−1个合法核点，各点概率为h。因此两列观察的rank为1的概率是(q−1)h，与幅值无关。

条件于rank为2，均匀GL₂ frame使观察在GL₂(F)上均匀。条件于rank为1，割线上均匀的核方向给出均匀非零列比，均匀frame给出均匀非零二维向量。故该条件分布可写为(y,cy)，其中y均匀于F²\{0}，c独立均匀于F*。

两类分布都对任意非零列缩放保持不变。单点观察同样均匀于F²\{0}。这个代入只用“该割线各核点等概率”和均匀frame，h的最优闭式与对偶下界均可留待S1审查。

IK00 Lemma3.3及其证明明确使用可逆矩阵乘法保持均匀分布、同秩对象经可逆变换相连的事实。以上是该不变性论证在r5条件分布中的直接应用。覆盖类型登记为“直接推论”，原文与r5采用的矩阵形状及随机量角色已在P01表中区分。

### S5b 三故障最坏性

对任意小支持S，选包含它的三列基B。把B观察投影到S，就得到S观察。对任意Q_B，πQ_B是一个可用的S模拟器。由统计距离的事件定义，TV(πP,πQ)≤TV(P,Q)。取各自的最坏幅值与最优模拟器后，δ_S≤δ_B。

因此max_{|S|≤3}δ_S=max_{|S|=3}δ_S。这一步适用于允许支持可扩成基的模型，数值δ*继续归S1处理。IK00印刷296页给出的统计距离区分优势定义直接支持该后处理推论。

### 降级记录

| 编号 | 降级子主张 | 原因 | 建议位置 |
|---|---|---|---|
| D5a | 将至多两故障完美隐私作为独立原创机制 | 均匀矩阵轨道的直接条件分布推论 | 构造正确性引理 |
| D5b | 将三故障达到最坏作为独立原创定理 | 基扩充及TV投影性质直接给出 | 证明中的归约步骤 |
| D3a | 将同一拟阵存在不同表示作为创新 | Oxley §6.3已有明确实例 | 研究背景 |
| D4b | 将偶阶Q+2弧的存在性作为创新 | Oxley Table6.1明确覆盖并指向更早文献 | 有限几何背景 |

S5整体按以上推论性降级。S3的δ*严格差异和S4的隐私全局极值仍保持单独的“存疑”判定。

### S4几何子项的直接代入

将Oxley Table6.1中的r取3、q取偶数子域大小Q，可得一个Q+2点弧。通过任意弧点有Q+1条直线，其余Q+1个弧点各占一条，故每条经过弧点的直线还包含第二个弧点。每个外点因此落在(Q+2)/2条割线上。

代入r5采用的r_K上界及双计数等式，可推出这类弧达到相应几何T上界。因此“存在达到几何端点的偶阶弧族”按已有可表示性结果的直接推论登记。具体正规二次曲线参数化的原始出处及其后续应用仍列入补取清单。S4中的隐私端点数值继续依赖S1、S3。

## 6. 分离优先门的查新评估

当前r5已有一项限定模型内的比较。输入族为q≥16n²的3×n弧字典及全部至多三故障。指标为同一双行无抹除观察类的模拟误差。对照为均匀合法核，预测差距为r5第9节给出的正分数。

“当前最强通用方法”这一字段仍待确定。可核对的通用基线集合至少包含逐项私密零判断、独立非零乘法掩码、完整共享解码以及已有完美隐私方案。

例如，独立均匀rᵢ∈F*并公开zᵢ=rᵢdᵢ，会精确显示支持，且非零zᵢ独立均匀，从而得到幅值模拟误差0。其安全计算、随机量生成、通信和预算成本需要一起计量。r5的行数限制和观察结构为另一项明确约束，现有材料尚待建立统一约束下通用方法必付更高代价的具体输入实例。

**实现门状态为待满足。** 下一份分离声明应固定一个实际输入实例、一个成本指标、最强适用通用对照及严格差距，并允许对照使用同样的服务接口、随机量、批准及预处理。当前阶段的交付为文献核对与命题映射。

## 7. 检索分母和访问台账

### 实际完成与尚待完成的数量

| 项目 | 本轮分母与完成量 |
|---|---|
| 外部搜索工具请求 | 1次批请求含3个关键词组合，返回transport错误，有效结果0 |
| arXiv浏览器检索 | 1个检索URL已建立标签，正文读取0次成功，结果条目数待取得 |
| 成功完成的外部数据库检索 | 0个 |
| 本地直接核读的原始文献 | 5份，其中IK00完整通读，其余按上列章节阅读 |
| Giorgi期刊版后向书目 | 55/55条已登记，所引原文的本轮正文获取0/55 |
| IK00后向书目 | 36条均已查看书目页，所引原文的后续闭包待完成 |
| Arithmetic Sketching后向集合 | 版本固定与完整清单待取得，集合基数待本轮核对 |
| 三个种子文献的前向被引集合 | 集合基数待建立，本轮取回记录0条 |

书目条目数与已读原文数分别计算。旧报告及r5自身材料属于研究对象，未计入五份外部文献。

### 访问事件

| 事件 | 路径或请求 | 结果 |
|---|---|---|
| A01 | 文献工具批检索“optimal simulation error” masking statistical distance | 提交后transport失败，搜索引擎执行状态未知 |
| A02 | 同批“Arithmetic Sketching” Boneh 2023 | 同上 |
| A03 | 同批“matroid port” entropy secret sharing | 同上 |
| B01 | Edge独立标签访问arXiv的Arithmetic Sketching精确题名检索 | 创建调用超时。随后标签清单确认URL和页面题名 |
| B02 | 绑定上述标签并读取正文 | 超时，正文未返回 |
| B03 | 通过Edge窗口读取 | Computer Use因无法可靠确认Windows当前浏览器URL而停止 |
| L01 | 本地IK00 PDF | 11页完整阅读，PDF结构预检通过，298–299页图像核对 |
| L02 | 本地Giorgi2026 PDF | 指定协议、成本段落和全部55条书目核对 |
| L03 | 本地Oxley PDF | 哈希与既有结构预检对应，读取指定章节 |
| L04 | 保存的arXiv2609.18876v1 HTML | 读取§2与§3相应正文 |
| L05 | 本地HKZ16 PDF | 读取§4.1的零点界应用与特征条件 |

B01实际URL为[arXiv检索页](https://arxiv.org/search/?query=%22Arithmetic+Sketching%22&searchtype=all)。浏览器控制结束后，本轮继续进行本地原文核对。该事件属于工具执行边界，网页内容没有给出查新结果。

### 待执行的标准化检索矩阵

| 编号 | 关键词组合 | 目标库或入口 | 当前状态 |
|---|---|---|---|
| Q01 | “optimal simulation error” “masking” “statistical distance” | 聚合搜索、arXiv、ePrint | A01失败，库内检索待完成 |
| Q02 | “statistical distance” “secret sharing” “masking” | arXiv、ePrint、Scholar | 待执行 |
| Q03 | “private sparse recovery lower bound” | arXiv、ePrint、HAL | 待执行 |
| Q04 | “sketch privacy” “statistical” | arXiv、ePrint、DBLP | 待执行 |
| Q05 | “matroid port” “entropy” | arXiv、出版社、作者主页 | A03失败，库内检索待完成 |
| Q06 | “ideal secret sharing matroid” | arXiv、HAL、出版社 | 待执行 |
| Q07 | “projective arc” “finite geometry” “leakage” | arXiv、HAL、作者主页 | 待执行 |
| Q08 | “secant” “finite geometry” “privacy” | 同上 | 待执行 |
| Q09 | “oblivious linear algebra” “matrix blinding” | ePrint、出版社、作者主页 | 待执行 |
| Q10 | “matrix blinding” “leaks only rank” | 同上 | 待执行 |
| Q11 | “Arithmetic Sketching” | arXiv、ePrint、出版社 | A02/B01–B03受阻 |
| Q12 | “Randomizing Polynomials” “statistical randomized encodings” | 作者主页、ECCC、ePrint | 种子原文已读，后续链待完成 |
| Q13 | “Constant-Round Secure Distributed Decoding and HQC Threshold Decryption” | ePrint、CiC、作者主页 | 种子期刊版已读，被引待完成 |
| Q14 | “fractional triangle decomposition” “complete graph” “edge weights” | arXiv、HAL、出版社 | 待执行 |
| Q15 | “inclusion matrix” “edges” “triangles” “inverse” | 同上 | 待执行 |

Q14–Q15对应r5第4节的显式右逆。它们补充用户指定的近邻领域，以便检查S1对偶权重是否属于已有定理的直接代入。

## 8. 引文闭包状态

| 种子 | 后向引用 | 前向被引 | 版本边界 |
|---|---|---|---|
| Arithmetic Sketching | H01保留了部分原文位置与[33]/[34]线索。完整清单待固定PDF后核对 | 待从指定索引导出并去重 | CRYPTO2023版、作者52页稿及后续修订需分开 |
| IK00 | 本地FOCS版36条书目已查看 | 2002后续、统计/计算随机编码及后来的引用集合待完成 | 2000会议Extended Abstract已固定 |
| Giorgi2026 | 期刊版55条书目全部列于附录A | 待从ePrint/CiC及引文索引核对 | ePrint2026/946与CiC期刊版分别登记 |

前向集合需明确截至2026-11-04、所用数据库及去重规则。当前有效返回集合待建立，报告未将取回数量0解释成被引数量0。

## 9. 给PI的具体获取清单

以下URL是明确的获取入口。状态“待人工获取”表示本轮页面或正文尚待取得。

| 优先级 | 需要的材料 | URL | 目的 |
|---|---|---|---|
| P0 | Arithmetic Sketching全文及完整参考表 | https://eprint.iacr.org/2023/1012.pdf | 固定版本、补齐后向集合 |
| P0 | 同文作者稿 | https://ntt-research.com/wp-content/uploads/2023/08/Arithmetic-Sketching.pdf | 与会议版本核对 |
| P0 | 同文出版记录 | https://doi.org/10.1007/978-3-031-38557-5_6 | 版本及被引入口 |
| P0 | Arithmetic Sketching被引索引 | https://scholar.google.com/scholar?q=%22Arithmetic+Sketching%22 | 导出索引返回的被引记录 |
| P0 | IK00被引索引 | https://scholar.google.com/scholar?q=%22Randomizing+Polynomials%22+Ishai+Kushilevitz | 建立2000年后续闭包 |
| P0 | Giorgi2026被引索引 | https://scholar.google.com/scholar?q=%22Constant-Round+Secure+Distributed+Decoding%22 | 建立前向集合 |
| P0 | q-polymatroid与秘密共享近邻全文 | https://arxiv.org/html/2601.07567v1 | 核对定理14/17/18及matroid-port原始引用 |
| P0 | Secret-sharing matroid专题检索 | https://arxiv.org/search/?query=ideal+secret+sharing+matroid&searchtype=all | 最近邻理论域 |
| P0 | Matroid port专题检索 | https://hal.science/search/index/?q=%22matroid%20port%22 | 补齐HAL及作者稿 |
| P1 | Communication Efficient Secure Linear Algebra | https://iacr.org/archive/tcc2006/38760526/38760526.pdf | 核对隐藏行空间/rank及其模拟性质 |
| P1 | Secure Distributed Linear Algebra in a Constant Number of Rounds | https://doi.org/10.1007/3-540-44647-8_7 | 早期通用线性代数基线 |
| P1 | Secure Multi-Party Linear Algebra with Perfect Correctness | https://cic.iacr.org/p/1/1/29/pdf | 完美正确性及随机矩阵机制 |
| P1 | Perfect Constant-Round Secure Computation via Perfect Randomizing Polynomials | https://www.cs.columbia.edu/~tal/6261/SP20/reading/IKicalp02.pdf | IK00后续链 |
| P1 | Statistical Zero-Knowledge与Randomized Encodings关系 | https://eccc.weizmann.ac.il/report/2015/186/ | 统计随机编码框架及后续引用 |
| P1 | FSS扩展稿 | https://eprint.iacr.org/2018/707.pdf | Arithmetic Sketching更早的草图基线 |
| P1 | Fast Secure Computations on Shared Polynomials and Applications to Private Set Operations | https://doi.org/10.4230/LIPIcs.ITC.2024.11 | Giorgi后向关键子协议 |
| P1 | Secure Matrix Invertibility Testing over Fields of Small Order or Characteristics | https://eprint.iacr.org/2026/514 | 同底座随机量及可逆性检查 |
| P1 | Giorgi作者出版目录 | https://www.lirmm.fr/lucas-ottow/ | 版本与后续工作 |
| P1 | Complete arcs检索入口 | https://hal.science/search/index/?q=%22Complete%20arcs%22 | Hirschfeld1997及有限几何引用链 |
| P1 | 分数三角形分解检索入口 | https://arxiv.org/search/?query=fractional+triangle+decomposition&searchtype=all | S1显式权重的代数先例 |

Oxley书目已经核对到Hirschfeld，*Complete arcs*，Discrete Mathematics174，177–184，1997，以及Bose，*Mathematical theory of the symmetrical factorial design*，Sankhyā8，107–166，1947。校园馆藏检索可按这些字段定位。具体原始定理与r5的映射仍待取得全文后完成。

Ishai–Kushilevitz 2000及Giorgi2026期刊正文已在本地取得，PI获取工作的重点转向其后续链和其余缺口。作者联系由PI自行安排。

## 10. 建议口径与待交接事项

建议把S1—S3保留为主要理论查新对象，把S4拆成几何背景与依赖S1/S3的应用推论，把S5放入构造性质及归约引理。

可使用的当前表述为“在限定双行线性观察模型中给出精确极值与表示敏感性的研究候选。已定位若干既有随机化和有限几何成分，核心主张的优先权正在逐命题核验”。强独立原创性确认待完整检索、最近邻命题归约和分离优先门完成后再评估。

PI回传材料应包含PDF版本、来源URL、引文导出时间及数据库名称。后续核验按本报告的S1—S5编号续接，并将每个新来源的读取位置、变量映射和具体覆盖子项填入台账。

## 11. 文件绑定和工作范围

| 文件 | SHA-256 |
|---|---|
| [r5 GENERAL_THEOREM.md](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/general_arc_2026-11-03_r5/GENERAL_THEOREM.md) | 565c8f4e3a52a992506060579c9869ea93741bd8dc2a15f6c4e46ae21d42241c |
| [r5 GLOBAL_EXTREMA.md](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/general_arc_2026-11-03_r5/GLOBAL_EXTREMA.md) | 361935a76da83416f90da22d8a7f35e882616f27bcf4d389ef2a29198b342fe4 |
| [IK00会议PDF](D:/毕业设计/研究/Randomizing_polynomials_A_new_representation_with_applications_to_round-efficient_secure_computation.pdf) | 963e0063ed3ff75206db802acefc1da010e77bc1e637c421ab16c04acf835791 |
| [Giorgi期刊PDF](D:/毕业设计/研究/3-3-4.pdf) | 8688a088693f77ca84525520081357cd5d838ffdb04a662c01d67a4c52668f37 |
| [Oxley第二版PDF](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/sources/oxley.pdf) | a4a6646ad354ef11e3716b73716f892ca20b69ffb04d8d1448974beb77f9f77b |
| [低秩加性掩码HTML](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/novelty_search_2026-11-03_r2/sources/lowrank2026.html) | d0f46914bcc01a3918eac8408bd4dc95c7a0c5991a22cab81cd0f63274643565 |
| [HKZ16 PDF](D:/毕业设计/研究/密码学辅助_一致性核验/papers/HKZ16.pdf) | 2229f5fc82fc3cb68308a04c848d4193b5e37e2c325cd77055a14a48968593cb |

本轮新文件位于独立查新目录。运行内容包括文献读取、现有PDF提取/渲染工具和报告编写。候选机制实现的进入状态见第6节。

## 附录A Giorgi期刊版全部后向书目

下列55条均来自该版References第38–43页。统一状态R0表示“书目已登记，所引原文正文待取得，变量映射及S1—S5覆盖判断待核”。R0条目不会进入覆盖结论的证据分母。年份和题名按所读书目登记，外部出版元数据复核另行进行。

| 原编号 | 题名及年份 | DOI或原文入口 | 状态 |
|---|---|---|---|
| AAB+22 | HQC，2022 | https://csrc.nist.gov/Projects/post-quantum-cryptography/round-4-submissions | R0 |
| ABC+22 | Classic McEliece，2022 | https://csrc.nist.gov/projects/post-quantum-cryptography/round-4-submissions | R0 |
| BCD+24 | An Improved Threshold Homomorphic Cryptosystem Based on Class Groups，2024 | https://doi.org/10.1007/978-3-031-71073-5_2 | R0 |
| BD10 | Threshold Decryption and Zero-Knowledge Proofs for Lattice-Based Cryptosystems，2010 | https://doi.org/10.1007/978-3-642-11799-2_13 | R0 |
| BGW88 | Completeness Theorems for Non-Cryptographic Fault-Tolerant Distributed Computation，1988 | https://doi.org/10.1145/62212.62213 | R0 |
| BIB89 | Non-Cryptographic Fault-Tolerant Computing in Constant Number of Rounds of Interaction，1989 | https://doi.org/10.1145/72981.72995 | R0 |
| BLRT26 | A Heuristic Subexponential Attack on the McEliece Cryptosystem，2026 | https://eprint.iacr.org/2026/1232 | R0 |
| BS23 | Simple Threshold (Fully Homomorphic) Encryption from LWE with Polynomial Modulus，2023 | https://doi.org/10.1007/978-981-99-8721-4_12 | R0 |
| Can01 | Universally Composable Security，2001 | https://doi.org/10.1109/SFCS.2001.959888 | R0 |
| CD01 | Secure Distributed Linear Algebra in a Constant Number of Rounds，2001 | https://doi.org/10.1007/3-540-44647-8_7 | R0 |
| CDM00 | General Secure Multi-Party Computation from Any Linear Secret-Sharing Scheme，2000 | https://doi.org/10.1007/3-540-45539-6_22 | R0 |
| CEN25 | Share the MAYO: Thresholdizing MAYO，2025 | https://doi.org/10.1007/978-3-031-86599-2_6 | R0 |
| CKP07 | A Note on Secure Computation of the Moore-Penrose Pseudoinverse and Its Application to Secure Linear Algebra，2007 | https://doi.org/10.1007/978-3-540-74143-5_34 | R0 |
| CLOS02 | Universally Composable Two-Party and Multi-Party Secure Computation，2002 | https://doi.org/10.1145/509907.509980 | R0 |
| CLT22 | Threshold Linearly Homomorphic Encryption on Z/2^k Z，2022 | https://doi.org/10.1007/978-3-031-22966-4_4 | R0 |
| CS19 | Sharing the LUOV: Threshold Post-Quantum Signatures，2019 | https://doi.org/10.1007/978-3-030-35199-1_7 | R0 |
| DDFY94 | How to Share a Function Securely，1994 | https://doi.org/10.1145/195058.195405 | R0 |
| Des93 | Treshold Cryptosystems，1993，题名按原书目拼写 | https://doi.org/10.1007/3-540-57220-1_47 | R0 |
| DF90 | Threshold Cryptosystems，1990 | https://doi.org/10.1007/0-387-34805-0_28 | R0 |
| DFK+06 | Unconditionally Secure Constant-Rounds Multi-Party Computation for Equality, Comparison, Bits and Exponentiation，2006 | https://doi.org/10.1007/11681878_15 | R0 |
| DJ01 | A Generalisation, a Simplification and Some Applications of Paillier's Probabilistic Public-Key System，2001 | https://doi.org/10.1007/3-540-44586-2_9 | R0 |
| DLN+21 | Non-Interactive CCA2-Secure Threshold Cryptosystems，2021 | https://doi.org/10.1007/978-3-030-75245-3_24 | R0 |
| FO13 | Secure Integration of Asymmetric and Symmetric Encryption Schemes，2013 | https://doi.org/10.1007/s00145-011-9114-1 | R0 |
| For65 | On Decoding BCH Codes，1965 | https://doi.org/10.1109/TIT.1965.1053825 | R0 |
| FP01 | Threshold Cryptosystems Secure Against Chosen-Ciphertext Attacks，2001 | https://doi.org/10.1007/3-540-45682-1_21 | R0 |
| FPS01 | Sharing Decryption in the Context of Voting or Lotteries，2001 | https://doi.org/10.1007/3-540-45472-1_7 | R0 |
| GG03 | Modern Computer Algebra，第二版2003 | Cambridge University Press，原书目未给URL | R0 |
| GIJS26 | Quasipolynomial Cryptanalysis of the McEliece Cryptosystem (or: PIR Meets McEliece)，2026 | https://eprint.iacr.org/2026/1630 | R0 |
| GJKR07 | Secure Distributed Key Generation for Discrete-Log Based Cryptosystems，2007 | https://doi.org/10.1007/s00145-006-0347-3 | R0 |
| GLOV24 | Fast Secure Computations on Shared Polynomials and Applications to Private Set Operations，2024 | https://doi.org/10.4230/LIPIcs.ITC.2024.11 | R0 |
| GLOV26 | Threshold Niederreiter: Chosen-Ciphertext Security and Improved Distributed Decoding，2026 | https://doi.org/10.1007/s10623-025-01795-6 | R0 |
| GRJK00 | Robust and Efficient Sharing of RSA Functions，2000 | https://doi.org/10.1007/s001459910011 | R0 |
| Hem26 | Key Recovery for the McEliece Cryptosystem Using Higher-Order Vanishing，2026 | https://eprint.iacr.org/2026/1339 | R0 |
| HHK17 | A Modular Analysis of the Fujisaki-Okamoto Transformation，2017 | https://doi.org/10.1007/978-3-319-70500-2_12 | R0 |
| HIKC23 | Efficient Decision Tree Training with New Data Structure for Secure Multi-Party Computation，2023 | https://doi.org/10.56553/popets-2023-0021 | R0 |
| HLPS26 | Secure Matrix Invertibility Testing over Fields of Small Order or Characteristics，2026 | https://eprint.iacr.org/2026/514 | R0 |
| HMR+19 | Efficient RSA Key Generation and Threshold Paillier in the Two-Party Setting，2019 | https://doi.org/10.1007/s00145-017-9275-7 | R0 |
| LC04 | Error Control Coding: Fundamentals and Applications，2004 | Pearson-Prentice Hall，原书目未给URL | R0 |
| Lin03 | A Simpler Construction of CCA2-Secure Public-Key Encryption under General Assumptions，2003 | https://doi.org/10.1007/3-540-39200-9_15 | R0 |
| LP01 | Adaptive Security in the Threshold Setting，2001 | https://doi.org/10.1007/3-540-45682-1_20 | R0 |
| Mas69 | Shift-Register Synthesis and BCH Decoding，1969 | https://doi.org/10.1109/TIT.1969.1054260 | R0 |
| MF06 | Efficient Polynomial Operations in the Shared-Coefficients Setting，2006 | https://doi.org/10.1007/11745853_4 | R0 |
| MS77 | The Theory of Error Correcting Codes，1977 | North Holland，原书目未给URL | R0 |
| MV24 | Secure Multi-Party Linear Algebra with Perfect Correctness，2024 | https://doi.org/10.62056/avzojbkrz | R0 |
| MW08 | Efficient Secure Linear Algebra in the Presence of Covert or Computationally Unbounded Adversaries，2008 | https://doi.org/10.1007/978-3-540-85174-5_27 | R0 |
| Nie86 | Knapsack-Type Cryptosystems and Algebraic Coding Theory，1986 | Problems of Control and Information Theory15(2)，159–166 | R0 |
| NY90 | Public-Key Cryptosystems Provably Secure Against Chosen Ciphertext Attacks，1990 | https://doi.org/10.1145/100216.100273 | R0 |
| Pan00 | New Techniques for the Computation of Linear Recurrence Coefficients，2000 | https://doi.org/10.1006/ffta.1999.0267 | R0 |
| Ran25 | The Syzygy Distinguisher，2025 | https://doi.org/10.1007/978-3-031-91095-1_12 | R0 |
| Ree54 | A Class of Multiple-Error-Correcting Codes and the Decoding Scheme，1954 | https://doi.org/10.1109/TIT.1954.1057465 | R0 |
| Sch93 | Fast Parallel Computation of Characteristic Polynomials by Leverrier's Power Sum Method Adapted to Fields of Finite Characteristic，1993 | https://doi.org/10.1007/3-540-56939-1_90 | R0 |
| SG02 | Securing Threshold Cryptosystems Against Chosen Ciphertext Attack，2002 | https://doi.org/10.1007/s00145-001-0020-9 | R0 |
| Sha79 | How to Share a Secret，1979 | https://doi.org/10.1145/359168.359176 | R0 |
| THO24 | Chosen-Ciphertext Secure Code-Based Threshold Public Key Encryptions with Short Ciphertext，2024 | https://doi.org/10.1007/s10623-023-01309-2 | R0 |
| Yao82 | Protocols for Secure Computations，1982 | https://doi.org/10.1109/SFCS.1982.38 | R0 |

## 附录B IK00的后续链交接

本地会议版本的参考表为36项，位于印刷302–303页。与本任务直接相关的后向节点包括[2]Bar-Ilan–Beaver1989、[14]Cramer–Damgård2000手稿、[16]Cramer–Damgård–Maurer2000、[17]Feige–Kilian–Naor1994及[22]Ishai–Kushilevitz1997。它们的原文读取和后续被引集合仍待完成。

前向链优先补取2002年的Perfect Randomizing Polynomials工作、统计随机编码后续、Arithmetic Sketching，以及与其共享矩阵随机化论证的安全线性代数。当前仅登记了获取入口和历史线索，完整前向集合仍是开放任务。
