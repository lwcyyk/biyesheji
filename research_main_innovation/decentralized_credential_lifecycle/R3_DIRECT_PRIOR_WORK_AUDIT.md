# DCL-R3：直接先例与来源边界

2026-11-10。沿用R1完整题录与R2关键段对照，新增BFT、ORM/SQLite与持续使用控制一手来源。读取记录为evidence/r3/web；全论文工件复现与外部联系为0。

## 1. 成熟BFT与本实例归属

Miguel Castro、Barbara Liskov，*Practical Byzantine Fault Tolerance*，OSDI1999，173–186。[官方HTML](https://static.usenix.org/events/osdi99/full_papers/castro/castro_html/castro.html)。本轮实际核读§2 System Model、§3 Service Properties、§4 Algorithm中的normal-case、checkpoint、view-change、correctness与determinism。PDF入口有403/502，官方分节HTML可读。

原文提供固定成员确定性服务的线性化与签名版算法，checkpoint需认证状态，并明确可通过不同管理员/系统降低相关故障；隐私不由普通SMR自动提供。D1沿用该同epoch底座，把成员epoch与leader view区分。跨epoch顺序Seal/Transfer是本目录给出的应用层连接实例和证明，不冒称原文已经发表了该具体RHO协议。

[BFT-SMaRt官方Wiki](https://github.com/bft-smart/library/wiki/How-BFT-SMaRt-works)说明state transfer及依TTP发起的实验重配置。本轮读到该限定，未将它当成“任意成员无交集都自动安全”的证明。Sisi Duan、Haibin Zhang，*Foundations of Dynamic BFT*，S&P2022、[ePrint2022/597](https://eprint.iacr.org/2022/597)，提供动态BFT模型和Dyno的直接正式近邻；官方元数据/作者出版列表已核，PDF403，具体定义/定理正文SOURCE_UNRESOLVED。D1没有依赖未读Dyno定理。

PBFT只给固定成员底座，完整G可自由采用已验证的动态协议和标准状态转交优化。本文顺序停顿实例用于闭合安全规格，未据此认领动态BFT首创或通信/停顿优势。

## 2. 授权与原生效果

|来源|本轮重核/沿用范围|与R3重叠与边界|
|---|---|---|
|[AID-Guard v1](https://arxiv.org/html/2608.21159v1)|重核§III-D，沿用R2 §II–IV关键机制与proof sketches|当前授权、不可变请求、带费UNKNOWN、终态fence/单继任有直接覆盖；可信边界/原生合同前提保留|
|[Root-Scoped Quiescence v1](https://arxiv.org/html/2609.21284v1)|重核附录A.3通道/不透明端点，沿用R2 §§3–5与附录A|支持、责任转交、root cut/sink fence/channel accounting及不透明历史边界直接相关；它不把账本cut当作全部原生效果截止|
|[EFFECTBOUND v1](https://arxiv.org/html/2609.02866v1)|重核附录C-E，沿用有限模型/配置历史/Post/Inv|真实行为精化、证据不足与可实现性、跨配置声明保持已是直接近邻；真实Provider完整性仍是外部责任|
|SC-A2A Gateway|DOI10.1109/ACCESS.2026.3742942、IEEE Access14:163751–163772、2026-10-13；作者及摘要已核|本轮具体标题/公开实现搜索与官方document/PDF读取仍未取得正文。SOURCE_UNRESOLVED：预算/未知责任、旧Bearer、重配置状态与native frontier细节继续缺证|

SC-A2A作者出版列表仍保留过时Under Review标签，按正式出版记录区分。来源缺口不提供新颖性肯定或否定证据；它不妨碍使用已读AID/RQ/EB对本轮具体功能构造G。

## 3. 持续控制与成本

Jaehong Park、Ravi Sandhu，*The UCONABC Usage Control Model*，ACM TISSEC7(1):128–174，2004，DOI[10.1145/984334.984339](https://doi.org/10.1145/984334.984339)。本轮取得[47页作者PDF](https://profsandhu.com/journals/tissec/p128-park.pdf)，核读摘要、PDF13页的模型分类段及continuity/mutability定位（web09）；其余正文未逐节重审。持续控制与属性变化给动态授权复审的直接基础。已有本地历史XACML/历史暴露联审标准组合继续有效。

D2累计费用阈值游戏属于标准有限状态/资源扩展方法；本轮给出自包含可靠性/完备性证明。最大累计费用按物理状态保留的引理需其Markov与不可见费用条件，独立先例优先权未核定；G可使用同一保持变换，当前无严格算法分离。

## 4. NC独立证据

固定XORM v1.1.6的Engine/Session源码、SQLite官方事务/隔离说明补上R2的DB层依赖；本轮还读object/ormer.go与session锁作用域。它们支持SOURCE_FEASIBLE调度，不承担实际二进制/DB配置的完整符合性。所有安全发现保持静态作用域，生产漏洞/发表优先权继续独立审查。
