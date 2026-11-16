# 行政封存与原生seal适用边界

Material Passport：PreT0Recovery-static-1/r3；历史MRA原生失败保持。

|实际条件|原生状态|行政行为|
|---|---|---|
|无runtime intent/state/counter/checkpoint|NATIVE_SEAL_NOT_APPLICABLE|保存STARTUP_ABORTED_PRE_T0、T0/R null，Root不调用依赖state的原native seal|
|存在初始化intent或部分运行对象，但checkpoint未完整|NATIVE_SEAL_UNRESOLVED|保存真实部分对象及失败，不能降级纯预窗|
|真实运行对象完整、关闭前提有效、原seal成功且ZIP/manifest校验一致|NATIVE_SEAL_COMPLETED|自动收尾记录独立审计事实|
|实际运行seal抛错|NATIVE_SEAL_FAILED或UNRESOLVED|保留首错和缺项，尝试行政快照但不升级native状态|
|仍有角色或组未确认退出|状态保持未决|行政完整封存延期，保存DEFERRED_ACTIVE_WRITERS/CLEANUP_UNKNOWN|

Root的M.seal在适用性层先分类；纯预窗只写disposition，不再访问不存在的batch_state。Windows冻结入口在active进程返回、原始stdout/stderr句柄关闭并保存退出记录后，自动调用受摘要绑定的startup_finalize。它启动唯一一个只读post-exit导出调用，核源码/输入、当前角色和组空，复制上限256文件/32MiB的原件与元数据；没有初始化、恢复、测试或预算API。

host将Native快照、完整原始双流、原文/回执、entry plan/exit、post审计及静态锁纳入STARTUP_ADMIN_MANIFEST和STARTUP_ADMIN_EVIDENCE.zip，逐流SHA通过后记ADMIN_EVIDENCE_SEALED。它与out/EVIDENCE.zip有独立名称和状态，行政完整性不赋予runtime seal、资源资格或进程清理成功。

若host在Root active调用前就因授权/输入等错误退出，单独frontend_abort自动保存本次host异常与可用锁，形成host-only行政包；它不启动WSL或评价以前的Native进程。重复封存返回已有事实，缺失/不匹配或活跃写者保留UNKNOWN。

本轮以上自动路径均未执行。历史MRA确实尝试原生seal并报FileNotFoundError，仍记NATIVE_SEAL_FAILED；不能用本轮“未来纯预窗不适用”规则追溯更改原结果。

[自动host收尾](evidence/SOURCE_FINAL_R3/host/startup_finalize.py) · [Native只读导出](evidence/SOURCE_FINAL_R3/src/startup_lifecycle.py)。
