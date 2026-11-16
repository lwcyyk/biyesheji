# batch02资源账与关闭

2026-11-10。Material Passport：原始账审查/ADMIN_CHECK，不含任何账回写。

|字段|实际值|
|---|---|
|批次状态|CLOSED_RESOURCE_GATE_FAILED；CLOSED.json为权威关闭证据|
|T0/CLOCK_BOOTTIME|399.708633895|
|校准软截止|699.708633895=T0+300|
|全局提前停/截止|2139.708633895 / 2199.708633895|
|关闭|699.878483695，elapsed300.1698498秒|
|外层实际WSL耗时|300.701767秒，exit65|
|累计持久预留|32191 / 1000000|
|journal|32191 PREPARED、32191 COMMITTED，逐条连续检查无错，最终意图COMMITTED/after32191|
|模糊事务/回收|未发现未完成事务；未回收未用预付信用|
|模型访问|F1=0，F4=0；32191为额度预留，不登记为模型展开量|
|重启/恢复/新窗|0 / 0 / 0|

原batch_state.status仍为CALIBRATING，关闭文件已存在。冻结state()先检查停止文件，后续拒绝；本报告不改写原状态字段来制造一致外观。

32191包含C00/C01/C02入口成本及尚未使用的C02预付信用。内存分配子进程未启动，信用保守占用。967809是算术差额，不授重用或新批窗口。batch01独立保持27次/118.7340827秒/旧deadline/关闭记录。

## 计量语义

AS配置与活时读取为每进程1GiB，最多4task的条件驻留界为4GiB。已观察的父组charge峰值下界55,111,680字节（52.55859375MiB），与RSS分列；没有精确瞬时RSS树峰值证书。普通映射/共享重复计量、kernel特殊区与外部TCB/调度假设按AS4保留，原WS4 E2未决。

关闭stop_result两份均empty=true；后续manager查询MainPID0、父slice inactive、瞬态单位not-found/inactive，当前专用服务清单为空。没有STOP_UNCONFIRMED，没有主动关闭WSL。截止附近的Watchdog终止是本次实际证据，C06独立故障校准仍未运行。

原始自动ZIP为31项（30个manifest文件＋manifest本身），逐流/hash核对通过，SHA256=910af1ca01bf8e2258a18f95d1a12187eb2b7efd23f44fbe11146c66c5d97c84。Linux→正确host快照32文件逐字节一致，原件未变。
