# 真实字段、四份O与证明精化

40项字段逐项分类见`REAL_TO_SYNTHETIC_FIELD_MAP.json`。映射已定义包含“实际缺失”这一结论，完整生产精化继续待完成。

## 六种版本

SQL user_version描述数据库结构；a为旧包装器调用世界版本；o为未来typed O语义版本；evidence_version属于证据生产者；Native版本/部署/frame属于AS；proposal ID/body/ledger属于幂等身份。Controller.boot是控制器一次启动标识，目录也不是持久DB实例身份证据。当前state没有authority_instance或o。

单次SELECT的a和ciphertext相互配对，但a不在当前AES-GCM AAD中；其可靠性依赖可信本地主机/数据库和无回滚前提。局部a不涵盖Provider、AS、外部配置或密钥生命周期。

## 四份 O 的实际位置

| 对象 | 当前真实支持与适配责任 |
|---|---|
| O_before | 当前只有由持久phase/window派生的legacy rid视图。完整持久typed O缺失；B1须将`legacy_obligations`与`conservative_O_view`分别命名，typed base/o以null和缺口表示 |
| O_projection | 当前S1输出obligations_proposed，但其入口限定合成。真实来源/模式桥尚缺；B1可独立展示待结风险与缺项，不能据此宣称已执行真实S1 |
| O_proof_context | 原包bindings.O_before绑定相应S1提案；原摘要算法和包保持，不能解释为DB读取 |
| O_after | 仅未来B2在真实锁内核CAS、覆盖与授权，并成功提交后才能成为生产权威状态 |

A08/A24的5→6是R10合成运行证据。本轮真实接口要求能表达同类新增close/await风险，当前没有读取真实数据去验证相同数值。旧DISPOSED和CLOSED会从legacy视图移除部分rid；新的来源/审计/持续失活债务仍应以staging hold保留，避免空legacy列表被解释为全局完成。

## S1入口的具体差异

`RequestSnapshot.parse`要求完整original_request，其中handle参与现有request_digest重算。公开净化输出移除handle后，原Schema和原摘要校验路径都不能直接复用。替换成占位handle再保留旧digest会失配。[C08:140–170]

可供以后评审的方向为：可信域内私有原请求校验/计算只输出净化结果，或有来源约束的redacted-request新版接口。现有S1的mode、FrozenTrust以及证据生产者/permit模型仍限定合成，以上任何方式还需真实信任入口。B1只输出`S1_V1_REDACTION_CONTRACT_GAP`，保持旧Schema与测试原样。[C08:358–377;C09:36–75]

B1输出校验记录来自可信宿主在源端的真实摘要计算，并绑定snapshot、a和tuple；普通payload中的verified/source_confirmed布尔值不进入信任来源。

## S2及S3-A复用边界

| 部件 | 可复用内容 | 尚需接线 |
|---|---|---|
| S2 math normalization/网络/证书 | I/T/c/U/E/D_P上的数学推导及独立校验 | 真实输入的可靠来源、有限容量、出生代次和D路径前提 |
| S3-A数据helper | 规范JSON、域分离hash、严格界、旧描述保守保留 | 实际ID规则/敏感性/源scope契约要匹配 |
| Prepare/Validate | 已测试的提案/预算/保守覆盖责任链 | 当前world含fixture_key/simulation，Registry固定R07包及路径；Validate还读checker源码，不能视为无环境依赖的生产纯函数 |
| SyntheticStore | 已验证事务顺序、约束和故障预期 | 路径、marker、四表和明文codec专用；生产需新加密事务适配层 |

S3-A的Actor只封装name；真实鉴权须来自服务端认证上下文。B1保持R10源码不变。B2若提取公共策略接口，应单独给最小重构与回归授权，避免复制O规则或优化算法。

ID合同也有实际差异：legacy标识通常为80字符，S1允许160字符及`/`，S3-A当前ident为128字符且不含`/`。真实`admin/<unit>`不能直接塞入S3-A的obligation ID。以后需要受控、可恢复的不透明别名映射并保留原ID出处；截断、删字符或仅比较显示名会丢失绑定。[C03:43–46;C08:59–62;C11:56–59]

## Native currentness and refinement gaps

I至少需已放行creator及全部相关竞争源；排队和未来调用需入前沿。c_i=1仅在G1 A01–A07的单dispatch/传输/handler/源/DB前提下成立；预算余额和NativeHTTP COUNT不能替代该证明。COUNT在network前预记账，不能作为AS已执行/创建下界。[M01]

U需要service/database/nativeID/出生代次及累计历史。签名JTI或最后一份lookup只提供部分信息，已删除单位也可能仍需保留见证。E保留全部相容来源；本地五元只能在可信正向结果时收紧。D_P需要指定接受路径、持续frame和有效时点；legacy DISPOSED、单次userinfo/introspect或revoke响应不足。[C09:179–255;M02]

以下情形仍缺独立证据：旧Refresh已读父后迟到插入；本地a/o不变而AS变；新批准或外部RT持有者产生更多机会；只读快照后出现材料；时点失活后来恢复/其他路径接受；源码版本和实际二进制/配置不一致。配置字符串4.25.0未证明部署忠实。

容量饱和可在可靠全源上界与互异创建下界下排除对应直接剩余容量，前沿/后代/审计/业务效果分别保持。B1为本地事实净化；B2为真实本地持久事务；B3才审真实来源资格，且S5实验授权另立。B1/B2均保持native_admission=SOURCE_OR_REFINEMENT_GAP、global_complete=false。
