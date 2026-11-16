# batch05 Root 协调器边界与实际生命周期

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

Root 协调器确实启动并参与本批监督。稳定身份来自 `batch_state.json`：父 PID 3834/start_ticks 387752，scheduler 子 Launcher PID 3835/start_ticks 387762；boot 均为 `8f92c77b-39bb-4526-a85c-174189b689ce`。独立 external-stop PID 3839/start_ticks 387769，STOP_ARMED 绑定原 stop_at 与控制 socket。

|职责|实际证据及范围|
|---|---|
|身份与启动|直接 fork、子身份握手及 pidfd 控制流见冻结 guard.py:963–1006；状态文件保存父子稳定身份|
|C09H 独立重算|root_verify_c09h 实际接受 34 项；额外 34 次全局访问|
|真实持久交接|C09 ready 前失败；commit/ACK/交接状态/专用退出见证均缺失|
|waitpid|源码普通退出分支调用 waitpid；外层退出 125 与该路径一致。原始 raw_wait_status 独立收据缺失，成功交接退出23见证未取得|
|停止|STOP_REQUEST 后 external-stop 发布 CLOSED、stop_exit=0、payload 组为空|
|Root 结束|scheduler 等待至 T0+300 后 C09_NOT_READY，finally 清理和 native seal；父透传 exit125；命令30查询两个 Root PID 均为空|
|权限与行为缺陷|特权审查替换 intent 导致 uid999 读取失败；C09 等待循环延迟观察闭合|

首次 STOP_REQUEST=T0+20.861903589 秒；CLOSED=T0+20.909951317；payload 组空=T0+20.927591657。scheduler 的后续 LAUNCHER_ERROR=T0+300.029941411，最终组空复核=T0+300.043546214；外层命令墙钟 300.5839319 秒。两段停止延迟分别报告，Root 管理组件未实现迅速随 CLOSED 退出。

guard.py:834–835 仅检查 `C09.ready` 与时间；闭合后继续等待至共享校准 T0+300。真实 handoff 状态尚未发布，父协调器没有生成该状态专用的退出见证；普通错误退出与交接成功分类分别保留。

Root 父、Root scheduler 和外部停止器属于 payload slice 外的 TCB；4 tasks 与条件性 4 GiB 仅对应已批准 payload 边界。新增 Root CPU/RSS 峰值为 UNMEASURED，外层生命期与 34 次审查访问已记录。AS4 的普通映射、内核特殊映射与可信内核/Root/fsync/调度假设保持。本批观察范围内未见预算/输入变更、无关单位操作或额外任务。

命令 28：stop service exit124、C09 SIGKILL、父 slice inactive；命令 27 专用 UID 空，命令 29 父组不存在，命令 30 父子 Root PID 空。事后默认/GC 属性仅作清理观察。原始证据见 [batch_state.json](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/batch_state.json>)、[STOP_ARMED.json](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/STOP_ARMED.json>)、[时间线](evidence/RUNTIME_TIMELINE.json)、[命令24](evidence/commands/24.result.json)、[命令30](evidence/commands/30.result.json)。
