# QPC截止与终止合同

QPC与QPF来自惰性WindowsApi，真实监督按90、115、120秒分区。当前锚点在只读策略预检与DLL加载后、owned输出/Job/pipe/child创建前。预检读取字节和父进程成本另记，整进程启动到锚点的严格墙钟覆盖仍有独立责任。

## 90秒工作截止

R43实际parser只接受--execution-lock，Driver缺少独立的停止dispatch IPC。实现选择work_cutoff_action=TERMINATE_OWNED_JOB，到真实90秒后请求终止当前Job。它会中断当时正在执行的case，结果按实际可取得证据登记。若要求停止新case但继续child内部恢复，仍需另行接口授权。

循环和pipe读取期间都会重新检查工作截止。调用和调度可能迟返，90秒表示截止检测/终止请求规则，STRICT_120S_COMPLETION_PROVED始终false。

## 115与120

115秒之后停止新pipe读取、采样和witness写入/fsync准入。异常收尾最多一次剩余时间内的process wait，普通监督持续读取两个pipe直至可确认结束或截止。120秒之后拒绝新的owned CloseHandle/FileIOclose准入。没有grace或自动重启。

TerminateJobObject/API成功、process signal和GetExitCodeProcess结果分别记录。未signal时为TERMINATION_PENDING，exit code保留UNKNOWN。关闭失败记录CLEANUP_UNCONFIRMED。父最后Job句柄关闭的后备终止仍依赖OS处理，pending I/O和系统调度的迟滞上界未证明。

## 清理配额

Windows API批准总额内划分32个清理调用槽，普通调用只能使用max_calls−32。它是现有批准总额内部预留，当前批准总额仍null。

单次清理路径保守需要28个槽。最多8个owned Win32句柄各一次QPC和CloseHandle占16，属性列表Delete占1，终止请求占1，cleanup wait的两个QPC、Wait及ExitCode占4，final tick占1，最终receipt准入QPC最多4，file close准入QPC占1。其他查询走普通额度，配额耗尽时保留失败事实。

Native FileIO、OS内部调用与执行迟滞继续独立计费。槽数界没有承担严格120秒完成保证。
