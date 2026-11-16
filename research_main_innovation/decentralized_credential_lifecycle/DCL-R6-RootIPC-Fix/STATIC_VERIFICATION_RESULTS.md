# 最终静态检查与回归影响

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

最终r4：17份源码均由实际CPython3.12.3 `py_compile`通过（命令11），CHECKED_HASH缓存17份；目标模块正文执行0。命令12复制最终44项到独立Linux静态目录；命令13对全部44项hash与目录ACL/metadata核对通过。源码/缓存/输入哈希均绑定最终r4；先前候选编译记录保留各自时点。

12份原源码字节保持：c09_oracle.py, c09_regression.py, compare.py, f1_check.py, f1_model.py, f4_dp.py, f4_reference.py, guard_probe.py, range_core.py, range_evidence.py, range_fixtures.py, run_batch.py。guard中24个预算/资格函数AST保持，涵盖init_counter、_counter_lock、_reserve、Budget、Root S/gate/C09H审查及FORMAL导入门；实际共享发布helper按当前专项范围修复。预算核心文件和事务算法保持，Root写入元数据与停止监督属于本轮授权的修改位置。

原C09H34、S34及门17输入语义核对通过，只有batch05→batch06命名绑定差异；业务计划、child合同、runtime_critical、runtime_tree四份输入原字节保持。源diff与输入diff全部封存。

|范围|静态影响审查|动态状态|
|---|---|---|
|C07 Controller崩溃|探针/原退出23判据保持；Root等待先查全批终止状态|本版本UNRUN|
|C08 Watchdog崩溃|monitor_failure/拒绝grant的原谓词保持；局部watchdog故障不等同全批STOP|本版本UNRUN|
|真实C09|前置新增IPC资格；保留ACK/receiver/waitpid/fresh-read/revision；I/O可取消|本版本NOT_EXERCISED|
|C09H34|原subject/oracle字节保持；输入只改batch命名；合并计费限5000|本版本UNRUN|
|C10子进程封闭|原探针/AS/能力/网络/cgroup规则保持|UNRUN|
|C11持久化故障|原local payload预算fault钩子及事务函数保持；Root新故障仅fixture|UNRUN|
|C12 CLOSED/恢复拒绝|原state谓词AST保持；真实恢复加IPC Root资格|UNRUN|
|S7持久化/S8身份关闭|原range_core、fixtures、evidence字节保持，S34 N/断言值保持|UNRUN|
|门17|原17输入及verify_sealed/negative/exercise函数AST保持；Root共享intent修复覆盖其记账|UNRUN|

当前runtime只读核验：Python3.12.3/e50d…150f、kernel6.18.33.2、UID999/GID989和nobody65534；32关键文件、1224运行时树hash全部相符。ext4和源目录无POSIX ACL；未来运行目录未创建，其owner/mode/ACL仍需启动前核验。systemd资源参数模板仅批次命名变化，实际单位和全局配置修改0。

本轮13条native命令均exit0：环境读2、语法编译5、静态复制4、最终只读核对2。当前最晚语法对应命令11，复制12，hash13。字段UNRUN与PASS_STATIC保持独立；没有任何本批机器行为PASS、RESOURCE_GATE_PASS或PASS_BOUNDED。

[静态结构检查](evidence/AST_AND_INVARIANT_CHECK.json)、[native摘要](evidence/STATIC_NATIVE_SUMMARY.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[命令目录](evidence/commands)。
