# 最小扩展与现有能力复用

## 1. 总判断

本场景的有限值均可用raw L0现有state/facts/approvals/budget/obligations/edge编码，顶层schema新增字段没有被证明必要。typed对象有利于正确构造/维护模型，属于G1接口/源语言候选。当前A source的直接表示和变换有限，不能把raw L0的表达能力等同于A bundle自动支持。

以下“缺失”限定直接字段/现有更新规则。反驳某一session编码或exact_fields的直接加键，不构成所有参数编码或全部算法的不可表达性证明。

## 2. 九项对象及最小设计

| ID/能力 | 当前raw L0/A状态及最小反例 | 优先复用/候选语义 |
|---|---|---|
| X1 Pending Refresh Attempt | L0的settle:i与state已够；A只有probe计次与session。CE1中丢响应仍有在途 | 复用rid/attempt/origin/v_rel，source可增加受限attempt记录引用；创建、登记、未结与终态分开 |
| X2 Potential Child | L0义务可先于材料存在；A opaque可保守表示，CE3难以解除 | 不预先授予可用材料；潜在槽/未结义务在可信见证后变已知材料责任 |
| X3 Parent-Child Origin | 单次固定标签可绑定；typed来源校验不在L0内，迟到挪到乙会错 | 复用materials/origin/source_rid和受权元数据摘要，关系保持原批准/代次而非到达时批准 |
| X4 Creation Capacity | 单次c_i=1为条件事实；标签不验证定理，CE2仍可迟到创建 | 将可靠直接上界与已计不同见证分别保存，只有绑定/代次证据才能减少未结余额；后代另入I |
| X5 Delayed Result | raw edge可换settle为close:c；A probe只能add sessions，CE3 | 源层候选resolve/replace责任操作：凭可信来源将opaque风险转已知c，并保持处置义务；不直接删光责任 |
| X6 Native Revocation Coverage | raw requires/状态可表达；B静态affects/verified/coverage须真实合同 | 复用原生域、路径及scope引用；“关闭创建前沿”与“失效一份材料”分开，未来相关/重叠域另建模型 |
| X7 Strict Obligation | raw普通义务及close配对已实现；A只从sessions生成 | source可直接引用命名责任或拓展现有session状态；终态仍全称检查，A选择器/参考需认识新责任 |
| X8 Independent B Support | raw protected cap/B preserve已有；CE5表明时间与源独立不能由名字保证 | 复用原生影响域及有效窗口/当前性证据；窗口外加入过期/撤回分支或重新建模 |
| X9 Persistent Cost Projection | raw多预算键已有；A source.budget精确仅requests/approvals | 复用真实per-grant reserved/spent和原生机会账本，建立保守剩余投影；直接加a_slots/native_calls会被现有A prepare拒绝 |

## 3. 对实现、状态空间与强方法的影响

| ID | A/B/AB与检查器责任 | 规模/复杂度 | 强通用方法与准入 |
|---|---|---|---|
| X1 | source.prepare/plant/reference/audit接入attempt；当前快照权限另验 | 一个固定attempt为有限状态乘子；k个需显式数量/状态界 | 标准FSM/规划可表达；ANALYSIS_ONLY |
| X2 | A/AB要按未结风险控制，不能当实际可用支持；B目录不凭空新增 | 固定潜在/已知/失效几态；并发多子扩大 | 普通may-state/效果分析可处理；无新优势 |
| X3 | 验证原来源/证书scope/digest，晚到不授新批准 | 单例常量引用；多来源相容图大小计费 | 标准来源账本/状态机覆盖；候选接口 |
| X4 | updater/关闭checker验证上界/见证，不接收算法猜测 | 有限计数需位长和全attempt界；无界退出 | 标准容量流/规划共享；动态优化另审 |
| X5 | 需要同步修改source解释、独立参考、审计、选择器的责任度量/证书 | 一例新增几种结果；多次迟到/竞争需重算 | 标准状态变换能做；新原生能力不能虚构 |
| X6 | B静态partition有效域保留；动态域需新语义/参考；真实adapter证明 | 影响图/域维护费用，不等同token数 | 通用图/状态机直接支持模型；尚无严格差距 |
| X7 | compiler生成准确义务，candidate与R-J/策略checker都按全义务终态 | k个责任可有2^k子集，固定一例常量 | 通用AND/OR可表达；工程与证明工作 |
| X8 | preserve、失效后继、执行前时效核验；模型外证书失效 | 时间可分有限区间，但真实时限/等待另证 | 标准定时/有限安全规划近邻；本轮不新增工具 |
| X9 | A/R-J价值函数、预算共享、checker/原生价目共同改；防低估 | 每预算取值范围/位长影响状态；不能免费压成Q | 标准多资源规划可表达；ANALYSIS_ONLY |

source若确需新增字段，其变化要同时出现在prepare、plant、独立_plant_reference、compiler/audit与引用point的选择器/诊断中；不得只扩JSON而保持旧证书含义。raw L0已有字段时可保留其参考解释，但真实映射和源审计仍须补证。本轮没有修改任何这些模块。

## 4. X10：事件与完成目标的正交责任

CE4表明需要独立审查“强制批准撤回/恢复事件更新”与“进入全局有界完成W菜单”的接口。可选纸面方向：把真实权威事件当成受权知识更新，保留全部义务、立即重核可派发动作；将C_local、指定材料闭合、责任持续托管、乙服务分别列scope目标和安全约束。

这些方向不需要仅为本例增加typed凭据字段；它们涉及监督策略与证书scope。当前W_h继续承担原有“所有观察有界到全终态”保证，安全部分进展需要另一份明确合同。普通安全监督/工作流也能表达，尚无新算法或效率资格。任何改动都应重新证明当前权限、外部事件、全部未知后继、义务和费用；实现门仍未通过。

## 5. 最小化顺序

先复用raw L0及G1来源侧映射，保留UNKNOWN；随后在纸面上选定X10目标/事件合同；只有需要当前A源自动构造有用进度时，才讨论X5/X7及X9的最小source更新。X3/X4的真实证据不能由更复杂字段替代。所有候选扩展保持DESIGN_ONLY，外部原文/数学核验及严格分离条件独立管理。
