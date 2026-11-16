# 待用户明确批准的合同文本

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


建议裁决：**APPROVE_RECOMMENDED**，范围仅限下列带先决条件的规则草案。该建议与用户批准、实现许可、动态执行许可及实际证书可用性分别登记；当前user_approved=false。

1. 原合同：B当批完成身份/运行时/资源、正常C09/ManagerRecovery及全部强制校准；强化验收还要求同批先完成主关闭异常场景再进入F1/F4。四条生命周期条件共同形成冲突。
2. 拟修订的唯一条款：允许独立A已实际完成并经原始字节复核的“专用原生服务故障→未审查失败识别→主A自动安全关闭”观察，作为B该有限实现能力观察项的条件性依据。其他资格条款保持。
3. 仅承认一个明确scenario、一个精确受审artifact pair、同一boot/等价关键TCB及一个预声明B。A未实际触发、未确认退出/组空、主自动路径失败、native/admin不完整或必需UNKNOWN均拒绝该类承认。
4. B必须重新证明当前boot、锁、单位、UID/GID、binary/maps、budget/T0/deadline/WORK、C00、真实C09、正常MR、当前监督/停止前提及所有原有C/S/门/资源强制项。A任何窗口、收据和预算均不转移。
5. A/B源锁均精确绑定。仅逐AST节点审阅的namespace字面量差异可以进入对应关系，安全控制流/数值/权限/pin/故障要求保持。approved_pairs表填实且经明确审核后方可应用，当前表为空。
6. 保留既有Root/kernel/systemd/存储与条件性运行时来源TCB；如无法接受这些前提则规则不可用。哈希不替代来源证明，主机合成数据不构成原生事件。
7. 所有当前必需raw/query/journal/ACK/退出/预算/关闭/封存及独立oracle程序和结果字节均需可取得。C_A在A封存后生成于其前像外，固定native/admin两个包及其manifest hash；不可为了取得证书回写旧包。
8. 当前B直接用户授权固定rule/CA/use_spec摘要及新nonce，现有once/新鲜namespace约束继续适用。任一撤销、版本/boot/TCB/fault scope/目标/锁变化使承认失效；未知撤销状态拒绝。当前没有部署额外防回滚注册表。
9. 攻击验收至少覆盖旧版本/旧boot重放、伪造原生事件、未触发、错误身份/InvocationID、缺退出、fallback-only、部分seal、checker共同错误、缺/换文件、预算转移与use重放。逐项拒绝规则见附件，测试当前尚未执行。
10. 资格门影响仅限经批准替换该强化的异常观察项，并增加CA适用性检查。RESOURCE_GATE仍由B全部当批条件合取决定。D1/D2语义、F1/F4有限域、PASS_BOUNDED条件和原创性裁决保持。
11. 规则本身记录有限经验性能力观察及其适用假设；不构成B关闭已发生、任意故障必定关闭或未来实例安全的无条件证明。
12. 额外行为需分别明确授权：实际gate/证据承认代码适配；最终源/合同/argv锁；修改4452/4451等容量字段；独立A动态注入/封存；新B完整校准与条件F1/F4。批准本文草案不会自动授权这些执行。
13. 生效前未决项：源码等价pair实填、raw日志/字节/工作量合同闭合、独立A真实验收、当前B精确使用授权、未来承认器的独立安全审查。当前这些前提尚未全部具备，任何实际证书均不可登记为已有效。
14. 本文的批准对象为与MR_CROSS_INSTANCE_RULE_DRAFT.json绑定的有限规则，实施与使用继续受以上先决条件约束。用户明确批准文字应引用该规则版本及最终交付中的SHA-256；本轮没有代用户勾选或生成批准回执。

待批准文本：

> 我批准MR-CROSS-INSTANCE-OBSERVATION-RULE/1-DRAFT所列的限定同boot、单目标B、精确受审源码对及原生场景观察承认原则，并保留全部当前B独立资格要求。此批准仅允许后续提交具体实现/执行申请；实际适配、容量变更、MR注入和F1/F4仍需按精确工件与范围另行明确授权。

规则附件SHA-256：`3ff536a551ea971304bc9478c81a54169e138cd9d172a0d6d61bf67f6994e021`。批准文字可直接引用此摘要；附件当前user_approved=false。

当前记录：**PENDING_USER_APPROVAL**；证书适用性：**NOT_USABLE_NOW**。

[规则附件](proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json) · [攻击拒绝条件](proposals/ATTACK_REJECTION_MATRIX.json) · [源码pair要求](proposals/SOURCE_PAIR_REVIEW_REQUIREMENTS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
