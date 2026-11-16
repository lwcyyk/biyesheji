# 字段级 ProjectEvidence 纸面规格

接口版本：`readonly-lifecycle-projection/1`。分类P：设计合同，未实现、未运行检查器。函数接受已获取的材料，读取/提交由受控外层负责。

## 1. 输入字段

| 字段组 | 必需字段/类型 | 实际来源与缺项行为 |
|---|---|---|
| authority | instance_ref、snapshot_version、read_ref、trusted_recovery_ref | C01.read_state/recover；单活/不回滚为合同，instance/恢复链字段需最小扩展 |
| grants | grant_id、caller/task/account/audience/generation、active、operations、limit/reserved/spent、creation_gate | C01批准；material不公开；快照无操作域时不能推未来创建封口 |
| requests | rid、digest、origin、attempt_id、release_version、phase、operation、source_rid、result_ref、disposal_refs | 前六项公开已有；其余由可信内部state或digest验证正文导出，禁止凭未鉴别AI叙述补齐 |
| attempts | attempt_key、creator_kind、c_i、capacity_contract_ref、dispatch/terminal evidence、frontier_scope | M02/G1与真实账本；direct/lifecycle分开；无界记未知 |
| evidence envelope | evidence_id、kind、producer/transport_ref、approval_scope、query_ref/parameters、event interval、received_at、profile/source_ref、payload_ref、integrity/provenance status | 可信Collector生成；日志monotonic_ns仅在可比较进程域使用 |
| creation witnesses | unit_key=(issuer/database_instance,owner/name,birth_ref)、account/app、native_jti_ref、creation_ref | C03/C10/G1；ID Token jti不另计；复用ID缺代次则保持别名歧义 |
| named observation | unit_key、path、performed、HTTP、active/accepted、sub、observation interval、errors | C13归一语义；未调用与false分开；token原值只在可信材料仓 |
| snapshot manifest | authorized org/account/app universe、query/filter/page、response完整性、Find范围、record_bound及依据、writer inventory、baseline/history refs | C04/C05/H01/H02；count与Find分离，第三grant重建 |
| obligations/cost | 原O及revision、历史/新增机会、预算与存储界、当前目标/路径/时间frame | 权威/费用账；无法持久保责时停止新增动作 |

所有引用需能在权限范围内解析；字段名含verified/complete只是一项声明，必须关联其验证规则和证据。

U只选有证明的互异创建下界。两个观察是否同一birth尚未确定时，不把它们都强行计入U，也不把可能不同的材料永久合并；保留别名分歧、未计数观察和材料风险，交给剩余容量/开放前沿覆盖。若这种分歧影响闭合，返回UNKNOWN。

## 2. 输出字段

| 输出 | 含义/证明依据 |
|---|---|
| observations[] | 直接事实，保留原字段、时间、来源/权限、错误和历史获取费用 |
| created_confirmed[] / U | 可靠创建下界及去重代次；inbox/journal/原生行与源映射联合支持 |
| material_aliases[] | 同一创建的多引用；未证明同一性时保留可能别名，不能重复计容量 |
| origin_edges / feasible_origin_status | E和F可行性状态；精确与可能边分别记录；有证明才删边 |
| capacity_bounds | c_i、C_T、m_T/d_T/R_T/H_T及所用I/T/U/D/合同；未完成计算填UNKNOWN，不伪造值 |
| possible_creations / open_frontiers | 未观察/未来创建及未覆盖写入者、重试、派生；始终可含匿名材料占位 |
| inactivity_observations / D_by_scope | 点时失活与持续失活证明分开；D按路径/frame管理 |
| native_relation_uncertainty | 共享RT组、账户级影响、接受路径和版本未决 |
| obligations_next / history_delta | 新O、每项转换依据、保留tombstone；不暴露长期secret |
| K_view / AB_dependencies | 来源/风险及批准/预算/路径的可靠过近似，非真实世界oracle |
| scope/version/dependencies | authority基准、证据/模型/profile版本、有效窗口、读取权限、依赖摘要及重核要求 |
| issues[] / statuses[] | unauthorized、conflict、stale、coverage、frontier、refinement逐项分类；可与独立局部证书共存 |

输出仅是对账提案。提交须在同一权威事务检查基准revision与依赖，把O转换、历史、费用及证书引用一起持久；并发变化时重投影。AS异步变化不会自动增加authority version，原生时间/frame须独立重核。

## 3. 规则 R01—R14

| 规则 | 前提/动作 | 保守失败行为 |
|---|---|---|
| R01 身份/权限 | 验证原生读批准、Collector身份、scope及使用权限 | 无权片段拒绝，不用其缩K；其他独立证据可保留 |
| R02 权威连接 | origin、rid、attempt、digest、release_version与当前可信历史一致 | 伪造拒绝；可信来源矛盾记冲突；旧快照先恢复 |
| R03 原请求 | operation/source_rid来自可信state或规范摘要匹配正文 | 不猜Issue/Refresh、父子；保留SOURCE_OR_REFINEMENT_GAP |
| R04 见证归一 | 多来源证明指向同一birth的单位，只计一次 | 代次未知保留别名集合；不靠三字符串计三单位 |
| R05 历史保留 | 已删除/失活材料仍保留U及来源；当前快照另存 | 无历史全集则不能重算成“从未创建” |
| R06 来源图 | 真实来源⊆E，加入全部可能创建者/外部来源；精确证据才缩边 | 不把同账户/近时间强制给某个i |
| R07 容量 | 独立证明各c_i；确认互异见证消费容量 | H账本不作创建下界；未知派生阻止全域数值闭合 |
| R08 可行性 | F非空才计算Γ和容量极值 | 空F→EVIDENCE_CONFLICT；未算→UNKNOWN，均无关闭许可 |
| R09 失活 | 按路径/时点接纳观察；持续frame与后代覆盖满足才加入D_P | 内省false不解释成刷新失败/无后代 |
| R10 负证据 | 按04的存在性、全集、前沿、接受路径分别使用 | 空inbox/日志/列表仅给局部缺失，不减c_i |
| R11 O转换 | 对全部相容来源保风险；饱和创建部分可转材料处置/分组义务 | 未知来源/剩余前沿/handler审计继续保留 |
| R12 当前提交 | 对authority、evidence epoch、frame及权限依赖重核 | authority变化重基准；AS前沿未证不靠version蒙混 |
| R13 局部证书 | 分别证明C_local/B许可/材料C_native；引用未结O | 不把局部true转成全局完成 |
| R14 成本/隐私 | 历史与新增读取、计算/存储/RPC/重试计账；向AI裁剪 | 缺证/预算不足拒绝进一步获取，保留O |

这些规则是标准可信投影、事务和来源图的领域规格。其运行复杂度和实现由后续实施评审确定，本轮没有生成投影函数或检查器代码。
