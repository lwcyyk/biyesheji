# LC证据索引

2026-11-10。Material Passport：本地原始记录与静态证据链。

|记录|内容|
|---|---|
|[授权原文](evidence/LC_AUTHORIZATION_TEXT.txt)|本轮用户指令|
|[授权收据](evidence/LC_AUTHORIZATION_RECEIPT.json)|LC精确上限/动态排除范围|
|[命令计划](evidence/LC_COMMAND_PLAN.json)|每条执行前argv和目的|
|[总命令](evidence/LC_COMMAND_RESULTS.json)|原生双流、时钟/退出、部署与静态分类|
|[账户](evidence/commands/11.result.json)|实际999/989|
|[verify](evidence/commands/22.result.json)|静态检查exit0|
|[service属性](evidence/commands/26.result.json)|限制/权限/Inactive/MainPID0|
|[slice属性](evidence/commands/27.result.json)|父层配置/Inactive|
|[最终状态](evidence/commands/50.result.json)|两单位仍inactive|
|[最终metadata](evidence/commands/59.result.json)|最终源/缓存/manifest/执行锁hash|
|[out空](evidence/commands/60.result.json)|无预算或模型结果|
|[batch02缺失](evidence/commands/61.result.json)|Linux目录未创建|
|[关键运行hash](evidence/LC_RUNTIME_HASH_RECHECK.json)|31文件原生复核|
|[源锁](evidence/LC_SOURCE_LOCK.json)|八源、缓存、host/Linux对应|
|[差异](evidence/LC_DIFF_INDEX.json)|三资源文件的完整v3→Linux diff|
|[runtime树](evidence/LC_RUNTIME_TREE_LOCK.json)|1224代码文件；三symlink已用Linux补核|
|[静态manifest](evidence/LC_STATIC_MANIFEST.json)|源/缓存/runtime/输入/配置冻结|
|[执行锁](evidence/LC_EXECUTION_LOCK.json)|14 payload＋停止/Launcher/唯一恢复/准备argv|
|[argv检查](evidence/LC_ARGV_STATIC_CHECK.json)|受限源码字面量提取，无目标代码执行|
|[入场锁](evidence/LC_BASELINE_LOCK.json)|LR全目录和4根导航快照|
|[历史核对](evidence/LC_HISTORY_INTEGRITY_CHECK.json)|旧版本/账/ZIP/研究锁保持|
|[交付核对](evidence/LC_DELIVERY_CHECK.json)|文档/JSON/链接/命令/源码/范围|
|[输出锁](evidence/LC_OUTPUT_MANIFEST.json)|本轮文件及根导航；排除自身/交付核对避免循环|

原始流为evidence/commands/NN.stdout.txt、NN.stderr.txt；按UTF-8或原生WSL UTF-16LE/混合段解码，原字节hash保存。boot_id/身份/系统路径保留本地，摘要省略唯一标识。没有读取私有目录或输出秘密字段，也无项目外发。

Python实际调用限版本和py_compile，未执行任何新目标模块正文；其他host源码/hash/字面量解析只属ADMIN_CHECK。代码PASS分支与配置值尚无动态实际结果。证据快照/编译/属性readback不构成资源或模型认证。

旧LR输出的4根导航条目从本轮evidence/navigation_before复核；更早快照继续适用，旧manifest原文保持。LC源码/单位实际文件在独立lc01中保存，历史batch01不作为新窗口。
