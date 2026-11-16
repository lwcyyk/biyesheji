# RT-1至RT-10安全影响矩阵

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

|性质|证据及静态适配|待动态事项/当前结论|
|---|---|---|
|RT-1 RuntimeIdentity|原严格pin守卫保留，3项显式重锁，新身份合同SHA绑定|未来fresh读取；CONDITIONAL_PASS|
|RT-2 LoaderConsistency|3项同libc6包、路径/alias/Build-ID/byte hash与当前映射一致|实际服务映射及变更窗口；CONDITIONAL_PASS|
|RT-3 PythonCompatibility|Python文件不变，66入口/114对象必要version集合满足|重定位/程序语义与全链性能；CONDITIONAL_PASS|
|RT-4 ResourceEnforcement|原AS/Task/cgroup代码/单位保持，接口符号存在，基本平台一致|实际C00/资源校准；CONDITIONAL_PASS|
|RT-5 NoSilentRelock|运行时匹配器只读、合同固定哈希，无法写回新值；source/key批准位|PASS_STATIC|
|RT-6 NoCrossBatchReuse|batch14静态新身份，batch13失败attempt和旧动态记录冻结|fresh PID/boot/T0/账；PASS_STATIC准备|
|RT-7 PreflightFailClosed|旧BC_ARTIFACT_DRIFT保持，新pkg/路径/映射不符均抛错|故障副本与实际拒绝；PASS_STATIC|
|RT-8 ExecutionTimeRecheck|预检两次、原Guard字节+映射、服务前full、服务内pkg/自身映射、seal及admin重查|非原子path→exec及后续特权修改边界；CONDITIONAL_PASS|
|RT-9 TerminalCompatibility|原TR/RootIPC/MR模块和PT/PF/TR判据保持；seal/admin只增加身份读取|真实CLOSED/native/admin联调；CONDITIONAL_PASS|
|RT-10 EvidenceProvenance|Root包目录/日志＋已验证签名索引；精确旧/新文件|新payload未重提取及既有信任锚条件；CONDITIONAL_PASS|

新代码检查点内可检测映射deleted、inode/device不符、路径或包目录变化；不能原子固定整个机器在预检与exec之间的所有文件，也无法阻止已获Root权限的更新或运行中内存修改。相同glibc身份下其他受信系统依赖和动态装载仍受原TCB边界约束，报告没有将一次扫描解释为永久保证。

没有扩大D1/D2安全结论、模型范围或原创性声明。RA身份匹配结果runtime_authority=NONE，执行/终态守卫仍由原接口支配。

[静态控制流](evidence/SYNTAX_AND_IDENTITY_CONTROL_CHECK.json) · [批准前提与剩余边界](evidence/PROVENANCE_DECISION.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
