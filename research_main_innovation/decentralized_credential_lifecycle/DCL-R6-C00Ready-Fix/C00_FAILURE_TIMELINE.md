# batch07 C00执行时序与时钟边界

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

真实顺序从单会话bootstrap开始：预检→sealed claim→同进程exec进入Guard→Root消费认领→fork scheduler→T0/初始账→systemd外部stop→C00 start请求→manager MainPID轮询→八项聚合复核拒绝→CLOSED/组空/父waitpid/原生seal。systemd为Root创建C00目标进程，Guard未先作为C00服务启动；这些角色应分别记录。

|journal单位|MONOTONIC µs|实际消息|
|---|---|---|
|dclr6batch07-stop.service|73824617|Starting dclr6batch07-stop.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role external-stop --batch-root /var/lib/dcl-r6/batch07...|
|dclr6batch07-stop.service|73825225|Started dclr6batch07-stop.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role external-stop --batch-root /var/lib/dcl-r6/batch07.|
|dclr6batch07-c00.service|74068353|Starting dclr6batch07-c00.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/batch07 --case C00...|
|dclr6batch07-c00.service|74093214|dclr6batch07-c00.service: Main process exited, code=killed, status=9/KILL|
|dclr6batch07-c00.service|74093317|dclr6batch07-c00.service: Failed with result 'signal'.|
|dclr6batch07-c00.service|74093576|Stopped dclr6batch07-c00.service - /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/guard.py --role controller --batch-root /var/lib/dcl-r6/batch07 --case C00.|
|dclr6batch07-stop.service|74141325|dclr6batch07-stop.service: Deactivated successfully.|

BC原34条事件、15条内部命令双流及7条run-boot journal均已从原始包复核。运行boot060a08fc…、Owner828/start7252跨exec一致，子scheduler886/start7372。T0=73.768774900；CLOSED=74.078122459，T0+0.309347559；组空74.095938066，T0+0.327163166；父waitpid raw32000/exit125。R0，C00票据、探针和BOOT_START没有生成。

C00 journal在同一MONOTONIC域的Starting→KILL相隔24.861ms。BC/账时钟为BOOTTIME，journal另有REALTIME，Host耗时为perf_counter；未校准的时钟不做跨域差值。八项读取无独立时间戳，具体失败点只能按控制流定位。

私有sealed原件不复制到本报告；审计只使用其摘要。当前未执行新的WSL、systemd查询或诊断。[机器时序](evidence/BATCH07_FAILURE_TIMELINE.json)、[batch07原包](../DCL-R6-batch07/BATCH07_EVIDENCE.zip)。
