# 本轮来源与阅读范围

2026-11-07。所有取证以本目录实际响应、来源记录与文件哈希为准。SHA-256 汇总见 SOURCE_MANIFEST.json。

## 1. 新取得并核读的材料

### A Pragmatic Introduction to Secure Multi-Party Computation

作者为 David Evans、Vladimir Kolesnikov、Mike Rosulek。作者站点标注 NOW Publishers 于 2018 年出版，所提供全文最近更新于 2022-06-11。取得 mpc_book.pdf，共 181 个 PDF 页面，并取得 6 页勘误。

实际阅读范围包括题名与目录、PDF 第 6–8 页简介、第 20–25 页安全定义、第 43–45 页 BGW 操作、第 128–130 页诚实多数方法。其余页面仅作标题和关键词定位。PDF 第 45 页回到渲染图像核对，打印页码为 44。

本轮根据 §3.3 展示的乘法降阶操作计算通信上界，按被动对手模型使用。§7.1 提及恶意安全、fairness 和 guaranteed output delivery 的后续方案，但本轮没有完成这些原始论文及动态状态组合的完整核读。

勘误已完整提取并查看，作者页所列版本与最新勘误日期一致。文件结构 preflight 均为 PASS，页数一致，warnings 为空。

该作者教材承担算法描述与安全定义来源。原 BGW 安全证明及其恶意版本的完整审计另行登记。[作者站点](https://securecomputation.org/) [全文](https://securecomputation.org/docs/pragmaticmpc.pdf) [勘误](https://securecomputation.org/docs/errata.pdf)

## 2. 复用的已有原文

复用 ae_decentralized_authority_exploration 中的 VERA PDF 与来源记录。本轮重看 PDF 第 8 页引用链，定位 SPKI/SDSI、分布式信任管理和撤销语义的经典来源。前轮已核的 Definition 2–4、Lemma 1 与 observed-prefix 范围继续按原记录使用。

原先的 DAAC-CR 及递归 DAC 官方记录、错误版本声明和获取失败记录继续作为来源身份依据。历史目录保持其版本身份。

## 3. 正常入口追加核查

### 递归 DAC

使用普通 HTTPS 客户端与默认 TLS 验证访问已登记公开 PDF，仍返回 HTTP 403。本轮未取得正文。未按摘要补写撤销、更新或复杂度证明。

### DAAC-CR 正式版

DOI 10.1109/TIFS.2025.3587182 本轮跳转到 IEEE 文档 11075711，最终响应 HTTP 202，文件为 0 字节。正式正文与附录继续待取得。前轮 ePrint 官方记录明确标注早期版本有错误并已 withdrawn。[正式入口](https://ieeexplore.ieee.org/document/11075711/)

### Hidden credentials

IACR 的 hidden credentials 查询正常取得两项官方摘要。

- Robert Bradshaw、Jason Holt、Kent Seamons，Concealing Complex Policies with Hidden Credentials，ePrint 2004/109。摘要讨论隐藏资源请求、资源、政策和凭证，以及向不满足政策者隐藏复杂政策。
- Jason E. Holt，Reconciling CA-Oblivious Encryption, Hidden Credentials, OSBE and Secret Handshakes，ePrint 2005/215。摘要强调这些系统之间有不同的安全范围。

本轮将其登记为主动观察和政策隐私的直接查新线索。完整正文、探测模型和同级协议覆盖尚未核读。[2004/109](https://eprint.iacr.org/2004/109) [2005/215](https://eprint.iacr.org/2005/215)

## 4. 检索覆盖与失败情况

追加检索使用公开 arXiv、IACR、作者主页及教材站点，关键词围绕 delegatable anonymous credentials、private reachability、credential discovery、hidden credentials、revocation privacy probing、trust negotiation probing。

arXiv 的 private reachability 单页返回 31 项，多数语义较远，按题名筛选。另两个探测关键词查询返回空结果。查询结果按实际入口范围使用，空结果没有承担原创性证明。

部分 PowerShell HTTPS 请求遇到 SSL 连接失败。使用保持默认 TLS 验证的 Python urllib 后，Purdue 作者主页、IACR 检索和 MPC 作者站点正常取得。IAS 页面返回 403，试探的 JCS 作者稿地址及 Rivest 页面返回 404。Google 搜索响应为脚本重定向页面，没有取得可读结果。

作者主页和安全阅读表用于来源发现。没有将未取得的 Distributed Credential Chain Discovery 原文登记为已读。

## 5. 取证与过程归属

本轮新增的菱形图族、费用代入和主动撤销双世界例均由模型辅助纸面推导。通用可达性、秘密共享电路和区分论证按标准工具应用归属。

脚本只用于网络响应保存、PDF 提取、结构检查、哈希和文稿检查。候选机制实现、参考实现、求解器和数学穷尽程序状态均为未开始。外部数学或密码学核验待取得。
