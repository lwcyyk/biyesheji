# 实际修复范围与RootIPC兼容性

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

最终host工作区`D:\毕业设计\DCL-R6-isolated-verification\bc01`；未来Linux位置`/var/lib/dcl-r6/bc01`。当前只有host文件，Linux部署/查询0，batch07目录创建0。

修改原guard.py的启动接入/授权/新证据门：Launcher进入BC.entry，Root/子scheduler接入复核；实际C00/C10服务确认；原RootIPC56后增加BC40；FORMAL业务导入前增加BC.formal_gate；父seal前保存启动闭合证据。原预算/原资源门算法24个函数AST保持。

root_ipc.py与c09_handoff.py只把batch06命名绑定改为batch07；权限、RPC、持久ACK、fresh-read、waitpid、CLOSED吸收和一次分类AST在命名归一后全等。14份其余程序逐字节保持，含五业务、预算核心、原探针、runner、C09H/RootIPC驱动与独立检查器。原56/34/34/17输入仅改未来batch命名。

新增boot_continuity.py、boot_continuity_regression.py、boot_continuity_oracle.py及host/windows_entry.py。Root boot私有文件位于原root_private下新子目录，仍用原RootIPC目录fd/ACL检查；新公共启动/BC资格收据0:989/0640，由新固定目标发布器写入。原RootIPC允许目标列表不扩大。

新source-only封装移除运行目录旧pyc：原17份3.12缓存保存在原件44项，不拿旧文件名/旧代码缓存充当新程序编译结果。新包20份Linux源码、1份Windows入口、11输入共32项。当前host解析3.12文法与host编译21份，无target import/body；实际3.12的compile(source)编排已实现，当前运行0。

新BC40在当前共同C09H ticket内计费，完成路径481、硬限512；C09H2245＋RootIPC505＋BC481=3231≤5000，完整校准硬界62034保持。新TCB无常驻增量，预检时间/AS及同进程恢复是需要新许可明确接受的差异。

[完整源码diff](evidence/SOURCE_COMPLETE.diff)、[完整输入diff](evidence/INPUT_COMPLETE.diff)、[原r4全部44项](evidence/original)、[静态检查](evidence/STATIC_CHECKS.json)、[最终锁](SOURCE_AND_INPUT_LOCK.md)。r1/r2/r3中间候选各32项及检查单独保留，最终申请仅绑定r4。
