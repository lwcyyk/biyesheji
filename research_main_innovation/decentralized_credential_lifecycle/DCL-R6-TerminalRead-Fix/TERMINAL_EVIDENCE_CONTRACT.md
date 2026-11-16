# 终态证据来源与一致性合同

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

|字段|创建/持久来源|可变性与核验|缺失/损坏裁决|
|---|---|---|---|
|batch/source/lock/auth|静态身份、Root一次认领activation和原文回执|固定namespace、manifest/执行锁/回执摘要精确匹配；不接受任意路径参数|拒绝/UNRESOLVED|
|原boot|原activation、state、checkpoint、关闭和waitpid|原运行身份各处相同；观察boot单独记录|拒绝/UNRESOLVED|
|T0/deadline/stop_at|原scheduler创建state；原checkpoint.window|只读原字段，有限数值与1800/1740关系；不取默认期限|UNRESOLVED|
|R/cap|原counter与预留协议|绑定magic/cap/device/inode，COMMITTED intent及完整journal对齐|UNRESOLVED；原字节保留|
|journal|原预算核心追加|正额连续PREPARED/COMMITTED，协议/原boot/cap一致，终点R；流式边界|缺失或不一致保持未决，R0也不补造journal|
|CLOSED/STOP与原因|原stop_tree/request_stop|原元数据与boot；CLOSED吸收，终态读取不覆盖|无终态标记拒绝终态审查|
|phase/version|原PF写者事务|共享counter/phase锁下读取公开/私有phase、seq和record/init摘要|UNRESOLVED|
|退出|原Root协调器waitpid与停止器/角色绑定|pid/start_ticks/原boot和原始exit status一致；同boot再审当前其他角色/组|缺失UNKNOWN；新boot只保留历史见证|
|内部状态|原MR关闭路径按需生成mr_close_state|读取已有值；缺失保持UNKNOWN；组空不升级|UNKNOWN|
|native状态|原生manifest/ZIP或真实SEAL_ERROR|已存在ZIP逐流/成员/当前关键原件摘要核验，未验证不报告完成|FAILED/UNRESOLVED按真实记录；纯预窗原分支NA|

各字段首次创建时间沿用原记录sample或T0，精确fsync完成时点缺少独立日志的字段继续UNKNOWN。历史PFA的T0/关闭/phase采样有原件，无法由新代码恢复旧文件未记录的具体IO时刻。

复用现有journal、Root state、运行点、终态标记和waitpid；没有新增不可变运行快照或预算检查点。原G.seal调用者在独立只读审查之后写入Root私有terminal_seal_review.json，标记PRE_NATIVE_ARCHIVE_READ_ONLY_REVIEW；该文件是新增审查报告，原始记录和journal不覆盖，native_ready不表示原生包已经完成。

真实性沿用受信kernel/Root launcher、冻结预留写者及无并发特权更新的原合同。没有为journal新增密码学认证声明。读取校验结构、身份、原件摘要和退出来源；只读描述符可能涉及文件系统自动管理的读取元数据，应用数据、预算和生命周期字节保持。

历史审查若设备身份等无法继续确认，保留未决；不将旧boot的deadline或旧PID用于当前工作资格。跨batch路径直接拒绝。源/锁或任一必要记录缺失时，不通过默认值补齐。

[逐字段详细合同](evidence/TERMINAL_FIELD_CONTRACT.json) · [只读代码与边界](evidence/SOURCE_FINAL_R1/src/terminal_evidence.py)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
