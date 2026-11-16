# B09独立身份绑定审计

Material Passport：B09-AdmissionFix-static-1/r1；2026-11-12；HOST_STATIC_ONLY；动态运行0。

**BS-1=PASS_STATIC。** 独立工作区为D:/毕业设计/DCL-R6-isolated-verification/cr09。原cr01、batch09准备阶段锁、batch08 CLOSED及所有历史账保持冻结。本轮实施验证基础设施修订，采用通用配置约束、原始账检查与故障夹具；协议机制实施门及严格分离实例0保持。

|身份对象|冻结具体值|
|---|---|
|batch_id / revision|batch09 / B09-AdmissionFix-static-1/r1|
|Linux源包|/var/lib/dcl-r6/cr09|
|Linux活账根|/var/lib/dcl-r6/batch09|
|slice / service前缀|dclr6batch09.slice / dclr6batch09-|
|Root原件|inputs/root_private；新增夹具位于其boot/ledger_gate子目录|
|全局账|out/visits.bin及同名.intent.json、.journal.jsonl|
|启动回执/原文|新控制目录中的execution_authorization.json、TASK_REQUEST.txt；复制后原文名BATCH09_AUTHORIZATION_TEXT.txt|
|新控制目录|DCL-R6-B09-Supplement/authorization/batch09-r1；本轮保持未创建|
|退出/封存|本批inputs/CLOSED.json、out/EVIDENCE.zip及本批单位集合|

[batch_identity.json](evidence/SOURCE_AFTER/inputs/batch_identity.json)与[batch_identity.py](evidence/SOURCE_AFTER/src/batch_identity.py)构成结构化合同和编译期精确身份约束：完整配置须等于SPEC，源包实际路径须匹配独立host/Linux包，单位生成只接受固定case枚举。运行代码通过受约束字段和单位函数接线；批次字符串替换只用于本轮离线源码迁移，运行路径上的任意批次字符串替换为0。

静态检索覆盖Launcher、Root、Guard、Receiver、slice、argv、回执、预算、原始证据、关闭、manifest及输入：最终有效包中batch08/BATCH08/cr01内容命中0。历史引用完整保留于SOURCE_BEFORE、FULL_DIFF.patch、原始研究报告和旧包，按历史用途单独登记。

在固定哈希代码、可信Root/内核、受保护部署及无并发特权改写前提下，合法路径受以下约束：ROOT与CLI根固定batch09；全部命令/单位/合同匹配新锁；旧批回执缺新revision、身份及manifest摘要；sealed ticket额外绑定实际回执字节SHA、scope、身份合同；服务再次核boot/PID/starttime；一次认领与既有窗口/CLOSED拒绝保持。batch08路径和回执均无法满足这条合法准入链。

同会话、same-PID exec、sealed FD、一次认领、14秒屏障、八字段及RootIPC/C09/预算语义保持。目录DAC/ACL、发布与停止函数保持；新增资格摘要只注册一个固定Root:989/0640文件，原件继续Root私有。

[静态检查](evidence/BINDING_AND_GATE_STATIC_CHECK.json) · [完整diff](evidence/FULL_DIFF.patch) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)。该结论覆盖静态合法路径；当前平台、真实权限及运行时接口责任继续待动态核验。
