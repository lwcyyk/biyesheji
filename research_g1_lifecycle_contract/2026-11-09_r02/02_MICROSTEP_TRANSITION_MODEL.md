# 有限微步骤合同 C_refresh

这是纸面关系模型，未编写/运行生成器或求解器。合同以00的P_direct为基础，覆盖一次目标refresh及既有父P、独立乙材料B和至多一个直接子代C。若扩大创建/派生/写入者，先扩合同或退出边界。全部真实后继相对固定源与A01—A12假设量化，未声称覆盖任意部署。

## 1. 状态与观察

真实状态s包含权威D、Controller/provider控制位置、请求传输/AS控制位置、原生记录与局部已加载父对象、原生材料、inbox/journal、当前批准、预算和未结责任。

合同状态z保存以下有限信息：

- 身份/来源元组及原请求引用固定，当前批准active位和相对版本顺序。
- 请求phase为未接纳、QUEUED、DISPATCHED_UNKNOWN、RESULT_AVAILABLE、QUARANTINED、DISPOSED/已取消之一；处置/窗口状态另列。
- 控制位置pc见下表，崩溃与恢复边可进入未知挂起态。
- 父P状态（未读/已加载检查通过/原生仍有效/已失效或删除）、新束是否仅在服务内生成、子代C是否已提交；服务内已检查父与当前DB父状态分别保存。
- 创建机会余额b_i∈{0,1}，累计不同创建见证与失效位，发送机会/响应/可见日志位；待决网络/handler位。
- 原批准reserved/spent/limit、原生预算各剩余槽；值由有限输入上限限定。原生ID使用固定P/B/C占位与可靠等同性/来源映射，原字符串由托管恢复元数据保存。
- 严格义务O：可能迟到创建、未知来源、已知隔离材料待处置、未覆盖派生、处置未知、未完成乙保留条件。

该抽象保留“AS已加载父并通过检查”状态，即使其后父已被撤销；这是覆盖迟到创建的必要位。精确整数版本/秘密字节不作为求解状态复制，保留身份等式及相关先后比较；控制器仍用原值重核。新批准、新调用/无限次后代超出当前有限集合时进入BOUNDARY或另建I。

运行观察obs为权威回执/UNKNOWN、预记账元数据、获准原生响应及校验、journal/inbox/点读/范围读、处置观察、当前批准和乙操作结果。AS内部pc、签名但未返回材料、未见子代和真实来源是证明用ghost，不输入策略。

## 2. 转移表

V表示当前权威version；v_rel为放行版本。AS看不到该版本；每行“批准”指本地当前性或已检查历史时点。表中0费用只指无新增该类资源，计算/读写另见06。

