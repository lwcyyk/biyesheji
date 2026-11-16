# 完成时间与有限工作量的分离裁决

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

**UNRESOLVED_EXACT：WALL_TIME_BOUND_UNRESOLVED。** 已核实的5/30/300/1800分别属于不同作用域，不能合并为全链成功完成时间。见[RESOURCE_TERMINATION_DECISION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/RESOURCE_TERMINATION_DECISION.json)。

|数值|真实绑定位置|可宣称的作用域|
|---:|---|---|
|5秒|[src/terminal_evidence.py:196](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/terminal_evidence.py:196)及terminal_contract.read_seconds|terminal只读检查的截止；guard.seal还含运行时核查、停止等待和归档，缺整体5秒包络|
|30秒|[src/admin_postexit.py:46](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/admin_postexit.py:46)、startup_contract.postexit_admin_timeout_seconds|Linux行政child的alarm；host父进程等待32/35秒后还有自身ZIP/hash，无整体30秒deadline|
|300秒|boot_contract.calibration_seconds及当前calibration检查|软校准窗口/准入与停止判断，未得到完整成功WCET|
|1800秒|共享state.deadline与boot total_seconds|全批原截止；1740 stop策略和unit RuntimeMax维持，不构成任意kernel阻塞下的真实退出上界|

Windows active入口[host/windows_entry.py:42](D:/毕业设计/DCL-R6-isolated-verification/ra01/host/windows_entry.py:42)的process.wait自身没有timeout。deadline检查依赖获得CPU并从syscall返回；SIGALRM/systemd timeout/kill是处理机制，D-state或外部响应延迟仍需明确模型。普通可信kernel和fsync正确性前提没有提供最大调度/响应时延。

若要声称严格成功完成时间，至少需要T_cpu/scheduling、read/write/fsync、systemd/query/stop/kill/reap、host/WSL返回的定量最坏界，及资源内存/FD/吞吐峰值证明。给定操作计数n_i也只能写总时间≤Σn_iτ_i＋T_cpu＋T_schedule；缺τ_i不能求值。

允许环境模型里可选择一次足够长的调度或存储延迟，使有限工作错过300秒；该推理反例针对“有限工作⇒严格时间”的推导，证据类型为静态分析，原生故障执行仍为0。合同须决定采用定量环境前提，或明确以超时/UNKNOWN和限定环境实测为目标。当前无新动态授权，不进行时延测试，不放宽已有期限。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
