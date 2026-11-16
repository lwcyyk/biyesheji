# MR-A授权及绑定

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

本次用户明确批准有限阶段A，绑定最终r5。实际scope=MR_RECOVERY_DIAGNOSTIC_ONLY，Full=false，Manager诊断及关闭注入批准=true。冻结方案以单项C10后返回78为收尾；完整C10–C12链及阶段B、S34/门18/F1F4保持关闭。本轮在更早前言失败，C10范围没有实际触发。

manifest `e32453a883905db0089e7fd480f43283edeba2d87604407bbea55f4b14c2d395`，execution_lock `a8358f504248377340e86c5d0b79210fd18c7c3207096f9fe7c7e27e4b928c64`。46项/31程序host及45份Linux源/输入实际摘要一致，原生Python3.12.3核验通过。回执SHA `88dcbeb912ad799cf1f1ab64fb0f90aaed01ce8261d68758d5b26d176cbafd0a`，原文SHA `024f02f21d273943ed39542a9d332e85f068d7bce3342ceabba129761f34144a`，控制目录为ManagerRecovery-Fix/authorization/batch10-r5。申请正文一处裸r4为历史文案残留，源码/执行锁/最终摘要及本次明确版本均为r5，历史文本保持。

运行boot=038cf87f-53c5-464e-ba0b-c2f20ae941e4；Root owner PID12242/start699487跨exec，初始scheduler PID12300/start699639。预检及同进程exec通过，当前窗口目录与一次认领建立；正式T0、deadline、counter/journal均未初始化。旧CalDiag及历史账保持。

[实际授权](evidence/execution_authorization.json) · [源码与范围准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [入口实际argv](evidence/ACTIVE_ENTRY_INVOCATION.json)。
