# 强制权威事件与R1—R4

## 1. CommitRevoke合同

输入是经过管理身份鉴别的(grant_id, task, account, generation/approval_version, revoke_op)，明确针对旧批准实例gA_v0。现有API实际接收revoke_op和grant_id；其余绑定通过权威解析/受信任命令封装，当前没有通用expected_version比较接口。task名不能自行替代精确grant_id。

操作在当前权威事务中将该grant.active设false，取消其QUEUED请求并释放reserved，将RESULT_AVAILABLE转QUARANTINED，原DISPATCHED_UNKNOWN及历史origin/spent保持。线性化点为AuthorityStore.call成功COMMIT。v_r为首次撤回commit_version。

该权威命令不要求认证语义模型的K已可用。即使K冲突或处于boundary，可信当前权威仍可处理有效撤回；局部B许可/原生关闭须等其各自可靠前提满足。撤回本身不会凭空修复未知原生模型。

本地返回LOCAL_REVOKE_COMMITTED只承担指定受控入口的新放行截止。请求已发起、事务是否提交、客户端是否收到ACK分别记录。事务/回执不确定时客户端显示UNKNOWN并通过同revoke_op当前查询/重放对账。

源码：storage.py:122—159、284—308；services.py:81—93。当前服务revoke路径没有调用L0 W_h，纸面组合沿用它。

## 2. R1：撤回后新放行安全

命题：在同一可信当前权威、所有声明入口均使用该admit/release、状态不回滚且同grant不重激活时，revoke(gA_v0)在v_r提交后，该grant不再产生新的成功release。

证明：admit对新rid检查active；已有QUEUED在revoke中取消；即使某线程此前已读到排队记录，release仍在新事务查当前grant.active并拒绝。对非QUEUED记录返回send=false。重复rid可能返回DUPLICATE历史投影，不能据此认定获得新资格。真实原生效果按原release顺序处理，不由此命题停止。

状态PROVED_WITHIN_MODEL，当前源码有直接依据；全执行覆盖/存储可信为条件。恶意旁路、持有原生秘密的外部调用者及不同新grant超出该断言。

## 3. R2：旧请求与责任保持

命题：release先于revoke的i，origin/rid/digest/attempt/release_version和spent不因撤回改变。撤回只改变当前资格/结果可用性，不清其潜在创建与迟到义务。

证明逐项展开revoke赋值：未写来源/attempt/spent，也不取消DISPATCHED_UNKNOWN；known结果仅转隔离。全局typed投影对该phase继续保留settle:i；存在已知材料时还有close相应引用。来源/责任更新见04。

状态PROVED_WITHIN_MODEL（本地字段）；真实全部风险覆盖依G1源合同，CONDITIONAL_ON_ASSUMPTIONS。

## 4. R3：幂等、历史与单调版本

同revoke_op/同grant返回原撤回收据，异grant复用同op冲突。grant.active在本源模型中没有false→true转移；approval_op重放返回原grant，不激活它；同caller/task/account/audience/generation重复grant被拒，另一个generation为不同批准对象。

global v在成功mutation事务中递增，包括部分重复/拒绝的无语义变化提交；它表示权威事务顺序，每对象依赖版本与AS撤销epoch需各自定义。原收据commit_version=v_r在重放时保持，外层返回version可已为v'>v_r。证书须分别记录撤回发生版本、观察/签发版本和当前检查条件，原生围栏需独立证据。

迟到record只匹配原rid/digest/origin/attempt/release_version；当前gA已inactive则QUARANTINED，重复相同结果返回历史状态，异体冲突。恢复只读当前权威，旧cache无授予能力。

## 5. R4：全部有效并发顺序

| 权威/原生顺序 | 当前后继 | 费用与责任 |
|---|---|---|
| revoke≺新Claim | 新admit因inactive拒绝 | 无新reserved/spent；拒绝读取/事务成本照计 |
| Claim≺revoke≺Release | QUEUED取消，release不send | reserved退回，spent不增 |
| Claim≺Release≺revoke≺HTTP发送 | 旧放行可继续发送 | spent保留，settle:i及来源保留 |
| Release≺AS处理中≺revoke | handler可能尚未/已经创建c | 本地撤回不推定无创建；容量/后代另核 |
| record≺revoke | 先AVAILABLE后QUARANTINED | 原材料与来源不删；处置另计 |
| revoke≺record | 结果直接QUARANTINED | 原请求和批准代次保持 |
| COMMIT≺ACK丢失/控制器崩溃 | 当前权威可能已撤回，客户端未知 | 恢复/幂等对账确认；不会退回旧cache |
| COMMIT前故障回滚 | 撤回未发生或回执无法判定 | 无C_local完成证书，重试需当前管理资格 |

权威事务可线性化这些本地事件，外部HTTP/AS不在该事务内。证书预检查与release之间若乙被撤回，release当前检查必须拒绝；把签发证书当未来通行证会破坏R1。

## 6. 强制性与活性

“强制”是有效用户命令由AuthorityTransition入口处理，摆脱完整关闭W门的先决条件；身份、精确对象和存储失败条件仍执行。模型不能承诺数据库不可达时也提交，不能从已提交权威推导AS已失效。公平调度/存储可用可支持最终处理，固定撤回时延需独立系统证据，本轮未取得。
