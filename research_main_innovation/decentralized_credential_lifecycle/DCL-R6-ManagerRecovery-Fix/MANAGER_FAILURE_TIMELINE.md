# 管理器失败真实时间线

Material Passport：历史机器结果=CalDiag/batch09-r1；本轮静态版本=ManagerRecovery-static-1/r5；2026-11-12；新增动态执行0。

本轮直接重读CalDiag归档1,398份清单成员并核SHA，结合原始C09事件、ACK、waitpid、恢复日志和初始/最终快照恢复时间线。原T0=1357.752228527，boot=55ac71b2-e2c9-4e7b-9c94-e49d7082d8f4，最终R=38,729。

|事件|CLOCK_BOOTTIME / 相对T0|身份、状态及证据|
|---|---|---|
|C09准备|1405.999754375|Root Launcher4314/start135771，HANDOFF_PREPARING|
|Receiver就绪/持久ACK阶段|1406.084741403 / 1406.098765724|Receiver4318/start135777，HANDOFF_READY/COMMITTED|
|Sender确认Receiver回复|1406.112880144|SENDER_ACK_OBSERVED；代码在ACK持久调用返回后处理回复|
|pidfd观察退出|1406.122524286|LAUNCHER_EXIT_OBSERVED；实际退出指令时间缺打点|
|Root直接waitpid|1406.135674940|coordinator4259/start135655，raw5888/exit23|
|fresh分类审查|1406.132821057起多轮PENDING|Receiver读取当前handoff/witness；完整见证到达后转VERIFIED|
|退出见证发布采样|1406.287321124|直接父waitpid见证、原window/预算绑定|
|成功分类|1406.334492167|HANDOFF_VERIFIED；分类次数1|
|C09 PASS采样|1406.344237780|T0+48.592009253；真实ACK/Receiver/退出链齐备|
|恢复入口|1406.427000870|同Root4259验证resume entry；新scheduler4804/start140642|
|systemd管理状态读取/抛错|T0+48.699583118–48.738270904|guard._launcher_body读取failed集合后抛UNREVIEWED_MANAGER_FAILURE；exit125|
|STOP_REQUEST/自动关闭|当时均缺失|初始607文件快照无STOP_REQUEST、CLOSED、原生seal；状态AWAIT_EXPECTED_RESUME，两管理身份null|
|残留停止器|事后快照记录PID4318仍在|Payload已空；coordinator身份清空使Owner丢失检查条件缺席|
|授权调用冻结关闭|CLOSED记录T0+299.567904452；发布完成≤299.596399447|原stop_tree/seal；R和原window保持|
|退出/封存确认|T0+299.993796083|角色全空，最终612常规文件，610行原生manifest/611 ZIP条目|

精确失败列表stdout和循环最先遇到的单位在旧程序中缺记录。事后列表为mnt-e.mount及本批c06/c07/c09三个failed单位，三者对应Root PASS。journal服务时钟采用MONOTONIC，以上Root/Receiver样本采用BOOTTIME；本轮保留各自域，实际退出/持久完成只在已有书签范围内声明。

[逐项15事件与原件书签](evidence/ACTUAL_FAILURE_TIMELINE.json) · [旧包核验](evidence/CALDIAG_ARCHIVE_RECHECK.json)。本轮没有重放历史检查器、创建服务或修改原时间线。
