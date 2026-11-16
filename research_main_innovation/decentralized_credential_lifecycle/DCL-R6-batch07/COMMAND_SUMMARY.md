# batch07命令、时钟与原始双流

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

活动入口严格使用冻结windows_entry.py，内部只启动1次WSL。Windows入口原件保存实际argv、PID54916、UTC起止、perf_counter耗时及其WSL子进程exit125；执行工具外层PowerShell报告exit1，两层结果分别保留。

|内部序号|实际argv|BOOTTIME开始|BOOTTIME结束|exit|
|---|---|---|---|---|
|1|/usr/bin/systemctl show --property=Version --value|73.016418056|73.021129646|0|
|2|/usr/bin/systemctl list-units --state=failed --all --no-pager --no-legend|73.021257088|73.025621176|0|
|3|/usr/bin/systemctl list-units dclr6batch07* --all --no-pager --no-legend|73.029965946|73.03353329|0|
|4|/usr/bin/install -d -m 0750 -o root -g dcl-r6 /var/lib/dcl-r6/batch07 /var/lib/dcl-r6/batch07/inputs /var/lib/dcl-r6/batch07/reports|73.0339137|73.037705403|0|
|5|/usr/bin/install -d -m 0700 -o dcl-r6 -g dcl-r6 /var/lib/dcl-r6/batch07/out|73.0379433|73.041514615|0|
|6|/usr/bin/install -d -m 0700 -o root -g root /var/lib/dcl-r6/batch07/inputs/root_private|73.041638798|73.044704596|0|
|7|/usr/bin/install -m 0644 -o root -g root /var/lib/dcl-r6/bc01/inputs/dclr6batch07.slice /etc/systemd/system/dclr6batch07.slice|73.044809004|73.047430605|0|
|8|/usr/bin/systemd-analyze verify /etc/systemd/system/dclr6batch07.slice|73.047537942|73.058469284|0|
|9|/usr/bin/systemctl daemon-reload|73.05861274|73.257819045|0|
|10|/usr/bin/systemctl show --property=Version --value|73.405517797|73.411422842|0|
|11|/usr/bin/systemctl list-units --state=failed --all --no-pager --no-legend|73.411540866|73.416389157|0|
|12|/usr/bin/systemctl show dclr6batch07.slice --property=LoadState --property=ActiveState --property=TasksMax --property=MemoryMax --property=ControlGroup|73.420257212|73.427489283|0|
|13|/usr/bin/systemctl show --property=Version --value|73.66852163|73.673456702|0|
|14|/usr/bin/systemctl list-units --state=failed --all --no-pager --no-legend|73.673589621|73.677409493|0|
|15|/usr/bin/systemctl show dclr6batch07.slice --property=LoadState --property=ActiveState --property=TasksMax --property=MemoryMax --property=ControlGroup|73.680883546|73.685862816|0|

15条命令的stdout/stderr由原BC事件hex逐字节解码，见[INTERNAL_COMMANDS](evidence/INTERNAL_COMMANDS.json)及[internal_commands](evidence/internal_commands)。Guard后续锁定的stop/C00/systemctl调用按冻结控制流与原journal对应，C00票据未生成，因此没有其argv/实际status局部frame的完整持久快照；不补造execve审计。

|行政编号|用途|exit|
|---|---|---|
|[01](<evidence/commands/01.result.json>)|Deploy/verify31 frozen Linux static files and source-only metadata; no batch07 runtime or unit created|0|
|[02](<evidence/commands/02.result.json>)|First failure: audit controlled processes, preserve native/private bytes and31 source files, export exact17-unit RUN-BOOT journal|0|
|[03](<evidence/commands/03.result.json>)|Postfailure manager properties for exact current batch parent/C00/stop; temporal scope after failure|0|
|[04](<evidence/commands/04.result.json>)|Postfailure exact batch07 unit list|0|
|[05](<evidence/commands/05.result.json>)|Read exact17-unit run journal using journalctl 32-hex boot descriptor; preserve previous UUID-format parse rejection|0|

行政1仅静态部署；2–5发生在失败后，仅读状态、导出或限定journal。首次journal错误及更正原件都保存。原始stderr为WSL客户端UTF16LE提示前缀＋native UTF8 traceback，原字节不改，解码说明见[STDERR_DECODE](evidence/STDERR_DECODE.json)。活动日志BOOTTIME、journal MONOTONIC与Host时钟域分别使用。
