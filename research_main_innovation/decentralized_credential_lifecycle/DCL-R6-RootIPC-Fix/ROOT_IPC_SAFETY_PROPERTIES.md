# IPC-1 至 IPC-10 静态性质与验证责任

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

以下为源码检查点和未来证据映射，动态结果统一UNRUN。权限和有界等待属于通用基础设施修复，原创性严格分离实例保持0。

|性质|检查谓词|最终源码检查点|未来证据|
|---|---|---|---|
|IPC-1 AuthorizedRead|shared intent999:989/0600；payload只读收据0:989/0640|[root_ipc.py:21 policy](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)|P.read/replace/receipt_read/unauthorized；M.root600/permissions|
|IPC-2 RootIntegrity|输入目录Root拥有；Root私有0700/0600；保护收据group只读|[root_ipc.py:72 directories](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)|P.private_write/private_read/receipt_write；真实C09来源核验|
|IPC-3 AtomicPublication|发布前metadata/ACL、完整write、文件和双目录屏障、发布后stat|[root_ipc.py:91 publish](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)|P.fault_*；P.umask/repeat；故障后无grant|
|IPC-4 NoPathSubstitution|Root发布固定名单、逐级NOFOLLOW/dirfd、目标type/nlink/identity|[root_ipc.py:72 directories](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)|P.outside/symlink/hardlink；未来调度攻击待验证|
|IPC-5 IdentityBinding|Root共享收据和handoff窗口绑定batch/boot/源/执行锁/身份|[c09_handoff.py:115 check_base](<../../../DCL-R6-isolated-verification/ri01/src/c09_handoff.py>)|P.bad_batch/boot/lock/digest；M.batch；真实C09|
|IPC-6 NoFalseHandoff|原持久ACK＋活receiver＋waitpid23＋fresh-read判据保持|[c09_handoff.py:168 sender_prepare](<../../../DCL-R6-isolated-verification/ri01/src/c09_handoff.py>)|M.exit23；C09H34；真实C09|
|IPC-7 StopDominance|每轮checkpoint，ready之后/ACK之前复查；缺监督立即拒绝|[root_ipc.py:143 checkpoint](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)|T.stop_before/after_ready/closed_wait/fd_cancel/socket_cancel；M.stop/closed|
|IPC-8 NoReactivation|CLOSED吸收；锁内发布与恢复复查；迟到ACK不重开|[c09_handoff.py:323 resume_admission](<../../../DCL-R6-isolated-verification/ri01/src/c09_handoff.py>)|T.late_ack/ack_stop；M.reactivate/closed；真实恢复|
|IPC-9 SingleClassification|原revision/id/classification_count=0→1与直接父见证|[c09_handoff.py:297 coordinator_witness](<../../../DCL-R6-isolated-verification/ri01/src/c09_handoff.py>)|M.duplicate；C09H及真实一次恢复|
|IPC-10 BudgetPreservation|24预算/资格函数AST与range_core文件保持；Root新访问原账记入|[guard.py:563 _reserve](<../../../DCL-R6-isolated-verification/ri01/src/guard.py>)|原C02/C05/C11、S34/门17；IPC前后原账比对；无退款/新窗|

共同前提：冻结payload/Root代码，可信内核/systemd/Root，原CPY312-UBU24/1和AS4-PAYLOAD/1条件；目录无未审查ACL且同一ext4设备；文件系统和调度语义支持实际屏障与终止。任意恶意同UID写者的完整账真实性、Root失陷、介质回滚、宿主断电及严格实时性未获得扩展认证。

Root发布路径的抗替换与旧预算读路径的额外强威胁分别登记，见[权限合同](ROOT_PAYLOAD_PERMISSION_CONTRACT.md)。本轮通过静态检查的谓词仍需专项56、C09H34、真实C09和完整C/S/门链产生实际接受及拒绝见证。
