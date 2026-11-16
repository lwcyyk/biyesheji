> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_research_manuscript_v2_2/REVISION_AND_READINESS.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# Frodo-FI研究稿v2.2：修正闭合与人工审阅准备

2026-11-11，Asia/Shanghai。身份：**INFORMED_AUTHOR_REVISION_AND_PROOF_INTEGRATION（知情作者修订与证明整合）**。本版完成固定A定向复核的正式整合、H尾验收加固、确定性标量重放及封存。历史材料保持原字节；本轮交付以MANIFEST.json的文件清单与输入快照为准。

## 1. 本版结果与适用范围

结果A保留CF-1：λ≥2、n=8λ、D=8ceil(log₂n)、q=2^D、m̄=n̄=8、B=2、精确独立χ640、Ord_n规范化。对每个预先固定A，最长n次诚实更新逐样本正确；原游戏攻击以≤3n+1次调用得到Δ→1。打印参数域、官方D≤16接口、精确LWE前提与作者实际软件按原审计分别对应。

结果B具有两个可靠性版本，均固定n=640、D=15、q=32768、m̄=n̄=8、B=2，采用同一A的两代、精确原始χ640乘积律、既定Ord、一次诚实未筛选TG/Upd及最近整数平局向上Decode。消息、行/坐标均在相关币之前固定。

| 项目 | B_U：均匀Setup | B_FA：每个预先固定A |
|---|---|---|
| 更新概率量词 | 平均均匀A、两代钥匙与全部诚实币 | 任取在全部原始χ抽样前固定的A，给定A后χ仍为精确乘积律；平均其后全部诚实币 |
| 初始完整正确率 | ≥1−2^-132；此项还逐A成立 | ≥1−2^-132 |
| 更新指定坐标正确率 | [0.2499054,0.2500946] | 本版未把该更紧坐标区间扩到任意A |
| 更新指定行8坐标全正确率 | [0.0000152532,0.000030345] | [0.0000135117,0.005043360] |
| 更新完整正确率 | ≤0.000030345 | ≤0.005043360 |
| 更新完整错误率 | ≥99.9969655% | ≥99.4956640% |
| 初始完整已正确条件下 | 同一更新显示端点 | 同一更新显示端点 |
| 证明依据 | §7.2、附录D，均匀A与H公平位重量 | §7.3、附录E，逐A的χ平移PGF与新全频率常数 |

行下界的事件为预先指定行J。完整消息上界由K⊆J推出，完整消息非空性下界另由U₀=F₀=R=0见证承担。I条件化采用完成原实验分析后的事件比率；列包iid只在其原条件空间中使用。

## 2. 修正闭合表

下表“v2.1位置”包括待替换的旧表述或新增入口。FA1—FA5均按固定A审阅的实际编号登记；E1为其唯一加固建议。每项状态为**CLOSED**，表示该项已在本版落实。

| ID | 来源与要求 | v2.1位置 | v2.2位置 | 完成依据/状态 |
|---|---|---|---|---|
| V22-01 | 用户冻结的固定A命题与两种量词并列 | 摘要、§1.2–1.3、§2.1、§7.2 | 摘要、§1.2–1.3、§2.1、§7.2–7.3 | 数字、量词、条件化与机器字段一致；CLOSED |
| FA1 | E10证明§3；E11审阅§4.1–4.2：固定A,u的独立χ平移、w≥L及PGF | §2.1、附录D.2使用均匀A | 附录E.1；C30 | Pr(w≤450∣A)≤2^-73，含边界并覆盖w<450；CLOSED |
| FA2 | E10§4；E11§4.3：R₂尾与好事件 | 附录D.4的旧坏预算2^-25 | 附录E.2；C31 | R₂≤3500包络≤2^-27，坏预算2^-26，好环境w+R₂≥3950；CLOSED |
| FA3 | E10§§2/5；E11§5：两层环境及真实1280系数律 | 附录D.3联合结构 | 附录E.3–E.4；C32 | V层列包iid，B层真实a/b律，全部rank诚实积分；CLOSED |
| FA4 | E10§§6–7；E11§§6–8：新ρ、全部频率、有向算术 | 附录D.4旧均匀常数 | 附录E.4–E.6；C33 | 49点ν、六组1…16384、64/精确ν/80顺序、松弛进入Z；CLOSED |
| FA5 | E10§8；E11§9：弦线、Jensen及事件包含 | 附录D.4–D.5旧端点 | 附录E.7；C34 | E[p(V)^8∣A]上界、Jensen行下界、K⊆J完整上界；CLOSED |
| FA-I | E10§9；E11§10：逐A初始正确与I条件化 | §7.2、附录D.5 | §7.3、附录E.8；C35 | PGF单坐标≤2^-138，64并集≤2^-132，精确比率保持显示端点；CLOSED |
| FA-SEED | E10模型§5；E11§12：逐seed平均 | §7.3旧迁移段、实现审计§5 | §7.3、§7.5、附录E.9；C36 | 每个相关公共seed下后续χ及算法仍满足合同；新界解除公共A分布责任；CLOSED |
| E1-H73 | E11修正报告E1；原compute_fixed_A.py:60断言仅≥70 | 固定A原脚本的外部历史来源 | certificates/compute_fixed_A.py；附录E.10 | 新副本直接检查指数≥73及2^73N_H≤D_H，当前证书相同；CLOSED |
| V22-MODEL | 用户及E12：模型迁移和作者工件状态 | §7.3；C25c | §7.4–7.5；C25c、C37 | 旧更紧数字保留分布责任，秘密seed/公式/筛选/Ord/算术继续核准；WAITING_FOR_AUTHOR_ARTIFACT；CLOSED |
| V22-REVIEW | 用户及E11实际身份/385项/人工入口 | 附录C、C25r、旧人工入口 | 附录C、E.10；C38；HUMAN_REVIEW_ENTRY | 原审阅与本轮重放分别登记，精确模型ID为null；CLOSED |
| V22-SEAL | 用户：只读输入、主张依赖与可追溯封存 | v2.1五文件及历史清单 | 主张矩阵、MANIFEST、evidence | 输入指纹、逐主张依赖、定向差分、全部链接及文件清单；CLOSED |

