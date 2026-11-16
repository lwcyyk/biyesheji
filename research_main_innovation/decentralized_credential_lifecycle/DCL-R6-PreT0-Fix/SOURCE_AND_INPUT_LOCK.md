# PreT0Recovery-static-1/r3最终源码输入锁

Material Passport：2026-11-12；独立host静态修复；新Native运行0。

host工作区D:/毕业设计/DCL-R6-isolated-verification/pt01；未来Linux源/var/lib/dcl-r6/pt01，未来实例batch11-r3，活账/var/lib/dcl-r6/batch11，slice=dclr6batch11.slice，控制目录DCL-R6-PreT0-Fix/authorization/batch11-r3。当前这些Linux/控制运行实体、T0及预算未建立。

|最终对象|SHA-256|
|---|---|
|static_manifest.json|34c9c4642c4ff8c68183845b66f49f1670efa3349ec82e07d80e8bbabfd86ab7|
|execution_lock.json|af8de2c099813d2e3018c6d46b2e95b435c2e75a122d32b73b3f96e3c47b58ec|

51项＝33 Linux程序＋2 host程序＋16输入；无pyc。原r5完整46项见SOURCE_BEFORE，最终副本SOURCE_FINAL_R3；r1/r2候选及各自锁保留构造历史。宿主postfinalizer的SHA及精确只读native命令纳入execution_lock，Root源/输入/工具/argv/namespace均由完整有向摘要链绑定。

[51项实际字节/摘要](evidence/STATIC_WORKSPACE_LOCK.json) · [最终源](evidence/SOURCE_FINAL_R3/inputs/static_manifest.json) · [原源](evidence/SOURCE_BEFORE/inputs/static_manifest.json) · [diff](evidence/FULL_DIFF.patch) · [前后SHA分类](evidence/FILE_DIFF_INDEX.json)。

只有阶段A互斥NORMAL_START/PREWINDOW_ABORT的未批准模板已生成；任一模式关闭后，第二模式及后续阶段B必须有新的独立身份/锁与明确批准。原MRA已关闭且claim消耗，缺T0也不构成重新运行许可。
