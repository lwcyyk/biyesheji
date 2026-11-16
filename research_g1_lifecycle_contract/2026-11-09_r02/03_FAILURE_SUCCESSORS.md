# 失败、迟到、重放与并发后继

以下采用02状态与00固定profile。表中“可能”指与源码及已列环境合同相容；没有执行故障注入。错误响应含义依故障发生位置，运行者无法定位时取允许后继并集。亲本P、直接子代C及未来后代分别记账。

| ID/事件 | 源码位置/发生点 | 必须保留的后继 | 持久状态/观察及责任 |
|---|---|---|---|
| F01 正常成功 | Go705/738/755，provider113—149，record | 新束1；轮换开启且删除成功时P行消失；C返回 | RESULT_AVAILABLE或随后撤回QUARANTINED；原来源 |
| F02 排队时撤回 | storage.revoke/release | QUEUED取消，无新放行；已先release者另归F04 | reserved退回，spent不增加；若RPC丢失从当前权威确认 |
| F03 放行事务提交前故障 | storage.call事务 | 回滚QUEUED，或提交已发生但回执丢失 | 两分支都需恢复；不得凭超时重建批准 |
| F04 release提交后、发送前崩溃 | services145；provider/NativeHTTP reserve前后 | 尚未发送；或未知具体进度，可能已创建 | spent保留；DISPATCHED_UNKNOWN；H可0或1 |
| F05 release回执丢失 | Controller到authority RPC | release可能已提交，但Controller未获send=true，不进入该次perform；或尚未提交 | 同rid重试读取phase；单活/无RPC自动重发下至多一放行 |
| F06 provider RPC丢失 | services149、Client.call | 请求未达provider；或已执行到AS/结果持久但Controller未知 | lookup只补已存inbox，不能重发原perform |
| F07 连接/发送失败 | NativeHTTP189—209 | 零处理；或部分发送后完整到达/已经处理而本地报错 | H已计费；错误类型一般不足以判C=0 |
| F08 客户端超时/断开 | C6—C9 | AS未执行、执行前检查失败、将来插入、已插入/删父/错误 | 原生handler可继续；未知创建槽保留 |
| F09 创建前源拒绝 | Go563—703 | 当前handler直接创建0 | 只有可靠绑定到该源分支才可用无创建结论；通用HTTP错误取并集 |
| F10 生成新束失败 | Go705—710；JWT签名过程 | 可信内存可能有部分字符串；无新Token插入 | 不把字符串数作创建根数；秘密不泄漏属TCB |
| F11 Insert错误/崩溃 | AddToken259 | 0行，或提交成功但错误/连接丢失；同一次固定键至多1行 | UNKNOWN；必须按最坏1保留 |
| F12 插入后DPoP/父删除失败 | Go738—758 | C已存在，P仍在/已删；响应错误 | 无“HTTP错误→零创建”推论；固定Bearer可排除DPoP分支 |
| F13 父删除返回false,nil | DeleteToken267—273、调用755 | 父已被别线程删除；当前代码只判断err；C仍可成功返回 | 不用成功响应证明本次独占消费父RT |
| F14 部分/非JSON/缺字段/验签失败 | NativeHTTP203—207；token_bundle/verified_claims | C可能已经可用，客户端无法登记可信材料 | SOURCE_RESULT_UNKNOWN；迟到或获准查询处理 |
| F15 刷新后批准撤回/迟到 | storage261—308 | 新结果归原origin；当前active=false时隔离 | 不转换为乙材料；spent与处置责任保持 |
| F16 同rid同体重放 | admit203—206、release233—234、record272—275 | 已QUEUED可由唯一release推进；已放行不新send；相同结果只重放 | 异体/异结果CONFLICT；本地去重不延伸为AS幂等 |
| F17 不同rid同父刷新 | 两个admit/release、Go父读取/插入 | 每attempt至多1；两handler可同时读父，创建两个子代 | 各计费/容量；轮换开启也不保证父只产生一个后代 |
| F18 客户端库自动重试 | 当前固定实现无此循环；若更换SDK | 同一逻辑调用可能多个原生请求/处理 | 需显式ρ_i上界和全attempt记账；沿用c_i=1有反例 |
| F19 中间层重复发送/AS dispatch重入 | 原生无rid；Go477非幂等 | 每次handler生成独立name；并发可多子代 | 无重复上界时不能从一个H推出容量1；部署前提须冻结 |
| F20 服务端/DB内部重试 | 单次固定name Insert；框架/驱动另有前提 | 同键标准主键插入重试至多一个记录；重入整个handler可另生name | 两类重试分别界定；不能仅靠PK排除后者 |
| F21 原生撤销与在途刷新竞争 | Go已读父/检查后，另线程ExpireToken父 | 父已失效但检查已通过的旧handler仍可创建C | 父AT/RT当前失效不终结旧handler责任 |
| F22 控制器重启/旧缓存 | services.recover/deliver；store当前权威 | 不重发旧perform；可补inbox或保持UNKNOWN；AS仍可能完成 | 旧cache只显示；权威/密钥失去时停止准入 |
| F23 两代理相关材料 | 身份/同origin规则；可能不同grant持有相同原生RT | source_rid跨origin拒绝；若批准时共享真实RT，原生副作用仍相关 | B分区合同需反映共享；独立grant名不证明原生独立 |
| F24 处置/对账失败 | prepare_disposal/provider/query/save | 可能已原生失效但回执丢失；缺页/来源/两个未知保留未知 | dispose的send不按同ID重发；新处置资格/费用另计 |
| F25 权威提交或审计输出后故障 | storage.call、NativeHTTP211—232 | 效果可能早于日志、日志可能早于调用；当前状态依提交事实 | “缺日志→无效果”“有日志→已创建”均无一般推论 |

## 1. 真实错误码与观察的作用

相同UNKNOWN可以对应C不存在/将创建/已存在。相同HTTP非200可以发生于创建前或创建后。只有固定源分支、绑定请求及可靠响应语义足够时，才能收缩这些分支。当前provider对非200与error_type统一返回UNKNOWN，保持了该保守方向。

HTTP200也可能是OAuth错误对象（需按controller实际响应处理），或native审计/元数据校验失败，故材料是否可登记以完整token_bundle验证为准。即使AS成功但原生父删除bool为false，代码也可返回新束；成功不提供父单次消费保证。

## 2. 并发不变量和终态

两个Controller线程的权威写入串行，provider/AS handler可并发。第二rid可以合法消耗另一个预算槽并使用同一仍RESULT_AVAILABLE的source_rid；当前没有本地“父RT正被刷新”独占标记。因此F17属于允许源轨迹，按每attempt容量建模可以覆盖，按每父容量1会失效。

单未知窗口只统计该账户DISPATCHED_UNKNOWN的issue/refresh，暂停新grant、issue/refresh，不中断已有放行handler；source忠实、唯一未知及创建上界饱和使后续直接创建余额归零。若出现第二未知/外部来源/未记重试，单未知收据前提失效，返回UNKNOWN。

## 3. 证据等级

F01/F02/F04/F15/F22/F24部分有M2—M6历史符合性轨迹；这些轨迹不覆盖本表全部时序。F17/F19/F21是本轮从源读写顺序构造的纸面反例/允许轨迹，详见08。F18/F19/F20未冻结的执行层视为合同边界，当前未开展原生复核。
