# 主额度耗尽与关闭保留区

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**PQ-4=UNRESOLVED；CLOSE_RESERVE_BOUND_UNRESOLVED。** 已精确划分主日志、局部紧急对象和完整关闭链；完整关闭证据空间及系统调用结果仍缺证明。

题设“256次观察、263条主记录、345148预留都已耗尽”在配额意义上可作为最坏包络。按正常typed schema，实际文件通常小于预留量；失败PENDING路径也达不到六个成功进度stage。安全策略仍按预留余额0处理，保留字节不回收，不把可观察余量当成新授权。

|分区|允许事件/角色|稳定数量与单项界|重入/失败行为|
|---|---|---|---|
|主PENDING/C09日志|认证Sender、Receiver、恢复scheduler|256分类＋6stage＋ACK1；345148|相同token重放0写；第257次0分类|
|局部首错摘要|首个拿到关闭资格的Root角色|1×334；所有角色共享同一不可变首错|失败留下raw staging；最多一次摘要尝试；后续异常不再追加摘要|
|STOP_REQUEST|序列化后的首关闭责任者|1×189，已有路径|现行writer可覆盖且多角色使用；v2所需单次门尚未实施|
|CLOSED|既有stop_tree/MR责任者|1×189，已有路径|失败后按原生收敛语义处理；stop_event/stop_result另列|
|cursor/staging|同H锁内的配额责任者|1198/次；两份失败cursor staging等已计350166|模糊预扣/完成立即烧额、停止；禁止退款和重建|
|native seal|唯一当批封存责任者|manifest/ZIP与必需输入另计|必须等待写者静止；封存失败留下真实原件和UNKNOWN|
|行政finalizer|post-exit行政进程|全部导出及host流另计|保留当前32MiB和256数量守卫，整体超限如实失败|

主日志耗尽后，状态机先永久拒绝新分类，完整保留最后一条已计算facts。持久写入completion/EXHAUSTED，尝试独立首错和STOP；释放H锁后调用冻结stop_tree/abort。[guard.py:758](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:758)再次获取H锁，因此锁内调用stop_tree会产生重入等待风险；合同明确拆开这两个步骤。

第257次及关闭后的重复错误请求只返回拒绝状态，无per-request错误行。首错已经存在时，后续关键异常不能把bounded emergency扩展成追加日志。独立原始系统错误仍按各自来源保留，其总量证明属于未决关闭集合；汇总代码不得替换/截断原始证据。

当前停止链的精确缺口：[guard.py:766](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:766)的stop_result包含closure_persistence_error=repr(exc)与before_stop_charged_snapshot；[manager_recovery.py:355](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:355)首错含reason、error_type、2048字符error和预算快照；[manager_recovery.py:390](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:390)close结果含roles/errors/预算后快照并追加mr_close_attempts。reason及若干系统返回/异常表示缺统一字段/编码/聚合界。[guard.py:759](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:759)还可能写不同stop_event；不能仅以固定STOP/CLOSED两个名字涵盖整条链。

2048字符error经BC紧凑JSON默认ensure_ascii=True后，字符串内容最坏可占24576个ASCII字节，再加引号和字段结构；2048不能当成字节界。socket错误的str(exc)、SEAL_ERROR的repr以及stop_result的closure_persistence_error没有相同截取合同。完整关闭保留区须分别证明这些字段、嵌套快照和所有实际追加次数，当前没有可用的统一差额数字。

最小反例CE-CLOSE-EIO：第256条PENDING已经完整持久，新的独立STOP/CLOSED文件创建或fsync返回EIO/ENOSPC。预留字节未提供物理磁盘空间和可写性保证。合同可证明拒绝后续工作并烧掉额度；无法从配额推出CLOSED必达、真实角色已退出或native seal已完成。缺失记录如实UNKNOWN，保留原预算/T0，继续按原有责任尝试清理，不创建免费重试窗口。

要完成严格关闭空间证明，需先数值化全部实际回收/MR/终态/行政输入、每角色最大尝试与锁序，证明其他生产者无法消耗关闭分区，再完成静态适配和独立授权的原生验收。[QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json)中的350166仅能批准为局部条件子项。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
