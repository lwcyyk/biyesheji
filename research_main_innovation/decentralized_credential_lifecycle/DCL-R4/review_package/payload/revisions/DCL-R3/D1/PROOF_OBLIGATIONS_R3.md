# D1-PBFT-SEAL/1：证明与未解部署义务

DCL-R3；2026-11-10。完整证明限BFT_RECONFIGURATION_PROTOCOL的纸面实例和本文件列出的依赖。它继承静态PBFT定理，不用quorum交集算式替代完整view-change。机器证明/原生新验证/外部独立评审为0。

## 1. 明示依赖

A1 同epoch的签名版PBFT满足确定性SMR线性化；正确节点持久保存view/sequence/投票约束、checkpoint及应用状态，崩溃后验证并恢复，无法恢复则停服。重启清空协议状态重新投票超出正确节点模型。

A2 各epoch n=3f+1、最多f个签名身份在其证书有效生命周期内失陷；验签/哈希与授权策略正确；客户端从可信anchor引导。静态签名界限制移动攻击和远期旧钥泄露。

A3 状态转换及schema验收确定；正确节点只在提交、执行、持久化后签状态收据；治理只能通过当前RSM改变唯一child，不绕开其phase。应用错误/不完整模型属于另一证明责任。

A4 全状态对象可按规范编码校验；验根且取得全部对象后才签Ready。材料密文/引用的解密、秘密使用及其权限可用性明确；活性另需足够正确持有者可达。

A5 V/Gt按已声明profile受信，原生发送权至多一次消费且不可回滚；新授权读取当前有序状态；Provider符合所选原生合同。CD25-LEAK显式放入历史能力和S_bypass，不能借A5删去已泄露Bearer。

A6 原生关闭checker使用范围、来源、完整性、因果/稳定性证据与全部在途能力；缺前提保持UNKNOWN。原生语义的输入真实性由已登记source/profile承担，静态/有限实验证据不升级为全域事实。

## 2. 委员会连接引理

**L1 同epoch唯一执行。** 由A1，同一seq的已执行命令及其前缀唯一；同状态同命令按A3产生同输出。有效状态证书有2f+1个签名，至少f+1来自正确节点；正确签名只指向该已执行状态，故两个冲突有效root不可能同时成立。

**L2 唯一Seal与唯一child。** 第一个成功Seal将mode置SEALED并固定next_cfg。所有随后业务/Seal命令的守卫均拒绝，因此同一应用历史中只有一个成功Seal。若有两个冲突Stop证书，则其中正确签名者分别声称不同成功Seal或不同root，违反L1及phase守卫。相同rid/body重放只返回同一Seal事实。

**L3 Seal后的旧授权截止。** 旧mode=SEALED是吸收态；后续Release/Approve等不能生成有效资格。新challenge无法匹配历史准入收据；f个恶意旧节点不足以形成合格新收据。Seal之前已放行IO可晚到，但在Seal状态的requests/Obl/send_rights中被包含。结论为受控授权顺序，原生有效材料继续接受不受本引理排除。

**L4 新genesis唯一。** 正确新节点只接受Cfg_new明确绑定且父链认证的Stop及完整快照。L2给唯一Stop、A4给与其root相等的唯一数据内容（除可忽略哈希碰撞概率）。确定性迁移F只改变epoch/phase/接管元数据，得到唯一新genesis。不同的新成员集合不能共享同一个有效Stop的next_cfg摘要。

该根覆盖逻辑应用状态；不同副本的PBFT局部日志不混入根。F的字段定义及代码/schema等同性由本实例固定，未证明升级不能进入这条引理。

**L5 新epoch唯一执行。** 在L4的固定genesis上应用A1，得到唯一新历史。Ready本身只证明数据就绪，不产生执行资格；Activate必须由新PBFT从该genesis提交。完全无交集的旧/新quorum也满足这个连接，所需桥梁是旧Seal和被绑定的genesis，不是跨委员会quorum交集。

**L6 全局历史。** 对epoch链长度归纳。e=0由A1；e成功Seal后无新业务写，唯一child从精确继承状态启动并追加线性化操作。将old前缀、Seal迁移F和child前缀串联得到唯一合法业务历史。尚未激活时历史停在Seal，安全保持。若旧侧输出“新业务成功”或child从其他初态提交，则分别违反L3/L4/L5。

## 3. 责任与授权不变量

**I1 RHO登记责任保全。** 在业务Release同一提交内建立attempt、charge和义务；Seal前的Record/Revoke等按序反映在快照。F逐字段复制全部未匹配关闭的请求/责任/证据引用，并检查schema、完整对象和root。新Record保持原r/a/o；仅匹配kind的合法Close删除相应开放项。对业务步与迁移F归纳，登记UNKNOWN不会由owner/epoch变化消失。

范围限制：完整快照证明的是已登记状态的完整继承。若失陷E1经未登记原生旁路产生效果，两个世界可有相同Q历史；此时仅靠checkpoint无法恢复全部外部ID。应保留MaySeen/unknownCreator这一保守责任；不能证明其不存在。

