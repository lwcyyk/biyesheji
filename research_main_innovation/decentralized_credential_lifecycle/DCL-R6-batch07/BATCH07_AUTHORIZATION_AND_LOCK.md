# batch07授权、冻结锁与真实执行关系

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

用户明确批准BootContinuity-static-1/r4的部署、单会话激活、sealed凭据/一次认领、同进程恢复、40/56/34项回归、C/S/门及完整资源资格后自动F1→F4。授权原文和实际回执分别见[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[execution_authorization](evidence/execution_authorization.json)。静态历史材料的未授权标签按其记录时点保留，本次权限由新原文hash绑定。

|对象|SHA-256|
|---|---|
|static_manifest.json|4cfebfbcd17fd39addbbab6a826ffec24d4cf8f586dfdd230c4cf397519e5863|
|execution_lock.json|4a71cd1135a82f46ae07fdb3abf49376732b6894b1fc00dc6d6accb9dda961fe|
|boot_contract.json|bc500b4512e3fb8bb2ddb966433ab20ebbe066caade04a944c23eba202065b40|
|root_ipc_contract.json|c402def08f2b7f9e81b077ab15dc50ce0dd73464cf53b4d5459a0336c914e3b3|
|c09_contract.json|649c71b6a56f2f61a4929e013b26a83833b0ebd5f5d410c600a61d20ec0aebe3|
|safety_contract.json|21366eb093350abea8ec808a009b4854b8d4334085693b7e497fafc1b903793b|
|TASK_REQUEST.txt|525655c32e765ea37523fa587fdde1dcb46f62345dabb19e7569b7bcd154c3fd|

host32项（21份程序、11输入）摘要一致；部署31项Linux源码/输入为Root0:0/0644、目录0755，无ACL/pyc；Windows入口原字节保持。部署boot只作静态对象观察，激活未把它设为期望常量。实际动态资格由冻结Windows入口的一次WSL子调用自行建立。

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch07
```

本批活动入口仅调用1次；无独立Guard或resume重试。源代码在同一PID执行预检→exec，Root接入复核后fork scheduler；T0创建后C00服务复核首次失败，后续测试停止。冻结实际顺序仍为C00–C08→C09H34→RootIPC56→BC40→真实C09→同进程同窗一次恢复→C10–C12→S34→门17→资格→F1→F4。

新增BC访问上界已复核：entry1＋40×(预付11＋Root审查1)=481；C09H2245＋RootIPC505＋BC481=3231≤共同5000，完整校准62034≤100000。代码将这些测试绑定同一C09H ticket/T0+300软窗；本次未到这些阶段，整套耗时仍待实测，任何窗口不足只能停止。

[部署结果](evidence/DEPLOYMENT_RESULT.json)、[实际Windows调用](evidence/WINDOWS_ENTRY_PLAN.json)、[原始活动stdout](evidence/windows_entry.stdout.raw)、[冻结锁](evidence/execution_lock.json)、[命令索引](COMMAND_SUMMARY.md)。
