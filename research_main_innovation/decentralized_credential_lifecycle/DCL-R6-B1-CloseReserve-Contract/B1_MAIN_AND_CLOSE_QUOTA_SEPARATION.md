# 主日志与关闭保留域

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

345148只对应拟主日志槽，close独立余额/请求绑定/发行规则及实际存储保障需要最小合同。当前主quota与关闭quota均未激活，LOGICAL_QUOTA_RESERVED的B1-close事实尚未建立，PHYSICAL_STORAGE_RESERVED尚未取得。[PHYSICAL_STORAGE_AUDIT.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/PHYSICAL_STORAGE_AUDIT.json)

|域|实际对象/计量|重叠处理|
|---|---|---|
|main|c09_events.jsonl，分类/stage/ACK，345148条件界|包含最后PENDING、VERIFIED等原主行|
|local quota|拟cursor和可选334摘要及其失败staging|原350166已包含声明main/marker等，不能再次整项相加|
|close core|STOP/first/delegate/state/attempt/CLOSED/event/result/父waitpid|同路径覆盖只计稳定版本，写入累计另算|
|global prepay|visits.bin、intent、journal原件|close中的budget map只引用hash/size|
|external witness/index|受信独立退出和实际原件引用|provider、profile和容量当前null|
|native/admin|原始输入引用、后层产物与实际层复制|由后层容量/资源合同约束|

每个健康scalar预付有PREPARED/COMMITTED两条compact＋LF journal，行界238/239，256事务共512行、增长≤122112。两次Root intent replace写累计142592，counter每次8字节共2048，因此266752=122112＋142592＋2048。122112和512行已经属于该总写量。[PREPAY_AND_CLOSE_PARTITION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/PREPAY_AND_CLOSE_PARTITION.json)

142592是intent多次替换写量，当前profile最终单份intent≤279；2048是counter覆盖写量，counter原件仍24字节。累计写入量与实际保留磁盘占用分别计算，B1 close不能把266752当作新可用关闭空间。Root健康2304次fsync只覆盖该256事务的两个跨目录intent、两个journal和counter共9次/事务。

拟closing reservation应在普通main进入前绑定一次，普通观察不能消费其计数/字节/物理底线，重复请求不能发新额度。STOP/CLOSED之后冻结普通观察和新reservation发行，已经预留的有限清理任务按合同继续完成。当前没有这套close额度执行对象，恢复缺失/模糊凭据时拒绝重新初始化是待实现义务。

本轮不分配新limit或改变budget事务。原始预付前缀/阶段限额和旧T0持续约束未来方案，任何关闭失败都不退款、不创建新免费窗口。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
