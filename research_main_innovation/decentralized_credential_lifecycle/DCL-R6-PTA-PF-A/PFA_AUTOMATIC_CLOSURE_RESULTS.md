# 自动关闭与真实退出

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**正常结束自动关闭和回收确认；PF-A5=CONDITIONAL_PASS，正式Root异常关闭未额外注入。** 本批extra fallback cleanup0、人工清理0。

PF48资格形成后，冻结流程自动调用stop_tree(PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE)。CLOSED在BOOTTIME131.278564941落记录；child838停止结果131.292400647为stop_exit0/empty=true/父组不存在。独立停止器849看到CLOSED后继续冻结清理，停止结果131.318848141同样成功。

协调器445对child838直接waitpid，raw_wait_status0/exit0。系统journal记录C00服务与停止服务均Deactivated successfully；精确kernel退出瞬间与最后Owner死亡时点没有单独打点。自动post同boot在131.528678948确认角色0、UID999进程0、父组不存在，读取已登记PID/starttime/boot核验无错误；其WSL客户端随后已reaped。事后独立只读导出再次确认角色/组空。

正常关闭没有产生STOP_REQUEST，CLOSED为实际终态支配对象。没有人为补STOP或伪造异常。17项异常变异都只作用于冻结合成Subject；主实例实际正常结束。

内部mr_close_state未生成，自动审计保持internal_cleanup_status=UNKNOWN；batch_state仍CALIBRATING、phase仍RUNNING，CLOSED对其继续发放具有支配作用。进程组空没有被用来改写内部状态或授予资源资格。

[实际关闭/退出原件汇总](evidence/ACTUAL_RESULTS.json) · [journal消息索引](evidence/JOURNAL_MESSAGE_INDEX.json) · [自动审计/独立导出](evidence/POSTRUN_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
