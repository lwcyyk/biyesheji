# 容量及故障负向专项检查

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


主机检查实际完成：27项新归档解析器用例、3项旧native函数边界、3项旧admin guard边界、10项原MR纯判据、21项新MR数据oracle用例；7项归档guard删除变异与8项MR义务删除变异实际检出。最终归档组件支持list manifest后，27项用例、7项变异及2份真实历史归档再次核对。

|覆盖|实际执行与结果|
|---|---|
|行政256/257/312|实际旧guard AST：接受256，拒绝257/312|
|native257/258/313|实际旧_native_artifact：257验证成功；258/313拒绝|
|测试cap313边界|维护组件及独立oracle：313接受、314拒绝；该cap仅为夹具边界|
|原件/manifest/ZIP完整性|缺项、多余、错误hash、重复JSON/成员、权限、路径穿越/反斜杠/drive、Unicode、symlink/FIFO、压缩方法/加密、膨胀声明、中央目录异常、部分ZIP均拒绝|
|MR义务|错误身份/boot/InvocationID、正常退出冒充故障、历史单位、未审查接受、查询/日志缺失、STOP/CLOSED/组空/角色退出缺失、预算变化、窗口重置、fallback/manual冒充、native/admin未完成及waitpid错误均拒绝|

旧函数由实际AST原文提取后执行；文件FD适配器只指向主机夹具，Linux uid/gid/ACL/锁/期限接口未模拟为已通过。MR数据夹具外层明确HOST_MR_ORACLE_FIXTURE，内层原生声明只是被验证输入字段，真实systemd/进程事件数0。

两个主机开发迭代保留：R1预算变异夹具意外共享before/after对象，改为各自deepcopy；R2路径变异仍被Windows ZIP名称规范化后的MEMBER_SET挡住，改用drive路径隔离目标guard。原始脚本、夹具和失败说明保留。初次行政收集还有一处GBK读取UTF-8错误，通过仅续作未完成AST收集修正。以上均为主机开发记录，原生重跑0。

最终变异通过实际AST删除特定guard后执行，再由独立oracle拒绝同一输入；最终检查使用固定PASS路径0。完整新容量精确N尚未确定，针对该N/N+1的资格测试继续PENDING_CONTRACT。

[最终主机汇总](evidence/HOST_ATTEMPT_R2/HOST_CHECK_SUMMARY.json) · [归档用例](evidence/HOST_ATTEMPT_R2/ARCHIVE_HOST_RESULTS.json) · [MR用例](evidence/HOST_ATTEMPT_R2/MR_HOST_RESULTS.json) · [两类变异](evidence/HOST_ATTEMPT_R2/MUTATION_HOST_RESULTS.json) · [MR变异](evidence/HOST_ATTEMPT_R2/MR_MUTATION_HOST_RESULTS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
