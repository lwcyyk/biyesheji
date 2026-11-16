# 访问、字节及时间责任重算

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


已冻结范围的校准硬界仍为68,498，实际本轮访问消耗0，T0/deadline/R均null。MR专项A若将旧前缀与新入口512预付集成，保守申请估计69,010；目前A源码/额度/执行批准尚未形成最终锁。A与B各有独立审计账和唯一窗口，不做预算合并或余额转移。

新B的正确公式为V_B=68,498＋V_当前证书验证＋V_新增字节工作检查＋V_新增oracle－已经证明共享的预付。新增规则尚无实现与收费合同，V_B数值保持UNRESOLVED。旧AdmissionFix的71,618仅为未接入79-job方案的条件估算，当前没有把它继承为新版本硬界。

源级数量包络K=4450已计算；raw总字节、通用单文件字节及端到端验证/构建工作量上界仍为EVIDENCE_MAX_BOUND_UNRESOLVED。具体源规则为C09退出见证PENDING循环的未计数append。另有602条readiness各131072字节的组合上界78,905,344字节，说明单记录界无法推出aggregate32MiB。

已明确的单项包括counter24字节、C03共享文件16MiB、readiness单条128KiB、接受的manifest≤4MiB、接受的native压缩/总解压及admin导出各≤32MiB。对已被这些字节守卫接受的输入，逐件checker工作量为O(K+B)，两个包扫描最多64MiB另加raw核对；该条件式界仅覆盖已接受输入的读验工作，构建输入和日志生成仍需独立上界。

总访问1,000,000、软校准100,000、总1800秒、软校准300秒、pre-T0 TCB120、提前1740、每进程AS1GiB及父TasksMax4全部保持。完整300秒、终态5秒、行政30秒的满足性继续UNRESOLVED；当前数量证明与主机逻辑状态探索不能替代原生时延/内存证书。

后续有限静态工作应为C09日志重复观察及外部原始journal导出补数值化record/byte/work责任、审查其安全停止边界和计费；本轮没有修改ACK协议、日志产生程序或预算核心。

[机器算式](evidence/RESOURCE_AND_WORK_MODEL.json) · [源循环证据](evidence/FINITE_FIXED_POINT.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
