# TerminalRead最终源码与输入锁

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

最终版本TerminalRead-static-1/r1；Windows工作区D:/毕业设计/DCL-R6-isolated-verification/tr01；副本evidence/SOURCE_FINAL_R1。规划Linux源/var/lib/dcl-r6/tr01、实例/var/lib/dcl-r6/batch13、slice=dclr6batch13.slice；规划控制目录DCL-R6-TerminalRead-Fix/authorization/batch13-r1。

|对象|SHA-256|
|---|---|
|static_manifest.json|d2a6f4f58d7afd5a14287cea1c86da76d137e80dea2b64b35535fd2b145f7aac|
|execution_lock.json|43f362a064209ff8359e410301017741d787cb3acd272d40c75d447820671878|

59项＝39 Linux程序＋2 host程序＋18输入，未来Linux57项。Source/输入→manifest，manifest/host/argv→execution_lock，最终回执绑定两锁、terminal合同和真实用户原文。当前仅保存TEMPLATE_UNAPPROVED，所有批准位false，原文SHA=null；实际control/回执、Linux实例、T0和预算均未创建。

旧pf01、batch12、PFA及其全部回执和归档保持。新静态身份不构成执行许可，也不借用历史RESOURCE_GATE_PASS。当前原生环境/boot不作fresh确认，本轮WSL调用为0。

[59项精确字节锁](evidence/STATIC_WORKSPACE_LOCK.json) · [最终源](evidence/SOURCE_FINAL_R1/inputs/static_manifest.json) · [执行锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json) · [全部前后SHA](evidence/FILE_DIFF_INDEX.json) · [未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
