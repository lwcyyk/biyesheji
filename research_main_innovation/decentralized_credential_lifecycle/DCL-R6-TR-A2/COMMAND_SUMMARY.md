# 实际命令和调用分类

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

WSL实际5次＝1冻结active＋1冻结自动post＋3行政（62源部署/compile、只读基础环境、退出后完整235原件/64源/journal导出）。精确argv、raw双流、SHA与耗时见[行政计划](evidence/ADMIN_COMMAND_PLAN.json)及commands/01–03.result.json。

active为/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ra01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch14；自动post为同解释器/参数的admin_postexit.py --post-exit-export。均Ubuntu-24.04/root，active/post/外层exit0。

唯一host入口及其内部实际argv见[调用原件](evidence/ACTIVE_ENTRY_INVOCATION.json)和[post计划](evidence/STARTUP_POSTEXIT_PLAN.json)。没有当前源码修复、系统库写入、依赖安装、WSL主动重启、手工seal/API/checker重放或下一批自动启动。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
