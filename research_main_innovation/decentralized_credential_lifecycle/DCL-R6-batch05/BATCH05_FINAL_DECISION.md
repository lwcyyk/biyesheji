# batch05 最终裁决

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

**RESOURCE_GATE_FAILED；真实 C09 交接 NOT_EXERCISED；F1/F4 均 UNRUN_RESOURCE_GATE。** 本轮预检通过并实际运行冻结C09Fix-static-1/r1；首个关键失败发生在Root完成C09H审查之后的C09入口。

|裁决轴|本批结论|
|---|---|
|B05-A C09修复|C09入口FAIL_ENTRY_PERMISSION；真实持久ACK、waitpid退出23见证、fresh-read与一次交接分类尚待验证|
|B05-B 资源资格|C00–C08九项PASS；C09H34 accepted（28 PASS+6 MUTATION_DETECTED）；C09失败；C10–C12/S34/门17未运行；RESOURCE_GATE_PASS未取得|
|B05-C F1/F4|模型搜索0；均UNRUN_RESOURCE_GATE；PASS_BOUNDED授予0|
|B05-D 证据完整性|37项源/缓存/输入及1282唯一Linux摘要启动前通过；全部原始双流/账/合成轨迹/权限与清理证据封存；交接缺件如实登记；行政完整性另见DELIVERY_CHECK|

主根因：Root独立审查以euid0替换全局共享intent为root:root/0600，下一uid999 payload读取失败并正确请求停止。次要缺陷：C09 ready等待忽略已发布CLOSED/STOP_REQUEST，Root scheduler延迟至共享T0+300才退出。实际handoff尚未进入；34项合成回归仅支持其自身事件/判据范围。

最终预算37,293/1,000,000；303组PREPARED/COMMITTED事务完整配对。T0+20.861903589请求停止、+20.909951317闭合、+20.927591657确认payload组空。Root最终清理+300.043546214，命令24外层exit125；其后专用UID、父slice及Root父子PID均为空。预算/deadline重置0、resume0、失败重试0、源码及权限修复0、batch06创建0。

C02局部路径通过：N32,896，核心预留43.751137ms，child跨度2.720971054秒，实际操作17,991，未用14,905保持占用。payload observed charged peak125,554,688B，pids上限4；精确树RSS与Root资源峰值未认证。完整校准300秒可完成性仍待验证。

程序在最终异常清理中实际完成native自动seal：345 manifest rows、346 ZIP entries、ZIP SHA-256 `0c548146e1c750da4d2cb0f26cf2bfae39c833caebf47e8f33a65a6261f8ebf0`；host保存347个native常规文件和37个冻结源/输入/缓存。socket只保存类型/身份/权限，字节复制不适用。该结果与历史batch04的封存情况分别保留。

360项本轮历史研究基线、37项canonical源、GC30/BF24、batch04 native94/source30、batch02原件51、误副本47再次只读/hash核验；历史R37,021/R32,191与`blocked by policy`保留。后续仅提出静态修复目标，当前执行授权已由首次失败终止规则收束。

继续保持 D1-PBFT-SEAL/1.1 原条件结论、强G覆盖、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED。资源工程结果与协议原创性分别裁决。

[授权与锁](BATCH05_AUTHORIZATION_AND_LOCK.md)、[Root生命周期](BATCH05_ROOT_COORDINATOR_RESULTS.md)、[真实交接](BATCH05_C09_HANDOFF_RESULTS.md)、[34项回归](BATCH05_C09_REGRESSION_RESULTS.md)、[首次失败与修复目标](BATCH05_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[最终交付核对](evidence/DELIVERY_CHECK.json)。
