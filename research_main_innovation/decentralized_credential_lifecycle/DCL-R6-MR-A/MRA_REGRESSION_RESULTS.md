# 64项回归与8项变异

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

A3：冻结64项实际执行0、获接受0；8项变异实际执行0、检出0。所有结果为UNRUN_STARTUP_FAILED_PRE_T0，原始mr_case_###及MR_QUALIFICATION均未生成。

这些数量表示阶段未到达，不能登记为已运行后MUTATION_NOT_DETECTED。当前目标行为未被实际exercise，正控制/注入/独立oracle/变异效果均继续待验。原31程序、64固定输入及独立oracle保持冻结，本轮没有运行关闭后的独立重放来补数字。

READY64/RootIPC56/BC40/H34、C00–C09等前置同样尚未启动；过去CalDiag通过结果保持各自范围。当前也没有新的PASS_BOUNDED。

[机器数量](evidence/REGRESSION_ACTUAL.json) · [全部冻结输入](evidence/FROZEN_SOURCE_REFERENCE/inputs/manager_contract.json)。
