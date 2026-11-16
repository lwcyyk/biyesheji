# TR40及兼容回归静态计划

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

**新增TR40＝32safe＋8mutant，实际UNRUN。原PT64/PF48及17项变异的历史原件保持，输入jobs精确相同。**

32safe按四类构造：正常读取8项；缺T0/deadline/journal/boot/batch/锁/版本/CLOSED/退出/native输入10项；新工作/预算/phase/Launcher/跨batch/原件修改权限6项；native完整/期限/预算/缺件/IO错误/重复/已完成/行政不同步8项。8mutant复用对应safe输入作为控制。

|变异|独立oracle目标|
|---|---|
|grant_terminal_work|TERMINAL_WORK_GRANTED|
|rebuild_budget|BUDGET_REBUILT|
|skip_identity|IDENTITY_CHECK_SKIPPED|
|default_deadline|DEFAULT_DEADLINE_USED|
|ignore_journal|JOURNAL_CORRUPTION_IGNORED|
|upgrade_unknown|UNKNOWN_UPGRADED|
|false_seal|FALSE_SEAL_SUCCESS|
|write_original|ORIGINAL_EVIDENCE_MODIFIED|

oracle只导入stdlib，以实际input/trace/hash/binding重算期望并独立分类差异，之后检查声明的目标及允许集合。没有将输入的expected标签当实际结果；当前未运行subject或oracle，检出数尚无动态值。

每job预付16、Root审查1，suite entry1；TR完成681、硬960。下一最小A选择全量PT64/PF48兼容重跑，加TR40共152合成job/25变异，再有独立真实C00。原因是新namespace/源码锁与seal调用路径已经改变；旧112动态结果只支持旧冻结版本历史范围，不能成为新窗口资格。

TR-SIMULATION/1覆盖策略和观察模型，无法替代原生文件权限、锁/损坏注入或真实seal IO。下一正常A的seal hook将提供真实CLOSED读取、活动接口拒绝、预算/原件摘要及native/admin分轴记录。任何正式实例破坏故障或其他独立启动模式仍需另外冻结与许可。

[40项输入](evidence/SOURCE_FINAL_R1/inputs/terminal_contract.json) · [独立oracle](evidence/SOURCE_FINAL_R1/src/terminal_oracle.py) · [静态配对/分支审查](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
