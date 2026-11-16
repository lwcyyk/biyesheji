# R/T/B/E/ΣV_j编码与实际输入域

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

最终状态：**R_MR为BOUND_PROVED（继承ABI/冻结调用域）；B为CONDITIONAL_BOUND；R_budget/T/E/V的完整数值为UNRESOLVED_EXACT，定量profile或新合同必须替代重复审计。** 变量的实际来源见[REASON_AND_VARIABLE_DECISION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/REASON_AND_VARIABLE_DECISION.json)及[SOURCE_EXCEPTION_CLASS_CENSUS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/SOURCE_EXCEPTION_CLASS_CENSUS.json)。

|变量|真实字段和生成者|现有边界|终局限制|
|---|---|---|---|
|R_MR|[src/manager_recovery.py:355](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:355)first.reason；来自固定M.abort/M.fail调用|字面量、launch_one状态PASS/FAIL、COORDINATOR_CHILD_RETURN_＋原生退出整数。最大内容36字节ASCII、token38|仅这些调用方；任意abort(reason=x_n)属于域外|
|R_budget|[src/guard.py:84](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:84)BUDGET_HALTED:＋str(exception)|H≤52；文件/锁/counter/JSON/clock/序列化错误来源|无source字节截取；完整pinned诊断目录/环境profile未给出数字|
|T|type(exception).__name__的JSON token|冻结应用自定义类名最大18 bytes；optional null以T≥4覆盖|导入的builtin/stdlib/native类名全集仍缺量化证书；18不能推广为全TCB|
|B|[src/manager_recovery.py:266](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:266)三份ledger原件的hash/size或UNKNOWN/type映射|健康全成功≤387；一般B≤69＋3max(106,29＋T)|hash64和size≤20字符是继承ABI；读取整份ledger的工作量另算|
|E|[src/guard.py:761](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:761)closure_persistence_error=repr(exception)|仅H锁、stamp和RootIPC marker发布的try产生；失败时可为null|后面的systemctl调用不在该try内，stderr_m没有已证路径进入E；需固定TCB文件/ACL/clock/JSON异常repr profile|
|V_j|[src/guard.py:175](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:175)12个cgroup文件read_text().strip()的JSON token|文件名集合固定；pids与内存配置、stat位宽已知|导出键集、计数宽度、缺件/null及并发进程/线程列表语义尚未量化；parent slice文件未设MemorySwapMax|

Root reason逐调用证明：固定字面量有有限长度；r['status']由launch_one自行赋PASS或FAIL，最多4；退出code沿用signed32十进制≤11的保守ABI界。COORDINATOR_CHILD_RETURN_长度25，因此reason≤36。加MR_CRITICAL:/MR_FALLBACK:各12后，Root marker的reason token≤50，整行≤194。它是新的来源子界，未改变任何守卫。原固定43字节quota reason对应189继续成立。

first_failure中的str(error)[:2048]限制Unicode code point数。BC compact编码默认ensure_ascii=True，每code point最多12字节，内容≤24576、带引号≤24578。该限制不作用于reason、type名或E。RootIPC/payload metadata采用ensure_ascii=False的UTF-8 pretty JSON，任意单code point的编码/转义可达6字节；固定ASCII无需额外转义。各token定义含引号，字节、字符、JSON结构分别计量。

12个V依次来自pids.current、pids.max、pids.events、memory.current、memory.peak、memory.max、memory.swap.max、memory.events、memory.oom.group、cgroup.events、cgroup.procs、cgroup.threads。TasksMax4约束同时存在的受管task，单凭这一值无法完成所有seq-file列表及churn语义的字节证明。所有值经kernel接口生成，当前没有任意V_n是合法冻结内输入的证明。

R_budget与E也不能从“通用str/repr可很长”直接推出冻结域真实无界：两者的当前事务路径没有任意业务文本注入点，E尤其不接后续systemctl stderr。缺少完整定量TCB异常目录时，数值保持null；若选择强制有界错误wire/acquisition profile，则属于待批准合同。TCB目录或新限制是下一输入，旧源码同范围审计到此结束。

task_id在C09原生日志中缺席；生产range任务来自固定child_contracts的三个ID，ASCII长度最大17；合成S1–S9固定job及L/R后缀最大20。二者均与R/T/E分开，见[FIXED_INPUT_WIDTHS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/FIXED_INPUT_WIDTHS.json)。PID/ticks/clock/hash/namespace的既有profile继续作为明确条件，未以OS物理内存有限代替应用层界。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
