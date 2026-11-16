# DCL-R6-LC静态部署交付

2026-11-10。Material Passport：APPROVED_STATIC_DEPLOYMENT。专用UID999/GID989、lc01工作区、两个inactive单位和三资源文件已建立；八文件语法与单位verify通过，五业务hash保持。当前没有资源探针/动态校准/模型。

|交付|范围|
|---|---|
|[运行时合同](LC_RUNTIME_CONTRACT.md)|CPY312精确身份、代码树/依赖、语义与退出合同|
|[身份与目录](LC_IDENTITY_AND_FILESYSTEM.md)|实际UID/GID/属主/权限和持久账边界|
|[systemd](LC_SYSTEMD_UNITS.md)|两个inactive配置/读回与执行前提|
|[适配差异](LC_LINUX_ADAPTER_DIFF.md)|三资源程序对应表、未测责任|
|[静态检查](LC_STATIC_VERIFICATION.md)|syntax/configuration/hash与未验证项|
|[源hash](LC_SOURCE_HASH_AUDIT.md)|五业务四方一致、旧档保留|
|[batch02执行锁](LC_BATCH02_EXECUTION_LOCK.md)|完整字面量argv和固定调度/停止|
|[独立授权申请](LC_BATCH02_AUTHORIZATION_REQUEST.md)|新增目录/单位/校准/正式模型范围|
|[最终裁决](LC_FINAL_DECISION.md)|LC1–4与后续准入|

[源码锁](evidence/LC_SOURCE_LOCK.json)、[三文件diff](evidence/LC_DIFF_INDEX.json)、[精确执行JSON](evidence/LC_EXECUTION_LOCK.json)、[原命令](evidence/LC_COMMAND_RESULTS.json)、[来源](SOURCE_INDEX.json)、[证据索引](EVIDENCE_INDEX.md)。

LC1–3 PASS_STATIC、LC4 CONDITIONAL_PASS。RUNTIME_COMPATIBILITY_UNVERIFIED、RESOURCE_ENFORCEMENT_UNVERIFIED、MODEL_CHECK_UNRUN；batch02仍UNAUTHORIZED。IMPLEMENTATION_GATE=CLOSED与严格分离0保持。原账/版本/失败和全部历史原件保留。
