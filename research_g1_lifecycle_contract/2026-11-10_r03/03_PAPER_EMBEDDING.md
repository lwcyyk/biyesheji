# 最小纸面输入、抽象与K

## 1. 三份完整静态样例

- [PAPER_L0_INSTANCE.json](evidence/PAPER_L0_INSTANCE.json)：一个world、15个手填节点、7个动作，实际初态为LOST后的K_U、h=7；s0保留作此前已发生事件的账本展示。直接使用当前auth-lifecycle-l0/1字段。
- [PAPER_A_SOURCE.json](evidence/PAPER_A_SOURCE.json)：一个B契约world、两个凭据/路径、三个probe、一个原生stop故障schedule；使用当前auth-lifecycle-a/1与b/1字段。它是保守责任模型，尚未表达完整进度。
- [PAPER_PROGRESS_SLICE.json](evidence/PAPER_PROGRESS_SLICE.json)：同一场景LOST后的四节点残余切片，显式允许撤回后在settle:i仍未结时调用乙；目标事实仅为C_local加乙观察，严格义务继续保留。

三份数据均按源码规则逐项手工填写。JSON解析只核文本格式；schema.prepare、compiler、audit、solver、checker及原生动作运行均0。本文记录PAPER_SYNTAX_REVIEW，未记录机器ACCEPTED。

## 2. L0标签解释与外部绑定

world=fixed固定一份服务合同，u0/u1/u2是同契约中的隐藏执行候选。native_roots的u_p/u_c/u_b为声明影响域引用；c可只是潜在槽。其不同字符串只有在G1证明B-independent后才承担independent检查的真实意义。

`handle:p`表示本过程仍需处理的父引用，移除后历史材料仍可保留；`material:c`表示已知且尚需处置的子引用，不授予甲新使用资格。`support:b`表示独立、当前适用的乙支持，依B-window。`settle:i`是普通严格义务，不要求c已存在；`close:handle:p`和`close:material:c`分别与相应cap配对。

`bind_i_rA_gA_v0_p`引用固定原始来源元组；它在每个节点保持，实际rid/attempt/完整origin/版本及原ID到p/c/b占位的关系由可信托管侧映射提供。标签无原生来源自证能力。ap_manager是真实已有管理资格的抽象，与已撤回ap_a_v0独立。

`i_unsettled`描述本分析责任尚未结清，包含潜在、已创建未观察、已迟到但尚未消费其证据等情况；它不对运行存储“没有材料”作断言。

## 3. 完整状态目录

资源余额写为(a_slots,b_slots,native_calls)，前缀中既有批准/材料费用另记。所有节点保留固定bind与direct_cap_i_1。

| 节点 | 真实范围/事实增量 | 当前批准 | 活跃引用/支持 | 严格义务 | 余额 |
|---|---|---|---|---|---|
| s0 | E0、refresh_ready | A/B/管理 | handle:p、support:b | 空 | (1,1,9) |
| u0/u1/u2 | E3，released/i_unsettled；分别锚W0/W1/W2 | A/B/管理 | 同上 | settle:i | (0,1,8) |
| v | 撤回甲，合并全部未结状态 | B/管理 | 同上 | settle:i、close:handle:p | (0,1,8) |
| d | p已证指定路径失效，i仍可迟到创建/未处置 | B/管理 | support:b | settle:i | (0,1,5) |
| fp | 父处置结果未知，固定本过程停止 | B/管理 | handle:p、support:b | settle:i、close:handle:p | (0,1,5) |
| n/x | 一次读取未绑定/未知 | B/管理 | support:b | settle:i | (0,1,4) |
| k | 可靠c绑定原i，直接容量饱和 | B/管理 | material:c、support:b | close:material:c | (0,1,4) |
| ne | 一次迟到轮询无交付 | B/管理 | support:b | settle:i | (0,1,4) |
| cd | c已证失效，A_native_closed | B/管理 | support:b | 空 | (0,1,1) |
| fc | c处置未知，本过程停止 | B/管理 | material:c、support:b | close:material:c | (0,1,1) |
| t | cd后乙一次UserInfo已接受 | B/管理 | support:b | 空 | (0,0,0) |
| fb | cd后乙调用结果未知 | B/管理 | support:b | 空，乙目标尚未完成 | (0,0,0) |

fp/x/ne/fc/fb是本例固定一次有限过程的保守停止状态，不声称真实服务以后永远不能恢复。它们的具体化允许未观察的环境继续推进，责任/目标不会被自动清空。

## 4. 动作与全部后继

| 动作 | 源节点 | 同观察全部后继 | 模型收费 |
|---|---|---|---|
| release_refresh | s0 | LOST→{u0,u1,u2} | a_slots1、native1 |
| withdraw_a | 任一u | A_WITHDRAWN→{v} | 0项原生；真实RPC/存储另记 |
| dispose_p | v | P_INACTIVE→d；P_DISPOSAL_UNKNOWN→fp | native3 |
| read_child_evidence | d | FOUND_C_BOUND→k；NO_BOUND_RECORD→n；QUERY_UNKNOWN→x | native1 |
| observe_late | n | LATE_BOUND_C→k；NO_DELIVERY→ne | native0；每次只读一次inbox/元数据 |
| dispose_c | k | C_INACTIVE→cd；C_DISPOSAL_UNKNOWN→fc | native3 |
| use_b | cd | B_ACCEPTED→t；B_UNCERTAIN→fb | b_slots1、native1 |

