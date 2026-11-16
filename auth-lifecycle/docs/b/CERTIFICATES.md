# 配置冲突和独立核验

`certificates.produce` 生成不可信 JSON 证明，`checker.check_conflict` 重新解释原始契约核验，不调用候选生成器或其 planner。

证书包含模型 SHA-256、完整模型快照（任务、凭据、效果域、全部接口、批准、预算和场景）、约束引用、作用域、逐配置反证。哈希不代表外部证据真实性。快照使用 canonical JSON 比较，布尔值不能冒充数值。

作用域严格区分：

- `fixed_configuration`：仅此配置不能在该 H/预算内实现全部指定场景；更换配置可能成功。
- `finite_catalog`：当前有限目录内的全部配置都不能交付各场景所需计划。

两者都不是“所有可获准观察策略均不可实现”，也不涵盖未列出的接口、补证、重绑或更长生命周期。不接受把 scope 改成一般观察策略不可行的证书。

每个配置由以下一种原因覆盖：

1. `invalid`：独立检查器复算具体 constraint_refs，例如缺任务路径、错账户、权限范围不足、批准缺失或预算超限。
2. `unplannable`：给出一个确实失败的场景及完整有界反证树；每个尚未使用的允许动作必须出现。分支提供真实阻塞约束，或对应确定后继的子反证。只有剩余步数为零时允许 horizon 叶，已经达到目标的状态不能被反证。

全目录证书按 `sorted(paths)` 的所有 `2^P` 个位掩码固定顺序覆盖，检查器自行生成期望目录；遗漏一个配置、动作或替换预算/批准都会被拒绝。证明采用“重复单调动作无益”缩减，所以不列已经执行过的动作；其前提详见 MODEL.md，不能用于会新增能力或退还预算的动作。

这是一种有限可检查覆盖证书，不声称最小核心；`minimality` 只能为 `not_claimed`。证书生产或检查未穷尽工作限额时返回 INCONCLUSIVE，不输出完整不可行结论。若找到可行配置，producer 返回 FEASIBLE 并停止生成冲突；该返回只表明存在可行解，最优性仍须 solve。

独立 G 审计入口 `checker.audit_G` 返回已取得授权、相交的原生效果域、逐域证据/操作/coverage 和 G。它明确报告 `token_labels_used_for_counting=false`。同一效果域内多个 grant/token 别名计为一；相同 token 标签不会将两个已登记的独立效果域合并。

样例见 `examples/b/shared_root_conflict.json` 及 `results/b/final01/artifacts/shared_root_remote_conflict.json`。当前保存完整背景和引用以便审核，没有用缺少两世界反例或权限贪心未找到方案替代不可行证明。
