# batch02最终裁决

2026-11-10。Material Passport：真实动态校准执行，已按首次失败停止并关闭。C00/C01局部PASS，C02在300秒校准软时限到达时仍在持久预付，原始FAIL；后续校准/兼容检查/F1/F4未运行。

|Gate|实际裁决|范围|
|---|---|---|
|B02-1 环境/运行时|PARTIAL|53项环境摘要及资源层真实启动有效；五业务动态兼容未到达|
|B02-2 资源资格|FAIL|C00/C01按冻结谓词通过，C02原FAIL/分析INCONCLUSIVE_LIMIT，C03–C12未完成|
|B02-3 F1|UNRUN|资源门阻断，真实模型访问0|
|B02-4 F4|UNRUN|资源门阻断，DP/参考/G64/变异访问0|
|B02-5 完整性|CONDITIONAL_PASS|原始账/ZIP/双流/版本/hash与退出证据核对通过；行政误路径副本清理尚未完成|

资源账最终32191/1000000，PREPARED/COMMITTED各32191，最终意图COMMITTED，无模糊事务或回收。批次在T0+300.1698498秒关闭，外层exit65，未超过总1800秒。分配子进程尚未启动，无法评判C02的AS触发/内存申请目标。实际组退出确认通过，无STOP_UNCONFIRMED，也没有C09恢复/重新激活新预算。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED为空；正式协议反例0。batch02=CLOSED_RESOURCE_GATE_FAILED。原WindowsWS4 E2未决、D1 1.1/D2纸面条件结论、强G覆盖、归档I1/I2/I3、严格分离0与IMPLEMENTATION_GATE=CLOSED保持。

实际C00/01支持原生AS、任务/权限/组与基础监督接口的有限条件观察；它们不授全矩阵或无限状态证明。cgroup charge峰值观测下界52.55859375MiB、RSS/虚拟空间/AS各自保留名称，特殊映射单列。原batch_state.status仍CALIBRATING，权威关闭文件已生效，原件未为展示而改写。

Linux自动ZIP 31项逐流核对，SHA=910af1ca01bf8e2258a18f95d1a12187eb2b7efd23f44fbe11146c66c5d97c84；正确host快照32文件逐字节匹配，另保存冻结LC副本。所有原batch01/各阶段/L-C文件和源码保持，本轮无代码修订/模型导入/未冻结实验/新批次。

下一步应先基于此预付成本证据形成有限的资源层静态修订/诊断申请。当前旧账、剩余次数或总窗口余量都不能重开已关闭batch02；未自动建batch03。已有专项授权已按其失败分支完整执行，当前瓶颈属于资源校准成本与窗口匹配。

[原始结果](evidence/BATCH02_RUN_RESULTS.json)、[资源账](evidence/BATCH02_ACCOUNTING_ACTUAL.json)、[导出锁](evidence/BATCH02_EXPORT_LOCK.json)、[原ZIP核对](evidence/BATCH02_NATIVE_ARCHIVE_CHECK.json)、[来源索引](SOURCE_INDEX.json)、[交付核对](evidence/BATCH02_DELIVERY_CHECK.json)。

行政封存误用了Host保留变量，副本一度写入D:\毕业设计\System.Management.Automation.Internal.Host.InternalHost。正确副本已复制到专用batch02并核验；自动审批拒绝误路径副本的迁移/删除，仅返回blocked by policy，重复副本保留待清理。此问题不改变Linux原件或资源失败裁决。
