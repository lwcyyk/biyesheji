# batch07运行时、服务与停止证据

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

实际入口使用原生Python3.12.3（e50d…150f）、Ubuntu-24.04，运行时/来源字节检查完成后记录PREFLIGHT_QUALIFIED。systemd实际输出255.4-1ubuntu8.18，page4096，专用UID999/GID989及既有65534身份通过冻结断言；20份Linux源码实际语法编译无cache输出。kernel/架构等比较按冻结代码通过，不扩展为任意环境兼容。

Root父协调器PID828/start7252、scheduler子Launcher PID886/start7372、外部停止器PID890/start7379，boot均为060a08fc-fceb-48ff-a264-50c34312f97a。外部stop服务真实启动并发布STOP_ARMED；C00仅到Starting/MainPID观察，复核失败后停止。

|运行boot journal单位|MONOTONIC µs|原始消息|
|---|---|---|
|dclr6batch07-stop.service|73824617|Starting dclr6batch07-stop.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role external-stop --batch-root /var/lib/dcl-r6/batch07...|
|dclr6batch07-stop.service|73825225|Started dclr6batch07-stop.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role external-stop --batch-root /var/lib/dcl-r6/batch07.|
|dclr6batch07-c00.service|74068353|Starting dclr6batch07-c00.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/batch07 --case C00...|
|dclr6batch07-c00.service|74093214|dclr6batch07-c00.service: Main process exited, code=killed, status=9/KILL|
|dclr6batch07-c00.service|74093317|dclr6batch07-c00.service: Failed with result 'signal'.|
|dclr6batch07-c00.service|74093576|Stopped dclr6batch07-c00.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/batch07 --case C00.|
|dclr6batch07-stop.service|74141325|dclr6batch07-stop.service: Deactivated successfully.|

C00从Starting到Main process KILL的journal同MONOTONIC差为24.861ms，未出现Started。关闭记录使用BOOTTIME，CLOSED在T0+0.309347559，首次组空T0+0.327163166；父waitpid在T0+0.345387720得到exit125/raw32000；最终父seal前记录T0+0.354242602。该错误路径未等待至300秒，但C09/RPC/专项停止竞态尚未测试。

受控payload组本generation观测charged peak=782336B，pids.current=1/max4，memory.max4GiB，OOM计数0；精确RSS树峰值与Root RSS未采样。Root预检入口按冻结源调用setrlimit1GiB并继续；C00进程的实际8项比较值没有持久化，因此AS/身份失配字段尚未定位。

事后不同boot的manager显示C00/stop为not-found/default，不能用其LimitAS=infinity或User空值回推运行时。post-failure UID999/Root角色扫描为空，父cgroup不存在。源/配置/权限现场修复0，额外顺序Root探针启动0。clock口径：BC/native账为BOOTTIME，journal为MONOTONIC/REALTIME，Host为perf_counter/UTC；不混算未校准时钟。