| pc | 前置条件/批准 | 持久写入 | 外部副作用/观察 | 允许后继 | 预算与材料 | 义务/崩溃点 |
|---|---|---|---|---|---|---|
| C0 请求入口 | 已鉴别caller、格式合法 | 无 | 本地拒绝或继续 | C1/拒绝 | 无放行费 | 鉴别/解析失败不产生新效果 |
| C1 admit事务 | grant绑定、active、op、窗口与预算 | QUEUED、正文/digest/origin | ADMITTED/DUPLICATE/CONFLICT或RPC未知 | C2/拒绝/已存在phase | reserved+1仅首次接纳 | 事务未提交回滚；已提交丢回执仍可能QUEUED |
| C2 等待release | QUEUED | 撤回可取消；否则进入release | 当前源材料须同origin可用 | C3/取消 | 取消reserved−1 | 提交前崩溃与排队撤回 |
| C3 release原子提交 | active，窗口未暂停；source有效 | attempt/v_rel、DISPATCHED_UNKNOWN | 首次send=true或未知回执 | C4/悬置 | reserved−1，spent+1 | C3/C4边界同一事务，不存在已提交“只扣费未设phase” |
| C4 provider调用前/中 | 仅send=true者发起；当前请求绑定 | 可无新增权威写入 | provider RPC丢失/开始验证 | C5/悬置 | 材料仍在托管 | 响应丢失不重放perform；现有provider自身无dedup |
| C5 验证与预记账 | 材料/issuer/account/client/time通过 | NativeHTTP reserve记录H+1 | 仍可能未发送 | C6/UNKNOWN | 原生槽−1；b_i仍1 | 验签前失败、reserve前/后崩溃分别覆盖 |
| C6 Request/open/传输 | 固定路由/字段、无重发 | 后续审计可尚未落盘 | 未达、部分/完整发送、超时/响应 | C7/C9/悬置 | 不确定S/P/C；不返还spent | 网络超时之后AS仍可能推进 |
| C7 AS校验父 | route/ValidateOAuth；父RT、scope、user检查 | 只读或辅助源行为 | 创建前错误可返回 | C8/C9 | 父对象可能已加载 | 与父revoke/delete并发；已检查不等于提交前重核 |
| C8a 生成新束 | 通过源检查 | 尚未AddToken | 生成AT/RT/ID及name；生成可失败 | C8b/C9 | 新束只在可信服务内 | 生成后进程崩溃不等于公开可用单位 |
| C8b AddToken | 一次构造newToken | 单次Insert，成功/失败/提交但错误 | C_i增加0或1 | C8c/C9/悬置 | 成功创建后b_i=0 | DB错误观察可含已提交；标准单键Insert至多1单位 |
| C8c 后处理 | Insert已发生或未出错 | 可DPoP update；轮换时DeleteToken(P) | 后处理可失败，或生成响应 | C9/悬置 | C已存在；P可仍在或已删除 | 在固定Bearer子域DPoP更新分支可收缩，保留它也不增插入容量 |
| C9 HTTP返回/缺失 | AS任意当前后继 | NativeHTTP封存/账本回写可能中断 | HTTP/解析/传输错误、部分响应或成功 | C10/UNKNOWN/悬置 | 创建与响应分开 | 审计写失败可在效果之后；继续有义务 |
| C10 验证/日志/inbox | body字段、AT/RT验签及绑定 | 可选journal/inbox fsync | PROVIDER_RESULT或UNKNOWN | C11/悬置 | 原来源仍不变 | 验证失败或收到后尚未持久，结果可能丢失 |
| C11 record | 原rid/digest/origin/attempt/v_rel一致 | 材料和result_digest，phase依active | RESULT_AVAILABLE/QUARANTINED/DUPLICATE/冲突 | C12/悬置 | 当前active才供使用 | 原生已生效但record失败保持未知责任 |
| C12 撤回/处置 | 撤回资格；处置须已知隔离材料 | active=false；处置先预记，再登记观察 | LOCAL_REVOKE_COMMITTED、DISPOSAL_RESPONSE/UNKNOWN | C13/未结 | 处置最多3显式原生调用 | 撤回可在任何C1以后交错；不撤销已放行历史 |
| C13 对账/恢复 | 当前权威、合法读范围、来源/容量前提 | window/query/收据/当前状态 | CLOSED或UNKNOWN/冲突 | 终态/未结/边界 | query/乙检查/处置均计费 | 恢复不重发旧perform；未结handler可仍有下一步 |

## 3. 并发、环境与崩溃规则

每个本地权威mutation按BEGIN IMMEDIATE串行。原生处理不与它共享事务。C1/C3/C11等事务可以发生“已提交但RPC回执丢失”；合同保留实际提交与未提交两种相容状态。崩溃只丢失相应易失状态，durable事实保留；进程/权威回滚或副本冲突超出当前P_local。

原生线程可在客户端UNKNOWN之后继续C7—C9；只要已提交一个独立子代，直接创建容量已用尽，后续该handler仍可删父/返回错误但不再产生第二子代。网络/AS终止与容量饱和分别证明，后者依据完整创建上界及可靠效果下界。

若任务乙或第二rid作用于同父，采用多个attempt控制位置的交错积；每个attempt各有容量。当前单attempt合同对新增创建者返回BOUNDARY。乙已有UserInfo可作为只读相交动作；乙刷新需要新增attempt，不能当免费旁路。

## 4. 状态不变量

I1：每grant reserved等于其QUEUED请求数，spent等于其历史成功release数，reserved+spent≤limit。I2：每rid最多一个attempt、首次release至多一次send=true。I3：结果来源与原请求绑定，撤回不更改origin。I4：0≤direct_created_i≤1且剩余潜在直接创建≤1−可靠不同创建见证数（仅P_direct）。I5：UNKNOWN/未覆盖派生不会被缺响应消除。I6：CLOSED要求严格义务为空且声明终态条件均有依据。I7：费用上界覆盖微步骤全部原生机会及本地计算，终态不授予新批准。

I1—I3由锁定本地源码归纳；I4依04的调用和源假设；I5/I6是本轮合同规范，现有收据只在其前提成立时满足；I7依06分项收费。上述合同未作为已运行L0实例或已验收新实现。
