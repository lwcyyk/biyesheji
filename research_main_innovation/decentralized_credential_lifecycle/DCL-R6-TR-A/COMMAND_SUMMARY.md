# 实际命令及分类

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

唯一active：冻结Windows入口调用Ubuntu-24.04/root的/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/tr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch13，exit125。

唯一自动post：admin_postexit.py --post-exit-export，原冻结host在active返回后真实发起，exit0。确切argv见[active调用](evidence/ACTIVE_ENTRY_INVOCATION.json)和[post计划](evidence/STARTUP_POSTEXIT_PLAN.json)。

另有4次行政WSL调用：57文件部署/原生语法；基础只读平台预检；拒绝后的1241运行时hash/包日志/空对象审计；57源＋3现行库只读导出。全部精确argv/双流/耗时/SHA见[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)及commands/01–04.result.json。

共6次WSL调用＝1 active＋1自动post＋4行政。没有依赖安装、系统配置修改、reset-failed、WSL重启、手工seal或目标重跑。其余主机步骤仅授权/摘要、原件审查、报告与包验证。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