完整JSON逐边给出facts/capabilities/obligations delta、批准撤回及空external_debit。创建潜在c只先加settle:i；FOUND时将其换成close:material:c，同时增加material:c，符合probe严格义务规则。迟到wait虽无自动义务规则，也手填同一责任。dispose移除cap与配对close义务；普通settle:i只在可信饱和绑定时移除。

`P_INACTIVE/C_INACTIVE`采用R02指定接受路径及持续性条件，非单独HTTP200。FOUND需可靠的已提交不同创建见证、原i绑定及容量饱和；可信迟到/inbox、预存标识点读或获准完整范围读取只能在其证据合同确实足够时提供这些事实。仅验签或知道句柄仍不足时保持未结。LATE_BOUND_C要求这些证据已经存在，0原生轮询不免费补发查询；不足时映为未取得合格交付并继续保责。read_child_evidence是拟议的规范结果分组，可由已有能力按其前提实现；当前没有新增适配封装或自动证明它正确。

## 5. K与隐藏状态

令f表示world=fixed。纸面前缀为：

\[
z_0=(\{(f,s0)\},8,\bot),\quad
Post(K_0,release,LOST)=\{(f,u0),(f,u1),(f,u2)\}.
\]

得到z_3=(K_U,7,⊥)，这就是附录实际initial/horizon。经可信A_WITHDRAWN更新为z_4=({(f,v)},6,⊥)。p失效后为({d},5)；FOUND后({k},4)；或NO_BOUND_RECORD后({n},4)，再可信迟到为({k},3)。随后c处置与乙成功分支分别到cd和t，h还在界内。任何未知停止节点保持非终态。

s0→LOST只回放已发生E1—E3并说明sunk收费；从E0进行前瞻原生派发，需要另列完整Refresh后继。正常KNOWN/REJECTED等前瞻结果均应保留。本轮从既成LOST初始化，避免用未来观察限定先前动作。

这些是由已给观察决定的表路径，未使用真实u编号。u0/u1/u2字段和后续相同，可以按相同抽象行为进一步合并，但本例保留三个标签展示LOST并集。W1内部先验检查位和W2父状态均合并进后继最坏范围，故为CONSERVATIVELY_EMBEDDABLE。

环境τ推进在动作前后纳入具体化闭包。例如旧handler在v/d期间创建c，仍属于这些节点的潜在责任范围；只有后续可信证据才收缩到k。模型从未通过“当前没看见c”删去该分支。

历史E2后接管时，通用prepare/solve理论上可用K_U及h=7；当前BoundedController构造器仅从spec.initial初始化。本附录已经把这组恢复初态显式填入数据，实际接入仍需受权快照和重新绑定的恢复模型/证书，不能假定已有原生恢复API。摘要/证书随初态变化重绑，另见04。

## 6. A source保守样例的含义

A样例的p/b为已经取得的材料，零请求issue/create/delegate只表示登记已付前缀与现有托管路径，不能用于免费新建凭据。可信R作为source.caller代表托管视角，甲乙真实caller/origin仍需G1侧绑定。

A数据中的read_a/read_b为本例任务能力标签，未声称Casdoor原生返回这两个OAuth scope。当前真实操作限UserInfo，原生openid/接受路径到任务能力标签的对应仍需G1合同；verified/evidence字段固定该条件声明，不提供原生证明。

可靠configure之后，refresh_i表示登记已发生的放行/LOST事件并分配此前已付1费用，不再次发起真实Refresh。其LOST结果添加`opaque:pending_i#refresh_i#0`，并由compiler产生对应session cap与close义务；withdraw_a另一步只撤回ap_a_v0；清理动作目录为空。所有后续probe只添加session，stop/configure不移除该opaque责任，因此它永远无法在本样例中消失。它保守防早闭合，同时丢失“c已可靠绑定并处置后可结清”的有限成功路径。

该回放不提供从E0预测原生Refresh全部可能观察的source合同；当前A initial固定为未配置/空session，没有现成的已发生事件恢复构造器，复现历史也不能靠W派发重做。上述初态恢复和真实绑定仍属接口缺口。

known_handle cleanup不能引用opaque；account_root cleanup若承担消除未来创建能力，需要当前AS不具备的对应栅栏/来源完备合同。把其设为applied=true去删除pending会偷加能力。本轮不这样做。

该A样例只证明这条直接编码可安全保留责任，完整父替换、迟到解析、多资源预算和终态B观察尚未完成。它不证明任何间接A编码均不可能，也不构成完整raw L0样例的source审计证书。
