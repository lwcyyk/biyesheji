# 首次失败与新增实现缺口

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

|登记|真实观察|结论|
|---|---|---|
|MRA-INIT-1|health(initial)在T0创建前调用query(record=True)，query的root_checkpoint默认要求batch_state|启动生命周期接线缺陷，IPC_STATE_MISSING在初始phase必然拒绝|
|MRA-CLOSE-2|state/BOOT_START/STOP_ARMED都尚未建立，abort无法得到运行deadline，留下UNKNOWN及后备超时|预窗口错误关闭上下文缺少已有的启动TCB期限；不能凭空造运行窗|
|MRA-SEAL-3|seal/Boot before_seal依赖不存在的batch_state，记录FileNotFoundError|预窗口封存分支缺口，原生自动seal未完成|

首错属于r5验证编排实现缺陷；静态检查未捕获该初始化依赖。预检manager查询正常，当前failed集合仅mnt-e，无新UNREVIEWED_MANAGER_FAILURE或C09交接错误可供裁决。原CalDiag实际通过和旧失败保持。

下一静态修复建议限于：把PRE_WINDOW只读身份/停止/boot核验与ACTIVE state检查明确分开；仅已认证初始阶段使用受限allow_uninitialized，恢复和正式执行仍要求state；预窗停止使用已绑定sealed/preflight期限与已登记Owner/child证据；预窗封存不依赖虚构T0/账，明确记录未初始化。增加对应前言故障和正向启动控制的独立fixture后重新冻结，再申请新独立有限A。

本轮源码/输入/判据/权限/上限修复0、重跑0、人工清理0、T0/预算重置0、自动下一批0。当前batch10已有CLOSED/一次认领事实，后续保持关闭，不能以缺T0为由重用同一目录或回执。

[首错链](evidence/FIRST_FAILURE.json) · [关闭原件](evidence/AUTOMATIC_CLOSURE_ACTUAL.json)。
