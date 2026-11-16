# CalDiag证据索引

Material Passport：batch09-r1真实方案B；RESOURCE_GATE_FAILED；时间未完成。

|证据|实际范围|
|---|---|
|[用户授权](evidence/TASK_REQUEST.txt) / [实际回执](evidence/execution_authorization.json)|方案B完整校准，F1/F4关闭；摘要见AUTHORIZATION_RECEIPT_LOCK|
|[冻结源与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json)|42份文件/28程序、18项门及硬界；host无缓存环境声明|
|[原生部署](evidence/DEPLOYMENT_RESULT.json)|41份Linux源/输入Root元数据/原生语法/摘要|
|[入口调用](evidence/ACTIVE_ENTRY_INVOCATION.json) / [返回](evidence/ACTIVE_ENTRY_RETURN.json)|唯一冻结入口调用，exit125，实际host时间及argv|
|[启动、身份与失败区间](evidence/BOOT_IDENTITY_AND_FAILURE.json)|same-PID/boot、C09 exit23与恢复exit125的原始waitpid及采样|
|[C00八字段](evidence/C00_ACTUAL_FIELDS_AND_TIMING.json)|真实STARTING/READY/双取样/完整字段；细打点PARTIAL|
|[完成套件](evidence/COMPLETED_NATIVE_AUDITS.json)|READY64、IPC56、BC40、H34的实际原生oracle、原件SHA与计费|
|[真实C09](evidence/C09_ACTUAL_HANDOFF.json)|ACK、Receiver、直接waitpid、fresh分类1、窗口和预算绑定；nonce保留私有原件|
|[逐case时间](evidence/CASE_DURATIONS.json) / [journal时间线](evidence/JOURNAL_TIMELINE.json)|原始时钟域、服务/child/收费阶段跨度及已落盘fsync聚合|
|[测量覆盖](evidence/MEASUREMENT_COVERAGE.json)|缺精确边界时UNMEASURED，完整链时间null|
|[持久账核算](evidence/JOURNAL_ACCOUNTING.json)|R38,729、1,739事务、3,478行，格式/顺序/范围行政核验|
|[资源与生命周期](evidence/RESOURCE_ACCOUNTING.json)|122.46484375MiB charged峰值观测、tasks4、关闭区间/清理时间|
|[首错与关闭缺口](evidence/FIRST_FAILURE_AND_CLOSURE_GAP.json)|预期failed单位、恢复前言失败、AWAIT身份清空与原初自动关闭缺失|
|[初次事后审计](evidence/POSTRUN_AUDIT.json) / [初次607文件锁](evidence/NATIVE_EXPORT_LOCK.json)|补充清理前的真实等待态和Root停止器；初始原件保持|
|[冻结补充清理](evidence/FROZEN_FAILURE_CLEANUP.json)|原stop_tree/seal、CLOSED、预算字节保持、无新case/新窗|
|[最终审计](evidence/FINAL_POSTRUN_AUDIT.json) / [最终612文件锁](evidence/FINAL_NATIVE_EXPORT_LOCK.json)|受控角色全空、父cgroup不存在；独立最终快照|
|[源导出42锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)|41 Linux文件＋原host Windows入口|
|[原生seal核验](evidence/NATIVE_ZIP_CHECK.json)|610行manifest、611 ZIP条目，逐流SHA一致；由补充冻结清理生成|
|[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)|4次部署/导出/关闭/最终导出调用及完整argv/双流；active入口另计1次|
|[原始入口stdout](evidence/windows_entry.stdout.raw) / [stderr](evidence/windows_entry.stderr.raw)|预检、exec、C00、resume事件和首次异常；原字节保持|
|[初次journal](evidence/RUN_BOOT_JOURNAL.stdout.raw) / [最终journal](evidence/FINAL_RUN_BOOT_JOURNAL.stdout.raw)|明确run boot及批次单位过滤，Root停止器最终退出|
|[环境绑定](evidence/RUNTIME_EXPECTED_AND_OBSERVED_BINDING.json)|本批原生3.12.3/工具/内核/systemd/UID/GID/cgroup资格|
|[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)|4,254份历史文件及47误路径副本，旧预算/失败保持|
|[nonce披露核验](evidence/NONCE_DISCLOSURE_CHECK.json)|实际随机nonce只留私有快照/归档；普通报告/派生证据零匹配|
|[交付核验](evidence/DELIVERY_CHECK.json)|报告/JSON/链接/全部快照/清单/ZIP SHA，ADMIN_ONLY|

十一份指定报告、README、命令摘要和下一静态修复申请均已生成。初始和最终完整原件位于D:/毕业设计/DCL-R6-isolated-verification/batch09的native_snapshot与final_snapshot，原始权限/非regular对象记录于导出锁。打包保留两套快照及私有证据，普通报告只展示摘要和必要非秘密字段。
