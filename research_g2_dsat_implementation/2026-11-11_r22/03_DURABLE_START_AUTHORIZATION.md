# 持久一次性动作批准

执行日期按原始UTC记录及本地时间核对；目录名沿用研究者冻结的2026-11-11。过程：本对话内知情模型辅助工程实现、真实离线运行及源码复核；外部核验待取得。


测试作业Scope只证明进入本轮受控环境；Start另需`r22-one-shot-start/1`动作批准。其字段绑定authorization_id、START_OFFLINE_SUPERVISOR、environment/run/root/instance、source/config、SID、Python路径/hash/version、assigned epoch、scope、预算1及原批准记录digest。它来自研究者已批准的合成测试bootstrap，无法转化为真实部署许可。

权威消费文件按authorization ID规范索引。初始UNCLAIMED只发布一次；grant已存在而slot缺失时进入RECOVERY_REQUIRED。显示issuer/source/client别名与display不改变权威索引。

允许状态边为UNCLAIMED→CLAIMED→STARTED→FINISHED，以及CLAIMED/STARTED→UNCERTAIN。没有回到UNCLAIMED的边。每行包含seq、grant digest、epoch、owner、previous digest、effect count；严格UTF8/JSON、行结尾、大小、顺序和链完整性均核验。

原子边界为同物理实例的Win32独占文件handle，覆盖读取、校验、append、flush/fsync和效果前置判断。所有消费入口持有该lease；readonly Status可观察历史但不能消费。CLAIMED记录刷新并回读成功后才分配Store/Host/listener。effect receipt按批准唯一文件独占创建，效果至多1。

在诚实受控写者模型下，两个进程在同实例锁上串行；首个在UNCLAIMED状态成功claim，后续只见spent或不确定状态，均无法第二次建立效果。已写但ACK丢失仍保留CLAIMED/STARTED。append截断、missing slot、broken chain或unknown marker使接纳关闭，后续恢复无法免费发放机会。

边界前提：单机Windows/NTFS、可信研究者/SYSTEM/运行时、私有DACL及完整文件身份、正常OS下的进程崩溃。哈希链检查意外损坏，真实性依赖可信存储；恶意同SID、管理员篡改、卷回滚、介质故障和断电持久性尚未验证。

完整形式审计和实际slot状态在R22_AUTHORIZATION_CONSUMPTION_AUDIT.json。此次结论为限定模型内的离线工程保证，未推出分布式一致性或新算法优势。
