# CR-1至CR-12独立oracle与负向规格

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

本轮只设计数据规格和静态判断规则，十二项执行数均为0。未来oracle/harness/test清单位置继承上轮五个PROPOSED_ABSENT位置，实施门满足且用户准确授权后才可创建。[REGRESSION_ORACLE_SPEC.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/REGRESSION_ORACLE_SPEC.json)

|性质|正常输入与失败输入|并发/崩溃交错|预期状态与字节|变异|
|---|---|---|---|---|
|CR-1 MainQuotaExhaustion|255已消费，最后合法PENDING原始行与completion持久，第257次仍进入facts/classify/event|两个合法调用竞争最后一个slot，预扣后尚未append、append后未完成cursor|无新观察资格，已消费槽不退；实际持久证据不足则UNKNOWN，main<=345148；第257次main字节增量0|skip quota gate|
|CR-2 CloseReserveAvailability|具备绑定真实provider的必要data/inode/metadata/temp保留凭据，最后main/cursor提交后新STOP staging返回ENOSPC|普通日志或其他允许writer试图占用关闭保护底线，provider授权/预留与进入main阶段之间进程死亡|当前条件下COUNTEREXAMPLE；声明的provider不足或缺失时拒绝准入，close物理bytes/inodes/metadata为null时UNSUPPORTED_BOUND|claim logical equals physical|
|CR-3 CloseReserveIsolation|main和close各有固定原始绑定及独立可审计allowance，PENDING debit动用close余额|main writer与首次M.abort同时消费各自域，main EXHAUSTED发布与close reservation消费交错|新的普通观察停止，既有关闭reservation依合同继续有限完成，分别核对main上限和close上限，不合并虚构可用余额|ordinary writer spends close allowance|
|CR-4 CloseAttemptBound|单一E事件、无恢复，Receiver2、coordinator4包络，以212作为唯一文件数或额外role/retry未计入|两Root调用者竞争STOP/first/CLOSED，某一wrapper调用abort后再次抛出|E域A<=6/S<=8/W<=1/Q<=3；域外额外调用报告SCOPE_VIOLATION，按记录类型和唯一路径/staging各自求和|ignore wrapper/role count|
|CR-5 NoAbortLoop|固定AdmissionBlocked经H上下文退出至808/817，只返回EXHAUSTED而caller801-805未消费|持续就绪pidfd与重复请求，最后completion成功但caller未退出|选定异常路径结束while；其他路径报告缺少quota局部退出界，拒绝本身main增量0，实际MR有限写入另计|returnEXHAUSTED without caller consumption|
|CR-6 NoFalseClosed|已有STOP/CLOSED真实吸收后返回CLOSED，无共享marker将EXHAUSTED伪装为CLOSED|marker在check与在途raw完成之间发布，CLOSED rename成功而directoryfsync未完成|presence取消与durable CLOSED/真实group empty分别判断，记录实际marker和partial字节，缺失不计为完成|mapEXHAUSTED toCLOSED without marker|
|CR-7 LockReleaseBeforeAbort|valid fd正常finally执行unlock与close，然后caller处理异常，持H调用stop_tree/M.abort再取同一锁|parent H等待与Receiver异常退出，H持有者死亡或unlock失败|只有已证锁释放/真实进程退出可确认；其他lock状态UNKNOWN，锁文件数据0仍有inode/目录元数据责任|abort whileH held|
|CR-8 CloseIdempotence|两层abort保留同一首错并各记录有限真实尝试，每个拒绝都重发close reservation或缺ledger重新初始化|首次first O_EXCL竞争、STOP同时覆盖，first或close-debit持久后确认丢失|首错不可替换；新close额度不重发；当前实现的追加行按调用图计，串行健康示例14写/9路径；全E用23稳定和47staging粗包络|reissue close reservation or reinit missing ledger|
|CR-9 BudgetConservation|idle E关闭前后原counter/intent/journal及hash一致，退款、重置R/T0或旧generation重建|另一个budget actor出现时显式切换为更宽scope，256预付在PREPARED/counter/COMMITTED各分界中断|已付前缀烧掉；ambiguous ledger不产生新授权，266752包含122112 journal+142592 intent写和2048 counter写|refund/resetR orT0|
|CR-10 FailureResponsibility|Root/kernel/manager/provider按具体受信身份提供原件，Root死亡、provider丢失、manager拒绝、parent先失去|多个Root关闭责任竞争且收据来自不同generation，ABORTING之后parent死亡而直接waitpid尚未发布|各角色退出、payload空、预算、完整性与native/admin独立裁决，外部own-exit收据的wire与retention未给定则保留null|trust localHALTED as shared stop or self as own-exit witness|
|CR-11 UnknownPreservation|成功barrier和新鲜事实足够支持对应结果，EIO/缺件/损坏数据被标成CLOSED_COMPLETE或PASS|一个调用者的final被另一个合法ABORTING替换，write/fsync/return间确认丢失|UNKNOWN与真实部分数据保留，原件来源决定结果，只核对实际取得字节与对应hash/size，未取得数据不伪造|replaceUNKNOWN withPASS|
|CR-12 EvidencePreservation|所有安全最小原件在admin归档前已被保留并可定位，先丢弃raw或把全部退出/预算事实推迟到可能失败的admin阶段|hash后晚到append或staging变化，native包仅部分创建且随后产生错误收据|缺最小事实为UNKNOWN/拒绝；native/admin产物不会追溯补造已失去事实，每个actual path和实际层复制一次，独立index只作引用|omit required raw/staging/exit source|


每项独立oracle读取原始identity/boot/source/input/authorization、main完整行与partial尾部、cursor预扣/完成、实际close原件、budget及独立退出/provider凭据。单独实现判断规则，不导入target classifier/logger/Store，不把提交者PASS视作事实。结果类别为ACCEPT_CONDITIONAL_EVIDENCE、REJECT、UNKNOWN、UNSUPPORTED_BOUND、SCOPE_VIOLATION。

必须拒绝missing/foreign/duplicate/extra、hash/size/type/mode/binding不符、回滚预算/重发token、逻辑保留冒充物理保障、把快照标成新鲜退出事实和null伪装数值PASS。scope选择和数据引用层也属于校验对象。

测试前需要精确输入、字节/FS/provider参数、资源/时间约束及原件保留方法。scope_E反例是推导输入，当前没有故障注入、Root死亡或原生关闭测试。未来变异检查须逐个击中所指不变量并保留失败原件。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
