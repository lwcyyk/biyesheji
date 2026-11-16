# batch06 Root/Payload 权限实际范围

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

结果为 **UNRUN_PREFLIGHT_FAILED / NOT_EXERCISED**。真实共享counter/intent尚未创建；UID999读取共享intent的实际次数0。Root发布器、临时文件、fchown/fchmod、replace、同步屏障和发布确认均未由本批程序执行。

|已存在对象|UID:GID|mode|ACL|证据范围|
|---|---|---|---|---|
|.|0:989|0750|[]|metadata只读观察|
|inputs|0:989|0750|[]|metadata只读观察|
|inputs/root_private|0:0|0700|[]|metadata只读观察|
|out|999:989|0700|[]|metadata只读观察|
|reports|0:989|0750|[]|metadata只读观察|
|inputs/BATCH06_AUTHORIZATION_TEXT.txt|0:989|0640|[]|实际安装字节/元数据|
|inputs/execution_authorization.json|0:989|0640|[]|实际安装字节/元数据|

元数据对应冻结准备结果，支持目录/授权文件安装正确；授权文件属于payload可读的Root保护收据。私有目录为空。UID999合法读取、65534拒绝、Root私有拒绝写入/伪造、发布前后inode/metadata、错误路径/链接及EIO拒绝都缺少本批动态见证，结果继续UNRUN。元数据观察没有替代非Root实际open测试。

部署源码44项的native副本在失败后逐字节导出，与r4全部对应。RootIPC56原输入及其静态权限策略保持，当前不授予IPC-1/2/3/4动态PASS。[事后审计](evidence/POSTFAIL_AUDIT.json)、[native字节锁](evidence/NATIVE_EXPORT_LOCK.json)、[冻结source锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)。
