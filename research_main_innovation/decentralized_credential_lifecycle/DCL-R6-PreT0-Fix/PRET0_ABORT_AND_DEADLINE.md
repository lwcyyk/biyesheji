# 预窗自动停止与期限

Material Passport：PreT0Recovery-static-1/r3；停止时界继承原合同；动态UNRUN。

预窗没有运行deadline，停止依据继承已经认证的activation.ticket.preflight_deadline，来源为原单会话启动前120秒TCB。停止函数只使用Root保护的当前boot/批次/源/执行锁及已消耗claim上下文；该终止权限不能生成运行资格。没有新增T0、免费60秒窗口或校准延期。

启动前初始health可在合法scope中只读；异常退出仍经原Root wrapper进入HALTED→STOP、固定首错、CLOSED/停止和pidfd回收。M.abort在缺state时先问PT的认证期限，再保留原BOOT_START/STOP_ARMED运行态后备。运行对象部分存在而初始化intent已发布时，不能按纯预窗关闭来伪造“未创建运行态”。

|来源|责任及可确认事实|
|---|---|
|Root child|保留异常/STOP/首错；固定本批停止，Owner负责收敛|
|Root coordinator|原已实测的STOP观察→stop_tree；回收自己登记的child，保持首错/原件|
|Controller/Watchdog|只有RUNTIME_ARMED后启动，原行为保持|
|systemd|只停止当前batch11 slice；原资源和RuntimeMax保持|
|自动host post-exit|只读角色/组空审计与行政证据导出；不产生运行对象或资格|

进程退出用稳定pidfd、原waitpid和事后/proc观察区分。CLEANUP_UNKNOWN不会被事后角色空自动改写；报告保留“当前进程确认退出”和“应用内部未知”两项。缺可信上下文、SPAWNING身份未发布、不可回收任务、全部停止源/内核/systemd或IO失效时继续UNKNOWN/UNRESOLVED。

原查询/锁/stop/grace/reap等有界等待及剩余deadline约束保持。新增post-exit只读导出设置30秒alarm、host最多35秒等待；它属于自动行政收尾的更小上界，列入下一执行申请，不延长启动120秒或运行300/1800窗口。系统调用/存储/调度仍保留正常返回前提，真实响应时延待动态验证。
