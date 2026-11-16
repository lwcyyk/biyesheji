# DCL-R6-LC最终裁决

2026-11-10。Material Passport：已授权的静态部署、资源代码接入、编译/单位检查和执行锁。CPY312-UBU24/1已批准用于L-C静态准备；兼容性、资源执行和模型运行仍待下一授权及真实证据。

## 实际完成

1. 重新核对Python3.12.3/e50d…150f，冻结31关键文件、1224标准库代码快照及八源/缓存/单位/输入hash；版本/路径/声明来源不变。
2. 创建dcl-r6专用用户/组，UID999/GID989；仅在lc01创建目录/源码/输入/缓存/输出权限。两端batch02未创建，lc01/out为空，没有预算账/新时间窗。
3. 安装两个获准单位并verify=0、daemon-reload一次；实际属性匹配，均inactive/dead、service MainPID0。既有失败仍mnt-e.mount，保持原状。
4. 只改新工作区guard.py、guard_probe.py、run_batch.py；包含实际OS准入、持久预留、C00–C12、监督/停止、固定调度与封存接线。五业务文件四方hash一致；新八文件编译通过，未运行目标模块正文。
5. 执行锁的14组payload argv与源码36项属性逐字面静态对应通过。两个外层启动/计划恢复命令及外部停止、准备/封存流程形成具体申请。

## Gate

|Gate|状态|实际边界|
|---|---|---|
|LC-1 运行时合同|PASS_STATIC|精确身份/静态文件/语言与I/O合同完整；RUNTIME_COMPATIBILITY_UNVERIFIED|
|LC-2 部署配置|PASS_STATIC|用户/目录/两个inactive单位按范围建立，verify/属性/权限读回；RESOURCE_ENFORCEMENT_UNVERIFIED|
|LC-3 Linux适配|PASS_STATIC|三资源文件实现/差异/语法与五业务hash通过；无导入、并发或故障动态认证|
|LC-4 后续准入|CONDITIONAL_PASS|真实源/输入/命令/权限/停止锁可审；特殊映射/动态资格及新batch02许可仍为前置|

STATIC_SYNTAX_PASS、STATIC_CONFIGURATION_PASS、SOURCE_HASH_MATCH成立。MODEL_CHECK_UNRUN；RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；batch02=UNAUTHORIZED。原WS4 E2=UNRESOLVED、D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖、I1/I2/I3归档、严格分离0与IMPLEMENTATION_GATE=CLOSED保持。

## 限制与停止原则

本次没有启动/enable/restart验证单位，没有资源探针、C00–C12、业务导入或模型调用。源码分支中的PASS只定义未来判据，当前不存在对应实际结果。潜在运行/API/并发问题仍需受限校准，不把编译成功等同可运行正确性。

AS4普通映射的条件上界、kernel特殊映射的单列评审、TCB及调度/挂起/终止假设均显式保留。C09故障会改变父组代次，charge峰值与RSS口径分开，观测下界保持原名。恢复仅同boot、同T0/deadline/账一次，未知退出和重启禁止补窗。

LC开始与后期boot_id不同，说明静态配置持久性和运行时身份应分别记录；未来批次必须新绑实际启动身份。所有LC准备耗时独立于batch02，未动原27次/118.7340827秒/过期关闭账。

## 证据与下一步

[命令原件](evidence/LC_COMMAND_RESULTS.json)、[源锁](evidence/LC_SOURCE_LOCK.json)、[静态manifest](evidence/LC_STATIC_MANIFEST.json)、[执行锁](evidence/LC_EXECUTION_LOCK.json)、[差异](evidence/LC_DIFF_INDEX.json)、[交付核对](evidence/LC_DELIVERY_CHECK.json)为主要审查入口。原LR及P/Envelope/Repair/batch01/各版本保持原字节，四根导航旧版另存本轮快照。

下一步审[batch02独立申请](LC_BATCH02_AUTHORIZATION_REQUEST.md)。其新增目录/父slice/瞬态服务、校准及条件F1→F4范围直接受LC任务§4、§10、§13约束，当前仍未授权。本轮已授权的静态部署范围已经完成，无需再次申请。
