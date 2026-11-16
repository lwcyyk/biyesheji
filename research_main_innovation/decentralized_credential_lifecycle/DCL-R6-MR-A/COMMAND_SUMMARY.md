# MR-A命令与执行边界

本次冻结host入口实际调用1次，root scope=MR_RECOVERY_DIAGNOSTIC_ONLY，host环境PYTHONDONTWRITEBYTECODE=1，native使用锁内-I -S -B。原命令为现有Python314执行mr01/host/windows_entry.py --activate，真实argv见ACTIVE_ENTRY_INVOCATION。

WSL调用合计3次：行政部署45份Linux文件；冻结入口的单次active调用；退出后的只读导出/manager/进程审计。其余host只做文件/hash/JSON/报告操作，没有额外Linux校准、oracle、故障、重放或人工清理命令。

实际parent协调器观察到STOP_REQUEST后通过冻结stop_tree关闭；abort内部两条slice stop/kill后备尝试记录TimeoutExpired，属于被测程序自身路径。外部独立停止service及Payload service从未启动。最终确认无残留，所以本轮没有追加第二条cleanup命令。

首错后源码/输入/权限/资源上限修复0、重跑0、预算重置0、自动下一批0。部署和导出都限新mr01/batch10对象；历史数据仅读hash，误路径47只读，旧blocked by policy保持。

完整CLI、时间、双流及分类见[ADMIN_COMMAND_PLAN](evidence/ADMIN_COMMAND_PLAN.json)，解码stderr仅为便读副本，原字节保持。当前T0、deadline、R及实际Payload峰值不适用；当前管理器基线和每个相关时钟书签已保存。
