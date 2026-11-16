# 容量合同与日志配额审批草案

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


**CAPACITY_CONTRACT_NOT_READY。** 本文件登记待批状态，扩容批准回执尚未生成。现行64份运行源、日志/构建/预算/资格门及数量守卫全部保持。

可独立审阅的日志配额条款：256个独立分类额度，成功PENDING≤255、所有路径PENDING≤256、终态分类≤1、主日志≤263行；逐行1322字节及按类型预扣主日志345148，cursor956、单次失败摘要334及失败staging≤2246。所有当前原件保持，持久预扣→append/fsync，模糊状态fail-closed，无退款/重建/免费窗口。计数/字节/identity先验证，失效只登记真实资源停止。完整参数见附件。

256为新政策，使用既有review块尺度并单独收费；当前没有性能/活性保证。批准该政策仍需后续最小维护实现和边界/崩溃/原件校验审查，不能自动授权源码修改或动态运行。

完整容量合同必须在批准前填实：最大文件/成员N、单文件与所有raw总字节、native压缩/解压与admin嵌套总量、manifest上限、文件类型/权限、相对路径规范、duplicate/missing/extra拒绝、source/boot/instance绑定、完整原件重放、编码/CRC/hash/集合逐项检查、所有生成/异常staging闭包、读写/内存/FD/访问成本和失败/UNKNOWN语义。

当前精确缺口为：当前C09额度未生效；ABI字段上界未转为明确输入校验；readiness/S34等局部cap未推出聚合32MiB；stdout/stderr/command/traceback与模型输出缺单项/总量证明；journal可生成体量超过后验接受界；native构建整文件读取缺前置总量；ZIP元数据/压缩膨胀/admin嵌套和新测试/证据ΔE、ΔV未闭合。

现行接受cap可供草案继承，但无法同时声称“所有必需原件都可完整生成、打包并通过”。超限应停止并如实封存适用原件，缺失/部分包保持FAIL/UNKNOWN，原始记录不得静默截断、丢弃或并入不受逐件检查的容器。

容量批准项保持BLOCKED；日志政策与MR规则分别可审阅。当前JSON全部user_approved/effective/runtime_enabled=false。

[日志具体合同](proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json) · [容量缺口/字段合同](proposals/EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
