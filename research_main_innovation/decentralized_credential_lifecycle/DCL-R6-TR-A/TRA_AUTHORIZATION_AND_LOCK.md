# TR-A授权、源码与批次锁

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

**PREFLIGHT_FAILED_RUNTIME_DRIFT：主机静态准入通过，唯一原生入口在运行时摘要检查处拒绝。** 本批没有建立正式运行实例或预算窗口。

|绑定|核验结果|
|---|---|
|版本|TerminalRead-static-1/r1；59文件/41程序，Linux部署57项|
|manifest SHA|d2a6f4f58d7afd5a14287cea1c86da76d137e80dea2b64b35535fd2b145f7aac|
|execution_lock SHA|43f362a064209ff8359e410301017741d787cb3acd272d40c75d447820671878|
|静态源/输入/副本|最终锁、当前tr01、最终静态副本和退出后Linux导出59项匹配|
|规划源/实例|/var/lib/dcl-r6/tr01；/var/lib/dcl-r6/batch13；dclr6batch13.slice|
|control|DCL-R6-TerminalRead-Fix/authorization/batch13-r1，新回执绑定真实用户原文及两锁|
|boot|ef808858-4c80-4fd8-ac74-25a41b5b99ef，预检、拒绝及自动行政审计一致|
|批准范围|PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START；PT64/PF48/TR40；Full/MR/预窗注入false|
|原生基础环境|Ubuntu-24.04/Python3.12.3、原kernel/systemd、UID999/GID989/cgroup基础检查匹配；完整runtime闭包失败|
|历史保护|执行前8017文件基线，原始导航字节另存；误路径47只读/hash|

静态计费重算为C00=1、PT1089、PF817、TR681，完成2588/硬3649，完整硬67730。152项已包括25变异，预算证明齐备。本次未执行这些测试，R/T0仍null。

兼容SameProcess_C09位满足冻结schema，scope保持最小A，没有C09发放。回执、源码和执行锁均未现场改写；失配来自系统运行库。当前control已记录一次失败及自动封存，保留该attempt，不以没有T0为由重用回执或重启。

[源码/范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json) · [资源准入](evidence/RESOURCE_ADMISSION_PROOF.json) · [源后核](evidence/SOURCE_AFTER_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
