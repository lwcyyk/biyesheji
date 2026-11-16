# 活动态与终态接口审查

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

**活动态接口维持原有严格资格检查；终态接口直接核验既有证据，不进入G.state或活动预算路径。**

|接口|实际实现/用途|权限与失败规则|
|---|---|---|
|check_active_runtime|薄封装原G.root_checkpoint；原调用者继续使用G.state/root_checkpoint及PF机制|STOP/CLOSED优先拒绝；身份、window、资源、运行点保持；失败抛原异常|
|read_terminal_evidence(REVIEW)|当前固定批次的既有window/counter/journal/phase/关闭/退出读取|Root只读描述符，身份与来源匹配，缺件损坏保留错误；无work/预算/阶段/Launcher权限|
|read_terminal_evidence(NATIVE_SEAL)|在原停止器等待之后评估既有证据|必须CLOSED、同原boot、原deadline尚有效、完整预算/检查点、稳定角色退出与直接waitpid；返回native_ready只表示输入前提|
|read_terminal_evidence(HISTORICAL_AUDIT)|同一固定namespace在新boot读取历史记录|保留original_boot和observation_boot，旧waitpid仅作历史见证，native_ready恒false|

活动接口的G.state/validate_state_document/root_checkpoint、counter创建/预留核心、PF状态事务和锁读写函数全部保持归一AST。旧terminal_inspection可选参数未扩大权限；批准的seal读取已分流到新接口，不再调用那条依赖活动期限的路径。

终态模块只打开原文件O_RDONLY|O_NOFOLLOW，既有Root目录通过原RootIPC只读目录遍历验证；未使用会创建boot目录的BC.Store。共享锁顺序counter→phase，兼容原预算写者的counter→phase顺序；最多512次/2秒获取，整个读取5秒。锁为瞬态描述符操作，无运行文件写入。

io局部until只限制行政读取耗时，不持久化为运行deadline。返回window直接来自原state并与checkpoint完全比较；没有新的T0、预算、生命周期转换或服务启动。

[调用图/只读闭包](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json) · [新接口](evidence/SOURCE_FINAL_R1/src/terminal_evidence.py)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
