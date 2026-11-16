# 下一阶段专项授权申请材料

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

本文件准备具体范围，**当前申请尚未获批，IMPLEMENTATION_GATE=CLOSED**。推荐先继续数值化关闭/错误/环境profile，全部条件明确后，再单独申请受G覆盖的最小静态维护。新动态链、WSL、真实故障和F1/F4均在本申请之外。

|候选文件|未来需审查的函数|合同变更责任|
|---|---|---|
|[src/c09_handoff.py](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py)|event, publish, sender_prepare, Receiver.observe_exit|prior v2 predebit/completion/7 lifecycle bits/terminal latch, exact fields and bounded no-log rejection; no dynamic handoff|
|[src/guard.py](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py)|request_stop, halt_budget, stop_tree, _run, seal error writer call sites|derive and explicitly approve response/encoded error/stop profiles and safe retained raw overflow behavior; no guessed cap or safety bypass|
|[src/manager_recovery.py](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py)|abort, budget_snapshot, _stop_other_roots|bounded shared closing responsibility, finite per-role attempts, failure dissemination, fixed typed close schemas; no cross-instance admission changes|


这些候选的diff只能位于将来新建的独立审查副本，旧ra01、batch14和所有历史字节继续冻结。最低输入合同集合为inputs/c09_contract.json、manager_contract.json、batch_identity.json、static_manifest.json、execution_lock.json、runtime_tree_lock.json，以及拟新增c09_quota_contract.json和close_reserve_contract.json；相关contract/schema/hash依赖须逐项重冻结。当前均未创建可执行新锁、身份、T0或预算。

如最终关闭/字段合同影响读者，src/terminal_evidence.py需要独立适配授权；完整行政容量若需生产端界，还涉及src/startup_lifecycle.py、host/startup_finalize.py，以及产生active-entry原始流、finalization-error和host wait的host/windows_entry.py。src/root_ipc.py仅在新target无法复用现有BC.Store私有.json域时纳入；权限、fsync和取消语义保持。具体条件与9个namespace字面量源文件的精确AST复核清单见[FUTURE_CHANGE_SCOPE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/FUTURE_CHANGE_SCOPE.json)，禁止宽泛字符串替换。

未来授权需要明确：采用的准确合同hash和字段上限依据；允许变更的文件/函数；全部原始字节及失败staging的保留规则；单首错/重复关闭/无标记EIO的责任；新文件/字节/visit/IO与静态负向检查增量；源码/输入/namespace/执行锁及独立raw oracle。常规工程维护与研究实施门的适用关系应随新授权明确，当前稿不自动获得例外。

继续保持预算预留核心、原native/admin安全准入、256/257和MR跨实例规则。完整关闭/字节/工作量未决时，可以申请继续静态证明；完整资源资格链申请仍需容量合同及所需独立规则、集成源锁和新的当批授权/资源条件全部到位。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
