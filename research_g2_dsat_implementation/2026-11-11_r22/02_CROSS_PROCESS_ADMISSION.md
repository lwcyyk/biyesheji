# 跨进程启动接纳

执行日期按原始UTC记录及本地时间核对；目录名沿用研究者冻结的2026-11-11。过程：本对话内知情模型辅助工程实现、真实离线运行及源码复核；外部核验待取得。


持久instance绑定environment/run、根volume/file-ID、instance ID、source/config摘要、singleton scope；seed descriptor单列真实新测试SQLite或模拟持久种子类型。没有可信descriptor的既有DB和缺失/矛盾marker进入恢复。

Prepare取得实例lease后创建/校验持久资源和独立合成启动批准。Initialize只建立/校验seed descriptor并标为SEED_READY。Start的新进程重新读全部元组，不反序列化旧Python对象。`_CLI_LOOPS`只保存当前进程拥有的运行引用，持久事实另行读取。

真实离线supervisor入口是固定的拥有worker协议：取得同实例锁、核验动作批准、持久claim、构造合成Store/Host/Handler/listener、发布STARTED，关闭资源后发布FINISHED，锁最后释放。worker可持有受信Event，另一个受控进程精确请求停止。普通shell没有获得后台服务启动资格；真实native服务和生产issuer仍闭合待审。

X01在父进程完成prepare/initialize后，由独立P1真正接纳A；A成功并停止后，P1对K先claim再以退出码73异常退出。X02由另一个P2在P1退出已被创建者记录之后重读相同文件，拒绝A/K及四类显示别名。PID、创建FILETIME、SID、image、退出码、原始stdout/stderr和文件摘要均保留。

F23读取X01独立进程拒绝stale marker、wrong config/origin、unowned resources、truncation、old epoch等结果。F26读取X02持久重放及别名结果。T45分辨A的consumed+started与K的consumed+未started。

Status将历史phase、消费状态与实际owner liveness分开；活体结论使用本轮创建登记和精确PID/创建时点/SID/image句柄。Stop只信号相符epoch的受控Event，创建时点或epoch不符即拒绝。进程退出后使用创建者EXITED记录表达已确认退出，单独旧marker无法宣布运行。

Recover为只读分类，SQL、key-load、world-decrypt、自动start和旧批准重开均0。真实key/DB内容一致性、native currentness、typed O/o和global COMPLETE保持原缺口。
