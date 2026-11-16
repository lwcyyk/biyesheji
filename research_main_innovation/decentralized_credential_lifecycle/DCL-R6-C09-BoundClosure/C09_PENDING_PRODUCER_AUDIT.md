# C09 PENDING生产与消费全路径审计

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


基线RuntimeAdapt-static-1/r1的64份源码/输入逐件匹配冻结锁；上轮8份审查对象和合同锁保持。c09_handoff.py SHA-256为0441874d3eec62720b920a48077bc52f4f3db9c64e3c21f3aa3aa97cd43e109f，与历史CalDiag部署副本完全相同。

|原生生产点|进程/阶段|触发与重复性|可变字段/持久化/约束|
|---|---|---|---|
|c09_handoff.py:75–84 event sink|实际调用者的Root身份|向inputs/root_private/c09_events.jsonl追加一行|compact JSON＋UTF-8＋LF，O_APPEND/O_NOFOLLOW，Root0600，逐条fsync；sink自身无行长/总量/终态守卫|
|publish:85–89；调用187/226/232/262/286/343|初始scheduler、Receiver、恢复scheduler|6种进度stage；单handoff下各最多一次|base identity/window/time/hash/revision；不把publish.extra或resources整图展开到event|
|sender_prepare:196|初始scheduler/COMMITTED后|SENDER_ACK_OBSERVED，冻结调用一次|仅追加commit_sha256；peer、fresh commit和live sender核验；RPC连接等待没有重发PREPARE业务循环|
|Receiver.observe_exit:277|独立external-stop Receiver/退出观察阶段|EXIT_CLASSIFICATION_CHECK；witness缺失时PENDING可重复|固定16项facts＋verdict；check_base默认允许sender已退出；每次append/fsync，缺记录/字节额度|

进度创建路径PREPARING→READY→COMMITTED→EXIT_OBSERVED→VERIFIED→RESUMED依次受旧state存在、当前PID/boot/window/counter、持久ACK和一次性分类/恢复约束。HANDOFF_FAILED仅在STAGES声明中，当前原生代码没有对应publish调用。原生日志没有task_id字段；重复对象为同一handoff_id。

waitpid生产者为guard.py:1225及coordinator_witness:309。父协调者未运行/见证持久发布尚未完成时，Receiver看到witness=None；就绪pidfd在PENDING返回后保留，select可立即再次返回。其余消费者读取commit/witness/result/原始H34资格，不把日志PENDING数量当作已受限条件。

C09H34实际204个事件、34个oracle文件，最大单job8事件，合同上限64。它们由UID999受控服务产生合成H1–H8轨迹，每事件收费；当前原生忙等自环没有从这些费用中取得隐含配额。RootIPC56和MR64的REVIEW_PENDING等合成标签与原生日志分别登记。

STOP_REQUEST可以在一次已入锁观察检查之后出现，因此当前代码允许一条在途记录晚于STOP；不能声称“终态标记后绝无日志写”。CLOSED在可信生命周期锁下阻止后续入口，VERIFIED早返回，resume仅记录RESUMED。stop/abort/native seal/admin没有递归调用本原生event sink，错误记录转入mr/SEAL_ERROR/stderr等各自对象。

[3个原生event调用及6个stage位置](evidence/C09_NATIVE_PRODUCERS.json) · [全部上下文矩阵](evidence/PRODUCER_CONTEXT_MATRIX.json) · [逐行源码](evidence/SOURCE_EXCERPTS.json) · [C09H34原输入](evidence/C09H34_FROZEN_INVENTORY.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
