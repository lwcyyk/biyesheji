# 实际命令与调用次数

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

实际共有3次行政WSL调用：53文件静态部署/原生compile、只读平台与独立实例预检、退出后的完整原件/源/journal导出。argv、双流、SHA及耗时位于[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)及evidence/commands/01–03.result.json。

冻结host入口调用一次，active Native argv为：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch12
```

冻结host自动post一次，目标admin_postexit.py --post-exit-export；active/post/外层均exit0。确切原始计划见[active调用](evidence/ACTIVE_ENTRY_INVOCATION.json)与[自动post计划](evidence/STARTUP_POSTEXIT_PLAN.json)。

统计为1 active＋1自动post＋3行政WSL，共5次；目标角色/测试重跑0。其他主机操作仅摘要、账/结构审查、报告及行政汇总。没有Root seal手工重放、管理器恢复或未来批次自动启动。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
