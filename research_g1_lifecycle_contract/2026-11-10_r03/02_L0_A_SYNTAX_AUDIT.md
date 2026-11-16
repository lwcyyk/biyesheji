# 当前L0/A语法与语义审查

路径根：`D:/毕业设计/auth-lifecycle/src/auth_lifecycle/`；具体哈希与行范围见evidence/SOURCE_LOCK.json。以下结论源于文本读取，未调用这些模块。

## 1. 通用L0的实际数据合同

schema.py定义State(knowledge,remaining,boundary)，Ref=(world,state)，MAX_TASKS=4、MAX_HORIZON=8。world提供semantics字符串、native_roots和state目录；state字段为account/facts/approvals/budget/capabilities/obligations/transitions。facts、capabilities、obligations是唯一非空字符串列表；budget为任意非负整数键值。L0没有强制的typed credential/attempt/provenance对象。

action字段为task/account/approval/cost/requires/independent/kind/operation；kind可probe/control/wait。前置条件对K全部状态检查：安全、account、approval、requires、预算、independent的native_roots异值及非空后继。

edge显式提供observation/target/effects/delta。delta包括facts/capabilities/obligations增删、withdraw_approvals和external_debit。schema要求目标集合与delta相等、批准只撤回、预算按同一资源逐键扣减。probe新增cap需有close:<cap>严格义务；移除cap时对应close义务须已消失，close前缀义务须有相应cap。普通settle:i这类义务可独立存在，适合表示尚未确定出现的材料责任。

这些字段允许手工有限编码；标签真实性/原生意义、来源绑定和容量定理不由字符串检查获得。

## 2. 核心语义与检查器

| 源码符号 | 实际保证/边界 |
|---|---|
| semantics.branches | 对K全部状态检查动作，按相同observation合并所有目标；每步h−1 |
| semantics.observe | 未登记/无效观察→boundary/空K，不能成功 |
| semantics.terminal | K非空、无boundary、全K安全/同账户/目标事实齐全/义务全空 |
| candidate.solve/allowed_actions | 有界AND/OR；完全求解后才给有限模型FEASIBLE/IMPOSSIBLE，限额为INCONCLUSIVE |
| _reference_kernel.expand/is_goal | 独立原始表解释；与参考和检查器共享，独立性按实际共享说明 |
| reference.solve | 可达知识图＋自底向上W求值，读同一有限表 |
| checker.check_policy | belief/h头匹配、观察分支全集、终态/义务检查；不能认证错误输入表的原生覆盖 |
| checker.check_impossibility | 绑定模型digest/查询/scope，核对所有动作或一条真实失败观察 | 
| BoundedController.step | 先对每个观察后继调用reference确认有界可胜，再调用adapter；异常/模型外退出 |
| abstraction.check_relation/lift_policy | 两个有限表的关系检查，cap/obligation标签identity映射；bindings仅检查callable；external_adapter_proof=NOT_PROVED |

W_h是“所有观察均能有界到完整终态”的屏障。一个动作即时合法/安全，仍可能因后继保留UNKNOWN且无法保证终态而被派发门拒绝；这与纯安全不变量监视分开。

## 3. A source的较窄约束

a/model.prepare只接受固定顶层字段；source.budget精确为requests/approvals；world为B模型，数量≤8，各world共享动作/批准/价目。probe每世界最多3次schedule、每次最多4条结果；edge只有observation/to_world/sessions/withdraw。setup后不允许to_world改变。cleanup只有known_handle/account_root两种，known_handle不能引用opaque:前缀。

point保存world/configuration/stopped/sessions/approved/budget/attempts/stop_steps/epoch。probe增加带probe/次数后缀的session；stop记录固定B动作；cleanup只按scope移除session。父子关系、已加载父pc、创建余量、迟到从opaque变成已知材料/句柄、持久reserve/spent均没有通用更新字段。它们可以部分编码为标签/世界/旁证，完整保持仍需逐条证明。

a/compiler只从这个source及plant构造bundle，goal固定stop_goal、严格义务来自sessions；a/audit用独立_plant_reference解释同一source。它不会接受任意手工L0表作为已经通过source审计的bundle。A1/AB选择器进一步读取source/properties/catalog/points，raw L0纸面表不自动成为其有效输入。

## 4. 对象映射分项

EXACT指本例有限值可以逐一编码；原生意义仍依G1关系。MISSING/UNSUPPORTED限定当前字段或直接路线，不宣称所有间接编码不可能。

| 真实对象 | 原始L0 | 当前A source直接路线 | 依据 |
|---|---|---|---|
| p引用/处置范围 | EXACT：facts/cap handle:p及原生scope引用 | CONSERVATIVE：B credentials p/固定域 | 原生可用性与引用持有分开 |
| attempt i | EXACT：固定ID事实/状态/settle:i | CONSERVATIVE：probe计次＋scope/session后缀 | typed rid/attempt持久绑定需旁证 |
| 潜在c | CONSERVATIVE：未结义务＋隐藏state | CONSERVATIVE：opaque session | 保留责任可行，精准迟到解除另证 |
| 批准版本 | EXACT：冻结标签及withdraw | CONSERVATIVE：approved/withdraw | 真实当前权威映射未实现；批准撤回不自动关闭B gates |
| 已用预算 | EXACT：分资源余额＋固定前缀/事实 | CONSERVATIVE：requests/approvals及attempts | 多维slots/native预算UNSUPPORTED_BY当前prepare |
| LOST | EXACT：同观察多后继并集 | EXACT：outcomes可共用标签 | 观察字符串本身无特殊无效果语义 |
| 未结创建责任 | EXACT：普通settle:i义务 | CONSERVATIVE：opaque session生成close义务 | pending无需冒充实际已创建材料 |
| 甲撤回 | EXACT：撤回ap_a，记录local stop | CONSERVATIVE：withdraw＋另关gate | 真实事件路由受W限制，见04/05 |
| 乙保留 | EXACT：protect support:b，目标B观察 | CONSERVATIVE：B preserve task_b | 原生独立和有效窗口需证；A固定goal不直接要求一次B观察 |
| 原生来源/父子/容量 | EXACT有限标签可编码；外部关系待证 | MISSING通用typed更新/验证 | 原生JTI/验签不单独证明任务来源 |

## 5. 版本与范围责任

raw schema通过只约束有限表内部一致性；source审计通过只覆盖登记source；策略证书通过只覆盖输入模型；真实控制器执行仍需当前批准/来源/预算重核及R02前提。四类责任分别保留。本轮所有“纸面符合”均未升级成机器检查结果。