**I2 同意图预算保持。** 每quota有limit，Admit在边界内加reserved，Release转reserved为charged；业务dedup和i跨epoch复制。F不修改limit/reserved/charged，不重建机会槽；Casdoor未知请求不发新继任。相同业务opid在新PBFT client序号下重试仍查全局去重表。由各本地守卫与F的恒等复制归纳得reserved+charged≤limit，迁移不产生第二机会。

**I3 旧批准重放拒绝。** 旧g的revoked状态、代次和grant_op去重被复制；重复Approve只返回旧实例的历史事实。新Release/Takeover检查当前批准，旧QC/旧generation不能覆盖inactive。跨Seal的Revoke按旧提交已包含或新端重试提交两种情形，协议不把未提交意图当成已生效撤回。

**I4 迟到来源保持。** Record要求r/a/body/origin及release版本绑定。F不改变这些字段；新epoch只改承担者与可用性判断。A已撤回时返回进入QUARANTINED，不得用B的合法批准改写该材料来源。

**I5 配置与接管一致。** 旧Seal绑定完整Cfg_new；Activate绑定相同Stop/Ready/genesis；Takeover在当前新状态核DeployCert、RHO和用户批准。任一依赖变化触发重评。Ready和配置证书均无法独立签发业务资格。

**I6 历史暴露单调。** Hist和CreatorCaps包含关系由业务潜在披露预留及F检查保证；恢复/重新分片不删除旧副本事实。旧材料失效通过NativeFacts改变接受关系，保留历史事件。

**I7 B支持的独立前提。** D2必须把Prepare/Seal/Recovering纳入允许转换并保持原Support(B)，包括其Gate资格条件。若只有将被暂停的同一委员会路径，本实例不能证明严格前缀支持，应返回该配置失败。若存在与本次暂停无关的当前充分路径，其批准/预算/来源也被验证且全部native处置footprint不影响它，则该路径在每步保留。这个条件不能由“账户有B Token”替代，也不能免费补一套备用部署。

## 4. 原生停止独立命题

**N1 不假关闭。** 在A5/A6与真实profile符合下，checker只接受匹配scope的真实截止/S-U-L证据、材料接受拒绝及稳定后续条件。由NativeCreationCut审计中的路径反证/计数饱和推导对应创建或材料关闭，再检查全部声明效果载体。RSM仅决定何时提交该匹配声明。它无法把LOCAL_ACK、Stop或Activate转成Provider截止。

**N2 复制安全不足以改变旧Bearer。** 固定一个旧域仍可直接使用的Bearer和完全忽略Q状态的接受端。只修改PBFT状态的两次运行在接受端输入相同，故接受判定相同。于是复制协议保证I1–I6可同时成立，强C_native/C_effect仍失败。该边界沿用R1反例及RQ/EB的既有中介条件。

## 5. 活性与停顿

若合法治理请求被公平提交、旧PBFT最终有进展、正确状态持有者可达、新委员会正确节点取得数据并达到q_new、网络最终同步且请求持续重试，则Propose/Prepare/Seal、Ready、Activate、Takeover依次完成。B完成还需其独立支持、预算、Provider及有限策略进展条件。Seal前可Abort，Seal后缺quorum可以永久停顿；安全不因此失效。

对账最终关闭还需原生义务实际可关闭，Provider永久无结果或旧旁路开放时保持UNKNOWN。协议能够承诺持久责任与明确返回状态，不能把网络最终恢复直接推出全部原生关闭。

## 6. 反证复核与状态

自反驳一：若Stop只写“允许换成员”而不绑定唯一new_cfg，两个无交集委员会可各自启动；本规格通过L2/L4排除。自反驳二：若新节点只验root但未取全数据就签Ready，恶意发送者可隐藏UNKNOWN；A4明确拒签，数据不可用仅阻活性。自反驳三：Seal后旧方重新选择child会破坏唯一链；本规格牺牲该恢复路径，第二次重配置只由当前激活child排序。

纸面实例在A1–A6内可标记CONDITIONAL_PROTOCOL_COMPLETE，范围为复制授权/责任迁移及按profile证据受约束的原生声明。它不代表已部署PBFT、一般动态攻击防护或全部署安全证明。外部独立复核和机器证明仍缺，REVIEW_READY暂缓。

包含严格A停/B保留的完整合同还需要I7及原生N1前提；缺I7时只能确认账本子协议闭合，原强目标保持未满足。该限定保留D2原谓词，未将停顿实例包装成无中断重配置优势。

|部署义务|当前状态|
|---|---|
|现有SQLite主工程到该PBFT状态服务实现|未实现/实施门关闭|
|共识日志稳定存储、schema/code绑定、密钥生命周期与近期anchor|规格给出；实际环境待证|
|V/Gt跨域隔离、发送权防回滚、材料对象可用性|条件规格；当前M6只支持原单机profile|
|原生全部入口/在途/历史材料与模型对应|已有静态证据与有限轨迹；全部署精化待证|
|独立正确性与原创性|同对话纸面推导；外审/机器证明0；强G覆盖继续|
