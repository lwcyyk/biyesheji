# 先例核验与反方审查

## Material Passport

性质：同一工程代理的推导、程序验证与文献初筛，不是独立同行审查。本轮没有运行真实 MPC 或 TLS 客户端，也没有完成外部新颖性审定。

## 本轮新增内容的准确归属

| 内容 | 可以说什么 | 不能说什么 |
|---|---|---|
| 两故障定位与遗漏复核 | 本轮给出具体代数协议和条件性论证 | 已有完整恶意安全 TLS 协议 |
| 秘密范数组合 | 本轮论证为何须在公开之前合并，避免仅放大接纳可靠性而不放大转录隐私 | 首次发明域范数、AND 或隐私放大 |
| 五乘法中间积 | 对所述双线性映射达到 5 的受限下界 | 整个协议只需 5 次乘法；新的通用多项式算法 |
| 全局非零掩码筛选反例 | 在输入独立线性掩码类中给出不可兼得论证 | 所有隐私协议都必须有失败重试 |
| Python 状态机 | 检查理想 API 顺序和输入不变前提 | 抵抗恶意操作系统或实现密码学承诺 |
| AES-GCM 例子 | 显示“标签正确”不能替代“输出份额绑定” | 完成凭据非导出实现 |

## 最近先例

1. **Express: Lowering the Cost of Metadata-hiding Communication with Cryptographic Privacy**，USENIX Security 2021。第 4.1 节讨论秘密共享向量的一稀疏审计、常数乘法检查和恶意服务器的输入修改问题，并追溯 Boyle–Gilboa–Ishai 的 FSS 工作。[原文](https://www.usenix.org/system/files/sec21-eskandarian.pdf)。本轮核对相关章节，未把该方法描绘成没有恶意安全处理。
2. **Private Analytics via Streaming, Sketching, and Silently Verifiable Proofs**，IEEE S&P 2024。已研究秘密共享数据的批量验证与恶意输入环境。需要进一步核对它与本方案的输入拥有者、允许泄漏及失败定位输出之间的区别，不能只比较老旧逐项检查。[作者论文页](https://people.eecs.berkeley.edu/~henrycg/pubs/whisper/)。
3. **The Middle Product Algorithm I**，Hanrot、Quercia、Zimmermann，2004，DOI [10.1007/s00200-003-0144-2](https://doi.org/10.1007/s00200-003-0144-2)。中间积与双线性复杂度是已有基础，本轮五乘法构造按特定实例归属。[作者出版列表](https://members.loria.fr/PZimmermann/papers/)。
4. **Sparse Polynomial Interpolation and Testing**，Andrew Arnold，2016。稀疏插值、稀疏性测试和同态测试已有系统研究，不能以本轮独立推导作为首次证据。[大学库](https://uwspace.uwaterloo.ca/items/c05cc165-fc2d-4e22-80e4-2d81ae1111bf)。
5. **Lightweight Authentication of Web Data via Garble-Then-Prove**，USENIX Security 2024。其低成本方法利用最终允许证明方获得相关秘密的条件；本研究原定 TLS 非导出目标不能直接沿用该条件。[原文](https://www.usenix.org/system/files/usenixsecurity24-xie-xiang.pdf)。本核验内核仍未替代其计算正确性证明。
6. **TLShare: Private Authenticated MPC and FHE Inputs Over TLS**，2025 初稿，档案当前标注 CIC 2026。认证 TLS 数据导入私密计算已经是直接先例。[档案与最新出版信息](https://eprint.iacr.org/2025/1434)。本轮没有以摘要排除其全部构造范围。

上述来源支持“重合风险必须认真审查”，不支持“本方案已被确认完全等价”，也不支持“尚未搜到同名协议所以原创”。

## 当前应收缩的主张

整体新颖性保持 **NOT_ESTABLISHED**。数学工具均有先例；可能值得进一步核验的组合对象是：在无完整残差知情者、输入固定、拒绝分支也需隐藏数值的条件下，对有限失败数定位作隐私与可靠性共同分析。但这一组合是否已有直接实例仍未排除。

现有文献中“常数次乘法”与“批量验证”已经很强。不能把 31 个理想乘法门与未优化的全电路实现简单对比后称为算法优势；真实底座的预处理、输入认证、通信、打开和中止都必须计价。

## 必须保留的反方结论

- 本内核不验证输入残差来自真实 AES、真实 TLS 会话或正确的份额生成过程。
- 在两个秘密份额参与方中一方主动腐化的情况下，所有接口都需要真实的状态认证与一致性保护；Python 不变性检查不够。
- 任何秘密输出的持久存储、跨调用绑定和不开放见证验证仍属于原协议未完成部分。
- 在一般失败数下，原型返回 MANY，而非完整定位；在掩码预算耗尽时可能已披露部分位置，故必须采用文档中的允许泄漏定义。
- 试验时间来自明文算术解释器，不能换算为 MPC 或 TLS 性能。
- 若强对照已以相同保证、相同输入条件和相近成本实现该功能，应将本成果收缩为受限实例化或工程验证。

## 下一步进入条件

先完成与既有一稀疏/多稀疏审计的逐式映射，再选择一个真实主动安全秘密共享底座，明确输入固定和公开挑战生成协议。只有当完整输入—残差—输出份额链已经绑定，才进行 TLS 端到端实验。新颖性、代数正确性、底座实现安全和系统效果分别验收。