完整更改块的旧/新行号及文本摘要哈希见[evidence/MANUSCRIPT_PATCH_LEDGER.json](../../frozen/crypto_fi_research_manuscript_v2_2/evidence/MANUSCRIPT_PATCH_LEDGER.json)，实际差分见[MANUSCRIPT_REVISION.diff](../../frozen/crypto_fi_research_manuscript_v2_2/evidence/MANUSCRIPT_REVISION.diff)。本轮使用既有稿定向补丁，附录A与D的证明正文逐文本保留；旧§7.3调整为§7.4，迁移表置§7.5。

## 3. 定向复核与当前执行的真实身份

| 记录 | 实际身份/曝光 | 计算与适用范围 |
|---|---|---|
| E7：640首轮概率审阅 | AUTHOR_PROOF_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 原记录375项含100条文件指纹，范围沿用v2.1 |
| E8：640补充概率审阅 | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 原记录303项；支持均匀Setup完整链 |
| E9：v2.1作者勘误 | AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY | 原记录243项；976全部1281系数与ε、三表一致性，按历史执行范围继承 |
| E10：固定A作者推导 | INFORMED_FIXED_A_PROBABILITY_DERIVATION_AND_DETERMINISTIC_FINITE_CERTIFICATES | 2026-11-10；原VERDICT当时登记待复核 |
| E11：固定A定向复核 | AUTHOR_PROOF_AND_PRIOR_REVIEW_VISIBLE_TARGETED_MATHEMATICAL_REVIEW | 2026-11-11；FA1—FA5、逐A初始/条件化、公开seed；385项通过，核心PROVED_UNDER_STATED_MODEL |
| E14：当前v2.2作者整合 | INFORMED_AUTHOR_REVISION_AND_PROOF_INTEGRATION | 作者与旧审阅可见；加固作者脚本副本1次、复核脚本副本1次，385项重放通过 |

E11会话为01a1c652-ba78-71a0-b293-a09d61f26039，turn为01a1c652-c18f-7f81-abf9-d4622bc71aac，身份及计算按原INPUT_AND_REVIEW_PROVENANCE与REVIEW_VERDICT引用。其声明家族为Codex基于GPT-6，精确后端ID与权重为null；作者/旧审阅后端对应及模型错误过程独立性未认证。当前执行声明相同可见家族，精确后端ID同样按实际可见证据为null。本轮新增独立审阅、人工、跨模型、盲审、子代理及证明助手次数均为0，经验校准NOT_CALIBRATED。两次385项执行分别有来源和结果哈希，其计数仅表明核对范围。

## 4. 有限数学重放与来源指纹

本轮先核对100个直接历史文件及其中1,789条带路径/哈希引用，全部匹配；输入快照含338个唯一历史文件。源论文PDF、源TeX、官方规范及旧证书的实际引用字节均在快照/嵌入核验记录中。指纹核对、JSON解析与语义阅读各自登记；本轮语义阅读集中在固定A模型/证明/复核、v2.1相关章节、作者实现迁移与发表影响裁决，旧攻击、LWE完整证明及来源页图沿用封存审阅范围。

