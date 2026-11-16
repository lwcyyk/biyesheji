# EE-R-PA2：来源与游戏校准

日期：2026-11-06。状态：RESEARCH_EXTENSION。历史输入只读；候选协议代码与原生 AS/RP 请求均为 0。内部审查由同一研究代理交叉核对原图、提取文本及推导完成；外部同行、作者确认和证明助手复核尚待进行。

## 1. 冻结起点与唯一主命题

本轮继续使用 **EE-R-PA1**，完整定义位于 `D:\毕业设计\crypto_expiring_ue_research\SECURITY_GAME.md`，SHA256 见 `STARTING_POINT_LOCK.json`。EE-R-PA2 是审计轮次名称，游戏名称保持 EE-R-PA1。本文未悄然修订查询权限。

主命题：具体 EE23 DSG/TIPE 在普通 Enc、ExPunc 完整随机位带暴露、挑战生成及自动更新带隐藏、单次到期后钥匙暴露下的联合视图安全。

继承结果：RISE 加公开到期元数据的攻击；保留公开不变量的包装攻击；单标签、通配令牌的 TIPE-R→UE-R 精确提升（优势损失 1）；较弱存储删除投影的 PPRF+AEAD 覆盖。前两项的对象和原游戏边界沿用上一轮；提升定理的前提仍是基础 TIPE-R 安全。

本轮已完成：普通接口完整随机带的一致生成引理；出版 Enc 公式的正文相同引理及其**正确性条件下的攻击定理**；明确定位 Lemma 5 的前提冲突。具体作者构造的完整增强安全结论保持未决。

## 2. 原文取得和版本

