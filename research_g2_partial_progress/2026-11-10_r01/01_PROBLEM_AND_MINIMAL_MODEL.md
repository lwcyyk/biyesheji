# 研究问题与最小模型

## 1. 唯一场景

LOST已发生，i为任务甲的一次已持久放行Refresh，p为父材料，c为潜在直接子代。用户撤回gA_v0，乙gB_v0拥有独立有效支持b并请求一次UserInfo。甲尚无原生关闭依据。用户/可信执行器只使用当前权威和合法证据，隐藏AS真值不作为选择输入。

目标是同时保存C_local、乙当前准入、甲未结责任与各项费用；C_native和C_effect只在其本身合同达到时报告。安全、局部操作完成、原生效果与有界全局闭合分别管理。

## 2. 组合状态

\[
\Sigma=(D_v,K,O_{global},E,P,C,Budget,History).
\]

- D_v：当前持久权威，包含grant/rid/attempt/origin/generation/phase/reserved/spent等；v为authority_state.version。本轮epoch若使用即这个权威顺序引用，不等同P03原生root-epoch或AS fence。
- K：满足已观察历史及固定profile的全部相容状态/其可靠上近似；可含未发送、未完成、已创建未收到、已迟到等。AS控制位置仅为证明ghost。
- O_global：当前权威/材料/处置/窗口及证据的类型化责任投影，沿用同一权威，不另造平行批准数据库。
- E/P：可靠证据与版本固定的原生/执行覆盖合同；含直接容量、来源完整、接受路径、b独立/窗口、无绕行等条件。
- C：结构化局部证书及依赖引用；签名/存储形式单独选择，本轮没有生成密码学对象。
- Budget/History：真实各批准reserved/spent、原生机会、计划余量、已发生/预付费用及不可删除的来源/结清凭证。

新证书/依赖投影均为设计。现有源码支持当前权威和请求状态/收据，完整typed ledger/证书验证/AB调度接入尚未实现。

## 3. 对R03四节点的最小必要细化

R03为局部动作摘要：pending_active→pending_revoked→B_observed或B_unknown。要讨论崩溃/费用，需要显式加入一次B_RELEASED_PENDING；否则“B已放行后崩溃”无法表现其spent和执行结果责任。

| 状态 | 甲批准/原生状态 | 乙 | 必须保留责任 |
|---|---|---|---|
| q0 | gA有效；i未知 | gB有效/b独立适用 | settle:i（创建/来源/迟到结果包络） |
| q1 | gA已撤回，C_local有依据；c仍未知 | 尚未放行本次B请求 | settle:i、close:p |
| q2（新增） | 同q1 | B已release，结果未知 | 上述＋exec:rB |
| q3 | 同q1 | 已取得本次B可信成功结果 | 甲责任不变，B执行结果义务结清 |
| q4 | 同q1 | B响应丢失/结果未知 | 甲责任不变，exec:rB继续 |

必要性反例：q1上把B看作原子成功/失败，真实release后、结果登记前崩溃会遗漏B的已扣预算与未知请求。即使UserInfo的Token表创建容量为0，它仍有执行/审计责任；不能把这个结果未知计为新凭据创建。

子代证据/处置再细化为qC_known、qA_native_closed等状态，理由是它们改变义务类型和可签发的具体性质。qA_native_closed允许仍有与本声明无关的B结果或A handler终态审计责任；全局台账持续显示这些项。

## 4. 事件及两类调用

事件包括CommitRevoke、Claim、Release、NativeOutcome、LateEvidence、ConvertObligation、DisposeObservation、Recover、Issue/CheckCertificate及带证据的依赖变更。

本轮Claim对齐AuthorityStore.admit，仅作排队预留；Release对齐release，产生DISPATCHED_UNKNOWN与spent。实际HTTP发送、AS处理和创建分别发生。若其他协议把Claim定义为不可逆效果领取，需另行映射。

受控调用分为：

1. 权威事件：有效用户管理请求，由当前权威按事务处理，不经过完成目标W门。
2. 局部安全动作：B的一次已获准UserInfo等，必须通过SafeLocal及当前最终准入，结果可以UNKNOWN。
3. 规划动作：涉及共享资源、潜在新创建/派生、配置替换、补证或清理的组合，调用原W或其他明确且经过证明的规划合同；不能仅凭“局部”标签绕过它。

## 5. 安全目标与进展边界

Inv包括：当前身份/批准约束；revoke后旧grant无新release；旧请求来源和spent保持；每个真实未结风险有相应责任/容量上界；证书不扩大范围；真实与模型预算保守；晚到不重新激活甲；乙动作在其合同下不引入未托管副作用。

乙独立性还需检查共享账户/user/client配置、原生影响域、预算和执行边界。原生根独立不能消除共享请求配额的耦合。相反，共享根也不意味着每个只读调用都应一律拒绝：本轮“独立B”证书路线必须退出，其他动作能否安全需完整关系/干预证明。

“及时撤回”指权威处理不依赖甲全局闭合；有限墙钟延迟/最终提交另需存储可用与调度公平。乙准入不等于乙原生调用必成功。永久UNKNOWN的轨迹可保持安全，但不获得原W完整终态或原生效果停止证书。
