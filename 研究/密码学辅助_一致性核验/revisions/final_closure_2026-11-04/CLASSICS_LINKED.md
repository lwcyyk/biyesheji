# 经典文献闭环与引理对接

2026-11-04。全部获取采用脚本HTTP。请求、状态、响应字节数和哈希见HTTP_REQUESTS.jsonl，原始响应保存在http目录。

## 1. Shannon 1949

C. E. Shannon，*Communication Theory of Secrecy Systems*，Bell System Technical Journal 28，656–715，1949。Crossref返回题名、作者、页码、1949年出版记录和DOI，原始元数据为http/C06.body。[出版记录](https://doi.org/10.1002/j.1538-7305.1949.tb00928.x)

| 实际文件 | 来源 | SHA-256 | 读取状态 |
|---|---|---|---|
| http/C04.pdf | University of Virginia托管的原文镜像，60页 | 2b9fee6a15fade84f35c378e645f3d1c397ebc9954deb345e7e32de88716390a | 结构预检PASS，主核读版本 |
| http/C01.pdf | University of Wisconsin课程页镜像，60页 | a5d14830f62a4dbfe92d32a86077d7a5ee30c70c76588618f9c7b15505ca8f23 | 文本可读，结构预检UNAVAILABLE，辅助比对 |

C04为大学托管的原文电子重排镜像，保持原印刷页码。C01存在读取结构告警，主定位使用C04。UCLA候选入口遇到证书校验失败，JHU候选入口404，均保留台账。[C04原始URL](https://www.cs.virginia.edu/~evans/greatworks/shannon1949.pdf) [C01原始URL](https://pages.cs.wisc.edu/~rist/642-spring-2014/shannon-secrecy.pdf)

### 核读位置

| 位置 | 原文内容 | 与本线的对应 |
|---|---|---|
| 第10节，印刷679–680，PDF24–25 | 完美保密要求观察后的消息概率等于先验，且与先验具体取值无关 | 对全部输入的观察分布进行点态比较 |
| Theorem6，印刷680，PDF25 | P_M(E)=P(E)，即密文的条件分布独立于消息 | 本线的输入x对应原文M，公开转录T对应E |
| 脚注9，印刷680 | 可将“没有消息”作为blank消息加密并发送，使发送存在性也隐藏 | 与空支持必须纳入输入域直接相关，零输入也需要服从同一观察契约 |
| 印刷681，PDF26 | 有限消息情形需要足够密钥，给出均匀模加法达到完美保密的例子 | 标准加性pad零误差构造和私密侧信息资源的经典来源 |

印刷680页另行渲染为readings/Shannon_p680.png并作视觉核对。

### 与不相容引理的正式对接

取两个输入x=0与x=eᵢ，并取观察事件A={Y≠0}。齐次线性观察使Pr[A∣0]=0，无抹除使Pr[A∣eᵢ]=1。二者违反Theorem6要求的条件分布一致性。因此“该观察不能达到完美支持隐私”是其判据的逆否应用。

从所有单支持进一步推出整张输入独立随机矩阵几乎必然为零，还使用有限个概率1事件的交及线性代数。这一附加步骤属于直接初等推论。引理继续归为限定观察模型的边界检查，原创性标签为CLASSICAL_DIRECT_COROLLARY。

## 2. Yamamoto 1985/1986

Crossref元数据已核实Hirosuke Yamamoto，*Secret sharing system using (k, L, n) threshold scheme*，Electronics and Communications in Japan (Part I: Communications)，69(9)，46–54，1986。DOI为10.1002/ecja.4410690906。原始元数据保存为http/C05.body，正文级证据仍为二手。[已核实DOI](https://doi.org/10.1002/ecja.4410690906)

Iwamoto–Yamamoto的后续论文参考[14]列出日文原版为IECE Transactions J68-A(9)，945–952，1985，并标明1986年英文翻译。原版和英译正文目前仍缺。

### 已读后续原文中的转述

| 已读论文及位置 | 转述内容 | 引用等级 |
|---|---|---|
| Iwamoto–Yamamoto，Strongly Secure Ramp Secret Sharing Schemes for General Access Structures，arXiv cs/0506065v1，PDF2 | (k,L,n)阈值ramp可达到每份额熵H(S)/L，并归于Yamamoto[14] | 对Yamamoto为二手转述 |
| 同文Definition1，PDF2；Definition7，PDF5 | 按层级规定H(S∣A)=(L−ℓ)H(S)/L，并区分强ramp对子向量的隐藏 | 对后续论文本身为原文已读，对1985/1986来源为二手 |
| 同文参考[14]，PDF9 | 日文及英译的题名、卷期、页码 | 原始书目信息的二手转述，DOI另由Crossref核实 |
| Chou–Kliewer，Secure Distributed Storage: Optimal Trade-Off Between Storage Rate and Privacy Leakage，2024，§II-B，PDF3 | 综述ramp的份额规模与随机性界，引用Yamamoto及Blakley–Meadows | 后续原文已读，历史归属按引用链登记 |

对应本地全文位于上一轮tradeoff_curve目录的http/TD01.pdf与http/TD02.pdf，其哈希保存在该轮NEW_SOURCES.json。本轮重新核对题名、相关段落和参考项。[后续论文全文](https://arxiv.org/pdf/cs/0506065v1) [2024论文全文](https://arxiv.org/pdf/2403.10676v1)

## 3. 引用等级更新

| 来源 | 旧缺口 | 归档等级 |
|---|---|---|
| Shannon1949 | 出版者PDF403，原文未核读 | 原文镜像已取得，§10/Theorem6/脚注9已核读并视觉核对 |
| Yamamoto1985/1986 | 出版者PDF403，候选DOI待核 | DOI元数据已核实，原版全文仍缺，定义和结果维持二手转述 |

本表是对历史SUICIDE_REVIEW引用等级的归档覆盖记录，历史目录保持原样。两项来源状态分别写入FINAL_VERDICT。

## 4. PI馆际获取条目

提交内容已整理为PI_HANDOFF.md，包含核实后的DOI、英译书目信息、日文原版信息和待核读位置。该文件供PI通过校园网或馆际服务办理获取。来源等级仅在实际原版材料到件并完成核读后更新。
