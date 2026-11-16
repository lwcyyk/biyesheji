# batch05独立执行申请

Material Passport：REVIEWABLE_REQUEST；当前未获动态许可、未创建batch05。

绑定C09Fix-static-1/r1及SOURCE_AND_INPUT_LOCK的真实hash。旧batch04已CLOSED，其37,021占用、T0及资格全部保留，不能恢复或移作新窗口。

申请完整流程：预检→C00–C08→C09H34合成回归及root独立核查→真实C09持久RPC/父waitpid见证/新状态分类→一次同窗恢复→C10–C12→原S34及root原始重算→17负向门→RESOURCE_GATE_PASS→原冻结F1→F4→关闭封存。正式导入仍要求全部原资格与完成交接证明。

预算保持总1000000/1800、1740提前停、cal100000/300、RANGE20000、单进程AS1GiB、payload父tasks4、AS4条件。新增C09H硬限5000，完成路径2245，完整校准硬上界62034。新增1个可信root父协调器位于payload外，必须显式接受该TCB/进程增量；没有新增服务/依赖。handoff观察12秒包含在cal300中，超时或证据不完整关闭。

权威argv为evidence/execution_lock.json。入口/一次恢复：
~~~text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/c09f01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch05
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/c09f01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch05 --resume
~~~

root协调器只在子Launcher实际exit23、当前handoff VERIFIED且receiver仍live时向外返回23。恢复还需Root的CLOSED检查、收据/原始回归/预算/window、一次bit全部匹配；C10之前不得跳过。calibrate-only仍需独立匹配scope，关闭窗口不能转为FORMAL。

新许可须绑定manifest/执行锁/S合同/C09合同hash，test_mode=RANGE_ONLY/1及handoff_profile=C09-DURABLE-RPC/1，并接受普通映射/特殊内核映射单列范围。授权原文及root receipt在批准后写入BATCH05_AUTHORIZATION_TEXT.txt及execution_authorization.json，当前静态文本不替代。

准备只涉及新的batch05 root/inputs/out及本批slice；先核实际Python/systemd/kernel/UID/完整树、源缓存、输入和资源属性，再创建唯一T0/账。源码、N、业务输入及判据保持。任何关键fail/缺件/错误退出/监督失效/预算或时间异常立即关闭，禁止自动修复后重跑、重置或创建下一批。

保存socket控制消息摘要/peer身份、状态revision、commit/ACK/waitpid/分类、Root闭合、原C/S账、全部双流与当前boot精确17-unit journal。非普通socket文件保存类型/身份清单，常规证据逐字节封存。native自动seal与行政快照分别登记。

当前所有新actual字段null，RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，IMPLEMENTATION_GATE=CLOSED，严格分离0。F2/F3、Casdoor、T1–T4、真实凭据、无关系统修改、误副本处置及对外发送保持授权范围之外。
