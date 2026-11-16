# 获准64项回归与17项变异的实际结果

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

冻结最小申请的64项全部执行并接受：**47 PASS、17 MUTATION_DETECTED**。每项私有raw、输入摘要、实际frame facts、subject shadow/decision、全局访问前后及Root独立结果均保存；没有以expected代填actual。

|case|variant|actual status|Root oracle实测违规|accepted|
|---|---|---|---|---|
|P.immediate|safe|PASS|∅|True|
|P.starting|safe|PASS|∅|True|
|P.pid_pending|safe|PASS|∅|True|
|P.transition|safe|PASS|∅|True|
|P.field_order|safe|PASS|∅|True|
|P.stable_lock|safe|PASS|∅|True|
|P.uid|safe|PASS|∅|True|
|P.gid|safe|PASS|∅|True|
|P.groups|safe|PASS|∅|True|
|P.caps|safe|PASS|∅|True|
|P.nnp|safe|PASS|∅|True|
|P.as_hard|safe|PASS|∅|True|
|P.as_soft|safe|PASS|∅|True|
|P.cgroup|safe|PASS|∅|True|
|P.unit|safe|PASS|∅|True|
|P.type|safe|PASS|∅|True|
|P.tasks|safe|PASS|∅|True|
|P.proc_as|safe|PASS|∅|True|
|P.proc_cgroup|safe|PASS|∅|True|
|P.boot|safe|PASS|∅|True|
|P.pid_reuse|safe|PASS|∅|True|
|P.read_error|safe|PASS|∅|True|
|P.missing_field|safe|PASS|∅|True|
|P.snapshot|safe|PASS|∅|True|
|P.exit|safe|PASS|∅|True|
|P.service_failed|safe|PASS|∅|True|
|P.timeout|safe|PASS|∅|True|
|P.stop|safe|PASS|∅|True|
|P.closed|safe|PASS|∅|True|
|P.lock|safe|PASS|∅|True|
|M.CR-01.safe|safe|PASS|∅|True|
|M.CR-01.mutant|mutant|MUTATION_DETECTED|CR-01|True|
|M.CR-02.safe|safe|PASS|∅|True|
|M.CR-02.mutant|mutant|MUTATION_DETECTED|CR-02|True|
|M.CR-03.safe|safe|PASS|∅|True|
|M.CR-03.mutant|mutant|MUTATION_DETECTED|CR-03|True|
|M.CR-04.safe|safe|PASS|∅|True|
|M.CR-04.mutant|mutant|MUTATION_DETECTED|CR-04|True|
|M.CR-05.safe|safe|PASS|∅|True|
|M.CR-05.mutant|mutant|MUTATION_DETECTED|CR-05|True|
|M.CR-06.safe|safe|PASS|∅|True|
|M.CR-06.mutant|mutant|MUTATION_DETECTED|CR-06|True|
|M.CR-07.safe|safe|PASS|∅|True|
|M.CR-07.mutant|mutant|MUTATION_DETECTED|CR-07|True|
|M.CR-08.safe|safe|PASS|∅|True|
|M.CR-08.mutant|mutant|MUTATION_DETECTED|CR-08|True|
|M.read.safe|safe|PASS|∅|True|
|M.read.mutant|mutant|MUTATION_DETECTED|CR-01,CR-02,CR-03,CR-04,CR-05,CR-06,CR-07,CR-08,CR-READ_ERROR|True|
|M.stale.safe|safe|PASS|∅|True|
|M.stale.mutant|mutant|MUTATION_DETECTED|CR-STALE,CR-TIMEOUT,CR-WAIT-MISMATCH|True|
|M.partial.safe|safe|PASS|∅|True|
|M.partial.mutant|mutant|MUTATION_DETECTED|CR-02|True|
|M.pid.safe|safe|PASS|∅|True|
|M.pid.mutant|mutant|MUTATION_DETECTED|CR-PID,CR-READ_ERROR|True|
|M.boot.safe|safe|PASS|∅|True|
|M.boot.mutant|mutant|MUTATION_DETECTED|CR-BOOT|True|
|M.stable.safe|safe|PASS|∅|True|
|M.stable.mutant|mutant|MUTATION_DETECTED|CR-REACTIVATION,CR-STALE,CR-WAIT-MISMATCH|True|
|M.timeout.safe|safe|PASS|∅|True|
|M.timeout.mutant|mutant|MUTATION_DETECTED|CR-STALE,CR-TIMEOUT|True|
|M.lock.safe|safe|PASS|∅|True|
|M.lock.mutant|mutant|MUTATION_DETECTED|CR-LOCK|True|
|M.version.safe|safe|PASS|∅|True|
|M.version.mutant|mutant|MUTATION_DETECTED|CR-SNAPSHOT|True|

17项错误行为均在声明的合成subject触发，并由冻结独立oracle接受其违规见证；它们覆盖逐项忽略8字段、读错视为匹配、陈旧快照、部分字段、错误PID/boot、稳定错误降级、超时续等、缺锁和跨版本拼接。其真实性范围为SIMULATION_ONLY/1，未主动改变真实UID/资源/WSL，也未运行BC40或原RootIPC等其他套件。

原始64文件SHA与Root资格结果逐一一致；当前host额外只读reference按实际observed/错误/身份/boot/版本和decision检查重新验证安全样本及每个mutant见证，错误0，未import或重放目标程序。[独立reference](evidence/REGRESSION_REFERENCE_CHECK.json)。

该阶段global_before=1/global_after=450，449次包含entry1＋每job预付6＋Root重算1；未用部分保守占用，硬限512。更广的故障调度及物理接口覆盖保持冻结声明，不把合成通过扩大成完整资源门。
