# 最终r3源码、输入与执行锁

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

最终版本：PTA-PhaseFinalizer-static-1/r3。主机工作区D:/毕业设计/DCL-R6-isolated-verification/pf01；静态副本evidence/SOURCE_FINAL_R3。规划Linux源/var/lib/dcl-r6/pf01，规划实例/var/lib/dcl-r6/batch12，slice=dclr6batch12.slice，未来control位于DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r3。

|对象|SHA-256|
|---|---|
|static_manifest.json|31be4cdcf2bebff97b8eca38fe1b4b606b7499921ff6babd1da23fd2c6f91c1d|
|execution_lock.json|31c6fe1ba61cd9acbc4c4c1d62f5f641a0d0be8c0ac6ca816df88cbebec0b0a7|

55项＝36 Linux程序＋2 host程序＋17输入；Linux部署53项。输入摘要→manifest、source/host程序摘要→相应manifest/执行锁、manifest→execution_lock、回执最终绑定两锁与用户原文。原模板始终TEMPLATE_UNAPPROVED，所有批准位false，authorization_text_sha256=null；没有生成实际回执、Linux实例或运行账。

旧r3的控制路径batch11-r5/正文r3标签差异在新版本统一为batch12-r3；历史原文件保持。r1/r2候选、各自源码锁/结果和diff均保留，不作为下一入口。

13文件/57成员保护清单、55项精确字节/摘要和所有变更前后SHA分别见下列工件；当前新Linux平台、boot及Native程序装载仍需下一授权内fresh核验。历史boot24fc4fce…仅属于batch11，本轮不将其冒充新执行boot。

[最终55项锁](evidence/STATIC_WORKSPACE_LOCK.json) · [最终源manifest](evidence/SOURCE_FINAL_R3/inputs/static_manifest.json) · [实际argv锁](evidence/SOURCE_FINAL_R3/inputs/execution_lock.json) · [全部diff](evidence/FULL_DIFF.patch) · [未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
