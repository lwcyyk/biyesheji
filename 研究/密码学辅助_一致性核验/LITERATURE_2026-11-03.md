# 行空间方案的新增文献核验与创新性审查

## Material Passport

origin_skill: academic-research-suite；origin_mode: targeted-literature-and-counterargument；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: rowspace-literature-01；repro_lock: null。

本轮是针对构造的定向核验，不是完成了数据库全覆盖的系统综述。检索无命中不能证明原创。所有论文和链接均经本轮一手页面核实；阅读范围逐条说明。

## 直接先例与新增近邻

| 工作 | 核实来源与年份 | 已核对范围 | 对本项目的约束 |
|---|---|---|---|
| Dan Boneh 等，Arithmetic Sketching | CRYPTO 2023；[DOI](https://doi.org/10.1007/978-3-031-38557-5_6)，[机构全文](https://ntt-research.com/wp-content/uploads/2023/08/Arithmetic-Sketching.pdf) | §4.1–4.2、Construction 21、Theorem 22 的相关段落 | 已有 Hankel 结构及秘密矩阵盲化；这些不能列为新贡献 |
| Ronald Cramer、Ivan Damgård，Secure Distributed Linear Algebra in a Constant Number of Rounds | CRYPTO 2001；[DOI](https://doi.org/10.1007/3-540-44647-8_7)，[机构记录](https://pure.au.dk/portal/en/publications/secure-distributed-linear-algebra-in-a-constant-number-of-rounds/) | 机构元数据、作者出版链接；全文访问失败 | 安全线性代数已有长期先例；尚未完成逐算法等价性核对 |
| Kobbi Nissim、Enav Weinreb，Communication Efficient Secure Linear Algebra | TCC 2006；[DOI](https://doi.org/10.1007/11681878_27)，[机构摘要](https://cris.bgu.ac.il/en/publications/communication-efficient-secure-linear-algebra/) | 作者机构摘要与元数据 | 高斯消元、线性空间相关安全计算不是本项目新原理 |
| Jules Maire、Damien Vergnaud，Secure Multi-Party Linear Algebra with Perfect Correctness | IACR Communications in Cryptology 2024；[DOI](https://doi.org/10.62056/avzojbkrz)，[期刊全文](https://cic.iacr.org/p/1/1/29/pdf) | 摘要、§1、§2 模型与贡献定位 | 完美正确性的安全线性代数已有工作；该文明确采用半诚实模型，不能与我们的底座模型不加区分地比较 |
| Pascal Giorgi 等，Fast Secure Computations on Shared Polynomials and Applications to Private Set Operations | ITC 2024；[DOI及出版页](https://doi.org/10.4230/LIPIcs.ITC.2024.11) | 出版方摘要、模型和元数据 | 共享多项式计算、减少秘密乘法、消除错误都有近邻工作，不能凭这些关键词主张首次 |
| Pascal Giorgi 等，Constant-Round Secure Distributed Decoding and HQC Threshold Decryption | 2026；[ePrint](https://eprint.iacr.org/2026/946)，[作者列出的DOI](https://doi.org/10.62056/ay4fvu7sf) | ePrint 摘要、作者出版目录及期刊引文链接；未核读完整算法 | 特征二的共享 Reed–Solomon 解码与 Padé 近似是必须补齐的直接技术比较，不能宣称本项目首次实现安全稀疏解码 |
| Seungwoo Han、Jooyoung Lee、Seungmin Park、Mincheol Son，Secure Multi-party Matrix Invertibility Testing over Small Finite Fields | 2026；[期刊DOI](https://doi.org/10.62056/av11fh888) | 期刊摘要及模型描述 | 完美私密可逆性检测及离线/在线权衡已有研究；本项目 GL2 采样检查不是新通用可逆性协议 |

2024 完美正确性论文在期刊已正式发表；ePrint 页面仍标为 preprint，不能仅凭该字段误判发表状态。对该文的特征限制和成本也不能忽略：大特征下的公式不能原样用于二元扩域，其正文单独讨论了正特征处理。

## 与 Arithmetic Sketching 的具体联系

该文的低重量方案将 Hankel 矩阵左右两侧随机化，以隐藏矩阵结构，再公开判定秩。本项目允许泄漏支持 S，因此保留右侧标签结构，只在左侧用均匀可逆矩阵随机化。随后由公开行空间识别标签，并保留独立稀疏 gate 以限制稠密输入泄漏。

这是一项明确的功能改造，但非常接近已有矩阵盲化思想。最强反驳是：它可能只是“已知稀疏草图 + 已知单侧随机基变换 + 已知支持恢复”的自然推论。完美幅值隐藏的证明和紧凑实现使方案可核对，却不足以自动消除这个反驳。

## 能主张什么，仍不能主张什么

可以准确报告：本项目构造并实现了一个允许支持集泄漏的特定诊断编码；在稀疏承诺和合法 GL 掩码下，给出精确定位和幅值完美隐藏的条件性证明；找到 SL、奇异矩阵、复用和省略 gate 的反例；给出具体成本与同功能对照。

尚不能报告：新通用安全线性代数、新分布式解码原理、完整无误差协议、所有协议的最优乘法数、强独立原创性已经成立。真实底座从半诚实换成主动安全也不是独立原创贡献；任何合法候选和基线都应获得同样底座能力。

## 反方审查结果

1. **原创性：未通过最终确认。** 上述旧、新工作使“自然扩展”风险升高；下一次审查应优先逐节核对 2026 分布式解码的公开/秘密输出与盲化结构，而非继续堆积更远文献。
2. **总体优势：未建立。** 实测与旧方案耗时接近，新方案更多 triples、较少 inverse tuples。旧方案稀疏误接纳还能收紧到固定参数下 O(q^-4)，不能继续用粗界夸大差距。
3. **有意义的差别：有条件成立。** 新的稀疏诊断层在成功生成掩码时精确，不会随机遗漏；但 gate 仍有错误，掩码采样仍可能耗尽，真实来源仍未绑定。
4. **主线适配：仍有前置条件。** 失败位置只能用于定位完整性核验异常，不等于服务撤销语义、原生撤销单元或配置不可行证书。没有来源绑定就不能直接作为 A 的可信契约证据。

本文件为同一研究助手的反方自审，没有冒充独立专家、第二模型或同行评审。
