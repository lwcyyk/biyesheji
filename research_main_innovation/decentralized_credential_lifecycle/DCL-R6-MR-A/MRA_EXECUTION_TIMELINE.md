# MR-A实际时间线

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

|事件|CLOCK_BOOTTIME|自预检开始秒|
|---|---:|---:|
|预检开始|6994.920257185|0.000000000|
|预检通过|6996.079301350|1.159044165|
|同PID entry验证|6996.379147975|1.458890790|
|初始child记录|6996.425596608|1.505339423|
|STOP记录|6996.456509400|1.536252215|
|首错记录|6996.461565999|1.541308814|
|CLOSED记录|6996.462158609|1.541901424|
|父停止结果|6996.480144993|1.559887808|
|child wait125|6996.508153474|1.587896289|
|最终UNKNOWN记录|6996.523022119|1.602764934|
|seal错误记录|6996.532321472|1.612064287|

本批boot=038cf87f-53c5-464e-ba0b-c2f20ae941e4，Root12242/start699487，scheduler12300/start699639。抛错发生在child记录与STOP采样之间，精确raise时点未打点。ABORTING由冻结控制流及后续CLEANUP文件见证，临时状态精确发布时刻缺独立记录。

初始化顺序为sealed认领/exec→child_admission→health(initial)→query(record=True)→root_checkpoint要求state→IPC_STATE_MISSING。后续创建T0/账的分支从未执行。自动父停止与abort尝试并发，不能把各条采样强行解释成单线程严格总序；原始每个actor/退出状态均保存。

[结构化时间线](evidence/EXECUTION_TIMELINE.json) · [原始stdout](evidence/windows_entry.stdout.raw) · [原始stderr](evidence/windows_entry.stderr.raw)。
