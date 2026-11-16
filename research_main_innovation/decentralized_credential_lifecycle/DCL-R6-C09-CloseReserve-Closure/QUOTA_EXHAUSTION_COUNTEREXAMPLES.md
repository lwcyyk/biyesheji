# 五类配额边界输入族与最小反例

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

全部轨迹为静态源码/合同输入族，执行和故障注入0。详细初态、事件、状态、记录、字节、预算和终态见[QUOTA_BOUNDARY_FAMILIES_A_E.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/QUOTA_BOUNDARY_FAMILIES_A_E.json)；反例登记含适用域，见[COUNTEREXAMPLE_REGISTER.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/COUNTEREXAMPLE_REGISTER.json)。

|族|初态及事件序列|记录与字节变化|预算、终态和前提|
|---|---|---|---|
|A 主分类额度耗尽|单handoff、有效ACK、见证暂缺；完成256次PENDING，再触发资源停止|主日志256 CHECK＋4个已到达stage＋ACK=261行；分类槽按1322预扣时主前缀≤343252。干净Receiver abort可再有8次核心发布/7路径，封存另计|观察/关闭R增量0；256预付只在此前已获准的假设中成立。存储/监督满足时可关闭，内部/原生/行政状态独立|
|B 第257次请求|256槽已耗尽；重发相同或新ordinal请求k次|待批v2拒绝所有新分类、0拒绝日志、0新增主行；当前源码仍可沿PENDING自环append|无新增预算账；当前deadline/STOP终止与v2 quota终止分别登记。旧源码257前缀为缺quota反例|
|C 耗尽与管理器/Root故障并发|A后manager stop报错、父Root退出或见证尚未发布；主停止转fallback|STOP/CLOSED/MR/回收/错误/角色证据另写；原件保留，缺失的父waitpid不能补造|group空可能已确认，native仍因缺退出原件保持UNKNOWN。真实管理器、Root生命周期和外部TCB条件必须明示|
|D 短写/EIO|接近耗尽时已预扣一次，append/fsync/marker发布失败|一槽烧掉，部分原始行/失败staging保留；可能0份持久停止标记|逻辑额度与物理持久性分别裁决；不退款/重建T0；外部退出/组空/证据完整性分别观察|
|E 重复关闭|CLOSED已存在、ZIP尚缺；两个已有Root角色先后abort|可重写ABORTING/final，追加close_attempts，产生stop_event/stop_result；冻结域append≤16；扩展API族E_n可随n增长|关闭函数自身不扣新visit；E_n任意外加调用超出4450的once/no-reentry前提，不能作为冻结域无界轨迹|

族A的261行接近共同包络263；六个成功stage与256条未完成PENDING在同一耗尽轨迹上无法同时出现。主分类耗尽也不会使剩余成功生命周期槽自动变成关闭额度。此前345148保留为共同主日志合同界。

CE-STOP-RACE：两个Root在[src/manager_recovery.py:328](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:328)同时看到STOP缺失，然后各自publish；该检查在mr_close锁之外，同一路径可能被覆盖两次。唯一文件数仍为1，写量与durability成本增加。CLOSED在H锁内保持一个固定终态路径，但后续[src/guard.py:759](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:759)明确创建不同stop_event。

CE-PARENT-WITNESS：C09 Sender已退出，父协调者尚未完成[src/guard.py:1225](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1225)的真实waitpid发布就死亡/被停止。Receiver可以按现有责任回收payload并观察角色退出；[src/terminal_evidence.py:129](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/terminal_evidence.py:129)仍可能缺少直接父见证，native_ready保持false。健康存储和足够配额不能恢复已经失去的内核亲子见证。

CE-EIO-NO-MARKER：[src/guard.py:82](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:82)设置的_HALTED属于当前进程；若共享STOP发布和产生模糊intent之前就写失败，其他进程仅凭该内存标志无法知晓停止。待批配额的跨角色失败传播和实际退出证据仍需独立证明。

CE-SEAL-TEXT(m)：在接口故障模型下，sealer的STOP查询经[src/guard.py:718](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:718)返回非零及m字节stderr，异常携带全文，最终可能写入[src/guard.py:1149](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1149)的SEAL_ERROR。m=400000展示局部350166未给该字段分配空间。此例只反驳“未约束接口输出也受局部配额覆盖”的推理；pinned systemctl在当前可信环境生成该输出的实际可达性未验证，本轮不将其宣称为原生执行反例。

所有增长族只量化底层表示、实际存储和期限允许的有限前缀；本轮没有物理无限吞吐、无限文件或任意n必能在12秒内完成的主张。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
