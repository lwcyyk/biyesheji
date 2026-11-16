# batch04资源校准实际结果

Material Passport：RESOURCE_GATE_FAILED；C00–C08局部PASS；C09监督器故障；后续未运行。

|case|实际观察与结果|
|---|---|
|C00|入口kernel/身份/AS/cgroup及映射谓词PASS|
|C01|正常执行与监督器握手PASS|
|C02|范围预留、实际内存child、96MiB局部AS及MemoryError判据PASS|
|C03|16MiB共享映射，4096信用/操作与可见数据PASS|
|C04|父组4tasks；第五task实际EAGAIN，pids.events max由0到2，PASS|
|C05|普通全局/局部并发计数的冻结判据PASS|
|C06|预期超时/Watchdog停止判据PASS；信号退出属于本case预期|
|C07|Controller预期exit23，PASS|
|C08|Watchdog故障后的冻结拒绝/退出判据PASS|
|C09|已ready且launcher预定exit23；停止器误判UNEXPECTED_LAUNCHER_EXIT，缺root成功收据；分析FAIL_SUPERVISOR|
|C10/C11/C12|UNRUN_RESOURCE_GATE|

尝试进入10个C case，root机器结果PASS文件9份。C09没有机器PASS文件，分析结果与原始缺件分别登记，原件没有补写。C00–C08结果不替代完整资源资格。

运行boot99fbdfbd-f0b9-4cf2-8914-0d71867b6138，T0=199.727213695，deadline=1999.727213695，stop_at=1939.727213695。C09.ready在209.043682578；关闭209.077071432，T0后9.349857737秒；组空确认209.089624773，T0后9.362411078秒。尚未接近300秒软界。

父组内核charged memory peak观测125067264字节（119.2734375MiB）；该量包括cgroup计费内存，RSS树峰值没有取得认证。实际pids.current观测4，pids.max4；C04拒绝第五task。子进程LimitAS原硬/软1GiB，C02自行降低到96MiB；AS4普通映射及内核特殊映射单列条件保持。

停止器真实exit125和C09控制器SIGKILL见运行boot的40条journal。关闭后专用UID进程查询为空、parent cgroup不存在。后续manager查询显示inactive/default字段，随后boot观察已变化；实际执行属性以运行ticket/startup/journal为准。
