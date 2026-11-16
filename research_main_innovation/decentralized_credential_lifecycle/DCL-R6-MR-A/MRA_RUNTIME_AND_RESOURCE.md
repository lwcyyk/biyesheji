# 时间、预算及资源

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

A4：启动host调用2.063384400秒，exit125；T0/deadline/R=null，counter、intent、journal及Root检查预付均未创建。无预算账时保持未初始化，不能填写R=0或虚构配对事务。

预检开始→通过1.159044165秒，开始→same-PID entry验证1.458890790秒；child wait退出在预检开始后1.587896289秒。所有Native跨度来自同boot CLOCK_BOOTTIME；host perf_counter单列。完整300秒校准时间继续TIME_FEASIBILITY_UNRESOLVED_NO_CALIBRATION。

原资源合同1,000,000/1,800/300/100,000/64,082/提前1,740、AS1GiB和Payload4tasks保持。Root bootstrap自限1GiB并被初始scheduler继承；Payload服务/slice未激活，实际Payload峰值和任务高水位不适用，Root RSS峰值未采样。单位定义安装按冻结预检执行，实际资源使用资格尚未到C00。

保存22份Native常规原件及46份冻结源导出；socket/非regular对象另记元数据。STOP/CLOSED存在，原生ZIP缺失。当前所有受控角色为空、父cgroup不存在。历史6,068份文件及47误路径副本最终hash复核，旧CalDiag账38,729保持。

[真实时间书签](evidence/EXECUTION_TIMELINE.json) · [Native审计](evidence/POSTRUN_AUDIT.json) · [历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。
