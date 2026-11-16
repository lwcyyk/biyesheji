# B1关闭资源与预付影响

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

本轮将累计写入量、稳定/临时保留数据和物理分配分别核算。预付数据按来源分区，字段全部来自上轮已核对源码codec/调用数，语义原件保持可追溯。[PREPAY_AND_CLOSE_PARTITION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/PREPAY_AND_CLOSE_PARTITION.json)

|计量|条件值|适用范围|
|---|---:|---|
|main保留|345148 bytes|拟main三类slot、codec和身份profile|
|global预付|256事务/512行journal|C09 controller/ready/counter固定前，原票据/deadline|
|journal新增数据|122112 bytes|256×(238＋239)，compact＋LF|
|intent累计替换写|142592 bytes|256×(278＋279)，同目标多次替换|
|counter累计覆盖写|2048 bytes|256×8，原文件24字节|
|上述预付总写|266752 bytes|三项一次相加，1280次数据写|
|Root健康预付fsync|2304|每txn两个Root intent各3、两个journal和counter各1|
|健康Receiver双abort例|14数据发布、31次helper fsync、12次budget文件扫描|8写首层＋6写外层，无清理错误，scope前提完整|
|E域core|59生产尝试、23稳定路径、47可能失败staging|A6/S8/W1/H0，encoded总量仍为符号式|

prepay数据已包含journal122112，closing snapshot仅嵌入三file hash/size；再次增加全journal会重复计量。稳定文件和暂存数据实际大小与累计写总和不同。FS data/inode/metadata/temp的保障须在它自己的单位和故障域求值。

正常handoff6次发布共≤11189＋4ΣV，稳定4载体≤7098＋3ΣV，主stage行已在main。fullIO/heap/FD/syscall/外部witness及原件index字节、kernel V profile和临界空间保障未闭合，当前不赋新资源上限。[NORMAL_HANDOFF_BYTE_MODEL.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/NORMAL_HANDOFF_BYTE_MODEL.json)

既有5秒terminal read、30秒Linux admin child、300校准、1800全批和1740stop政策维持其原作用域。有限fsync/调用数不推出严格墙钟，端到端native/host时间仍需定量环境假设或获准的限定验证方案。本轮新T0/预算/WSL/动态均为0。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
