# 实际命令与分类

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

部署、平台审计、角色审计、完整原件导出共4次行政WSL调用，精确argv、前后时间、原始双流及SHA见[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)和evidence/commands/01–04.result.json。行政调用没有导入生产目标或重放checker。

active由冻结host entry执行一次，Native精确argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch11
```

冻结host自动post一次：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/startup_lifecycle.py --post-exit-export
```

前者exit125，后者exit1；源码修复/重跑/手工finalize/停止后备0。其余主机操作仅准备授权、hash/内存compile、保存原件、报告与归档。完整源码与运行副本分别保存在FROZEN_SOURCE_REFERENCE及独立batch11导出目录，摘要随包提供。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
