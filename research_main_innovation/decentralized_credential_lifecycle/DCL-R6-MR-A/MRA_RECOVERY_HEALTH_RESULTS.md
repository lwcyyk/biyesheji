# 恢复健康动态状态

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

A1=UNRUN_STARTUP_FAILED_PRE_T0。C00、C09、MR64及后续恢复均未启动；RECOVERY_HEALTH_PASS=false，含义为尚未取得该结果。

原CalDiag真实C09 PASS、T0+48.592秒和194项/41变异保持历史归属。本批对新r5只取得预检/启动身份的实际证据，初始健康检查在T0之前失败。首错为IPC_STATE_MISSING，未发生新的ACK/Receiver/退出/恢复事件，也未达到预声明的C10后返回78故障点。

修复建议应限于PRE_WINDOW与ACTIVE窗口的检查点职责：预窗只读manager查询仍核当前boot、sealed初始身份、SOURCE/receipt、STOP/CLOSED和新目录约束；运行窗建立后继续强制state/预算。不能将allow_uninitialized无差别放开到恢复或正式执行。当前源码冻结，本轮不实施修复。

[实际阶段结果](evidence/MRA_RESULT.json) · [根因链](evidence/FIRST_FAILURE.json)。
