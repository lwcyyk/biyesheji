# 单向 UE 随机性泄露：构造选择

日期：2026-11-06。独立分支，游戏 **UNI-R-CPA-1**。旧 EE-R-PA1 与 TIPE/DSG 保持各自作用域，后者状态 WAITING_FOR_EXTERNAL_SPEC。本轮邮件、外部联系及原生 AS/RP 请求为 0；候选协议实现为 0。

## 来源与实际取得范围

| ID | 完整来源、版本与核读范围 | 工件与 SHA256 |
|---|---|---|
| RC26 | Tanishita、Hayashi、Ishii、Matsuda、Matsuura，*Updatable Encryption Secure against Randomness Compromise*，IEICE E109-A(3)，2026，pp.232–245；DOI 10.1587/transfun.2025CIP0020。核读 §2–4，尤其 Definition 3、普通带 oracle、RISE 及绝缘区模拟 | 既有 `sources\ieice2026_pdf.pdf`，14 页；`abe458562c57c0d1023d79e3d1e6037c785fd78f4e8248c43e8a351ad11163ae` |
| FRODO-FI | Jurkiewicz、Prabucka，*Unidirectional Key Update in Updatable Encryption, Revisited*，DOI 10.46298/fi.14425。PDF 页眉：Fundamenta Informaticae 194(4), Article 4, **2025**；文件标 arXiv:2410.03948v4，2025-12-29。已存发表页面标 **2026-01-11**。三种日期分别保存。核读 §§3–7，重点 pp.12–20 算法、参数与证明 | 既有 `sources\unidir2026_full.pdf`，23 页；`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4` |
| MPW23 | Miao、Patranabis、Watson，*Unidirectional Updatable Encryption and Proxy Re-encryption from DDH*，PKC 2023 Part II, LNCS 13941, pp.368–398；DOI **10.1007/978-3-031-31371-4_13**。本轮取得正式全文，定向核读 KPHE 接口、blinding 游戏及 §3 的变换要求；具体 DDH 实例和若干详细证明委托扩展版 | 本目录 `sources\mpw23.pdf`，31 页；`a1c93970df50b4df088a9526d42b60f5886287f52eac49d2e03935ff7aac5368` |
| GP23 | Yao Jiang Galteland、Jiaxin Pan，*Backward-Leak Uni-Directional Updatable Encryption from (Homomorphic) Public Key Encryption*，PKC 2023 Part II, LNCS 13941, pp.399–428；DOI **10.1007/978-3-031-31371-4_14**。本轮取得正式全文；核读 §2–5，特别 p417 ElGamal、pp419–422/Fig.5 与 Theorem 3；§6 只作变换覆盖核对 | 本目录 `sources\gp23.pdf`，30 页；`78c8fed13666afba2fcf211f81e7f2765fb140d19cba7fd3c716a3591cf51cb4` |

RC26 与 FI 的既有逐页/全文文本均已用于核对；排版较差的 `rc2026_full.txt` 与可靠布局文本 `rc2026_poppler.txt` 分别冻结。PDF 结构预检及原图检查记录保留。GP23、MPW23 来自 Springer 正式 PDF；Crossref 只用于定位 DOI，正文以实际 PDF 为准。FI 参考文献中 GP23 的 ISBN/DOI 字段与取得的正式版本不同，本轮采用后者。

ePrint 2022/324 和 2022/311 扩展 PDF 本轮各尝试一次，均为 HTTP 403 HTML，未登记为全文。网页搜索连接传输失败。Frodo 官方参数参考文件/规范的有限获取也失败；未把已知常用参数冒充论文性能实验的已核准配置。详见 `SOURCE_REGISTER.json`。

## 两个具体对象的审查顺序

1. **FRODO-FI**：完成维度、Ord/Tensor 恒等式及噪声递推。存在明确的基础安全反例路线：公开方阵 P2 可逆时，更新第一块可恢复其小支撑随机矩阵。已在 `PROOF_ATTACK_OR_OBSTRUCTION.md` 给出独立合法攻击与假设界。因而退出主增强安全证明对象。
2. **最终唯一主对象：UNIUE-GP23-EG-CTX1**。采用 GP23 Fig.5 的逐代新增坐标变换，底层为 p417 的 modified ElGamal。固定公开键上下文和正确的非零密钥域，完整算法见 `CORRECTNESS_AND_PARAMETERS.md`。对它完成固定挑战切点的普通全带安全证明。

MPW23 在本轮用于审查转换能力与假设，没有展开其未取得的 DDH 具体实例；未深入第三个具体 UE。GP23 的 bootstrapping 分支同样只核对接口和覆盖条件。

## 主对象的版本边界与显式补全

这是对已有泛型变换的**明确实例化 profile**，不声称某份未取得的官方实现逐字与它相同。

- 密钥及倍率取 Z_q*；保证 modified ElGamal 的逆运算有定义。GP23 p417 简写 x∈Z_q，本文显式采用其正确性所需非零域，与 RC26 RISE 的密钥域相同。
- 加密指数取 Z_q，包含 0；这是 modified ElGamal 的完整均匀随机指数，RC26 的具体算法亦使用此域。KHC 新指数仍可按 GP23 的 Z_q* 采样。新 PKE 加密指数的全域均匀性使本轮挑战新鲜化精确成立。
- 将 KHC 所需目标公钥作为显式公开参数：`KHC(δ,P_new,C;a)`。p417 的公式已使用 [xy]；Fig.5 的简写未把这个参数列出。公开缓存由初始公钥和各 token 递推，属于接口显式化。本游戏已允许暴露 K1，故该缓存不增加本证明族的秘密信息。
- 消息群取 G，Fig.5 的 ⊕ 实例化为群乘法；向量补空位对应 `(1,1)` 的单位密文。未引入新保护协议、裁剪、到期或认证机制。

每项补全都明示在上述 profile 名称内，安全定理只针对这个已冻结规范。理论结果不依赖取得作者新版本来完成。

## 结果定位

主对象通过本轮明确规范的类型及代数正确性检查；其受限随机带增强安全由成熟 modified ElGamal/DDH 与公开算法模拟覆盖。提供完整归约，有助于澄清具体量词；尚无相对同功能强基线的资源优势。

Frodo 仿射支撑区分器可作为独立密码分析候选，优先权及独立复核尚待进行。新证明的固定切点不能与 GP23 对更广自适应游戏的 `2l²` 界直接作紧致性优势比较。
