# 启动连续性与稳定身份核验

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

**SAME_BOOT_CONFIRMED（本次有效最小启动范围）**。单会话预检、same-PID exec前后Root、scheduler和C00服务自查均绑定0cc7ff50-243e-41d0-bf3f-ba45b3f95695。exec前后Owner均438/start4792；C00自己的kernel_admission报告811/start4978和相同boot。

sealed能力实际生成并由Guard核验，seals15；摘要`38fdd579b3dddee236c6b7ff5957fbc44ca6770e92ef41aa5453ef2d90f9c2be`。原始能力材料保留Root私有路径和授权私有审阅包，普通日志/报告只展示摘要。实际初始认领消费一次，未发起独立重复认领或恢复测试。

3份原生readiness记录的目标身份均为811/start4978/该boot，双侧/proc中Pid与UID/GID等值对应当前目标。READY返回意味着冻结pidfd_open、G.identity前后比较及select存活检查路径已成功；但记录未独立保存每次pidfd检查时间/后侧starttime原始stat，成功属于控制流见证。精细pidfd事件覆盖与八项原始值完整性分别报告。

D08-4总体取 **FIELD_EVIDENCE_PARTIAL**：八字段值、双次原文、来源时刻/版本完整；单独pidfd时刻和wait函数精确返回点缺少打点，不能补造成实测值。D08-3 C00_PASS独立保留，不因记录粒度而改写安全判断。

[boot摘要](evidence/BOOT_IDENTITY_ACTUAL.json)、[原生字段重算](evidence/C00_FIELD_ACTUAL.json)、[原始readiness目录](<../../../DCL-R6-isolated-verification/batch08/native_snapshot/inputs/root_private/boot>)。
