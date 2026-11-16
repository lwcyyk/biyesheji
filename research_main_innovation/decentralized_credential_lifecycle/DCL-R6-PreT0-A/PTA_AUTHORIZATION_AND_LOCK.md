# 阶段A授权、版本与隔离锁

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**已按 NORMAL_START 调用冻结入口一次，实际返回125；本批随后自动关闭。** 用户第4节将正常预窗初始化列为最高优先级，第14节要求按初始化、检查点、PT64顺序立即执行；据此选择双方共同允许的较小正常模式。PREWINDOW_ABORT保持UNRUN。本次授权原文没有书写模式字面量，这一选择属于对明确正常初始化目标的执行映射，已在启动前公告并记入回执说明。

|绑定对象|核验结果|
|---|---|
|最终版本|PreT0Recovery-static-1/r3，51文件＝33 Linux程序＋2 host程序＋16输入|
|manifest SHA-256|34c9c4642c4ff8c68183845b66f49f1670efa3349ec82e07d80e8bbabfd86ab7|
|execution_lock SHA-256|af8de2c099813d2e3018c6d46b2e95b435c2e75a122d32b73b3f96e3c47b58ec|
|部署|49份Linux源/输入，Root:Root/0644，目录0755，无额外ACL/pyc；目标模块导入0、33程序原生内存compile通过|
|主机程序|35程序文法/compile通过；主机入口Python3.14，正式Native精确/usr/bin/python3.12 3.12.3|
|boot_id|24fc4fce-f68c-4ab5-8662-261ed17d831b，部署/预检/执行/首次事后审计一致|
|身份|Root827/start6546；child887/start6672；停止服务892/start6693；当前UID999/GID989和组符合合同|
|环境|内核6.18.33.2-microsoft-standard-WSL2；systemd255.4-1ubuntu8.18；cgroup v2；初始failed仅mnt-e.mount|
|独立namespace|/var/lib/dcl-r6/pt01源；/var/lib/dcl-r6/batch11运行；dclr6batch11.slice；启动前运行目录/单位/cgroup均无|
|标签差异|冻结JSON、batch_identity.py和execution_lock一致指定控制目录DCL-R6-PreT0-Fix/authorization/batch11-r5；报告正文称batch11-r3，phase_A_identity_rule另残留r1文字。采用摘要绑定的实际路径，源码版本仍为r3，历史batch10保持关闭|
|历史保护|启动前锁6,522份历史文件，4份根导航另存原字节；误路径副本只读/hash|

回执中的RootIPC/单会话/同父恢复兼容字段按冻结schema置true；实际scope仅PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START，Full/MR诊断/预窗77注入均false。兼容字段不扩展到C09发放权限。完整用户原文与SHA绑定，51份源码、冻结模板、历史锁原件保持。

主机精确入口：`python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\pt01\host\windows_entry.py --activate`，环境PYTHONDONTWRITEBYTECODE=1。唯一active WSL argv与只读post-exit argv见[命令记录](evidence/ACTIVE_ENTRY_INVOCATION.json)及[自动收尾计划](evidence/STARTUP_POSTEXIT_PLAN.json)。共有1次active、1次自动post、4次部署/只读行政WSL调用；行政调用均无测试/恢复/T0创建。

[源码与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [部署](evidence/DEPLOYMENT_RESULT.json) · [平台](evidence/ENVIRONMENT_AUDIT.json) · [回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json) · [执行后源码](evidence/SOURCE_AFTER_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
