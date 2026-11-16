# 原生兼容性与资源接口结果

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**RA-D2=PASS_DYNAMIC，范围为获批正常A2路径。** 新运行时下CPython、单会话启动、当前映射与C00资源接口实际运行，未观察到动态链接/符号加载错误。

原生预检两侧完成、Root449同PID进入ENTRY_VERIFIED，sealed capability/一次认领保持，随后原Root/scheduler/停止器关系建立。C00八项主比较及辅助资源检查均MATCH，实际工作进入RUNNING。

C00实际Payload RLIMIT_AS软/硬1GiB，任务/身份/cgroup/NoNewPrivileges等按原readiness比较通过。Node-free包读取没有增加Payload子进程；捕获的任务最大观测为3，父limit4。hash读取、flock、fsync、waitpid、终态共享锁及ZIP写读在相应真实路径被执行。

这不等同于C01–C12/S34/门18完整资源资格、全部ABI行为或完整300秒性能通过。未故意破坏系统库/包/加载路径测试故障，也没有旧ELF的执行或安装操作。

[实际C00比较](evidence/C00_READINESS_SUMMARY.json) · [运行时回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json) · [完整实际资源](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
