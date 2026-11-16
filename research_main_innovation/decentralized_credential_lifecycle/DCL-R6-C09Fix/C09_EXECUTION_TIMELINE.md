# C09执行因果时间线

Material Passport：历史机器事实＋源码偏序重建；本轮新动态事件0。

batch04运行boot99fbdfbd-f0b9-4cf2-8914-0d71867b6138，T0=199.727213695。完整字段表见evidence/RECONSTRUCTED_TIMELINE.json。

|事件|身份/时钟|对象与事实|
|---|---|---|
|E01 C09开始|systemd；208.860835|unit启动，Controller1117/start20882|
|E02 payload ready|Controller1117；209.043682578|C09.ready、counter37021、身份匹配|
|E03 Launcher观察ready|Launcher857/start19965；时间未打点|旧guard779–780，源码偏序|
|E04 退出意图发布|Launcher857；时间未打点|batch_state.expected_launcher_exit=C09；旧atomic文件/目录屏障|
|E05 成功交接/接收ACK|无证据|旧代码没有退出前双方提交事件；result_C09不存在|
|E06 Launcher退出23|命令29实际结果；精确BOOTTIME未记录|发生在意图发布之后|
|E07 pidfd可读/分类|Stopper861/start19974；时间未打点|旧guard656取s，673等待，674使用同一s|
|E08 CLOSED持久化|Stopper861；209.077071432|UNEXPECTED_LAUNCHER_EXIT|
|E09 C09被杀|systemd；209.086639|SIGKILL|
|E10 组空|Stopper861；209.089624773|empty=true|
|E11 Stopper退出|209.099784|实际exit125|
|E12 恢复拒绝|外层；精确BOOTTIME未记录|CLOSED导致检查退出，Linux resume调用0|

旧状态没有revision。读状态、意图fsync完成、pidfd返回的精确时刻均为null，无法把源码推导交错写成逐步机器追踪。交接开始可对应单方意图发布；独立收据生成、接收确认、责任转移提交均缺失。实际关闭后账37021、31对事务、组空保持，后续测试均未执行。
