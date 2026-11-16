# 独立管理批准下的合法 Q 路线

证据：C01:161—259、264—327；C02:103—151；C03:41—149；C06—C09。以下为源码允许的条件轨迹，本轮无执行。

## 1. 身份、批准与材料分别成立

gV 是新任务的本地批准，不自动创建新 AS 用户、OAuth grant 或独立撤销根。固定账户/组织/application 可与甲乙相同；可证明的材料隔离取决于 fresh Token/RT hash、动作范围和外部写入排除。

基础及 M6 的 user 没有 call。专用 verifier 身份尚未接线。合法候选路径采用**已配置 caller**，例如将验证任务独立委托给 agentA 的新 task/generation；gA 撤回不等同禁用该 caller 的全部未来批准。若安全合同要求可信管理执行器自行完成，当前须标记 `INTERFACE_BLOCKED`，保留角色配置及可信执行缺口。

user 创建 gV 时明确绑定：approval_op、caller、verification task、account、audience、generation、operations、budget、合法 casdoor_login。不读取或导出本轮真实凭据；这里只检查 schema 和来源条件。账户须属于 NativeHTTP allowlist，audience/client须匹配，API和客户端策略须允许 password/refresh。

## 2. 完整顺序

1. 核验 gA 已持久撤回，旧 i1/i2及其历史 spent/来源责任保留；确认当前账户无 active reconciliation window。
2. user 用新 approval_op 批准 gV，允许 issue、refresh，预算至少2；批准版本/用户交互/RPC/持久化均记账。
3. 被批准 caller 用 hV、完整 gV 身份元组和新 rid `rV0` 提交 issue。准入 reserve 本地额度，release再核当前批准/窗口，写新 attempt_id和release_version。
4. C03发送一次 issue，返回材料经验签/账户client核验及可信登记，`rV0.phase=RESULT_AVAILABLE`。若 UNKNOWN，先保留 `j_issue`；当前不能绕开源守卫继续 refresh。
5. 同 caller、hV、同 task/account/audience/generation提交新 rid `rV1`，payload.source_rid=`rV0`。source_rid 是本地请求标识。C01要求 source 的完整 origin 与新请求一致且结果可用。
6. release创建独立 `j_refresh`，发送一次 Refresh；结果为可信登记的 z1 或 UNKNOWN。轮换开启时父 z0正常被删除，异常后继保留。
7. 验证任务结束，由管理者撤回 gV：队列取消、已知结果隔离，迟到结果仍回到 gV并隔离。已知 QUARANTINED 才能走现有 dispose；未知责任继续托管。
8. 恢复、查询、必要处置、乙的操作及完整审计按实际权限和范围完成。Q不携带旧 i1/i2的终态收据。

## 3. 批准不等于程序化序列约束

operations={issue,refresh}和budget=2只限制允许动作与数量；它也允许两次issue。当前 grant schema没有“一次issue后一次refresh”的阶段机。纸面路线选择该顺序时，需信任执行策略；若交给有偏离可能的caller，安全外包络必须覆盖全部允许放行。

在严格单次调用/handler假设下，两次创建release的持久单位容量总和至多2。若开放更多预算/重试/外部持有者，按全部机会加总；不能借用旧 i1/i2 的容量证明来省略新 j。适配器把材料留在可信域，降低代理直接拿RT的风险，仍需证明无旁路、泄漏和多活重放。

## 4. 互斥和来源限制

| 情形 | 实际结果/责任 |
|---|---|
| gA已撤回后直接刷新p | 原批准新release被拒绝 |
| gV引用gA的rP | origin不等，SOURCE_MATERIAL_UNAVAILABLE |
| gV新Issue结果UNKNOWN | 缺RESULT_AVAILABLE源，refresh不能放行 |
| user直接调用call | 现有role拒绝 |
| 未配置verifier调用 | 身份或操作拒绝 |
| 窗口已active再grant | RECONCILIATION_CREATION_PAUSED |
| 窗口在grant后、release前active | issue/refresh拒绝或取消 |
| gV仍active时dispose其结果 | 无已知QUARANTINED材料，无法走现有处置 |
| gV撤回后结果迟到 | 保留gV原origin，记录QUARANTINED |

同账户创建第三grant后，C01:384的清单包括撤回项，现有枚举的2批准/20预算条件继续失配。撤回gV无法自动恢复旧manifest。若先开窗口再Q，创建受阻；若先Q再窗口，原单未知/两批准来源证明需重建。

## 5. 合法性裁决

`NATIVE_INTERFACE_CONFIRMED`：明确委托给已配置call身份、材料合法、无窗口、范围/预算/服务策略满足的参数路径。

`INTERFACE_BLOCKED`：默认管理user或未经配置的新verifier直接代发；窗口内新建/放行；跨origin借p。

`SOURCE_OR_REFINEMENT_GAP`：专用可信管理执行器、严格两阶段批准、所需诊断投影、未知Issue对账、多尝试关闭及有界恢复。代码级路径可行性保留；当前活服务、批准及账户可用性未作新核验。
