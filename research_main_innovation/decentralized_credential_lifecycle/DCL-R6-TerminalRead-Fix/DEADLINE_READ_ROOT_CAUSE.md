# 关闭后期限读取根因

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

**CLOSED后的只读审查进入了复用的活动态辅助函数。** 旧P.runtime_checkpoint虽然收到terminal_inspection=True，_phase_guard仍先执行_phase_deadline(G)；后者无条件G.state，G.validate_state_document看到stopped即抛BATCH_STOPPED。

terminal_inspection只影响_cancel和后续snapshot比较，无法影响之前的期限来源读取。P.seal_applicability捕获AdmissionBlocked并返回NATIVE_SEAL_UNRESOLVED，解释了没有独立SEAL_ERROR/traceback且底层G.seal未运行的现象。

旧state/phase/预算均有完整持久原件；本次关键信号是CLOSED131.278564941先于defer分类131.332716174。捕获异常精确抛出时点仍UNKNOWN，BATCH_STOPPED是冻结调用图与当时CLOSED共同限定的源码追溯结果，未伪装成实际异常日志。

新版本保留原G.state及PF期限/活动锁机制；seal直接接入独立终态只读接口。该接口从现有state读取原window，身份/完整性/预算/版本分别验证，不以活动态许可为前提。未决错误由调用者保留具体类型和摘要到新批的pt_seal_disposition，原生applicable字符串协议保持。

该修复解除已定位的前置依赖；退出等待、真实打包、落盘、最终摘要和资源时限等仍需独立动态验收。

[原依赖证据](evidence/HISTORICAL_FAILURE_FACTS.json) · [新分流diff](evidence/FULL_DIFF.patch)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
