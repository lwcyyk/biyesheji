# dsat-commit/1版本化提交合同

全部为P/D纸面规格，未实现。先限定S3-A合成专用库，再保留S3-B真实门。

## 1. 状态和版本

状态世界W包含批准/请求/来源、typed O、已接纳证明引用、风险/审计历史、逻辑费用索引及schema。a为世界状态revision；o为O语义revision（成员、覆盖、状态/依赖变化时+1）；authority_instance为创建/迁移时持久固定实例ID；schema/policy_epoch另绑定。

accepted S3提交令a+1；O变化才o+1，纯数学归档可以o不变。合成domain event的release/revoke/late-result/新批准也在同一事务派生O并适当增o；只给S3 handler维护o不够。

独立o是本合同的显式审计/绑定选择：若一个完整a已可靠覆盖所有O写入，单a CAS也能保证该部分一致性。本方案在namespace中增加一个整数，使O变更与纯归档可分别核对；它不能补救遗漏的writer/风险钩子。

提案幂等簿/未接纳对象档案与W分开：它们可记录拒绝或回执而不改变a/o。a不声称覆盖整个DB每个遥测/档案写入；source_snapshot_digest只绑定W的声明投影。现有旧a语义保留在未升级模式，新的拒绝路径不借旧包装器提交世界状态。

## 2. 三阶段接口

**PrepareDSatCommit**：从可信来源一次读W与a/o，导出无秘密快照和vault版本引用，得到source_snapshot_digest、request_scope_digest、current_grant_digest、base_O_digest。提交者身份来自外部可信调用上下文；body.actor必须匹配，不能自填权限true。

**ValidateDSatCommit**：只对冻结证据计算S1/S2，独立检查不可变数学包；生成packet/checker版本/输入摘要绑定的验证记录。source_scope、条件/历史时点、仍欠的原生前提和O覆盖都保留。昂贵计算放写锁外，不能将其布尔结果直接当当前权限。

**CommitDSatProposal**：在新受控事务入口检查所有本地当前守卫、作用域、CAS及覆盖，保存证明/条件记录、O变换、历史、费用与幂等回执。没有任何Native调用/凭据创建/真实C_native授权。

## 3. 提案字段

必需：schema/mode、authority_instance、proposal_id、authenticated actor/scope引用、base_authority_revision、base_obligation_revision、base_O_digest、source_snapshot_digest、request_scope_digest、current_grant_digest、proof_ref/packet_digest、math_input_digest、checker_source_digest/可信验证记录引用、projection_digest、projection_O_digest、proof_context_O_digest、obligations_delta、dependency_refs、cost_delta/paid_work_refs、requested_level、proposal_digest。

requested_level仅MATH_ARCHIVE、CONDITIONAL_ARCHIVE或COVER_PRESERVING_MODEL_TRANSFORM。原生/全局完成字段不在S3-A允许写集。hash按新域绑定整个规范body，旧request_digest算法保持。

R07.make_bindings的O_before实际来自projection.obligations_proposed。A08输入O5项而证明上下文6项（新增close:c2）；A24新增await_terminal。故base_O_digest与proof_context_O_digest分别校验，后者必须等于投影提案摘要及包内对应绑定；不能强行等同数据库O，也不能拿proof.remaining覆盖当前O。

## 4. 原子事务顺序

T0校验规范化/资源/身份和body摘要；T1 BEGIN IMMEDIATE读取当前W；T2以(authority_instance,proposal_id)查持久幂等簿；T3对新合法ID暂存owner/digest并检查a/o/各base摘要、当前管理写权、请求origin及风险范围；T4核packet/checker引用、当前本地依赖及覆盖/费用唯一性；T5原子写对象/接受记录、O_after、历史/逻辑费用、a/o、世界事件、proposal回执；T6 COMMIT；T7发送回执。

成功必须全部T5一起提交。对象可与状态置于同一SQLite事务/库，首次原型存完整规范包；外部文件ref若没有先行持久可验证对象，会有悬空风险，暂不采用。

## 5. 幂等与拒绝的持久性

ID绑定适用于已通过schema/认证并持久登记的提交。相同ID/owner/digest返回相同不可变历史回执，不重用世界更新/逻辑cost_delta，不再检查旧base等于当前；当前使用资格另报。不同body返回CONFLICT_PROPOSAL_BODY；不同owner不获回执或写入。read-own-history权限也丢失则拒绝披露。

为防止CAS失败后换body复用ID，新合法ID的拒绝结果也写幂等簿并提交**档案事务**，a/o与世界O不动。重放该ID返回原拒绝；重新基准必须新ID。无权/畸形输入不预占他人ID。事务未提交即崩溃没有持久ID事实，按重试新接纳处理，不能宣称跨未持久事件的exactly-once。

幂等簿与完整证明/回执留tombstone；清理策略不能抹掉仍承诺的ID绑定。外部DB/key一起回滚、恶意管理员或分叉不在SQLite崩溃恢复保证内。

## 6. 冲突与历史复用

严格全局CAS是最小策略，不采用免费依赖oracle绕过a变化。冲突保留原计算/费用/证据档案；新快照重核O和origin后生成新ID。不可变数学输入未变时可复用已核数学包，改变的是新提交基准，不改旧packet。

证据陈旧或外部当前性未证时，只允许MATH/HISTORICAL归档及保守O，不签当前关闭。数学归档、条件记录与真实资格分层，S3-A永远不改grants、legacy request phase/spent/reserved、旧window或CLOSED/COMPLETE。
