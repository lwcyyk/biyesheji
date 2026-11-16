# 最小依赖集合与实际实现

Material Passport：真实静态代码；C09Fix-static-1/r1。

修改guard.py，新增c09_handoff.py、c09_regression.py、c09_oracle.py。其余10个程序逐字节保持：五业务、runner、原探针及三个range预算/夹具/检查模块。S输入仅改未来batch命名绑定，不改34job的N/事件/断言；17门检查保持。

guard：外部停止器增加受保护socket与协调器监测；pidfd返回后调用当前状态分类；C09入口先完成C09H回归，再执行真实交接；恢复调用严格收据核验。CLOSED记录写入与handoff共锁。FORMAL保留原C/S/17门并追加完成交接来源检查。

c09_handoff：root输入目录0600 AF_UNIX SOCK_SEQPACKET，SO_PEERCRED核peerPID/UID和稳定身份；receiver写完文件/目录屏障后才返回ACK。仅“文件可见”无法替代该确认。父协调器fork一个scheduler子Launcher，用waitpid独立记录退出码；receiver核见证和组空后写唯一root PASS。

父协调器仅对当前handoff的sender写退出见证，普通完成/已经seal的其他退出不补写成功。C09后恢复仍需同T0/boot/账，一次恢复；关闭不可复用。

c09_regression：34个冻结事件job，含正常顺序、观测重排、缺证/错码/绑定/receiver/写入/fsync/停止源/预算/重复/晚收据等。6种指定错误行为只作用合成subject。c09_oracle独立从输入事件重建真值，检查H1–H8，不导入被测模块。

源码、完整diff及hash在SOURCE_DIFF_INDEX和STATIC_WORKSPACE_LOCK。本轮没有运行socket、fork退出、pidfd、校准或模型。
