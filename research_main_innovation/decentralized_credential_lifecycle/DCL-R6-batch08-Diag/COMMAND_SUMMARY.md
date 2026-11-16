# 实际命令、控制路径和时钟索引

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

单次活动调用由冻结windows_entry.py完成，控制路径[WINDOWS_ENTRY_PLAN.json](<../DCL-R6-batch08/evidence/WINDOWS_ENTRY_PLAN.json>)与[WINDOWS_ENTRY_EXIT.json](<../DCL-R6-batch08/evidence/WINDOWS_ENTRY_EXIT.json>)保留实际argv、Windows PID和UTC/perf_counter区间。报告内同名副本逐字节相同。

|内部序号|实际argv|BOOTTIME开始|BOOTTIME结束|exit|
|---|---|---|---|---|
|1|/usr/bin/systemctl show --property=Version --value|48.79576021|48.800400337|0|
|2|/usr/bin/systemctl list-units --state=failed --all --no-pager --no-legend|48.800530633|48.804696872|0|
|3|/usr/bin/systemctl list-units dclr6batch08* --all --no-pager --no-legend|48.811429059|48.815486388|0|
|4|/usr/bin/install -d -m 0750 -o root -g dcl-r6 /var/lib/dcl-r6/batch08 /var/lib/dcl-r6/batch08/inputs /var/lib/dcl-r6/batch08/reports|48.815780138|48.819380929|0|
|5|/usr/bin/install -d -m 0700 -o dcl-r6 -g dcl-r6 /var/lib/dcl-r6/batch08/out|48.819561413|48.822722941|0|
|6|/usr/bin/install -d -m 0700 -o root -g root /var/lib/dcl-r6/batch08/inputs/root_private|48.822833924|48.825630879|0|
|7|/usr/bin/install -m 0644 -o root -g root /var/lib/dcl-r6/cr01/inputs/dclr6batch08.slice /etc/systemd/system/dclr6batch08.slice|48.825870755|48.8285123|0|
|8|/usr/bin/systemd-analyze verify /etc/systemd/system/dclr6batch08.slice|48.82863308|48.839149682|0|
|9|/usr/bin/systemctl daemon-reload|48.839380903|49.013424302|0|
|10|/usr/bin/systemctl show --property=Version --value|49.165027183|49.170454201|0|
|11|/usr/bin/systemctl list-units --state=failed --all --no-pager --no-legend|49.17061496|49.174500763|0|
|12|/usr/bin/systemctl show dclr6batch08.slice --property=LoadState --property=ActiveState --property=TasksMax --property=MemoryMax --property=ControlGroup|49.179994878|49.187604169|0|
|13|/usr/bin/systemctl show --property=Version --value|49.437837093|49.44243378|0|
|14|/usr/bin/systemctl list-units --state=failed --all --no-pager --no-legend|49.442578221|49.446836478|0|
|15|/usr/bin/systemctl show dclr6batch08.slice --property=LoadState --property=ActiveState --property=TasksMax --property=MemoryMax --property=ControlGroup|49.452467551|49.458744425|0|

内部命令双流由原始事件hex无损解码，见[INTERNAL_COMMANDS](evidence/INTERNAL_COMMANDS.json)。Guard/C00后续被冻结控制流执行，native票据/结果、startup及journal进一步见证；本表没有补造独立execve审计。

|行政编号|用途|exit|
|---|---|---|
|[1](<evidence/commands/01.result.json>)|Deploy/verify35 frozen Linux static files and source-only metadata; no batch08 runtime or unit created|0|
|[2](<evidence/commands/02.result.json>)|Closed minimal batch: export native/diagnostic bytes and frozen sources, scoped run-boot journal, controlled-process audit|0|
|[3](<evidence/commands/03.result.json>)|Postrun exact minimal parent/C00/stop manager state, not used as past runtime measurements|0|

行政1为静态部署，2–3在正常关闭后只读导出/清理核查。所有source与测试判据不改，无失败case重跑。run-boot journal使用同一UUID的32-hex表示限定17个既定unit；未运行unit无对应日志，不构造启动记录。
