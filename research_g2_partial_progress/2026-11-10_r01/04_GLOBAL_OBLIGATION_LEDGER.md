# 全局义务与O1—O6

## 1. 单一权威与类型

O_global为当前持久请求/材料/处置/窗口及可靠证据的保守责任视图，源为同一D_v和历史。新的typed投影尚未实现；现有storage.state_projection从DISPATCHED_UNKNOWN/QUARANTINED及未闭窗口提取义务，可作为工程基础。

| 类型 | 覆盖的风险/待决事实 | 关闭依据 |
|---|---|---|
| settle:i | 甲未知创建、来源、可能迟到材料，及按profile需保留的后继 | 可靠创建/终态与容量证明；未排除部分继续保留 |
| close:p / close:c | 已知甲材料在声明路径的潜在可用性及处置 | 来源绑定、原生失效与持续范围证据 |
| exec:rB | 已放行乙调用的执行/结果未知 | 同rid/attempt的可靠结果或范围明确的终态；不计为新token创建 |
| await_terminal:i（必要时） | 原handler/交付终态仍未确认的审计责任 | 可信响应/终态及源语义；单独明确是否涉及可用材料风险 |
| window:account（存在时） | 已打开的对账/创建暂停及尚未满足的退出条件 | 当前窗口合同与实际API所需证据；材料scope证书不自动关闭窗口 |
| effect:w（扩域时） | 已接纳业务工作仍可能产生被禁止效果 | sink/通道前沿及终态合同；当前UserInfo切片不声称已覆盖 |

历史rid、origin、spent及已结清见证保存于History/tombstone，不能因active义务移除而删除。恢复/幂等/累计创建U仍依赖这些历史。

## 2. 覆盖不变量

对每个相容真实s，定义R_req(s)为本合同要求托管的潜在创建、可用材料、未知请求/来源、派生及业务效果责任。每个o的语义⟦o⟧给出其覆盖范围/上界；要求

\[
R_{req}(s)\subseteq\bigcup_{o\in O_{global}}\llbracket o\rrbracket,
\quad s\in\gamma(K).
\]

标签数量不等于风险个数，set也无需只增不减；责任转换/可信排除允许变化，覆盖必须保持。当前未知真实材料无需一个实际handle才能有settle项；预算/容量未知时不能擅设有限小值。

常规有效批准下的已知p/b作为资源留在D中，不自动要求立即关闭；撤回目标、未知创建/结果等产生本合同待处置或待核责任。CommitRevoke扩展待处理风险范围时，同一权威更新/投影必须相应增close项。否则“有效材料全部都算未结关闭风险”的定义会与本例初态不一致。

## 3. 转换规则

| 事件 | 旧义务→新义务 | 必需前提/费用 |
|---|---|---|
| CommitRevoke A | 保留settle:i，按需增close:p | 无新增native关闭；来源/spent不变 |
| Release B | O_A→O_A∪{exec:rB} | 先持久attempt/消费，再发送；结果未知继续保留 |
| B可信结果 | exec:rB→已结结果记录；O_A原样 | 原请求绑定且结果语义正确；b束重复出现不新增U |
| B结果丢失 | exec:rB保持；O_A原样 | native0创建不等于没有执行结果责任 |
| 发现同源c但未饱和 | settle:i→settle:i＋close:c | 可见一份不排除更多，需保留剩余上界/其他来源 |
| 同源c、上界饱和 | settle:i创建部分→close:c，保留未满足的结果/handler等剩余项 | c_i=1、真实互异见证、未来重试/派生全部计入或封口；须有真实源/创建证据 |
| 处置c且持续失效 | close:c→结清tombstone | 接受路径/后代/原生单位覆盖可靠；处置UNKNOWN不清除 |
| 取得无效果/终态证据 | 对应部分settle/await项结清 | 必须验证证据范围与源前提，超时/空列表不提供它 |
| 新刷新/补证有副作用 | 新attempt及相应创建/执行义务加入 | 批准/容量/来源/预算完整；不能以补证名义漏记 |

若可靠c证据只足够关闭创建前沿，却未证明原handler完整终止/响应归档，await_terminal:i继续显示。它若被证明不再影响A材料可用scope，允许一个明确排除handler终止的Cert_native_close；原全局义务和C_effect并未因此完成。

## 4. O1—O6证明

**O1责任不丢。** 初始化由G1包含。每类Release在外部效果前建立责任上界；可信证据只能缩相容集或转换为覆盖同风险的新项；删除须有逐scope证明。对事件序列归纳得到上述包含。真实源/全部创建路径完整仍是前提。

**O2撤回不清责。** CommitRevoke只改批准/队列/隔离，i已release项来源/spent不删；Ledger投影保留它并加待处置known材料。状态GLOBAL_OBLIGATION_PRESERVED（模型内）。

**O3局部进展不覆盖全局。** Issue/Check B证书为读/记录动作，不执行删除A责任；Release/Outcome B仅增减自己的exec:rB。跨任务别名/共享影响必须在frame或依赖中暴露，否则拒绝独立路线。

**O4转换保来源。** 证据携带rid/digest/origin/attempt/release_version，转换继承原grant/task/generation与native占位映射；迟到不能归到gB或新generation。冲突保留证据/旧义务，F为空返回CONFLICT/UNKNOWN。

**O5恢复保持。** 当前权威/密钥可用且无回滚时，恢复重建同一或更保守责任视图；cache只显示。新证书在当前依赖重核前无准入权。全设备丢失/旧权威自身回滚/多主未证，继续SOURCE_OR_REFINEMENT_GAP。

**O6费用保持。** 已release的spent和原生机会/失败/读取/清理费用不由局部证书或UNKNOWN返还；QUEUED取消只退未放行reserved；已结记录可压缩但保留累计见证与费用。每次补证/清理/恢复重新计其真实路径。

## 5. 范围与资源

义务可永久UNKNOWN，系统仍可给其他独立操作当前准入；这不提供甲最终关闭/有界完成。存储配额和恢复能力必须可持续：新请求若无法可靠持久化其责任就拒绝，不能静默丢旧项。对固定本例O规模有限，对不断新任务需要容量/保留策略及完整维护成本，属于G2扩域责任。

现有代码的typed风险细分、await_terminal状态、分scope原生关闭及证书引用未全部接入；纸面全局视图不会替代原AuthorityStore。成熟持久工作流/事务外发台账也可执行相同规则，见07。