| 资料 | 取得状态与版本 | 实际核读 | 定位与限制 |
|---|---|---|---|
| Slamanig–Striecks, *Revisiting Updatable Encryption: Controlled Forward Security, Constructions and a Puncturable Perspective*, TCC 2023 | 正式章全文，31 页，印刷 pp.220–250；DOI 10.1007/978-3-031-48618-0_8 | §§2–3，Fig.2/3、Theorem 1/2、全部混合引理及 DSG 性质 | `D:\毕业设计\crypto_expiring_ue_research\sources\tcc_publisher_pdf.pdf`；SHA256 `afe4c0d4577feaa581aa5c7c15c699bafbf624cc7df5baedea593e9ca7038f0b` |
| ePrint 2021/268 作者完整版、历史版本、勘误 | PDF 与版本页持续访问受阻；本地 PDF 请求结果为 Cloudflare HTML | 只取得上一轮官方摘要/元数据；显示 2021-03-03 收稿、2023-10-03 为第 4 次修订 | `https://eprint.iacr.org/2021/268.pdf`；`https://eprint.iacr.org/archive/versions/2021/268`。历史版本正文及公开勘误未核实；公开元数据不能代替全文 |
| *Updatable Encryption Secure against Randomness Compromise*, IEICE 2026，DOI 10.1587/transfun.2025CIP0020 | 正式全文，14 页，pp.232–245 | §3 游戏、§4 RISE 与完整模拟的相关步骤，特别 pp.239–242 | 原目录 `sources\ieice2026_pdf.pdf`；SHA256 `abe458562c57c0d1023d79e3d1e6037c785fd78f4e8248c43e8a351ad11163ae`；CANS 2024 早期全文继续缺失 |
| Pranshu Kumar, *Upgrading Security Properties for Updatable Public-Key Encryption through Modular Transformations*, Waterloo MMath thesis, 2026 | **本轮机构直链取得完整 PDF，95 页** | 标题页；§2.1 Definitions 1–5；§3.1/Fig.3.1；§3.4；§4 Definition 15；§6 开头、Theorem 6；§7 与结论 | `sources\waterloo_full.pdf`；SHA256 `4f526c4505739fbf4232e1b91af28ac64db7e61d811cb7d9ffec657b49e53e94`。源链接：`https://uwspace.uwaterloo.ca/bitstreams/b87c745e-9efb-4fa5-b2ff-1ce152b15e40/download` |
| RCCA19，ePrint 2019/222 | 全文继续缺失 | 上轮官方摘要及作者页面 | 转换的逐接口随机带保持性质继续未核实 |
| *Unidirectional Key Update in Updatable Encryption, Revisited*, 2026，DOI 10.46298/fi.14425 | 23 页正式全文 | 本轮定向核对安全模型、§6.1/Thm.6.9 及到期相关工作 | 上轮 `sources\unidir2026_full.pdf`；SHA256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4` |

获取记录：`RETRIEVAL_01.json`、`RETRIEVAL_02_CLASSIFICATION.json`、`RETRIEVAL_FINAL.json`。urllib 的 TLS EOF 后，curl 成功取得 Waterloo 文件；ePrint PDF/历史页返回访问挑战，最终历史页 HTTP 403。一次定向网页检索连接传输失败。有限尝试后继续局部推导；本轮没有穷尽作者镜像、历史存档或全部公开勘误。

## 3. 逐接口与有效性校准

记代次标签为 a(e)，原文用 t(e)；密文对象标签另记 t，避免混同。

| 项目 | 正式原文 | EE-R-PA1 处理 | 对应状态 |
|---|---|---|---|
| RotKey / KPunc | 输入 K_e，产生 K_{e+1} 与 Δ_{e+1}，pp.230、232–234 | Next 同一方向，全部通配 Δ 公开 | 一致，权限更明确 |
| Corrupt(token,e') | Fig.2 返回 Δ_{e'}、登记 e'；Fig.3 同时登记标签集 | 令牌直接公开；只允许一次 j>τ 的钥匙暴露 | 限制到单链/单次晚钥匙，包含目标到期情形 |
| 已公开挑战集 C* | Chall 和 GetUpdC*/GetUnpuncC* 将实际公开版本记入 C*；Next 内部更新本身未自动加入公开集 | 保存所有公开挑战，合法更新可达闭包也参与资格判断 | 明示本地更新路径，避免只看已登记中间版本 |
| 有效性条款 2 | Fig.2/3 对 e' 代钥匙及 e'−1 挑战，检查 e'−1 的 token 登记 | 从公开挑战出发，使用 Δ_j 的边只在 j≤τ 时允许；不能连到获准钥匙 | Fig.2/3 的下标疑点单列 O-GAME；保持研究游戏独立命名 |
| 普通 Enc/Upd | 原图只返回密文，无完整随机带 | 返回完整算法位带；挑战/自动更新带隐藏 | 研究扩展 |
| 到期正确性 | p230/233 只保证未到期正确性；具体算法 p239 的 guard 使过期返回 ⊥ | 诚实过期更新返回 ⊥；攻击者可离线改字段和执行计算 | 严格失败约定属于本轮固定功能 |
| 接口顺序 | p233 ExPunc(Δ,C)；p234 UE.Upd 定义行写 ExPunc(C,Δ)；p235 证明再用 ExPunc(Δ,C) | 固定 ExPunc(Δ,C) | 类型/上下文支持参数次序排版疑点；单列 O-ORDER |
| 初始代次 | Gen 返回 K1；Fig.2/3 初始化 e=0 | 初始代次 1 | 原图存在记号对应待确认；本轮不据此提出攻击 |

O-GAME：按图字面，先公开 C2（expiry=3），到 3 代取 K3、Δ3，不公开中间挑战，条款 2 检查 2∉D*，局部更新后可解密。上一轮已给完整查询串。它是字面定义的一致性反例。作者意图游戏与版本校正后的结论分别待核准。EE-R-PA1 的合法可达闭包会将此**活跃目标攻击**排为平凡胜利；到期后的 K3/τ2 攻击仍合法。

分类：原图与提取内容一致，**提取错误的解释缺少支持**；图内返回/登记与有效性检查之间存在字面下标和可达性缺口。正文明确意图排除借令牌到达已知钥匙的平凡胜利，因此“下标排版＋省略传递闭包约定”是一种可能解释。作者完整版未取得，尚无法在排版、版本差异、隐含约定和定义修订之间作最终归因。本轮只对已取得出版图的字面语义作审计，作者意图的安全定义继续待核准。

## 4. 构造/证明的原图审计

以下内容由原 PDF 图像核对，提取文本的定位可在 `tcc2023_full.txt` 中复查。新图位于 `render\gamma_correct.png`（PDF17/印刷236）、`gen_kpunc.png`（PDF19/238）、`enc_expunct.png` 与 `enc_crop.png`（PDF20/239）、`lemma5.png`（PDF24/243）、`tipe_fig3.png`（PDF15/234）。`render\gamma.png` 是较早取错页的图，保留原工件并明确排除为 Γ 公式依据。

| 审计项 | 原文关系 | 本轮裁决 |
|---|---|---|
| O-TOKEN | p239 Δ_{e+1} 的乘积编码 **a(e+1)**；p243 Lemma 5 称 Δ_{e*} 编码 **e*−1**，以此断言与挑战无前缀 | 直接证明迁移的精确障碍；原图确认，版本或作者约定尚待解释 |
| O-FRONTIER | p239 Enc 使用 I(e,τ)=Γ_{a(e)}\Γ_{a(τ+1)}；a2=1、a3=11、a4=111 时 I(2,2)=I(2,3)={1} | 正文相同关系已证明；保留该关系的正确构造满足条件性攻击定理，详见 ATTACK_OR_OBSTRUCTION |
| O-TYPE | ExPunc 输入/返回分别写全 Γ_e/Γ_{e+1}，中间循环又写 Γ_e\Γ_{τ+1}；委派后的节点与循环域也未统一 | 固定一个完整、类型一致的实际算法前，逐行执行与功能证明存在缺口；本轮不自行加入新的范围保护 |
| O-ROOT | p238 的初始元组印为 (h0,k1·h1,…,hλ)，而一般节点描述及空标签需要明确根坐标布局 | 记录源语法疑点，未据此证明方案攻击 |
| O-WINDOW | p242 Lemma 4 要求猜测 e'>e* 且 e'≤τ；τ=e* 时该集合为空。p244 Lemma 7 的中止式又需上下文核准 | 本轮主模型允许 τ=e*；原证明需要“无窗口”分支或等价解释。未将原文 poly(λ) 损失实例化为具体常数 |
| O-RERAND | Lemma 1/3 写精确 0；s∈Z_N* 及“生成元均匀分布”对乘法/平移闭包需额外检查 | 隐藏挑战分布可另作统计耦合；普通位带必须诚实生成。边缘采样差异不能单独升格为密文攻击 |

O-TOKEN 的三代前缀反例及 O-FRONTIER 的正文相同关系独立于随机带泄露。两者支持的结论与具体增强安全证明的结论分别登记。

## 5. 原游戏与研究游戏的攻击归属

| 见证 | 出版图字面游戏 | EE-R-PA1 | 作者意图/完整版 |
|---|---|---|---|
| 活跃 τ3 目标、C2→本地 C3、K3/Δ3 | 根据图的字面登记规则有效 | 由合法更新可达性排除 | 未决 |
| RISE 元数据到期，τ2、K3 反推 K2 | 原 RC26 双向钥匙闭包排除；RISE 本身未承诺到期 | 有效 | 与原 RISE 定理相容 |
| 普通 Enc 带＋晚钥匙 | 原 EE23 游戏未给带 | 有效 | 增强扩展待证 |
| 本轮正文相同条件攻击，τ2、K3 | 同样晚钥匙、无过期合法边；原图还需完善语法 | 有效，**前提为正文相同及正确性** | 完整版是否保留该 Enc 关系未决 |

## 6. 定向先例覆盖判断

RC26 pp.239–242 的普通 Upd 模拟保存累计标量 r，返回新鲜加密的 r̂−r；其精确平移使用 Z_q 的加法均匀性，并依赖绝缘区边界令牌不暴露。EE-R-PA1 公开全部令牌、允许晚钥匙；DSG 的 Enc/ExPunc 又有向量采样。该证明不能逐句替换算法名称得到本轮结论。其可借鉴部分是显式记录普通位带和分清挑战带。

Waterloo 2026 的 R2 是 **UpdPk 的随机性**，Fig.3.1 UpdO(ρ) 让攻击者选择该带；Enc 使用独立 R1。Definition 15 的 ShiftCt 是附加性质；§6 的变换只证明选择性腐化范围（完整自适应腐化列为后续问题）。从这些接口到“带到期的对称 TIPE、普通 ExPunc 完整带、fresh-vs-update 挑战、全部令牌公开”尚缺归约。取得全文关闭了“无法核实题名/接口”的资料缺项，目标安全覆盖仍未建立。

RCCA19 全文缺失，继续保留未决。单向 UE 2026 的 rand-ind-eu-cpa/backward-leak 模型及其 §6.1 旧随机性辅助模拟没有给出本轮所需的 Enc/ExPunc 完整位带与到期晚钥匙组合定理。EE23 引用 [43]（Gong、Cao、Tang、Chen，*Extended dual system group and shorter unbounded hierarchical identity based encryption*，DCC 80(3):525–559，2016）的独立全文本轮尚未取得；本文核对的是 EE23 内写出的 DSG 定义及调用该文 Lemma 11 的理由，没有将 [43] 的完整证明登记为已读。以上是定向覆盖核对，优先权与全领域无覆盖结论保持开放。
