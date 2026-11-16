# DCL-R6-C09Fix

Material Passport：C09Fix-static-1/r1；静态修复完成，新动态执行0。

根因增量：旧快照分类缺陷与未完成的单方交接分开；batch04没有成功交接收据。新实现增加持久接收ACK、直接父waitpid见证、fresh-read及闭合/版本约束。预算核心、原探针、runner及五业务等10程序保持字节相同。

[最终裁决](FINAL_DECISION.md)、[时间线](C09_EXECUTION_TIMELINE.md)、[根因](C09_ROOT_CAUSE_ANALYSIS.md)、[状态机](C09_HANDOFF_STATE_MACHINE.md)、[源码锁](SOURCE_AND_INPUT_LOCK.md)、[batch05申请](BATCH05_EXECUTION_REQUEST.md)、[证据索引](EVIDENCE_INDEX.md)。
