# 生命周期与资源所有权

日期：2026-11-11。范围：R21明确批准的九目标及离线合成验收。过程为本对话内模型辅助实现、实际执行与知情复核；外部独立核验待取得。


实现NEW→PREFLIGHTED→RESOURCES_RESERVED→INITIALIZING→SEED_READY→STORE_READY→HOST_DORMANT→LISTENER_READY→SERVICE_READY→STOPPING→STOPPED，以及FAILED/RECOVERY_REQUIRED。转移除次序外，还检查前置事实；phase为只读属性，CLI无法提交任意phase。

Scope把目录和文件操作限定到当前R21 run。新实例记录及有界JSONL阶段日志在测试目录持久保存，start_claim在Store构造前写入。该日志当前用于证据，重启入口尚未将它变成完整消费/重放判定，F23/F26/T45据此保留阻塞。

OwnedResources按获取次序登记强引用和creator scope，退出逆序关闭。Store connection在ctor返回前即登记，schema/metrics/marker/config失败均由内外层幂等关闭。connect_owned在row_factory/authorizer/trace配置失败时也会关闭已打开连接。strict bootstrap使用时再次核验lease，过期锁在SQL前拒绝。

默认与原业务方法保持：strict路径只接受新Schema2/version2，禁止genesis/migration。初始化正常15次SQL，strict ctor正常7次；两者作为函数和同一新DB的前后阶段分别实际验证。22为组合正常调用推导，完整生产boot尚未执行。

失败关闭先retire context，再关闭listener/connection/lock；一个closer抛错后继续其余closer，primary与cleanup错误分开。listener只有明确登记的替身，server_close替代未运行loop上的shutdown等待。持久DB/key/审计自动删除0。

正常stop可重复；close异常保留RECOVERY_REQUIRED并保持已消耗状态。超时、丢失ACK和partial marker只能恢复无权限记录。recover只读元数据和文件身份，SQL/key-load/decrypt/start/repair均0；key_DB_content_verified始终false，来源一致与密码学内容一致分别管理。

六操作在同一受控driver进程中实际执行并保存receipt。跨独立进程的initialize/start/status/stop需要拥有同一监督进程的控制接线，当前没有该实现；新进程无法自动反序列化旧opaque对象。该收缩保护了读取权限，也限制了当前CLI实用范围。
