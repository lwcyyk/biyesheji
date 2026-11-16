# batch09授权、版本与静态执行锁

Material Passport：DCL-R6-batch09；2026-11-12；HOST_STATIC_ADMISSION；目标执行0；原版本C00Ready-static-1/r2。

**收到完整条件执行授权；当前静态准入为BLOCKED_STATIC_ADMISSION。** 用户允许准备新独立批次，全部资源资格满足后自动F1→F4；同时要求摘要匹配、保持冻结源码，并在锁或资源上界无法建立时止于准备阶段。本轮执行这一准备阶段停止分支。

原文与摘要见[evidence/TASK_REQUEST.txt](evidence/TASK_REQUEST.txt)及[授权接收记录](evidence/AUTHORIZATION_RECEIVED.json)。该记录只证明收到指令，运行授权收据尚待匹配新版本后建立。

|项目|本轮核验|
|---|---|
|冻结文件|36份全部摘要及长度匹配；23 Linux源码、1 Windows入口、12输入|
|manifest SHA-256|23f93f4b436ae4f5285d631735ca497855d84b598a7f55ca1b42a0c436b9e629|
|原execution_lock SHA-256|051cc0d995f084504fc393f176321eec09d03c8f4113509d8e253ab4e29dd8e3|
|源码/输入交叉摘要|全部匹配；24份程序仅作host AST解析，目标模块导入0|
|batch08归档|246清单成员/247条目逐流核验，外层SHA及内部原生ZIP CRC通过|
|实际源码/权限/系统修改|0|
|实际WSL/systemd/目标测试调用|0|

首项阻断D09-A01：冻结Windows入口固定读取DCL-R6-batch08回执并写其日志；boot_continuity.py固定ROOT=batch08、batch_id=batch08，参数choices仅接受该根；guard.py、root_ipc.py、C09接收单位及五份测试合同同样绑定batch08。直接执行会触及历史路径，新batch09回执也无法通过绑定。旧入口处于只读参考状态。

D09-A02：访问上界可重算为62,546；完整校准在300秒内成功完成的静态耗时依据仍缺。D09-A03：本轮要求的预算账异常负向资格测试尚未列入冻结17项。

[STATIC_EXECUTION_LOCK](evidence/STATIC_EXECUTION_LOCK.json)明确runnable=false、actual_target_argv=[]、T0/R/current_boot_id=null。它是一份阻断状态的行政锁。当前Linux版本、UID/GID、cgroup、boot及pidfd平台资格保留UNRUN_STATIC_ADMISSION；batch08历史值仅作为期望参考。单会话启动、当前nonce和一次性认领尚待准入成立后执行。

完整准入说明见[BATCH09_STATIC_ADMISSION](BATCH09_STATIC_ADMISSION.md)，最小补充范围见[BATCH09_MINIMAL_SUPPLEMENT_REQUEST](BATCH09_MINIMAL_SUPPLEMENT_REQUEST.md)。
