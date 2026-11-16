# 失败、恢复与见证结果

执行日期按原始UTC记录及本地时间核对；目录名沿用研究者冻结的2026-11-11。过程：本对话内知情模型辅助工程实现、真实离线运行及源码复核；外部核验待取得。


R21的三项阻塞分别由实际独立进程数据补证。X01/X02的原始文件及拥有进程信息见R22_CROSS_PROCESS_WITNESSES.json，完整authoritative journal保留于当前new54 run。

- 首次有效A由P1产生一个效果，关闭后FINISHED。
- P1对K先持久CLAIMED，随后真实异常退出；K的效果0，新的P2仍拒绝重放。
- P2对同A改变issuer/source/client/display均REPLAY。
- 缺slot、truncated slot、invalid previous chain，以及prepare/initialize入口读取损坏状态均RECOVERY_REQUIRED。
- F24实际两个进程竞争同A，仅一个接纳；其败者退出时暴露stdio关闭错误，已保留ERROR。
- T41实际owner Event停止，错误PID创建时点/旧epoch安全拒绝，退出后Status使用创建者退出记录。

首轮F24 OSError22来自拥有竞争败者已退出后的BufferedWriter.close。最小修复要求`process.poll() is not None`才接纳BrokenPipe/OSError，存活peer异常继续RECOVERY_REQUIRED。修复未改动授权消费算法。是否已补跑以R22_TEST_RUNS和最终源版本哈希为准。

首轮败者的亲本回收观察窗口约17.953s，因错误推迟到suite末尾回收；它已经退出。该值无法作为内核实际存活时长，内核寿命当轮未独立记录。保留此计量缺项，额外run有记录时独立报告。

还有一次PowerShell stderr路径误写，shell在Python启动前报错。该路径未创建、suite没有启动，实际suite槽位仍为两次。包装错误及一次越界写尝试在COMMAND_WRAPPER_FAILURE_001登记；实际越界写为0。它不计作已运行suite，也未被删除。

实际Authority崩溃、真实TLS握手、生产WAL/AS凭据状态和断电试验均未执行。
