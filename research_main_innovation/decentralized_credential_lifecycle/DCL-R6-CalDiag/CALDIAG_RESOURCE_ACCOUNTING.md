# CalDiag资源、持久账与关闭核算

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

最终R=38,729/1,000,000；1,739组PREPARED/COMMITTED完整配对、3,478行journal。counter、最终intent及全部顺序范围一致；3个精确范围信用替代逐次事务，未用信用保守占用。

|实际计费阶段|访问|
|---|---:|
|C00–C08|37,020|
|READY64|449|
|C09H34＋Root原始重算|273|
|RootIPC56|505|
|BC40|481|
|真实C09|1|
|合计|38,729|

原全批1,800/校准300/提前1,740秒，校准100,000访问，单进程AS1GiB及Payload父4tasks保持。C02 child按合同降至96MiB，C04实际第5任务拒绝，观测最大任务数4。跨case/父组快照所见charged memory peak最大128,413,696B=122.46484375MiB；该值是已采到的内核计费峰值，精确RSS树峰值及Root RSS峰值仍UNMEASURED。Root/外部可信编排器和清理行政进程单列，清理进程设置AS1GiB。

T0=1357.752228527；deadline=3157.752228527；stop_at=3097.752228527。最后完成C09在T0+48.592009253；失败区间T0+48.699583118–48.738270904。停止器因关闭缺口继续等待，初次快照记录Payload为空、Root停止器仍在。追加冻结关闭于CLOSED记录采样T0+299.567904452，并于+299.596399447的冻结停止返回书签确认持久完成，T0+299.993796083完成seal并确认角色全空。该生命周期保留实际诊断/导出/清理时间，校准本身尚未完整完成。

初始607常规文件与最终612常规文件分别保留；冻结源导出42项。CLOSED权威标记存在，state原AWAIT_EXPECTED_RESUME字段保持原件，后续准入优先读取CLOSED。清理前后counter/journal/intent的SHA完全一致，退款/重置/新增测试访问0。

冻结seal包含610行文件manifest、611个ZIP条目，767366B，SHA `538063e6ef37408ffbf611952a1a7bbfebcc5c4ac7e1c5e41cc90d0f16bcac14`；逐流检查差异0。控制socket等非regular对象只记录元数据。最终Payload及Root角色为空，父cgroup不存在。旧历史账及原失败保持。

[账格式与配对](evidence/JOURNAL_ACCOUNTING.json) · [资源书签](evidence/RESOURCE_ACCOUNTING.json) · [冻结清理](evidence/FROZEN_FAILURE_CLEANUP.json) · [原生seal核验](evidence/NATIVE_ZIP_CHECK.json)。

AS4及4GiB驻留和结论按冻结Payload范围解释；外部Root停止器的实际AS/RSS全程记录未取得，Root资源继续单列。R含全额保守范围预付及未用烧余，作为已收费访问上界报告。
