# 资格证据与执行清单一致性

Material Passport：B09-AdmissionFix-static-1/r1；静态调用关系复核；动态UNRUN。

当前依赖为：新源/输入/工具/授权及boot → 同会话/同PID/sealed一次认领 → C00原生双次READY → READY64 → C01–C08 → C09H34 → RootIPC56 → BC40 → 真实C09持久ACK/Receiver/waitpid/fresh-read → 同父一次恢复 → C10 READY及C11–C12 → S34 → Root原件重算 → 门18及新ledger原件 → 当前健康账 → RESOURCE_QUALIFICATION → A的F1→F4，或B关闭封存。

|一致性责任|静态证据与接线|
|---|---|
|源/执行锁|新manifest包含全部27 Linux程序及14输入中的绑定对象；执行锁绑定manifest及Windows入口|
|当前身份|结构化batch09-r1配置、实际根检查、当前boot/PID/starttime、sealed回执SHA及scope|
|18项执行与验收|顶层合同18项；执行器新增recipe；审核硬核18唯一ID；原17保持|
|ledger原件与独立参考|生产evaluate→原始账检查；oracle独立解析；Root资格含三个源/输入摘要|
|权限|specimen及原行在Root私有boot子目录；公共资格固定Root:989/0640，payload只读|
|原始证据保持|目录创建与原件O_EXCL、逐行Root发布exclusive；原件摘要与Root重算比较|
|预算|新driver、即时参考、初审和两轮Root重算共账；专项640及RANGE20,000保持|
|时限|资格原件重算和收据发布均在原RANGE截止复核内；超时进入既有关闭流程|
|正式入口|继续只接受A，业务导入前检查全部C、S、门18、新ledger资格、C09及fresh健康账|

公共ledger资格保留实际结果、原件哈希和绑定。Root在静态规定的审核阶段直接重读私有原件；FORMAL使用受保护Root资格及摘要，当前真实全局账继续fresh读取。该设计保持既有可信Root/固定payload/内核/存储假设，额外同UID恶意程序保证继续保留原未决边界。

静态审查中修正的接线问题：回执SHA改为sealed ticket持有并避免自哈希循环；私有原件与公共只读资格分开；所有新增Root重算显式收费；资格发布后补原300秒截止检查。完整diff与冻结源反映最终实现。本轮这些路径均未运行。

[调用图与语法](evidence/SYNTAX_AND_CALL_GRAPH.json) · [机器一致性审查](evidence/BINDING_AND_GATE_STATIC_CHECK.json) · [完整diff](evidence/FULL_DIFF.patch)。