| 本轮核对 | 结果 | 可追溯入口 |
|---|---|---|
| H尾直接验收 | 指数73，认证2^73N_H≤D_H<2^74N_H | 新作者脚本与FINITE_CERTIFICATES.environment.H |
| R₂尾、初始坐标尾 | 包络最大指数27、138；初始完整失败预算2^-132 | FINITE_CERTIFICATES.environment.R2及initial |
| χ/ν/乘积分布、舍入 | 完整25点、49点差值律、625对产品；4标签×32768残差穷举 | 385项复核结果中的逐检查字段 |
| 全频率及端点 | 六组、ρ、R̄/Q、Z/F/U/L、条件端点全部匹配 | 本版FINITE_CERTIFICATES及RECOMPUTED_CERTIFICATES |
| 作者证书相等性 | 本版输出与E10原证书逐字节相同 | SHA256 `206ce2a3fa4c21307f98f896b20801a384960fe348cea47fa6f4f68f82894235` |
| 复核结果相等性 | 本版385项结果与E11原结果逐字节相同 | 具体SHA256见REPLAY_EXECUTION与MANIFEST |
| χ976/三张表 | v2.1的纠错与历史证书继续有效；本轮核对新版显示三行与v2.1数据逐项一致 | 本版DOCUMENT_QA及v2.1显示绑定/重放记录 |

执行指纹见[REPLAY_EXECUTION.json](../../frozen/crypto_fi_research_manuscript_v2_2/evidence/REPLAY_EXECUTION.json)，原脚本与副本的逐项改动见[SCRIPT_COPY_AND_HARDENING.json](../../frozen/crypto_fi_research_manuscript_v2_2/evidence/SCRIPT_COPY_AND_HARDENING.json)。加固只改变H验收阈值；复核副本只改变证书输入路径，数学检查保持。复制后输出中的数学参考日期沿用原数据，2026-11-11的实际执行由独立执行记录标识。

复算入口（工作目录为v2.2）：

```powershell
python -X utf8 certificates/compute_fixed_A.py
python -X utf8 certificates/recompute_certificates.py
```

两脚本只向本版写有限标量结果。重新运行时应同时核对结果与封存哈希；正式版本修改写入后续新目录。历史脚本本轮执行0次。密钥/密文/token抽样、攻击或保护机制实现、Monte Carlo、LWE求解、联网检索、作者联系及原生服务操作均为0。本轮代码只承担用户已授权的确定性有限数学与文档/指纹检查。

## 5. 模型迁移与作者工件的剩余最小事实

公开前置Z_pub先确定A=g(Z_pub)，且每个相关z下后续原始χ与整个算法满足冻结合同时，逐seed使用固定A定理并平均。**对0.005043360新上界，公共A的均匀性、伪随机性、像熵及其与均匀全矩阵的距离责任已解除。** 更紧0.000030345仍属于均匀Setup或有效对应模型。秘密噪声seed产生的多坐标/多调用联合律、实际公式、筛选重试、Ord及算术继续决定作者程序适用范围。

当前状态为**WAITING_FOR_AUTHOR_ARTIFACT**，六种作者配置的整体映射均UNRESOLVED，带原消息、初始及更新后消息比对的真实作者UE轨迹取得数为0。最小外部提交为：

1. 论文/作者/机构可认证关联的不可变UE commit或归档，包含TG、Upd、Ord/Tensor、Decode及实际640配置与依赖。
2. 同A两代、公开seed确定时序及给定公开seed后的秘密噪声来源/域分离/切片/复用规格，附足够证明精确合同或具体损失的材料；同时给完整筛选、重试与异常路径。
3. 一条诚实未筛选Enc→TG→Upd→Dec轨迹，记录原消息、初始/更新后消息及两次比对、代次/token标识、可重复随机性、算术/舍入配置、失败与分母。性能表整体对应另需六配置及原100次计时日志。

最能改变结论适用范围的下一项证据是上述认证作者工件及640轨迹。它将支持或改变性能对象到理论模型的迁移；单条路径证据只认证具体执行。

## 6. 原声明影响与人工交接

固定640的Theorem6.3打印充分前提仍未满足；本版给该前提之外的一步可靠性概率。完整正确性充分式继续为B₀+t_maxW<q/2^(B+1)，s=12吸收初始项的结论携带§6.2原参数范围。Theorem6.9沿用精确LWE审计：CF-1丰富独立同秘密样本前件失效，固定n/3n样本与FI完整归约待核。有限640下界与任意渐近族的正确性定义分别评价。

应用优先权沿用截至2026-11-10的有界审计，固定A扩展本轮新增检索0。贡献表述增加**公开矩阵量词扩展及迁移前提缩减**，通用方法归属保留经典概率、Fourier、卷积、凸性与有向算术来源。

[HUMAN_REVIEW_ENTRY.md](HUMAN_REVIEW_ENTRY.md)已指向v2.2，包含A、B_U、B_FA完整合同、最短攻击、条件链、三个具体审阅问题与证书入口。材料足以交付人工密码学审阅；人工数学判断、作者程序对应、完整FI归约、缺失前驱版本和全球优先权继续作为外部问题列示。五份核心文件及支撑目录实际生成并由MANIFEST封存。
