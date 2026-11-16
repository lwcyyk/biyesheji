# 最小依赖修复与完整源码差异

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

最终RootIPC-static-1/r4位于`D:\毕业设计\DCL-R6-isolated-verification\ri01`和`/var/lib/dcl-r6/ri01`。修改原guard.py、c09_handoff.py两份，新增root_ipc.py、root_ipc_regression.py、root_ipc_oracle.py三份；其余12份程序原字节保持。

guard：Root atomic分支委托新发布器；payload atomic分支保持；Root等待加入checkpoint、C09双进程活性检查、父有限回收；C09H独立重算后执行IPC56，并在真实C09/恢复/FORMAL前核Root IPC资格；普通waitpid记录与最终seal移至父协调器。原预算数值/事务算法、探针和业务导入门保留。

handoff：Root内部事件日志移入私有目录；RPC连接/发送/接收可取消且保留原期限；ACK发送前生命周期锁内fresh检查；原classify、window/counter、resume及completed_handoff函数AST保持。c09_oracle/c09_regression原字节保持。

root_ipc：固定策略、私有暂存、目录fd与ACL/type/metadata校验、有界wait/checkpoint及资格重核。root_ipc_regression：Root受限fixture驱动、一次至多一个独立降权探针子进程、原账计费、逐job即时独立oracle，首次意外失败即停止。root_ipc_oracle：独立原始文件/元数据/实际probe/事件真值检查；导入仅标准库。

新增子探针位于外部Root测试TCB，顺序执行、最多1个，saved/real/effective UID/GID一致、补充组受限、CapEff=0、AS≤1GiB、2秒alarm、父3秒等待/3秒清理。该新增运行范围需要下一动态授权明确接受；当前fork执行0，实际系统UID/GID配置变更0。

[原源码37项](evidence/original)、[完整source diff](evidence/SOURCE_COMPLETE.diff)、[完整input diff](evidence/INPUT_COMPLETE.diff)、[变更索引](evidence/SOURCE_DIFF_INDEX.json)、[24函数及原文件不变检查](evidence/AST_AND_INVARIANT_CHECK.json)。输入仅必要路径/版本/哈希/未来批名与新合同发生变化；S34的N/事件/断言、C09H34、门17值保持。

r1/r2/r3候选各44项及当时检查保存在evidence/freeze_candidate_r1、freeze_candidate_r2、freeze_candidate_r3。r4保留原12秒交接期内可取消I/O并加入ACL与探针权限核查；中间候选未获动态执行资格。
