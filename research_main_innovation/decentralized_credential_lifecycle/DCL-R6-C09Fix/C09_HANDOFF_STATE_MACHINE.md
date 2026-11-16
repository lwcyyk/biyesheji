# C09交接状态机与线性化

Material Passport：C09Fix-static-1/r1；静态规格与代码对应，动态UNRUN。

|状态|进入条件与持久化|
|---|---|
|HANDOFF_PREPARING|sender发布当前事件nonce、身份、window/锁/源、预算指纹及C09 ticket/ready摘要|
|HANDOFF_READY|真实receiver校验sender存活、payload/watchdog、资源和主账|
|HANDOFF_COMMITTED|receiver持久写commit、事件与版本状态；全部fsync完成后才经认证RPC返回ACK|
|LAUNCHER_EXIT_OBSERVED|pidfd可读后持锁重新读取当前状态；预算/window未改；可有界等待退出见证|
|HANDOFF_VERIFIED|直接父协调器waitpid证明exit23，独立停止源仍active，组空确认；一次终态分类|
|RESUMED|新Launcher核完整收据与receiver，原窗口下resume_count由0到1|
|HANDOFF_FAILED/CLOSED|缺证、错误身份、失败、期限或监督失效；CLOSED吸收，迟到收据不恢复|

责任接受的线性化点为receiver完成COMMITTED持久屏障。sender还须实际收到同一活receiver的SO_PEERCRED认证ACK，才执行exit23。最终正常退出分类另在线性化于HANDOFF_VERIFIED发布；exit23本身不产生资格。

版本存于c09_handoff.revision，commit_version固定1；handoff_id绑定随机nonce、batch/boot、sender/coordinator稳定身份、完整window。窗口含T0、deadline、stop_at、执行模式、源manifest、执行锁、合同和授权摘要。counter绑定used/cap、设备/inode和原始字节摘要。

CLOSED发布与C09状态更新共用root生命周期flock；receiver在清理前后分别fresh-read，晚到ACK不能覆盖闭合。观察期限=min(T0+300,stop_at,准备时刻+12秒)。待确认期间没有AWAIT/恢复许可，超时关闭。

外部独立停止服务是receiver，位于payload slice外。父协调器是直接waitpid见证，监测中死亡会触发关闭。receiver死亡导致sender/恢复拒绝；原case Watchdog与systemd限制仍约束已存在的payload。上述保证依赖可信root、内核、fsync及调度合同，不能升级为无限故障容忍。
